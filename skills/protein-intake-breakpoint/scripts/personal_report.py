#!/usr/bin/env python3
"""Offline comparison with a published study-arm breakpoint, never a gain model."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BREAKPOINT, BREAKPOINT_CI, MODEL_P, OBSERVED_INTAKE, BOUNDARY, SCENARIO_NOTE


def calculate(values, eligible):
    relative = values['protein_g_day'] / values['weight_kg']
    result = dict(protein_g_kg_day=relative, breakpoint_difference=None, position=None,
                  scope='未确认研究适用情境')
    if not eligible:
        return result
    if not OBSERVED_INTAKE[0] <= relative <= OBSERVED_INTAKE[1]:
        result['scope'] = '超出论文拐点分析摄入范围'
        return result
    result['scope'] = '可作研究拐点位置比较'
    # Exact comparison to the printed value; no invented clinical tolerance.
    result['position'] = ('低于研究拐点' if relative < BREAKPOINT else
                          '高于研究拐点' if relative > BREAKPOINT else
                          '等于研究拐点（按印出精度）')
    result['breakpoint_difference'] = relative - BREAKPOINT
    return result


def levers(values, targets, eligible):
    current = calculate(values, eligible)
    p, w = values['protein_g_day'], values['weight_kg']
    result = {
        'schema': 'longevity-levers/1', 'model': 'protein-intake-breakpoint',
        'model_zh': '总蛋白相对摄入量与研究拐点的位置', 'current': current,
        'sensitivity': [
            {'key': 'protein_g_day', 'unit': 'g/d', 'value': p, 'output': 'protein_g_kg_day', 'output_units_per_input_unit': 1 / w},
            {'key': 'weight_kg', 'unit': 'kg', 'value': w, 'output': 'protein_g_kg_day', 'output_units_per_input_unit': -p / w**2},
        ], 'levers': [], 'note_zh': SCENARIO_NOTE,
    }
    for key, target in targets.items():
        moved = calculate({**values, key: target}, eligible)
        result['levers'].append({'key': key, 'from': values[key], 'to': target,
                                 'outputs': moved, 'protein_g_kg_day_delta': moved['protein_g_kg_day'] - current['protein_g_kg_day']})
    if targets:
        moved = calculate({**values, **targets}, eligible)
        result['targets'] = {'values': targets, 'outputs': moved,
                             'protein_g_kg_day_delta': moved['protein_g_kg_day'] - current['protein_g_kg_day']}
    return result


def collect(path, manifest, partial=False):
    specs = copy.deepcopy(manifest)
    if partial:
        for spec in specs['inputs']:
            spec['required'] = False
    try:
        collected = skillkit.collect_file(path, specs)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {}, [skillkit.Problem('file', '测量文件', 'file', f'无法读取表格：{exc}')]
    problems = list(collected.problems)
    if partial:
        if collected.unmatched:
            problems.append(skillkit.Problem('targets', '情景表', 'unknown', '情景表包含未识别项目：' + '、'.join(collected.unmatched)))
        if not collected.values and not problems:
            problems.append(skillkit.Problem('targets', '情景表', 'missing', '情景表没有体重或每日总蛋白质记录。'))
    return collected.values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='实足年龄（岁），用于成人适用性判断，不校正拐点')
    parser.add_argument('--sex', help='可选上下文；不参与计算')
    parser.add_argument('--context', help='healthy-ret / other / unknown；见 SKILL.md')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    age = None
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        problems.append(skillkit.Problem('age', '实足年龄', 'parse', '实足年龄必须是以岁为单位的数值。'))
    if args.context not in ('healthy-ret', 'other', 'unknown'):
        problems.append(skillkit.Problem('context', '研究情境', 'missing' if args.context is None else 'parse',
            '请确认情境：healthy-ret 表示健康、无能量限制且抗阻训练持续至少六周、每周至少两次；不符合填 other，不清楚填 unknown。'))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems += target_problems
    heading = ['# 蛋白质摄入与研究拐点', '', *paper_card_lines(), '']
    if problems:
        path = skillkit.write_problems(args.out, problems, '输入未通过检查', BOUNDARY)
        path.write_text('\n'.join(heading) + '\n' + path.read_text(), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {o['key']: None for o in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    eligible = age >= 18 and args.context == 'healthy-ret'
    outputs = calculate(values, eligible)
    scenario = levers(values, targets, eligible)
    lines = heading + [
        '## 你的记录', '',
        f"记录的每日总蛋白质：{values['protein_g_day']:g} g/d（食物与补充来源合计）。",
        f"记录的体重：{values['weight_kg']:g} kg。",
        f"总摄入量除以体重：{outputs['protein_g_kg_day']:.3f} g/kg/day。",
        f"适用性：{outputs['scope']}。", '',
        '## 与研究的关系', '',
        f'论文组水平拐点为 {BREAKPOINT:g} g/kg/day，95% 置信区间为 {BREAKPOINT_CI[0]:g}–{BREAKPOINT_CI[1]:.2f} g/kg/day。',
        f'分段模型与线性模型的比较 p={MODEL_P:g}，未达到论文预设的统计显著性水平；第二段斜率为零是建模约束。',
        '置信区间描述研究拐点的不确定性，不是个人需要量范围，也不作为分档界限。',
    ]
    if outputs['position'] is not None:
        lines += [f"位置：{outputs['position']}；当前相对摄入量减研究拐点为 {outputs['breakpoint_difference']:+.3f} g/kg/day。",
                  '低于不等于蛋白缺乏，高于不证明个人已经达到增肌平台。']
    else:
        lines += [f'仅报告摄入量的算术换算，不作拐点分档。该分析中的摄入范围为 {OBSERVED_INTAKE[0]:g}–{OBSERVED_INTAKE[1]:g} g/kg/day。']
    if targets:
        moved = scenario['targets']
        lines += ['', '## 用户提供的情景', '',
                  f"情景中的相对摄入量：{moved['outputs']['protein_g_kg_day']:.3f} g/kg/day；与当前相差 {moved['protein_g_kg_day_delta']:+.3f} g/kg/day。",
                  f"情景适用性：{moved['outputs']['scope']}；位置：{moved['outputs']['position'] or '不分档'}。", SCENARIO_NOTE]
    lines += ['', '验证状态：暂定。已核对正文及九份附件中的常数，但论文未印出可复现的个人体重与总摄入量计算示例。',
              '研究未提供经过个人验证的增肌预测模型；不使用年龄或训练经验的组水平回归系数校正个人结果。',
              '', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
