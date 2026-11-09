#!/usr/bin/env python3
"""Senior Fitness Test results placed in the sex-specific quintiles of the Taiwan
National Physical Fitness Survey cohort (Wu et al., JAMA Netw Open 2026), with the
printed adjusted hazard ratios of all-cause mortality for that quintile versus Q1.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AHR_ALL,
    AHR_SEX,
    BOUNDARY,
    COHORT,
    DOMAIN_ZH,
    MEDIAN_IQR,
    ONE_LEG_CEILING_S,
    QUINTILE_RANGES,
    TESTS,
)

TITLE = "老年体适能七项测试的五分位和全因死亡风险比（台湾国民体能队列）"
_EPS = 1e-9

# Unit words people write on score sheets that skillkit does not map. Counts have no
# unit (skill.json unit "1"); seconds are "s".
_UNIT_WORDS = {
    "次": "", "个": "", "下": "", "reps": "", "rep": "", "count": "", "counts": "", "times": "", "次数": "",
    "秒": "s", "sec": "s", "secs": "s", "second": "s", "seconds": "s", "秒钟": "s",
}

SEX_ZH = {"male": "男", "female": "女"}


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man", "男性"}:
        return "male"
    if text in {"female", "f", "女", "woman", "女性"}:
        return "female"
    return None


DIRECTION = {test: direction for test, _key, _label, _unit, direction in TESTS}


def quintile(test: str, sex: str, value: float) -> dict:
    """Quintile (1-5) of a raw value with eTable 3's sex-specific ranges.

    A value inside a printed range gets that quintile. eTable 3 prints the observed
    range of each quintile, so there can be small gaps between neighbouring quintiles
    (one-leg stance 4.10 / 4.12 s in men); a value in a gap goes to the poorer
    quintile and is flagged. A value beyond the observed extremes goes to Q1 or Q5 and
    is flagged.
    """
    ranges = QUINTILE_RANGES[sex][test]
    for q, (low, high) in enumerate(ranges, start=1):
        if low - _EPS <= value <= high + _EPS:
            return {"q": q, "flag": None}
    if DIRECTION[test] == "higher":
        if value < ranges[0][0]:
            return {"q": 1, "flag": "below"}
        if value > ranges[4][1]:
            return {"q": 5, "flag": "above"}
        for q in range(1, 5):
            if ranges[q - 1][1] < value < ranges[q][0]:
                return {"q": q, "flag": "gap"}
    else:
        if value > ranges[0][1]:
            return {"q": 1, "flag": "above"}
        if value < ranges[4][0]:
            return {"q": 5, "flag": "below"}
        for q in range(1, 5):
            if ranges[q][1] < value < ranges[q - 1][0]:
                return {"q": q, "flag": "gap"}
    raise ValueError(f"cannot place {value} for {test}")


def _hr_text(row: tuple) -> str:
    est, low, high = row
    if low is None:
        return "1（参照组）"
    return f"{est:.2f}（95% 置信区间 {low:.2f}–{high:.2f}）"


def _range_text(test: str, sex: str, q: int, unit: str) -> str:
    low, high = QUINTILE_RANGES[sex][test][q - 1]
    digits = {"次": 0, "cm": 1, "秒": 2}[unit]
    return f"{low:.{digits}f} 到 {high:.{digits}f} {unit}"


def next_step(test: str, sex: str, q: int, direction: str) -> float | None:
    """Raw value at which the next better quintile's printed range starts."""
    if q >= 5:
        return None
    low, high = QUINTILE_RANGES[sex][test][q]
    return low if direction == "higher" else high


def read_inputs(path: Path | None, manifest: dict) -> skillkit.Collected:
    rows = skillkit.read_rows(path) if path is not None else []
    if rows:
        unit_col = next((c for c in rows[0].keys() if c and c.strip().lower() in ("unit", "units", "单位")), None)
        if unit_col:
            for row in rows:
                word = (row.get(unit_col) or "").strip().lower()
                if word in _UNIT_WORDS:
                    row[unit_col] = _UNIT_WORDS[word]
    return skillkit.collect_measurements(rows, manifest)


def assess(values: dict, sex: str) -> list:
    out = []
    for test, key, label, unit, direction in TESTS:
        if key not in values:
            continue
        raw = values[key]
        used = raw
        capped = False
        if test == "one_leg" and raw > ONE_LEG_CEILING_S:
            used, capped = ONE_LEG_CEILING_S, True
        place = quintile(test, sex, used)
        q = place["q"]
        out.append({
            "test": test, "key": key, "label": label, "unit": unit, "direction": direction,
            "value": raw, "used": used, "capped": capped, "q": q, "flag": place["flag"],
            "ahr_all": AHR_ALL[test][q - 1], "ahr_sex": AHR_SEX[sex][test][q - 1],
            "next_at": next_step(test, sex, q, direction),
        })
    return out


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _fmt_value(row: dict) -> str:
    v = row["value"]
    return f"{v:g} {row['unit']}"


def report_lines(rows: list, sex: str, age: float | None, missing: list) -> list:
    who = SEX_ZH[sex]
    lines = [f"# {TITLE}", "", "## 输入", ""]
    lines.append(f"- {who}" + (f"，{age:g} 岁" if age is not None else ""))
    for row in rows:
        lines.append(f"- {row['label']}：{_fmt_value(row)}")
    lines += ["", "## 结果", "",
              f"每项成绩放进论文里{who}性 65–90 岁人群的五分位（Q1 最差，Q5 最好；8 英尺起身绕行越快越好）。"
              f"风险比是该组相对同性别 Q1 组的全因死亡风险比，每项测试单独建模。", "",
              f"| 测试 | 你的成绩 | 五分位 | 该组成绩范围（{who}） | 风险比（{who}性分层模型） | 风险比（男女合并模型） |",
              "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(f"| {row['label']}（{DOMAIN_ZH[row['test']]}） | {_fmt_value(row)} | Q{row['q']} | "
                     f"{_range_text(row['test'], sex, row['q'], row['unit'])} | {_hr_text(row['ahr_sex'])} | {_hr_text(row['ahr_all'])} |")
    notes = []
    for row in rows:
        if row["capped"]:
            notes.append(f"{row['label']}：论文的测试每次到 {ONE_LEG_CEILING_S:g} 秒就停，你的 {row['value']:g} 秒按 {ONE_LEG_CEILING_S:g} 秒归档。")
        if row["flag"] == "gap":
            notes.append(f"{row['label']}：{_fmt_value(row)} 落在论文印出的两档成绩范围之间（那一段没有人），按较差的一档 Q{row['q']} 归档。")
        elif row["flag"] in ("below", "above"):
            notes.append(f"{row['label']}：{_fmt_value(row)} 超出了论文人群里观察到的成绩范围，按 Q{row['q']} 归档，请核对测量和单位。")
    if notes:
        lines += ["", "归档说明：", ""] + [f"- {item}" for item in notes]
    lines += ["", "## 这意味着什么", ""]
    q1 = [row["label"] for row in rows if row["q"] == 1]
    if q1:
        lines.append(f"{'、'.join(q1)}在同性别最低的五分之一（Q1）。论文发现死亡风险的差别主要集中在 Q1 和其余各组之间，"
                     "作者据此推测离开最低一档可能收益最大；但这是观察性关联，论文没有检验提高成绩后风险是否随之下降，也不是你个人的死亡概率。")
    else:
        lines.append("没有一项落在同性别最低的五分之一（Q1），这是好的信号。")
    better = [row for row in rows if row["next_at"] is not None]
    if better:
        parts = []
        for row in better:
            word = "达到" if row["direction"] == "higher" else "缩短到"
            unit = row["unit"]
            parts.append(f"{row['label']}{word} {row['next_at']:g} {unit}")
        lines.append("按论文的分档，进入上一档的成绩起点：" + "；".join(parts) + "。这只是分档界线，不是训练目标或处方。")
    lines.append("风险比低于 1 表示在论文人群里，这一组的人比 Q1 组死亡更少；置信区间跨过 1 的组和 Q1 没有统计学差异。"
                 "不同测试的风险比来自不同的模型，不能相乘，也不能合成一个总风险。")
    lines.append("论文的综合体适能指数（七项同性别百分位之和）需要整个队列每项的百分位分布，论文只印了五分位范围，所以这里不算综合指数。")
    if missing:
        lines.append(f"没有交的项目：{'、'.join(missing)}。论文七项是分别分析的，缺项不影响已交项目的归档。")
    lines += ["", "## 说明", "",
              f"- 论文人群：台湾国民体能检测数据库 2015–2016 年 {COHORT['n']} 名 65–90 岁社区老人（男 {COHORT['n_male']}、女 {COHORT['n_female']}），"
              f"平均 {COHORT['mean_age']} 岁，连到健保死亡登记，中位随访 {COHORT['followup_median_years']:g} 年，{COHORT['deaths']} 人（{COHORT['deaths_pct']}%）死亡。"
              "排除了失智、脑卒中、截肢和持重大伤病卡（主要是癌症、自身免疫病、慢性精神疾病）的人。",
              "- 风险比调整了性别（合并模型）、年龄、规律运动、体重指数、收入、教育、就业、独居、居住地、城市化程度、十种慢病和 Charlson 共病指数；没有调整吸烟。",
              "- 测法照台湾老年体适能（Senior Fitness Test）规范：2 分钟原地抬膝踏步计双膝都抬到髂前上棘和髌骨中点连线中点高度的次数；30 秒手臂弯举女性 2.27 kg、男性 3.63 kg 哑铃；"
              "抓背和椅子坐姿体前弯重叠记正、差距记负，取两次较好值；单脚站立双手叉腰、睁眼，两次各到 30 秒停，取较长；8 英尺（2.44 米）起身绕锥返回坐下，取两次较快。",
              "- 8 英尺起身绕行不是常见的 3 米“起立-行走计时”，两者不能互换。"]
    if age is not None:
        low, high = COHORT["age_range"]
        if not low <= age <= high:
            lines.append(f"- 你的年龄 {age:g} 岁不在论文人群（{low}–{high} 岁）内，这些五分位和风险比不一定适用。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def result_values(rows: list) -> dict:
    out = {}
    for test, _key, _label, _unit, _direction in TESTS:
        out[f"{test}_quintile"] = None
        out[f"{test}_ahr_sex"] = None
        out[f"{test}_ahr"] = None
    for row in rows:
        out[f"{row['test']}_quintile"] = row["q"]
        out[f"{row['test']}_ahr_sex"] = row["ahr_sex"][0]
        out[f"{row['test']}_ahr"] = row["ahr_all"][0]
    out["tests_done"] = len(rows) if rows else None
    out["tests_in_q1"] = sum(1 for row in rows if row["q"] == 1) if rows else None
    return out


def levers(rows: list, sex: str, targets: dict) -> dict:
    """Current quintile and hazard ratio per test, the value that starts the next
    quintile, and (with targets) the quintile and printed hazard ratio at each target.

    The method is a step lookup, so there is no per-unit slope. Each test is its own
    model; there is no combined value for all targets together.
    """
    by_key = {row["key"]: row for row in rows}
    out = {
        "schema": "longevity-levers/1",
        "model": "senior-fitness-quintiles",
        "model_zh": "老年体适能五分位与全因死亡风险比（台湾国民体能队列，同性别分层模型）",
        "current": {row["key"]: {"value": row["value"], "quintile": row["q"], "ahr_sex": row["ahr_sex"][0]} for row in rows},
        "sensitivity": [
            {"key": row["key"], "label_zh": row["label"], "unit": row["unit"], "value": row["value"], "quintile": row["q"],
             "next_quintile_at": row["next_at"], "direction": row["direction"]}
            for row in rows
        ],
        "levers": [],
        "note_zh": "按五分位查表，没有连续斜率；每项测试单独建模，风险比不能相乘或合成。这是人群关联，不是提高成绩后的个人预测。",
    }
    for key, target in targets.items():
        row = by_key.get(key)
        if row is None:
            continue
        used = min(target, ONE_LEG_CEILING_S) if row["test"] == "one_leg" else target
        place = quintile(row["test"], sex, used)
        to_hr = AHR_SEX[sex][row["test"]][place["q"] - 1][0]
        out["levers"].append({
            "key": key, "label_zh": row["label"], "unit": row["unit"], "from": row["value"], "to": target,
            "quintile_from": row["q"], "quintile_to": place["q"],
            "ahr_sex_from": row["ahr_sex"][0], "ahr_sex_to": to_hr, "ahr_sex_delta": round(to_hr - row["ahr_sex"][0], 2),
        })
    out["levers"].sort(key=lambda item: item["ahr_sex_delta"])
    return out


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex: str | None,
                 targets: Path | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        stale = out_dir / name
        if stale.exists():
            stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = read_inputs(measurements, manifest)
    problems = list(collected.problems)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if person_sex is None:
        if sex:
            problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex}”，请写男或女。五分位男女分开。"))
        else:
            problems.append(skillkit.Problem("sex", "性别", "missing", "需要性别（男或女）：论文的五分位和风险比男女分开。"))
    test_keys = [key for _t, key, *_ in TESTS]
    if not any(key in collected.values for key in test_keys) and not any(p.key in test_keys for p in problems):
        problems.append(skillkit.Problem(
            "step_2min_count", "体适能测试成绩", "missing",
            "没有读到任何一项体适能成绩。至少交一项：2 分钟原地抬膝踏步、30 秒手臂弯举、30 秒椅子坐立、抓背、椅子坐姿体前弯、睁眼单脚站立、8 英尺起身绕行。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    rows = assess(dict(collected.values), person_sex)
    missing = [label for _t, key, label, *_ in TESTS if key not in collected.values]
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(rows, person_sex, age, missing)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, result_values(rows))
    wanted: dict = {}
    if targets is not None:
        wanted = dict(read_inputs(targets, manifest).values)
    (out_dir / "levers.json").write_text(json.dumps(levers(rows, person_sex, wanted), ensure_ascii=False, indent=1) + "\n",
                                         encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit：七项体适能成绩，至少一项")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--targets", type=Path, help="同样列的目标成绩表，写 out/levers.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex, args.targets)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
