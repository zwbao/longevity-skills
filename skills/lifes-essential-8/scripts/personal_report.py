#!/usr/bin/env python3
"""Adult Life's Essential 8, frozen to the 2022 advisory."""
import argparse
import csv
import json
import math
from pathlib import Path
import skillkit
from paper_card import lines as paper_card_lines
import presets as p

TITLE = '成人 Life’s Essential 8 心血管健康评分'
BOUNDARY = '这是心血管健康评分，不是个人患病概率、寿命预测或治疗建议；目标情景只是同一算法的重算，不能据此开始、停止或调整药物。'


def lookup(value, table):
    return next(score for lower,score in reversed(table) if value>=lower)


def glucose(v):
    if v['diabetes']:
        return lookup(v['hba1c_pct'],p.A1C_DIABETES)
    if 'fasting_glucose_mg_dl' in v:
        return 100 if v['fasting_glucose_mg_dl']<p.FBG_NORMAL else 60
    return 100 if v['hba1c_pct']<p.A1C_NORMAL else 60


def calculate(v):
    nicotine=p.NICOTINE[int(v['smoking_status'])]
    if v['inhaled_nicotine']: nicotine=min(nicotine,25)
    components = [
        lookup(v['mepa_score'],p.DIET),
        lookup(v['moderate_min_week']+p.VIGOROUS_WEIGHT*v['vigorous_min_week'],p.ACTIVITY),
        max(0,nicotine-p.PENALTY*v['indoor_smoke']),
        max(0,lookup(v['sleep_h'],p.SLEEP)-p.PENALTY*v.get('sleep_apnea_penalty',0)),
        lookup(v['bmi_kg_m2'],p.BMI_ASIAN if v['bmi_asian_scale'] else p.BMI),
        max(0,lookup(v['non_hdl_mg_dl'],p.LIPIDS)-p.PENALTY*v['lipid_treated']),
        max(0,glucose(v)-p.PENALTY*v.get('prediabetes_penalty',0)),
        max(0,min(lookup(v['sbp_mmhg'],p.SBP),lookup(v['dbp_mmhg'],p.DBP))-p.PENALTY*v['bp_treated']),
    ]
    total=sum(components)
    score=total/p.N_METRICS
    return {**{k+'_score':s for k,s in zip(p.METRICS,components)},
            'score_sum':total,'le8_score':score,'cvh_category':lookup(score,p.CATEGORY)}


def problem(key,msg,kind='unsupported'):
    return skillkit.Problem(key,key,kind,msg)


def validate(v):
    problems=[]
    for k in (*p.FLAGS,'smoking_status','mepa_score','moderate_min_week','vigorous_min_week'):
        if k in v and v[k]!=int(v[k]):
            problems.append(problem(k,f'{k} 必须为整数，状态项请按说明编码。','range'))
    if v.get('bmi_kg_m2',20)<18.5:
        problems.append(problem('bmi_kg_m2','BMI 低于 18.5 时原文要求医生判断，本技能不能自动赋分。'))
    if v.get('sbp_mmhg',200)<=v.get('dbp_mmhg',0):
        problems.append(problem('sbp_mmhg','收缩压应高于舒张压，请核实两项读数。','range'))
    if v.get('moderate_min_week',0)+v.get('vigorous_min_week',0)>10080:
        problems.append(problem('moderate_min_week','两种强度的实际运动时长之和超过一周总分钟数。','range'))
    if v.get('diabetes')==1:
        if 'hba1c_pct' not in v:
            problems.append(problem('hba1c_pct','有糖尿病史时需要 HbA1c（%），不能以空腹血糖代替。','missing'))
        if v.get('prediabetes_penalty',0):
            problems.append(problem('prediabetes_penalty','糖尿病分支不适用糖尿病前期的酌情扣分。'))
    elif v.get('diabetes')==0:
        available=[]
        for k,normal,limit in [('fasting_glucose_mg_dl',p.FBG_NORMAL,p.FBG_UNCLASSIFIED),('hba1c_pct',p.A1C_NORMAL,p.A1C_UNCLASSIFIED)]:
            if k in v:
                if v[k]>=limit:
                    problems.append(problem(k,'无糖尿病史但血糖超出原文无糖尿病评分档；请由医生核实病史和结果，不自动诊断或套用糖尿病分支。'))
                available.append(v[k]<normal)
        if not available:
            problems.append(problem('fasting_glucose_mg_dl','请提供空腹血糖或 HbA1c；八项不齐不计算总分。','missing'))
        elif len(set(available))>1:
            problems.append(problem('hba1c_pct','空腹血糖与 HbA1c 对应不同评分档，原文没有裁决规则；请核实同一评估时点的数据。'))
        if v.get('prediabetes_penalty',0) and not all(available):
            problems.append(problem('prediabetes_penalty','原文酌情扣分仅针对糖尿病前期接受治疗且血糖已正常的情形。'))
    return problems


def load(path,manifest,partial=False):
    try:
        got=skillkit.collect_file(path,manifest)
    except (OSError,ValueError,csv.Error) as e:
        return {},[problem('file',f'无法读取测量 CSV：{e}','parse')]
    problems=[x for x in got.problems if not partial or x.kind!='missing']
    problems += [problem('marker',f'无法识别指标：{name}，请核实表头和名称。','unknown') for name in got.unmatched]
    return got.values,problems


def levers(v,targets,manifest):
    current=calculate(v)['le8_score']
    specs={x['key']:x for x in manifest['inputs']}
    out={'schema':'longevity-levers/1','model':'lifes-essential-8','model_zh':TITLE,
         'current':{'le8_score':current},'sensitivity':[], 'levers':[],
         'note_zh':'离散评分不输出伪精确导数。逐项情景和联合情景均固定病史、用药状态及评分尺度；分数变化不代表干预的因果获益。'}
    for k,target in targets.items():
        score=calculate({**v,k:target})['le8_score']
        out['levers'].append({'key':k,'label_zh':specs[k]['label_zh'],'unit':specs[k]['unit'],
                              'from':v[k],'to':target,'le8_score':score,'le8_delta':score-current})
    if targets:
        score=calculate({**v,**targets})['le8_score']
        out['targets']={'values':targets,'le8_score':score,'le8_delta':score-current}
    return out


def main(argv=None):
    parser=argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements',type=Path)
    parser.add_argument('--age',help='实足年龄（岁），成人规则从20岁起')
    parser.add_argument('--sex',help='仅作上下文，不进入本实现的评分')
    parser.add_argument('--targets',type=Path)
    parser.add_argument('--out',type=Path,default=Path('out'))
    args=parser.parse_args(argv)
    m=skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True,exist_ok=True)
    for name in ('result.json','problems.json','report.md','levers.json'):
        (args.out/name).unlink(missing_ok=True)
    v,problems=load(args.measurements,m)
    try:
        age=skillkit.parse_number(args.age) if args.age is not None else None
        problems+=skillkit.check_scalar(m,'age',age)
    except (ValueError,TypeError):
        problems.append(problem('age','实足年龄必须是有限数值。','parse'))
    problems+=validate(v)
    targets={}
    if args.targets:
        targets,extra=load(args.targets,m,True);problems+=extra
        for k in targets:
            if k not in p.TARGET_KEYS:
                problems.append(problem(k,'目标情景只接受测量和行为数值；不能修改病史、用药状态或评分规则。'))
            elif k not in v:
                problems.append(problem(k,'目标指标必须有对应的当前测量。','missing'))
        if not targets and not extra:
            problems.append(problem('targets','目标文件没有可重算的指标。','missing'))
        if not problems:
            problems+=validate({**v,**targets})
            for k,t in targets.items(): problems+=validate({**v,k:t})
    card=[f'# {TITLE}','']+paper_card_lines()+['']
    if problems:
        path=skillkit.write_problems(args.out,problems,TITLE,BOUNDARY)
        path.write_text('\n'.join(card)+path.read_text().split('\n',1)[1],encoding='utf-8')
        skillkit.write_result(args.out,m,{x['key']:None for x in m['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    outputs=calculate(v)
    skillkit.write_result(args.out,m,outputs)
    lev=levers(v,targets,m)
    (args.out/'levers.json').write_text(json.dumps(lev,ensure_ascii=False,indent=2)+'\n')
    lines=card+['## 你的结果','',f"LE8 总分：**{outputs['le8_score']:.2f}/100**；心血管健康分档：**{outputs['cvh_category']}**。",'',
       '| 项目 | 得分 |','|---|---:|']
    lines += [f'| {label} | {outputs[k+"_score"]:g} |' for k,label in zip(p.METRICS,p.LABELS)]
    lines += ['',f"八项合计 {outputs['score_sum']:g} 分，除以 {p.N_METRICS}；保留未四舍五入的均值用于分档。",
       'BMI 尺度：'+('原文亚洲/太平洋祖源调整尺度。' if v['bmi_asian_scale'] else '原文通用成人尺度。'),
       '年龄范围为成人；饮食输入为已完成的成人 16 项 MEPA 总分。用药扣分反映评分构造，并不意味着药物有害。',
       '睡眠呼吸暂停及糖尿病前期治疗的酌情扣分仅按提供的医生决定应用；未提供时不应用。']
    if targets:
        lines += ['', '## 目标情景','',f"所有目标同时代入：{lev['targets']['le8_score']:.2f} 分，变化 {lev['targets']['le8_delta']:+.2f} 分。",'',
                  '| 单独变化的指标 | 当前值 → 目标值 | 总分变化 |','|---|---|---:|']
        lines += [f"| {x['label_zh']} | {x['from']:g} → {x['to']:g} {x['unit']} | {x['le8_delta']:+.2f} |" for x in lev['levers']]
        lines += ['',lev['note_zh']]
    lines += ['',f'边界：{BOUNDARY}']
    (args.out/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
