#!/usr/bin/env python3
"""Offline nearest-grid lookup of author-released non-occupational PA curves."""
from __future__ import annotations

import argparse
from bisect import bisect_left
import csv
from functools import lru_cache
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, DATA, HIGH_ACTIVITY, INTENSITIES, MAX_WEEK_MINUTES,
                     MINUTES_PER_HOUR, OUTCOMES, SPARSE_ACTIVITY, TITLE)


@lru_cache(maxsize=None)
def curve(key):
    with (DATA / OUTCOMES[key][1]).open(encoding='utf-8') as stream:
        return tuple({k: float(v) for k, v in row.items()} for row in csv.DictReader(stream))


def lookup(key, exposure):
    """Author server.R::get_ma_table: nearest dose; first (lower) row on a tie.

    Unlike nearest-neighbour clamping, refuse values outside the released curve.
    No interpolation, fitted coefficients, or extrapolation is introduced.
    """
    rows = curve(key)
    if not math.isfinite(exposure) or not rows[0]['dose'] <= exposure <= rows[-1]['dose']:
        return None
    return min(rows, key=lambda row: abs(row['dose'] - exposure))


def activity_volume(values):
    return sum(values[key] * intensity / MINUTES_PER_HOUR for key, intensity in INTENSITIES.items())


def calculate(values):
    exposure = activity_volume(values)
    result = {'activity_mmet_h_week': exposure}
    for key in OUTCOMES:
        row = lookup(key, exposure)
        for suffix, column in [('rr', 'RR'), ('ci_lower', 'lb'), ('ci_upper', 'ub'),
                               ('matched_mmet_h_week', 'dose')]:
            result[key + '_' + suffix] = row[column] if row is not None else None
    return result


def volume_problems(values, prefix=''):
    problems = []
    if not all(key in values for key in INTENSITIES):
        return problems  # Required-field problems are supplied by skillkit.
    if sum(values[key] for key in INTENSITIES) > MAX_WEEK_MINUTES:
        problems.append(skillkit.Problem('activity', prefix + '活动时长', 'range',
                                        prefix + '三个互不重叠的活动时长合计超过一周全部分钟数；请核对是否重复计时或填了日均值。'))
    exposure = activity_volume(values)
    maximum = max(curve(key)[-1]['dose'] for key in OUTCOMES)
    if exposure > maximum:
        problems.append(skillkit.Problem('activity', prefix + '活动量', 'range',
                                        f'{prefix}活动量超出所有已发布曲线的范围（最大 {maximum:g} mMET-hours/week），无法查询；不会截断或外推。'))
    return problems


def collect(path, manifest, targets=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as error:
        return {}, [skillkit.Problem('file', '目标表' if targets else '活动表', 'file',
                                    f'无法读取表格：{error}。需要 marker,value,unit 三列表。')]
    problems = [p for p in collected.problems if not (targets and p.kind == 'missing')]
    if collected.unmatched:
        problems.append(skillkit.Problem('file', '活动项目', 'unknown',
                                        '无法识别项目：' + '、'.join(collected.unmatched) + '。请填写三种非职业活动的每周累计时长。'))
    if targets and not collected.values and not problems:
        problems.append(skillkit.Problem('targets', '目标表', 'missing', '目标表没有可识别的活动时长，不能作为目标运行。'))
    return collected.values, problems


def levers(values, targets):
    current = calculate(values)
    exposure = current['activity_mmet_h_week']
    slopes, brackets = {}, {}
    for outcome in OUTCOMES:
        rows = curve(outcome)
        if lookup(outcome, exposure) is None:
            slopes[outcome] = None
            continue
        i = max(1, min(bisect_left([row['dose'] for row in rows], exposure), len(rows) - 1))
        left, right = rows[i - 1], rows[i]
        slopes[outcome] = (right['RR'] - left['RR']) / (right['dose'] - left['dose'])
        brackets[outcome] = [left['dose'], right['dose']]
    manifest = skillkit.load_manifest(__file__)
    labels = {s['key']: s['label_zh'] for s in manifest['inputs']}
    result = {
        'schema': 'longevity-levers/1', 'model': 'nonoccupational_activity_relative_risk',
        'model_zh': TITLE, 'current': current, 'sensitivity': [], 'levers': [],
        'note_zh': '目标比较是同一人群关联曲线上的位置比较，不是个体因果获益。敏感度是相邻发布网格点的割线斜率，不是阶梯查询函数的导数；小目标变化可能仍查到同一行。RR差没有置信区间，不能把两组CI端点相减当成差值CI。',
    }
    for key, intensity in INTENSITIES.items():
        result['sensitivity'].append({
            'key': key, 'label_zh': labels[key], 'unit': 'min', 'value': values[key],
            'method': 'adjacent_grid_secant', 'brackets_mmet_h_week': brackets,
            'rr_per_unit': {k: None if slope is None else slope * intensity / MINUTES_PER_HOUR
                            for k, slope in slopes.items()},
        })
    def comparison(moved):
        output = calculate(moved)
        delta = {key: None if output[key + '_rr'] is None or current[key + '_rr'] is None
                 else output[key + '_rr'] - current[key + '_rr'] for key in OUTCOMES}
        return output, delta
    for key, target in targets.items():
        output, delta = comparison(dict(values, **{key: target}))
        result['levers'].append({'key': key, 'label_zh': labels[key], 'unit': 'min',
                                 'from': values[key], 'to': target, 'outputs': output, 'rr_delta': delta})
    if targets:
        combined = dict(values, **targets)
        output, delta = comparison(combined)
        result['targets'] = {'values': targets, 'combined_values': combined, 'outputs': output, 'rr_delta': delta}
    return result


def render(values, age, result, changes):
    exposure = result['activity_mmet_h_week']
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 本次活动量', '',
             f'年龄 {age:g} 岁，仅用于核对成年人适用范围。以下为通常一周内、互不重叠的非职业活动时长：', '']
    manifest = skillkit.load_manifest(__file__)
    for spec in skillkit.input_specs(manifest):
        lines.append(f"- {spec['label_zh']}：{values[spec['key']]:g} 分钟。")
    lines += ['', f'按论文的强度假设换算：**{exposure:g} mMET-hours/week**。mMET扣除了静息能量消耗；这里不包含工作活动。',
              '这项换算使用固定的强度代表值，并非实际能耗测量。手环全天活动量、步数和含静息或职业活动的MET总量不能直接替代这些输入。']
    if exposure > HIGH_ACTIVITY:
        lines += ['', '该活动量位于论文较高的活动区间，额外风险差较小且不确定。']
    if exposure > SPARSE_ACTIVITY:
        lines += ['该活动量还超过论文绝大多数观察人年的范围，高活动量证据尤其稀少。']
    lines += ['', '## 对应研究人群的相对风险', '',
              '参照均为零非职业活动量；RR为0.69表示研究人群的相对风险约为参照的69%，不是个人有69%的概率患病或死亡。',
              '置信区间表示研究估计的不确定性，不是你的风险范围。疾病“发生”合并致死和非致死事件；性别限定结局只对应表中注明的研究人群，其他结局使用总人群主分析，未作个人年龄或性别校准。', '',
              '| 结局 | RR（95%置信区间） | 查询网格活动量（mMET-hours/week） |', '|---|---|---|']
    for key, (label, _) in OUTCOMES.items():
        rr, lb, ub, dose = (result[key + '_' + suffix] for suffix in ('rr', 'ci_lower', 'ci_upper', 'matched_mmet_h_week'))
        if rr is None:
            lines.append(f'| {label} | 未计算：超过该曲线发布范围 | — |')
        else:
            lines.append(f'| {label} | {rr:.2f}（{lb:.2f}–{ub:.2f}） | {dose:.4f} |')
    lines += ['', '采用作者的最近网格点查询，因此实际查询活动量可能与输入略有差别。区间跨过1的结果不能表述为明确降低或升高风险。各结局有重叠，不能相加。']
    if 'targets' in changes:
        target = changes['targets']
        lines += ['', '## 你提供的目标情景', '',
                  f"目标合并后活动量：{target['outputs']['activity_mmet_h_week']:g} mMET-hours/week。未填写的活动项保持当前值。", '',
                  '| 结局 | 当前RR | 目标情景RR | RR差（目标−当前） |', '|---|---|---|---|']
        for key, (label, _) in OUTCOMES.items():
            old, new, delta = result[key + '_rr'], target['outputs'][key + '_rr'], target['rr_delta'][key]
            def fmt(v):
                return '未计算' if v is None else f'{v:.3f}'
            lines.append(f'| {label} | {fmt(old)} | {fmt(new)} | {fmt(delta)} |')
        if target['outputs']['activity_mmet_h_week'] > HIGH_ACTIVITY:
            lines += ['', '目标位于较高活动区间，额外风险差更不确定；超过某个结局发布范围时该结局留空。']
        lines += ['', changes['note_zh']]
    lines += ['', '适用范围是一般成年人；研究排除了面向住院/机构人群、二三级预防患者或特定高风险人群的队列。结果不能用于这些人群的个体评估。',
              '', f'边界: {BOUNDARY}']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except ValueError:
        problems.append(skillkit.Problem('age', '实足年龄', 'parse', '年龄必须是以岁为单位的有限数值。'))
    else:
        problems += skillkit.check_scalar(manifest, 'age', age)
    problems += volume_problems(values)
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, targets=True)
        problems += [skillkit.Problem(p.key, p.label, p.kind, '目标表：' + p.message_zh) for p in target_problems]
        if not problems:
            problems += volume_problems(dict(values, **targets), '目标合并后')
            for key, value in targets.items():
                problems += volume_problems(dict(values, **{key: value}), '单项目标情景')
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        content = path.read_text(encoding='utf-8').splitlines()
        path.write_text('\n'.join([content[0], '', *paper_card_lines(), '', *content[2:]]) + '\n', encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    changes = levers(values, targets)
    (args.out / 'report.md').write_text(render(values, age, result, changes), encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'levers.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
