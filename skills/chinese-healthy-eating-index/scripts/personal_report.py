#!/usr/bin/env python3
"""CHEI 2017: energy-density scoring from confirmed daily standard portions."""
import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (TITLE, BOUNDARY, INPUTS, COMPONENTS, DIET_KEYS, ENERGY_SCALE,
                     GRAM_TO_MG, ALCOHOL, ADULT_AGE)


def score_item(key, value, age=None, sex=None, pregnant_lactating=False):
    c = COMPONENTS[key]
    if key == 'alcohol':
        if age is None or sex not in ALCOHOL:
            raise ValueError('Alcohol scoring requires age and sex.')
        if age < ADULT_AGE or pregnant_lactating:
            return c['max'] if value == 0 else 0
        full, zero = ALCOHOL[sex]
    else:
        full, zero = c['full'], c['zero']
    fraction = (value - zero) / (full - zero)
    return c['max'] * min(1.0, max(0.0, fraction))


def densities(values):
    scale = ENERGY_SCALE / values['energy_kcal_d']
    result = {}
    for key, c in COMPONENTS.items():
        x = values[c['input']]
        if key not in ('added_sugars', 'alcohol'):
            x *= scale
        if key == 'sodium':
            x *= GRAM_TO_MG
        result[key] = x
    return result


def score(values, age, sex):
    d = densities(values)
    points = {key + '_score': score_item(key, value, age, sex, bool(values['pregnant_lactating_yes']))
              for key, value in d.items()}
    return {'chei_total': sum(points.values()), **points}


def collect(path, manifest, partial=False):
    if partial:
        manifest = {**manifest, 'inputs': [{**s, 'required': False} for s in manifest['inputs']]}
    try:
        got = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, csv.Error, AttributeError) as e:
        return {}, [skillkit.Problem('intake', '饮食记录', 'file', f'无法读取记录表：{e}')]
    problems = list(got.problems)
    for name in got.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'不认识项目「{name}」，请使用清单中的项目名。'))
    if 'pregnant_lactating_yes' in got.values and got.values['pregnant_lactating_yes'] not in (0, 1):
        problems.append(skillkit.Problem('pregnant_lactating_yes', '孕期或哺乳期', 'category', '孕期或哺乳期只能填 1 或 0。'))
    if partial:
        if not got.values and not problems:
            problems.append(skillkit.Problem('targets', '目标表', 'missing', '目标表至少需要一项有效饮食数据。'))
        for key in set(got.values) - set(DIET_KEYS):
            problems.append(skillkit.Problem(key, INPUTS[key]['label_zh'], 'target', '孕期或哺乳期状态不能作为饮食目标改变。'))
    return got.values, problems


def consistency(values, sex):
    problems = []
    if values.get('dark_vegetables_sp_d', 0) > values.get('total_vegetables_sp_d', float('inf')):
        problems.append(skillkit.Problem('dark_vegetables_sp_d', '深色蔬菜', 'consistency', '深色蔬菜是总蔬菜的一部分，标准份数不能超过总蔬菜。'))
    if sex == 'male' and values.get('pregnant_lactating_yes') == 1:
        problems.append(skillkit.Problem('pregnant_lactating_yes', '孕期或哺乳期', 'consistency', '孕期或哺乳期与所选论文性别分组不一致，请核对。'))
    return problems


def profile(manifest, raw_age, sex):
    age = None
    problems = []
    if raw_age is not None:
        try:
            age = skillkit.parse_number(raw_age)
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须是有限数值（岁）。'))
    if not problems:
        problems += skillkit.check_scalar(manifest, 'age', age)
    if sex not in ALCOHOL:
        problems.append(skillkit.Problem('sex', '论文性别分组', 'missing' if sex is None else 'category', '请提供 --sex male 或 female，用于论文的酒精评分规则。'))
    return age, problems


def levers(values, targets, age, sex):
    current = score(values, age, sex)['chei_total']
    sensitivity = []
    for key in DIET_KEYS:
        x = values[key]
        lo, hi = INPUTS[key]['range']
        h = max(abs(x), 1.0) * 1e-6  # Numerical step, not a paper coefficient.
        lower, upper = max(lo, x - h), min(hi, x + h)
        left = (current - score({**values, key: lower}, age, sex)['chei_total']) / (x - lower) if lower < x else None
        right = (score({**values, key: upper}, age, sex)['chei_total'] - current) / (upper - x) if upper > x else None
        discontinuous = key == 'alcohol_g_d' and (age < ADULT_AGE or values['pregnant_lactating_yes'] == 1) and x == 0
        sensitivity.append({'key': key, 'label_zh': INPUTS[key]['label_zh'], 'unit': INPUTS[key]['unit'],
                            'display_unit': INPUTS[key]['display_unit'], 'value': x,
                            'left_score_per_unit': None if discontinuous else left,
                            'right_score_per_unit': None if discontinuous else right,
                            'discontinuous': discontinuous,
                            'delta_if_any_positive_alcohol': -COMPONENTS['alcohol']['max'] if discontinuous else None})
    out = {'schema': 'longevity-levers/1', 'model': 'chei_2017', 'model_zh': TITLE,
           'current': {'chei_total': current}, 'sensitivity': sensitivity, 'levers': [],
           'note_zh': '敏感度为固定其他记录值时的左右数值导数；切点可有不同左右斜率，未成年人及孕哺期零饮酒处显示离散跳变。食物、总能量及添加糖能量占比并不独立；这里只做算术情景，不生成目标，也不估计健康收益。'}
    for key, target in targets.items():
        changed = {**values, key: target}
        problems = consistency(changed, sex)
        lever = {'key': key, 'label_zh': INPUTS[key]['label_zh'], 'unit': INPUTS[key]['unit'],
                 'display_unit': INPUTS[key]['display_unit'], 'from': values[key], 'to': target,
                 'computable': not problems}
        if problems:
            lever['problem_zh'] = '；'.join(p.message_zh for p in problems)
        else:
            total = score(changed, age, sex)['chei_total']
            lever.update(chei_total=total, chei_total_delta=total-current)
        out['levers'].append(lever)
    if targets:
        total = score({**values, **targets}, age, sex)['chei_total']
        out['targets'] = {'values': targets, 'chei_total': total, 'chei_total_delta': total-current}
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--intake', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'levers.json', 'problems.json'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.intake, manifest)
    age, errors = profile(manifest, args.age, args.sex)
    problems += errors + consistency(values, args.sex)
    targets = {}
    if args.targets is not None:
        targets, errors = collect(args.targets, manifest, partial=True)
        errors += consistency({**values, **targets}, args.sex)
        problems += [skillkit.Problem(p.key, p.label, p.kind, '目标表：' + p.message_zh) for p in errors]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        head, rest = path.read_text(encoding='utf-8').split('\n', 1)
        path.write_text(head + '\n\n' + '\n'.join(paper_card_lines()) + '\n' + rest, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = score(values, age, args.sex)
    changes = levers(values, targets, age, args.sex)
    d = densities(values)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f"CHEI 总分：**{outputs['chei_total']:.2f} / 100 分**。",
             '分数越高，越符合本版指南的评分规则；不另划疾病风险等级。', '',
             '| 项目 | 每日记录 | 计分用值 | 得分 / 满分 |', '| --- | --- | --- | --- |']
    for key, c in COMPONENTS.items():
        inp = c['input']
        lines.append(f"| {c['label_zh']} | {values[inp]:g} {INPUTS[inp]['display_unit']} | {d[key]:.4g} {c['density_unit']} | {outputs[key+'_score']:.2f} / {c['max']} |")
    lines += ['', f"总能量：{values['energy_kcal_d']:g} kcal/d。食品和能量须来自同一记录时段的每日平均值。",
              '标准份（SP）不等于一碗、一杯或任意食物的固定克数。本文未公开全部食物的逐项换算表；仅接受已确认的标准份数，不自动把普通份数当作 SP。',
              '钠按本文口径记录食盐及高钠食品中的钠，不是食盐重量；添加糖占比不是总糖占比。',
              '三日记录可能漏掉偶尔食用的食物；原研究并非全国代表性调查。孕哺期、幼儿和素食者的适用性仍待验证。']
    if age < ADULT_AGE or values['pregnant_lactating_yes'] == 1:
        lines.append('本次酒精项采用未成年人或孕哺期规则：零摄入得满分，任何正摄入得零分。')
    if targets:
        lines += ['', '## 你提供的目标对应的分数', '',
                  f"全部目标同时成立时：{changes['targets']['chei_total']:.2f} 分；变化 {changes['targets']['chei_total_delta']:+.2f} 分。"]
        for item in changes['levers']:
            text = f"- {item['label_zh']}：{item['from']:g} → {item['to']:g} {item['display_unit']}；"
            text += f"仅改变此项时总分变化 {item['chei_total_delta']:+.2f} 分。" if item['computable'] else item['problem_zh'] + '，不单独计算。'
            lines.append(text)
        lines.append('改变食物时需同时核对总能量和添加糖供能比例；这里的分数变化不等于健康收益。')
    lines += ['', f'边界：{BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
