"""Printed per-item examples: Heatherton et al. (1991), Table 3, p. 1125.

The paper prints item scores, not a complete person's total. Tests of totals
below check summation only and are not claimed as printed total examples.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())
BASE = {
    'current_cigarette_smoker': 1,
    'time_to_first_cigarette_min': 60,
    'difficulty_refraining': 0,
    'morning_cigarette_hardest': 0,
    'cigarettes_per_day_count': 10,
    'smoke_more_after_waking': 0,
    'smoke_when_ill_in_bed': 0,
}


@pytest.mark.parametrize('minutes,points', [(5, 3), (6, 2), (30, 2), (31, 1), (60, 1), (61, 0)])
def test_table3_time_to_first(minutes, points):
    # Printed cells: Within 5 minutes 3; 6–30 minutes 2;
    # 31–60 minutes 1; After 60 minutes 0. 61 satisfies the last category.
    assert report.score_item('time_to_first_cigarette_min', minutes) == points


@pytest.mark.parametrize('count,points', [(10, 0), (11, 1), (20, 1), (21, 2), (30, 2), (31, 3)])
def test_table3_cigarettes_per_day(count, points):
    # Printed cells: 10 or less 0; 11–20 1; 21–30 2; 31 or more 3.
    assert report.score_item('cigarettes_per_day_count', count) == points


@pytest.mark.parametrize('key', [
    'difficulty_refraining', 'morning_cigarette_hardest',
    'smoke_more_after_waking', 'smoke_when_ill_in_bed',
])
def test_table3_binary_items(key):
    # Q2/Q5/Q6: yes=1, no=0; Q3: first morning cigarette=1, all others=0.
    assert report.score_item(key, 1) == 1
    assert report.score_item(key, 0) == 0


def run_cli(tmp_path, changes=None, omit=(), extra=(), targets=None):
    values = dict(BASE, **(changes or {}))
    specs = {s['key']: s for s in MANIFEST['inputs']}
    rows = [(k, v, specs[k]['unit']) for k, v in values.items() if k not in omit]
    rows += list(extra)
    source = tmp_path / 'answers.csv'
    with source.open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['marker', 'value', 'unit'])
        writer.writerows(rows)
    out = tmp_path / 'out'
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
            '--measurements', str(source), '--out', str(out)]
    if targets is not None:
        target_path = tmp_path / 'targets.csv'
        with target_path.open('w') as f:
            writer = csv.writer(f)
            writer.writerow(['marker', 'value', 'unit'])
            writer.writerows(targets)
        args += ['--targets', str(target_path)]
    return subprocess.run(args, capture_output=True, text=True), out


def test_manifest_matches_presets():
    specs = {s['key']: s for s in MANIFEST['inputs'] if s['from'] == 'measurements'}
    assert {k: s['unit'] for k, s in specs.items()} == presets.INPUT_UNITS
    assert set(presets.ITEM_KEYS) == set(BASE) - {'current_cigarette_smoker'}
    assert MANIFEST['validation']['status'] == 'reproduced'
    assert {o['key'] for o in MANIFEST['outputs']} == {'ftnd_score', *presets.OUTPUT_KEYS.values()}


def test_report_has_printed_item_values_and_sum(tmp_path):
    proc, out = run_cli(tmp_path)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    # Table 3: 31–60 minutes -> 1, 10 or less -> 0, negative answers -> 0.
    assert result['q1_points']['value'] == 1
    for key in ('q2_points', 'q3_points', 'q4_points', 'q5_points', 'q6_points'):
        assert result[key]['value'] == 0
    assert result['ftnd_score']['value'] == sum(result[k]['value'] for k in presets.OUTPUT_KEYS.values())
    text = (out / 'report.md').read_text()
    assert text.index('论文卡片') < text.index('你的结果')
    assert presets.BOUNDARY in text
    assert '边界' in text and '未定义轻、中、重度' in text


@pytest.mark.parametrize('changes,omit,extra,kind', [
    ({}, ('difficulty_refraining',), (), 'missing'),
    ({'time_to_first_cigarette_min': 1500}, (), (), 'range'),
    ({'difficulty_refraining': 0.5}, (), (), 'value'),
    ({'time_to_first_cigarette_min': 5.5}, (), (), 'value'),
    ({'cigarettes_per_day_count': 10.5}, (), (), 'value'),
    ({'cigarettes_per_day_count': 0}, (), (), 'range'),
    ({'current_cigarette_smoker': 0}, (), (), 'population'),
    ({'difficulty_refraining': 'NaN'}, (), (), 'parse'),
    ({}, ('time_to_first_cigarette_min',), (('TTF', 30, 'kg'),), 'unit'),
    ({}, ('time_to_first_cigarette_min',), (('TTF', 30, ''),), 'unit_missing'),
    ({}, (), (('CPD', 20, '1'),), 'duplicate'),
    ({}, (), (('unexpected', 1, '1'),), 'unknown'),
])
def test_bad_inputs_exit3_without_score(tmp_path, changes, omit, extra, kind):
    proc, out = run_cli(tmp_path, changes, omit, extra)
    assert proc.returncode == 3, proc.stderr
    problems = json.loads((out / 'problems.json').read_text())['problems']
    assert kind in {p['kind'] for p in problems}
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    assert 'FTND总分：' not in (out / 'report.md').read_text()
    assert '论文卡片' in (out / 'report.md').read_text()


def test_hours_convert_and_chinese_alias(tmp_path):
    proc, out = run_cli(tmp_path, omit=('time_to_first_cigarette_min',),
                        extra=(('醒后第一支烟时间', 0.5, 'h'),))
    assert proc.returncode == 0, proc.stderr
    # 0.5 h = 30 min; printed Table 3 assigns 2 points to 6–30 minutes.
    assert json.loads((out / 'result.json').read_text())['outputs']['q1_points']['value'] == 2


def test_targets_use_printed_scores_not_treatment_effects(tmp_path):
    proc, out = run_cli(tmp_path, targets=[('CPD', 31, '1')])
    assert proc.returncode == 0, proc.stderr
    data = json.loads((out / 'levers.json').read_text())
    assert data['schema'] == 'longevity-levers/1'
    # Table 3: 31 or more -> 3; 10 or less -> 0.
    assert data['targets']['q4_points'] == 3
    assert data['current']['q4_points'] == 0
    assert data['levers'][0]['ftnd_score_delta'] == 3 - 0
    assert '不是治疗效果' in data['note_zh']


def test_target_failure_clears_previous_outputs(tmp_path):
    proc, out = run_cli(tmp_path)
    assert proc.returncode == 0
    proc, out = run_cli(tmp_path, targets=[('CPD', 0, '1')])
    assert proc.returncode == 3
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()


def test_no_file_lists_missing_answers(tmp_path):
    out = tmp_path / 'out'
    proc = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                           '--out', str(out)], capture_output=True, text=True)
    assert proc.returncode == 3
    assert {p['key'] for p in json.loads((out / 'problems.json').read_text())['problems']} == set(BASE)
