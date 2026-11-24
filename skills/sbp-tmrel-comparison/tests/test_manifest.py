"""Printed constants, not a printed personal example: validation remains draft.

Appendix 1, Table S9, p 513:
High systolic blood pressure | 110–115 mmHg | 105–115 mmHg
Columns: Risk Name | 2019 TMREL range | 2021 TMREL range.
Synthetic boundary/property cases below test software only.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets
import personal_report as pr

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def run(tmp_path, rows, out=None):
    src = tmp_path / "measurements.csv"
    src.write_text("item,value,unit\n" + rows, encoding="utf-8")
    out = out or tmp_path / "out"
    done = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--measurements", str(src), "--out", str(out)], capture_output=True, text=True)
    result = json.loads((out / "result.json").read_text())["outputs"]
    return done.returncode, result, (out / "report.md").read_text(), out


def test_table_s9_constants():
    # Transcription check only; no invented worked example.
    assert presets.TMREL_MMHG == (105, 115)


def test_manifest_matches_presets():
    spec = MANIFEST["inputs"][0]
    assert spec["key"] == presets.SBP_KEY
    assert spec["unit"] == presets.SBP_UNIT
    assert spec["range"] == list(presets.SBP_RANGE)
    assert MANIFEST["validation"]["status"] == "draft"


@pytest.mark.parametrize("sbp", [105, 115])
def test_report_at_printed_endpoints(tmp_path, sbp):
    code, result, report, _ = run(tmp_path, f"收缩压,{sbp},mmHg\n")
    assert code == 0
    assert result["sbp_mmhg"]["value"] == sbp
    assert result["tmrel_lower_mmhg"]["value"] == 105
    assert result["tmrel_upper_mmhg"]["value"] == 115
    assert result["position"]["value"] == "within"
    assert report.index("论文卡片") < report.index("## 个人结果")
    assert "边界:" in report and "不是降压治疗目标" in report


@pytest.mark.parametrize("sbp,position", [(104, "below"), (110, "within"), (116, "above")])
def test_synthetic_arithmetic_invariants(sbp, position):
    r = pr.compare(sbp)
    assert r["position"] == position
    assert r["difference_from_lower_mmhg"] + r["tmrel_lower_mmhg"] == sbp
    assert r["difference_from_upper_mmhg"] + r["tmrel_upper_mmhg"] == sbp


@pytest.mark.parametrize("rows", ["", "SBP,115,mg/dL\n", "SBP,1000,mmHg\n",
                                  "SBP,nan,mmHg\n", "SBP,115,\n", "SBP,abc,mmHg\n",
                                  "SBP,105,mmHg\nSBP,115,mmHg\n"])
def test_invalid_input_stops_without_personal_numbers(tmp_path, rows):
    code, result, report, out = run(tmp_path, rows)
    assert code == 3
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v["value"] is None for v in result.values())
    assert "## 个人结果" not in report
    assert "论文卡片" in report and "边界:" in report


def test_kpa_conversion(tmp_path):
    # Software equivalence using the repository's declared unit factor, not paper validation.
    code, a, _, _ = run(tmp_path, "SBP,15,kPa\n")
    code2, b, _, _ = run(tmp_path, f"SBP,{15 * 7.500617},mmHg\n")
    assert code == code2 == 0
    assert a == b


def test_reused_output_has_no_stale_results(tmp_path):
    _, _, _, out = run(tmp_path, "SBP,115,mmHg\n")
    code, result, _, _ = run(tmp_path, "", out)
    assert code == 3 and all(v["value"] is None for v in result.values())
    code, _, _, _ = run(tmp_path, "SBP,105,mmHg\n", out)
    assert code == 0 and not (out / "problems.json").exists()
