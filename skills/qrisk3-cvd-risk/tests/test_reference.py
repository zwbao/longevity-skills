"""Python/C parity is engineering verification, not paper-example reproduction."""
import ctypes
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import presets


@unittest.skipUnless(shutil.which('cc'), 'C compiler required for source parity check')
class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        src = (ROOT/'references/qrisk3-2017.c').read_text()
        path = Path(cls.tmp.name)/'reference.c'
        path.write_text('#include <math.h>\n'+src.replace('static double', 'double'))
        lib = Path(cls.tmp.name)/'reference.so'
        subprocess.run(['cc','-shared','-fPIC','-O0',str(path),'-lm','-o',str(lib)],check=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.params = {}
        for name, args in re.findall(r'static double (\w+)\(\s*(.*?)\s*\)', src, re.S):
            parts = [p.strip().split() for p in args.split(',')]
            fn = getattr(cls.lib, name)
            fn.argtypes = [ctypes.c_int if t=='int' else ctypes.c_double for t,k in parts]
            fn.restype = ctypes.c_double
            cls.params[name] = parts

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_frozen_source_hash(self):
        manifest = json.loads((ROOT/'skill.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/'references/qrisk3-2017.c').read_bytes()).hexdigest(),
                         manifest['data_files'][0]['sha256'])

    def test_python_matches_published_c_both_sexes_and_categories(self):
        rng = random.Random(2099)
        for sex in ('female','male'):
            name = 'cvd_'+sex+'_raw'
            for age in (25,44,60,84):
                for eth in range(1,10):
                    for smoke in range(5):
                        v = {k:rng.randrange(2) for k in presets.BINARY_KEYS}
                        v['b_type2'] = 0 if v['b_type1'] else v['b_type2']
                        v.update(bmi_kg_m2=rng.uniform(18,40),tc_hdl_ratio=rng.uniform(2,8),
                                 sbp_mmhg=rng.uniform(90,200),sbp_sd_mmhg=rng.uniform(0,40),
                                 townsend_score=rng.uniform(-6,10),ethnicity=eth,smoking=smoke)
                        args = dict(v, age=age,bmi=v['bmi_kg_m2'],rati=v['tc_hdl_ratio'],
                                    sbp=v['sbp_mmhg'],sbps5=v['sbp_sd_mmhg'],town=v['townsend_score'],
                                    smoke_cat=smoke,ethrisk=eth,surv=10)
                        expected = getattr(self.lib,name)(*[args[k] for t,k in self.params[name]])
                        self.assertAlmostEqual(presets.risk(age,sex,v),expected,delta=1e-11)

if __name__ == '__main__':
    unittest.main()
