"""Offline lookup of the printed nonlinear predictions; standard library only."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, INPUT_KEY, OUTCOMES, REFERENCE_H, TABLE_2, TITLE


def lookup(hours):
    cells = TABLE_2[hours]
    result = {INPUT_KEY: hours, "reference_sleep_h": REFERENCE_H}
    for outcome, cell in zip(OUTCOMES, cells):
        for suffix, value in zip(("rr", "ci_lower", "ci_upper"), cell or (None, None, None)):
            result[f"{outcome}_{suffix}"] = value
    return result


def collect(path, manifest, label):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, label, "file", f"{label}文件无法读取：{exc}")]
    problems = list(data.problems)
    if data.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, label, "unknown", f"{label}含无法识别的项目：{'、'.join(data.unmatched)}。请核对项目名称。"))
    hours = data.values.get(INPUT_KEY)
    if hours is not None and hours not in TABLE_2:
        problems.append(skillkit.Problem(INPUT_KEY, label, "unsupported", f"{label}为 {hours:g} h。表 2 只印出 3 至 11 小时的整数点；没有这个输入对应的查表值。不四舍五入、不插值、不外推，请保留真实测量。"))
    if label == "目标睡眠时长":
        for problem in problems:
            problem.message_zh = "目标文件：" + problem.message_zh
    return data.values, problems


def rr_delta(current, other):
    return {
        f"{key}_rr": None if current[f"{key}_rr"] is None or other[f"{key}_rr"] is None
        else round(other[f"{key}_rr"] - current[f"{key}_rr"], 10)
        for key in OUTCOMES
    }


def levers(hours, target=None):
    current = lookup(hours)
    neighbors = []
    for other_h in (hours - 1, hours + 1):
        if other_h in TABLE_2:
            other = lookup(other_h)
            neighbors.append({INPUT_KEY: other_h, "outputs": other, "rr_delta": rr_delta(current, other)})
    result = {
        "schema": "longevity-levers/1",
        "model": "sleep-duration-risk-lookup",
        "model_zh": "表 2 整数睡眠时长的非线性关联查表",
        "current": current,
        "sensitivity": [{"key": INPUT_KEY, "unit": "h", "value": hours,
                         "method": "adjacent_printed_points", "neighbors": neighbors}],
        "levers": [],
        "note_zh": "敏感度仅列相邻已印出小时点的 RR 差；没有连续导数。目标比较是两个人群关联查表值之差，不是个人风险降低量或睡眠建议；未印出的值及其差均为空，不计算差值置信区间。",
    }
    if target is not None:
        other = lookup(target)
        delta = rr_delta(current, other)
        result["targets"] = {"values": {INPUT_KEY: target}, "outputs": other, "rr_delta": delta}
        result["levers"] = [{"key": INPUT_KEY, "label_zh": "通常的睡眠时长", "unit": "h",
                             "from": hours, "to": target, "outputs": other, "rr_delta": delta}]
    return result


def risk_table(result):
    lines = ["| 研究结局 | RR（相对每日 7 小时） | 研究人群的 95% 置信区间 |",
             "|---|---:|---|"]
    for key, label in OUTCOMES.items():
        rr, low, high = (result[f"{key}_{s}"] for s in ("rr", "ci_lower", "ci_upper"))
        value = "未报告" if rr is None else f"{rr:.2f}"
        ci = "未报告" if rr is None else "参照点，未印区间" if low is None else f"{low:.2f}–{high:.2f}"
        lines.append(f"| {label} | {value} | {ci} |")
    return lines


def render(result, target=None):
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的查表结果", "",
             f"你提供的通常睡眠时长为每日 {result[INPUT_KEY]:g} 小时。以下为正文表 2 对应小时点的结果。", "",
             *risk_table(result), "",
             "RR 是不同睡眠时长在研究人群中的相对风险；置信区间反映研究估计的不确定性，不是你的个人预测区间。参照值并不代表风险为零。", "",
             "研究汇总了夜间睡眠与全天睡眠的自报问卷或访谈，未按你的睡眠口径、年龄、性别或地区重新校准；手环测量也没有在此单独验证。单晚睡眠不能代表通常睡眠。", "",
             "研究人群：67 篇文章中一般健康成人的前瞻性队列（亚洲、欧洲、美国和澳大利亚），共约 358 万名参与者，随访 2.3–34 年；排除了糖尿病和规律透析人群。", "",
             "这张表面向一般健康人群的观察研究，不用于儿童或特定疾病人群的风险预测。总心血管疾病、冠心病和卒中汇总了发病与死亡结局，不能称为单独的发病风险。"]
    if target is not None:
        lines += ["", "## 你指定的目标情景", "", f"目标为每日 {target:g} 小时；仅比较表中对应点，不代表建议达到这个时长。", "",
                  *risk_table(lookup(target)), "", "目标与当前点的查表差异不代表改变睡眠后的因果效应。"]
    lines += ["", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age", help="可选年龄背景，不调整查表值")
    parser.add_argument("--sex", help="可选 male/female 背景，不调整查表值")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "result.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest, "睡眠时长")
    target = None
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, "目标睡眠时长")
        problems += target_problems
        target = targets.get(INPUT_KEY)
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems += skillkit.check_scalar(manifest, "age", age)
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值。"))
    if args.sex is not None and args.sex not in ("male", "female"):
        problems.append(skillkit.Problem("sex", "性别", "parse", "性别参数仅接受 male 或 female，也可以省略；此项不改变查表结果。"))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    hours = values[INPUT_KEY]
    result = lookup(hours)
    skillkit.write_result(args.out, manifest, result)
    (args.out / "report.md").write_text(render(result, target), encoding="utf-8")
    (args.out / "levers.json").write_text(json.dumps(levers(hours, target), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
