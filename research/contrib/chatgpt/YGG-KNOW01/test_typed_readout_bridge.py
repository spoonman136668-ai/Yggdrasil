"""KNOW02: no-source fixture-only bridge contracts and negative controls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("know02", HERE / "typed_readout_bridge.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def envelope(*, accepted=False, mode="engineering_fixture_only"):
    native = {
        "schema": mod.NATIVE_SCHEMA,
        "source_mode": mode,
        "accepted_native": accepted,
        "scientific_pass": False,
    }
    joint = {
        "schema": mod.AMALGAM_SCHEMA,
        "native_ascii": mod._canonical(native).decode("ascii"),
        "native_parent_sha256": "a" * 64,
        "specialist_parent_sha256": "b" * 64,
        "action_heads": [{"kind": "transition"}, {"kind": "reward"}],
        "temporal_heads": [{"kind": "transition"}, {"kind": "reward"}],
    }
    return mod._canonical(joint)


def facts_checkpoint(*, admission=False, authenticity="ENGINEERING_FIXTURE_ONLY_NOT_CERTIFIED"):
    return mod._canonical({
        "schema": mod.FACT_SCHEMA,
        "base_manifest_sha256": mod.MANIFEST_SHA,
        "base_train_sha256": mod.HISTORICAL_SHA,
        "evidence": [], "bundles": [],
        "source_authenticity": authenticity,
        "scientific_pass": False,
        "native_admission": admission,
    })


class FakeNative:
    def __init__(self, raw=None):
        self.raw = envelope() if raw is None else raw
        self.plan_calls = 0

    def checkpoint(self):
        return self.raw

    def plan(self, view):
        self.plan_calls += 1
        return {"public_view": view, "native_only": True}


class FakeFacts:
    class Base:
        receipt = {"image_manifest_sha256": mod.MANIFEST_SHA,
                   "source_train_sha256": mod.HISTORICAL_SHA,
                   "native_accepted": False}

    def __init__(self, raw=None):
        self.raw = facts_checkpoint() if raw is None else raw
        self.base = self.Base()
        self.answer = self.hist_fact()
        self.proposal = self.proposed_paths()
        self.fact_calls = 0

    def checkpoint(self):
        return self.raw

    @staticmethod
    def hist_fact():
        return {"classification": "HISTORICAL_TRAIN_FACT", "witnessed": True,
                "subject_q": 1, "relation_p": 2, "object_q": 3,
                "source_train_sha256": mod.HISTORICAL_SHA,
                "source_temporality": "HISTORICAL_NOT_CURRENT",
                "native_accepted": False, "can_write_causal_consequence": False}

    @staticmethod
    def proposed_paths():
        return {"classification": "UNVERIFIED_COMPOSED_PATH_HYPOTHESES",
                "objects": [12, 13],
                "source_train_sha256": mod.HISTORICAL_SHA,
                "candidate_delta_sha256": mod._digest(facts_checkpoint()),
                "native_accepted": False,
                "verified_new_real_knowledge": False,
                "can_write_causal_consequence": False}

    def fact(self, subject, relation, obj):
        self.fact_calls += 1
        return self.answer

    def hypothesize(self, *_args, **_kwargs):
        return self.proposal


def bridge(native=None, facts=None):
    native = FakeNative() if native is None else native
    facts = FakeFacts() if facts is None else facts
    return mod.TypedFactualReadoutBridge(
        native, facts, native_checkpoint_sha256=mod._digest(native.checkpoint()),
        facts_checkpoint_sha256=mod._digest(facts.checkpoint()))


class KnowledgeBridgeTests(unittest.TestCase):
    def test_factual_history_separate_from_native_model(self):
        native, facts = FakeNative(), FakeFacts()
        out = bridge(native, facts).fact(1, 2, 3)
        self.assertEqual(out["evidence_kind"], "HISTORICAL_STORED_QPQ")
        self.assertTrue(out["stored_witness"])
        self.assertFalse(out["native_model_consulted_for_fact"])
        self.assertFalse(out["causal_observation_admitted"])
        self.assertEqual(native.plan_calls, 0)

    def test_synthetic_delta_never_laundered(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(),
            "classification": "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED",
            "source_mode": "engineering_fixture_only",
            "source_provenance": "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
            "verified_new_real_knowledge": False}
        out = bridge(facts=facts).fact(1, 2, 3)
        self.assertEqual(out["evidence_kind"], "SYNTHETIC_ENGINEERING_QPQ")
        self.assertFalse(out["native_model_knowledge_updated"])

    def test_unknown_abstention(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(),
                        "classification": "UNKNOWN_ABSTAIN", "witnessed": False}
        out = bridge(facts=facts).fact(1, 2, 3)
        self.assertEqual(out["evidence_kind"], "UNSUPPORTED_ABSTAIN")

    def test_composed_path_is_unverified_not_native_evidence(self):
        out = bridge().hypotheses(1, 2, 3)
        self.assertEqual(out["unverified_objects"], [12, 13])
        self.assertFalse(out["causal_observation_admitted"])
        self.assertIn("UNVERIFIED", out["classification"])

    def test_reject_false_native_promotion(self):
        native = FakeNative(envelope(accepted=True))
        with self.assertRaisesRegex(ValueError, "UNACCEPTED_NATIVE_ONLY"):
            bridge(native=native)

    def test_reject_false_owner_admission(self):
        facts = FakeFacts(facts_checkpoint(admission=True))
        with self.assertRaisesRegex(ValueError, "UNACCEPTED_FACTUAL_ONLY"):
            bridge(facts=facts)

    def test_reject_self_asserted_source_authenticity(self):
        facts = FakeFacts(facts_checkpoint(authenticity="OWNER_VERIFIED"))
        with self.assertRaisesRegex(ValueError, "UNACCEPTED_FACTUAL_ONLY"):
            bridge(facts=facts)

    def test_mutated_native_checkpoint_detected_on_query(self):
        native, facts = FakeNative(), FakeFacts()
        node = bridge(native, facts)
        native.raw = envelope(mode="fake-other-mode")
        with self.assertRaisesRegex(ValueError, "NATIVE_PIN_MISMATCH"):
            node.fact(1, 2, 3)

    def test_mutating_factual_backend_detected(self):
        native, facts = FakeNative(), FakeFacts()
        node = bridge(native, facts)
        original = facts.fact
        def mutating(*args):
            facts.raw = facts_checkpoint(admission=True)
            return original(*args)
        facts.fact = mutating
        with self.assertRaisesRegex(ValueError, "FACTS_PIN_MISMATCH"):
            node.fact(1, 2, 3)

    def test_forged_historical_claim_denied(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(), "source_train_sha256": "a" * 64}
        with self.assertRaisesRegex(ValueError, "HISTORICAL_FACT_PROVENANCE"):
            bridge(facts=facts).fact(1, 2, 3)

    def test_causal_write_claim_denied(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(), "can_write_causal_consequence": True}
        with self.assertRaisesRegex(ValueError, "FACTUAL_READOUT_CONTRACT"):
            bridge(facts=facts).fact(1, 2, 3)

    def test_forged_hypothesis_rejected(self):
        facts = FakeFacts()
        facts.proposal = {**facts.proposed_paths(), "classification": "OBSERVED_CAUSE"}
        with self.assertRaisesRegex(ValueError, "HYPOTHESES_ARE_NOT_FACTS"):
            bridge(facts=facts).hypotheses(1, 2, 3)

    def test_duplicate_hypothesis_ids_rejected(self):
        facts = FakeFacts()
        facts.proposal = {**facts.proposed_paths(), "objects": [12, 12]}
        with self.assertRaisesRegex(ValueError, "HYPOTHESES_OUTPUT_SHAPE"):
            bridge(facts=facts).hypotheses(1, 2, 3)

    def test_bool_and_zero_identifiers_rejected(self):
        node = bridge()
        for ids in ((True, 2, 3), (0, 2, 3), (-1, 2, 3), (2**32, 2, 3)):
            with self.assertRaisesRegex(ValueError, "INVALID_QPQ_IDENTIFIER"):
                node.fact(*ids)

    def test_denied_training_and_staging(self):
        node = bridge()
        with self.assertRaisesRegex(PermissionError, "NO_FACTUAL_WRITE"):
            node.stage(b"test", "0" * 64)
        with self.assertRaisesRegex(PermissionError, "NO_FACTUAL_WRITE"):
            node.observe_experience()

    def test_native_plan_only_original_public_view(self):
        node = bridge()
        view = ((1, 0), (1, 0))
        out = node.independent_native_plan(view)
        self.assertEqual(out, {"public_view": view, "native_only": True})

    def test_bad_pins_and_source_receipts(self):
        native, facts = FakeNative(), FakeFacts()
        with self.assertRaisesRegex(ValueError, "EXPLICIT_TRUSTED_PINS_REQUIRED"):
            mod.TypedFactualReadoutBridge(native, facts,
                native_checkpoint_sha256="fake", facts_checkpoint_sha256="0" * 64)
        facts.base.receipt = {**facts.base.receipt, "native_accepted": True}
        with self.assertRaisesRegex(ValueError, "PINNED_HISTORICAL_SOURCE_REQUIRED"):
            bridge(native, facts)

    def test_duplicate_json_keys_denied(self):
        native = FakeNative(b'{"schema":1,"schema":2}')
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            bridge(native=native)


if __name__ == "__main__":
    unittest.main()
