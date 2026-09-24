"""skill.json inputs match presets, and unit or range mistakes stop the indices.

Before the kit, an ACR in mg/mmol (3.4) was compared with the 30 mg/g line as
if it were mg/g, a self-rated health answer on the 1-5 scale (4) was put into
the formula, and text in a number line crashed with a traceback.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import ACR_MICROALBUMINURIA, BOUNDARY, COMORBIDITIES, comorbidity_index, self_health_index, smoking_score

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Keys parse_measurements()/render() read besides comorbidity=, in skill.json order.
SCRIPT_KEYS = ["cotinine_ng_ml", "acr_mg_g", "fair_general_health", "poor_general_health",
               "better_current_health", "worse_current_health", "huq050"]
DOCUMENTED = (
    "comorbidity=高血压\ncomorbidity=diabetes mellitus\n并存病=骨质疏松\ncomorbidity=不在二十二项里\n"
    "cotinine_ng_ml=150\nacr_mg_g=42\nfair_general_health=1\npoor_general_health=0\n"
    "better_current_health=0\nworse_current_health=1\nhuq050=3\n"
)


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(measurements: Path) -> str:
    """The report the unchanged key=value reader and render() write."""
    return personal_report._with_paper_card(personal_report.render(60, None, None, measurements))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "principal-component-clinical-aging"
    return result["outputs"]


def test_manifest_matches_presets():
    specs = skillkit.input_specs(MANIFEST)
    comorbid = [spec for spec in specs if spec.get("group") == "comorbidity"]
    assert [(spec["key"], spec["label_zh"]) for spec in comorbid] == [(key.replace(" ", "_"), label) for key, label in COMORBIDITIES]
    index = skillkit.alias_index(specs)
    for key, label in COMORBIDITIES:
        assert index[skillkit.fold_name(key)][0]["key"] == index[skillkit.fold_name(label)][0]["key"] == key.replace(" ", "_")
    assert [spec["key"] for spec in specs if spec.get("group") != "comorbidity"] == SCRIPT_KEYS
    assert index[skillkit.fold_name("healthcare_use")][0]["key"] == "huq050"
    acr = skillkit.spec_by_key(MANIFEST, "acr_mg_g")
    assert acr["unit"] == "mg/g" and acr["unit_required"] is True
    assert acr["range"][0] < ACR_MICROALBUMINURIA < acr["range"][1]
    assert not any(spec["required"] for spec in MANIFEST["inputs"])
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"]) == ("profile", "--age", "a")
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert [item["key"] for item in MANIFEST["outputs"]] == ["comorbidity_index", "smoking_score", "self_health_index", "acr_at_least_30"]


def test_documented_file_gives_the_same_report(tmp_path: Path):
    measurements = tmp_path / "measures.txt"
    measurements.write_text(DOCUMENTED, encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--age", "60", "--out", str(out)]) == 0
    before = _before(measurements)
    assert (out / "report.md").read_text(encoding="utf-8") == before
    index, present = comorbidity_index(["高血压", "diabetes mellitus", "骨质疏松", "不在二十二项里"])
    assert present == ["hypertension", "diabetes mellitus", "osteoporosis"]
    assert f"并存病指数：{index:.4f}" in before
    outputs = _result(out)
    assert outputs["comorbidity_index"]["value"] == pytest.approx(index)
    assert outputs["smoking_score"]["value"] == smoking_score(150.0)[0]
    assert outputs["self_health_index"]["value"] == pytest.approx(self_health_index(1.0, 0.0, 0.0, 1.0))
    assert outputs["acr_at_least_30"]["value"] == "达到"
    assert not (out / "problems.json").exists()


def test_table_with_units_and_other_names_is_read(tmp_path: Path):
    rows = [("高血压", "1", ""), ("diabetes_mellitus", "1", ""), ("骨质疏松", "1", "score"), ("哮喘", "0", ""),
            ("可替宁", "150", "µg/L"), ("ACR", "4.75113", "mg/mmol"), ("fair_general_health", "1", ""),
            ("poor_general_health", "0", ""), ("better_current_health", "0", ""), ("worse_current_health", "1", ""),
            ("就医使用指数", "3", "")]
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "- 高血压\n- 糖尿病\n- 骨质疏松\n- 并存病指数" in text and "哮喘" not in text.split("## 方法算出的名单")[1]
    acr = 4.75113 * skillkit.unit_factor(skillkit.spec_by_key(MANIFEST, "acr_mg_g"), "mg/mmol")
    assert f"尿白蛋白肌酐比 {acr:g} mg/g，达到 30 mg/g。" in text
    assert _result(out)["smoking_score"]["value"] == smoking_score(150.0)[0]


def test_nothing_given_is_not_a_problem(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == 0
    assert "没有给出这二十二种并存病里的名字，所以没有指数。" in (out / "report.md").read_text(encoding="utf-8")
    assert all(item["value"] is None for item in _result(out).values())


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("ACR", "3.4", "")], None, "没有写单位"),
        ([("acr_mg_g", "40", "mg/L")], None, "不能换算"),
        ([("cotinine_ng_ml", "150", "nmol/L")], None, "不能换算"),
        ([("cotinine_ng_ml", "-5", "")], None, "不在合理范围"),
        ([("fair_general_health", "4", "")], None, "不在合理范围"),
        ([("高血压", "有", "")], None, "不是一个可以计算的数"),
        ([("高血压", "1", ""), ("hypertension", "0", "")], None, "出现了两次"),
        ([("高血压", "1", "")], "400", "实足年龄"),
    ],
    ids=["acr-no-unit", "acr-unit", "cotinine-molar", "cotinine-negative", "health-scale", "yes-word", "duplicate", "age"],
)
def test_wrong_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)] + (["--age", age] if age else [])
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 临床指数"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以这次没有算指数" in text and reason in text
    assert "## 方法算出的名单" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert all(item["value"] is None for item in _result(out).values())
