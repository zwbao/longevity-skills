"""Offline six-item FTND scoring; Python standard library only."""
import argparse
import copy
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BINARY_KEYS, BINARY_POINTS, BOUNDARY, CPD_POINTS,
                     ITEM_KEYS, OUTPUT_KEYS, SCENARIO_NOTE, STUDY_AGE_RANGE,
                     TTF_POINTS)


def score_item(key, value):
    if key in BINARY_KEYS:
        return BINARY_POINTS[value]
    table = TTF_POINTS if key == 'time_to_first_cigarette_min' else CPD_POINTS
    if key not in ITEM_KEYS:
        raise KeyError(key)
    return next(points for upper, points in table if upper is None or value <= upper)


def calculate(values):
    points = {OUTPUT_KEYS[key]: score_item(key, values[key]) for key in ITEM_KEYS}
    return dict(points, ftnd_score=sum(points.values()))


def problem(key, message, kind='value'):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [problem('file', f'无法读取回答表：{exc}', 'file')]
    problems = list(data.problems)
    for name in data.unmatched:
        problems.append(problem(name, f'无法识别「{name}」，请核对回答项目名称。', 'unknown'))
    for key, value in data.values.items():
        if key in BINARY_KEYS and value not in BINARY_POINTS:
            problems.append(problem(key, '二选一题只能填0或1；未知须补问，不能填0。'))
        elif key in ('time_to_first_cigarette_min', 'cigarettes_per_day_count'):
            # Paper uses integer response bands; do not invent rounding for gaps.
            if not math.isclose(value, round(value), rel_tol=0, abs_tol=1e-9):
                problems.append(problem(key, '请填整数分钟或每日整数支数；不对小数回答自动取整。'))
            else:
                data.values[key] = int(round(value))
    return data.values, problems


def levers(values, targets, manifest):
    current = calculate(values)
    specs = {s['key']: s for s in manifest['inputs']}
    data = {
        'schema': 'longevity-levers/1', 'model': manifest['name'],
        'model_zh': 'FTND六题计分', 'current': current,
        'sensitivity': [], 'levers': [], 'note_zh': SCENARIO_NOTE,
    }
    # A discrete score has no useful continuous derivative. Expose the actual
    # printed answer-to-point table rather than inventing default goal values.
    for key in ITEM_KEYS:
        table = (TTF_POINTS if key == ITEM_KEYS[0] else
                 CPD_POINTS if key == 'cigarettes_per_day_count' else None)
        data['sensitivity'].append({
            'key': key, 'label_zh': specs[key]['label_zh'], 'unit': specs[key]['unit'],
            'value': values[key], 'points': current[OUTPUT_KEYS[key]],
            'method': 'discrete_table',
            'scoring': ([{'upper_inclusive': bound, 'points': pts} for bound, pts in table]
                        if table else [{'answer': answer, 'points': pts}
                                       for answer, pts in BINARY_POINTS.items()]),
        })
    for key, target in targets.items():
        moved = calculate(dict(values, **{key: target}))
        data['levers'].append({
            'key': key, 'label_zh': specs[key]['label_zh'], 'unit': specs[key]['unit'],
            'from': values[key], 'to': target, **moved,
            'ftnd_score_delta': moved['ftnd_score'] - current['ftnd_score'],
        })
    if targets:
        moved = calculate(dict(values, **targets))
        data['targets'] = {'values': targets, **moved,
                           'ftnd_score_delta': moved['ftnd_score'] - current['ftnd_score']}
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description='FTND尼古丁依赖六题计分')
    parser.add_argument('--measurements', type=Path, help='marker,value,unit CSV')
    parser.add_argument('--age', help='可选，年龄（岁）；仅检查研究年龄范围')
    parser.add_argument('--sex', help='可选，male/female或男/女；不参与计分')
    parser.add_argument('--targets', type=Path, help='可选，变化后的回答CSV；不是治疗目标建议')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'levers.json', 'problems.json'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    if values.get('current_cigarette_smoker') == 0:
        problems.append(problem('current_cigarette_smoker',
                                '本方法限当前卷烟吸烟者；非吸烟者、已戒烟者或仅用其他尼古丁产品者不计算。',
                                'population'))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, 'age', age))
        except ValueError:
            problems.append(problem('age', '年龄须为有限数值，单位为岁。', 'parse'))
    if args.sex is not None and args.sex.strip().lower() not in ('male', 'female', '男', '女'):
        problems.append(problem('sex', '可选性别请填male/female或男/女，或省略；不进入得分。'))
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        for spec in target_manifest['inputs']:
            spec['required'] = False
        targets, target_problems = collect(args.targets, target_manifest)
        problems.extend(target_problems)
        for key in targets:
            if key not in ITEM_KEYS:
                problems.append(problem(key, '情境比较只接受六题回答，不接受适用性状态、年龄或性别。', 'target'))
        if not targets and not target_problems:
            problems.append(problem('targets', '情境比较表至少需要一项有效回答。', 'missing'))
    header = ['# FTND尼古丁依赖计分报告', '', *paper_card_lines(), '']
    if problems:
        skillkit.write_problems(args.out, problems, 'FTND尼古丁依赖计分报告', BOUNDARY)
        body = skillkit.problems_markdown(problems, 'FTND尼古丁依赖计分报告', BOUNDARY).split('\n', 2)[2]
        (args.out / 'report.md').write_text('\n'.join(header) + '\n' + body, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    skillkit.write_result(args.out, manifest, result)
    scenario = levers(values, targets, manifest)
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    specs = {s['key']: s for s in manifest['inputs']}
    maximum = sum(max(p for _, p in TTF_POINTS) if k == ITEM_KEYS[0] else
                  max(p for _, p in CPD_POINTS) if k == 'cigarettes_per_day_count' else
                  max(BINARY_POINTS.values()) for k in ITEM_KEYS)
    lines = header + ['## 你的结果', '', f"FTND总分：{result['ftnd_score']}分（范围0–{maximum}分）。",
                      '分数越高表示本量表记录的依赖表现越多；本论文未定义轻、中、重度分档。', '',
                      '| 项目 | 你的回答 | 得分 |', '|---|---|---:|']
    for key in ITEM_KEYS:
        if key == 'morning_cigarette_hardest':
            answer = '晨起第一支' if values[key] else '其他支'
        elif key in BINARY_KEYS:
            answer = '是' if values[key] else '否'
        else:
            answer = f"{values[key]:g}" + ('分钟' if key == ITEM_KEYS[0] else '支/日')
        lines.append(f"| {specs[key]['label_zh']} | {answer} | {result[OUTPUT_KEYS[key]]} |")
    lines += ['', '采用原文表3；已核对逐题印刷分值，原文没有完整个人总分算例。',
              '中文题意为本技能的说明性翻译，未声称是经过验证的中文版量表。']
    if age is None:
        lines.append('未提供年龄；未核对年龄适用性。原研究年龄范围为17–77岁。')
    elif not STUDY_AGE_RANGE[0] <= age <= STUDY_AGE_RANGE[1]:
        lines.append(f'你的年龄（{age:g}岁）超出原研究17–77岁范围；分数仅是规则计算，适用性未验证。')
    if targets:
        goal = scenario['targets']
        lines += ['', '## 你指定的回答变化', '',
                  f"所有变化同时代入：{goal['ftnd_score']}分，较当前变化{goal['ftnd_score_delta']:+g}分。",
                  SCENARIO_NOTE]
    lines += ['', f'边界: {BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
