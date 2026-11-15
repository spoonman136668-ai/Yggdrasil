"""ST7 frozen original private-source unit and falsifying fixtures.

The following are SOURCE-only controls. Learners MUST NOT import the
private true coefficient / quadratic generator, and no held law is opened.
"""
import json
import unittest

from research.nci04_st7.private_world import (
    ACTIONS,PrivateQuadraticWorld,TRIALS,
    byte_to_bits,public_byte,rol,features,private_params,
    private_coefficient_rows,quadratic,original_episode,
    diagnostic_from_public
)
from research.nci04_st7.source_audit import disposition,source_rank_insert


class ST7OriginalSourceTests(unittest.TestCase):
    def test_real_public_actuator_recovery_on_training_laws_only(self):
        for law in (3,5,7,11):
            for seed in (100,103):
                trace,cue=original_episode(law,seed,0)
                self.assertEqual(cue,private_params(law,seed,0))
                self.assertEqual(tuple(t[1] for t in trace),ACTIONS)
                self.assertEqual(len(trace),5)
                for before,action,after,change in trace:
                    self.assertEqual(
                        change,tuple(a^b for a,b in zip(before,after))
                    )

    def test_true_quadratic_polynomial_is_not_simple_linear(self):
        rows=private_coefficient_rows(False)
        self.assertEqual(len(rows),8)
        self.assertGreaterEqual(
            sum((r>>8).bit_count() for r in rows),32
        )
        for b in (0,1,2,3,19,173):
            f=features(b)
            expected=sum(((f&r).bit_count()&1)<<j
                         for j,r in enumerate(rows))
            self.assertEqual(quadratic(b),expected)
        self.assertEqual(features(0),0)
        self.assertEqual(features(1),1)
        self.assertEqual(features(3)&((1<<8)-1),3)
        self.assertNotEqual(features(3)>>8,0)

    def test_delayed_action_has_real_one_step_effect(self):
        for law in (3,7):
            trace,cue=original_episode(law,102,3)
            r,a,b=cue
            pre,action,after,target=trace[4]
            self.assertEqual(action,3)
            self.assertEqual(
                public_byte(after)^rol(public_byte(pre),r),
                a^quadratic(b,False)
            )
            self.assertEqual(diagnostic_from_public(trace[:3]),cue)
            self.assertEqual(diagnostic_from_public(trace),cue)
            self.assertIsNone(diagnostic_from_public(trace[:2]))

    def test_public_evidence_is_not_predictive_label_leak(self):
        trace,cue=original_episode(3,103,4)
        changed=list(trace)
        pre,action,post,target=changed[4]
        changed[4]=(pre,action,post,tuple(1-t for t in target))
        self.assertEqual(diagnostic_from_public(changed),cue)

    def test_source_true_cold_snapshot_after_three_real_acts(self):
        w=PrivateQuadraticWorld(3,102,2)
        for action in ACTIONS[:3]:
            w.step(action)
        frozen=w.snapshot()
        clone=PrivateQuadraticWorld.restore(frozen)
        self.assertEqual(clone.snapshot(),frozen)
        for action in ACTIONS[3:]:
            self.assertEqual(w.step(action),clone.step(action))
        self.assertEqual(w.snapshot(),clone.snapshot())

    def test_invalid_actor_and_source_exhaustion_are_atomic(self):
        w=PrivateQuadraticWorld(3,100,0)
        previous=w.snapshot()
        for bad in (-1,0,1,2,4,True,1.2,"3"):
            with self.assertRaises(ValueError):w.step(bad)
            self.assertEqual(w.snapshot(),previous)
        for action in ACTIONS:w.step(action)
        with self.assertRaises(ValueError):w.step(3)

    def test_private_cold_source_checkpoint_rejects_corruption(self):
        w=PrivateQuadraticWorld(3,100,0)
        raw=json.loads(w.snapshot())
        for mutation in (
            {"schema":"bad"},{"law":True},{"step":6},
            {"x":-1},{"pending":256},{"r":4},{"a":"3"}
        ):
            altered={**raw,**mutation}
            with self.assertRaises(ValueError):
                PrivateQuadraticWorld.restore(
                    json.dumps(altered,sort_keys=True,separators=(",",":"))
                )

    def test_source_only_rank_independence_computed_not_assumed(self):
        pivots=[0]*36
        for b in range(256):
            source_rank_insert(pivots,features(b))
        self.assertEqual(sum(z!=0 for z in pivots),36)
        self.assertFalse(source_rank_insert(pivots,features(19)))
        self.assertEqual(sum(z!=0 for z in pivots),36)

    def test_frozen_source_gate_rejects_missing_rank_and_actions(self):
        ok=disposition(7680,1536,1536,36,64,8,0)
        self.assertEqual(ok["decision"],
                         "SOURCE_UNKNOWN_QUADRATIC_IDENTIFIABLE_DEV_ONLY")
        for args in (
            (7679,1536,1536,36,64,8,0),
            (7680,1535,1536,36,64,8,0),
            (7680,1536,1535,36,64,8,0),
            (7680,1536,1536,35,64,8,0),
            (7680,1536,1536,36,31,8,0),
            (7680,1536,1536,36,64,7,0),
            (7680,1536,1536,36,64,8,1)
        ):
            self.assertEqual(disposition(*args)["decision"],
                             "SOURCE_UNIDENTIFIABLE_DEV_NO_GO")


if __name__=="__main__":unittest.main()
