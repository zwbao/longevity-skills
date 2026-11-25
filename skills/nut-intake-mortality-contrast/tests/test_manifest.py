"""Printed linear contrast: Results, Table 1 footnote b and Discussion.

The paper prints a 28 g/day increment, RR 0.78 (0.72–0.84), and a 22%
relative reduction. This validates the published increment conversion only;
it does not reproduce the meta-analysis or validate a person's prognosis.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report


def test_printed_linear_increment():
    # The printed input is the difference 28, not a prescribed intake.
    actual = report.contrast(28)
    assert actual['linear_rr'] == pytest.approx(0.78, abs=1e-12)
    assert actual['linear_rr_lower'] == pytest.approx(0.72, abs=1e-12)
    assert actual['linear_rr_upper'] == pytest.approx(0.84, abs=1e-12)
    assert actual['relative_difference_pct'] == pytest.approx(-22, abs=1e-10)


def run(tmp_path, rows, targets=None):
    path = tmp_path / 'input.csv'
    path.write_text('marker,value,unit\n' + rows, encoding='utf-8')
    out = tmp_path / 'out'
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(path), '--out', str(out)]
    if targets is not None:
        target = tmp_path / 'targets.csv'
        target.write_text('marker,value,unit\n' + targets, encoding='utf-8')
        args += ['--targets', str(target)]
    process = subprocess.run(args, capture_output=True, text=True)
    return process, out


def test_report_and_targets(tmp_path):
    process, out = run(tmp_path, '总坚果摄入量,28,g/d\n比较基准摄入量,0,g/d\n', 'nut_intake_g_d,0,g/d\n')
    assert process.returncode == 0, process.stderr
    result = json.loads((out / 'result.json').read_text())
    assert result['outputs']['linear_rr']['value'] == pytest.approx(0.78)
    text = (out / 'report.md').read_text()
    assert text.startswith('## 论文卡片')
    assert '10.1186/s12916-016-0730-3' in text
    assert report.BOUNDARY in text and '非线性' in text
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['schema'] == 'longevity-levers/1'
    assert levers['targets']['linear_rr'] == 1
    assert levers['sensitivity'][0]['rr_per_unit'] < 0
    assert levers['levers'][0]['linear_rr_delta'] > 0


@pytest.mark.parametrize('rows', [
    '', '总坚果摄入量,28,g/d\n',
    '总坚果摄入量,28,mg/d\n比较基准摄入量,0,g/d\n',
    '总坚果摄入量,28,\n比较基准摄入量,0,g/d\n',
    '总坚果摄入量,-1,g/d\n比较基准摄入量,0,g/d\n',
    '总坚果摄入量,nan,g/d\n比较基准摄入量,0,g/d\n',
    '总坚果摄入量,500,g/d\n比较基准摄入量,0,g/d\n',
    '总坚果摄入量,28,g/d\n总坚果摄入量,12,g/d\n比较基准摄入量,0,g/d\n',
])
def test_invalid_input_exits_three(tmp_path, rows):
    process, out = run(tmp_path, rows)
    assert process.returncode == 3, process.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert (out / 'report.md').read_text().startswith('## 论文卡片')
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())


def test_reverse_contrast_and_equal_intakes():
    forward, reverse = report.contrast(28), report.contrast(-28)
    assert reverse['linear_rr_lower'] == pytest.approx(1 / forward['linear_rr_upper'])
    assert reverse['linear_rr_upper'] == pytest.approx(1 / forward['linear_rr_lower'])
    assert report.contrast(0)['linear_rr'] == 1


def test_bad_target_clears_old_success(tmp_path):
    rows = 'nut_intake_g_d,28,g/d\nreference_intake_g_d,0,g/d\n'
    assert run(tmp_path, rows)[0].returncode == 0
    process, out = run(tmp_path, rows, 'nut_intake_g_d,NaN,g/d\n')
    assert process.returncode == 3
    assert not (out / 'levers.json').exists()
    assert run(tmp_path, rows)[0].returncode == 0
    assert not (out / 'problems.json').exists()


def test_unknown_target_is_not_ignored(tmp_path):
    process, _ = run(tmp_path, 'nut_intake_g_d,28,g/d\nreference_intake_g_d,0,g/d\n', 'peanut_butter,20,g/d\n')
    assert process.returncode == 3
