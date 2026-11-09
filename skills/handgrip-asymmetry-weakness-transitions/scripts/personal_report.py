#!/usr/bin/env python3
"""Two-wave handgrip asymmetry (HGSA) and low handgrip strength (LHGS) patterns,
classified with the cut points of Xu, Lin & Ran (GeroScience 2026; CHARLS 2011/2013),
with the printed all-cause mortality hazard ratios for that pattern (Table 2 /
Supplementary Tables S11, S12, S14).

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    COHORT,
    COMORBID_ZH,
    DELTA_AAI_HR,
    DELTA_AAI_KNOTS,
    HGSA_HR,
    HGSA_RATIO_HIGH,
    HGSA_RATIO_LOW,
    JOINT_HR,
    LHGS_AGE_SPLIT,
    LHGS_HR,
    LHGS_KG,
    LOSS_RGS_HR,
    LOSS_RGS_KNOTS,
    PATTERN_ZH,
    S12_HGSA,
    S12_JOINT,
    S12_LHGS,
)

TITLE = "两次握力：左右不对称和握力低的变化模式与全因死亡风险比（CHARLS 队列）"
_EPS = 1e-9  # a ratio printed as exactly 0.90 or 1.10 (e.g. 27/30, 33/30) is not asymmetric
HAND_ZH = {"right": "右手", "left": "左手", "both": "两手一样"}


# ---------- method ----------

def grip_ratio(left_kg: float, right_kg: float, dominant: str) -> float:
    """Methods: non-dominant / dominant HGS. With no dominant hand ('both'), the paper's
    stronger-hand sensitivity definition (weaker / stronger, Supplementary Table S16 Panel B)."""
    if dominant == "right":
        return left_kg / right_kg
    if dominant == "left":
        return right_kg / left_kg
    return min(left_kg, right_kg) / max(left_kg, right_kg)


def is_hgsa(ratio: float) -> bool:
    """Methods: HGSA when the ratio is < 0.90 or > 1.10."""
    return ratio < HGSA_RATIO_LOW - _EPS or ratio > HGSA_RATIO_HIGH + _EPS


def lhgs_threshold(sex: str, age: float) -> float:
    band = "under65" if age < LHGS_AGE_SPLIT else "65plus"
    return LHGS_KG[(sex, band)]


def is_lhgs(max_kg: float, sex: str, age: float) -> bool:
    """Methods: AWGS 2025, maximum HGS below the sex- and age-specific threshold."""
    return max_kg < lhgs_threshold(sex, age) - _EPS


def pattern(abnormal_w1: bool, abnormal_w2: bool) -> int:
    """0 normal at both, 1 newly abnormal at Wave 2, 2 normalized at Wave 2, 3 abnormal at both."""
    return {(False, False): 0, (False, True): 1, (True, False): 2, (True, True): 3}[(abnormal_w1, abnormal_w2)]


def aai(ratio: float) -> float:
    return abs(ratio - 1.0)


def assess(values: dict, sex: str, dominant: str, age_w1: float, age_w2: float) -> dict:
    l1, r1 = values["grip_left_w1_kg"], values["grip_right_w1_kg"]
    l2, r2 = values["grip_left_w2_kg"], values["grip_right_w2_kg"]
    ratio1, ratio2 = grip_ratio(l1, r1, dominant), grip_ratio(l2, r2, dominant)
    max1, max2 = max(l1, r1), max(l2, r2)
    hgsa1, hgsa2 = is_hgsa(ratio1), is_hgsa(ratio2)
    lhgs1, lhgs2 = is_lhgs(max1, sex, age_w1), is_lhgs(max2, sex, age_w2)
    out = {
        "ratio1": ratio1, "ratio2": ratio2, "max1": max1, "max2": max2,
        "hgsa1": hgsa1, "hgsa2": hgsa2, "lhgs1": lhgs1, "lhgs2": lhgs2,
        "thr1": lhgs_threshold(sex, age_w1), "thr2": lhgs_threshold(sex, age_w2),
        "hgsa_pattern": pattern(hgsa1, hgsa2),
        "lhgs_pattern": pattern(lhgs1, lhgs2),
        "joint": int(hgsa2) + int(lhgs2),
        "delta_aai": aai(ratio2) - aai(ratio1),
        "loss_rgs": None,
    }
    if "bmi_w1_kg_m2" in values and "bmi_w2_kg_m2" in values:
        out["loss_rgs"] = max1 / values["bmi_w1_kg_m2"] - max2 / values["bmi_w2_kg_m2"]
    return out


# ---------- inputs ----------

def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def parse_hand(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"right", "r", "右", "右手", "right hand"}:
        return "right"
    if text in {"left", "l", "左", "左手", "left hand"}:
        return "left"
    if text in {"both", "either", "ambidextrous", "两手", "两手一样", "双手", "都一样"}:
        return "both"
    return None


# ---------- report ----------

def _hr_text(row: tuple) -> str:
    est, low, high = row
    if low is None:
        return "1（参照组）"
    return f"{est:.2f}（95% 置信区间 {low:.2f}–{high:.2f}）"


def _position(value: float, knots: tuple) -> str:
    p10, p50, p90 = knots
    if value < p10:
        return "低于论文人群第 10 百分位"
    if value < p50:
        return "在论文人群第 10 到第 50 百分位之间"
    if value < p90:
        return "在论文人群第 50 到第 90 百分位之间"
    return "高于论文人群第 90 百分位"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _yn(flag: bool) -> str:
    return "有" if flag else "没有"


def report_lines(res: dict, values: dict, sex: str, dominant: str, age_w1: float, age_w2: float,
                 age_w1_given: bool, chronic: int | None) -> list:
    sex_zh = "男" if sex == "male" else "女"
    lines = [f"# {TITLE}", "", "## 输入", "",
             f"- {sex_zh}，第二次测量时 {age_w2:g} 岁，第一次测量时 {age_w1:g} 岁" + ("" if age_w1_given else "（没有给出，按第二次的年龄算）"),
             f"- 惯用手：{HAND_ZH[dominant]}",
             f"- 第一次：左手 {values['grip_left_w1_kg']:.1f} kg，右手 {values['grip_right_w1_kg']:.1f} kg",
             f"- 第二次：左手 {values['grip_left_w2_kg']:.1f} kg，右手 {values['grip_right_w2_kg']:.1f} kg"]
    if res["loss_rgs"] is not None:
        lines.append(f"- 体质指数：第一次 {values['bmi_w1_kg_m2']:.1f}，第二次 {values['bmi_w2_kg_m2']:.1f} kg/m²")
    ratio_def = "非惯用手 ÷ 惯用手" if dominant != "both" else "弱手 ÷ 强手（两手一样时用论文敏感性分析的强手定义）"
    h, w, j = res["hgsa_pattern"], res["lhgs_pattern"], res["joint"]
    lines += ["", "## 分型", "",
              f"- 左右握力比（{ratio_def}）：第一次 {res['ratio1']:.3f}，第二次 {res['ratio2']:.3f}。论文把小于 0.90 或大于 1.10 算作左右不对称。",
              f"  第一次{_yn(res['hgsa1'])}不对称，第二次{_yn(res['hgsa2'])}不对称 → 不对称模式：**{PATTERN_ZH[h]}**。",
              f"- 最大握力（两手取高）：第一次 {res['max1']:.1f} kg（切点 {res['thr1']:g} kg），第二次 {res['max2']:.1f} kg（切点 {res['thr2']:g} kg）。低于切点算握力低（亚洲肌少症工作组 2025 标准）。",
              f"  第一次握力{'低' if res['lhgs1'] else '不低'}，第二次握力{'低' if res['lhgs2'] else '不低'} → 握力低模式：**{PATTERN_ZH[w]}**。",
              f"- 第二次的联合异常分：{j}（左右不对称 1 分 + 握力低 1 分）。",
              "", "## 论文里这些模式的全因死亡风险比", "",
              f"- 不对称模式“{PATTERN_ZH[h]}”：{_hr_text(HGSA_HR[h])}，参照是两次都没有左右不对称。",
              f"- 握力低模式“{PATTERN_ZH[w]}”：{_hr_text(LHGS_HR[w])}，参照是两次握力都不低。",
              f"- 联合异常分 {j}：{_hr_text(JOINT_HR[j])}，参照是 0 分。"]
    if chronic is not None:
        c = min(chronic, 2)
        lines.append(f"- 按慢病负担分层（补充表 S12，{COMORBID_ZH[c]}）：不对称 {_hr_text(S12_HGSA[c][h])}；握力低 {_hr_text(S12_LHGS[c][w])}；联合异常分 {_hr_text(S12_JOINT[c][j])}。")
    lines += ["", "## 连续变化", "",
              f"- 不对称指数（|握力比 − 1|）的变化：{res['delta_aai']:+.3f}，{_position(res['delta_aai'], DELTA_AAI_KNOTS)}（正值表示两手差别变大）。"
              f"论文里每增加 1 个单位，风险比 {DELTA_AAI_HR[0]:.2f}（{DELTA_AAI_HR[1]:.2f}–{DELTA_AAI_HR[2]:.2f}）。"]
    if res["loss_rgs"] is not None:
        lines.append(f"- 相对握力（最大握力 ÷ 体质指数）的下降：{res['loss_rgs']:+.3f}，{_position(res['loss_rgs'], LOSS_RGS_KNOTS)}（正值表示下降）。"
                     f"论文里每下降 1 个单位，风险比 {LOSS_RGS_HR[0]:.2f}（{LOSS_RGS_HR[1]:.2f}–{LOSS_RGS_HR[2]:.2f}）。")
    else:
        lines.append("- 相对握力下降没有算：需要两次测量时的体质指数。")
    lines.append("- 这里只给出你在论文人群分布里的位置，不把每单位风险比外推成你的风险比。")
    lines += ["", "## 这意味着什么", ""]
    if h == 0 and w == 0:
        lines.append("- 两次都没有左右不对称，也没有握力低，在论文里都属于参照组，这是好的信号。")
    else:
        lines.append("- 风险比大于 1 表示在论文人群里，这一组的人随后约 5 年的全因死亡比参照组更常见；置信区间跨过 1 的组，论文里没有统计学差异。"
                     "这是人群关联，不是你个人的死亡概率。")
        if w in (1, 3):
            lines.append("- 握力低在论文里的关联比左右不对称更一致。握力低或下降明显，可以请医生评估肌肉、营养和慢病情况。")
        if w == 2:
            lines.append("- 论文里第一次握力低、第二次恢复的人，风险比仍高于两次都不低的人；一次回到切点以上不代表储备已经完全恢复。")
        if h in (1, 2):
            lines.append("- 左右不对称只出现在其中一次时，论文里没有看到死亡风险升高；一次波动可能来自测量误差或手部局部问题。")
        if h == 3:
            lines.append("- 两次都左右不对称在论文里和较高死亡风险有关；两手差别也可能来自手、腕或神经的局部问题，可以请医生看看。")
    lines += ["", "## 说明", "",
              f"- 论文人群：CHARLS {COHORT['wave1']} 和 {COHORT['wave2']} 两次握力都齐的 {COHORT['n']} 名 {COHORT['min_age']} 岁及以上中国成人，"
              f"从 {COHORT['wave2']} 年随访到 {COHORT['end']} 年，中位 {COHORT['followup_median_years']} 年，{COHORT['deaths']} 人死亡。",
              "- 测量：每只手测两次，取各自最高值；握力计为 Yuejian WL-1000。两次测量要用同样方法。",
              "- 风险比来自 Cox 模型，调整了年龄、性别、教育、城乡、婚姻、收入、吸烟、饮酒、体力活动和体质指数。",
              "- 论文两次测量间隔约 2 年；你的间隔差得多时，这些风险比不一定适用。"]
    if age_w2 < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age_w2:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内。")
    if not age_w1_given and age_w2 >= LHGS_AGE_SPLIT:
        lines.append("- 没有给第一次测量时的年龄，第一次的握力切点按第二次的年龄段取；如果第一次时不到 65 岁，切点会不同，请补上第一次的年龄。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex: str | None,
                 dominant_hand: str | None, chronic: float | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    problems += skillkit.check_scalar(manifest, "age", age)
    if chronic is not None:
        problems += skillkit.check_scalar(manifest, "chronic_conditions", chronic)
        if float(chronic) != int(chronic):
            problems.append(skillkit.Problem("chronic_conditions", "慢病数", "parse", "慢病数要写整数（0、1、2……）。"))
    person_sex = parse_sex(sex)
    if person_sex is None:
        msg = "缺少性别（握力低的切点男女不同），请写男或女。" if not sex else f"性别写的是“{sex}”，请写男或女。"
        problems.append(skillkit.Problem("sex", "性别", "missing" if not sex else "unit", msg))
    hand = parse_hand(dominant_hand)
    if hand is None:
        msg = ("缺少惯用手（左右握力比要用惯用手作分母），请写右手、左手或两手一样。" if not dominant_hand
               else f"惯用手写的是“{dominant_hand}”，请写右手、左手或两手一样。")
        problems.append(skillkit.Problem("dominant_hand", "惯用手", "missing" if not dominant_hand else "unit", msg))
    values = dict(collected.values)
    age_w1_given = "age_w1_years" in values
    if age is not None and age_w1_given and values["age_w1_years"] > age:
        problems.append(skillkit.Problem("age_w1_years", "第一次测量时年龄", "range",
                                         f"第一次测量时年龄 {values['age_w1_years']:g} 岁大于第二次的 {age:g} 岁，请核对。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    age_w1 = values["age_w1_years"] if age_w1_given else float(age)
    res = assess(values, person_sex, hand, age_w1, float(age))
    chronic_n = int(chronic) if chronic is not None else None
    path = out_dir / "report.md"
    text = "\n".join(report_lines(res, values, person_sex, hand, age_w1, float(age), age_w1_given, chronic_n)) + "\n"
    path.write_text(_with_paper_card(text), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "grip_ratio_w1": round(res["ratio1"], 4),
        "grip_ratio_w2": round(res["ratio2"], 4),
        "hgsa_pattern": PATTERN_ZH[res["hgsa_pattern"]],
        "hgsa_pattern_hr": HGSA_HR[res["hgsa_pattern"]][0],
        "max_grip_w1_kg": res["max1"],
        "max_grip_w2_kg": res["max2"],
        "lhgs_pattern": PATTERN_ZH[res["lhgs_pattern"]],
        "lhgs_pattern_hr": LHGS_HR[res["lhgs_pattern"]][0],
        "joint_score_w2": res["joint"],
        "joint_score_hr": JOINT_HR[res["joint"]][0],
        "delta_aai": round(res["delta_aai"], 4),
        "loss_rgs": None if res["loss_rgs"] is None else round(res["loss_rgs"], 4),
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 第一次左手握力, 第一次右手握力, 第二次左手握力, 第二次右手握力（kg，必填）；"
                             "第一次测量时年龄、第一次体质指数、第二次体质指数（可选）")
    parser.add_argument("--age", type=float, help="第二次测量时的年龄（岁）")
    parser.add_argument("--sex", help="男 / 女")
    parser.add_argument("--dominant-hand", help="惯用手：右手 / 左手 / 两手一样")
    parser.add_argument("--chronic-conditions", type=float,
                        help="可选：心血管病、高血压、血脂异常、糖尿病、癌症、慢性肺病中确诊了几种")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex, args.dominant_hand, args.chronic_conditions)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
