"""Table 3 FRIEND cells are the expected values, transcribed before implementation.
These are reference-table round trips, not invented individual case predictions.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as pr
import presets
import skillkit

MANIFEST = json.loads((ROOT / 'skill.json').read_text())
# Table 3 columns: 5th, 10th, 25th, 50th, 75th, 90th, 95th.
PRINTED = {
    'male': [
        (20, [29.0, 32.1, 40.1, 48.0, 55.2, 61.8, 66.3]),
        (30, [27.2, 30.2, 35.9, 42.4, 49.2, 56.5, 59.8]),
        (40, [24.2, 26.8, 31.9, 37.8, 45.0, 52.1, 55.6]),
        (50, [20.9, 22.8, 27.1, 32.6, 39.7, 45.6, 50.7]),
        (60, [17.4, 19.8, 23.7, 28.2, 34.5, 40.3, 43.0]),
        (70, [16.3, 17.1, 20.4, 24.4, 30.4, 36.6, 39.7]),
    ],
    'female': [
        (20, [21.7, 23.9, 30.5, 37.6, 44.7, 51.3, 56.0]),
        (30, [19.0, 20.9, 25.3, 30.2, 36.1, 41.4, 45.8]),
        (40, [17.0, 18.8, 22.1, 26.7, 32.4, 38.4, 41.7]),
        (50, [16.0, 17.3, 19.9, 23.4, 27.6, 32.0, 35.9]),
        (60, [13.4, 14.6, 17.2, 20.0, 23.8, 27.0, 29.4]),
        (70, [13.1, 13.6, 15.6, 18.3, 20.8, 23.1, 24.1]),
    ],
}


def test_table3_printed_reference_points():
    for sex, groups in PRINTED.items():
        for age, row in groups:
            for percentile, vo2 in zip([5, 10, 25, 50, 75, 90, 95], row):
                assert pr.reference_row(age, sex)[percentile] == vo2
                result = pr.lookup(age, sex, vo2)
                assert result['percentile_lower'] == percentile
                assert result['percentile_upper'] == percentile
                assert result['reference_median_ml_kg_min'] == row[3]


def run(tmp_path, rows=None, **overrides):
    if rows is None:
        rows = 'VO2max,48.0,mL/kg/min\nRER,1.20,1\n'
    path = tmp_path / 'measurements.csv'
    path.write_text('marker,value,unit\n' + rows)
    out = tmp_path / 'out'
    options = dict(age='20', sex='male', test_type='maximal_treadmill_cpx',
                   cvd='no', copd='no', early_stop='no')
    options.update(overrides)
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
            '--measurements', str(path), '--out', str(out)]
    for key, value in options.items():
        if value is not None:
            args.extend(['--' + key.replace('_', '-'), str(value)])
    process = subprocess.run(args, capture_output=True, text=True)
    return process, out


def test_table3_end_to_end(tmp_path):
    process, out = run(tmp_path)
    assert process.returncode == 0, process.stderr
    values = json.loads((out / 'result.json').read_text())['outputs']
    assert values['percentile_lower']['value'] == 50
    assert values['percentile_upper']['value'] == 50
    assert values['reference_median_ml_kg_min']['value'] == 48.0
    assert values['measured_vo2max_ml_kg_min']['value'] == 48.0
    report = (out / 'report.md').read_text()
    assert report.index('## 论文卡片') < report.index('## 你的结果')
    assert presets.BOUNDARY in report


@pytest.mark.parametrize('vo2,lower,upper,band', [
    (28.9, None, 5, '<P5'), (29.0, 5, 5, 'P5'),
    (29.1, 5, 10, 'P5–P10'), (66.3, 95, 95, 'P95'),
    (66.4, 95, None, '>P95'),
])
def test_interval_and_tails_do_not_interpolate(vo2, lower, upper, band):
    result = pr.lookup(20, 'male', vo2)
    assert (result['percentile_lower'], result['percentile_upper']) == (lower, upper)
    assert result['percentile_band'] == band


@pytest.mark.parametrize('sex', ['male', 'female'])
def test_decade_edges(sex):
    for age, row in PRINTED[sex]:
        assert list(pr.reference_row(age, sex).values()) == row
        assert list(pr.reference_row(age + 9, sex).values()) == row


@pytest.mark.parametrize('rows', [
    'VO2max,48,L/min\nRER,1.2,1\n',
    'VO2max,480,mL/kg/min\nRER,1.2,1\n',
    'VO2max,48,\nRER,1.2,1\n',
    'VO2max,nan,mL/kg/min\nRER,1.2,1\n',
    'VO2max,48,mL/kg/min\n',
    'RER,1.2,1\n',
    'VO2max,48,mL/kg/min\nRER,0.99,1\n',
    'VO2max,48,mL/kg/min\nVO2max,37,mL/kg/min\nRER,1.2,1\n',
    'VO2max,48,mL/kg/min,unexpected-column\nRER,1.2,1\n',
])
def test_bad_measurements_exit_three(tmp_path, rows):
    process, out = run(tmp_path, rows)
    assert process.returncode == 3, process.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert not (out / 'result.json').exists()
    report = (out / 'report.md').read_text()
    assert '## 论文卡片' in report and presets.BOUNDARY in report
    assert '## 你的结果' not in report


@pytest.mark.parametrize('override', [
    {'age': '19'}, {'age': '80'}, {'age': '20.5'}, {'age': 'nan'},
    {'age': 'bad'}, {'age': None}, {'sex': None}, {'sex': 'unknown'},
    {'test_type': None}, {'test_type': 'watch'}, {'test_type': 'cycle'},
    {'cvd': 'yes'}, {'cvd': None}, {'copd': 'yes'}, {'copd': 'unknown'},
    {'early_stop': 'yes'}, {'early_stop': None},
])
def test_ineligible_or_unknown_context_exit_three(tmp_path, override):
    process, out = run(tmp_path, **override)
    assert process.returncode == 3, process.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()


def test_conversion_and_chinese_aliases(tmp_path):
    process, out = run(tmp_path, '最大摄氧量,0.048,L/kg/min\n呼吸交换率,120,%\n', sex='男')
    assert process.returncode == 0, process.stderr
    values = json.loads((out / 'result.json').read_text())['outputs']
    assert values['measured_vo2max_ml_kg_min']['value'] == 48.0
    assert values['percentile_lower']['value'] == 50


def test_out_directory_reuse_clears_stale_files(tmp_path):
    assert run(tmp_path)[0].returncode == 0
    process, out = run(tmp_path, age='80')
    assert process.returncode == 3 and not (out / 'result.json').exists()
    assert run(tmp_path)[0].returncode == 0
    assert not (out / 'problems.json').exists()


def test_manifest_units_and_presets_agree():
    for key, unit, bounds in [
        ('vo2max_ml_kg_min', presets.VO2_UNIT, presets.VO2_RANGE),
        ('peak_rer', '1', presets.RER_RANGE), ('age', 'a', presets.AGE_RANGE),
    ]:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec['unit'] == unit and spec['range'] == list(bounds)
        assert spec['required']
    assert MANIFEST['validation']['status'] == 'reproduced'
    assert MANIFEST['inputs_status'] == 'verified'
