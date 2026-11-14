"""WSP86 synthetic coverage engineering only: no experimental World instantiated."""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from coverage_policy import CYCLE,STAGE_B,stage_b_actions,full_triple_coverage

class Tests(unittest.TestCase):
    def test_canonical_cycle(self):
        self.assertEqual(len(CYCLE),216)
        self.assertEqual(full_triple_coverage(CYCLE+CYCLE[:2]),216)

    def test_all_36_stage_a_tails_complete_paid_coverage(self):
        for a,b in product(range(6),repeat=2):
            prefix=(0,)*142+(a,b)
            plan=stage_b_actions(prefix)
            self.assertEqual(len(plan),STAGE_B)
            self.assertEqual(plan,stage_b_actions(prefix))
            self.assertEqual(full_triple_coverage((a,b)+plan[:216]),216)
            self.assertEqual(full_triple_coverage(prefix+plan),216)

    def test_independent_public_history_fixture(self):
        prefix=tuple(int.from_bytes(sha256(
            f"WSP86|UNIT|{i}".encode("ascii")).digest()[:8],"big")%6
            for i in range(144))
        plan=stage_b_actions(prefix)
        self.assertEqual(len(prefix+plan),384)
        self.assertEqual(full_triple_coverage(prefix+plan),216)

    def test_fail_closed_bad_paid_action_history(self):
        for bad in ((),(0,)*143,(0,)*145,(-1,)*144,
                    (6,)*144,(True,)*144,"0"*144,(0,)*143+(1.0,)):
            with self.assertRaises(PermissionError):
                stage_b_actions(bad)
        for bad in ("",(-1,),[None],[True],[2.0]):
            with self.assertRaises(ValueError):
                full_triple_coverage(bad)

    def test_no_private_source_policy_access(self):
        code=(HERE/"coverage_policy.py").read_text("utf8")
        for forbidden in ("import source","from source import","World(",
                          "private_truth(","private_receipt(","import torch"):
            self.assertNotIn(forbidden,code)

    def test_prospective_prereg_and_scoring_strata(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["schema"],"wsp86.reachable-history-coverage-developer.v1")
        self.assertEqual(p["worlds"]["total_physical_paid_actions"],6912)
        self.assertEqual(p["worlds"]["stratified_query_counts_per_arm_world"],
            {"cold_start_length_0_1":2688,"reachable_length_2":13824,"total":16512})
        self.assertEqual(p["worlds"]["unregistered_developer_seeds"],
            [10601,10602,10603,10604,10605,10606])
        self.assertEqual(p["frozen_outcomes"]["full_triple_cover_each_debruijn_world"],216)
        self.assertFalse(p["authority"]["scientific_first_use"])

if __name__=="__main__":
    unittest.main()
