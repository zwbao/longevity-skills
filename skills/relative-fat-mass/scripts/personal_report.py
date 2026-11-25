#!/usr/bin/env python3
"""Offline RFM estimate with structured input errors and waist scenarios."""
import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (INTERCEPT, RATIO_COEFFICIENT, SEX_COEFFICIENT, SEX_CODES,
                     DEVELOPMENT_AGE, VALIDATION_AGE, DXA_HEIGHT_LIMIT_CM,
                     TITLE, BOUNDARY, TARGET_NOTE)


def rfm(values, sex):
    return INTERCEPT + RATIO_COEFFICIENT * values['height_cm'] / values['waist_cm'] + SEX_COEFFICIENT * sex


def read_measurements(path, manifest):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(
            'measurements', '测量文件', 'file', f'无法读取测量表：{exc}。请提供 marker,value,unit 格式的 CSV。')])
    for name in collected.unmatched:
        collected.problems.append(skillkit.Problem(name, name, 'unknown', f'无法识别指标「{name}」，请核对名称。'))
    return collected


def output_problem(values, sex, label):
    value = rfm(values, sex)
    if not 0 <= value <= 100:
        return [skillkit.Problem('rfm_pct', label, 'domain',
            f'{label}的身高与腰围组合使公式超出体脂百分比的物理范围，无法给出可解释估计；请核对单位和测量部位。不截断或改写公式。')]
    return []


def levers(values, age, sex, targets, manifest):
    current = rfm(values, sex)
    h, w = values['height_cm'], values['waist_cm']
    slopes = {'height_cm': RATIO_COEFFICIENT / w,
              'waist_cm': -RATIO_COEFFICIENT * h / w ** 2,
              'age': 0, 'sex': SEX_COEFFICIENT}
    inputs = dict(values, age=age, sex=sex)
    result = {
        'schema': 'longevity-levers/1', 'model': 'relative-fat-mass',
        'model_zh': TITLE, 'current': {'rfm_pct': current},
        'sensitivity': [
            {'key': s['key'], 'label_zh': s['label_zh'], 'unit': s['unit'],
             'value': inputs[s['key']], 'rfm_pp_per_unit': slopes[s['key']],
             'modifiable': s['key'] == 'waist_cm',
             'note_zh': ('性别项表示两种论文编码的离散差，不是可改变目标。' if s['key'] == 'sex'
                         else '年龄不进入方程。' if s['key'] == 'age'
                         else '当前输入附近的公式敏感度，不是干预效应。')}
            for s in manifest['inputs']],
        'levers': [], 'note_zh': TARGET_NOTE,
    }
    if targets:
        moved = dict(values, **targets)
        future = rfm(moved, sex)
        result['levers'] = [{'key': 'waist_cm', 'label_zh': '腰围', 'unit': 'cm',
                             'from': w, 'to': targets['waist_cm'], 'rfm_pct': future,
                             'rfm_delta_pp': future - current}]
        result['targets'] = {'values': targets, 'rfm_pct': future, 'rfm_delta_pp': future - current}
    return result


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='实足年龄（岁），仅作适用性检查')
    parser.add_argument('--sex', help='male/m/男/0 或 female/f/女/1，按论文编码')
    parser.add_argument('--targets', type=Path, help='仅腰围目标，marker,value,unit CSV')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    # A failed rerun must never leave a successful result from an older run.
    for filename in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    collected = read_measurements(args.measurements, manifest)
    problems = list(collected.problems)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        problems.append(skillkit.Problem('age', '实足年龄', 'parse', '年龄必须是有限的岁数。'))
    sex = SEX_CODES.get(args.sex.strip().lower()) if args.sex is not None else None
    if args.sex is not None and sex is None:
        problems.append(skillkit.Problem('sex', '论文性别编码', 'category', '性别只接受 male/m/男/0 或 female/f/女/1；不推断缺失性别。'))
    else:
        problems += skillkit.check_scalar(manifest, 'sex', sex)
    targets = {}
    if args.targets is not None:
        # Target files are partial: only waist may be changed; all errors stay fatal.
        target_manifest = dict(manifest, inputs=[dict(s, required=False) for s in manifest['inputs']])
        wanted = read_measurements(args.targets, target_manifest)
        problems += wanted.problems
        if 'height_cm' in wanted.values:
            problems.append(skillkit.Problem('height_cm', '身高', 'target', '目标文件只接受腰围；身高是固定测量，不作为改变目标。'))
        targets = {k: v for k, v in wanted.values.items() if k == 'waist_cm'}
        if not targets and not wanted.problems:
            problems.append(skillkit.Problem('waist_cm', '腰围目标', 'missing', '目标文件没有有效腰围目标。'))
    if not problems:
        problems += output_problem(collected.values, sex, '当前测量')
        if targets:
            problems += output_problem(dict(collected.values, **targets), sex, '目标情景')
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        text = report.read_text(encoding='utf-8')
        heading, body = text.split('\n', 1)
        report.write_text(heading + '\n\n' + '\n'.join(paper_card_lines()) + '\n' + body, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values = collected.values
    estimate = rfm(values, sex)
    scenarios = levers(values, age, sex, targets, manifest)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f'RFM 全身体脂率估计：**{estimate:.1f}%**。这是公式估计，不是一次体脂测量。', '',
             f'采用身高 {values["height_cm"]:g} cm、腰围 {values["waist_cm"]:g} cm；'
             f'论文性别编码 {sex}（{"女" if sex else "男"}）；年龄 {age:g} 岁仅作范围提示。', '',
             '腰围需按论文方法：站立、呼气末，在右侧髂骨上缘水平绕裸露腰部测量，记录至 0.1 cm。'
             '肚脐、最细腰部或其他部位的围度不能直接当作同一测量。', '',
             '研究来自美国成年人，分族群分析限墨西哥裔、欧洲裔和非洲裔；对中国及其他亚洲人群、'
             '运动员和特定疾病人群，本研究未验证。孕妇被研究排除，不适用本报告；较瘦人群估计表现较弱。']
    if age > VALIDATION_AGE[1]:
        lines += ['', '你的年龄超出独立验证年龄范围（20–69 岁），结果需视为该范围之外的公式估计。']
    if age > DEVELOPMENT_AGE[1]:
        lines += ['', '推导数据将 85 岁及以上统一编码为 85，不能确认你的具体年龄在研究中的表现。']
    if values['height_cm'] > DXA_HEIGHT_LIMIT_CM:
        lines += ['', '你的身高超出该研究 DXA 扫描入选上限，适用性有限。']
    lines += ['', '研究还排除了自报体重超过 300 磅及近期接受造影等人群；当前输入不能核对所有排除条件。']
    if targets:
        target = scenarios['targets']
        lines += ['', '## 你指定的腰围情景', '',
                  f'腰围变为 {targets["waist_cm"]:g} cm 时，公式估计为 {target["rfm_pct"]:.1f}%，'
                  f'相对当前变化 {target["rfm_delta_pp"]:+.1f} 个百分点。', '', TARGET_NOTE]
    lines += ['', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, {'rfm_pct': estimate})
    (args.out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
