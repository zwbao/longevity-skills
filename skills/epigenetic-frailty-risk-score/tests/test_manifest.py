"""skill.json inputs match presets, and a value that is not a beta stops the computation.

Before skillkit, a beta written as a percentage (45) made efrs() return None and
the report blamed missing sites; a frailty index of 25 (percent) was banded as
frail; a deficit count above 31 was dropped without a word; and a number such as
0,52 crashed with a traceback.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import EFRS, ESTHER_DEFICITS, KORA_DEFICITS, efrs

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
SITES = [site for site, _coef in EFRS if site != "intercept"]
BETAS = {site: round(0.2 + 0.03 * index, 2) for index, site in enumerate(SITES)}


def _legacy(path: Path, betas: dict, *extra: str) -> Path:
    """The headerless betas.tsv documented in SKILL.md."""
    lines = [f"{site}\t{value}" for site, value in betas.items()] + list(extra)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _table(path: Path, rows) -> Path:
    """The table entry.measurements_header describes."""
    lines = [",".join(MANIFEST["entry"]["measurements_header"])] + [",".join(str(cell) for cell in row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(out: Path, measurements: Path, age: str = "70"):
    code = personal_report.main(["--measurements", str(measurements), "--age", age, "--out", str(out)])
    text = (out / "report.md").read_text(encoding="utf-8")
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, text, result


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    assert [key for key in declared if key.startswith("cg")] == SITES
    for site in SITES:
        assert declared[site]["label_zh"] == site
        assert skillkit.normalize_unit(declared[site]["unit"]) == "1"
        assert declared[site]["range"] == [0, 1]
        assert declared[site]["required"] is True
    assert set(declared) == set(SITES) | {"fi", "esther_deficits", "kora_deficits"}
    assert skillkit.normalize_unit(declared["fi"]["unit"]) == "1"
    assert declared["fi"]["range"] == [0, 1] and "accept" not in declared["fi"]
    assert declared["esther_deficits"]["range"] == [0, ESTHER_DEFICITS]
    assert declared["kora_deficits"]["range"] == [0, KORA_DEFICITS]
    assert personal_report.DEFICIT_TOTALS == {"esther_deficits": ESTHER_DEFICITS, "kora_deficits": KORA_DEFICITS}
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert age["from"] == "profile" and age["flag"] == MANIFEST["entry"]["age_flag"] == "--age"
    assert MANIFEST["entry"]["measurements_flag"] == "--measurements"
    assert [item["key"] for item in MANIFEST["outputs"]] == ["efrs", "frailty_index", "frailty_band"]


def test_inputs_are_verified():
    assert MANIFEST["inputs_status"] == "verified"


@pytest.mark.parametrize("value", ["45", "-2.3", "1.7"])
def test_beta_outside_zero_to_one_is_refused(tmp_path: Path, value: str):
    betas = dict(BETAS, cg00921350=value)
    code, text, result = _run(tmp_path / "out", _legacy(tmp_path / "betas.tsv", betas))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "没有风险分" in text
    assert "cg00921350" in text and "不在合理范围" in text and "β" in text
    assert "算出了风险分" not in text and "- 风险分" not in text
    assert result["efrs"]["value"] is None
    assert json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"][0]["key"] == "cg00921350"


def test_percent_unit_is_refused_not_rescaled(tmp_path: Path):
    rows = [(site, value, "") for site, value in BETAS.items()]
    rows[0] = (SITES[0], 20, "%")
    code, text, result = _run(tmp_path / "out", _table(tmp_path / "t.csv", rows))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不能换算" in text
    assert "算出了风险分" not in text
    assert all(item["value"] is None for item in result.values())


def test_frailty_index_in_percent_is_refused(tmp_path: Path):
    code, text, result = _run(tmp_path / "out", _legacy(tmp_path / "fi.txt", {}, "fi=25"))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "衰弱指数" in text and "0.2" in text
    assert "属于衰弱" not in text
    assert result["frailty_band"]["value"] is None


def test_deficit_count_above_the_index_size_is_refused(tmp_path: Path):
    code, text, result = _run(tmp_path / "out", _legacy(tmp_path / "d.txt", {}, "esther_deficits=40"))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "31" in text and "属于" not in text
    assert result["frailty_index"]["value"] is None


def test_unparsable_beta_is_a_problem_not_a_traceback(tmp_path: Path):
    betas = dict(BETAS, cg00921350="0,52")
    code, text, _result = _run(tmp_path / "out", _legacy(tmp_path / "betas.tsv", betas))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不是一个可以计算的数" in text


def test_age_out_of_range_is_refused(tmp_path: Path):
    code, text, _result = _run(tmp_path / "out", _legacy(tmp_path / "betas.tsv", BETAS), age="700")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "实足年龄" in text and "算出了风险分" not in text


def test_result_json_holds_the_score(tmp_path: Path):
    out = tmp_path / "out"
    _run(out, _legacy(tmp_path / "bad.tsv", dict(BETAS, cg00921350="45")))
    assert (out / "problems.json").exists()
    code, text, result = _run(out, _legacy(tmp_path / "betas.tsv", BETAS, "esther_deficits=8"))
    expected = efrs(BETAS)
    assert code == 0
    assert not (out / "problems.json").exists()
    assert f"用你给的甲基化算出了风险分，是 {expected:.4f}。" in text
    assert result["efrs"]["value"] == pytest.approx(expected)
    assert result["efrs"]["unit"] == "score"
    assert result["frailty_index"]["value"] == pytest.approx(8 / ESTHER_DEFICITS)
    assert result["frailty_band"]["value"] == "衰弱"


def test_table_with_header_gives_the_same_score(tmp_path: Path):
    rows = [(site.upper(), value, "") for site, value in BETAS.items()] + [("衰弱指数", 0.18, "")]
    code, _text, result = _run(tmp_path / "out", _table(tmp_path / "t.csv", rows))
    assert code == 0
    assert result["efrs"]["value"] == pytest.approx(efrs(BETAS))
    assert result["frailty_index"]["value"] == pytest.approx(0.18)
    assert result["frailty_band"]["value"] == "衰弱前期"


def test_missing_site_keeps_the_old_wording(tmp_path: Path):
    betas = dict(BETAS)
    del betas["cg23458887"]
    code, text, result = _run(tmp_path / "out", _legacy(tmp_path / "betas.tsv", betas, "cg99999999 0.7"))
    assert code == 0
    assert "位点不全，或数值不在零到一之间，不算 eFRS。" in text
    assert result["efrs"]["value"] is None
