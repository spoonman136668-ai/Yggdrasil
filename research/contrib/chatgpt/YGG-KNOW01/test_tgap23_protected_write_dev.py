"""Frozen TGAP23 same-input write-admission/readout-factorial controls."""
import json
import unittest
from tgap23_protected_write_dev import (
    GuardedTwoSlot, PosteriorMix, HELD, FIT, PREREG, ARMS,
    fit, proof, evaluate_world, digest, SOURCE
)
from tgap21_same_address_dev import TwoSlotMemory, witness


class TGAP23Tests(unittest.TestCase):
    def test_frozen_cohort_source_privacy_and_budgets(self):
        self.assertEqual(FIT, (9501, 0, 24, 48, 72))
        self.assertEqual(len(HELD), 10)
        self.assertEqual(sum(64 - w[3] for w in HELD), 234)
        self.assertEqual(len(set(w[0] for w in HELD)), 10)
        self.assertTrue(all(w[0] != FIT[0] for w in HELD))
        for seed, role, first, second in HELD:
            self.assertEqual(
                tuple(witness(seed, role, t, t % 2, first, second)
                      for t in range(64)),
                tuple(witness(seed, role, t, t % 2, first, second)
                      for t in range(64)))

    def test_guard_snapshot_admission_cannot_see_switch_truth(self):
        g = GuardedTwoSlot()
        # Clear confidence built from 8 actual public action-outcome witnesses.
        for step in range(16):
            a = step % 2
            g.observe(step, a, 1 if a == 0 else 0)
        self.assertTrue(g.sealed)
        before = tuple(g.slot_prediction(0, a) for a in (0, 1))
        for step in range(16, 40):
            a = step % 2
            g.observe(step, a, 0 if a == 0 else 1)
        self.assertEqual(before,
                         tuple(g.slot_prediction(0, a) for a in (0, 1)))
        self.assertGreater(g.suppressed, 0)
        self.assertEqual(
            sum(p[1] for slot in g.slots for p in slot) + g.suppressed,
            g.base.total_witnesses)

    def test_true_posterior_readout_only_shares_writer_ledger(self):
        for klass in (TwoSlotMemory, GuardedTwoSlot):
            a, b = klass(), klass()
            selector = PosteriorMix(b)
            for t in range(16):
                action, outcome = t % 2, int(t % 3 == 0)
                a.observe(t, action, outcome)
                selector.observe(t, action, outcome)
                self.assertEqual(a.checkpoint(), b.checkpoint())
            self.assertGreaterEqual(selector.p1, 1 / 16)
            self.assertLessEqual(selector.p1, 15 / 16)

    def test_typed_negative_replay_and_checkpoint_custody(self):
        m = GuardedTwoSlot()
        m.observe(0, 0, 1)
        raw = m.checkpoint()
        self.assertEqual(GuardedTwoSlot.restore(raw, digest(raw)).checkpoint(), raw)
        with self.assertRaises(ValueError):
            GuardedTwoSlot.restore(raw, "0" * 64)
        with self.assertRaises(ValueError):
            GuardedTwoSlot.restore(raw + b" ", digest(raw + b" "))
        with self.assertRaises(ValueError):
            m.observe(0, 0, 1)
        with self.assertRaises(ValueError):
            m.observe(1, True, 1)
        with self.assertRaises(ValueError):
            m.observe(1, 0, 1, source_mode="owner_original_first_use")
        self.assertEqual(SOURCE, "engineering_fixture_only")

    def test_fit_recurrent_writes_and_per_world_equal_tapes(self):
        b = fit()
        self.assertIn(b["guard_sealed_at"], range(-1, 72))
        for model in (b["original"], b["guard"]):
            raw = model.checkpoint()
            cls = type(model)
            self.assertEqual(cls.restore(raw, digest(raw)).checkpoint(), raw)
        receipt = evaluate_world(b, HELD[0])
        self.assertEqual(receipt["budget"], 64)
        self.assertEqual(receipt["return_budget"], 28)
        self.assertEqual(receipt["guards_equal"], 64)
        self.assertEqual(set(receipt["sum_losses"]), set(ARMS))

    def test_preregistered_full_result_and_no_science_promotion(self):
        r = proof()
        self.assertEqual(r["prereg_commit"], PREREG)
        self.assertEqual(r["fit_witnesses"], 72)
        self.assertEqual(r["held_actions_per_policy"], 640)
        self.assertEqual(r["return_actions_per_policy"], 234)
        self.assertEqual(r["write_ledger_parity_steps"], 640)
        self.assertTrue(r["write_ledger_equal_over_readout_arms"])
        self.assertEqual(r["engineering_gate"], "PASS")
        self.assertEqual(r["science_gate"], "DEV_NO_GO_SYNTHETIC_NOT_NATIVE")
        self.assertEqual(r["deployment"], "NONE")
        self.assertFalse(r["canonical_native_modified"])
        self.assertFalse(r["first_use_426"])
        self.assertEqual(r["held_brier"]["source_only"]["all"], .25)
        self.assertEqual(set(r["held_brier"]), set(ARMS))
        self.assertEqual(len(r["frozen_hypotheses"]), 4)
        self.assertIn(r["development_verdict"], (
            "WRITE_RECOVERY_SUPPORTED_DEV",
            "MIXED_WRITE_PROTECTION_DEV", "WRITE_PROTECTION_NO_GO"
        ))
        print("YGG_TGAP23_FROZEN_RECEIPT=" + json.dumps({
            "held_brier": r["held_brier"],
            "hypotheses": r["frozen_hypotheses"],
            "old_A_drift": r["A_readout_drift_after_B"],
            "margins": r["frozen_margins"],
            "science": r["science_gate"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
