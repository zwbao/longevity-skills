#!/usr/bin/env python3
"""Exact lookup of printed Burden of Proof red-meat estimates; standard library only."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, GRID, INPUT_KEY, INPUT_UNIT, LABELS, STARS, TABLE

TITLE = '未加工红肉摄入量与慢病相对风险查表'
REFERENCE_NOTE = ('参照说明：下列数值保留补充表7的原始标度。正文将结直肠癌等结局与零摄入比较，'
                  '但缺血性卒中在0克/日时表值为1.03，在25克/日时为1.00，'
                  '所以不能把该结局解释为相对零摄入；也不能推定25克就是精确最低风险点。'
                  '本报告不重新归一化这些数值。')
LEVER_NOTE = ('仅比较同一论文已印出的摄入点，差值是相对风险表值之差，不是患病概率变化或因果效应。'
              '表格没有连续导数或两点差值的不确定区间，因此不计算这些量。目标值由用户提供，不是推荐摄入量。')


def lookup(intake, sex):
    if intake not in GRID:
        raise ValueError('Only printed intake points are supported')
    values = {'intake_g_d': intake}
    for key in LABELS:
        triple = TABLE[key][intake] if key != 'breast_cancer' or sex == 'female' else (None, None, None)
        for suffix, number in zip(('_rr', '_ui_lower', '_ui_upper'), triple):
            values[key + suffix] = number
    return values


def difference(after, before):
    return {key: round(after[key] - before[key], 10) for key in after
            if key.endswith('_rr') and after[key] is not None and before[key] is not None}


def levers(intake, target, sex):
    current = lookup(intake, sex)
    index = GRID.index(intake)
    neighbors = [GRID[i] for i in (index - 1, index + 1) if 0 <= i < len(GRID)]
    data = {
        'schema': 'longevity-levers/1', 'model': 'red-meat-burden-of-proof',
        'model_zh': '未加工红肉证据负担查表（2022）', 'current': current,
        'sensitivity': [{'key': INPUT_KEY, 'label_zh': '未加工红肉摄入量', 'unit': INPUT_UNIT,
                         'value': intake, 'derivative': None,
                         'method': 'adjacent_printed_rows',
                         'adjacent_table_rows': [{'intake_g_d': n, 'outputs': lookup(n, sex),
                                                  'delta': difference(lookup(n, sex), current)} for n in neighbors]}],
        'levers': [], 'note_zh': LEVER_NOTE,
    }
    if target is not None:
        after = lookup(target, sex)
        delta = difference(after, current)
        data['targets'] = {'values': {INPUT_KEY: target}, 'outputs': after, 'delta': delta}
        data['levers'] = [{'key': INPUT_KEY, 'label_zh': '未加工红肉摄入量', 'unit': INPUT_UNIT,
                           'from': intake, 'to': target, 'outputs': after, 'delta': delta}]
    return data


def read_intake(path, manifest, label):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, AttributeError) as exc:
        return None, [skillkit.Problem(INPUT_KEY, label, 'file', f'{label}文件无法读取：{exc}')]
    problems = list(collected.problems)
    if collected.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, label, 'unmatched', f'{label}存在无法识别的项目：' + '、'.join(collected.unmatched)))
    value = collected.values.get(INPUT_KEY)
    if value is not None and value not in GRID:
        problems.append(skillkit.Problem(INPUT_KEY, label, 'unsupported_grid',
                         f'{label}为{value:g} g/d；此查表仅支持' + '、'.join(map(str, GRID)) +
                         ' g/d。请保留真实摄入量，不要为使用本工具而取整；论文未提供该摄入点，本次无法查询。'))
    return value, problems


def table_lines(values):
    lines = ['| 结局 | 相对风险表值 | 保守95%不确定区间 | 论文关联证据 |',
             '|---|---:|---|---|']
    for key, label in LABELS.items():
        value = values[key + '_rr']
        if value is None:
            continue
        interval = f"{values[key + '_ui_lower']:.2f}–{values[key + '_ui_upper']:.2f}"
        strength = '2星：较弱' if STARS[key] == 2 else '1星：证据不足'
        lines.append(f'| {label} | {value:.2f} | {interval} | {strength} |')
    return lines


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    intake, problems = read_intake(args.measurements, manifest, '当前摄入量')
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems.extend(skillkit.check_scalar(manifest, 'age', age))
    except ValueError:
        problems.append(skillkit.Problem('age', '实足年龄', 'number', '实足年龄需要有限数值，单位为岁。'))
    if args.sex not in ('female', 'male', 'unknown'):
        problems.append(skillkit.Problem('sex', '性别', 'missing' if args.sex is None else 'category',
                         '请提供性别female、male或unknown，用于判断乳腺癌结果的适用性。'))
    target = None
    if args.targets is not None:
        target, target_problems = read_intake(args.targets, manifest, '目标摄入量')
        problems.extend(target_problems)
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report = args.out / 'report.md'
        original = report.read_text(encoding='utf-8')
        report.write_text(original.replace(f'# {TITLE}\n', f'# {TITLE}\n\n' + '\n'.join(paper_card_lines()) + '\n', 1), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values = lookup(intake, args.sex)
    comparison = levers(intake, target, args.sex)
    skillkit.write_result(args.out, manifest, values)
    (args.out / 'levers.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的摄入量', '',
             f'日均未加工红肉摄入量：{intake:g} 克/日；查询补充表7同一摄入点。', '',
             '未加工红肉包括未加工牛、羊、猪肉，不含香肠、培根等加工肉；输入应是习惯性日均摄入量，不能用一顿或一天代替。', '',
             f'年龄{age:g}岁仅用于核对研究适用人群；本表没有按年龄、地区或性别校准个人风险。', '',
             REFERENCE_NOTE, '', *table_lines(values), '',
             '不确定区间包含研究间异质性；星级是整段暴露范围的证据强度，不是你个人的风险等级。'
             '区间跨过1表示与无关联相容；卒中证据不足，不应解释成红肉已被证实有害或有保护作用。', '']
    if args.sex != 'female':
        lines += ['乳腺癌结果仅适用于女性；本次性别为male或unknown，因此未返回该项数值。', '']
    if target is not None:
        lines += ['## 你指定的摄入点比较', '', f'目标摄入量：{target:g} 克/日。', '',
                  LEVER_NOTE, '', *table_lines(comparison['targets']['outputs']), '',
                  '| 结局 | 目标表值减当前表值 |', '|---|---:|']
        for key, delta in comparison['targets']['delta'].items():
            lines.append(f'| {LABELS[key[:-3]]} | {delta:+.2f} |')
        lines += ['']
    lines += ['连续摄入曲线和连续敏感度未计算；相邻已印出摄入点及其表值差见levers.json。', '', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
