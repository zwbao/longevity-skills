"""Offline, exact lookup of printed genotype associations; standard library."""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (TITLE, BOUNDARY, AGE_MIN_EXCLUSIVE, AGE_SANITY_MAX,
                     SURVIVAL_AGE_MAX_EXCLUSIVE, ANCESTRY_MIN_EXCLUSIVE,
                     GENOTYPES, GROUPS, ANCESTRIES, SEX_LABELS)


def load_rows():
    return json.loads((Path(__file__).resolve().parents[1] / "data/associations.json").read_text())


def normalize_genotype(raw):
    if raw is None:
        return None
    text = unicodedata.normalize("NFKC", raw).strip().lower()
    text = re.sub(r"^apoe\s*", "", text)
    text = re.sub(r"[εϵe*\s]", "", text)
    if re.fullmatch(r"[234]/?[234]", text):
        genotype = "".join(sorted(text.replace("/", "")))
        if genotype in GENOTYPES:
            return genotype
    raise ValueError("请提供已确认的两个 APOE 等位基因，如 ε3/ε4、3/4 或 34；不能只写‘携带 ε4’，也不能由单个 SNP 猜测。")


def problem(key, text, kind="invalid"):
    return skillkit.Problem(key, key, kind, text)


def fail(out, manifest, issues):
    path = skillkit.write_problems(out, issues, TITLE, BOUNDARY)
    first, rest = path.read_text().split("\n", 1)
    path.write_text(first + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest, encoding="utf-8")
    skillkit.write_result(out, manifest, {spec["key"]: None for spec in manifest["outputs"]})
    return skillkit.EXIT_INPUT_PROBLEM


def lookup(analysis, group, sex, genotype):
    matched_genotype = "22+23" if group == "east_asian" and genotype in ("22", "23") else genotype
    for row in load_rows():
        if (row["analysis"], row["group"], row["sex"], row["genotype"]) == (analysis, group, sex, matched_genotype):
            if row["status"] == "unestimable":
                raise ValueError("eTable 16 该组合印为 0.00 [0.00, Inf]，无法提供可靠的有限估计；不能解释为零风险。")
            return row
    raise ValueError("原表没有这个分析、人群、性别与基因型组合，不能插值或借用其他分组。")


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--genotype", help="已确认的 APOE 双等位基因型，如 3/4")
    parser.add_argument("--age", help="当前年龄，岁；仅适用范围检查")
    parser.add_argument("--sex", help="male/female/pooled；pooled 明确请求男女合并")
    parser.add_argument("--analysis", default="case-control", help="case-control/survival/ancestry")
    parser.add_argument("--group", help="nhw/nhb/hispanic/east_asian；祖源模式不填")
    parser.add_argument("--ancestry", help="祖源模式：european/african/amerindian")
    parser.add_argument("--measurements", type=Path, help="祖源模式的比例 CSV：marker,value,unit")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "report.md", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    issues = []
    genotype = None
    try:
        genotype = normalize_genotype(args.genotype)
        if genotype is None:
            issues.append(problem("genotype", "缺少已确认的 APOE 基因型。", "missing"))
    except ValueError as exc:
        issues.append(problem("genotype", str(exc)))
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        issues.extend(skillkit.check_scalar(manifest, "age", age))
        if age is not None and not AGE_MIN_EXCLUSIVE < age <= AGE_SANITY_MAX:
            issues.append(problem("age", "本工具仅查询年龄大于 55 岁的人群关联；年龄不得超过输入质量检查上限 120 岁。", "not_applicable"))
    except (ValueError, TypeError):
        issues.append(problem("age", "年龄需为有限数值，单位为岁。"))
    if args.analysis not in ("case-control", "survival", "ancestry"):
        issues.append(problem("analysis", "分析接受 case-control/survival/ancestry。"))
    if args.sex not in SEX_LABELS:
        issues.append(problem("sex", "请明确选 male、female 或 pooled（男女合并），不默认推断性别。", "missing" if args.sex is None else "invalid"))
    values = {}
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
        values = collected.values
        issues.extend(collected.problems)
        issues.extend(problem("measurements", f"未识别项目：{name}。") for name in collected.unmatched)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        issues.append(problem("measurements", f"无法读取祖源比例文件：{exc}"))
    group = args.group
    if args.analysis == "ancestry":
        group = args.ancestry
        if group not in ANCESTRIES:
            issues.append(problem("ancestry", "需要报告明确给出的祖源类型：european/african/amerindian。", "missing" if group is None else "invalid"))
        if args.group is not None:
            issues.append(problem("group", "祖源模式使用 eTable 16，不接受种族／族裔分组叠加。"))
        if args.sex != "pooled":
            issues.append(problem("sex", "eTable 16 只有男女合并值，请明确选 pooled；无法作性别分层。", "not_applicable"))
        if "ancestry_percent" not in values:
            issues.append(problem("ancestry_percent", "需要全基因组祖源报告中的比例，CSV 单位为 %；不能由种族、语言或出生地推断。", "missing"))
        elif values["ancestry_percent"] <= ANCESTRY_MIN_EXCLUSIVE:
            issues.append(problem("ancestry_percent", "eTable 16 要求该祖源严格超过 75%；恰为 75% 或较低值不外推。", "not_applicable"))
    else:
        if group not in GROUPS:
            issues.append(problem("group", "请明确选择研究分组 nhw/nhb/hispanic/east_asian；不能自动推断或把中国样本当作日、韩样本。", "missing" if group is None else "invalid"))
        if args.ancestry is not None or args.measurements is not None:
            issues.append(problem("analysis", "祖源比例只用于 ancestry 模式，不能乘到种族／族裔结果中。"))
        if group == "east_asian" and (args.sex != "pooled" or args.analysis != "case-control"):
            issues.append(problem("group", "东亚原表仅有男女合并 OR，没有性别分层或 HR。", "not_applicable"))
        if args.analysis == "survival" and age is not None and age >= SURVIVAL_AGE_MAX_EXCLUSIVE:
            issues.append(problem("age", "生存分析排除了年龄仅记录为 90+ 的个体；本工具保守地不向 90 岁及以上者提供 HR。", "not_applicable"))
    if issues:
        return fail(args.out, manifest, issues)
    try:
        row = lookup(args.analysis, group, args.sex, genotype)
    except ValueError as exc:
        return fail(args.out, manifest, [problem("combination", str(exc), "not_applicable")])
    result = {key: row[key] for key in ("effect", "ci_low", "ci_high", "effect_type")}
    result.update(genotype_stratum=row["genotype"], reference_genotype="33", source=row["source"],
                  population_stratum=group, sex_stratum=args.sex, age_stratum="not_age_stratified")
    skillkit.write_result(args.out, manifest, result)
    group_label = (ANCESTRIES if args.analysis == "ancestry" else GROUPS)[group]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的输入", "",
             f"已确认基因型：APOE ε{genotype[0]}/ε{genotype[1]}；年龄：{age:g} 岁。",
             f"选择的研究分组：{group_label}；性别分层：{SEX_LABELS[args.sex]}。"]
    if args.analysis == "ancestry":
        lines += [f"报告给出的该全基因组祖源比例：{values['ancestry_percent']:g}%；使用原表严格 >75% 分组。",
                  "祖源比例与自报种族／族裔不是同一个量；本结果不是性别与祖源联合分层。"]
    lines += ["", "## 对应研究组的关联", "",
              f"来源：{row['source']}；基因型行：APOE*{row['genotype']}；参照：同一分层的 APOE ε3/ε3。",
              "年龄未分层：年龄仅检查适用范围，数值不是这个岁数的风险估计。"]
    if row["status"] == "reference":
        lines += [f"{row['effect_type']} = 1（参照定义）；原表未提供参照行置信区间。这不表示不会患病。"]
    else:
        lines += [f"人群 {row['effect_type']}：{row['effect']:.2f}；95% 置信区间：{row['ci_low']:.2f}–{row['ci_high']:.2f}。",
                  "置信区间描述研究组关联估计的不确定性，不是个人风险范围。"]
    if row["genotype"] == "22+23":
        lines += ["东亚 ε2/ε2 与 ε2/ε3 合并报告，不能将此值解释为其中一个基因型的独立估计。"]
    if group == "east_asian":
        lines += ["东亚结果来自日本和韩国样本，不能直接当作中国人群的专属估计；原资料缺少完整人口学分层。"]
    if args.analysis == "survival":
        lines += ["HR 是以发病年龄为时间尺度的危险比；研究主要利用混合来源数据，并非从你当前年龄开始的前瞻性预测。"]
    else:
        lines += ["OR 是病例对照的优势比，不等于风险比；不能把它乘以一个自行选择的基线患病率。",
                  "原病例对照分析未作年龄协变量调整；其他协变量和入组方式见来源合同。"]
    lines += ["论文没有用于此查询的完整基线风险或生存函数，不能计算个人绝对概率、发病时间、寿命或认知下降速度。",
              "这些关联受招募方式和人群构成影响；不能通过改变祖源、性别或基因型设置健康目标。",
              "", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
