"""Offline cigarette-smoking stratum lookup; no individual survival model."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, CAUSES, CAUSE_LABELS, ETABLE1, LABELS, PARTS,
                     TABLE2, TARGET_NOTE)

TITLE = "卷烟吸烟分档与队列死亡 HR"
STATUS = {"never": "never", "从未吸烟": "never", "past": "past", "既往吸烟": "past",
          "已戒烟": "past", "current": "current", "目前吸烟": "current", "现在吸烟": "current"}


def category(status, count):
    if status != "current":
        return status
    if count <= 14:
        return "current_1_14"
    if count <= 24:
        return "current_15_24"
    return "current_25_plus"


def lookup(group):
    result = {"smoking_category": group}
    for prefix, table in (("", TABLE2), ("before75_", ETABLE1)):
        for cause, row in zip(CAUSES, table[group]):
            for part, value in zip(PARTS, row):
                result[f"{prefix}{cause}_{part}"] = value
    return result


def problem(key, message):
    return skillkit.Problem(key, key, "invalid", message)


def collect(path, manifest):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        return skillkit.Collected(problems=[problem("measurements", f"无法读取输入表：{exc}")])
    for name in data.unmatched:
        data.problems.append(problem(name, f"无法识别项目「{name}」；只接受每日卷烟支数。"))
    count = data.values.get("cigarettes_per_day")
    if count is not None and not count.is_integer():
        data.problems.append(problem("cigarettes_per_day", "本文只印出整支分档；请核实每日卷烟整数支数，不能自行四舍五入或将偶尔吸烟归入从未吸烟。"))
    return data


def table_lines(group, table):
    result = ["| 结局 | 该组 HR | 95% 置信区间 |", "|---|---:|---|"]
    for label, (hr, low, high) in zip(CAUSE_LABELS, table[group]):
        ci = "参照组，原表未给出" if low is None else f"{low:.2f}–{high:.2f}"
        result.append(f"| {label} | {hr:.2f} | {ci} |")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--smoking-status", help="never / past / current；也接受从未吸烟 / 已戒烟 / 目前吸烟")
    parser.add_argument("--age", help="可选年龄，仅作上下文，不改动表中 HR")
    parser.add_argument("--sex", help="可选 female/male/女/男，仅作上下文")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    data = collect(args.measurements, manifest)
    problems = list(data.problems)
    status = STATUS.get((args.smoking_status or "").strip().lower())
    count = data.values.get("cigarettes_per_day")
    if status is None:
        problems.append(problem("smoking_status", "缺少或无法识别吸烟史；请填写 never（从未吸烟）、past（既往吸烟）或 current（目前吸烟）。零支不能区分前两者。"))
    elif status == "current" and count is None:
        problems.append(problem("cigarettes_per_day", "目前吸烟者需要填写每日卷烟支数。"))
    elif status == "current" and count == 0:
        problems.append(problem("cigarettes_per_day", "目前吸烟却填写零支，请核实吸烟史；偶尔吸烟不在本文可直接映射的每日整支分档内。"))
    elif status in ("never", "past") and count not in (None, 0):
        problems.append(problem("cigarettes_per_day", "从未吸烟或已戒烟者的当前每日支数应为零；过去的支数不能填作当前支数。"))
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(problem("age", "年龄必须为有限数值。"))
    if args.sex is not None and args.sex.lower() not in ("female", "male", "女", "男"):
        problems.append(problem("sex", "性别仅接受 female/male/女/男；本表未提供性别单独系数。"))
    targets = None
    if args.targets is not None:
        target_data = collect(args.targets, manifest)
        problems.extend(target_data.problems)
        targets = target_data.values.get("cigarettes_per_day")
        if targets is None:
            problems.append(problem("targets", "目标表需要每日卷烟支数。"))
        if status != "current":
            problems.append(problem("targets", "目标比较仅支持目前吸烟者；吸烟史不能作为可逆数值调整。"))
    header = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join(header) + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    group = category(status, count)
    result = lookup(group)
    lines = header + ["## 你的吸烟分档", "", LABELS[group] + "。",
        "仅适用于卷烟；电子烟、雪茄、烟斗、包年或终生总支数不能代入。", "",
        "## 对应队列结果（正文 Table 2）", "",
        "以下是该组相对从未吸烟组的调整后 HR，不是你的个人预测。", "", *table_lines(group, TABLE2), "",
        "## 75 岁之前随访的敏感性分析（补充 eTable 1）", "",
        "这是同一研究限制观察到 75 岁之前的另一套结果，并非给你的年龄单独校准的风险。", "",
        *table_lines(group, ETABLE1), "",
        "参照组 HR=1 是比较基准，不代表零风险；置信区间反映组间关联估计的不确定性。",
        "研究对象主要为美国白人医护人员；对其他人群的适用性有限。年龄、性别和其他体检信息不改变此合并表的数值。",
        "本次不生成饮食分位数、五因素总分或预期寿命。", ""]
    levers = {"schema": "longevity-levers/1", "model": manifest["name"],
              "model_zh": TITLE, "current": result, "sensitivity": [], "levers": [],
              "note_zh": TARGET_NOTE + " 分档查表不提供连续导数；sensitivity 为空，不能解释为无关联。"}
    if targets is not None:
        target_group = "past" if targets == 0 else category("current", targets)
        wanted = lookup(target_group)
        deltas = {f"{cause}_hr_delta": wanted[f"{cause}_hr"] - result[f"{cause}_hr"] for cause in CAUSES}
        levers["targets"] = {**wanted, **deltas, "values": {"cigarettes_per_day": targets}}
        levers["levers"] = [{"key": "cigarettes_per_day", "label_zh": "每日卷烟支数", "unit": "1",
                              "from": count, "to": targets, **deltas}]
        lines += ["## 目标对应的另一组（非干预效果）", "", TARGET_NOTE, "",
                  f"目标每日 {targets:g} 支，对应：{LABELS[target_group]}。", "",
                  *table_lines(target_group, TABLE2), ""]
    lines += [f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
