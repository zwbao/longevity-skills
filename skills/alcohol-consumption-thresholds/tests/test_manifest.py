"""Printed numerical example first; other cases test the input/output contract."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets
import personal_report as report


class TestManifest(unittest.TestCase):
    def test_paper_unit_example(self):
        # Methods p1513: "per 100 g per week of alcohol (12·5 units per week)".
        # Annex 1 p1: "1 unit=8 grams of ethanol". Exact arithmetic, not a fit.
        result = report.calculate(100, 1, 0)
        self.assertEqual(result['uk_units_per_week'], 12.5)
        self.assertEqual(result['reported_alcohol_g_week'], 100)
        self.assertEqual(presets.GRAMS_PER_UK_UNIT, 8)

    def test_manifest_units(self):
        manifest = json.loads((ROOT / 'skill.json').read_text())
        specs = {s['key']: s for s in manifest['inputs']}
        self.assertEqual(specs[presets.ALCOHOL_KEY]['unit'], presets.ALCOHOL_UNIT)
        self.assertEqual(specs[presets.ALCOHOL_KEY]['accept']['kg'], 1000)
        self.assertEqual(specs[presets.ALCOHOL_KEY]['range'], [0, 3500])

    def test_printed_category_boundaries(self):
        # Results p1520/Figure 4: >100–≤200 -> approx 6 months;
        # >200–≤350 -> 1–2 years; >350 -> 4–5 years.
        self.assertEqual(report.calculate(100, 1, 0)['consumption_band'], '>0–≤100 g/week')
        self.assertEqual(report.calculate(200, 1, 0)['study_loss_at_40'], '约6个月')
        self.assertEqual(report.calculate(350, 1, 0)['study_loss_at_40'], '约1–2年')
        self.assertEqual(report.calculate(351, 1, 0)['study_loss_at_40'], '约4–5年')
        self.assertIsNone(report.calculate(0, 0, 0)['study_loss_at_40'])
        self.assertIsNone(report.calculate(200, 1, 1)['study_loss_at_40'])

    def run_cli(self, alcohol='100', unit='g', extra=(), rows=None, out=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        csv = base / 'measurements.csv'
        csv.write_text(rows if rows is not None else
                       f'marker,value,unit\n每周纯酒精总量,{alcohol},{unit}\ncurrent_drinker,1,1\ncvd_history,0,1\n')
        out = out or base / 'out'
        p = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                            '--measurements', str(csv), '--out', str(out), *extra], capture_output=True, text=True)
        return p, out

    def test_normal_json_and_card(self):
        p, out = self.run_cli('0.1', 'kg')
        self.assertEqual(p.returncode, 0, p.stderr)
        outputs = json.loads((out / 'result.json').read_text())['outputs']
        self.assertEqual(outputs['uk_units_per_week']['value'], 12.5)
        text = (out / 'report.md').read_text()
        self.assertLess(text.index('论文卡片'), text.index('你的记录'))
        self.assertIn(presets.BOUNDARY, text)

    def test_bad_inputs_exit_three_without_results(self):
        for alcohol, unit in [('100', 'mL'), ('3501', 'g'), ('nan', 'g'), ('-1', 'g')]:
            with self.subTest(alcohol=alcohol, unit=unit):
                p, out = self.run_cli(alcohol, unit)
                self.assertEqual(p.returncode, 3, p.stderr)
                self.assertTrue((out / 'problems.json').exists())
                self.assertFalse((out / 'result.json').exists())
                self.assertNotIn('你的记录', (out / 'report.md').read_text())
        for rows in ['marker,value,unit\n', 'marker,value,unit\nalcohol_g_week,100,g\ncurrent_drinker,0.5,1\ncvd_history,0,1\n']:
            p, out = self.run_cli(rows=rows)
            self.assertEqual(p.returncode, 3, p.stderr)
            self.assertFalse((out / 'result.json').exists())

    def test_targets_and_stale_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'targets.csv'
            target.write_text('marker,value,unit\nalcohol_g_week,100,g\n')
            p, out = self.run_cli('200', extra=('--targets', str(target)))
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads((out / 'levers.json').read_text())
            self.assertEqual(data['targets']['outputs']['consumption_band'], '>0–≤100 g/week')
            self.assertEqual(data['levers'][0]['amount_delta_g'], -100)
            p, out = self.run_cli('100', 'mL', out=out)
            self.assertEqual(p.returncode, 3)
            self.assertFalse((out / 'result.json').exists())
            self.assertFalse((out / 'levers.json').exists())


if __name__ == '__main__':
    unittest.main()
