"""Expected values transcribed from Appendix 1, Tables S13/S14, PDF pp. 69–70."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets


def run(tmp_path, value='90', unit='g/d', marker='全谷物食品摄入量', target=None):
    source = tmp_path / 'input.csv'
    source.write_text(f'marker,value,unit\n{marker},{value},{unit}\n', encoding='utf-8')
    out = tmp_path / 'out'
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(source), '--out', str(out)]
    if target is not None:
        dest = tmp_path / 'target.csv'
        dest.write_text(f'marker,value,unit\n{marker},{target},g/d\n', encoding='utf-8')
        cmd += ['--targets', str(dest)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p, out


def test_printed_s13_90():
    # S13: g/d | RR (95% CI), left to right, at 90 g/d.
    expected = {
        'coronary_heart_disease': (0.72, 0.69, 0.76),
        'stroke': (0.73, 0.66, 0.79),
        'cardiovascular_disease': (0.79, 0.76, 0.82),
        'cancer_mortality': (0.87, 0.84, 0.91),
        'all_cause_mortality': (0.81, 0.79, 0.83),
    }
    for key, numbers in expected.items():
        item = report.lookup(90, key)
        assert item['status'] == 'exact'
        assert item['reference_g_d'] == 0
        assert tuple(item['lower'][k] for k in ('rr', 'ci_low', 'ci_high')) == numbers


def test_printed_s14_90():
    expected = {
        'respiratory_mortality': (0.73, 0.67, 0.80),
        'diabetes_mortality': (0.42, 0.37, 0.48),
        'infectious_mortality': (0.76, 0.68, 0.85),
        'nervous_system_mortality': (1.05, 0.93, 1.17),
        'non_cvd_non_cancer_mortality': (0.79, 0.77, 0.82),
    }
    for key, numbers in expected.items():
        item = report.lookup(90, key)
        assert item['reference_g_d'] == (0 if key == 'non_cvd_non_cancer_mortality' else 4.8)
        assert tuple(item['lower'][k] for k in ('rr', 'ci_low', 'ci_high')) == numbers


def test_manifest_matches_presets():
    m = json.loads((ROOT / 'skill.json').read_text())
    spec = m['inputs'][0]
    assert (spec['key'], spec['unit'], spec['range']) == (presets.INPUT_KEY, presets.INPUT_UNIT, list(presets.INPUT_RANGE))
    assert m['validation']['status'] == 'reproduced'
    assert {s['key'] for s in m['outputs']} == set(report.output_values(90))


def test_result_and_targets_use_printed_rows(tmp_path):
    p, out = run(tmp_path, target=225)
    assert p.returncode == 0, p.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    assert outputs['all_cause_mortality_lower_rr']['value'] == 0.81
    assert outputs['all_cause_mortality_lower_ci_low']['value'] == 0.79
    assert outputs['all_cause_mortality_lower_ci_high']['value'] == 0.83
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['schema'] == 'longevity-levers/1'
    assert levers['targets']['all_cause_mortality'] == 0.70  # S13 225 0.70 (0.65-0.75)
    assert levers['levers'][0]['all_cause_mortality_delta'] == pytest.approx(0.70 - 0.81)
    assert levers['targets']['infectious_mortality'] is None
    text = (out / 'report.md').read_text()
    assert text.index('10.1136/bmj.i2716') < text.index('你的输入')
    assert '边界：' in text and '不是个人死亡概率' in text


@pytest.mark.parametrize('value,unit,marker', [
    ('90','mg/dL','全谷物食品摄入量'),
    ('1501','g/d','全谷物食品摄入量'),
    ('-1','g/d','全谷物食品摄入量'),
    ('nan','g/d','全谷物食品摄入量'),
    ('90','','全谷物食品摄入量'),
    ('90','g/d','unknown'),
    ('','g/d','全谷物食品摄入量'),
])
def test_invalid_input_stops(tmp_path, value, unit, marker):
    p, out = run(tmp_path, value, unit, marker)
    assert p.returncode == 3, p.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'levers.json').exists()
    result = json.loads((out / 'result.json').read_text())
    assert all(x['value'] is None for x in result['outputs'].values())
    text = (out / 'report.md').read_text()
    assert '10.1136/bmj.i2716' in text
    assert '没有计算' in text


def test_bracketing_and_unavailable_are_not_interpolated():
    item = report.lookup(100, 'all_cause_mortality')
    assert item['status'] == 'bracketed'
    assert (item['lower']['g_d'], item['lower']['rr']) == (90, 0.81)
    assert (item['upper']['g_d'], item['upper']['rr']) == (105, 0.80)
    for x in (0, 4.7, 106, 240):
        item = report.lookup(x, 'infectious_mortality')
        assert item['status'] == 'outside_table'
        assert item['lower'] is None and item['upper'] is None
    baseline = report.lookup(4.8, 'infectious_mortality')['lower']
    assert baseline['rr'] == 1.00 and baseline['ci_low'] is None
    assert report.lookup(240, 'stroke')['lower']['rr'] == 0.70
    assert report.lookup(226, 'all_cause_mortality')['status'] == 'outside_table'


def test_bad_target_and_reused_output_clear_old_results(tmp_path):
    p, out = run(tmp_path, target=225)
    assert p.returncode == 0
    p, out = run(tmp_path, target='wrong')
    assert p.returncode == 3
    assert not (out / 'levers.json').exists()
    assert all(x['value'] is None for x in json.loads((out / 'result.json').read_text())['outputs'].values())
    p, out = run(tmp_path, value='100', target=90)
    assert p.returncode == 0
    levers = json.loads((out / 'levers.json').read_text())
    assert levers['current']['all_cause_mortality'] is None
    assert levers['levers'][0]['all_cause_mortality_delta'] is None
    assert not (out / 'problems.json').exists()
