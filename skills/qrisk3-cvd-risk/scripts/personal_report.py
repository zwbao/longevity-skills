"""Local QRISK3-2017 report; standard library only."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
import presets

TITLE = 'QRISK3 十年心血管风险'
BOUNDARY = '这是英国人群观察性模型的估计，仍在验证，不能替代医生评估，也不能证明改变某项就能获得对应治疗收益；不能据此开始、停止或调整药物。'
NOTE = '目标情景固定其他输入，只显示关联模型内的差异，不是个人干预效果；血压变异度必须来自真实重复记录。'


def problem(key, message, kind='invalid'):
    return skillkit.Problem(key, key, kind, message)


def read_file(path, manifest):
    try:
        c = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, AttributeError, TypeError) as exc:
        return skillkit.Collected(problems=[problem('measurements', f'无法读取测量表：{exc}', 'file')])
    if c.unmatched:
        c.problems.append(problem('measurements', '无法识别的项目：' + '、'.join(c.unmatched), 'unknown'))
    return c


def validate(values, age, sex):
    errors = []
    if sex not in ('male', 'female'):
        errors.append(problem('sex', '需要模型性别 female 或 male；不得自动推断。', 'missing' if sex is None else 'invalid'))
    if age is None:
        errors.append(problem('age', '需要25至84岁的周岁整数。', 'missing'))
    elif not math.isfinite(age) or age != int(age) or not 25 <= age <= 84:
        errors.append(problem('age', '年龄必须为25至84岁的有限周岁整数。'))
    discrete = presets.BINARY_KEYS + ['smoking', 'ethnicity', 'sbp_readings_n', 'prior_cvd', 'statin_use']
    for key in discrete:
        if key in values and values[key] != int(values[key]):
            errors.append(problem(key, f'{key} 必须为整数编码，不能是小数。'))
    if sex == 'male' and 'b_impotence2' not in values:
        errors.append(problem('b_impotence2', '男性模型需要明确勃起功能障碍诊断或治疗状态；未知不能填0。', 'missing'))
    if values.get('b_type1') == 1 and values.get('b_type2') == 1:
        errors.append(problem('b_type1', '糖尿病类型只能为无、1型或2型，不能同时填有。'))
    if values.get('prior_cvd') == 1:
        errors.append(problem('prior_cvd', '既往心血管病不属于本工具计算范围。', 'population'))
    if values.get('statin_use') == 1:
        errors.append(problem('statin_use', '正在使用他汀不属于本工具计算范围；不能为计算而停药。', 'population'))
    return errors


def levers(age, sex, values, targets, manifest):
    current = presets.risk(age, sex, values)
    specs = {x['key']: x for x in manifest['inputs']}
    result = dict(schema='longevity-levers/1', model='qrisk3_2017_model_c',
                  model_zh='QRISK3-2017模型C（仍在验证）',
                  current={'risk_10y_pct': current, 'age': age},
                  sensitivity=[], levers=[], note_zh=NOTE)
    # Numeric derivatives only for continuous covariates, clipped to accepted input domain.
    for key in presets.MODIFIABLE + ('townsend_score',):
        x = values[key]; step = 1e-4 * max(1, abs(x))
        lower, upper = specs[key]['range']
        lo, hi = max(lower, x-step), min(upper, x+step)
        slope = (presets.risk(age, sex, dict(values, **{key:hi})) -
                 presets.risk(age, sex, dict(values, **{key:lo}))) / (hi-lo)
        result['sensitivity'].append(dict(key=key, label_zh=specs[key]['label_zh'],
            unit=specs[key]['unit'], value=x, risk_pct_points_per_unit=slope,
            target_allowed=key in presets.MODIFIABLE))
    # Discrete model terms: alternatives are model contrasts, never treatment targets.
    for key in presets.BINARY_KEYS + ['ethnicity', 'smoking']:
        if sex == 'female' and key == 'b_impotence2': continue
        alternatives = []
        codes = range(1,10) if key == 'ethnicity' else range(5) if key == 'smoking' else range(2)
        for code in codes:
            if code == values[key]: continue
            moved = dict(values, **{key:code})
            if key == 'b_type1' and code == 1: moved['b_type2'] = 0
            if key == 'b_type2' and code == 1: moved['b_type1'] = 0
            q = presets.risk(age, sex, moved)
            alternatives.append({'to':code, 'risk_10y_pct':q, 'risk_delta_pct_points':q-current,
                                 'mutually_exclusive_diabetes':key in ('b_type1','b_type2')})
        result['sensitivity'].append(dict(key=key, value=values[key],
             target_allowed=False, alternatives=alternatives,
             note_zh='类别对照，不是可采取的行动；糖尿病类型对照保持互斥。'))
    ages = [n for n in (age-1, age+1) if 25 <= n <= 84]
    result['sensitivity'].append({'key':'age', 'value':age, 'unit':'a', 'target_allowed':False,
        'alternatives':[{'to':n, 'risk_10y_pct':presets.risk(n,sex,values),
        'risk_delta_pct_points':presets.risk(n,sex,values)-current} for n in ages]})
    other = 'female' if sex == 'male' else 'male'
    if other == 'female' or 'b_impotence2' in values:
        q = presets.risk(age, other, values)
        result['sensitivity'].append({'key':'sex','value':sex,'target_allowed':False,
            'alternatives':[{'to':other,'risk_10y_pct':q,'risk_delta_pct_points':q-current}],
            'note_zh':'不同性别方程的数学对照，不是改变性别的效应。'})
    else:
        result['sensitivity'].append({'key':'sex','value':sex,'target_allowed':False,
            'alternatives':[], 'note_zh':'男性模型还需要勃起功能障碍状态，未补值。'})
    for key, target in targets.items():
        q = presets.risk(age, sex, dict(values, **{key:target}))
        result['levers'].append(dict(key=key, label_zh=specs[key]['label_zh'],
            unit=specs[key]['unit'], **{'from':values[key]}, to=target,
            risk_10y_pct=q, risk_delta_pct_points=q-current))
    if targets:
        q = presets.risk(age, sex, dict(values, **targets))
        result['targets'] = dict(values=targets, risk_10y_pct=q, risk_delta_pct_points=q-current)
    return result


def fail(out, errors):
    path = skillkit.write_problems(out, errors, TITLE, BOUNDARY)
    original = path.read_text()
    path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', *original.splitlines()[2:]])+'\n')
    return skillkit.EXIT_INPUT_PROBLEM


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--out', type=Path, default=Path('out'))
    parser.add_argument('--targets', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ('result.json','problems.json','levers.json','report.md'):
        (args.out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    c = read_file(args.measurements, manifest)
    try:
        age = float(args.age) if args.age is not None else None
    except ValueError:
        age = float('nan')
    errors = c.problems + validate(c.values, age, args.sex)
    targets = {}
    if args.targets:
        target_manifest = dict(manifest, inputs=[dict(s, required=False) for s in manifest['inputs']])
        tc = read_file(args.targets, target_manifest)
        errors += tc.problems
        for key in tc.values:
            if key not in presets.MODIFIABLE:
                errors.append(problem(key, '目标仅接受BMI、TC/HDL比值、收缩压和收缩压标准差。', 'target'))
        if not tc.values and not tc.problems:
            errors.append(problem('targets', '目标文件没有可读取的目标值。', 'target'))
        targets = tc.values
    if errors: return fail(args.out, errors)
    age = int(age)
    value = presets.risk(age, args.sex, c.values)
    scenarios = levers(age, args.sex, c.values, targets, manifest)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
        f'十年心血管病风险（模型估计）：**{value:.2f}%**。', '',
        '结局包括冠心病、缺血性卒中和短暂性脑缺血发作；不是全因死亡或寿命。',
        '适用背景为英格兰基层医疗人群。英国华人亚组的表现不等同于中国居民的校准。',
        '仍在验证：完整个人示例未复现，结果应视为暂定。', '',
        f'血压标准差使用你提供的 {c.values["sbp_sd_mmhg"]:g} mmHg，来自评估前五年内 {c.values["sbp_readings_n"]:g} 次记录；本次未从原始序列重新计算。', '', NOTE]
    if targets:
        lines += ['', f'所有目标同时达到时的模型估计：{scenarios["targets"]["risk_10y_pct"]:.2f}%。']
    lines += ['', f'边界：{BOUNDARY}', '', '原始代码声明（适用于本结果）：', '',
              (Path(__file__).resolve().parents[1] / 'references/disclaimer.txt').read_text().strip()]
    skillkit.write_result(args.out, manifest, {'risk_10y_pct':value})
    (args.out/'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2)+'\n')
    (args.out/'report.md').write_text('\n'.join(lines)+'\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
