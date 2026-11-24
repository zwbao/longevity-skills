"""A bounded, standard-library implementation of AutoGaitA 2D kinematics.

Input is a long CSV: a time_s row starts each frame, followed by eight joint
coordinate rows. Each frame is read and validated with the shared skillkit.
"""
import argparse
import csv
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import ANGLE_TRIPLES, BOUNDARY, CYCLE_BINS, FRAME_KEYS, JOINTS, TITLE


def normalize(values, bins=CYCLE_BINS):
    """Repeat evenly distributed indices, or average contiguous source bins.

    Methods normalization and upstream define_bins, v1.3.1. Arithmetic written
    independently; no upstream package or pretrained model is needed at runtime.
    """
    n = len(values)
    if n >= bins:
        q, remainder = divmod(n, bins)
        result, start = [], 0
        for i in range(bins):
            length = q + (i < remainder)
            result.append(sum(values[start:start + length]) / length)
            start += length
        return result
    extra = bins - n
    repeated = [0] if extra == 1 else [int(i * (n - 1) / (extra - 1)) for i in range(extra)]
    return [values[i] for i in sorted(list(range(n)) + repeated)]


def angle(frame, names):
    a, b, c = names
    u = [frame[f"{a}_{axis}_cm"] - frame[f"{b}_{axis}_cm"] for axis in ("x", "y")]
    v = [frame[f"{c}_{axis}_cm"] - frame[f"{b}_{axis}_cm"] for axis in ("x", "y")]
    magnitude = math.hypot(*u) * math.hypot(*v)
    if magnitude == 0:
        raise ValueError("相邻关节坐标重合，无法定义关节角度；请检查原始追踪。")
    return math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(u, v)) / magnitude))))


def gradient(values, dt):
    # Upstream np.gradient defaults: central interior and one-sided endpoints.
    return [(values[1] - values[0]) / dt] + [
        (values[i + 1] - values[i - 1]) / (2 * dt) for i in range(1, len(values) - 1)
    ] + [(values[-1] - values[-2]) / dt]


def problem(message, key="measurements", kind="structure"):
    return skillkit.Problem(key, "步态坐标", kind, message)


def read_frames(path, manifest):
    if path is None:
        return [], [problem("缺少测量文件：请提供一个完整步态周期逐帧标定后的髋、膝、踝和足中部坐标。", kind="missing")]
    try:
        rows = skillkit.read_rows(path)
    except (OSError, ValueError, csv.Error) as e:
        return [], [problem(f"无法读取测量表：{e}")]
    if not rows or not {"item", "value", "unit"}.issubset(rows[0]):
        return [], [problem("测量表必须有 item,value,unit 三列；每帧以 time_s 行开始。")]
    index = skillkit.alias_index(skillkit.input_specs(manifest))
    blocks, current, issues = [], [], []
    for row in rows:
        hit = next((index[x] for x in skillkit.name_variants(row["item"]) if x in index), None)
        if hit is None:
            issues.append(problem(f"未识别项目「{row['item']}」，请使用清单中的关节坐标名。"))
            continue
        if hit[0]["key"] == "time_s":
            if current:
                blocks.append(current)
            current = [row]
        elif not current:
            issues.append(problem("每帧第一行须为 time_s（时间戳），其后才是该帧的关节坐标。"))
        else:
            current.append(row)
    if current:
        blocks.append(current)
    frames = []
    for i, block in enumerate(blocks, 1):
        collected = skillkit.collect_measurements(block, manifest)
        for p in collected.problems:
            p.message_zh = f"第 {i} 帧：" + p.message_zh
        issues.extend(collected.problems)
        frames.append(collected.values)
    if len(frames) < 3:
        issues.append(problem("至少需要三帧，且必须覆盖一个完整周期；不能用三个任意瞬间代替整段追踪。"))
    if issues:
        return frames, issues
    times = [f["time_s"] for f in frames]
    dt = times[1] - times[0]
    if not 0.0001 <= dt <= 1 or any(t <= times[i] or not math.isclose(t - times[i], dt, rel_tol=1e-6, abs_tol=1e-9)
                      for i, t in enumerate(times[1:])):
        issues.append(problem("时间戳必须严格递增且等间隔，间隔须在 0.0001–1 秒内；缺帧或可变帧率数据须先由追踪人员核查，不能在此自动填补。"))
    try:
        for frame in frames:
            for triple in ANGLE_TRIPLES.values():
                angle(frame, triple)
    except ValueError as e:
        issues.append(problem(str(e), kind="geometry"))
    if max(f["midfoot_x_cm"] for f in frames) <= frames[0]["midfoot_x_cm"]:
        issues.append(problem("足中部没有正向位移。此入口只接收向 x 正方向前进的地面步行，请核对方向及周期标注。"))
    return frames, issues


def compute(frames):
    dt = frames[1]["time_s"] - frames[0]["time_s"]
    angles = {joint: [angle(f, names) for f in frames] for joint, names in ANGLE_TRIPLES.items()}
    xs = {j: [f[f"{j}_x_cm"] for f in frames] for j in JOINTS}
    velocities = {j: normalize(gradient(xs[j], dt)) for j in JOINTS}
    peak = max(range(len(frames)), key=lambda i: xs["midfoot"][i])
    outputs = {"stride_length_cm": xs["midfoot"][peak] - xs["midfoot"][0],
               "time_to_peak_s": frames[peak]["time_s"] - frames[0]["time_s"]}
    for joint, values in angles.items():
        outputs[f"{joint}_angle_min_deg"] = min(values)
        outputs[f"{joint}_angle_max_deg"] = max(values)
    for joint in JOINTS:
        outputs[f"{joint}_peak_vx_cm_s"] = max(velocities[joint])
    series = {"cycle_pct": [100 * (i + 1) / CYCLE_BINS for i in range(CYCLE_BINS)]}
    origin = min(xs["midfoot"])
    for joint in JOINTS:
        series[f"{joint}_x_cm"] = normalize([x - origin for x in xs[joint]])
        series[f"{joint}_vx_cm_s"] = velocities[joint]
    for joint, values in angles.items():
        series[f"{joint}_angle_deg"] = normalize(values)
    return outputs, series


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--age")
    parser.add_argument("--sex")
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "cycle.csv", "problems.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)
    frames, issues = read_frames(args.measurements, manifest)
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            issues.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            issues.append(problem("年龄必须是以岁计的有限数值。", key="age"))
    if args.sex is not None and args.sex not in ("male", "female", "other", "unknown"):
        issues.append(problem("性别可填 male、female、other 或 unknown，也可以不填。", key="sex"))
    card = paper_card_lines()
    if issues:
        path = skillkit.write_problems(args.out, issues, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *card, body]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    outputs, series = compute(frames)
    skillkit.write_result(args.out, manifest, outputs)
    with (args.out / "cycle.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(series)
        writer.writerows(zip(*series.values()))
    lines = [f"# {TITLE}", "", *card, "", "## 本次步态", "",
             "暂定读出：尚未复现论文印出的个人运动学结果。以下只描述你提供的一个周期。", "",
             "| 指标 | 本次结果 |", "|---|---:|"]
    for spec in manifest["outputs"]:
        lines.append(f"| {spec['label_zh']} | {outputs[spec['key']]:.4g} {spec['unit']} |")
    lines += ["", "膝、踝角度为三个标志点形成的内角；小角表示更屈曲，不是关节活动度检查中的零位角。",
              "水平速度是沿行进方向的速度分量，单位为厘米/秒；峰值来自归一化后的周期曲线。它不是整体步行速度，也不是推进力。",
              "跨步距离按足中部最大横坐标减去周期起点横坐标计算，不等同于左右脚之间的步长。",
              "本次不作年龄分档、同龄百分位或正常/异常判断；单次差异也不能解释为衰老或干预效果。",
              "完整归一化曲线见 cycle.csv；与后续记录比较时，需保持标定、步行条件、追踪方式和周期起止一致。"]
    if age is not None and not (21 <= age <= 36 or 46 <= age <= 85):
        lines += ["提供的年龄不在论文两个人体样本组的实测年龄段内；此方法没有给出该年龄的参考范围。"]
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
