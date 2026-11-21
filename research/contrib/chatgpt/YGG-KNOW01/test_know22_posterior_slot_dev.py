"""Frozen KNOW22 source-integrity and posterior READOUT isolation tests."""
import copy
import unittest

from know22_posterior_slot_dev import (
    SCHEMA, HELD, HAZARD, POLICIES, PosteriorReadout,
    frozen_protocol, validate_world, score_held, proof,
)
from tgap21_same_address_dev import (
    TwoSlotMemory, fit_memory, witness,
)


class Know22Tests(unittest.TestCase):
    def test_frozen_public_budget_and_new_private_worlds(self):
        p = frozen_protocol()
        self.assertEqual(len(HELD), 8)
        self.assertEqual(len(set(x[0] for x in HELD)), 8)
        self.assertEqual({x[1] for x in HELD}, {0, 1})
        self.assertTrue(all(0 < f < s < 64 for _, _, f, s in HELD))
        self.assertEqual(sum(64 - w[3] for w in HELD), 190)
        self.assertEqual(p["data"]["budget"]["held_actions_per_policy"], 512)
        self.assertTrue(set(x[0] for x in HELD).isdisjoint(
            {7501, 7601, 7607, 7613, 7621, 6451, 6581, 6703,
             6823, 6947, 7069}))

    def test_off_protocol_world_rejected_including_seed_schedule_swap(self):
        validate_world(*HELD[0])
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            validate_world(HELD[0][0], HELD[0][1], *HELD[2][2:])
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            validate_world(True, 0, 12, 36)
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            validate_world(HELD[0][0], 1, 12, 36)

    def test_one_witness_and_original_provenance_still_refused(self):
        state = PosteriorReadout(TwoSlotMemory())
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_OUTCOME"):
            state.observe(0, 0, 1, source_mode="owner_accepted")
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_OUTCOME"):
            state.observe(0, 0, True)
        with self.assertRaisesRegex(ValueError, "SELECTOR_TYPE"):
            PosteriorReadout(TwoSlotMemory(), 0.5)
        with self.assertRaisesRegex(ValueError, "ACTION"):
            state.forecast(True)
        outcome = witness(HELD[0][0], HELD[0][1], 0, 0, *HELD[0][2:])
        state.observe(0, 0, outcome)
        with self.assertRaises(ValueError):
            state.observe(0, 0, outcome)

    def test_posterior_is_bounded_and_uses_preupdate_prediction(self):
        state = PosteriorReadout(TwoSlotMemory())
        self.assertEqual(state.forecast(0), 0.5)
        self.assertEqual(state.weight_slot1, 0.5)
        state.observe(0, 0, 1)
        self.assertGreater(state.weight_slot1, 0)
        self.assertLess(state.weight_slot1, 1)
        self.assertEqual(state.memory.total_witnesses, 1)
        self.assertEqual(HAZARD, 1 / 16)

    def test_new_readout_does_not_change_original_storage(self):
        trained, controls, logs, snapshots = fit_memory()
        baseline = trained.new_public_world()
        candidate = PosteriorReadout(trained.new_public_world())
        self.assertEqual(candidate.memory.checkpoint(), baseline.checkpoint())
        seed, role, first, second = HELD[0]
        for step in range(64):
            action = step % 2
            y = witness(seed, role, step, action, first, second)
            candidate.forecast(action)
            candidate.observe(step, action, y)
            baseline.observe(step, action, y)
            self.assertEqual(candidate.memory.checkpoint(), baseline.checkpoint())
        with self.assertRaisesRegex(ValueError, "FROZEN_WORLD"):
            score_held(trained, controls, seed, role, 20, 44)

    def test_eight_world_budget_and_result_are_deterministic(self):
        a = proof()
        b = proof()
        self.assertEqual(a["schema"], SCHEMA)
        self.assertEqual(a["held_actions_per_policy"], 512)
        self.assertEqual(a["return_actions_per_policy"], 190)
        self.assertEqual(set(a["held_brier"]), set(POLICIES))
        self.assertEqual(a["held_brier"], b["held_brier"])
        self.assertEqual(a["return_brier"], b["return_brier"])
        self.assertEqual(a["frozen_predicates"], b["frozen_predicates"])
        self.assertTrue(a["same_original_memory_after_every_update"])
        self.assertTrue(a["source_only_not_native"])
        self.assertFalse(a["accepted_main_or_checkpoint_changed"])
        self.assertEqual(a["deployment"], "NONE")
        for x in a["held_brier"].values():
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 1)


if __name__ == "__main__":
    unittest.main()
