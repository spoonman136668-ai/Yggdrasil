"""MR34I10 source-free exact finite source/arch tests. Never read original heldout."""
import math
from pathlib import Path
import random
import sys
import unittest

import numpy as np

# Original S4C1 native runtime remains in its separately pinned read-only checkout.
original=Path(__file__).resolve().parents[3]/"original_s4c1"
if not original.is_dir():
    raise RuntimeError("MR34I10_PINNED_ORIGINAL_S4C1_CHECKOUT_REQUIRED")
sys.path.insert(0,str(original))

from research.mr34i10 import fixed160_train as q
from research.mr34i7.portable_kernel import portable_decimal


class Fixed160NativeTests(unittest.TestCase):
    @staticmethod
    def example():
        result=[]
        for i in range(3):
            x=np.zeros(23,dtype=np.float64)
            x[:16]=np.asarray([((i+j)%3)/3 for j in range(16)],dtype=np.float64)
            x[16+i]=1.
            y=np.asarray([(i+j)%2 for j in range(8)],dtype=np.float64)
            result.append((x,np.zeros(69,dtype=np.float64),y))
        return result

    def test_frozen_source_roles_and_exact_first_protocol(self):
        self.assertEqual(q.FIRST,"ca07d425f16943ecfc3a3731119236465dcbbe22")
        self.assertEqual(q.PARENT,"fb09dd537183bb56ce10a96c27695883fe32cf52")
        self.assertEqual(q.MAX_CANDIDATE_TO_DECIMAL_CPU,.75)
        self.assertEqual(q.MAX_CANDIDATE_TO_ORIGINAL_CPU,2.)
        self.assertEqual(len(q.SEEDS),20)
        self.assertTrue(max(q.SEEDS)<2003)
        self.assertEqual(set(q.ORIGINAL_EVENT_SHA),set(q.SOURCES))
        self.assertEqual(q.S,1<<160)

    def test_fixedpoint_is_source_neutral_and_matches_higher_precision(self):
        src=[-35.,-32.,-16.,-4.,-1.,-.125,-0.,0.,.125,1.,4.,16.,32.,35.]
        src.extend(random.Random(i).uniform(-35.,35.) for i in range(256))
        for x in src:
            self.assertEqual(q.fixed160_sigmoid(x),
                             portable_decimal([x],80)[0])
        with self.assertRaises(ValueError):
            q.fixed160_sigmoid(float("nan"))
        with self.assertRaises(ValueError):
            q.fixed160_sigmoid(float("inf"))

    def test_existing_frozen_original_490_input_static_cohorts(self):
        frozen=q.frozen()
        edge,random_values=q.static_cases(frozen)
        a=q.corpus_screen("canonical_frozen_boundaries",edge)
        b=q.corpus_screen("canonical_seeded_binary64_inputs",random_values)
        self.assertEqual(a["original_binary64_input_count"],42)
        self.assertEqual(b["original_binary64_input_count"],128)
        self.assertTrue(a["candidate_490_input_fidelity_PASS"])
        self.assertTrue(b["candidate_490_input_fidelity_PASS"])

    def test_three_native_models_keep_exact_45_original_coefficients(self):
        Fast,Portable,Original=q.make_fast_class()
        a,b,c=Fast(),Portable(),Original()
        self.assertEqual(a.snapshot(),b.snapshot())
        self.assertEqual(a.snapshot(),c.snapshot())
        self.assertEqual(sum(z.size for z in a.params()),45)
        e=self.example()
        before=a.snapshot()
        np.testing.assert_array_equal(a.forward(e),b.forward(e))
        self.assertEqual(before,a.snapshot())
        self.assertTrue(a.source_gradient_finite_difference(e)["passed"])

    def test_synthetic_native_training_full40_equivalence(self):
        Fast,Portable,Original=q.make_fast_class()
        e=[self.example()]
        fixed,r=q.exact_frozen_optimizer(Fast(),e)
        portable,s=q.exact_frozen_optimizer(Portable(),e)
        self.assertEqual(fixed.snapshot(),portable.snapshot())
        self.assertEqual(r["original_train_only_epoch_Brier"],s["original_train_only_epoch_Brier"])
        self.assertEqual(r["source_actual_training_updates"],40)
        self.assertEqual(len(r["original_train_only_epoch_checkpoint_sha256"]),40)
        self.assertTrue(r["source_native_gradient_finite_difference"]["passed"])

    def test_original_model_and_source_first_use_untouched(self):
        source=Path(q.__file__).read_text()
        self.assertIn("episodes(root,family,SEEDS)",source)
        self.assertIn("train_native(data)",source)
        self.assertIn("fixed160_sigmoid(z)",source)
        self.assertNotIn("episodes(root,family,EVAL)",source)
        self.assertNotIn("model.forward =",source)


if __name__=="__main__":
    unittest.main()
