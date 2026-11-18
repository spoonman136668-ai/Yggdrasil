"""CKAD28 non-leaking policy tests on authentic native retained hypotheses."""
import importlib.util
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
import policy


class DecisionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=HERE.parent/"CKAD-22"/"seed-101-expanded-native.json"
        raw=path.read_bytes()
        cls.model=NativeCumulativeLearner.restore(raw,digest(raw)).begin_experience_stream()

    def test_exact_source_policy_is_read_only_and_deterministic(self):
        model=self.model
        view=(0,1)
        original=model.checkpoint()
        actions=[]
        for arm in policy.ARMS:
            for i in (0,1,2,3,4,5,7):
                a,b=policy.choices(model,view,arm,"frozen/101/"+arm,i)
                x=a(0)
                self.assertIn(x,(0,1))
                self.assertEqual(x,a(0))
                for state in (0,1):
                    y=b(0,x,state)
                    self.assertIn(y,(0,1))
                    self.assertEqual(y,b(0,x,state))
                actions.append((arm,i,x))
        self.assertEqual(model.checkpoint(),original)
        self.assertEqual(policy.QUARTER_EXPLOIT,4)
        self.assertEqual(len(actions),21)

    def test_first_action_scores_all_reachable_second_states(self):
        model=self.model
        view=(1,0)
        self.assertEqual(policy.decision_first(model,view),
                         policy.decision_first(model,view))
        for first in (0,1):
            for state in (0,1):
                v=policy.value_perfect_information(model,view,first,state)
                self.assertIsInstance(v,Fraction)
                self.assertGreaterEqual(v,0)
        self.assertIn(policy.decision_second(model,view,1,0),(0,1))

    def test_bad_public_arguments_and_hidden_source_denied(self):
        with self.assertRaisesRegex(ValueError,"PUBLIC_VIEW"):
            policy.decision_first(self.model,(0,))
        with self.assertRaisesRegex(ValueError,"ARM"):
            policy.choices(self.model,(0,0),"oracle","test",0)
        with self.assertRaisesRegex(ValueError,"RANDOM_SOURCE"):
            policy.random_bits("bad🚫",0)

    def test_random_is_stably_seeded_and_source_independent(self):
        self.assertEqual(policy.random_bits("frozen/101/random",0),
                         policy.random_bits("frozen/101/random",0))
        self.assertEqual(policy.random_bits("frozen/101/random",9),
                         policy.random_bits("frozen/101/random",9))
        self.assertEqual(len(policy.ARMS),3)


if __name__=="__main__":
    unittest.main()
