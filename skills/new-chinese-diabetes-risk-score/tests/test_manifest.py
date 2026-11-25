"""Expected points transcribed BEFORE implementation from Table 2, p. 3947.

Each tuple is a printed bin endpoint and its printed Score, not a prediction
from this implementation. Interior and fractional boundaries are covered too.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets
import skillkit


@pytest.mark.parametrize('age,expected', [
    (20, 0), (24, 0), (25, 4), (34, 4), (35, 8), (39, 8),
    (40, 11), (44, 11), (45, 12), (49, 12), (50, 13), (54, 13),
    (55, 15), (59, 15), (60, 16), (64, 16), (65, 18), (74, 18),
])
def test_table2_age_points(age, expected):
    assert report.points('age', age) == expected


@pytest.mark.parametrize('bmi,expected', [(22, 1), (23.9, 1), (24, 3), (29.9, 3), (30, 5)])
def test_table2_bmi_points(bmi, expected):
    assert report.points('bmi_kg_m2', bmi) == expected


@pytest.mark.parametrize('male,female,expected', [
    (75, 70, 3), (79.9, 74.9, 3), (80, 75, 5), (84.9, 79.9, 5),
    (85, 80, 7), (89.9, 84.9, 7), (90, 85, 8), (94.9, 89.9, 8), (95, 90, 10),
])
def test_table2_sex_specific_waist(male, female, expected):
    assert report.points('waist_cm', male, 'male') == expected
    assert report.points('waist_cm', female, 'female') == expected


@pytest.mark.parametrize('sbp,expected', [
    (110, 1), (119, 1), (120, 3), (129, 3), (130, 6), (139, 6),
    (140, 7), (149, 7), (150, 8), (159, 8), (160, 10),
])
def test_table2_sbp_points(sbp, expected):
    assert report.points('sbp_mmhg', sbp) == expected


def test_table2_binary_points():
    # Table 2: Family history No 0 / Yes 6; Sex Women 0 / Men 2.
    assert report.points('family_history', 0) == 0
    assert report.points('family_history', 1) == 6
    assert report.points('sex', 0) == 0
    assert report.points('sex', 1) == 2


def test_printed_score_range():
    # Results p. 3947: "The point totals ranged from 0 to 51."
    # Combinations of the printed lowest/highest bins, not worked patients.
    low = dict(age=20, bmi_kg_m2=20, waist_cm=60, sbp_mmhg=100, family_history=0)
    high = dict(age=74, bmi_kg_m2=30, waist_cm=95, sbp_mmhg=160, family_history=1)
    assert report.compute(low, 'female')['total_score'] == 0
    assert report.compute(high, 'male')['total_score'] == 51


MANIFEST = json.loads((ROOT / 'skill.json').read_text(encoding='utf-8'))
ROWS = [('腰围', '95', 'cm'), ('BMI', '30', 'kg/m^2'),
        ('收缩压', '160', 'mmHg'), ('糖尿病家族史', '1', '1')]
FLAGS = ['--age', '74', '--sex', 'male', '--known-diabetes', 'no']


def csv_file(path, rows):
    path.write_text('marker,value,unit\n' + '\n'.join(','.join(map(str, row)) for row in rows) + '\n', encoding='utf-8')
    return path


def run(tmp_path, rows=None, flags=None, target_rows=None):
    source = csv_file(tmp_path / 'measurements.csv', ROWS if rows is None else rows)
    argv = ['--measurements', str(source), *(FLAGS if flags is None else flags), '--out', str(tmp_path / 'out')]
    if target_rows is not None:
        target = csv_file(tmp_path / 'targets.csv', target_rows)
        argv += ['--targets', str(target)]
    return report.main(argv)


def result(tmp_path):
    return json.loads((tmp_path / 'out/result.json').read_text())['outputs']


def test_manifest_units_ranges_and_outputs_agree():
    assert {s['key']: s['unit'] for s in MANIFEST['inputs']} == presets.INPUT_UNITS
    assert {s['key']: tuple(s['range']) for s in MANIFEST['inputs']} == presets.INPUT_RANGES
    assert MANIFEST['population']['age_years'] == list(presets.DERIVATION_AGES)
    high = dict(age=74, bmi_kg_m2=30, waist_cm=95, sbp_mmhg=160, family_history=1)
    assert set(report.compute(high, 'male')) == {s['key'] for s in MANIFEST['outputs']}


def test_normal_cli_reproduces_printed_upper_range_and_paper_card(tmp_path):
    assert run(tmp_path) == 0
    output = result(tmp_path)
    assert output['total_score']['value'] == 51  # Results p.3947 printed maximum.
    assert output['age_points']['value'] == 18
    assert output['sex_points']['value'] == 2
    assert output['waist_cm_points']['value'] == 10
    assert output['bmi_kg_m2_points']['value'] == 5
    assert output['sbp_mmhg_points']['value'] == 10
    assert output['family_history_points']['value'] == 6
    text = (tmp_path / 'out/report.md').read_text()
    assert text.index('论文卡片') < text.index('你的评分')
    assert '10.2337/dc13-0593' in text and '边界：' + presets.BOUNDARY in text
    assert not (tmp_path / 'out/problems.json').exists()
    payload = json.loads((tmp_path / 'out/levers.json').read_text())
    assert payload['current']['total_score'] == 51
    assert len(payload['sensitivity']) == 6 and 'targets' not in payload


def test_published_cutoff_is_inclusive():
    assert presets.CUTOFF == 25
    assert report.category(25) == '达到筛查阈值'
    assert report.category(25 - 1) == '低于筛查阈值'


def test_fractional_boundaries_follow_methods_not_rounded_table_labels():
    # Methods p.3945: >=22 and <24; >=75 and <80; >=110 and <120.
    assert report.points('bmi_kg_m2', 23.99) == 1
    assert report.points('waist_cm', 79.99, 'male') == 3
    assert report.points('sbp_mmhg', 119.99) == 1
    assert report.points('bmi_kg_m2', 21.99) == 0
    assert report.points('waist_cm', 69.99, 'female') == 0
    assert report.points('sbp_mmhg', 109.99) == 0


def test_accepted_units_convert_and_preserve_score(tmp_path):
    rows = [('waist circumference', str(95 / 2.54), 'in'), ('body mass index', '30', 'kg/m²'),
            ('SBP', str(161 / 7.500617), 'kPa'), ('family history of diabetes', '1', '1')]
    assert run(tmp_path, rows) == 0
    assert result(tmp_path)['total_score']['value'] == 51
    for unit, number in [('m', .95), ('mm', 950)]:
        rows[0] = ('腰围', str(number), unit)
        assert run(tmp_path, rows) == 0
        assert result(tmp_path)['waist_cm_points']['value'] == 10


@pytest.mark.parametrize('rows,flags', [
    ([('腰围', '95', 'mg/dL'), *ROWS[1:]], FLAGS),
    ([('腰围', '95', ''), *ROWS[1:]], FLAGS),
    ([('腰围', '950', 'cm'), *ROWS[1:]], FLAGS),
    (ROWS[:-1], FLAGS),
    ([*ROWS[:-1], ('糖尿病家族史', '0.5', '1')], FLAGS),
    ([*ROWS[:-1], ('糖尿病家族史', '未知', '1')], FLAGS),
    ([('腰围', 'nan', 'cm'), *ROWS[1:]], FLAGS),
    ([('腰围', 'inf', 'cm'), *ROWS[1:]], FLAGS),
    ([*ROWS, ('腰围', '90', 'cm')], FLAGS),
    (ROWS, []),
    (ROWS, ['--age', '75', '--sex', 'male', '--known-diabetes', 'no']),
    (ROWS, ['--age', '19', '--sex', 'male', '--known-diabetes', 'no']),
    (ROWS, ['--age', '40.5', '--sex', 'male', '--known-diabetes', 'no']),
    (ROWS, ['--age', 'oops', '--sex', 'male', '--known-diabetes', 'no']),
    (ROWS, ['--age', 'NaN', '--sex', 'male', '--known-diabetes', 'no']),
    (ROWS, ['--age', '50', '--sex', 'unknown', '--known-diabetes', 'no']),
    (ROWS, ['--age', '50', '--sex', 'male', '--known-diabetes', 'yes']),
    (ROWS, ['--age', '50', '--sex', 'male', '--known-diabetes', 'unknown']),
])
def test_invalid_inputs_exit_three_and_clear_stale_outputs(tmp_path, rows, flags):
    assert run(tmp_path) == 0
    assert run(tmp_path, rows, flags) == skillkit.EXIT_INPUT_PROBLEM == 3
    assert json.loads((tmp_path / 'out/problems.json').read_text())['problems']
    assert not (tmp_path / 'out/result.json').exists()
    assert not (tmp_path / 'out/levers.json').exists()
    text = (tmp_path / 'out/report.md').read_text()
    assert '总分：' not in text and '这次没有计算' in text
    assert text.index('论文卡片') < text.index('输入没有通过检查')
    assert presets.BOUNDARY in text


def test_missing_file_reports_input_problem(tmp_path):
    assert report.main(['--measurements', str(tmp_path / 'absent.csv'), *FLAGS, '--out', str(tmp_path / 'out')]) == 3
    assert (tmp_path / 'out/problems.json').exists()


@pytest.mark.parametrize('targets', [
    [('收缩压', '120', 'mg/dL')], [('BMI', '100', 'kg/m^2')],
    [('age', '40', 'a')], [('family_history', '0', '1')],
    [('typo', '80', 'cm')], [('腰围', 'nan', 'cm')], [],
])
def test_invalid_targets_fail_without_score(tmp_path, targets):
    assert run(tmp_path, target_rows=targets) == 3
    assert not (tmp_path / 'out/result.json').exists()
    assert (tmp_path / 'out/problems.json').exists()


def test_target_scenarios_and_step_sensitivity(tmp_path):
    assert run(tmp_path, target_rows=[('腰围', '90', 'cm'), ('BMI', '24', 'kg/m^2'), ('收缩压', '130', 'mmHg')]) == 0
    data = json.loads((tmp_path / 'out/levers.json').read_text())
    # All expectations below are differences/sums of printed Table 2 terms.
    expected_delta = {'waist_cm': 8 - 10, 'bmi_kg_m2': 3 - 5, 'sbp_mmhg': 6 - 10}
    assert {s['key']: s['score_delta'] for s in data['levers']} == expected_delta
    assert data['targets']['total_score'] == sum([18, 2, 8, 3, 6, 6])
    assert data['targets']['score_delta'] == sum(expected_delta.values())
    assert data['targets']['screening_category'] == report.category(data['targets']['total_score'])
    waist = next(s for s in data['sensitivity'] if s['key'] == 'waist_cm')
    assert waist['score_delta'] == 0
    assert waist['lower_band'] == {'below_exclusive': 95, 'score_delta': 8 - 10}
    assert not waist['not_a_target']
    assert all(s['not_a_target'] for s in data['sensitivity'] if s['key'] in ('age', 'sex', 'family_history'))
    assert '个人三年发病概率' in (tmp_path / 'out/report.md').read_text()


def test_population_extremes_warn_for_current_and_targets(tmp_path):
    assert run(tmp_path, [('腰围', '125', 'cm'), *ROWS[1:]], target_rows=[('BMI', '45', 'kg/m^2')]) == 0
    data = json.loads((tmp_path / 'out/levers.json').read_text())
    assert any('腰围' in s for s in data['warnings_zh'])
    assert any('体质指数' in s for s in data['targets']['warnings_zh'])
    assert '外推' in (tmp_path / 'out/report.md').read_text()


def test_female_and_zero_history_are_not_missing(tmp_path):
    rows = [('腰围', '60', 'cm'), ('BMI', '20', 'kg/m^2'), ('收缩压', '100', 'mmHg'), ('糖尿病家族史', '0', '1')]
    assert run(tmp_path, rows, ['--age', '20', '--sex', '女', '--known-diabetes', '否']) == 0
    assert result(tmp_path)['total_score']['value'] == 0


def test_malformed_csv_reports_input_problem(tmp_path):
    source = tmp_path / 'bad.csv'
    source.write_text('marker,value,unit\n腰围,95,cm,extra\n')
    assert report.main(['--measurements', str(source), *FLAGS, '--out', str(tmp_path / 'out')]) == 3
    assert (tmp_path / 'out/problems.json').exists()
    assert not (tmp_path / 'out/result.json').exists()
