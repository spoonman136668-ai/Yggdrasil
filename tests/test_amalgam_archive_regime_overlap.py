"""Source-free targeted negatives for read-only archived regime accounting."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "CAUSAL-AMALGAM" / "archive_regime_overlap_audit.py"
spec = importlib.util.spec_from_file_location("arc_overlap", ROOT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ArchiveRegimeOverlapTests(unittest.TestCase):
    def test_sha_digest(self):
        self.assertEqual(m.digest(b"abc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_expected_first_original_id(self):
        self.assertEqual(m.expected_id("ckad25", "ckad25-stream", 56101, 59, "coverage_active"),
                         "8f1966d3d600aac4eb2926ea0e680e653fd16437285c19187651183072d10ed7")
        self.assertNotEqual(m.expected_id("ckad25", "ckad25-stream", 56101, 59, "coverage_active"),
                            m.expected_id("ckad25", "ckad25-stream", 56101, 59, "uniform_random"))

    def test_frozen_segments_contiguous(self):
        self.assertEqual(sum(b-a for _,a,b in m.RANGES),134)
        self.assertEqual([(a,b) for _,a,b in m.RANGES],[(891,912),(912,976),(976,1024),(1024,1025)])

    def test_tampered_archive_rejected_before_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.zip";p.write_bytes(b"not a verified source archive")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_ZIP_PIN"):
                m.read_original_archive(p)

    def test_missing_ep_count_rejected(self):
        with self.assertRaisesRegex(ValueError,"ORIGINAL_LEDGER_COUNT_IDS"):
            m.validate_rows([])

    def test_stage_count_no_duplicate_ids(self):
        rows = [["same",[[0,0],[0,0]],0,0,0,0]]*1025
        with self.assertRaisesRegex(ValueError,"ORIGINAL_LEDGER_COUNT_IDS"):
            m.validate_rows(rows)

    def test_public_shape_guard(self):
        rows = [[str(i),[[0,0],[0,0]],0,0,0,0] for i in range(1025)]
        for i in range(891,1024):
            rows[i][0]=m.expected_id("ckad25","ckad25-stream",56101,i-832,"coverage_active")
        rows[1024][0]=m.expected_id("ckad20","amalgam-growth-engineering-v1",271991,0,"engineering")
        rows[912][1][1][0]=1
        with self.assertRaisesRegex(ValueError,"PUBLIC_EVENT_SHAPE"):
            m.validate_rows(rows)

    def test_stage_id_order_mutation_guard(self):
        rows = [[str(i),[[0,0],[0,0]],0,0,0,0] for i in range(1025)]
        for i in range(891,1024):
            rows[i][0]=m.expected_id("ckad25","ckad25-stream",56101,i-832,"coverage_active")
        rows[1024][0]=m.expected_id("ckad20","amalgam-growth-engineering-v1",271991,0,"engineering")
        rows[913][0],rows[914][0]=rows[914][0],rows[913][0]
        with self.assertRaisesRegex(ValueError,"CKAD25_SOURCE_ID_DRIFT"):
            m.validate_rows(rows)


if __name__=="__main__":
    unittest.main()
