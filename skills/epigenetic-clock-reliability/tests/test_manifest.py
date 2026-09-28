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


def test_replicate_pair_from_harness_keys(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nPhenoAge_a,80,a\nPhenoAge_b,70,a\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "表型年龄" in text
    assert "绝对差是 10 年" in text
    half = tmp_path / "half.csv"
    half.write_text("marker,value,unit\nPhenoAge_a,80,a\n", encoding="utf-8")
    missing = personal_report.report(tmp_path / "half", None, None, half).read_text(encoding="utf-8")
    assert "没有算出两次之差" in missing
    assert "绝对差是 10" not in missing
