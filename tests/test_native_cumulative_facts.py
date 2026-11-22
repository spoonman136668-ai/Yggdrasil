"""NKR-08: 256 sequential source observations, 128 protected base facts.

Engineering fixture only; exact symbolic set is the strongest expected
control, not a claim of learned out-of-family science or model acceptance.
"""
from __future__ import annotations

import json
import unittest

from yggdrasil.native_cumulative_facts import (
    BUNDLE_SCHEMA, CumulativeNativeFacts, canonical, digest)
from yggdrasil.native_knowledge_activation import (
    NativeKnowledgeSession, PINNED_MANIFEST_SHA, PINNED_TRAIN_SHA)
from yggdrasil.public_causal_cells import PublicCausalCells

BASE = frozenset((s, p, 1000 + s * 10 + p)
                 for s in range(1, 65) for p in (1, 2))
PHASE_ONE = tuple((s, p, (3000 if p == 3 else 4000) + s)
                  for s in range(1, 65) for p in (3, 4))
PHASE_TWO = tuple((3000+s, 5, 5000+s) for s in range(1, 65)) + tuple(
    (4000+s, 6, 6000+s) for s in range(1, 65))


class SmallSource:
    """Separate unoptimized symbolic exact-record control, no live source."""
    def __init__(self, triples):
        self.facts = frozenset(triples)

    def has_fact(self, s, p, o):
        return (s, p, o) in self.facts

    def objects(self, s, p, *, limit=64, after=0):
        return sorted({o for a, b, o in self.facts
                       if a == s and b == p and o > after})[:limit]

    def close(self):
        pass


def source():
    return NativeKnowledgeSession(SmallSource(BASE), {
        "schema": "yggdrasil.nkr06.offline-factual-activation.v1",
        "image_manifest_sha256": PINNED_MANIFEST_SHA,
        "source_train_sha256": PINNED_TRAIN_SHA,
        "native_accepted": False,
    })


def bundle(source_id, records, kind="direct_public_observation",
           mode="engineering_fixture_only"):
    return canonical({
        "schema": BUNDLE_SCHEMA, "source_id": source_id,
        "source_kind": kind, "source_mode": mode, "records": records})


def batch(prefix, triples, start=0):
    return [[*triple, f"{prefix}:{i:04d}"]
            for i, triple in enumerate(triples, start)]


def phases():
    first = bundle("synthetic-phase1", batch("p1", PHASE_ONE))
    # One publicly observed source identity per provided fact; duplicates in
    # phase two are distinct documented observations, not reusing source_refs.
    second_facts = list(PHASE_TWO) + list(PHASE_ONE[:32]) + sorted(BASE)[:32]
    second = bundle("synthetic-phase2", batch("p2", second_facts))
    return first, second


class NativeCumulativeFactsTests(unittest.TestCase):
    def test_two_phases_256_new_and_original_128_cold_retention(self):
        native = source()
        before = PublicCausalCells().snapshot()
        initial = CumulativeNativeFacts(native)
        original_checkpoint = initial.checkpoint()
        self.assertEqual(initial._facts, frozenset())
        first_raw, second_raw = phases()
        first, first_receipt = initial.stage(first_raw, digest(first_raw))
        self.assertEqual(first_receipt["new_unique_facts"], 128)
        self.assertEqual(first_receipt["total_candidate_delta_facts"], 128)
        self.assertEqual(first_receipt["already_in_historical"], 0)
        self.assertEqual(first_receipt["total_evidence_refs"], 128)
        self.assertEqual(initial.checkpoint(), original_checkpoint)
        self.assertFalse(first_receipt["native_accepted"])
        self.assertFalse(first_receipt["scientific_pass"])
        second, receipt = first.stage(second_raw, digest(second_raw))
        self.assertEqual(receipt["new_unique_facts"], 128)
        self.assertEqual(receipt["already_in_delta"], 32)
        self.assertEqual(receipt["already_in_historical"], 32)
        self.assertEqual(receipt["duplicate_source_refs"], 0)
        self.assertEqual(receipt["total_candidate_delta_facts"], 256)
        self.assertEqual(receipt["total_evidence_refs"], 320)
        self.assertEqual(second._facts, set(PHASE_ONE) | set(PHASE_TWO))
        self.assertEqual(first.checkpoint_sha256, first_receipt["checkpoint_sha256"])
        self.assertNotEqual(first.checkpoint(), second.checkpoint())
        cold = CumulativeNativeFacts(native, second.checkpoint(),
                                     checkpoint_sha256=second.checkpoint_sha256)
        self.assertEqual(cold.checkpoint(), second.checkpoint())
        self.assertEqual(cold._facts, second._facts)
        self.assertEqual(len(cold._facts), 256)
        self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_exact_symbolic_membership_and_no_invented_hypothesis_promotion(self):
        native = source()
        first, second = phases()
        state = CumulativeNativeFacts(native)
        state, _ = state.stage(first, digest(first))
        state, _ = state.stage(second, digest(second))
        expected = set(BASE) | set(PHASE_ONE) | set(PHASE_TWO)
        self.assertEqual(len(expected), 384)
        for s, p, o in sorted(expected):
            prediction = state.fact(s, p, o)
            self.assertTrue(prediction["witnessed"])
            if (s, p, o) not in BASE:
                self.assertEqual(prediction["classification"],
                                 "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED")
                self.assertFalse(prediction["native_accepted"])
                self.assertFalse(prediction["verified_new_real_knowledge"])
                self.assertFalse(prediction["can_write_causal_consequence"])
        for s in range(1, 65):
            for p in range(1, 7):
                wanted = sorted({o for a, b, o in expected if a == s and b == p})
                actual = state.objects(s, p)["objects"]
                self.assertEqual(actual, wanted)
            self.assertEqual(state.hypothesize(s, 3, 5)["objects"], [5000 + s])
            self.assertEqual(state.hypothesize(s, 4, 6)["objects"], [6000 + s])
            self.assertEqual(state.hypothesize(s, 3, 5)["classification"],
                             "UNVERIFIED_COMPOSED_PATH_HYPOTHESES")
            self.assertFalse(state.hypothesize(s, 3, 5)["verified_new_real_knowledge"])
        for s in range(1, 129):
            self.assertEqual(state.fact(s, 15, 999999)["classification"],
                             "UNKNOWN_ABSTAIN")
            self.assertEqual(state.hypothesize(s, 1, 15)["objects"], [])

    def test_duplicate_bundle_noop_and_source_ref_rebind_denied(self):
        native = source()
        first, second = phases()
        initial = CumulativeNativeFacts(native)
        one, _ = initial.stage(first, digest(first))
        repeated, nochange = one.stage(first, digest(first))
        self.assertIs(repeated, one)
        self.assertEqual(nochange["classification"], "DUPLICATE_BUNDLE_NO_CHANGE")
        self.assertEqual(nochange["new_unique_facts"], 0)
        bad = bundle("synthetic-phase1", batch("other", PHASE_ONE))
        with self.assertRaisesRegex(ValueError, "NKR08_SOURCE_ID_REBOUND"):
            one.stage(bad, digest(bad))
        reuse = bundle("synthetic-phase2", [
            [99, 3, 100, "p1:0000"]])
        with self.assertRaisesRegex(ValueError, "NKR08_EVIDENCE_REFERENCE_CONFLICT"):
            one.stage(reuse, digest(reuse))
        self.assertEqual(initial._facts, frozenset())
        self.assertEqual(one._facts, set(PHASE_ONE))

    def test_original_base_covered_observations_not_duplicated(self):
        native = source()
        base_overlap = sorted(BASE)[:64]
        raw = bundle("fixture-references-on-base", batch("b", base_overlap))
        first, rec = CumulativeNativeFacts(native).stage(raw, digest(raw))
        self.assertEqual(rec["new_unique_facts"], 0)
        self.assertEqual(rec["already_in_historical"], 64)
        self.assertEqual(rec["total_candidate_delta_facts"], 0)
        self.assertEqual(rec["total_evidence_refs"], 64)
        self.assertEqual(len(first._facts), 0)
        second_raw = bundle("fixture-aliases-on-base", batch("b2", base_overlap[:8]))
        later, rec2 = first.stage(second_raw, digest(second_raw))
        self.assertEqual(rec2["already_in_historical"], 8)
        self.assertEqual(len(later._facts), 0)
        for triple in base_overlap:
            self.assertEqual(later.fact(*triple)["classification"],
                             "HISTORICAL_TRAIN_FACT")

    def test_forged_digest_source_type_and_tampered_checkpoint_fail_closed(self):
        native = source()
        first, _ = phases()
        state = CumulativeNativeFacts(native)
        with self.assertRaisesRegex(ValueError, "NKR08_BUNDLE_PIN_MISMATCH"):
            state.stage(first, "0" * 64)
        for forbidden_kind in ("inferred_model_hypothesis", "graph_two_hop",
                               "learned_prediction", "heldout_label"):
            raw = bundle("invalid-kind", [], kind=forbidden_kind)
            with self.assertRaises(PermissionError):
                state.stage(raw, digest(raw))
        claimed_real = bundle("self-qualified", [], mode="owner_qualified")
        with self.assertRaises(PermissionError):
            state.stage(claimed_real, digest(claimed_real))
        updated, _ = state.stage(first, digest(first))
        corrupt = updated.checkpoint()[:-1] + b"0"
        with self.assertRaisesRegex(ValueError, "NKR08_CHECKPOINT_PIN_MISMATCH"):
            CumulativeNativeFacts(native, corrupt,
                                  checkpoint_sha256=updated.checkpoint_sha256)
        with self.assertRaisesRegex(ValueError, "NKR08_CHECKPOINT_PIN_MISMATCH"):
            CumulativeNativeFacts(native, updated.checkpoint(),
                                  checkpoint_sha256="0" * 64)
        no_pin = updated.checkpoint()
        with self.assertRaisesRegex(ValueError, "NKR08_CHECKPOINT_PIN_MISMATCH"):
            CumulativeNativeFacts(native, no_pin)
        self.assertEqual(state._facts, frozenset())

    def test_noncanonical_malformed_conflicting_alias_and_capacity(self):
        native = source()
        state = CumulativeNativeFacts(native)
        for bad in (
            [[3, 5, 7, "ref"], [3, 5, 8, "ref"]],
            [[3, 5, 7, "z"], [3, 5, 8, "a"]],
            [[True, 5, 7, "a"]],
            [[3, 5, 7, "../escape"]],
            [[3, 5, 7]],
        ):
            raw = bundle("bad-evidence", bad)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                state.stage(raw, digest(raw))
        raw = bundle("too-many", batch("x", ((3, 5, n) for n in range(1, 1030))))
        with self.assertRaisesRegex(ValueError, "NKR08_BUNDLE_CAPACITY"):
            state.stage(raw, digest(raw))
        good = bundle("nonnormal", batch("a", PHASE_ONE[:1]))
        pretty = json.dumps(json.loads(good), indent=2).encode("ascii")
        with self.assertRaisesRegex(ValueError, "NKR08_BUNDLE_NONCANONICAL"):
            state.stage(pretty, digest(pretty))
        duplicate_json = good.replace(b'"schema":', b'"schema":"duplicate","schema":')
        with self.assertRaisesRegex(ValueError, "NKR08_BUNDLE_JSON"):
            state.stage(duplicate_json, digest(duplicate_json))
        self.assertEqual(state._facts, frozenset())

    def test_reject_base_session_mismatch_and_non_native_controller(self):
        native = source()
        with self.assertRaisesRegex(ValueError, "NKR08_NATIVE_FACT_SESSION_REQUIRED"):
            CumulativeNativeFacts(object())
        native.receipt["native_accepted"] = True
        with self.assertRaisesRegex(ValueError, "NKR08_HISTORICAL_BASE_PIN_DRIFT"):
            CumulativeNativeFacts(native)
        native.receipt["native_accepted"] = False
        native.receipt["image_manifest_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "NKR08_HISTORICAL_BASE_PIN_DRIFT"):
            CumulativeNativeFacts(native)


if __name__ == "__main__":
    unittest.main()
