"""WSP215 source-only preflight: verify every frozen group count EXACTLY.

Never generate a WSP215 FIT or held target before source/G29 qualification.
"""
import json
from pathlib import Path
import unittest

from experiment import (WORLDS,PREVIOUS_PRIMARY,PREREG,SCHEMA,metadata,
                        _factor,_git_blob_sha,EXPECTED_BLOB,SRC,
                        ConsensusGate,SurpriseGate,RandomGate,SYNTHETIC_DIGEST)
from verify_parity import compare_receipts,metric


class WSP215ExactPartitionPreflight(unittest.TestCase):
    def test_exact_preregistered_partition_counts_before_any_targets(self):
        p=json.loads((Path(__file__).parent/"prereg.json").read_text("utf-8"))
        self.assertEqual(p["experiment_id"],"WSP-215")
        self.assertEqual(PREREG,"bbb386dec56f01002a16278c8375c7d71b2302a1")
        self.assertEqual(SCHEMA,"wsp215.gate-admission.source-free.v1")
        self.assertEqual([r["seed"] for r in p["design"]["worlds"]],
                         [w[0] for w in WORLDS])
        self.assertEqual(p["source_exact_reuse"]["parent_blob_sha1"],EXPECTED_BLOB)
        self.assertEqual(_git_blob_sha(SRC),EXPECTED_BLOB)
        self.assertFalse(p["controls"]["original_GFP_first_use"])
        self.assertFalse(p["controls"]["training_authority"])
        self.assertFalse(p["controls"]["merge"])
        frozen=p["preflight_only_routing_custody"]["frozen_new_pair_group_counts"]
        self.assertEqual(set(frozen),{str(w[0]) for w in WORLDS})
        for w in WORLDS:
            gene,groups=metadata(w)
            self.assertEqual(gene,f"FABRICATED_WSP215_{w[0]}")
            actual={f"B{s}":len(groups[("FIT",s)]) for s in range(4)}
            actual["PUBLIC_DEV"]=len(groups[("PUBLIC_DEV",None)])
            self.assertEqual(actual,frozen[str(w[0])],
                             msg=f"PREDECLARED ROUTING MISMATCH world={w[0]}")
            self.assertGreaterEqual(actual["PUBLIC_DEV"],3)
            self.assertGreaterEqual(min(actual[f"B{s}"] for s in range(4)),1)
            fit={g for s in range(4) for i,j,g in groups[("FIT",s)]}
            held={g for i,j,g in groups[("PUBLIC_DEV",None)]}
            self.assertFalse(fit & held)
        for old in ((21011,"hub",64),(21101,"hub",24),
                    (21201,"hub",24),(21301,"hub",24),
                    (21403,"hub",24),(21413,"hub",24),
                    (21599,"hub",24)):
            with self.assertRaises(ValueError):
                metadata(old)
            with self.assertRaises(ValueError):
                _factor(old[0],"C",1,0)

    def test_policy_bound_source_and_checkpoint_negative(self):
        self.assertEqual(len(PREVIOUS_PRIMARY),8)
        for cls in (ConsensusGate,SurpriseGate,RandomGate):
            m=cls(SYNTHETIC_DIGEST)
            checkpoint=m.checkpoint()
            self.assertEqual(cls.restore(checkpoint,SYNTHETIC_DIGEST).checkpoint(),checkpoint)
            bad_source = "0"*64 if SYNTHETIC_DIGEST != "0"*64 else "1"*64
            with self.assertRaises(ValueError):
                cls.restore(checkpoint,bad_source)
            with self.assertRaises(ValueError):
                cls.restore(checkpoint[:-1]+b" ",SYNTHETIC_DIGEST)
        with self.assertRaises(ValueError):
            ConsensusGate.restore(
                SurpriseGate(SYNTHETIC_DIGEST).checkpoint(),SYNTHETIC_DIGEST)
        for bad in (("F",1,0),("C",-1,0),("C",1,5)):
            with self.assertRaises(ValueError):
                _factor(21503,*bad)

    def test_unchanged_threshold_parity_verifier_fails_closed(self):
        metric("close",0.1,0.100000001)
        for bad in (float("nan"),float("inf"),"bad"):
            with self.assertRaises(ValueError):
                metric("invalid",0,bad)
        with self.assertRaises(ValueError):
            metric("drift",.2,.3)
        with self.assertRaises(ValueError):
            compare_receipts({"schema":"wrong"},{"schema":"wrong"})
        with self.assertRaises(ValueError):
            compare_receipts({"classification":"GATE_ADVANTAGE"},
                             {"classification":"GATE_ADVANTAGE"})


if __name__=="__main__":
    unittest.main()
