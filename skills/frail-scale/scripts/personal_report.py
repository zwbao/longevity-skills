"""Offline FRAIL questionnaire scoring with manifest-driven input validation."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY, CATEGORY_ZH, COMPONENT_LABELS, FATIGUE_LABELS,
    FATIGUE_POSITIVE_CODES, FRAIL_MIN_SCORE, ILLNESS_THRESHOLD, INTEGER_KEYS,
    MAX_SCORE, PERCENT_FACTOR, VALIDATION_AGE_YEARS, WEIGHT_LOSS_THRESHOLD_PCT,
    WEIGHT_RULE_NOTE,
)

TITLE = "FRAIL 衰弱问卷"


def illness_points(count):
    return int(count >= ILLNESS_THRESHOLD)


def fatigue_points(code):
    return int(code in FATIGUE_POSITIVE_CODES)


def weight_loss_percent(current, previous):
    # Decimal avoids subtraction noise at the printed boundary.
    current, previous = Decimal(str(current)), Decimal(str(previous))
    return (previous - current) / previous * PERCENT_FACTOR


def classify(total):
    if total == 0:
        return "robust"
    return "frail" if total >= FRAIL_MIN_SCORE else "prefrail"


def calculate(values):
    loss = weight_loss_percent(values["weight_current_kg"], values["weight_year_ago_kg"])
    scores = {
        "fatigue_score": fatigue_points(values["fatigue_response_code"]),
        "resistance_score": int(values["resistance_difficulty_binary"]),
        "ambulation_score": int(values["ambulation_difficulty_binary"]),
        "illnesses_score": illness_points(values["illnesses_count"]),
        "weight_loss_score": int(loss >= WEIGHT_LOSS_THRESHOLD_PCT),
    }
    total = sum(scores.values())
    return {**scores, "weight_loss_pct": float(loss),
            "frail_total_score": total, "frail_category": classify(total)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选实足年龄，只用于适用人群提示")
    parser.add_argument("--sex", help="可选 male/female/other/unknown 或 男/女/其他/未知，不影响计分")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "测量表", "file", f"测量表无法读取，请提供 marker,value,unit 格式的 CSV：{exc}"
        )])
    problems = list(collected.problems)
    for key in INTEGER_KEYS:
        if key in collected.values and not collected.values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                                             f"{spec['label_zh']}必须填写规定范围内的整数。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄必须是有限数值（岁）。"))
    if args.sex is not None and args.sex.casefold() not in {
        "male", "female", "other", "unknown", "男", "女", "其他", "未知"
    }:
        problems.append(skillkit.Problem("sex", "性别", "category", "性别请填男、女、其他或未知，也可不提供。"))
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values)
    skillkit.write_result(args.out, manifest, outputs)
    rows = [
        ("fatigue_score", FATIGUE_LABELS[int(collected.values["fatigue_response_code"])]),
        ("resistance_score", "是" if collected.values["resistance_difficulty_binary"] else "否"),
        ("ambulation_score", "是" if collected.values["ambulation_difficulty_binary"] else "否"),
        ("illnesses_score", f"{int(collected.values['illnesses_count'])} 种"),
        ("weight_loss_score", f"{outputs['weight_loss_pct']:.6g}%（正数为下降，负数为增加）"),
    ]
    report = heading + [
        "## 你的结果", "",
        f"FRAIL 总分：**{outputs['frail_total_score']} / {MAX_SCORE}**；筛查分层："
        f"**{CATEGORY_ZH[outputs['frail_category']]}**。", "",
        "| 项目 | 你的回答或测量 | 得分 |", "| --- | --- | --- |",
        *[f"| {COMPONENT_LABELS[key]} | {answer} | {outputs[key]} |" for key, answer in rows],
        "", "“健壮”仅是本问卷的分档名称，不表示没有疾病。", "", WEIGHT_RULE_NOTE, "",
        "体重变化按穿衣、不穿鞋的当前体重与一年前体重计算；缺项不能按没有症状处理。", "",
        "研究的验证人群为美国圣路易斯社区非裔成年人；它没有建立适用于任意人群的个人死亡概率计算器。",
    ]
    if age is not None and not VALIDATION_AGE_YEARS[0] <= age <= VALIDATION_AGE_YEARS[1]:
        report += ["", f"你提供的年龄不在本研究基线年龄范围 {VALIDATION_AGE_YEARS[0]}–{VALIDATION_AGE_YEARS[1]} 岁内；计分规则照用，适用性证据有限。"]
    report += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
