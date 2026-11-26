"""Original Appendix, p. 212, component 5, printed cells:
Sum of # 5b-5j    Component 5 score
0  0
1-9  1
10-18  2
19-27  3
Expected scores below come from the printed tables, not program output.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def test_appendix_disturbance_scores():
    from personal_report import disturbance_score
    assert disturbance_score(0) == 0
    for total in range(1, 10):
        assert disturbance_score(total) == 1
    for total in range(10, 19):
        assert disturbance_score(total) == 2
    for total in range(19, 28):
        assert disturbance_score(total) == 3


@pytest.mark.parametrize('minutes,expected', [(0, 0), (15, 0), (16, 1), (30, 1), (31, 2), (60, 2), (61, 3)])
def test_appendix_latency(minutes, expected):
    from personal_report import latency_score
    assert latency_score(minutes) == expected


@pytest.mark.parametrize('total,expected', [(0, 0), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3)])
def test_appendix_pair_sum(total, expected):
    # pp. 211, 213: component 2 and component 7 recoding.
    from personal_report import pair_score
    assert pair_score(total) == expected


@pytest.mark.parametrize('hours,expected', [(8, 0), (7, 1), (6.5, 1), (5.5, 2), (5, 2), (4, 3)])
def test_appendix_duration(hours, expected):
    from personal_report import duration_score
    assert duration_score(hours) == expected


@pytest.mark.parametrize('pct,expected', [(86, 0), (84, 1), (75, 1), (74, 2), (65, 2), (64, 3)])
def test_appendix_efficiency(pct, expected):
    from personal_report import efficiency_score
    assert efficiency_score(pct) == expected


def test_manifest_matches_presets():
    from presets import MEASUREMENTS
    manifest = json.loads((ROOT / 'skill.json').read_text())
    assert {x['key']: (x['unit'], tuple(x['range'])) for x in manifest['inputs']
            if x['from'] == 'measurements'} == MEASUREMENTS


# Artificial complete questionnaire, not a participant published in the paper.
# All component scores are zero, corresponding to the printed p. 211 global
# endpoint 0 (no difficulty); the maximum endpoint printed there is 21.
VALID = [('bedtime_min', '1380', 'min'), ('rise_time_min', '420', 'min'),
         ('sleep_latency_min', '15', 'min'), ('sleep_duration_h', '8', 'h')]
VALID += [(f'q5{letter}_code', '0', 'score') for letter in 'abcdefghij']
VALID += [(f'q{n}_code', '0', 'score') for n in (6, 7, 8, 9)]


def run_report(tmp_path, changes=None, omit=(), extra=()):
    rows = [(k, *(changes or {}).get(k, (v, u))) for k, v, u in VALID if k not in omit]
    path = tmp_path / 'input.csv'
    path.write_text('marker,value,unit\n' + '\n'.join(','.join(r) for r in rows) + '\n')
    out = tmp_path / 'out'
    proc = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                           '--measurements', str(path), '--out', str(out), *extra],
                          capture_output=True, text=True)
    return proc, out


def test_result_and_report(tmp_path):
    proc, out = run_report(tmp_path)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    assert result['psqi_global_score']['value'] == 0
    assert all(result[f'component_{n}_score']['value'] == 0 for n in range(1, 8))
    report = (out / 'report.md').read_text()
    assert report.index('## 论文卡片') < report.index('## 你的结果')
    assert '边界:' in report
    assert not (out / 'problems.json').exists()


def test_printed_maximum_endpoint(tmp_path):
    changes = {k: ('3', 'score') for k, _, u in VALID if u == 'score'}
    changes.update(sleep_duration_h=('4', 'h'), sleep_latency_min=('61', 'min'))
    proc, out = run_report(tmp_path, changes)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / 'result.json').read_text())['outputs']
    assert all(result[f'component_{n}_score']['value'] == 3 for n in range(1, 8))
    assert result['psqi_global_score']['value'] == 21
    assert result['sleep_quality_category']['value'] == 'above_cutoff'


@pytest.mark.parametrize('total,expected', [(5, 'not_above_cutoff'), (6, 'above_cutoff')])
def test_strict_cutoff(total, expected):
    from personal_report import classify
    assert classify(total) == expected


@pytest.mark.parametrize('key,value,unit', [
    ('sleep_duration_h', '8', 'mg/dL'), ('sleep_duration_h', '25', 'h'),
    ('q5b_code', '4', 'score'), ('q5a_code', '0.5', 'score'),
    ('sleep_duration_h', 'nan', 'h'), ('sleep_latency_min', '15.5', 'min'),
    ('bedtime_min', '1440', 'min'), ('rise_time_min', '1380', 'min'),
    ('sleep_duration_h', '9', 'h'),  # exceeds the reported eight hours in bed
    ('sleep_latency_min', '600', 'min'),
    ('sleep_duration_h', '6', 'h'),  # overlapping original duration intervals
    ('sleep_duration_h', '6.8', 'h'),  # exactly 85%, not covered in original table
    ('sleep_duration_h', '6.76', 'h'),  # 84.5%, no printed rounding rule
    ('sleep_duration_h', '5.96', 'h'),  # 74.5%, no printed rounding rule
])
def test_wrong_or_ambiguous_input_exits_three(tmp_path, key, value, unit):
    proc, out = run_report(tmp_path, {key: (value, unit)})
    assert proc.returncode == 3, proc.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()
    report = (out / 'report.md').read_text()
    assert '## 论文卡片' in report and '边界:' in report
    assert '## 你的结果' not in report


@pytest.mark.parametrize('key', [r[0] for r in VALID])
def test_every_missing_input_exits_three(tmp_path, key):
    proc, out = run_report(tmp_path, omit=(key,))
    assert proc.returncode == 3
    assert any(p['key'] == key and p['kind'] == 'missing'
               for p in json.loads((out / 'problems.json').read_text())['problems'])


def test_units_and_aliases(tmp_path):
    proc, out = run_report(tmp_path, {'sleep_duration_h': ('480', 'min'), 'sleep_latency_min': ('900', 's')})
    assert proc.returncode == 0, proc.stderr
    assert json.loads((out / 'result.json').read_text())['outputs']['psqi_global_score']['value'] == 0
    import skillkit
    manifest = skillkit.load_manifest(str(ROOT / 'scripts/personal_report.py'))
    path = tmp_path / 'alias.csv'
    path.write_text('marker,value,unit\n入睡潜伏期,15,min\nHours of sleep,480,min\n')
    values = skillkit.collect_file(path, manifest).values
    assert values['sleep_latency_min'] == 15 and values['sleep_duration_h'] == 8


@pytest.mark.parametrize('extra', [('--age', 'abc'), ('--age', '10'), ('--sex', 'invalid')])
def test_invalid_context(tmp_path, extra):
    assert run_report(tmp_path, extra=extra)[0].returncode == 3


def test_stale_outputs(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    proc, out = run_report(tmp_path, omit=('q5j_code',))
    assert proc.returncode == 3 and not (out / 'result.json').exists()
    assert run_report(tmp_path)[0].returncode == 0
    assert not (out / 'problems.json').exists()
