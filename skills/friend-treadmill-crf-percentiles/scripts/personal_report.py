#!/usr/bin/env python3
"""Classify measured maximal treadmill CPX VO2max against printed FRIEND points."""
import argparse
import csv
import io
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGE_RANGE, BOUNDARY, FRIEND, PERCENTILES, TITLE, VO2_UNIT


def reference_row(age, sex):
    if not math.isfinite(age) or int(age) != age or not AGE_RANGE[0] <= age <= AGE_RANGE[1]:
        raise ValueError('需要 20–79 整周岁年龄。')
    if sex not in FRIEND:
        raise ValueError('需要论文中的 male 或 female 分层。')
    return dict(zip(PERCENTILES, FRIEND[sex][int(age) // 10 * 10]))


def lookup(age, sex, vo2):
    row = reference_row(age, sex)
    if not math.isfinite(vo2):
        raise ValueError('VO2max must be finite')
    lower, upper = None, None
    for percentile, threshold in row.items():
        if vo2 == threshold:
            lower = upper = percentile
            break
        if vo2 > threshold:
            lower = percentile
        else:
            upper = percentile
            break
    if lower == upper:
        band = f'P{lower}'
    elif lower is None:
        band = f'<P{upper}'
    elif upper is None:
        band = f'>P{lower}'
    else:
        band = f'P{lower}–P{upper}'
    decade = int(age) // 10 * 10
    return {
        'age_group': f'{decade}–{decade + 9}',
        'measured_vo2max_ml_kg_min': vo2,
        'percentile_band': band,
        'percentile_lower': lower,
        'percentile_upper': upper,
        'reference_median_ml_kg_min': row[50],
    }


def problem(key, label, message, kind='context'):
    return skillkit.Problem(key, label, kind, message)


def check_table_shape(path):
    """Reject unlabelled extra fields before skillkit maps names and units."""
    if path is None:
        return
    text = path.read_text(encoding='utf-8-sig')
    sample = text[:2048]
    delimiter = '\t' if sample.count('\t') > sample.count(',') else ','
    rows = [row for row in csv.reader(io.StringIO(text), delimiter=delimiter, strict=True) if row]
    if rows and any(len(row) != len(rows[0]) for row in rows[1:]):
        raise ValueError('测量表的数据列数与表头不一致，请核对分隔符及多余列。')


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--test-type')
    parser.add_argument('--cvd')
    parser.add_argument('--copd')
    parser.add_argument('--early-stop')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ('result.json', 'problems.json', 'report.md'):
        (args.out / filename).unlink(missing_ok=True)
    try:
        check_table_shape(args.measurements)
        collected = skillkit.collect_file(args.measurements, manifest)
        problems = list(collected.problems)
    except (OSError, ValueError, csv.Error) as exc:
        collected = skillkit.Collected()
        problems = [problem('measurements', '测量表', f'无法读取测量表：{exc}', 'file')]
    age = None
    try:
        if args.age is not None:
            age = skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, 'age', age)
        if age is not None and age != int(age):
            problems.append(problem('age', '年龄', '请填写测试时的整周岁年龄，不四舍五入跨入下一个年龄段。'))
    except (ValueError, OverflowError):
        problems.append(problem('age', '年龄', '年龄应为测试时的整周岁数字。', 'parse'))
    sex = {'male': 'male', 'm': 'male', '男': 'male',
           'female': 'female', 'f': 'female', '女': 'female'}.get((args.sex or '').strip().lower())
    if sex is None:
        problems.append(problem('sex', '性别分层', '缺少或无法识别性别分层；论文仅提供 male（男）和 female（女）。'))
    contexts = [
        ('test_type', args.test_type, 'maximal_treadmill_cpx', '测试类型',
         '需要确认最大跑台 CPX 且以呼吸气体实测摄氧量；--test-type maximal_treadmill_cpx。手表、负荷估算、自行车或次最大试验不适用。'),
        ('cvd', args.cvd, 'no', '已知心血管病',
         '需明确无已知心血管病（冠心病、外周动脉病、心力衰竭）：--cvd no；有病史或未知时不套用此参考。'),
        ('copd', args.copd, 'no', '慢性阻塞性肺疾病',
         '需明确无 COPD：--copd no；有病史或未知时不套用此参考。'),
        ('early_stop', args.early_stop, 'no', '因异常提前终止',
         '需确认未在达到自愿最大努力前因异常临床发现终止：--early-stop no。'),
    ]
    for key, value, expected, label, message in contexts:
        if value != expected:
            problems.append(problem(key, label, message, 'missing' if value is None else 'context'))
    if problems:
        report_path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = report_path.read_text(encoding='utf-8').split('\n', 1)[1]
        report_path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = lookup(age, sex, collected.values['vo2max_ml_kg_min'])
    row = reference_row(age, sex)
    band = result['percentile_band']
    sex_zh = '男性' if sex == 'male' else '女性'
    if result['percentile_lower'] == result['percentile_upper']:
        interpretation = f'与论文印出的 {band} 阈值相同。'
    elif result['percentile_lower'] is None:
        interpretation = '低于论文印出的 P5 阈值，无法给出更精细的尾部百分位。'
    elif result['percentile_upper'] is None:
        interpretation = '高于论文印出的 P95 阈值，无法给出更精细的尾部百分位。'
    else:
        interpretation = f'位于论文印出的 {band} 两个阈值之间。'
    report = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
              f"测试时年龄：{age:g} 岁；参照组：{result['age_group']} 岁{sex_zh}。",
              f"实测最大摄氧量：{result['measured_vo2max_ml_kg_min']:g} {VO2_UNIT}；峰值 RER：{collected.values['peak_rer']:g}。",
              f'参考位置：**{band}**。{interpretation}',
              f"本组中位数（P50）：{result['reference_median_ml_kg_min']:g} {VO2_UNIT}。", '',
              '## 本组参考阈值', '', '| 百分位 | 摄氧量（mL/kg/min） |', '| --- | ---: |',
              *[f'| P{p} | {v:.1f} |' for p, v in row.items()], '',
              '百分位表只印出七个点，阈值保留一位小数；相等表示匹配印出的阈值，不能理解为未经舍入的精确人群排名。区间内不插值，尾部不外推。', '',
              '该参考来自美国多中心资料，并非中国人群标准；原研究也不完全代表全美国。年龄段之间的横断面差异不能用来预测你今后的下降速度。', '',
              f'边界: {BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
