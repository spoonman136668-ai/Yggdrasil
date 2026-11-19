"""KNOW04: synthetic fixture-only negative controls and shadow readout parity."""
import json
import unittest

from explicit_view_projection import (
    ExplicitPublicViewProjection, canonical, digest, make_fixture_manifest)
from test_typed_readout_bridge import FakeNative, FakeFacts, facts_checkpoint
from typed_readout_bridge import TypedFactualReadoutBridge


class SparseFacts(FakeFacts):
    def fact(self, subject, relation, obj):
        self.fact_calls += 1
        if (subject, relation, obj) == (1, 2, 3):
            return self.answer
        return {**self.hist_fact(), "classification": "UNKNOWN_ABSTAIN",
                "witnessed": False, "subject_q": subject,
                "relation_p": relation, "object_q": obj}


def make_bridge(n, f):
    return TypedFactualReadoutBridge(n, f,
        native_checkpoint_sha256=digest(n.checkpoint()),
        facts_checkpoint_sha256=digest(f.checkpoint()))


def rows():
    return [
        [[1, 2, 3], [[0, 1], [0, 0]]],
        [[7, 8, 9], [[1, 0], [1, 1]]],
    ]


def node(*, entries=None, native=None, facts=None, amend=None):
    native = native or FakeNative()
    facts = facts or SparseFacts()
    seam = make_bridge(native, facts)
    raw, pin = make_fixture_manifest(digest(native.checkpoint()),
                                     digest(facts.checkpoint()),
                                     rows() if entries is None else entries)
    if amend is not None:
        doc = json.loads(raw)
        doc.update(amend)
        raw = canonical(doc)
        pin = digest(raw)
    return ExplicitPublicViewProjection(seam, raw, pin), native, facts


class Know04Tests(unittest.TestCase):
    def test_frozen_historical_fact_has_explicit_view_without_training(self):
        projection, native, facts = node()
        saved_native, saved_facts = native.checkpoint(), facts.checkpoint()
        candidate = projection.query(1, 2, 3)
        self.assertEqual(candidate["classification"], "SYNTHETIC_VIEW_PROPOSAL_ONLY")
        self.assertEqual(candidate["paired_public_views"], [[0, 1], [0, 0]])
        self.assertEqual(candidate["source_fact_kind"], "HISTORICAL_STORED_QPQ")
        self.assertFalse(candidate["real_semantic_grounding"])
        self.assertFalse(candidate["native_training_performed"])
        self.assertEqual(native.plan_calls, 0)
        plan = projection.shadow_plan(1, 2, 3)
        self.assertTrue(plan["native_plan_called"])
        self.assertEqual(plan["shadow_plan"], {"public_view": (0, 1), "native_only": True})
        self.assertEqual(native.plan_calls, 1)
        self.assertFalse(plan["policy_activation"])
        self.assertEqual((native.checkpoint(), facts.checkpoint()), (saved_native, saved_facts))

    def test_unknown_fact_never_calls_planner_even_when_mapped(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(), "classification": "UNKNOWN_ABSTAIN", "witnessed": False}
        projection, native, _ = node(facts=facts)
        result = projection.shadow_plan(1, 2, 3)
        self.assertEqual(result["classification"], "ABSTAIN_UNKNOWN_FACT")
        self.assertFalse(result["native_plan_called"])
        self.assertEqual(native.plan_calls, 0)

    def test_unmapped_fact_abstains_without_proposing_fabricated_view(self):
        projection, native, _ = node()
        self.assertEqual(projection.query(7, 8, 9)["classification"], "ABSTAIN_UNKNOWN_FACT")
        self.assertEqual(projection.query(1, 2, 3)["classification"], "SYNTHETIC_VIEW_PROPOSAL_ONLY")
        projection2, native2, _ = node(entries=[])
        answer = projection2.shadow_plan(1, 2, 3)
        self.assertEqual(answer["classification"], "ABSTAIN_NO_EXPLICIT_VIEW_MAP")
        self.assertFalse(answer["native_plan_called"])
        self.assertEqual(native2.plan_calls, 0)

    def test_synthetic_observation_is_development_only(self):
        facts = FakeFacts()
        facts.answer = {**facts.hist_fact(),
            "classification": "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED",
            "source_mode": "engineering_fixture_only",
            "source_provenance": "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
            "verified_new_real_knowledge": False}
        proposal, native, _ = node(facts=facts)
        answer = proposal.shadow_plan(1, 2, 3)
        self.assertEqual(answer["source_fact_kind"], "SYNTHETIC_ENGINEERING_QPQ")
        self.assertFalse(answer["native_training_performed"])
        self.assertFalse(answer["causal_observation_admitted"])

    def test_external_sha_cannot_be_self_forged(self):
        n, f = FakeNative(), FakeFacts()
        seam = make_bridge(n, f)
        raw, good = make_fixture_manifest(digest(n.checkpoint()), digest(f.checkpoint()), rows())
        with self.assertRaisesRegex(ValueError, "EXTERNAL_MANIFEST_PIN"):
            ExplicitPublicViewProjection(seam, raw, "0" * 64)
        with self.assertRaisesRegex(ValueError, "EXTERNAL_MANIFEST_PIN"):
            ExplicitPublicViewProjection(seam, raw + b" ", good)

    def test_wrong_native_or_fact_checkpoint_refused(self):
        for changed in ({"amalgam_checkpoint_sha256": "a"*64},
                        {"factual_checkpoint_sha256": "b"*64}):
            with self.assertRaisesRegex(ValueError, "BOUND_CHECKPOINT_MISMATCH"):
                node(amend=changed)

    def test_source_claim_and_accepted_model_promotion_refused(self):
        for changed in ({"source_mode": "owner_verified"},
                        {"source_kind": "historical_facts_are_causes"},
                        {"native_accepted": True}, {"scientific_pass": True}):
            with self.assertRaisesRegex(ValueError, "UNQUALIFIED_OR_UNSUPPORTED_MAPPING"):
                node(amend=changed)

    def test_duplicates_unsorted_and_view_collisions_fail(self):
        bads = [
            rows() + [rows()[1]],
            list(reversed(rows())),
            [rows()[0], [[7, 8, 9], [[0, 1], [0, 0]]]],
        ]
        for entries in bads:
            with self.assertRaises(ValueError):
                node(entries=entries)

    def test_view_shape_enforces_native_two_bit_constraints(self):
        bads = [
            [[1,2,3], [[0,1], [1,0]]],
            [[1,2,3], [[True,1], [True,0]]],
            [[1,2,3], [[0,2], [0,1]]],
            [[1,2,3], [[0,0]]],
        ]
        for entry in bads:
            with self.assertRaises(ValueError):
                node(entries=[entry])

    def test_false_or_missing_qpq_denied(self):
        for bad in (0, True, -1, 2**32):
            p, _, _ = node()
            with self.assertRaisesRegex(ValueError, "INVALID_QPQ"):
                p.query(bad, 2, 3)

    def test_changed_native_or_facts_detected_before_plan(self):
        p, native, facts = node()
        native.raw = native.raw + b" "
        with self.assertRaisesRegex(ValueError, "NATIVE_PIN_MISMATCH"):
            p.shadow_plan(1, 2, 3)
        p2, native2, facts2 = node()
        facts2.raw = facts_checkpoint(admission=True)
        with self.assertRaisesRegex(ValueError, "FACTS_PIN_MISMATCH"):
            p2.shadow_plan(1, 2, 3)

    def test_write_surfaces_absent(self):
        p, _, _ = node()
        for method in (p.stage, p.observe_experience):
            with self.assertRaisesRegex(PermissionError, "NO_.*WRITE"):
                method()
        self.assertFalse(hasattr(p, "learn"))

    def test_manifest_determinism_and_cold_recreation(self):
        p, n, f = node()
        assert p.checkpoint() == p.checkpoint()
        x = p.query(1, 2, 3)
        new = ExplicitPublicViewProjection(make_bridge(n, f), p.checkpoint(), digest(p.checkpoint()))
        self.assertEqual(new.query(1, 2, 3), x)

    def test_noncanonical_and_duplicate_json_refused(self):
        n, f = FakeNative(), FakeFacts()
        seam = make_bridge(n, f)
        raw, pin = make_fixture_manifest(digest(n.checkpoint()), digest(f.checkpoint()), rows())
        with self.assertRaisesRegex(ValueError, "NONCANONICAL_MANIFEST"):
            ExplicitPublicViewProjection(seam, raw + b" ", digest(raw + b" "))
        raw2 = b'{"schema":1,"schema":2}'
        with self.assertRaisesRegex(ValueError, "DUPLICATE_KEY"):
            ExplicitPublicViewProjection(seam, raw2, digest(raw2))

    def test_strongest_equal_info_symbolic_control_not_beaten(self):
        p, native, _ = node()
        historical = {(1,2,3)}
        mappings = {(1,2,3): ((0,1),(0,0)), (7,8,9): ((1,0),(1,1))}
        for query in ((1,2,3), (7,8,9)):
            want = query in historical and query in mappings
            got = p.query(*query)["classification"] == "SYNTHETIC_VIEW_PROPOSAL_ONLY"
            self.assertEqual(got, want)
        self.assertEqual(native.plan_calls, 0)


if __name__ == "__main__":
    unittest.main()
