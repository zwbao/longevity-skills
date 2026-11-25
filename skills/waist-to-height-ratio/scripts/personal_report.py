"""Adult WHtR screening with manifest-driven units and explicit draft status."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, CATEGORY_LABELS, SCREENING_BOUNDARY, TARGET_NOTE, TITLE


def calculate(values):
    ratio = values["waist_cm"] / values["height_cm"]
    return {
        "waist_height_ratio": ratio,
        "screening_category": "below_boundary" if ratio < SCREENING_BOUNDARY else "at_or_above_boundary",
    }


def levers(values, targets):
    waist, height = values["waist_cm"], values["height_cm"]
    current = calculate(values)
    result = {
        "schema": "longevity-levers/1",
        "model": "waist_height_ratio",
        "model_zh": "成人腰围身高比（Ashwell 等，2012）",
        "current": current,
        "sensitivity": [
            {"key": "waist_cm", "label_zh": "腰围", "unit": "cm", "value": waist,
             "ratio_per_unit": 1 / height, "modifiable": True},
            {"key": "height_cm", "label_zh": "身高", "unit": "cm", "value": height,
             "ratio_per_unit": -waist / height ** 2, "modifiable": False},
        ],
        "levers": [],
        "note_zh": TARGET_NOTE,
    }
    if targets:
        changed = calculate({**values, **targets})
        delta = changed["waist_height_ratio"] - current["waist_height_ratio"]
        result["levers"] = [{
            "key": "waist_cm", "label_zh": "腰围", "unit": "cm", "from": waist,
            "to": targets["waist_cm"], "waist_height_ratio_delta": delta,
            **changed,
        }]
        result["targets"] = {"values": targets, **changed, "waist_height_ratio_delta": delta}
    return result


def collect(path, manifest, label):
    try:
        return skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(
            label, label, "file", f"无法读取{label}：{exc}。请提供 item,value,unit 格式的 CSV 或 TSV。",
        )])


def stop(out, manifest, problems):
    path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    body = path.read_text(encoding="utf-8").split("\n", 1)[1]
    path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
    skillkit.write_result(out, manifest, {s["key"]: None for s in manifest["outputs"]})
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="腰围、身高 CSV/TSV")
    parser.add_argument("--age", help="实足年龄，岁；仅用于成人适用性检查")
    parser.add_argument("--sex", help="可选：男/女、male/female；不改变计算")
    parser.add_argument("--targets", type=Path, help="可选：用户自定腰围目标，格式同测量表")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Reusing an output directory must never leave a stale successful readout.
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    collected = collect(args.measurements, manifest, "测量表")
    problems = list(collected.problems)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄必须是有限的数值，单位为岁。"))
    if args.sex is not None and args.sex.casefold() not in {"男", "女", "男性", "女性", "m", "f", "male", "female", "other", "unknown", "其他", "未知"}:
        problems.append(skillkit.Problem("sex", "性别", "parse", "性别可省略，或填写男、女、male、female、其他、未知；它不改变腰围身高比。"))
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        for spec in target_manifest["inputs"]:
            if spec["from"] == "measurements":
                spec["required"] = spec["key"] == "waist_cm"
        wanted = collect(args.targets, target_manifest, "目标表")
        problems += wanted.problems
        for name in wanted.unmatched:
            problems.append(skillkit.Problem("targets", "目标表", "unknown", f"目标表中的「{name}」不是可识别的腰围目标。"))
        if "height_cm" in wanted.values:
            problems.append(skillkit.Problem("height_cm", "身高", "target", "目标表只接受腰围；成人身高在情景计算中保持当前测量值。"))
        targets = {k: v for k, v in wanted.values.items() if k == "waist_cm"}
    if problems:
        return stop(args.out, manifest, problems)

    values = collected.values
    result = calculate(values)
    lever = levers(values, targets)
    category = result["screening_category"]
    text = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
            f"本次测量：腰围 {values['waist_cm']:g} cm；身高 {values['height_cm']:g} cm。",
            f"腰围身高比：**{result['waist_height_ratio']:.6f}**（无单位）。",
            f"与 {SCREENING_BOUNDARY:g} 界值相比：**{CATEGORY_LABELS[category]}**。分档使用未四舍五入的比值。", ""]
    if category == "below_boundary":
        text.append("本次比值低于这条筛查界线，不能由此排除高血压、糖尿病或其他心代谢问题。")
    else:
        text.append("本次比值已达到这条筛查界线。它提示需要结合血压、血糖、血脂及病史进一步评估，并不表示已经患病。")
    if age > manifest["population"]["age_years"][1]:
        text += ["", "年龄超出正文概述的研究年龄上限；比值仍可计算，但筛查解释的适用性更不确定。"]
    text += ["", "比较多次测量时应保持腰围测量部位和方法一致；本文没有规定唯一测量部位。接近界值时，小幅测量差异即可改变分档。"]
    if targets:
        text += ["", "## 你的目标情景", "",
                 f"如果腰围达到你提供的 {targets['waist_cm']:g} cm，身高保持不变，腰围身高比为 {lever['targets']['waist_height_ratio']:.6f}，变化为 {lever['targets']['waist_height_ratio_delta']:+.6f}。",
                 f"目标情景分档：{CATEGORY_LABELS[lever['targets']['screening_category']]}。", TARGET_NOTE]
    text += ["", "验证状态：仍在验证。论文印有计算定义及筛查界值，但没有配套个人输入和输出的计算示例；当前测试仅核查单位、边界与程序行为。",
             "", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(lever, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
