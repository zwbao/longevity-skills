#!/usr/bin/env python3
"""Original 1994 8-foot SPPB; no imported modern scoring conventions."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BALANCE_HOLD_S, BALANCE_KEYS, BOUNDARY, CHAIR_BANDS,
                     SCENARIO_NOTE, STATUS_KEYS, STUDY_MIN_AGE, TANDEM_BANDS,
                     TIMED_TASKS, UNABLE_SCORE, WALK_BANDS)

TITLE = '原版 SPPB 下肢体能报告（8英尺方案）'


def timed_score(seconds, bands):
    # Values are validated at the printed recording precision before scoring.
    for low, high, score in bands:
        if low <= seconds <= high:
            return score
    raise ValueError('时间不在原文印出的区间内。')


def balance_score(semi, side=None, tandem=None):
    if semi < BALANCE_HOLD_S:
        if side is None:
            raise ValueError('缺少并足站立时间。')
        return 1 if side == BALANCE_HOLD_S else UNABLE_SCORE
    if tandem is None:
        raise ValueError('缺少全串联站立时间。')
    return timed_score(tandem, TANDEM_BANDS)


def assess(values):
    balance = balance_score(values['semi_tandem_s'], values.get('side_by_side_s'), values.get('full_tandem_s'))
    walk = (timed_score(min(values[k] for k in TIMED_TASKS['walk_completed']), WALK_BANDS)
            if values['walk_completed'] else UNABLE_SCORE)
    chair = (timed_score(values['five_chair_stands_s'], CHAIR_BANDS)
             if values['chair_completed'] else UNABLE_SCORE)
    return dict(balance_score=balance, walk_score=walk, chair_score=chair, sppb_score=balance + walk + chair)


def problem(manifest, key, kind, message):
    label = skillkit.spec_by_key(manifest, key)['label_zh'] if key else '测量文件'
    return skillkit.Problem(key, label, kind, message)


def validate(values, manifest, complete=True):
    """Check discrete precision and the actual protocol branches; never impute."""
    errors = []
    for key, value in values.items():
        errors += skillkit.check_scalar(manifest, key, value)
        multiplier = 1 if key in BALANCE_KEYS + STATUS_KEYS else 10
        if not math.isfinite(value):
            continue  # Range check already records this.
        if not math.isclose(value * multiplier, round(value * multiplier), abs_tol=1e-8, rel_tol=0):
            msg = ('此项只接受 0 或 1。' if key in STATUS_KEYS else
                   '此项需提供原表整秒记录。' if key in BALANCE_KEYS else '此项需提供原表 0.1 秒精度的记录。')
            errors.append(problem(manifest, key, 'precision', msg + '不自动四舍五入或补齐原文区间。'))
    if not complete:
        return errors
    for spec in skillkit.input_specs(manifest):
        if spec['required'] and spec['key'] not in values:
            errors.append(problem(manifest, spec['key'], 'missing', f"缺少{spec['label_zh']}；缺测不能填 0。"))
    semi = values.get('semi_tandem_s')
    if semi is not None:
        needed = 'full_tandem_s' if semi == BALANCE_HOLD_S else 'side_by_side_s'
        unused = 'side_by_side_s' if semi == BALANCE_HOLD_S else 'full_tandem_s'
        if needed not in values:
            errors.append(problem(manifest, needed, 'missing', f"此平衡测试分支需要{skillkit.spec_by_key(manifest, needed)['label_zh']}。"))
        if unused in values:
            errors.append(problem(manifest, unused, 'protocol', '该项不属于本次半串联结果所对应的测试分支，请核对后省略。'))
    for status, keys in TIMED_TASKS.items():
        for key in keys:
            if values.get(status) == 1 and key not in values:
                errors.append(problem(manifest, key, 'missing', f"已声明完成，仍缺少{skillkit.spec_by_key(manifest, key)['label_zh']}。"))
            if values.get(status) == 0 and key in values:
                errors.append(problem(manifest, key, 'protocol', '已声明无法完成，但同时提供完成时间，请核对记录。'))
    return errors


def canonical_precision(values):
    # Only remove binary unit-conversion noise AFTER validation; not rounding raw data.
    return {key: round(value, 0 if key in BALANCE_KEYS + STATUS_KEYS else 1)
            for key, value in values.items()}


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError, __import__('csv').Error) as exc:
        return {}, [problem(manifest, '', 'file', f'无法读取测量文件：{exc}')]
    errors = [p for p in data.problems if p.kind != 'missing']
    if data.unmatched:
        errors.append(problem(manifest, '', 'unknown', '未识别的项目：' + '、'.join(data.unmatched) + '；请按输入说明核对。'))
    errors += validate(data.values, manifest, complete=not partial)
    if partial and not data.values and not errors:
        errors.append(problem(manifest, '', 'missing', '目标文件没有可用项目。'))
    return (canonical_precision(data.values) if not errors else data.values), errors


def scenario(values, manifest):
    errors = validate(values, manifest)
    if errors:
        return None, '；'.join(p.message_zh for p in errors)
    return assess(canonical_precision(values)), None


def levers(values, targets, manifest):
    current = assess(values)
    payload = {'schema': 'longevity-levers/1', 'model': 'sppb_8ft_1994',
               'model_zh': '原版 SPPB（8英尺）', 'current': current,
               'sensitivity': [], 'levers': [], 'note_zh': SCENARIO_NOTE}
    for key, value in values.items():
        spec = skillkit.spec_by_key(manifest, key)
        if key in STATUS_KEYS:
            step = 1 if value == 0 else -1
        else:
            step = 1 if key in BALANCE_KEYS else 0.1
            if value + step > spec['range'][1]:
                step = -step
        moved = {**values, key: round(value + step, 1)}
        result, reason = scenario(moved, manifest)
        delta = None if result is None else result['sppb_score'] - current['sppb_score']
        payload['sensitivity'].append({'key': key, 'label_zh': spec['label_zh'], 'unit': spec['unit'],
                                       'value': value, 'step': step, 'sppb_score_delta': delta,
                                       'score_per_unit': None if delta is None else delta / step,
                                       'unavailable_reason_zh': reason})
    for key, target in targets.items():
        result, reason = scenario({**values, key: target}, manifest)
        payload['levers'].append({'key': key, 'from': values.get(key), 'to': target,
                                  'unit': skillkit.spec_by_key(manifest, key)['unit'],
                                  'outputs': result,
                                  'sppb_score_delta': None if result is None else result['sppb_score'] - current['sppb_score'],
                                  'unavailable_reason_zh': reason})
    if targets:
        combined = assess({**values, **targets})  # Combined scenario validated by caller.
        payload['targets'] = {'values': targets, 'outputs': combined,
                              'sppb_score_delta': combined['sppb_score'] - current['sppb_score']}
    return payload


def add_card(text):
    title, *rest = text.splitlines()
    return '\n'.join([title, '', *paper_card_lines(), '', *rest]) + '\n'


def write_report(out, measurements, age=None, targets_path=None):
    out.mkdir(parents=True, exist_ok=True)
    for name in ('problems.json', 'result.json', 'levers.json'):
        (out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, errors = collect(measurements, manifest)
    errors += skillkit.check_scalar(manifest, 'age', age)
    targets = {}
    if targets_path is not None:
        targets, target_errors = collect(targets_path, manifest, partial=True)
        errors += target_errors
        if not errors:
            errors += validate({**values, **targets}, manifest)
    if errors:
        path = skillkit.write_problems(out, errors, TITLE, BOUNDARY)
        path.write_text(add_card(path.read_text(encoding='utf-8')), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = assess(values)
    rows = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
            '| 项目 | 得分 |', '|---|---:|']
    for spec in manifest['outputs']:
        rows.append(f"| {spec['label_zh']} | {result[spec['key']]} |")
    rows += ['', '三项各为 0–4 分，总分为 0–12 分；在相同方案下，分数越高表示本次测得的下肢体能越好。',
             '这不是生物年龄；本报告不套用其他研究的衰弱分界，也不把人群结局发生率当成你的概率。', '', '## 本次记录', '']
    for key, value in values.items():
        spec = skillkit.spec_by_key(manifest, key)
        display = ('确认无法完成或因安全原因未尝试' if value == 0 else '按方案完成') if key in STATUS_KEYS else f"{value:g} {spec['unit']}"
        rows.append(f"- {spec['label_zh']}：{display}")
    if values['walk_completed']:
        rows.append(f"- 两次 8 英尺步行取较快者：{min(values[k] for k in TIMED_TASKS['walk_completed']):g} 秒。")
    rows += ['', '平衡采用原表整秒记录，步行与起立采用原表 0.1 秒记录；没有自动舍入。'
             '平衡中的 0 秒可以表示确认无法完成或因安全原因未尝试，不能表示记录缺失。',
             '本方案起立计时从坐位开始，到第 5 次完全站直结束；三项成绩需要按同一标准流程测得。']
    if age is None:
        rows += ['未提供年龄，无法核对是否属于原研究的 71 岁及以上社区人群。']
    elif age < STUDY_MIN_AGE:
        rows += [f'你的年龄为 {age:g} 岁，低于原研究人群的年龄下限；分值仅按规则计算，不代表其风险关联适用于你。']
    else:
        rows += [f'你的年龄为 {age:g} 岁；评分不按年龄调整，原研究对象为社区老人。']
    payload = levers(values, targets, manifest)
    if targets:
        rows += ['', '## 目标情景', '', f"按目标记录重算，总分为 {payload['targets']['outputs']['sppb_score']}，"
                 f"相对本次变化 {payload['targets']['sppb_score_delta']:+d} 分。", SCENARIO_NOTE]
    rows += ['', f'边界: {BOUNDARY}']
    (out / 'report.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    skillkit.write_result(out, manifest, result)
    (out / 'levers.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', type=float)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    code = write_report(args.out, args.measurements, args.age, args.targets)
    print(args.out / 'report.md')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
