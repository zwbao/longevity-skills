#!/usr/bin/env python3
"""Record a clinician-selected original CFS descriptor as its printed grade."""

import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, DESCRIPTORS

TITLE = "原版七级临床衰弱量表报告"


def with_card(text):
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="临床人员选定的完整描述，CSV item,value,unit；选中值为 1，单位为 1")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    manifest = skillkit.load_manifest(__file__)
    (out / "problems.json").unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "临床评估文件", "file", f"无法读取评估文件：{exc}")])
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem("descriptor", "临床描述", "unknown",
                                        f"无法识别“{name}”。请提供原版量表的完整描述选项；不接受新版分数或症状清单。"))
    for key, value in collected.values.items():
        if value not in (0, 1):
            problems.append(skillkit.Problem(key, DESCRIPTORS[key]["label_zh"], "selection",
                                            "选项值只能是 0（未选）或 1（选中），不能填写概率或小数。"))
    selected = [key for key, value in collected.values.items() if value == 1]
    if not problems and len(selected) != 1:
        problems.append(skillkit.Problem("descriptor", "临床描述", "missing" if not selected else "selection",
                                        "需要临床人员综合评估后确认一个完整描述，且只能选一个；不能用缺项代替评估或将多个描述加分。"))
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        path.write_text(with_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out, manifest, {s["key"]: None for s in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM

    item = DESCRIPTORS[selected[0]]
    report = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
              f"按你提供的临床评估描述，对应原版量表 **{item['grade']} 级：{item['label_zh']}**。",
              "", f"描述：{item['description_zh']}", "",
              "这是对已确认临床描述的等级映射。选择完整描述需要病史、查体及功能评估，不能仅凭单项症状或一次自评决定。",
              "", "原版最高等级同时涵盖完全依赖和终末期疾病两类情形；仅凭等级不能判断是哪一种，也不由软件推断终末期。",
              "", "本量表在加拿大健康与老龄化研究（CSHA）2305 名 65 岁及以上老年人中验证（1996 年评估、约 5 年随访死亡与入住照护机构），样本偏向认知受损及机构居住者；不能将本量表当作年轻人或急性病情变化的自动评估工具。",
              "", "等级之间不是等距的健康损失，论文中的队列风险关联不代表改变等级会改变个人结局。",
              "", f"边界: {BOUNDARY}"]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    skillkit.write_result(out, manifest, {
        "cfs7_grade": item["grade"], "cfs7_category": item["label_zh"],
        "cfs7_description": item["description_zh"],
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
