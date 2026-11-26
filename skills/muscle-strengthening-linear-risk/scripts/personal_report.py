#!/usr/bin/env python3
"""Rescale published per-increment RRs under the paper's linear log-risk model."""
import argparse
import csv
import io
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, INCREMENT_MIN, INPUT_KEY, MODEL_NOTE, OUTCOMES

TITLE = '力量训练时长：线性群体关联换算'


def linear_contrast(minutes_difference, outcome):
    """RR(delta) = RR(10)**(delta/10); reverse CI endpoints for negative delta."""
    rr, lo, hi = OUTCOMES[outcome][1]
    exponent = minutes_difference / INCREMENT_MIN
    limits = sorted((lo ** exponent, hi ** exponent))
    return rr ** exponent, limits[0], limits[1]


def output_values(minutes):
    values = {INPUT_KEY: minutes}
    for key in OUTCOMES:
        for suffix, value in zip(('rr', 'ci_low', 'ci_high'), linear_contrast(minutes, key)):
            values[f'{key}_linear_{suffix}'] = value
    return values


def levers(minutes, target):
    current = {key: linear_contrast(minutes, key)[0] for key in OUTCOMES}
    slopes = {key: current[key] * math.log(OUTCOMES[key][1][0]) / INCREMENT_MIN for key in OUTCOMES}
    data = {
        'schema': 'longevity-levers/1', 'model': 'muscle-strengthening-linear-risk',
        'model_zh': TITLE, 'current': current,
        'sensitivity': [{'key': INPUT_KEY, 'label_zh': '每周力量训练总时长', 'unit': 'min', 'value': minutes, 'rr_per_min': slopes}],
        'levers': [], 'note_zh': MODEL_NOTE + '敏感度是线性模型 RR 对每周总分钟数的导数，差值与比值均不是个人获益；不自动提出目标。',
    }
    if target is not None:
        wanted = {key: linear_contrast(target, key)[0] for key in OUTCOMES}
        delta = {key + '_rr_delta': wanted[key] - current[key] for key in OUTCOMES}
        # One shared estimated slope: use time difference directly, not independent CI division.
        contrast = {key: linear_contrast(target - minutes, key) for key in OUTCOMES}
        data['targets'] = {'values': {INPUT_KEY: target}, 'linear_rr': wanted, 'contrast': contrast, **delta}
        data['levers'] = [{'key': INPUT_KEY, 'label_zh': '每周力量训练总时长', 'unit': 'min', 'from': minutes, 'to': target, **delta}]
    return data


def collect(path, manifest):
    try:
        if path is not None:
            # Check row structure before skillkit reads values, aliases and units.
            source = path.read_text(encoding='utf-8-sig')
            delimiter = '\t' if source[:2048].count('\t') > source[:2048].count(',') else ','
            for row in csv.DictReader(io.StringIO(source), delimiter=delimiter, strict=True):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('数据行列数与表头不一致。')
        return skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(INPUT_KEY, '每周力量训练总时长', 'format', f'无法读取 CSV：{exc}')])


def table_lines(minutes):
    lines = ['| 结局 | 线性模型 RR | 线性模型 95% CI |', '|---|---:|---:|']
    for key, (label, _) in OUTCOMES.items():
        rr, lo, hi = linear_contrast(minutes, key)
        lines.append(f'| {label} | {rr:.4g} | {lo:.4g}–{hi:.4g} |')
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age', help='实足年龄，用于检查成年人适用范围，不进入公式')
    parser.add_argument('--sex', help='可选上下文，不进入公式')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    found = collect(args.measurements, manifest)
    problems = list(found.problems)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        age = None
        problems.append(skillkit.Problem('age', '实足年龄', 'parse', '年龄必须是可计算的有限数值（岁）。'))
    targets = collect(args.targets, manifest) if args.targets is not None else None
    if targets is not None:
        problems += [skillkit.Problem(p.key, p.label, p.kind, '目标文件：' + p.message_zh) for p in targets.problems]
    prefix = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 1)[1].replace('边界:', '边界：')
        path.write_text('\n'.join(prefix) + body, encoding='utf-8')
        skillkit.write_result(args.out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    minutes = found.values[INPUT_KEY]
    target = targets.values[INPUT_KEY] if targets is not None else None
    lines = prefix + ['## 你的输入', '', f'每周力量训练总时长：{minutes:g} 分钟；年龄：{age:g} 岁。', '',
        '这里记录一周的力量或抗阻训练、负重训练及自重训练总时长，不是单次时长、训练次数、有氧运动时长或负重家务时长。', '',
        '## 线性模型下的群体关联', '', MODEL_NOTE, '',
        '以下以每周零分钟为参照，把论文表 1 的每增加十分钟关联按线性模型换算到你的输入时长。RR 是群体相对风险，不是个人患病或死亡概率；95% CI 仅传播已印线性斜率的不确定性，不是个人预测区间，也不包含模型形状的不确定性。', '',
        *table_lines(minutes), '',
        '零时长的 RR 和区间均为参照定义的一，不代表没有风险。论文未给出该线性近似用于个人时长换算的可靠范围；输入排错上限仅是一周的总分钟数，不代表该范围得到验证。', '',
        '全因死亡、心血管疾病和总癌症的线性分析未显示明确关联。心血管与总癌症条目合并发病和死亡，不能解释成单一死亡概率，也不能把各条目相加。研究为观察性队列的汇总，以美国人群为主，采用自报或访谈活动量，存在残余混杂和异质性；证据确定性为低或很低。年龄仅检查成年人范围，性别不调整结果。']
    if target is not None:
        lines += ['', '## 你提供的目标情景', '', f'目标输入：每周 {target:g} 分钟，仅是你指定的比较值。以下以当前时长为参照。', '',
                  *table_lines(target - minutes), '', '目标相对当前的 RR 及置信区间使用同一线性斜率和时长差换算；不将两次计算当作独立研究。目标结果、RR 差值与敏感度另存于 levers.json，不能据此推断改变训练会带来多少收益。']
    lines += ['', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, output_values(minutes))
    (args.out / 'levers.json').write_text(json.dumps(levers(minutes, target), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
