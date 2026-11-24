#!/usr/bin/env python3
"""Offline, manifest-checked lookup of published smoking RR predictions."""
import argparse
import csv
import io
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, OUTCOMES, SCENARIO_NOTE, TITLE


def problem(key, kind, message):
    return skillkit.Problem(key, key, kind, message)


def resolve_outcome(name):
    if name is None:
        return None
    for row in OUTCOMES.values():
        labels = [row["key"], row["label_zh"], row["printed_label"], row["printed_label"].split(" (")[0]]
        if any(skillkit.fold_name(name) == skillkit.fold_name(x) for x in labels):
            return row
    return None


def lookup(row, exposure):
    """Return exact published predictions or explicitly labelled reference points.

    A 1e-10 absolute comparison absorbs floating point representation only;
    it does not round a person's measurement to a published dose.
    """
    if row["exposure_key"] is None:
        return {"status": "binary", **row["binary"], "references": []}
    points = row["points"]
    exact = next((p for p in points if math.isclose(p["exposure"], exposure, rel_tol=0, abs_tol=1e-10)), None)
    if exact:
        return {"status": "exact_printed_point", **exact, "references": []}
    below = [p for p in points if p["exposure"] < exposure]
    above = [p for p in points if p["exposure"] > exposure]
    refs = ([below[-1]] if below else []) + ([above[0]] if above else [])
    return {"status": "between_printed_points" if below and above else "outside_printed_points",
            "rr": None, "ui_lower": None, "ui_upper": None, "references": refs}


def read_file(path, manifest):
    try:
        # skillkit intentionally ignores unnamed surplus CSV fields. Here reject
        # structural mistakes before using its alias/unit/range validation.
        if path is not None:
            text = path.read_text(encoding="utf-8-sig")
            sample = text[:2048]
            delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
            rows = csv.reader(io.StringIO(text), delimiter=delimiter, strict=True)
            header = next(rows, [])
            if any(row and len(row) != len(header) for row in rows):
                raise ValueError("数据列数与表头不一致，请检查多余分隔符或未加引号的数值。")
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error) as exc:
        return {}, [problem("measurements", "file", f"无法读取CSV/TSV测量表：{exc}")]
    problems = list(collected.problems)
    if collected.unmatched:
        problems.append(problem("measurements", "unknown", "无法识别项目：" + "、".join(collected.unmatched)))
    return collected.values, problems


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def levers(row, exposure, current, targets):
    key = row["exposure_key"]
    result = {"schema": "longevity-levers/1", "model": "smoking-burden-of-proof",
              "model_zh": TITLE, "outcome": row["key"], "current": {"exposure": exposure, **current},
              "sensitivity": [], "levers": [], "note_zh": SCENARIO_NOTE}
    if key:
        # No fitted curve is available in this implementation. Never fabricate a derivative.
        sensitivity = {"key": key, "value": exposure, "unit": row["printed_unit"],
                       "rr_per_unit": None, "status": "discrete_reference_only", "comparisons": []}
        points = row["points"]
        below = [p for p in points if p["exposure"] < exposure]
        above = [p for p in points if p["exposure"] > exposure]
        for point in ([below[-1]] if below else []) + ([above[0]] if above else []):
            sensitivity["comparisons"].append({**point, "rr_delta": point["rr"] - current["rr"] if current["rr"] is not None else None})
        result["sensitivity"].append(sensitivity)
        if key in targets:
            target = lookup(row, targets[key])
            delta = target["rr"] - current["rr"] if target["rr"] is not None and current["rr"] is not None else None
            result["targets"] = {"values": targets, **target, "rr_delta": delta}
            result["levers"] = [{"key": key, "from": exposure, "to": targets[key],
                                  "unit": row["printed_unit"], "rr_delta": delta, "target": target}]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--outcome")
    parser.add_argument("--smoking-status")
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Reusing an output directory must never leave a previous successful result.
    for name in ["report.md", "result.json", "problems.json", "lookup.json", "levers.json"]:
        (args.out / name).unlink(missing_ok=True)
    values, problems = read_file(args.measurements, manifest)
    row = resolve_outcome(args.outcome)
    if row is None:
        problems.append(problem("outcome", "missing" if not args.outcome else "category", "请明确选择结局；可选键见 references/outcomes.md。"))
    if args.smoking_status not in ("current", "当前吸烟"):
        problems.append(problem("smoking_status", "missing" if not args.smoking_status else "population", "须确认当前吸烟；从不吸烟或已戒烟不适用此查表，不能把0当作戒烟后的风险。"))
    age = None
    try:
        if args.age is not None:
            age = skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(problem("age", "parse", "年龄必须是有限数值，单位为岁。"))
    sex = {"男": "male", "女": "female", "male": "male", "female": "female"}.get(args.sex)
    if args.sex is not None and sex is None:
        problems.append(problem("sex", "category", "论文性别分组只接受male/female或男/女。"))
    exposure = None
    if row:
        if row["sex"] and sex != row["sex"]:
            problems.append(problem("sex", "population", f"论文中{row['label_zh']}仅适用于{row['sex']}分组，须提供匹配分组。"))
        reference_age = row["reference_age_years"]
        if reference_age and age is not None and not reference_age[0] <= age < reference_age[1] + 1:
            problems.append(problem("age", "population", f"{row['label_zh']}表2只印出{reference_age[0]}–{reference_age[1]}岁参考组，无法把此表换算到你的年龄。"))
        key = row["exposure_key"]
        if key:
            exposure = values.get(key)
            if exposure is None and not any(p.key == key for p in problems):
                label = skillkit.spec_by_key(manifest, key)["label_zh"]
                problems.append(problem(key, "missing", f"{row['label_zh']}需要{label}；不能用另一种烟史代替。"))
            elif exposure is not None and exposure <= 0:
                problems.append(problem(key, "population", "当前吸烟者须提供大于0的实际暴露；不从零外推。"))
    targets = {}
    if args.targets:
        targets, target_problems = read_file(args.targets, manifest)
        problems += target_problems
        if not targets and not target_problems:
            problems.append(problem("targets", "missing", "比较文件没有可读的烟史。"))
        if row:
            for key, value in targets.items():
                if key != row["exposure_key"] or value <= 0:
                    problems.append(problem(key, "target", "比较项须为本结局使用的正数烟史；不提供戒烟后模型或骨折的剂量比较。"))
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        text = report.read_text()
        header, rest = text.split("\n", 1)
        report.write_text(header + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    found = lookup(row, exposure)
    out_values = {"outcome": row["key"], "lookup_status": found["status"], "exposure": exposure,
                  "exposure_unit": row["printed_unit"], "relative_risk": found["rr"],
                  "ui_lower": found["ui_lower"], "ui_upper": found["ui_upper"], "evidence_stars": row["stars"]}
    skillkit.write_result(args.out, manifest, out_values)
    write_json(args.out / "lookup.json", {"source": "Table 2", "outcome": row["key"],
               "exposure_key": row["exposure_key"], "exposure_unit": row["printed_unit"],
               "input_exposure": exposure, **found})
    scenario = levers(row, exposure, found, targets)
    write_json(args.out / "levers.json", scenario)
    unit = {"pack_years": "包年", "cigarettes_per_day": "支/日", None: "当前吸烟（有/无比较）"}[row["exposure_key"]]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 本次查表", "",
             f"结局：{row['label_zh']}。吸烟状态：当前吸烟。年龄：{age:g}岁。"]
    if exposure is not None:
        lines += [f"提供的烟史：{exposure:g} {unit}。"]
    if row["reference_age_years"]:
        lo, hi = row["reference_age_years"]
        lines += [f"使用论文{lo}–{hi}岁参考年龄组；未额外校正年龄。"]
    if row["sex"]:
        lines += [f"论文此结局的性别分组：{'女性' if row['sex']=='female' else '男性'}。"]
    if found["rr"] is not None:
        lines += ["", f"表2平均相对风险 RR：**{found['rr']:.2f}**；95% 不确定区间：**{found['ui_lower']:.2f}–{found['ui_upper']:.2f}**。",
                  "参照为论文的从不吸烟/零暴露基准（底层研究的对照定义存在差异）；该区间计入研究间异质性，不是个人风险区间。"]
    else:
        lines += ["", "论文表2没有印出与你输入完全相同的暴露点，本次不计算该烟史的RR，也不插值、取整或外推。以下仅为邻近的已发表参考点，不构成你的风险区间。", "",
                  "| 参考暴露量 | 表2平均RR | 95% 不确定区间 |", "|---|---|---|"]
        for p in found["references"]:
            lines.append(f"| {p['exposure']:g} {unit} | {p['rr']:.2f} | {p['ui_lower']:.2f}–{p['ui_upper']:.2f} |")
    lines += ["", f"该结局的研究证据星级：{row['stars']}/5。这是固定的关联证据等级，不是你的病情分级；低星级不表示吸烟安全。"]
    if row["publication_bias"]:
        lines += ["作者对此结局检测到潜在发表偏倚，未据此校正风险。"]
    if row["key"] == "parkinsons_disease":
        lines += ["帕金森病的逆向关联不能解释为吸烟有净健康获益，也不是开始或继续吸烟的依据。"]
    if targets:
        target = scenario["targets"]
        lines += ["", "## 另一烟史的参考比较", "", SCENARIO_NOTE]
        if target["rr"] is not None:
            lines += [f"所给比较烟史的表内RR为{target['rr']:.2f}（95% 不确定区间{target['ui_lower']:.2f}–{target['ui_upper']:.2f}）。"]
            if target["rr_delta"] is not None:
                lines += [f"两处表值之差：{target['rr_delta']:+.2f}。这不是个人风险下降幅度。"]
        else:
            lines += ["比较烟史也未匹配印出的点；不计算目标RR或变化。邻近点见levers.json。"]
    lines += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
