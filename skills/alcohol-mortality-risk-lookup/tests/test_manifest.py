"""Printed expectations transcribed before implementation: Zhao 2023 Tables 2/4.
Only Fully adjusted columns, reference = lifetime nondrinker.
"""
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
# Row lower boundaries printed in the tables (occasional is >0 to <1.30).
PRINTED = {
    'overall': [(1.30, 0.93, 0.85, 1.01), (25, 1.05, 0.96, 1.14),
                (45, 1.19, 1.07, 1.32), (65, 1.35, 1.23, 1.47)],
    'male': [(1.30, 0.94, 0.88, 1.01), (25, 1.01, 0.93, 1.10),
             (45, 1.15, 1.03, 1.28), (65, 1.34, 1.23, 1.47)],
    'female': [(1.30, 0.99, 0.90, 1.10), (25, 1.21, 1.08, 1.36),
               (45, 1.34, 1.11, 1.63), (65, 1.61, 1.44, 1.80)],
}
OCCASIONAL = {'overall': (0.96, 0.86, 1.06), 'male': (1.00, 0.91, 1.09), 'female': (0.99, 0.87, 1.11)}
FORMER = {'overall': (1.26, 1.12, 1.42), 'male': (1.39, 1.21, 1.58), 'female': (1.27, 1.13, 1.43)}


def run(tmp_path, text=None, sex='overall', extra=(), target=None):
    args = [sys.executable, str(ROOT/'scripts/personal_report.py'), '--out', str(tmp_path/'out')]
    if text is not None:
        path = tmp_path/'input.csv'
        path.write_text(text, encoding='utf-8')
        args += ['--measurements', str(path)]
    if sex != 'overall': args += ['--sex', sex]
    if target is not None:
        path = tmp_path/'target.csv'
        path.write_text(target, encoding='utf-8')
        args += ['--targets', str(path)]
    result = subprocess.run(args + list(extra), text=True, capture_output=True)
    return result, tmp_path/'out'


def csv(value, unit='g/d', key='ethanol_g_day'):
    return f'item,value,unit\n{key},{value},{unit}\n'


def outputs(out):
    return {k:v['value'] for k,v in json.loads((out/'result.json').read_text())['outputs'].items()}


@pytest.mark.parametrize('sex,row', [(s,r) for s,rows in PRINTED.items() for r in rows])
def test_printed_tables_2_and_4(tmp_path, sex, row):
    dose, rr, lower, upper = row
    proc, out = run(tmp_path, csv(dose), sex)
    assert proc.returncode == 0, proc.stderr
    got = outputs(out)
    assert (got['rr'], got['ci_lower'], got['ci_upper']) == (rr, lower, upper)
    assert got['ethanol_g_day'] == dose
    assert got['stratum'] == sex
    report = (out/'report.md').read_text()
    assert report.index('论文卡片') < report.index('你的查表结果')
    assert '边界:' in report and '不是个人死亡概率' in report


@pytest.mark.parametrize('sex', OCCASIONAL)
def test_occasional_and_former_printed_rows(tmp_path, sex):
    proc, out = run(tmp_path, csv(0.5), sex)
    assert proc.returncode == 0
    got = outputs(out)
    assert tuple(got[k] for k in ('rr','ci_lower','ci_upper')) == OCCASIONAL[sex]
    proc, out = run(tmp_path, csv(0), sex, extra=('--drinking-status','former'))
    assert proc.returncode == 0
    got = outputs(out)
    assert tuple(got[k] for k in ('rr','ci_lower','ci_upper')) == FORMER[sex]
    proc, out = run(tmp_path, csv(0), sex, extra=('--drinking-status','lifetime_abstainer'))
    assert proc.returncode == 0
    got = outputs(out)
    assert got['rr'] == 1 and got['ci_lower'] is None and got['ci_upper'] is None


@pytest.mark.parametrize('value,category', [(0.001,'occasional'),(1.299,'occasional'),(1.3,'low'),
    (24.99,'low'),(25,'medium'),(44.99,'medium'),(45,'high'),(64.99,'high'),(65,'higher'),(300,'higher')])
def test_interval_boundaries(tmp_path, value, category):
    proc, out = run(tmp_path, csv(value))
    assert proc.returncode == 0
    assert outputs(out)['category'] == category


def test_manifest_and_aliases(tmp_path):
    sys.path.insert(0,str(ROOT/'scripts'))
    import presets
    m = json.loads((ROOT/'skill.json').read_text())
    spec = m['inputs'][0]
    assert (spec['key'],spec['unit'],spec['range']) == (presets.INPUT_KEY,presets.INPUT_UNIT,list(presets.PLAUSIBLE_RANGE))
    assert spec['accept']['g/d'] == 1
    proc,out=run(tmp_path,'项目,结果,单位\n日均纯酒精摄入量,45,g/d\n',extra=('--age','80'))
    assert proc.returncode == 0
    assert outputs(out)['rr'] == 1.19


@pytest.mark.parametrize('text,extra', [
    (None,()),('item,value,unit\n',()),(csv(45,'mL/d'),()),(csv(301),()),(csv(-1),()),
    (csv('nan'),()),(csv(45,'drinks/day'),()),(csv(45,'','日均纯酒精摄入量'),()),
    (csv(0),()),(csv(0),('--drinking-status','current')),
    (csv(25),('--drinking-status','former')),(csv(25),('--drinking-status','lifetime_abstainer')),
    (csv(25),('--sex','unknown')),(csv(25),('--age','nan')),(csv(25),('--age','10')),
    (csv(25),('--drinking-status','unknown')),
    (csv(25)+'日均纯酒精摄入量,45,g/d\n',()),
])
def test_invalid_inputs_exit_3(tmp_path,text,extra):
    proc,out=run(tmp_path,text,extra=extra)
    assert proc.returncode == 3,proc.stderr
    assert json.loads((out/'problems.json').read_text())['problems']
    assert all(v is None for v in outputs(out).values())
    assert not (out/'levers.json').exists()
    report=(out/'report.md').read_text()
    assert '论文卡片' in report and '边界:' in report and '你的查表结果' not in report


def test_target_is_table_comparison_not_causal_prediction(tmp_path):
    proc,out=run(tmp_path,csv(45),'female',target=csv(25))
    assert proc.returncode == 0,proc.stderr
    v=json.loads((out/'levers.json').read_text())
    assert v['current']['rr'] == 1.34
    assert v['targets']['outputs']['rr'] == 1.21
    assert v['levers'][0]['rr_delta'] == pytest.approx(1.21-1.34)
    assert [r['outputs']['rr'] for r in v['sensitivity'][0]['neighbors']] == [1.21,1.61]
    assert '不是改变饮酒后的因果效应' in v['note_zh']
    # A newly zero target must never become a lifetime abstainer or a cessation forecast.
    proc,out=run(tmp_path,csv(45),'female',target=csv(0))
    assert proc.returncode == 3
    assert all(v is None for v in outputs(out).values())
    assert not (out/'levers.json').exists()
    proc,out=run(tmp_path,csv(45),'female')
    assert proc.returncode == 0 and not (out/'problems.json').exists()
