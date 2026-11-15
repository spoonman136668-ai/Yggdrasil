"""FKP-14 fixture-only tests: NEVER invoke true registered source world."""
from pathlib import Path
import hashlib
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import evaluate


class FKP14Preflight(unittest.TestCase):
    def test_new_dev_is_disjoint_and_closed(self):
        self.assertEqual(len(evaluate.SOURCE_SEEDS),32)
        self.assertEqual(evaluate.SOURCE_SEEDS[0],974000)
        self.assertEqual(evaluate.SOURCE_SEEDS[-1],974031)
        self.assertEqual(evaluate.ANCHORS,(0,16,32,64))
        self.assertEqual(evaluate.HORIZONS,(8,16))
        self.assertEqual(len(evaluate.ACTIONS),9)
        self.assertNotIn(973500,evaluate.SOURCE_SEEDS)
        self.assertNotIn(974500,evaluate.SOURCE_SEEDS)

    def test_macro8_prefix_independent_of_source(self):
        p=evaluate.public_prefix(974000)
        self.assertEqual(len(p),64)
        self.assertTrue(all(p[t]==p[t+1] for t in range(0,64,8) for t in range(t,t+7)))
        self.assertEqual(p,evaluate.public_prefix(974000))
        self.assertEqual(len(set(evaluate.ACTIONS)),9)

    def test_no_unregistered_source(self):
        for seed in (973500,974500,975000):
            with self.assertRaises(ValueError):
                evaluate.public_prefix(seed)
            with self.assertRaises(ValueError):
                evaluate.episode(seed,0,None,0)
        with self.assertRaises(ValueError):
            evaluate.episode(974000,6,None,0)
        with self.assertRaises(ValueError):
            evaluate.episode(974000,0,(1,1),7)
        with self.assertRaises(ValueError):
            evaluate.episode(974000,0,(1,1),0)
        with self.assertRaises(ValueError):
            evaluate.episode(974000,0,None,16)

    def test_frozen_random_choice_never_uses_rewards(self):
        x=evaluate.fixed_random_control(974000,16)
        self.assertEqual(x,evaluate.fixed_random_control(974000,16))
        self.assertGreaterEqual(x,0)
        self.assertLess(x,9)
        with self.assertRaises(ValueError):
            evaluate.fixed_random_control(974500,16)

    def test_real_source_image_frame_integrity_contract(self):
        import numpy as np
        a=hashlib.sha256()
        evaluate.digest_public(np.zeros((3,4,3),dtype=np.uint8),a)
        b=hashlib.sha256()
        x=np.zeros((3,4,3),dtype=np.uint8)
        x[0,0,0]=1
        evaluate.digest_public(x,b)
        self.assertNotEqual(a.hexdigest(),b.hexdigest())
        with self.assertRaises(ValueError):
            evaluate.digest_public(np.zeros((3,4),dtype=np.uint8),hashlib.sha256())
        with self.assertRaises(ValueError):
            evaluate.digest_public(np.zeros((3,4,3),dtype=np.float32),hashlib.sha256())

    def test_branch_scoring_uses_only_sealed_true_consequences(self):
        reference={"prefix_sha256":"ref"}
        rows=[]
        for k,action in enumerate(evaluate.ACTIONS):
            rows.append({"valid":True,"prefix_sha256":"ref",
                         "future_actual_return":0.05 if k==8 else -0.05,
                         "positive_events":int(k==8),
                         "terminal_goal_events":0,
                         "future_source_actions":16,
                         "branch_sha256":str(k)})
        out=evaluate.summarize_anchor(974000,16,reference,16,rows)
        self.assertEqual(out["return_spread"],.10)
        self.assertTrue(out["return_contrast_ge_005"])
        self.assertTrue(out["any_positive_return"])
        self.assertTrue(out["any_positive_event"])
        self.assertFalse(out["any_terminal_goal"])
        rows[0]["prefix_sha256"]="tamper"
        with self.assertRaises(AssertionError):
            evaluate.summarize_anchor(974000,16,reference,16,rows)

    def test_no_source_truth_or_privileged_evaluator_access(self):
        import inspect
        src=inspect.getsource(evaluate.episode)
        for prohibited in ("env.unwrapped","env.info","mystery_path.path",
                           "normalized_agent_position","env._target","env.end"):
            self.assertNotIn(prohibited,src)
        self.assertIn("env.step(public_action)",src)
        self.assertIn("env.reset(seed=seed",src)


if __name__=="__main__":
    unittest.main()
