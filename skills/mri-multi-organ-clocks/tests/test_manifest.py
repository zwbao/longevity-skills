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


def test_one_printed_organ_age(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nbrain,36.4,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 32).read_text(encoding="utf-8")
    assert "脑的预测年龄减去实足年龄是 4.4 年" in text
    missing = personal_report.report(tmp_path / "bare", None, None, None, 32).read_text(encoding="utf-8")
    assert "没有算出年龄差" in missing
    assert "4.4" not in missing
