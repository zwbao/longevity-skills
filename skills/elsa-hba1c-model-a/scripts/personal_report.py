"""Standalone standard-library implementation of the printed final Model A."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, DCCT_FACTOR, DCCT_OFFSET, DCCT_DIABETES,
                     IFCC_DIABETES, IFCC_MINIMUM, INTERCEPT, MODEL,
                     TARGET_NOTE, TITLE, TYPICAL_INTERVALS)


def to_ifcc(percent):
    return (percent - DCCT_OFFSET) * DCCT_FACTOR


def estimate(values):
    transformed = {"hba1c_ifcc": to_ifcc(values["hba1c_pct"]),
                   "age": values["age"], "female": values["sex"],
                   "log_years_next": math.log(values["years_next"])}
    eta = INTERCEPT + sum(beta * (transformed[key] - mean) / sd
                          for key, (mean, sd, beta) in MODEL.items())
    probability = 1 / (1 + math.exp(-eta)) if eta >= 0 else math.exp(eta) / (1 + math.exp(eta))
    return {"diabetes_probability_pct": 100 * probability, "linear_predictor": eta}


def problem(key, message, kind="scope"):
    return skillkit.Problem(key, key, kind, message)


def hba1c_scope(values):
    if "hba1c_pct" not in values:
        return []
    h = values["hba1c_pct"]
    if to_ifcc(h) < IFCC_MINIMUM:
        return [problem("hba1c_pct", "HbA1c 换算后低于论文的测量合理性下限，不能计算。")]
    if h >= DCCT_DIABETES or to_ifcc(h) >= IFCC_DIABETES:
        return [problem("hba1c_pct", "HbA1c 达到论文的基线排除阈值；该模型不适用于这一输入。这不是临床诊断。")]
    return []


def read_scalar(manifest, key, raw, problems):
    if raw is None:
        problems.extend(skillkit.check_scalar(manifest, key, None))
        return None
    try:
        value = skillkit.parse_number(raw)
    except ValueError:
        problems.append(problem(key, f"{key} 必须是有限数值。", "parse"))
        return None
    errors = skillkit.check_scalar(manifest, key, value)
    problems.extend(errors)
    return None if errors else value


def collect(path, manifest):
    try:
        return skillkit.collect_file(Path(path) if path else None, manifest)
    except (OSError, ValueError) as exc:
        return skillkit.Collected(problems=[problem("measurements", f"无法读取测量文件：{exc}", "file")])


def levers(values, targets):
    current = estimate(values)
    p = current["diabetes_probability_pct"] / 100
    common = 100 * p * (1 - p)
    derivatives = {"hba1c_pct": MODEL["hba1c_ifcc"][2] / MODEL["hba1c_ifcc"][1] * DCCT_FACTOR,
                   "age": MODEL["age"][2] / MODEL["age"][1],
                   "years_next": MODEL["log_years_next"][2] / MODEL["log_years_next"][1] / values["years_next"]}
    sensitivity = [{"key": k, "value": values[k], "unit": "%" if k == "hba1c_pct" else "a",
                    "probability_pct_per_unit": common * derivative,
                    "modifiable": k == "hba1c_pct"} for k, derivative in derivatives.items()]
    female = estimate({**values, "sex": 1})["diabetes_probability_pct"]
    male = estimate({**values, "sex": 0})["diabetes_probability_pct"]
    sensitivity.append({"key": "sex", "value": values["sex"], "unit": "1", "modifiable": False,
                        "female_minus_male_probability_pct": female - male,
                        "note_zh": "二元编码的模型差值，不是可干预目标。"})
    payload = {"schema": "longevity-levers/1", "model": "elsa-hba1c-model-a",
               "model_zh": TITLE, "current": current, "sensitivity": sensitivity,
               "levers": [], "note_zh": TARGET_NOTE,
               "fixed": {k: values[k] for k in ("age", "sex", "years_next")}}
    if targets:
        moved = estimate({**values, **targets})
        payload["targets"] = moved
        payload["levers"] = [{"key": "hba1c_pct", "unit": "%", "from": values["hba1c_pct"],
                              "to": targets["hba1c_pct"], **moved,
                              "diabetes_probability_pct_delta": moved["diabetes_probability_pct"] - current["diabetes_probability_pct"]}]
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    for flag in ("measurements", "age", "sex", "years-next", "eligible-baseline", "targets"):
        parser.add_argument("--" + flag)
    parser.add_argument("--out", default="out", type=Path)
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Reused output folders must not expose stale successes after failed input.
    for filename in ("report.md", "problems.json", "result.json", "levers.json"):
        (args.out / filename).unlink(missing_ok=True)
    collected = collect(args.measurements, manifest)
    problems = list(collected.problems)
    values = dict(collected.values)
    for key in ("age", "years_next", "eligible_baseline"):
        value = read_scalar(manifest, key, getattr(args, key), problems)
        if value is not None:
            values[key] = value
    sex_codes = {"female": 1, "f": 1, "女": 1, "1": 1,
                 "male": 0, "m": 0, "男": 0, "0": 0}
    sex = sex_codes.get((args.sex or "").strip().lower())
    if sex is None:
        problems.append(problem("sex", "请明确提供模型性别编码：female/女/1 或 male/男/0。", "missing" if args.sex is None else "parse"))
    else:
        problems.extend(skillkit.check_scalar(manifest, "sex", sex))
        values["sex"] = sex
    if "eligible_baseline" in values and values["eligible_baseline"] != 1:
        problems.append(problem("eligible_baseline", "须确认此前及当前无论文定义的糖尿病，且至少三个月前有一项无糖尿病时的 HbA1c 测量；未知或不符合时不计算。"))
    problems.extend(hba1c_scope(values))
    targets = {}
    if args.targets:
        target_manifest = {**manifest, "inputs": [dict(s, required=False) for s in manifest["inputs"]]}
        target_data = collect(args.targets, target_manifest)
        problems.extend(target_data.problems)
        targets = target_data.values
        if target_data.unmatched or not targets:
            problems.append(problem("targets", "目标文件必须包含 HbA1c；只接受 HbA1c 目标，不接受年龄、性别、随访间隔或未知项目。", "target"))
        problems.extend(hba1c_scope(targets))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text().split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {s["key"]: None for s in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    output = estimate(values)
    payload = levers(values, targets)
    skillkit.write_result(args.out, manifest, output)
    (args.out / "levers.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 本次计算", "",
             f"输入：HbA1c {values['hba1c_pct']:g}%；年龄 {values['age']:g} 岁；模型性别编码 {'女性' if sex else '男性'}；访视间隔 {values['years_next']:g} 年。",
             "已确认符合研究基线条件。",
             f"在指定的 {values['years_next']:g} 年访视间隔下，Model A 的模型概率为 **{output['diabetes_probability_pct']:.2f}%**。",
             "结局是截至下一健康访视被检测或报告的糖尿病，包含血液指标、报告诊断及糖尿病用药，未区分糖尿病类型。",
             "原研究用实际观察到的下一次访视间隔；此处若输入计划间隔，得到的是条件情景，不是经过验证的固定年限预测，也不是建议的复查周期。",
             "研究来自英格兰中老年人，参与者几乎均为白人；用于其他地区或族群尚无外部验证。最终重拟合模型未单独评估，不能把交叉验证的表现当作本报告的精度。",
             "S4 采用舍入系数，论文未印出可复现的个人概率示例，结果为暂定研究读出。",
             "", TARGET_NOTE]
    if not TYPICAL_INTERVALS[0] <= values["years_next"] <= TYPICAL_INTERVALS[1]:
        lines += ["指定间隔超出论文通常约四至七年的范围，属于进一步外推。"]
    if targets:
        delta = payload["levers"][0]["diabetes_probability_pct_delta"]
        lines += ["", f"若 HbA1c 改为 {targets['hba1c_pct']:g}%，其他条件相同：模型概率为 {payload['targets']['diabetes_probability_pct']:.2f}%，变化 {delta:+.2f} 个百分点。"]
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
