#!/usr/bin/env python3
"""Offline translation of the CTT 2010 multiplicative LDL-C relation."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, INPUT_KEY, INPUT_UNIT, REDUCTION_RANGE,
                     RR_CI95, RR_PER_MMOL, TITLE)


def calculate(reduction):
    if not math.isfinite(reduction) or not REDUCTION_RANGE[0] <= reduction <= REDUCTION_RANGE[1]:
        raise ValueError('降幅必须在支持范围内')
    rr = RR_PER_MMOL ** reduction
    return {'ldl_reduction_mmol_l': reduction, 'major_vascular_rr': rr,
            'rr_ci95_lower': RR_CI95[0] ** reduction,
            'rr_ci95_upper': RR_CI95[1] ** reduction,
            'relative_reduction_pct': 100 * (1 - rr)}


def read_input(path, manifest, target=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, 'LDL-C 绝对降幅', 'file', f'无法读取输入文件：{exc}')]
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, 'LDL-C 绝对降幅', 'unmatched',
            f'无法识别「{name}」。这里需要 LDL-C 绝对降幅，不是单次 LDL-C 浓度或百分比。'))
    if target:
        problems = [skillkit.Problem(p.key, p.label, p.kind, '目标文件：' + p.message_zh) for p in problems]
    return collected.values, problems


def levers(reduction, target):
    current = calculate(reduction)
    output = {'schema': 'longevity-levers/1', 'model': 'ctt_2010_ldl_relative_rate',
        'model_zh': TITLE, 'current': current,
        'sensitivity': [{'key': INPUT_KEY, 'label_zh': 'LDL-C 绝对降幅', 'unit': INPUT_UNIT,
                         'value': reduction, 'rr_per_unit': current['major_vascular_rr'] * math.log(RR_PER_MMOL)}],
        'levers': [], 'note_zh': '目标是相对同一参照状态的总降幅，不是额外降低量；情景是数学换算，不表示该目标适合你或可以安全达到。' + BOUNDARY}
    if target is not None:
        projected = calculate(target)
        delta = projected['major_vascular_rr'] - current['major_vascular_rr']
        output['levers'] = [{'key': INPUT_KEY, 'label_zh': 'LDL-C 绝对降幅', 'unit': INPUT_UNIT,
                             'from': reduction, 'to': target, **projected, 'rr_delta': delta}]
        output['targets'] = {'values': {INPUT_KEY: target}, **projected, 'rr_delta': delta}
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json', 'levers.json', 'report.md'):
        (out / name).unlink(missing_ok=True)
    values, problems = read_input(args.measurements, manifest)
    target = None
    if args.targets is not None:
        target_values, target_problems = read_input(args.targets, manifest, target=True)
        problems.extend(target_problems)
        target = target_values.get(INPUT_KEY)
    header = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding='utf-8').split('\n', 2)[2]
        report.write_text('\n'.join(header) + '\n' + body, encoding='utf-8')
        skillkit.write_result(out, manifest, {item['key']: None for item in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    reduction = values[INPUT_KEY]
    result = calculate(reduction)
    scenarios = levers(reduction, target)
    body = ['## 你的结果', '',
        f"输入的 LDL-C 绝对降幅为 **{reduction:.3f} mmol/L**。",
        f"按论文关系换算的主要血管事件相对发生率为 **{result['major_vascular_rr']:.3f}**，相对降低 **{result['relative_reduction_pct']:.1f}%**。",
        f"由研究系数的 95% 置信区间换算：{result['rr_ci95_lower']:.3f}–{result['rr_ci95_upper']:.3f}。这不是个人预测区间，也未包含测量误差或人群差异。", '',
        '参照是没有这段 LDL-C 降幅的状态。结局为首次冠心病死亡、非致死性心肌梗死、冠状动脉血运重建或卒中组成的复合终点。', '',
        '原研究按随机分组约一年时的 LDL-C 组间差异标准化，观察期约五年。个人前后化验差值只用于情景换算，不能证明这段变化导致了你的风险改变；结果不是未来一年发病概率，也不按随访年数重复相乘。', '',
        '输入必须是同一单位下参照值减去比较值的绝对降幅，不是当前浓度，也不是降低百分比。目标文件沿用同一参照。', '',
        '这项关系来自成人他汀试验；不能直接外推到儿童、其他降脂手段或很低的终点 LDL-C。透析、心衰等情境的获益不能仅靠这个总体关系判断。未计算绝对风险、需要治疗人数或不良反应概率。']
    if reduction == 0:
        body += ['', '降幅为零时，相对发生率为参照值；这不表示你没有血管风险。']
    if target is not None:
        projected = scenarios['targets']
        body += ['', '## 目标情景', '',
                 f"若相对同一参照的总降幅为 {target:.3f} mmol/L，模型相对发生率为 {projected['major_vascular_rr']:.3f}，比当前模型值变化 {projected['rr_delta']:+.3f}。",
                 '这是情景计算，不是推荐目标或用药方案。']
    body += ['', f'边界: {BOUNDARY}', '']
    (out / 'report.md').write_text('\n'.join(header + body), encoding='utf-8')
    skillkit.write_result(out, manifest, result)
    (out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
