#!/usr/bin/env python3
"""FIB-4 personal readout; standard library only, offline after installation."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    ADVANCED_CUTS, MODERATE_ADVANCED_CUTS, BOUNDARY, ENTRY_PLATELET_MIN,
    MIN_AGE_EXCLUSIVE, OBSERVED_INDEX_RANGE, band, fib4,
)

TITLE = "FIB-4 肝纤维化指数"


def with_card(text):
    lines = text.splitlines()
    return "\n".join([lines[0], "", *paper_card_lines(), "", *lines[1:]]) + "\n"


def evaluate(values, age):
    index = fib4(age, values["ast_u_l"], values["platelets_10e9_l"], values["alt_u_l"])
    return {
        "fib4_index": index,
        "advanced_fibrosis_band": band(index, ADVANCED_CUTS),
        "moderate_advanced_fibrosis_band": band(index, MODERATE_ADVANCED_CUTS),
    }


def band_text(category, cuts):
    lower, upper = cuts
    return {
        "low": f"低值区（≤{lower:g}）",
        "indeterminate": f"不确定区（>{lower:g} 且 <{upper:g}）",
        "high": f"高值区（≥{upper:g}）",
    }[category]


def report(values, age, result, unmatched):
    index = result["fib4_index"]
    primary = result["advanced_fibrosis_band"]
    interpretations = {
        "low": "在原研究人群中，低值区用于辅助排除进展期纤维化，但仍可能漏掉病例；不能据此认定肝脏没有问题。",
        "indeterminate": "这个指数位于原研究的不确定区，单凭 FIB-4 无法区分是否存在进展期纤维化。",
        "high": "在原研究人群中，高值区提示需关注进展期纤维化的可能性，但不能据此确定纤维化分期。",
    }
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
             f"FIB-4 指数：**{index:.6f}**。",
             f"表 5A：{band_text(primary, ADVANCED_CUTS)}。这一组切点对应 Ishak 0–3 与 4–6 的区分。",
             interpretations[primary],
             "请结合既往病史与其他检查，由医生判断这些切点是否适用于你及是否需要进一步评估。",
             "", "## 输入与适用范围", "",
             f"采血时年龄：{age:g} 岁；AST：{values['ast_u_l']:g} U/L；"
             f"ALT：{values['alt_u_l']:g} U/L；血小板：{values['platelets_10e9_l']:g} ×10⁹/L。",
             "请使用同次采血的结果。上述化验本身不能确认 HIV/HCV 共感染、ALT 持续升高或肝病代偿状态；"
             "本报告仅对照原研究切点，没有自动确认你符合原研究入组条件。",
             "原研究要求此前一年内至少两次 ALT 升高；ALT 正常、肝功能失代偿及未满足其他入组条件者，不能套用原研究的诊断表现。"]
    if values["platelets_10e9_l"] < ENTRY_PLATELET_MIN:
        lines += [f"本次血小板低于原研究入组下限 {ENTRY_PLATELET_MIN:g} ×10⁹/L，已超出该入组条件；指数仍按公式给出。"]
    if not OBSERVED_INDEX_RANGE[0] <= index <= OBSERVED_INDEX_RANGE[1]:
        lines += [f"本次指数超出论文报告的观测范围 {OBSERVED_INDEX_RANGE[0]:g}–{OBSERVED_INDEX_RANGE[1]:g}；未截断结果，原研究表现不能据此外推。"]
    if unmatched:
        lines += ["未用于计算的项目：" + "、".join(unmatched) + "。"]
    lines += ["", "## 原文的另一组切点", "",
              f"表 5B：{band_text(result['moderate_advanced_fibrosis_band'], MODERATE_ADVANCED_CUTS)}。"
              "这组切点对应 Ishak 0–1 与 2–6 的区分，验证表现弱于表 5A；两组不能混用，也不表示你属于某个确诊分期。",
              "", "分档使用未四舍五入的指数；显示值接近切点时，以区间文字为准。",
              "该指数评估的是现患纤维化相关信号，不衡量衰老速度，也不是干预目标；不能把公式变化解释成健康改善。",
              "", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV/TSV: item,value,unit，AST、ALT、血小板计数")
    parser.add_argument("--age", help="采血时年龄（岁）")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "problems.json"):
        (args.out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, AttributeError) as exc:
        collected = skillkit.Collected()
        collected.problems.append(skillkit.Problem(
            "measurements", "化验表", "file", f"无法读取化验表：{exc}。请提供 item,value,unit 格式的 CSV/TSV。"))
    problems = list(collected.problems)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except (ValueError, OverflowError):
        problems.append(skillkit.Problem("age", "采血时实足年龄", "parse", "年龄需要是以岁为单位的有限数值。"))
    else:
        problems += skillkit.check_scalar(manifest, "age", age)
        if age == MIN_AGE_EXCLUSIVE:
            problems.append(skillkit.Problem("age", "采血时实足年龄", "range", "原研究要求年龄大于 18 岁，本技能不用于 18 岁及以下者。"))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        path.write_text(with_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(path)
        return skillkit.EXIT_INPUT_PROBLEM
    result = evaluate(collected.values, age)
    path = args.out / "report.md"
    path.write_text(report(collected.values, age, result, collected.unmatched), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
