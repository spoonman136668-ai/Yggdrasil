"""AAI-06A mechanical tests on reserved seeds, not scientific first use."""
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aai06", HERE / "run.py")
e = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e)


class AAI06Tests(unittest.TestCase):
    def test_budget_and_rule_construction(self):
        self.assertEqual(len(e.PRIMITIVES), 30)
        self.assertEqual((e.PROBES, e.TASKS, e.CANDIDATE_BEAM, e.CAP), (16, 12, 6, 2))
        self.assertTrue(e.audit())

    def test_disjoint_unseen_terminal_states(self):
        for seed in range(990000, 990004):
            w = e.world(seed, transfer=True)
            seen, goals = e.observations(w)
            self.assertEqual(len({(s,a) for s,a,_ in seen}), 16)
            self.assertFalse({s for s,_,_ in seen} & {s for s,_ in goals})

    def test_no_hidden_law_in_training(self):
        w = e.world(990000)
        obs, goals = e.observations(w)
        self.assertTrue(all(len(row) == 3 for row in obs))
        self.assertTrue(all("circuit" not in repr(row) for row in obs))

    def test_exact_and_graph_growth_counts(self):
        w = e.world(990001, True)
        obs,_ = e.observations(w)
        self.assertEqual(e.fit("grow", obs)["evaluations"], 2220)
        self.assertEqual(e.fit("exhaustive", obs)["evaluations"], 10800)

    def test_mutable_shared_memory_eviction(self):
        for method in ("grow", "exhaustive"):
            outcome=e.interference_case(990002, method)
            self.assertTrue(outcome["retained_A"])
            self.assertTrue(outcome["lru_lost_A"])
            self.assertEqual(outcome["value_keys"], ["0","2"])
            self.assertEqual(outcome["peak_slots"], 2)

    def test_cold_restore_and_reproducibility(self):
        x=e.one_world(990003, True, ("grow","exhaustive","logistic","random"))
        y=e.one_world(990003, True, ("grow","exhaustive","logistic","random"))
        for key in x:
            self.assertEqual(x[key]["reward"],y[key]["reward"])
            self.assertEqual(x[key]["predictions"],y[key]["predictions"])
            self.assertEqual(x[key]["evaluations"],y[key]["evaluations"])

    def test_prereg_and_split(self):
        self.assertEqual(e.PREREG, "71941d3d825050977ab5fb8a4d8dd6489d5bd546")
        self.assertEqual((len(e.DEV),len(e.TRANSFER),len(e.NEGATIVE),len(e.INTERFERENCE)),(32,64,32,32))


if __name__ == "__main__":
    unittest.main()
