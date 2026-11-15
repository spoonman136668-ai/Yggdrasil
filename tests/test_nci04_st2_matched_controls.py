"""Frozen ST2 comparison controls: source-free API and negatives only."""
import json
import unittest

from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_st2.event_memory import (
    EventGroundedMemory45, canonical
)
from research.nci04_st2.matched_controls import (
    FixedCameraCount45, RecurrentDelta45, shuffled_prediction,
    estimate, update_pair, brier, SHUFFLE_OFFSET
)


def frame(i):
    r = [0] * 24
    r[3*i:3*i+3] = [1, 2, 3]
    return tuple(r)


def changed(a, b):
    return tuple(int(a[3*i:3*i+3] != b[3*i:3*i+3]) for i in range(8))


class FrozenST2Comparators(unittest.TestCase):
    def setUp(self):
        self.s1 = LocalPredictiveMessages45().snapshot()
        self.bits = (0,) * 8
        self.a, self.b = frame(0), frame(1)

    def test_fixed_camera_has_exact_192_counter_bytes_and_no_45_weight_edits(self):
        fixed = FixedCameraCount45(self.s1)
        frozen = fixed.native.runtime.core.snapshot()
        fixed.observe(self.a,self.bits,0,changed(self.a,self.b),self.b)
        fixed.observe(self.b,self.bits,0,changed(self.b,self.a),self.a)
        self.assertEqual(fixed.accounting()["counter_uint16_bytes"], 192)
        self.assertEqual(fixed.accounting()["reserved_signature_bytes_for_equal_budget"],24)
        self.assertEqual(fixed.native.runtime.core.snapshot(),frozen)

    def test_frozen_fixed_camera_preaction_uses_current_location_not_identity(self):
        fixed = FixedCameraCount45(self.s1)
        fixed.observe(self.a,self.bits,0,changed(self.a,self.b),self.b)
        for i in range(4):
            current,next_raw = ((self.b,self.a) if i%2==0 else
                                (self.a,self.b))
            fixed.observe(current,self.bits,0,changed(current,next_raw),next_raw)
        base = fixed.native.predict(self.b,self.bits,0)
        preds = fixed.predict(self.b,self.bits,0)
        self.assertEqual(preds[1],base[1])  # Counts learned at previous camera.
        self.assertEqual(fixed.counts[0][0][0],2)
        self.assertEqual(fixed.counts[1][0][0],2)

    def test_identity_shuffle_is_predeclared_and_same_core_state(self):
        m = EventGroundedMemory45(self.s1)
        self.assertEqual(SHUFFLE_OFFSET,3)
        m.observe(self.a,self.bits,0,changed(self.a,self.b),self.b)
        for i in range(4):
            current,next_raw = ((self.b,self.a) if i%2==0 else
                                (self.a,self.b))
            m.observe(current,self.bits,0,changed(current,next_raw),next_raw)
        base = m.native.predict(self.b,self.bits,0)
        p = shuffled_prediction(m,self.b,self.bits,0)
        self.assertEqual(p[1],base[1])
        self.assertNotEqual(m.predict(self.b,self.bits,0)[1],p[1])
        self.assertEqual(m.accounting()["persistent_uint16_counter_bytes"],192)

    def test_erase_episode_throws_counts_without_weakening_candidate(self):
        m = EventGroundedMemory45(self.s1)
        m.observe(self.a,self.bits,0,changed(self.a,self.b),self.b)
        m.observe(self.b,self.bits,0,changed(self.b,self.a),self.a)
        fresh = EventGroundedMemory45(m.native.snapshot())
        fresh.reset_episode()
        self.assertGreater(m.clock,0)
        self.assertEqual(fresh.clock,0)
        self.assertEqual(fresh.labels,[None]*8)

    def test_45_weight_trained_recurrent_can_freeze_and_exact_restore(self):
        r = RecurrentDelta45()
        original = r.weights_snapshot()
        p = r.predict(self.a,self.bits,0)
        self.assertEqual(len(p),8)
        r.observe(self.a,self.bits,0,changed(self.a,self.b),train=True)
        self.assertNotEqual(original,r.weights_snapshot())
        checkpoint = r.snapshot()
        restored = RecurrentDelta45.restore(checkpoint)
        self.assertEqual(restored.snapshot(),checkpoint)
        frozen = restored.weights_snapshot()
        restored.observe(self.b,self.bits,0,changed(self.b,self.a),
                         train=False)
        self.assertEqual(restored.weights_snapshot(),frozen)
        restored.reset_episode()
        self.assertEqual(restored.state,[0.0]*8)

    def test_recurrent_restore_tampering_fails(self):
        r=RecurrentDelta45()
        for mutate in (
            lambda d: d.update(schema="nope"),
            lambda d: d["local"][0].__setitem__(0,float("inf")),
            lambda d: d["shared"].__setitem__(2,100.0),
            lambda d: d["state"].append(0.0),
        ):
            d=json.loads(r.snapshot())
            mutate(d)
            with self.assertRaises(ValueError):
                RecurrentDelta45.restore(
                    json.dumps(d,sort_keys=True,separators=(",",":"),
                               allow_nan=True)
                )

    def test_frozen_brier_and_saturation(self):
        self.assertAlmostEqual(brier([.5]*8,[1]*8),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,[1]*8)
        pair=[65535,6]
        update_pair(pair,1)
        self.assertEqual(pair,[32768,3])
        self.assertEqual(estimate(.4,[0,0]),.4)
        self.assertAlmostEqual(estimate(.4,[4,0]),.5*.4+.5*5/6)

    def test_refuses_invalid_target_and_preserves_count_on_precondition(self):
        fixed=FixedCameraCount45(self.s1)
        saved=fixed.snapshot()
        with self.assertRaises(ValueError):
            fixed.observe(self.a,self.bits,0,[0]*8,self.b)
        self.assertEqual(fixed.snapshot(),saved)


if __name__=="__main__":
    unittest.main()
