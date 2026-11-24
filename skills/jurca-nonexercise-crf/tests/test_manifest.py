"""Printed worksheet checks; the full worked example is explicitly unresolved."""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets
import skillkit

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


def paper_inputs(metric=False):
    # Discussion p.191: 45-year-old male, 193 lb (87.7 kg), 68 in
    # (172 cm), resting HR 72, Level 2. Figure 1 prints BMI factor 703.
    bmi = 87.7 / (172 / 100) ** 2 if metric else 193 * 703 / 68 ** 2
    return {'age': 45, 'sex': 1, 'bmi_kg_m2': bmi,
            'resting_hr_bpm': 72, 'activity_level': 2}


@pytest.mark.parametrize('metric', [False, True])
@pytest.mark.xfail(strict=True, reason='Printed Table 5/Figure 1 constants do not reproduce p.191; validation remains draft')
def test_paper_worked_example(metric):
    # Printed output, not an output made by this implementation.
    assert report.estimate(paper_inputs(metric)) == pytest.approx(9.02, abs=0.005)


@pytest.mark.parametrize('level,score', [(1, 0.00), (2, 0.32), (3, 1.06), (4, 1.76), (5, 3.03)])
def test_figure1_activity_scores(level, score):
    assert report.terms({**paper_inputs(), 'activity_level': level})['activity_level'] == score


def test_manifest_matches_presets():
    declared = {i['key']: i['unit'] for i in MANIFEST['inputs']}
    assert declared == presets.INPUT_UNITS
    assert MANIFEST['validation']['status'] == 'draft'
    assert MANIFEST['inputs_status'] == 'draft'


def csv_file(path, rows):
    path.write_text('marker,value,unit\n' + '\n'.join(','.join(map(str, r)) for r in rows) + '\n')
    return path


def rows():
    return [('体质指数', paper_inputs()['bmi_kg_m2'], 'kg/m²'),
            ('静息心率', 72, '次/分钟'), ('活动等级', 2, 'score')]


def run(tmp_path, data=None, extra=None):
    source = csv_file(tmp_path / 'measurements.csv', rows() if data is None else data)
    return report.main(['--measurements', str(source), '--age', '45', '--sex', '男',
                        '--out', str(tmp_path / 'out')] + (extra or []))


def test_normal_report_and_machine_outputs(tmp_path):
    assert run(tmp_path) == 0
    result = json.loads((tmp_path / 'out/result.json').read_text())
    value = result['outputs']['estimated_crf_met']['value']
    assert math.isfinite(value)
    assert result['outputs']['activity_score_met']['value'] == 0.32
    text = (tmp_path / 'out/report.md').read_text()
    assert text.index('## 论文卡片') < text.index('## 你的估计结果')
    assert '9.02' in text and '暂定' in text and f'{value:.2f} MET' in text
    assert presets.BOUNDARY in text
    levers = json.loads((tmp_path / 'out/levers.json').read_text())
    slopes = {s['key']: s.get('met_per_unit') for s in levers['sensitivity']}
    # Table 5, NASA column: printed regression coefficients.
    assert slopes['bmi_kg_m2'] == -0.17
    assert slopes['resting_hr_bpm'] == -0.03
    assert slopes['age'] == -0.10
    assert slopes['sex'] == 2.77


@pytest.mark.parametrize('bad_rows,extra', [
    ([('BMI', 30, 'mg/dL'), ('RHR', 72, 'bpm'), ('活动等级', 2, 'score')], []),
    ([('BMI', 300, 'kg/m2'), ('RHR', 72, 'bpm'), ('活动等级', 2, 'score')], []),
    (rows()[:-1], []),
    (rows()[:-1] + [('活动等级', 2.5, 'score')], []),
    (rows(), ['--age', '71']),
    (rows(), ['--age', 'nonsense']),
    (rows(), ['--sex', 'unknown']),
    (rows(), ['--age', 'nan']),
])
def test_invalid_input_exits_three_without_result(tmp_path, bad_rows, extra):
    assert run(tmp_path, bad_rows, extra) == 3
    out = tmp_path / 'out'
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    text = (out / 'report.md').read_text()
    assert '## 你的估计结果' not in text
    assert '## 论文卡片' in text and presets.BOUNDARY in text


def test_missing_inputs_and_unreadable_file(tmp_path):
    assert report.main(['--out', str(tmp_path / 'out')]) == 3
    assert report.main(['--measurements', str(tmp_path / 'absent.csv'), '--out', str(tmp_path / 'out')]) == 3


def test_target_activity_uses_printed_score_not_linear_level(tmp_path):
    targets = csv_file(tmp_path / 'targets.csv', [('活动等级', 5, 'score')])
    assert run(tmp_path, extra=['--targets', str(targets)]) == 0
    data = json.loads((tmp_path / 'out/levers.json').read_text())
    # Figure 1 prints score 3.03 for Level 5 and 0.32 for Level 2.
    assert data['levers'][0]['estimated_crf_met_delta'] == pytest.approx(3.03 - 0.32)
    assert data['targets']['estimated_crf_met_delta'] == pytest.approx(3.03 - 0.32)
    choices = next(s['categories'] for s in data['sensitivity'] if s['key'] == 'activity_level')
    assert [c['score_met'] for c in choices] == [0.00, 0.32, 1.06, 1.76, 3.03]


@pytest.mark.parametrize('target_rows', [
    [('RHR', 60, 'mg/dL')], [('activity_level', 2.5, 'score')],
    [('age', 40, 'a')], [('sex', 0, '1')], [('unknown', 20, '1')],
    [('RHR', 5, 'bpm')], [('BMI', '', 'kg/m2')],
    [('RHR', 72, 'bpm'), ('BMI', '', 'kg/m2')],
])
def test_invalid_targets_clear_stale_outputs(tmp_path, target_rows):
    assert run(tmp_path) == 0
    targets = csv_file(tmp_path / 'targets.csv', target_rows)
    assert run(tmp_path, extra=['--targets', str(targets)]) == 3
    assert not (tmp_path / 'out/levers.json').exists()
    assert not (tmp_path / 'out/result.json').exists()


def test_combined_targets_preserve_current_and_sum_independent_changes(tmp_path):
    assert run(tmp_path) == 0
    current = json.loads((tmp_path / 'out/result.json').read_text())
    targets = csv_file(tmp_path / 'targets.csv', [
        ('BMI', paper_inputs()['bmi_kg_m2'] + 1, 'kg/m2'), ('RHR', 72 - 1, 'bpm'),
        ('活动等级', 5, 'score'),
    ])
    assert run(tmp_path, extra=['--targets', str(targets)]) == 0
    assert json.loads((tmp_path / 'out/result.json').read_text()) == current
    data = json.loads((tmp_path / 'out/levers.json').read_text())
    # Each numerical expectation is a printed coefficient or Figure 1 score.
    assert [x['estimated_crf_met_delta'] for x in data['levers']] == pytest.approx(
        [-0.17, 0.03, 3.03 - 0.32])
    assert data['targets']['estimated_crf_met_delta'] == pytest.approx(-0.17 + 0.03 + 3.03 - 0.32)
