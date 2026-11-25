#!/usr/bin/env python3
"""Rescale the published log-linear diabetes association; no fitted constants."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    INCREMENT_MIN_WEEK, RR_PER_INCREMENT, CI_LOWER_PER_INCREMENT,
    CI_UPPER_PER_INCREMENT, INPUT_KEY, INPUT_UNIT, TITLE, BOUNDARY,
    STUDY_AGE_RANGE,
)


def contrast(delta_min_week: float) -> dict:
    """RR for higher/lower exposure relative to the comparison exposure.

    Exponentiate the same published slope and its confidence limits. A
    negative contrast reverses the order of confidence interval endpoints.
    These are coefficient uncertainty bounds, not individual prediction bands.
    """
    exponent = delta_min_week / INCREMENT_MIN_WEEK
    bounds = sorted((CI_LOWER_PER_INCREMENT ** exponent,
                     CI_UPPER_PER_INCREMENT ** exponent))
    return {'rr': RR_PER_INCREMENT ** exponent,
            'ci_lower': bounds[0], 'ci_upper': bounds[1]}


def levers(current: float, target: float | None) -> dict:
    now = contrast(current)
    out = {
        'schema': 'longevity-levers/1',
        'model': 'strength_training_diabetes_log_linear',
        'model_zh': TITLE,
        'current': {'strength_min_week': current, 'rr_vs_none': now['rr']},
        'sensitivity': [{
            'key': INPUT_KEY, 'label_zh': '每周力量训练时长', 'unit': INPUT_UNIT,
            'value': current,
            'rr_vs_none_per_unit': now['rr'] * math.log(RR_PER_INCREMENT) / INCREMENT_MIN_WEEK,
        }],
        'levers': [],
        'note_zh': BOUNDARY + ' 敏感度是固定线性模型中每周总时长增加一分钟时的局部导数；目标由用户提供。',
    }
    if target is not None:
        after = contrast(target)
        relative = contrast(target - current)
        out['levers'].append({
            'key': INPUT_KEY, 'label_zh': '每周力量训练时长', 'unit': INPUT_UNIT,
            'from': current, 'to': target,
            'rr_vs_none_delta': after['rr'] - now['rr'],
            'relative_to_current': relative,
        })
        out['targets'] = {
            'values': {INPUT_KEY: target}, 'rr_vs_none': after['rr'],
            'rr_vs_none_ci_lower': after['ci_lower'],
            'rr_vs_none_ci_upper': after['ci_upper'],
            'rr_vs_none_delta': after['rr'] - now['rr'],
            'relative_to_current': relative,
        }
    return out


def read_measurements(path, manifest):
    try:
        if path is not None:
            text = path.read_text(encoding='utf-8-sig')
            sample = text[:2048]
            delimiter = '\t' if sample.count('\t') > sample.count(',') else ','
            rows = [row for row in csv.reader(io.StringIO(text), delimiter=delimiter, strict=True) if row]
            if rows and any(len(row) != len(rows[0]) for row in rows[1:]):
                raise ValueError('表格数据行列数与表头不一致。')
        got = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error) as exc:
        return {}, [skillkit.Problem('file', '输入文件', 'file', f'无法读取输入文件：{exc}')]
    problems = list(got.problems)
    # Unknown target names must not silently turn a requested scenario into no-op.
    for name in got.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'未识别项目「{name}」，请使用每周力量训练时长。'))
    return got.values, problems


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex', help='可选背景信息：female、male、other、unknown；不进入公式。')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # An unsuccessful rerun must not leave old numeric results for a caller.
    for filename in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / filename).unlink(missing_ok=True)
    values, problems = read_measurements(args.measurements, manifest)
    age = None
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        problems.append(skillkit.Problem('age', '实足年龄', 'parse', '实足年龄必须是以岁为单位的数字。'))
    if args.sex not in (None, 'female', 'male', 'other', 'unknown'):
        problems.append(skillkit.Problem('sex', '性别', 'parse', '性别可写 female、male、other 或 unknown；也可省略。'))
    targets = {}
    if args.targets is not None:
        targets, target_problems = read_measurements(args.targets, manifest)
        for problem in target_problems:
            problem.message_zh = '目标文件：' + problem.message_zh
        problems += target_problems
    header = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report = skillkit.problems_markdown(problems, TITLE, BOUNDARY).split('\n', 2)[2]
        (args.out / 'report.md').write_text('\n'.join(header) + '\n' + report, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    current = values[INPUT_KEY]
    rr = contrast(current)
    outputs = {
        'rr_vs_none': rr['rr'], 'rr_vs_none_ci_lower': rr['ci_lower'],
        'rr_vs_none_ci_upper': rr['ci_upper'],
    }
    report = header + [
        '## 你的输入', '', f'每周力量训练总时长：{current:g} 分钟；年龄：{age:g} 岁。',
        '这里的时长是每周抗阻、力量或举重训练的总时间，不是有氧运动、搬运劳动、训练次数或强度。', '',
        '## 线性关联换算', '',
        f"相对每周零分钟，线性关联 RR：{rr['rr']:.4g}，换算的 95% CI：{rr['ci_lower']:.4g}–{rr['ci_upper']:.4g}。",
        'RR 是两种时长在论文线性模型下的相对比值，不是发病百分比；区间只传播论文斜率的不确定性。',
        '论文没有提供个人基线风险或统一预测年限，因此不计算绝对风险、预期寿命或患病人数。',
        '糖尿病证据确定性为低。自报时长、残余混杂和研究间差异限制了个体解释。',
        '论文也观察到 L 形关系；这里没有复现非线性曲线，较长时长的恒定斜率外推尤其不能当成额外收益。', '',
    ]
    if age < STUDY_AGE_RANGE[0] or age > STUDY_AGE_RANGE[1]:
        report += ['年龄在这项线性分析所含研究的年龄跨度之外，适用性更不确定。', '']
    target = targets.get(INPUT_KEY)
    if target is not None:
        change = contrast(target - current)
        outputs.update({
            'target_delta_min_week': target - current,
            'target_vs_current_rr': change['rr'],
            'target_vs_current_ci_lower': change['ci_lower'],
            'target_vs_current_ci_upper': change['ci_upper'],
        })
        report += [
            '## 你提供的目标情景', '',
            f'目标为每周 {target:g} 分钟，较当前相差 {target-current:g} 分钟。',
            f"目标相对当前的线性关联 RR：{change['rr']:.4g}，换算的 95% CI：{change['ci_lower']:.4g}–{change['ci_upper']:.4g}。",
            '这是用户设定时长之间的数学比较，不表示改变训练就会产生该幅度的风险变化。', '',
        ]
    report += [f'边界: {BOUNDARY}', '']
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(levers(current, target), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.out / 'report.md').write_text('\n'.join(report), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
