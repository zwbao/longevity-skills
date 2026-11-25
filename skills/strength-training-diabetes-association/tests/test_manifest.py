"""Paper numbers, not calculator-generated expected values."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from personal_report import contrast
from presets import INPUT_KEY, INPUT_UNIT, INPUT_RANGE, BOUNDARY


def test_table1_printed_ten_minute_increment():
    # Table 1: Dose–response meta-analysis (10 min/week increase)
    # Diabetes ... 0.98 (0.97 to 0.99). Tests this published increment only;
    # it does not independently validate multi-increment extrapolation.
    actual = contrast(10)
    assert actual['rr'] == pytest.approx(0.98, abs=1e-12)
    assert actual['ci_lower'] == pytest.approx(0.97, abs=1e-12)
    assert actual['ci_upper'] == pytest.approx(0.99, abs=1e-12)


def run_report(tmp_path, value='10', unit='min', marker=INPUT_KEY, targets=None, age='45'):
    measurements = tmp_path / 'measurements.csv'
    measurements.write_text(f'marker,value,unit\n{marker},{value},{unit}\n')
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
            '--measurements', str(measurements), '--age', age, '--out', str(tmp_path / 'out')]
    if targets is not None:
        target = tmp_path / 'targets.csv'
        target.write_text(targets)
        args += ['--targets', str(target)]
    return subprocess.run(args, capture_output=True, text=True), tmp_path / 'out'


def test_manifest_and_printed_result_json(tmp_path):
    manifest = json.loads((ROOT / 'skill.json').read_text())
    spec = next(x for x in manifest['inputs'] if x['key'] == INPUT_KEY)
    assert spec['unit'] == INPUT_UNIT
    assert spec['range'] == list(INPUT_RANGE)
    p, out = run_report(tmp_path)
    assert p.returncode == 0, p.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    assert result['rr_vs_none']['value'] == pytest.approx(0.98)
    assert result['rr_vs_none_ci_lower']['value'] == pytest.approx(0.97)
    assert result['rr_vs_none_ci_upper']['value'] == pytest.approx(0.99)
    report = (out / 'report.md').read_text()
    assert report.index('论文卡片') < report.index('你的输入')
    assert BOUNDARY in report


@pytest.mark.parametrize('value,unit,marker,age', [
    ('10', 'kg', INPUT_KEY, '45'), ('-1', 'min', INPUT_KEY, '45'),
    ('10081', 'min', INPUT_KEY, '45'), ('', 'min', INPUT_KEY, '45'),
    ('nan', 'min', INPUT_KEY, '45'), ('ten', 'min', INPUT_KEY, '45'),
    ('10', '', '每周力量训练时长', '45'), ('10', 'min', INPUT_KEY, '17'),
    ('10', 'min', INPUT_KEY, 'bad'), ('10', 'min', INPUT_KEY, 'nan'),
])
def test_bad_inputs_exit_three(tmp_path, value, unit, marker, age):
    p, out = run_report(tmp_path, value, unit, marker, age=age)
    assert p.returncode == 3, p.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    report = (out / 'report.md').read_text()
    assert '论文卡片' in report and BOUNDARY in report
    assert '线性关联 RR：' not in report


def test_hour_conversion_and_targets(tmp_path):
    p, out = run_report(tmp_path, '0', 'h', '每周力量训练时长',
                        targets=f'marker,value,unit\n{INPUT_KEY},10,min\n')
    assert p.returncode == 0, p.stderr
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['targets']['relative_to_current']['rr'] == pytest.approx(0.98)
    assert levers['targets']['relative_to_current']['ci_lower'] == pytest.approx(0.97)
    assert levers['targets']['relative_to_current']['ci_upper'] == pytest.approx(0.99)
    p, out = run_report(tmp_path, str(10 / 60), 'h', '每周力量训练时长')
    assert p.returncode == 0, p.stderr
    assert json.loads((out / 'result.json').read_text())['outputs']['rr_vs_none']['value'] == pytest.approx(0.98)


def test_reverse_contrast_and_zero_are_algebraic_invariants():
    forward, reverse = contrast(10), contrast(-10)
    assert forward['rr'] * reverse['rr'] == pytest.approx(1)
    assert forward['ci_lower'] * reverse['ci_upper'] == pytest.approx(1)
    assert forward['ci_upper'] * reverse['ci_lower'] == pytest.approx(1)
    assert contrast(0) == {'rr': 1.0, 'ci_lower': 1.0, 'ci_upper': 1.0}


def test_invalid_target_removes_stale_outputs(tmp_path):
    p, out = run_report(tmp_path)
    assert p.returncode == 0
    p, out = run_report(tmp_path, targets=f'marker,value,unit\n{INPUT_KEY},10,kg\n')
    assert p.returncode == 3
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()


def test_missing_file_and_age_exit_three(tmp_path):
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                        '--out', str(tmp_path)], capture_output=True, text=True)
    assert p.returncode == 3
    keys = {x['key'] for x in json.loads((tmp_path / 'problems.json').read_text())['problems']}
    assert INPUT_KEY in keys and 'age' in keys


@pytest.mark.parametrize('contents', [None, 'marker,value,unit\nstrength_min_week,10,min,extra\n'])
def test_unreadable_or_malformed_file(tmp_path, contents):
    path = tmp_path / 'input.csv'
    if contents is not None:
        path.write_text(contents)
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                        '--measurements', str(path), '--age', '45', '--out', str(tmp_path / 'out')],
                       capture_output=True, text=True)
    assert p.returncode == 3, p.stderr
    assert (tmp_path / 'out/problems.json').exists()
    assert not (tmp_path / 'out/result.json').exists()
