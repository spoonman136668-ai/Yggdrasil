"""ST3 source mechanics and frozen source-only negative controls; NOT science."""
import json
import unittest

from research.nci04_st3.causal_switchboard import (
    HiddenLawSwitchboard, STEPS, bits, byte, choose_blind_action,
    rotl8, source_mask
)
from research.nci04_st3.source_audit import stage0_verdict, TRAIN_LAWS, TRAIN_SEEDS


class SourceMechanics(unittest.TestCase):
    def test_boolean_public_representation_and_rotation(self):
        for n in (0, 1, 43, 127, 128, 255):
            self.assertEqual(byte(bits(n)), n)
        self.assertEqual(rotl8(0b10000001, 1), 0b00000011)
        for bad in (-1, 256, True, 3.5):
            with self.assertRaises(ValueError):
                bits(bad)

    def test_real_action_consequence_and_pending_delay(self):
        a = HiddenLawSwitchboard(3, 100)
        b = HiddenLawSwitchboard(3, 100)
        old = a.public()
        p1, target = a.step(2)
        p2, _ = b.step(3)
        self.assertEqual(p1, p2)
        self.assertEqual(target, tuple(x ^ y for x, y in zip(old, p1)))
        aa, _ = a.step(3)
        bb, _ = b.step(3)
        if source_mask(3,2) != 0:
            self.assertNotEqual(aa, bb)
        self.assertEqual(byte(aa) ^ byte(bb), source_mask(3,2))

    def test_mask_0_1_produce_different_public_consequences(self):
        a = HiddenLawSwitchboard(5, 100)
        b = HiddenLawSwitchboard(5, 100)
        a1, _ = a.step(0)
        b1, _ = b.step(1)
        self.assertEqual(
            byte(a1) ^ byte(b1), source_mask(5,0) ^ source_mask(5,1)
        )

    def test_exact_state_restore_and_actual_continuation(self):
        a=HiddenLawSwitchboard(13,104)
        for t in range(12):
            a.step(choose_blind_action(104,t))
        snap=a.snapshot()
        b=HiddenLawSwitchboard.restore(snap)
        self.assertEqual(b.snapshot(),snap)
        for t in range(12,STEPS):
            act=choose_blind_action(104,t)
            self.assertEqual(a.public(),b.public())
            self.assertEqual(a.step(act),b.step(act))
        with self.assertRaises(ValueError):
            a.step(0)
        self.assertEqual(a.snapshot(),b.snapshot())

    def test_actor_is_fixed_and_each_action_exercised(self):
        for seed in TRAIN_SEEDS:
            actions=[choose_blind_action(seed,t) for t in range(STEPS)]
            self.assertEqual([actions.count(i) for i in range(4)],[16]*4)

    def test_reject_noncanonical_and_illegal_inputs_atomically(self):
        a=HiddenLawSwitchboard(7,101)
        snap=a.snapshot()
        for bad in (True, -1, 4, "0", 1.0):
            with self.assertRaises(ValueError):
                a.step(bad)
            self.assertEqual(a.snapshot(),snap)
        p=json.loads(snap)
        for update in (
            lambda d:d.update(schema="broken"),
            lambda d:d.update(steps=1000),
            lambda d:d.update(state=-1),
            lambda d:d.update(pending=256),
            lambda d:d.update(law=True),
        ):
            q=dict(p);update(q)
            with self.assertRaises(ValueError):
                HiddenLawSwitchboard.restore(
                    json.dumps(q,sort_keys=True,separators=(",",":"))
                )

    def test_source_only_frozen_headroom_boundary(self):
        base={"episodes":len(TRAIN_LAWS)*len(TRAIN_SEEDS),
              "source_steps":len(TRAIN_LAWS)*len(TRAIN_SEEDS)*STEPS,
              "action_totals":[100,100,100,100],
              "unique_same_public_and_action_different_hidden_law_outcome_keys":8}
        self.assertEqual(stage0_verdict(base,[3,5])["disposition"],
                         "SOURCE_TASK_IDENTIFIABLE_DEV_ONLY")
        base["unique_same_public_and_action_different_hidden_law_outcome_keys"]=7
        self.assertEqual(stage0_verdict(base,[3,5])["disposition"],
                         "SOURCE_TASK_INVALID_NO_GO")
        base["unique_same_public_and_action_different_hidden_law_outcome_keys"]=8
        self.assertEqual(stage0_verdict(base,[3])["disposition"],
                         "SOURCE_TASK_INVALID_NO_GO")


if __name__=="__main__":
    unittest.main()
