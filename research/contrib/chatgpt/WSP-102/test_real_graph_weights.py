"""WSP102 full-width numeric writer unit controls with fabricated tiny sources."""
from io import BytesIO
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from real_graph_weights import PACK, _positive_id, pack_train_source, TRAIN_ROWS, WEIGHT_BYTES


class NumericCapacityTests(unittest.TestCase):
    def test_three_uint32_numeric_slots_per_known_relation(self):
        records=b"Q1\tP31\tQ5\nQ5\tP279\tQ7\nQ8\tP31\tQ9\nQ1\tP17\tQ30\n"
        proof=pack_train_source(
            BytesIO(records),expected_rows=4,
            expected_bytes=len(records),expected_sha=hashlib.sha256(records).hexdigest(),
            expected_relations=3,max_weight_bytes=1024,max_seconds=8)
        self.assertEqual(proof["numeric_weight_slots"],12)
        self.assertEqual(proof["numeric_weight_bytes"],48)
        self.assertEqual(proof["half_cold_image_bytes"],24)
        self.assertFalse(proof["heldout_truth_read"])
        self.assertEqual(proof["novel_facts_inferred"],0)
        self.assertFalse(proof["scientific_superiority"])

    def test_mismatched_training_sha_or_budget_fails_closed(self):
        row=b"Q1\tP31\tQ5\n"
        for kw in (
            {"expected_rows":1,"expected_bytes":len(row),"expected_sha":"bad","expected_relations":1},
            {"expected_rows":2,"expected_bytes":len(row),"expected_sha":hashlib.sha256(row).hexdigest(),"expected_relations":1},
            {"expected_rows":1,"expected_bytes":len(row),"expected_sha":hashlib.sha256(row).hexdigest(),"expected_relations":2},
            {"expected_rows":1,"expected_bytes":len(row),"expected_sha":hashlib.sha256(row).hexdigest(),"expected_relations":1,"max_weight_bytes":11}
        ):
            with self.subTest(kwargs=kw):
                with self.assertRaises((ValueError,MemoryError,AssertionError)):
                    pack_train_source(BytesIO(row),max_seconds=8,**kw)

    def test_invalid_qid_pid_shape_never_admitted(self):
        for entry in (b"Q0\tP31\tQ5\n", b"Q1\tP0\tQ5\n",
                      b"Q1\tP31\tQ0\n", b"Q1\tP31\tQinvalid\n"):
            with self.subTest(data=entry):
                with self.assertRaises(ValueError):
                    pack_train_source(BytesIO(entry),expected_rows=1,
                        expected_bytes=len(entry),expected_sha=hashlib.sha256(entry).hexdigest(),
                        expected_relations=1,max_seconds=8)

    def test_frozen_maximum_real_data_capacity(self):
        self.assertEqual(TRAIN_ROWS,21343681)
        self.assertEqual(PACK.size,12)
        self.assertEqual(WEIGHT_BYTES,256124172)
        self.assertEqual(_positive_id(b"Q4294967295",b"Q"),4294967295)


if __name__=="__main__":
    unittest.main()
