"""Read the exact Table S12 cell for age and click-ABR Wave I latency."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGE_GRID, BOUNDARY, LATENCY_GRID_MS, OUTPUT_KEYS, TABLE, TITLE


def grid_member(value, grid):
    # Only binary floating-point noise from declared unit conversions is allowed.
    # This is not measurement rounding or nearest-neighbour selection.
    return next((point for point in grid if math.isclose(value, point, rel_tol=0, abs_tol=1e-12)), None)


def lookup(age_years, w1_latency_ms):
    age = grid_member(age_years, AGE_GRID)
    latency = grid_member(w1_latency_ms, LATENCY_GRID_MS)
    if age is None or latency is None:
        raise ValueError("Input is not a printed Table S12 coordinate")
    return dict(TABLE[(age, latency)])


def write_failure(out, manifest, problems):
    report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    body = report.read_text(encoding="utf-8").split("\n", 1)[1]
    report.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
    skillkit.write_result(out, manifest, {key: None for key in OUTPUT_KEYS})
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="同一只耳的波 I 潜伏期 CSV：marker,value,unit")
    parser.add_argument("--age", help="实足年龄（岁）；原表仅有 45、55、65、75")
    parser.add_argument("--sex", help="可选背景：male/female/男/女；不改变原表的男性参考设定")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as error:
        return write_failure(args.out, manifest, [skillkit.Problem(
            "measurements", "测量表", "file", f"无法读取测量表，请提供 marker,value,unit 格式的 CSV：{error}")])
    problems = list(collected.problems)
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
        except ValueError:
            problems.append(skillkit.Problem("age_years", "实足年龄", "parse", "年龄须为有限数值，单位为岁。"))
    if not any(p.key == "age_years" for p in problems):
        problems += skillkit.check_scalar(manifest, "age_years", age)
    if args.sex is not None and args.sex.casefold() not in {"male", "female", "男", "女"}:
        problems.append(skillkit.Problem("sex", "自报性别", "category", "自报性别可写 male、female、男或女；也可省略，不改变原表设定。"))
    latency = collected.values.get("w1_latency_ms")
    if age is not None and not any(p.key == "age_years" for p in problems) and grid_member(age, AGE_GRID) is None:
        problems.append(skillkit.Problem(
            "age_years", "实足年龄", "unsupported_grid",
            "此年龄不在原表中。S12 仅印有 45、55、65、75 岁；不插值、不取整，也不要为匹配原表更改真实年龄。"))
    if latency is not None and grid_member(latency, LATENCY_GRID_MS) is None:
        problems.append(skillkit.Problem(
            "w1_latency_ms", "ABR 波 I 潜伏期", "unsupported_grid",
            "此潜伏期不在原表中。S12 仅印有 1、1.2667、1.4、1.48、1.83 ms；不插值、不就近匹配，不要修改真实测量值。"))
    if problems:
        return write_failure(args.out, manifest, problems)

    result = lookup(age, latency)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "problems.json").unlink(missing_ok=True)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 原表参考值", "",
             f"提供的年龄：{age:g} 岁；同一只耳的点击 ABR 波 I 潜伏期：{latency:g} ms。",
             "对应补充表 S12 的一个精确坐标；其余连续协变量为中心化零值，使用男性参考设定。",
             "", "| 指标 | 原表模型均值 | 均值的 95% 置信区间 | 均值标准误（百分点） |",
             "| --- | ---: | ---: | ---: |"]
    for prefix, label in [("ws", "词语识别（WS）"), ("ps", "音素识别（PS）")]:
        lines.append(
            f"| {label} | {result[prefix + '_reference_pct']:.2f}% | "
            f"{result[prefix + '_mean_ci_lower_pct']:.2f}%–{result[prefix + '_mean_ci_upper_pct']:.2f}% | "
            f"{result[prefix + '_mean_se_pp']:.2f} |")
    lines += ["", "区间来自原表的 HC3 稳健估计，描述模型均值的不确定性，不是个人预测区间。"
              "原表区间若超过 100%，仍保留原值，不能解读为超过满分的实际表现。",
              "", "自报性别只作背景，不调整表内数值；即使提供女性信息，仍是男性参考设定。",
              "", "## 适用条件", "",
              "研究来自无耳鸣、未使用助听器或人工耳蜗的瑞典成年人；"
              "言语测试为瑞典语单词、+4 dB 信噪比。"
              "ABR 为 90 dBnHL、100 微秒交替极性点击、9.1 次/秒，使用 Chartr 或 Eclipse 系统。"
              "不同语言、刺激强度、设备或有耳鸣者不能直接套作个人预测。",
              "", "此表固定了听力阈值、耳声发射和其他波潜伏期；没有使用你的这些测量。"
              "目前仅提供原表参考，不生成完整回归、听力年龄、风险分档或可设定的干预目标。",
              "", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
