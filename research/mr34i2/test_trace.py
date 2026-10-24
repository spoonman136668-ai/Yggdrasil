"""MR34I2 SOURCE-FREE engineering tests: no original source reset."""
import ast
import json
import unittest
from pathlib import Path

import numpy as np

from research.mr34i2 import trace_first_update as t
from research.mr34i1.train_only_numeric import SEEDS


class Dummy:
    def __init__(self):
        self.a=np.array([[.4,-.2]],dtype=np.float64)
        self.b=np.array([[.1,.3]],dtype=np.float64)
        self.train_updates=0
    def params(self):
        return self.a,self.b
    def analytic_bptt(self,ep):
        return np.array([[.2,-.1]],dtype=np.float64),np.array([[-.5,.25]],dtype=np.float64)
    def snapshot(self):
        return json.dumps({"params":[self.a.tolist(),self.b.tolist()],"updates":self.train_updates},sort_keys=True)


class MR34I2Tests(unittest.TestCase):
    def test_original_immutable_training_roles(self):
        self.assertEqual(len(SEEDS),20)
        self.assertEqual(t.FIRST,"1d867b52af3062096b3f4f8df3b4726b499b2dbf")
        self.assertEqual(set(t.WIN),set(t.LIN))
        self.assertTrue(all(len(rec[0])==64 for record in (t.WIN,t.LIN) for rec in record.values()))
        self.assertNotIn(2003,SEEDS)
        self.assertNotIn(2063,SEEDS)

    def test_first_adam_update_has_valid_original_persistent_receipt(self):
        m=Dummy()
        state_before=t.raw_params_digest(m)
        a=[np.zeros_like(p) for p in m.params()]
        b=[np.zeros_like(p) for p in m.params()]
        z=t.update_exact(m,[],a,b,1,.035,(.9,.999),1e-8,.0002,5.)
        self.assertEqual(m.train_updates,1)
        self.assertNotEqual(t.raw_params_digest(m),state_before)
        self.assertEqual(z["post_update_parameter_float64_sha256"],t.raw_params_digest(m))
        self.assertEqual(len(z["original_unregularized_gradient_sha256"]),2)
        for key in ("adam_first_moment_sha256","adam_second_moment_sha256"):
            self.assertEqual(len(z[key]),64)
        self.assertTrue(np.all(np.isfinite(m.a)))
        self.assertTrue(np.all(np.isfinite(m.b)))

    def test_restore_data_source_never_influences_ahead_of_time_training(self):
        src=ast.parse(Path(t.__file__).read_text())
        f=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=="trace_one")
        text=ast.unparse(f)
        self.assertIn("episodes(root, family, SEEDS)",text)
        self.assertIn("train_native(source_rows)",text)
        self.assertNotIn("EVAL",text)
        self.assertIn("source_gradient_finite_difference",text)
        self.assertEqual(t.SCHEMA,"mass.mr34i2.original-source-training-only-float-divergence.v1")


if __name__=="__main__":
    unittest.main()
