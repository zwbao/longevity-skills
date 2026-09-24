"""skill.json inputs match presets, and wrong points stop the index.

Before the kit, raw scale scores written under the domain names (ADL 6, MNA-SF
12) were averaged into an index of 2.5 that was only called out of range, an
age of 400 was recorded, and a missing domain was reported without an exit code
a caller could act on.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, DOMAINS, mpi_group

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
POINTS = {"adl": "0", "iadl": "0.5", "spmsq": "0", "cirs_ci": "0.5", "mna_sf": "0.5", "ess": "0", "nm": "1", "social": "0"}


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(measurements: Path, age=None) -> str:
    """The report the unchanged file reader and method_lines() write."""
    return personal_report._with_paper_card(personal_report.render(age, None, None, measurements))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "ampk-gamma1-refeeding-longevity"
    return result["outputs"]


def test_manifest_matches_presets():
    specs = skillkit.input_specs(MANIFEST)
    domains = [spec for spec in specs if spec.get("group") == "mpi"]
    assert [(spec["key"], spec["label_zh"]) for spec in domains] == list(DOMAINS)
    assert all(spec["required"] and spec["unit"] == "score" and spec["range"] == [0, 1] for spec in domains)
    index = skillkit.alias_index(specs)
    for alias, key in personal_report.ALIASES.items():
        assert index[skillkit.fold_name(alias)][0]["key"] == key
    prkag1 = skillkit.spec_by_key(MANIFEST, "prkag1")
    assert (prkag1["required"], "unit" in prkag1, "range" in prkag1) == (False, False, False)
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", False)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert {item["key"]: item.get("unit") for item in MANIFEST["outputs"]} == {"mpi": "score", "mpi_group": None}


@pytest.mark.parametrize(
    "points, age",
    [
        (POINTS, None),
        ({**POINTS, "adl": "1", "iadl": "1", "spmsq": "1", "nm": "0.5"}, "80"),
        ({key: "0.5" for key in POINTS}, "70"),
        ({**POINTS, "adl": "0.25", "spmsq": "0.4", "social": "1"}, None),
    ],
    ids=["mpi-1", "mpi-3", "mpi-2", "gap"],
)
def test_documented_file_gives_the_same_index(tmp_path: Path, points, age):
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\n" + "".join(f"{key},{value}\n" for key, value in points.items()) + "prkag1,1.20\n", encoding="utf-8")
    out = tmp_path / "out"
    argv = ["--measurements", str(measurements), "--out", str(out)] + (["--age", age] if age else [])
    assert personal_report.main(argv) == 0
    before = _before(measurements, float(age) if age else None)
    assert (out / "report.md").read_text(encoding="utf-8") == before
    expected = sum(Decimal(points[key]) for key, _label in DOMAINS) / Decimal(8)
    shown = personal_report.show_num(expected)
    assert f"- 预后指数：{shown}" in before
    assert "记下 1.20" in before
    outputs = _result(out)
    assert outputs["mpi"]["value"] == pytest.approx(float(expected))
    group = mpi_group(expected)
    assert outputs["mpi_group"]["value"] == (group if group in personal_report.LABELS else None)
    assert not (out / "problems.json").exists()


def test_other_names_units_and_raw_scores(tmp_path: Path):
    rows = [(label, POINTS[key], "score") for key, label in DOMAINS] + [("adl_raw", "6", ""), ("MNA-SF 原始分", "12", "")]
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    old = tmp_path / "old.csv"
    old.write_text("name,value\n" + "".join(f"{key},{value}\n" for key, value in POINTS.items()) + "adl_raw,6\nMNA-SF 原始分,12\n", encoding="utf-8")
    assert text == _before(old)
    assert "这次看到原始分：adl_raw、MNA-SF 原始分。" in text


@pytest.mark.parametrize(
    "change, age, reason",
    [
        ({"adl": ("6", "")}, None, "不在合理范围"),
        ({"mna_sf": ("12", "")}, None, "不在合理范围"),
        ({"nm": ("0.5", "%")}, None, "不能换算"),
        ({"social": ("中等", "")}, None, "不是一个可以计算的数"),
        ({"ess": None}, None, "缺少Exton Smith 量表"),
        ({}, "400", "实足年龄"),
    ],
    ids=["adl-raw", "mna-raw", "unit", "text", "missing", "age"],
)
def test_wrong_or_missing_point_is_refused(tmp_path: Path, change, age, reason):
    rows = []
    for key, value in POINTS.items():
        if key in change:
            if change[key] is None:
                continue
            rows.append((key, *change[key]))
        else:
            rows.append((key, value, ""))
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)] + (["--age", age] if age else [])
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 再喂食时的调节亚基与预后指数"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以没有预后指数" in text and reason in text
    assert "- 预后指数：" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {key: item["value"] for key, item in _result(out).items()} == {"mpi": None, "mpi_group": None}


def test_nothing_given_is_refused(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    keys = [item["key"] for item in json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]]
    assert keys == [key for key, _label in DOMAINS]
