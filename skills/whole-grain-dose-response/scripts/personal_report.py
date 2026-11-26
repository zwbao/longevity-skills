#!/usr/bin/env python3
"""Match personal intake to printed points without reconstructing spline coefficients."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, INPUT_KEY, OUTCOMES, TABLES

TITLE = '全谷物摄入量与群体相对风险查表'


def lookup(value, outcome):
    rows = TABLES[outcome]
    result = {'reference_g_d': rows[0]['g_d'], 'status': 'outside_table', 'lower': None, 'upper': None}
    if value < rows[0]['g_d'] or value > rows[-1]['g_d']:
        return result
    lower = next(row for row in reversed(rows) if row['g_d'] <= value)
    upper = next(row for row in rows if row['g_d'] >= value)
    result.update(status='exact' if lower['g_d'] == upper['g_d'] else 'bracketed', lower=lower, upper=upper)
    return result


def output_values(value):
    output = {INPUT_KEY: value}
    for key in OUTCOMES:
        item = lookup(value, key)
        output[key + '_status'] = item['status']
        output[key + '_reference_g_d'] = item['reference_g_d']
        for side in ('lower', 'upper'):
            for field in ('g_d', 'rr', 'ci_low', 'ci_high'):
                output[f'{key}_{side}_{field}'] = item[side][field] if item[side] is not None else None
    return output


def exact_values(value):
    return {key: item['lower']['rr'] if item['status'] == 'exact' else None
            for key in OUTCOMES for item in [lookup(value, key)]}


def levers(value, target):
    current = exact_values(value)
    result = {'schema': 'longevity-levers/1', 'model': 'whole-grain-dose-response',
              'model_zh': TITLE, 'current': current, 'sensitivity': [], 'levers': [],
              'note_zh': '仅比较用户给定摄入量对应的原表群体相对风险。非精确表点或超出表范围时，单值及其差为 null；不插值、不计算导数，差值不是个人获益。'}
    result['current_lookup'] = {key: lookup(value, key) for key in OUTCOMES}
    if target is not None:
        wanted = exact_values(target)
        delta = {key + '_delta': wanted[key] - current[key] if wanted[key] is not None and current[key] is not None else None for key in OUTCOMES}
        result['targets'] = {'values': {INPUT_KEY: target}, **wanted, **delta}
        result['target_lookup'] = {key: lookup(target, key) for key in OUTCOMES}
        result['levers'] = [{'key': INPUT_KEY, 'label_zh': '全谷物食品摄入量', 'unit': 'g/d', 'from': value, 'to': target, **delta}]
    return result


def table_lines(value):
    lines = ['| 结局 | 表中参照量（g/日） | 匹配方式 | 原表摄入量（g/日） | 群体 RR（95% CI） |',
             '|---|---:|---|---:|---|']
    for key, label in OUTCOMES.items():
        item = lookup(value, key)
        if item['status'] == 'outside_table':
            lines.append(f'| {label} | {item["reference_g_d"]:g} | 超出该结局表值范围 | — | 未提供 |')
            continue
        rows = [item['lower']] if item['status'] == 'exact' else [item['lower'], item['upper']]
        for row in rows:
            ci = f'{row["ci_low"]:.2f}–{row["ci_high"]:.2f}' if row['ci_low'] is not None else '参照行未印区间'
            mode = '对应原表点' if item['status'] == 'exact' else '相邻原表点'
            lines.append(f'| {label} | {item["reference_g_d"]:g} | {mode} | {row["g_d"]:g} | {row["rr"]:.2f}（{ci}） |')
    return lines


def collect(path, manifest):
    try:
        return skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(INPUT_KEY, '全谷物食品摄入量', 'format', f'无法读取输入 CSV：{exc}')])


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age', type=float, help='可选上下文，不参与群体查表')
    parser.add_argument('--sex', help='可选上下文，不参与群体查表')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (args.out / name).unlink(missing_ok=True)
    found = collect(args.measurements, manifest)
    problems = list(found.problems)
    targets = collect(args.targets, manifest) if args.targets is not None else None
    if targets is not None:
        problems += [skillkit.Problem(p.key, p.label, p.kind, '目标文件：' + p.message_zh) for p in targets.problems]
    prefix = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 1)[1]
        path.write_text('\n'.join(prefix) + body, encoding='utf-8')
        skillkit.write_result(args.out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    value = found.values[INPUT_KEY]
    target = targets.values[INPUT_KEY] if targets is not None else None
    lines = prefix + ['## 你的输入', '', f'全谷物食品摄入量：{value:g} g/日。', '',
        '输入按论文多数研究的全谷物食品或产品重量口径理解，不是纯全谷物原料干重，也不是膳食纤维克数。原研究定义不完全一致，不能由产品重量统一换算为纯谷物干重。', '',
        '## 对应的群体关联', '',
        '表中 RR 是相对于各结局参照摄入量的群体相对风险，不是个人死亡概率。95% CI 描述群体关联估计的不确定性，不是个人预测区间。', '',
        '非原表点只列出摄入量两侧的原表行；这两行不是你的风险上下界。超出各结局已印范围时留空，不插值、不外推。', '', *table_lines(value), '',
        'S13 的前三项合并发病或死亡，癌症一项在正文对应癌症死亡；S14 各项均为死亡结局。不能把这些行相加或当作相互独立的风险。', '',
        '研究汇总前瞻性观察队列，主要全谷物证据来自美国与欧洲；残余混杂、食品定义差异和全因死亡分析的较高异质性限制了个人应用。年龄和性别不改变查表结果。']
    if target is not None:
        lines += ['', '## 你提供的目标情景', '', f'目标输入：{target:g} g/日，仅用于比较，并非推荐摄入量。', '', *table_lines(target), '',
                  '仅当当前和目标都落在同一结局的精确原表点时，levers.json 才提供 RR 差值；差值不表示改变饮食会使你的风险改变多少。']
    lines += ['', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, output_values(value))
    (args.out / 'levers.json').write_text(json.dumps(levers(value, target), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
