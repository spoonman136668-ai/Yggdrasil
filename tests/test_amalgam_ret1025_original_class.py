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


    def test_recovery_frozen_counts(self):
        self.assertEqual(gate.RECOVERY_K,(0,1,2,4,8,16,32))
        self.assertEqual(gate.ORIGINAL_BAYES_SOURCE_BLOB,
                         "659bcac55aba4e90eb27bccf90e9fb4fc2fc2bce")
        self.assertEqual(gate.STOP_AFTER-gate.STOP_BEFORE,48)

    def test_exact_original_bayesian_class_loaded_portably(self):
        classic=gate._native_pinned_bayes_class()
        obj=classic(32,1/32)
        key=("transition",0,1)
        self.assertEqual(obj.forecast(key),(0.5,0.5))
        for value in (1,0,1,1):
            obj.update(key,value)
        trailing,change=obj.forecast(key)
        self.assertAlmostEqual(trailing,0.7)
        self.assertTrue(0<=change<=1)
        self.assertAlmostEqual(sum(obj.weights[key]),1)

    def test_public_only_control_updates_and_invalid_reject(self):
        ctrl=gate._HistoryControls()
        e=["a"*64,[[0,1],[0,0]],1,0,1,1]
        pre=ctrl.forecast(("transition",0,1))
        ctrl.observe(e)
        self.assertNotEqual(pre,ctrl.forecast(("transition",0,1)))
        self.assertEqual(ctrl.full[("transition",0,1)],[1,0])
        with self.assertRaisesRegex(ValueError,"INVALID_PUBLIC_OUTCOME"):
            ctrl.observe(["b"*64,[[0,1],[0,0]],1,2,1,1])

    def test_no_evaluator_extra_field_accepted(self):
        with self.assertRaises((TypeError,ValueError)):
            gate._paired_keys(["a"*64,[[0,1],[0,0]],1,0,1,1,{"phase":"A"}])


if __name__=="__main__":
    unittest.main()
