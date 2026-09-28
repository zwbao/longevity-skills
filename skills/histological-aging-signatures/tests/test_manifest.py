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


def test_one_tissue_and_profile_age(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nliver,55,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 60).read_text(encoding="utf-8")
    assert "肝" in text and "-5.0" in text
    missing = personal_report.report(tmp_path / "bare", None, None, None, 60).read_text(encoding="utf-8")
    assert "没有算出年龄差" in missing
    assert "-5.0" not in missing
