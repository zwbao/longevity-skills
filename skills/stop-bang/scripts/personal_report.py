"""Offline 2008 STOP and STOP-Bang counts and binary screening categories."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AGE_THRESHOLD, BMI_THRESHOLD, BOUNDARY, CATEGORY_ZH, COMPONENT_LABELS,
    HIGH_RISK_MIN, MAX_SCORE, NECK_THRESHOLD_CM, SEX_CODES, STOP_KEYS, VALIDATION_NOTE,
)

TITLE = "STOP / STOP-Bang 睡眠呼吸暂停筛查（2008 版）"


def classify(count, method):
    return "high" if count >= HIGH_RISK_MIN[method] else "low"


def calculate(values, age, male):
    scores = {key.replace("_binary", "_score"): int(values[key]) for key in STOP_KEYS}
    stop = sum(scores.values())
    scores.update({
        "bmi_score": int(values["bmi_kg_m2"] > BMI_THRESHOLD),
        "age_score": int(age > AGE_THRESHOLD),
        "neck_score": int(values["neck_circumference_cm"] > NECK_THRESHOLD_CM),
        "male_score": male,
    })
    bang = sum(scores.values())
    return {**scores, "stop_score": stop, "stop_bang_score": bang,
            "stop_category": classify(stop, "stop"),
            "stop_bang_category": classify(bang, "stop_bang")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="marker,value,unit 格式的 CSV")
    parser.add_argument("--age", help="实足年龄，单位岁；必需")
    parser.add_argument("--sex", help="原问卷的性别项，male/female 或 男/女；必需")
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
            "measurements", "测量表", "file", f"无法读取测量表，请提供 marker,value,unit 格式的 CSV：{exc}"
        )])
    problems = list(collected.problems)
    for key in STOP_KEYS:
        if key in collected.values and collected.values[key] not in (0, 1):
            label = skillkit.spec_by_key(manifest, key)["label_zh"]
            problems.append(skillkit.Problem(key, label, "category", f"{label}只能填 1（是）或 0（否）；不清楚时保持缺失。"))
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems.extend(skillkit.check_scalar(manifest, "age", age))
    except ValueError:
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄须为有限数值，单位岁。"))
    sex = args.sex.strip().casefold() if args.sex is not None else None
    if sex not in SEX_CODES:
        problems.append(skillkit.Problem("sex", "原问卷性别项", "missing" if sex is None else "category",
            "请确认原问卷性别项并填写 male/female 或 男/女；未知或无法套用原二元题项时，不能自动按非男性计分。"))
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values, age, SEX_CODES[sex])
    skillkit.write_result(args.out, manifest, outputs)
    answers = {key.replace("_binary", "_score"): "是" if collected.values[key] else "否" for key in STOP_KEYS}
    answers.update({
        "bmi_score": f"{collected.values['bmi_kg_m2']:g} kg/m²；阈值 >{BMI_THRESHOLD}",
        "age_score": f"{age:g} 岁；阈值 >{AGE_THRESHOLD}",
        "neck_score": f"{collected.values['neck_circumference_cm']:g} cm；阈值 >{NECK_THRESHOLD_CM}",
        "male_score": "男" if SEX_CODES[sex] else "女",
    })
    report = heading + ["## 你的结果", ""]
    for method, label in (("stop", "STOP"), ("stop_bang", "STOP-Bang")):
        report += [f"{label}：**{outputs[method + '_score']} / {MAX_SCORE[method]}**；"
                   f"2008 版筛查分档：**{CATEGORY_ZH[outputs[method + '_category']]}**。", ""]
    report += [
        "| 项目 | 你的回答或测量 | 肯定项计数 |", "| --- | --- | --- |",
        *[f"| {label} | {answers[key]} | {outputs[key]} |" for key, label in COMPONENT_LABELS.items()],
        "", f"STOP 至少 {HIGH_RISK_MIN['stop']} 项回答是为高风险；"
        f"STOP-Bang 至少 {HIGH_RISK_MIN['stop_bang']} 项回答是为高风险。其余归入各自的低风险档。",
        "", "三个连续指标恰好等于阈值时均不计入肯定项。高血压正在治疗，即使当前血压正常，该题仍应回答是。",
        "", "高风险表示筛查阳性，可把结果交给主诊或术前评估医生进一步评估；"
        "低风险不能排除睡眠呼吸暂停，也不能当作手术许可。症状持续时仍需医学评估。",
        "", "原研究来自加拿大两家医院的成人术前门诊，排除了已确诊的睡眠呼吸障碍患者。"
        "已确诊者不应把此评分当作治疗效果监测；一般人群不能直接套用该队列的预测准确率。",
        "", VALIDATION_NOTE, "", f"边界: {BOUNDARY}", "",
    ]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
