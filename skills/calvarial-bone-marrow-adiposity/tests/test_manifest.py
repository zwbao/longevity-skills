"""Engineering checks only: the paper publishes no complete individual example.

Synthetic inputs must not be presented as a reproduced paper example. Expected
predictions come from the released checkpoint, evaluated independently here;
summary expectations follow the inclusive R indexing in the upstream script.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets


def synthetic_scan():
    # Frozen artificial profiles, never a claimed patient/paper reproduction.
    profiles = np.loadtxt(ROOT / "tests/data/synthetic_profiles.csv", delimiter=";")
    return np.tile(profiles, (313, 1))


def upstream_bounds(data):
    import tensorflow as tf
    reader = tf.train.load_checkpoint(str(ROOT / "data/model/variables/variables"))
    x = np.pad(data.astype(np.float32) / 255, ((0, 0), (0, 100)))
    for i in range(4):
        prefix = f"layer_with_weights-{i}/"
        x = x @ reader.get_tensor(prefix + "kernel/.ATTRIBUTES/VARIABLE_VALUE")
        x += reader.get_tensor(prefix + "bias/.ATTRIBUTES/VARIABLE_VALUE")
        if i < 3:
            x = np.maximum(x, 0)
    return np.rint(np.clip(x * 50, 1, 50)).astype(int)


def run_cli(tmp_path, data=None, extra=()):
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--out", str(tmp_path / "out")]
    if data is not None:
        path = tmp_path / "layers.csv"
        np.savetxt(path, data, delimiter=";", fmt="%.9g")
        args += ["--layers", str(path)]
    return subprocess.run(args + list(extra), capture_output=True, text=True,
                          env={**os.environ, "TF_CPP_MIN_LOG_LEVEL": "3"})


def test_manifest_and_published_constants():
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = next(s for s in manifest["inputs"] if s["key"] == "layer_intensity_score")
    assert spec["range"] == [0, presets.MAX_INTENSITY]
    assert spec["unit"] == "score"
    assert manifest["validation"]["status"] == "draft"
    # Methods: ANN quality control measures; upstream computeAuxiliaryFiles.r.
    assert presets.N_LAYERS == 50
    assert presets.MAX_INTENSITY == 255
    assert presets.MIN_VERTICES == 5000
    assert presets.MAX_OUTER_SD == 30
    assert presets.MD_CUTOFF == 25
    assert presets.MAX_OUTLIER_FRACTION == 0.005


@pytest.mark.parametrize("data,extra", [
    (None, ()),
    (np.ones((2, 50)), ("--intensity-unit", "mg/dL")),
    (np.full((2, 50), 256), ()),
    (np.full((2, 50), np.nan), ()),
    (np.ones((2, 49)), ()),
    (np.ones((2, 50)), ("--layer-spacing-mm", "1")),
    (np.ones((2, 50)), ("--age", "not-a-number")),
])
def test_invalid_input_returns_three_without_result(tmp_path, data, extra):
    result = run_cli(tmp_path, data, extra)
    assert result.returncode == 3, result.stderr
    assert (tmp_path / "out/problems.json").exists()
    assert not (tmp_path / "out/result.json").exists()
    text = (tmp_path / "out/report.md").read_text()
    assert text.startswith("## 论文卡片")
    assert "边界" in text


def test_inference_and_report_agree_with_released_weights(tmp_path):
    data = synthetic_scan()
    expected_bounds = upstream_bounds(data)
    np.testing.assert_array_equal(report.predict_bounds(data), expected_bounds)
    # R's a:b includes both endpoints, including descending intervals.
    expected = np.array([np.mean(row[min(b[2], b[3])-1:max(b[2], b[3])])
                         for row, b in zip(data, expected_bounds)])
    # Include masked non-calvarial vertices and the author's 50 x N orientation.
    result = run_cli(tmp_path, np.vstack((np.zeros((2, 50)), data)).T)
    assert result.returncode == 0, result.stderr + result.stdout
    outputs = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert outputs["bma_intensity_score"]["value"] == pytest.approx(expected.mean(), abs=1e-6)
    assert outputs["qc_status"]["value"] == "pass"
    vertices = np.loadtxt(tmp_path / "out/vertices.csv", delimiter=",", skiprows=1)
    np.testing.assert_array_equal(vertices[:, 0], np.arange(3, len(data) + 3))
    # Independent scalar expression of the 2D sample Mahalanobis quadratic form.
    a = expected_bounds[:, 2] - expected_bounds[:, 2].mean()
    b = expected - expected.mean()
    aa, ab, bb = (np.dot(a, a)/(len(a)-1), np.dot(a, b)/(len(a)-1),
                  np.dot(b, b)/(len(a)-1))
    expected_md = (bb*a*a - 2*ab*a*b + aa*b*b)/(aa*bb - ab*ab)
    np.testing.assert_allclose(vertices[:, -1], expected_md, atol=1e-6)
    assert "脂肪百分比" in (tmp_path / "out/report.md").read_text()


def test_qc_failure_and_stale_result_cleanup(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "result.json").write_text('{"stale": true}')
    result = run_cli(tmp_path, synthetic_scan()[:10])
    assert result.returncode == 3
    assert not (out / "result.json").exists()


def test_orientation_and_qc_boundaries():
    data = synthetic_scan()
    np.testing.assert_array_equal(report.orient(data.T), data)
    # The printed inequalities are strict: less than 5000, above 30,
    # more than 0.5% of vertices with MD >25.
    assert report.qc_reasons(5000, 30, 0.005) == []
    assert report.qc_reasons(4999, 30, 0.005)
    assert report.qc_reasons(5000, 30.01, 0.005)
    assert report.qc_reasons(5000, 30, 0.0051)


def test_singular_covariance_is_not_silently_regularized():
    data = np.tile(synthetic_scan()[0], (5000, 1))
    bounds = np.tile(upstream_bounds(data[:1]), (5000, 1))
    with pytest.raises(ValueError, match="协方差"):
        report.summarize(data, bounds)
