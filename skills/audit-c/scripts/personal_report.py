"""Offline scoring of the original three AUDIT consumption questions."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, CUTOFFS, DRINK_NOTE, LABELS, MAX_SCORE, OPTIONS_ZH, POINTS

TITLE = "AUDIT-C 饮酒筛查"


def item_points(question, response_code):
    if isinstance(response_code, bool) or int(response_code) != response_code:
        raise ValueError("选项编码必须是整数")
    code = int(response_code)
    if not 0 <= code < len(POINTS[question]):
        raise ValueError("选项编码超出范围")
    return POINTS[question][code]


def screens(total):
    return {f"screen_ge{cutoff}": "positive" if total >= cutoff else "negative"
            for cutoff in CUTOFFS}


def calculate(values):
    scores = {f"{q}_score": item_points(q, values[f"{q}_response_code"]) for q in POINTS}
    total = sum(scores.values())
    return {**scores, "audit_c_total_score": total, **screens(total)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选年龄（岁），不改变计分")
    parser.add_argument("--sex", help="male/female/other/unknown 或 男/女/其他/未知")
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
            "measurements", "问卷回答表", "file", f"无法读取问卷回答表：{exc}")])
    problems = list(collected.problems)
    for key, value in collected.values.items():
        if not value.is_integer():
            problems.append(skillkit.Problem(key, key, "integer", "请填写选项表中的整数编码，不是频率、杯数或小数。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须为有限数值（岁）。"))
    sex = (args.sex or "unknown").casefold()
    if sex not in {"male", "female", "other", "unknown", "男", "女", "其他", "未知"}:
        problems.append(skillkit.Problem("sex", "性别", "category", "性别请填男、女、其他或未知。"))
    if not problems:
        q1, q2, q3 = (collected.values[f"q{i}_response_code"] for i in (1, 2, 3))
        if (q1 == 0 and (q2 != 0 or q3 != 0)) or (q1 > 0 and q2 == 0):
            problems.append(skillkit.Problem("q1_response_code", "饮酒回答一致性", "inconsistent",
                "过去一年从不饮酒与饮酒日杯数、单次至少六杯频率的回答不一致，请核对；不会自动改写回答。"))
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values)
    skillkit.write_result(args.out, manifest, outputs)
    report = heading + ["## 你的结果", "",
        f"总分：**{outputs['audit_c_total_score']} / {MAX_SCORE}**。", "",
        "| 项目 | 你的回答 | 得分 |", "| --- | --- | --- |"]
    for q in POINTS:
        answer = OPTIONS_ZH[q][int(collected.values[f"{q}_response_code"])]
        report.append(f"| {LABELS[q]} | {answer} | {outputs[q + '_score']} |")
    report += ["", "两个切点是本研究对同一男性样本评估的不同筛查选择，不是男女分界：", ""]
    for cutoff in CUTOFFS:
        status = "达到（筛查阳性）" if outputs[f"screen_ge{cutoff}"] == "positive" else "未达到（筛查阴性）"
        report.append(f"- ≥{cutoff} 分：{status}。")
    report += ["", "达到切点提示需要进一步了解饮酒及相关问题，不能据此确诊；未达到也不代表饮酒安全或排除问题。",
               "", DRINK_NOTE, "",
               "研究对象为美国退伍军人门诊的男性饮酒者；第三题保持原版单次至少六杯，不替换成其他版本的题干。"]
    if sex in {"female", "other", "女", "其他"}:
        report += ["", "本研究未验证你所属性别人群的筛查性能；此处仅展示原版分数与研究切点的数值比较。"]
    elif sex in {"unknown", "未知"}:
        report += ["", "未提供性别，无法确认是否符合男性验证样本；此处仅展示原版分数与研究切点的数值比较。"]
    if outputs["audit_c_total_score"] == 0:
        report += ["", "原验证分析排除了过去一年饮酒总量不足入组要求者；零分是量表可计算端点，不是该人群的验证证据。"]
    report += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
