#!/usr/bin/env python3
"""Framingham 2008 general CVD continuous Cox equations, offline, standard library."""
import argparse
import copy
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COEFFICIENTS, DERIVATION_AGES, MODEL_KEYS, NORMAL

TITLE = 'Framingham 十年总体心血管风险'


def linear_predictor(values, age, sex, treated, smoker, diabetes, model):
    c = COEFFICIENTS[model][sex]
    total = c['age'] * math.log(age)
    total += c['sbp_treated' if treated else 'sbp_untreated'] * math.log(values['sbp_mmhg'])
    total += sum(c[key] * math.log(values[key]) for key in MODEL_KEYS[model] if key != 'sbp_mmhg')
    return total + c['smoker'] * smoker + c['diabetes'] * diabetes


def risk(total, c):
    return -100 * math.expm1(math.log(c['s10']) * math.exp(total - c['mean']))


def compute(values, age, sex, treated, smoker, diabetes, model='lipids'):
    c = COEFFICIENTS[model][sex]
    total = linear_predictor(values, age, sex, treated, smoker, diabetes, model)
    normal_total = linear_predictor(NORMAL, age, sex, False, False, False, model)
    # Algebraic inversion of the same equation at normal factors, not a fitted constant.
    heart_age = age * math.exp((total - normal_total) / c['age'])
    return {'model': model, 'risk_10y_pct': risk(total, c), 'linear_predictor': total,
            'normal_risk_10y_pct': risk(normal_total, c), 'heart_age_years': heart_age,
            'heart_age_difference_years': heart_age - age}


def levers(values, age, sex, treated, smoker, diabetes, model, targets, manifest):
    def evaluate(v):
        return compute(v, age, sex, treated, smoker, diabetes, model)['risk_10y_pct']
    current = evaluate(values)
    result = {'schema': 'longevity-levers/1', 'model': f'framingham-general-cvd-{model}',
              'model_zh': TITLE, 'current': {'risk_pct': current}, 'sensitivity': [], 'levers': [],
              'population_age_years': list(DERIVATION_AGES), 'age_outside_derivation': False,
              'note_zh': '变化单位是风险百分点；仅替换指定测量值，年龄、性别、吸烟、糖尿病和降压治疗保持原状。'
                         '这是模型情景，不是实际干预可获得的收益，也不提供目标值或用药建议。'}
    c = COEFFICIENTS[model][sex]
    total = linear_predictor(values, age, sex, treated, smoker, diabetes, model)
    hazard = -math.log(c['s10']) * math.exp(total - c['mean'])
    for key in MODEL_KEYS[model]:
        spec = skillkit.spec_by_key(manifest, key)
        beta = c['sbp_treated' if treated else 'sbp_untreated'] if key == 'sbp_mmhg' else c[key]
        result['sensitivity'].append({'key': key, 'label_zh': spec['label_zh'], 'unit': spec['unit'],
                                      'value': values[key],
                                      'per_unit': 100 * math.exp(-hazard) * hazard * beta / values[key]})
    for key, target in targets.items():
        spec = skillkit.spec_by_key(manifest, key)
        moved = evaluate({**values, key: target})
        result['levers'].append({'key': key, 'label_zh': spec['label_zh'], 'unit': spec['unit'],
                                 'from': values[key], 'to': target, 'risk_pct': moved,
                                 'risk_delta_pct': moved - current})
    if targets:
        together = evaluate({**values, **targets})
        result['targets'] = {'values': targets, 'risk_pct': together, 'risk_delta_pct': together-current}
        result['levers'].sort(key=lambda item: item['risk_delta_pct'])
    return result


def with_card(text):
    rows = text.splitlines()
    return '\n'.join([rows[0], '', *paper_card_lines(), '', *rows[1:]]) + '\n'


def issue(key, kind, message):
    return skillkit.Problem(key, key, kind, message)


def load_measurements(path, manifest):
    try:
        return skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return skillkit.Collected(problems=[issue('file', 'parse', f'无法读取测量表：{exc}')])


def parse_yes_no(raw):
    value = str(raw).strip().lower()
    if value in {'yes', 'y', 'true', '1', '是', '有'}:
        return True
    if value in {'no', 'n', 'false', '0', '否', '无'}:
        return False
    return None


def write_report(args):
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'problems.json', 'result.json', 'levers.json'):
        (out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    problems = []
    model = args.model
    if model not in MODEL_KEYS:
        problems.append(issue('model', 'parse', '模型只能是 lipids（血脂版）或 bmi（非化验版）。'))
        model = 'lipids'  # Only to collect input errors; the invalid model never computes.
    selected = copy.deepcopy(manifest)
    for spec in selected['inputs']:
        if spec['from'] == 'measurements':
            spec['required'] = spec['key'] in MODEL_KEYS[model]
    collected = load_measurements(args.measurements, selected)
    problems.extend(collected.problems)
    try:
        age = float(args.age) if args.age is not None else None
        problems.extend(skillkit.check_scalar(manifest, 'age', age))
    except (ValueError, TypeError):
        age = None
        problems.append(issue('age', 'parse', '年龄需要以岁为单位填写有限数值。'))
    sex = {'male':'male', 'm':'male', '男':'male', 'female':'female', 'f':'female', '女':'female'}.get(str(args.sex).lower())
    if sex is None:
        problems.append(issue('sex', 'missing' if args.sex is None else 'parse', '需要论文分层性别：male/男 或 female/女。'))
    flags = {}
    for key in ('treated', 'smoker', 'diabetes', 'prior_cvd'):
        raw = getattr(args, key)
        value = parse_yes_no(raw)
        if value is None:
            label = skillkit.spec_by_key(manifest, key)['label_zh']
            problems.append(issue(key, 'missing' if raw is None else 'parse', f'请明确{label}：yes/是 或 no/否，不能按未知填否。'))
        flags[key] = value
    if flags['prior_cvd'] is True:
        problems.append(issue('prior_cvd', 'population', '已有心血管病不符合首次事件模型；本次不计算。'))
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(selected)
        target_manifest['inputs'] = [s for s in target_manifest['inputs'] if s['key'] in MODEL_KEYS[model]]
        for spec in target_manifest['inputs']:
            spec['required'] = False
        target_data = load_measurements(args.targets, target_manifest)
        problems.extend(target_data.problems)
        for key in target_data.unmatched:
            problems.append(issue(key, 'target', f'当前模型不接受目标项「{key}」；只能填写本模型的连续测量值。'))
        targets = target_data.values
        if not targets and not target_data.problems:
            problems.append(issue('targets', 'missing', '目标表中没有可用测量值。'))
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        path.write_text(with_card(path.read_text()), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values = collected.values
    result = compute(values, age, sex, flags['treated'], flags['smoker'], flags['diabetes'], model)
    skillkit.write_result(out, manifest, result)
    changes = levers(values, age, sex, flags['treated'], flags['smoker'], flags['diabetes'], model, targets, manifest)
    (out / 'levers.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 个人结果', '',
             f"- 十年首次总体心血管事件风险：**{result['risk_10y_pct']:.1f}%**。",
             f"- 连续方程心脏/血管年龄：{result['heart_age_years']:.1f} 岁，与实足年龄差 {result['heart_age_difference_years']:+.1f} 岁。",
             f"- 相同性别、相同年龄、参考风险因素下的风险：{result['normal_risk_10y_pct']:.1f}%。",
             '', '## 输入与含义', '',
             f"模型：{'血脂版' if model == 'lipids' else 'BMI 非化验版'}；年龄 {age:g} 岁；性别 {'男' if sex == 'male' else '女'}。", '']
    for key in MODEL_KEYS[model]:
        spec = skillkit.spec_by_key(manifest, key)
        lines.append(f"- {spec['label_zh']}：{values[key]:g} {spec['unit']}")
    for key in ('treated', 'smoker', 'diabetes', 'prior_cvd'):
        lines.append(f"- {skillkit.spec_by_key(manifest, key)['label_zh']}：{'是' if flags[key] else '否'}")
    unused = set(values) - set(MODEL_KEYS[model])
    if unused or collected.unmatched:
        lines.append('本模型未使用的额外行：' + '、'.join(sorted(unused) + collected.unmatched) + '。')
    lines += ['', '总体结局包括冠心病、脑血管事件、间歇性跛行及心力衰竭；不能当作单独心肌梗死、ASCVD 或死亡风险。',
              '论文使用医生测量的两次坐位左臂血压均值。糖尿病按已有诊断信息填写，本报告不凭一项血糖诊断糖尿病。',
              '参考状态为未接受降压治疗、收缩压 125 mmHg、不吸烟、无糖尿病，'
              + ('总胆固醇 180 mg/dL、HDL-C 45 mg/dL。' if model == 'lipids' else 'BMI 22.5 kg/m²。')
              + '这是原模型的风险对照，不是个人治疗目标。',
              '心脏年龄由连续方程反解；论文整数积分表的心脏年龄可能不同。',
              '模型来自以白人为主的历史美国人群，适用于 30–74 岁、既往无心血管病者；未经本报告对中国人群重新校准。']
    if not DERIVATION_AGES[0] <= result['heart_age_years'] <= DERIVATION_AGES[1]:
        lines.append('此等价心脏年龄超出模型推导年龄范围，仅为方程外推值，不能解释为实测器官年龄。')
    if targets:
        lines += ['', '## 目标值情景', '',
                  f"同时替换所填测量值后风险为 {changes['targets']['risk_pct']:.1f}%，"
                  f"相对当前变化 {changes['targets']['risk_delta_pct']:+.2f} 个百分点。",
                  changes['note_zh']]
        for lever in changes['levers']:
            lines.append(f"- 仅替换{lever['label_zh']}：{lever['from']:g} → {lever['to']:g} {lever['unit']}，"
                         f"风险变化 {lever['risk_delta_pct']:+.2f} 个百分点。")
    lines += ['', f'边界：{BOUNDARY}']
    (out / 'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return 0


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--model', default='lipids')
    parser.add_argument('--age')
    parser.add_argument('--sex')
    for name in ('treated', 'smoker', 'diabetes', 'prior-cvd'):
        parser.add_argument('--'+name)
    parser.add_argument('--out', type=Path, default=Path('out'))
    return write_report(parser.parse_args())


if __name__ == '__main__':
    raise SystemExit(main())
