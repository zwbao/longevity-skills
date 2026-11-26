"""Printed expectations: Momma et al. 2022 Table 1, dose-response column.

This validates the published 10 min/week contrast, not the nonlinear Figure 4.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets


def test_printed_table1_ten_minutes():
    # Table header: Dose–response meta-analysis (10 min/week increase).
    expected = {
        'all_cause_mortality': (0.99, 0.98, 1.00),
        'cvd': (0.996, 0.99, 1.003),
        'total_cancer': (0.99, 0.98, 1.004),
        'diabetes': (0.98, 0.97, 0.99),
    }
    for outcome, printed in expected.items():
        assert report.linear_contrast(10, outcome) == pytest.approx(printed, abs=1e-12)


def run(tmp_path, value='10', unit='min', marker='每周力量训练总时长', target=None, age='40'):
    source = tmp_path / 'input.csv'
    source.write_text(f'marker,value,unit\n{marker},{value},{unit}\n', encoding='utf-8')
    out = tmp_path / 'out'
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(source), '--age', age, '--out', str(out)]
    if target is not None:
        path = tmp_path / 'target.csv'
        path.write_text(f'marker,value,unit\n{marker},{target},min\n', encoding='utf-8')
        cmd += ['--targets', str(path)]
    return subprocess.run(cmd, capture_output=True, text=True), out


def test_manifest_matches_presets():
    m = json.loads((ROOT / 'skill.json').read_text())
    s = m['inputs'][0]
    assert (s['key'], s['unit'], s['range']) == (presets.INPUT_KEY, presets.INPUT_UNIT, list(presets.INPUT_RANGE))
    assert set(report.output_values(10)) == {s['key'] for s in m['outputs']}
    assert m['validation']['status'] == 'reproduced'


def test_cli_printed_result_and_target_increment(tmp_path):
    p, out = run(tmp_path, target='20')
    assert p.returncode == 0, p.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    assert result['diabetes_linear_rr']['value'] == 0.98
    assert result['diabetes_linear_ci_low']['value'] == 0.97
    assert result['diabetes_linear_ci_high']['value'] == 0.99
    levers = json.loads((out / 'levers.json').read_text())
    # 20 minus 10 is the Table 1 contrast, not a new invented expected RR.
    assert levers['targets']['contrast']['diabetes'] == pytest.approx([0.98, 0.97, 0.99])
    assert levers['sensitivity'][0]['rr_per_min']['diabetes'] < 0
    body = (out / 'report.md').read_text()
    assert body.index('10.1136/bjsports-2021-105061') < body.index('你的输入')
    assert '边界：' in body and '不是个人患病或死亡概率' in body
    assert '非线性' in body and 'J 形' in body


@pytest.mark.parametrize('value,unit,marker,age', [
    ('10','mg/dL','每周力量训练总时长','40'),
    ('10081','min','每周力量训练总时长','40'),
    ('-1','min','每周力量训练总时长','40'),
    ('nan','min','每周力量训练总时长','40'),
    ('10','','每周力量训练总时长','40'),
    ('10','min','unknown','40'),
    ('','min','每周力量训练总时长','40'),
    ('10','min','每周力量训练总时长','17'),
    ('10','min','每周力量训练总时长','bad'),
])
def test_invalid_inputs_exit_three(tmp_path, value, unit, marker, age):
    p, out = run(tmp_path, value, unit, marker, age=age)
    assert p.returncode == 3, p.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'levers.json').exists()
    result = json.loads((out / 'result.json').read_text())
    assert all(x['value'] is None for x in result['outputs'].values())
    body = (out / 'report.md').read_text()
    assert '10.1136/bjsports-2021-105061' in body and '没有计算' in body


def test_hours_conversion_and_missing_file(tmp_path):
    a, out = run(tmp_path, '1', 'h')
    assert a.returncode == 0, a.stderr
    hours = json.loads((out / 'result.json').read_text())
    b, out = run(tmp_path, '60', 'min')
    assert b.returncode == 0
    assert hours == json.loads((out / 'result.json').read_text())
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), '--age', '40', '--out', str(out)], capture_output=True, text=True)
    assert p.returncode == 3 and not (out / 'levers.json').exists()


def test_bad_target_clears_previous_success(tmp_path):
    p, out = run(tmp_path, target='20')
    assert p.returncode == 0
    p, out = run(tmp_path, target='-1')
    assert p.returncode == 3 and not (out / 'levers.json').exists()
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())


def test_contrast_reversal_and_zero_are_consistent():
    for key in presets.OUTCOMES:
        forward = report.linear_contrast(10, key)
        reverse = report.linear_contrast(-10, key)
        assert reverse == pytest.approx((1 / forward[0], 1 / forward[2], 1 / forward[1]))
        assert report.linear_contrast(0, key) == (1, 1, 1)
        assert reverse[1] <= reverse[0] <= reverse[2]


def test_malformed_csv_exits_three(tmp_path):
    source = tmp_path / 'bad.csv'
    source.write_text('marker,value,unit\n每周力量训练总时长,10,min,extra\n')
    out = tmp_path / 'out'
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(source), '--age', '40', '--out', str(out)], capture_output=True, text=True)
    assert p.returncode == 3, p.stderr
    assert (out / 'problems.json').exists()


def test_missing_age_is_not_silently_assumed(tmp_path):
    p, out = run(tmp_path)
    assert p.returncode == 0
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(tmp_path / 'input.csv'), '--out', str(out)], capture_output=True, text=True)
    assert p.returncode == 3
    problems = json.loads((out / 'problems.json').read_text())['problems']
    assert any(p['key'] == 'age' and p['kind'] == 'missing' for p in problems)
