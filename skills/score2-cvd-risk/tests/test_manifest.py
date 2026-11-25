"""Expected values are printed in ehab309 Results and updated Methods Table 4."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def test_printed_main_text_example():
    from personal_report import compute
    values = dict(sbp_mmhg=140, tc_mmol_l=5.5, hdl_mmol_l=1.3, smoker=1)
    # Results: 50-year-old smoker; 140 mmHg, 5.5 and 1.3 mmol/L.
    for sex, region, expected in [('male','low',5.9), ('male','very_high',14.0),
                                   ('female','low',4.2), ('female','very_high',13.7)]:
        assert compute(values, 50, sex, region)['risk_10y_pct'] == pytest.approx(expected, abs=0.05)


def test_printed_methods_table4():
    from personal_report import compute
    values = dict(sbp_mmhg=140, tc_mmol_l=6.3, hdl_mmol_l=1.4, smoker=1)
    # Printed probabilities; Table 4 substitutes rounded intermediate risks.
    # A half-unit (0.00005) intermediate error propagates by <4 here, plus
    # 0.00005 final rounding: absolute probability tolerance 0.00025.
    expected = {'male': [0.0631, 0.0811, 0.0881, 0.1506],
                'female': [0.0434, 0.0523, 0.0713, 0.1414]}
    for sex in expected:
        for region, probability in zip(['low','moderate','high','very_high'], expected[sex]):
            result = compute(values, 50, sex, region)
            assert result['risk_10y_pct']/100 == pytest.approx(probability, abs=0.00025)
        assert result['linear_predictor'] == pytest.approx(0.3221 if sex == 'male' else 0.39788, abs=1e-8)
        assert result['uncalibrated_risk'] == pytest.approx(0.0541 if sex == 'male' else 0.0332, abs=0.00005)


def run(tmp_path, rows=None, flags=None, targets=None):
    path = tmp_path/'measurements.csv'
    path.write_text('marker,value,unit\n' + (rows or 'SBP,140,mmHg\nTC,5.5,mmol/L\nHDL-C,1.3,mmol/L\nsmoker,1,1\n'))
    args = ['--measurements',str(path),'--age','50','--sex','male','--region','low',
            '--europe','yes','--prior-cvd','no','--diabetes','no']
    if flags:
        args += flags
    if targets is not None:
        t = tmp_path/'targets.csv'; t.write_text('marker,value,unit\n'+targets)
        args += ['--targets',str(t)]
    proc = subprocess.run([sys.executable,str(ROOT/'scripts/personal_report.py'),*args,'--out',str(tmp_path/'out')],capture_output=True,text=True)
    return proc, tmp_path/'out'


def test_result_and_targets(tmp_path):
    proc, out = run(tmp_path, targets='SBP,120,mmHg\nsmoker,0,1\n')
    assert proc.returncode == 0, proc.stderr
    data = json.loads((out/'result.json').read_text())
    assert data['outputs']['risk_10y_pct']['value'] == pytest.approx(5.9, abs=0.05)
    levers = json.loads((out/'levers.json').read_text())
    assert len(levers['sensitivity']) == 4 and len(levers['levers']) == 2
    assert levers['targets']['risk_pct'] < levers['current']['risk_pct']
    assert all(v['risk_delta_pct'] < 0 for v in levers['levers'])
    report = (out/'report.md').read_text()
    assert report.index('10.1093/eurheartj/ehab309') < report.index('你的结果')
    assert '边界' in report and '不代表干预效果' in report


@pytest.mark.parametrize('rows,flags,targets', [
    ('SBP,140,mg/dL\nTC,5.5,mmol/L\nHDL-C,1.3,mmol/L\nsmoker,1,1\n',None,None),
    ('SBP,900,mmHg\nTC,5.5,mmol/L\nHDL-C,1.3,mmol/L\nsmoker,1,1\n',None,None),
    ('SBP,140,mmHg\n',None,None),
    (None,['--age','70'],None), (None,['--age','abc'],None),
    (None,['--sex','unknown'],None), (None,['--region','China'],None),
    (None,['--europe','no'],None), (None,['--diabetes','yes'],None),
    (None,['--prior-cvd','yes'],None),
    (None,None,'smoker,0.5,1\n'), (None,None,'unknown,123,1\n'),
    (None,None,'TC,1,mmol/L\n'),
])
def test_input_problems(tmp_path, rows, flags, targets):
    proc, out = run(tmp_path, rows, flags, targets)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out/'problems.json').read_text())['problems']
    assert json.loads((out/'result.json').read_text())['outputs']['risk_10y_pct']['value'] is None
    assert not (out/'levers.json').exists()
    assert '边界' in (out/'report.md').read_text()


def test_units_and_manifest(tmp_path):
    from presets import INPUT_UNITS, RANGES
    manifest = json.loads((ROOT/'skill.json').read_text())
    for spec in manifest['inputs']:
        if spec['key'] in INPUT_UNITS:
            assert spec['unit'] == INPUT_UNITS[spec['key']]
            assert spec['range'] == list(RANGES[spec['key']])
    # Exact inverse of declared cholesterol conversion (molar mass 386.65).
    proc, out = run(tmp_path, f'SBP,140,mmHg\nTC,{5.5*38.665},mg/dL\nHDL-C,{1.3*38.665},mg/dL\nsmoker,1,1\n')
    assert proc.returncode == 0, proc.stderr
    assert json.loads((out/'result.json').read_text())['outputs']['risk_10y_pct']['value'] == pytest.approx(5.9, abs=0.05)


def test_missing_arguments_and_stale_outputs(tmp_path):
    proc, out = run(tmp_path)
    assert proc.returncode == 0
    proc = subprocess.run([sys.executable,str(ROOT/'scripts/personal_report.py'),'--out',str(out)],capture_output=True)
    assert proc.returncode == 3
    assert not (out/'levers.json').exists()
    assert json.loads((out/'result.json').read_text())['outputs']['risk_10y_pct']['value'] is None
