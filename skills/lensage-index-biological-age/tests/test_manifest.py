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


def test_harness_row_uses_profile_age_when_the_file_has_no_chronological_age(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nlens_age,62,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 55).read_text(encoding="utf-8")
    assert "7.00" in text
    bare = personal_report.report(tmp_path / "bare", None, None, None, 55).read_text(encoding="utf-8")
    assert "没有算出指数" in bare
    assert "7.00" not in bare
