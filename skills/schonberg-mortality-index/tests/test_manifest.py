"""Expected scores and risks below are printed in Schonberg 2009, not generated."""
import csv
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())
# Discussion: woman aged 80 with no other risk factors. BMI=25 encodes the
# printed >=25 reference category, not a claimed exact BMI for this woman.
BASE = {'bmi_kg_m2': 25, 'health_code': 0, 'copd_history': 0,
        'cancer_history': 0, 'diabetes_history': 0, 'iadl_help': 0,
        'walking_difficulty': 0, 'smoking_code': 0, 'hospitalizations_count': 0}


def run_cli(tmp_path, values=None, age='80', sex='female', units=None, targets=None):
    path = tmp_path / 'input.csv'
    with path.open('w') as f:
        w = csv.writer(f)
        w.writerow(['marker', 'value', 'unit'])
        for k, v in (BASE if values is None else values).items():
            w.writerow([k, v, (units or {}).get(k, presets.INPUT_UNITS.get(k, '1'))])
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
           '--measurements', str(path), '--out', str(tmp_path / 'out')]
    if age is not None:
        cmd += ['--age', age]
    if sex is not None:
        cmd += ['--sex', sex]
    if targets is not None:
        target_path = tmp_path / 'targets.csv'
        with target_path.open('w') as f:
            w = csv.writer(f); w.writerow(['marker', 'value', 'unit'])
            for k, v in targets.items():
                w.writerow([k, v, presets.INPUT_UNITS.get(k, '1')])
        cmd += ['--targets', str(target_path)]
    return subprocess.run(cmd, capture_output=True, text=True)


def outputs(tmp_path):
    return {k: v['value'] for k, v in json.loads((tmp_path / 'out/result.json').read_text())['outputs'].items()}


def test_printed_discussion_example(tmp_path):
    # Discussion: woman aged 80, no other risk factors -> 5 points, 8%.
    result = run_cli(tmp_path)
    assert result.returncode == 0, result.stderr
    values = outputs(tmp_path)
    assert values['total_score'] == 5
    assert values['mortality_5y_pct'] == 8
    # Table 3 validation 4-5: 8 (6-10).
    assert values['mortality_5y_ci_low_pct'] == 6
    assert values['mortality_5y_ci_high_pct'] == 10
    text = (tmp_path / 'out/report.md').read_text()
    assert text.index('## 论文卡片') < text.index('## 你的结果')
    assert report.BOUNDARY in text


def test_printed_second_discussion_example():
    # Discussion: 80-year-old female, former smoker, COPD, diabetes,
    # shopping help, walking difficulty, fair health -> 17 points, >50%.
    person = dict(BASE, age_years=80, male=0, smoking_code=1, copd_history=1,
                  diabetes_history=1, iadl_help=1, walking_difficulty=1, health_code=2)
    result = report.calculate(person)
    assert result['total_score'] == 17
    assert result['mortality_5y_pct'] > 50
    # Table 3 validation 16-17: 55 (48-62).
    assert result['mortality_5y_pct'] == 55
    assert result['mortality_5y_ci_low_pct'] == 48
    assert result['mortality_5y_ci_high_pct'] == 62


def test_printed_table3_all_validation_rows():
    # Table 3, Point score; Validation: mortality and 95% confidence limits.
    rows = [(0, 1, 3, 1, 6), (2, 3, 5, 3, 8), (4, 5, 8, 6, 10),
            (6, 7, 12, 10, 15), (8, 9, 19, 16, 23), (10, 11, 29, 25, 33),
            (12, 13, 37, 32, 42), (14, 15, 49, 43, 55),
            (16, 17, 55, 48, 62), (18, 18, 62, 54, 70)]
    for lo, hi, mortality, ci_lo, ci_hi in rows:
        for score in (lo, hi):
            result = report.risk_for_score(score)
            assert result['mortality_5y_pct'] == mortality
            assert result['mortality_5y_ci_low_pct'] == ci_lo
            assert result['mortality_5y_ci_high_pct'] == ci_hi


def test_printed_table2_age_and_categories():
    person = dict(BASE, age_years=65, male=0)
    for age, points in [(65, 0), (69, 0), (70, 1), (74, 1), (75, 3),
                        (79, 3), (80, 5), (84, 5), (85, 7)]:
        assert report.score_terms(dict(person, age_years=age))['age_years'] == points
    for key, categories in {
        'male': [(0, 0), (1, 3)], 'bmi_kg_m2': [(24.9, 2), (25, 0)],
        'health_code': [(0, 0), (1, 1), (2, 2)],
        'smoking_code': [(0, 0), (1, 1), (2, 3)],
        'hospitalizations_count': [(0, 0), (1, 1), (2, 3)],
        'walking_difficulty': [(0, 0), (1, 3)],
        **{k: [(0, 0), (1, 2)] for k in ['copd_history', 'cancer_history', 'diabetes_history', 'iadl_help']}
    }.items():
        for value, expected in categories:
            assert report.score_terms(dict(person, **{key: value}))[key] == expected


def test_manifest_keys_units():
    specs = {s['key']: s for s in MANIFEST['inputs']}
    assert set(specs) == set(presets.INPUT_UNITS) | {'sex'}
    for key, unit in presets.INPUT_UNITS.items():
        assert specs[key]['unit'] == unit


def test_wrong_unit_and_range_exit3(tmp_path):
    for values, units in [(BASE, {'bmi_kg_m2': 'lb'}),
                          (dict(BASE, bmi_kg_m2=250), {})]:
        result = run_cli(tmp_path, values, units=units)
        assert result.returncode == 3, result.stderr
        assert (tmp_path / 'out/problems.json').exists()
        assert not (tmp_path / 'out/result.json').exists()
        assert '## 你的结果' not in (tmp_path / 'out/report.md').read_text()


def test_missing_invalid_and_stale_outputs(tmp_path):
    assert run_cli(tmp_path).returncode == 0
    bad_cases = [(dict(BASE, health_code=0.5), '80', 'female'),
                 (dict(BASE, smoking_code=float('nan')), '80', 'female'),
                 ({k:v for k,v in BASE.items() if k != 'cancer_history'}, '80', 'female'),
                 (BASE, None, 'female'), (BASE, 'not-a-number', 'female'),
                 (BASE, '64', 'female'), (BASE, '80.5', 'female'),
                 (BASE, '80', None), (BASE, '80', 'unknown')]
    for values, age, sex in bad_cases:
        result = run_cli(tmp_path, values, age=age, sex=sex)
        assert result.returncode == 3, result.stderr
        assert not (tmp_path / 'out/result.json').exists()
        assert not (tmp_path / 'out/levers.json').exists()
    assert run_cli(tmp_path).returncode == 0
    assert not (tmp_path / 'out/problems.json').exists()


def test_targets_and_discrete_sensitivity(tmp_path):
    # Baseline discussion score 5 / 8%; fair health moves to score 7.
    # Table 3 validation 6-7 -> 12%, so the contrast is 12 - 8.
    result = run_cli(tmp_path, targets={'health_code': 2})
    assert result.returncode == 0, result.stderr
    levers = json.loads((tmp_path / 'out/levers.json').read_text())
    assert levers['schema'] == 'longevity-levers/1'
    assert levers['current']['total_score'] == 5
    assert levers['targets']['total_score'] == 7
    assert levers['targets']['mortality_5y_pct'] == 12
    assert levers['levers'][0]['mortality_delta_pp'] == 12 - 8
    assert len(levers['sensitivity']) == 11
    for bad in [{'health_code': 0.5}, {'age_years': 70}, {'typo': 1},
                {'cancer_history': 1}]:
        assert run_cli(tmp_path, targets=bad).returncode == 3
        assert not (tmp_path / 'out/result.json').exists()


def test_chinese_aliases_and_equivalent_bmi_unit(tmp_path):
    # Same Discussion case; only input spelling/units change.
    values = dict(BASE)
    del values['bmi_kg_m2']
    values['体质指数'] = 25
    result = run_cli(tmp_path, values, sex='女', units={'体质指数': 'kg/m2'})
    assert result.returncode == 0, result.stderr
    assert outputs(tmp_path)['total_score'] == 5
    assert outputs(tmp_path)['mortality_5y_pct'] == 8


def test_joint_targets_recompute_and_preserve_smoking_history(tmp_path):
    # Table 3 validation: scores 6 and 7 both have 12%, against baseline 8%.
    result = run_cli(tmp_path, targets={'health_code': 1, 'hospitalizations_count': 1})
    assert result.returncode == 0, result.stderr
    levers = json.loads((tmp_path / 'out/levers.json').read_text())
    assert levers['targets']['mortality_5y_pct'] == 12
    assert levers['targets']['mortality_delta_pp'] == 12 - 8
    assert all(item['mortality_5y_pct'] == 12 for item in levers['levers'])
    result = run_cli(tmp_path, dict(BASE, smoking_code=2), targets={'smoking_code': 0})
    assert result.returncode == 3
    assert not (tmp_path / 'out/result.json').exists()
