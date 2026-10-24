"""MR34I9 focused synthetic (source-free) validation of opt-in native training."""
import ast
from pathlib import Path
import unittest

import numpy as np

from research.mr34i9 import optin_train as q
from research.mr34i7.portable_kernel import portable_decimal


class OptinFullTrainTests(unittest.TestCase):
    @staticmethod
    def episode():
        rows=[]
        for i in range(3):
            x=np.zeros(23,dtype=np.float64)
            x[:16]=np.asarray([(i+j)%3/3 for j in range(16)],dtype=np.float64)
            x[16+i]=1.
            y=np.asarray([(i+j)%2 for j in range(8)],dtype=np.float64)
            rows.append((x,np.zeros(69,dtype=np.float64),y))
        return rows

    def test_protocol_and_source_roles(self):
        self.assertEqual(q.FIRST,"edd80b67d0d9b45a8098a3f676393db3788a4e5c")
        self.assertEqual(q.PARENT,"608675a3343ff9ff34a96e2057a8091f738aaf5f")
        self.assertEqual(len(q.SEEDS),20)
        self.assertTrue(all(x<2003 for x in q.SEEDS))
        self.assertEqual(q.MAX_TRAIN_CPU_RATIO,50.)
        self.assertEqual(set(q.ORIGINAL_EVENT_SHA),set(q.SOURCES))

    def test_portable_kernel_unchanged_and_native_45_params(self):
        Portable,Original=q.make_portable_class()
        self.assertTrue(issubclass(Portable,Original))
        self.assertEqual(len(portable_decimal([0.,-.5,.5],48)),3)
        orig=Original()
        candidate=Portable()
        self.assertEqual(orig.snapshot(),candidate.snapshot())
        self.assertEqual(sum(x.size for x in candidate.params()),45)
        before=candidate.snapshot()
        original=orig.forward(self.episode())
        revised=candidate.forward(self.episode())
        self.assertEqual(revised.shape,(3,8))
        self.assertTrue(np.all(np.isfinite(revised)))
        self.assertLess(float(np.max(np.abs(revised-original))),1e-11)
        self.assertEqual(before,candidate.snapshot())
        self.assertEqual(candidate.source_gradient_finite_difference(self.episode())["passed"],True)

    def test_exact_original_and_candidate_40_epoch_training_on_synthetic(self):
        Portable,Original=q.make_portable_class()
        data=[self.episode()]
        baseline,baselines=q.exact_frozen_optimizer(Original(),data)
        portable,screen=q.exact_frozen_optimizer(Portable(),data)
        for report in (baselines,screen):
            self.assertEqual(report["original_frozen_training_epochs"],40)
            self.assertEqual(report["source_actual_training_updates"],40)
            self.assertEqual(len(report["original_train_only_epoch_Brier"]),40)
            self.assertEqual(len(report["original_train_only_epoch_checkpoint_sha256"]),40)
            self.assertTrue(report["exact_native_45_weights"])
            self.assertTrue(report["source_native_gradient_finite_difference"]["passed"])
            self.assertLessEqual(report["source_train_only_selected_epoch"],40)
        self.assertEqual(type(portable).__name__,"PortableNative45")
        self.assertEqual(type(baseline).__name__,"NativePredictiveQuotient45")

    def test_no_original_source_eval_or_model_patch(self):
        source=Path(q.__file__).read_text()
        tree=ast.parse(source)
        func=next(t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name=="evaluate_source")
        s=ast.unparse(func)
        self.assertIn("episodes(root, family, SEEDS)",s)
        self.assertIn("train_native(data)",s)
        self.assertIn("make_portable_class()",s)
        self.assertNotIn("EVAL",s)
        self.assertNotIn("model.forward =",s)
        self.assertIn("portable_decimal(u,48)",source.replace(" ",""))


if __name__=="__main__":
    unittest.main()
