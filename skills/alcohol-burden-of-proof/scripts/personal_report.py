"""Offline, literal Table 3 lookup; no interpolation or individualized risk model."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import ALCOHOL_INPUT, GRID, MAX_EXPOSURE, MIN_EXPOSURE, OUTCOMES, REFERENCE_RR, TABLE

TITLE = "饮酒量与健康结局：论文查表报告"
BOUNDARY = (
    "本报告按你提供的饮酒量查阅人群观察性研究的关联，不是个人患病概率、因果效应或安全饮酒阈值；"
    "不能据此开始饮酒、增加饮酒或开始、停用任何药物，不提供饮酒量或药物剂量建议。"
)
SCENARIO_NOTE = (
    "情景由用户指定；表格数值之差只描述两个摄入量节点的关联差异，不能预测个人改变饮酒后的获益。"
    "不合并各疾病的风险，不寻找最优饮酒量。"
)


def lookup(amount: float) -> dict:
    if not math.isfinite(amount) or not MIN_EXPOSURE <= amount <= MAX_EXPOSURE:
        raise ValueError("摄入量超出本查表范围")
    lower = max(g for g in GRID if g <= amount)
    upper = min(g for g in GRID if g >= amount)
    result = {
        "alcohol_g_day": amount,
        "lower_exposure_g_day": lower,
        "upper_exposure_g_day": upper,
        "lookup_mode": "reference" if amount == 0 else "exact" if lower == upper else "bracket",
    }
    for key, _ in OUTCOMES:
        for side, g in (("lower", lower), ("upper", upper)):
            values = (REFERENCE_RR, None, None) if g == 0 else TABLE[(key, g)]
            for part, value in zip(("rr", "ui_low", "ui_high"), values):
                result[f"{key}_{side}_{part}"] = value
    return result


def rr_delta(current: dict, other: dict):
    # Off-grid inputs have no printed point prediction; never invent a delta.
    if "bracket" in (current["lookup_mode"], other["lookup_mode"]):
        return None
    return {key: other[f"{key}_lower_rr"] - current[f"{key}_lower_rr"] for key, _ in OUTCOMES}


def make_levers(amount: float, target: float | None) -> dict:
    current = lookup(amount)
    neighbors = []
    # Finite table contrasts, not derivatives of a fitted curve.
    before = [g for g in GRID if g < amount]
    after = [g for g in GRID if g > amount]
    for g in ([max(before)] if before else []) + ([min(after)] if after else []):
        result = lookup(g)
        neighbors.append({"alcohol_g_day": g, "result": result, "rr_delta": rr_delta(current, result)})
    payload = {
        "schema": "longevity-levers/1", "model": "alcohol-burden-of-proof",
        "model_zh": "酒精 Burden of Proof 表 3 查表",
        "current": current,
        "sensitivity": [{"key": ALCOHOL_INPUT[0], "label_zh": ALCOHOL_INPUT[1],
            "unit": ALCOHOL_INPUT[2], "value": amount, "derivative": None,
            "method": "adjacent_printed_nodes", "neighbors": neighbors,
            "note_zh": "论文查表未实现连续曲线，导数不可得；只列邻近节点，不能当作风险界限。"}],
        "levers": [], "note_zh": SCENARIO_NOTE,
    }
    if target is not None:
        other = lookup(target)
        payload["targets"] = other
        payload["levers"].append({"key": ALCOHOL_INPUT[0], "label_zh": ALCOHOL_INPUT[1],
            "unit": ALCOHOL_INPUT[2], "from": amount, "to": target,
            "result": other, "rr_delta": rr_delta(current, other)})
    return payload


def table_lines(result: dict) -> list[str]:
    low, high = result["lower_exposure_g_day"], result["upper_exposure_g_day"]
    sides = [("lower", low)] if low == high else [("lower", low), ("upper", high)]
    lines = []
    if low != high:
        lines += ["该输入不在论文印出的节点上。下列仅是相邻摄入量节点的查表值，"
                  "不是该摄入量风险的上下限，也没有计算中间点的风险。", ""]
    for side, g in sides:
        lines += [f"### 摄入量节点：{g:g} g/d", ""]
        if g == 0:
            lines += ["这是论文的无饮酒参照，RR 按定义为 1，不表示疾病风险为零；"
                      "表 3 未印此节点的不确定性区间，留空。", ""]
        lines += ["| 健康结局 | 平均相对风险 RR | 95% 不确定性区间 |",
                  "| --- | ---: | --- |"]
        for key, label in OUTCOMES:
            rr = result[f"{key}_{side}_rr"]
            lo, hi = result[f"{key}_{side}_ui_low"], result[f"{key}_{side}_ui_high"]
            interval = "未提供（参照）" if lo is None else f"{lo:g}–{hi:g}"
            lines.append(f"| {label} | {rr:g} | {interval} |")
        lines.append("")
    return lines


def collect(path: Path | None, manifest: dict, prefix: str):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        return None, [skillkit.Problem(ALCOHOL_INPUT[0], ALCOHOL_INPUT[1], "file",
            f"{prefix}文件无法读取，请提供 marker,value,unit 三列的 CSV：{exc}")]
    problems = list(collected.problems)
    if collected.unmatched:
        problems.append(skillkit.Problem(ALCOHOL_INPUT[0], ALCOHOL_INPUT[1], "unknown",
            f"{prefix}包含无法识别的项目：{'、'.join(collected.unmatched)}。请确认是纯酒精的每日平均克数。"))
    if prefix == "目标":
        problems = [skillkit.Problem(p.key, p.label, p.kind, "目标：" + p.message_zh) for p in problems]
    return collected.values.get(ALCOHOL_INPUT[0]), problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    amount, problems = collect(args.measurements, manifest, "测量")
    target = None
    if args.targets is not None:
        target, target_problems = collect(args.targets, manifest, "目标")
        problems += target_problems
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding="utf-8").split("\n", 1)[1]
        report.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {item["key"]: None for item in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    result = lookup(amount)
    skillkit.write_result(args.out, manifest, result)
    levers = make_levers(amount, target)
    (args.out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的输入", "",
        f"每日平均纯酒精摄入量：{amount:g} g/d。这里不是饮料体积，也不是单次饮酒量。", "",
        "## 按摄入量查阅论文", "",
        "以下是相对于无饮酒的人群平均 RR，95% 不确定性区间已计入研究间异质性。"
        "RR 大于 1 表示表中关联较高，小于 1 表示关联较低；区间跨过或接触 1 时，不排除无差异。"
        "印出的数值经过取整，区间看似 1–1 也不等于精确确定。", "",
        "适用人群：表中数值来自截至 2023 年发表、覆盖多个国家和地区的 843 项队列及病例对照研究的荟萃分析，"
        "反映这些研究人群中当前饮酒与不饮酒相比的平均关联，未在你所属的具体人群中单独验证。", "",
        "乳腺癌条目来自女性研究，前列腺癌条目来自男性研究；全表展示不表示每个结局均适用于你。"
        "表中没有可用于个人年龄、性别、既往饮酒、饮酒年限或暴饮模式的校正系数。", "",
        *table_lines(result)]
    if target is not None:
        lines += ["## 你指定的情景", "", f"情景输入：{target:g} g/d。", "", SCENARIO_NOTE, "",
                  *table_lines(levers["targets"])]
    lines += [f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
