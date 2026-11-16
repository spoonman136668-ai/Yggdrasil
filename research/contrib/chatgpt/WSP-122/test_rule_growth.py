"""WSP-122 source-safe fixtures and negative controls; no primary first-use."""
import json
from unittest import TestCase
import rule_growth as r


class RuleGrowthTests(TestCase):
    def test_growth_parity_cold_and_budget(self):
        report = r.engineering_fixture()
        self.assertEqual(report["schema"], "wsp122.engineering-fixture.v1")
        self.assertFalse(report["scientific_pass"])
        self.assertFalse(report["source_first_use"])
        self.assertFalse(report["native_admission"])
        self.assertTrue(report["cold_ok"])
        self.assertTrue(report["symbolic_anf_matches_numeric"])
        self.assertEqual(report["numeric_evidence_rows"], 24)
        self.assertEqual(report["numeric_slot_bytes"], 64)
        self.assertGreaterEqual(report["numeric_degree"], 2)
        self.assertEqual([x["budget"] for x in report["worlds"]], [12, 4, 4, 4])
        for world in report["worlds"]:
            for arm in world["arms"].values():
                self.assertEqual(sum(arm.values()), 4)
            self.assertEqual(world["arms"]["NO_UPDATE"]["correct"], 0)

    def test_original_protected_and_replay_denied(self):
        for seed in (122000,122047,122800,122863,121800,120800,121900,True):
            with self.subTest(seed=seed), self.assertRaises(PermissionError):
                r.engineering_world(seed)
            with self.subTest(original=seed), self.assertRaises(PermissionError):
                r.original_world(seed)
        a = r.engineering_world(122900)
        b = r.engineering_world(122901)
        self.assertNotEqual(a.subjects, b.subjects)
        self.assertEqual((len(a.legal), len(a.held)), (12, 4))
        self.assertFalse(set(a.legal) & set(a.held))
        source = r.EngineeringSource(a, 4)
        with self.assertRaises(PermissionError):
            source.query(a.held[0])
        for subject in a.legal[:4]:
            source.query(subject)
        with self.assertRaises(PermissionError):
            source.query(a.legal[4])
        with self.assertRaises(PermissionError):
            source.query(a.legal[0])
        self.assertEqual(source.count, 4)

    def test_conflicting_or_duplicate_evidence_rejected(self):
        world = r.engineering_world(122900)
        model = r.NumericRuleMemory()
        source = r.EngineeringSource(world, 4)
        evidence = source.query(world.legal[0])
        model.observe(world, evidence)
        with self.assertRaisesRegex(ValueError, "WSP122_DUPLICATE_EVIDENCE"):
            model.observe(world, evidence)
        other = r.engineering_world(122901)
        other_subject = next(s for s in other.legal
                             if other.feature(s) == evidence.context)
        forged = r.VerifiedObservation(other.seed, other_subject,
                                       evidence.context, 1 - evidence.outcome,
                                       "0" * 64)
        with self.assertRaisesRegex(ValueError, "WSP122_CAUSAL_CONTRADICTION"):
            model.observe(other, forged)
        self.assertEqual(len(model.evidence), 1)

    def test_unlisted_nonlinear_rule_expansion_and_abstention(self):
        world = r.engineering_world(122900)
        source = r.EngineeringSource(world, 12)
        growing = r.NumericRuleMemory()
        fixed = r.NumericRuleMemory(allow_growth=False)
        for subject in world.legal:
            observed = source.query(subject)
            growing.observe(world, observed)
            fixed.observe(world, observed)
        self.assertGreaterEqual(growing.degree, 2)
        self.assertFalse(growing.inconsistent)
        self.assertTrue(fixed.inconsistent)
        for subject in world.legal:
            self.assertEqual(growing.infer(world, subject),
                             r._engineering_law(world.feature(subject)))
            self.assertIsNone(fixed.infer(world, subject))
        self.assertIsNone(r.NumericRuleMemory().infer_context(12))

    def test_cold_digest_and_valid_digest_weight_forgery_denied(self):
        world = r.engineering_world(122900)
        source = r.EngineeringSource(world, 4)
        model = r.NumericRuleMemory()
        for subject in world.legal[:4]:
            model.observe(world, source.query(subject))
        snapshot = model.snapshot()
        self.assertEqual(r.NumericRuleMemory.restore(snapshot).snapshot(), snapshot)
        tampered = json.loads(snapshot)
        tampered["payload"]["weights"][0] += 1
        with self.assertRaisesRegex(ValueError, "WSP122_COLD_DIGEST_INVALID"):
            r.NumericRuleMemory.restore(r.canonical(tampered))
        tampered["sha256"] = r.digest(tampered["payload"])
        with self.assertRaisesRegex(ValueError, "WSP122_COLD_WEIGHT_PROVENANCE"):
            r.NumericRuleMemory.restore(r.canonical(tampered))

    def test_source_blind_active_selection(self):
        world = r.engineering_world(122900)
        model = r.NumericRuleMemory()
        chosen = model.select_query(world, set(world.legal))
        self.assertEqual(chosen, min(world.legal,
                                    key=lambda s: (world.feature(s), s)))
        self.assertIsNone(model.select_query(world, []))
