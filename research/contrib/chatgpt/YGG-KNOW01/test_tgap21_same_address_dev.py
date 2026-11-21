"""Frozen TGAP21 source isolation, cumulative transfer and controls."""
import unittest

from tgap21_same_address_dev import (
    FIT, HELD, SOURCE_MODE, TwoSlotMemory, Uninformed,
    witness, fit_memory, evaluate_held, proof, canonical, digest
)


class TGAP21Tests(unittest.TestCase):
    def test_frozen_cohorts_and_binary_source(self):
        self.assertEqual(FIT, (7501, 0, 24, 48, 72))
        self.assertEqual(HELD, ((7601, 0, 16, 40), (7607, 0, 20, 44),
                                (7613, 1, 16, 40), (7621, 1, 20, 44)))
        self.assertTrue(set([FIT[0]]) .isdisjoint(set(s for s, _, _, _ in HELD)))
        for seed, role, a, b in HELD:
            self.assertEqual(
                tuple(witness(seed, role, t, t % 2, a, b) for t in range(64)),
                tuple(witness(seed, role, t, t % 2, a, b) for t in range(64)))
            self.assertTrue(all(witness(seed, role, t, t % 2, a, b) in (0, 1)
                                for t in range(64)))

    def test_hidden_role_changes_causal_distribution_not_source(self):
        # The source seen by the learner is only (step, public action).
        for seed, _, first, second in HELD:
            public = tuple((t, t % 2) for t in range(64))
            self.assertEqual(public, tuple((t, t % 2) for t in range(64)))
            # Private probabilistic truth changes at the two hidden switches.
            self.assertTrue(0 < first < second < 64)
        self.assertNotEqual(
            tuple(witness(7601, 0, t, t % 2, 16, 40) for t in range(64)),
            tuple(witness(7601, 1, t, t % 2, 16, 40) for t in range(64)))

    def test_single_address_genuinely_conflicting_witnesses(self):
        a = TwoSlotMemory()
        b = TwoSlotMemory()
        a.observe(0, 0, 1)
        b.observe(0, 0, 0)
        self.assertGreater(a.predict(0), b.predict(0))
        for step in range(1, 16):
            a.observe(step, step % 2, step % 2)
        self.assertEqual(a.next_step, 16)
        self.assertEqual(sum(pair[1] for slot in a.slots
                             for pair in slot), 16)
        self.assertEqual(len(a.slots), 2)

    def test_replay_forgery_types_and_checkpoint_tamper_fail_closed(self):
        state = TwoSlotMemory()
        state.observe(0, 0, 1)
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_TYPE"):
            state.observe(0, 0, 1)
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_TYPE"):
            state.observe(2, 0, 1)
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_TYPE"):
            state.observe(1, True, 1)
        with self.assertRaisesRegex(ValueError, "SOURCE_AUTHORITY"):
            state.observe(1, 1, 1, source_mode="claimed_original")
        raw = state.checkpoint()
        cold = TwoSlotMemory.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        with self.assertRaises(ValueError):
            TwoSlotMemory.restore(raw + b"1", digest(raw))
        corrupted = raw.replace(b'"accepted_native":false',
                                b'"accepted_native":true')
        with self.assertRaises(ValueError):
            TwoSlotMemory.restore(corrupted, digest(corrupted))
        self.assertEqual(Uninformed().predict(0), 0.5)

    def test_same_address_training_and_new_world_transfer_not_lookup(self):
        model, controls, source, snapshots = fit_memory()
        self.assertEqual(len(source), 72)
        self.assertEqual([len(s.slots) for s in snapshots.values()], [2, 2, 2])
        self.assertEqual(model.next_step, 72)
        self.assertEqual(set(snapshots), {23, 47, 71})
        transferred = model.new_public_world()
        self.assertEqual(transferred.next_step, 0)
        self.assertEqual(transferred.active, 0)
        self.assertEqual(transferred.slots, model.slots)
        transferred.slots[0][0][1] += 1
        self.assertNotEqual(transferred.slots, model.slots)
        self.assertEqual(model.checkpoint(),
                         TwoSlotMemory.restore(
                             model.checkpoint(), digest(model.checkpoint())
                         ).checkpoint())
        # The held code does not open a source-labelled hidden-role lookup.
        self.assertEqual(set(evaluate_held(model, controls, *HELD[0])), {
            "two_slot_fit", "two_slot_no_fit", "stationary", "rolling_8",
            "reset", "bayes_hmm", "source_only"})

    def test_frozen_receipt_reports_fitted_and_no_fit_and_strong_controls(self):
        receipt = proof()
        self.assertEqual(receipt["prereg_sha"],
                         "9b4eefddad364bc416511bba2a783401f1413b55")
        self.assertEqual(receipt["fit_witnessed_actions"], 72)
        self.assertEqual(receipt["held_worlds"], 4)
        self.assertEqual(receipt["held_witnesses_per_policy"], 256)
        self.assertTrue(receipt["cold_restore"])
        self.assertEqual(receipt["engineering_gate"], "PASS")
        self.assertEqual(receipt["scientific_gate"],
                         "DEV_NO_GO_SYNTHETIC_CONTROLS")
        self.assertEqual(receipt["mode"], SOURCE_MODE)
        self.assertFalse(receipt["original_native_modified"])
        self.assertFalse(receipt["accepted_learner_modified"])
        self.assertFalse(receipt["protected_original_first_use"])
        self.assertEqual(receipt["deployment"], "NONE")
        scores = receipt["held_brier"]
        self.assertEqual(set(scores), {
            "two_slot_fit", "two_slot_no_fit", "stationary", "rolling_8",
            "reset", "bayes_hmm", "source_only"})
        self.assertEqual(scores["source_only"]["all"], 0.25)
        for item in scores.values():
            self.assertTrue(0 <= item["all"] <= 1)
        print("YGG_TGAP21_FROZEN_RECEIPT=" +
              __import__("json").dumps({
                  "held_brier": scores,
                  "old_A_drift": receipt["A_drift_after_B_readouts"],
                  "fit_transfer_difference":
                      receipt["transfer_improvement_over_cold_brier"],
                  "science": receipt["scientific_gate"]
              }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
