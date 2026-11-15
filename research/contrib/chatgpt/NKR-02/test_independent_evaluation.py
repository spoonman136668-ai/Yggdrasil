"""NKR02 frozen independent comparison contracts: no protected first-use data."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("nkr02_independent_evaluation",
                                            HERE/"independent_evaluation.py")
ev=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

class IndependentNKR02Tests(unittest.TestCase):
    def test_train_and_holdout_disjoint_with_multiple_unseen_compositions(self):
        self.assertEqual(ev.TRAIN,(0,1,2,4,8))
        self.assertEqual(len(ev.TEST),11)
        self.assertEqual(len(set(ev.TEST)),11)
        self.assertFalse(set(ev.TRAIN)&set(ev.TEST))
        self.assertEqual(ev.NATIVE,16)
        self.assertEqual(ev.PREREG,"2aedc2a5ab0da62563fca1c8dbd079a18a634f6d")

    def test_quadratic_novelty_is_truly_invisible_during_training(self):
        for slot in range(16):
            for ctx in ev.TRAIN:
                for action in (0,1):
                    self.assertEqual(ev.consequence(slot,ctx,action,False),
                                     ev.consequence(slot,ctx,action,True))
            for ctx in (3,7,11,15):
                for action in (0,1):
                    self.assertNotEqual(ev.consequence(slot,ctx,action,False),
                                        ev.consequence(slot,ctx,action,True))

    def test_independent_symbolic_solver_uses_only_observed_examples(self):
        for slot in range(16):
            obs=[(ctx,action,ev.consequence(slot,ctx,action))
                 for ctx in ev.TRAIN for action in (0,1)]
            control=ev.independent_symbolic_fit(obs)
            for ctx in range(16):
                for action in (0,1):
                    self.assertEqual(control(ctx,action),
                                     ev.consequence(slot,ctx,action))

    def test_gradient_model_trains_from_public_observations_not_oracle_state(self):
        g=ev.AdamMLP(19)
        with self.assertRaises(ValueError):g.predict(0,0)
        obs=[(ctx,action,ev.consequence(0,ctx,action))
             for ctx in ev.TRAIN for action in (0,1)]
        g.fit(obs)
        self.assertTrue(g.fitted)
        self.assertGreaterEqual(g.training_correct,8)
        self.assertLessEqual(g.training_correct,10)

if __name__=="__main__":
    unittest.main()
