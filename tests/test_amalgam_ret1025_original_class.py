"""RET1025 source-only pre-primary guards: no archive replay or source use."""
import hashlib
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0,str(HERE))
import ret1025_original_class as gate


class RET1025OriginalClassSourceTests(unittest.TestCase):
    def test_original_native_source_not_modified(self):
        root=Path(__file__).resolve().parents[1]
        blob=(root/"yggdrasil/native_episode_experience.py").read_bytes()
        git=hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()
        self.assertEqual(git,"5a18b00a4c4131526e71f51d63dfd9eb9471c81e")

    def test_custody_pins_and_historical_scoring_window(self):
        self.assertEqual((gate.STOP_BEFORE,gate.STOP_AFTER,gate.EVENTS_TOTAL),
                         (976,1024,1025))
        self.assertEqual((gate.STREAM_START,gate.REFRESH_START,gate.GROWTH_START),
                         (448,832,1024))
        self.assertEqual(gate.ORIGINAL_RETURN_SHA256,
                         "8064affa804d7f011b86210b3564e99ac714c4f26c6e14f0ec2b924c0a7a0797")
        self.assertEqual(gate.ORIGINAL_EPISODE_SHA256,
                         "3c6433c9e60a0f7e6b750327ae7b705984fb20b25e8bd04fe16a3e9a31c9dde8")

    def test_archive_fail_closed_without_unseen_authentic_bytes(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as root:
            missing=Path(root)/"missing.json"
            with self.assertRaises(FileNotFoundError):
                gate.read_original_archive(missing)
            bad=Path(root)/"original.json"
            for raw in (b"{}", b"", b"not a checkpoint"):
                bad.write_bytes(raw)
                with self.assertRaisesRegex(ValueError, "RET1025_ORIGINAL_JOINT_SHA"):
                    gate.read_original_archive(bad)

    def test_no_partial_or_invalid_public_witness(self):
        for invalid in ((),("id",[[0,0]],0,1,0,1),
                        ("id",[[0,0],[0]],0,1,0,1)):
            with self.assertRaises((TypeError,ValueError,IndexError)):
                gate._public_row(invalid)
        i,v,row=gate._public_row(["id",[[0,1],[0,0]],1,0,1,1])
        self.assertEqual((i,v),("id",((0,1),(0,0))))
        self.assertEqual(row,{"s1":0,"x1":1,"s2":0,"x2":1,"y":1})

    def test_cannot_claim_native_replay_without_original_public_tape(self):
        with self.assertRaisesRegex(ValueError,"RET1025_NO_PRETURN_NATIVE_STATE"):
            gate.original_class_replay([])

    def test_original_retrospective_negative_and_tolerance_are_fixed(self):
        self.assertGreater(gate.EXPECTED_NATIVE, gate.EXPECTED_BETA)
        self.assertAlmostEqual(gate.EXPECTED_NATIVE-gate.EXPECTED_BETA,
                               gate.EXPECTED_NEGATIVE_DELTA,places=12)
        self.assertEqual(gate.PRECISION,1e-9)


if __name__=="__main__":
    unittest.main()
