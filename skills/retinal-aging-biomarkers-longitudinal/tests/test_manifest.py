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

import argparse


def test_file_supplies_retinal_age(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("marker,value,unit\nretinal_age,66.8,a\n", encoding="utf-8")
    ns = argparse.Namespace(
        medications=None, labs=None, out=tmp_path / "out", retinal_age=None, age=59, probs=None, measurements=meas,
    )
    text = personal_report.report(ns).read_text(encoding="utf-8")
    assert "7.8" in text
    empty = argparse.Namespace(
        medications=None, labs=None, out=tmp_path / "empty", retinal_age=None, age=59, probs=None, measurements=None,
    )
    blank = personal_report.report(empty).read_text(encoding="utf-8")
    assert "没有算出年龄差" in blank
    assert "7.8" not in blank
