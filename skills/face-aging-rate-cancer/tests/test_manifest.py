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

from presets import far_value


def test_three_numbers_make_the_rate_and_a_gap_does_not(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nface_age_1,60,a\nface_age_2,62,a\ninterval_days,400,d\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, None, None, None).read_text(encoding="utf-8")
    rate = far_value(60, 62, 400)
    assert f"{rate:.4f}" in text
    gap = tmp_path / "gap.csv"
    gap.write_text("marker,value,unit\nface_age_1,60,a\nface_age_2,62,a\n", encoding="utf-8")
    missing = personal_report.report(tmp_path / "gap", gap, None, None, None).read_text(encoding="utf-8")
    assert "没有老化速率" in missing
    assert f"{rate:.4f}" not in missing
