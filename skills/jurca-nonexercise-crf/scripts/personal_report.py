#!/usr/bin/env python3
"""NASA non-exercise CRF worksheet; standard library only."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (ACTIVITY_LABELS, ACTIVITY_SCORES, BOUNDARY, COEFFICIENTS,
                     INTERCEPT, MODIFIABLE, SCENARIO_NOTE, VALIDATION_NOTE)

TITLE = '非运动测试心肺适能估计'


def terms(values):
    return {'intercept': INTERCEPT,
            **{k: c * values[k] for k, c in COEFFICIENTS.items()},
            'activity_level': ACTIVITY_SCORES[int(values['activity_level'])]}


def estimate(values):
    return sum(terms(values).values())


def problem(key, message, kind='parse'):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest, partial=False):
    if partial:
        manifest = {**manifest, 'inputs': [{**s, 'required': False} for s in manifest['inputs']]}
    try:
        rows = skillkit.read_rows(path) if path is not None else []
        data = skillkit.collect_measurements(rows, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [problem('measurements', f'无法读取输入表：{exc}', 'file')]
    problems = list(data.problems)
    if partial and rows:
        value_names = {skillkit.fold_name(name) for name in skillkit.VALUE_COLUMNS}
        value_column = next((key for key in rows[0] if skillkit.fold_name(key) in value_names), None)
        if value_column and any(not row.get(value_column, '').strip() for row in rows):
            problems.append(problem('targets', '目标表存在空数值，请填写目标或删除该行。', 'missing'))
    for name in data.unmatched:
        problems.append(problem(name, f'无法识别项目「{name}」，请使用清单中的名称。', 'unknown'))
    if 'activity_level' in data.values and not data.values['activity_level'].is_integer():
        problems.append(problem('activity_level', '活动等级须为1到5的整数，请按图1描述选择一档。', 'range'))
    if partial and not data.values and not problems:
        problems.append(problem('targets', '目标表没有可计算的目标值。', 'missing'))
    return dict(data.values), problems


def scalar(raw, key, manifest):
    try:
        value = float(raw) if raw is not None else None
    except (ValueError, TypeError):
        return None, [problem(key, f'{key} 不是可计算的数。')]
    return value, skillkit.check_scalar(manifest, key, value)


def make_levers(values, wanted, manifest):
    current = estimate(values)
    specs = {s['key']: s for s in manifest['inputs']}
    sensitivities = []
    for key, coefficient in COEFFICIENTS.items():
        sensitivities.append({'key': key, 'label_zh': specs[key]['label_zh'],
                              'unit': specs[key]['unit'], 'value': values[key],
                              'met_per_unit': coefficient, 'modifiable': key in MODIFIABLE,
                              'kind': 'binary_contrast' if key == 'sex' else 'linear'})
    level = int(values['activity_level'])
    sensitivities.append({'key': 'activity_level', 'label_zh': '活动等级',
                          'unit': 'score', 'value': level, 'modifiable': True,
                          'kind': 'categorical', 'categories': [
                              {'level': k, 'score_met': score,
                               'estimated_crf_met_delta': score - ACTIVITY_SCORES[level]}
                              for k, score in ACTIVITY_SCORES.items()]})
    out = {'schema': 'longevity-levers/1', 'model': 'jurca-nasa-nonexercise-crf',
           'model_zh': 'Jurca NASA非运动测试心肺适能估计',
           'current': {'estimated_crf_met': current},
           'sensitivity': sensitivities, 'levers': [], 'note_zh': SCENARIO_NOTE}
    for key, target in wanted.items():
        moved = estimate({**values, key: target})
        out['levers'].append({'key': key, 'label_zh': specs[key]['label_zh'],
                              'unit': specs[key]['unit'], 'from': values[key], 'to': target,
                              'estimated_crf_met': moved, 'estimated_crf_met_delta': moved-current})
    if wanted:
        together = estimate({**values, **wanted})
        out['targets'] = {'values': wanted, 'estimated_crf_met': together,
                          'estimated_crf_met_delta': together-current}
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex', help='论文编码：female/女/0；male/男/1')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for filename in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    age, errors = scalar(args.age, 'age', manifest)
    problems += errors
    sex_map = {'male': 1, 'm': 1, '男': 1, '1': 1,
               'female': 0, 'f': 0, '女': 0, '0': 0}
    raw_sex = args.sex.strip().lower() if args.sex is not None else None
    sex = sex_map.get(raw_sex)
    if raw_sex is not None and sex is None:
        problems.append(problem('sex', '性别须按论文编码提供：female/女/0 或 male/男/1。'))
    else:
        problems += skillkit.check_scalar(manifest, 'sex', sex)
    wanted = {}
    if args.targets is not None:
        wanted, errors = collect(args.targets, manifest, partial=True)
        problems += errors
        for key in wanted:
            if key not in MODIFIABLE:
                problems.append(problem(key, '目标仅接受BMI、静息心率和活动等级。', 'target'))
    if problems:
        report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        lines = report.read_text().splitlines()
        report.write_text('\n'.join([lines[0], '', *paper_card_lines(), '', *lines[1:]]) + '\n')
        return skillkit.EXIT_INPUT_PROBLEM
    values.update(age=age, sex=sex)
    result = estimate(values)
    levers = make_levers(values, wanted, manifest)
    skillkit.write_result(out, manifest, {'estimated_crf_met': result,
                                        'activity_score_met': ACTIVITY_SCORES[int(values['activity_level'])]})
    (out / 'levers.json').write_text(json.dumps(levers, ensure_ascii=False, indent=2) + '\n')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的估计结果', '',
             f'按NASA计算表估计的最大心肺适能为 **{result:.2f} MET**。',
             'MET是代谢当量；这里描述估计的最大能力，不是日常活动的耗能量。',
             VALIDATION_NOTE, '', '## 本次输入', '']
    specs = {s['key']: s for s in manifest['inputs']}
    shown_units = {'age': '岁', 'bmi_kg_m2': 'kg/m²', 'resting_hr_bpm': '次/分钟',
                   'activity_level': '级'}
    for key, value in values.items():
        if key == 'sex':
            lines.append('- 论文性别类别：' + ('男' if value == 1 else '女'))
        else:
            lines.append(f'- {specs[key]["label_zh"]}：{value:g} {shown_units[key]}')
    lines += ['', '活动档位：' + ACTIVITY_LABELS[int(values['activity_level'])],
              '静息心率的研究测法为平卧或半卧休息5分钟后记录心电图；设备日均心率不能直接等同。',
              '原模型来自20–70岁人群，不能据此给出适能达标档位或死亡风险。',
              '推导样本未使用影响心率的药物；若正在使用这类药物，本模型的适用性未获验证。']
    if result <= 0:
        lines.append('本组输入得到非正估计，提示线性模型在该组合下不适用；数值未截断，不能作生理解释。')
    if wanted:
        lines += ['', '## 你提供的目标情景', '',
                  f'全部目标同时代入：{levers["targets"]["estimated_crf_met"]:.2f} MET；'
                  f'相对当前公式值变化：{levers["targets"]["estimated_crf_met_delta"]:+.2f} MET。']
        for item in levers['levers']:
            lines.append(f'- 只改变{item["label_zh"]}：{item["from"]:g} → {item["to"]:g}，'
                         f'公式值变化 {item["estimated_crf_met_delta"]:+.2f} MET。')
    lines += ['', SCENARIO_NOTE, '', f'边界: {BOUNDARY}']
    (out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
