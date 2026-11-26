"""Expectations transcribed from Kanis et al. (2008), Table 2, before implementation."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
FACTORS = ('parental_hip_fracture', 'current_smoking', 'high_alcohol',
           'rheumatoid_arthritis', 'oral_glucocorticoids', 'previous_fragility_fracture')
# Each row: major osteoporotic probability at ages 50,60,70,80, then hip at same ages.
PRINTED = {
    'male': [
        (2.8, 3.9, 5.7, 7.2, 0.1, 0.4, 1.3, 3.4),
        (5.5, 7.6, 9.1, 15, 0.2, 0.6, 2.8, 11),
        (2.8, 4.1, 5.9, 7.5, 0.2, 0.7, 1.8, 4.2),
        (3.3, 4.7, 7.1, 9.5, 0.2, 0.7, 2.0, 5.1),
        (3.7, 5.3, 8.0, 11, 0.2, 0.8, 2.3, 5.8),
        (4.4, 6.1, 8.5, 10, 0.3, 0.9, 2.4, 5.5),
        (5.8, 7.9, 11, 12, 0.5, 1.3, 2.7, 5.2),
    ],
    'female': [
        (3.5, 6.0, 11, 17, 0.2, 0.7, 2.3, 7.0),
        (6.9, 12, 17, 31, 0.3, 0.9, 5.0, 22),
        (3.6, 6.5, 12, 19, 0.3, 1.1, 3.4, 9.5),
        (4.1, 7.3, 14, 22, 0.3, 1.1, 3.6, 10),
        (4.7, 8.2, 15, 25, 0.4, 1.3, 4.1, 12),
        (5.6, 9.8, 18, 26, 0.5, 1.5, 4.8, 13),
        (7.4, 12, 20, 28, 0.8, 2.1, 4.9, 11),
    ],
}


def measurements(factor=None):
    return 'item,value,unit\nbmi_kg_m2,25,kg/m^2\n' + ''.join(
        f'{key},{int(key == factor)},1\n' for key in (*FACTORS, 'secondary_osteoporosis'))


def run(tmp_path, text=None, age='80', sex='female', targets=None):
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--out', str(tmp_path / 'out')]
    for flag, value in [('--age', age), ('--sex', sex)]:
        if value is not None:
            args += [flag, value]
    for flag, name, data in [('--measurements', 'input.csv', text), ('--targets', 'targets.csv', targets)]:
        if data is not None:
            path = tmp_path / name
            path.write_text(data)
            args += [flag, str(path)]
    return subprocess.run(args, text=True, capture_output=True), tmp_path / 'out'


def outputs(out):
    return {k: v['value'] for k, v in json.loads((out / 'result.json').read_text())['outputs'].items()}


@pytest.mark.parametrize('sex', ['male', 'female'])
def test_table_2_printed_values(tmp_path, sex):
    for factor, row in zip((None, *FACTORS), PRINTED[sex]):
        for col, age in enumerate((50, 60, 70, 80)):
            proc, out = run(tmp_path, measurements(factor), str(age), sex)
            assert proc.returncode == 0, proc.stderr
            got = outputs(out)
            assert got['major_osteoporotic_10y_pct'] == row[col]
            assert got['hip_fracture_10y_pct'] == row[col + 4]
            report = (out / 'report.md').read_text()
            assert report.index('论文卡片') < report.index('你的查表结果')
            assert '边界:' in report and '2008' in report


def test_manifest_matches_presets():
    sys.path.insert(0, str(ROOT / 'scripts'))
    import presets
    m = json.loads((ROOT / 'skill.json').read_text())
    specs = {s['key']: s for s in m['inputs']}
    assert tuple(presets.FACTORS) == FACTORS
    for key, (unit, bounds) in presets.INPUT_SPECS.items():
        assert (specs[key]['unit'], specs[key]['range']) == (unit, list(bounds))


@pytest.mark.parametrize('text,age,sex', [
    (None, '80', 'female'), (measurements(), None, 'female'),
    (measurements(), '80', None), (measurements(), '80', 'unknown'),
    (measurements(), 'nan', 'male'), (measurements(), '200', 'male'),
    (measurements(), '65', 'male'), (measurements(), '70.1', 'male'),
    (measurements().replace('25,kg/m^2', '25,mg/dL'), '80', 'female'),
    (measurements().replace('25,kg/m^2', '250,kg/m^2'), '80', 'female'),
    (measurements().replace('25,kg/m^2', '24.99,kg/m^2'), '80', 'female'),
    (measurements().replace('current_smoking,0', 'current_smoking,0.5'), '80', 'female'),
    (measurements().replace('secondary_osteoporosis,0', 'secondary_osteoporosis,1'), '80', 'female'),
    (measurements('parental_hip_fracture').replace('current_smoking,0', 'current_smoking,1'), '80', 'female'),
    (measurements().replace('high_alcohol,0,1\n', ''), '80', 'female'),
    (measurements() + 'T-score,-2.5,score\n', '80', 'female'),
    (measurements() + 'BMI,20,kg/m^2\n', '80', 'female'),
])
def test_invalid_inputs_exit_3(tmp_path, text, age, sex):
    proc, out = run(tmp_path, text, age, sex)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert all(v is None for v in outputs(out).values())
    report = (out / 'report.md').read_text()
    assert '论文卡片' in report and '边界:' in report
    assert '你的查表结果' not in report
    assert not (out / 'levers.json').exists()


def test_targets_use_printed_categories(tmp_path):
    proc, out = run(tmp_path, measurements('current_smoking'), targets='item,value,unit\ncurrent_smoking,0,1\n')
    assert proc.returncode == 0, proc.stderr
    data = json.loads((out / 'levers.json').read_text())
    assert data['schema'] == 'longevity-levers/1'
    assert data['current']['hip_fracture_10y_pct'] == 9.5
    assert data['targets']['outputs']['hip_fracture_10y_pct'] == 7.0
    assert data['levers'][0]['delta_percentage_points']['hip_fracture_10y_pct'] == 7.0 - 9.5
    assert len(data['sensitivity']) == 10


@pytest.mark.parametrize('target', [
    'bmi_kg_m2,24,kg/m^2', 'oral_glucocorticoids,0,1',
    'high_alcohol,1,1', 'current_smoking,0.5,1', 'unknown,0,1', '',
])
def test_bad_target_clears_stale_results(tmp_path, target):
    text = measurements('current_smoking')
    assert run(tmp_path, text)[0].returncode == 0
    proc, out = run(tmp_path, text, targets='item,value,unit\n' + target + '\n')
    assert proc.returncode == 3, proc.stderr
    assert all(v is None for v in outputs(out).values())
    assert not (out / 'levers.json').exists()


def test_chinese_aliases(tmp_path):
    text = measurements('parental_hip_fracture').replace('bmi_kg_m2', '体质指数').replace('parental_hip_fracture', '父母髋部骨折史')
    proc, out = run(tmp_path, text)
    assert proc.returncode == 0, proc.stderr
    assert outputs(out)['major_osteoporotic_10y_pct'] == 31
    assert outputs(out)['hip_fracture_10y_pct'] == 22
