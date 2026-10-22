#!/usr/bin/env python3
"""LinAge for one person, with the parameters of Fong et al., Nature Aging 2024.

Inputs are read through skillkit as skill.json declares them. Missing or
wrong inputs write out/problems.json and exit 3; a computed LinAge writes
out/report.md and out/result.json.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_BELOW, AGE_MIN, BOUNDARY, COMORBIDITIES, PARAMS, SELF_HEALTH_KEYS, comorbidity_index,
                     huq050_from_visits, ldl_mmol_l, linage, self_health_index, smoking_label, smoking_score)

TITLE = "LinAge 临床衰老年龄"
LAB_KEYS = [key for _code, key, _t, _m, _f in PARAMS
            if key not in ("comorbidity_index", "self_health_index", "healthcare_use_code", "ldl_mmol_l")]
TOP_TERMS = 5


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man", "1"}:
        return "male"
    if text in {"female", "f", "女", "woman", "2"}:
        return "female"
    return None


def _flag(values: dict, key: str, label: str, problems: list) -> int:
    value = values.get(key, 0.0)
    if value not in (0.0, 1.0):
        problems.append(skillkit.Problem(key, label, "parse", f"{label} 只能写 1（有/是）或 0（没有/不是），收到 {value:g}。"))
        return 0
    return int(value)


def derive(values: dict, problems: list) -> dict:
    """The derived LinAge inputs, as linAge.R computes them; unanswered questions count as no."""
    present = [label for key, label, _item in COMORBIDITIES if _flag(values, key, label, problems)]
    manifest = skillkit.load_manifest(__file__)
    labels = {key: skillkit.spec_by_key(manifest, key)["label_zh"] for key in SELF_HEALTH_KEYS}
    fair, poor, better, worse = (_flag(values, key, labels[key], problems) for key in SELF_HEALTH_KEYS)
    if fair and poor:
        problems.append(skillkit.Problem("poor_general_health", labels["poor_general_health"], "parse",
                                         "总体健康自评只能选一个：「一般」和「差」不能都写 1。"))
    if better and worse:
        problems.append(skillkit.Problem("worse_current_health", labels["worse_current_health"], "parse",
                                         "和一年前比只能选一个：「更好」和「更差」不能都写 1。"))
    code = values.get("huq050")
    visits = values.get("healthcare_visits_past_year")
    if code is not None and code != int(code):
        problems.append(skillkit.Problem("huq050", "就医使用编码（HUQ050）", "parse", f"HUQ050 编码是 0–5 的整数，收到 {code:g}。"))
    if visits is not None and visits != int(visits):
        problems.append(skillkit.Problem("healthcare_visits_past_year", "过去一年看医生的次数", "parse", f"看医生次数是整数，收到 {visits:g}。"))
    if code is not None and visits is not None and int(code) != huq050_from_visits(visits):
        problems.append(skillkit.Problem("huq050", "就医使用编码（HUQ050）", "duplicate",
                                         f"HUQ050 编码 {code:g} 和看医生 {visits:g} 次对应的编码 {huq050_from_visits(visits)} 不一致。请只保留一个。"))
    if code is None:
        code = huq050_from_visits(visits) if visits is not None else 0
    derived = {
        "comorbidity_index": comorbidity_index(len(present)),
        "self_health_index": self_health_index(fair, poor, better, worse),
        "healthcare_use_code": float(int(code)),
        "present": present,
        "answered_health": any(key in values for key in SELF_HEALTH_KEYS),
        "answered_use": "huq050" in values or "healthcare_visits_past_year" in values,
    }
    if all(key in values for key in ("tc_mmol_l", "tg_mmol_l", "hdl_mmol_l")):
        derived["ldl_mmol_l"] = ldl_mmol_l(values["tc_mmol_l"], values["tg_mmol_l"], values["hdl_mmol_l"])
    return derived


def collect(measurements: Path | None, age: float | None, sex: str | None):
    manifest = skillkit.load_manifest(__file__)
    exists = measurements is not None and Path(measurements).exists()
    collected = skillkit.collect_file(measurements if exists else None, manifest)
    problems = list(collected.problems)
    problems += skillkit.check_scalar(manifest, "age", age)
    if age is not None and not problems and not (AGE_MIN <= age < AGE_BELOW):
        problems.append(skillkit.Problem("age", "实足年龄", "range",
                                         f"LinAge 只在 {AGE_MIN}–{AGE_BELOW - 1} 岁的人里训练（论文代码只算这个年龄段），{age:g} 岁不算。"))
    person_sex = parse_sex(sex)
    if person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "missing", "需要性别（男或女）：LinAge 男女各用一套参数。"))
    values = dict(collected.values)
    derived = derive(values, problems)
    if not any(key in values for key in LAB_KEYS):
        problems.append(skillkit.Problem("measurements", "化验和体检", "missing",
                                         "没有读到任何 LinAge 化验或体检项（血常规、生化、血压等），只靠问卷和年龄算不出有意义的 LinAge。"))
    return values, derived, person_sex, problems


def model_inputs(values: dict, derived: dict) -> dict:
    inputs = {key: values[key] for key in LAB_KEYS if key in values}
    for key in ("comorbidity_index", "self_health_index", "healthcare_use_code", "ldl_mmol_l"):
        if key in derived:
            inputs[key] = derived[key]
    return inputs


def render(age: float, sex: str, values: dict, derived: dict, result: dict, meds: list, labs: list) -> str:
    manifest = skillkit.load_manifest(__file__)
    label = {spec["key"]: spec["label_zh"] for spec in manifest["inputs"]}
    label.update({"comorbidity_index": "并存病指数", "self_health_index": "自评健康指数",
                  "healthcare_use_code": "就医使用编码", "ldl_mmol_l": "计算的低密度脂蛋白胆固醇"})
    delta = result["delta"]
    direction = "大" if delta >= 0 else "小"
    sex_zh = "男" if sex == "male" else "女"
    lines = [f"# {TITLE}", "",
             f"按论文公布的 LinAge 公式（{sex_zh}性参数），你的 LinAge 是 {result['linage']:.1f} 岁，"
             f"比实足年龄 {age:g} 岁{direction} {abs(delta):.1f} 岁。"
             + (f"61 个参数里有 {len(result['missing'])} 个没有给出，按 0 计，见下面的缺项。" if result["missing"] else ""), "",
             "## 怎么算的", "",
             "每一项先减去论文「健康衰老」组同性别的中位数，再除以该组的离散度（MAD），乘上权重后相加；"
             "C 反应蛋白和 NT-proBNP 先取对数，可替宁先分成 0–3 档，并存病、自评健康和就医使用三个指数不标准化。"
             "年龄差 = 常数 + 年龄权重 × 实足年龄（月）+ 各项之和。", "",
             f"- 各项之和：{result['sum_terms']:.2f}",
             f"- 年龄差：{delta:+.2f} 岁"]
    missing = result["missing"]
    if missing:
        weight = sum(w for _k, w in missing)
        names = "、".join(label.get(key, key) for key, _w in missing)
        lines += ["", f"## 缺项（{len(missing)} 个，按 0 计）", "",
                  f"{names}。", "",
                  f"论文的办法是把缺项的标准化值记为 0，每个缺项带来的误差大约是它的权重；这些缺项权重的绝对值加起来是 {weight:.2f} 岁，"
                  "缺得越多，这个岁数越不可靠。"]
    else:
        lines += ["", "61 个参数都给齐了。"]
    top = sorted(result["terms"].items(), key=lambda item: abs(item[1]), reverse=True)[:TOP_TERMS]
    lines += ["", "## 贡献最大的几项", ""]
    for key, term in top:
        lines.append(f"- {label.get(key, key)}：{term:+.2f} 岁")
    lines += ["", "这些是死亡风险模型里的统计贡献，有些方向和常识相反（例如男性参数里谷丙转氨酶和白蛋白的权重为负，女性参数里高密度脂蛋白的权重为正），不能当成改善目标。"]
    lines += ["", "## 问卷得到的指数", "",
              f"- 并存病指数：{derived['comorbidity_index']:.4f}（22 项里答「有」{len(derived['present'])} 项"
              + (f"：{'、'.join(derived['present'])}" if derived["present"] else "") + "）",
              f"- 自评健康指数：{derived['self_health_index']:g}" + ("" if derived["answered_health"] else "（没有作答，按 0 计）"),
              f"- 就医使用编码：{derived['healthcare_use_code']:g}" + ("" if derived["answered_use"] else "（没有作答，按 0 计）")]
    if "cotinine_ng_ml" in values:
        score = smoking_score(values["cotinine_ng_ml"])
        lines.append(f"- 可替宁 {values['cotinine_ng_ml']:g} ng/mL，吸烟分档 {score}（{smoking_label(score)}）")
    if "ldl_mmol_l" in derived:
        lines.append(f"- 计算的低密度脂蛋白胆固醇：{derived['ldl_mmol_l']:.2f} mmol/L（论文代码的算法 TC − TG/5 − HDL，不是化验单上的 LDL）")
    lines += ["", "没有作答的并存病按「没有」计，这和论文的代码一样。LinAge 是在美国 40–84 岁人群里建的，用在别的人群时偏差未知。"]
    lines += ["", "## 你正在使用的药", ""]
    if meds:
        lines += [f"- {name}：LinAge 不读用药。不能据此停。" for name in meds]
    else:
        lines.append("没有提供现用药。")
    lines += ["", "## 体检", ""]
    if labs:
        lines.append("下面照录体检文件。要进 LinAge 的数值请写进测量表。体检不增删方法算出的名单。")
        lines += [f"- {row}" for row in labs]
    else:
        lines.append("没有提供体检。体检不增删方法算出的名单。")
    lines += ["", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def _read_lines(path: Path | None) -> list:
    if path is None or not Path(path).exists():
        return []
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    out = "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]])
    return out + ("\n" if text.endswith("\n") else "")


def report(out: Path, age: float | None, sex: str | None, medications: Path | None, labs: Path | None,
           measurements: Path | None) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    stale = out / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    values, derived, person_sex, problems = collect(measurements, age, sex)
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out, manifest, {item["key"]: None for item in manifest["outputs"]})
        return path
    result = linage(model_inputs(values, derived), person_sex, age)
    path = out / "report.md"
    path.write_text(_with_paper_card(render(age, person_sex, values, derived, result,
                                            _read_lines(medications), _read_lines(labs))), encoding="utf-8")
    skillkit.write_result(out, manifest, {
        "linage_years": result["linage"],
        "linage_delta_years": result["delta"],
        "missing_count": len(result["missing"]),
        "missing_weight_years": sum(w for _k, w in result["missing"]),
        "comorbidity_index": derived["comorbidity_index"],
        "self_health_index": derived["self_health_index"],
        "healthcare_use_code": derived["healthcare_use_code"],
        "smoking_score": smoking_score(values["cotinine_ng_ml"]) if "cotinine_ng_ml" in values else None,
        "ldl_mmol_l": derived.get("ldl_mmol_l"),
    })
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--medications", type=Path)
    parser.add_argument("--labs", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    report(args.out, args.age, args.sex, args.medications, args.labs, args.measurements)
    if (args.out / "problems.json").exists():
        return skillkit.EXIT_INPUT_PROBLEM
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
