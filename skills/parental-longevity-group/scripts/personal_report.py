#!/usr/bin/env python3
"""Parental longevity group (high / medium / low) from both parents' ages, with the
cut-off and exclusion rule printed by Seidu et al. (GeroScience 2026, Gothenburg H70).

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
    EARLY_DEATH_EXCLUSION_YEARS,
    FDR_LOST_ZH,
    FINDINGS_ZH,
    GROUP_BY_REACHED,
    GROUP_ZH,
    SEX_INTERACTION_ZH,
    SURVIVAL_CUTOFF_YEARS,
)

TITLE = "父母长寿分组（哥德堡 H70 队列）"
PARENTS = (("father", "父亲"), ("mother", "母亲"))


def parent_state(death_age: float | None, current_age: float | None) -> str:
    """One parent: 'early' (died before 41), 'reached' (85 or older, dead or alive),
    'not_reached' (died before 85), 'pending' (alive and younger than 85)."""
    if death_age is not None:
        if death_age < EARLY_DEATH_EXCLUSION_YEARS:
            return "early"
        return "reached" if death_age >= SURVIVAL_CUTOFF_YEARS else "not_reached"
    return "reached" if current_age >= SURVIVAL_CUTOFF_YEARS else "pending"


def classify(states: list[str]) -> dict:
    """Group from the two parents' states (Methods, "Definition of the PL groups")."""
    reached = states.count("reached")
    if "early" in states:
        return {"status": "excluded", "group": None, "floor": None, "reached": reached}
    if "pending" in states:
        return {"status": "provisional", "group": None, "floor": GROUP_BY_REACHED[reached], "reached": reached}
    return {"status": "determined", "group": GROUP_BY_REACHED[reached], "floor": GROUP_BY_REACHED[reached], "reached": reached}


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def parent_problems(values: dict) -> list:
    problems = []
    for key, name in PARENTS:
        dead, alive = values.get(f"{key}_death_age_a"), values.get(f"{key}_current_age_a")
        if dead is not None and alive is not None:
            problems.append(skillkit.Problem(
                f"{key}_death_age_a", f"{name}年龄", "duplicate",
                f"{name}同时填了去世年龄和目前年龄，请只留一项：已去世写去世时年龄，在世写目前年龄。"))
        elif dead is None and alive is None:
            problems.append(skillkit.Problem(
                f"{key}_death_age_a", f"{name}年龄", "missing",
                f"缺少{name}的年龄：已去世写去世时年龄，在世写目前年龄。论文对缺一方年龄的人不补值、不分组。"))
    return problems


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _parent_line(name: str, dead: float | None, alive: float | None, state: str) -> str:
    if dead is not None:
        base = f"{name}去世时 {dead:g} 岁"
    else:
        base = f"{name}在世，目前 {alive:g} 岁"
    note = {
        "early": f"（不到 {EARLY_DEATH_EXCLUSION_YEARS} 岁去世，论文把这种情况排除在分组之外）",
        "reached": f"（活到了 {SURVIVAL_CUTOFF_YEARS} 岁）",
        "not_reached": f"（没活到 {SURVIVAL_CUTOFF_YEARS} 岁）",
        "pending": f"（还没到 {SURVIVAL_CUTOFF_YEARS} 岁，结果未定）",
    }[state]
    return f"- {base}{note}"


def report_lines(values: dict, states: dict, result: dict, mean_age: float, sex: str | None, age: float | None) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    for key, name in PARENTS:
        lines.append(_parent_line(name, values.get(f"{key}_death_age_a"), values.get(f"{key}_current_age_a"), states[key]))
    who = []
    if sex:
        who.append("男" if sex == "male" else "女")
    if age is not None:
        who.append(f"{age:g} 岁")
    if who:
        lines.append("- 你：" + "，".join(who))
    lines += ["", "## 结果", ""]
    status = result["status"]
    if status == "excluded":
        lines.append(f"- 有一方父母在 {EARLY_DEATH_EXCLUSION_YEARS} 岁前去世。论文认为这多半和衰老无关（例如意外），把这类人排除在分组之外，所以这里不给分组。")
    elif status == "provisional":
        lines.append(f"- 目前活到 {SURVIVAL_CUTOFF_YEARS} 岁的父母：{result['reached']} 位；另有在世、还不到 {SURVIVAL_CUTOFF_YEARS} 岁的，最终分组未定。")
        lines.append(f"- 按现在的情况，至少是“{GROUP_ZH[result['floor']]}”。论文的父母都已到 85 岁前后，没有处理父母尚未满 85 岁的情况，这一点是本技能的操作约定。")
    else:
        lines.append(f"- 活到 {SURVIVAL_CUTOFF_YEARS} 岁的父母：{result['reached']} 位。")
        lines.append(f"- 父母长寿分组：**{GROUP_ZH[result['group']]}**（论文记作 {result['group']}）。")
    lines.append(f"- 父母年龄均值（去世或目前年龄）：{mean_age:.1f} 岁。论文把它作为连续变量另做分析，没有给切点。")

    lines += ["", "## 论文里这一组的人怎样", ""]
    group = result["group"]
    if group in FINDINGS_ZH:
        lines.append(f"论文 1126 名 70 岁瑞典人里，和“低”组（双亲都没活到 85 岁）相比，“{GROUP_ZH[group]}”这一组平均而言：")
        lines += [f"- {item}" for item in FINDINGS_ZH[group]]
        if group == "high-PL":
            lines.append(f"- {FDR_LOST_ZH}")
        if group == "medium-PL" and sex == "female":
            lines.append(f"- {SEX_INTERACTION_ZH}")
    elif group == "low-PL":
        lines.append("“低”组是论文的参照组。论文发现另外两组在教育、认知、炎症、同型半胱氨酸、吸烟和血压等方面平均更有利；"
                     "这是群体平均，不说明你个人的这些指标一定更差。")
    else:
        lines.append("没有确定的分组，所以不套用论文各组的比较结果。")
    lines.append("这些是约 70 岁时同一次检查里的横断面关联（只有 pTau217 是约 6 年随访的变化），不能说明因果。论文作者认为父母长寿可以作为衰老相关疾病筛查的线索，这一点还没有前瞻性研究证实。")

    lines += ["", "## 可以怎么用", ""]
    lines.append("父母长寿是一个免费、好问的家族史信息。不论分在哪一组，都可以把血压、血脂、同型半胱氨酸、炎症指标和认知筛查放进常规体检，结果请和医生一起解读。")

    lines += ["", "## 说明", ""]
    lines.append(f"- 论文人群：哥德堡 H70 出生队列，{COHORT['birth_year']} 年出生、2014–2016 年约 70 岁的 {COHORT['n']} 人；"
                 f"高 {COHORT['n_high']} 人（{COHORT['pct_high']}%）、中 {COHORT['n_medium']} 人（{COHORT['pct_medium']}%）、低 {COHORT['n_low']} 人（{COHORT['pct_low']}%）。"
                 f"{COHORT['n_followup']} 人约 {COHORT['followup_years']} 年后复查。")
    lines.append("- 父母年龄是受访者自报的，论文没有核实。父母的出生年代（约 1920 年）队列预期寿命约 74 岁，所以 85 岁算长寿；你的父母年代不同时，这个切点的含义可能不同。")
    lines.append("- 论文另算了多基因长寿评分（PRS-CS，有无 APOE 位点两版），每个位点的权重没有公布，本技能不算。论文里父母长寿分组和多基因评分之间没有关联（补充表 S1）。")
    if age is not None and not 65 <= age <= 80:
        lines.append(f"- 你的年龄 {age:g} 岁，论文人群是 70 岁左右；各组比较结果对你不一定适用。")
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
    values = dict(collected.values)
    flagged = {p.key for p in problems}
    problems += [p for p in parent_problems(values)
                 if not ({p.key, p.key.replace("death", "current")} & flagged)]
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if sex and person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex}”，请写男或女，或者不填。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    states = {key: parent_state(values.get(f"{key}_death_age_a"), values.get(f"{key}_current_age_a")) for key, _ in PARENTS}
    result = classify([states["father"], states["mother"]])
    ages = [values.get(f"{key}_death_age_a", values.get(f"{key}_current_age_a")) for key, _ in PARENTS]
    mean_age = sum(ages) / 2
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(values, states, result, mean_age, person_sex, age)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "pl_group": result["group"],
        "pl_status": result["status"],
        "pl_group_floor": result["floor"],
        "parents_reached_85": result["reached"],
        "parents_mean_age_a": round(mean_age, 2),
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 父亲去世年龄 或 父亲目前年龄；母亲去世年龄 或 母亲目前年龄（岁）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
