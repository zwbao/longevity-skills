"""Printed examples transcribed before implementation: Table 2 and corrected Table S8."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
OUTCOMES = ('all_cause_mortality', 'cvd_incidence', 'cvd_mortality',
            'cancer_incidence', 'cancer_mortality', 'type2_diabetes',
            'dementia', 'depressive_symptoms', 'falls')


def run(tmp_path, text=None, target=None, extra=()):
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--out', str(tmp_path / 'out')]
    for flag, content, name in [('--measurements', text, 'input.csv'), ('--targets', target, 'targets.csv')]:
        if content is not None:
            path = tmp_path / name
            path.write_text(content, encoding='utf-8')
            args += [flag, str(path)]
    return subprocess.run(args + list(extra), capture_output=True, text=True), tmp_path / 'out'


def values(out):
    return {k: v['value'] for k, v in json.loads((out / 'result.json').read_text())['outputs'].items()}


def assert_cells(got, expected):
    for key, cell in zip(OUTCOMES, expected):
        for suffix, value in zip(('hr', 'ci_lower', 'ci_upper'), cell):
            assert got[f'{key}_{suffix}'] == value


def test_table_2_7000_printed(tmp_path):
    # Table 2 p e676, 7000 row. Diabetes upper CI is 1.00 here, not abstract 0.99.
    expected = [(0.53, 0.46, 0.60), (0.75, 0.67, 0.85), (0.53, 0.37, 0.77),
                (0.94, 0.87, 1.01), (0.63, 0.55, 0.72), (0.86, 0.74, 1.00),
                (0.62, 0.53, 0.73), (0.78, 0.73, 0.83), (0.72, 0.65, 0.81)]
    result, out = run(tmp_path, 'item,value,unit\ndaily_steps_per_day,7000,1\n')
    assert result.returncode == 0, result.stderr
    got = values(out)
    assert got['daily_steps_per_day'] == 7000
    assert got['reference_steps_per_day'] == 2000
    assert_cells(got, expected)
    report = (out / 'report.md').read_text()
    assert report.index('论文卡片') < report.index('你的查表结果')
    assert '边界:' in report and '不是个人发病或死亡概率' in report


def test_corrected_s8_10000_printed(tmp_path):
    # Corrected appendix p82, 10,000 row; deliberately distinct from Table 2.
    expected = [(0.90, 0.86, 0.94), (0.93, 0.91, 0.95), (1.68, 1.02, 2.78),
                (0.97, 0.93, 1.01), (0.90, 0.82, 0.98), (0.96, 0.86, 1.07),
                (0.88, 0.79, 0.98), (0.86, 0.79, 0.93), (1.01, 0.93, 1.09)]
    result, out = run(tmp_path, 'item,value,unit\ndaily_steps_per_day,10000,1\n', extra=('--reference-steps', '7000'))
    assert result.returncode == 0, result.stderr
    got = values(out)
    assert got['daily_steps_per_day'] == 10000
    assert got['reference_steps_per_day'] == 7000
    assert_cells(got, expected)
    assert '不能直接比较' in (out / 'report.md').read_text()


@pytest.mark.parametrize('steps,expected', [
    (3000, (0.77, 0.71, 0.83)), (4000, (0.64, 0.57, 0.73)),
    (5000, (0.57, 0.50, 0.66)), (6000, (0.54, 0.47, 0.62)),
    (8000, (0.52, 0.46, 0.60)), (9000, (0.52, 0.46, 0.60)),
    (10000, (0.52, 0.45, 0.59)), (11000, (0.49, 0.43, 0.57)),
    (12000, (0.45, 0.39, 0.53)),
])
def test_table_2_other_mortality_rows(tmp_path, steps, expected):
    result, out = run(tmp_path, f'item,value,unit\n日均步数,{steps},1\n')
    assert result.returncode == 0, result.stderr
    assert_cells(values(out), [expected])


def test_manifest_matches_presets():
    import presets
    m = json.loads((ROOT / 'skill.json').read_text())
    spec = next(s for s in m['inputs'] if s['from'] == 'measurements')
    assert (spec['key'], spec['unit'], spec['range']) == (presets.INPUT_KEY, presets.INPUT_UNIT, list(presets.PLAUSIBLE_RANGE))
    assert spec['accept'] == {}
    assert tuple(presets.OUTCOMES) == OUTCOMES
    assert set(presets.TABLES[2000]) == set(range(2000, 12001, 1000))
    assert set(presets.TABLES[7000]) == set(range(7000, 12001, 1000))


@pytest.mark.parametrize('text', [None, 'item,value,unit\n',
    'item,value,unit\ndaily_steps_per_day,7000,km\n',
    'item,value,unit\ndaily_steps_per_day,100001,1\n',
    'item,value,unit\ndaily_steps_per_day,nan,1\n',
    'item,value,unit\ndaily_steps_per_day,7500,1\n',
    'item,value,unit\ndaily_steps_per_day,1000,1\n',
    'item,value,unit\ndaily_steps_per_day,13000,1\n',
    'item,value,unit\ndaily_steps_per_day,7000,1\n日均步数,8000,1\n'])
def test_invalid_input(tmp_path, text):
    result, out = run(tmp_path, text)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert all(v is None for v in values(out).values())
    assert not (out / 'levers.json').exists()
    report = (out / 'report.md').read_text()
    assert '论文卡片' in report and '边界:' in report
    assert '你的查表结果' not in report


def test_targets_and_profile(tmp_path):
    result, out = run(tmp_path, 'item,value,unit\nmean daily steps,7000,1\n',
                      'item,value,unit\n日均步数,10000,1\n', extra=('--age', '65', '--sex', 'female'))
    assert result.returncode == 0, result.stderr
    lev = json.loads((out / 'levers.json').read_text())
    assert lev['current']['all_cause_mortality_hr'] == 0.53
    assert lev['targets']['outputs']['all_cause_mortality_hr'] == 0.52
    assert lev['levers'][0]['hr_delta']['all_cause_mortality_hr'] == pytest.approx(0.52 - 0.53)
    assert [v['daily_steps_per_day'] for v in lev['sensitivity'][0]['neighbors']] == [6000, 8000]
    # S8 mortality 0.90 must never be obtained by rebasing the Table 2 outputs.
    assert lev['targets']['outputs']['reference_steps_per_day'] == 2000


@pytest.mark.parametrize('ref', [2000, 7000])
def test_reference_preserves_unprinted_ci(tmp_path, ref):
    result, out = run(tmp_path, f'item,value,unit\ndaily_steps_per_day,{ref},1\n', extra=('--reference-steps', str(ref)))
    assert result.returncode == 0, result.stderr
    assert_cells(values(out), [(1, None, None)] * 9)


def test_bad_target_clears_stale_output(tmp_path):
    text = 'item,value,unit\ndaily_steps_per_day,7000,1\n'
    result, out = run(tmp_path, text)
    assert result.returncode == 0
    result, out = run(tmp_path, text, 'item,value,unit\ndaily_steps_per_day,7500,1\n')
    assert result.returncode == 3
    assert all(v is None for v in values(out).values())
    assert not (out / 'levers.json').exists()


@pytest.mark.parametrize('extra', [('--reference-steps', '5000'), ('--reference-steps', '7000'), ('--age', '17'), ('--age', 'nan'), ('--sex', 'unknown')])
def test_bad_arguments(tmp_path, extra):
    result, out = run(tmp_path, 'item,value,unit\ndaily_steps_per_day,4000,1\n', extra=extra)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
