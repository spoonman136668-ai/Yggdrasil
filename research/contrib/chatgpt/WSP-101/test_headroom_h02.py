"""H02 prospective DEV task headroom audit; synthetic worlds only."""
from __future__ import annotations

import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from headroom_h02_world import DEV_IDS, PROBES, HELDOUT, observer, collect_active, collect_passive, truth_for_auditor_only
from headroom_h02_symbolic import (
    GRAMMAR, ExactBayes, prior_predict, validate_source,
    is_query_identifiable
)

FREEZE = "9764c6f3c86bb56bfe21a898179fb9470f89a6ee"


def audit():
    start = time.perf_counter_ns()
    observed_digest = hashlib.sha256()
    true_correct = prior_correct = majority_correct = lookup_covered = 0
    alias_counts = []
    identifiable_worlds = 0
    passive = None
    for world in DEV_IDS:
        p = collect_passive(world)
        if passive is None:
            passive = p
        if passive != p:
            raise AssertionError("H02_PASSIVE_LEAK")
        source = collect_active(world)
        validate_source(source)
        observed_digest.update(json.dumps(source, separators=(",", ":")).encode("ascii"))
        model = ExactBayes(source)
        source_clean = tuple(truth_for_auditor_only(world, probe) for probe in PROBES)
        held_clean = tuple(truth_for_auditor_only(world, probe) for probe in HELDOUT)
        valid, aliases = is_query_identifiable(PROBES, HELDOUT, source_clean, held_clean)
        identifiable_worlds += int(valid)
        alias_counts.append(aliases)
        for probe, target in zip(HELDOUT, held_clean):
            true_correct += model.predict(probe) == target
            prior_correct += prior_predict(probe) == target
            majority_correct += target == 0
            lookup_covered += probe in dict(source)
    queries = len(DEV_IDS) * len(HELDOUT)
    bayes_accuracy, majority_accuracy = true_correct / queries, majority_correct / queries
    if identifiable_worlds < len(DEV_IDS):
        classification = "DEV_SOURCE_UNDERIDENTIFIED"
    elif 0.60 <= bayes_accuracy <= 0.92 and bayes_accuracy - majority_accuracy >= 0.10:
        classification = "DEV_NONCEILING_HEADROOM"
    elif bayes_accuracy > 0.92:
        classification = "DEV_SYMBOLIC_CEILING"
    else:
        classification = "DEV_BOTH_CONTROLS_WEAK"
    return {
        "schema": "yggdrasil.wsp101.h02.dev-headroom.v1",
        "classification": classification,
        "preregistration_sha": FREEZE,
        "contexts": len(DEV_IDS),
        "hypotheses": len(GRAMMAR),
        "active_intervention_steps": len(DEV_IDS) * len(PROBES) * 2,
        "heldout_questions": queries,
        "query_identifiable_worlds": identifiable_worlds,
        "true_hypothesis_alias_counts": alias_counts,
        "strong_symbolic_correct": true_correct,
        "passive_only_correct": prior_correct,
        "fixed_zero_correct": majority_correct,
        "exact_lookup_heldout_coverage": lookup_covered,
        "strong_symbolic_accuracy": bayes_accuracy,
        "fixed_zero_accuracy": majority_accuracy,
        "source_transcript_sha256": observed_digest.hexdigest(),
        "whole_process_wall_ns": time.perf_counter_ns() - start,
        "scientific_pass": False,
        "fully_trained_conventional_baseline": False,
        "weight_programming_run": False,
        "original_worlds_used": False,
        "limits": "Known finite four-family grammar, 16 synthetic DEV worlds, delayed noisy public interventions only, no recipient/native weight programming tested."
    }


class H02Tests(unittest.TestCase):
    def test_frozen_actions_and_no_overlap(self):
        self.assertEqual(len(PROBES), 12)
        self.assertEqual(len(HELDOUT), 12)
        self.assertEqual(len(set(PROBES) & set(HELDOUT)), 0)
        self.assertEqual(DEV_IDS, tuple(range(16)))
        self.assertEqual(len(GRAMMAR), 252)

    def test_symbolic_not_importing_oracle(self):
        code = (HERE / "headroom_h02_symbolic.py").read_text("utf-8")
        for needle in ("from headroom_h02_world", "import headroom_h02_world",
                       "truth_for_auditor_only", "._mask", "._family", "_hidden("):
            self.assertNotIn(needle, code)

    def test_passive_cannot_reveal_hidden_rule(self):
        sources = [collect_passive(w) for w in DEV_IDS]
        self.assertTrue(all(s == sources[0] for s in sources))
        self.assertTrue(all(set(s) == {(0, 0)} for s in sources))

    def test_delayed_action_and_observer_fields(self):
        o = observer(0)
        self.assertEqual(set(o.__slots__), {"reset", "step"})
        self.assertEqual(o.reset(), 0)
        self.assertEqual(o.step(PROBES[0]), {"observation": 0, "reward": 0})
        self.assertIn(o.step(0)["observation"], (0, 1))
        with self.assertRaises(ValueError):
            o.step(0)

    def test_original_identifiers_fail_closed(self):
        for bad in (16, 101011, 101101, 101201, 101301, True, None):
            with self.assertRaises(PermissionError):
                observer(bad)

    def test_malformed_actions_rejected(self):
        o = observer(0)
        for bad in (-1, 64, True, None, "3"):
            with self.assertRaises(ValueError):
                o.step(bad)
        o.reset()
        with self.assertRaises(ValueError):
            o.step(1.0)

    def test_exact_symbolic_posterior_is_positive_normalized(self):
        model = ExactBayes(collect_active(0))
        self.assertEqual(len(model.weighted), 252)
        self.assertGreater(model.partition, 0)
        for p in HELDOUT:
            self.assertTrue(0 <= model.posterior_probability_one(p) <= 1)

    def test_tampered_source_fails_closed(self):
        s = collect_active(0)
        with self.assertRaises(ValueError):
            validate_source(s[:-1])
        with self.assertRaises(ValueError):
            validate_source(tuple((p, True) for p, _ in s))
        with self.assertRaises(ValueError):
            validate_source(s[:-1] + (s[0],))

    def test_same_dev_transcripts_repeat_exactly(self):
        self.assertEqual(collect_active(5), collect_active(5))
        self.assertEqual(collect_passive(5), collect_passive(5))

    def test_measured_headroom_classification_is_not_pass(self):
        outcome = audit()
        self.assertIn(outcome["classification"], (
            "DEV_SOURCE_UNDERIDENTIFIED", "DEV_NONCEILING_HEADROOM",
            "DEV_SYMBOLIC_CEILING", "DEV_BOTH_CONTROLS_WEAK"))
        self.assertFalse(outcome["scientific_pass"])
        self.assertFalse(outcome["weight_programming_run"])
        self.assertFalse(outcome["original_worlds_used"])
        print("WSP101_H02_DEV_RESULT=" + json.dumps(outcome, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
