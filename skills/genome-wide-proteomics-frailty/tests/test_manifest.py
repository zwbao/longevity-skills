"""skill.json inputs match Supplementary Table 18, and wrong values stop the grouping.

Before the kit, a ready-made score of 500 was put in the high group, a score
written as text was dropped without a word, "否" beside a code counted as
having the diagnosis, and a one-column list of codes crashed with a traceback.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, DEMENTIA_CODES, HFRS_ITEMS, hfrs_bin

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
WEIGHT = {code: weight for code, weight, _zh, _desc in HFRS_ITEMS}


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(measurements: Path) -> str:
    """The report the unchanged reader, conditions() and render() write."""
    rows = personal_report.read_rows(measurements)
    return personal_report._with_paper_card(personal_report.render([], None, rows))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "genome-wide-proteomics-frailty"
    return result["outputs"]


def test_manifest_matches_table_18():
    specs = skillkit.input_specs(MANIFEST)
    assert specs[0]["key"] == "hfrs"
    codes = specs[1:]
    assert [(spec["key"], spec["label_zh"], spec["aliases"]) for spec in codes] == [
        (code, zh, [desc]) for code, _weight, zh, desc in HFRS_ITEMS
    ]
    assert all(spec["range"] == [0, 1] and spec["unit"] == "score" and not spec["required"] for spec in codes)
    score = specs[0]
    assert score["range"] == [0, pytest.approx(sum(WEIGHT.values()))]
    index = skillkit.alias_index(specs)
    for name in ("hfrs", "医院衰弱风险分"):
        assert index[skillkit.fold_name(name)][0]["key"] == "hfrs"
    assert all(spec.get("group") == "hfrs" for spec in specs)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["result_json"]) == ("--measurements", True)
    assert "age_flag" not in entry
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert [item["key"] for item in MANIFEST["outputs"]] == [
        "hfrs_score", "hfrs_group", "hfrs_score_without_dementia", "hfrs_group_without_dementia"
    ]


@pytest.mark.parametrize(
    "text",
    [
        "item,value\nF00.1,1\nG81,1\nI50,1\n",
        "item,value\nhfrs,5\nI50,1\n",
        "item,value\n偏瘫,1\nUnspecified fall,1\nR50,0\n",
        "code,value\nF00.1,\nG81,yes\nW19,1\n",
        "item,value\nI50,1\n",
    ],
    ids=["codes", "ready-made-score", "names", "code-column", "nothing-matched"],
)
def test_documented_files_give_the_same_report(tmp_path: Path, text):
    measurements = tmp_path / "m.csv"
    measurements.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--out", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8") == _before(measurements)
    hits, supplied = personal_report.conditions(personal_report.read_rows(measurements))
    outputs = _result(out)
    if hits:
        total = sum(weight for _code, weight, _zh in hits)
        assert outputs["hfrs_score"]["value"] == pytest.approx(total)
        assert outputs["hfrs_group"]["value"] == hfrs_bin(total)
        dementia = sum(WEIGHT[code] for code, _weight, _zh in hits if code in DEMENTIA_CODES)
        expected = total - dementia if dementia else None
        assert outputs["hfrs_score_without_dementia"]["value"] == (pytest.approx(expected) if dementia else None)
    elif supplied is not None:
        assert outputs["hfrs_score"]["value"] == pytest.approx(supplied)
        assert outputs["hfrs_group"]["value"] == hfrs_bin(supplied)
    else:
        assert all(item["value"] is None for item in outputs.values())
    assert not (out / "problems.json").exists()


def test_eleven_point_five_from_two_codes(tmp_path: Path):
    out = tmp_path / "out"
    rows = [("F00.1", "1", ""), ("偏瘫", "1", "score"), ("I50", "1", "")]
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == 0
    outputs = _result(out)
    assert outputs["hfrs_score"]["value"] == pytest.approx(WEIGHT["F00"] + WEIGHT["G81"])
    assert outputs["hfrs_score_without_dementia"]["value"] == pytest.approx(WEIGHT["G81"])
    assert outputs["hfrs_group_without_dementia"]["value"] == hfrs_bin(WEIGHT["G81"])


def test_one_column_list_and_no_word(tmp_path: Path):
    listed = tmp_path / "codes.csv"
    listed.write_text("code\nF00.1\nG81\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(listed), "--out", str(out)]) == 0
    assert _result(out)["hfrs_score"]["value"] == pytest.approx(WEIGHT["F00"] + WEIGHT["G81"])
    no = _csv(tmp_path / "no.csv", [("G81", "1", ""), ("W19", "否", "")])
    assert personal_report.main(["--measurements", str(no), "--out", str(tmp_path / "out2")]) == 0
    assert _result(tmp_path / "out2")["hfrs_score"]["value"] == pytest.approx(WEIGHT["G81"])


@pytest.mark.parametrize(
    "rows, reason",
    [
        ([("hfrs", "500", "")], "不在合理范围"),
        ([("hfrs", "很高", "")], "不是一个可以计算的数"),
        ([("hfrs", "5", "%")], "不能换算"),
        ([("G81", "2", "")], "不在合理范围"),
        ([("F00.1", "1", ""), ("F00.9", "0", "")], "出现了两次"),
    ],
    ids=["score-range", "score-text", "score-unit", "code-count", "code-conflict"],
)
def test_wrong_value_is_refused(tmp_path: Path, rows, reason):
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 医院衰弱风险分组"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以这次没有分组" in text and reason in text
    assert "落在「" not in text and "## 方法算出的名单" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert all(item["value"] is None for item in _result(out).values())


def test_nothing_given_is_not_a_problem(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == 0
    assert "没有对上诊断编码，也没有现成的医院衰弱风险分，所以这次没有分组。" in (out / "report.md").read_text(encoding="utf-8")
    assert not (out / "problems.json").exists()
