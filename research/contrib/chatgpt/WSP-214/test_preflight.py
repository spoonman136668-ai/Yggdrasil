"""WSP214 negative/source preflight: no 214xx target is generated here."""
import json
from pathlib import Path
import unittest

from experiment import (WORLDS,FORBIDDEN,metadata,_factor,gate_inputs,
                        ConsensusGate,SurpriseGate,RandomGate,
                        SYNTHETIC_DIGEST,PREREG,MODELS,RANK,RIDGE)
from verify_parity import metric,compare_receipts


class GateAdmissionPreflight(unittest.TestCase):
    def test_frozen_source_boundary_and_whole_group_disjointness(self):
        p=json.loads((Path(__file__).parent/"prereg.json").read_text("utf-8"))
        self.assertEqual(p["experiment_id"],"WSP-214")
        self.assertEqual(PREREG,"905cbef5df7d1cace00231ea4bcd079c0780a1ef")
        self.assertEqual([w["seed"] for w in p["design"]["worlds"]],
                         [x[0] for x in WORLDS])
        self.assertTrue(FORBIDDEN.isdisjoint({x[0] for x in WORLDS}))
        self.assertFalse(p["controls"]["training_authority"])
        self.assertFalse(p["controls"]["original_GFP_first_use"])
        self.assertFalse(p["controls"]["merge"])
        self.assertEqual(RANK,4)
        self.assertEqual(RIDGE,.2)
        self.assertEqual(len(MODELS),7)
        for w in WORLDS:
            gene,groups=metadata(w)
            self.assertTrue(gene.startswith("FABRICATED_WSP214_"))
            fit={g for stage in range(4)
                 for _,_,g in groups[("FIT",stage)]}
            held={g for _,_,g in groups[("PUBLIC_DEV",None)]}
            self.assertTrue(fit)
            self.assertTrue(held)
            self.assertTrue(fit.isdisjoint(held))
            self.assertTrue(all(groups[("FIT",stage)] for stage in range(4)))
        for old in ((21011,"hub",64),(21101,"hub",24),
                    (21201,"hub",24),(21301,"hub",24),
                    (21499,"hub",24)):
            with self.assertRaises(ValueError):
                metadata(old)

    def test_policy_bound_cold_restore_and_cross_policy_negative(self):
        for cls in (ConsensusGate,SurpriseGate,RandomGate):
            model=cls(SYNTHETIC_DIGEST)
            state=model.checkpoint()
            restored=cls.restore(state,SYNTHETIC_DIGEST)
            self.assertEqual(state,restored.checkpoint())
            self.assertEqual(restored.mode,"always")
            self.assertEqual(restored.rank,4)
            with self.assertRaises(ValueError):
                cls.restore(state,"0"*64)
            with self.assertRaises(ValueError):
                cls.restore(state[:-1]+b" ",SYNTHETIC_DIGEST)
            with self.assertRaises(ValueError):
                ConsensusGate.restore(
                    RandomGate(SYNTHETIC_DIGEST).checkpoint(),
                    SYNTHETIC_DIGEST)
        for old in (21011,21101,21201,21301,99999):
            with self.assertRaises(ValueError):
                _factor(old,"C",1,0)
        with self.assertRaises(ValueError):
            _factor(21401,"F",1,0)
        with self.assertRaises(ValueError):
            _factor(21401,"C",-1,0)

    def test_no_cohort_gate_diagnostic_and_numeric_negatives(self):
        # A standalone in-memory fabricated negative fixture, not a WSP214
        # seed, split or model fit; exercises read-only gate arithmetic.
        from learner import Learner,Sample
        model=Learner(SYNTHETIC_DIGEST,"contradiction",4)
        model.mean=0.0
        model.sd=1.0
        gene="FABRICATED_WSP214_TEST_ONLY"
        a=gene+"\0" + "1\0A\0C"
        b=gene+"\0" + "2\0A\0C"
        rows=[Sample("dev_0",gene+"\0"+"1\0"+"2",a,b,1.2),
              Sample("dev_1",gene+"\0"+"1\0"+"2",a,b,1.3)]
        stats,eligible=gate_inputs(model,rows)
        self.assertEqual(stats["new_addresses"],2)
        self.assertEqual(stats["eligible"],2)
        self.assertEqual(stats["quarter_budget"],1)
        self.assertEqual(stats["k"],1)
        self.assertEqual(len(eligible),2)
        metric("near",.123456789,.123456790)
        for bad in ("x",float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                metric("bad",0,bad)
        with self.assertRaises(ValueError):
            metric("large-drift",.2,.3)
        with self.assertRaises(ValueError):
            compare_receipts({"schema":"other"},{"schema":"other"})
        with self.assertRaises(ValueError):
            compare_receipts({"classification":"GATE_ADVANTAGE"},
                             {"classification":"GATE_ADVANTAGE"})


if __name__=="__main__":
    unittest.main()
