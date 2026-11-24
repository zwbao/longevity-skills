"""Expected readouts come from Thomas et al. 2013 Figure 3 and Figure S2."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def run_report(tmp_path, rows, targets=None):
    measurement = tmp_path / 'measurements.csv'
    measurement.write_text('marker,value,unit\n' + rows, encoding='utf-8')
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
           '--measurements', str(measurement), '--out', str(tmp_path / 'out')]
    if targets is not None:
        target_file = tmp_path / 'targets.csv'
        target_file.write_text('marker,value,unit\n' + targets, encoding='utf-8')
        cmd += ['--targets', str(target_file)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc, tmp_path / 'out'


def test_figure3_printed_bri(tmp_path):
    # Figure 3: Height (in) 65; Waist (in) 39; Body Roundness Index: 5.4.
    # BRI is printed to one decimal place: half a last-place unit is 0.05.
    proc, out = run_report(tmp_path, 'Height,65,in\nWaist,39,in\n')
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / 'result.json').read_text())
    assert result['outputs']['bri']['value'] == pytest.approx(5.4, abs=0.05)
    text = (out / 'report.md').read_text()
    assert text.index('## 论文卡片') < text.index('## 你的结果')
    assert '10.1002/oby.20408' in text
    assert '边界:' in text


@pytest.mark.parametrize('height,waist,expected', [(169.6, 147.7, 0.961), (166.4, 85.8, 0.986)])
def test_supplement_figure_s2(height, waist, expected):
    from personal_report import calculate
    assert calculate({'height_cm': height, 'waist_cm': waist})['waist_eccentricity'] == pytest.approx(expected, abs=0.0005)


def test_manifest_matches_presets():
    from presets import MEASUREMENTS
    manifest = json.loads((ROOT / 'skill.json').read_text())
    declared = [(s['key'], s['label_zh'], s['unit']) for s in manifest['inputs'] if s['from'] == 'measurements']
    assert declared == list(MEASUREMENTS)
    assert manifest['validation']['status'] == 'reproduced'


@pytest.mark.parametrize('rows', [
    '身高,165,kg\n腰围,99,cm\n',
    '身高,1650,cm\n腰围,99,cm\n',
    '身高,165,cm\n',
    '身高,165,cm\n腰围,39,\n',
    '身高,nan,cm\n腰围,99,cm\n',
    '身高,165,cm\n腰围,99,cm\nWaist,90,cm\n',
])
def test_invalid_input_exits_three(tmp_path, rows):
    proc, out = run_report(tmp_path, rows)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())
    report = (out / 'report.md').read_text()
    assert '## 论文卡片' in report and '边界:' in report
    assert '## 你的结果' not in report
    assert not (out / 'levers.json').exists()


def test_centimetres_and_metres_reproduce_figure3(tmp_path):
    proc, out = run_report(tmp_path, '身高,1.651,m\n腰围,99.06,cm\n')
    assert proc.returncode == 0, proc.stderr
    assert json.loads((out / 'result.json').read_text())['outputs']['bri']['value'] == pytest.approx(5.4, abs=0.05)


def test_waist_target_reproduces_figure3(tmp_path):
    proc, out = run_report(tmp_path, 'Height,65,in\nWaist,45,in\n', 'Waist,39,in\n')
    assert proc.returncode == 0, proc.stderr
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['schema'] == 'longevity-levers/1'
    assert levers['targets']['bri'] == pytest.approx(5.4, abs=0.05)
    assert levers['levers'][0]['bri_delta'] < 0
    assert levers['sensitivity'][0]['bri_per_unit'] > 0
    # Target output and delta must refer to the same scenario.
    assert levers['levers'][0]['bri_delta'] == pytest.approx(levers['targets']['bri'] - levers['current']['bri'])


@pytest.mark.parametrize('targets', ['Waist,39,kg\n', 'Height,170,cm\n', 'unknown,90,cm\n', ''])
def test_bad_targets_clear_previous_success(tmp_path, targets):
    proc, out = run_report(tmp_path, 'Height,65,in\nWaist,39,in\n')
    assert proc.returncode == 0
    proc, out = run_report(tmp_path, 'Height,65,in\nWaist,39,in\n', targets)
    assert proc.returncode == 3
    assert not (out / 'levers.json').exists()
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())
