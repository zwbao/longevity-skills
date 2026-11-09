"""skill.json matches presets; wrong or missing inputs stop with exit 3;
the exported model gives the published pickle's outputs.

The reference probabilities in PICKLE_REFERENCE are what the authors'
models/final_model_cognitive_scores.pkl (commit c67358d) returns from
CalibratedClassifierCV.predict_proba under scikit-learn 1.8.0 (the version it
was saved with), xgboost 3.2.0 and imbalanced-learn 0.14.2, for synthetic
inputs (not people). They check the export, not the paper: the paper prints
no per-person probability (see validation.gap_zh).
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cog_model  # noqa: E402
import personal_report  # noqa: E402
import skillkit  # noqa: E402
from presets import FEATURES, MODEL_SOURCE_SHA256, TABLE_S2_MEAN_SD  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

# (MMSE, CDR global, CDR-SB, ADAS11, ADAS13, FAQ) -> pickle predict_proba[:, 1]
PICKLE_REFERENCE = [
    ((29, 0.5, 0.5, 5.0, 8.0, 0), 0.055064342393028674),
    ((28, 0.5, 1.0, 8.0, 13.0, 1), 0.07971976129757495),
    ((27, 0.5, 1.5, 10.33, 16.33, 2), 0.4348976000982695),
    ((26, 0.5, 2.0, 13.0, 21.0, 5), 0.7122438656235048),
    ((25, 0.5, 3.0, 16.67, 26.0, 9), 0.836535278523637),
    ((24, 1.0, 4.5, 20.0, 31.0, 15), 0.874007077336025),
    ((30, 0.0, 0.0, 3.0, 5.0, 0), 0.05019520490018037),
    ((27, 0.5, 2.5, 12.0, 19.67, 6), 0.7354784189215557),
]
PICKLE_THRESHOLD = 0.32039103389120177

CHINESE = [
    ("简易精神状态检查", "27", ""),
    ("CDR全局分", "0.5", ""),
    ("CDR-SB", "1.5", ""),
    ("ADAS-Cog 11", "10.33", ""),
    ("ADAS-Cog 13", "16.33", ""),
    ("功能活动问卷", "2", "score"),
]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["marker,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows):
    out = tmp_path / "out"
    code = personal_report.main(["--scores", str(_csv(tmp_path / "s.csv", rows)), "--out", str(out)])
    return code, out


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == [key for key, _c, _l, _u in FEATURES]
    for item, (key, _col, label, unit) in zip(declared, FEATURES):
        assert item["label_zh"] == label
        assert item["unit"] == unit
        assert item["required"] is True
        assert key in TABLE_S2_MEAN_SD
    assert MANIFEST["inputs_status"] == "verified"
    assert {o["key"] for o in MANIFEST["outputs"]} == {"conversion_probability_pct", "model_group", "model_threshold_pct"}
    assert MANIFEST["validation"]["status"] == "draft"


def test_model_file_is_the_declared_export():
    path = ROOT / "data" / "cog_model.json"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (declared,) = [d for d in MANIFEST["data_files"] if d["path"] == "data/cog_model.json"]
    assert digest == declared["sha256"]
    model = json.loads(path.read_text(encoding="utf-8"))
    assert model["source_sha256"] == MODEL_SOURCE_SHA256
    assert model["features"] == [col for _k, col, _l, _u in FEATURES]
    assert len(model["folds"]) == 5
    assert all(len(f["trees"]) == 451 for f in model["folds"])


@pytest.mark.parametrize("scores,expected", PICKLE_REFERENCE)
def test_export_matches_published_pickle(scores, expected):
    assert cog_model.conversion_probability(scores) == pytest.approx(expected, abs=1e-6)


def test_threshold_matches_published_pickle():
    assert cog_model.threshold() == pytest.approx(PICKLE_THRESHOLD, abs=1e-12)


def test_chinese_names_give_result_json(tmp_path: Path):
    code, out = _run(tmp_path, CHINESE)
    assert code == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["conversion_probability_pct"]["value"] == pytest.approx(100 * 0.4348976000982695, abs=1e-4)
    assert result["model_group"]["value"] == "above_threshold"
    assert result["model_threshold_pct"]["value"] == pytest.approx(100 * PICKLE_THRESHOLD)
    assert not (out / "problems.json").exists()


def test_wrong_unit_stops(tmp_path: Path):
    rows = [r if r[0] != "简易精神状态检查" else ("MMSE", "27", "mg/dL") for r in CHINESE]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["kind"] for p in problems] == ["unit"]
    assert "%" not in (out / "report.md").read_text(encoding="utf-8").split("边界")[0]
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["conversion_probability_pct"]["value"] is None


def test_out_of_range_stops(tmp_path: Path):
    rows = [r if r[0] != "功能活动问卷" else ("FAQ", "45", "") for r in CHINESE]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "faq_score" and problems[0]["kind"] == "range"
    assert "校准概率是" not in (out / "report.md").read_text(encoding="utf-8")


def test_cdr_sum_of_boxes_in_global_row_stops(tmp_path: Path):
    rows = [r if r[0] != "CDR全局分" else ("CDR", "1.5", "") for r in CHINESE]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "CDR-SB" in text and "校准概率是" not in text


def test_fractional_mmse_stops(tmp_path: Path):
    rows = [r if r[0] != "简易精神状态检查" else ("MMSE", "27.5", "") for r in CHINESE]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "mmse_score"


def test_adas13_below_adas11_stops(tmp_path: Path):
    rows = [r if r[0] != "ADAS-Cog 13" else ("ADAS13", "8", "") for r in CHINESE]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "adas13_score"


def test_missing_score_reports_no_probability(tmp_path: Path):
    rows = [r for r in CHINESE if r[0] != "功能活动问卷"]
    code, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["key"] for p in problems] == ["faq_score"]
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "没有转化概率" in text and "论文卡片" in text
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["conversion_probability_pct"]["value"] is None
