"""Offline lookup of published male CKB tobacco-amount strata; no risk fitting."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AREAS, BANDS, BOUNDARY, CUTPOINTS, INPUT_KEY, OUTCOMES, TABLE_2, TITLE


def band_index(amount):
    return sum(amount >= point for point in CUTPOINTS)


def lookup(amount, area):
    index = band_index(amount)
    result = {INPUT_KEY: amount, "amount_band": BANDS[index], "area": area}
    for key, cell in zip(OUTCOMES, TABLE_2[area][index]):
        for suffix, value in zip(("rr", "gsci_lower", "gsci_upper"), cell):
            result[f"{key}_{suffix}"] = value
    return result


def collect(path, manifest):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, "每日烟草当量", "file", f"无法读取输入文件：{exc}")]
    problems = list(data.problems)
    if data.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, "每日烟草当量", "unknown", "无法识别的项目：" + "、".join(data.unmatched)))
    return data.values, problems


def rr_delta(current, other):
    return {f"{key}_rr": round(other[f"{key}_rr"] - current[f"{key}_rr"], 10) for key in OUTCOMES}


def make_levers(amount, area, target=None):
    current = lookup(amount, area)
    index = band_index(amount)
    neighbors = []
    for other_index in (index - 1, index + 1):
        if 0 <= other_index < len(BANDS):
            cells = TABLE_2[area][other_index]
            outputs = {f"{key}_rr": cell[0] for key, cell in zip(OUTCOMES, cells)}
            neighbors.append({"amount_band": BANDS[other_index], "outputs": outputs,
                              "rr_delta": rr_delta(current, outputs)})
    result = {
        "schema": "longevity-levers/1", "model": "china-tobacco-mortality-lookup",
        "current": current,
        "sensitivity": [{"key": INPUT_KEY, "unit": "g/d", "value": amount,
                         "method": "adjacent_printed_categories", "derivative": None,
                         "neighbors": neighbors}],
        "levers": [],
        "note_zh": "仅比较同一城乡分层的历史人群关联。分档没有连续导数；邻档仅列已印出的RR，不要求达到任何吸烟量。不计算差值置信区间。目标差不是减量或戒烟的因果效应，农村非单调结果不能解释为多吸更安全。因病停烟者的输入是历史吸烟量，情景不表示重新吸烟。",
    }
    if target is not None:
        other = lookup(target, area)
        delta = rr_delta(current, other)
        result["targets"] = {"values": {INPUT_KEY: target}, "outputs": other, "rr_delta": delta}
        result["levers"] = [{"key": INPUT_KEY, "label_zh": "每日烟草当量", "unit": "g/d",
                             "from": amount, "to": target, "outputs": other, "rr_delta": delta}]
    return result


def table(result):
    body = ["| 研究结局 | 对应人群 RR | 组别特异性 95% 区间 |", "|---|---:|---|"]
    for key, label in OUTCOMES.items():
        rr, lo, hi = (result[f"{key}_{suffix}"] for suffix in ("rr", "gsci_lower", "gsci_upper"))
        body.append(f"| {label} | {rr:.2f} | {lo:.2f}–{hi:.2f} |")
    return body


def render(result, smoking, target=None):
    timing = "停烟前最后规律吸烟时" if smoking == "stopped_ill" else "目前规律吸烟时"
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的查表结果", "",
             f"按你提供的{AREAS[result['area']]}环境，{timing}每日烟草当量为 {result[INPUT_KEY]:g} g/d，匹配表 2 的 {result['amount_band']} 档。", "",
             "烟草当量按论文口径为每日卷烟支数加每日其他烟草克数；这里的 g/d 当量不是卷烟实际重量、焦油或尼古丁量。", "",
             *table(result), "",
             "RR 的参照是同研究中从未规律吸烟者（包括从未规律、仅偶尔吸烟者）。这些是人群死亡率比，不是你的死亡概率；RR 为 1 也不表示没有风险。", "",
             "表内区间只反映该吸烟量组的对数风险方差，未合并参照组方差，不能称为通常的两组比较置信区间，更不是你的个人预测区间。", "",
             "使用的是 CKB 在 2006–14 年随访、40–79 岁死亡分析的结果，按研究地区和五岁年龄组分层，并调整教育和饮酒。当前年龄只用于适用范围检查，不会重新校准表值；城乡历史差异也不能解释为迁居的效果。", "",
             "本文为减少反向因果偏倚，将因病停烟者与仍吸烟者合并；主动戒烟者不在本查表人群中。因病停烟者应填写停烟前的量，不能填零；这里不估计戒烟收益。", "",
             "农村分档并非所有结局都随吸烟量单调上升，作者讨论了疾病症状导致减量等反向因果因素；不能据此认为多吸更安全。", "",
             "缺血性卒中与缺血性心脏病是合并死亡结局，不能拆成各自风险或发病率。附录 Webtable 1 中 COPD 分组使用 ICD-10 J40–J44、I26–I27（含肺血管疾病编码），保留原文分组口径。"]
    if target is not None:
        lines += ["", "## 你指定的情景", "", f"每日烟草当量 {target:g} g/d，对应同一城乡分层的另一查表情景。", "",
                  *table(lookup(target, result["area"])), "",
                  "情景仅用于比较分组关联，不表示建议达到这个量，也不是改变吸烟量的因果收益。零吸烟量和戒烟后的风险不由此表推算。"]
    return "\n".join(lines + ["", f"边界: {BOUNDARY}"]) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--area")
    parser.add_argument("--smoking")
    parser.add_argument("--regular-six-months")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
        if age is not None and not age.is_integer():
            problems.append(skillkit.Problem("age", "周岁", "unsupported", "请提供40–79岁的整数周岁；年龄不参与风险校准。"))
    except ValueError:
        problems.append(skillkit.Problem("age", "周岁", "parse", "周岁必须是有限数值。"))
    for key, value, allowed, message in (
        ("sex", args.sex, ("male",), "表2仅支持男性（male），没有女性的吸烟量分层。"),
        ("area", args.area, tuple(AREAS), "请按长期居住环境明确城乡：urban或rural；无法匹配时不猜。"),
        ("smoking", args.smoking, ("current", "stopped_ill"), "请明确current（当前吸烟）或stopped_ill（因病停烟）；主动戒烟及从未规律吸烟者不适用。"),
        ("regular_six_months", args.regular_six_months, ("yes",), "需确认曾每日≥1支卷烟或≥1g烟草持续至少6个月（yes），否则不适用。"),
    ):
        if value not in allowed:
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "missing" if value is None else "unsupported", message))
    target = None
    if args.targets is not None:
        target_values, target_problems = collect(args.targets, manifest)
        for problem in target_problems:
            problem.message_zh = "目标文件：" + problem.message_zh
        problems += target_problems
        target = target_values.get(INPUT_KEY)
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {x["key"]: None for x in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    amount = values[INPUT_KEY]
    result = lookup(amount, args.area)
    skillkit.write_result(args.out, manifest, result)
    (args.out / "report.md").write_text(render(result, args.smoking, target), encoding="utf-8")
    (args.out / "levers.json").write_text(json.dumps(make_levers(amount, args.area, target), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
