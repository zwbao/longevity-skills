import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


def _list_section(text: str) -> str:
    start = text.index("## 方法算出的名单")
    end = text.index("## 体检")
    return text[start:end]


def test_boundary_medicine_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = personal_report.report(tmp_path / "out", 60, meds, labs, None)
    text = out.read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "该开始" not in text
    assert "建议停" not in text
    bare = personal_report.report(tmp_path / "bare", 60, meds, None, None)
    assert _list_section(text) == _list_section(bare.read_text(encoding="utf-8"))


def test_repository_formula_matches_example_row():
    from presets import MOUSE, MOUSE_EXAMPLE_AGE, MOUSE_EXAMPLE_SUM, predict_from_sum
    assert predict_from_sum(MOUSE_EXAMPLE_SUM, MOUSE) == pytest_approx(MOUSE_EXAMPLE_AGE)


def test_published_human_blood_error_and_read_floor():
    from presets import HUMAN_N, HUMAN_TEST_MEDAE_YEARS, HUMAN_TEST_R, READ_MINIMUM
    assert HUMAN_TEST_R == 0.96
    assert HUMAN_TEST_MEDAE_YEARS == 3.39
    assert HUMAN_N == 1056
    assert READ_MINIMUM == 100000


def test_low_reads_and_scale_block_the_age(tmp_path: Path):
    from presets import HUMAN, cpgs, methylation_gap
    low = tmp_path / "low.txt"
    low.write_text("total_reads=99999\nchr12_1940556 50\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "low", 60, None, None, low).read_text(encoding="utf-8")
    assert "少于 100000" in text
    assert "算出了年龄" not in text
    values = {site: 50.0 for site in cpgs(HUMAN)}
    values[cpgs(HUMAN)[0]] = 150.0
    assert methylation_gap(values, HUMAN) == "scale"
    assert methylation_gap({site: 50.0 for site in cpgs(HUMAN)}, HUMAN) is None


def test_missing_cpg_does_not_impute(tmp_path: Path):
    meas = tmp_path / "m.txt"
    meas.write_text("chr12_1940556\t50\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "o", 60, None, None, meas).read_text(encoding="utf-8")
    assert "不填补，不算年龄" in text
    assert "预测年龄是" not in text


def pytest_approx(value):
    import pytest
    return pytest.approx(value)
