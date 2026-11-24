"""Expected scores and risks transcribed from Kivipelto 2006, Tables 2–4.
Table 4 supplies categories, not exact measurements. Representative raw values
below merely select those printed categories; expected outcomes are printed.
"""
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


class TestManifest(unittest.TestCase):
    def test_table4_printed_examples(self):
        # Table 4 column order: low M1/M2, intermediate M1/M2, high M1/M2.
        # Printed score=0 score=0 score=10 score=10 score=15 score=18.
        # Printed risks: 0·13%, 0·09%, 6·91%, 4·06%, 35·55%, 48·93%.
        profiles = [
            dict(age=46, education_years=10, sex='female', sbp_mmhg=140,
                 bmi_kg_m2=30, total_cholesterol_mmol_l=6.5, physical_active_1=1, apoe_e4_1=0),
            dict(age=47, education_years=7, sex='female', sbp_mmhg=141,
                 bmi_kg_m2=30, total_cholesterol_mmol_l=6.6, physical_active_1=0, apoe_e4_1=0),
            dict(age=54, education_years=6, sex='male', sbp_mmhg=141,
                 bmi_kg_m2=31, total_cholesterol_mmol_l=6.6, physical_active_1=0, apoe_e4_1=1),
        ]
        expected = [(0, 0.13), (0, 0.09), (10, 6.91), (10, 4.06), (15, 35.55), (18, 48.93)]
        for i, profile in enumerate(profiles):
            for j, model in enumerate(('basic', 'apoe')):
                result = report.calculate(profile, model)
                score, risk = expected[2*i+j]
                self.assertEqual(result['score'], score)
                # Table 4 rounds to two decimals in percent: half a last digit.
                self.assertAlmostEqual(result['model_risk_20y_pct'], risk, delta=0.005)

    def test_table3_printed_groups(self):
        for model, rows in {
            'basic': [(0,5,1.0),(6,7,1.9),(8,9,4.2),(10,11,7.4),(12,15,16.4)],
            'apoe': [(0,5,0.3),(6,8,1.7),(9,10,4.6),(11,12,4.4),(13,18,16.3)],
        }.items():
            for low, high, risk in rows:
                for score in range(low, high+1):
                    self.assertEqual(report.group_for_score(score, model)['risk_pct'], risk)

    def run_cli(self, rows=None, extra=(), targets=None):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(__import__('shutil').rmtree, folder)
        path = folder / 'measurements.csv'
        path.write_text('marker,value,unit\n' + (rows if rows is not None else
            'education_years,7,a\nsbp_mmhg,141,mmHg\nbmi_kg_m2,30,kg/m^2\n'
            'total_cholesterol_mmol_l,6.6,mmol/L\nphysical_active_1,0,1\n'))
        args = [sys.executable, str(ROOT/'scripts/personal_report.py'), '--measurements', str(path),
                '--age','47','--sex','female','--out',str(folder/'out'), *extra]
        if targets is not None:
            t = folder/'targets.csv'; t.write_text('marker,value,unit\n'+targets)
            args += ['--targets',str(t)]
        p = subprocess.run(args, capture_output=True, text=True)
        return p, folder/'out'

    def test_manifest_units_and_success(self):
        manifest = json.loads((ROOT/'skill.json').read_text())
        self.assertEqual({i['key']:i.get('unit') for i in manifest['inputs']}, presets.INPUT_UNITS)
        p, out = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads((out/'result.json').read_text())['outputs']
        self.assertEqual(r['score']['value'], 10)
        self.assertAlmostEqual(r['model_risk_20y_pct']['value'], 6.91, delta=0.005)
        self.assertEqual(r['group_risk_pct']['value'], 7.4)
        text = (out/'report.md').read_text()
        self.assertIn('边界', text)
        self.assertLess(text.index('10.1016'), text.index('你的结果'))

    def test_bad_inputs_exit_three(self):
        base = ('education_years,7,a\nsbp_mmhg,141,mmHg\nbmi_kg_m2,30,kg/m^2\n'
                'total_cholesterol_mmol_l,6.6,mmol/L\nphysical_active_1,0,1\n')
        cases = [base.replace('141,mmHg','141,mg/L'), base.replace('141,mmHg','800,mmHg'),
                 base.replace('physical_active_1,0,1\n',''), base.replace('active_1,0,1','active_1,0.5,1'),
                 base.replace('years,7,a','years,7.5,a')]
        for rows in cases:
            p,out = self.run_cli(rows)
            self.assertEqual(p.returncode,3,p.stderr)
            self.assertTrue((out/'problems.json').exists())
            self.assertFalse((out/'result.json').exists())
            self.assertNotIn('你的结果',(out/'report.md').read_text())

    def test_apoe_missing_and_outside_population(self):
        for extra in [('--model','apoe'),('--age','70'),('--age','nan'),('--sex','unknown')]:
            p,out = self.run_cli(extra=extra)
            self.assertEqual(p.returncode,3,p.stderr)
            self.assertTrue((out/'problems.json').exists())

    def test_units_and_targets(self):
        rows = ('受教育年限,7,年\n收缩压,141,mmHg\nBMI,30,kg/m²\n'
                'TC,6600,umol/L\n身体活动达标,0,1\n')
        p,out = self.run_cli(rows, targets='收缩压,140,mmHg\nTC,6.5,mmol/L\n身体活动达标,1,1\n')
        self.assertEqual(p.returncode,0,p.stderr)
        data=json.loads((out/'levers.json').read_text())
        self.assertEqual(data['current']['score'],10)
        # Each target crosses a printed Table 2 term: 2, 2, 1 points.
        self.assertEqual([x['delta_score'] for x in data['levers']],[-2,-2,-1])
        self.assertEqual(len(data['sensitivity']),7)
        p,out=self.run_cli(targets='education_years,10,a\n')
        self.assertEqual(p.returncode,3,p.stderr)

    def test_table2_cutoffs(self):
        v=dict(age=47,education_years=7,sex='female',sbp_mmhg=140,bmi_kg_m2=30,
               total_cholesterol_mmol_l=6.5,physical_active_1=1,apoe_e4_1=0)
        terms=report.term_scores(v,'basic')
        self.assertEqual(terms,dict(age=3,education_years=2,sex=0,sbp_mmhg=0,bmi_kg_m2=0,
                                    total_cholesterol_mmol_l=0,physical_active_1=0))
        for key in ['sbp_mmhg','bmi_kg_m2','total_cholesterol_mmol_l']:
            self.assertEqual(report.term_scores(dict(v,**{key:v[key]+0.001}),'basic')[key],2)
        self.assertEqual(report.term_scores(dict(v,age=53),'basic')['age'],3)


if __name__=='__main__':
    unittest.main()
