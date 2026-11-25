"""Offline Lee 4-year mortality point index. Python standard library only."""
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_POINTS, BINARY_KEYS, BMI_CUTOFF, BOUNDARY,
                     LOW_BMI_POINTS, MALE_POINTS, TARGET_KEYS,
                     VALIDATION_NOTE, VALIDATION_PERCENT, WEIGHTS)


def components(values):
    result = {'age': next(points for minimum, points in reversed(AGE_POINTS)
                          if values['age'] >= minimum),
              'sex': MALE_POINTS * int(values['sex']),
              'bmi_kg_m2': LOW_BMI_POINTS if values['bmi_kg_m2'] < BMI_CUTOFF else 0}
    result.update({key: weight * int(values[key]) for key, weight in WEIGHTS.items()})
    return result


def mortality_for_score(score):
    if not isinstance(score, int) or score < 0:
        raise ValueError('score must be a nonnegative integer')
    return VALIDATION_PERCENT[min(score, len(VALIDATION_PERCENT) - 1)]


def calculate(values):
    total = sum(components(values).values())
    return {'lee_score': total, 'mortality_4y_pct': mortality_for_score(total)}


def problem(key, message, kind='value'):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [problem('file', f'无法读取输入表：{exc}', 'file')]
    problems = list(result.problems)
    for name in result.unmatched:
        problems.append(problem(name, f'无法识别项目「{name}」，请核对名称。', 'unknown'))
    for key, value in result.values.items():
        if key in BINARY_KEYS and value not in (0, 1):
            problems.append(problem(key, f'{key} 必须填0（否）或1（是），未知不能填0。'))
    return result.values, problems


def levers(values, targets, manifest):
    current = calculate(values)
    specs = {s['key']: s for s in manifest['inputs']}
    sensitivity = []
    # Discrete comparisons suit a step score. Do not report continuous slopes.
    for key in components(values):
        x = values[key]
        if key == 'age':
            alternatives = [cut for cut, _ in AGE_POINTS if cut > x]
        elif key == 'bmi_kg_m2':
            # Printed threshold and one-decimal below-threshold example from Table 2.
            alternatives = [BMI_CUTOFF if x < BMI_CUTOFF else 24.9]
        else:
            alternatives = [1 - x]
        comparison = None
        if alternatives:
            target = alternatives[0]
            moved = calculate(dict(values, **{key: target}))
            comparison = {'to': target, **moved,
                          'lee_score_delta': moved['lee_score'] - current['lee_score'],
                          'mortality_delta_pct': moved['mortality_4y_pct'] - current['mortality_4y_pct']}
        sensitivity.append({'key': key, 'label_zh': specs[key]['label_zh'],
                            'unit': specs[key]['unit'], 'value': x,
                            'target_allowed': key in TARGET_KEYS,
                            'method': 'discrete_comparison', 'comparison': comparison})
    data = {'schema': 'longevity-levers/1', 'model': 'lee-mortality-index',
            'model_zh': 'Lee四年死亡风险指数（表3、表4）',
            'current': current, 'sensitivity': sensitivity, 'levers': [],
            'note_zh': BOUNDARY + '离散比较不是连续导数；年龄和病史的比较不是可设目标。'
                       '表4的11分与12分观察死亡率不单调，保留原表。'}
    for key, target in targets.items():
        moved = calculate(dict(values, **{key: target}))
        data['levers'].append({'key': key, 'label_zh': specs[key]['label_zh'],
                               'unit': specs[key]['unit'], 'from': values[key], 'to': target,
                               **moved,
                               'lee_score_delta': moved['lee_score'] - current['lee_score'],
                               'mortality_delta_pct': moved['mortality_4y_pct'] - current['mortality_4y_pct']})
    if targets:
        moved = calculate(dict(values, **targets))
        data['targets'] = {'values': targets, **moved,
                           'lee_score_delta': moved['lee_score'] - current['lee_score'],
                           'mortality_delta_pct': moved['mortality_4y_pct'] - current['mortality_4y_pct']}
    return data


def main():
    parser = argparse.ArgumentParser(description='Lee四年死亡风险指数')
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='整数实足年龄，岁；50岁及以上')
    parser.add_argument('--sex', help='male/female、男/女，或1/0；论文的二分类性别')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except ValueError:
        age = None
        problems.append(problem('age', '年龄必须是有限的数字，单位为岁。', 'parse'))
    problems += skillkit.check_scalar(manifest, 'age', age)
    if age is not None and not age.is_integer():
        problems.append(problem('age', '请填已满的整数周岁，不对年龄四舍五入。'))
    sex = {'male': 1, 'female': 0, '男': 1, '女': 0, '1': 1, '0': 0}.get(
        (args.sex or '').strip().lower())
    problems += skillkit.check_scalar(manifest, 'sex', sex)
    if args.sex is not None and sex is None:
        problems.append(problem('sex', '性别须为male/female、男/女或1/0，不能推断。'))
    if values.get('community_dwelling') == 0:
        problems.append(problem('community_dwelling', '本方法仅用于社区居住者，机构照护人群不计算。', 'population'))
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        for spec in target_manifest['inputs']:
            spec['from'] = 'measurements'
            spec['required'] = False
        targets, target_problems = collect(args.targets, target_manifest)
        problems.extend(target_problems)
        for key in targets:
            if key not in TARGET_KEYS:
                problems.append(problem(key, f'{key} 不是可设目标项；不得把年龄、性别或既往诊断改成治疗目标。', 'target'))
    header = ['# Lee四年死亡风险报告', '', *paper_card_lines(), '', VALIDATION_NOTE, '']
    if problems:
        skillkit.write_problems(args.out, problems, 'Lee四年死亡风险报告', BOUNDARY)
        body = skillkit.problems_markdown(problems, 'Lee四年死亡风险报告', BOUNDARY).split('\n', 2)[2]
        (args.out / 'report.md').write_text('\n'.join(header) + '\n' + body, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values.update(age=age, sex=sex)
    result = calculate(values)
    skillkit.write_result(args.out, manifest, result)
    scenario = levers(values, targets, manifest)
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    labels = {s['key']: s['label_zh'] for s in manifest['inputs']}
    lines = header + ['## 你的结果', '', f"Lee总分：{result['lee_score']}分。",
                      f"表4中验证队列同分组的四年死亡率：{result['mortality_4y_pct']}%。",
                      '这是历史队列的观察比例，按原文整数百分数展示；并非你个人的确定结局。', '',
                      '| 项目 | 输入值 | 得分 |', '|---|---:|---:|']
    for key, points in components(values).items():
        shown = ('男' if sex == 1 else '女') if key == 'sex' else f'{values[key]:g}'
        lines.append(f'| {labels[key]} | {shown} | {points} |')
    lines += ['', '问卷项：1=符合问卷条件，0=不符合。总分达到14分后使用表4的合并组。',
              '风险表没有作平滑处理：分数相邻不保证观察百分数严格递增。']
    if targets:
        goal = scenario['targets']
        lines += ['', '## 你提供的目标情境', '',
                  f"所有目标同时代入：{goal['lee_score']}分，对应历史观察死亡率{goal['mortality_4y_pct']}%。",
                  '这不是改善后的个人风险预测；不把更低的模型输出自动解释为更好的健康状态。']
        for item in scenario['levers']:
            lines.append(f"- 仅改变{item['label_zh']}：{item['from']:g}→{item['to']:g}；"
                         f"得分变化{item['lee_score_delta']:+g}，表中死亡率变化{item['mortality_delta_pct']:+g}个百分点。")
    lines += ['', f'边界: {BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
