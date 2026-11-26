"""Offline, original-appendix PSQI scoring on uniquely defined inputs."""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, LATENCY_BANDS, PAIR_BANDS, DISTURBANCE_BANDS,
                     DURATION_BANDS, EFFICIENCY_BANDS, CUTOFF, MAX_SCORE,
                     COMPONENT_LABELS, CATEGORY_ZH, INTEGER_KEYS, DISTURBANCE_KEYS,
                     MINUTES_PER_HOUR, MINUTES_PER_DAY, PERCENT_FACTOR, STUDY_AGE_RANGE)

TITLE = 'PSQI 匹兹堡睡眠质量指数'


class SourceAmbiguity(ValueError):
    def __init__(self, key, message):
        self.key = key
        super().__init__(message)


def integer_lookup(value, bands):
    for low, high, score in bands:
        if low <= value and (high is None or value <= high):
            return score
    raise ValueError('不在印刷计分表覆盖范围内')


def latency_score(minutes):
    return integer_lookup(minutes, LATENCY_BANDS)


def pair_score(total):
    return integer_lookup(total, PAIR_BANDS)


def disturbance_score(total):
    return integer_lookup(total, DISTURBANCE_BANDS)


def strict_lookup(value, bands, key, message):
    matches = []
    for low, high, include_low, include_high, score in bands:
        above = value >= low if include_low else value > low
        below = high is None or (value <= high if include_high else value < high)
        if above and below:
            matches.append(score)
    if len(matches) != 1:
        raise SourceAmbiguity(key, message)
    return matches[0]


def duration_score(hours):
    return strict_lookup(hours, DURATION_BANDS, 'sleep_duration_h',
                         '原论文将 6 小时同时列入两个得分区间，不能唯一计分。这是来源歧义，请保留真实回答，由计分人员核对适用版本。')


def efficiency_score(percent):
    return strict_lookup(percent, EFFICIENCY_BANDS, 'sleep_duration_h',
                         '按上床、起床和实睡时长计算的效率落在原论文未覆盖区间 (74,75)% 或 (84,85]%。原文未提供舍入规则，不能唯一计分；请保留真实回答，由计分人员核对版本。')


def classify(total):
    return 'above_cutoff' if total > CUTOFF else 'not_above_cutoff'


def timing(values):
    # All clock inputs are validated integer minutes after midnight.
    minutes = (int(values['rise_time_min']) - int(values['bedtime_min'])) % MINUTES_PER_DAY
    hours = Decimal(minutes) / MINUTES_PER_HOUR
    sleep = Decimal(str(values['sleep_duration_h']))
    efficiency = sleep / hours * PERCENT_FACTOR if hours else None
    return hours, sleep, efficiency


def calculate(values):
    hours, sleep, efficiency = timing(values)
    components = [int(values['q6_code']),
                  pair_score(latency_score(values['sleep_latency_min']) + values['q5a_code']),
                  duration_score(sleep), efficiency_score(efficiency),
                  disturbance_score(sum(values[k] for k in DISTURBANCE_KEYS)),
                  int(values['q7_code']), pair_score(values['q8_code'] + values['q9_code'])]
    total = sum(components)
    return {**{f'component_{n}_score': score for n, score in enumerate(components, 1)},
            'psqi_global_score': total, 'sleep_quality_category': classify(total),
            'time_in_bed_h': float(hours), 'sleep_efficiency_pct': float(efficiency)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='可选年龄（岁），不进入计分')
    parser.add_argument('--sex', help='可选性别，不进入计分')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json'):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            'measurements', '问卷回答', 'file', f'无法读取回答表，请提供 marker,value,unit 格式的 CSV：{exc}')])
    problems = list(collected.problems)
    values = collected.values
    for key in INTEGER_KEYS:
        if key in values and not values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec['label_zh'], 'integer',
                            f"{spec['label_zh']}要求整数；请核对原始回答，不自动舍入。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, 'age', age))
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须为有限数值，单位为岁。'))
    if args.sex is not None and args.sex.casefold() not in {'male', 'female', 'other', 'unknown', '男', '女', '其他', '未知'}:
        problems.append(skillkit.Problem('sex', '性别', 'category', '性别请填男、女、其他或未知，也可不提供。'))
    outputs = None
    if not problems:
        hours, sleep, efficiency = timing(values)
        if hours == 0:
            problems.append(skillkit.Problem('rise_time_min', '起床时刻', 'inconsistent',
                            '上床和起床时刻相同，无法确定卧床时长；本方法不推断零小时或整天。'))
        elif sleep > hours:
            problems.append(skillkit.Problem('sleep_duration_h', '实际睡眠时长', 'inconsistent',
                            '实际睡眠时长超过上床至起床的时间，请核对原始回答。'))
        elif Decimal(str(values['sleep_latency_min'])) > hours * MINUTES_PER_HOUR:
            problems.append(skillkit.Problem('sleep_latency_min', '入睡潜伏期', 'inconsistent',
                            '入睡所需时间超过卧床时间，请核对原始回答。'))
        if not problems:
            try:
                outputs = calculate(values)
            except SourceAmbiguity as exc:
                spec = skillkit.spec_by_key(manifest, exc.key)
                problems.append(skillkit.Problem(exc.key, spec['label_zh'], 'source_ambiguity', str(exc)))
    heading = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 2)[2]
        path.write_text('\n'.join(heading) + '\n' + body, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    skillkit.write_result(args.out, manifest, outputs)
    report = heading + ['## 你的结果', '', '回顾期：过去一个月。分数越高，表示自评睡眠困难越多。', '',
                        f"**PSQI 总分：{outputs['psqi_global_score']} / {MAX_SCORE} 分。**",
                        CATEGORY_ZH[outputs['sleep_quality_category']] + '。', '',
                        '| 分量 | 得分（0–3） |', '|---|---:|']
    report.extend(f"| {label} | {outputs[f'component_{n}_score']} |" for n, label in enumerate(COMPONENT_LABELS, 1))
    report += ['', f"计算用卧床时长：{outputs['time_in_bed_h']:.6g} 小时；习惯性睡眠效率：{outputs['sleep_efficiency_pct']:.6g}%。",
               '', '总分只作睡眠质量筛查；助眠药分量是过去使用频度的记录，不能当作减少用药的目标。', '', BOUNDARY]
    if age is not None and not STUDY_AGE_RANGE[0] <= age <= STUDY_AGE_RANGE[1]:
        report += ['', '你的年龄超出原研究受试者的观察年龄范围，筛查表现不能直接外推。']
    (args.out / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
