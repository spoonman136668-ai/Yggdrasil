"""MR34I11 source-free tests; original held/DEV source never acquired."""
from pathlib import Path
import sys
import unittest
import math

import numpy as np

original=Path(__file__).resolve().parents[3]/"original_s4c1"
if not original.is_dir():
    raise RuntimeError("MR34I11_ORIGINAL_PINNED_S4C1_CHECKOUT_REQUIRED")
sys.path.insert(0,str(original))

from research.mr34i11 import initial_u as q


class OriginalInitialUTests(unittest.TestCase):
    def test_frozen_original_source_scope(self):
        self.assertEqual(q.FIRST,"a12f477b12d74e7c383cb944318ea371fbef292f")
        self.assertEqual(q.PARENT,"1ab12be5dce0502c32c532ac32d095b2378dc82c")
        self.assertEqual(len(q.SEEDS),20)
        self.assertTrue(max(q.SEEDS)<2003)
        self.assertEqual(set(q.ORIGINAL_EVENT_SHA),set(q.SOURCES))
        self.assertEqual(q.SCHEMA,"mass.mr34i11.original-first-preaction-source-neutral-fsum.v1")

    def test_native_initial_fsum_exact_and_nonmutating(self):
        from research.nci04_s4c1.native_predictive_quotient import NativePredictiveQuotient45
        model=NativePredictiveQuotient45()
        before=model.snapshot()
        f=np.arange(56,dtype=np.float64).reshape(8,7)/90.
        got,read=q.exact_initial_from_public(f,model.g,model.roles)
        self.assertEqual(got.shape,(8,))
        self.assertEqual(read.shape,(8,))
        for i in range(8):
            self.assertEqual(float(got[i]),math.fsum(
                [float(f[i,j])*float(model.g[0,j]) for j in range(7)]+
                [float(model.roles[i,0])]))
        self.assertEqual(model.snapshot(),before)
        self.assertEqual(model.train_updates,0)

    def test_source_free_ieee_nonfinite_rejected(self):
        f=np.zeros((8,7),dtype=np.float64)
        g=np.zeros((3,7),dtype=np.float64)
        roles=np.zeros((8,3),dtype=np.float64)
        a,b=q.exact_initial_from_public(f,g,roles)
        self.assertTrue(np.array_equal(a,np.zeros(8)))
        self.assertTrue(np.array_equal(b,np.zeros(8)))
        mark=q.mark(np.array([0.,-0.,np.nextafter(1.,2.)]))
        self.assertNotEqual(mark["hex"][0],mark["hex"][1])
        self.assertEqual(len(mark["sha256"]),64)
        with self.assertRaises(ValueError):
            q.exact_initial_from_public(f[:7],g,roles)
        f[0,0]=np.nan
        with self.assertRaises(ValueError):
            q.exact_initial_from_public(f,g,roles)

    def test_no_source_roles_other_than_original_train(self):
        text=Path(q.__file__).read_text()
        self.assertIn("episodes(root,name,SEEDS)",text)
        self.assertIn("original.forward([rows[0]])",text)
        self.assertIn("exact_initial_from_public(",text)
        self.assertNotIn("episodes(root,name,EVAL)",text)
        self.assertNotIn("model.forward =",text)
        self.assertNotIn("model.g =",text)


if __name__=="__main__":
    unittest.main()
