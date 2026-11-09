#!/usr/bin/env python3
"""Six-domain sleep health score (0–6) of Marent et al., GeroScience 2026.

Reads one week of wearable sleep summaries and two PSQI items, marks each
domain favourable or not with the paper's printed cut points (presets.py),
and sums them. Writes out/report.md, out/result.json and, with --targets,
out/levers.json. Exits 3 with out/problems.json when an input is missing,
in an unknown unit, out of range, or not an answer code.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    COHORT_IQR_SCORE,
    COHORT_MEDIAN_SCORE,
    DOMAINS,
    DURATION_HIGH_H,
    DURATION_LOW_H,
    EFFICIENCY_MIN_PCT,
    MIDPOINT_EARLIEST_H,
    MIDPOINT_LATEST_H,
    MIDPOINT_SD_BELOW_MIN,
    SCORE_MAX,
    TITLE,
    midpoint_clock,
    score,
)

CODE_KEYS = ("psqi_sleep_quality_code", "psqi_trouble_awake_code")
CODE_WORDS = {
    "psqi_sleep_quality_code": ("非常好", "尚好", "不好", "非常差"),
    "psqi_trouble_awake_code": ("过去一个月没有", "每周少于 1 次", "每周 1–2 次", "每周 3 次或以上"),
}


def collect(path: Path | None, manifest: dict) -> tuple[dict, list]:
    collected = skillkit.collect_file(path, manifest)
    problems = list(collected.problems)
    values = dict(collected.values)
    for key in CODE_KEYS:
        if key in values and not float(values[key]).is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(
                key, spec["label_zh"], "parse",
                f"{spec['label_zh']} 读成 {values[key]:g}，不是 0、1、2、3 中的一个答案代码。{spec.get('note_zh', '')}",
            ))
            values.pop(key)
    return values, problems


def clock_text(value_h: float) -> str:
    total = int(round(midpoint_clock(value_h) * 60)) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def shown_value(input_key: str, value: float) -> str:
    if input_key == "sleep_duration_h":
        return f"{value:.2f} 小时"
    if input_key == "sleep_efficiency_pct":
        return f"{value:.1f}%"
    if input_key == "sleep_midpoint_clock_h":
        return clock_text(value)
    if input_key == "sleep_midpoint_sd_min":
        return f"{value:.0f} 分钟"
    return f"{int(value)}（{CODE_WORDS[input_key][int(value)]}）"


def gap_text(input_key: str, value: float) -> str:
    """How far the value sits from the favourable band, in the input's unit."""
    if input_key == "sleep_duration_h":
        if value < DURATION_LOW_H:
            return f"比 {DURATION_LOW_H:g} 小时少 {60 * (DURATION_LOW_H - value):.0f} 分钟"
        if value > DURATION_HIGH_H:
            return f"比 {DURATION_HIGH_H:g} 小时多 {60 * (value - DURATION_HIGH_H):.0f} 分钟"
    if input_key == "sleep_efficiency_pct" and value < EFFICIENCY_MIN_PCT:
        return f"比 {EFFICIENCY_MIN_PCT:g}% 低 {EFFICIENCY_MIN_PCT - value:.1f} 个百分点"
    if input_key == "sleep_midpoint_clock_h":
        clock = midpoint_clock(value)
        early = (MIDPOINT_EARLIEST_H - clock) % 24
        late = (clock - MIDPOINT_LATEST_H) % 24
        if early > 0 and late > 0:
            if early <= late:
                return f"比 02:00 早 {early * 60:.0f} 分钟"
            return f"比 04:00 晚 {late * 60:.0f} 分钟"
    if input_key == "sleep_midpoint_sd_min" and value >= MIDPOINT_SD_BELOW_MIN:
        return f"要低于 {MIDPOINT_SD_BELOW_MIN:g} 分钟"
    if input_key in CODE_KEYS and value > 1:
        return "答案落在后两档"
    return ""


def levers(values: dict, targets: dict) -> dict:
    """Score at each target alone and at all targets together.

    The score is a count of thresholds, so the sensitivity of each input is
    reported as whether it is favourable now and how far it sits from the
    favourable band, not as a slope.
    """
    manifest = skillkit.load_manifest(__file__)
    current, flags = score(values)
    sensitivity = []
    for flag_key, input_key, name, rule in DOMAINS:
        sensitivity.append({
            "key": input_key,
            "label_zh": name,
            "unit": skillkit.spec_by_key(manifest, input_key).get("unit", ""),
            "value": values[input_key],
            "favourable": bool(flags[flag_key]),
            "rule_zh": rule,
            "gap_zh": gap_text(input_key, values[input_key]),
        })
    out = {
        "schema": "longevity-levers/1",
        "model": "sleep_health_score_6",
        "model_zh": "六维睡眠健康分（Marent 等，GeroScience 2026）",
        "current": {"sleep_health_score": current},
        "sensitivity": sensitivity,
        "levers": [],
        "note_zh": "分数只数有几项落在论文的有利范围；分数变化不代表认知或健康结局会跟着变化，论文没有发现总分与认知相关。",
    }
    usable = {key: value for key, value in targets.items() if key in values}
    if usable:
        for key, target in usable.items():
            moved, _ = score(dict(values, **{key: target}))
            spec = skillkit.spec_by_key(manifest, key)
            out["levers"].append({
                "key": key,
                "label_zh": spec.get("label_zh", key),
                "unit": spec.get("unit", ""),
                "from": values[key],
                "to": target,
                "sleep_health_score_delta": moved - current,
            })
        together, _ = score(dict(values, **usable))
        out["targets"] = {
            "values": usable,
            "sleep_health_score": together,
            "sleep_health_score_delta": together - current,
        }
        out["levers"].sort(key=lambda item: -item["sleep_health_score_delta"])
    return out


def report(values: dict, age: float | None) -> tuple[str, dict]:
    total, flags = score(values)
    lines = [f"# {TITLE}", ""]
    lines += paper_card_lines()
    lines += ["", "## 你的结果", "", f"六维睡眠健康分：**{total} / {SCORE_MAX}**（每项落在论文的有利范围记 1 分）。", ""]
    lines += ["| 维度 | 你的数值 | 论文的有利范围 | 判定 |", "| --- | --- | --- | --- |"]
    for flag_key, input_key, name, rule in DOMAINS:
        verdict = "有利（1 分）" if flags[flag_key] else "不利（0 分）"
        gap = gap_text(input_key, values[input_key])
        if gap and not flags[flag_key]:
            verdict += f"，{gap}"
        lines.append(f"| {name} | {shown_value(input_key, values[input_key])} | {rule} | {verdict} |")
    lines += [
        "",
        "## 怎么读",
        "",
        f"- 论文队列基线（233 人）的总分中位数是 {COHORT_MEDIAN_SCORE} 分（四分位 {COHORT_IQR_SCORE[0]}–{COHORT_IQR_SCORE[1]}），这是人群描述，不是你的参考值或正常值。",
        "- 论文里，这个总分、睡眠时长和 PSQI 总分都没有和记忆、执行功能或处理速度显著相关；只有手环测的睡眠效率越高，执行功能越好。这是观察性关联，方向不能确定，所以这里不按你的分数估算认知表现。",
        "- 论文的睡眠效率、睡眠中点来自手腕 ActiGraph 加 GGIR 算法；消费级手环的算法不同，接近切点（例如效率 84–86%）的判定可能随设备翻转。",
    ]
    if age is not None and age < 55:
        lines.append(f"- 你填的年龄是 {age:g} 岁，论文人群是 55 岁及以上；计分规则照样适用，但与认知的关联没在你这个年龄检验过。")
    lines += [
        "",
        "## 没有算的",
        "",
        "- 认知领域 z 分或痴呆风险：论文补充表 6B 等给了混合模型系数，但结局是相对 PASOCA 队列基线的 CANTAB z 分，需要同一套测验和同一队列的均值标准差，个人算不出，也不该用睡眠去推。",
        "- PSQI 总分（0–21）：需要全部 19 道题，这里只用了论文计分用到的两道。",
    ]
    lines += ["", f"边界: {BOUNDARY}"]
    outputs = {"sleep_health_score": total, **flags}
    return "\n".join(lines) + "\n", outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit with the six inputs")
    parser.add_argument("--age", type=float, help="age in years (only for the population note)")
    parser.add_argument("--targets", type=Path, help="CSV of target values (item,value,unit) for out/levers.json")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json", "result.json"):
        (out_dir / name).unlink(missing_ok=True)

    manifest = skillkit.load_manifest(__file__)
    path = args.measurements if args.measurements is not None and args.measurements.exists() else None
    values, problems = collect(path, manifest)
    if args.measurements is not None and path is None:
        problems.insert(0, skillkit.Problem("", "", "missing", f"找不到测量文件 {args.measurements}。"))
    problems += skillkit.check_scalar(manifest, "age", args.age)
    target_values: dict = {}
    if args.targets is not None:
        if not args.targets.exists():
            problems.append(skillkit.Problem("", "", "missing", f"找不到目标文件 {args.targets}。"))
        else:
            target_values, target_problems = collect(args.targets, manifest)
            problems += [
                skillkit.Problem(p.key, p.label, p.kind, "目标文件：" + p.message_zh)
                for p in target_problems if p.kind != "missing"
            ]
    if problems:
        skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        return skillkit.EXIT_INPUT_PROBLEM

    text, outputs = report(values, args.age)
    (out_dir / "report.md").write_text(text, encoding="utf-8")
    skillkit.write_result(out_dir, manifest, outputs)
    if args.targets is not None:
        (out_dir / "levers.json").write_text(
            json.dumps(levers(values, target_values), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
