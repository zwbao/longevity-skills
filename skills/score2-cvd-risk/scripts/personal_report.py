#!/usr/bin/env python3
"""SCORE2, using the published updated supplement; standard library only."""
import argparse
import json
import math
from pathlib import Path
import skillkit
from paper_card import lines as paper_card_lines
from presets import (COEFFICIENTS, BASE_SURVIVAL, SCALES, CENTRES, DIVISORS,
                     REGION_ZH, BOUNDARY)


def compute(values, age, sex, region):
    a, sbp, tc, hdl = [(x-c)/d for x,c,d in zip(
        [age, values['sbp_mmhg'], values['tc_mmol_l'], values['hdl_mmol_l']], CENTRES, DIVISORS)]
    smoke = values['smoker']
    terms = (a, smoke, sbp, tc, hdl, a*smoke, a*sbp, a*tc, a*hdl)
    lp = sum(x*b for x,b in zip(terms, COEFFICIENTS[sex]))
    log_hazard = math.log(-math.log(BASE_SURVIVAL[sex])) + lp
    scale1, scale2 = SCALES[region][sex]
    return {'linear_predictor': lp, 'uncalibrated_risk': -math.expm1(-math.exp(log_hazard)),
            'risk_10y_pct': -100*math.expm1(-math.exp(scale1 + scale2*log_hazard))}


def levers(values, age, sex, region, targets, manifest):
    risk = lambda v: compute(v, age, sex, region)['risk_10y_pct']
    current = risk(values)
    result = {'schema': 'longevity-levers/1', 'model': 'score2', 'model_zh': 'SCORE2 欧洲心血管风险',
              'region': region, 'current': {'risk_pct': current}, 'sensitivity': [], 'levers': [],
              'note_zh': '保持年龄、性别、地区不变；目标情景不代表干预效果，也不代表戒烟后的即时风险。HDL 的关联不等同于提高 HDL 的治疗获益。'}
    for key, x in values.items():
        spec = skillkit.spec_by_key(manifest, key)
        if key == 'smoker':
            per_unit = risk(dict(values, smoker=1)) - risk(dict(values, smoker=0))
            method = '吸烟 1 相对非当前吸烟 0 的模型差'
        else:
            h = max(abs(x),1)*1e-5
            lo, hi = spec['range']
            left, right = max(lo,x-h), min(hi,x+h)
            per_unit = (risk(dict(values, **{key:right})) - risk(dict(values, **{key:left})))/(right-left)
            method = '当前值附近每单位的有限差分'
        result['sensitivity'].append({'key':key, 'label_zh':spec['label_zh'], 'unit':spec['unit'],
                                      'value':x, 'per_unit':per_unit, 'method_zh':method})
    for key, target in targets.items():
        spec = skillkit.spec_by_key(manifest,key)
        moved = risk(dict(values, **{key:target}))
        result['levers'].append({'key':key, 'label_zh':spec['label_zh'], 'unit':spec['unit'],
                                 'from':values[key], 'to':target, 'risk_pct':moved, 'risk_delta_pct':moved-current})
    together = risk(dict(values, **targets))
    result['targets'] = {'values':targets, 'risk_pct':together, 'risk_delta_pct':together-current}
    return result


def problem(key, message, kind='invalid'):
    return skillkit.Problem(key,key,kind,message)


def collect(path, manifest, optional=False):
    try:
        data = skillkit.collect_file(Path(path) if path else None, manifest)
    except (OSError, ValueError, KeyError) as exc:
        return {}, [problem('file',f'无法读取测量表：{exc}')]
    problems = [p for p in data.problems if not (optional and p.kind == 'missing')]
    problems += [problem(name,f'未识别指标：{name}；请使用技能声明的指标名。') for name in data.unmatched]
    if optional and not data.values and not problems:
        problems.append(problem('targets','目标表没有可用指标。'))
    if 'smoker' in data.values and data.values['smoker'] not in (0,1):
        problems.append(problem('smoker','当前吸烟只能填 1，其他状态填 0；不能填比例。'))
    return data.values, problems


def consistency(values):
    if {'tc_mmol_l','hdl_mmol_l'} <= values.keys() and values['hdl_mmol_l'] >= values['tc_mmol_l']:
        return [problem('hdl_mmol_l','HDL 胆固醇必须小于总胆固醇，请核对数值和单位。')]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('measurements','age','sex','region','europe','prior-cvd','diabetes','targets'):
        parser.add_argument('--'+name)
    parser.add_argument('--out',type=Path,default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True,exist_ok=True)
    for name in ('levers.json','problems.json','result.json','report.md'):
        (args.out/name).unlink(missing_ok=True)
    values, problems = collect(args.measurements,manifest)
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest,'age',age)
    except ValueError:
        age = None
        problems.append(problem('age','年龄必须是数值。'))
    for key, allowed in [('sex',('male','female')),('region',tuple(SCALES)),('europe',('yes','no')),
                          ('prior_cvd',('yes','no')),('diabetes',('yes','no'))]:
        value = getattr(args,key)
        if value not in allowed:
            problems.append(problem(key,f'请提供 {key}：可选 '+', '.join(allowed),'missing' if value is None else 'invalid'))
    if args.europe == 'no':
        problems.append(problem('europe','该模型未针对非欧洲人群校准，不能选择欧洲地区套算。','ineligible'))
    for key in ('prior_cvd','diabetes'):
        if getattr(args,key) == 'yes':
            problems.append(problem(key,'该 SCORE2 模型不适用于已有心血管病或糖尿病的人。','ineligible'))
    problems += consistency(values)
    targets = {}
    if args.targets:
        targets, target_problems = collect(args.targets,manifest,optional=True)
        problems += target_problems
        problems += consistency(dict(values, **targets))
        for key,value in targets.items():
            problems += consistency(dict(values, **{key:value}))
    if problems:
        skillkit.write_problems(args.out,problems,'SCORE2 输入待补全',BOUNDARY)
        # Input-error reports carry the same paper card and boundary as successful reports.
        body = (args.out/'report.md').read_text()
        (args.out/'report.md').write_text('\n'.join(paper_card_lines())+'\n\n'+body)
        skillkit.write_result(args.out,manifest,{'risk_10y_pct':None})
        return skillkit.EXIT_INPUT_PROBLEM
    result = compute(values,age,args.sex,args.region)
    risk = result['risk_10y_pct']
    skillkit.write_result(args.out,manifest,{'risk_10y_pct':risk})
    lever = levers(values,age,args.sex,args.region,targets,manifest)
    (args.out/'levers.json').write_text(json.dumps(lever,ensure_ascii=False,indent=2)+'\n')
    lines = paper_card_lines()+['','## 你的结果','',
        f'按{REGION_ZH[args.region]}校准，未来十年首次致死或非致死心血管事件风险估计为 **{risk:.1f}%**。',
        '',f'年龄：{age:g} 岁；模型性别：'+('男性' if args.sex=='male' else '女性')+'。',
        '', '| 输入 | 数值 | 单位 |','|---|---:|---|']
    for key,value in values.items():
        spec = skillkit.spec_by_key(manifest,key)
        lines.append(f"| {spec['label_zh']} | {value:g} | {spec['unit']} |")
    lines += ['', '吸烟：1 表示当前吸烟，0 表示其他状态。地区等级是人群校准分组，不是你的个人风险分档。']
    if targets:
        lines += ['', '## 如果达到所填目标','',
                  f"全部目标同时达到时：{lever['targets']['risk_pct']:.1f}%；与当前相差 {lever['targets']['risk_delta_pct']:+.2f} 个百分点。",
                  '', '| 单项目标 | 目标值 | 风险变化（百分点） |','|---|---:|---:|']
        for item in lever['levers']:
            lines.append(f"| {item['label_zh']} | {item['to']:g} {item['unit']} | {item['risk_delta_pct']:+.2f} |")
    lines += ['',lever['note_zh'],'',BOUNDARY,'']
    (args.out/'report.md').write_text('\n'.join(lines),encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
