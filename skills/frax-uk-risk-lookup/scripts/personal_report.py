"""Strict offline lookup, not an implementation of the continuous FRAX model."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGES, BMI, BOUNDARY, FACTORS, OUTPUTS, TABLE_2, TARGET_KEYS, TITLE


def problem(key, message, kind='unsupported'):
    return skillkit.Problem(key, FACTORS.get(key, key), kind, message)


def domain_problems(values):
    errors = []
    if 'bmi_kg_m2' in values and values['bmi_kg_m2'] != BMI:
        errors.append(problem('bmi_kg_m2', '表2仅适用于BMI恰为25 kg/m²；保留真实测量，不取整、不插值。'))
    for key in (*FACTORS, 'secondary_osteoporosis'):
        if key in values and values[key] not in (0, 1):
            errors.append(problem(key, f'{key}只能填0（否）或1（是），未知不能填0。'))
    if values.get('secondary_osteoporosis', 0) != 0:
        errors.append(problem('secondary_osteoporosis', '表2没有其他继发性骨质疏松的单列；完整FRAX计算器会套用类风湿关节炎系数，但本查表技能不作替代映射，请使用完整计算器。'))
    if sum(values.get(key, 0) == 1 for key in FACTORS) > 1:
        errors.append(problem('risk_factors', '表2只支持无危险因素或一个危险因素；多因素没有对应单元格。'))
    return errors


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [problem('measurements', f'文件无法读取：{exc}', 'file')]
    errors = [p for p in data.problems if not (partial and p.kind == 'missing')]
    if data.unmatched:
        errors.append(problem('measurements', '无法识别的输入：' + '、'.join(data.unmatched), 'unknown'))
    if partial and not data.values:
        errors.append(problem('targets', '目标文件为空或没有可用目标。', 'missing'))
    return data.values, errors


def lookup(age, sex, values):
    factor = next((key for key in FACTORS if values[key] == 1), 'none')
    row = TABLE_2[sex][factor]
    i = AGES.index(age)
    return dict(zip(OUTPUTS, (row[i], row[i + len(AGES)])))


def delta(current, other):
    return {key: round(other[key] - current[key], 10) for key in OUTPUTS}


def levers(age, sex, values, targets, manifest):
    current = lookup(age, sex, values)
    data = {'schema': 'longevity-levers/1', 'model': manifest['name'],
            'model_zh': TITLE, 'current': current, 'sensitivity': [], 'levers': [],
            'note_zh': '仅比较表2已印出的分类点；差值单位为百分点，无连续导数，不是戒烟或减少饮酒后的风险降低预测。年龄、性别、BMI与病史不作为目标。'}
    for spec in manifest['inputs']:
        key = spec['key']
        item = {'key': key, 'label_zh': spec['label_zh'], 'unit': spec.get('unit'),
                'value': age if key == 'age' else sex if key == 'sex' else values[key],
                'method': 'not_estimable', 'neighbors': []}
        if key in TARGET_KEYS:
            other_values = {**values, key: 1 - values[key]}
            if not domain_problems(other_values):
                other = lookup(age, sex, other_values)
                item.update(method='printed_category_difference', neighbors=[
                    {'value': other_values[key], 'outputs': other, 'delta_percentage_points': delta(current, other)}])
            else:
                item['reason_zh'] = '切换此分类会形成多危险因素，超出表2。'
        else:
            item['reason_zh'] = '固定查表条件或病史；不估算可改变敏感度。'
        data['sensitivity'].append(item)
    if targets:
        other = lookup(age, sex, {**values, **targets})
        data['targets'] = {'values': targets, 'outputs': other, 'delta_percentage_points': delta(current, other)}
        for key, value in targets.items():
            one = {**values, key: value}
            valid = not domain_problems(one)
            result = lookup(age, sex, one) if valid else None
            data['levers'].append({'key': key, 'from': values[key], 'to': value, 'unit': '1',
                                   'outputs': result, 'delta_percentage_points': delta(current, result) if valid else None,
                                   'note_zh': '单独切换该分类的表格差。' if valid else '单独切换会形成多危险因素，表2未印出。'})
    return data


def render(age, sex, values, result, scenario):
    factor = next((FACTORS[k] for k in FACTORS if values[k] == 1), '无表列危险因素')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的查表结果', '',
             f'年龄：{age:g}岁；论文性别分组：{"男性" if sex == "male" else "女性"}；BMI：25 kg/m²；分类：{factor}。', '',
             '| 结局 | 十年概率（英国模型表值） |', '|---|---:|']
    lines += [f'| {label} | {result[key]:g}% |' for key, label in OUTPUTS.items()]
    lines += ['', '主要骨质疏松性骨折包含临床脊柱、髋部、肱骨和前臂骨折；髋部骨折已包含在前一项中，两项不能相加。',
              '结果来自2008年英国流行病学校准、未加入骨密度的模型；表2没有置信区间，数值保留原表精度。没有按你所在地区或当前年代重新校准。',
              '其他年龄、BMI、多个危险因素及骨密度输入均超出此查表。不能据此判定是否骨质疏松或是否需要治疗。']
    if 'targets' in scenario:
        lines += ['', '## 你指定的分类情景', '', '以下仅比较已印出的分类，差异不代表改变行为后能够实现的获益。']
        for key, value in scenario['targets']['values'].items():
            lines.append(f'- {FACTORS[key]}：{values[key]:g} → {value:g}（0=否，1=是）。')
        for key, label in OUTPUTS.items():
            lines.append(f'- {label}：{scenario["targets"]["outputs"][key]:g}%；与当前相差{scenario["targets"]["delta_percentage_points"][key]:+g}个百分点。')
    return '\n'.join([*lines, '', f'边界: {BOUNDARY}', ''])


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    values, errors = collect(args.measurements, manifest)
    errors += domain_problems(values)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        errors += skillkit.check_scalar(manifest, 'age', age)
        if age is not None and age not in AGES:
            errors.append(problem('age', '年龄必须恰为50、60、70或80岁，不插值、不四舍五入。'))
    except ValueError:
        errors.append(problem('age', '年龄必须是有限数字。', 'parse'))
    if args.sex not in ('male', 'female'):
        errors.append(problem('sex', '请提供论文性别分组male或female。', 'missing' if args.sex is None else 'parse'))
    targets = {}
    if args.targets is not None:
        targets, target_errors = collect(args.targets, manifest, partial=True)
        for key in targets:
            if key not in TARGET_KEYS:
                target_errors.append(problem(key, '目标仅支持目前吸烟和高酒精摄入分类，不能把病史或用药设置成目标。'))
        target_errors += domain_problems({**values, **targets})
        for p in target_errors:
            p.message_zh = '目标文件：' + p.message_zh
        errors += target_errors
    if errors:
        report = skillkit.write_problems(args.out, errors, TITLE, BOUNDARY)
        body = report.read_text().split('\n', 1)[1]
        report.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {key: None for key in OUTPUTS})
        return skillkit.EXIT_INPUT_PROBLEM
    result = lookup(age, args.sex, values)
    scenario = levers(age, args.sex, values, targets, manifest)
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'report.md').write_text(render(age, args.sex, values, result, scenario), encoding='utf-8')
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
