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


def test_partial_organs_have_no_seven_organ_mean(tmp_path: Path):
    one = tmp_path / "one.csv"
    one.write_text("marker,value,unit\nbrain,36.4,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "one", 32, None, None, one).read_text(encoding="utf-8")
    assert "脑" in text and "4.4" in text
    assert "七个器官的年龄差平均" not in text
    rows = "\n".join(f"{key},{value},a" for key, value in [
        ("brain", 70), ("heart", 65), ("body", 60), ("kidney", 80), ("liver", 62), ("pancreas", 61), ("eye", 59),
    ])
    full = tmp_path / "full.csv"
    full.write_text("marker,value,unit\n" + rows + "\n", encoding="utf-8")
    whole = personal_report.report(tmp_path / "full", 50, None, None, full).read_text(encoding="utf-8")
    assert "15.2857" in whole
