"""AAI-08P stochastic RNG source/seed mechanical checks (no science worlds)."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("aai08_rng",ROOT/"stochastic_custody.py")
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)

class RNGTests(unittest.TestCase):
    def test_exact_sources_and_custody_boundary(self):
        self.assertEqual(x.UPSTREAM_COMMIT,"127df4b714fe4fcf680721d8e9278a96090acd7e")
        self.assertEqual(x.SEEDS,tuple(range(996100,996116)))
        self.assertEqual(x.INITIAL,(1.,0.,0.))
        self.assertEqual(x.STOCHASTIC,(.15,.70,.15))

    def test_global_rng_restored(self):
        before=x.np.random.get_state()
        x.rollout(x.SEEDS[0],True)
        after=x.np.random.get_state()
        self.assertTrue(x.rng_state_equal(before,after))

    def test_stochastic_replay_and_real_shift(self):
        result=x.main()
        self.assertTrue(result["replay_identical_when_scoped_seed_reapplied"])
        self.assertTrue(result["global_numpy_rng_original_state_restored"])
        self.assertGreaterEqual(result["stochastic_shift_changes_executed_outcome_cases"],8)
        self.assertFalse(result["scientific_primary_consumed"])

    def test_hidden_transition_information_not_consumed(self):
        t=ast.parse((ROOT/"stochastic_custody.py").read_text(encoding="utf-8"))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in
             ("unwrapped","transition_matrix","get_planning_env","P_left","P_right")
             for n in ast.walk(t)))


if __name__=="__main__":
    unittest.main()
