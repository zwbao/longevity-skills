"""Offline exact lookup; the primary and post-hoc tables are never rebased."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, CERTAINTY, INPUT_KEY, OUTCOMES, TABLES, TABLE_LABELS, TITLE


def lookup(steps, reference=2000):
    result = {INPUT_KEY: steps, 'reference_steps_per_day': reference,
              'source_table': 'table_2' if reference == 2000 else 'supplementary_table_8_corrected'}
    for key, cell in TABLES[reference][steps].items():
        for suffix, value in zip(('hr', 'ci_lower', 'ci_upper'), cell):
            result[f'{key}_{suffix}'] = value
    return result


def collect(path, manifest, label, reference):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, label, 'file', f'{label}文件无法读取：{exc}')]
    problems = list(data.problems)
    if data.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, label, 'unknown', f'{label}含无法识别的项目：{"、".join(data.unmatched)}。'))
    steps = data.values.get(INPUT_KEY)
    if steps is not None and reference in TABLES and steps not in TABLES[reference]:
        problems.append(skillkit.Problem(INPUT_KEY, label, 'unsupported',
            f'{label}为 {steps:g} 步/日；所选表只印出 {reference} 至 12000 步/日、每1000步一个点。'
            '没有该输入的精确值，不取整、不插值、不外推。请保留真实测量；本查表方法无法计算这个步数。'))
    if label.startswith('目标'):
        for problem in problems:
            problem.message_zh = '目标文件：' + problem.message_zh
    return data.values, problems


def hr_delta(current, other):
    return {f'{key}_hr': round(other[f'{key}_hr'] - current[f'{key}_hr'], 10) for key in OUTCOMES}


def levers(steps, reference, target=None):
    current = lookup(steps, reference)
    neighbors = []
    for neighbor in (steps - 1000, steps + 1000):
        if neighbor in TABLES[reference]:
            other = lookup(neighbor, reference)
            neighbors.append({INPUT_KEY: neighbor, 'outputs': other, 'hr_delta': hr_delta(current, other)})
    result = {
        'schema': 'longevity-levers/1', 'model': 'daily-steps-health-lookup',
        'model_zh': TABLE_LABELS[reference], 'current': current,
        'sensitivity': [{'key': INPUT_KEY, 'unit': '1', 'value': steps,
                         'method': 'adjacent_printed_points', 'neighbors': neighbors}],
        'levers': [],
        'note_zh': '敏感度仅为同一张表相邻已印出点的HR差，没有连续导数。目标比较不表示个人风险下降或运动建议；不计算差值置信区间，不跨表比较或换算参照。',
    }
    if target is not None:
        other = lookup(target, reference)
        delta = hr_delta(current, other)
        result['targets'] = {'values': {INPUT_KEY: target}, 'outputs': other, 'hr_delta': delta}
        result['levers'] = [{'key': INPUT_KEY, 'label_zh': '日均步数', 'unit': '1',
                             'from': steps, 'to': target, 'outputs': other, 'hr_delta': delta}]
    return result


def risk_table(result):
    reference = result['reference_steps_per_day']
    lines = [f'| 研究结局 | HR（相对每日{reference}步） | 研究人群95%置信区间 | 证据确定性 |',
             '|---|---:|---|---|']
    for key, label in OUTCOMES.items():
        hr, low, high = (result[f'{key}_{s}'] for s in ('hr', 'ci_lower', 'ci_upper'))
        ci = '参照点，未印区间' if low is None else f'{low:.2f}–{high:.2f}'
        lines.append(f'| {label} | {hr:.2f} | {ci} | {CERTAINTY[key]} |')
    return lines


def render(result, reference, target=None):
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的查表结果', '',
             f'设备记录的日均步数：{result[INPUT_KEY]:g} 步/日。数值来自{TABLE_LABELS[reference]}。', '',
             *risk_table(result), '',
             'HR是研究人群中的相对危险率，不是发病百分比；置信区间描述研究估计的不确定性，不是你的个人预测区间。参照值1不代表没有风险。', '',
             '研究纳入成人，主要分析汇总一般人群；跌倒研究均为老年人。没有按你的年龄、性别、疾病或设备佩戴位置校准。主要证据来自高收入国家、研究级设备的数日测量，单日偶然记录或消费级手环长期均值并不具有完全相同的测量口径。', '',
             '表中确定性来自正文表3对各结局整体证据的评价，不是你个人的置信度。身体功能未做荟萃分析，没有可查HR。']
    if reference == 7000:
        lines += ['', '补表8为事后分析。2025年8月27日更正后的表注明其模型与主要分析相似，但基线危险率不同，两表结果不能直接比较；不能用正文表2的HR相除代替补表8。', '',
                  '补表8的心血管疾病死亡等单元格与正文概述方向并不完全一致。这里保留表格原值，不改写为“步数越多风险一定越低”，也不据此选择最佳步数。']
    if target is not None:
        lines += ['', '## 你指定的目标情景', '',
                  f'目标日均步数为 {target:g} 步/日；仍查询同一张表。这是你指定的情景，不是建议达到的步数。', '',
                  *risk_table(lookup(target, reference)), '',
                  '目标与当前点的HR差只表示两个人群关联查表值的差，不是改变步数后的因果效应。']
    lines += ['', f'边界: {BOUNDARY}']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--reference-steps', default='2000', help='2000（正文表2）或7000（更正后补表8）')
    parser.add_argument('--age', help='可选成人年龄，不调整查表值')
    parser.add_argument('--sex', help='可选male/female，不调整查表值')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('problems.json', 'result.json', 'levers.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    reference = {'2000': 2000, '7000': 7000}.get(args.reference_steps)
    values, problems = collect(args.measurements, manifest, '日均步数', reference)
    if reference is None:
        problems.append(skillkit.Problem('reference_steps_per_day', '论文参照步数', 'unsupported',
                                         '参照参数只接受2000或7000，分别选择正文表2或补表8。'))
    target = None
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, '目标日均步数', reference)
        problems += target_problems
        target = targets.get(INPUT_KEY)
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems += skillkit.check_scalar(manifest, 'age', age)
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须是有限数值。'))
    if args.sex is not None and args.sex not in ('male', 'female'):
        problems.append(skillkit.Problem('sex', '性别', 'parse', '性别参数只接受male或female，也可以省略。'))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 1)[1]
        path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    steps = values[INPUT_KEY]
    result = lookup(steps, reference)
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'report.md').write_text(render(result, reference, target), encoding='utf-8')
    (args.out / 'levers.json').write_text(json.dumps(levers(steps, reference, target), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
