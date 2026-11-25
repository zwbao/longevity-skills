"""skill.json inputs match presets; wrong units and wrong scales stop the computation.

The paper prints no person's 38 NPX values with a score, so no test here
asserts a printed SASP Score (validation is draft). The constants checked
below are the ones the paper does print (protein list, cutoff 65).
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pytest.importorskip("numpy")

import personal_report  # noqa: E402
import skillkit  # noqa: E402
from presets import CUTOFF, KEYS, PROTEINS, UKB_MEAN_SD  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

# Methods 2.3 prints the panel (SERPINE1 as "SERPIN1").
PAPER_PANEL = (
    "ANG, CCL2, CCL3, CCL4, CCL13, CCL20, CHI3L1, CSF2, CXCL1, CXCL8, CXCL9, CXCL10, FGA, FGF2, FSTL3, GDF15, "
    "HGF, ICAM1, IGFBP2, IGFBP6, IL1B, IL4, IL5, IL6, IL6ST, LEP, MIF, MMP12, PGF, PLAUR, SERPIN1, TF, TIMP1, "
    "TNFRSF1A, TNFRSF1B, TNFRSF11B, TNFSF10, VEGFA"
)


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["marker,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    return path


def _rows(z: float = 0.0, unit: str = "NPX"):
    return [(name, f"{UKB_MEAN_SD[name][0] + z * UKB_MEAN_SD[name][1]:.6f}", unit) for name in PROTEINS]


def _run(tmp_path: Path, rows):
    out = tmp_path / "out"
    try:
        personal_report.write_report(out, _csv(tmp_path / "p.csv", rows))
        return 0, out
    except SystemExit as exc:
        return exc.code, out


def test_panel_matches_paper_methods():
    printed = {name.strip().replace("SERPIN1", "SERPINE1") for name in PAPER_PANEL.split(",")}
    assert printed == set(PROTEINS)
    assert len(PROTEINS) == 38


def test_paper_cutoff_is_65():
    assert CUTOFF == 65


def test_manifest_inputs_match_presets():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == [KEYS[name] for name in PROTEINS]
    for item in MANIFEST["inputs"]:
        assert item["required"] and item["from"] == "measurements" and item["unit_required"]
        assert item["range"] == [-10, 15]
    assert {o["key"] for o in MANIFEST["outputs"]} == {"sasp_score", "sasp_group", "proteins_far_from_ukb"}
    assert MANIFEST["validation"]["status"] == "draft"


def test_frozen_weights_hash():
    item = MANIFEST["data_files"][0]
    digest = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
    assert digest == item["sha256"]


def test_normal_input_writes_result(tmp_path: Path):
    code, out = _run(tmp_path, _rows())
    assert code == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert set(result) == {"sasp_score", "sasp_group", "proteins_far_from_ukb"}
    assert result["sasp_group"]["value"] == ("high" if result["sasp_score"]["value"] > 65 else "low")
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.index("## 论文卡片") < text.index("## 你的结果")
    assert "10.1111/acel.70737" in text
    assert "边界:" in text and "不能据此开始或停止" in text


def test_aliases_with_npx_unit_are_read(tmp_path: Path):
    rows = _rows()
    rows[15] = ("GDF-15", rows[15][1], "NPX")
    rows[30] = ("PAI-1", rows[30][1], "npx")
    code, _ = _run(tmp_path, rows)
    assert code == 0


def test_concentration_unit_stops(tmp_path: Path):
    rows = _rows()
    rows[23] = ("IL-6", "3.2", "pg/mL")
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "il6_npx" and p["kind"] == "unit" for p in problems)
    assert not (out / "result.json").exists()


def test_missing_unit_on_alias_stops(tmp_path: Path):
    rows = _rows()
    rows[0] = ("Angiogenin", rows[0][1], "")
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "ang_npx" and p["kind"] == "unit_missing" for p in problems)


def test_key_named_rows_need_no_unit(tmp_path: Path):
    rows = [(KEYS[name], value, "") for name, value, _ in _rows()]
    code, _ = _run(tmp_path, rows)
    assert code == 0


def test_out_of_range_value_stops(tmp_path: Path):
    rows = _rows()
    rows[5] = ("CCL4", "250", "NPX")
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "SASP 评分：" not in report


def test_missing_protein_stops(tmp_path: Path):
    code, out = _run(tmp_path, _rows()[:-1])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["key"] for p in problems] == ["vegfa_npx"]


def test_other_platform_scale_stops(tmp_path: Path):
    # Olink Target 96 style NPX: every protein around 5-8, far from the UKB-PPP centring.
    rows = [(name, "6.5", "NPX") for name in PROTEINS]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "scale"
    assert not (out / "result.json").exists()
