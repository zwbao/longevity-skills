"""Printed expectations from Doll et al., BMJ 2004, Table 5 and Figure 4 text.

Written before the lookup implementation. Rates are per 1000 men per year,
not probabilities; dashes remain missing. Column order is never, quit 35-44,
quit 45-54, quit 55-64, continuing cigarettes, printed smoker/never ratio.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PRINTED = {
    35: [(1.6, 55), None, None, None, (2.7, 150), 1.6],
    45: [(3.8, 145), (5.4, 95), None, None, (8.5, 487), 2.3],
    55: [(8.4, 290), (9.0, 132), (16.4, 229), None, (21.4, 703), 2.5],
    65: [(18.6, 528), (22.7, 262), (31.7, 331), (36.4, 250), (50.7, 722), 2.7],
    75: [(51.7, 666), (53.1, 316), (69.1, 370), (78.9, 299), (112.2, 453), 2.2],
}


def run(tmp_path, text="item,value,unit\nsmoking_history_code,2,1\nquit_age_years,50,a\n",
        age="65", sex="male", extra=()):
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(tmp_path / "out")]
    if text is not None:
        path = tmp_path / "history.csv"
        path.write_text(text, encoding="utf-8")
        args += ["--measurements", str(path)]
    if age is not None:
        args += ["--age", str(age)]
    if sex is not None:
        args += ["--sex", sex]
    p = subprocess.run(args + list(extra), capture_output=True, text=True)
    return p, tmp_path / "out"


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


@pytest.mark.parametrize("age,row", PRINTED.items())
def test_table_5_printed_rows(age, row):
    from personal_report import lookup
    for column, (history, quit_age) in enumerate([(0, None), (2, 40), (2, 50), (2, 60), (1, None)]):
        if quit_age is not None and quit_age > age:
            continue  # impossible personal chronology; these empty cells are tested separately
        got = lookup(age, history, quit_age)
        cell = row[column]
        assert got["cohort_annual_deaths_per_1000"] == (None if cell is None else cell[0])
        assert got["cohort_observed_deaths"] == (None if cell is None else cell[1])
        assert got["never_smoker_annual_deaths_per_1000"] == row[0][0]
        assert got["continuing_smoker_annual_deaths_per_1000"] == row[4][0]
        assert got["printed_smoker_vs_never_ratio"] == row[5]


def test_table_5_cli_example(tmp_path):
    # Printed row: 65-74 | 18.6 (528) | 22.7 (262) | 31.7 (331) |
    # 36.4 (250) | 50.7 (722) | 2.7; select the 45-54 quit-age column.
    p, out = run(tmp_path)
    assert p.returncode == 0, p.stderr
    got = outputs(out)
    assert got["attained_age_band"] == "65-74"
    assert got["quit_age_band"] == "45-54"
    assert got["cohort_annual_deaths_per_1000"] == 31.7
    assert got["cohort_observed_deaths"] == 331
    assert got["never_smoker_annual_deaths_per_1000"] == 18.6
    assert got["continuing_smoker_annual_deaths_per_1000"] == 50.7
    assert got["printed_smoker_vs_never_ratio"] == 2.7
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的历史分组")
    assert "边界:" in report and "不是你的死亡概率" in report
    assert "不能据此开始或停止任何药物" in report


@pytest.mark.parametrize("quit_age,gain", [(30, 10), (40, 9), (50, 6), (60, 3)])
def test_figure_4_printed_gains(quit_age, gain):
    from personal_report import lookup
    assert lookup(75, 2, quit_age)["cohort_approx_life_years_gained"] == gain


def test_manifest_matches_presets():
    import presets
    manifest = json.loads((ROOT / "skill.json").read_text())
    for key, (unit, bounds) in presets.INPUT_SPECS.items():
        spec = next(s for s in manifest["inputs"] if s["key"] == key)
        assert spec["unit"] == unit
        assert spec["range"] == list(bounds)
    quit_spec = next(s for s in manifest["inputs"] if s["key"] == "quit_age_years")
    assert quit_spec["accept"] == {"mo": 1 / 12}
    assert manifest["validation"]["status"] == "reproduced"


@pytest.mark.parametrize("age,quit_age,band,quit_band,rate", [
    (44.999, 35, "35-44", "35-44", None),
    (45, 44.999, "45-54", "35-44", 5.4),
    (55, 45, "55-64", "45-54", 16.4),
    (65, 55, "65-74", "55-64", 36.4),
    (84.999, 64.999, "75-84", "55-64", 78.9),
    (75, 34.999, "75-84", "25-34", None),
])
def test_age_band_edges_and_missing_cells(age, quit_age, band, quit_band, rate):
    from personal_report import lookup
    got = lookup(age, 2, quit_age)
    assert got["attained_age_band"] == band
    assert got["quit_age_band"] == quit_band
    assert got["cohort_annual_deaths_per_1000"] == rate


def test_alias_and_month_conversion(tmp_path):
    p, out = run(tmp_path, "项目,结果,单位\n吸烟史编码,2,1\n戒烟年龄,600,mo\n")
    assert p.returncode == 0, p.stderr
    assert outputs(out)["cohort_annual_deaths_per_1000"] == 31.7


@pytest.mark.parametrize("text,age,sex", [
    (None, "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\nquit_age_years,50,mg/dL\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\nquit_age_years,150,a\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\nquit_age_years,70,a\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\nquit_age_years,20,a\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,2,1\nquit_age_years,nan,a\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\nquit_age_years,50,a\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,1.5,1\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,3,1\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\n", None, "male"),
    ("item,value,unit\nsmoking_history_code,1,1\n", "nan", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\n", "34", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\n", "85", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\n", "65", None),
    ("item,value,unit\nsmoking_history_code,1,1\n", "65", "female"),
    ("item,value,unit\nsmoking_history_code,1,1\n吸烟史编码,0,1\n", "65", "male"),
    ("item,value,unit\nsmoking_history_code,1,1\nunknown,50,a\n", "65", "male"),
])
def test_invalid_inputs_exit_3(tmp_path, text, age, sex):
    p, out = run(tmp_path, text, age, sex)
    assert p.returncode == 3, p.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in outputs(out).values())
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界:" in report
    assert "你的历史分组" not in report


def test_success_error_success_clears_stale_files(tmp_path):
    assert run(tmp_path)[0].returncode == 0
    p, out = run(tmp_path, sex="female")
    assert p.returncode == 3
    assert all(v is None for v in outputs(out).values())
    assert run(tmp_path)[0].returncode == 0
    assert not (out / "problems.json").exists()
