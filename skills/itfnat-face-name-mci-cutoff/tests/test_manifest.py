"""ItFNAT delayed free recall and MoCA cut-offs against Scaramuzzi et al., GeroScience 2026.

Expected values are printed in the paper: Table 4 (cut-offs, sensitivity, specificity,
accuracy) and the Results text (DFR PLR = 3.086, MoCA NLR = 0.485). The person-level
inputs are synthetic adjusted scores.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import COHORT, DFR_CUTOFF, MOCA_CUTOFF, TABLE4

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    code = pr.main(["--measurements", str(m), "--out", str(out)])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    # Table 4
    assert DFR_CUTOFF == 3.21 and MOCA_CUTOFF == 23.99
    assert (TABLE4["dfr"]["sens"], TABLE4["dfr"]["spec"], TABLE4["dfr"]["acc"]) == (60.00, 80.56, 71.21)
    assert (TABLE4["moca"]["sens"], TABLE4["moca"]["spec"], TABLE4["moca"]["acc"]) == (65.00, 72.22, 68.94)
    assert TABLE4["dfr"]["auc"] == 0.711 and TABLE4["moca"]["auc"] == 0.705
    # Participants / Table 1
    assert (COHORT["n"], COHORT["n_ch"], COHORT["n_mci"]) == (136, 72, 64)


def test_paper_dfr_positive_likelihood_ratio(tmp_path: Path):
    # Table 4: DFR cut-off <= 3.21, sensitivity 60.00, specificity 80.56 -> Results: PLR = 3.086.
    assert pr.positive_likelihood_ratio(60.00, 80.56) == pytest.approx(3.086, abs=0.0005)
    code, result, report, _ = _run(tmp_path, [("ItFNAT DFR adjusted", "3.21", "score")])
    assert code == 0
    assert result["dfr_cutoff_result"]["value"] == "≤3.21 阳性"
    assert result["dfr_likelihood_ratio"]["value"] == pytest.approx(3.086, abs=0.0005)
    assert "3.086" in report


def test_paper_moca_negative_likelihood_ratio(tmp_path: Path):
    # Table 4: MoCA cut-off <= 23.99, sensitivity 65.00, specificity 72.22 -> Results: NLR = 0.485.
    assert pr.negative_likelihood_ratio(65.00, 72.22) == pytest.approx(0.485, abs=0.0005)
    code, result, report, _ = _run(tmp_path, [("MoCA 校正分", "24", "")])
    assert code == 0
    assert result["moca_cutoff_result"]["value"] == ">23.99 阴性"
    assert result["moca_likelihood_ratio"]["value"] == pytest.approx(0.485, abs=0.0005)
    assert "0.485" in report


def test_table4_accuracy_is_consistent():
    # Table 4 accuracy 71.21 (DFR) and 68.94 (MoCA) follow from 72 CH (Table 1) and 60 MCI with
    # a ROC score: 36/60 and 58/72 for DFR, 39/60 and 52/72 for MoCA, out of 132.
    assert (36 + 58) / 132 * 100 == pytest.approx(71.21, abs=0.005)
    assert (39 + 52) / 132 * 100 == pytest.approx(68.94, abs=0.005)
    assert 58 / 72 * 100 == pytest.approx(TABLE4["dfr"]["spec"], abs=0.005)
    assert 52 / 72 * 100 == pytest.approx(TABLE4["moca"]["spec"], abs=0.005)


def test_both_scores_negative_and_positive(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("DFR校正分", "6.5", ""), ("MoCA adjusted", "21.5", "score")])
    assert code == 0
    assert result["dfr_cutoff_result"]["value"] == ">3.21 阴性"
    # NLR for DFR from Table 4: (1 - 0.60) / 0.8056
    assert result["dfr_likelihood_ratio"]["value"] == pytest.approx(0.497, abs=0.0005)
    assert result["moca_cutoff_result"]["value"] == "≤23.99 阳性"
    assert result["moca_likelihood_ratio"]["value"] == pytest.approx(2.340, abs=0.0005)
    assert "不一致" in report and "不把两个似然比相乘" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02599-9" in report
    assert "诊断" in report and "你患有" not in report


def test_one_score_is_enough(tmp_path: Path):
    code, result, _, _ = _run(tmp_path, [("延迟自由回忆校正分", "2", "")])
    assert code == 0
    assert result["moca_cutoff_result"]["value"] is None and result["moca_likelihood_ratio"]["value"] is None


def test_raw_moca_is_refused(tmp_path: Path):
    code, result, report, out = _run(tmp_path, [("MoCA", "22", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "moca_adjusted_score" and "校正" in problems[0]["message_zh"]
    assert all(item["value"] is None for item in result.values())
    assert "## 论文卡片" in report and "边界:" in report


def test_out_of_range_is_refused(tmp_path: Path):
    # A raw score out of 100 typed into the 0-34 MoCA field.
    code, result, _, out = _run(tmp_path, [("MoCA 校正总分", "85", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())


def test_wrong_unit_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("ItFNAT DFR adjusted", "4", "%")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "unit"


def test_nothing_given_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("血压", "120", "mmHg")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "missing"


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["itfnat_dfr_adjusted_score", "moca_adjusted_score"]
    assert keys == [spec["key"] for spec in pr.TESTS.values()]
    for key in keys:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "score" and spec["from"] == "measurements"
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "reproduced"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["dfr_cutoff_result", "dfr_likelihood_ratio",
                                                      "moca_cutoff_result", "moca_likelihood_ratio"]
