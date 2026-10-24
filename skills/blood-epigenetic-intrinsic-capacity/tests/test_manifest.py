"""skill.json inputs match the 91 sites, the coefficients are Supplementary Table 1, bad input exits 3.

No printed per-person example exists (validation is draft), so these tests check
the manifest, the provenance of the constants and input handling, not a paper value.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import CPG_COEF, IC_INTERCEPT

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _table(path: Path, rows) -> Path:
    lines = ["item,value,unit"] + [",".join(str(cell) for cell in row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_table(tmp_path / "m.csv", rows)), "--out", str(out)])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, (out / "report.md").read_text(encoding="utf-8"), result, out


def test_manifest_keys_match_the_script():
    declared = {item["key"]: item for item in MANIFEST["inputs"]}
    assert list(declared) == list(CPG_COEF)
    for spec in declared.values():
        assert spec["from"] == "measurements" and spec["required"] is True
        assert skillkit.normalize_unit(spec["unit"]) == "1" and spec["range"] == [0, 1]
    assert [item["key"] for item in MANIFEST["outputs"]] == ["dnam_ic"]


def test_constants_are_supplementary_table_1():
    # Printed in Supplementary Table 1: "(Intercept) 0.7852837523517947", "cg06846752 -0.02306195434895264",
    # "cg13022624 -0.1964813653979209"; 91 CpGs.
    assert len(CPG_COEF) == 91
    assert IC_INTERCEPT == 0.7852837523517947
    assert CPG_COEF["cg06846752"] == -0.02306195434895264
    assert CPG_COEF["cg13022624"] == -0.1964813653979209


def test_linear_combination(tmp_path: Path):
    betas = {site: 0.5 for site in CPG_COEF}
    code, text, result, _ = _run(tmp_path, [(site, value, "") for site, value in betas.items()])
    assert code == 0
    expected = IC_INTERCEPT + 0.5 * sum(CPG_COEF.values())
    assert result["dnam_ic"]["value"] == pytest.approx(expected)
    assert f"{expected:.3f}" in text
    assert text.splitlines()[-1].startswith("边界: ")


def test_missing_site_exits_3(tmp_path: Path):
    rows = [(site, 0.5, "") for site in list(CPG_COEF)[1:]]
    code, text, result, out = _run(tmp_path, rows)
    assert code == 3
    assert (out / "problems.json").exists()
    assert result["dnam_ic"]["value"] is None
    assert list(CPG_COEF)[0] in text


def test_percent_unit_exits_3(tmp_path: Path):
    rows = [(site, 50, "%") for site in CPG_COEF]
    code, _text, result, _ = _run(tmp_path, rows)
    assert code == 3
    assert result["dnam_ic"]["value"] is None


def test_percent_number_without_unit_exits_3(tmp_path: Path):
    rows = [(site, 50, "") for site in CPG_COEF]
    code, _text, _result, _ = _run(tmp_path, rows)
    assert code == 3
