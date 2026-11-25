"""Printed expectations: Rikli & Jones 2013, Table 4 and pp. 262–263."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets


class ManifestTests(unittest.TestCase):
    def test_printed_example(self):
        # pp. 262–263: male age 73, chair 19, curl 18, walk 500 yards.
        # Printed interpretation: strength items met, aerobic endurance not met.
        got = report.evaluate(73, 'male', {
            'chair_stand_count': 19, 'arm_curl_count': 18,
            'walk_6min_m': 500 * 0.9144,
        })
        self.assertEqual(got['chair_stand_status'], 'meets_standard')
        self.assertEqual(got['arm_curl_status'], 'meets_standard')
        self.assertEqual(got['walk_6min_status'], 'below_standard')
        # Table 4, Men, age 70–74: 15, 17, 620, 95, 5.5.
        self.assertEqual(got['chair_stand_cutoff'], 15)
        self.assertEqual(got['arm_curl_cutoff'], 17)
        self.assertAlmostEqual(got['walk_6min_cutoff'] / 0.9144, 620)
        self.assertEqual(got['step_2min_cutoff'], 95)
        self.assertEqual(got['up_go_cutoff'], 5.5)
        self.assertIsNone(got['step_2min_status'])
        self.assertIsNone(got['up_go_status'])

    def test_all_printed_cutoffs(self):
        # Table 4, seven columns in order 60–64 ... 90–94; no fitted constants.
        expected = {
            'female': [
                [15, 15, 14, 13, 12, 11, 9],
                [17, 17, 16, 15, 14, 13, 11],
                [625, 605, 580, 550, 510, 460, 400],
                [97, 93, 89, 84, 78, 70, 60],
                [5.0, 5.3, 5.6, 6.0, 6.5, 7.1, 8.0],
            ],
            'male': [
                [17, 16, 15, 14, 13, 11, 9],
                [19, 18, 17, 16, 15, 13, 11],
                [680, 650, 620, 580, 530, 470, 400],
                [106, 101, 95, 88, 80, 71, 60],
                [4.8, 5.1, 5.5, 5.9, 6.4, 7.1, 8.0],
            ],
        }
        for sex, rows in expected.items():
            for index, age in enumerate([60, 65, 70, 75, 80, 85, 90]):
                for edge in (age, age + 4):
                    got = report.evaluate(edge, sex, {})
                    for metric, row in zip(presets.METRICS, rows):
                        value = got[metric['output'] + '_cutoff']
                        if metric['key'] == 'walk_6min_m':
                            value /= 0.9144
                        self.assertAlmostEqual(value, row[index])

    def run_cli(self, directory, rows, age='73', sex='male', targets=None):
        source = directory / 'measurements.csv'
        source.write_text('marker,value,unit\n' + rows, encoding='utf-8')
        args = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
                '--measurements', str(source), '--out', str(directory / 'out')]
        if age is not None:
            args += ['--age', age]
        if sex is not None:
            args += ['--sex', sex]
        if targets is not None:
            target_file = directory / 'targets.csv'
            target_file.write_text('marker,value,unit\n' + targets, encoding='utf-8')
            args += ['--targets', str(target_file)]
        return subprocess.run(args, text=True, capture_output=True)

    def test_manifest_units_and_normal_result(self):
        manifest = json.loads((ROOT / 'skill.json').read_text())
        specs = {s['key']: s for s in manifest['inputs']}
        for metric in presets.METRICS:
            self.assertEqual(specs[metric['key']]['unit'], metric['unit'])
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            p = self.run_cli(d, '30-s chair stand,19,1\n30-s arm curl,18,1\n6-min walk,45720,cm\n')
            self.assertEqual(p.returncode, 0, p.stderr)
            output = json.loads((d / 'out/result.json').read_text())['outputs']
            self.assertEqual(output['chair_stand_cutoff']['value'], 15)
            self.assertEqual(output['walk_6min_status']['value'], 'below_standard')
            text = (d / 'out/report.md').read_text()
            self.assertLess(text.index('论文卡片'), text.index('你的结果'))
            self.assertIn('边界', text)

    def test_bad_inputs_and_stale_results(self):
        for rows, age, sex in [
            ('walk_6min_m,500,kg\n', '73', 'male'),
            ('walk_6min_m,20000,m\n', '73', 'male'),
            ('chair_stand_count,19.5,1\n', '73', 'male'),
            ('chair_stand_count,NaN,1\n', '73', 'male'),
            ('', '73', 'male'),
            ('chair_stand_count,19,1\n', None, 'male'),
            ('chair_stand_count,19,1\n', '59', 'male'),
            ('chair_stand_count,19,1\n', '95', 'male'),
            ('chair_stand_count,19,1\n', '73.5', 'male'),
            ('chair_stand_count,19,1\n', 'abc', 'male'),
            ('chair_stand_count,19,1\n', '73', None),
            ('chair_stand_count,19,1\n', '73', 'unknown'),
            ('6-min walk,500,\n', '73', 'male'),
            ('unrecognized,19,1\n', '73', 'male'),
        ]:
            with self.subTest(rows=rows, age=age, sex=sex), tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                self.assertEqual(self.run_cli(d, 'chair_stand_count,19,1\n').returncode, 0)
                p = self.run_cli(d, rows, age, sex)
                self.assertEqual(p.returncode, 3, p.stderr)
                self.assertTrue((d / 'out/problems.json').exists())
                self.assertFalse((d / 'out/result.json').exists())
                self.assertFalse((d / 'out/levers.json').exists())
                text = (d / 'out/report.md').read_text()
                self.assertIn('论文卡片', text)
                self.assertNotIn('你的结果', text)

    def test_boundaries_and_targets(self):
        # Table 4, male age 90–94: 9 stands, up-and-go 8.0 seconds.
        got = report.evaluate(94, 'male', {'chair_stand_count': 9, 'up_go_s': 8.0})
        self.assertEqual(got['chair_stand_status'], 'meets_standard')
        self.assertEqual(got['up_go_status'], 'meets_standard')
        got = report.evaluate(94, 'male', {'up_go_s': 8.1})
        self.assertEqual(got['up_go_status'], 'below_standard')
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            p = self.run_cli(d, 'walk_6min_m,457.2,m\n', targets='walk_6min_m,566.928,m\n')
            self.assertEqual(p.returncode, 0, p.stderr)
            levers = json.loads((d / 'out/levers.json').read_text())
            self.assertEqual(levers['targets']['outputs']['walk_6min_status'], 'meets_standard')
            self.assertEqual(levers['levers'][0]['outputs']['walk_6min_status'], 'meets_standard')
            p = self.run_cli(d, 'walk_6min_m,457.2,m\n', targets='arm_curl_count,18,1\n')
            self.assertEqual(p.returncode, 3)
            self.assertFalse((d / 'out/result.json').exists())


if __name__ == '__main__':
    unittest.main()
