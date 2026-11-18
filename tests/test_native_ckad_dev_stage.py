"""CKAD development stage: real native train/save/cold restore, fixture only."""
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_ckad_dev_stage import (
    SCHEMA, COMPONENT, SOURCE_REPO, StageDenied,
    checkout_identity, run_fixture_stage,
)


def bootstrap():
    properties = NativePropertyKnowledge("ckad-stage-test", entities=8, context_bits=3)
    facts = [[e, p, (e >> p) & 1] for e in range(8) for p in range(3)]
    properties = properties.stage_properties(facts, digest(canonical(facts)),
                                             source_namespace="ckad-stage-test")
    raw = properties.checkpoint()
    return NativeCumulativeLearner(raw, digest(raw)).checkpoint()


def outcomes():
    return [[x & 7, x >> 3, int((x & 3) == 3)] for x in range(16)]


def payload(rows, *, ref="a"*64):
    return canonical({"source_mode": "engineering_fixture_only",
                      "source_kind": "engineering_public_binary_consequence",
                      "source_ref": ref, "slot": 0, "rows": rows})


def order(checkpoint, packet, *, stage=0):
    sha, tree = checkout_identity()
    return {"schema": SCHEMA, "campaign_id": "ckad-stage-fixture",
            "stage_index": stage, "stage_id": "learn-stage-01",
            "phase": "learn", "source_repo": SOURCE_REPO,
            "source_commit": sha, "source_tree": tree,
            "native_component": COMPONENT,
            "source_mode": "previously-consumed-engineering-fixture-only",
            "source_ref_sha256": "a"*64,
            "input_checkpoint_sha256": digest(checkpoint),
            "packet_sha256": digest(packet), "max_observations": 8,
            "max_wall_seconds": 60, "scientific_first_use": False,
            "forge_dispatch_authorized": False, "promotion_authorized": False,
            "paid_api_calls": 0}


class NativeStageDevelopmentTests(unittest.TestCase):
    def test_two_real_stages_cold_continue_and_preserve_parent(self):
        initial = bootstrap()
        a = payload(outcomes()[:8]); b = payload(outcomes()[8:])
        request = order(initial, a)
        next_raw, proof = run_fixture_stage(
            request, initial, a, checkout_sha=request["source_commit"],
            checkout_tree=request["source_tree"])
        self.assertEqual(proof["observations"], 8)
        self.assertTrue(proof["native_cold_restore_verified"])
        self.assertFalse(proof["scientific_pass"])
        self.assertFalse(proof["forge_dispatch_authorized"])
        self.assertNotEqual(digest(initial), digest(next_raw))
        second = order(next_raw, b, stage=1)
        final, final_proof = run_fixture_stage(
            second, next_raw, b, checkout_sha=second["source_commit"],
            checkout_tree=second["source_tree"])
        m = NativeCumulativeLearner.restore(final, digest(final))
        self.assertEqual([m.predict(0, x & 7, x >> 3) for x in range(16)],
                         [r[2] for r in outcomes()])
        self.assertEqual(m.info()["stored_properties"], 24)
        self.assertEqual(m.info()["events"], 2)
        self.assertEqual(final_proof["input_checkpoint_sha256"], digest(next_raw))
        self.assertEqual(final_proof["output_checkpoint_sha256"], digest(final))
        self.assertEqual(NativeCumulativeLearner.restore(initial,digest(initial))
                         .checkpoint(), initial)

    def test_duplicate_packet_rejected_without_new_training(self):
        original = bootstrap(); packet = payload(outcomes()[:8])
        request = order(original, packet)
        new, _ = run_fixture_stage(request, original, packet,
                                   checkout_sha=request["source_commit"],
                                   checkout_tree=request["source_tree"])
        repeated = order(new, packet, stage=1)
        with self.assertRaisesRegex(StageDenied, "REPLAY_OR_NO_LEARNING"):
            run_fixture_stage(repeated, new, packet,
                              checkout_sha=repeated["source_commit"],
                              checkout_tree=repeated["source_tree"])

    def test_wrong_source_tree_checkpoint_and_rows_denied(self):
        raw = bootstrap(); rows = payload(outcomes()[:8]); req = order(raw, rows)
        for field, altered in (("source_commit", "0"*40),
                               ("source_tree", "0"*40),
                               ("input_checkpoint_sha256", "0"*64),
                               ("packet_sha256", "0"*64),
                               ("native_component", "gpt-token-predictor")):
            bad = dict(req, **{field: altered})
            with self.subTest(field=field), self.assertRaises(StageDenied):
                run_fixture_stage(bad, raw, rows, checkout_sha=req["source_commit"],
                                  checkout_tree=req["source_tree"])
        with self.assertRaises(StageDenied):
            run_fixture_stage(req, raw+b" ", rows,
                              checkout_sha=req["source_commit"],
                              checkout_tree=req["source_tree"])
        with self.assertRaises(StageDenied):
            run_fixture_stage(req, raw, rows+b" ",
                              checkout_sha=req["source_commit"],
                              checkout_tree=req["source_tree"])

    def test_first_use_paid_model_forge_dispatch_promotion_denied(self):
        raw = bootstrap(); packet = payload(outcomes()[:8]); req = order(raw, packet)
        for key, value in (("scientific_first_use", True),
                           ("forge_dispatch_authorized", True),
                           ("promotion_authorized", True),
                           ("paid_api_calls", 1),
                           ("source_mode", "original-science"),
                           ("phase", "evaluate")):
            bad = dict(req, **{key: value})
            with self.subTest(key=key), self.assertRaises(StageDenied):
                run_fixture_stage(bad, raw, packet,
                                  checkout_sha=req["source_commit"],
                                  checkout_tree=req["source_tree"])

    def test_hidden_labels_duplicate_fields_budget_and_wrong_kind_denied(self):
        raw = bootstrap(); packet = payload(outcomes()[:8]); req = order(raw, packet)
        over = dict(req, max_observations=7)
        with self.assertRaises(StageDenied):
            run_fixture_stage(over, raw, packet, checkout_sha=req["source_commit"],
                              checkout_tree=req["source_tree"])
        for bad_packet in (
                packet.replace(b'"rows":',b'"hidden_target":true,"rows":'),
                packet.replace(b'"rows":',b'"rows":[],"rows":'),
                packet.replace(b'engineering_public_binary_consequence',
                               b'correlation_only')):
            changed = dict(req, packet_sha256=digest(bad_packet))
            with self.subTest(packet=bad_packet[:35]), self.assertRaises(StageDenied):
                run_fixture_stage(changed, raw, bad_packet,
                                  checkout_sha=req["source_commit"],
                                  checkout_tree=req["source_tree"])

    def test_conflicting_consequence_is_quarantined_not_rewritten(self):
        raw=bootstrap(); rows=payload(outcomes()[:8]); first=order(raw, rows)
        after,_=run_fixture_stage(first,raw,rows,
                                  checkout_sha=first["source_commit"],
                                  checkout_tree=first["source_tree"])
        # Observe a contradictory outcome for one known action. Native learner
        # must retain original knowledge and record the quarantine.
        packet=payload([[0,0,1]])
        req=order(after,packet,stage=1)
        done,receipt=run_fixture_stage(req,after,packet,
                                      checkout_sha=req["source_commit"],
                                      checkout_tree=req["source_tree"])
        m=NativeCumulativeLearner.restore(done,digest(done))
        self.assertTrue(m.info()["quarantined"][0])
        self.assertIsNone(m.predict(0,0,0))
        self.assertEqual(receipt["observations"],1)


if __name__=="__main__":
    unittest.main()
