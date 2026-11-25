#!/usr/bin/env python3
"""Adult personal exposure lookup; no interpolation, extrapolation or joint risk."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, EXPOSURES, NOTE, OUTCOMES, TABLES, THRESHOLDS, TITLE


def lookup(exposure, outcome, hours):
    rows = TABLES[exposure][outcome]
    result = {'status': 'missing', 'reference_hours': rows[0]['hours'],
              'rr': None, 'lci': None, 'uci': None}
    for side in ('lower', 'upper'):
        for field in ('hours', 'rr', 'lci', 'uci'):
            result[side + '_' + field] = None
    if hours is None:
        return result
    # Tolerance only absorbs floating-point unit conversion, not dose rounding.
    for row in rows:
        if math.isclose(hours, row['hours'], rel_tol=0, abs_tol=1e-10):
            result.update(status='exact', **{s: row[s] for s in ('rr', 'lci', 'uci')})
            return result
    if hours < rows[0]['hours'] or hours > rows[-1]['hours']:
        result['status'] = 'outside'
        return result
    result['status'] = 'between'
    lower = max((r for r in rows if r['hours'] < hours), key=lambda r: r['hours'])
    upper = min((r for r in rows if r['hours'] > hours), key=lambda r: r['hours'])
    for side, row in [('lower', lower), ('upper', upper)]:
        result.update({side + '_' + s: row[s] for s in ('hours', 'rr', 'lci', 'uci')})
    return result


def evaluate(values):
    outputs = {}
    for exposure in EXPOSURES:
        hours = values.get(exposure + '_hours_day')
        outputs[exposure + '_hours_day'] = hours
        for outcome in OUTCOMES:
            prefix = f'{exposure}_{outcome}'
            outputs.update({prefix + '_' + k: v for k, v in lookup(exposure, outcome, hours).items()})
            if (exposure, outcome) in THRESHOLDS:
                cutoff, below, above = THRESHOLDS[exposure, outcome]
                outputs[prefix + '_threshold_hours'] = cutoff
                outputs[prefix + '_band'] = None if hours is None else ('above' if hours > cutoff else 'at_or_below')
                gradient = (None, None, None) if hours is None else (above if hours > cutoff else below)
                for suffix, number in zip(('rr', 'lci', 'uci'), gradient):
                    outputs[prefix + '_per_hour_' + suffix] = number
    return outputs


def levers(values, targets):
    current = evaluate(values)
    result = {'schema': 'longevity-levers/1', 'model': 'sedentary-dose-response',
              'model_zh': '久坐与看电视的印刷风险表', 'current': current,
              'sensitivity': [], 'levers': [], 'note_zh': NOTE,
              'sensitivity_note_zh': '敏感度仅为相邻印刷点之间的RR差/小时差（割线），不是原样条局部导数，不用于内插或个人收益预测。表外不可计算；原表点两侧分别列示。'}
    for key, x in values.items():
        exposure = key.removesuffix('_hours_day')
        item = {'key': key, 'label_zh': EXPOSURES[exposure] + '时间', 'unit': 'h',
                'value': x, 'outcomes': {}}
        for outcome, rows in TABLES[exposure].items():
            prefix = exposure + '_' + outcome
            status = current[prefix + '_status']
            segments = []
            if status in ('exact', 'between'):
                for a, b in zip(rows, rows[1:]):
                    if a['hours'] - 1e-10 <= x <= b['hours'] + 1e-10:
                        segments.append({'from_hours': a['hours'], 'to_hours': b['hours'],
                                         'from_rr': a['rr'], 'to_rr': b['rr'],
                                         'rr_difference_per_hour': (b['rr'] - a['rr']) / (b['hours'] - a['hours'])})
            item['outcomes'][outcome] = {'status': status, 'segments': segments}
        result['sensitivity'].append(item)
    for key, target in targets.items():
        changed = evaluate(dict(values, **{key: target}))
        deltas = {k: (None if current[k] is None or changed[k] is None else changed[k] - current[k])
                  for k in current if k.endswith('_rr') and '_per_hour_' not in k and '_lower_' not in k and '_upper_' not in k}
        result['levers'].append({'key': key, 'unit': 'h', 'from': values[key], 'to': target,
                                 'outputs': changed, 'rr_delta': deltas})
    if targets:
        result['targets'] = {'values': targets, 'outputs': evaluate(dict(values, **targets))}
    return result


def consistency(values):
    if values.get('tv_hours_day', 0) > values.get('sitting_hours_day', 24):
        return [skillkit.Problem('tv_hours_day', '看电视时间', 'inconsistent',
                                '坐着看电视已包含在总久坐中，看电视时长不能超过总久坐；请核对两项是否都是平均每天的时长。')]
    return []


def collect(path, manifest, target=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, AttributeError) as exc:
        return {}, [skillkit.Problem('file', '目标文件' if target else '测量文件', 'file',
                                    f'无法读取表格：{exc}。请提供marker,value,unit格式的CSV或TSV。')]
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem('marker', '指标名称', 'unknown', f'无法识别指标「{name}」；本技能只读取总久坐和看电视的每日时长。'))
    if not collected.values and not problems:
        problems.append(skillkit.Problem('exposure', '目标时长' if target else '每日时长', 'missing',
                                        '请至少提供总久坐或看电视的一项平均每日时长及单位h或min。'))
    return collected.values, problems


def result_lines(outputs, heading):
    lines = [heading, '']
    for exposure, name in EXPOSURES.items():
        x = outputs[exposure + '_hours_day']
        if x is None:
            lines += [f'{name}：未提供，不计算这一暴露。', '']
            continue
        lines += [f'**{name}：{x:g} 小时/日**', '',
                  '| 结局 | 原表参照（小时/日） | 查表结果：RR（95%CI） |',
                  '|---|---:|---|']
        for outcome, label in OUTCOMES.items():
            p = f'{exposure}_{outcome}'
            status = outputs[p + '_status']
            if status == 'exact':
                value = f"{outputs[p+'_rr']:.2f}（{outputs[p+'_lci']:.2f}–{outputs[p+'_uci']:.2f}）"
            elif status == 'between':
                points = []
                for side in ('lower', 'upper'):
                    q = p + '_' + side
                    points.append(f"{outputs[q+'_hours']:g}小时：{outputs[q+'_rr']:.2f}（{outputs[q+'_lci']:.2f}–{outputs[q+'_uci']:.2f}）")
                value = '未印出该时长；相邻原表行：' + '；'.join(points)
            else:
                rows = TABLES[exposure][outcome]
                value = f"超出原表{rows[0]['hours']:g}–{rows[-1]['hours']:g}小时范围，不外推"
            lines.append(f"| {label} | {outputs[p+'_reference_hours']:g} | {value} |")
        lines += ['', '分段位置（附表5；不是安全界限）：', '']
        for outcome in ('all_cause', 'cvd'):
            p = exposure + '_' + outcome
            band = '高于' if outputs[p + '_band'] == 'above' else '不高于'
            lines.append(f"- {OUTCOMES[outcome]}：{band}{outputs[p+'_threshold_hours']:g}小时/日；该段每增加1小时的平均RR为{outputs[p+'_per_hour_rr']:.2f}（95%CI {outputs[p+'_per_hour_lci']:.2f}–{outputs[p+'_per_hour_uci']:.2f}）。")
        lines += ['']
    return lines


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='年龄（岁），仅检查成人适用范围')
    parser.add_argument('--sex', help='可选上下文，不进入模型')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json', 'levers.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄需要是以岁为单位的有限数值。'))
    problems += consistency(values)
    targets = {}
    if args.targets is not None:
        targets, issues = collect(args.targets, manifest, target=True)
        problems += issues
        for key in targets:
            if key not in values:
                problems.append(skillkit.Problem(key, '目标时长', 'missing_baseline', '目标对应的当前时长未提供，无法比较，请先提供当前测量。'))
            else:
                problems += consistency(dict(values, **{key: targets[key]}))
        problems += consistency(dict(values, **targets))
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report = args.out / 'report.md'
        body = report.read_text().split('\n', 1)[1]
        report.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]) + '\n', encoding='utf-8')
        raise SystemExit(skillkit.EXIT_INPUT_PROBLEM)
    outputs = evaluate(values)
    changes = levers(values, targets)
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', f'边界：{BOUNDARY}', '',
             '## 如何读这份报告', '',
             'RR是相对原表参照时长的人群风险比；置信区间描述研究估计的不确定性，不是你的个人风险区间。'
             'RR为1不代表没有风险。不同结局的参照时长不同，不能横向比较RR大小。', '',
             '只返回原表点；两点之间只列相邻印刷行，它们不是该时长的风险上下界。'
             '体力活动已在原研究中统计调整，但本表不能根据你的运动量进一步校正。', '',
             '癌症死亡不等于癌症发病，心血管死亡不等于新发心血管疾病；总久坐与癌症死亡的关联在正文中未达统计显著。', '',
             '适用背景为成人一般人群的前瞻性观察研究，主要依赖自报时长；不作为已确诊疾病人群的专用预后模型。', '',
             *result_lines(outputs, '## 当前时长对应结果')]
    if targets:
        lines += result_lines(changes['targets']['outputs'], '## 目标时长对应结果')
        lines += ['## 每项目标单独改变时的表值差', '']
        for item in changes['levers']:
            exposure = item['key'].removesuffix('_hours_day')
            lines += [f"{EXPOSURES[exposure]}从{item['from']:g}到{item['to']:g}小时/日：", '']
            for outcome, label in OUTCOMES.items():
                delta = item['rr_delta'][exposure + '_' + outcome + '_rr']
                lines.append(f'- {label}：' + ('至少一个时长未命中原表，不计算RR差。' if delta is None else f'原表RR差 {delta:+.2f}（目标减当前）。'))
            lines.append('')
    lines += [NOTE, '', '敏感度文件中的相邻点割线只概括表值变化，不是原样条导数；不据此内插未印出的风险。', '', f'边界：{BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(args.out / 'report.md')


if __name__ == '__main__':
    main()
