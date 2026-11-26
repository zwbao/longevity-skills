#!/usr/bin/env python3
"""Compare an individual's exposure with printed GBD population thresholds."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (ALCOHOL_KEY, BOUNDARY, GRAMS_PER_STANDARD_DRINK, REGION_ZH,
                     VALUE_KEYS, YEARS, lookup, normalize_region, normalize_sex)

TITLE = "酒精摄入量与 GBD 人群阈值比较"


def side(value, threshold):
    # Values are printed rounded constants, not unrounded posterior estimates.
    if abs(value - threshold) <= 1e-12:
        return "equal_to_printed_mean"
    return "above_printed_mean" if value > threshold else "below_printed_mean"


def calculate(ethanol, row):
    drinks = ethanol / GRAMS_PER_STANDARD_DRINK
    return {**{key: row[key] for key in VALUE_KEYS},
            "ethanol_g_day": ethanol, "standard_drinks_day": drinks,
            "tmrel_gap_g_day": ethanol - row["tmrel_standard_drinks_day"] * GRAMS_PER_STANDARD_DRINK,
            "nde_gap_g_day": ethanol - row["nde_standard_drinks_day"] * GRAMS_PER_STANDARD_DRINK,
            "tmrel_side": side(drinks, row["tmrel_standard_drinks_day"]),
            "nde_side": side(drinks, row["nde_standard_drinks_day"]),
            "reference_region": row["region"], "reference_year": row["year"],
            "reference_age_group": row["age_group"], "reference_sex": row["sex"]}


def make_levers(ethanol, targets, row):
    current = calculate(ethanol, row)
    payload = {
        "schema": "longevity-levers/1", "model": "gbd-alcohol-tmrel-nde",
        "model_zh": "已发表人群阈值的算术比较", "current": current,
        "sensitivity": [{"key": ALCOHOL_KEY, "label_zh": "平均每日纯酒精摄入量", "unit": "g/d",
                         "value": ethanol, "nde_gap_g_day_per_unit": 1,
                         "tmrel_gap_g_day_per_unit": 1}],
        "levers": [],
        "note_zh": "仅展示用户自填情景与固定阈值的差值，不估算风险变化，不生成或推荐饮酒目标。年龄、性别、地区和年份固定。",
    }
    if ALCOHOL_KEY in targets:
        target = targets[ALCOHOL_KEY]
        payload["targets"] = {"values": targets, **calculate(target, row)}
        payload["levers"] = [{"key": ALCOHOL_KEY, "unit": "g/d", "from": ethanol, "to": target,
                             "nde_gap_g_day_delta": target - ethanol,
                             "tmrel_gap_g_day_delta": target - ethanol}]
    return payload


def collect(path, manifest, label, targets=False):
    try:
        got = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {}, [skillkit.Problem(ALCOHOL_KEY, label, "format", f"无法读取{label}文件：{exc}")], []
    problems = list(got.problems)
    if targets and got.unmatched:
        problems.append(skillkit.Problem(ALCOHOL_KEY, label, "format", "情景文件只接受平均每日纯酒精摄入量，不能改动年龄、性别、地区或年份。"))
    return got.values, problems, got.unmatched


def with_card(text):
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--region")
    parser.add_argument("--year", default="2020")
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--list-regions", action="store_true")
    args = parser.parse_args(argv)
    if args.list_regions:
        print("\n".join(f"{en}\t{zh}" for en, zh in REGION_ZH.items()))
        return 0
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "result.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems, unmatched = collect(args.measurements, manifest, "测量")
    scalars = {}
    for key in ("age", "year"):
        raw = getattr(args, key)
        if raw is None:
            problems.extend(skillkit.check_scalar(manifest, key, None))
            continue
        try:
            scalars[key] = skillkit.parse_number(raw)
            problems.extend(skillkit.check_scalar(manifest, key, scalars[key]))
        except ValueError:
            problems.append(skillkit.Problem(key, key, "number", f"{key} 需要有限数值。"))
    if "year" in scalars and scalars["year"] not in YEARS:
        problems.append(skillkit.Problem("year", "参考年份", "range", "只能使用 1990、2000、2010、2020 年的原表值；不插值。"))
    normalized = {}
    for key, function in [("region", normalize_region), ("sex", normalize_sex)]:
        raw = getattr(args, key)
        try:
            if raw is None:
                raise ValueError(f"缺少{key}，需提供论文对应的人群分层。")
            normalized[key] = function(raw)
        except ValueError as exc:
            problems.append(skillkit.Problem(key, key, "missing" if raw is None else "category", str(exc)))
    targets = {}
    if args.targets is not None:
        targets, target_problems, _ = collect(args.targets, manifest, "情景", targets=True)
        problems.extend(target_problems)
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        path.write_text(with_card(path.read_text()), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {o["key"]: None for o in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    row = lookup(normalized["region"], scalars["age"], normalized["sex"], scalars["year"])
    ethanol = values[ALCOHOL_KEY]
    result = calculate(ethanol, row)
    labels = {"above_printed_mean": "高于已发表均值", "below_printed_mean": "低于已发表均值",
              "equal_to_printed_mean": "等于已发表的四舍五入均值"}
    lines = [f"# {TITLE}", "", "## 你的输入", "",
             f"平均每日纯酒精摄入量：{ethanol:g} g/d，相当于本论文定义的 {result['standard_drinks_day']:g} 标准杯/日（每杯 10 g 纯乙醇）。",
             f"年龄：{scalars['age']:g} 岁；论文年龄档：{row['age_group']}；性别：{'男' if row['sex'] == 'male' else '女'}。",
             f"参照：{REGION_ZH[row['region']]}（{row['region']}），{row['year']} 年的历史人群模型。",
             "", "## 与已发表人群阈值比较", "",
             "| 阈值 | 均值（论文标准杯/日） | 95% 不确定区间 | 你的摄入量减去阈值（g/d） | 所在侧 |",
             "|---|---:|---:|---:|---|"]
    for prefix, title in [("tmrel", "TMREL：理论最低风险暴露水平"), ("nde", "NDE：非饮酒者等效水平")]:
        lines.append(f"| {title} | {result[prefix + '_standard_drinks_day']:g} | "
                     f"{result[prefix + '_ui_low']:g}–{result[prefix + '_ui_high']:g} | "
                     f"{result[prefix + '_gap_g_day']:+.6g} | {labels[result[prefix + '_side']]} |")
    lines += ["", "正差值表示高于原表均值，负差值表示低于；差值不是建议增减的饮酒量。",
              "TMREL 是模型中综合疾病负担最低处；NDE 是模型综合风险与不饮酒者相当处。"
              "高于 NDE 均值符合论文用于统计人群的超阈值定义；低于或等于它不能证明个人安全或有益。",
              "不确定区间描述人群阈值估计，并非个人风险区间。均值和区间按表格原样保留，不能用来断言个人风险有显著差异。",
              f"数值来源：附录 2 表 S1，第 {row['appendix_page']} 页（PDF 第 {row['pdf_page']} 页），2022 年 7 月 19 日更正版。",
              "本方法不计算个人疾病概率、寿命变化或饮酒带来的收益；不按杯子体积、饮料酒精度或不同国家的标准杯自动换算。"]
    if scalars["age"] >= 80:
        lines.append("80 岁及以上统一对应原表 80 plus 合并档，不提供更细的年龄阈值。")
    if unmatched:
        lines.append("未用于计算的测量项：" + "、".join(unmatched))
    if targets:
        scenario = calculate(targets[ALCOHOL_KEY], row)
        lines += ["", "## 你自填的比较情景", "",
                  f"情景摄入量 {targets[ALCOHOL_KEY]:g} g/d；相对 NDE 的差值为 {scenario['nde_gap_g_day']:+.6g} g/d。",
                  "此情景只改变算术差值，不表示风险改善，也不是系统建议的目标。"]
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text(with_card("\n".join(lines)), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(make_levers(ethanol, targets, row), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
