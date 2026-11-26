"""Behavioural checks for input rejection, published-grid boundaries, and targets."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report

BASE = 'marker,value,unit\nlight_min_week,0,min\nmoderate_min_week,150,min\nvigorous_min_week,0,min\n'


class ReportTests(unittest.TestCase):
    def run_cli(self, directory, targets=None, age='50', data=BASE):
        p = Path(directory)
        (p / 'input.csv').write_text(data)
        args = [sys.executable, str(ROOT / 'scripts/personal_report.py'), '--measurements', str(p / 'input.csv'), '--out', str(p / 'out')]
        if age is not None:
            args += ['--age', age]
        if targets is not None:
            (p / 'targets.csv').write_text(targets)
            args += ['--targets', str(p / 'targets.csv')]
        return subprocess.run(args, capture_output=True, text=True)

    def test_targets_and_single_input_changes(self):
        with tempfile.TemporaryDirectory() as d:
            target = 'marker,value,unit\nmoderate_min_week,300,min\n'
            p = self.run_cli(d, target)
            self.assertEqual(p.returncode, 0, p.stderr)
            lever = json.loads((Path(d) / 'out/levers.json').read_text())
            # Table 1: at 17.5 mMET-hours/week, all-cause RR 0.66 (0.62 to 0.70).
            self.assertEqual(lever['targets']['outputs']['activity_mmet_h_week'], 17.5)
            self.assertAlmostEqual(lever['targets']['outputs']['all_cause_mortality_rr'], 0.66, delta=0.005)
            self.assertAlmostEqual(lever['targets']['outputs']['all_cause_mortality_ci_lower'], 0.62, delta=0.005)
            self.assertAlmostEqual(lever['targets']['outputs']['all_cause_mortality_ci_upper'], 0.70, delta=0.005)
            self.assertEqual(lever['levers'][0]['outputs'], lever['targets']['outputs'])
            self.assertEqual(len(lever['sensitivity']), 3)
            for item in lever['sensitivity']:
                self.assertEqual(item['method'], 'adjacent_grid_secant')
                self.assertLess(item['rr_per_unit']['all_cause_mortality'], 0)
            text = (Path(d) / 'out/report.md').read_text()
            self.assertIn('不是个体因果获益', text)

    def test_bad_targets_and_ages_clear_old_results(self):
        with tempfile.TemporaryDirectory() as d:
            for target, age in [
                ('marker,value,unit\nmoderate_min_week,200,steps\n', '50'),
                ('marker,value,unit\nmoderate_min_week,-1,min\n', '50'),
                ('marker,value,unit\nmoderate_min_week,inf,min\n', '50'),
                ('marker,value,unit\nunknown,200,min\n', '50'),
                ('marker,value,unit\n', '50'),
                ('marker,value,unit\nmoderate_min_week,200,min\nmoderate_min_week,201,min\n', '50'),
                (None, None), (None, '17'), (None, 'nan'), (None, 'abc')]:
                self.assertEqual(self.run_cli(d).returncode, 0)
                p = self.run_cli(d, target, age)
                self.assertEqual(p.returncode, 3, p.stderr)
                out = Path(d) / 'out'
                self.assertTrue((out / 'problems.json').exists())
                self.assertFalse((out / 'result.json').exists())
                self.assertFalse((out / 'levers.json').exists())
                text = (out / 'report.md').read_text()
                self.assertIn('论文卡片', text)
                self.assertIn('这次没有计算', text)

    def test_zero_and_no_extrapolation(self):
        for key in report.OUTCOMES:
            row = report.lookup(key, 0)
            self.assertEqual((row['dose'], row['RR'], row['lb'], row['ub']), (0, 1, 1, 1))
            end = report.curve(key)[-1]['dose']
            self.assertIsNotNone(report.lookup(key, end))
            self.assertIsNone(report.lookup(key, end + 0.001))
        # Released bladder curve ends at 33.25; 35 is outside it but inside all-cause.
        result = report.calculate({'light_min_week': 0, 'moderate_min_week': 600, 'vigorous_min_week': 0})
        self.assertIsNone(result['bladder_incidence_rr'])
        self.assertIsNotNone(result['all_cause_mortality_rr'])
        self.assertIsNone(report.lookup('all_cause_mortality', -1))

    def test_nearest_grid_not_interpolation(self):
        rows = report.curve('all_cause_mortality')
        query = rows[80]['dose'] + (rows[81]['dose'] - rows[80]['dose']) / 4
        self.assertEqual(report.lookup('all_cause_mortality', query), rows[80])

    def test_impossible_duration_and_unavailable_volume(self):
        with tempfile.TemporaryDirectory() as d:
            for data in [BASE.replace('moderate_min_week,150', 'moderate_min_week,10081'),
                         BASE.replace('moderate_min_week,150', 'moderate_min_week,10000').replace('light_min_week,0', 'light_min_week,100'),
                         BASE.replace('moderate_min_week,150', 'moderate_min_week,0').replace('vigorous_min_week,0', 'vigorous_min_week,10080')]:
                self.assertEqual(self.run_cli(d, data=data).returncode, 3)


if __name__ == '__main__':
    unittest.main()
