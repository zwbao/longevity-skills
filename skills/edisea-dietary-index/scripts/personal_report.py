#!/usr/bin/env python3
"""Personal EDISEA readout. Lai et al., Nature Communications 2026.

EDISEA = sum over ten food groups of weight x servings per 2000 kcal/day,
with the Source Data Fig. 2b weights, as `ediea_servday` in the authors'
construct/hrs-ediea.R. Higher means a diet pattern the paper links to slower
GrimAge2 acceleration.

Not computed: the person's place in the HRS distribution (the paper does not
publish the training means the centred score needs), a predicted GrimAge2
acceleration in years, or a mortality risk.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    ENERGY_PLAUSIBLE_KCAL,
    FOODS,
    LABELS,
    Q1_Q5_MEDIANS,
    REFERENCE_KCAL,
    TITLE,
    WEIGHTS,
)

FOOD_KEYS = [key for key, _label, _name, _weight in FOODS]
ENERGY_KEY = "energy_kcal_d"


def energy_factor(energy_kcal: float | None) -> float:
    """Multiplier from servings/day to servings per 2000 kcal/day.

    Without total energy the servings are used as given (as if the day were
    2000 kcal); the report says so.
    """
    if energy_kcal is None:
        return 1.0
    return REFERENCE_KCAL / energy_kcal


def contributions(servings: dict[str, float], energy_kcal: float | None) -> dict[str, float]:
    factor = energy_factor(energy_kcal)
    return {key: WEIGHTS[key] * servings[key] * factor for key in FOOD_KEYS}


def edisea(servings: dict[str, float], energy_kcal: float | None = None) -> float:
    """EDISEA on the servings-per-2000-kcal scale (Source Data Fig. 2b weights)."""
    return sum(contributions(servings, energy_kcal).values())


def collect_inputs(path: Path | None, sex: str | None) -> tuple[dict[str, float], list, list[str]]:
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(path, manifest)
    problems = [item for item in collected.problems if item.kind != "missing"]
    missing = [key for key in FOOD_KEYS if key not in collected.values]
    for key in missing:
        problems.append(skillkit.Problem(key, LABELS[key], "missing",
                                         f"缺少{LABELS[key]}（每天几份）。不吃不喝就填 0；十项要齐才算 EDISEA。"))
    return dict(collected.values), problems, missing


def sex_key(sex: str | None) -> str | None:
    label = (sex or "").strip().casefold()
    if label in {"男", "male", "m", "man"}:
        return "male"
    if label in {"女", "female", "f", "woman"}:
        return "female"
    return None


def energy_lines(energy_kcal: float | None, sex: str | None) -> list[str]:
    if energy_kcal is None:
        return [
            "没有提供每日总能量，所以按你给的每天份数直接算（相当于把你的一天当作 2000 千卡）。"
            "论文用的是按能量校正到每 2000 千卡的份数；吃得明显多于或少于 2000 千卡的人，分数会偏。"
        ]
    lines = [f"每日总能量 {energy_kcal:g} 千卡：各项份数先乘以 2000/{energy_kcal:g}，换算成每 2000 千卡的份数再加权。"]
    who = sex_key(sex)
    if who is not None:
        low, high = ENERGY_PLAUSIBLE_KCAL[who]
        if not low <= energy_kcal <= high:
            label = "男性" if who == "male" else "女性"
            lines.append(
                f"论文在美国健康与退休研究里把{label}每日能量低于 {low:g} 或高于 {high:g} 千卡的问卷当作不可信而剔除；"
                "你的能量在这个范围外，请先核对问卷或记录。"
            )
    return lines


def render(values: dict[str, float], energy_kcal: float | None, sex: str | None) -> str:
    parts = contributions(values, energy_kcal)
    score = sum(parts.values())
    factor = energy_factor(energy_kcal)
    lines = [f"# {TITLE}", ""]
    lines.append(f"你的 EDISEA 是 {score:.4f}。分数越高，表示饮食越接近论文里与 GrimAge2 表观衰老加速较低相关的模式。")
    lines.append(
        "这个分数没有单位，也没有公布的人群百分位：论文公布了每项权重，"
        "但没有公布推导队列各食物组的均值，所以算不出你在队列里排第几，也不把它换算成“慢几岁”。"
    )
    lines.extend(["", *energy_lines(energy_kcal, sex), "", "## 十项食物的份数和贡献", ""])
    lines.append("| 食物组 | 你每天份数 | 每 2000 千卡份数 | 权重（每份） | 贡献 | 论文 Q1 / Q5 中位数（份/天） |")
    lines.append("|---|---|---|---|---|---|")
    for key, label, _name, weight in FOODS:
        q1, q5 = Q1_Q5_MEDIANS[key]
        lines.append(
            f"| {label} | {values[key]:g} | {values[key] * factor:.2f} | {weight:+.5f} | {abs(parts[key]) if parts[key] == 0 else parts[key]:+.4f} | {q1:.2f} / {q5:.2f} |"
        )
    lines.append("")
    lines.append(
        "Q1、Q5 是论文推导队列（美国健康与退休研究，1,711 人）里 EDISEA 最低和最高五分之一人群各项的中位摄入量，"
        "照正文印出的数抄录，作为参照，不是目标值。"
    )
    ranked = sorted(parts.items(), key=lambda item: item[1])
    negatives = [(key, part) for key, part in ranked if part < 0][:3]
    if negatives:
        lines.extend(["", "## 拉低分数最多的项", ""])
        for key, part in negatives:
            lines.append(f"- {LABELS[key]}：{part:+.4f}")
    lines.extend([
        "",
        "## 没有计算的",
        "",
        "- 你在推导队列里的百分位或五分位：缺推导队列各食物组的均值（论文和源数据只给了中心化后的分数）。",
        "- 预测的 GrimAge2 加速年数、死亡或疾病风险：论文报告的是人群间比较（最高与最低分位、第 90 与第 10 百分位），不是个人预测方程。",
        "- 论文用残差法按能量校正；这里用每 2000 千卡的份数比例换算，残差法需要的队列回归系数没有公布。",
        "",
        f"边界: {BOUNDARY}",
    ])
    return "\n".join(lines) + "\n"


def levers(values: dict[str, float], energy_kcal: float | None, targets: dict[str, float]) -> dict:
    """Per-serving sensitivity and the change from moving each food to a target."""
    manifest = skillkit.load_manifest(__file__)
    factor = energy_factor(energy_kcal)
    current = edisea(values, energy_kcal)
    sensitivity = []
    for key in FOOD_KEYS:
        spec = skillkit.spec_by_key(manifest, key)
        sensitivity.append({"key": key, "label_zh": spec["label_zh"], "unit": spec.get("unit", ""),
                            "value": values[key], "per_unit": WEIGHTS[key] * factor})
    out = {
        "schema": "longevity-levers/1",
        "model": "edisea",
        "model_zh": "EDISEA 表观衰老饮食指数（Lai 2026，美国健康与退休研究推导）",
        "current": {"edisea": current, "energy_kcal_d": energy_kcal},
        "sensitivity": sensitivity,
        "levers": [],
        "note_zh": "每项的变化是这个加权和的算术变化，不是对表观年龄或寿命的预测。总能量不是杠杆。",
    }
    usable = {key: value for key, value in targets.items() if key in WEIGHTS}
    if usable:
        for key, target in usable.items():
            moved = edisea(dict(values, **{key: target}), energy_kcal)
            spec = skillkit.spec_by_key(manifest, key)
            out["levers"].append({"key": key, "label_zh": spec["label_zh"], "unit": spec.get("unit", ""),
                                  "from": values[key], "to": target, "edisea_delta": moved - current})
        together = edisea(dict(values, **usable), energy_kcal)
        out["targets"] = {"values": usable, "edisea": together, "edisea_delta": together - current}
        out["levers"].sort(key=lambda item: -item["edisea_delta"])
    return out


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    rest = rows[1:]
    while rest and rest[0] == "":
        rest = rest[1:]
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rest]) + "\n"


def write_report(out_dir: Path, measurements: Path | None, sex: str | None = None, targets: Path | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        if (out_dir / name).exists():
            (out_dir / name).unlink()
    manifest = skillkit.load_manifest(__file__)
    values, problems, _missing = collect_inputs(measurements, sex)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        text = path.read_text(encoding="utf-8").replace("这次没有计算。原因如下：", "输入没有通过检查，所以没有 EDISEA。原因如下：")
        path.write_text(_with_paper_card(text), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {"edisea": None})
        return path
    energy = values.get(ENERGY_KEY)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card(render(values, energy, sex)), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {"edisea": edisea(values, energy)})
    wanted: dict[str, float] = {}
    if targets is not None:
        wanted = dict(skillkit.collect_file(targets, manifest).values)
    (out_dir / "levers.json").write_text(json.dumps(levers(values, energy, wanted), ensure_ascii=False, indent=1) + "\n",
                                         encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EDISEA dietary index (Lai et al., Nature Communications 2026)")
    parser.add_argument("--intake", type=Path, help="CSV item,value,unit: servings/day of the ten food groups, optional energy_kcal_d")
    parser.add_argument("--sex", default=None, help="Only used to flag energy outside the paper's plausibility range")
    parser.add_argument("--targets", type=Path, help="CSV of target servings/day (same columns) for out/levers.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.intake, args.sex, args.targets)
    sys.stdout.write(str(path) + "\n")
    if (args.out / "problems.json").exists():
        return skillkit.EXIT_INPUT_PROBLEM
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
