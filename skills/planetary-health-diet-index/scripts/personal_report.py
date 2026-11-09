#!/usr/bin/env python3
"""Planetary Health Diet Index (0-140) for one person, with the cutoffs of
Supplementary Table 1 of Diez-Echave et al. (J Gerontol A 2026; Seniors-ENRICA),
and the printed frailty odds ratios of that study as population context.

Constants and sources are in presets.py; the contract is in references/contract.md.
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
    COHORT_PHDI,
    COMPONENT_PER2,
    COMPONENTS,
    LOW_ACTIVITY_T3,
    MIN_COHORT_AGE,
    PHDI_MAX,
    POINTS_PER_COMPONENT,
    POOLED_N,
    TABLE2_MODEL3,
    WHOLE_GRAIN_MAX,
)

TITLE = "地球健康饮食指数（PHDI）与衰弱（Seniors-ENRICA 队列）"


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man", "男性"}:
        return "male"
    if text in {"female", "f", "女", "woman", "女性"}:
        return "female"
    return None


def cutoffs(key: str, sex: str) -> tuple[float, float, float]:
    """(intake scoring 0, intake scoring 10, weight) from Supplementary Table 1."""
    _no, _label, _unit, zero, ten, weight = COMPONENTS[key]
    if ten is None:
        ten = WHOLE_GRAIN_MAX[sex]
    return zero, ten, weight


def component_score(key: str, intake: float, sex: str) -> float:
    """Proportional score between the printed cutoffs, times the printed weight."""
    zero, ten, weight = cutoffs(key, sex)
    fraction = (intake - zero) / (ten - zero)
    fraction = min(1.0, max(0.0, fraction))
    return POINTS_PER_COMPONENT * weight * fraction


def component_slope(key: str, intake: float, sex: str) -> float:
    """Points per unit of intake at this intake (0 where the score is already capped)."""
    zero, ten, weight = cutoffs(key, sex)
    low, high = min(zero, ten), max(zero, ten)
    if intake < low or intake > high:
        return 0.0
    slope = POINTS_PER_COMPONENT * weight / (ten - zero)
    if (intake == high and slope > 0) or (intake == low and slope < 0):
        return 0.0
    return slope


def phdi(values: dict, sex: str) -> dict:
    scores = {key: component_score(key, values[key], sex) for key in COMPONENTS}
    return {"total": sum(scores.values()), "scores": scores}


def component_max(key: str) -> float:
    return POINTS_PER_COMPONENT * COMPONENTS[key][5]


def _fmt_intake(key: str, value: float) -> str:
    unit = COMPONENTS[key][2]
    return f"{value:g} 克/天" if unit == "g/d" else f"占总能量 {value:g}%"


def _direction(key: str, sex: str) -> str:
    zero, ten, _ = cutoffs(key, sex)
    unit = " 克/天" if COMPONENTS[key][2] == "g/d" else "%（占总能量）"
    if ten > zero:
        return f"{zero:g}{unit}及以下得 0 分，{ten:g}{unit}及以上得满分"
    return f"{zero:g}{unit}及以上得 0 分，{ten:g}{unit}及以下得满分"


def _or(row: tuple) -> str:
    return f"{row[0]:.2f}（95% 置信区间 {row[1]:.2f}–{row[2]:.2f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, sex: str, age: float | None) -> list:
    total = result["total"]
    lines = [f"# {TITLE}", "", "## 结果", "",
             f"- 你的 PHDI：**{total:.1f} 分**（满分 {PHDI_MAX:g}，越高越接近地球健康饮食）。", ""]
    lines += ["| 序号 | 食物组 | 你的摄入 | 得分 / 满分 | 计分规则（补充表 S1） |", "| --- | --- | --- | --- | --- |"]
    for key, (no, label, _unit, _z, _t, _w) in COMPONENTS.items():
        lines.append(f"| {no} | {label} | {_fmt_intake(key, values[key])} | {result['scores'][key]:.1f} / {component_max(key):g} | {_direction(key, sex)} |")
    gaps = sorted(((component_max(k) - s, k) for k, s in result["scores"].items()), reverse=True)
    gaps = [(gap, key) for gap, key in gaps if gap > 0.05][:5]
    lines += ["", "## 离满分最远的几项", ""]
    if gaps:
        for gap, key in gaps:
            lines.append(f"- {COMPONENTS[key][1]}：差 {gap:.1f} 分（{_direction(key, sex)}）。")
    else:
        lines.append("- 15 项都已接近满分。")
    lines += ["", "## 放在论文队列里看", ""]
    for name, info in COHORT_PHDI.items():
        t1, t2, t3 = info["tertile_means"]
        lines.append(f"- {name}（{info['n']} 人）：平均 {info['mean']} 分（标准差 {info['sd']}）；三分位组的平均分依次为 {t1}、{t2}、{t3}。")
    lines.append("- 论文没有印出三分位的切点，所以这里不判断你落在哪一个三分位，只列出各组平均分供对照。")
    pooled = TABLE2_MODEL3["pooled"]
    lines += [
        f"- 合并两个队列（{POOLED_N} 人，表 2 模型 3）：最高三分位比最低三分位发生衰弱的比值比 {_or(pooled['t3'])}；"
        f"PHDI 每高 20 分，比值比 {_or(pooled['per20'])}。",
        f"- 衰弱五项里，关联主要落在“体力活动少”（最高 vs 最低三分位比值比 {_or(LOW_ACTIVITY_T3)}，表 3）；"
        f"单项食物里，蔬菜（每多 2 分 {_or(COMPONENT_PER2['vegetables_g_d'])}）和水果（每多 2 分 {_or(COMPONENT_PER2['fruit_g_d'])}）的独立关联最明显。",
        "", "## 这意味着什么", "",
        "PHDI 分数是你饮食与 EAT-Lancet 地球健康饮食的接近程度。论文里分数越高的老人，随访中出现衰弱的比值比越低；"
        "这是调整了年龄、性别、教育、吸烟、饮酒、活动、能量、体重指数、慢病和用药之后的人群关联，不是你个人发生衰弱的概率，也不能说明换饮食就会降低风险。",
        "", "## 说明", "",
        "- 分数只按补充表 S1 的切点线性计算；论文用的是覆盖 880 种食物的饮食史问卷，你的摄入量估得越粗，分数误差越大。",
        "- 第 13–15 项按占总能量的百分比计分，不是克数；全谷物满分线女性 75 克/天、男性 90 克/天。",
        f"- 论文人群是西班牙 {MIN_COHORT_AGE} 岁及以上（Seniors-ENRICA-1）和 65 岁及以上（Seniors-ENRICA-2）的社区老人，衰弱按 Fried 表型定义（五项中至少三项）。",
    ]
    if age is not None and age < MIN_COHORT_AGE:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{MIN_COHORT_AGE} 岁及以上）内；分数照样能算，衰弱关联不一定适用。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def levers(values: dict, sex: str, targets: dict) -> dict:
    """Points per unit of each intake at the current values, and what moving each
    targeted intake alone (then all together) does to the PHDI. A score, not a
    prediction for this person."""
    current = phdi(values, sex)
    sensitivity = [{
        "key": key, "label_zh": COMPONENTS[key][1], "unit": COMPONENTS[key][2], "value": values[key],
        "points_per_unit": component_slope(key, values[key], sex),
        "score": current["scores"][key], "score_max": component_max(key),
    } for key in COMPONENTS]
    out = {
        "schema": "longevity-levers/1",
        "model": "phdi",
        "model_zh": "地球健康饮食指数（PHDI，0–140 分；补充表 S1）",
        "current": {"phdi_total": current["total"]},
        "sensitivity": sensitivity,
        "levers": [],
        "note_zh": "每项在切点之外得分封顶，再多或再少都不加分；第 13–15 项是占总能量的百分比。",
    }
    usable = {key: value for key, value in targets.items() if key in COMPONENTS}
    if usable:
        for key, target in usable.items():
            moved = phdi(dict(values, **{key: target}), sex)["total"]
            out["levers"].append({
                "key": key, "label_zh": COMPONENTS[key][1], "unit": COMPONENTS[key][2],
                "from": values[key], "to": target, "phdi_delta": moved - current["total"],
            })
        together = phdi(dict(values, **usable), sex)["total"]
        out["targets"] = {"values": usable, "phdi_total": together, "phdi_delta": together - current["total"]}
        out["levers"].sort(key=lambda item: -item["phdi_delta"])
    return out


def _output_keys(manifest: dict) -> list:
    return [spec["key"] for spec in manifest["outputs"]]


def write_report(out_dir: Path, measurements: Path | None, sex: str | None, age: float | None,
                 targets: Path | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        stale = out_dir / name
        if stale.exists():
            stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if person_sex is None:
        message = "全谷物的满分线按性别不同（女 75 克/天、男 90 克/天），请写男或女。" if not sex else f"性别写的是“{sex}”，请写男或女。"
        problems.append(skillkit.Problem("sex", "性别", "missing" if not sex else "unit", message))
    target_values: dict = {}
    if targets is not None:
        target_collected = skillkit.collect_file(targets, manifest)
        problems += [p for p in target_collected.problems if p.kind != "missing"]
        target_values = dict(target_collected.values)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {key: None for key in _output_keys(manifest)})
        return path
    values = dict(collected.values)
    result = phdi(values, person_sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, person_sex, age)) + "\n"), encoding="utf-8")
    outputs = {"phdi_total": round(result["total"], 2)}
    for key, score in result["scores"].items():
        outputs[f"score_{key}"] = round(score, 2)
    skillkit.write_result(out_dir, manifest, outputs)
    (out_dir / "levers.json").write_text(
        json.dumps(levers(values, person_sex, target_values), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit：15 个食物组的每日摄入（g/d 或 % 总能量）")
    parser.add_argument("--sex")
    parser.add_argument("--age", type=float)
    parser.add_argument("--targets", type=Path, help="同样格式的目标摄入 CSV，写出 out/levers.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.sex, args.age, args.targets)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
