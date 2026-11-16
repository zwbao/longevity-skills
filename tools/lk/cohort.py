"""Compare one clock readout between two groups of samples in a study (research use, not a personal readout).

`contrast` answers the question a paper asks of a public dataset: is the case group's clock readout higher, lower,
or not significantly different from the control group's? The readout can be the raw clock output ("age"), the
residual of the clock on chronological age ("acceleration_residual"), the clock minus chronological age
("acceleration_difference"), or a pace ("rate").

The test follows the study design:
  paired        the two groups are the same individuals measured twice: paired t test on per-individual differences
  unit means    an individual contributes several samples to a group: samples are averaged per individual first
  age adjusted  a raw clock output with known ages: least squares  value ~ group + age, test of the group term
  welch         everything else (residuals and differences are already age-processed): Welch's t test

The caller can fix the design, the samples the residual regression is fitted on, and the significance level; the
defaults are choices of this library, reported in the result as `method`.

Standard library only.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .library import LKError

MEASURES = ("age", "acceleration_residual", "acceleration_difference", "rate", "other")
DESIGNS = ("auto", "welch", "age_adjusted", "paired")
ARTIFACT_ABS = 1000.0  # a clock output beyond this is a numerical artefact, not an age
_UNITS = {"age": "years", "acceleration_residual": "years", "acceleration_difference": "years", "rate": "years/year"}


# ---------------------------------------------------------------- distributions and small linear algebra

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (Lentz's method)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-16:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_two_sided(t: float, df: float) -> float:
    """Two-sided P value of a t statistic."""
    if df <= 0 or t != t:
        return float("nan")
    if math.isinf(t):
        return 0.0
    return _betainc(df / 2.0, 0.5, df / (df + t * t))


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _var(xs: Sequence[float]) -> float:
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def welch(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float, float]:
    """(mean difference a - b, t, P) for Welch's unequal-variance t test."""
    if len(a) < 2 or len(b) < 2:
        raise LKError("each group needs at least 2 values", "bad_input", 3)
    diff = _mean(a) - _mean(b)
    qa, qb = _var(a) / len(a), _var(b) / len(b)
    se2 = qa + qb
    if se2 == 0.0:
        return diff, (0.0 if diff == 0 else math.copysign(math.inf, diff)), (1.0 if diff == 0 else 0.0)
    t = diff / math.sqrt(se2)
    df = se2 * se2 / ((qa * qa / (len(a) - 1) if qa else 0.0) + (qb * qb / (len(b) - 1) if qb else 0.0))
    return diff, t, t_two_sided(t, df)


def paired(d: Sequence[float]) -> Tuple[float, float, float]:
    """(mean difference, t, P) for a paired t test on per-individual differences."""
    if len(d) < 2:
        raise LKError("a paired test needs at least 2 individuals", "bad_input", 3)
    m, v = _mean(d), _var(d)
    if v == 0.0:
        return m, (0.0 if m == 0 else math.copysign(math.inf, m)), (1.0 if m == 0 else 0.0)
    t = m / math.sqrt(v / len(d))
    return m, t, t_two_sided(t, len(d) - 1)


def _solve(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Solve A X = B by Gaussian elimination with partial pivoting (A is small and square)."""
    n = len(a)
    m = [row[:] + rhs[:] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            raise LKError("the design is singular: the group and a covariate carry the same information", "not_computed", 3)
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(n):
            if r != col and m[r][col]:
                f = m[r][col] / m[col][col]
                m[r] = [x - f * y for x, y in zip(m[r], m[col])]
    return [[m[r][n + j] / m[r][r] for j in range(len(b[0]))] for r in range(n)]


def ols(y: Sequence[float], x: Sequence[Sequence[float]]) -> Tuple[List[float], List[float], int]:
    """(coefficients, standard errors, residual degrees of freedom) of y on the columns of x (include the intercept)."""
    n, p = len(y), len(x[0])
    if n <= p:
        raise LKError("too few samples for the adjusted model", "not_computed", 3)
    xtx = [[sum(row[i] * row[j] for row in x) for j in range(p)] for i in range(p)]
    xty = [[sum(row[i] * yi for row, yi in zip(x, y))] for i in range(p)]
    inv = _solve(xtx, [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)])
    beta = [sum(inv[i][j] * xty[j][0] for j in range(p)) for i in range(p)]
    rss = sum((yi - sum(b * v for b, v in zip(beta, row))) ** 2 for row, yi in zip(x, y))
    s2 = rss / (n - p)
    return beta, [math.sqrt(max(s2 * inv[i][i], 0.0)) for i in range(p)], n - p


# ---------------------------------------------------------------- the contrast

def alpha_from(text: Optional[str], default: float = 0.05) -> float:
    """Significance level stated in a sentence such as 'P < 0.05' or 'two-tailed p-value ≤ 0.01'."""
    if not text:
        return default
    m = re.search(r"[<≤]\s*=?\s*(0?\.\d+|\d(?:\.\d+)?\s*[x×]\s*10\s*\^?\s*-\s*\d+|\d(?:\.\d+)?e-\d+)", text, re.I)
    if not m:
        return default
    raw = re.sub(r"\s", "", m.group(1)).lower()
    try:
        if "10" in raw and ("x" in raw or "×" in raw):
            base, exp = re.split(r"[x×]10\^?", raw)
            value = float(base) * 10 ** float(exp)
        else:
            value = float(raw)
    except ValueError:
        return default
    return value if 0 < value < 1 else default


def _finite(v: Any) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def contrast(values: Dict[str, Any], case: Sequence[str], control: Sequence[str], measure: str = "age", *,
             ages: Optional[Dict[str, Any]] = None, subjects: Optional[Dict[str, str]] = None,
             design: str = "auto", residual_pool: Optional[Sequence[str]] = None, alpha: float = 0.05,
             min_group: int = 3) -> Dict[str, Any]:
    """Case versus control for one readout. `values`, `ages` and `subjects` are keyed by sample id."""
    if measure not in MEASURES:
        raise LKError(f"measure must be one of {', '.join(MEASURES)}", "bad_input", 3)
    if design not in DESIGNS:
        raise LKError(f"design must be one of {', '.join(DESIGNS)}", "bad_input", 3)
    ages = ages or {}
    notes: List[str] = []
    both = set(case) & set(control)
    if both:
        notes.append(f"{len(both)} sample(s) listed in both groups were left out")
    groups = {"case": [s for s in dict.fromkeys(case) if s not in both],
              "control": [s for s in dict.fromkeys(control) if s not in both]}
    given = {g: len(ids) for g, ids in groups.items()}

    def value_of(s: str) -> Optional[float]:
        v = _finite(values.get(s))
        return None if v is None or abs(v) > ARTIFACT_ABS else v

    needs_age = measure in ("acceleration_residual", "acceleration_difference")
    rows: Dict[str, List[Tuple[str, float, Optional[float]]]] = {}
    for g, ids in groups.items():
        rows[g] = [(s, value_of(s), _finite(ages.get(s))) for s in ids]  # type: ignore[misc]
        rows[g] = [r for r in rows[g] if r[1] is not None and (r[2] is not None or not needs_age)]
    used_before_units = {g: len(r) for g, r in rows.items()}
    base = {"measure": measure, "n_given": given, "alpha": alpha}
    if needs_age and min(used_before_units.values()) < min_group:
        return {**base, "status": "not_computed", "reason": "needs_age",
                "message": "this measure needs each sample's chronological age; too few samples have a value and an age",
                "n_used": used_before_units, "notes": notes}

    # the readout the paper compares
    if measure == "acceleration_residual":
        pool = [s for s in (residual_pool or [r[0] for g in rows.values() for r in g])]
        pts = [(value_of(s), _finite(ages.get(s))) for s in dict.fromkeys(pool)]
        pts = [(v, a) for v, a in pts if v is not None and a is not None]
        if len(pts) < 4 or len({a for _, a in pts}) < 2:
            return {**base, "status": "not_computed", "reason": "needs_age_spread",
                    "message": "the residual needs at least 4 samples with different ages", "n_used": used_before_units, "notes": notes}
        beta, _, _ = ols([v for v, _ in pts], [[1.0, a] for _, a in pts])
        y_of = lambda v, a: v - (beta[0] + beta[1] * a)  # noqa: E731
        notes.append(f"residual of the clock on age fitted on {len(pts)} samples (slope {beta[1]:.3f})")
    elif measure == "acceleration_difference":
        y_of = lambda v, a: v - a  # noqa: E731
    else:
        y_of = lambda v, a: v  # noqa: E731
    data = {g: [(s, y_of(v, a), a) for s, v, a in r] for g, r in rows.items()}

    # one row per individual
    method_bits: List[str] = []
    unit: Dict[str, Dict[str, Tuple[float, Optional[float]]]] = {}
    for g, r in data.items():
        by: Dict[str, List[Tuple[float, Optional[float]]]] = {}
        for s, y, a in r:
            by.setdefault((subjects or {}).get(s) or f"sample:{s}", []).append((y, a))
        unit[g] = {k: (_mean([y for y, _ in v]), (_mean([a for _, a in v if a is not None]) if any(a is not None for _, a in v) else None))
                   for k, v in by.items()}
        if any(len(v) > 1 for v in by.values()):
            method_bits.append("unit_means")
    shared = [k for k in unit["case"] if k in unit["control"] and not k.startswith("sample:")]
    n_units = {g: len(u) for g, u in unit.items()}

    use = design
    if use == "auto":
        if len(shared) >= max(min_group, math.ceil(0.8 * min(n_units.values()))):
            use = "paired"
        elif measure in ("age", "rate", "other") and all(a is not None for u in unit.values() for _, a in u.values()) \
                and len({a for u in unit.values() for _, a in u.values()}) > 1:
            use = "age_adjusted"
        else:
            use = "welch"
    if use == "paired":
        if len(shared) < 2:
            return {**base, "status": "not_computed", "reason": "no_pairs",
                    "message": "a paired design needs the same individuals in both groups", "n_used": n_units, "notes": notes}
        effect, t, p = paired([unit["case"][k][0] - unit["control"][k][0] for k in shared])
        n_used = {"pairs": len(shared)}
    else:
        if min(n_units.values()) < min_group:
            return {**base, "status": "not_computed", "reason": "too_few",
                    "message": f"each group needs at least {min_group} individuals with a value", "n_used": n_units, "notes": notes}
        if use == "age_adjusted":
            pts = [(1.0, y, a) for y, a in unit["case"].values() if a is not None] + \
                  [(0.0, y, a) for y, a in unit["control"].values() if a is not None]
            if len(pts) < sum(n_units.values()):
                notes.append(f"{sum(n_units.values()) - len(pts)} individual(s) without an age were left out of the adjusted model")
            try:
                beta, se, df = ols([y for _, y, _ in pts], [[1.0, g, a] for g, _, a in pts])
                effect = beta[1]
                t = effect / se[1] if se[1] else (0.0 if effect == 0 else math.copysign(math.inf, effect))
                p = t_two_sided(t, df) if se[1] else (1.0 if effect == 0 else 0.0)
            except LKError:
                notes.append("the age-adjusted model could not be fitted (age and group are confounded); Welch's test used")
                use = "welch"
        if use == "welch":
            effect, t, p = welch([y for y, _ in unit["case"].values()], [y for y, _ in unit["control"].values()])
        n_used = n_units
    direction = "higher" if effect > 0 else "lower" if effect < 0 else "none"
    return {**base, "status": "ok", "call": direction if p < alpha and direction != "none" else "not significant",
            "direction": direction, "p_value": p, "effect": effect, "effect_unit": _UNITS.get(measure),
            "statistic": t, "method": "+".join([use] + method_bits), "n_used": n_used, "notes": notes}


# ---------------------------------------------------------------- JSON entry (command line and MCP)

LABEL_ZH = "队列分析：比较一项研究里两组样本的时钟读数（研究用途，不是个人读数；检验方法是本库按研究设计选的）"


def _read_values(path: str, value_column: str, id_column: Optional[str] = None) -> Dict[str, str]:
    import csv
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
        fh.seek(0)
        reader = csv.DictReader(fh, delimiter="\t" if first.count("\t") > first.count(",") else ",")
        names = reader.fieldnames or []
        idc = id_column or next((c for c in names if c.lower() in ("gsm", "gsm_id", "sample", "sample_id", "id")), names[0] if names else None)
        if value_column not in names or idc not in names:
            raise LKError(f"{path} needs columns {idc!r} and {value_column!r}; it has {', '.join(names[:12])}", "bad_input", 3)
        return {row[idc]: row[value_column] for row in reader if row.get(value_column) not in (None, "")}


def contrast_from_payload(lib: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    from . import geo
    values = payload.get("values")
    if not values and payload.get("values_file"):
        if not payload.get("value_column"):
            raise LKError("values_file needs value_column (the clock's column name)", "bad_input", 3)
        values = _read_values(str(payload["values_file"]), str(payload["value_column"]), payload.get("id_column"))
    if not isinstance(values, dict) or not values:
        raise LKError("give values {sample: clock readout}, or values_file and value_column", "bad_input", 3)
    case, control = payload.get("case"), payload.get("control")
    if not isinstance(case, list) or not isinstance(control, list) or not case or not control:
        raise LKError("give case and control as lists of sample ids", "bad_input", 3)
    samples = None
    if payload.get("annotations_file"):
        text = open(str(payload["annotations_file"]), encoding="utf-8", errors="replace").read()
        samples = geo.parse_sdrf(text) if text.lstrip().startswith("Source Name") else geo.parse_series_matrix_header(text)
    chosen: Dict[str, Any] = {}
    ages = payload.get("ages")
    if ages is None and samples:
        got = geo.ages_from(samples, payload.get("age_field"))
        ages, chosen["age_field"] = got["ages"], {"field": got["field"], "guessed": got["guessed"], "samples_with_age": len(got["ages"])}
    subjects = payload.get("subjects")
    if subjects is None and samples:
        got = geo.subjects_from(samples, payload.get("subject_field"))
        subjects, chosen["subject_field"] = got["subjects"], {"field": got["field"], "guessed": got["guessed"]}
    alpha = payload.get("alpha")
    if alpha is None:
        alpha = alpha_from(payload.get("threshold_text"))
    pool = payload.get("residual_pool")
    if pool == "all_samples":
        pool = [s for s in values if ages and s in ages]
    result = contrast(values, [str(s) for s in case], [str(s) for s in control], str(payload.get("measure") or "age"),
                      ages=ages, subjects=subjects, design=str(payload.get("design") or "auto"),
                      residual_pool=pool if isinstance(pool, list) else None, alpha=float(alpha))
    caveats = ["这是对公开数据的组间比较，不是对任何个人的判断。",
               "年龄和个体标识取自样本注释；标注为 guessed 的字段是本库猜的，应由使用者核对。"]
    return {"method": "cohort contrast", "label_zh": LABEL_ZH, **lib.stamp(), **result, "chosen": chosen, "caveats_zh": caveats}


def annotations_from_file(lib: Any, path: str) -> Dict[str, Any]:
    """Every sample annotation of a series with examples, plus this library's guess of the age and individual fields."""
    from . import geo
    text = open(path, encoding="utf-8", errors="replace").read()
    samples = geo.parse_sdrf(text) if text.lstrip().startswith("Source Name") else geo.parse_series_matrix_header(text)
    if not samples:
        return {"status": "input_problem", "message_zh": "没有读到样本注释（需要 GEO series matrix 文件的表头部分，或 EBI 的 sdrf 文件）。", **lib.stamp()}
    age, subject = geo.ages_from(samples), geo.subjects_from(samples)
    return {"status": "ok", "samples": len(samples), "fields": geo.field_summary(samples),
            "guess": {"age_field": age["field"], "samples_with_age": len(age["ages"]), "subject_field": subject["field"]},
            "titles": [e["title"] for e in list(samples.values())[:5]], **lib.stamp()}
