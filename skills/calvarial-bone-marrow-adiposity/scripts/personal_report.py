"""Apply the unchanged published SavedModel to personal extracted MRI layers."""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import skillkit
from paper_card import lines as paper_card_lines
from presets import (N_LAYERS, MAX_INTENSITY, LAYER_SPACING_MM, VERTEX_SUM_CUTOFF,
                     MIN_VERTICES, MAX_OUTER_SD, MD_CUTOFF,
                     MAX_OUTLIER_FRACTION, TITLE, BOUNDARY)

ROOT = Path(__file__).resolve().parents[1]


def orient(data):
    if data.ndim != 2:
        raise ValueError("强度矩阵必须为二维。")
    if data.shape[1] == N_LAYERS:
        return data
    if data.shape[0] == N_LAYERS:
        return data.T
    raise ValueError("强度矩阵必须恰有 50 列或 50 行，不能缺层或补零。")


def predict_bounds(data):
    # Integrity check before loading any graph or weights.
    manifest = skillkit.load_manifest(__file__)
    for item in manifest["data_files"]:
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise RuntimeError("发布模型校验失败，请恢复技能内原始模型文件。")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    import tensorflow as tf
    config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=1,
                                      inter_op_parallelism_threads=1,
                                      device_count={"GPU": 0})
    # Legacy graph loader avoids Keras 3 incompatibility with the TF 2.4.1
    # optimizer objects. It restores the original graph and checkpoint directly.
    with tf.compat.v1.Session(graph=tf.Graph(), config=config) as session:
        meta = tf.compat.v1.saved_model.loader.load(session, ["serve"], str(ROOT / "data/model"))
        signature = meta.signature_def["serving_default"]
        inp = session.graph.get_tensor_by_name(signature.inputs["dense_input"].name)
        out = session.graph.get_tensor_by_name(signature.outputs["dense_3"].name)
        chunks = []
        for start in range(0, len(data), 8192):
            normalized = (data[start:start+8192] / MAX_INTENSITY).astype(np.float32)
            padded = np.pad(normalized, ((0, 0), (0, N_LAYERS * 2)))
            chunks.append(session.run(out, {inp: padded}))
    values = np.concatenate(chunks) * N_LAYERS
    if not np.isfinite(values).all():
        raise ValueError("模型产生非有限边界，无法报告。")
    # np.savetxt(fmt='%1.0f') in run_predBM rounds to nearest/even.
    return np.rint(np.clip(values, 1, N_LAYERS)).astype(int)


def qc_reasons(count, outer_sd, outlier_fraction):
    reasons = []
    if count < MIN_VERTICES:
        reasons.append("可用颅顶部位点少于 5000，未达到论文质控要求。")
    if outer_sd > MAX_OUTER_SD:
        reasons.append("外板平均信号在位点间的标准差超过 30，定位可能失败。")
    if outlier_fraction > MAX_OUTLIER_FRACTION:
        reasons.append("马氏距离平方大于 25 的位点超过 0.5%，未通过定位质控。")
    return reasons


def summarize(data, bounds):
    def means(first, last):
        # Inclusive endpoints, matching R's a:b (also if reversed).
        return np.array([row[min(a, b)-1:max(a, b)].mean()
                         for row, a, b in zip(data, bounds[:, first], bounds[:, last])])
    bm = means(2, 3)
    outer = means(0, 1)
    xy = np.column_stack((bounds[:, 2], bm))
    centered = xy - xy.mean(axis=0)
    covariance = np.cov(xy, rowvar=False, ddof=1)
    if np.linalg.matrix_rank(covariance) != 2:
        raise ValueError("骨髓起始层与信号的协方差不可逆；不能用任意正则化参数代替。")
    md = np.einsum("ij,ji->i", centered, np.linalg.solve(covariance, centered.T))
    outer_sd = float(outer.std(ddof=1))
    fraction = float(np.mean(md > MD_CUTOFF))
    reasons = qc_reasons(len(data), outer_sd, fraction)
    return {
        "bma_intensity_score": float(bm.mean()),
        "outer_table_intensity_score": float(outer.mean()),
        "outer_table_sd_score": outer_sd,
        "calvarial_vertices": len(data),
        "md_outlier_fraction": fraction,
        "qc_status": "fail" if reasons else "pass",
    }, bm, outer, md, reasons


def problem(message, kind="format", key="layer_intensity_score"):
    return skillkit.Problem(key, "个人 MRI 强度矩阵", kind, message)


def stop(out, problems):
    skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    report = out / "report.md"
    report.write_text("\n".join(paper_card_lines()) + "\n\n" + report.read_text(), encoding="utf-8")
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--layers", type=Path, help="作者流程提取的分号分隔、无表头的 50 层强度矩阵")
    parser.add_argument("--intensity-unit", default="score")
    parser.add_argument("--layer-spacing-mm", default=str(LAYER_SPACING_MM))
    parser.add_argument("--age")
    parser.add_argument("--sex", help="male/female；仅记录背景")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    # A failed rerun must not leave an old successful readout behind.
    for name in ("result.json", "problems.json", "vertices.csv", "qc.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    problems = []
    for key, raw in (("age", args.age), ("layer_spacing_mm", args.layer_spacing_mm)):
        try:
            value = float(raw) if raw is not None else None
            problems += skillkit.check_scalar(manifest, key, value)
            if key == "layer_spacing_mm" and value != LAYER_SPACING_MM:
                problems.append(problem("需要按作者流程以 0.5 mm 间距提取的 50 层；不重采样、不猜测。", key=key))
        except ValueError:
            problems.append(problem(f"{key} 不是可读取的数值。", key=key))
    if args.sex is not None and args.sex not in ("male", "female"):
        problems.append(problem("性别参数接受 male 或 female；可不填。", key="sex"))
    if args.layers is None:
        problems.append(problem("缺少 --layers：需要个人 MRI 经作者预处理后导出的 50 层强度矩阵，影像文字报告不能替代。", "missing"))
    if problems:
        return stop(args.out, problems)
    try:
        data = orient(np.loadtxt(args.layers, delimiter=";", ndmin=2))
        if data.size == 0 or not np.isfinite(data).all():
            raise ValueError("强度矩阵为空或含缺失值、NaN、无穷值，不能填补。")
        # Skillkit validates units and range for extrema of the entire matrix.
        # For finite values, this checks every element's membership in range.
        spec = dict(next(x for x in manifest["inputs"] if x["key"] == "layer_intensity_score"))
        spec["from"] = "measurements"
        for value in (data.min(), data.max()):
            check = skillkit.collect_measurements(
                [{"marker": spec["key"], "value": str(value), "unit": args.intensity_unit}],
                {"inputs": [spec]})
            problems += check.problems
        if problems:
            return stop(args.out, problems)
        # No alternative intensity scale is accepted: no scan-wise min/max fit.
        indices = np.flatnonzero(data.sum(axis=1) > VERTEX_SUM_CUTOFF)
        data = data[indices]
        if len(data) < MIN_VERTICES:
            return stop(args.out, [problem(qc_reasons(len(data), 0, 0)[0], "quality")])
        bounds = predict_bounds(data)
        outputs, bm, outer, md, reasons = summarize(data, bounds)
        (args.out / "qc.json").write_text(json.dumps({
            "calvarial_vertices": len(data), "outer_table_sd_score": outputs["outer_table_sd_score"],
            "md_outlier_fraction": outputs["md_outlier_fraction"], "reasons_zh": reasons,
        }, ensure_ascii=False, indent=2) + "\n")
        if reasons:
            return stop(args.out, [problem(x, "quality") for x in reasons])
    except (OSError, ValueError) as exc:
        return stop(args.out, [problem(str(exc))])
    except (ImportError, RuntimeError) as exc:
        # Environment/model failures are not missing patient measurements.
        (args.out / "report.md").write_text("\n".join(paper_card_lines() + [
            "", f"# {TITLE}", "", f"运行环境未就绪：{exc}", "", f"边界：{BOUNDARY}"]) + "\n")
        return 2
    np.savetxt(args.out / "vertices.csv", np.column_stack((indices + 1, bounds, bm, outer, md)),
               delimiter=",", comments="", fmt="%.9g",
               header="vertex,ob_first,ob_last,bm_first,bm_last,ib_first,ib_last,bm_mean,ob_mean,md_squared")
    skillkit.write_result(args.out, manifest, outputs)
    lines = paper_card_lines() + ["", f"# {TITLE}", "", "验证状态：仍在验证，未复现论文印出的个人算例。", "",
        f"骨髓信号代理指标：**{outputs['bma_intensity_score']:.3f}**（作者归一化信号尺度，0–255）。",
        f"通过质控的扫描包含 {len(data)} 个颅顶部位点；外板信号均值为 {outputs['outer_table_intensity_score']:.3f}。",
        f"外板信号标准差为 {outputs['outer_table_sd_score']:.3f}；马氏距离平方超限位点占 {outputs['md_outlier_fraction']:.3%}。",
        "", "数值是对定位到的骨髓层求均值后，再对所有可用颅顶部位点求均值。没有换算为脂肪百分比，也没有同龄人排名或正常/异常分档。",
        "扫描仪、采集序列与预处理会影响信号；跨扫描的差值不能直接解释为脂肪变化。", "",
        "本次从提取后的强度矩阵开始，未执行原始影像分割；数学质控不能替代对提取区域和定位边界的影像核对。",
        "年龄、性别仅作为背景记录，不改变此信号指标。"]
    if args.age is not None:
        lines += [f"年龄：{args.age} 岁。"]
    if args.sex is not None:
        lines += ["性别：" + {"male": "男", "female": "女"}[args.sex] + "。"]
    lines += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
