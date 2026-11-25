"""Expected values transcribed from Lee 2006 Tables 3/4, not fitted outputs."""
import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from personal_report import calculate, components, mortality_for_score
from presets import INPUT_UNITS, WEIGHTS


def baseline():
    return dict(age=50, sex=0, bmi_kg_m2=25, community_dwelling=1,
                **{key: 0 for key in WEIGHTS})


def test_table3_age_points():
    # Table 3 age cells: 60-64:1; 65-69:2; 70-74:3; 75-79:4;
    # 80-84:5; >=85:7. Reference age 50-59 is described in Methods.
    for age, points in [(50, 0), (59, 0), (60, 1), (64, 1), (65, 2),
                        (69, 2), (70, 3), (74, 3), (75, 4), (79, 4),
                        (80, 5), (84, 5), (85, 7)]:
        assert components(dict(baseline(), age=age))['age'] == points


def test_table3_terms_and_correction():
    expected = {'diabetes': 1, 'cancer': 2, 'lung_disease': 2,
                'heart_failure': 2, 'current_smoker': 2,
                'bathing_difficulty': 2, 'finances_difficulty': 2,
                'walking_difficulty': 2, 'pushing_difficulty': 1}
    # Table 3; diabetes=1 independently confirmed by JAMA 295(16):1900.
    for key, points in expected.items():
        assert components(dict(baseline(), **{key: 1}))[key] == points
    assert components(dict(baseline(), sex=1))['sex'] == 2
    assert components(dict(baseline(), bmi_kg_m2=24.9))['bmi_kg_m2'] == 1
    assert components(dict(baseline(), bmi_kg_m2=25))['bmi_kg_m2'] == 0


def test_table4_validation_rates():
    # Table 4, point score / validation cohort percent, including its
    # nonmonotone 11->12 rows. Do not smooth or pool these rows.
    printed = [(0, 1), (1, 2), (2, 2), (3, 4), (4, 6), (5, 8),
               (6, 9), (7, 15), (8, 20), (9, 20), (10, 28),
               (11, 45), (12, 44), (13, 59), (14, 64)]
    for score, percent in printed:
        assert mortality_for_score(score) == percent


def test_printed_comment_16_point_example():
    # Comment: "For example, a 75-year-old male smoker with heart failure,
    # difficulty bathing, walking, and managing finances ... his probability
    # of 4-year mortality is greater than 64% (16 points)".
    # BMI is not stated; a printed total of 16 implies the BMI<25 item is
    # absent (BMI 28 used here). Unlisted items absent for this illustration.
    person = dict(baseline(), age=75, sex=1, bmi_kg_m2=28, current_smoker=1,
                  heart_failure=1, bathing_difficulty=1, walking_difficulty=1,
                  finances_difficulty=1)
    result = calculate(person)
    assert result['lee_score'] == 16
    assert result['mortality_4y_pct'] == 64


@pytest.mark.xfail(strict=True, reason='Published 78-year example says age=3 and total=6; Table 3 gives age=4. Table 3 governs.')
def test_printed_78_year_example_unresolved():
    # Results / Risk Stratification by Points: printed inputs 78-year-old,
    # nonsmoking woman, BMI 28, diabetes and difficulty managing finances;
    # printed total risk score 6. Other listed conditions assumed absent
    # for this illustration only, never for incomplete user input.
    person = dict(baseline(), age=78, bmi_kg_m2=28, diabetes=1,
                  finances_difficulty=1)
    assert calculate(person)['lee_score'] == 6


def test_manifest_units():
    manifest = json.loads((ROOT / 'skill.json').read_text())
    assert {s['key']: s.get('unit') for s in manifest['inputs']} == INPUT_UNITS


def run_cli(tmp_path, updates=None, omit=(), targets=None, age='60', sex='female'):
    person = baseline()
    person.update(updates or {})
    source = tmp_path / 'measurements.csv'
    with source.open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['marker', 'value', 'unit'])
        for key, value in person.items():
            if key not in ('age', 'sex', *omit):
                writer.writerow([key, *(value if isinstance(value, tuple) else (value, INPUT_UNITS[key]))])
    out = tmp_path / 'out'
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
            '--measurements', str(source), '--out', str(out)]
    if age is not None:
        args += ['--age', age]
    if sex is not None:
        args += ['--sex', sex]
    if targets is not None:
        target_path = tmp_path / 'targets.csv'
        target_path.write_text('marker,value,unit\n' + targets)
        args += ['--targets', str(target_path)]
    result = subprocess.run(args, capture_output=True, text=True)
    return result, out


def test_report_and_result(tmp_path):
    proc, out = run_cli(tmp_path)
    assert proc.returncode == 0, proc.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    # 60-year age term=1 (Table 3), score 1 -> 2% (Table 4).
    assert outputs['lee_score']['value'] == 1
    assert outputs['mortality_4y_pct']['value'] == 2
    report = (out / 'report.md').read_text()
    assert report.index('论文卡片') < report.index('你的结果')
    assert '边界:' in report and '验证' in report
    assert len(json.loads((out / 'levers.json').read_text())['sensitivity']) == 12


@pytest.mark.parametrize('updates,omit,age,sex', [
    ({'bmi_kg_m2': (25, 'mg/dL')}, (), '60', 'female'),
    ({'bmi_kg_m2': 300}, (), '60', 'female'),
    ({'diabetes': 0.5}, (), '60', 'female'),
    ({'community_dwelling': 0}, (), '60', 'female'),
    ({}, ('heart_failure',), '60', 'female'),
    ({}, (), None, 'female'), ({}, (), '60', None),
    ({}, (), 'nan', 'female'), ({}, (), '49', 'female'),
    ({}, (), '60', 'unknown'),
])
def test_invalid_inputs_exit3(tmp_path, updates, omit, age, sex):
    # A preceding success must never survive a later input failure.
    assert run_cli(tmp_path)[0].returncode == 0
    proc, out = run_cli(tmp_path, updates, omit, age=age, sex=sex)
    assert proc.returncode == 3, proc.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    report = (out / 'report.md').read_text()
    assert '这次没有计算' in report and '论文卡片' in report
    assert '你的结果' not in report


def test_targets_and_discrete_sensitivity(tmp_path):
    proc, out = run_cli(tmp_path, updates={'current_smoker': 1},
                        targets='current_smoker,0,1\n')
    assert proc.returncode == 0, proc.stderr
    data = json.loads((out / 'levers.json').read_text())
    # Table 3: age 60=1 and smoking=2; Table 4: score3=4%, score1=2%.
    assert data['current']['lee_score'] == 3
    assert data['current']['mortality_4y_pct'] == 4
    assert data['targets']['lee_score'] == 1
    assert data['targets']['mortality_4y_pct'] == 2
    assert data['levers'][0]['lee_score_delta'] == -2


@pytest.mark.parametrize('target', ['bmi,25,mg/dL\n', 'current_smoker,0.5,1\n',
                                    'diabetes,0,1\n', 'age,55,a\n',
                                    'unknown_marker,1,1\n'])
def test_invalid_targets_exit3(tmp_path, target):
    proc, out = run_cli(tmp_path, targets=target)
    assert proc.returncode == 3, proc.stderr
    assert not (out / 'result.json').exists()
    assert (out / 'problems.json').exists()
