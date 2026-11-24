"""Printed parameter checks and synthetic CLI checks, NOT paper case reproduction.

Sources: Supplementary Data 1, MitoAge!G2:G28; Table 2 (PDF p. 5).
No participant's complete inputs plus prediction are published.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


def run(tmp_path, *, value='0', unit='1', sex='female', age='54', omit=None, targets=None, preprocessing='somascan-1.3k-ln-qc'):
    source = tmp_path / 'measurements.csv'
    with source.open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['marker', 'value', 'unit'])
        for feature in presets.PROTEINS:
            if feature['key'] != omit:
                writer.writerow([feature['seq_id'], value, unit])
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(source), '--out', str(tmp_path / 'out')]
    if sex is not None:
        args += ['--sex', sex]
    if age is not None:
        args += ['--age', age]
    if preprocessing is not None:
        args += ['--preprocessing', preprocessing]
    if targets is not None:
        target = tmp_path / 'targets.csv'
        target.write_text(targets)
        args += ['--targets', str(target)]
    return subprocess.run(args, capture_output=True, text=True)


def test_printed_parameters_and_manifest():
    # These are constants, not a claimed worked example.
    assert presets.INTERCEPT == 7.49653775853267
    assert presets.SEX_MALE_WEIGHT == -0.120048854106948
    assert presets.WEIGHTS['ccl2_ln_rfu'] == -0.433005733637459
    specs = {s['key']: s for s in MANIFEST['inputs'] if s['from'] == 'measurements'}
    assert len(specs) == len(presets.PROTEINS) == 25
    assert set(specs) == set(presets.WEIGHTS)
    for p in presets.PROTEINS:
        assert specs[p['key']]['unit'] == presets.INPUT_UNIT
        assert specs[p['key']]['range'] == list(presets.INPUT_RANGE)
        assert p['seq_id'] in specs[p['key']]['aliases']
    assert MANIFEST['validation']['status'] == 'draft'
    assert MANIFEST['inputs_status'] == 'draft'


def test_synthetic_zero_features_return_printed_intercept(tmp_path):
    # Artificial zero log-RFU vector, not a participant in the paper.
    completed = run(tmp_path)
    assert completed.returncode == 0, completed.stderr
    result = json.loads((tmp_path / 'out/result.json').read_text())
    assert result['outputs']['mitoage_score']['value'] == 7.49653775853267
    report = (tmp_path / 'out/report.md').read_text()
    assert report.index('论文卡片') < report.index('你的结果')
    assert '仍在验证' in report and '边界' in report
    assert '不是年龄岁数' in report
    assert not (tmp_path / 'out/problems.json').exists()


def test_male_term_and_target_delta_use_printed_weights(tmp_path):
    target = 'marker,value,unit\nMCP-1,1,1\nAREG,1,1\n'
    completed = run(tmp_path, sex='male', targets=target)
    assert completed.returncode == 0, completed.stderr
    levers = json.loads((tmp_path / 'out/levers.json').read_text())
    assert levers['current']['mitoage_score'] == pytest.approx(7.49653775853267 - 0.120048854106948)
    changes = {p['key']: p for p in levers['levers']}
    assert changes['ccl2_ln_rfu']['mitoage_delta'] == pytest.approx(-0.433005733637459)
    assert changes['areg_ln_rfu']['mitoage_delta'] == pytest.approx(-0.00220802248058917)
    assert levers['targets']['mitoage_delta'] == pytest.approx(-0.433005733637459 - 0.00220802248058917)
    assert len(levers['sensitivity']) == 25
    assert 'years_per_unit' not in levers['sensitivity'][0]


@pytest.mark.parametrize('kwargs,kind', [
    ({'unit': 'ng/mL'}, 'unit'),
    ({'unit': 'RFU'}, 'unit'),
    ({'value': '1000'}, 'range'),
    ({'value': 'nan'}, 'parse'),
    ({'omit': 'ccl2_ln_rfu'}, 'missing'),
    ({'sex': None}, 'missing'),
    ({'sex': 'unknown'}, 'category'),
    ({'age': 'nan'}, 'number'),
    ({'age': 'abc'}, 'number'),
    ({'preprocessing': None}, 'preprocessing'),
    ({'targets': 'marker,value,unit\nMCP-1,1,mg/L\n'}, 'unit'),
    ({'targets': 'marker,value,unit\nUnknown,1,1\n'}, 'unknown'),
])
def test_bad_input_exits_three_and_removes_stale_results(tmp_path, kwargs, kind):
    assert run(tmp_path).returncode == 0
    completed = run(tmp_path, **kwargs)
    assert completed.returncode == 3, completed.stderr
    out = tmp_path / 'out'
    problems = json.loads((out / 'problems.json').read_text())['problems']
    assert any(kind in p['kind'] for p in problems), problems
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    report = (out / 'report.md').read_text()
    assert '论文卡片' in report and '边界' in report
    assert '你的结果' not in report


def test_age_is_context_only_and_rerun_clears_problems(tmp_path):
    assert run(tmp_path, unit='RFU').returncode == 3
    assert run(tmp_path, age='100').returncode == 0
    report = (tmp_path / 'out/report.md').read_text()
    assert '超出' in report and '22–92' in report
    assert not (tmp_path / 'out/problems.json').exists()
    result = json.loads((tmp_path / 'out/result.json').read_text())
    assert result['outputs']['mitoage_score']['value'] == 7.49653775853267
