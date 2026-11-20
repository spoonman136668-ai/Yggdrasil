"""Source-free KNOW15 factual cue identifiability/negative tests."""
import unittest
from same_slot_blind_regime_dev import (
    SEEDS, CUES, FIT, N, subject, object_id, world
)
from source_only_regime_leakage import select_cue_without_actions


class FactsOnly:
    """Only exposes source membership. No actions or reward API."""
    def __init__(self, seed_index=0, *, source_mode="engineering_fixture_only"):
        self.rows = set()
        self.mode = source_mode
        for task in (0, 1):
            _private_role, modes, columns = world(seed_index, task)
            for entity in range(N):
                q = subject(seed_index, task, entity)
                self.rows.add((q, 960, object_id(task, 4, modes[entity])))
                for feature, predicate in enumerate(CUES):
                    self.rows.add((
                        q, predicate,
                        object_id(task, feature, columns[feature][entity])))

    def fact(self, q, p, o):
        present = (q, p, o) in self.rows
        return {
            "classification": (
                "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if present else "UNKNOWN_ABSTAIN"),
            "source_mode": self.mode,
            "witnessed": present,
            "source_provenance": "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
            "native_accepted": False,
            "verified_new_real_knowledge": False,
            "can_write_causal_consequence": False
        }


class Know15Tests(unittest.TestCase):
    def test_source_only_falsifies_role_identification_necessity(self):
        for i, seed in enumerate(SEEDS):
            facts = FactsOnly(i)
            result = select_cue_without_actions(facts, i)
            self.assertEqual(
                result["status"], "SOURCE_ONLY_UNIQUE_REGIME_CUE")
            # Only a POST-selection evaluator checks hidden labels.
            self.assertEqual(result["cue"], world(i, 0)[0])
            self.assertEqual(result["selected_predicate"],
                             CUES[world(i, 0)[0]])
            self.assertEqual(result["readouts"], 256)
            self.assertEqual(result["membership_probes"], 512)
            self.assertEqual(result["observed_action_outcomes"], 0)

    def test_source_selector_never_requires_mode_or_action_outcomes(self):
        import inspect
        from source_only_regime_leakage import select_cue_without_actions
        src = inspect.getsource(select_cue_without_actions)
        for forbidden in (
            "training_events(", "expected(", "detect(", "world(",
            "NativeContextAccumulator", "MODE_P", "reward(",
            "observed_actions(", "predict("):
            self.assertNotIn(forbidden, src)

    def test_missing_any_candidate_source_fact_fails_closed(self):
        facts = FactsOnly()
        role = world(0, 0)[0]
        q = subject(0, 0, 0)
        facts.rows.remove((q, CUES[role], object_id(0, role, 0)))
        result = select_cue_without_actions(facts, 0)
        self.assertEqual(
            result["status"], "ABSTAIN_UNQUALIFIED_OR_CONFLICTING_SOURCE")

    def test_conflicting_source_bit_fails_closed(self):
        facts = FactsOnly()
        role = world(0, 0)[0]
        facts.rows.add((
            subject(0, 0, 0), CUES[role], object_id(0, role, 1)))
        self.assertEqual(
            select_cue_without_actions(facts, 0)["status"],
            "ABSTAIN_UNQUALIFIED_OR_CONFLICTING_SOURCE")

    def test_forged_source_authority_fails_closed(self):
        facts = FactsOnly(source_mode="claimed_verified_real")
        self.assertEqual(
            select_cue_without_actions(facts, 0)["status"],
            "ABSTAIN_UNQUALIFIED_OR_CONFLICTING_SOURCE")

    def test_duplicate_qualifying_source_cues_abstain(self):
        facts = FactsOnly()
        true = world(0, 0)[0]
        duplicate = (true + 1) % 4
        for task in (0, 1):
            for e in range(FIT):
                q = subject(0, task, e)
                facts.rows.discard(
                    (q, CUES[duplicate],
                     object_id(task, duplicate, 0)))
                facts.rows.discard(
                    (q, CUES[duplicate],
                     object_id(task, duplicate, 1)))
                facts.rows.add(
                    (q, CUES[duplicate],
                     object_id(task, duplicate, task)))
        result = select_cue_without_actions(facts, 0)
        self.assertEqual(
            result["status"], "ABSTAIN_ZERO_OR_MULTIPLE_SOURCE_CUES")
        self.assertEqual(result["candidate_count"], 2)

    def test_without_regime_changing_cue_abstains(self):
        facts = FactsOnly()
        for task in (0, 1):
            for e in range(FIT):
                q = subject(0, task, e)
                for f in range(4):
                    facts.rows.discard(
                        (q, CUES[f], object_id(task, f, 0)))
                    facts.rows.discard(
                        (q, CUES[f], object_id(task, f, 1)))
                    facts.rows.add(
                        (q, CUES[f], object_id(task, f, 0)))
        result = select_cue_without_actions(facts, 0)
        self.assertEqual(
            result["status"], "ABSTAIN_ZERO_OR_MULTIPLE_SOURCE_CUES")
        self.assertEqual(result["candidate_count"], 0)

    def test_held_entities_not_used_to_choose(self):
        facts = FactsOnly()
        before = select_cue_without_actions(facts, 0)
        for task in (0, 1):
            for e in range(FIT, N):
                q = subject(0, task, e)
                for f in range(4):
                    facts.rows.discard(
                        (q, CUES[f], object_id(task, f, 0)))
                    facts.rows.discard(
                        (q, CUES[f], object_id(task, f, 1)))
        self.assertEqual(before, select_cue_without_actions(facts, 0))

    def test_reject_invalid_seed_index_including_bool(self):
        for i in (-1, 3, True):
            with self.assertRaises(ValueError):
                select_cue_without_actions(FactsOnly(), i)

    def test_no_owner_controller_or_training_method(self):
        import source_only_regime_leakage as module
        for forbidden in (
            "activate", "train_canonical", "merge", "deploy",
            "schedule", "observer_owner", "observe_experience"):
            self.assertFalse(hasattr(module, forbidden))


if __name__ == "__main__":
    unittest.main()
