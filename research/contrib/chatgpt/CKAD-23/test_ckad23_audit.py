"""Frozen CKAD23 independent aggregate: source, false alarms, and negative controls."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad23_stream_audit",HERE/"audit.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditControls(unittest.TestCase):
    def test_original_checkpoint_source_pins(self):
        pins=audit.parent_pins()
        self.assertEqual(set(pins),set(audit.SEEDS))
        self.assertTrue(all(audit.valid_sha(v) for v in pins.values()))
        self.assertEqual(audit.PARENT_SHA,
                         "f04cfcac2aa07806a6b942d968119de87bfb6aaf")

    def test_count_based_change_detection_falsification(self):
        class Det(dict):pass
        good=[
          {"identifier":"a"*64,"count":448+49,"score":[16,1]},
          {"identifier":"b"*64,"count":448+98,"score":[20,1]},
          {"identifier":"c"*64,"count":448+145,"score":[21,1]},
        ]
        false=[
          {"identifier":"d"*64,"count":448+20,"score":[24,1]},
          {"identifier":"e"*64,"count":448+89,"score":[20,1]},
        ]
        self.assertEqual(audit.false_alarms(good),0)
        self.assertEqual(audit.false_alarms(good+false),2)
        self.assertEqual(audit.phase(0),("invariant",0))
        self.assertEqual(audit.phase(48),("invariant",0))
        self.assertEqual(audit.phase(64),("terminal_switch",1))
        self.assertEqual(audit.phase(112),("invariant",1))
        self.assertEqual(audit.phase(192),("invariant",0))

    def test_cannot_convert_missing_evidence_into_success(self):
        with self.assertRaisesRegex(ValueError,"SEED_COUNT"):
            audit.aggregate([])
        forged={"schema":"yggdrasil.ckad23.unsignaled-context-development.result.v1",
                "classification":"PARTIAL_SOURCE_PROOF",
                "scientific_pass":True,"accepted_native":True,"deployment":"PRODUCTION"}
        with self.assertRaisesRegex(ValueError,"SEED_COUNT"):
            audit.aggregate([forged])
        self.assertEqual(len(audit.ARMS),8)
        self.assertEqual(len(audit.COUNTS),13)

    def test_stable_hash_ignores_only_execution_metadata(self):
        raw={"source_candidate_sha":"b"*40,
             "wall_seconds":1.1,"scientific_pass":False,
             "rewards":[1,2,3]}
        value=audit.stable(raw)
        raw["wall_seconds"]=9.9
        raw["source_candidate_sha"]="c"*40
        self.assertEqual(value,audit.stable(raw))
        raw["rewards"]=[1,2,4]
        self.assertNotEqual(value,audit.stable(raw))

if __name__=="__main__":unittest.main()
