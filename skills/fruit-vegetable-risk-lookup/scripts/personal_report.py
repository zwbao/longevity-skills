"""Offline exact/bracketing lookup; never reconstruct the unpublished splines."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, ENDPOINTS, FOODS, INPUT_KEY, MODEL_NOTE, OUTCOMES, series)

TITLE = "果蔬摄入量与人群相对风险查表"


def lookup(food, outcome, endpoint, intake):
    meta, points = series(food, outcome, endpoint)
    result = dict(meta, intake_g_d=intake, status="not_published", rr=None,
                  ci_low=None, ci_high=None, lower=None, upper=None)
    if not points:
        return result
    for point in points:
        if intake == point[INPUT_KEY]:
            return dict(result, **point, status="exact")
    if intake < points[0][INPUT_KEY] or intake > points[-1][INPUT_KEY]:
        return dict(result, status="outside_table", table_min_g_d=points[0][INPUT_KEY],
                    table_max_g_d=points[-1][INPUT_KEY])
    lower = max((p for p in points if p[INPUT_KEY] < intake), key=lambda p: p[INPUT_KEY])
    upper = min((p for p in points if p[INPUT_KEY] > intake), key=lambda p: p[INPUT_KEY])
    return dict(result, status="bracket", lower=lower, upper=upper)


def output_values(result):
    values = {k: result[k] for k in ("food_group", "outcome", "endpoint", "intake_g_d", "status", "reference_g_d", "rr", "ci_low", "ci_high", "table", "pdf_page")}
    for side in ("lower", "upper"):
        for field in ("intake_g_d", "rr", "ci_low", "ci_high"):
            values[f"{side}_{field}"] = (result[side] or {}).get(field)
    for field in ("table_min_g_d", "table_max_g_d"):
        values[field] = result.get(field)
    return values


def levers(current, target=None):
    food, outcome, endpoint = (current[k] for k in ("food_group", "outcome", "endpoint"))
    _, points = series(food, outcome, endpoint)
    value = current[INPUT_KEY]
    sensitivity = {"key": INPUT_KEY, "label_zh": "日均摄入量", "unit": "g/d", "value": value,
                   "rr_per_g_d": None, "method": "adjacent_printed_rows_secant"}
    # A descriptive finite difference of printed rows, not a spline derivative.
    if current["status"] in ("exact", "bracket") and len(points) > 1:
        if current["status"] == "bracket":
            low, high = current["lower"], current["upper"]
        else:
            index = next(i for i, p in enumerate(points) if p[INPUT_KEY] == value)
            low, high = points[max(0, index - 1)], points[min(len(points) - 1, index + 1)]
        sensitivity.update(lower=low, upper=high,
                           rr_per_g_d=(high["rr"] - low["rr"]) / (high[INPUT_KEY] - low[INPUT_KEY]))
    payload = {"schema": "longevity-levers/1", "model": "fruit_vegetable_risk_lookup",
               "model_zh": TITLE, "current": current, "sensitivity": [sensitivity], "levers": [], "note_zh": MODEL_NOTE}
    if target is not None:
        wanted = lookup(food, outcome, endpoint, target)
        delta = wanted["rr"] - current["rr"] if wanted["rr"] is not None and current["rr"] is not None else None
        payload["targets"] = dict(wanted, values={INPUT_KEY: target}, rr_delta=delta)
        payload["levers"] = [{"key": INPUT_KEY, "label_zh": "日均摄入量", "unit": "g/d",
                              "from": value, "to": target, "rr_delta": delta}]
    return payload


def rr_text(point):
    if point["ci_low"] is None:
        return f"{point['rr']:.2f}（参照行，未印置信区间）"
    return f"{point['rr']:.2f}（95% CI：{point['ci_low']:.2f}–{point['ci_high']:.2f}）"


def result_lines(result):
    lines = [f"摄入量：{result['intake_g_d']:g} g/d。来源：补充表 {result['table']}，PDF 第 {result['pdf_page']} 页。"]
    if result["reference_g_d"] is not None:
        lines += [f"该列参照摄入量：{result['reference_g_d']:g} g/d，RR=1；参照量不代表推荐量。"]
    if result["status"] == "exact":
        lines += [f"对应印出行的相对风险 RR：{rr_text(result)}。"]
    elif result["status"] == "bracket":
        lines += ["这个摄入量没有单独印出数值；以下是相邻表格行，不是本人的风险估计或上下界："]
        for side in ("lower", "upper"):
            p = result[side]
            lines += [f"- {p['intake_g_d']:g} g/d：RR {rr_text(p)}。"]
    elif result["status"] == "outside_table":
        lines += [f"摄入量超出该列已印范围 {result['table_min_g_d']:g}–{result['table_max_g_d']:g} g/d，本次不估计 RR。"]
    else:
        lines += ["该列没有印出非线性风险估计，本次没有 RR。不能把空白解释为没有关联。"]
    return lines


def read_input(path, manifest, purpose):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        return None, [skillkit.Problem(INPUT_KEY, "日均摄入量", "file", f"{purpose}文件无法读取：{exc}")]
    problems = collected.problems[:]
    if collected.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, "日均摄入量", "unknown", f"{purpose}包含无法识别的项目：{'、'.join(str(x) for x in collected.unmatched)}；请使用 intake_g_d。"))
    return collected.values.get(INPUT_KEY), problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--food-group", default="combined")
    parser.add_argument("--outcome", default="all_cause_mortality")
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    intake, problems = read_input(args.measurements, manifest, "当前摄入量")
    target = None
    if args.targets is not None:
        target, bad = read_input(args.targets, manifest, "目标摄入量")
        problems.extend(bad)
    endpoint = args.endpoint or ("mortality" if args.outcome == "all_cause_mortality" else "mixed")
    if args.food_group not in FOODS or args.outcome not in OUTCOMES or endpoint not in ENDPOINTS:
        problems.append(skillkit.Problem("selection", "查表选择", "choice", "食物组、结局或分析类型不支持；见 SKILL.md 中的选项。"))
    else:
        try:
            series(args.food_group, args.outcome, endpoint)
        except ValueError as exc:
            problems.append(skillkit.Problem("endpoint", "分析类型", "choice", str(exc)))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    current = lookup(args.food_group, args.outcome, endpoint, intake)
    scenario = levers(current, target)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 本次查表", "",
             f"食物组：{FOODS[args.food_group]}；结局：{OUTCOMES[args.outcome]}；分析：{ENDPOINTS[endpoint]}。", "",
             *result_lines(current), "", "RR 是不同摄入量人群的相对比较，95% CI 表示研究估计的不确定性，不是个人概率范围。"]
    if target is not None:
        lines += ["", "## 自设目标的表格对比", "", *result_lines(scenario["targets"])]
        delta = scenario["targets"]["rr_delta"]
        lines += [f"目标行 RR 减当前行 RR：{delta:+.2f}。这个差不是绝对风险下降或治疗效果。" if delta is not None else "当前值或目标值没有对应印出行，因此不计算 RR 差。"]
    lines += ["", MODEL_NOTE, "", "未按年龄、性别或既往病史校准；研究以成人队列为主。食物定义和测量方式在各队列间不同，重量状态不明确时应先核实饮食记录。", "", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n\n".join(line for line in lines if line) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, output_values(current))
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
