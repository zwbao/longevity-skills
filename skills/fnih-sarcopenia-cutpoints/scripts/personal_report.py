"""Offline FNIH Table 3 classification from personal measurements."""
import argparse
from decimal import Decimal
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, CUTPOINTS

TITLE = "FNIH 握力与四肢瘦体重分层"


def calculate(values, sex):
    cuts = CUTPOINTS[sex]
    grip = Decimal(str(values["grip_max_kg"]))
    alm = Decimal(str(values["alm_kg"]))
    bmi = Decimal(str(values["bmi_kg_m2"]))

    def category(value, key):
        return "below_cutpoint" if value < Decimal(str(cuts[key])) else "not_below_cutpoint"

    return {
        "alm_bmi": float(alm / bmi),
        "grip_bmi": float(grip / bmi),
        "weakness": category(grip, "grip_max_kg"),
        "low_lean_mass": category(alm / bmi, "alm_bmi"),
        "weakness_bmi_alternate": category(grip / bmi, "grip_bmi"),
        "low_lean_mass_alternate": category(alm, "alm_kg"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Never leave a prior successful result beside a new input error, or vice versa.
    for filename in ("result.json", "problems.json"):
        (args.out / filename).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
        problems = list(collected.problems)
    except (OSError, ValueError) as exc:
        collected = None
        problems = [skillkit.Problem("measurements", "测量表", "file",
                                    f"无法读取测量表：{exc}。请提供 marker,value,unit 三列的 CSV 或 TSV。")]
    try:
        age = float(args.age) if args.age is not None else None
        problems.extend(skillkit.check_scalar(manifest, "age", age))
    except ValueError:
        problems.append(skillkit.Problem("age", "实足年龄", "value", "年龄必须是以岁为单位的数字。"))
    sexes = {"male": "male", "m": "male", "男": "male", "男性": "male",
             "female": "female", "f": "female", "女": "female", "女性": "female"}
    sex = sexes.get((args.sex or "").strip().lower())
    if sex is None:
        problems.append(skillkit.Problem("sex", "论文分层性别", "missing" if not args.sex else "value",
                                        "请提供论文分层使用的性别 male/男 或 female/女，不能自动选择切点。"))
    card = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join(card) + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    values = collected.values
    result = calculate(values, sex)
    cuts = CUTPOINTS[sex]
    label = {"below_cutpoint": "低于切点", "not_below_cutpoint": "未低于切点"}
    rows = [
        ("推荐：最大握力", f"{values['grip_max_kg']:g} kg", f"< {cuts['grip_max_kg']:g} kg", "weakness"),
        ("推荐：四肢瘦体重 / BMI", f"{result['alm_bmi']:.6g}", f"< {cuts['alm_bmi']:g}", "low_lean_mass"),
        ("备选：最大握力 / BMI", f"{result['grip_bmi']:.6g}", f"< {cuts['grip_bmi']:g}", "weakness_bmi_alternate"),
        ("备选：四肢瘦体重", f"{values['alm_kg']:g} kg", f"< {cuts['alm_kg']:g} kg", "low_lean_mass_alternate"),
    ]
    lines = card + ["## 你的结果", "", f"按论文{'男性' if sex == 'male' else '女性'}分层；年龄 {age:g} 岁。",
                    f"本次 BMI 为 {values['bmi_kg_m2']:g} kg/m²。", "",
                    "| 指标 | 你的值 | 论文切点（表 3） | 结果 |",
                    "|---|---:|---:|---|"]
    lines += [f"| {name} | {value} | {cut} | {label[result[key]]} |" for name, value, cut, key in rows]
    lines += ["", "推荐与备选标准分别显示，不合并为一个诊断；恰好等于切点时属于未低于切点。判断使用未显示舍入的数值。",
              "ALM/BMI 的 ALM 使用 kg，BMI 使用 kg/m²；它不是 ALM/身高²。握力/BMI 同样沿用论文单位约定。",
              "握力须为手持测力计双手测量的最大值；ALM 须为 DXA 双臂及双腿去骨瘦体重之和。体脂秤总肌肉量、单腿瘦体重或缺肢体测量不能直接代替。",
              "这些切点源自社区老年人研究；对中国人群、住院者或明显功能受限者的适用性仍需核实。未低于切点不等于排除了功能问题。",
              "验证状态：仍在验证。已核对表 3 的全部切点并测试边界行为，但正文及补充附录没有个人输入—输出算例。",
              "", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
