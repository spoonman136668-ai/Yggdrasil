"""Source-free chronology, admission, retention and matched-cost qualification."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr29_test_audit",
 ROOT/"research/contrib/chatgpt/NKR-29/audit.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def fixture():
    data={}
    for seed in audit.SEEDS:
        rows=[]
        for i in range(31):
            before=i%2;action=(i//2)%2
            reward=int(before==action)
            if i>=24 and i%3==0: reward^=1
            rows.append({"before":before,"action":action,"reward":reward,
                         "after":1-before,"terminated":i==30,"truncated":False})
        data[seed]=rows
    return data

class FeedbackRepairAuditTests(unittest.TestCase):
    def test_full_frozen_native_knowledge_is_present_and_immutable(self):
        data=fixture();bank=audit.initial(data);raw=bank.snapshot()
        result=audit.run_scale(data,28)
        self.assertEqual(result["initial_checkpoint_hex"],raw.hex())
        self.assertEqual(result["arms"]["frozen"]["cold_checkpoint_hex"],raw.hex())
        self.assertEqual(sum(audit.counts(bank)),192)
        self.assertEqual(result["arms"]["frozen"]["checkpoint_bytes"],164)

    def test_future_duplicate_and_malformed_witnesses_reject_atomically(self):
        data=fixture();bank=audit.initial(data);state=audit.arm_state(data,bank.snapshot())
        available={(w,i) for w in range(4) for i in range(24)}
        original=state["bank"].snapshot()
        for index in (24,0):
            with self.assertRaises(ValueError):
                audit.learn(state,data,0,index,available,28)
            self.assertEqual(state["bank"].snapshot(),original)
        available.add((0,24));data[audit.SEEDS[0]][24]["hidden_oracle"]=1
        with self.assertRaises(ValueError):
            audit.learn(state,data,0,24,available,28)
        self.assertEqual(state["bank"].snapshot(),original)
        self.assertEqual(state["updates"],0)

    def test_matched_random_has_same_actual_cost_and_no_repeated_events(self):
        result=audit.run_scale(fixture(),14)
        error=result["arms"]["error_only"]
        self.assertGreater(error["updates_events"],0)
        for seed in audit.RANDOM_SEEDS:
            arm=result["arms"]["random_matched_"+str(seed)]
            self.assertEqual(arm["updates_events"],error["updates_events"])
            self.assertEqual(len({tuple(k) for k in arm["repair_event_ids"]}),arm["updates_events"])
            self.assertEqual(arm["unrelated_posterior_readouts_retained"],24*arm["updates_events"])

    def test_future_final_round_labels_cannot_change_earlier_forecasts(self):
        data=fixture();first=audit.run_scale(data,28)
        for rows in data.values():
            rows[30]["reward"]^=1;rows[30]["after"]^=1
        second=audit.run_scale(data,28)
        for name in audit.ARMS:
            self.assertEqual(first["arms"][name]["pre_final_round_prediction_sha256"],
                             second["arms"][name]["pre_final_round_prediction_sha256"])

    def test_cold_retention_includes_all_original_observation_counts(self):
        for cap in audit.CAPS:
            result=audit.run_scale(fixture(),cap)
            for arm in result["arms"].values():
                bank=audit.PublicCausalCells.restore(bytes.fromhex(arm["cold_checkpoint_hex"]))
                self.assertEqual(sum(audit.counts(bank)),192+arm["outcome_counter_increments"])
                self.assertEqual(arm["retained_original_events"],96)
                self.assertEqual(arm["scored_outputs"],56)
                self.assertLessEqual(arm["updates_events"],cap)

    def test_confidence_rule_is_exact_and_inclusive(self):
        self.assertTrue(audit.wrong_confident(Fraction(3,4),0))
        self.assertTrue(audit.wrong_confident(Fraction(1,4),1))
        self.assertFalse(audit.wrong_confident(Fraction(1,2),0))
        self.assertFalse(audit.wrong_confident(Fraction(3,4),1))
        with self.assertRaises(ValueError):
            audit.run_scale(fixture(),29)

if __name__=="__main__": unittest.main()
