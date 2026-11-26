"""Printed endpoints first: Yuan et al. Nutrients 2017, Table 3 and §3.1.3.

These reproduce printed per-component input/output pairs, not an invented
participant total or the CHNS population mean. Alcohol follows the explicit
prose, because Table 3's alcohol row reverses the two score columns.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
from presets import INPUTS, COMPONENTS

# Table 3, columns Score 0 / 5 / 10; inputs in SP/1000 kcal except
# oils (g/1000 kcal), sodium (mg/1000 kcal), sugar (% energy).
PRINTED = [
    ('total_grains', 0, 0, 2.5, 5),
    ('whole_grains_mixed_beans', 0, 0, 0.6, 5),
    ('tubers', 0, 0, 0.3, 5),
    ('total_vegetables', 0, 0, 1.9, 5),
    ('dark_vegetables', 0, 0, 0.9, 5),
    ('fruits', 0, 0, 1.1, 10),
    ('dairy', 0, 0, 0.5, 5),
    ('soybeans', 0, 0, 0.4, 5),
    ('fish_seafood', 0, 0, 0.6, 5),
    ('poultry', 0, 0, 0.3, 5),
    ('eggs', 0, 0, 0.5, 5),
    ('seeds_nuts', 0, 0, 0.4, 5),
    ('red_meat', 3.5, 0, 0.4, 5),
    ('cooking_oils', 32.6, 0, 15.6, 10),
    ('sodium', 3608, 0, 1000, 10),
    ('added_sugars', 20, 0, 10, 5),
]


def test_table3_printed_component_scores():
    for key, zero_input, zero_score, full_input, full_score in PRINTED:
        assert report.score_item(key, zero_input) == zero_score
        assert report.score_item(key, full_input) == full_score


def test_section313_printed_alcohol_scores():
    # §3.1.3: 25/15 g per day -> 5; 60/40 g per day -> zero.
    for sex, full, zero in [('male', 25, 60), ('female', 15, 40)]:
        assert report.score_item('alcohol', full, 18, sex, False) == 5
        assert report.score_item('alcohol', zero, 18, sex, False) == 0
    # Same paragraph: no alcohol -> 5; any alcohol -> zero for minors,
    # pregnant and lactating women. Positive intake below is a boundary probe.
    for age, sex, pregnant in [(17, 'male', False), (18, 'female', True)]:
        assert report.score_item('alcohol', 0, age, sex, pregnant) == 5
        assert report.score_item('alcohol', 0.001, age, sex, pregnant) == 0


def values_at_printed_endpoints():
    values = {COMPONENTS[k]['input']: full for k, _, _, full, _ in PRINTED}
    # Daily inputs at 1000 kcal: SP and oil densities equal daily amounts.
    values['sodium_g_d'] = 1000 / 1000
    values.update(energy_kcal_d=1000, alcohol_g_d=25, pregnant_lactating_yes=0)
    return values


def csv_file(path, values, overrides=None):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['marker', 'value', 'unit'])
        for key, value in values.items():
            w.writerow([key, value, (overrides or {}).get(key, INPUTS[key]['unit'])])
    return path


def run(tmp_path, values=None, extra=(), overrides=None, profile=('--age', '18', '--sex', 'male')):
    path = csv_file(tmp_path / 'intake.csv', values if values is not None else values_at_printed_endpoints(), overrides)
    out = tmp_path / 'out'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                             '--intake', str(path), '--out', str(out), *profile, *extra],
                            capture_output=True, text=True)
    return result, out


def test_manifest_and_presets_agree():
    manifest = json.loads((ROOT / 'skill.json').read_text())
    specs = {s['key']: s for s in manifest['inputs'] if s['from'] == 'measurements'}
    assert specs.keys() == INPUTS.keys()
    for key, spec in specs.items():
        assert spec['unit'] == INPUTS[key]['unit']
        assert spec['range'] == INPUTS[key]['range']
    assert {s['key'] for s in manifest['outputs']} == {'chei_total', *[k + '_score' for k in COMPONENTS]}


def test_cli_printed_scores_and_sum(tmp_path):
    p, out = run(tmp_path)
    assert p.returncode == 0, p.stderr
    outputs = json.loads((out / 'result.json').read_text())['outputs']
    for key, _, _, _, full in PRINTED:
        assert outputs[key + '_score']['value'] == full
    assert outputs['alcohol_score']['value'] == 5
    # §3.1.2 prints maximum total score 100; no personal example is claimed.
    assert outputs['chei_total']['value'] == 100
    text = (out / 'report.md').read_text()
    assert text.index('论文卡片') < text.index('你的结果')
    assert '边界' in text and '10.3390/nu9090977' in text
    assert '不代表安全饮酒量' in text
    assert len(json.loads((out / 'levers.json').read_text())['sensitivity']) == 18


@pytest.mark.parametrize('key,value,unit', [
    ('sodium_g_d', 1000, 'mg/dL'), ('sodium_g_d', -1, 'g/d'),
    ('energy_kcal_d', 0, '1'), ('energy_kcal_d', 'NaN', '1'),
    ('dairy_sp_d', 1, 'g'), ('pregnant_lactating_yes', 0.5, '1'),
    ('dark_vegetables_sp_d', 20, '1'),
])
def test_bad_input_exits_three(tmp_path, key, value, unit):
    values = values_at_printed_endpoints()
    values[key] = value
    p, out = run(tmp_path, values, overrides={key: unit})
    assert p.returncode == 3, p.stderr
    assert (out / 'problems.json').exists()
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
    text = (out / 'report.md').read_text()
    assert '论文卡片' in text and '这次没有计算' in text


def test_missing_is_not_zero(tmp_path):
    values = values_at_printed_endpoints()
    del values['fruits_sp_d']
    p, out = run(tmp_path, values)
    assert p.returncode == 3
    assert any(x['key'] == 'fruits_sp_d' and x['kind'] == 'missing'
               for x in json.loads((out / 'problems.json').read_text())['problems'])


@pytest.mark.parametrize('profile', [(), ('--age', '1', '--sex', 'male'),
    ('--age', 'abc', '--sex', 'male'), ('--age', '18', '--sex', 'unknown')])
def test_invalid_profile(tmp_path, profile):
    p, out = run(tmp_path, profile=profile)
    assert p.returncode == 3
    assert not (out / 'result.json').exists()


def test_energy_density_and_linear_interpolation():
    v = values_at_printed_endpoints()
    initial = report.score(v, 18, 'male')
    doubled = {k: x * 2 if k.endswith('_sp_d') or k in ('energy_kcal_d', 'cooking_oils_g_d', 'sodium_g_d') else x for k, x in v.items()}
    assert report.score(doubled, 18, 'male') == initial
    for key, zero, s0, full, s1 in PRINTED:
        assert report.score_item(key, (zero + full) / 2) == pytest.approx((s0 + s1) / 2)


def test_targets_and_fraction_conversion(tmp_path):
    targets = csv_file(tmp_path / 'targets.csv', {'added_sugars_energy_pct': 0.2}, {'added_sugars_energy_pct': '1'})
    p, out = run(tmp_path, extra=['--targets', str(targets)])
    assert p.returncode == 0, p.stderr
    levers = json.loads((out / 'levers.json').read_text())
    # Table 3 sugar: at 20% -> 0; at 10% -> 5.
    assert levers['levers'][0]['to'] == 20
    assert levers['levers'][0]['chei_total_delta'] == 0 - 5
    assert levers['targets']['chei_total'] == levers['current']['chei_total'] - 5


def test_failed_rerun_removes_stale_results(tmp_path):
    p, out = run(tmp_path)
    assert p.returncode == 0
    targets = csv_file(tmp_path / 'targets.csv', {'sodium_g_d': -1})
    p, out = run(tmp_path, extra=['--targets', str(targets)])
    assert p.returncode == 3
    assert not (out / 'result.json').exists()
    assert not (out / 'levers.json').exists()
