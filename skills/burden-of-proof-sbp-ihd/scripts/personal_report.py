"""Read published SBP–IHD RR values; standard-library-only offline runtime."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, DENSE_RANGE, INPUT_KEY, INPUT_UNIT, REFERENCE_SBP,
                     RR_KEYS, TABLE, TABLE_RANGE, TITLE)


def bracket(sbp: float):
    if not math.isfinite(sbp) or not TABLE_RANGE[0] <= sbp <= TABLE_RANGE[1]:
        raise ValueError("收缩压超出已发表查表范围，不外推。")
    for row in TABLE:
        if sbp == row[INPUT_KEY]:
            return row, row
    for lower, upper in zip(TABLE, TABLE[1:]):
        if lower[INPUT_KEY] < sbp < upper[INPUT_KEY]:
            return lower, upper
    raise ValueError("未找到对应的表格区间。")


def compute(sbp: float) -> dict:
    lower, upper = bracket(sbp)
    exact = lower is upper
    result = {INPUT_KEY: sbp, "reference_sbp_mmhg": REFERENCE_SBP,
              "bracket_lower_sbp_mmhg": lower[INPUT_KEY],
              "bracket_upper_sbp_mmhg": upper[INPUT_KEY],
              "readout_method": "table_lookup" if exact else "log_linear_interpolation",
              "evidence_region": "data_dense" if DENSE_RANGE[0] <= sbp <= DENSE_RANGE[1] else "data_sparse"}
    for key in RR_KEYS:
        if exact:
            result[key] = lower[key]
        else:
            fraction = (sbp - lower[INPUT_KEY]) / (upper[INPUT_KEY] - lower[INPUT_KEY])
            result[key] = math.exp(math.log(lower[key]) + fraction * math.log(upper[key] / lower[key]))
    return result


def levers(sbp: float, target: float | None) -> dict:
    current = compute(sbp)
    # Local derivatives of this explicit interpolation, not of the original
    # fitted spline. At knots average left/right derivatives; at ends one-sided.
    slopes = []
    for lower, upper in zip(TABLE, TABLE[1:]):
        if lower[INPUT_KEY] <= sbp <= upper[INPUT_KEY]:
            slopes.append(current["ihd_rr"] * math.log(upper["ihd_rr"] / lower["ihd_rr"])
                          / (upper[INPUT_KEY] - lower[INPUT_KEY]))
    result = {
        "schema": "longevity-levers/1", "model": "burden-of-proof-sbp-ihd",
        "model_zh": TITLE, "current": current,
        "sensitivity": [{"key": INPUT_KEY, "label_zh": "收缩压", "unit": INPUT_UNIT,
                         "value": sbp, "output_key": "ihd_rr", "per_unit": sum(slopes) / len(slopes),
                         "method": "interpolation_slope_mean_at_knots_one_sided_at_endpoints"}],
        "levers": [], "note_zh": BOUNDARY,
    }
    if target is not None:
        moved = compute(target)
        delta = moved["ihd_rr"] - current["ihd_rr"]
        ratio = moved["ihd_rr"] / current["ihd_rr"]
        result["targets"] = {"values": {INPUT_KEY: target}, **moved,
                             "ihd_rr_delta": delta, "rr_ratio_to_current": ratio}
        result["levers"] = [{"key": INPUT_KEY, "label_zh": "收缩压", "unit": INPUT_UNIT,
                             "from": sbp, "to": target, "ihd_rr_delta": delta,
                             "rr_ratio_to_current": ratio}]
    return result


def collect(path: Path | None, manifest: dict, label: str):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, "收缩压", "file",
                                    f"{label}无法读取：{exc}。请提供 marker,value,unit 的 CSV 或 TSV。")]
    problems = list(result.problems)
    if label == "目标表" and result.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, "收缩压", "unknown_target",
                                         "目标表含未识别项目：" + "、".join(result.unmatched)))
    value = result.values.get(INPUT_KEY)
    if value is not None and not TABLE_RANGE[0] <= value <= TABLE_RANGE[1]:
        problems.append(skillkit.Problem(INPUT_KEY, "收缩压", "model_range",
                                         f"{label}的收缩压为 {value:g} mmHg；论文查表范围仅为 "
                                         f"{TABLE_RANGE[0]}–{TABLE_RANGE[1]} mmHg，不外推。"
                                         "若测量无误，本方法不适用；不要为了运行修改读数。"))
    return result.values, problems


def readout_lines(result: dict) -> list[str]:
    exact = result["readout_method"] == "table_lookup"
    method = "补充表 4 原值" if exact else "相邻表格节点的对数线性插值近似（并非原论文样条模型的精确输出）"
    text = [f"收缩压：{result[INPUT_KEY]:g} mmHg；参照：{REFERENCE_SBP} mmHg。",
            f"读取方式：{method}。",
            f"对应的人群平均相对风险 RR：{result['ihd_rr']:.2f}；"
            f"95% 不确定区间：{result['ihd_rr_ui_lower']:.2f}–{result['ihd_rr_ui_upper']:.2f}。",
            "该区间包含研究间异质性，不是你的个人预测区间；RR 也不是百分比发病率。"]
    if not exact:
        text.append(f"插值使用的收缩压节点为 {result['bracket_lower_sbp_mmhg']:g} 和 "
                    f"{result['bracket_upper_sbp_mmhg']:g} mmHg；区间端点也分别作插值近似。")
    if result["evidence_region"] == "data_sparse":
        text.append(f"这个读数位于证据较稀疏的区段；论文数据较密集的区间为 {DENSE_RANGE[0]}–{DENSE_RANGE[1]} mmHg。")
    if result[INPUT_KEY] == REFERENCE_SBP:
        text.append("参照点的 RR 和区间按模型归一化为 1；这不表示没有患病风险或测量误差。")
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="收缩压 CSV/TSV，marker,value,unit")
    parser.add_argument("--targets", type=Path, help="用户自行提供的目标收缩压，列格式同测量表")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "levers.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest, "测量表")
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, "目标表")
        for problem in target_problems:
            problem.message_zh = "目标表：" + problem.message_zh
        problems.extend(target_problems)
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        rows = report.read_text(encoding="utf-8").replace("边界: ", "边界：").splitlines()
        report.write_text("\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n", encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    sbp = values[INPUT_KEY]
    result = compute(sbp)
    lever = levers(sbp, targets.get(INPUT_KEY))
    rows = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的查算结果", "",
            *readout_lines(result), "",
            "曲线来自已发表前瞻性队列研究与降压随机对照试验的荟萃分析（66 个国家、1,486,007 名参与者、"
            "12,628 例缺血性心脏病事件）；它是人群平均关系，只在这些研究人群中拟合。",
            "这条曲线合并不同研究人群，没有按你的年龄、性别、既往病史或用药校准。",
            "100 mmHg 是论文的数学参照，不是为你设定的治疗目标；研究的五星评级描述整条证据关系，不是个人风险分级。"]
    if "targets" in lever:
        moved = lever["targets"]
        rows += ["", "## 你提供的目标值对比", "", *readout_lines(moved),
                 f"模型 RR 差：{moved['ihd_rr_delta']:+.3f}；目标与当前的 RR 比：{moved['rr_ratio_to_current']:.3f}。",
                 "目标由你提供；这些差和比只描述曲线读数，不代表个人降压治疗的获益，也没有治疗效应置信区间。"]
    rows += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(lever, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
