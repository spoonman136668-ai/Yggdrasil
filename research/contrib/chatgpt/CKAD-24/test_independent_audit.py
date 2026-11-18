"""Toy contract negatives; no CKAD24 primary worlds or outcomes are scored."""
import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ckad24_audit_unit",HERE / "independent_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def event(index, *, context=0, first=0, state=0, second=0, reward=0):
    return [str(index), [[context,0],[context,1]], first,state,second,reward]


class IndependentContractTests(unittest.TestCase):
    def test_window_is_total_rows_before_context_filter(self):
        events = [event(i,first=0) for i in range(32)]
        events += [event(i+32,context=1,first=1) for i in range(32)]
        self.assertEqual(audit.coverage_counts(events,0,(0,1)),[0,0])
        self.assertEqual(audit.coverage_counts(events,0,(1,0)),[0,32])

    def test_stage_history_and_reward_independence(self):
        events = [event(0,first=0,state=0,second=1),
                  event(1,first=1,state=0,second=0),
                  event(2,first=0,state=1,second=0)]
        self.assertEqual(audit.coverage_counts(events,0,(0,0)),[2,1])
        self.assertEqual(audit.coverage_counts(events,0,(0,0),0,0),[0,1])
        changed = copy.deepcopy(events)
        for row in changed:
            row[-1] = 1-row[-1]
        self.assertEqual(audit.coverage_counts(changed,0,(0,0),0,0),[0,1])
        with self.assertRaisesRegex(RuntimeError,"COVERAGE_HISTORY"):
            audit.coverage_counts(events,0,(0,0),0,None)

    def test_frozen_gate_arithmetic_and_per_seed_floor(self):
        seeds = []
        for seed in (101,202,303):
            stream = []
            for count in (64,112,160,192):
                values = {arm:{"reward_sum":80,"episodes":96,"pooled_brier":[1,8]}
                          for arm in audit.ARMS}
                values["original_active"]["reward_sum"] = 76
                stream.append({"count":count,"evaluation":values})
            seeds.append({"seed":seed,"stream":stream})
        gates,metrics = audit.development(seeds)
        self.assertTrue(all(gates.values()))
        self.assertEqual(metrics["gain_vs_original"],[1,24])
        result = {"seeds":seeds,"development_gates":gates,"development_metrics":metrics,
                  "development_pass":True,"classification":"DEVELOPMENT_GO"}
        audit.verify_gates(result)
        changed = copy.deepcopy(result)
        changed["development_gates"]["held_gain_vs_original"] = False
        with self.assertRaisesRegex(RuntimeError,"FROZEN_METRICS_GATES"):
            audit.verify_gates(changed)
        # A mean gain cannot hide a harmed replica under the frozen criterion.
        for row in seeds[0]["stream"]:
            row["evaluation"]["coverage_active"]["reward_sum"] = 70
        self.assertFalse(audit.development(seeds)[0]["per_seed_no_reward_loss"])

    def test_stable_hash_keeps_scientific_data_and_excludes_cost(self):
        value = {"scientific_pass":False,"scope":{"actions":4},
                 "resource_accounting":{"child":{"peak":100}},
                 "whole_wall_seconds":1.2,"child_peak_rss_bytes":5,
                 "source_candidate_sha":"a","stable_sha256":"b"}
        self.assertEqual(audit.stable(value),{"scientific_pass":False,"scope":{"actions":4}})


if __name__ == "__main__":
    unittest.main()
