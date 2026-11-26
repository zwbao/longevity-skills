#!/usr/bin/env python3
"""Classify reported weekly ethanol mass using printed categories; no survival fit."""
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import ALCOHOL_KEY, BANDS, BOUNDARY, GRAMS_PER_UK_UNIT, TITLE


def calculate(grams, current_drinker, cvd_history):
    applicable = grams > 0 and current_drinker == 1 and cvd_history == 0
    band = loss = None
    if applicable:
        _, band, loss = next(row for row in BANDS if row[0] is None or grams <= row[0])
    return {
        'reported_alcohol_g_week': grams,
        'uk_units_per_week': grams / GRAMS_PER_UK_UNIT,
        'scope_status': '可作原研究分档对照' if applicable else '不适用原研究主要人群',
        'consumption_band': band,
        'study_loss_at_40': loss,
    }


def read_input(path, manifest):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(
            '', '输入文件', 'file', f'无法读取输入表：{exc}')])
    for key in ('current_drinker', 'cvd_history'):
        if key in collected.values and collected.values[key] not in (0, 1):
            collected.problems.append(skillkit.Problem(key, key, 'category', '请填写0（否）或1（是），不能填写小数。'))
    if collected.unmatched:
        collected.problems.append(skillkit.Problem('', '指标名称', 'unknown',
                                  '未识别指标：' + '、'.join(collected.unmatched)))
    return collected


def levers(values, targets):
    current = calculate(values[ALCOHOL_KEY], values['current_drinker'], values['cvd_history'])
    payload = {
        'schema': 'longevity-levers/1', 'model': 'alcohol-consumption-thresholds',
        'model_zh': TITLE, 'current': current,
        'sensitivity': [{'key': ALCOHOL_KEY, 'unit': 'g', 'value': values[ALCOHOL_KEY],
                         'uk_units_per_g': 1 / GRAMS_PER_UK_UNIT,
                         'band_derivative': None,
                         'note_zh': '分档为阶梯函数；不提供每克对应的寿命变化。'}],
        'levers': [], 'note_zh': '仅比较输入量与分档；不估算减酒带来的寿命收益。',
    }
    if ALCOHOL_KEY in targets:
        target = targets[ALCOHOL_KEY]
        result = calculate(target, values['current_drinker'], values['cvd_history'])
        change = {'key': ALCOHOL_KEY, 'unit': 'g', 'from': values[ALCOHOL_KEY], 'to': target,
                  'amount_delta_g': target - values[ALCOHOL_KEY],
                  'uk_units_delta': (target - values[ALCOHOL_KEY]) / GRAMS_PER_UK_UNIT,
                  'from_band': current['consumption_band'], 'to_band': result['consumption_band']}
        payload['levers'].append(change)
        payload['targets'] = {'values': targets, 'outputs': result}
    return payload


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ('problems.json', 'result.json', 'levers.json', 'report.md'):
        (args.out / filename).unlink(missing_ok=True)
    collected = read_input(args.measurements, manifest)
    problems = list(collected.problems)
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        target_manifest['inputs'] = [s for s in target_manifest['inputs'] if s['key'] == ALCOHOL_KEY]
        target_collected = read_input(args.targets, target_manifest)
        problems.extend(target_collected.problems)
        targets = target_collected.values
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report = ['# ' + TITLE, '', *paper_card_lines(), '',
                  skillkit.problems_markdown(problems, '输入待补充或更正', BOUNDARY)]
        (args.out / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    values = collected.values
    result = calculate(values[ALCOHOL_KEY], values['current_drinker'], values['cvd_history'])
    report = ['# ' + TITLE, '', *paper_card_lines(), '', '## 你的记录', '',
              f"每周纯酒精总量：{result['reported_alcohol_g_week']:g} 克。",
              f"换算为英国酒精单位：{result['uk_units_per_week']:g} 单位/周（每单位8克，不等于一杯）。", '',
              f"适用性：{result['scope_status']}。"]
    if result['consumption_band'] is not None:
        report.extend([f"按自报量所在档位：{result['consumption_band']}。", '',
                       '## 对应研究人群的结果', '',
                       (f"相对 >0–≤100 g/week 档，论文在40岁起算的研究人群预期寿命较短：{result['study_loss_at_40']}。"
                        if values[ALCOHOL_KEY] > BANDS[0][0] else f"{result['study_loss_at_40']}。"),
                       '这些近似值是把分档死亡风险比套用到美国40岁及以上死亡率（CDC WONDER）后的模型估计，不是置信区间，也不适用于把其他年龄换算为寿命损失。'])
    else:
        report.append('非当前饮酒者、酒精总量为零或有既往心血管病时，不给出该研究的寿命差对照。')
    report.extend(['', '每周总量无法反映一次大量饮酒；这份报告不评估该模式，也不计算绝对患病概率。'])
    if targets:
        compared = calculate(targets[ALCOHOL_KEY], values['current_drinker'], values['cvd_history'])
        report.extend(['', '## 你提供的情景', '',
                       f"每周纯酒精总量为 {targets[ALCOHOL_KEY]:g} 克时：{compared['consumption_band'] or compared['scope_status']}。",
                       '这里只比较档位，不把两档研究寿命差相减当作个人获益。'])
    report.extend(['', BOUNDARY])
    (args.out / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'levers.json').write_text(json.dumps(levers(values, targets), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
