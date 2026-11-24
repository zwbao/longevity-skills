#!/usr/bin/env python3
"""Relative APOE dosage contrasts from printed joint longitudinal-hazard models."""

import argparse
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, INPUT_KEY, LABELS, MODELS, TITLE


def calculate(count, ancestry):
    if ancestry not in MODELS or count not in (0, 1, 2):
        raise ValueError("需要 EUR/AFR/AMR 模型和 0、1、2 整数拷贝数")
    return {f"hr_{term}": math.exp(beta * count)
            for term, beta in MODELS[ancestry]["beta"].items()}


def problem(key, label, kind, message):
    return skillkit.Problem(key, label, kind, message)


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--ancestry", help="明确选择研究模型 EUR、AFR 或 AMR；不自动推定")
    parser.add_argument("--age", help="可选年龄，仅用于说明适用范围，不改变风险比")
    parser.add_argument("--sex", help="可选上下文：female、male、unknown；不改变风险比")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "problems.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)

    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError) as exc:
        collected = skillkit.Collected(problems=[problem(
            INPUT_KEY, "APOE ε4 拷贝数", "file", f"无法读取测量表：{exc}")])
    problems = list(collected.problems)
    count = collected.values.get(INPUT_KEY)
    if count is not None and count not in (0, 1, 2):
        problems.append(problem(INPUT_KEY, "APOE ε4 拷贝数", "category",
                                "只接受已确认的 0、1 或 2 拷贝整数，不接受插补剂量或未知状态。"))
    if args.ancestry not in MODELS:
        problems.append(problem("ancestry", "研究祖源模型", "missing" if args.ancestry is None else "category",
                                "需明确选择研究中的 EUR、AFR 或 AMR 模型；东亚或未知祖源没有可用系数，不能自动套用。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(problem("age", "年龄", "parse", "年龄需要有限的数字，单位为岁。"))
    if args.sex is not None and args.sex not in ("female", "male", "unknown"):
        problems.append(problem("sex", "性别上下文", "category", "性别上下文只接受 female、male 或 unknown。"))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    count = int(count)
    model = MODELS[args.ancestry]
    values = calculate(count, args.ancestry)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 本次结果", "",
             f"输入为 APOE ε4 {count} 拷贝；选择 {model['label']}，来源 {model['table']}。",
             "比较对象为同一研究模型中 APOE ε4 为 0 拷贝、其他协变量相同的参照。",
             "结果是瞬时发生率之比（HR），没有时间范围对应的绝对患病概率。", "",
             "| 模型关联 | 按输入拷贝数计算的 HR |", "|---|---:|"]
    for term, label in LABELS.items():
        lines.append(f"| {label} | {values[f'hr_{term}']:.3f} |")
    lines += ["", "各路径不能相加为患病概率；总关联使用论文单独印出的总系数。",
              "剩余直接关联不是已证实的生物学作用，路径分解也不证明因果关系。",
              "若输入为 0 拷贝，所有比值为参照值 1，不表示不会发生失智。", "",
              "## 研究估计的不确定性", "",
              "下表是原文每增加 1 拷贝的 95% 置信区间，属于研究估计；不是你的个人预测区间，也未按本次拷贝数变换。", "",
              "| 模型关联 | 原文每拷贝 HR 的 95% 置信区间 |", "|---|---:|"]
    for term, label in LABELS.items():
        low, high = model["ci_per_allele"][term]
        lines.append(f"| {label} | {low:.2f}–{high:.2f} |")
    lines += ["", "区间包含 1 的关联，研究没有明确排除无关联；不能把不显著解释为无风险。",
              "## 适用范围", "",
              "研究纳入美国中老年人，使用 HRS 的算法性失智判定。这里不拟合个人认知轨迹、不生成多基因评分、不计算终生或若干年风险。",
              "祖源是所选研究模型的标签，不能根据中文报告、国籍或肤色推断。东亚人群和其他未建模祖源不适用。",
              "ε4 拷贝数是遗传状态，不能作为生活方式目标；这些结果不能估计治疗或改变行为的收益。",
              "年龄和性别仅作上下文；论文已在拟合时调整年龄、测量年份、性别和遗传主成分，这里不重新调整。"]
    if age is not None and not (50 < age <= 107):
        lines += ["", "提供的年龄不在正文所述大于 50 岁且表 S11 最大 107 岁的研究范围内；结果仅是模型算术演示。"]
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, {**values, "model_ancestry": args.ancestry,
                                              INPUT_KEY: count})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
