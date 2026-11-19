"""CAP01 engineering-only receipt repair negative controls."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from parity_recovery import seal_comparison
from parity import COMPARE_FILES

class ReceiptRecoveryTests(unittest.TestCase):
    def originals(self, root, *, left=10000, right=10500):
        l=root/"linux"
        w=root/"windows"
        l.mkdir()
        w.mkdir()
        for name in COMPARE_FILES:
            a={"science_pass":False,"source_id":"same","verdict":"NO_GO"}
            b=dict(a)
            if name=="result.json":
                a["replicas"]=[
                    {"old_seed":14071,"final_checkpoint_bytes":left},
                    {"old_seed":14072,"final_checkpoint_bytes":left},
                ]
                b["replicas"]=[
                    {"old_seed":14071,"final_checkpoint_bytes":right},
                    {"old_seed":14072,"final_checkpoint_bytes":right},
                ]
            (l/name).write_text(json.dumps(a))
            (w/name).write_text(json.dumps(b))
        return l,w

    def test_actual_byte_lengths_preserved_and_only_one_int_exception(self):
        with tempfile.TemporaryDirectory() as temp:
            l,w=self.originals(Path(temp))
            v=seal_comparison(l,w)
            self.assertTrue(v["source_and_science_verdict_exact"])
            sizes=v["per_file"]["result.json"][
                "serialized_checkpoint_size_receipts"]
            self.assertEqual(len(sizes),2)
            self.assertEqual(sizes[0]["linux_checkpoint_bytes"],10000)
            self.assertEqual(sizes[0]["windows_checkpoint_bytes"],10500)
            self.assertFalse(v["per_file"]["result.json"]["original_exact_bytes"])
            self.assertEqual(len(v["per_file"]["audit.json"][
                "serialized_checkpoint_size_receipts"]),0)

    def test_inconsistent_science_verdict_still_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            l,w=self.originals(Path(temp))
            (w/"audit.json").write_text(json.dumps(
                {"science_pass":True,"source_id":"same","verdict":"NO_GO"}))
            with self.assertRaises(ValueError):
                seal_comparison(l,w)

    def test_unbounded_length_is_not_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            l,w=self.originals(Path(temp),left=10000,right=100000)
            with self.assertRaisesRegex(ValueError,"LEARNED_CHECKPOINT_BOUND"):
                seal_comparison(l,w)

    def test_original_source_hash_mismatch_still_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            l,w=self.originals(Path(temp))
            (w/"audit.json").write_text(json.dumps(
                {"science_pass":False,"source_id":"different",
                 "verdict":"NO_GO"}))
            with self.assertRaises(ValueError):
                seal_comparison(l,w)

if __name__=="__main__":
    unittest.main()
