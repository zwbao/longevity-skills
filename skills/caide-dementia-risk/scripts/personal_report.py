#!/usr/bin/env python3
"""CAIDE score models 1 and 2 from the printed 2006 paper; standard library."""
import argparse
import json
from pathlib import Path
import skillkit
from paper_card import lines as paper_card_lines
from presets import (TITLE, BOUNDARY, CATEGORIES, AGE_CUTOFFS, EDUCATION_CUTOFFS,
                     BINARY_CUTOFFS, LOGISTIC, GROUPS, MODIFIABLE, SCENARIO_NOTE)
import math


def term_scores(v, model):
    categories=CATEGORIES[model]
    indices={'age':0 if v['age'] < AGE_CUTOFFS[0] else (1 if v['age'] <= AGE_CUTOFFS[1] else 2),
             'education_years':0 if v['education_years'] <= EDUCATION_CUTOFFS[0] else
                                (1 if v['education_years'] <= EDUCATION_CUTOFFS[1] else 2),
             'sex':int(v['sex']=='male'), 'physical_active_1':int(v['physical_active_1'])}
    indices.update({k:int(v[k]>cutoff) for k,cutoff in BINARY_CUTOFFS.items()})
    if model=='apoe': indices['apoe_e4_1']=int(v['apoe_e4_1'])
    return {k:categories[k][i][1] for k,i in indices.items()}


def group_for_score(score, model):
    for low,high,risk,ci_low,ci_high in GROUPS[model]:
        if low<=score<=high:
            return dict(category=f'{low}–{high}',risk_pct=risk,ci_low_pct=ci_low,ci_high_pct=ci_high)
    raise ValueError('Score outside published table')


def from_score(score, model):
    b0,b1,b2=LOGISTIC[model]
    group=group_for_score(score,model)
    return dict(model=model,score=score,model_risk_20y_pct=100/(1+math.exp(-(b0+b1+b2*score))),
                score_category=group['category'],group_risk_pct=group['risk_pct'],
                group_ci_low_pct=group['ci_low_pct'],group_ci_high_pct=group['ci_high_pct'])


def calculate(v, model):
    return from_score(sum(term_scores(v,model).values()),model)


def levers(v, targets, model, manifest):
    current=calculate(v,model)
    terms=term_scores(v,model)
    specs={x['key']:x for x in manifest['inputs']}
    sensitivities=[]
    for key,old_score in terms.items():
        transitions=[]
        for label,new_score in CATEGORIES[model][key]:
            result=from_score(current['score']-old_score+new_score,model)
            transitions.append({'category':label,'term_score':new_score,
                                'delta_score':new_score-old_score,
                                'model_risk_20y_pct':result['model_risk_20y_pct'],
                                'delta_model_risk_pp':result['model_risk_20y_pct']-current['model_risk_20y_pct']})
        sensitivities.append({'key':key,'label_zh':specs[key]['label_zh'],'unit':specs[key].get('unit',''),
                              'value':v[key],'modifiable':key in MODIFIABLE,'term_score':old_score,
                              'kind':'category_transition','transitions':transitions})
    result={'schema':'longevity-levers/1','model':f'caide_{model}','model_zh':TITLE,
            'current':current,'sensitivity':sensitivities,'levers':[], 'note_zh':SCENARIO_NOTE}
    for key,target in targets.items():
        after=calculate(dict(v,**{key:target}),model)
        result['levers'].append({'key':key,'label_zh':specs[key]['label_zh'],'unit':specs[key]['unit'],
                                'current':v[key],'target':target,'result':after,
                                'delta_score':after['score']-current['score'],
                                'delta_model_risk_pp':after['model_risk_20y_pct']-current['model_risk_20y_pct']})
    if targets:
        after=calculate(dict(v,**targets),model)
        result['combined']={'targets':targets,'result':after,'delta_score':after['score']-current['score'],
                            'delta_model_risk_pp':after['model_risk_20y_pct']-current['model_risk_20y_pct']}
    return result


def issue(key, message, kind='value'):
    return skillkit.Problem(key,key,kind,message)


def collect(path, manifest, targets=False):
    try:
        data=skillkit.collect_file(path,manifest)
    except (OSError,ValueError,UnicodeError) as exc:
        return {},[issue('file',f'无法读取输入文件：{exc}','file')]
    problems=[p for p in data.problems if not (targets and p.kind=='missing')]
    problems += [issue(k,f'未识别的指标：{k}，请使用说明中的指标名。','unknown') for k in data.unmatched]
    for key in ('physical_active_1','apoe_e4_1'):
        if key in data.values and data.values[key] not in (0,1):
            problems.append(issue(key,f'{key} 必须明确填 0 或 1，未知不能当成 0。'))
    if 'education_years' in data.values and not data.values['education_years'].is_integer():
        problems.append(issue('education_years','受教育年限请填已完成的整年数；不对小数自动取整。'))
    if targets:
        problems += [issue(k,f'{k} 不是本技能允许的目标；目标仅限收缩压、BMI、总胆固醇和身体活动。')
                     for k in data.values if k not in MODIFIABLE]
        if not data.values and not problems: problems.append(issue('targets','目标文件没有可用目标。'))
    return data.values,problems


def main():
    parser=argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements',type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--model',default='basic',choices=('basic','apoe'))
    parser.add_argument('--targets',type=Path)
    parser.add_argument('--out',type=Path,default=Path('out'))
    args=parser.parse_args()
    manifest=skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True,exist_ok=True)
    # Remove only our own prior generated outputs, so failure cannot expose stale results.
    for filename in ('result.json','levers.json','problems.json','report.md'):
        (args.out/filename).unlink(missing_ok=True)
    values,problems=collect(args.measurements,manifest)
    try:
        age=skillkit.parse_number(args.age) if args.age is not None else None
        problems+=skillkit.check_scalar(manifest,'age',age)
    except ValueError:
        age=None; problems.append(issue('age','年龄必须是有限数值（岁）。'))
    values['age']=age
    if args.sex not in ('female','male'):
        problems.append(issue('sex','请按原研究分类填写 --sex female 或 male；不能推断。','missing' if args.sex is None else 'value'))
    values['sex']=args.sex
    if args.model=='apoe' and 'apoe_e4_1' not in values:
        problems.append(issue('apoe_e4_1','APOE 模型缺少明确的 ε4 携带状态；未知不能当作非携带。','missing'))
    targets={}
    if args.targets is not None:
        targets,target_problems=collect(args.targets,manifest,targets=True)
        problems+=target_problems
    if problems:
        path=skillkit.write_problems(args.out,problems,TITLE,BOUNDARY)
        lines=path.read_text().splitlines()
        path.write_text('\n'.join(lines[:2]+paper_card_lines()+['']+lines[2:])+'\n')
        return skillkit.EXIT_INPUT_PROBLEM
    result=calculate(values,args.model)
    terms=term_scores(values,args.model)
    scenario=levers(values,targets,args.model,manifest)
    skillkit.write_result(args.out,manifest,result)
    (args.out/'levers.json').write_text(json.dumps(scenario,ensure_ascii=False,indent=2)+'\n')
    specs={x['key']:x for x in manifest['inputs']}
    lines=[f'# {TITLE}','',*paper_card_lines(),'','## 你的结果','',
           f"采用模型：{'模型 1（不含 APOE）' if args.model=='basic' else '模型 2（含 APOE）'}。",
           f"你的 CAIDE 总分：**{result['score']} 分**；表 3 分组：{result['score_category']} 分。",
           f"这一分组在原研究中的痴呆发生率为 {result['group_risk_pct']:.1f}%",
           f"（分组的 95% 置信区间：{result['group_ci_low_pct']:.1f}%–{result['group_ci_high_pct']:.1f}%）。",
           f"按方法段公式换算的 20 年模型估计为 **{result['model_risk_20y_pct']:.2f}%**。",
           '分组发生率是同档受试者的观察结果；公式估计随总分变化，两者含义不同。',
           '这些数值未按当前中国人群重新校准，也不是包含死亡竞争风险的无条件终生风险。','',
           '| 输入 | 本次值 | 单位 | 分值 |','|---|---:|---|---:|']
    for key,score in terms.items():
        shown={'female':'女','male':'男'}.get(values[key],values[key])
        lines.append(f"| {specs[key]['label_zh']} | {shown} | {specs[key].get('unit','')} | {score} |")
    if 'apoe_e4_1' in values and args.model=='basic':
        lines+=['','本次明确选择模型 1，所提供 APOE 状态未参与此模型。']
    if result['group_ci_low_pct']<0:
        lines+=['','表 3 的置信区间下限原文印为负值，此处保留原值；负值不是可能的发病概率。']
    lines+=['','身体活动达标（1）指休闲活动每周至少两次，每次至少 20–30 分钟且引起出汗和气促；否则为 0。']
    if targets:
        after=scenario['combined']['result']
        lines+=['','## 你提供的目标情景','',
                f"全部目标代入后：{after['score']} 分，公式估计 {after['model_risk_20y_pct']:.2f}%。",
                f"公式估计变化：{scenario['combined']['delta_model_risk_pp']:+.2f} 个百分点。"]
        for item in scenario['levers']:
            lines.append(f"- 仅改变{item['label_zh']}：{item['current']:g} → {item['target']:g} {item['unit']}，分数变化 {item['delta_score']:+d} 分。")
    lines+=['',SCENARIO_NOTE,'',f'边界：{BOUNDARY}']
    (args.out/'report.md').write_text('\n'.join(lines)+'\n')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
