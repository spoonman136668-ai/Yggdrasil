"""F50 real source-artifact admission: negative-only, no DEV first use."""
from hashlib import sha256
import io
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

import f50_source_arm_factory as roles
import f50_comparison_harness as harness
import f50_worlds as world


class F50RealSourcePreflightTests(unittest.TestCase):
    def test_bogus_artifacts_do_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.zip"
            path.write_bytes(b"invalid")
            with self.assertRaisesRegex(roles.SourceAdmissionRejected, "DIGEST_MISMATCH"):
                roles.preflight(path, path, candidate_sha="a"*40)
            with self.assertRaisesRegex(roles.SourceAdmissionRejected, "CANDIDATE_INVALID"):
                roles.preflight(path, path, candidate_sha="invalid")
        with self.assertRaisesRegex(roles.SourceAdmissionRejected, "UNAUDITED_FACTORY"):
            roles.SourceArmFactory({}, {}, "a"*40)

    def test_members_only_and_wrong_inventory_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "toy.zip"
            contents = io.BytesIO()
            with ZipFile(contents, "w") as archive:
                archive.writestr("good.json", b"{}")
            blob = contents.getvalue()
            path.write_bytes(blob)
            self.assertEqual(
                roles.verified_zip(path, sha256(blob).hexdigest(), {"good.json"}),
                {"good.json": b"{}"})
            with self.assertRaisesRegex(roles.SourceAdmissionRejected, "ARCHIVE_INVENTORY"):
                roles.verified_zip(path, sha256(blob).hexdigest(), {"missing.json"})

    def test_routes_and_no_private_evaluator_module(self):
        self.assertEqual(roles.LOWER_ARTIFACT_ID, 14191256763)
        self.assertEqual(len(harness.frozen_plan()), 9)
        self.assertEqual(len(harness.KINDS), 12)
        names = [roles.arm_role(kind) for kind in harness.KINDS]
        self.assertEqual(names.count("conventional"), 3)
        self.assertEqual(names.count("bayesian"), 2)
        self.assertEqual(names.count("native"), 7)
        with self.assertRaisesRegex(roles.SourceAdmissionRejected, "UNKNOWN_ARM"):
            roles.arm_role("target_oracle")
        self.assertNotIn("PrivateTargetEvaluator", roles.__dict__)

    def test_all_512_heldout_predictions_are_retained(self):
        class Limited:
            def __init__(self):
                self.batches = []
            def probabilities(self, episodes):
                self.batches.append(len(episodes))
                assert len(episodes) <= world.PUBLIC_QUERIES
                return tuple((.5, .5, .5) for _ in episodes)
        arm = Limited()
        pred = harness._probabilities(arm, ((0, 0, 0, 0),) * harness.HELDOUT)
        self.assertEqual(len(pred), 512)
        self.assertEqual(arm.batches, [world.PUBLIC_QUERIES])


    def test_cold_roundtrip_rejects_corruption_and_wrong_clone(self):
        class Tiny:
            size = 1024
            seed = 4013
            used = []
            observed_bits = 0
            target_graph_available = False
            pending = None
            awaiting = None
            pool = tuple(range(world.PUBLIC_QUERIES))

            def cold_checkpoint(self):
                return b"frozen.abc"

        arm = Tiny()
        def valid_restorer(packet):
            if packet != b"frozen.abc":
                raise ValueError("tampered")
            return Tiny()
        clone = roles._prove_cold_arm(
            arm, valid_restorer, size=1024, seed=4013,
            kind="native", source_identity=None)
        self.assertEqual(clone.cold_checkpoint(), arm.cold_checkpoint())
        with self.assertRaisesRegex(roles.SourceAdmissionRejected,
                                    "COLD_TAMPER_ACCEPTED"):
            roles._prove_cold_arm(
                arm, lambda packet: Tiny(), size=1024, seed=4013,
                kind="native", source_identity=None)
        with self.assertRaisesRegex(roles.SourceAdmissionRejected,
                                    "COLD_BIT_EXACT_RESTORE"):
            class Broken(Tiny):
                def cold_checkpoint(self):
                    return b"wrong"
            roles._prove_cold_arm(
                arm, lambda packet: Broken(), size=1024, seed=4013,
                kind="native", source_identity=None)

    def test_owner_scope_and_no_private_target_in_source_smoke(self):
        with self.assertRaisesRegex(roles.SourceAdmissionRejected,
                                    "COLD_SOURCE_SCOPE_INVALID"):
            roles.cold_source_arms(object())
        self.assertNotIn("PrivateTargetEvaluator", roles.__dict__)
        self.assertNotIn("DevelopmentEvaluatorClient", roles.__dict__)


    def test_synthetic_public_labels_are_fixed_and_causal(self):
        fn = roles.synthetic_public_bits
        # Every action must be nonzero, distinct and carry 3-7 set bits.
        # These are actual admissible public interventions, not shortcuts.
        self.assertEqual(fn((7, 28, 56, 0)), (1, 1, 1))
        self.assertEqual(fn((14, 28, 56, 0)), (0, 1, 1))
        self.assertEqual(fn((11, 28, 56, 0)), (1, 0, 1))
        self.assertEqual(fn((7, 28, 44, 0)), (1, 1, 0))
        self.assertEqual(fn((7, 28, 56, 1)), (1, 1, 0))
        with self.assertRaises(world.F50Rejected):
            fn((0, 0, 0, 0))
        self.assertNotIn("PrivateTargetEvaluator", roles.__dict__)

    def test_synthetic_only_accepts_qualified_factory(self):
        with self.assertRaisesRegex(roles.SourceAdmissionRejected,
                                    "SYNTHETIC_SCOPE_INVALID"):
            roles.synthetic_single_event_arms(object())
        with self.assertRaisesRegex(roles.SourceAdmissionRejected,
                                    "SYNTHETIC_SCOPE_INVALID"):
            roles.synthetic_single_event_arms(object(), max_cpu_seconds=0)


if __name__ == "__main__":
    unittest.main()
