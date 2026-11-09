#!/usr/bin/env python3
"""Personal Life's Simple 7 (LS7) score as scored in HANDLS (Georgescu et al., GeroScience 2026).

Seven components, each 2 (ideal), 1 (intermediate) or 0 (poor) points, summed
to 0-14. Every cutoff is in presets.py with its locator in the paper's
supplement (Supplementary Methods 2 and Table S1A).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BMI_IDEAL_BELOW,
    BMI_POOR_AT,
    BOUNDARY,
    COMPONENT_ZH,
    COMPONENTS,
    DBP_IDEAL_BELOW,
    DBP_POOR_AT,
    DIET_GOALS_ZH,
    DIET_IDEAL_AT,
    DIET_INTERMEDIATE_AT,
    GLUCOSE_IDEAL_BELOW,
    GLUCOSE_POOR_AT,
    LEVEL_ZH,
    PA_MODERATE_IDEAL_AT,
    PA_VIGOROUS_IDEAL_AT,
    POINTS,
    SBP_IDEAL_BELOW,
    SBP_POOR_AT,
    SMOKING_LEVEL,
    SMOKING_ZH,
    TC_IDEAL_BELOW,
    TC_POOR_AT,
    TOTAL_BANDS,
    TOTAL_MAX,
)

TITLE = "Life's Simple 7 心血管健康总分（HANDLS 计分）"
TREATED_FLAGS = ("bp_treated", "chol_treated", "glucose_treated")
YES = {"1", "yes", "y", "true", "是", "有"}
NO = {"0", "no", "n", "false", "否", "无", "没有"}
SMOKING_ALIASES = {
    "never": "never", "从不": "never", "从不吸烟": "never", "不吸烟": "never",
    "quit_over_1y": "quit_over_1y", "former_over_1y": "quit_over_1y", "戒烟超过1年": "quit_over_1y",
    "quit_within_1y": "quit_within_1y", "former_within_1y": "quit_within_1y", "戒烟不满1年": "quit_within_1y",
    "current": "current", "现在吸烟": "current", "吸烟": "current",
}
MEASUREMENT_KEYS = ("bmi_kg_m2", "sbp_mmhg", "dbp_mmhg", "tc_mg_dl", "glucose_mg_dl",
                    "pa_moderate_min_wk", "pa_vigorous_min_wk", "diet_goals_met")


def level_bmi(bmi: float) -> str:
    if bmi < BMI_IDEAL_BELOW:
        return "ideal"
    return "intermediate" if bmi < BMI_POOR_AT else "poor"


def level_bp(sbp: float, dbp: float, treated: bool) -> str:
    if sbp >= SBP_POOR_AT or dbp >= DBP_POOR_AT:
        return "poor"
    if sbp < SBP_IDEAL_BELOW and dbp < DBP_IDEAL_BELOW:
        return "intermediate" if treated else "ideal"
    return "intermediate"


def level_lab(value: float, ideal_below: float, poor_at: float, treated: bool) -> str:
    """Total cholesterol and fasting glucose: ideal only when untreated; treated to ideal is intermediate."""
    if value >= poor_at:
        return "poor"
    if value < ideal_below:
        return "intermediate" if treated else "ideal"
    return "intermediate"


def level_diet(goals_met: int) -> str:
    if goals_met >= DIET_IDEAL_AT:
        return "ideal"
    return "intermediate" if goals_met >= DIET_INTERMEDIATE_AT else "poor"


def level_activity(moderate_min: float, vigorous_min: float) -> Tuple[str, bool]:
    """Level, and whether it is a mix whose combination rule the paper does not print."""
    if moderate_min >= PA_MODERATE_IDEAL_AT or vigorous_min >= PA_VIGOROUS_IDEAL_AT:
        return "ideal", False
    if moderate_min <= 0 and vigorous_min <= 0:
        return "poor", False
    return "intermediate", moderate_min > 0 and vigorous_min > 0


def total_score(points: Dict[str, float]) -> float:
    """LS7 total: the sum of the seven component points (Supplementary Methods 2, 1.5)."""
    missing = [name for name in COMPONENTS if name not in points]
    if missing:
        raise KeyError(f"missing components: {', '.join(missing)}")
    return sum(points[name] for name in COMPONENTS)


def band(total: float) -> str:
    for low, label in TOTAL_BANDS:
        if total >= low:
            return label
    return TOTAL_BANDS[-1][1]


def score(values: Dict[str, float], smoking: str, treated: Dict[str, bool]) -> Dict:
    activity, mixed = level_activity(values["pa_moderate_min_wk"], values["pa_vigorous_min_wk"])
    levels = {
        "smoking": SMOKING_LEVEL[smoking],
        "diet": level_diet(int(round(values["diet_goals_met"]))),
        "physical_activity": activity,
        "bmi": level_bmi(values["bmi_kg_m2"]),
        "blood_pressure": level_bp(values["sbp_mmhg"], values["dbp_mmhg"], treated["bp_treated"]),
        "cholesterol": level_lab(values["tc_mg_dl"], TC_IDEAL_BELOW, TC_POOR_AT, treated["chol_treated"]),
        "glucose": level_lab(values["glucose_mg_dl"], GLUCOSE_IDEAL_BELOW, GLUCOSE_POOR_AT, treated["glucose_treated"]),
    }
    points = {name: POINTS[level] for name, level in levels.items()}
    total = total_score(points)
    return {"levels": levels, "points": points, "total": total, "band": band(total), "activity_mix_unscored": mixed}


def parse_flag(name: str, raw: Optional[str]) -> Tuple[Optional[bool], Optional[str]]:
    if raw is None:
        return None, None
    text = str(raw).strip().lower()
    if text in YES:
        return True, None
    if text in NO:
        return False, None
    return None, f"--{name.replace('_', '-')} 只接受 yes 或 no（是/否），收到「{raw}」。"


def parse_smoking(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if raw is None:
        return None, None
    key = SMOKING_ALIASES.get(str(raw).strip().lower().replace(" ", ""))
    if key is None:
        return None, f"--smoking 只接受 never、quit_over_1y、quit_within_1y 或 current，收到「{raw}」。"
    return key, None


def levers(values: Dict[str, float], smoking: str, treated: Dict[str, bool], targets: Dict[str, float]) -> Dict:
    """Score now, and the point change when each target is reached alone and all together."""
    manifest = skillkit.load_manifest(__file__)
    current = score(values, smoking, treated)
    sensitivity = []
    for key in MEASUREMENT_KEYS:
        spec = skillkit.spec_by_key(manifest, key)
        sensitivity.append({"key": key, "label_zh": spec.get("label_zh", key), "unit": spec.get("unit", ""),
                            "value": values[key], "per_unit": 0.0,
                            "note_zh": "分档计分：只有跨过切点时总分才变，切点之间每单位变化为 0。"})
    out = {"schema": "longevity-levers/1", "model": "ls7-handls", "model_zh": "Life's Simple 7（HANDLS 计分，0–14 分）",
           "current": {"ls7_total": current["total"], "band": current["band"]}, "sensitivity": sensitivity, "levers": [],
           "note_zh": "吸烟状态和是否用药不在杠杆里；这里只算测量值和行为分钟数到目标值时总分的变化。总分越高越好。"}
    usable = {key: value for key, value in targets.items() if key in MEASUREMENT_KEYS}
    if usable:
        for key, target in usable.items():
            moved = score(dict(values, **{key: target}), smoking, treated)["total"]
            spec = skillkit.spec_by_key(manifest, key)
            out["levers"].append({"key": key, "label_zh": spec.get("label_zh", key), "unit": spec.get("unit", ""),
                                  "from": values[key], "to": target, "score_delta": moved - current["total"]})
        together = score(dict(values, **usable), smoking, treated)
        out["targets"] = {"values": usable, "ls7_total": together["total"], "band": together["band"],
                          "score_delta": together["total"] - current["total"]}
        out["levers"].sort(key=lambda item: -item["score_delta"])
    return out


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _empty_outputs() -> Dict[str, None]:
    return {"ls7_total": None, "ls7_band": None, **{f"{name}_points": None for name in COMPONENTS}}


def write_report(out_dir: Path, measurements: Optional[Path], smoking_raw: Optional[str], flag_values: Dict[str, Optional[str]],
                 targets: Optional[Path] = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        if (out_dir / name).exists():
            (out_dir / name).unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems: List[skillkit.Problem] = list(collected.problems)
    goals = collected.values.get("diet_goals_met")
    if goals is not None and goals != int(goals):
        problems.append(skillkit.Problem("diet_goals_met", "达到的饮食目标数", "parse",
                                         f"达到的饮食目标数要是 0 到 5 的整数，收到 {goals:g}。"))
    smoking, message = parse_smoking(smoking_raw)
    if message:
        problems.append(skillkit.Problem("smoking", "吸烟状态", "parse", message))
    elif smoking is None:
        problems.append(skillkit.Problem("smoking", "吸烟状态", "missing",
                                         "缺少吸烟状态（--smoking never、quit_over_1y、quit_within_1y 或 current）。"))
    treated: Dict[str, Optional[bool]] = {}
    for name in TREATED_FLAGS:
        value, message = parse_flag(name, flag_values.get(name))
        label = skillkit.spec_by_key(manifest, name).get("label_zh", name)
        if message:
            problems.append(skillkit.Problem(name, label, "parse", message))
        elif value is None:
            problems.append(skillkit.Problem(name, label, "missing", f"缺少{label}（--{name.replace('_', '-')} yes 或 no）。"))
        treated[name] = value
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, _empty_outputs())
        return path

    values = collected.values
    result = score(values, smoking, treated)  # type: ignore[arg-type]
    yes_no = lambda flag: "在用药" if flag else "未用药"
    lines = [f"# {TITLE}", "", "## 输入", ""]
    lines.append(f"- 吸烟：{SMOKING_ZH[smoking]}")
    lines.append(f"- 饮食：五项目标达到 {int(values['diet_goals_met'])} 项")
    lines.append(f"- 身体活动：中等强度每周 {values['pa_moderate_min_wk']:g} 分钟，高强度每周 {values['pa_vigorous_min_wk']:g} 分钟")
    lines.append(f"- 体重指数 {values['bmi_kg_m2']:.1f} kg/m²")
    lines.append(f"- 血压 {values['sbp_mmhg']:g}/{values['dbp_mmhg']:g} mmHg（降压药：{yes_no(treated['bp_treated'])}）")
    lines.append(f"- 总胆固醇 {values['tc_mg_dl']:.0f} mg/dL（调脂药：{yes_no(treated['chol_treated'])}）")
    lines.append(f"- 空腹血糖 {values['glucose_mg_dl']:.0f} mg/dL（降糖药：{yes_no(treated['glucose_treated'])}）")
    lines += ["", "## 结果", "", f"LS7 总分 **{result['total']:g} / {TOTAL_MAX}**，属于{result['band']}。", "",
              "| 项目 | 档次 | 得分 |", "|---|---|---|"]
    for name in COMPONENTS:
        lines.append(f"| {COMPONENT_ZH[name]} | {LEVEL_ZH[result['levels'][name]]} | {result['points'][name]} |")
    lines += ["", "## 说明", "",
              "- 每项理想 2 分、中等 1 分、差 0 分，七项相加得 0–14 分（论文补充方法 2 与补充表 S1A）。分段“较好 10–14、中等 5–9、较差 0–4”是论文引用的其他研究的分法。",
              "- 研究（美国巴尔的摩 HANDLS 队列，中年城市成人）发现 LS7 总分越高，随访期间全因死亡风险越低，在白人中更明显。论文的风险比在正文表 2、表 3，本技能没有取得这两张表，所以不给出每分对应的风险比，也不把你的总分换算成死亡概率。",
              "- 用药后控制到理想范围的血压、胆固醇、血糖只算中等（1 分），这是 LS7 的计分规则，不是说用药不好。"]
    if smoking == "quit_over_1y":
        lines.append("- 论文补充表 S1A 把戒烟超过 1 年算理想（2 分）；同一补充材料的文字（补充方法 2 第 1.1 节）把所有已戒烟者算中等。按文字的说法，你的总分会低 1 分。")
    if result["activity_mix_unscored"]:
        lines.append(f"- 你的中等和高强度分钟数各自都没到切点（中等 {PA_MODERATE_IDEAL_AT:g}、高强度 {PA_VIGOROUS_IDEAL_AT:g} 分钟/周）。论文写“或两者组合”达到也算理想，但没有印出怎样折算，这里按中等计 1 分；若组合达标，总分可能高 1 分。")
    lines.append("- 饮食五项目标（按每天 2000 千卡折算）：" + "；".join(DIET_GOALS_ZH) + "。")
    lines += ["", f"边界: {BOUNDARY}"]
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(lines) + "\n"), encoding="utf-8")
    outputs = {"ls7_total": result["total"], "ls7_band": result["band"],
               **{f"{name}_points": result["points"][name] for name in COMPONENTS}}
    skillkit.write_result(out_dir, manifest, outputs)
    wanted = dict(skillkit.collect_file(targets, manifest).values) if targets is not None else {}
    (out_dir / "levers.json").write_text(json.dumps(levers(values, smoking, treated, wanted), ensure_ascii=False, indent=1) + "\n",  # type: ignore[arg-type]
                                         encoding="utf-8")
    return path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 体重指数, 收缩压, 舒张压, 总胆固醇, 空腹血糖, 中等强度分钟/周, 高强度分钟/周, 达到的饮食目标数")
    parser.add_argument("--smoking", help="never | quit_over_1y | quit_within_1y | current")
    for name in TREATED_FLAGS:
        parser.add_argument(f"--{name.replace('_', '-')}", dest=name, help="yes or no")
    parser.add_argument("--targets", type=Path, help="CSV of target values for out/levers.json")
    parser.add_argument("--age", type=float, help="accepted and ignored: LS7 has no age term")
    parser.add_argument("--sex", help="accepted and ignored: LS7 has no sex term")
    parser.add_argument("--medications", type=Path, help="accepted and ignored: treatment enters only through the yes/no flags")
    parser.add_argument("--labs", type=Path, help="accepted and ignored")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.smoking, {name: getattr(args, name) for name in TREATED_FLAGS}, args.targets)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
