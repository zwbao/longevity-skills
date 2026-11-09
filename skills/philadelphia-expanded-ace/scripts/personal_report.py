#!/usr/bin/env python3
"""Count Philadelphia expanded ACEs from the 21 items and read the paper's tables for that category.

Temple et al., JAMA Netw Open 2026;9(9):e2635834. Item coding: eTable 1. Categories: Methods.
Cohort rates and odds ratios: Tables 2 and 3. The cohort numbers stay the cohort's; the report
never turns them into this person's probability.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    CATEGORIES,
    CATEGORY_N,
    CATEGORY_ZH,
    DOMAINS,
    ITEMS,
    OUTCOMES,
    SCALES,
    TABLE2,
    TABLE3,
    TABLE3_NOTES,
    TITLE,
)

ITEM_BY_KEY = {item[0]: item for item in ITEMS}
COHORT_AGE = (18, 20)


# ---------------------------------------------------------------- reading the file

def has_header(line: str) -> bool:
    cells = {skillkit.fold_name(cell.strip().strip('"')) for cell in re.split(r"[,\t]", line)}
    names = {skillkit.fold_name(name) for name in skillkit.NAME_COLUMNS}
    values = {skillkit.fold_name(name) for name in skillkit.VALUE_COLUMNS}
    return bool(cells & names) and bool(cells & values)


def _cell(row: Dict[str, str], columns) -> str:
    folded = {skillkit.fold_name(key): value for key, value in row.items()}
    for name in columns:
        value = folded.get(skillkit.fold_name(name))
        if value is not None:
            return value
    return ""


def measurement_rows(path: Optional[Path]) -> List[Dict[str, str]]:
    """Rows as item/value/unit. A file with an item,value,unit header is read by skillkit;
    otherwise each line is name,value[,unit]."""
    if path is None:
        return []
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    if lines and has_header(lines[0]):
        return [
            {
                "item": _cell(row, skillkit.NAME_COLUMNS),
                "value": _cell(row, skillkit.VALUE_COLUMNS),
                "unit": _cell(row, skillkit.UNIT_COLUMNS),
            }
            for row in skillkit.read_rows(path)
        ]
    rows = []
    for line in lines:
        parts = [p.strip() for p in line.replace("，", ",").split(",")]
        if len(parts) >= 2:
            rows.append({"item": parts[0], "value": parts[1], "unit": parts[2] if len(parts) > 2 else ""})
    return rows


def collect_inputs(manifest, measurements: Optional[Path], age: Optional[float]):
    """Item codes keyed by input key, and the problems that stop the computation.

    Text answers ('more than once', '有时符合', 是/否) are turned into the item's code first;
    then skillkit checks names, units and ranges. A missing item is not a problem here.
    """
    rows = measurement_rows(measurements)
    index = skillkit.alias_index(skillkit.input_specs(manifest))
    for row in rows:
        hit = next((index[name] for name in skillkit.name_variants(row["item"]) if name in index), None)
        if not hit or hit[0]["key"] not in ITEM_BY_KEY:
            continue
        scale = SCALES[ITEM_BY_KEY[hit[0]["key"]][3]]
        token = row["value"].strip().lower()
        if token in scale["text"]:
            row["value"] = str(scale["text"][token])
    collected = skillkit.collect_measurements(rows, manifest)
    problems = [p for p in collected.problems if p.kind != "missing"]
    problems += [p for p in skillkit.check_scalar(manifest, "age", age) if p.kind != "missing"]
    codes: Dict[str, int] = {}
    for key, value in collected.values.items():
        if key not in ITEM_BY_KEY:
            continue
        if value != int(value):
            label = skillkit.spec_by_key(manifest, key)["label_zh"]
            options = "、".join(f"{code}={name}" for code, name in SCALES[ITEM_BY_KEY[key][3]]["codes"].items())
            problems.append(skillkit.Problem(key, label, "range", f"{label} 读成 {value:g}。这一题只收整数选项：{options}。"))
            continue
        codes[key] = int(value)
    return codes, problems, collected.unmatched


# ---------------------------------------------------------------- the method

def meets(key: str, code: int) -> bool:
    """eTable 1 threshold for one item."""
    _key, _domain, _label, _scale, op, threshold, _printed = ITEM_BY_KEY[key]
    return code >= threshold if op == ">=" else code <= threshold


def domain_status(codes: Dict[str, int]) -> Dict[str, dict]:
    """Per domain: 'yes', 'no' or 'unknown', the items that met the threshold, the missing items,
    and whether every item met it (for the stricter all-items reading)."""
    out = {}
    for domain, _label, _incidence in DOMAINS:
        keys = [item[0] for item in ITEMS if item[1] == domain]
        hits = [key for key in keys if key in codes and meets(key, codes[key])]
        missing = [key for key in keys if key not in codes]
        if hits:
            status = "yes"
        elif missing:
            status = "unknown"
        else:
            status = "no"
        out[domain] = {"status": status, "hits": hits, "missing": missing, "all": len(hits) == len(keys)}
    return out


def category(count: int) -> str:
    for name, low, high in CATEGORIES:
        if low <= count <= high:
            return name
    raise ValueError(f"ACE count {count} outside 0..14")


def score(codes: Dict[str, int]) -> dict:
    status = domain_status(codes)
    positive = [d for d, s in status.items() if s["status"] == "yes"]
    unknown = [d for d, s in status.items() if s["status"] == "unknown"]
    low, high = len(positive), len(positive) + len(unknown)
    cat_low, cat_high = category(low), category(high)
    result = {
        "status": status,
        "count_min": low,
        "count_max": high,
        "category": cat_low if cat_low == cat_high else None,
        "count": low if not unknown else None,
    }
    if not unknown:
        strict = sum(1 for d in positive if status[d]["all"])
        result["strict_count"] = strict
        result["strict_category"] = category(strict)
    return result


# ---------------------------------------------------------------- the report

def _pct(cell) -> str:
    n, pct = cell
    return f"{pct:.1f}%（{n} 人）"


def outcome_lines(cat: str) -> List[str]:
    lines = []
    if cat == "0":
        lines.append(f"你在 0 条这一档。这一档是论文所有比值比的参照组，所以下表只列这一档在队列里的比例（共 {CATEGORY_N['0']} 人）。")
        lines += ["", "| 结局 | 0 条组的比例 | 全队列的比例 |", "| --- | --- | --- |"]
        for key, label, _group in OUTCOMES:
            lines.append(f"| {label} | {_pct(TABLE2[key]['0'])} | {_pct(TABLE2[key]['overall'])} |")
        return lines
    lines.append(
        f"下表左两列是论文表 2：0 条组和你所在的「{CATEGORY_ZH[cat]}」组（共 {CATEGORY_N[cat]} 人）里有这个结局的人的比例。"
        "右列是论文表 3：校正性别、种族和民族、自评收入、性取向和干预分组后，这一档相对 0 条组的比值比（95% 置信区间）和 P 值。"
    )
    lines += ["", f"| 结局 | 0 条组 | {CATEGORY_ZH[cat]}组 | 比值比（95% CI），P |", "| --- | --- | --- | --- |"]
    notes = []
    for key, label, _group in OUTCOMES:
        or_text, p = TABLE3[key][cat]
        ratio = "NA（并入参照组）" if or_text == "NA" else f"{or_text}，P {p}"
        lines.append(f"| {label} | {_pct(TABLE2[key]['0'])} | {_pct(TABLE2[key][cat])} | {ratio} |")
        if key in TABLE3_NOTES and (key != "dv_exp_psychological" or cat == "4-5"):
            notes.append(f"- {label}：{TABLE3_NOTES[key]}")
    lines += ["", "比值比大于 1 表示这一档的人比 0 条组更常有这个结局；学业三行是好的结局，比值比小于 1 表示更少。置信区间跨过 1 的，这一档和 0 条组的差别没有统计学意义。"]
    if notes:
        lines += ["", *notes]
    return lines


def render(manifest, codes: Dict[str, int], result: dict, age: Optional[float], unmatched: List[str]) -> str:
    status = result["status"]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的逆境条数", ""]
    if result["count"] is not None:
        lines.append(
            f"按论文补充表 eTable 1 的计分，14 类童年逆境里你符合 {result['count']} 类，"
            f"落在论文的「{CATEGORY_ZH[result['category']]}」这一档。"
        )
    else:
        lines.append(
            f"有题没答，逆境条数在 {result['count_min']} 到 {result['count_max']} 之间；"
            f"两端都落在论文的「{CATEGORY_ZH[result['category']]}」这一档，所以分档已经确定。"
        )
    lines.append("")
    for domain, label, _inc in DOMAINS:
        s = status[domain]
        if s["status"] == "yes":
            why = "；".join(
                f"「{ITEM_BY_KEY[key][2]}」答{SCALES[ITEM_BY_KEY[key][3]]['codes'][codes[key]]}" for key in s["hits"]
            )
            lines.append(f"- {label}：符合。依据：{why}。")
        elif s["status"] == "no":
            lines.append(f"- {label}：不符合。")
        else:
            lines.append(f"- {label}：未知，缺 {'、'.join(ITEM_BY_KEY[key][2] for key in s['missing'])}。")
    if "strict_count" in result and result["strict_count"] != result["count"]:
        same = "仍是同一档" if result["strict_category"] == result["category"] else f"会落在「{CATEGORY_ZH[result['strict_category']]}」"
        lines += ["", f"两题一类的逆境，本报告按任一题达到阈值就算符合（eTable 1 没写两题都要满足）。若改成两题都要满足，条数是 {result['strict_count']}，{same}。"]
    lines += ["", "## 研究队列里这一档的情况", "", *outcome_lines(result["category"])]
    lines += ["", "## 怎么读", ""]
    lines.append(
        "这些比例和比值比来自美国得克萨斯州东南部学校招募的约 19 岁青年（分析样本 1850 人），"
        "是一群人里的平均情况，不是你自己会不会出现这些结局的概率。逆境条数是回顾性自填，研究是观察性的，不能说明因果。"
    )
    lines.append("论文还发现，在同一模型里同时放入 14 类时，情感虐待、性虐待、目睹家庭暴力和感到被歧视与抑郁、创伤后应激和约会暴力的关联最一致（表 4）。本报告不按单类逆境另算风险。")
    if age is not None and not COHORT_AGE[0] <= age <= COHORT_AGE[1]:
        lines.append(f"你填的年龄是 {age:g} 岁。论文的结局是在 18 到 19 岁前后测的，别的年龄段的比例可能不同。")
    lines += ["", "## 不能算的", ""]
    missing = [key for key in ITEM_BY_KEY if key not in codes]
    if missing:
        lines.append(f"没答的题：{'、'.join(ITEM_BY_KEY[key][2] for key in missing)}。缺的题不当作「没有」。")
    if unmatched:
        lines.append(f"这些行的名称对不上任何一题，没有读入：{'、'.join(unmatched)}。")
    lines.append("论文没有给个人发生概率的方程（表 3 只印了比值比，没有截距），所以报告不算你自己的风险。")
    lines += ["", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def with_paper_card(text: str) -> str:
    title, _newline, rest = text.partition("\n")
    return "\n".join([title, "", *paper_card_lines(), "", rest.lstrip("\n")])


EMPTY = {"ace_count": None, "ace_category": None}


def report(out: Path, measurements: Optional[Path], age: Optional[float] = None) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    stale = out / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    codes, problems, unmatched = collect_inputs(manifest, measurements, age)
    result = None
    if not problems:
        result = score(codes)
        if result["category"] is None:
            for domain, s in result["status"].items():
                for key in s["missing"] if s["status"] == "unknown" else []:
                    label = skillkit.spec_by_key(manifest, key)["label_zh"]
                    problems.append(skillkit.Problem(key, label, "missing", f"缺少「{label}」这一题。"))
            problems.append(skillkit.Problem(
                "", "", "missing",
                f"有题没答，逆境条数可能在 {result['count_min']} 到 {result['count_max']} 之间，跨了论文的分档，所以没有分档。缺的题不当作「没有」。",
            ))
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        path.write_text(with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out, manifest, dict(EMPTY))
        return path
    path = out / "report.md"
    path.write_text(render(manifest, codes, result, age, unmatched), encoding="utf-8")
    skillkit.write_result(out, manifest, {
        "ace_count": result["count"],
        "ace_category": result["category"],
    })
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, required=True, help="21 题的答案：item,value,unit")
    parser.add_argument("--age", type=float)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    report(args.out, args.measurements, args.age)
    if (args.out / "problems.json").exists():
        return skillkit.EXIT_INPUT_PROBLEM
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
