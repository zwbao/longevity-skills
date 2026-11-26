"""Expected scores come from Methods, SARC-F questionnaire (0–10 points)."""
import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from personal_report import calculate, falls_points
from presets import INPUT_UNITS, ITEM_KEYS


def test_printed_falls_per_term():
    # Verbatim: "1 for respondents who reported falling 1–3 times in the past year"
    # Printed interval endpoints are inputs, printed per-term score is expected.
    for count in (1, 3):
        assert falls_points(count) == 1


def test_printed_other_falls_categories():
    # Same Methods paragraph: no falls -> 0; four or more falls -> 2.
    assert falls_points(0) == 0
    assert falls_points(4) == 2


def test_printed_scale_endpoints():
    # Methods explicitly prints 0=best, 10=worst, each component 0–2.
    assert calculate(dict.fromkeys(ITEM_KEYS, 0) | {'falls_past_year_count': 0})['sarc_f_score'] == 0
    assert calculate(dict.fromkeys(ITEM_KEYS, 2) | {'falls_past_year_count': 4})['sarc_f_score'] == 10


def test_printed_threshold():
    # Methods prints the total-score categories 0–3 and 4+.
    for strength, total, category in [(0, 3, '筛查阴性'), (1, 4, '筛查阳性')]:
        values = dict(zip(ITEM_KEYS, (strength, 1, 1, 0)))
        values['falls_past_year_count'] = 1
        result = calculate(values)
        assert result['sarc_f_score'] == total
        assert result['screening_category'] == category


def test_manifest_units():
    manifest = json.loads((ROOT / 'skill.json').read_text())
    assert {s['key']: s['unit'] for s in manifest['inputs']} == INPUT_UNITS


def run_cli(tmp_path, updates=None, omit=(), extra=(), age=None, sex=None):
    values = dict.fromkeys(ITEM_KEYS, 2) | {'falls_past_year_count': 4}
    values.update(updates or {})
    source = tmp_path / 'measurements.csv'
    with source.open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['marker', 'value', 'unit'])
        for key, value in values.items():
            if key not in omit:
                writer.writerow([key, *(value if isinstance(value, tuple) else (value, '1'))])
        writer.writerows(extra)
    out = tmp_path / 'out'
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
            '--measurements', str(source), '--out', str(out)]
    if age is not None:
        args += ['--age', age]
    if sex is not None:
        args += ['--sex', sex]
    return subprocess.run(args, capture_output=True, text=True), out


def test_report_and_result(tmp_path):
    proc, out = run_cli(tmp_path)
    assert proc.returncode == 0, proc.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    assert outputs['sarc_f_score']['value'] == 10  # printed worst score
    assert outputs['falls_score']['value'] == 2  # printed four-falls category
    report = (out / 'report.md').read_text()
    assert report.index('论文卡片') < report.index('你的结果')
    assert '边界:' in report and '不能确诊或排除肌少症' in report
    assert 'NHANES' in report


@pytest.mark.parametrize('updates,omit,extra,age,sex', [
    ({'strength_score': (1, 'kg')}, (), (), None, None),
    ({'strength_score': 3}, (), (), None, None),
    ({'walking_score': 0.5}, (), (), None, None),
    ({'falls_past_year_count': -1}, (), (), None, None),
    ({'falls_past_year_count': 1.5}, (), (), None, None),
    ({'falls_past_year_count': 'nan'}, (), (), None, None),
    ({}, ('chair_score',), (), None, None),
    ({}, (), [('strength_score', 0, '1')], None, None),
    ({}, (), [('unknown', 0, '1')], None, None),
    ({}, (), (), 'nan', None),
    ({}, (), (), '17', None),
    ({}, (), (), None, 'unknown'),
])
def test_bad_inputs_exit3_and_clear_stale(tmp_path, updates, omit, extra, age, sex):
    assert run_cli(tmp_path)[0].returncode == 0
    proc, out = run_cli(tmp_path, updates, omit, extra, age, sex)
    assert proc.returncode == 3, proc.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()
    report = (out / 'report.md').read_text()
    assert '这次没有计算' in report and '论文卡片' in report and '边界:' in report
    assert '你的结果' not in report


def test_aliases_and_optional_context(tmp_path):
    aliases = [('力量', 2, '1'), ('Assistance walking', 2, '1'),
               ('Rise from a chair', 2, '1'), ('Climb stairs', 2, '1'),
               ('过去一年跌倒次数', 4, '1')]
    proc, out = run_cli(tmp_path, omit=(*ITEM_KEYS, 'falls_past_year_count'),
                        extra=aliases, age='70', sex='女')
    assert proc.returncode == 0, proc.stderr
    assert json.loads((out / 'result.json').read_text())['outputs']['sarc_f_score']['value'] == 10


def test_missing_file_exit3(tmp_path):
    out = tmp_path / 'out'
    proc = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                           '--measurements', str(tmp_path / 'absent.csv'), '--out', str(out)])
    assert proc.returncode == 3
    assert (out / 'problems.json').exists()
