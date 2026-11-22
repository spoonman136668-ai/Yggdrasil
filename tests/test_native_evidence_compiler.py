"""NKR-04: source-safe native evidence-to-weights staging and safety tests."""
from __future__ import annotations

import json
import unittest

from yggdrasil.native_evidence_compiler import (
    SCHEMA, canonical_json, digest, stage_native_bundle)
from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells


def outcome(slot, context, action):
    """Explicit synthetic development-only public consequence."""
    return action ^ (context & 1) ^ (((context >> 1) & 1)
                                    & ((context >> 2) & 1)) ^ (slot & 1)


def bundle(rows):
    return canonical_json({
        "schema": SCHEMA,
        "source_id": "nkr04-development-fixture-20261116",
        "source_mode": "engineering_fixture_only",
        "source_kind": "observed_public_intervention",
        "license": "synthetic-fixture",
        "records": rows,
    })


def full_rows():
    return [[slot, context, action, outcome(slot, context, action),
             f"fixture:{slot}:{context}:{action}"]
            for slot in range(16) for context in range(16)
            for action in range(2)]


class NativeCompilerTests(unittest.TestCase):
    def test_stage_all_native_slots_and_full_512_observation_capacity(self):
        rows = full_rows()
        raw = bundle(rows)
        staged = stage_native_bundle(raw, digest(raw))
        receipt = staged.receipt
        self.assertEqual(receipt["schema"], "yggdrasil.native-evidence-candidate.v1")
        self.assertEqual(receipt["source_records"], 512)
        self.assertEqual(receipt["unique_added"], 512)
        self.assertEqual(receipt["duplicates_ignored"], 0)
        self.assertEqual(receipt["total_native_observations"], 512)
        self.assertEqual(receipt["populated_native_slots"], 16)
        self.assertFalse(receipt["scientific_pass"])
        self.assertFalse(receipt["native_admission"])
        self.assertFalse(receipt["accepted_main_mutated"])
        self.assertEqual(receipt["source_authenticity"], "UNVERIFIED_EXACT_BYTES_ONLY")
        self.assertEqual(digest(staged.checkpoint),
                         receipt["candidate_checkpoint_sha256"])
        restored = NativeRelationMemory.restore(staged.checkpoint)
        self.assertEqual(restored.unique_observations, 512)
        self.assertEqual(restored.checkpoint(), staged.checkpoint)

    def test_native_verified_decisions_tie_independent_symbolic_lookup(self):
        raw = bundle(full_rows())
        staged = stage_native_bundle(raw, digest(raw))
        memory = NativeRelationMemory.restore(staged.checkpoint)
        incumbent = PublicCausalCells()
        legacy = incumbent.snapshot()
        self.assertEqual(len(legacy), 164)
        independent = {(slot, context, action): outcome(slot, context, action)
                       for slot in range(16) for context in range(16)
                       for action in (0, 1)}
        correct = 0
        for slot in range(16):
            retained = slot >= 7
            address = slot - 7 if retained else slot
            for context in range(16):
                pair = (independent[slot, context, 0],
                        independent[slot, context, 1])
                expected_action = 0 if pair[0] > pair[1] else 1
                self.assertEqual(
                    memory.observed_action_pair(address, context,
                                                retained=retained), pair)
                choice = incumbent.choose_verified_contextual(
                    address, context, memory, retained=retained)
                self.assertEqual(choice, expected_action)
                correct += outcome(slot, context, choice)
        self.assertEqual(correct, 256)
        self.assertEqual(incumbent.snapshot(), legacy)

    def test_incremental_transactional_staging_is_idempotent(self):
        rows = full_rows()
        left, right = bundle(rows[:256]), bundle(rows[256:])
        first = stage_native_bundle(left, digest(left))
        second = stage_native_bundle(right, digest(right),
                                     prior_checkpoint=first.checkpoint)
        whole = bundle(rows)
        direct = stage_native_bundle(whole, digest(whole))
        self.assertEqual(second.checkpoint, direct.checkpoint)
        self.assertEqual(second.receipt["total_native_observations"], 512)
        replay = stage_native_bundle(whole, digest(whole),
                                     prior_checkpoint=direct.checkpoint)
        self.assertEqual(replay.receipt["unique_added"], 0)
        self.assertEqual(replay.receipt["duplicates_ignored"], 512)
        self.assertEqual(replay.checkpoint, direct.checkpoint)

    def test_unsupported_context_preserves_native_fallback(self):
        row = full_rows()[0]  # only one action at slot=0, context=0
        raw = bundle([row])
        staged = stage_native_bundle(raw, digest(raw))
        memory = NativeRelationMemory.restore(staged.checkpoint)
        incumbent = PublicCausalCells()
        incumbent.observe(0, 0, 1)
        incumbent.observe(0, 1, 0)
        baseline = incumbent.choose(0)
        self.assertEqual(incumbent.choose_verified_contextual(0, 0, memory),
                         baseline)
        self.assertEqual(incumbent.choose_verified_contextual(0, 15, memory),
                         baseline)
        self.assertIsNone(memory.observed_action_pair(0, 0))

    def test_duplicate_alias_and_conflicting_source_rejection(self):
        first = full_rows()[0]
        repeated = first[:4] + ["independent-alias-with-same-answer"]
        raw = bundle([first, repeated])
        staged = stage_native_bundle(raw, digest(raw))
        self.assertEqual(staged.receipt["unique_added"], 1)
        self.assertEqual(staged.receipt["duplicates_ignored"], 1)
        bad = first.copy()
        bad[3] = 1 - bad[3]
        conflicting = bundle([first, bad])
        with self.assertRaises(ValueError):
            stage_native_bundle(conflicting, digest(conflicting))
        # Failed compilation could not mutate a previously issued checkpoint.
        self.assertEqual(NativeRelationMemory.restore(staged.checkpoint).checkpoint(),
                         staged.checkpoint)

    def test_unqualified_inferred_graph_triples_and_source_pin_denied(self):
        raw = bundle(full_rows()[:1])
        with self.assertRaisesRegex(ValueError, "NKR04_SOURCE_PIN_MISMATCH"):
            stage_native_bundle(raw, "0" * 64)
        doc = json.loads(raw)
        for forbidden in ("inferred_counterfactual", "knowledge_graph_triple",
                          "held_answer", "model_prediction"):
            doc["source_kind"] = forbidden
            other = canonical_json(doc)
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(PermissionError):
                    stage_native_bundle(other, digest(other))
        doc["source_kind"] = "observed_public_intervention"
        doc["source_mode"] = "owner_qualified"
        other = canonical_json(doc)
        with self.assertRaises(PermissionError):
            stage_native_bundle(other, digest(other))
        doc["source_mode"] = "engineering_fixture_only"
        doc["records"][0][0] = 16
        other = canonical_json(doc)
        with self.assertRaisesRegex(ValueError, "NKR04_BAD_OBSERVATION"):
            stage_native_bundle(other, digest(other))

    def test_noncanonical_duplicate_json_and_tampered_checkpoint_denied(self):
        raw = bundle(full_rows()[:1])
        pretty = json.dumps(json.loads(raw), indent=2).encode("ascii")
        with self.assertRaisesRegex(ValueError, "NKR04_NONCANONICAL_SOURCE"):
            stage_native_bundle(pretty, digest(pretty))
        duplicated_json = raw.replace(b'"license":"synthetic-fixture",',
                                      b'"license":"synthetic-fixture","license":"synthetic-fixture",')
        with self.assertRaisesRegex(ValueError, "NKR04_SOURCE_DOCUMENT_INVALID"):
            stage_native_bundle(duplicated_json, digest(duplicated_json))
        original = stage_native_bundle(raw, digest(raw))
        tampered = bytearray(original.checkpoint)
        tampered[-4] ^= 1
        with self.assertRaises(ValueError):
            stage_native_bundle(raw, digest(raw),
                                prior_checkpoint=bytes(tampered))
        with self.assertRaisesRegex(ValueError, "NKR04_PRIOR_CHECKPOINT_TYPE"):
            stage_native_bundle(raw, digest(raw), prior_checkpoint="not-bytes")

    def test_capacity_limit_order_and_type_negatives(self):
        rows = full_rows()
        oversized = bundle(rows + [rows[-1]])
        with self.assertRaisesRegex(ValueError, "NKR04_SOURCE_CAPACITY"):
            stage_native_bundle(oversized, digest(oversized))
        unordered = bundle([rows[1], rows[0]])
        with self.assertRaisesRegex(ValueError, "NKR04_SOURCE_ORDER_NONCANONICAL"):
            stage_native_bundle(unordered, digest(unordered))
        bad_boolean = bundle([[True, 0, 0, 0, "invalid:bool"]])
        with self.assertRaisesRegex(ValueError, "NKR04_BAD_OBSERVATION"):
            stage_native_bundle(bad_boolean, digest(bad_boolean))
