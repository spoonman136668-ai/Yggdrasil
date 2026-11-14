"""WSP102 train-only real KG parser with negative controls, zero real data."""
from io import BytesIO
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from train_source_audit import _parse_id, count_train_rows, SEALED_SOURCE_SHA256

def _fixture(data, n):
    return count_train_rows(BytesIO(data), expected_lines=n,
                            expected_bytes=len(data), max_seconds=2)

class RealTrainSourceTests(unittest.TestCase):
    def test_small_structured_graph(self):
        raw=b"Q1\tP31\tQ5\nQ5\tP279\tQ1\nQ2\tP31\tQ5\nQ1\tP31\tQ1\n"
        r=_fixture(raw,4)
        self.assertEqual(r["train_lines"],4)
        self.assertEqual(r["relation_types"],2)
        self.assertEqual(r["unique_entity_ids_in_train"],3)
        self.assertEqual(r["self_relation_edges"],1)
        self.assertEqual(r["heldout_rows_read"],0)

    def test_malformed_qid_pid_and_source_records_fail_closed(self):
        for raw in (b"Q0\tP31\tQ5\n",b"Q1\tP0\tQ5\n",b"Q1\tP31\tQx\n",
                    b"Q1 P31 Q5\n",b"Q1\tP31\tQ5\textra\n",
                    b"Q1\tP31\tQ5\x00\n"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    _fixture(raw,1)

    def test_budget_and_bad_labels_fail_closed(self):
        with self.assertRaises(ValueError):
            count_train_rows(BytesIO(b"Q1\tP31\tQ5\n"),expected_lines=2,
                             expected_bytes=10,max_seconds=2)
        self.assertEqual(_parse_id(b"Q123",b"Q"),123)
        with self.assertRaises(ValueError):
            _parse_id(b"P5",b"Q")

    def test_provenance_is_frozen_before_first_full_source_row(self):
        self.assertEqual(SEALED_SOURCE_SHA256,
          "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878")


if __name__=="__main__":
    unittest.main()
