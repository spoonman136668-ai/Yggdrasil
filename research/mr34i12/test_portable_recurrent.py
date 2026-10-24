"""MR34I12 focused source-FREE tests: source identity and original model untouched."""
from pathlib import Path
import math
import sys
import unittest

import numpy as np

orig=Path(__file__).resolve().parents[3]/"original_s4c1"
if not orig.is_dir():
    raise RuntimeError("MR34I12_ORIGINAL_S4C1_READONLY_CHECKOUT_REQUIRED")
sys.path.insert(0,str(orig))

from research.mr34i12 import portable_recurrent as q


class PortableFullRecurrenceTests(unittest.TestCase):
    @staticmethod
    def synthetic_episode():
        data=[]
        for i in range(3):
            x=np.zeros(23,dtype=np.float64)
            x[:16]=np.array([((i+j)%5)/5 for j in range(16)],dtype=np.float64)
            x[16+i]=1.
            y=np.array([(i+j)%2 for j in range(8)],dtype=np.float64)
            data.append((x,np.zeros(69,dtype=np.float64),y))
        return data

    def test_frozen_original_source_and_governance(self):
        self.assertEqual(q.FIRST,"84790ee328d3f4c3ba8fbe6c8f9077f7844ba8fc")
        self.assertEqual(q.PARENT,"f37da027ab92618c21d47fd2a50c46d949ef6bca")
        self.assertEqual(q.MAX_TO_NUMPY,2.50)
        self.assertEqual(q.MAX_TO_DECIMAL48,1.00)
        self.assertEqual(q.MAX_TRAIN_BRIER_DAMAGE,.01)
        self.assertEqual(len(q.SEEDS),20)
        self.assertTrue(all(1861<=n<2003 for n in q.SEEDS))

    def test_fsum_exact_explicit_inner_sum_zero_and_nonzero_state(self):
        f=np.arange(56,dtype=np.float64).reshape(8,7)/37.
        g=np.arange(21,dtype=np.float64).reshape(3,7)/51.
        roles=np.arange(24,dtype=np.float64).reshape(8,3)/29.
        s=np.linspace(-.75,.75,8,dtype=np.float64)
        read,u=q.fsum_native_read_u(f,g,roles,s)
        for i in range(8):
            self.assertEqual(read[i],math.fsum(
                [float(f[i,j])*float(g[1,j]) for j in range(7)]
                +[float(roles[i,1])]))
            self.assertEqual(u[i],math.fsum(
                [float(f[i,j])*float(g[0,j]) for j in range(7)]
                +[float(roles[i,0]),float(s[i])*float(read[i])]))
        with self.assertRaises(ValueError):
            q.fsum_native_read_u(f[:7],g,roles,s)
        bad=f.copy()
        bad[3,1]=np.nan
        with self.assertRaises(ValueError):
            q.fsum_native_read_u(bad,g,roles,s)

    def test_optin_full_native_45_original_identity_and_analytic_gradients(self):
        Fsum,Q160,Decimal,Original=q.make_recurrent_candidate()
        self.assertTrue(issubclass(Fsum,Original))
        a,b,c,d=Fsum(),Q160(),Decimal(),Original()
        snapshots=[x.snapshot() for x in (a,b,c,d)]
        self.assertEqual(len(set(snapshots)),1)
        self.assertEqual(sum(p.size for p in a.params()),45)
        ep=self.synthetic_episode()
        before=a.snapshot()
        p=a.forward(ep)
        self.assertEqual(p.shape,(3,8))
        self.assertTrue(np.all(np.isfinite(p)))
        self.assertLess(np.max(np.abs(p-b.forward(ep))),1e-9)
        self.assertEqual(before,a.snapshot())
        self.assertTrue(a.source_gradient_finite_difference(ep)["passed"])

    def test_full40_synthetic_training_and_original_analytic_loss(self):
        from research.mr34i9.optin_train import exact_frozen_optimizer
        Fsum,Q160,Decimal,Original=q.make_recurrent_candidate()
        data=[self.synthetic_episode()]
        trained,trace=exact_frozen_optimizer(Fsum(),data)
        other,control=exact_frozen_optimizer(Q160(),data)
        self.assertTrue(trace["exact_native_45_weights"])
        self.assertEqual(trace["source_actual_training_updates"],40)
        self.assertEqual(len(trace["original_train_only_epoch_Brier"]),40)
        self.assertEqual(len(trace["original_train_only_epoch_checkpoint_sha256"]),40)
        self.assertTrue(trace["source_native_gradient_finite_difference"]["passed"])
        self.assertTrue(np.all(np.isfinite(trained.forward(data[0]))))
        self.assertEqual(sum(p.size for p in other.params()),45)
        self.assertTrue(control["source_native_gradient_finite_difference"]["passed"])

    def test_exact_original_public_source_roles_only(self):
        src=Path(q.__file__).read_text()
        self.assertIn("episodes(root,family,SEEDS)",src)
        self.assertIn("train_native(episodes_data)",src)
        self.assertIn("original_git(root,SOURCES[family])",src)
        self.assertNotIn("episodes(root,family,EVAL)",src)
        self.assertNotIn("model.forward =",src)
        self.assertNotIn("protected_first_use=True",src)


if __name__=="__main__":
    unittest.main()
