#!/usr/bin/env python3
"""32-item frailty index (deficit accumulation, CHARLS items) and frailty status with the
cut points of Zhang et al. (GeroScience 2026; CHARLS adults aged 45+ with CKM stages 0-3).

FI = sum of the 32 deficit scores / 32 (Supplementary Table 2). Robust FI <= 0.12,
pre-frail 0.12 < FI <= 0.25, frail FI > 0.25. When the continuous cognition item is not
given, the FI is reported as the interval [S/32, (S+1)/32] that the paper's formula
allows, and the status only when both ends fall in the same group.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BINARY_ITEMS,
    BOUNDARY,
    CESD10_CUT,
    CESD_ITEM,
    COGNITION_ITEM,
    COHORT,
    HR_MODEL2,
    N_ITEMS,
    NO_WORDS,
    OUTCOME_ZH,
    PREFRAIL_MAX,
    ROBUST_MAX,
    SELF_RATED_GOOD,
    SELF_RATED_POOR,
    STATUS_ZH,
    UNDETERMINED_ZH,
    YES_WORDS,
)

TITLE = "32 项衰弱指数与衰弱分档（CHARLS 队列，CKM 0–3 期）"
_EPS = 1e-9
_SELF_RATED_KEY = "self_rated_health_poor_yn"


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text)).strip().casefold()


def status_of(fi: float) -> str:
    """Methods: robust FI <= 0.12, pre-frail 0.12 < FI <= 0.25, frail FI > 0.25."""
    if fi <= ROBUST_MAX + _EPS:
        return "robust"
    if fi <= PREFRAIL_MAX + _EPS:
        return "prefrail"
    return "frail"


def cesd_deficit(score: float) -> int:
    """Supplementary Table 2, item 31: CESD-10 > 10 = 1, <= 10 = 0."""
    return 1 if score > CESD10_CUT else 0


def frailty_index(values: dict) -> dict:
    """Sum of deficit scores divided by 32; an interval when the cognition item is absent."""
    binary = {key: int(values[key]) for _, key, *_ in BINARY_ITEMS}
    cesd = cesd_deficit(values[CESD_ITEM[1]])
    known = sum(binary.values()) + cesd
    cognition = values.get(COGNITION_ITEM[1])
    if cognition is not None:
        fi = (known + cognition) / N_ITEMS
        low = high = fi
    else:
        fi = None
        low, high = known / N_ITEMS, (known + 1) / N_ITEMS
    s_low, s_high = status_of(low), status_of(high)
    return {
        "binary": binary,
        "cesd_deficit": cesd,
        "known_sum": known,
        "cognition": cognition,
        "fi": fi,
        "fi_low": low,
        "fi_high": high,
        "status": s_low if s_low == s_high else None,
        "status_range": (s_low, s_high),
    }


def _text_to_code(key: str, raw: str) -> str | None:
    """Map a yes/no (or self-rated health) answer to the item's printed coding."""
    word = _fold(raw)
    if key == _SELF_RATED_KEY:
        if word in {_fold(w) for w in SELF_RATED_POOR}:
            return "1"
        if word in {_fold(w) for w in SELF_RATED_GOOD}:
            return "0"
    if word in {_fold(w) for w in YES_WORDS}:
        return "1"
    if word in {_fold(w) for w in NO_WORDS}:
        return "0"
    return None


def read_measurements(path: Path | None, manifest: dict) -> skillkit.Collected:
    """skillkit reads numbers only; turn the printed yes/no answers into 1/0 first."""
    if path is None:
        return skillkit.collect_measurements([], manifest)
    rows = skillkit.read_rows(path)
    if rows:
        fields = list(rows[0].keys())
        name_col = skillkit._column(fields, skillkit.NAME_COLUMNS)
        value_col = skillkit._column(fields, skillkit.VALUE_COLUMNS)
        if name_col and value_col:
            specs = [s for s in skillkit.input_specs(manifest, "measurements") if s["key"].endswith("_yn")]
            index = skillkit.alias_index(specs)
            for row in rows:
                spec = None
                for variant in skillkit.name_variants(row.get(name_col, "")):
                    if variant in index:
                        spec = index[variant][0]
                        break
                if spec is None:
                    continue
                code = _text_to_code(spec["key"], row.get(value_col, ""))
                if code is not None:
                    row[value_col] = code
    return skillkit.collect_measurements(rows, manifest)


def binary_problems(manifest: dict, values: dict) -> list:
    problems = []
    for _, key, *_ in BINARY_ITEMS:
        if key in values and values[key] not in (0.0, 1.0):
            label = skillkit.spec_by_key(manifest, key)["label_zh"]
            problems.append(skillkit.Problem(
                key, label, "range",
                f"{label} 读成 {values[key]:g}。这一项只能是 1（是/有困难）或 0（否/没有困难），也可以直接写“是”“否”。"))
    return problems


def _hr_text(row: tuple) -> str:
    est, low, high = row
    return f"{est:.2f}（95% 置信区间 {low:.2f}–{high:.2f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _status_text(key: str | None, result: dict) -> str:
    if key is not None:
        return STATUS_ZH[key]
    a, b = result["status_range"]
    return f"{UNDETERMINED_ZH}（在{STATUS_ZH[a]}和{STATUS_ZH[b]}之间）"


def in_paper_population(result: dict, age: float | None) -> tuple:
    reasons = []
    b = result["binary"]
    if b["heart_disease_dx_yn"] or b["stroke_dx_yn"]:
        reasons.append("你已经有医生诊断的心脏病或中风，论文基线排除了已有心血管病的人")
    if b["cancer_dx_yn"]:
        reasons.append("你有癌症诊断，论文基线排除了已有癌症的人")
    if age is not None and age < COHORT["min_age"]:
        reasons.append(f"你的年龄 {age:g} 岁，论文人群是 {COHORT['min_age']} 岁及以上")
    return (not reasons, reasons)


def report_lines(result: dict, age: float | None) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    if age is not None:
        lines.append(f"- 年龄 {age:g} 岁")
    domains: dict = {}
    for no, key, domain, label, *_ in BINARY_ITEMS:
        domains.setdefault(domain, []).append((no, label, result["binary"][key]))
    for domain, rows in domains.items():
        hit = [f"{label}" for _, label, v in rows if v]
        lines.append(f"- {domain}（{len(rows)} 项）：{len(hit)} 项计 1 分" + (f"——{'；'.join(hit)}" if hit else ""))
    lines.append(f"- 抑郁（第 31 项）：CES-D-10 总分超过 {CESD10_CUT} 计 1 分，本项 {result['cesd_deficit']} 分")
    if result["cognition"] is None:
        lines.append("- 认知（第 32 项）：没有提供认知缺损分，按论文公式这一项只能在 0 到 1 之间，下面给出区间")
    else:
        lines.append(f"- 认知（第 32 项）：认知缺损分 {result['cognition']:.3f}")
    lines += ["", "## 结果", ""]
    if result["fi"] is not None:
        lines.append(f"- 衰弱指数（32 项得分之和 ÷ 32）：{result['fi']:.3f}")
    else:
        lines.append(f"- 已知 31 项得分之和 {result['known_sum']}；衰弱指数在 {result['fi_low']:.3f} 到 {result['fi_high']:.3f} 之间（认知项取 0 到 1）")
    lines.append(f"- 论文分档（≤{ROBUST_MAX} 强健；{ROBUST_MAX} 到 ≤{PREFRAIL_MAX} 衰弱前期；>{PREFRAIL_MAX} 衰弱）：{_status_text(result['status'], result)}")
    if result["status"] is None:
        lines.append("- 区间跨过了切点，要确定分档需要认知缺损分；本技能不从记忆和定向原始分自行换算，因为论文没有印出换算方法。")
    lines += ["", "## 这意味着什么", ""]
    ok, reasons = in_paper_population(result, age)
    status = result["status"]
    if status == "robust":
        lines.append("你在论文里属于强健组，这是论文的参照组。论文强调重复评估：隔一段时间（论文约每两年一次）用同样的 32 项再算一次，看指数是否在上升。")
    elif status in ("prefrail", "frail"):
        if ok:
            hr = HR_MODEL2[status]
            lines.append(f"在论文人群里，基线{STATUS_ZH[status]}的人与强健的人相比，随访中新发心血管病的风险比（表 3，模型 2）：")
            for outcome in ("total_cvd", "heart_disease", "stroke"):
                lines.append(f"- {OUTCOME_ZH[outcome]}：{_hr_text(hr[outcome])}")
            lines.append("这是人群里的相对关联，不是你个人的发病概率。论文认为重复评估衰弱指数、看它是否持续上升，可以帮助决定是否需要更密切地随访。")
        else:
            lines.append("你不完全符合论文人群（" + "；".join(reasons) + "），所以不套用论文里衰弱分档对应的心血管病风险比，只给出指数和分档。")
    else:
        lines.append("分档还不能确定，所以不给对应的风险比。补上认知缺损分后再算一次即可确定。")
    lines += ["", "## 不能算的", "",
              "- 衰弱指数轨迹分组（低-稳定、中-逐渐上升、高-快速上升）：论文用 2011–2018 年四次测量拟合潜类别增长模型，各组的模型参数没有印出，所以不能把你的多次测量归入某一组；本技能每次只算一次的指数。",
              "- 个人心血管病概率：论文只给了相对风险比和优势比，没有给可用于个人的基线风险。"]
    lines += ["", "## 说明", "",
              f"- 论文人群：中国健康与养老追踪调查（CHARLS）{COHORT['n']} 名 {COHORT['min_age']} 岁及以上、心血管-肾脏-代谢（CKM）综合征 0–3 期的成人，"
              f"中位年龄 {COHORT['median_age']:g} 岁，女性 {COHORT['female_pct']}%，随访到 2020 年共 {COHORT['cvd_events']} 人新发心血管病（自报医生诊断）。",
              "- 论文的三条轨迹组基线（2011 年）衰弱指数中位数分别是 0.06、0.17 和 0.30；这是人群描述，不是你的分组。",
              "- 32 项里包括高血压、糖尿病、心脏病和中风本身，所以衰弱指数和心血管代谢状态有部分重叠（论文局限里也写了）。",
              "- 各项都是自报：医生诊断过的病、日常活动和行动是否有困难。和论文一样，按“现在是否有困难”填写。"]
    if age is not None and age < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = read_measurements(measurements, manifest)
    problems = list(collected.problems)
    problems += binary_problems(manifest, collected.values)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    result = frailty_index(dict(collected.values))
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, age)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "frailty_index": None if result["fi"] is None else round(result["fi"], 4),
        "frailty_index_low": round(result["fi_low"], 4),
        "frailty_index_high": round(result["fi_high"], 4),
        "frailty_status": _status_text(result["status"], result),
        "deficit_sum_31_items": result["known_sum"],
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 30 项是/否（1/0）、CES-D-10 总分、可选认知缺损分（0–1）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
