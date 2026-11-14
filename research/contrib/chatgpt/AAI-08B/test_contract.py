"""Source-only AAI-08B future science contract; never execute science worlds."""
import ast
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parent

class FutureScienceContract(unittest.TestCase):
    def test_all_frozen_cohorts_disjoint_and_outside_previous(self):
        p=json.loads((ROOT/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["experiment_id"],"AAI-08B")
        self.assertEqual(p["protocol"]["budgets"],[0,1,2,4,8])
        cohorts=p["protocol"]["cohorts"]
        ranges={name:set(range(row["first"],row["first"]+row["count"]))
                for name,row in cohorts.items()}
        for name in ranges:
            for other in ranges:
                if name!=other:
                    self.assertFalse(ranges[name]&ranges[other])
        self.assertEqual(len(ranges["transfer"]),64)
        self.assertEqual(len(ranges["negative"]),32)
        self.assertTrue(all(0<=x<1200000 for v in ranges.values() for x in v))

    def test_no_primary_science_execution_in_preparatory_cli(self):
        script=(ROOT/"evaluate.py").read_text(encoding="utf8")
        tree=ast.parse(script,filename="evaluate.py")
        self.assertIn('parser.error("Scientific first-use disabled',script)
        p=json.loads((ROOT/"prereg.json").read_text(encoding="utf8"))
        self.assertFalse(p["authority"]["first_use_authorized"])
        self.assertEqual(p["authority"]["merge_authorized"],False)

    def test_no_privileged_simulator_state_used(self):
        tree=ast.parse((ROOT/"evaluate.py").read_text(encoding="utf8"))
        banned={"unwrapped","get_planning_env","transition_matrix",
                "success_pos","failure_pos","grid"}
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr in banned
                             for node in ast.walk(tree)))

    def test_fair_condition_pair_and_no_probe_identity(self):
        script=(ROOT/"evaluate.py").read_text(encoding="utf8")
        self.assertIn('SCENARIOS=("return_A","hold_B")',script)
        self.assertIn('if budget==0:',script)
        self.assertIn('forks["return_A:0"]["decisions"]==forks["hold_B:0"]["decisions"]',script)
        self.assertIn('correct_decision":2 if condition=="return_A" else 3',script)

    def test_frozen_original_algorithm_and_baseline_family(self):
        model=(ROOT/"models.py").read_text(encoding="utf8")
        tree=ast.parse(model)
        cls={node.name for node in tree.body if isinstance(node,ast.ClassDef)}
        self.assertTrue({"RegimeCache","Beta","Recent","Stationary","Logistic",
                         "KnownLawBayes","AlwaysRight"}.issubset(cls))
        self.assertIn("BLOCK = 5",model)
        self.assertIn("THRESHOLD = math.log(3.)",model)
        self.assertIn("LOGISTIC_EPOCHS = 1200",model)

if __name__=="__main__":
    unittest.main()
