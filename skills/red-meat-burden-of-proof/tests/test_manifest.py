"""Expected values transcribed from Table 2 and Supplementary Table 7, not generated."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/personal_report.py'

# Table 2: rows ordered colorectal, breast, IHD, diabetes, ischemic and hemorrhagic stroke.
TABLE2 = {
    50: [(1.3, 1.01, 1.64), (1.26, 0.98, 1.56), (1.09, 0.99, 1.18),
         (1.14, 0.97, 1.32), (1.05, 0.97, 1.12), (0.9, 0.64, 1.26)],
    100: [(1.37, 1.01, 1.78), (1.26, 0.98, 1.56), (1.12, 0.99, 1.25),
          (1.23, 0.96, 1.52), (1.15, 0.93, 1.4), (0.87, 0.56, 1.35)],
}
KEYS = ['colorectal_cancer', 'breast_cancer', 'ischemic_heart_disease',
        'type_2_diabetes', 'ischemic_stroke', 'hemorrhagic_stroke']
# S7 pp.39–40: nine rows per outcome, intake 0,25,50,75,100,125,150,175,200 g/day.
# Each triple is the mean and conservative 95% UI (never the conventional UI).
S7 = {
 'colorectal_cancer': '1,1,1;1.28,1.01,1.58;1.3,1.01,1.64;1.34,1.01,1.71;1.37,1.01,1.78;1.4,1.02,1.86;1.43,1.02,1.94;1.47,1.02,2.02;1.5,1.02,2.1',
 'breast_cancer': '1,1,1;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56;1.26,0.98,1.56',
 'ischemic_heart_disease': '1,1,1.01;1.03,1,1.05;1.09,0.99,1.18;1.1,0.99,1.21;1.12,0.99,1.25;1.14,0.99,1.29;1.16,0.99,1.33;1.17,0.99,1.37;1.19,0.99,1.41',
 'type_2_diabetes': '1,1,1;1.06,0.99,1.14;1.14,0.97,1.32;1.19,0.96,1.42;1.23,0.96,1.52;1.27,0.95,1.62;1.31,0.94,1.72;1.35,0.94,1.83;1.39,0.93,1.94',
 'ischemic_stroke': '1.03,0.98,1.07;1,1,1.01;1.05,0.97,1.12;1.13,0.93,1.34;1.15,0.93,1.4;1.17,0.92,1.45;1.19,0.91,1.51;1.21,0.9,1.58;1.24,0.89,1.64',
 'hemorrhagic_stroke': '1,1,1;0.94,0.8,1.13;0.9,0.64,1.26;0.89,0.6,1.31;0.87,0.56,1.35;0.86,0.52,1.41;0.85,0.48,1.46;0.84,0.45,1.52;0.83,0.42,1.58',
}


class TestManifest(unittest.TestCase):
    def run_report(self, directory, value='50', unit='g/d', marker='未加工红肉摄入量',
                   age='50', sex='female', targets=None):
        base = Path(directory)
        path = base / 'measurements.csv'
        path.write_text('marker,value,unit\n' + (f'{marker},{value},{unit}\n' if value is not None else ''), encoding='utf-8')
        command = [sys.executable, str(SCRIPT), '--measurements', str(path), '--out', str(base / 'out')]
        if age is not None:
            command += ['--age', age]
        if sex is not None:
            command += ['--sex', sex]
        if targets is not None:
            target_path = base / 'targets.csv'
            target_path.write_text(targets, encoding='utf-8')
            command += ['--targets', str(target_path)]
        return subprocess.run(command, capture_output=True, text=True), base / 'out'

    def read_values(self, out):
        return {k: v['value'] for k, v in json.loads((out / 'result.json').read_text())['outputs'].items()}

    def test_table2_all_six_outcomes(self):
        for intake, expected in TABLE2.items():
            with self.subTest(intake=intake), tempfile.TemporaryDirectory() as d:
                run, out = self.run_report(d, str(intake))
                self.assertEqual(run.returncode, 0, run.stderr)
                values = self.read_values(out)
                for key, triple in zip(KEYS, expected):
                    self.assertEqual(tuple(values[key + s] for s in ['_rr', '_ui_lower', '_ui_upper']), triple)
                report = (out / 'report.md').read_text()
                self.assertLess(report.index('10.1038/s41591-022-01968-z'), report.index('你的摄入量'))
                self.assertIn('边界', report)
                self.assertIn('缺血性卒中', report)

    def test_supplementary_table7_all_printed_cells(self):
        for index, intake in enumerate([0, 25, 50, 75, 100, 125, 150, 175, 200]):
            with self.subTest(intake=intake), tempfile.TemporaryDirectory() as d:
                run, out = self.run_report(d, str(intake))
                self.assertEqual(run.returncode, 0, run.stderr)
                values = self.read_values(out)
                for key, rows in S7.items():
                    expected = tuple(map(float, rows.split(';')[index].split(',')))
                    self.assertEqual(tuple(values[key + s] for s in ['_rr', '_ui_lower', '_ui_upper']), expected)

    def test_manifest_matches_presets(self):
        spec = importlib.util.spec_from_file_location('redmeat_presets', ROOT / 'scripts/presets.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        manifest = json.loads((ROOT / 'skill.json').read_text())
        entry = next(x for x in manifest['inputs'] if x['from'] == 'measurements')
        self.assertEqual((entry['key'], entry['unit']), (module.INPUT_KEY, module.INPUT_UNIT))
        self.assertEqual(entry['range'], [module.GRID[0], module.GRID[-1]])
        self.assertEqual(set(module.TABLE), set(KEYS))

    def test_invalid_inputs_fail_without_stale_results(self):
        for kwargs in [dict(unit='kg'), dict(value='201'), dict(value='-1'), dict(value='75.5'),
                       dict(value=None), dict(value='nan'), dict(unit=''), dict(marker='processed meat'),
                       dict(age=None), dict(age='24'), dict(age='bad'), dict(sex='invalid'), dict(sex=None),
                       dict(targets='marker,value,unit\nunprocessed_red_meat_g_d,60,g/d\n')]:
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory() as d:
                self.assertEqual(self.run_report(d)[0].returncode, 0)
                run, out = self.run_report(d, **kwargs)
                self.assertEqual(run.returncode, 3, run.stderr)
                self.assertTrue(json.loads((out / 'problems.json').read_text())['problems'])
                self.assertFalse((out / 'result.json').exists())
                self.assertFalse((out / 'levers.json').exists())
                report = (out / 'report.md').read_text()
                self.assertIn('10.1038/s41591-022-01968-z', report)
                self.assertNotIn('| 结直肠癌 |', report)

    def test_targets_are_table_comparisons_not_continuous_slopes(self):
        with tempfile.TemporaryDirectory() as d:
            run, out = self.run_report(d, '100', targets='marker,value,unit\nunprocessed_red_meat_g_d,50,g/d\n')
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((out / 'levers.json').read_text())
            self.assertEqual(data['targets']['outputs']['colorectal_cancer_rr'], 1.3)
            self.assertAlmostEqual(data['levers'][0]['delta']['colorectal_cancer_rr'], 1.3 - 1.37)
            self.assertIsNone(data['sensitivity'][0]['derivative'])
            self.assertEqual(data['sensitivity'][0]['adjacent_table_rows'][0]['intake_g_d'], 75)
            self.assertEqual(data['sensitivity'][0]['adjacent_table_rows'][0]['outputs']['colorectal_cancer_rr'], 1.34)

    def test_male_breast_not_computed_and_english_alias(self):
        with tempfile.TemporaryDirectory() as d:
            run, out = self.run_report(d, marker='unprocessed red meat', sex='male')
            self.assertEqual(run.returncode, 0, run.stderr)
            values = self.read_values(out)
            self.assertIsNone(values['breast_cancer_rr'])
            self.assertEqual(values['colorectal_cancer_rr'], 1.3)


if __name__ == '__main__':
    unittest.main()
