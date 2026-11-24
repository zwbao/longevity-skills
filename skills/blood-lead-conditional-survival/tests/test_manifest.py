"""Printed v2 Table 2/S3 coefficients and Results doubling example, not refitted data."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report
import presets
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def test_printed_lead_doubling():
    # Results / Primary analysis prints 1.57 -> 3.14 µg/dL.
    # Table 2 and appendix p9 S3 print these per-doubling values (I1..I5).
    result = personal_report.contrast(3.14, 1.57)
    printed = {
        10: [-0.671, -0.685, -0.679, -0.706, -0.625],
        25: [-0.555, -0.607, -0.587, -0.650, -0.612],
        50: [None, -0.613, -0.626, None, -0.620],
    }
    for quantile, values in printed.items():
        for i, expected in enumerate(values, 1):
            actual = result[f"q{quantile}_i{i}_years"]
            if expected is None:
                assert actual is None
            else:
                assert actual == pytest.approx(expected, abs=1e-12)


def test_printed_results_ranges():
    # Independent prose summary in Results, rounded to two decimals.
    result = personal_report.contrast(3.14, 1.57)
    for q, expected in [(10, (0.63, 0.71)), (25, (0.55, 0.65)), (50, (0.61, 0.63))]:
        losses = [-v for k, v in result.items() if k.startswith(f"q{q}_") and v is not None]
        assert (min(losses), max(losses)) == pytest.approx(expected, abs=0.006)


def run(tmp_path, rows, age="55", targets=None):
    path = tmp_path / "labs.csv"
    path.write_text("marker,value,unit\n" + "\n".join(rows) + "\n")
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        target_file = tmp_path / "targets.csv"
        target_file.write_text("marker,value,unit\n" + "\n".join(targets) + "\n")
        args += ["--targets", str(target_file)]
    result = subprocess.run(args, text=True, capture_output=True)
    return result, out


VALID = ["血铅,3.14,ug/dL", "参考血铅,1.57,ug/dL"]


def test_manifest_and_normal_result(tmp_path):
    inputs = {s["key"]: s for s in MANIFEST["inputs"] if s["from"] == "measurements"}
    assert set(inputs) == set(presets.MEASUREMENTS)
    for key, unit in presets.MEASUREMENTS.items():
        assert skillkit.normalize_unit(inputs[key]["unit"]) == skillkit.normalize_unit(unit)
    result, out = run(tmp_path, VALID)
    assert result.returncode == 0, result.stderr
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["q10_i1_years"]["value"] == pytest.approx(-0.671)
    assert values["q50_i1_years"]["value"] is None
    assert set(values) == {o["key"] for o in MANIFEST["outputs"]}
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("## 输入")
    assert "预印本，未经同行评审" in report
    assert "镉调整后" in report and "不可估计" in report
    assert presets.BOUNDARY in report
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("rows,age", [
    (["血铅,3.14,mmol/L", VALID[1]], "55"),
    (["血铅,301,ug/dL", VALID[1]], "55"),
    (["血铅,0,ug/dL", VALID[1]], "55"),
    (["血铅,nan,ug/dL", VALID[1]], "55"),
    (["血铅,<0.2,ug/dL", VALID[1]], "55"),
    (["血铅,3.14,", VALID[1]], "55"),
    ([VALID[0]], "55"),
    ([], "55"), (VALID, None), (VALID, "39"), (VALID, "bad"),
])
def test_invalid_inputs_exit_three(tmp_path, rows, age):
    result, out = run(tmp_path, rows, age)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert all(x["value"] is None for x in values.values())
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and presets.BOUNDARY in report
    assert "−0.671" not in report


def test_units_and_targets(tmp_path):
    result, out = run(tmp_path, ["Whole blood lead,31.4,μg/L", "参考血铅,15.7,ng/mL"],
                      targets=["血铅,15.7,ug/L"])
    assert result.returncode == 0, result.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["q10_i1_years"] == pytest.approx(-0.671)
    assert levers["targets"]["outputs"]["q10_i1_years"] == 0
    assert levers["levers"][0]["delta"]["q10_i1_years"] == pytest.approx(0.671)
    assert levers["targets"]["outputs"]["q50_i1_years"] is None
    assert levers["sensitivity"][0]["years_per_unit"]["q10_i1_years"] < 0


@pytest.mark.parametrize("targets", [["血铅,2,mmol/L"], ["参考血铅,1,ug/dL"], [], ["尿铅,1,ug/dL"]])
def test_invalid_targets_do_not_publish_results(tmp_path, targets):
    result, out = run(tmp_path, VALID, targets=targets)
    assert result.returncode == 3
    assert not (out / "levers.json").exists()
    assert all(v["value"] is None for v in json.loads((out / "result.json").read_text())["outputs"].values())


def test_reversal_and_reused_output_directory(tmp_path):
    forward = personal_report.contrast(3.14, 1.57)
    reverse = personal_report.contrast(1.57, 3.14)
    for key, value in forward.items():
        assert reverse[key] is None if value is None else reverse[key] == pytest.approx(-value)
    ok, out = run(tmp_path, VALID)
    assert ok.returncode == 0 and (out / "levers.json").exists()
    bad, out = run(tmp_path, [VALID[0]])
    assert bad.returncode == 3 and not (out / "levers.json").exists()
    ok, out = run(tmp_path, VALID)
    assert ok.returncode == 0 and not (out / "problems.json").exists()
