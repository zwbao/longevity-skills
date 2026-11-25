"""Printed inputs/outputs first: Supplementary Table 6 (MOESM3), not model-generated targets.

C92_002_s1 / SF3B1 p.K700E: Total depth 1671; Variant depth 134;
VAF 0.0801915020945541 (cells K2:M2).
C92_012_s5 / SRSF2 p.P95H: Total depth 1822; Variant depth 644;
VAF 0.3534577387486279. Threshold classification assertions below are separate
synthetic rule tests, not printed UK Biobank individual outcomes.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as pr
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


def run(tmp_path, rows, variant='SF3B1 p.K700E', extra=()):
    path = tmp_path / 'measurements.csv'
    path.write_text('item,value,unit\n' + '\n'.join(','.join(map(str, r)) for r in rows) + '\n')
    out = tmp_path / 'out'
    args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(path), '--out', str(out)]
    if variant is not None:
        args += ['--variant', variant]
    p = subprocess.run(args + list(extra), text=True, capture_output=True)
    result = json.loads((out / 'result.json').read_text())['outputs']
    return p, result, (out / 'report.md').read_text(), out


def test_paper_table6_vaf(tmp_path):
    p, result, report, _ = run(tmp_path, [('Total depth', 1671, '1'), ('Variant depth', 134, '1')])
    assert p.returncode == 0, p.stderr
    assert result['vaf_fraction']['value'] == pytest.approx(0.0801915020945541, abs=1e-15)
    assert '论文卡片' in report and '边界:' in report
    assert report.index('论文卡片') < report.index('本次记录')
    assert '10.1038/s41586-026-11269-x' in report


def test_paper_table6_high_vaf(tmp_path):
    p, result, _, _ = run(tmp_path, [('total_reads_count', 1822, '1'), ('variant_reads_count', 644, '1')], 'SRSF2 p.P95H')
    assert p.returncode == 0, p.stderr
    assert result['vaf_fraction']['value'] == pytest.approx(0.3534577387486279, abs=1e-15)


def test_manifest_units_and_presets():
    specs = {x['key']: x for x in MANIFEST['inputs']}
    for key, bounds in presets.COUNT_RANGES.items():
        assert specs[key]['unit'] == '1'
        assert specs[key]['range'] == list(bounds)
    assert presets.SWEEP_VAF_FRACTION == 0.30
    assert presets.MIN_VARIANT_READS == 3
    # Verify every printed grouped substitution, not all possible changes at a codon.
    assert presets.HOTSPOT_GROUPS['DNMT3A'] == ('R320*', 'R326C/G/S', 'R598*', 'R729G/W', 'Y735C/F', 'R736C/G/H/L/S', 'R771*', 'R882H/C/S/L/P', 'W860R', 'P904L/Q/R')
    assert presets.HOTSPOT_GROUPS['GNB1'] == ('K57E',)
    assert presets.HOTSPOT_GROUPS['IDH1'] == ('R132H',)
    assert presets.HOTSPOT_GROUPS['IDH2'] == ('R140Q', 'R172K')
    assert presets.HOTSPOT_GROUPS['JAK2'] == ('V617F',)
    assert presets.HOTSPOT_GROUPS['KIT'] == ('D816F/H/V/Y',)
    assert presets.HOTSPOT_GROUPS['KRAS'] == presets.HOTSPOT_GROUPS['NRAS'] == ('G12C/D/V',)
    assert presets.HOTSPOT_GROUPS['MPL'] == ('W515L',)
    assert presets.HOTSPOT_GROUPS['SF3B1'] == ('K666N', 'K700E')
    assert presets.HOTSPOT_GROUPS['SRSF2'] == ('P95H/L/R',)


@pytest.mark.parametrize('variant,total,alt,status', [
    ('SRSF2 p.P95H', 10, 3, 'below_or_equal_cutoff'),
    ('SRSF2 p.P95H', 100, 31, 'meets_screen'),
    ('SRSF2 p.P95H', 5, 2, 'insufficient_support'),
    ('SRSF2 p.P95H', 5, 3, 'meets_screen'),
    ('IDH1 p.R132C', 100, 50, 'outside_panel'),
    ('DNMT3A p.R320*', 100, 40, 'meets_screen'),
    ('DNMT3A p.R320X', 100, 40, 'meets_screen'),
])
def test_rule_boundaries(variant, total, alt, status):
    assert pr.readout(variant, total, alt)['screen_status'] == status


@pytest.mark.parametrize('rows,variant,extra', [
    ([('Total depth', 100, '%'), ('Variant depth', 40, '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 0, '1'), ('Variant depth', 0, '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 100, '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 100, '1'), ('Variant depth', 101, '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 100, '1'), ('Variant depth', 3.5, '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 100, '1'), ('Variant depth', 'nan', '1')], 'SF3B1 p.K700E', ()),
    ([('Total depth', 100, '1'), ('Variant depth', 40, '1')], None, ()),
    ([('Total depth', 100, '1'), ('Variant depth', 40, '1')], 'SF3B1', ()),
    ([('Total depth', 100, '1'), ('Variant depth', 40, '1')], 'SF3B1 p.K700E', ('--age', 'nan')),
    ([('Total depth', 100, '1'), ('Variant depth', 40, '1')], 'SF3B1 p.K700E', ('--sex', 'invalid')),
])
def test_input_problems(tmp_path, rows, variant, extra):
    p, result, report, out = run(tmp_path, rows, variant, extra)
    assert p.returncode == 3, p.stderr
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert all(x['value'] is None for x in result.values())
    assert '本次记录' not in report
    assert '论文卡片' in report and '边界:' in report


def test_reuse_output_does_not_leave_stale_results(tmp_path):
    good = [('总读段数', 100, '1'), ('突变支持读段数', 40, '1')]
    assert run(tmp_path, good)[0].returncode == 0
    _, result, _, _ = run(tmp_path, [('Total depth', 100, '1')])
    assert all(x['value'] is None for x in result.values())
    _, _, _, out = run(tmp_path, good)
    assert not (out / 'problems.json').exists()
