"""Independent conventional comparator under frozen public-action evidence."""
import random
import unittest
import binding as m
from strong_control import ExactTwoFeatureControl
from test_contract import tape, Past


class EqualInformationControlTests(unittest.TestCase):
    def test_exact_control_identical_action_policy_three_families(self):
        for seed,a,b,table in ((7125,1,6,6),(7126,18,32,6),(7127,5,35,8)):
            native, conventional = m.ConditionalTemporalBinder(), ExactTwoFeatureControl()
            for observed in tape(seed,a,b,table):
                native.observe_public(observed)
                conventional.observe_public(observed)
            native.seal(); conventional.seal()
            rng=random.Random(seed + 500)
            score = 0
            for _ in range(128):
                state=tuple(rng.randrange(16) for _ in range(8))
                s0=tuple(rng.randrange(16) for _ in range(8))
                s1=tuple(rng.randrange(16) for _ in range(8))
                p0,p1=rng.randrange(2),rng.randrange(2)
                history=(Past(s0,p0,0,s1,False),Past(s1,p1,0,state,False))
                actual=native.choose_public(state,history)
                self.assertEqual(actual,conventional.choose_public(state,history))
                bitmask=m._feature_bits(state,p1,p0)
                target=(table>>(((bitmask>>a&1)<<1)|(bitmask>>b&1)))&1
                score+=actual == target
            self.assertEqual(score,128)
            self.assertEqual(native.binding[1:3], (b,table))


if __name__ == '__main__': unittest.main()
