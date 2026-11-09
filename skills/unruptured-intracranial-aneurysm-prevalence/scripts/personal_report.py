#!/usr/bin/env python3
"""Which of the printed prevalence groups of Dremel et al. (Lancet Neurol 2026) a person falls in.

The paper pools studies; it publishes a prevalence per group and prevalence or risk
ratios against a reference population, not a joint model. This script places one
person in each printed group (age band, sex, comorbidity, smoking, hypertension,
country) and quotes the paper's numbers for those groups. It never multiplies ratios.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AGE_BANDS,
    AGE_CUTOFF,
    AGE_PER_YEAR_PRINTED,
    BOUNDARY,
    COUNTRIES,
    COUNTRY_ALIASES,
    FAMILY_SUBGROUPS,
    GROUPS,
    RECENT_IMAGING,
    REFERENCE_PREDICTION_INTERVAL,
    REFERENCE_PREVALENCE,
    RR_ANY_SMOKING,
    RR_CURRENT_SMOKING,
    RR_FEMALE,
    RR_HYPERTENSION,
    RR_HYPERTENSION_STRICT,
    SEX,
)

TITLE = "未破裂颅内动脉瘤：你所在人群的患病率"
YES = {"1", "yes", "y", "true", "是", "有"}
NO = {"0", "no", "n", "false", "否", "无", "没有"}
YES_NO_FLAGS = ("adpkd", "connective_tissue", "atherosclerosis", "hypertension")
OUTPUT_KEYS = (
    "age_band", "age_band_prevalence_pct", "sex_prevalence_pct", "female_rr",
    "comorbidity_group", "comorbidity_group_prevalence_pct", "comorbidity_group_count",
    "adjusted_elevated_group_count", "family_subgroup_prevalence_pct",
    "current_smoking_rr", "hypertension_rr", "country_prevalence_pct", "country_pr_age_sex",
)


def num(value: float) -> str:
    """As printed: one decimal, two where the paper prints two (1·14)."""
    return f"{value:.1f}" if round(value, 1) == value else f"{value:.2f}"


def ci(triple, unit: str = "%", counts: str = "") -> str:
    point, low, high = triple
    extra = f"；{counts}" if counts else ""
    if low is None:
        return f"{num(point)}{unit}" + (f"（{counts}）" if counts else "")
    return f"{num(point)}{unit}（95% CI {num(low)}–{num(high)}{unit}{extra}）"


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def parse_yes_no(raw: str | None) -> tuple[bool | None, bool]:
    """(value, readable)."""
    if raw is None:
        return None, True
    text = str(raw).strip().lower()
    if text in YES:
        return True, True
    if text in NO:
        return False, True
    return None, False


def parse_family(raw: str | None) -> tuple[str | None, bool]:
    """no / one / two_or_more / unknown_count; (value, readable)."""
    if raw is None:
        return None, True
    text = str(raw).strip().lower().replace(" ", "")
    if text in NO:
        return "no", True
    if text in {"2+", "2", "3", "4", ">=2", "≥2", "two_or_more", "两位及以上", "2个及以上", "多位"}:
        return "two_or_more", True
    if text in {"1", "one", "一位", "1位", "1个"}:
        return "one", True
    if text in YES:
        return "unknown_count", True
    return None, False


def parse_smoking(raw: str | None) -> tuple[str | None, bool]:
    if raw is None:
        return None, True
    text = str(raw).strip().lower()
    if text in {"current", "yes", "y", "现在吸", "正在吸", "吸烟", "是", "1"}:
        return "current", True
    if text in {"former", "past", "ex", "previous", "已戒", "戒烟", "以前吸"}:
        return "former", True
    if text in {"never", "no", "n", "从不", "不吸", "否", "0"}:
        return "never", True
    return None, False


def parse_country(raw: str | None) -> tuple[str | None, bool]:
    if raw is None or not str(raw).strip():
        return None, True
    text = str(raw).strip().lower()
    for key, names in COUNTRY_ALIASES.items():
        if text in names:
            return key, True
    return "other", True


def age_band(age: float) -> str:
    """The paper splits study populations at 55 years; age 55 itself is placed in the older band."""
    return "under_55" if age < AGE_CUTOFF else "over_55"


def lookup(age: float, sex: str, answers: dict) -> dict:
    """The printed numbers for each group the person belongs to."""
    band = age_band(age)
    matched = [key for key in GROUPS if (answers["family_history"] != "no" if key == "family_history" else answers[key])]
    top = max(matched, key=lambda key: GROUPS[key]["prevalence"][0]) if matched else None
    elevated = [key for key in matched if GROUPS[key]["pr_adjusted"][1] > 1]
    family = answers["family_history"]
    country = answers.get("country")
    country_row = COUNTRIES.get(country) if country else None
    return {
        "age_band": "<55" if band == "under_55" else "≥55",
        "age_band_prevalence_pct": AGE_BANDS[band]["prevalence"][0],
        "sex_prevalence_pct": SEX[sex]["prevalence"][0],
        "female_rr": RR_FEMALE[0] if sex == "female" else None,
        "comorbidity_group": top or "none",
        "comorbidity_group_prevalence_pct": GROUPS[top]["prevalence"][0] if top else None,
        "comorbidity_group_count": len(matched),
        "adjusted_elevated_group_count": len(elevated),
        "family_subgroup_prevalence_pct": FAMILY_SUBGROUPS[family]["prevalence"][0] if family in FAMILY_SUBGROUPS else None,
        "current_smoking_rr": RR_CURRENT_SMOKING[0] if answers["smoking"] == "current" else None,
        "hypertension_rr": RR_HYPERTENSION[0] if answers["hypertension"] else None,
        "country_prevalence_pct": country_row["prevalence"][0] if country_row else None,
        "country_pr_age_sex": country_row["pr_age_sex"][0] if country_row and country_row["pr_age_sex"] else None,
        "_matched": matched,
        "_elevated": elevated,
    }


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _collect(manifest: dict, age, sex_raw, raw: dict) -> tuple[list, str | None, dict]:
    problems = list(skillkit.check_scalar(manifest, "age", age))
    sex = parse_sex(sex_raw)
    if sex is None:
        problems.append(skillkit.Problem("sex", "性别", "missing", "需要性别（男或女）：论文分别印出女性和男性的患病率。"))
    answers: dict = {}
    for name in YES_NO_FLAGS:
        value, ok = parse_yes_no(raw.get(name))
        label = skillkit.spec_by_key(manifest, name).get("label_zh", name)
        flag = "--" + name.replace("_", "-")
        if not ok:
            problems.append(skillkit.Problem(name, label, "parse", f"{flag} 只接受 yes 或 no（是/否），收到「{raw.get(name)}」。"))
        elif value is None:
            problems.append(skillkit.Problem(name, label, "missing", f"缺少「{label}」（{flag} yes 或 no）。"))
        answers[name] = value
    for name, parser, accepted in (
        ("family_history", parse_family, "no、1 或 2+（一级亲属里患病的人数；只知道有、不知道几位时写 yes）"),
        ("smoking", parse_smoking, "current、former 或 never（现在吸、已戒、从不吸）"),
    ):
        value, ok = parser(raw.get(name))
        label = skillkit.spec_by_key(manifest, name).get("label_zh", name)
        flag = "--" + name.replace("_", "-")
        if not ok:
            problems.append(skillkit.Problem(name, label, "parse", f"{flag} 只接受 {accepted}，收到「{raw.get(name)}」。"))
        elif value is None:
            problems.append(skillkit.Problem(name, label, "missing", f"缺少「{label}」（{flag} {accepted}）。"))
        answers[name] = value
    answers["country"], _ = parse_country(raw.get("country"))
    return problems, sex, answers


def write_report(out_dir: Path, age: float | None, sex_raw: str | None, raw: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "problems.json").exists():
        (out_dir / "problems.json").unlink()
    manifest = skillkit.load_manifest(__file__)
    problems, sex, answers = _collect(manifest, age, sex_raw, raw)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {key: None for key in OUTPUT_KEYS})
        return path

    found = lookup(age, sex, answers)
    yes_no = lambda value: "是" if value else "否"
    family_text = {"no": "无", "one": "一位亲属", "two_or_more": "两位及以上亲属", "unknown_count": "有（人数未说明）"}
    smoking_text = {"current": "现在吸烟", "former": "已戒烟", "never": "从不吸烟"}
    lines = [f"# {TITLE}", "", "## 你给的信息", ""]
    lines.append(f"- 年龄 {age:g} 岁，{'女' if sex == 'female' else '男'}")
    lines.append(f"- 多囊肾病（ADPKD）{yes_no(answers['adpkd'])}；结缔组织病（马方、埃勒斯-当洛斯、Loeys-Dietz）{yes_no(answers['connective_tissue'])}；"
                 f"动脉粥样硬化相关病 {yes_no(answers['atherosclerosis'])}")
    lines.append(f"- 一级亲属动脉瘤或动脉瘤破裂出血：{family_text[answers['family_history']]}；{smoking_text[answers['smoking']]}；高血压 {yes_no(answers['hypertension'])}")
    if answers["country"]:
        name = COUNTRIES[answers["country"]]["label_zh"] if answers["country"] in COUNTRIES else "论文附录表 6 没有单列的国家"
        lines.append(f"- 国家：{name}")

    lines += ["", "## 你落在论文的哪些人群", ""]
    lines.append(f"- 参考人群（无合并病、一半女性、平均 50 岁）：估计患病率 {ci(REFERENCE_PREVALENCE)}，预测区间 {num(REFERENCE_PREDICTION_INTERVAL[0])}%–{num(REFERENCE_PREDICTION_INTERVAL[1])}%。下面的比值都以它或以对应的无该因素者为参照。")
    band = age_band(age)
    lines.append(f"- 年龄：{AGE_BANDS[band]['label_zh']}，患病率 {ci(AGE_BANDS[band]['prevalence'])}。论文按研究人群的平均年龄在 55 岁处分两档，不是按个人年龄；55 岁整按 55 岁以上算。"
                 f"论文另写每多一岁患病率相对增加 {AGE_PER_YEAR_PRINTED}，记法有歧义，这里不据此换算。")
    sex_row = SEX[sex]
    sex_counts = f"{sex_row['events']}/{sex_row['total']}"
    lines.append(f"- 性别：{'女性' if sex == 'female' else '男性'}患病率 {ci(sex_row['prevalence'], counts=sex_counts)}。女性相对男性的风险比 {ci(RR_FEMALE, '')}。")
    if found["_matched"]:
        for key in found["_matched"]:
            row = GROUPS[key]
            note = "校正年龄和性别后仍高于参考人群" if key in found["_elevated"] else "校正年龄和性别后置信区间包含 1，是否高于参考人群不确定"
            counts = f"{row['events']}/{row['total']}"
            lines.append(f"- {row['label_zh']}：患病率 {ci(row['prevalence'], counts=counts)}，"
                         f"相对参考人群的患病率比 {ci(row['pr_crude'], '')}，校正年龄和性别后 {ci(row['pr_adjusted'], '')}；{note}。证据确定性（GRADE）{row['grade_zh']}。")
            if key == "family_history" and answers["family_history"] in FAMILY_SUBGROUPS:
                sub = FAMILY_SUBGROUPS[answers["family_history"]]
                lines.append(f"  - 其中{sub['label_zh']}的研究：患病率 {ci(sub['prevalence'])}。")
        top = GROUPS[found["comorbidity_group"]]
        if len(found["_matched"]) > 1:
            lines.append(f"- 你同时属于 {len(found['_matched'])} 个合并病人群。论文没有同时有几种病的人的数，这里只报各组自己的数，"
                         f"点估计最高的是「{top['label_zh']}」{num(top['prevalence'][0])}%；几组的比值不相乘。")
    else:
        lines.append("- 合并病：不属于论文单列的四类人群（多囊肾病、结缔组织病、一级亲属患病、动脉粥样硬化相关病）。")
    if answers["smoking"] == "current":
        lines.append(f"- 现在吸烟：相对不吸烟者（从不吸或已戒）的风险比 {ci(RR_CURRENT_SMOKING, '')}（7 项健康人研究）。")
    elif answers["smoking"] == "former":
        lines.append(f"- 已戒烟：论文把已戒烟者归在“不吸烟”参照组，没有单独的数。论文另印“任何吸烟对不吸烟”的风险比 {ci(RR_ANY_SMOKING, '')}，吸烟的定义随原研究而定。")
    else:
        lines.append("- 从不吸烟：属于吸烟比较里的参照组。")
    if answers["hypertension"]:
        lines.append(f"- 高血压：相对无高血压者的风险比 {ci(RR_HYPERTENSION, '')}（各研究自己的定义）；只用“血压 >140/90 mmHg 或在用降压药”定义的 7 项研究为 {ci(RR_HYPERTENSION_STRICT, '')}。")
    else:
        lines.append("- 无高血压：属于高血压比较里的参照组。")
    if answers["country"] in COUNTRIES:
        row = COUNTRIES[answers["country"]]
        country_counts = f"{row['events']}/{row['total']}"
        text = f"- {row['label_zh']}的健康人研究：患病率 {ci(row['prevalence'], counts=country_counts)}"
        if row["pr_age_sex"]:
            text += f"；以美国为参照，粗患病率比 {ci(row['pr_crude'], '')}，校正年龄和性别后 {ci(row['pr_age_sex'], '')}"
        else:
            text += "；美国是国家比较的参照"
        lines.append(text + "。论文正文的结论是校正年龄和性别后各国患病率没有显著差别。")
    elif answers["country"] == "other":
        lines.append("- 国家：论文附录表 6 只单列了 8 个国家，你的国家没有单独的数。")

    lines += ["", "## 怎么读", "",
              f"- 这些数来自不同研究的不同人群，每个数只回答“像你这样的一类人里，查到未破裂颅内动脉瘤的比例”。论文没有把年龄、性别、合并病、吸烟、高血压放进同一个模型，所以这里不把它们乘成一个“你的概率”。",
              f"- 时间趋势：用 MRA 或 CTA 做的健康人研究里，2016–2022 年的患病率 {ci(RECENT_IMAGING['2016_2022'])}，2002–2015 年 {ci(RECENT_IMAGING['2002_2015'])}；校正年龄和性别后比值 {ci(RECENT_IMAGING['pr_age_sex'], '')}。近年的研究普遍更高，部分来自更容易查到小动脉瘤。",
              "- 查到的大多数是 5 mm 以下的小动脉瘤。患病率不等于破裂风险；已经查到动脉瘤的人，这份报告不适用。",
              "", f"边界: {BOUNDARY}"]
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(lines) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {key: found[key] for key in OUTPUT_KEYS})
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--adpkd", help="yes/no: autosomal dominant polycystic kidney disease")
    parser.add_argument("--connective-tissue", dest="connective_tissue", help="yes/no: Marfan, Ehlers-Danlos or Loeys-Dietz syndrome")
    parser.add_argument("--family-history", dest="family_history", help="no, 1, 2+ (first-degree relatives with aSAH or UIA), or yes")
    parser.add_argument("--atherosclerosis", help="yes/no: carotid stenosis, ischaemic stroke, ischaemic heart disease and similar")
    parser.add_argument("--smoking", help="current, former or never")
    parser.add_argument("--hypertension", help="yes/no")
    parser.add_argument("--country", help="optional: one of the eight countries of Appendix Table 6")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    raw = {name: getattr(args, name) for name in ("adpkd", "connective_tissue", "family_history", "atherosclerosis",
                                                    "smoking", "hypertension", "country")}
    path = write_report(args.out, args.age, args.sex, raw)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
