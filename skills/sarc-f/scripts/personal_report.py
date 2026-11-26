"""Offline standard SARC-F (AAH/BLSA wording); Python standard library only."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, FALLS_HIGH_MIN, FALLS_SOME_MIN, ITEM_KEYS,
                     ITEM_MAX, ITEM_MIN, LABELS, POSITIVE_MIN, TOTAL_MAX)

TITLE = 'SARC-F 肌少症风险筛查'


def falls_points(count):
    if count >= FALLS_HIGH_MIN:
        return ITEM_MAX
    return FALLS_SOME_MIN if count >= FALLS_SOME_MIN else ITEM_MIN


def calculate(values):
    scores = {key: int(values[key]) for key in ITEM_KEYS}
    scores['falls_score'] = falls_points(values['falls_past_year_count'])
    total = sum(scores.values())
    return {**scores, 'sarc_f_score': total,
            'screening_category': '筛查阳性' if total >= POSITIVE_MIN else '筛查阴性'}


def with_card(text):
    first, *rest = text.splitlines()
    return '\n'.join([first, '', *paper_card_lines(), '', *rest]) + '\n'


def collect(path, manifest, age, sex):
    try:
        collected = skillkit.collect_file(path, manifest)
        values, problems = dict(collected.values), list(collected.problems)
        for name in collected.unmatched:
            problems.append(skillkit.Problem(name, name, 'unknown', f'无法识别项目「{name}」，请核对问卷项目名称。'))
    except (OSError, ValueError, UnicodeError, AttributeError) as exc:
        values = {}
        problems = [skillkit.Problem('file', '问卷文件', 'file', f'无法读取问卷表：{exc}')]
    for key, value in values.items():
        if not value.is_integer():
            problems.append(skillkit.Problem(key, key, 'value', f'{key} 必须是整数；未知不要填0。'))
    if age is not None:
        try:
            age_value = skillkit.parse_number(age)
            problems += skillkit.check_scalar(manifest, 'age', age_value)
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄应填写有限的数值（岁）。'))
    if sex is not None and sex not in ('male', 'female', '男', '女', '1', '0'):
        problems.append(skillkit.Problem('sex', '性别', 'value', '性别可省略，或填male/男/1、female/女/0。'))
    return values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='可选，年龄仅作背景，不参与评分')
    parser.add_argument('--sex', help='可选，性别仅作背景，不参与评分')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest, args.age, args.sex)
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report.write_text(with_card(report.read_text(encoding='utf-8')), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f"总分：**{result['sarc_f_score']} / {TOTAL_MAX}**；**{result['screening_category']}**。",
             f'论文筛查阈值为总分≥{POSITIVE_MIN}。', '', '| 问卷项目 | 得分 |', '|---|---:|']
    lines += [f'| {label} | {result[key]} |' for key, label in LABELS.items()]
    lines += ['', f"过去一年自报跌倒次数：{int(values['falls_past_year_count'])}。"]
    if args.age is not None:
        lines.append(f'年龄：{args.age}岁（不参与评分）。')
    if args.sex is not None:
        lines.append(f"性别：{'男' if args.sex in ('male', '男', '1') else '女'}（不参与评分）。")
    if result['sarc_f_score'] >= POSITIVE_MIN:
        lines += ['', '达到论文的筛查阳性阈值，提示需要进一步评估肌力和身体功能；可将问卷结果带给医生。']
    else:
        lines += ['', '未达到论文的筛查阳性阈值，但低分不能排除肌少症；已有无力、步行困难或跌倒仍值得进一步评估。']
    lines += ['', '采用AAH/BLSA版本；NHANES以平衡或跌倒问题替代跌倒次数，不能与这里的输入混用。',
              '该研究来自美国社区中老年人；本报告中文题意是说明性翻译，不代表中文量表已在本研究验证。',
              '这是一份自报问卷，无需现场尝试负重或爬楼。分数不能用于推断减少助具使用会改善健康。',
              '', f'边界: {BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    print(args.out / 'report.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
