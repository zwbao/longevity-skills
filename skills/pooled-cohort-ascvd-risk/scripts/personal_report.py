"""Offline personal report for the original 2013 Pooled Cohort Equations."""
import argparse
import csv
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGES, BASELINES, BOUNDARY, COEFFICIENTS, DISPLAY_LIMITS,
                     FLAGS, MEASUREMENTS, SCENARIO_NOTE, TARGET_KEYS)

TITLE = 'PCE 十年首次心血管病风险'


def compute(values, age, sex, race):
    """Table A dot product and Table B survival equation; return percent."""
    la, lt, lh, lb = map(math.log, (age, values['tc_mg_dl'], values['hdl_mg_dl'], values['sbp_mmhg']))
    treated = values['treated']
    terms = dict(ln_age=la, ln_age_squared=la * la, ln_tc=lt, ln_age_tc=la * lt,
                 ln_hdl=lh, ln_age_hdl=la * lh,
                 ln_sbp_treated=lb * treated, ln_sbp_untreated=lb * (1 - treated),
                 ln_age_sbp_treated=la * lb * treated,
                 ln_age_sbp_untreated=la * lb * (1 - treated),
                 smoker=values['smoker'], ln_age_smoker=la * values['smoker'],
                 diabetes=values['diabetes'])
    total = math.fsum(coef * terms[key] for key, coef in COEFFICIENTS[sex, race].items())
    mean, survival = BASELINES[sex, race]
    return -100 * math.expm1(math.log(survival) * math.exp(total - mean))


def display_risk(risk):
    if risk < DISPLAY_LIMITS[0]:
        return '<1%'
    if risk > DISPLAY_LIMITS[1]:
        return '>30%'
    return f'{risk:.1f}%'


def issue(key, message, kind='invalid'):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest, partial=False):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error) as exc:
        return {}, [issue('file', f'无法读取输入表：{exc}', 'file')]
    problems = [p for p in result.problems if not (partial and p.kind == 'missing')]
    if partial:
        problems += [issue(name, f'目标项目「{name}」无法识别。') for name in result.unmatched]
        for key in result.values.keys() - TARGET_KEYS:
            problems.append(issue(key, f'{key} 不是允许的目标；治疗和糖尿病状态不能作为调节开关。'))
        if not result.values and not problems:
            problems.append(issue('targets', '目标表没有可用的目标值。', 'missing'))
    for key in FLAGS:
        if key in result.values and result.values[key] not in (0, 1):
            problems.append(issue(key, f'{key} 必须是 0（否）或 1（是），不能用小数。'))
    return result.values, problems


def levers(values, age, sex, race, targets, manifest):
    current = compute(values, age, sex, race)
    sensitivity = []
    specs = {s['key']: s for s in manifest['inputs']}
    for key in (*MEASUREMENTS, 'age'):
        x = age if key == 'age' else values[key]
        lo, hi = specs[key]['range']
        step = max(1, abs(x)) * 1e-4  # Numerical differentiation step, not a model constant.
        low, high = max(lo, x-step), min(hi, x+step)
        if key == 'age':
            delta = compute(values, high, sex, race) - compute(values, low, sex, race)
        else:
            delta = compute(dict(values, **{key: high}), age, sex, race) - compute(dict(values, **{key: low}), age, sex, race)
        sensitivity.append(dict(key=key, label_zh=specs[key]['label_zh'], unit=specs[key]['unit'],
            value=x, per_unit=delta/(high-low), not_a_target=key == 'age'))
    for key in FLAGS:
        delta = compute(dict(values, **{key: 1}), age, sex, race) - compute(dict(values, **{key: 0}), age, sex, race)
        sensitivity.append(dict(key=key, label_zh=specs[key]['label_zh'], unit='1', value=values[key],
            change_0_to_1_pct=delta, not_a_target=key != 'smoker'))
    out = dict(schema='longevity-levers/1', model='pooled-cohort-ascvd-risk',
        model_zh=TITLE, population_age_years=list(AGES), age_outside_derivation=False,
        current=dict(risk_10y_pct=current, risk_display=display_risk(current), age=age, sex=sex, race=race),
        sensitivity=sensitivity, levers=[], note_zh=SCENARIO_NOTE)
    for key, target in targets.items():
        risk = compute(dict(values, **{key: target}), age, sex, race)
        out['levers'].append(dict(key=key, label_zh=specs[key]['label_zh'], unit=specs[key]['unit'],
            **{'from': values[key], 'to': target}, risk_10y_pct=risk, risk_display=display_risk(risk), risk_delta_pct=risk-current))
    if targets:
        risk = compute(dict(values, **targets), age, sex, race)
        out['targets'] = dict(values=targets, risk_10y_pct=risk, risk_display=display_risk(risk), risk_delta_pct=risk-current)
    return out


def with_card(text):
    first, rest = text.split('\n', 1)
    return first + '\n\n' + '\n'.join(paper_card_lines()) + '\n' + rest


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--race')
    parser.add_argument('--eligible', help='yes only if asymptomatic and no excluded cardiovascular history; see SKILL.md')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Remove stale outputs before validation, including success -> failure reruns.
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except (ValueError, TypeError):
        age = None
        problems.append(issue('age', '年龄必须是有限的数字，单位为岁。'))
    sex = {'m': 'male', '男': 'male', 'f': 'female', '女': 'female'}.get(str(args.sex).lower(), str(args.sex).lower())
    race = str(args.race).lower()
    if sex not in ('male', 'female'):
        problems.append(issue('sex', '请提供原方程使用的性别 male 或 female。', 'missing' if args.sex is None else 'invalid'))
    if race not in ('white', 'african_american'):
        problems.append(issue('race', '请明确原方程组 white 或 african_american；不能自动把中国或其他族群归入白人组。', 'missing' if args.race is None else 'invalid'))
    if args.eligible != 'yes':
        problems.append(issue('eligible', '需要确认无心血管症状，且无心肌梗死、卒中、心衰、冠脉介入/搭桥或房颤史（--eligible yes）；不满足时不适用此首次事件模型。', 'missing' if args.eligible is None else 'ineligible'))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems += target_problems
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report.write_text(with_card(report.read_text(encoding='utf-8')), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {o['key']: None for o in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    risk = compute(values, age, sex, race)
    outputs = dict(risk_10y_pct=risk, risk_display=display_risk(risk), equation_group=f'{race}_{sex}')
    skillkit.write_result(args.out, manifest, outputs)
    scenario = levers(values, age, sex, race, targets, manifest)
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    group = ('白人' if race == 'white' else '非裔美国人') + ('男性' if sex == 'male' else '女性')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '',
             f'你的十年首次 ASCVD 风险估计：**{display_risk(risk)}**。', '',
             f'采用原论文的{group}方程；年龄 {age:g} 岁。结局包括非致死性心肌梗死、冠心病死亡及致死或非致死性卒中。', '',
             '这是相似条件人群的风险估计，不是你必然会发生的事。原模型来自美国队列，不能默认适用于中国人群。', '',
             '| 输入 | 本次值 |', '|---|---|']
    for key, value in values.items():
        spec = skillkit.spec_by_key(manifest, key)
        shown = ('是' if value else '否') if key in FLAGS else f'{value:g} {spec["unit"]}'
        lines.append(f'| {spec["label_zh"]} | {shown} |')
    if risk < DISPLAY_LIMITS[0] or risk > DISPLAY_LIMITS[1]:
        lines += ['', '结果处于论文提示的不稳定边缘，报告仅显示 <1% 或 >30%；机器文件保留原方程值供审计，不应当作精确概率解读。']
    if targets:
        lines += ['', f'若同时达到所填目标，模型估计为 **{scenario["targets"]["risk_display"]}**。', SCENARIO_NOTE]
    lines += ['', '敏感度和单项情景见 levers.json；年龄、族群和性别不是健康目标。本文不计算终生风险、治疗获益或用药分档。', '', f'边界: {BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
