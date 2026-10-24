"""P0F-C1D focused SOURCE-FREE tests. No native or original source resets."""
import ast
from pathlib import Path
import unittest
import numpy as np

from research.p0fc1d import gate_models as g
from research.p0fc1b.full_public_controls import FullFrameCategorical


class LearnedGateTests(unittest.TestCase):
    def fixture(self):
        rng=np.random.default_rng(19)
        x=rng.normal(0,0.2,(65,15))
        x[:,5:10]+=.04
        x[:,10:]+=.08
        y=(np.arange(65*3,dtype=np.int64).reshape(65,3)%2).astype(np.uint8)
        return x,y

    def test_new_roles_are_frozen_and_disjoint_from_old_science(self):
        self.assertTrue(g.check_roles())
        self.assertEqual(len(g.FIT),24)
        self.assertEqual(len(g.SELECT),6)
        self.assertEqual(len(g.PUBLIC_DEV),12)
        self.assertEqual(g.FIRST,"2e2b6198c6704874d9cd03df29085590d336e453")
        self.assertEqual(g.ARM_NAMES,("history_masked","history_visible",
                                      "trained_history_shrink","learned_two_gate"))

    def test_source_free_history_feature_scaling_does_not_mutate_current(self):
        x,_=self.fixture()
        masked=g.features_at_gate(x,(0.,0.))
        half=g.features_at_gate(x,(.5,.5))
        full=g.features_at_gate(x,(1.,1.))
        np.testing.assert_array_equal(x,full)
        np.testing.assert_array_equal(masked[:,:5],x[:,:5])
        np.testing.assert_array_equal(masked[:,5:],0.)
        np.testing.assert_array_equal(half[:,5:],x[:,5:]/2.)
        with self.assertRaises(ValueError):
            g.features_at_gate(x[:,:14],(.5,.5))

    def test_learned_two_gate_receives_only_real_public_target_gradients(self):
        x,y=self.fixture()
        model,mapper,m=g.fit_model("learned_two_gate",x,y,17)
        self.assertEqual(m["trainable_parameters_including_gates"],
                         sum(p.size for p in model.p)+2)
        self.assertEqual(m["training_updates"],48)
        self.assertEqual(model.checkpoint_bytes(),sum(p.nbytes for p in model.p)+
                         sum(len(v) for v in model.vocab)+16)
        self.assertTrue(all(0<v<1 for v in m["history_gate_values_after_fit"]))
        self.assertTrue(np.all(np.isfinite(model.score(mapper(x),y))))
        self.assertEqual(len(model.checkpoint_sha()),64)

    def test_all_controls_use_same_full_input_dimensionality_and_fitted_loss(self):
        x,y=self.fixture()
        for arm in g.ARM_NAMES:
            model,mapper,m=g.fit_model(arm,x,y,17)
            self.assertEqual(model.p[0].shape,(x.shape[1],g.UNITS))
            self.assertTrue(np.all(np.isfinite(model.score(mapper(x),y))))
            self.assertEqual(m["training_updates"],48)

    def test_cluster_bootstrap_reproducible_no_per_transition_pseudoreplication(self):
        delta=[.1]*12
        self.assertEqual(g.confidence(delta),[.10000000000000002,.10000000000000002])
        with self.assertRaises(ValueError):
            g.confidence([.1]*11)

    def test_prospective_dev_acquired_only_after_model_freeze(self):
        src=ast.parse(Path(g.__file__).read_text())
        body=next(x for x in src.body if isinstance(x,ast.FunctionDef) and x.name=="evaluate_source")
        calls=[(i,ast.unparse(x.args[1])) for i,x in enumerate(ast.walk(body))
               if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="acquire"]
        self.assertEqual([v for _,v in calls],["FIT","SELECT","PUBLIC_DEV"])
        text=Path(g.__file__).read_text()
        self.assertIn('dev_rows,dev_receipts=acquire(name,PUBLIC_DEV)',text)
        self.assertLess(text.index('for arm in ARM_NAMES:'),text.index('dev_rows,dev_receipts=acquire(name,PUBLIC_DEV)'))


if __name__=="__main__":
    unittest.main()
