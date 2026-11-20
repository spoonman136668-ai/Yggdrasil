"""MH07 exact ORIGINAL-archive qualification only. No new source/training."""
from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from research import mh03_checkpoint_bank_readback as bank
from research import mh07_mixed_bank_archive as m


class MH07ArchiveProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a, b = os.getenv("MH07_UBUNTU_ZIP"), os.getenv("MH07_WINDOWS_ZIP")
        if not a or not b:
            raise AssertionError("MH07_AUTHENTIC_ORIGINAL_ZIPS_REQUIRED")
        cls.ubuntu = Path(a)
        cls.windows = Path(b)
        cls.left = m.load_archive(cls.ubuntu, "ubuntu")
        cls.right = m.load_archive(cls.windows, "windows")

    def test_all_20_original_stage_checkpoints_and_dual_os_source(self):
        m.aligned_originals(self.left, self.right)
        self.assertEqual(len(self.left["results"]), 10)
        for row in self.left["results"]:
            for stage in ("a240", "x240"):
                out = m.verify_stage(row, stage)
                self.assertEqual(len(out["cells"]), 8)
                self.assertTrue(all(len(c["weights"]) == 2
                                    for c in out["cells"]))

    def test_256_ways_are_evaluator_only_and_no_native_claim(self):
        result = m.evaluate(self.ubuntu, self.windows)
        self.assertEqual(result["counts"]["original_cohorts"], 10)
        self.assertEqual(result["counts"]["cross_os_original_checkpoints"], 20)
        self.assertEqual(result["counts"]["masks_evaluated_per_cohort"], 256)
        self.assertEqual(len(result["cohorts"]), 10)
        for row in result["cohorts"]:
            self.assertEqual(row["masks_output_old"] +
                             row["masks_output_new"] +
                             row["masks_output_neither_trained_target"], 256)
            self.assertEqual(row["actual_native_selected_mask"], 255)
            self.assertTrue(row["evaluator_masks_only"])
            self.assertEqual(len(row["census_sha256"]), 64)
        self.assertFalse(result["native_retrieval_gain_verified"])
        self.assertFalse(result["scientific_gain_verified"])
        self.assertFalse(result["native_learner_modified"])

    def test_reject_zip_digest_mutation_before_json_parse(self):
        raw = self.ubuntu.read_bytes()
        changed = raw[:-1] + bytes([raw[-1] ^ 1])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tampered-mh05.zip"
            path.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "ARTIFACT_SHA"):
                m.load_archive(path, "ubuntu")
        self.assertEqual(hashlib.sha256(self.ubuntu.read_bytes()).hexdigest(),
                         m.EXPECTED["ubuntu"][0])

    def test_reject_cross_host_modified_checkpoint(self):
        other = copy.deepcopy(self.right)
        other["results"][0]["full_original_checkpoint_hex"]["x240"] = (
            other["results"][0]["full_original_checkpoint_hex"]["a240"])
        with self.assertRaisesRegex(ValueError, "CROSS_OS_ORIGINAL_BYTES"):
            m.aligned_originals(self.left, other)

    def test_reject_checkpoint_corruption_and_wrong_mask(self):
        row = copy.deepcopy(self.left["results"][0])
        original = row["full_original_checkpoint_hex"]["x240"]
        row["full_original_checkpoint_hex"]["x240"] = "ff" + original[2:]
        with self.assertRaises(ValueError):
            m.verify_stage(row, "x240")
        state = m.verify_stage(self.left["results"][0], "x240")
        for bits in ((0,), (0,) * 7 + (2,), (0,) * 7 + (True,)):
            with self.assertRaisesRegex(ValueError, "INVALID_OFFLINE_MASK"):
                m.policy(state, bits)

    def test_original_archive_immutable_before_after_readouts(self):
        before = [hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in (self.ubuntu, self.windows)]
        row = self.left["results"][0]
        state = m.verify_stage(row, "x240")
        source_weights = tuple(c["weights"] for c in state["cells"])
        for bits in ((0,) * 8, (1,) * 8, (0, 1) * 4):
            result = m.policy(state, bits)
            self.assertEqual(len(result), 4)
        self.assertEqual(source_weights,
                         tuple(c["weights"] for c in state["cells"]))
        self.assertEqual(before,
                         [hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (self.ubuntu, self.windows)])


if __name__ == "__main__":
    unittest.main()
