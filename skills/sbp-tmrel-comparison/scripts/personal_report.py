#!/usr/bin/env python3
"""Compare a supplied brachial SBP to the published GBD 2021 TMREL interval."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, SBP_KEY, TMREL_MMHG

TITLE = "收缩压与 GBD 2021 理论最低风险区间比较"
LABELS = {"below": "低于区间", "within": "位于区间内（含端点）", "above": "高于区间"}


def compare(sbp):
    lower, upper = TMREL_MMHG
    return {
        "sbp_mmhg": sbp,
        "tmrel_lower_mmhg": lower,
        "tmrel_upper_mmhg": upper,
        "difference_from_lower_mmhg": sbp - lower,
        "difference_from_upper_mmhg": sbp - upper,
        "position": "below" if sbp < lower else "above" if sbp > upper else "within",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "problems.json").unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
        problems = list(collected.problems)
    except (OSError, ValueError) as exc:
        problems = [skillkit.Problem(SBP_KEY, "肱动脉收缩压", "missing", f"测量文件无法读取：{exc}")]
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        rows = report.read_text(encoding="utf-8").splitlines()
        report.write_text("\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n", encoding="utf-8")
        skillkit.write_result(args.out, manifest, {o["key"]: None for o in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM

    r = compare(collected.values[SBP_KEY])
    rows = [f"# {TITLE}", "", *paper_card_lines(), "", "## 个人结果", "",
            f"你提供的肱动脉收缩压为 {r['sbp_mmhg']:g} mmHg。",
            f"论文参照区间：{r['tmrel_lower_mmhg']:g}–{r['tmrel_upper_mmhg']:g} mmHg；相对位置：{LABELS[r['position']]}。",
            f"与下端点之差：{r['difference_from_lower_mmhg']:+g} mmHg；与上端点之差：{r['difference_from_upper_mmhg']:+g} mmHg。",
            "差值按“你的测量值减端点”计算；正号表示高于该端点，负号表示低于该端点。", "",
            "## 如何理解", "",
            "论文以这个均匀分布表达群体疾病负担估计中最低风险暴露水平的不确定性。区间位置只描述数值关系，不是临床正常范围或危险程度分级。",
            "本报告只比较你提供的一个数值，不把单次读数换算成长期血压，也不进行年龄、性别或测量设备校正。",
            "验证状态：暂定；原文区间已核对，但尚无可复现的个人差值计算示例。", "",
            f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
