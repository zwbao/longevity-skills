"""Arithmetic comparison to Stanaway et al. 2022's published TMREL endpoints."""
import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, FOOD_DEFINITION, POPULATION, INTAKE_KEY, OBSERVED_MAX_G_D,
                     TMREL_LOWER_G_D, TMREL_UPPER_G_D, UNIT)


def calculate(x):
    lower, upper = TMREL_LOWER_G_D - x, TMREL_UPPER_G_D - x
    return {
        "vegetables_g_d": x,
        "tmrel_lower_g_d": TMREL_LOWER_G_D,
        "tmrel_upper_g_d": TMREL_UPPER_G_D,
        "lower_difference_g_d": lower,
        "upper_difference_g_d": upper,
        "shortfall_g_d": max(0.0, lower),
        "position": "below" if lower > 0 else "above" if upper < 0 else "within",
    }


def levers(x, target=None):
    current = calculate(x)
    out = {
        "schema": "longevity-levers/1", "model": "vegetable_tmrel_gap",
        "model_zh": "蔬菜摄入与论文参考范围的差距", "current": current,
        "sensitivity": [{"key": INTAKE_KEY, "label_zh": "蔬菜日均摄入量", "unit": UNIT,
                         "value": x, "output": "lower_difference_g_d", "per_unit": -1.0}],
        "levers": [],
        "note_zh": "敏感度表示摄入量每变动一克，下端点减摄入量的差值变动多少克；仅为算术情景，不是健康获益估计或饮食处方。",
    }
    if target is not None:
        moved = calculate(target)
        changes = {f"{key}_delta": moved[key] - current[key] for key in
                   ("lower_difference_g_d", "upper_difference_g_d", "shortfall_g_d")}
        out["levers"] = [{"key": INTAKE_KEY, "label_zh": "蔬菜日均摄入量", "unit": UNIT,
                          "from": x, "to": target, **changes}]
        out["targets"] = {"values": {INTAKE_KEY: target}, **moved, **changes}
    return out


def read_input(path, manifest, target=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, csv.Error) as exc:
        return {}, [skillkit.Problem(INTAKE_KEY, "蔬菜日均摄入量", "file", f"无法读取摄入表：{exc}")]
    problems = collected.problems
    # Unknown target names must never silently become a no-op.
    if target and collected.unmatched:
        problems.append(skillkit.Problem(INTAKE_KEY, "目标摄入量", "unknown", "目标表存在无法识别的指标：" + "、".join(collected.unmatched)))
    return collected.values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age", help="可选上下文；不进入计算")
    parser.add_argument("--sex", help="可选上下文；不进入计算")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Avoid exposing previous successful outputs after a failed rerun.
    for filename in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)
    values, problems = read_input(args.intake, manifest)
    targets = {}
    if args.targets is not None:
        targets, target_problems = read_input(args.targets, manifest, target=True)
        for problem in target_problems:
            problem.message_zh = "目标表：" + problem.message_zh
        problems += target_problems
    title = "蔬菜摄入参考范围差距"
    card = [f"# {title}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, title, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(card) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    x = values[INTAKE_KEY]
    result = calculate(x)
    scenarios = levers(x, targets.get(INTAKE_KEY))
    lower, upper = TMREL_LOWER_G_D, TMREL_UPPER_G_D
    label = {"below": "低于", "within": "位于", "above": "高于"}[result["position"]]
    body = ["## 你的摄入记录", "", f"你记录的日均蔬菜摄入量为 {x:g} 克/日，{label}论文的 {lower:g}–{upper:g} 克/日参考范围。", "",
            f"下端点减摄入量：{result['lower_difference_g_d']:g} 克/日；上端点减摄入量：{result['upper_difference_g_d']:g} 克/日。正数表示低于相应端点，负数表示高于相应端点。", ""]
    if result["shortfall_g_d"] > 0:
        body += [f"与范围下端点的距离为 {result['shortfall_g_d']:g} 克/日。这是记录比较值。", ""]
    body += ["参考范围来自纳入研究中的高摄入暴露分布；它不是个人最优摄入量，也不是安全上限。高于上端点不等于有害，不代表需要减少摄入。", "", POPULATION, "", FOOD_DEFINITION, "",
             "请确认输入是完整记录期间的日均量，记录中的零摄入日也纳入平均；缺失的天不能当作零。论文没有提供统一的生熟重量或干鲜重量换算系数，这里不做这些换算，也不把碗、杯或未称量的份数转换成克。", "",
             "验证状态：仍在验证。论文公布了参考范围，但没有个人摄入差距的独立算例；本报告未复现原研究的风险模型或参考范围估计过程。", ""]
    if x > OBSERVED_MAX_G_D or targets.get(INTAKE_KEY, 0) > OBSERVED_MAX_G_D:
        body += [f"当前记录或情景值超过论文描述的最高观测摄入量 {OBSERVED_MAX_G_D:g} 克/日；只保留算术比较，不延伸解释健康效应。", ""]
    if targets:
        t = scenarios["targets"]
        body += ["## 你提供的摄入情景", "", f"如果日均摄入量为 {targets[INTAKE_KEY]:g} 克/日，下端点差值为 {t['lower_difference_g_d']:g} 克/日，上端点差值为 {t['upper_difference_g_d']:g} 克/日。该情景由你提供，仅重算差距。", ""]
    body += [f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(card + body), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
