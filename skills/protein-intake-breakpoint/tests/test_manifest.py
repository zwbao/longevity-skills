"""Printed constants are checked first; these are NOT a worked-example reproduction.

Figure 5: 'break point=1.62 g protein/kg/day, p=0.079.'
Figure 5: 'Solid arrow indicates 95% CI, (1.03 to 2.20).'
No printed body weight + total daily intake + computed result was found.
Other cases below are engineering checks, not paper validation examples.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets
import personal_report as report
import skillkit

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


def test_printed_figure5_constants_only():
    assert presets.BREAKPOINT == 1.62
    assert presets.BREAKPOINT_CI == (1.03, 2.20)
    assert presets.MODEL_P == 0.079
    assert MANIFEST['validation']['status'] == 'draft'


def test_manifest_matches_presets():
    actual = [(s['key'], s['label_zh'], s['unit']) for s in MANIFEST['inputs'] if s['from'] == 'measurements']
    assert actual == list(presets.MEASUREMENTS)
    assert set(report.calculate({'protein_g_day': 100, 'weight_kg': 100}, True)) == {s['key'] for s in MANIFEST['outputs']}


def run(tmp_path, rows, extra=()):
    path = tmp_path / 'input.csv'
    path.write_text('marker,value,unit\n' + rows)
    out = tmp_path / 'out'
    proc = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(path), '--age', '40', '--context', 'healthy-ret', '--out', str(out), *extra], capture_output=True, text=True)
    return proc, out


def test_success_and_targets(tmp_path):
    target = tmp_path / 'target.csv'
    target.write_text('marker,value,unit\n每日总蛋白质,180,g/d\n')
    proc, out = run(tmp_path, '每日总蛋白质,140,g/d\n体重,100,kg\n', ['--targets', str(target)])
    assert proc.returncode == 0, proc.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    # Synthetic arithmetic fixture, not a published individual.
    assert outputs['protein_g_kg_day']['value'] == pytest.approx(1.4)
    assert outputs['position']['value'] == '低于研究拐点'
    assert outputs['breakpoint_difference']['value'] == pytest.approx(-0.22)
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['targets']['outputs']['protein_g_kg_day'] == pytest.approx(1.8)
    assert levers['levers'][0]['protein_g_kg_day_delta'] == pytest.approx(0.4)
    text = (out / 'report.md').read_text()
    assert text.index('论文卡片') < text.index('你的记录')
    assert presets.BOUNDARY in text
    assert '0.079' in text and '暂定' in text


@pytest.mark.parametrize('rows', [
    '每日总蛋白质,140,mg/dL\n体重,100,kg\n',
    '每日总蛋白质,140,g/d\n体重,1000,kg\n',
    '每日总蛋白质,140,g/d\n',
    '每日总蛋白质,nan,g/d\n体重,100,kg\n',
    '每日总蛋白质,140,g/d\n体重,100,\n',
    '每日总蛋白质,140,g/d\n体重,100,kg\n体重,90,kg\n',
])
def test_bad_inputs_exit_three(tmp_path, rows):
    proc, out = run(tmp_path, rows)
    assert proc.returncode == 3, proc.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'levers.json').exists()
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())
    text = (out / 'report.md').read_text()
    assert '论文卡片' in text and presets.BOUNDARY in text
    assert '你的记录' not in text


def test_units_and_threshold_equality():
    c = skillkit.collect_measurements([{'marker': 'protein_g_day', 'value': '162', 'unit': 'g/d'}, {'marker': 'weight_kg', 'value': '100000', 'unit': 'g'}], MANIFEST)
    assert not c.problems
    assert c.values['weight_kg'] == 100
    assert report.calculate(c.values, True)['position'] == '等于研究拐点（按印出精度）'
    c = skillkit.collect_measurements([{'marker': 'protein_g_day', 'value': '162', 'unit': 'g/d'}, {'marker': 'weight_kg', 'value': '100', 'unit': 'lb'}], MANIFEST)
    assert c.values['weight_kg'] == pytest.approx(45.359237)


def test_outside_context_and_observed_range():
    outside = report.calculate({'protein_g_day': 140, 'weight_kg': 100}, False)
    assert outside['protein_g_kg_day'] == pytest.approx(1.4)
    assert outside['position'] is None
    outside = report.calculate({'protein_g_day': 400, 'weight_kg': 100}, True)
    assert outside['position'] is None
    assert outside['breakpoint_difference'] is None
    assert outside['scope'] == '超出论文拐点分析摄入范围'


@pytest.mark.parametrize('extra', [
    ['--age', 'not-a-number'], ['--context', 'typo'], ['--age', 'nan'],
    ['--measurements', '/not/a/file.csv'],
])
def test_invalid_arguments_structured(tmp_path, extra):
    proc, out = run(tmp_path, '每日总蛋白质,140,g/d\n体重,100,kg\n', extra)
    assert proc.returncode == 3, proc.stderr
    assert (out / 'problems.json').exists()


def test_invalid_target_and_stale_results(tmp_path):
    rows = '每日总蛋白质,140,g/d\n体重,100,kg\n'
    proc, out = run(tmp_path, rows)
    assert proc.returncode == 0
    target = tmp_path / 'target.csv'
    target.write_text('marker,value,unit\n蛋白粉,40,g\n')
    proc, out = run(tmp_path, rows, ['--targets', str(target)])
    assert proc.returncode == 3
    assert not (out / 'levers.json').exists()
    proc, out = run(tmp_path, rows)
    assert proc.returncode == 0
    assert not (out / 'problems.json').exists()
