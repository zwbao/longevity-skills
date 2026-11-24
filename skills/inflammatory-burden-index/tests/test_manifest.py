"""Printed threshold checks and engineering checks; no printed lab-to-IBI example exists.

Figure S4, p. 4: 'Low-IBI stratum (IBI < 1.496)' and
'High-IBI stratum (IBI ≥ 1.496)'. This verifies the boundary convention,
not an independent reproduction of the continuous IBI calculation.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets
from personal_report import stratum


def test_printed_threshold_convention():
    assert presets.IBI_THRESHOLD == 1.496
    assert stratum(1.496) == 'high'
    # Table 1 prints total IBI median 0.54; it is below the S4 threshold.
    assert stratum(0.54) == 'low'


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.out = self.base / 'out'

    def run_report(self, rows, targets=None):
        p = self.base / 'labs.csv'
        p.write_text('marker,value,unit\n' + rows, encoding='utf-8')
        cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
               '--measurements', str(p), '--out', str(self.out)]
        if targets is not None:
            t = self.base / 'targets.csv'
            t.write_text('marker,value,unit\n' + targets, encoding='utf-8')
            cmd += ['--targets', str(t)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_manifest_units(self):
        manifest = json.loads((ROOT / 'skill.json').read_text())
        self.assertEqual({x['key']: x['unit'] for x in manifest['inputs']
                          if x['from'] == 'measurements'}, presets.INPUT_UNITS)
        self.assertEqual(manifest['validation']['status'], 'draft')

    def test_printed_threshold(self):
        test_printed_threshold_convention()

    def test_formula_identity_and_converted_result(self):
        # Synthetic identity case, NOT a paper example: N/L=1 implies IBI=CRP.
        result = self.run_report('CRP,1.496,mg/L\nNEUT#,2,10^9/L\nLYM#,2,10^9/L\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        a = json.loads((self.out / 'result.json').read_text())['outputs']
        self.assertAlmostEqual(a['ibi_mg_l']['value'], 1.496)
        self.assertEqual(a['ibi_stratum']['value'], 'high')
        result = self.run_report('C反应蛋白,0.1496,mg/dL\n中性粒细胞绝对值,2000,/uL\n淋巴细胞计数,2,10^3/uL\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        b = json.loads((self.out / 'result.json').read_text())['outputs']
        self.assertAlmostEqual(a['ibi_mg_l']['value'], b['ibi_mg_l']['value'])
        report = (self.out / 'report.md').read_text()
        self.assertLess(report.index('论文卡片'), report.index('你的结果'))
        self.assertIn('边界', report)
        self.assertIn('仍在验证', report)

    def test_missing_wrong_units_ranges_and_stale_results(self):
        good = 'CRP,1.496,mg/L\nNEUT#,2,10^9/L\nLYM#,2,10^9/L\n'
        bad_rows = [good.replace('mg/L', 'mmol/L'), good.replace('1.496', '9999'),
                    good.replace('LYM#,2,10^9/L\n', ''),
                    good.replace('LYM#,2,', 'LYM#,0,'),
                    good.replace('mg/L', ''), good.replace('1.496', 'NaN'),
                    good.replace('1.496', '<0.1'),
                    good.replace('NEUT#,2,10^9/L', 'NEUT#,60,%')]
        for rows in bad_rows:
            with self.subTest(rows=rows):
                self.assertEqual(self.run_report(good).returncode, 0)
                result = self.run_report(rows)
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertTrue((self.out / 'problems.json').exists())
                self.assertFalse((self.out / 'result.json').exists())
                self.assertFalse((self.out / 'levers.json').exists())
                report = (self.out / 'report.md').read_text()
                self.assertIn('论文卡片', report)
                self.assertNotIn('你的结果', report)

    def test_targets_match_direct_calculation(self):
        rows = 'CRP,1.496,mg/L\nNEUT#,2,10^9/L\nLYM#,2,10^9/L\n'
        run = self.run_report(rows, 'CRP,0.54,mg/L\n')
        self.assertEqual(run.returncode, 0, run.stderr)
        levers = json.loads((self.out / 'levers.json').read_text())
        # Identity case again; 0.54 is not claimed as a printed worked output.
        self.assertAlmostEqual(levers['targets']['ibi_mg_l'], 0.54)
        self.assertEqual(levers['targets']['ibi_stratum'], 'low')
        self.assertEqual(len(levers['sensitivity']), len(presets.INPUT_UNITS))
        self.assertEqual(len(levers['levers']), 1)
        for bad in ['LYM#,0,10^9/L\n', 'unknown,2,mg/L\n', 'CRP,2,\n']:
            self.assertEqual(self.run_report(rows, bad).returncode, 3)


if __name__ == '__main__':
    unittest.main()
