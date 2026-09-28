import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def test_inputs_are_verified():
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["inputs"]
    assert (ROOT / "scripts" / "skillkit.py").is_file()
    assert MANIFEST["entry"]["measurements_header"] == ["marker", "value", "unit"]


def test_week32_minus_baseline_stays_separate_from_the_group_estimate(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nphenoage_baseline,60,a\nphenoage_week32,55,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "PhenoAge 从基线到第 32 周的变化是 -5.0" in text
    assert "组间差别是 -4.9" in text
    half = tmp_path / "half.csv"
    half.write_text("marker,value,unit\nphenoage_baseline,60,a\n", encoding="utf-8")
    missing = personal_report.report(tmp_path / "half", None, None, half).read_text(encoding="utf-8")
    assert "没有算出变化" in missing
    assert "-5.0" not in missing
