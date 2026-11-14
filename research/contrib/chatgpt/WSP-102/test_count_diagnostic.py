"""Source-count mismatch diagnostic negatives (synthetic bytes only)."""
from io import BytesIO
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from count_diagnostic import count_train_only, SEALED_SHA

class CountDiagnosticTests(unittest.TestCase):
    def test_exact_and_mismatch_are_different_labels(self):
        data=b"Q1\tP31\tQ5\nQ2\tP31\tQ6\n"
        a=count_train_only(BytesIO(data),expected_bytes=len(data),published_rows=2,max_seconds=5)
        b=count_train_only(BytesIO(data),expected_bytes=len(data),published_rows=3,max_seconds=5)
        self.assertTrue(a["row_count_equal"])
        self.assertEqual(a["observed_relation_types"],1)
        self.assertFalse(b["row_count_equal"])
        self.assertEqual(b["classification"],"SOURCE_PUBLISHED_COUNT_MISMATCH")
        self.assertFalse(a["source_admitted_for_science"])
        self.assertFalse(b["source_admitted_for_science"])

    def test_bad_metadata_fails_closed(self):
        for data in (b"Q1\tP31\tbad\n",b"Q0\tP31\tQ5\n",b"Q1\tP31\tQ5\tX\n",
                     b"Q1 P31 Q5\n",b""):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    count_train_only(BytesIO(data),expected_bytes=20,published_rows=2,max_seconds=5)

    def test_provenance_sha_cannot_be_runtime_selected(self):
        self.assertEqual(SEALED_SHA,
          "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878")

if __name__=="__main__":
    unittest.main()
