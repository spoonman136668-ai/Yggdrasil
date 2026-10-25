"""C30 source-only focused parity against original R1 public-input grammar."""
import json
import unittest

from research.native.itd02.r1.native_policy import PublicGrid,features,canonical
from research.mass_r7c29.effects import NativeCellEffect,exploratory_proxy
from research.mass_r7c30.independent_logistic import (
    IndependentPublicLogistic,independently_encoded_public
)


def public(front=False,direction=0,gx=6,gy=5):
    return PublicGrid(2,3,gx,gy,direction,front)


class FullNineFeatureConventionalParity(unittest.TestCase):
    def test_exact_original_r1_all_nine_features(self):
        for x in range(4):
            for front in (False,True):
                for gx,gy in ((0,0),(4,6),(18,23),(64,64)):
                    s=PublicGrid(1,2,gx,gy,x,front)
                    self.assertEqual(independently_encoded_public(s),features(s))
                    self.assertEqual(len(independently_encoded_public(s)),9)

    def test_invalid_private_or_nonpublic_inputs_denied(self):
        m=IndependentPublicLogistic(0.)
        with self.assertRaisesRegex(ValueError,"NOT_PUBLIC"):
            m.predict({"front_blocked":False,"private":1},1)
        with self.assertRaisesRegex(ValueError,"INVALID_PUBLIC"):
            m.predict(PublicGrid(2,3,6,5,1,0),1)
        with self.assertRaisesRegex(ValueError,"ILLEGAL_PUBLIC"):
            m.predict(public(),True)

    def test_learning_uses_selected_real_action_only(self):
        m=IndependentPublicLogistic(0.)
        s=public()
        before=m.predict(s,1)
        m.observe(s,1,1)
        self.assertGreater(m.predict(s,1),before)
        self.assertEqual(m.predict(s,0),before)
        self.assertEqual(m.updates,1)

    def test_opposing_results_revose_and_reacquire(self):
        m=IndependentPublicLogistic(.85)
        s=public(front=True)
        for _ in range(15):m.observe(s,2,1)
        high=m.predict(s,2)
        for _ in range(25):m.observe(s,2,0)
        low=m.predict(s,2)
        for _ in range(50):m.observe(s,2,1)
        rehigh=m.predict(s,2)
        self.assertLess(low,high)
        self.assertGreater(rehigh,low)

    def test_identical_public_budget_both_lr_and_time_variant(self):
        for momentum in (0.,.85):
            m=IndependentPublicLogistic(momentum)
            for act in (0,1,2):
                m.observe(public(direction=act),act,act%2)
            self.assertEqual(set(m.weight),{"0","1","2"})
            self.assertEqual(sum(len(v) for v in m.weight.values()),27)
            self.assertEqual(sum(len(v) for v in m.velocity.values()),27)
            self.assertEqual(m.updates,3)

    def test_goal_features_actually_affect_prediction(self):
        m=IndependentPublicLogistic(0.)
        first=public(gx=6,gy=5)
        m.observe(first,1,1)
        self.assertNotEqual(m.predict(first,1),m.predict(public(gx=2,gy=3),1))

    def test_frozen_and_native_controls_are_distinct_implementations(self):
        source=public()
        a=NativeCellEffect()
        b=IndependentPublicLogistic(.85)
        a.observe(source,1,1)
        b.observe(source,1,1)
        self.assertNotEqual(a.predict(source,1),b.predict(source,1))
        self.assertNotEqual(a.snapshot()["cells"],b.snapshot()["weight"])

    def test_true_os_serialization_grammar_and_prediction_roundtrip(self):
        for momentum in (0.,.85):
            m=IndependentPublicLogistic(momentum)
            for i in range(12):
                m.observe(public(i%2==0,direction=i%4),i%3,i%2)
            wire=m.checkpoint()
            cold=IndependentPublicLogistic.restore(wire)
            self.assertEqual(cold.checkpoint(),wire)
            for a in (0,1,2):
                s=public(True,a)
                self.assertEqual(m.predict(s,a),cold.predict(s,a))
                self.assertEqual(exploratory_proxy(m,s,a),exploratory_proxy(cold,s,a))

    def test_tampered_native_competitor_memory_rejected(self):
        m=IndependentPublicLogistic(.85)
        wire=json.loads(m.checkpoint())
        wire["payload"]["weight"]["0"][2]=0.75
        with self.assertRaisesRegex(ValueError,"TAMPER"):
            IndependentPublicLogistic.restore(canonical(wire))

    def test_invalid_checkpoint_counts_fail_even_with_rehashed_wire(self):
        import hashlib
        m=IndependentPublicLogistic(.85)
        wire=json.loads(m.checkpoint())
        wire["payload"]["updates"]=-1
        wire["sha256"]=hashlib.sha256(canonical(wire["payload"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"COUNTER"):
            IndependentPublicLogistic.restore(canonical(wire))

if __name__=="__main__":
    unittest.main()
