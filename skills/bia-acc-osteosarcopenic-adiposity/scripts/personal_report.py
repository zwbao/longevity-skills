#!/usr/bin/env python3
"""BIA-ACC-based osteosarcopenic adiposity (OSA) phenotype from one person's BIA-ACC report.

Applies the operational cut-offs printed in Ilich et al., GeroScience 2026
(doi:10.1007/s11357-026-02496-1): T-score (bone), S-score (skeletal muscle) and
sex-specific fat mass %. The scores come from the device; nothing is re-estimated.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BONE_LABELS,
    BOUNDARY,
    FAT_PCT_ADIPOSITY,
    OSA_LABELS,
    S_REDUCED,
    STUDY,
    T_MARKED,
    T_REFERENCE_LOWER,
    YES_NO,
)

TITLE = "骨-肌-脂综合表型（BIA-ACC 骨肌减少性肥胖）"
MIN_AGE = 18


def bone_category(t_score: float) -> str:
    if t_score >= T_REFERENCE_LOWER:
        return BONE_LABELS[0]
    if t_score > T_MARKED:
        return BONE_LABELS[1]
    return BONE_LABELS[2]


def bone_reduced(t_score: float) -> bool:
    return t_score < T_REFERENCE_LOWER


def muscle_reduced(s_score: float) -> bool:
    return s_score <= S_REDUCED


def adiposity(fat_pct: float, sex: str) -> bool:
    return fat_pct >= FAT_PCT_ADIPOSITY[sex]


def classify(t_score: float, s_score: float, fat_pct: float, sex: str) -> dict:
    parts = {
        "bone": bone_reduced(t_score),
        "muscle": muscle_reduced(s_score),
        "fat": adiposity(fat_pct, sex),
    }
    return {
        "bone_category": bone_category(t_score),
        "reduced_bone_mass": YES_NO[parts["bone"]],
        "reduced_muscle_mass": YES_NO[parts["muscle"]],
        "adiposity": YES_NO[parts["fat"]],
        "components_met": sum(parts.values()),
        "osa_phenotype": OSA_LABELS[all(parts.values())],
    }


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, sex: str, age: float | None) -> list:
    who = "男" if sex == "male" else "女"
    fat_cut = FAT_PCT_ADIPOSITY[sex]
    t, s, fat = values["bia_acc_t_score"], values["bia_acc_s_score"], values["body_fat_pct"]
    lines = [f"# {TITLE}", "", "## 输入（来自 BIA-ACC 报告）", ""]
    lines.append(f"- {who}" + (f"，{age:g} 岁" if age is not None else ""))
    lines.append(f"- 骨量 T 值 {t:g}，肌量 S 值 {s:g}，体脂率 {fat:g}%")
    lines += ["", "## 结果", ""]
    lines.append(f"- 骨量：{result['bone_category']}（T ≥ −1.0 在参考范围内；−2.5 < T < −1.0 中度降低；T ≤ −2.5 明显降低）。")
    lines.append(f"- 肌量降低：{result['reduced_muscle_mass']}（切点 S ≤ −1.0）。")
    lines.append(f"- 脂肪偏多：{result['adiposity']}（{who}性切点 体脂率 ≥ {fat_cut:g}%）。")
    lines.append(f"- 三项同时达到才算骨肌减少性肥胖表型（OSA）。你达到 {result['components_met']} 项，"
                 f"结论：{result['osa_phenotype']}论文的 BIA-ACC 操作性 OSA 表型。")
    lines += ["", "## 这意味着什么", ""]
    if result["osa_phenotype"] == OSA_LABELS[1]:
        lines.append("骨量和肌量都低于设备参考人群，同时体脂偏多。论文在 20–90 岁的意大利成人里看到，"
                     "符合这一表型的人群，骨和肌肉随年龄的曲线更早往下走、更不稳定，连最年轻的年龄组里也有人符合。"
                     "这是人群层面的横断面关联，不是对你个人未来变化的预测。"
                     "可以把这份报告带去和医生讨论，看是否需要做双能 X 线骨密度、握力或步速等功能检查。")
    elif result["components_met"] > 0:
        flagged = [name for name, key in (("骨量", "reduced_bone_mass"), ("肌量", "reduced_muscle_mass"), ("脂肪", "adiposity"))
                   if result[key] == YES_NO[1]]
        lines.append(f"没有三项同时达到，不符合 OSA 表型；但{'、'.join(flagged)}这几项已经越过论文切点。"
                     "下次用同一台设备、同样条件再测，看是否变化；有疑问可以和医生讨论。")
    else:
        lines.append("三项都没有越过论文切点，骨、肌、脂这三方面目前没有提示，这是好的信号。")
    lines += ["", "## 说明", "",
              f"- 研究对象是 {STUDY['n']} 名 {STUDY['ages'][0]}–{STUDY['ages'][1]} 岁、无慢性病的意大利白人成人"
              f"（女 {STUDY['women']}、男 {STUDY['men']}），横断面研究。用在中国人身上，切点是否同样合适没有验证。",
              "- T 值和 S 值由 BIA-ACC（BioTekna）设备按厂商专有算法和参考人群算出，论文没有公开这些算法；"
              "本技能不重算 T、S 值，只把论文印出的切点套在你报告上的数。",
              "- 其他品牌的体脂秤、生物电阻抗仪或双能 X 线（DXA）的 T 值，与 BIA-ACC 的 T 值不可互换；用它们得到的分档不是论文的方法。",
              "- 肌量 S 值只反映肌肉量，不含握力和体能，所以「肌量降低」不等于肌少症诊断。",
              ]
    if age is not None and not STUDY["ages"][0] <= age <= STUDY["ages"][1]:
        lines.append(f"- 你的年龄 {age:g} 岁不在研究人群的 {STUDY['ages'][0]}–{STUDY['ages'][1]} 岁之内。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex: str | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    if age is not None and age < MIN_AGE:
        problems.append(skillkit.Problem("age", "实足年龄", "range",
                                         f"年龄 {age:g} 岁。论文研究的是 20–90 岁成人，切点不用于未成年人。"))
    elif age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "missing", "需要性别（男或女）：体脂率切点男女不同（男 25%，女 32%）。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    values = dict(collected.values)
    result = classify(values["bia_acc_t_score"], values["bia_acc_s_score"], values["body_fat_pct"], person_sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, person_sex, age)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, result)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: BIA-ACC T 值、S 值、体脂率")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
