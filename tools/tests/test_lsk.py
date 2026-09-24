"""Tests for the repository tooling (tools/lsk) and the shared skillkit."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lsk import jsonschema_lite, readme, registry, units  # noqa: E402
from tools.lsk.common import load_skillkit  # noqa: E402
from tools.lsk.doi import normalize_doi  # noqa: E402

kit = load_skillkit()


@pytest.mark.parametrize("raw, expected", [
    (" DOI: 10.1038/S41467-026-68399-Z。", "10.1038/s41467-026-68399-z"),
    ("https://doi.org/10.1016/j.immuni.2026.02.007。全文已读。代码仓库是", "10.1016/j.immuni.2026.02.007"),
    ("https://doi.org/10.1016/S0140-6736(20)30183-5).", "10.1016/s0140-6736(20)30183-5"),
    ("doi:10.1093/brain/awag311", "10.1093/brain/awag311"),
    ("not a doi", ""),
    (None, ""),
])
def test_normalize_doi(raw, expected):
    assert normalize_doi(raw) == expected


def test_unit_cases_shared_with_the_plugin():
    cases = json.loads((ROOT / "schema" / "unit_cases.json").read_text(encoding="utf-8"))["cases"]
    for raw, expected in cases:
        assert kit.normalize_unit(raw) == expected, raw


def test_expected_factors():
    table = units.load_table()
    assert units.expected_factor("mg/L", "mg/dL", None, table) == pytest.approx(0.1)
    assert units.expected_factor("g/dL", "g/L", None, table) == pytest.approx(10)
    assert units.expected_factor("10^9/L", "10^3/uL", None, table) == pytest.approx(1)
    assert units.expected_factor("mg/dL", "mmol/L", 180.16, table) == pytest.approx(0.0555, rel=0.01)
    assert units.expected_factor("mg/dL", "umol/L", 113.12, table) == pytest.approx(88.4, rel=0.01)
    assert units.expected_factor("mg/dL", "mmol/L", None, table) is None


def test_wrong_accept_factor_is_reported():
    table = units.load_table()
    good = {"key": "crp", "unit": "mg/dL", "accept": {"mg/L": 0.1}}
    bad = {"key": "crp", "unit": "mg/dL", "accept": {"mg/L": 10}}
    assert units.check_input_units(good, table) == []
    assert "mg/L" in units.check_input_units(bad, table)[0]


MANIFEST = {
    "name": "demo",
    "inputs": [
        {"key": "crp_mg_dl", "label_zh": "C反应蛋白", "aliases": ["crp", "超敏c反应蛋白"], "unit": "mg/dL",
         "accept": {"mg/L": 0.1}, "range": [0.001, 50], "unit_required": True, "required": True, "from": "measurements"},
        {"key": "albumin_gL", "label_zh": "白蛋白", "aliases": ["ALB"], "unit": "g/L", "accept": {"g/dL": 10},
         "range": [15, 65], "required": True, "from": "measurements"},
        {"key": "age", "label_zh": "实足年龄", "unit": "a", "range": [18, 110], "required": True, "from": "profile", "flag": "--age"},
    ],
    "outputs": [{"key": "score", "label_zh": "分数"}],
}


def _rows(*rows):
    return [dict(zip(("marker", "value", "unit"), row)) for row in rows]


def test_key_names_carry_their_unit():
    got = kit.collect_measurements(_rows(("crp_mg_dl", "0.2", ""), ("albumin_gL", "44", "")), MANIFEST)
    assert got.ok and got.values == {"crp_mg_dl": 0.2, "albumin_gL": 44.0}


def test_alias_needs_unit_only_when_required():
    got = kit.collect_measurements(_rows(("超敏C反应蛋白", "1.0", ""), ("白蛋白(ALB)", "44", "")), MANIFEST)
    assert [p.kind for p in got.problems] == ["unit_missing"]
    assert got.values == {"albumin_gL": 44.0}


def test_declared_units_convert_and_unknown_units_do_not():
    got = kit.collect_measurements(_rows(("CRP", "1.0", "mg/L"), ("白蛋白", "4.4", "g/dL")), MANIFEST)
    assert got.ok
    assert got.values["crp_mg_dl"] == pytest.approx(0.1)
    assert got.values["albumin_gL"] == pytest.approx(44)
    bad = kit.collect_measurements(_rows(("CRP", "1.0", "nmol/L"), ("白蛋白", "44", "g/L")), MANIFEST)
    assert [p.kind for p in bad.problems] == ["unit"]


def test_range_problem_suggests_the_likely_unit():
    got = kit.collect_measurements(_rows(("CRP", "0.1", "mg/dL"), ("白蛋白", "4.5", "")), MANIFEST)
    assert [p.kind for p in got.problems] == ["range"]
    assert "g/dL" in got.problems[0].message_zh


def test_missing_duplicate_and_unparsable_rows():
    got = kit.collect_measurements(_rows(("CRP", "<0.5", "mg/L"), ("白蛋白", "44", ""), ("ALB", "40", "")), MANIFEST)
    kinds = sorted(p.kind for p in got.problems)
    assert kinds == ["duplicate", "parse"]
    empty = kit.collect_measurements([], MANIFEST)
    assert sorted(p.key for p in empty.problems) == ["albumin_gL", "crp_mg_dl"]


def test_scalar_range_and_result_json(tmp_path):
    assert kit.check_scalar(MANIFEST, "age", 40) == []
    assert kit.check_scalar(MANIFEST, "age", 400)[0].kind == "range"
    path = kit.write_result(tmp_path, MANIFEST, {"score": 1.5})
    assert json.loads(path.read_text(encoding="utf-8"))["outputs"]["score"]["value"] == 1.5
    with pytest.raises(KeyError):
        kit.write_result(tmp_path, MANIFEST, {"not_declared": 1})


def test_jsonschema_lite_subset():
    schema = {"type": "object", "required": ["a"], "additionalProperties": False,
              "properties": {"a": {"type": "integer", "minimum": 1}, "b": {"enum": ["x"]}}}
    assert jsonschema_lite.validate({"a": 2}, schema) == []
    errors = jsonschema_lite.validate({"a": True, "c": 1}, schema)
    assert any("expected integer" in e for e in errors) and any("unknown field c" in e for e in errors)


def test_registry_upsert_is_idempotent_on_normalized_doi():
    rows = []
    row, created = registry.upsert(rows, {"doi": "https://doi.org/10.1038/S41586-1。", "tier": "C", "outcome": "indexed"})
    assert created and row["doi"] == "10.1038/s41586-1"
    again, created = registry.upsert(rows, {"doi": "10.1038/s41586-1", "tier": "A", "outcome": "skill", "skill": "x"})
    assert not created and len(rows) == 1 and again["tier"] == "A" and again["first_seen"] == row["first_seen"]


def test_readme_roundtrip():
    text = "# T\n\n## 工具与证据库\n\n- `skills/tool-a/` — 工具。\n\n## 甲基化\n\n- `skills/skill-a/` — 甲基化年龄。\n\n## 衰弱与死亡风险\n\n- `skills/skill-a/` — 见「甲基化」。同一技能也收在那里。\n"
    parsed = readme.parse_readme(text)
    assert parsed["skill-a"] == {"domains": ["甲基化", "衰弱与死亡风险"], "blurb": "甲基化年龄。"}
    manifests = {
        "tool-a": {"tier": "tool", "domains": ["工具与证据库"], "blurb_zh": "工具。"},
        "skill-a": {"tier": "A", "domains": ["甲基化", "衰弱与死亡风险"], "blurb_zh": "甲基化年龄。"},
        "skill-c": {"tier": "C", "domains": ["比较生物学"], "blurb_zh": "小鼠。"},
    }
    rendered = readme.render_list(manifests)
    again = readme.parse_readme(rendered)
    assert again["skill-a"]["domains"][:2] == ["甲基化", "衰弱与死亡风险"]
    assert "只收录，不参与个人调度" in rendered and "skills/skill-c/" in rendered
    spliced = readme.splice(text, rendered)
    assert spliced.startswith("# T") and readme.BEGIN in spliced
    assert readme.splice(spliced, rendered) == spliced
