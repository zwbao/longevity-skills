"""Expected values are printed cells, written before implementation.

Supplementary PDF p.168, Table 18, fruit and vegetables:
g/d RR (95% CI); 0 1.00; 500 0.73 (0.70-0.77); 800 0.69 (0.66-0.73).
Supplementary PDF p.158, Table 8, combined / incidence / mortality:
35.6 1.00; 500 0.84 (0.81-0.86); 500 0.84 (0.81-0.87); 500 0.80 (0.75-0.85).
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


def test_printed_table18():
    for intake, expected in [(500, (0.73, 0.70, 0.77)), (800, (0.69, 0.66, 0.73))]:
        got = report.lookup('combined', 'all_cause_mortality', 'mortality', intake)
        assert got['status'] == 'exact'
        assert (got['rr'], got['ci_low'], got['ci_high']) == expected
        assert got['reference_g_d'] == 0
    assert report.lookup('combined', 'all_cause_mortality', 'mortality', 0)['rr'] == 1.00


def test_printed_table8_endpoints():
    for endpoint, expected in [('mixed', (0.84, 0.81, 0.86)), ('incidence', (0.84, 0.81, 0.87)), ('mortality', (0.80, 0.75, 0.85))]:
        got = report.lookup('combined', 'coronary_heart_disease', endpoint, 500)
        assert (got['rr'], got['ci_low'], got['ci_high']) == expected
        assert got['reference_g_d'] == 35.6


def test_other_printed_tables():
    # Tables 9–17, at 200 g/d; keep exposure and endpoint separate.
    cases = [
        ('fruit', 'coronary_heart_disease', 'mixed', (0.85, 0.83, 0.88)),
        ('combined', 'stroke', 'mixed', (0.84, 0.80, 0.88)),
        ('vegetables', 'stroke', 'mortality', (0.90, 0.78, 1.04)),
        ('fruit', 'ischemic_stroke', 'mixed', (0.80, 0.76, 0.85)),
        ('vegetables', 'hemorrhagic_stroke', 'mixed', (0.72, 0.65, 0.79)),
        ('combined', 'cardiovascular_disease', 'incidence', (0.95, 0.91, 0.99)),
        ('fruit', 'cardiovascular_disease', 'mortality', (0.75, 0.71, 0.80)),
        ('combined', 'total_cancer', 'mixed', (0.94, 0.92, 0.95)),
        ('vegetables', 'total_cancer', 'mortality', (0.87, 0.83, 0.91)),
    ]
    for food, outcome, endpoint, expected in cases:
        got = report.lookup(food, outcome, endpoint, 200)
        assert (got['rr'], got['ci_low'], got['ci_high']) == expected


def test_brackets_and_missing_cells_are_not_estimates():
    got = report.lookup('combined', 'all_cause_mortality', 'mortality', 525)
    assert got['status'] == 'bracket' and got['rr'] is None
    assert (got['lower']['intake_g_d'], got['lower']['rr'], got['lower']['ci_high']) == (500, 0.73, 0.77)
    assert (got['upper']['intake_g_d'], got['upper']['rr'], got['upper']['ci_high']) == (550, 0.73, 0.76)
    assert report.lookup('combined', 'hemorrhagic_stroke', 'mixed', 200)['status'] == 'not_published'
    assert report.lookup('fruit', 'all_cause_mortality', 'mortality', 650)['status'] == 'outside_table'
    assert report.lookup('combined', 'coronary_heart_disease', 'mixed', 0)['status'] == 'outside_table'
    ref = report.lookup('combined', 'cardiovascular_disease', 'incidence', 86.8)
    assert ref['rr'] == 1.00 and ref['ci_low'] is None and ref['ci_high'] is None


def run_cli(tmp_path, text, extra=()):
    measurements = tmp_path / 'measurements.csv'
    measurements.write_text(text, encoding='utf-8')
    out = tmp_path / 'out'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(measurements), '--out', str(out), *extra], capture_output=True, text=True)
    return result, out


def test_report_result_and_targets(tmp_path):
    targets = tmp_path / 'targets.csv'
    targets.write_text('marker,value,unit\nintake_g_d,800,g/d\n')
    proc, out = run_cli(tmp_path, 'marker,value,unit\n日均摄入量,500,g/d\n', ['--targets', str(targets)])
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    assert result['rr']['value'] == 0.73
    assert result['ci_low']['value'] == 0.70
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['targets']['rr'] == 0.69
    assert levers['levers'][0]['rr_delta'] == pytest.approx(0.69 - 0.73)
    text = (out / 'report.md').read_text()
    assert text.index('论文卡片') < text.index('本次查表')
    assert presets.BOUNDARY in text and '目标' in text and '0.73' in text


@pytest.mark.parametrize('rows', [
    '', 'intake_g_d,500,kg\n', 'intake_g_d,3001,g/d\n', 'intake_g_d,-1,g/d\n',
    'intake_g_d,nan,g/d\n', '日均摄入量,500,\n', 'intake_g_d,500,g/d\nintake_g_d,600,g/d\n',
])
def test_invalid_inputs_exit3(tmp_path, rows):
    proc, out = run_cli(tmp_path, 'marker,value,unit\n' + rows)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    assert '论文卡片' in (out / 'report.md').read_text()


def test_bad_target_clears_previous_outputs(tmp_path):
    proc, out = run_cli(tmp_path, 'marker,value,unit\nintake_g_d,500,g/d\n')
    assert proc.returncode == 0
    targets = tmp_path / 'targets.csv'
    targets.write_text('marker,value,unit\nintake_g_d,800,kg\n')
    proc, out = run_cli(tmp_path, 'marker,value,unit\nintake_g_d,500,g/d\n', ['--targets', str(targets)])
    assert proc.returncode == 3 and not (out / 'result.json').exists()


def test_bracket_target_has_no_invented_delta():
    current = report.lookup('combined', 'all_cause_mortality', 'mortality', 500)
    result = report.levers(current, 525)
    assert result['targets']['status'] == 'bracket'
    assert result['targets']['rr'] is None
    assert result['levers'][0]['rr_delta'] is None
    # Table 18: 450 0.74 (0.71-0.78); 550 0.73 (0.70-0.76).
    sensitivity = result['sensitivity'][0]
    assert sensitivity['lower']['intake_g_d'] == 450
    assert sensitivity['upper']['intake_g_d'] == 550
    assert sensitivity['rr_per_g_d'] == pytest.approx((0.73 - 0.74) / (550 - 450))
    outside = report.lookup('combined', 'all_cause_mortality', 'mortality', 900)
    assert report.levers(outside)['sensitivity'][0]['rr_per_g_d'] is None


@pytest.mark.parametrize('extra', [
    ['--food-group', 'juice'],
    ['--outcome', 'all_cause_mortality', '--endpoint', 'incidence'],
    ['--outcome', 'ischemic_stroke', '--endpoint', 'mortality'],
])
def test_invalid_column_selection_exit3(tmp_path, extra):
    proc, out = run_cli(tmp_path, 'marker,value,unit\nintake_g_d,500,g/d\n', extra)
    assert proc.returncode == 3
    assert not (out / 'result.json').exists()
    assert json.loads((out / 'problems.json').read_text())['problems']


def test_missing_file_exit3(tmp_path):
    out = tmp_path / 'out'
    code = report.main(['--measurements', str(tmp_path / 'absent.csv'), '--out', str(out)])
    assert code == 3 and (out / 'problems.json').exists()


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / 'skill.json').read_text())
    spec = next(s for s in manifest['inputs'] if s['key'] == presets.INPUT_KEY)
    assert spec['unit'] == presets.UNIT == 'g/d'
    assert spec['range'] == list(presets.INPUT_RANGE)
    assert manifest['validation']['status'] == 'reproduced'
    assert {s['key'] for s in manifest['outputs']} == set(report.output_values(report.lookup('combined', 'all_cause_mortality', 'mortality', 500)))
