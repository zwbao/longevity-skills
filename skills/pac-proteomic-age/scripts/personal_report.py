#!/usr/bin/env python3
"""Personal PAC proteomic age from Olink Explore NPX values.

PAC is Kuo et al., Aging Cell 2024: a Gompertz model of 10-year all-cause
mortality on age and 128 Olink proteins (UK Biobank Pharma Proteomics Project),
turned back into an age with the age-only Gompertz model. Zhavoronkov et al.,
Nature Biotechnology 2026 ran it, with five other clocks, on raw NPX of a
phase 2a trial and compared the change from baseline (ΔBioAge) between arms.

All 128 proteins are required, as in pac_proteomic_age.R: a missing protein is
not filled with 0 or a population mean. Checkup labs and current medicines are
context only; they do not change the inputs or the result.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BETA_AGE,
    BETA_AGE0,
    BOUNDARY,
    HORIZON_YEARS,
    PAC_PROTEIN_COEFFICIENTS,
    RATE,
    RATE0,
    SHAPE,
    SHAPE0,
    TITLE,
    TRAINING_AGE_RANGE,
    input_key,
)

# Units a lab export writes for NPX. They mean "the value is NPX", which is
# the input's own scale, so the row is read as is. Concentration units are left
# in place and refused by skillkit (they cannot be converted to NPX).
NPX_UNIT_WORDS = {"npx", "log2npx", "npx(log2)", "log2"}


def linear_predictor(npx: Dict[str, float], age: float) -> float:
    """b(x) of pac_proteomic_age.R: beta_age * age + sum(beta_i * NPX_i)."""
    xb = BETA_AGE * age
    for symbol, beta in PAC_PROTEIN_COEFFICIENTS:
        xb += beta * npx[input_key(symbol)]
    return xb


def cumulative_hazard_10y(xb: float) -> float:
    """-log(1 - cdf_10_year) of the 128-protein Gompertz model."""
    return RATE * math.exp(xb) / SHAPE * (math.exp(SHAPE * HORIZON_YEARS) - 1.0)


def mortality_10y(xb: float) -> float:
    """cdf_10_year in pac_proteomic_age.R (0-1): the model's 10-year mortality."""
    return -math.expm1(-cumulative_hazard_10y(xb))


def pac_age(npx: Dict[str, float], age: float) -> float:
    """PAC proteomic age, pac_proteomic_age.R:

    (1/beta_age0) * log(shape0 * log(1 - cdf) / (rate0 * (1 - exp(10 * shape0))))

    log(1 - cdf) is taken as minus the cumulative hazard, which is the same
    number without the round trip through cdf (stable when cdf is near 1).
    """
    hazard = cumulative_hazard_10y(linear_predictor(npx, age))
    inner = SHAPE0 * (-hazard) / (RATE0 * (1.0 - math.exp(HORIZON_YEARS * SHAPE0)))
    return math.log(inner) / BETA_AGE0


def _normalize_npx_units(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for row in rows:
        fixed = dict(row)
        for column in list(fixed):
            if skillkit.fold_name(column) in {"unit", "units", "单位"}:
                if skillkit.normalize_unit(fixed[column]).replace(" ", "") in NPX_UNIT_WORDS:
                    fixed[column] = ""
        out.append(fixed)
    return out


def collect_sample(path: Optional[Path], manifest: Dict, which: str) -> Tuple[Dict[str, float], List[skillkit.Problem], List[str]]:
    """The 128 NPX values of one sample, the problems that stop the run, and unmatched names."""
    if path is None:
        rows: List[Dict[str, str]] = []
    else:
        path = Path(path)
        if not path.exists():
            return {}, [skillkit.Problem("", "", "file", f"找不到{which}文件 {path}。")], []
        if path.suffix.lower() in {".xlsx", ".xls", ".pdf", ".parquet"}:
            return {}, [skillkit.Problem("", "", "format", f"{which}文件 {path.name} 不是表格文本。请导出成 CSV 或 TSV（列：marker,value,unit），每行一个 Olink 蛋白的 NPX。")], []
        rows = _normalize_npx_units(skillkit.read_rows(path))
    collected = skillkit.collect_measurements(rows, manifest)
    problems = list(collected.problems)
    missing = [p for p in problems if p.kind == "missing"]
    others = [p for p in problems if p.kind != "missing"]
    if missing:
        names = "、".join(p.label for p in missing)
        others.append(skillkit.Problem(
            "pac_128", "PAC 蛋白", "missing",
            f"{which}缺少 PAC 需要的 {len(missing)} 个蛋白：{names}。PAC 要 128 个蛋白全部齐全，缺的不用 0 或人群平均值代替；"
            "Olink Explore 3072（或含这些检测的 Explore 1536/HT）才有全部 128 项。",
        ))
    return collected.values, others, collected.unmatched


def _load_lines(path: Optional[Path]) -> List[str]:
    if path is None or not Path(path).exists():
        return []
    return [line.strip() for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def _fmt(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def build_report(age: float, values: Dict[str, float], result: Dict[str, Optional[float]],
                 baseline_age: Optional[float], medications: List[str], labs: List[str],
                 unmatched: int) -> str:
    pac = result["pac_age"]
    gap = result["pac_age_gap"]
    lines = [f"# {TITLE}", ""]
    lines += paper_card_lines()
    lines += ["", "## 输入", ""]
    lines.append(f"- 实足年龄：{_fmt(age)} 岁")
    extra = f"文件里另有 {unmatched} 行不是 PAC 用的蛋白，没有使用。" if unmatched else ""
    lines.append(f"- PAC 的 128 个 Olink 蛋白全部读到（NPX，原值直接代入，不做缩放）。{extra}")
    if result.get("baseline_pac_age") is not None:
        lines.append(f"- 基线样本：128 个蛋白齐全，基线年龄 {_fmt(baseline_age)} 岁")
    low, high = TRAINING_AGE_RANGE
    if not low <= age <= high:
        lines.append(f"- 注意：PAC 在 {low}–{high} 岁的人里拟合，你的年龄在这个范围外，结果是外推。")
    lines += ["", "## 你的结果", ""]
    lines.append(f"按 PAC 模型，你的蛋白质组年龄是 {_fmt(pac, 2)} 岁，比实足年龄{'大' if gap >= 0 else '小'} {_fmt(abs(gap), 2)} 岁。")
    lines.append(f"同一模型给出的 10 年全因死亡风险估计是 {_fmt(result['pac_mortality_10y_pct'], 2)}%；这是英国生物银行人群模型代入你的数后的数，不是对你本人的预测。")
    if result.get("pac_age_change") is not None:
        change = result["pac_age_change"]
        lines.append("")
        lines.append(f"基线样本的 PAC 蛋白质组年龄是 {_fmt(result['baseline_pac_age'], 2)} 岁；本次减基线是 {'+' if change >= 0 else ''}{_fmt(change, 2)} 岁"
                     f"（同期实足年龄增加 {_fmt(age - baseline_age, 2)} 岁）。论文把这个差叫 ΔBioAge。")
        lines.append("两份样本不在同一 Olink 批次时，这个差里混有批次偏移；同一批次测的前后两份最可比。")
    lines += ["", "## 怎么读", ""]
    lines.append("- PAC 是按死亡风险训练的时钟，不是按年龄训练的。论文的试验人群里，它与实足年龄只弱相关，基线时普遍比实足年龄小约 9–16 岁（各组中位数，补充表 3）；论文用的 Olink 数据也没有做跨批次桥接。所以单次结果的绝对值意义有限，同一个人、同一批次的前后变化更有参考价值。")
    lines.append("- 论文的试验对象是特发性肺纤维化患者（在中国招募的 42 名患者，平均 67.1 岁）。PAC 的蛋白里有 LTBP2、SPP1、KRT19 等纤维化相关蛋白，所以 PAC 的变化不能单独说明是衰老变慢还是某种疾病减轻。")
    lines.append("- 本报告只算 PAC。论文里另外五个时钟（ProtAge、OrganAge 的两个版本、ipfP3GPT、PAOPAC）的权重没有全部公开，或者需要按一批样本做标准化，这里不算。")
    if medications or labs:
        lines += ["", "## 你提供的其他信息", ""]
        if medications:
            lines.append(f"- 现用药（{len(medications)} 条）只作背景，不改变 PAC 结果；也不能据此停用或调整任何药物。")
        if labs:
            lines.append(f"- 体检结果（{len(labs)} 行）只作背景，不进入 PAC 公式。")
    lines += ["", f"边界: {BOUNDARY}", ""]
    return "\n".join(lines)


def write_report(out_dir: Path, measurements: Optional[Path], age: Optional[float],
                 baseline: Optional[Path] = None, baseline_age: Optional[float] = None,
                 medications: Optional[Path] = None, labs: Optional[Path] = None) -> int:
    manifest = skillkit.load_manifest(__file__)
    out_dir = Path(out_dir)
    values, problems, unmatched = collect_sample(measurements, manifest, "测量")
    problems += skillkit.check_scalar(manifest, "age", age)
    base_values: Dict[str, float] = {}
    if baseline is not None:
        base_values, base_problems, _ = collect_sample(baseline, manifest, "基线")
        for problem in base_problems:
            problem.message_zh = "基线样本：" + problem.message_zh if not problem.message_zh.startswith("基线") else problem.message_zh
        problems += base_problems
        if baseline_age is None:
            problems.append(skillkit.Problem("baseline_age", "基线采血时的年龄", "missing", "给了基线 NPX 文件，还需要 --baseline-age（基线采血那天的年龄）。"))
        else:
            problems += skillkit.check_scalar(manifest, "baseline_age", baseline_age)
            if age is not None and baseline_age > age:
                problems.append(skillkit.Problem("baseline_age", "基线采血时的年龄", "range", f"基线年龄 {baseline_age:g} 岁大于本次年龄 {age:g} 岁，请检查两份样本是否放反。"))
    if problems:
        skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        skillkit.write_result(out_dir, manifest, {key["key"]: None for key in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM

    pac = pac_age(values, age)
    result: Dict[str, Optional[float]] = {
        "pac_age": pac,
        "pac_age_gap": pac - age,
        "pac_mortality_10y_pct": 100.0 * mortality_10y(linear_predictor(values, age)),
        "baseline_pac_age": None,
        "pac_age_change": None,
    }
    if baseline is not None:
        base = pac_age(base_values, baseline_age)
        result["baseline_pac_age"] = base
        result["pac_age_change"] = pac - base
    text = build_report(age, values, result, baseline_age, _load_lines(medications), _load_lines(labs), len(unmatched))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text(text, encoding="utf-8")
    problems_file = out_dir / "problems.json"
    if problems_file.exists():
        problems_file.unlink()
    skillkit.write_result(out_dir, manifest, result)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV/TSV: marker,value,unit — Olink NPX，每行一个蛋白")
    parser.add_argument("--age", type=float, help="采这份血样那天的实足年龄（岁）")
    parser.add_argument("--baseline", type=Path, help="可选：同一个人更早一份样本的 NPX 文件，用来算前后变化")
    parser.add_argument("--baseline-age", type=float, dest="baseline_age", help="基线采血那天的年龄（岁）")
    parser.add_argument("--medications", type=Path, help="可选：现用药，每行一条（只作背景）")
    parser.add_argument("--labs", type=Path, help="可选：体检结果（只作背景）")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    code = write_report(args.out, args.measurements, args.age, args.baseline, args.baseline_age, args.medications, args.labs)
    print((args.out / "report.md").read_text(encoding="utf-8"))
    return code


if __name__ == "__main__":
    sys.exit(main())
