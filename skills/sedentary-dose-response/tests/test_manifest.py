"""Expected risks are printed cells of Patterson 2018 Appendix Tables 7–8."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def run_report(tmp_path, rows, extra=()):
    measurements = tmp_path / 'measurements.csv'
    measurements.write_text('marker,value,unit\n' + rows, encoding='utf-8')
    out = tmp_path / 'out'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                             '--measurements', str(measurements), '--age', '50',
                             '--out', str(out), *extra], capture_output=True, text=True)
    return result, out


def test_printed_sitting_eight_hours(tmp_path):
    # Appendix Table 7: dose h/day | RR | LCI | UCI.
    # All-cause: 8 | 1.06 | 1.03 | 1.09; CVD: 8 | 1.11 | 1.01 | 1.22.
    # Cancer: 8 | 1.02 | 0.96 | 1.08; Type 2 Diabetes: 8 | 1.08 | 0.99 | 1.17.
    p, out = run_report(tmp_path, '总久坐时间,8,h\n')
    assert p.returncode == 0, p.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    for outcome, expected in [('all_cause', (1.06, 1.03, 1.09)),
                              ('cvd', (1.11, 1.01, 1.22)),
                              ('cancer', (1.02, 0.96, 1.08)),
                              ('t2d', (1.08, 0.99, 1.17))]:
        assert tuple(outputs[f'sitting_{outcome}_{s}']['value'] for s in ('rr', 'lci', 'uci')) == expected
    assert outputs['sitting_all_cause_band']['value'] == 'at_or_below'
    assert outputs['sitting_cvd_band']['value'] == 'above'


def test_printed_tv_four_hours(tmp_path):
    # Appendix Table 8: dose h/day | RR | LCI | UCI.
    # All-cause: 4 | 1.12 | 1.06 | 1.18; CVD: 4 | 1.06 | 0.97 | 1.16.
    # Cancer: 4 | 1.07 | 1.01 | 1.13; Type 2 Diabetes: 4 | 1.56 | 1.38 | 1.77.
    p, out = run_report(tmp_path, 'TV viewing,240,min\n')
    assert p.returncode == 0, p.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    for outcome, expected in [('all_cause', (1.12, 1.06, 1.18)),
                              ('cvd', (1.06, 0.97, 1.16)),
                              ('cancer', (1.07, 1.01, 1.13)),
                              ('t2d', (1.56, 1.38, 1.77))]:
        assert tuple(outputs[f'tv_{outcome}_{s}']['value'] for s in ('rr', 'lci', 'uci')) == expected
    assert outputs['tv_all_cause_band']['value'] == 'above'
    assert outputs['tv_cvd_band']['value'] == 'at_or_below'


def test_printed_thresholds():
    from personal_report import evaluate
    # Appendix Table 5: 0–8hrs / >8hrs; 0–6hrs / >6hrs;
    # 0–3.5hrs / >3.5hrs; 0–4hrs / >4hrs. Each RR is per additional h/day.
    cases = [('sitting', 'all_cause', 8, (1.01, 1.00, 1.01), (1.04, 1.03, 1.05)),
             ('sitting', 'cvd', 6, (1.01, 0.99, 1.02), (1.04, 1.03, 1.04)),
             ('tv', 'all_cause', 3.5, (1.03, 1.01, 1.04), (1.06, 1.05, 1.08)),
             ('tv', 'cvd', 4, (1.02, 0.99, 1.04), (1.08, 1.05, 1.12))]
    for exposure, outcome, cutoff, below, above in cases:
        for x, expected, band in [(cutoff, below, 'at_or_below'), (cutoff + .001, above, 'above')]:
            o = evaluate({f'{exposure}_hours_day': x})
            prefix = f'{exposure}_{outcome}'
            assert o[prefix + '_threshold_hours'] == cutoff
            assert o[prefix + '_band'] == band
            assert tuple(o[prefix + '_per_hour_' + s] for s in ('rr', 'lci', 'uci')) == expected


def test_manifest_matches_presets():
    from presets import EXPOSURES, OUTCOMES, TABLES
    m = json.loads((ROOT / 'skill.json').read_text())
    specs = {s['key']: s for s in m['inputs']}
    for e in EXPOSURES:
        assert specs[e + '_hours_day']['unit'] == 'h'
        assert specs[e + '_hours_day']['range'] == [0, 24]
        assert specs[e + '_hours_day']['accept']['min'] == 1 / 60
        assert set(TABLES[e]) == set(OUTCOMES)
    # Every frozen printed row remains available without interpolation.
    from personal_report import evaluate
    for exposure, outcomes in TABLES.items():
        for outcome, rows in outcomes.items():
            for row in rows:
                o = evaluate({exposure + '_hours_day': row['hours']})
                assert [o[f'{exposure}_{outcome}_{s}'] for s in ('rr', 'lci', 'uci')] == [row[s] for s in ('rr', 'lci', 'uci')]


@pytest.mark.parametrize('rows', ['总久坐时间,8,mg/dL\n', '总久坐时间,25,h\n',
                                  '总久坐时间,nan,h\n', '总久坐时间,-1,h\n',
                                  '总久坐时间,8,\n', '', '总久坐时间,abc,h\n',
                                  '总久坐时间,3,h\n看电视时间,4,h\n'])
def test_bad_or_missing_input_stops(tmp_path, rows):
    p, out = run_report(tmp_path, rows)
    assert p.returncode == 3, p.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    report = (out / 'report.md').read_text()
    assert '10.1007/s10654-018-0380-1' in report
    assert '边界' in report


def test_between_and_outside_never_invent_risk(tmp_path):
    from personal_report import evaluate
    o = evaluate({'sitting_hours_day': 8.2, 'tv_hours_day': 0})
    assert o['sitting_all_cause_status'] == 'between'
    assert o['sitting_all_cause_rr'] is None
    # Printed adjacent rows Table 7: 8 1.06 1.03 1.09 / 8.5 1.07 1.04 1.11.
    assert o['sitting_all_cause_lower_hours'] == 8
    assert o['sitting_all_cause_lower_rr'] == 1.06
    assert o['sitting_all_cause_upper_hours'] == 8.5
    assert o['sitting_all_cause_upper_rr'] == 1.07
    assert o['tv_all_cause_status'] == 'outside'
    assert o['tv_all_cause_rr'] is None


def test_targets_use_printed_cells(tmp_path):
    target = tmp_path / 'targets.csv'
    target.write_text('marker,value,unit\n看电视时间,2,h\n')
    p, out = run_report(tmp_path, '看电视时间,4,h\n', ['--targets', str(target)])
    assert p.returncode == 0, p.stderr
    data = json.loads((out / 'levers.json').read_text())
    # Table 8: 2 | 1.03 | 1.01 | 1.06 (all cause), 2 | 1.29 | 1.18 | 1.41 (T2D).
    assert data['targets']['outputs']['tv_all_cause_rr'] == 1.03
    assert data['targets']['outputs']['tv_t2d_rr'] == 1.29
    assert data['levers'][0]['rr_delta']['tv_all_cause_rr'] == pytest.approx(1.03 - 1.12)
    assert data['levers'][0]['rr_delta']['tv_t2d_rr'] == pytest.approx(1.29 - 1.56)
    assert data['sensitivity']
    assert '目标' in (out / 'report.md').read_text()


def test_stale_success_removed_on_bad_target(tmp_path):
    p, out = run_report(tmp_path, '总久坐时间,8,h\n')
    assert p.returncode == 0
    target = tmp_path / 'targets.csv'
    target.write_text('marker,value,unit\n总久坐时间,500,h\n')
    p, out = run_report(tmp_path, '总久坐时间,8,h\n', ['--targets', str(target)])
    assert p.returncode == 3
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()


def test_age_required_and_adult(tmp_path):
    p, out = run_report(tmp_path, '总久坐时间,8,h\n', ['--age', '17'])
    assert p.returncode == 3
