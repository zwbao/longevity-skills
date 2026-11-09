"""skill.json inputs match presets, and wrong or missing inputs stop the run (exit 3)."""

import json
from pathlib import Path

import pytest

import personal_report
import skillkit
from conftest import ROOT, synthetic_subjects, write_rows
from presets import (
    BETA_AGE,
    BETA_AGE0,
    PAC_PROTEIN_COEFFICIENTS,
    PAC_PROTEINS,
    RATE,
    RATE0,
    SHAPE,
    SHAPE0,
    input_key,
)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _subject(name="syn_4"):
    return synthetic_subjects()[name]


def _run(tmp_path, rows, age, *extra):
    path = write_rows(tmp_path / "npx.csv", rows)
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(path), "--age", str(age), "--out", str(out), *extra])
    return code, out


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == [input_key(symbol) for symbol in PAC_PROTEINS]
    assert len(declared) == 128
    for item, symbol in zip(declared, PAC_PROTEINS):
        assert item["label_zh"] == symbol
        assert item["required"] is True
        assert skillkit.normalize_unit(item["unit"]) == "1"
    assert MANIFEST["inputs_status"] == "verified"
    assert {item["key"] for item in MANIFEST["outputs"]} == {
        "pac_age", "pac_age_gap", "pac_mortality_10y_pct", "baseline_pac_age", "pac_age_change"}
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert age["from"] == "profile" and age["flag"] == "--age"


def test_constants_are_the_released_pac_code():
    # pac_proteomic_age.R, kuo-lab-uchc/PAC commit e15edb6.
    assert SHAPE == 0.148766187078631
    assert RATE == 0.000231560557596016
    assert SHAPE0 == 0.1200806
    assert RATE0 == 0.000004885383
    assert BETA_AGE0 == 0.1087932
    assert BETA_AGE == 0.029353964
    coefs = dict(PAC_PROTEIN_COEFFICIENTS)
    assert coefs["ADA2"] == 0.099491261
    assert coefs["LTBP2"] == 0.457163801
    assert coefs["XG"] == -0.08933844


def test_normal_input_writes_result(tmp_path):
    age, rows = _subject()
    code, out = _run(tmp_path, rows, age)
    assert code == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["pac_age"]["value"] == pytest.approx(60.479266, abs=1e-5)
    assert result["pac_age_gap"]["value"] == pytest.approx(60.479266 - 67, abs=1e-5)
    assert 0 < result["pac_mortality_10y_pct"]["value"] < 100
    assert result["pac_age_change"]["value"] is None
    assert not (out / "problems.json").exists()


def test_npx_unit_words_and_extra_proteins_are_accepted(tmp_path):
    age, rows = _subject()
    rows = [(name, value, "log2 NPX") for name, value, _unit in rows]
    rows += [("CRP", "1.2", "NPX")]
    code, out = _run(tmp_path, rows, age)
    assert code == 0
    assert "另有 1 行不是 PAC 用的蛋白" in (out / "report.md").read_text(encoding="utf-8")


def test_concentration_unit_is_refused(tmp_path):
    age, rows = _subject()
    rows = [(n, "1500", "pg/mL") if n == "GDF15" else (n, v, u) for n, v, u in rows]
    code, out = _run(tmp_path, rows, age)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "gdf15_npx" and p["kind"] == "unit" for p in problems)
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "这次没有计算" in text and "蛋白质组年龄是" not in text
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["pac_age"]["value"] is None


def test_out_of_range_value_is_refused(tmp_path):
    age, rows = _subject()
    rows = [(n, "1500", "") if n == "NEFL" else (n, v, u) for n, v, u in rows]
    code, out = _run(tmp_path, rows, age)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["kind"] for p in problems if p["key"] == "nefl_npx"] == ["range"]
    assert "蛋白质组年龄是" not in (out / "report.md").read_text(encoding="utf-8")


def test_missing_protein_is_not_imputed(tmp_path):
    age, rows = _subject()
    rows = [row for row in rows if row[0] not in {"LTBP2", "FUT3-FUT5"}]
    code, out = _run(tmp_path, rows, age)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    missing = [p for p in problems if p["kind"] == "missing"]
    assert len(missing) == 1 and "2 个蛋白" in missing[0]["message_zh"]
    assert "LTBP2" in missing[0]["message_zh"] and "FUT3-FUT5" in missing[0]["message_zh"]


def test_missing_age_is_a_problem(tmp_path):
    _age, rows = _subject()
    path = write_rows(tmp_path / "npx.csv", rows)
    code = personal_report.main(["--measurements", str(path), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "age" and p["kind"] == "missing" for p in problems)


def test_fut3_fut5_underscore_name_matches(tmp_path):
    age, rows = _subject()
    rows = [("FUT3_FUT5", v, u) if n == "FUT3-FUT5" else (n, v, u) for n, v, u in rows]
    code, _out = _run(tmp_path, rows, age)
    assert code == 0


def test_baseline_change(tmp_path):
    age, rows = _subject("syn_4")
    _base_age, base_rows = _subject("syn_7")
    base = write_rows(tmp_path / "base.csv", base_rows)
    code, out = _run(tmp_path, rows, 67, "--baseline", str(base), "--baseline-age", "58")
    assert code == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["baseline_pac_age"]["value"] == pytest.approx(52.721563, abs=1e-5)
    assert result["pac_age_change"]["value"] == pytest.approx(60.479266 - 52.721563, abs=1e-5)


def test_baseline_without_age_is_a_problem(tmp_path):
    age, rows = _subject()
    base = write_rows(tmp_path / "base.csv", rows)
    code, out = _run(tmp_path, rows, age, "--baseline", str(base))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "baseline_age" for p in problems)


def test_xlsx_is_refused_with_a_reason(tmp_path):
    path = tmp_path / "olink.xlsx"
    path.write_bytes(b"PK")
    code = personal_report.main(["--measurements", str(path), "--age", "60", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "CSV" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_two_different_il6_rows_stop_the_run(tmp_path):
    age, rows = _subject()
    rows = rows + [("IL6", "3.5", "NPX")]
    code, out = _run(tmp_path, rows, age)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(p["key"] == "il6_npx" and p["kind"] == "duplicate" for p in problems)
