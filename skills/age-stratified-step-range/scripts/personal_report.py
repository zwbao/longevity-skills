"""Offline comparison against printed age-specific ranges; no risk equation."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, TITLE, LABELS, evaluate


def collect(path, manifest, target=False):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem("daily_steps", "日均步数", "file", f"无法读取步数表：{exc}")]
    problems = list(result.problems)
    if target:
        problems += [skillkit.Problem(name, name, "target", "目标表只接受日均步数，不能修改年龄或其他项目。")
                     for name in result.unmatched]
    return result.values, problems


def levers(age, steps, target=None):
    current = evaluate(age, steps)
    payload = {
        "schema": "longevity-levers/1", "model": "age_stratified_step_range",
        "model_zh": TITLE, "current": current,
        "sensitivity": [{"key": "daily_steps", "label_zh": "日均步数", "unit": "1",
                         "value": steps, "signed_gap_per_step": 1}],
        "levers": [],
        "note_zh": "年龄保持不变。敏感度仅表示日均步数每增加一步，与固定范围端点的有符号差增加一步；分档为阶梯函数，没有连续风险敏感度。目标由用户指定，不是处方或获益预测。",
    }
    if target is not None:
        moved = evaluate(age, target)
        payload["levers"] = [{"key": "daily_steps", "label_zh": "日均步数", "unit": "1",
                               "from": steps, "to": target, "daily_steps_delta": target - steps,
                               "from_position": current["step_position"], "to_position": moved["step_position"]}]
        payload["targets"] = {"values": {"daily_steps": target}, "outputs": moved,
                              "daily_steps_delta": target - steps}
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="实足年龄，岁")
    parser.add_argument("--sex", help="可选上下文，不参与年龄分组或步数范围计算")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "problems.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    try:
        age = float(args.age) if args.age is not None else None
    except ValueError:
        age = None
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "年龄不是一个可以计算的数，请用岁填写。"))
    if not any(p.key == "age" for p in problems):
        problems += skillkit.check_scalar(manifest, "age", age)
    wanted = {}
    if args.targets is not None:
        wanted, target_problems = collect(args.targets, manifest, target=True)
        problems += target_problems
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    steps = values["daily_steps"]
    result = evaluate(age, steps)
    target = wanted.get("daily_steps")
    scenario = levers(age, steps, target)
    low, high = result["reference_low_daily_steps"], result["reference_high_daily_steps"]
    group = "60 岁及以上" if result["age_group"] == "ge_60" else "18 岁至未满 60 岁"
    lines = [f"# {TITLE}", "", *paper_card_lines(), "",
             "仍在验证：论文印出了年龄对应的平台范围，但没有个人分档算例；本报告是范围比较。", "",
             "## 你的步数", "", f"- 实足年龄：{age:g} 岁；对应组别：{group}。",
             f"- 你提供的日均步数：{steps:g} 步/日。",
             f"- 论文所述约略平台范围：{low:g}–{high:g} 步/日。",
             f"- 位置：{LABELS[result['step_position']]}。",
             f"- 日均步数减范围下端：{result['difference_from_low_daily_steps']:+g} 步/日；减上端：{result['difference_from_high_daily_steps']:+g} 步/日。", "",
             "范围端点来自人群曲线的约略描述；这里把两个端点都归入范围内，仅为显示约定，不是达标线或危险线。年龄跨过分组边界时显示范围会改变，不代表健康状态突然改变。",
             "日均步数应是连续一周观察中有效佩戴日的总步数除以有效日数，不是某一次散步、周总步数或每分钟步频。缺失日不能当零；设备、佩戴位置和慢速行走会影响计数，不同设备结果可能不直接可比。",
             "该研究以高收入国家的志愿者为主，且多数为白人；不直接推广到儿童、急性病期或特殊康复人群。不能由此估算你的寿命、死亡概率、增加步数后的风险变化或最佳步频。"]
    if target is not None:
        lines += ["", "## 你指定的假设目标", "",
                  f"若日均步数为 {target:g} 步/日，与当前相差 {target - steps:+g} 步/日，位置为：{LABELS[scenario['targets']['outputs']['step_position']]}。",
                  "这只是同一年龄下的数值比较，不表示需要达到此目标或可获得多少健康收益。"]
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
