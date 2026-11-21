"""KNOW23 frozen quarantine-before-write source, replay, retention, strong controls."""
import json
import unittest

from write_quarantine_memory_dev import (
    FIT, HELD, POLICIES, HAZARD, PREREG, SOURCE_MODE,
    QuarantineWriteMemory, CommonPosteriorReader,
    fit_all, evaluate_one, proof, protocol, validate_world,
    canonical, digest,
)
from tgap21_same_address_dev import TwoSlotMemory, witness


class Know23Tests(unittest.TestCase):
    def test_frozen_new_worlds_and_prereg(self):
        d = protocol()
        self.assertEqual(d["schema"],
            "yggdrasil.know23.quarantined-write-custody-frozen-dev.v1")
        self.assertEqual(PREREG,
            "5d2eb5d552d6fa5c202f422798d1b4e0f7dfcecf")
        self.assertEqual(FIT, (9151, 0, 22, 47, 72))
        self.assertEqual(len(HELD), 8)
        self.assertEqual(sum(64 - x[3] for x in HELD), 192)
        self.assertEqual(len({s for s, _, _, _ in HELD}), len(HELD))
        self.assertTrue(set(s for s, _, _, _ in HELD).isdisjoint(
            {FIT[0], 7501, 8501, 8901, 8903, 8911, 8917, 8923,
             8929, 8933, 8941, 7601, 7607, 7613, 7621}))
        for row in HELD:
            validate_world(row)
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            validate_world((HELD[0][0], HELD[0][1],
                            HELD[1][2], HELD[2][3]))
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            validate_world((HELD[0][0], True, HELD[0][2], HELD[0][3]))

    def test_private_causal_law_not_readout_input(self):
        public = tuple((step, step % 2) for step in range(64))
        for s, role, a, b in HELD:
            self.assertEqual(public,
                tuple((step, step % 2) for step in range(64)))
            result = [witness(s, role, t, t % 2, a, b)
                      for t in range(64)]
            self.assertEqual(set(result), {0, 1})
            self.assertEqual(result, [witness(s, role, t, t % 2, a, b)
                                     for t in range(64)])
        self.assertNotIn("role", QuarantineWriteMemory().__dict__)
        self.assertNotIn("shifts", QuarantineWriteMemory().__dict__)

    def test_quarantine_memory_learns_outcome_and_delays_public_writes(self):
        x, y = QuarantineWriteMemory(), QuarantineWriteMemory()
        x.observe(0, 0, 1)
        y.observe(0, 0, 0)
        self.assertGreater(x.slot_prediction(0, 0),
                           y.slot_prediction(0, 0))
        z = QuarantineWriteMemory()
        for t in range(8):
            z.observe(t, t % 2, int(t % 2 == 0))
        self.assertEqual(z._counted_events(), z.total_witnesses)
        self.assertEqual(z.total_witnesses, 8)
        z.observe(8, 0, 1)
        self.assertEqual(len(z.pending), 1)
        with self.assertRaisesRegex(ValueError, "UNFLUSHED_WORLD"):
            z.new_public_world()
        z.finish_episode()
        self.assertEqual(len(z.pending), 0)
        self.assertEqual(z._counted_events(), z.total_witnesses)
        self.assertEqual(z.new_public_world().next_step, 0)

    def test_checkpoint_roundtrip_and_rejects_tamper_duplicates_replay(self):
        z = QuarantineWriteMemory()
        for t in range(11):
            z.observe(t, t % 2, (t + 1) % 2)
        raw = z.checkpoint()
        cold = QuarantineWriteMemory.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold._counted_events(), z.total_witnesses)
        with self.assertRaises(ValueError):
            QuarantineWriteMemory.restore(raw, "0" * 64)
        corrupt = raw.replace(b'"accepted_native":false',
                              b'"accepted_native":true')
        with self.assertRaises(ValueError):
            QuarantineWriteMemory.restore(corrupt, digest(corrupt))
        duplicate = raw.replace(b'"active":', b'"active":0,"active":')
        with self.assertRaises(ValueError):
            QuarantineWriteMemory.restore(duplicate, digest(duplicate))
        bad = json.loads(raw)
        bad["total_witnesses"] += 1
        edited = canonical(bad)
        with self.assertRaises(ValueError):
            QuarantineWriteMemory.restore(edited, digest(edited))
        with self.assertRaisesRegex(ValueError, "WITNESS_OR_REPLAY"):
            z.observe(10, 0, 1)
        with self.assertRaisesRegex(ValueError, "SOURCE"):
            z.observe(11, 0, 1, source_mode="original_world")

    def test_same_reader_for_both_mechanisms(self):
        orig = CommonPosteriorReader(TwoSlotMemory())
        fixed = CommonPosteriorReader(QuarantineWriteMemory())
        self.assertEqual(orig.forecast(0), fixed.forecast(0))
        self.assertEqual(HAZARD, 1 / 16)
        for t in range(15):
            action = t % 2
            outcome = int(t % 3 == 0)
            orig.observe(t, action, outcome)
            fixed.observe(t, action, outcome)
            self.assertTrue(HAZARD <= orig.weight_slot1 <= 1-HAZARD)
            self.assertTrue(HAZARD <= fixed.weight_slot1 <= 1-HAZARD)
        with self.assertRaisesRegex(ValueError, "READER_SOURCE"):
            fixed.observe(15, 0, 1, source_mode="owner_approved")
        with self.assertRaisesRegex(ValueError, "ACTION"):
            fixed.forecast(True)

    def test_fit_is_one_address_and_preserves_cold_checkpoint(self):
        d = fit_all()
        self.assertEqual(len(d["fit_tape"]), 72)
        self.assertGreater(d["quarantine_bytes"], d["original_bytes"])
        self.assertEqual(d["quarantine"].total_witnesses, 72)
        self.assertEqual(d["original"].total_witnesses, 72)
        self.assertEqual(len(d["quarantine"].pending), 0)
        self.assertEqual(d["quarantine"].new_public_world().total_witnesses, 72)
        self.assertEqual(set(d["A"]), {"quarantine", "original"})
        self.assertEqual(set(d["B"]), {"quarantine", "original"})

    def test_held_witness_and_fitted_capacity_budgets(self):
        fitted = fit_all()
        world = evaluate_one(fitted, HELD[0])
        self.assertEqual(world["actions"], 64)
        self.assertEqual(world["return_actions"], 26)
        self.assertEqual(set(world["loss_sums"]), set(POLICIES))
        self.assertGreater(world["max_candidate_bytes"], 0)
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            evaluate_one(fitted, (9173, 0, 19, 41))

    def test_frozen_scoring_once_and_deterministic_negative_reports(self):
        a, b = proof(), proof()
        self.assertEqual(a["held_brier"], b["held_brier"])
        self.assertEqual(a["return_brier"], b["return_brier"])
        self.assertEqual(a["frozen_predicates"], b["frozen_predicates"])
        self.assertEqual(a["prereg_commit"], PREREG)
        self.assertEqual(a["fit_actions"], 72)
        self.assertEqual(a["held_worlds"], 8)
        self.assertEqual(a["held_actions_per_policy"], 512)
        self.assertEqual(a["return_actions_per_policy"], 192)
        self.assertEqual(a["source_mode"], SOURCE_MODE)
        self.assertEqual(a["held_brier"]["source_only"], .25)
        self.assertEqual(a["return_brier"]["source_only"], .25)
        self.assertEqual(set(a["held_brier"]), set(POLICIES))
        self.assertEqual(set(a["frozen_predicates"]), {
            "H1_overall_vs_original", "H2_return_vs_original",
            "H3_A_drift_reduced", "H4_vs_rolling"})
        self.assertIn(a["development_verdict"], {
            "PROTECTION_SUPPORTED_DEV","MIXED_PROTECTION","PROTECTION_NO_GO"})
        self.assertEqual(a["engineering_gate"], "PASS")
        self.assertEqual(a["scientific_gate"],
            "NO_GO_SYNTHETIC_SOURCE_AND_STRONGEST_CONTROL")
        self.assertFalse(a["accepted_model_or_checkpoint_changed"])
        self.assertFalse(a["original_native_modified"])
        self.assertFalse(a["protected_original_first_use"])
        self.assertEqual(a["deployment"], "NONE")


if __name__ == "__main__":
    unittest.main()
