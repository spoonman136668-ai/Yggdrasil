"""NKR-16: public-action info gain, exact source receipts and negative controls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_active_intervention import (
    NativeActiveIntervention, source_bundle, COLD,
)
from yggdrasil.native_intervention_repair import digest, canonical
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT = (Path(__file__).resolve().parents[1]
          / "research/contrib/chatgpt/NKR-16/experiment.py")
spec = importlib.util.spec_from_file_location("nkr16_frozen_study", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def initial(world=0, mode="unrestricted", policy="active"):
    env = study.environment(world, mode)
    warm, public = study.original_evidence(env, mode)
    original = study.pinned_source(public, "nkr16-test-initial")
    state = NativeActiveIntervention.from_initial_public_source(
        original, digest(original), mode=mode, policy=policy)
    return env, public, state


def selected_receipt(env, state, mode, round_index):
    choice = state.select_next_action()
    if choice is None:
        raise AssertionError("NKR16_TEST_NO_ACTION_AVAILABLE")
    x = choice["context"]
    outcome = study.env_outcome(env, mode, x, 1)
    rows = [(f"test-public-action-{round_index:02d}", x, 1, outcome)]
    source = study.pinned_source(rows, "nkr16-test-receipt")
    return source, choice


class ActiveInterventionQualificationTests(unittest.TestCase):
    def test_frozen_dual_track_strong_controls_and_retention(self):
        result = study.run_frozen()
        self.assertTrue(result["engineering_contract_pass"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertEqual(result["unrestricted_information_gain_advantage"], 0)
        self.assertEqual(result["unrestricted_total_consistent_functions_after_4"], 16)
        self.assertEqual(result["novel_unrestricted_effects_inferred"], 0)
        for policy in ("active", "random"):
            u = result["totals"]["unrestricted"][policy]
            s = result["totals"]["structured"][policy]
            self.assertEqual(u["public_actions"], 48)
            self.assertEqual(u["baseline_correct"], 96)
            self.assertEqual(u["old_retention"], 384)
            self.assertEqual(u["remaining_unprobed_effects"], 48)
            self.assertEqual(u["unprobed_generalization_coverage"], 0)
            self.assertEqual(u["unprobed_generalization_wrong"], 0)
            self.assertTrue(all(x == 16 for x in u["remaining_version_counts"]))
            self.assertEqual(s["public_actions"], 24)
            self.assertEqual(s["baseline_correct"], 96)
            self.assertEqual(s["old_retention"], 384)
            self.assertEqual(s["remaining_unprobed_effects"], 72)
            self.assertEqual(s["unprobed_generalization_wrong"], 0)
        self.assertEqual(len(result["per_world"]), 48)

    def test_unrestricted_choose_observe_only_one_bit_then_128_versions(self):
        env, public, state = initial(7)
        saved = state.checkpoint()
        self.assertEqual(state.candidate_count, 256)
        self.assertEqual(state.select_next_action()["context"], 6)
        self.assertEqual(state.select_next_action()["expected_information_gain_bits"], 1.0)
        self.assertIsNone(state.predict(6, 1)["public_outcome"])
        source, choice = selected_receipt(env, state, "unrestricted", 0)
        after, receipt = state.observe_selected_public_action(source, digest(source))
        self.assertEqual(state.checkpoint(), saved)
        self.assertEqual(receipt["choice"], [6, 1])
        self.assertEqual(after.candidate_count, 128)
        self.assertEqual(after.additional_public_actions, 1)
        self.assertEqual(after.predict(6, 1)["classification"],
                         "DIRECTLY_OBSERVED_ACTION_OUTCOME")
        self.assertEqual(after.predict(6, 1)["public_outcome"],
                         study.env_outcome(env, "unrestricted", 6, 1))
        self.assertIsNone(after.predict(7, 1)["public_outcome"])
        self.assertEqual(after.select_next_action()["context"], 7)
        self.assertFalse(after.predict(6, 1)["can_write_historical_facts"])

    def test_exact_four_probe_limit_and_source_cold_restore(self):
        env, _, state = initial(4)
        before = PublicCausalCells().snapshot()
        original = state.checkpoint()
        for k in range(4):
            source, proposal = selected_receipt(env, state, "unrestricted", k)
            next_, _ = state.observe_selected_public_action(source, digest(source))
            self.assertEqual(state.checkpoint(), original if k == 0 else state.checkpoint())
            state = NativeActiveIntervention(
                next_.checkpoint(), next_.checkpoint_sha256)
        self.assertEqual(state.candidate_count, 16)
        self.assertEqual(state.additional_public_actions, 4)
        self.assertIsNone(state.select_next_action())
        with self.assertRaises(PermissionError):
            state.observe_selected_public_action(source, digest(source))
        for x in COLD:
            if state.predict(x, 1)["classification"] != "DIRECTLY_OBSERVED_ACTION_OUTCOME":
                self.assertIsNone(state.predict(x, 1)["public_outcome"])
        self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_wrong_action_wrong_source_and_duplicate_source_refuse(self):
        env, _, state = initial(1)
        source, choice = selected_receipt(env, state, "unrestricted", 0)
        with self.assertRaisesRegex(ValueError, "NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            state.observe_selected_public_action(source, "0" * 64)
        wrong = json.loads(source)
        wrong["records"][0][1] = 7
        forged = canonical(wrong)
        with self.assertRaisesRegex(ValueError, "NKR16_FEEDBACK_NOT_SELECTED_ACTION"):
            state.observe_selected_public_action(forged, digest(forged))
        wrong = json.loads(source)
        wrong["source_kind"] = "synthetic_verified_owner"
        forged = canonical(wrong)
        with self.assertRaises(PermissionError):
            state.observe_selected_public_action(forged, digest(forged))
        after, _ = state.observe_selected_public_action(source, digest(source))
        with self.assertRaisesRegex(ValueError, "NKR16_REPLAYED_SOURCE_ID"):
            after.observe_selected_public_action(source, digest(source))
        tampered = json.loads(after.checkpoint())
        tampered["receipts"][0]["records"][0][3] ^= 1
        with self.assertRaisesRegex(ValueError, "NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            forged = canonical(tampered)
            NativeActiveIntervention(forged, digest(forged))

    def test_wrong_saved_choice_and_checkpoint_promotion_refuse(self):
        env, _, state = initial(9)
        source, _ = selected_receipt(env, state, "unrestricted", 0)
        after, _ = state.observe_selected_public_action(source, digest(source))
        doc = json.loads(after.checkpoint())
        doc["receipts"][0]["records"][0][1] = 7
        edited = doc["receipts"][0]
        amended = source_bundle(edited["source_id"], edited["records"])
        edited["source_sha256"] = digest(amended)
        with self.assertRaisesRegex(ValueError, "NKR16_SELECTED_ACTION_MISMATCH"):
            payload = canonical(doc)
            NativeActiveIntervention(payload, digest(payload))
        doc = json.loads(after.checkpoint())
        doc["native_accepted"] = True
        with self.assertRaisesRegex(ValueError, "NKR16_CHECKPOINT_CONTRACT_INVALID"):
            payload = canonical(doc)
            NativeActiveIntervention(payload, digest(payload))
        with self.assertRaisesRegex(ValueError, "NKR16_CHECKPOINT_SHA_DRIFT"):
            NativeActiveIntervention(after.checkpoint(), "0" * 64)

    def test_structured_strong_symbolic_selects_same_outcome_and_no_guess(self):
        for world in range(12):
            result = study.run_one_world(world, "structured", "active")
            self.assertEqual(result["new_actions_observed"], 2)
            self.assertEqual(len(result["selected"]), 2)
            self.assertEqual(result["remaining_unprobed_effects"], 6)
            self.assertEqual(result["unprobed_generalization_wrong"], 0)
            self.assertEqual(result["old_retention"], 32)
            self.assertEqual(result["unprobed_generalization_correct"],
                             result["independent_strong_correct"])
            self.assertEqual(result["unprobed_generalization_coverage"],
                             result["independent_strong_coverage"])

    def test_random_policy_is_deterministic_and_source_bound(self):
        env, public, a = initial(10, mode="structured", policy="random")
        _, _, b = initial(10, mode="structured", policy="random")
        self.assertEqual(a.checkpoint_sha256, b.checkpoint_sha256)
        self.assertEqual(a.select_next_action(), b.select_next_action())
        sample, choice = selected_receipt(env, a, "structured", 0)
        a2, _ = a.observe_selected_public_action(sample, digest(sample))
        b2, _ = b.observe_selected_public_action(sample, digest(sample))
        self.assertEqual(a2.checkpoint_sha256, b2.checkpoint_sha256)
        self.assertEqual(a2.select_next_action(), b2.select_next_action())

    def test_invalid_initial_source_outcomes_and_mode_fail_closed(self):
        env, public, _ = initial(0)
        wrong = [list(row) for row in public]
        wrong[1][1], wrong[1][2] = 7, 0
        payload = study.pinned_source(wrong, "nkr16-tamper-source")
        with self.assertRaisesRegex(ValueError, "NKR16_INITIAL_ACTION_SEQUENCE_DRIFT"):
            NativeActiveIntervention.from_initial_public_source(
                payload, digest(payload), mode="unrestricted", policy="active")
        source = study.pinned_source(public, "nkr16-valid-source")
        with self.assertRaises(ValueError):
            NativeActiveIntervention.from_initial_public_source(
                source, digest(source), mode="bad_mode", policy="active")
        with self.assertRaises(ValueError):
            NativeActiveIntervention.from_initial_public_source(
                source, digest(source), mode="structured", policy="bad_policy")


if __name__ == "__main__":
    unittest.main()
