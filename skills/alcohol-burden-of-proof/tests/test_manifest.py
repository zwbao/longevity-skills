"""Printed expected values: Dai et al., Nature Health 2026, Table 3, p. 984.

These tests were written before the implementation. The source table has
10 g/day columns; expectations are transcribed cells, not fitted predictions.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report
import presets


def run(tmp_path, value="10", unit="g/d", marker="每日纯酒精摄入量", targets=None):
    source = tmp_path / "input.csv"
    source.write_text(f"marker,value,unit\n{marker},{value},{unit}\n", encoding="utf-8")
    out = tmp_path / "out"
    args = ["--measurements", str(source), "--out", str(out)]
    if targets is not None:
        target = tmp_path / "targets.csv"
        target.write_text(f"marker,value,unit\nalcohol_g_day,{targets},g/d\n")
        args += ["--targets", str(target)]
    code = personal_report.main(args)
    result = json.loads((out / "result.json").read_text())
    return code, {k: v["value"] for k, v in result["outputs"].items()}, out


def test_table3_printed_examples(tmp_path):
    # Table 3: 1 standard drink = 10 g/day, cells quoted in skill.json.
    code, result, out = run(tmp_path)
    assert code == 0
    assert result["lower_exposure_g_day"] == result["upper_exposure_g_day"] == 10
    for side in ("lower", "upper"):
        assert result[f"breast_cancer_{side}_rr"] == 1.13
        assert result[f"breast_cancer_{side}_ui_low"] == 1.08
        assert result[f"breast_cancer_{side}_ui_high"] == 1.19
        assert result[f"ischaemic_heart_disease_{side}_rr"] == 0.92
        assert result[f"ischaemic_heart_disease_{side}_ui_low"] == 0.81
        assert result[f"ischaemic_heart_disease_{side}_ui_high"] == 1.05
        assert result[f"type_2_diabetes_{side}_rr"] == 0.84
        assert result[f"type_2_diabetes_{side}_ui_low"] == 0.73
        assert result[f"type_2_diabetes_{side}_ui_high"] == 0.97
    report = (out / "report.md").read_text()
    assert report.index("10.1038/s44360-026-00139-5") < report.index("## 你的输入")
    assert "边界:" in report and "不能据此开始饮酒" in report
    assert "研究间异质性" in report and "女性" in report and "男性" in report


def test_table3_all_outcomes_at_10_and_100():
    # All 20 rows in Table 3, columns 1 and 10. RR, 95% UI lower, upper.
    printed = [
        ("breast_cancer", (1.13, 1.08, 1.19), (1.49, 1.29, 1.73)),
        ("colorectal_cancer", (1.17, 1.1, 1.24), (1.57, 1.33, 1.87)),
        ("oesophageal_cancer", (1.32, 1.0, 1.75), (5.11, 0.99, 26.27)),
        ("laryngeal_cancer", (1.23, 1.09, 1.4), (3.64, 1.66, 7.99)),
        ("lip_oral_cavity_cancer", (1.03, 1.01, 1.05), (3.68, 1.57, 8.62)),
        ("liver_cancer", (1.02, 1.0, 1.04), (2.64, 0.94, 7.38)),
        ("pancreatic_cancer", (1.05, 1.01, 1.1), (1.21, 1.04, 1.41)),
        ("other_pharyngeal_cancer", (1.16, 1.13, 1.18), (4.75, 3.66, 6.17)),
        ("prostate_cancer", (1.04, 1.0, 1.09), (1.19, 1.0, 1.41)),
        ("stomach_cancer", (1.03, 0.99, 1.06), (1.22, 0.96, 1.54)),
        ("atrial_fibrillation_flutter", (1.02, 1.01, 1.04), (1.6, 1.27, 2.01)),
        ("ischaemic_heart_disease", (0.92, 0.81, 1.05), (1.01, 0.99, 1.04)),
        ("ischaemic_stroke", (0.87, 0.72, 1.04), (1.55, 0.88, 2.73)),
        ("haemorrhagic_stroke", (0.92, 0.83, 1.02), (1.62, 0.89, 2.97)),
        ("alzheimers_other_dementias", (0.89, 0.83, 0.95), (1.40, 1.16, 1.69)),
        ("cirrhosis_chronic_liver_diseases", (1.12, 1.05, 1.19), (6.56, 2.26, 19.05)),
        ("type_2_diabetes", (0.84, 0.73, 0.97), (1.26, 1.04, 1.52)),
        ("lower_respiratory_infections", (1.00, 1.0, 1), (2.61, 1.1, 6.18)),
        ("pancreatitis", (1.01, 1.0, 1.01), (6.02, 2.32, 15.64)),
        ("tuberculosis", (1.07, 0.98, 1.17), (6.67, 0.64, 69.3)),
    ]
    for amount, index in ((10, 1), (100, 2)):
        result = personal_report.lookup(amount)
        for row in printed:
            for side in ("lower", "upper"):
                actual = tuple(result[f"{row[0]}_{side}_{part}"] for part in ("rr", "ui_low", "ui_high"))
                assert actual == row[index]


def test_table3_40g_and_targets(tmp_path):
    # Table 3, column 4: Other pharyngeal cancer 2.73 (2.3, 3.23).
    code, result, out = run(tmp_path, "40", targets="10")
    assert code == 0
    assert result["other_pharyngeal_cancer_lower_rr"] == 2.73
    assert result["other_pharyngeal_cancer_lower_ui_low"] == 2.3
    assert result["other_pharyngeal_cancer_lower_ui_high"] == 3.23
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["other_pharyngeal_cancer_lower_rr"] == 2.73
    assert levers["targets"]["other_pharyngeal_cancer_lower_rr"] == 1.16
    assert levers["levers"][0]["rr_delta"]["other_pharyngeal_cancer"] == pytest.approx(1.16 - 2.73)
    assert levers["sensitivity"][0]["derivative"] is None


def test_between_nodes_is_not_interpolated(tmp_path):
    code, result, out = run(tmp_path, "25", targets="15")
    assert code == 0
    assert (result["lower_exposure_g_day"], result["upper_exposure_g_day"]) == (20, 30)
    # Table 3: Type 2 diabetes columns 2/3 are 0.8 and 0.87.
    assert result["type_2_diabetes_lower_rr"] == 0.8
    assert result["type_2_diabetes_upper_rr"] == 0.87
    assert result["lookup_mode"] == "bracket"
    levers = json.loads((out / "levers.json").read_text())
    assert levers["levers"][0]["rr_delta"] is None
    assert "不是该摄入量风险的上下限" in (out / "report.md").read_text()


def test_reference_is_not_zero_disease_risk(tmp_path):
    code, result, out = run(tmp_path, "0")
    assert code == 0 and result["lookup_mode"] == "reference"
    assert result["breast_cancer_lower_rr"] == 1
    assert result["breast_cancer_lower_ui_low"] is None
    assert "不表示疾病风险为零" in (out / "report.md").read_text()
    below = personal_report.lookup(5)
    assert (below["lower_exposure_g_day"], below["upper_exposure_g_day"]) == (0, 10)


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = manifest["inputs"][0]
    assert (spec["key"], spec["label_zh"], spec["unit"]) == presets.ALCOHOL_INPUT
    assert spec["range"] == [presets.MIN_EXPOSURE, presets.MAX_EXPOSURE]
    assert set(personal_report.lookup(10)) == {x["key"] for x in manifest["outputs"]}
    assert manifest["inputs_status"] == "verified"


@pytest.mark.parametrize("value,unit,marker", [
    ("10", "mL/d", "每日纯酒精摄入量"),
    ("10", "g/week", "每日纯酒精摄入量"),
    ("10", "", "每日纯酒精摄入量"),
    ("101", "g/d", "alcohol_g_day"),
    ("-1", "g/d", "alcohol_g_day"),
    ("NaN", "g/d", "alcohol_g_day"),
    ("abc", "g/d", "alcohol_g_day"),
    ("10", "g/d", "unknown"),
])
def test_bad_inputs_exit3_without_results(tmp_path, value, unit, marker):
    # Reuse a previously successful output directory: stale results must vanish.
    run(tmp_path)
    code, result, out = run(tmp_path, value, unit, marker)
    assert code == 3 and all(v is None for v in result.values())
    assert (out / "problems.json").exists()
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "这次没有计算" in report and "| 乳腺癌" not in report
    assert report.index("10.1038/s44360-026-00139-5") < report.index("输入没有通过")


def test_invalid_targets_and_missing_file(tmp_path):
    code, result, out = run(tmp_path, targets="500")
    assert code == 3 and all(v is None for v in result.values())
    process = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--measurements", str(tmp_path / "absent.csv"), "--out", str(out)], capture_output=True)
    assert process.returncode == 3
    assert (out / "problems.json").exists()
