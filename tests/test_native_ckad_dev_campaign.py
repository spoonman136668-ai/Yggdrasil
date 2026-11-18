"""Bounded two-stage source-owned synthetic learning campaign tests."""
import json
from pathlib import Path
import tempfile
import unittest

from yggdrasil.native_ckad_dev_campaign import run, verify
from yggdrasil.native_context_basis import digest


class DevelopmentCampaignTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.out = Path(temp.name)/"run"

    def test_end_to_end_two_stages_persist_cold_evaluate_and_replay(self):
        result=run(self.out)
        self.assertEqual(result["stages_completed"],2)
        self.assertEqual(result["observations"],12)
        self.assertEqual(result["held_total"],4)
        self.assertNotEqual(result["initial_checkpoint_sha256"],
                            result["final_checkpoint_sha256"])
        self.assertEqual(verify(self.out),result)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["forge_dispatch_authorized"])
        with self.assertRaises(ValueError):
            run(self.out)

    def test_tampered_checkpoint_receipt_evaluation_and_missing_file_rejected(self):
        result=run(self.out)
        path=self.out/"stage-01.native.json"
        contents=path.read_bytes()
        path.write_bytes(contents+b"x")
        with self.assertRaises(ValueError):verify(self.out)
        path.write_bytes(contents)
        path=self.out/"stage-02.receipt.json"; data=json.loads(path.read_bytes())
        data["input_checkpoint_sha256"]="0"*64
        path.write_text(json.dumps(data,sort_keys=True,separators=(",",":")))
        with self.assertRaises(ValueError):verify(self.out)

    def test_missing_and_tampered_evaluation_rejected(self):
        run(self.out)
        path=self.out/"evaluation.json"
        content=path.read_bytes();path.unlink()
        with self.assertRaises(ValueError):verify(self.out)
        path.write_bytes(content.replace(b'"scientific_pass":false',
                                        b'"scientific_pass":true'))
        with self.assertRaises(ValueError):verify(self.out)


if __name__=="__main__":
    unittest.main()
