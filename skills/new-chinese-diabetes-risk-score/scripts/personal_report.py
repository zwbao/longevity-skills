#!/usr/bin/env python3
"""Offline New Chinese Diabetes Risk Score; standard library only."""
from __future__ import annotations

import argparse
import csv
from bisect import bisect_right
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_BINS, BMI_BINS, WAIST_BINS, SBP_BINS, BINARY_POINTS,
                     CUTOFF, DERIVATION_RANGES, INPUT_RANGES, MODIFIABLE,
                     BOUNDARY, LEVER_NOTE)

TITLE = '新中国糖尿病风险评分'


def bins_for(key, sex='female'):
    return {'age': AGE_BINS, 'bmi_kg_m2': BMI_BINS, 'waist_cm': WAIST_BINS[sex],
            'sbp_mmhg': SBP_BINS}[key]


def points(key, value, sex='female'):
    if key in BINARY_POINTS:
        return BINARY_POINTS[key][value]
    bins = bins_for(key, sex)
    index = bisect_right([lower for lower, _ in bins], value) - 1
    if index < 0:
        raise ValueError('Age below the published range')
    return bins[index][1]


def category(total):
    return '达到筛查阈值' if total >= CUTOFF else '低于筛查阈值'


def compute(values, sex):
    terms = {key + '_points': points(key, values[key], sex)
             for key in ('age', 'waist_cm', 'bmi_kg_m2', 'sbp_mmhg', 'family_history')}
    terms['sex_points'] = points('sex', int(sex == 'male'))
    total = sum(terms.values())
    return {**terms, 'total_score': total, 'screening_category': category(total)}


def warnings(values):
    specs = {s['key']: s for s in skillkit.load_manifest(__file__)['inputs']}
    return [f"{specs[key]['label_zh']}={values[key]:g} {specs[key]['unit']} 超出推导样本保留范围 {low:g}–{high:g}；分数属于外推。"
            for key, (low, high) in DERIVATION_RANGES.items() if not low <= values[key] <= high]


def levers(values, sex, targets, manifest):
    current = compute(values, sex)
    specs = {s['key']: s for s in manifest['inputs']}
    sensitivity = []
    numeric = {**values, 'sex': int(sex == 'male')}
    for key in ('age', 'sex', 'family_history', *MODIFIABLE):
        x = numeric[key]
        low, high = INPUT_RANGES[key]
        to = 1 - x if key in BINARY_POINTS else (x + 1 if x + 1 <= high else x - 1)
        moved = dict(values)
        moved_sex = sex
        if key == 'sex':
            moved_sex = 'male' if to else 'female'
        else:
            moved[key] = to
        score = compute(moved, moved_sex)['total_score']
        item = {'key': key, 'label_zh': specs[key]['label_zh'], 'unit': specs[key]['unit'],
                'value': x, 'to': to, 'step': to - x, 'score_delta': score - current['total_score'],
                'not_a_target': key not in MODIFIABLE, 'method': 'finite_change'}
        if key in MODIFIABLE:
            bins = bins_for(key, sex)
            index = bisect_right([b for b, _ in bins], x) - 1
            if index:
                item['lower_band'] = {'below_exclusive': bins[index][0],
                                      'score_delta': bins[index - 1][1] - bins[index][1]}
            if index + 1 < len(bins):
                item['higher_band'] = {'at_or_above': bins[index + 1][0],
                                       'score_delta': bins[index + 1][1] - bins[index][1]}
        sensitivity.append(item)
    out = {'schema': 'longevity-levers/1', 'model': manifest['name'], 'model_zh': TITLE,
           'current': current, 'sensitivity': sensitivity, 'levers': [],
           'note_zh': LEVER_NOTE, 'warnings_zh': warnings(values)}
    for key, target in targets.items():
        moved = compute(dict(values, **{key: target}), sex)
        out['levers'].append({'key': key, 'label_zh': specs[key]['label_zh'], 'unit': specs[key]['unit'],
                              'from': values[key], 'to': target, 'total_score': moved['total_score'],
                              'score_delta': moved['total_score'] - current['total_score'],
                              'screening_category': moved['screening_category']})
    if targets:
        moved_values = dict(values, **targets)
        moved = compute(moved_values, sex)
        out['targets'] = {'values': targets, **moved,
                          'score_delta': moved['total_score'] - current['total_score'],
                          'warnings_zh': warnings(moved_values)}
    return out


def problem(key, kind, message):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest, *, targets=False):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError, csv.Error) as exc:
        return {}, [problem('targets' if targets else 'measurements', 'file', f'无法读取测量文件：{exc}')]
    problems = list(result.problems)
    problems += [problem(name, 'unknown', f'无法识别项目「{name}」，请核对项目名称；目标文件只接受腰围、BMI、收缩压。')
                 for name in result.unmatched]
    if targets and not result.values and not problems:
        problems.append(problem('targets', 'missing', '目标文件没有可读取的目标值。'))
    return result.values, problems


def read_scalar(raw, key, manifest):
    if raw is None:
        return None, skillkit.check_scalar(manifest, key, None)
    try:
        value = skillkit.parse_number(raw)
    except ValueError:
        return None, [problem(key, 'parse', f'{key} 必须是数值。')]
    problems = skillkit.check_scalar(manifest, key, value)
    if not problems and value != int(value):
        problems.append(problem(key, 'category', '年龄请填写已满周岁整数。'))
    return value, problems


def read_choice(raw, key, choices, manifest):
    if raw is None:
        return None, skillkit.check_scalar(manifest, key, None)
    value = choices.get(raw.strip().lower())
    if value is None:
        return None, [problem(key, 'category', f'{key} 的取值不明确，请使用：' + '、'.join(choices))]
    return value, skillkit.check_scalar(manifest, key, value)


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='已满周岁，20–74')
    parser.add_argument('--sex', help='male/female 或 男/女；按论文性别分类')
    parser.add_argument('--known-diabetes', help='yes/no；是否已经由医生诊断糖尿病')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    age, issues = read_scalar(args.age, 'age', manifest)
    problems += issues
    sex_number, issues = read_choice(args.sex, 'sex', {'male': 1, 'female': 0, '男': 1, '女': 0}, manifest)
    problems += issues
    known, issues = read_choice(args.known_diabetes, 'known_diabetes', {'yes': 1, 'no': 0, '是': 1, '否': 0}, manifest)
    problems += issues
    if known == 1:
        problems.append(problem('known_diabetes', 'population', '已确诊糖尿病者不适用此未诊断糖尿病筛查评分；本次不计算。'))
    if 'family_history' in values and values['family_history'] not in (0, 1):
        problems.append(problem('family_history', 'category', '一级亲属糖尿病史只接受 0（无）或 1（有）；未知不能填 0。'))
    targets = {}
    if args.targets is not None:
        target_manifest = {**manifest, 'inputs': [{**s, 'required': False} for s in manifest['inputs'] if s['key'] in MODIFIABLE]}
        targets, issues = collect(args.targets, target_manifest, targets=True)
        problems += issues
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 1)[1]
        path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values['age'] = age
    sex = 'male' if sex_number else 'female'
    result = compute(values, sex)
    scenario = levers(values, sex, targets, manifest)
    labels = {s['key']: s for s in manifest['inputs']}
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的评分', '',
             f"总分：**{result['total_score']} 分**（0–51 分）；**{result['screening_category']}**（≥25 分）。", '',
             '| 项目 | 当前值 | 得分 |', '|---|---|---|']
    for key in ('age', 'sex', 'waist_cm', 'bmi_kg_m2', 'sbp_mmhg', 'family_history'):
        display = ('男' if sex_number else '女') if key == 'sex' else (
            ('有' if values[key] else '无') if key == 'family_history' else f"{values[key]:g} {('岁' if key == 'age' else labels[key]['unit'])}")
        lines.append(f"| {labels[key]['label_zh']} | {display} | {result[key + '_points']} |")
    lines += ['', '达到阈值表示落入论文的进一步血糖检测筛查组，不能据此确诊；低于阈值仍可能漏检。',
              '适用背景：中国未确诊糖尿病成人；外部验证来自青岛。三年随访结果用于群体验证，不能直接换算成你的三年发病概率。']
    lines += ['', *warnings(values)] if warnings(values) else []
    if targets:
        moved = scenario['targets']
        lines += ['', '## 你提供的目标情景', '',
                  f"全部目标同时达到：{moved['total_score']} 分，变化 {moved['score_delta']:+g} 分，{moved['screening_category']}。", '',
                  '| 单项目标 | 原值 → 目标值 | 单独达到时总分 | 分差 |', '|---|---|---|---|']
        for item in scenario['levers']:
            lines.append(f"| {item['label_zh']} | {item['from']:g} → {item['to']:g} {item['unit']} | {item['total_score']} | {item['score_delta']:+g} |")
        lines += ['', *moved['warnings_zh']]
    lines += ['', LEVER_NOTE, '', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
