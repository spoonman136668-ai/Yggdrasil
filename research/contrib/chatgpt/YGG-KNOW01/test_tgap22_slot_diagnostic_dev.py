"""TGAP22: frozen causal-slot attribution experiment and negative controls."""
import copy
import json
import unittest

from tgap21_same_address_dev import TwoSlotMemory, witness, digest
from tgap22_slot_diagnostic_dev import (
    FIT, HELD, ARMS, PRIVILEGED, SOURCE,
    evaluator_only_intervention, fit, states_for_world,
    evaluate_one_world, proof,
)


class TGAP22Tests(unittest.TestCase):
    def test_new_preregistered_fixed_worlds_not_tgap21_scoring(self):
        self.assertEqual(FIT, (8501, 0, 24, 48, 72))
        self.assertEqual(HELD, (
            (8603, 0, 15, 40), (8621, 0, 21, 44),
            (8647, 0, 17, 35), (8663, 1, 15, 40),
            (8681, 1, 21, 44), (8699, 1, 17, 35),
        ))
        self.assertEqual(len({w[0] for w in HELD}), 6)
        self.assertEqual(len({FIT[0], *(w[0] for w in HELD)}), 7)
        self.assertEqual(sum(64 - w[3] for w in HELD), 146)
        self.assertEqual(len(ARMS), 9)
        self.assertEqual(len(PRIVILEGED), 4)
        for seed, role, first, second in HELD:
            self.assertTrue(0 < first < second < 64)
            outcomes = tuple(witness(seed, role, t, t % 2, first, second)
                             for t in range(64))
            self.assertEqual(outcomes, tuple(
                witness(seed, role, t, t % 2, first, second)
                for t in range(64)))
            self.assertEqual(set(outcomes), {0, 1})

    def test_fit_custody_and_same_address_readout_interference(self):
        b = fit()
        self.assertEqual(b["fit_witnesses"], 72)
        self.assertEqual(len(b["pristine_A_slot"]), 2)
        self.assertEqual(len(b["A_after_B"]), 2)
        self.assertEqual(len(b["A_after_return"]), 2)
        self.assertTrue(b["checkpoint_restored_exactly"])
        self.assertEqual(
            b["model"].checkpoint(),
            TwoSlotMemory.restore(
                b["model"].checkpoint(),
                digest(b["model"].checkpoint())
            ).checkpoint())
        self.assertIn(b["old_A_drift"], (0, 1, 2))

    def test_evaluator_privilege_does_not_touch_unprivileged_candidate(self):
        b = fit()
        states = states_for_world(b)
        base = states["baseline_fit"]
        old_base = base.checkpoint()
        for label in ("baseline_fit", "no_fit", "rolling_8",
                      "bayes_hmm", "source_only"):
            state = states[label]
            original = copy.deepcopy(getattr(state, "__dict__", {}))
            evaluator_only_intervention(
                label, state, 44, 21, 44, b["pristine_A_slot"])
            self.assertEqual(original, getattr(state, "__dict__", {}))
        self.assertEqual(base.checkpoint(), old_base)
        self.assertEqual(states["baseline_fit"].slots,
                         states["route_only_oracle"].slots)
        evaluator_only_intervention(
            "route_plus_restore_oracle",
            states["route_plus_restore_oracle"], 44, 21, 44,
            b["pristine_A_slot"])
        self.assertEqual(states["route_plus_restore_oracle"].active, 0)
        self.assertEqual(states["route_plus_restore_oracle"].slots[0],
                         b["pristine_A_slot"])
        self.assertEqual(states["baseline_fit"].checkpoint(), old_base)

    def test_each_arm_has_identical_witnessed_evaluation_budget(self):
        b = fit()
        score, routing, tape = evaluate_one_world(b, *HELD[0])
        self.assertEqual(len(tape), 64)
        self.assertEqual(len(score), 9)
        self.assertEqual(len(routing), 6)
        for name in ARMS:
            self.assertEqual(len(score[name]["all"]), 64)
            self.assertEqual(len(score[name]["return"]), 24)
        self.assertEqual(routing["baseline_fit"]["return_steps"], 24)

    def test_replay_and_forged_source_are_rejected(self):
        m = TwoSlotMemory()
        m.observe(0, 0, 1)
        with self.assertRaises(ValueError):
            m.observe(0, 0, 1)
        with self.assertRaises(ValueError):
            m.observe(2, 1, 0)
        with self.assertRaises(ValueError):
            m.observe(1, 1, 0, source_mode="owner_protected")
        self.assertEqual(SOURCE, "engineering_fixture_only")

    def test_frozen_prequential_receipt_and_science_fence(self):
        d = proof()
        self.assertEqual(d["schema"],
                         "yggdrasil.tgap22.sealed-synthetic-diagnostic.v1")
        self.assertEqual(d["prereg_commit"],
                         "0201c733501b8dfe20e6f1e07ea016542814928a")
        self.assertEqual(d["fit_witnessed_actions"], 72)
        self.assertEqual(d["held_witnesses_per_policy"], 384)
        self.assertEqual(d["return_witnesses_per_policy"], 146)
        self.assertEqual(d["worlds"], 6)
        self.assertTrue(d["fit_cold_exact"])
        self.assertEqual(d["engineering_gate"], "PASS")
        self.assertEqual(d["scientific_gate"],
                         "DEV_NO_GO_SYNTHETIC_ORACLE_ATTRIBUTION")
        self.assertFalse(d["canonical_native_modified"])
        self.assertFalse(d["protected_first_use"])
        self.assertEqual(d["deployment"], "NONE")
        self.assertEqual(set(d["brier"]), set(ARMS))
        self.assertEqual(d["brier"]["source_only"]["all"], .25)
        self.assertEqual(d["brier"]["source_only"]["return"], .25)
        for phases in d["brier"].values():
            self.assertTrue(0 <= phases["all"] <= 1)
            self.assertTrue(0 <= phases["return"] <= 1)
        self.assertTrue(
            d["diagnostics"]["oracle_variants_are_not_fair_learners"])
        self.assertEqual(
            set(d["privileged_delta_vs_baseline_return"]), PRIVILEGED)
        print("YGG_TGAP22_FROZEN_RECEIPT=" + json.dumps({
            "fit_transfer_facts": {
                "A_slot_actions_changed_after_B":
                    d["old_A_slot_actions_changed_after_B"],
                "fit_checkpoint_bytes": d["fit_checkpoint_bytes"]
            },
            "held_brier": d["brier"],
            "return_privileged_deltas":
                d["privileged_delta_vs_baseline_return"],
            "diagnostics": d["diagnostics"],
            "held_actions_each": d["held_witnesses_per_policy"],
            "scientific_gate": d["scientific_gate"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
