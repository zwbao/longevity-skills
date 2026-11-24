"""Score already administered EMFRA items; standard library only."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, ITEM_KEYS, ITEM_RANGE, OBSERVED_AGES,
                     OUTPUT_KEYS, THEORETICAL_MAXIMA, TITLE, WEIGHTS)


def compute(values):
    """SM sections 5.3 and 6: absolute weights after factor-specific reversal."""
    if any(key not in values or values[key] not in (0, 1, 2) for key in ITEM_KEYS):
        raise ValueError("需要九项原始 EMFRA 整数条目分数 0、1 或 2。")
    return {
        name: math.fsum(
            abs(weights[j]) * (ITEM_RANGE[1] - values[key] if weights[j] < 0 else values[key])
            for key, weights in WEIGHTS.items()
        )
        for j, name in enumerate(OUTPUT_KEYS)
    }


def front():
    return [f"# {TITLE}", "", *paper_card_lines(), ""]


def stop(out, manifest, problems):
    skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    # Overwrite earlier results if the same output directory is reused.
    skillkit.write_result(out, manifest, {key: None for key in OUTPUT_KEYS})
    body = skillkit.problems_markdown(problems, TITLE, BOUNDARY).split("\n", 2)[2]
    (out / "report.md").write_text("\n".join(front()) + "\n" + body, encoding="utf-8")
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="九项原始条目分数 CSV/TSV：marker,value,unit")
    parser.add_argument("--age", help="实足年龄（岁），仅核对适用人群")
    parser.add_argument("--sex", help="可选背景资料，不进入公式")
    parser.add_argument("--dementia-diagnosis", help="是否已有医生确诊痴呆：no / yes；不代表认知筛查结果")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    problems = []
    values = {}
    try:
        if args.measurements is not None and args.measurements.suffix.lower() not in (".csv", ".tsv"):
            problems.append(skillkit.Problem("measurements", "条目评分表", "format", "请提供 CSV 或 TSV 条目评分表；不直接读取 PDF、图片或 Excel。"))
        else:
            collected = skillkit.collect_file(args.measurements, manifest)
            values = collected.values
            problems.extend(collected.problems)
    except (OSError, UnicodeError, csv.Error, AttributeError) as error:
        problems.append(skillkit.Problem("measurements", "条目评分表", "file", f"无法读取条目评分表：{error}"))

    for spec in skillkit.input_specs(manifest):
        key = spec["key"]
        if key in values and values[key] not in (0, 1, 2):
            problems.append(skillkit.Problem(key, spec["label_zh"], "category", "EMFRA 原始条目分数只能是 0、1 或 2，不能填连续测量值或小数。"))

    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems.extend(skillkit.check_scalar(manifest, "age", age))
    except ValueError:
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄需要有限数值，单位为岁。"))

    dementia = (args.dementia_diagnosis or "").strip().lower()
    if dementia not in ("no", "yes"):
        problems.append(skillkit.Problem("dementia_diagnosis", "医生确诊痴呆情况", "missing" if not dementia else "category", "请确认是否已有医生确诊痴呆，并填写 --dementia-diagnosis no 或 yes；不能把未知当作没有。"))
    elif dementia == "yes":
        problems.append(skillkit.Problem("dementia_diagnosis", "医生确诊痴呆情况", "population", "研究未纳入已有医生确诊痴呆的人群，本技能不为这一人群生成个人分数。"))

    if problems:
        return stop(args.out, manifest, problems)

    scores = {key: round(value, 2) for key, value in compute(values).items()}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "problems.json").unlink(missing_ok=True)
    skillkit.write_result(args.out, manifest, scores)
    lines = front() + [
        "## 本次结果", "",
        f"自主性：**{scores['autonomy_score']:.2f} 分**。",
        f"心理困扰：**{scores['psychological_distress_score']:.2f} 分**。", "",
        "自主性分数较高表示该因子所描述的自主性较强；心理困扰分数较高表示该因子所描述的困扰较多。",
        f"两因子的理论范围分别为 0–{THEORETICAL_MAXIMA[0]:.2f} 和 0–{THEORETICAL_MAXIMA[1]:.2f} 分（显示至两位小数）。这些范围不是正常值或诊断界值。",
        "每个因子都使用全部九项；不能把两个分数相加，也不能把它们直接相减或比较大小来判断健康。", "",
        "研究尚未建立临床分档切点，也未证明这些分数能可靠判断一个人的随访变化；本次不判断正常、异常或改善。", "",
    ]
    if age > OBSERVED_AGES[1]:
        lines += [f"年龄提示：你超出研究实际年龄范围（{OBSERVED_AGES[0]}–{OBSERVED_AGES[1]} 岁），分数适用性尚未验证。", ""]
    lines += ["## 本次输入", "", "以下均为原版 EMFRA 评定后的原始条目分数（0、1、2）；反向计分由脚本完成。", "",
              "| 条目 | 原始分数 |", "| --- | ---: |"]
    lines += [f"| {spec['label_zh']} | {values[spec['key']]:.0f} |" for spec in skillkit.input_specs(manifest)]
    lines += ["", f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
