"""Convert a recorded total-nut intake contrast using the printed linear slope."""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path

import paper_card
import skillkit
from presets import BOUNDARY, INCREMENT_G_D, RR, RR_LOWER, RR_UPPER


def contrast(difference):
    exponent = difference / INCREMENT_G_D
    rr = RR ** exponent
    lower, upper = sorted((RR_LOWER ** exponent, RR_UPPER ** exponent))
    return {'intake_difference_g_d': difference, 'linear_rr': rr,
            'linear_rr_lower': lower, 'linear_rr_upper': upper,
            'relative_difference_pct': 100 * (rr - 1)}


def compute(values):
    return contrast(values['nut_intake_g_d'] - values['reference_intake_g_d'])


def levers(values, targets, manifest):
    current = compute(values)
    specs = {s['key']: s for s in manifest['inputs']}
    payload = {'schema': 'longevity-levers/1', 'model': manifest['name'],
               'model_zh': '总坚果摄入差的全因死亡线性关联', 'current': current,
               'sensitivity': [], 'levers': [],
               'note_zh': '仅描述线性公式对输入的敏感度。目标完全由使用者提供，不代表推荐摄入量或因果收益；比较基准变化只是改变分母。'}
    for key, sign in [('nut_intake_g_d', 1), ('reference_intake_g_d', -1)]:
        payload['sensitivity'].append({'key': key, 'label_zh': specs[key]['label_zh'],
            'unit': 'g/d', 'value': values[key],
            'rr_per_unit': sign * current['linear_rr'] * math.log(RR) / INCREMENT_G_D})
        if key in targets:
            moved = compute({**values, key: targets[key]})
            payload['levers'].append({'key': key, 'label_zh': specs[key]['label_zh'],
                'unit': 'g/d', 'from': values[key], 'to': targets[key],
                'linear_rr': moved['linear_rr'], 'linear_rr_delta': moved['linear_rr'] - current['linear_rr']})
    if targets:
        moved = compute({**values, **targets})
        payload['targets'] = {'values': targets, **moved,
            'linear_rr_delta': moved['linear_rr'] - current['linear_rr']}
    return payload


def collect(path, manifest, partial=False):
    spec = copy.deepcopy(manifest)
    if partial:
        for item in spec['inputs']:
            item['required'] = False
    try:
        result = skillkit.collect_file(path, spec)
    except (OSError, UnicodeError, ValueError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem('', '输入文件', 'file', f'无法读取输入文件：{exc}')])
    for name in result.unmatched:
        result.problems.append(skillkit.Problem(name, name, 'unknown', f'未识别的摄入指标：{name}。请使用总坚果摄入量或比较基准摄入量。'))
    if partial and not result.values and not result.problems:
        result.problems.append(skillkit.Problem('', '目标', 'missing', '目标文件没有可计算的摄入量。'))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for filename in ('problems.json', 'levers.json', 'result.json', 'report.md'):
        (out / filename).unlink(missing_ok=True)
    collected = collect(args.measurements, manifest)
    problems = collected.problems
    if args.age is not None:
        try:
            problems += skillkit.check_scalar(manifest, 'age', float(args.age))
        except ValueError:
            problems.append(skillkit.Problem('age', '实足年龄', 'parse', '实足年龄必须是有限数值。'))
    target = collect(args.targets, manifest, partial=True) if args.targets else skillkit.Collected()
    problems += target.problems
    card = '\n'.join(paper_card.lines()) + '\n\n'
    if problems:
        report = skillkit.write_problems(out, problems, '坚果摄入差关联', BOUNDARY)
        report.write_text(card + report.read_text(encoding='utf-8'), encoding='utf-8')
        skillkit.write_result(out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    result = compute(collected.values)
    skillkit.write_result(out, manifest, result)
    payload = levers(collected.values, target.values, manifest)
    (out / 'levers.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    x, ref = collected.values['nut_intake_g_d'], collected.values['reference_intake_g_d']
    text = card + f'''## 摄入记录的线性关联对照

你的记录为 {x:g} g/d，明确提供的比较基准为 {ref:g} g/d，两者相差 {x-ref:+g} g/d。

把这个差放入研究的线性模型，得到全因死亡关联 RR **{result['linear_rr']:.3f}**，95% 区间 {result['linear_rr_lower']:.3f}–{result['linear_rr_upper']:.3f}；相对差为 {result['relative_difference_pct']:+.2f}%。这里的百分比不是绝对死亡概率差，也不是你改变饮食后的预期收益。

论文同时报告了非线性关系；线性换算把斜率视为固定，无法表达曲线趋平，因此不能把数字理解为摄入越多收益越大。区间只换算已发表斜率的不确定性，不包括个人差异、饮食记录误差或残余混杂。年龄和性别不改变计算。

边界: {BOUNDARY}
'''
    if target.values:
        text += f"\n你提供的情景对应线性 RR {payload['targets']['linear_rr']:.3f}，相对当前模型值变化 {payload['targets']['linear_rr_delta']:+.3f}。这是公式情景比较，不是摄入建议。\n"
    (out / 'report.md').write_text(text, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
