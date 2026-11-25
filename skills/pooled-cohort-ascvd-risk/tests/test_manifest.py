"""Expected values transcribed before implementation from Table A and supplement Tables 8–11."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def test_paper_table_a():
    from personal_report import compute
    # Table A: age 55, TC 213 mg/dL, HDL-C 50 mg/dL, untreated SBP 120 mmHg,
    # nonsmoker, without diabetes. Three examples reproduce to printed rounding.
    values = dict(tc_mg_dl=213, hdl_mg_dl=50, sbp_mmhg=120, treated=0, smoker=0, diabetes=0)
    for sex, race, expected in [('female', 'white', 2.1), ('female', 'african_american', 3.0),
                                ('male', 'african_american', 6.1)]:
        assert compute(values, 55, sex, race) == pytest.approx(expected, abs=0.05)


def test_supplement_table_9():
    from personal_report import compute
    # First row, rightmost cell of Table 9: age 40, TC 160,
    # HDL 65, treated SBP 160, current smoker Yes, diabetes Yes.
    # Printed probability: 0.044 (not a percentage).
    values = dict(tc_mg_dl=160, hdl_mg_dl=65, sbp_mmhg=160, treated=1, smoker=1, diabetes=1)
    assert compute(values, 40, 'female', 'white') / 100 == pytest.approx(0.044, abs=0.0005)


def test_documented_printed_discrepancies_are_not_fitted_away():
    from personal_report import compute
    values = dict(tc_mg_dl=213, hdl_mg_dl=50, sbp_mmhg=120, treated=0, smoker=0, diabetes=0)
    # Table A white men prints 5.3%; rounded constants miss half a printed digit.
    assert abs(compute(values, 55, 'male', 'white') - 5.3) > 0.05
    values.update(tc_mg_dl=160, hdl_mg_dl=65, sbp_mmhg=160, treated=1, smoker=1, diabetes=1)
    # Tables 10/11 disagree by >2%; these cells are NOT validation evidence.
    for race, printed in [('african_american', 0.215), ('white', 0.068)]:
        assert abs(compute(values, 40, 'male', race)/100 - printed) / printed > 0.02
    # Table 8 also misses the half-digit rounding tolerance, though <2% relative.
    assert abs(compute(values, 40, 'female', 'african_american')/100 - 0.124) > 0.0005


ROWS = [('总胆固醇', 213, 'mg/dL'), ('HDL-C', 50, 'mg/dL'), ('收缩压', 120, 'mmHg'),
        ('降压治疗', 0, '1'), ('当前吸烟', 0, '1'), ('糖尿病', 0, '1')]


def write_csv(path, rows):
    path.write_text('item,value,unit\n' + ''.join(f'{k},{v},{u}\n' for k,v,u in rows), encoding='utf-8')
    return path


def run_cli(tmp_path, rows=None, extra=(), targets=None, profile=None):
    measurements = write_csv(tmp_path / 'measurements.csv', ROWS if rows is None else rows)
    args = ['--measurements', str(measurements), '--out', str(tmp_path / 'out')]
    args += profile if profile is not None else ['--age', '55', '--sex', 'female', '--race', 'white', '--eligible', 'yes']
    if targets is not None:
        args += ['--targets', str(write_csv(tmp_path / 'targets.csv', targets))]
    return subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'), *args, *extra], capture_output=True, text=True)


def test_manifest_matches_units_and_ranges():
    from presets import AGES, FLAGS, MEASUREMENTS, MMOL_TO_MG_DL
    m = json.loads((ROOT / 'skill.json').read_text())
    specs = {s['key']: s for s in m['inputs']}
    assert m['inputs_status'] == 'verified'
    assert m['population']['age_years'] == list(AGES)
    assert m['entry']['targets_flag'] == '--targets' and m['entry']['levers_json']
    assert {s['key'] for s in m['inputs'] if s['from'] == 'measurements'} == set(MEASUREMENTS) | set(FLAGS)
    for key,(unit,bounds) in MEASUREMENTS.items():
        assert specs[key]['unit'] == unit and specs[key]['range'] == list(bounds)
    for key in ('tc_mg_dl','hdl_mg_dl'):
        assert specs[key]['accept']['mmol/L'] == MMOL_TO_MG_DL


def test_report_and_targets_reproduce_two_printed_examples(tmp_path):
    # Current is Table A white women 2.1%; targets bring age-40 baseline to Table 9 0.044.
    result = run_cli(tmp_path)
    assert result.returncode == 0, result.stderr
    data = json.loads((tmp_path / 'out/result.json').read_text())
    assert data['outputs']['risk_10y_pct']['value'] == pytest.approx(2.1, abs=0.05)
    report = (tmp_path / 'out/report.md').read_text()
    from presets import BOUNDARY
    assert report.index('论文卡片') < report.index('你的十年')
    assert BOUNDARY in report
    rows = [('TC',160,'mg/dL'),('HDL-C',65,'mg/dL'),('SBP',120,'mmHg'),
            ('treated',1,'1'),('smoker',0,'1'),('diabetes',1,'1')]
    result = run_cli(tmp_path, rows, extra=['--age','40'], targets=[('SBP',160,'mmHg'),('smoker',1,'1')])
    assert result.returncode == 0, result.stderr
    l = json.loads((tmp_path / 'out/levers.json').read_text())
    assert l['schema'] == 'longevity-levers/1'
    assert l['targets']['risk_10y_pct']/100 == pytest.approx(0.044, abs=0.0005)
    assert {s['key'] for s in l['sensitivity']} == {'age','sbp_mmhg','tc_mg_dl','hdl_mg_dl','treated','smoker','diabetes'}
    assert {s['key'] for s in l['sensitivity'] if s['not_a_target']} == {'age','treated','diabetes'}
    for item in l['levers']:
        assert item['risk_delta_pct'] == pytest.approx(item['risk_10y_pct'] - l['current']['risk_10y_pct'])


def test_alternative_units_preserve_printed_example(tmp_path):
    rows = [('TC',213/38.665,'mmol/L'),('HDL-C',500,'mg/L'),('SBP',120/7.500617,'kPa'),*ROWS[3:]]
    result = run_cli(tmp_path, rows)
    assert result.returncode == 0, result.stderr
    data = json.loads((tmp_path/'out/result.json').read_text())
    assert data['outputs']['risk_10y_pct']['value'] == pytest.approx(2.1, abs=0.05)


@pytest.mark.parametrize('rows', [
    [('TC',213,'g/L'),*ROWS[1:]],
    [('TC',2130,'mg/dL'),*ROWS[1:]],
    [('TC',213,''),*ROWS[1:]],
    [('TC','NaN','mg/dL'),*ROWS[1:]],
    ROWS[1:],
    [*ROWS[:4],('smoker',0.5,'1'),ROWS[5]],
    [*ROWS,('TC',220,'mg/dL')],
])
def test_invalid_measurement_returns_3_without_risk(tmp_path, rows):
    result = run_cli(tmp_path,rows)
    assert result.returncode == 3, result.stderr
    p = json.loads((tmp_path/'out/problems.json').read_text())
    assert p['problems']
    r = json.loads((tmp_path/'out/result.json').read_text())
    assert all(o['value'] is None for o in r['outputs'].values())
    assert not (tmp_path/'out/levers.json').exists()
    report = (tmp_path/'out/report.md').read_text()
    assert '这次没有计算' in report and '你的十年首次' not in report
    assert '论文卡片' in report and '边界' in report


@pytest.mark.parametrize('extra', [
    ['--age','39'],['--age','80'],['--age','NaN'],['--age','oops'],
    ['--sex','unknown'],['--race','asian'],['--eligible','no'],
])
def test_invalid_profile_returns_3(tmp_path,extra):
    assert run_cli(tmp_path,extra=extra).returncode == 3
    assert (tmp_path/'out/problems.json').exists()


def test_missing_profile_is_structured(tmp_path):
    assert run_cli(tmp_path,profile=[]).returncode == 3
    p = json.loads((tmp_path/'out/problems.json').read_text())
    assert {'age','sex','race','eligible'} <= {x['key'] for x in p['problems']}


@pytest.mark.parametrize('targets', [[], [('unknown',120,'mmHg')], [('SBP',120,'mg/dL')],
    [('SBP',250,'mmHg')], [('treated',0,'1')], [('diabetes',0,'1')], [('smoker',0.2,'1')]])
def test_invalid_targets_clear_stale_outputs(tmp_path,targets):
    assert run_cli(tmp_path).returncode == 0
    assert run_cli(tmp_path,targets=targets).returncode == 3
    assert not (tmp_path/'out/levers.json').exists()
    assert all(x['value'] is None for x in json.loads((tmp_path/'out/result.json').read_text())['outputs'].values())
    assert run_cli(tmp_path).returncode == 0
    assert not (tmp_path/'out/problems.json').exists()


def test_missing_file_is_structured(tmp_path):
    assert run_cli(tmp_path,extra=['--measurements',str(tmp_path/'absent.csv')]).returncode == 3
    assert run_cli(tmp_path,extra=['--targets',str(tmp_path/'absent.csv')]).returncode == 3


def test_display_limits_are_not_raw_risk_clipping():
    from personal_report import compute, display_risk
    # Table 9 first row, untreated 100/no smoking/no diabetes prints <.01.
    v=dict(tc_mg_dl=160,hdl_mg_dl=65,sbp_mmhg=100,treated=0,smoker=0,diabetes=0)
    risk=compute(v,40,'female','white')
    assert 0 < risk < 1 and display_risk(risk) == '<1%'
    assert display_risk(30) == '30.0%' and display_risk(30.1) == '>30%'
