"""Offline historical cohort lookup; no survival-curve reconstruction."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_STARTS, BOUNDARY, FIGURE_4_GAINS, HISTORY_LABELS,
                     PRINTED_RATIOS, QUIT_STARTS, TABLE_5, TITLE, band_label, band_start)


def lookup(age, history, quit_age=None):
    low = band_start(age, AGE_STARTS)
    if low is None or history not in HISTORY_LABELS:
        raise ValueError("Unsupported age or smoking history")
    quit_low = None
    if history == 2:
        quit_low = None if quit_age is None else band_start(quit_age, QUIT_STARTS)
        if quit_low is None or quit_age > age:
            raise ValueError("Unsupported or inconsistent cessation age")
    elif quit_age is not None:
        raise ValueError("Cessation age requires former smoking history")
    row = TABLE_5[low]
    if history == 2:
        cell = None if quit_low == 25 else row[(quit_low - 35) // 10 + 1]
    else:
        cell = row[0 if history == 0 else 4]
    return {
        "attained_age_band": band_label(low),
        "smoking_history_group": HISTORY_LABELS[history],
        "quit_age_band": None if quit_low is None else band_label(quit_low),
        "cohort_annual_deaths_per_1000": None if cell is None else cell[0],
        "cohort_observed_deaths": None if cell is None else cell[1],
        "never_smoker_annual_deaths_per_1000": row[0][0],
        "continuing_smoker_annual_deaths_per_1000": row[4][0],
        "printed_smoker_vs_never_ratio": PRINTED_RATIOS[low],
        "cohort_approx_life_years_gained": None if quit_low is None else FIGURE_4_GAINS[quit_low],
    }


def collect(args, manifest):
    try:
        data = skillkit.collect_file(args.measurements, manifest)
        values, problems = data.values, list(data.problems)
        if data.unmatched:
            problems.append(skillkit.Problem("", "吸烟史", "unknown", "有无法识别的项目：" + "、".join(data.unmatched)))
    except (OSError, ValueError, UnicodeError) as exc:
        values = {}
        problems = [skillkit.Problem("", "吸烟史", "file", f"无法读取吸烟史文件：{exc}")]
    age = None
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, "age", age)
        if age is not None and age == 85:
            problems.append(skillkit.Problem("age", "年龄", "unsupported", "表5只覆盖35岁至85岁生日之前，没有85岁及以上的年龄行。"))
    except ValueError:
        problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值，单位为岁。"))
    if args.sex != "male":
        problems.append(skillkit.Problem("sex", "性别", "missing" if args.sex is None else "unsupported",
                                        "请提供性别参数；本查表只接受male（男性），女性没有对应数据，不套用男性数值。"))
    history = values.get("smoking_history_code")
    quit_age = values.get("quit_age_years")
    if history is not None and history not in HISTORY_LABELS:
        problems.append(skillkit.Problem("smoking_history_code", "吸烟史编码", "unsupported",
                                        "编码仅接受0终生不吸烟、1持续仅吸卷烟、2曾持续仅吸卷烟现已戒烟；3其他或混合模式没有对应数据，小数编码无效。"))
    if history == 2:
        if quit_age is None and not any(p.key == "quit_age_years" for p in problems):
            problems.append(skillkit.Problem("quit_age_years", "戒烟年龄", "missing", "已戒烟者需要真实戒烟年龄，不能用当前年龄代替。"))
        if quit_age is not None and band_start(quit_age, QUIT_STARTS) is None:
            problems.append(skillkit.Problem("quit_age_years", "戒烟年龄", "unsupported", "表5及图4只支持25岁至65岁生日之前的戒烟分组；不插值、不外推。"))
        if quit_age is not None and age is not None and quit_age > age:
            problems.append(skillkit.Problem("quit_age_years", "戒烟年龄", "inconsistent", "戒烟年龄不能大于当前年龄；这里读取已发生的吸烟史，不读取未来计划。"))
    elif history is not None and quit_age is not None:
        problems.append(skillkit.Problem("quit_age_years", "戒烟年龄", "inconsistent", "只有编码2的已戒烟者可以填写戒烟年龄；请核对吸烟史，不用0作为缺失值。"))
    return age, history, quit_age, problems


def render(result, age, quit_age):
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的历史分组", "",
             f"当前年龄 {age:g} 岁，对应表5的 {result['attained_age_band']} 岁行；吸烟史为“{result['smoking_history_group']}”。"]
    if quit_age is not None:
        lines += [f"你填写的戒烟年龄为 {quit_age:g} 岁，属于 {result['quit_age_band']} 岁组。"]
    rate = result["cohort_annual_deaths_per_1000"]
    if rate is None:
        reason = ("表5没有25–34岁戒烟组这一列。" if result["quit_age_band"] == "25-34"
                  else "表5仅列戒烟年龄段之后的死亡率，你仍处于戒烟年龄段。")
        lines += ["", f"**所匹配组的年死亡率：未报告。** {reason}空缺保持为空，不用终生不吸烟者或其他组的数据代替。"]
    else:
        lines += ["", f"**所匹配组的队列年死亡率：每千名男性每年 {rate:.1f} 例。**",
                  f"该表格单元记录的队列死亡数为 {result['cohort_observed_deaths']}；这不是你的个人事件数。"]
    lines += ["", "## 同年龄行的队列参照", "",
              "| 历史人群 | 年死亡率（每千名男性） |", "|---|---:|",
              f"| 终生不吸烟 | {result['never_smoker_annual_deaths_per_1000']:.1f} |",
              f"| 持续仅吸卷烟 | {result['continuing_smoker_annual_deaths_per_1000']:.1f} |", "",
              f"论文印出的持续吸卷烟者/终生不吸烟者死亡率比为 {result['printed_smoker_vs_never_ratio']:.1f}。这是两个人群的比较，不是你的个人风险比，也不是戒烟者相对风险。",
              "表5的年死亡率为两个五岁年龄组死亡率的均值，不是个人一年死亡概率，也不能乘以十作为十年概率。比值直接照录原表，不用已四舍五入的死亡率重新相除。"]
    gain = result["cohort_approx_life_years_gained"]
    if gain is not None:
        lines += ["", "## 对应戒烟组的寿命差说明", "",
                  f"图4及正文对 {result['quit_age_band']} 岁戒烟组的概括是：相对持续吸卷烟者，队列平均寿命约多 {gain:g} 年。",
                  "这是按历史戒烟组匹配的近似概括，不是你从现在起还能增加的寿命，不随当前年龄重新计算，也不保证每个人获得同样差异。",
                  "图4中约60岁戒烟者在60–64岁的死亡率曾由作者插值，并非直接观测；本工具仅引用已发表的寿命差概括，不重建曲线。"]
    lines += ["", "## 适用范围", "",
              "资料来自1900–1930年出生的英国男性医生，随访期间为1951–2001年。今天不同地区、医疗条件和吸烟经历的男性只能把它作为历史队列参照；没有进行现代人群校准。",
              "当前或既往吸烟组限持续仅吸卷烟的模式；不能把电子烟、雪茄、烟斗、混合使用、复吸或间歇吸烟自动归入这些组。终生不吸烟按论文定义排除曾在一年内大多数日子吸烟者。",
              "部分参与者因患病而戒烟，存在反向因果；原表留空的同期死亡率不能补造。表5未给个人预测区间，图4的完整五岁分层率和权重未公开列出，本报告不生成个人生存曲线。",
              "", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="当前年龄，岁；35≤年龄<85")
    parser.add_argument("--sex", help="male；该队列仅有男性")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    age, history, quit_age, problems = collect(args, manifest)
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {s["key"]: None for s in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    result = lookup(age, history, quit_age)
    skillkit.write_result(args.out, manifest, result)
    (args.out / "report.md").write_text(render(result, age, quit_age), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
