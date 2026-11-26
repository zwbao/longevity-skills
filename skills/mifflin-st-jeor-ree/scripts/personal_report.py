"""Manifest-driven, standard-library implementation of the printed MSJE."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COEFFICIENTS, STUDY_RANGES, TARGET_NOTE, TITLE


def calculate(values, age, sex):
    inputs = dict(values, age=age, sex=int(sex == 'male'))
    return {key: c['intercept'] + sum(c[k] * inputs[k] for k in ('weight_kg', 'height_cm', 'age', 'sex'))
            for key, c in COEFFICIENTS.items()}


def population_warnings(values, age, sex):
    inputs = dict(values, age=age)
    labels = {'weight_kg': '体重（kg）', 'height_cm': '身高（cm）', 'age': '年龄（岁）'}
    return [f'{labels[key]}超出原研究该性别的观测范围（{low:g}–{high:g}）；本次属于外推，准确性未获该研究验证。'
            for key, (low, high) in STUDY_RANGES[sex].items() if not low <= inputs[key] <= high]


def problem(key, kind, message, manifest):
    spec = next((s for s in manifest['inputs'] if s['key'] == key), {})
    return skillkit.Problem(key, spec.get('label_zh', key), kind, message)


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError) as exc:
        return {}, [problem('measurements', 'file', f'无法读取输入表：{exc}', manifest)]
    issues = [p for p in data.problems if not (partial and p.kind == 'missing')]
    issues += [problem(k, 'unknown', f'无法识别项目：{k}。', manifest) for k in data.unmatched]
    if partial:
        issues += [problem(k, 'target', '只接受体重目标；年龄、身高和性别保持当前资料。', manifest)
                   for k in data.values if k != 'weight_kg']
        if not data.values and not issues:
            issues.append(problem('targets', 'missing', '目标表需要一项带单位的体重。', manifest))
    return data.values, issues


def levers(values, age, sex, targets, manifest):
    current = calculate(values, age, sex)
    inputs = dict(values, age=age, sex=sex)
    sensitivity = []
    for spec in manifest['inputs']:
        key = spec['key']
        item = {'key': key, 'label_zh': spec['label_zh'], 'unit': spec.get('unit', ''),
                'value': inputs[key], 'modifiable': key == 'weight_kg'}
        if key == 'sex':
            item.update({'method': 'fixed_profile_contrast', 'contrast': 'female_to_male',
                         'delta': {output: c['sex'] for output, c in COEFFICIENTS.items()},
                         'note_zh': '论文性别编码对应的固定差值，不是可改变目标。'})
        else:
            item.update({'method': 'analytic_derivative',
                         'derivatives': {output: c[key] for output, c in COEFFICIENTS.items()},
                         'note_zh': '其他输入不变，每增加一个输入单位对应的kcal/d变化；不是因果效应。'})
        sensitivity.append(item)
    result = {'schema': 'longevity-levers/1', 'model': manifest['name'], 'model_zh': TITLE,
              'current': current, 'sensitivity': sensitivity, 'levers': [], 'note_zh': TARGET_NOTE + BOUNDARY}
    for key, target in targets.items():
        moved_values = dict(values, **{key: target})
        moved = calculate(moved_values, age, sex)
        delta = {output: moved[output] - current[output] for output in current}
        result['levers'].append({'key': key, 'label_zh': '体重', 'unit': 'kg',
                                 'from': values[key], 'to': target, 'outputs': moved, 'delta': delta})
        result['targets'] = {'values': targets, 'outputs': moved, 'delta': delta,
                             'warnings_zh': population_warnings(moved_values, age, sex)}
    return result


def fail(out, issues):
    path = skillkit.write_problems(out, issues, TITLE, BOUNDARY)
    heading, rest = path.read_text(encoding='utf-8').split('\n', 1)
    path.write_text(heading + '\n\n' + '\n'.join(paper_card_lines()) + '\n' + rest, encoding='utf-8')
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='年龄，19–78岁，可为小数年')
    parser.add_argument('--sex', help='male/男 或 female/女')
    parser.add_argument('--targets', type=Path, help='可选，仅体重目标，marker,value,unit')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'levers.json', 'problems.json'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, issues = collect(args.measurements, manifest)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except ValueError:
        issues.append(problem('age', 'parse', '年龄需要有限的数值，单位为年。', manifest))
    issues.extend(skillkit.check_scalar(manifest, 'age', age))
    sex_text = (args.sex or '').strip().lower()
    sex = {'男': 'male', '女': 'female'}.get(sex_text, sex_text)
    if sex not in STUDY_RANGES:
        issues.append(problem('sex', 'category', '请提供male（男）或female（女），不能猜测方程使用的性别系数。', manifest))
    targets = {}
    if args.targets is not None:
        targets, target_issues = collect(args.targets, manifest, partial=True)
        issues.extend(target_issues)
    if issues:
        return fail(args.out, issues)
    outputs = calculate(values, age, sex)
    scenarios = levers(values, age, sex, targets, manifest)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f"静息能量消耗（原式）：**{outputs['ree_original_kcal_d']:.1f} kcal/d**。",
             f"静息能量消耗（简化式）：**{outputs['ree_simplified_kcal_d']:.1f} kcal/d**。", '',
             '这是静息状态下的能量消耗估计，尚未包括活动和食物热效应，不能直接作为每天应该吃多少的答案。',
             '两个结果来自原文系数的舍入差异；这不是两次独立测量，也不是置信区间。', '',
             f"本次输入：体重{values['weight_kg']:g} kg，身高{values['height_cm']:g} cm，年龄{age:g}岁，"
             f"方程性别{'男' if sex == 'male' else '女'}。", '',
             '原研究对象为健康成人；患病、妊娠、哺乳、极端体重或与原研究不同的人群不能据此获得已验证的能量需求。']
    lines += population_warnings(values, age, sex)
    if targets:
        lines += ['', '## 你提供的体重情景', '', TARGET_NOTE]
        for item in scenarios['levers']:
            lines += [f"体重从{item['from']:g} kg改为{item['to']:g} kg：",
                      f"原式估计{item['outputs']['ree_original_kcal_d']:.1f} kcal/d，变化{item['delta']['ree_original_kcal_d']:+.1f} kcal/d；"
                      f"简化式估计{item['outputs']['ree_simplified_kcal_d']:.1f} kcal/d，变化{item['delta']['ree_simplified_kcal_d']:+.1f} kcal/d。"]
        lines += scenarios['targets']['warnings_zh']
    lines += ['', f'边界：{BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
