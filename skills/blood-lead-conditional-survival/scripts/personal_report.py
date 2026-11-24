"""Offline log2 blood-lead contrasts, retaining all five reported imputations."""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BETAS, BOUNDARY, CAUTION, SCENARIO_NOTE, TITLE


def contrast(lead: float, reference: float) -> dict:
    if not all(math.isfinite(x) and x > 0 for x in (lead, reference)):
        raise ValueError("血铅与参考浓度必须为有限正数")
    log_ratio = math.log2(lead) - math.log2(reference)
    return {f"q{q}_i{i}_years": None if beta is None else beta * log_ratio
            for q, betas in BETAS.items() for i, beta in enumerate(betas, 1)}


def difference(after: dict, before: dict) -> dict:
    return {k: None if after[k] is None or v is None else after[k] - v
            for k, v in before.items()}


def make_levers(lead: float, reference: float, target: float | None) -> dict:
    current = contrast(lead, reference)
    slopes = {f"q{q}_i{i}_years": None if b is None else b / (lead * math.log(2))
              for q, bs in BETAS.items() for i, b in enumerate(bs, 1)}
    out = {
        "schema": "longevity-levers/1", "model": "blood-lead-conditional-survival",
        "model_zh": "血铅条件生存时间差（五次插补分别保留）",
        "reference_lead_ug_dl": reference, "current": current,
        "sensitivity": [{"key": "blood_lead_ug_dl", "label_zh": "全血铅",
                         "unit": "ug/dL", "value": lead, "years_per_unit": slopes}],
        "levers": [], "note_zh": SCENARIO_NOTE + CAUTION + BOUNDARY,
    }
    if target is not None:
        moved = contrast(target, reference)
        delta = difference(moved, current)
        out["levers"].append({"key": "blood_lead_ug_dl", "label_zh": "全血铅",
                              "unit": "ug/dL", "from": lead, "to": target,
                              "outputs": moved, "delta": delta})
        out["targets"] = {"values": {"blood_lead_ug_dl": target}, "outputs": moved, "delta": delta}
    return out


def collect(path: Path | None, manifest: dict) -> skillkit.Collected:
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "测量文件", "file", f"无法读取测量表：{exc}")])
    for name in result.unmatched:
        result.problems.append(skillkit.Problem(name, name, "unknown", f"无法识别项目「{name}」；请只提供所需的全血铅和参考浓度。"))
    return result


def table(values: dict) -> list[str]:
    lines = ["| 插补 | 第10百分位差（年） | 第25百分位差（年） | 第50百分位差（年） |",
             "|---|---:|---:|---:|"]
    for i in range(1, 6):
        cells = []
        for q in BETAS:
            value = values[f"q{q}_i{i}_years"]
            cells.append("不可估计（NE）" if value is None else f"{value:+.3f}")
        lines.append(f"| I{i} | " + " | ".join(cells) + " |")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="实足年龄；仅核查是否属于40岁及以上人群")
    parser.add_argument("--sex", help="可选上下文；相同协变量下的浓度差不需要性别系数")
    parser.add_argument("--targets", type=Path, help="仅全血铅目标浓度，marker,value,unit")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)
    collected = collect(args.measurements, manifest)
    problems = list(collected.problems)
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except (ValueError, TypeError):
        age = None
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄必须为数值。"))
    target = None
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        target_manifest["inputs"] = [s for s in target_manifest["inputs"] if s["key"] == "blood_lead_ug_dl"]
        wanted = collect(args.targets, target_manifest)
        problems += wanted.problems
        target = wanted.values.get("blood_lead_ug_dl")
    header = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding="utf-8").split("\n", 1)[1]
        report.write_text("\n".join(header) + "\n" + body, encoding="utf-8")
        skillkit.write_result(args.out, manifest, {o["key"]: None for o in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    lead = collected.values["blood_lead_ug_dl"]
    reference = collected.values["reference_lead_ug_dl"]
    values = contrast(lead, reference)
    lines = header + ["## 输入", "", f"年龄：{age:g} 岁（只检查适用年龄，不进入浓度差公式）。",
                      f"全血铅：{lead:g} µg/dL；用户指定参考浓度：{reference:g} µg/dL。",
                      "参考值仅为比较基准，不是安全阈值。输入范围用于检查单位和数值，不代表模型适用的暴露范围。",
                      "", "## 条件生存时间差", "", CAUTION, "",
                      "计算方向为当前浓度减参考浓度：β × log₂（当前浓度 / 参考浓度）。负数表示模型中的条件生存时间较短。",
                      "第10、25、50百分位指相同协变量条件下累计死亡比例达到10%、25%、50%的时间位置；不是你的死亡概率。",
                      "", *table(values), "",
                      "I1–I5 是论文五份插补数据的估计，不是五个人群，也未合并成一个估计。",
                      "不可估计项保持缺失；表格未给个人预测区间。原研究置信区间未包含插补间不确定性、复杂抽样方差与系统性偏倚。",
                      "这是主分析的对数线性浓度对比，不是图2的样条预测；极端暴露及美国研究人群以外的外推未经验证。"]
    levers = make_levers(lead, reference, target)
    if target is not None:
        lines += ["", "## 用户指定浓度情景", "", SCENARIO_NOTE,
                  f"假设全血铅为 {target:g} µg/dL，参考浓度仍为 {reference:g} µg/dL。",
                  "", *table(levers["targets"]["outputs"]), "",
                  "下表是目标情景减当前情景的模型变化（年）：", "", *table(levers["targets"]["delta"])]
    lines += ["", f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(args.out, manifest, values)
    (args.out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
