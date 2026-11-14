"""WSP86 harness engineering-only checks; no DEV private World is constructed."""
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from experiment import ARMS,PUBLIC,admit_frozen_source,classify,PRE_COMMIT

class HarnessEngineering(unittest.TestCase):
    def test_frozen_protocol_and_source_pins(self):
        sha,p=admit_frozen_source()
        self.assertEqual(len(sha),40)
        self.assertEqual(PRE_COMMIT,"e1bd60aa10d0cab42a1d81284cb23cc1dd9b6222")
        self.assertEqual(ARMS,("debruijn_full_triple","WSP85_hypothesis_active","hash_random"))
        self.assertEqual(len(PUBLIC),16512)
        self.assertEqual(sum(len(x[2])<2 for x in PUBLIC),2688)
        self.assertEqual(sum(len(x[2])==2 for x in PUBLIC),13824)
        self.assertFalse(p["authority"]["scientific_first_use"])

    def test_equal_score_no_gain_classifies_negative(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        records=[]
        for seed in p["worlds"]["unregistered_developer_seeds"]:
            for arm in ARMS:
                rows={
                    "seed":seed,"arm":arm,"stageA_144_digest":str(seed),
                    "paid_actions":384,"stageB_216_coverage":216,
                    "numeric_symbolic_full_parity":True,
                    "numeric_cold_exact_readout":True,
                    "Adam64":{"fully_trained":True},
                    "policy_receipt":{"any_direct_private_source_lookups":False}
                    if arm=="WSP85_hypothesis_active" else None,
                    "operator_receipt":{"learned_operator_receipts":[
                        {"operator_candidates":2} for _ in range(6)]},
                    "scores":{"numeric":{"by_history_length":{
                        "cold_start_length_0_1":{"correct":1344,"wrong_confident":0,"abstain":1344},
                        "reachable_length_2":{"correct":13824,"wrong_confident":0,"abstain":0}}}}
                }
                records.append(rows)
        answer=classify(records,p)
        self.assertEqual(answer["classification"],"DEV_COVERAGE_NEGATIVE")
        self.assertEqual(answer["reachability_diagnostic"],
                         "DEV_REACHABILITY_BOUND_DIAGNOSIS")
        self.assertEqual(answer["debruijn_minus_random_reachable_confident_correct"],0)
        self.assertFalse(answer["checks"]["debruijn_reachable_gain_over_random"])

    def test_public_policies_have_no_private_source_imports(self):
        code=(HERE/"coverage_policy.py").read_text("utf8")
        self.assertNotIn("import source",code)
        harness=(HERE/"experiment.py").read_text("utf8")
        self.assertEqual(harness.count("world.private_truth("),1)
        self.assertIn("all_frozen.append(",harness)
        self.assertIn("scores=score_only_after_all_frozen(world,arm,receipt)",harness)

if __name__=="__main__":
    unittest.main()
