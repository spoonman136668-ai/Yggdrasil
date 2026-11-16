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


if __name__ == "__main__":
    unittest.main()
