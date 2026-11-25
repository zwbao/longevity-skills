"""Printed examples: Supplemental Appendix 3, pp. 12–14 (PDF pages).
Expected scores below are printed values, not generated golden outputs.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets
import skillkit

MANIFEST = json.loads((ROOT / 'skill.json').read_text())
# Appendix 3 Example 4: Ms. D, 75 y, MEPA 15, 20 min daily,
# never tobacco, sleep 7 h, BMI 24, non-HDL 120 untreated, FBG 96,
# BP 132/68 on antihypertensive medication. Other optional modifiers
# are not applied because the example does not invoke them.
D = dict(mepa_score=15, moderate_min_week=20*7, vigorous_min_week=0,
         smoking_status=0, inhaled_nicotine=0, indoor_smoke=0,
         sleep_h=7, bmi_kg_m2=24, non_hdl_mg_dl=120, lipid_treated=0,
         diabetes=0, fasting_glucose_mg_dl=96, sbp_mmhg=132,
         dbp_mmhg=68, bp_treated=1, bmi_asian_scale=0)


def test_appendix3_example4():
    # Printed: Sum: 720; total 720/8 = 90. Exact, no rounding needed.
    out = report.calculate(D)
    assert [out[k + '_score'] for k in presets.METRICS] == [100, 90, 100, 100, 100, 100, 100, 30]
    assert out['score_sum'] == 720
    assert out['le8_score'] == 90
    assert out['cvh_category'] == '高'


def test_appendix3_examples1_and3():
    a = {**D, 'mepa_score':12, 'moderate_min_week':30*3, 'sleep_h':6.5,
         'bmi_kg_m2':31, 'non_hdl_mg_dl':136, 'lipid_treated':1,
         'fasting_glucose_mg_dl':107, 'sbp_mmhg':135, 'dbp_mmhg':76}
    out = report.calculate(a)
    assert [out[k + '_score'] for k in presets.METRICS] == [80,80,100,70,30,40,60,30]
    assert out['score_sum'] == 490
    assert abs(out['le8_score'] - 61) <= .5  # printed nearest whole point
    c = {**D, 'mepa_score':2, 'moderate_min_week':0, 'smoking_status':2,
         'sleep_h':5, 'bmi_kg_m2':38, 'non_hdl_mg_dl':185, 'diabetes':1,
         'hba1c_pct':9.2, 'sbp_mmhg':137, 'dbp_mmhg':84}
    c.pop('fasting_glucose_mg_dl')
    out = report.calculate(c)
    assert [out[k + '_score'] for k in presets.METRICS] == [0,0,50,40,15,40,10,30]
    assert out['score_sum'] == 185
    assert abs(out['le8_score'] - 23) <= .5


def write_csv(path, values, override=None):
    specs = {x['key']:x for x in MANIFEST['inputs']}
    with path.open('w') as f:
        w=csv.writer(f); w.writerow(['marker','value','unit'])
        for k,v in values.items():
            w.writerow((k,v,specs[k]['unit']) if not override or k not in override else override[k])
    return path


def run(tmp_path, values=None, override=None, targets=None, age='75'):
    inp=write_csv(tmp_path/'input.csv', D if values is None else values, override)
    cmd=[sys.executable,str(ROOT/'scripts/personal_report.py'),'--measurements',str(inp),'--age',age,'--out',str(tmp_path/'out')]
    if targets is not None:
        cmd += ['--targets',str(write_csv(tmp_path/'targets.csv',targets))]
    return subprocess.run(cmd,capture_output=True,text=True)


def test_manifest_matches_presets():
    declared={x['key']:x['unit'] for x in MANIFEST['inputs'] if x['from']=='measurements'}
    assert declared == presets.INPUT_UNITS
    assert MANIFEST['validation']['status']=='reproduced'


def test_cli_printed_example(tmp_path):
    proc=run(tmp_path); assert proc.returncode==0,proc.stderr
    obj=json.loads((tmp_path/'out/result.json').read_text())
    assert obj['outputs']['le8_score']['value']==90
    txt=(tmp_path/'out/report.md').read_text()
    assert txt.index('10.1161/cir.0000000000001078') < txt.index('你的结果')
    assert '边界' in txt


@pytest.mark.parametrize('over',[
 {'non_hdl_mg_dl':('非高密度脂蛋白胆固醇',120,'g/kg')},
 {'sleep_h':('sleep_h',40,'h')},
 {'diabetes':('diabetes',0.5,'1')},
 {'mepa_score':('mepa_score','NaN','score')},
])
def test_wrong_input_exit3(tmp_path,over):
    proc=run(tmp_path,override=over); assert proc.returncode==3,proc.stderr
    assert (tmp_path/'out/problems.json').exists()
    obj=json.loads((tmp_path/'out/result.json').read_text())
    assert all(v['value'] is None for v in obj['outputs'].values())
    assert not (tmp_path/'out/levers.json').exists()


@pytest.mark.parametrize('change', ['missing','diabetic_without_a1c','unclassified_glucose','underweight','discordant_glucose'])
def test_incomplete_or_undefined_cases(tmp_path,change):
    d=D.copy()
    if change=='missing': d.pop('sleep_h')
    elif change=='diabetic_without_a1c': d['diabetes']=1
    elif change=='unclassified_glucose': d['fasting_glucose_mg_dl']=126
    elif change=='underweight': d['bmi_kg_m2']=17
    else: d['hba1c_pct']=6.0
    assert run(tmp_path,d).returncode==3


def test_units_aliases(tmp_path):
    assert run(tmp_path,override={
        'non_hdl_mg_dl':('非高密度脂蛋白胆固醇',120/38.665,'mmol/L'),
        'fasting_glucose_mg_dl':('空腹血糖',96/18.016,'mmol/L')}).returncode==0
    obj=json.loads((tmp_path/'out/result.json').read_text())
    assert obj['outputs']['le8_score']['value']==90


def test_targets_and_stale_results(tmp_path):
    assert run(tmp_path,targets={'moderate_min_week':150}).returncode==0
    levers=json.loads((tmp_path/'out/levers.json').read_text())
    # Table 1: 140 min -> 90 activity points, 150 -> 100; mean delta 10/8.
    assert levers['targets']['le8_delta']==(100-90)/8
    assert levers['levers'][0]['le8_delta']==(100-90)/8
    d=D.copy();d.pop('sleep_h')
    assert run(tmp_path,d).returncode==3
    assert not (tmp_path/'out/levers.json').exists()
    assert run(tmp_path,targets={'bp_treated':0}).returncode==3


def test_asian_bmi_scale_not_printed(tmp_path):
    # Table 1 notes say scores 'should be aligned as appropriate' for Asian or
    # Pacific ancestry but print no cutoffs, so the skill must stop, not guess.
    assert run(tmp_path,{**D,'bmi_asian_scale':1}).returncode==3
    assert not hasattr(presets,'BMI_ASIAN')


def test_adult_scope(tmp_path):
    assert run(tmp_path,age='19').returncode==3


@pytest.mark.parametrize('changes,metric,printed_points',[
    ({'sbp_mmhg':119,'dbp_mmhg':80,'bp_treated':0},'bp',50),
    ({'sbp_mmhg':160,'dbp_mmhg':70,'bp_treated':1},'bp',0),
    ({'non_hdl_mg_dl':130,'lipid_treated':1},'lipids',40),
    ({'non_hdl_mg_dl':220,'lipid_treated':1},'lipids',0),
    ({'smoking_status':4,'inhaled_nicotine':1,'indoor_smoke':1},'nicotine',0),
    ({'smoking_status':0,'inhaled_nicotine':1,'indoor_smoke':1},'nicotine',5),
    ({'smoking_status':1},'nicotine',75),
    ({'sleep_h':9},'sleep',90),
    ({'sleep_h':10},'sleep',40),
    ({'moderate_min_week':0,'vigorous_min_week':75},'activity',100),
    ({'diabetes':1,'hba1c_pct':6.9},'glucose',40),
    ({'diabetes':1,'hba1c_pct':7},'glucose',30),
    ({'diabetes':1,'hba1c_pct':8},'glucose',20),
    ({'diabetes':1,'hba1c_pct':10},'glucose',0),
])
def test_printed_table1_boundaries(changes,metric,printed_points):
    # Table 1 / implementation notes. Nicotine 5 also appears in Appendix 3
    # Example 2; floors reflect the explicitly bounded 0–100 scale.
    assert report.calculate({**D,**changes})[metric+'_score']==printed_points


def test_invalid_target_does_not_publish_current_score(tmp_path):
    assert run(tmp_path,targets={'sleep_h':99}).returncode==3
    assert not (tmp_path/'out/levers.json').exists()
    obj=json.loads((tmp_path/'out/result.json').read_text())
    assert obj['outputs']['le8_score']['value'] is None
