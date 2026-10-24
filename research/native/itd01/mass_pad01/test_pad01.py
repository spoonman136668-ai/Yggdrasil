"""PAD-01 focused source-free tests: honest public source and frozen roles."""
import unittest

from research.native.itd01.mass_pad01 import run as p


class PAD01Tests(unittest.TestCase):
    def test_fixed_original_roles_and_separation(self):
        self.assertEqual(p.family_seed("P", 0), 202610230000)
        self.assertEqual(p.family_seed("P", 2), 202610232000)
        self.assertEqual(p.family_seed("N", 0), 202610240000)
        self.assertEqual(len({p.family_seed(f, r) for f in p.FAMILIES for r in p.REPLICAS}), 6)
        self.assertEqual(p.FIT, 96)
        self.assertEqual(p.DEV, 128)

    def test_actual_source_step_is_chosen_action_dependent(self):
        for family in p.FAMILIES:
            src = p.HiddenSource(family, p.family_seed(family, 0))
            possibilities = [
                tuple(src.step(tuple((x >> i) & 1 for i in range(6)), a) for a in range(3))
                for x in range(64)
            ]
            self.assertTrue(any(len(set(outcomes)) > 1 for outcomes in possibilities))
            self.assertTrue(all(set(outcomes) <= {0, 1} for outcomes in possibilities))

    def test_fit_only_public_chronology_and_checkpoint(self):
        seed = p.family_seed("P", 1)
        source = p.HiddenSource("P", seed)
        rows = p.fit_history(source, seed)
        self.assertEqual(len(rows), p.FIT)
        self.assertEqual(rows, p.fit_history(source, seed))
        self.assertTrue(all(len(x) == 6 and a in range(3) and y in (0,1) for x, a, y in rows))
        self.assertEqual(len(p.dev_inputs(seed)), p.DEV)
        self.assertNotEqual(p.sha(rows), p.sha(p.dev_inputs(seed)))
        for arm in p.ARMS:
            m = p.train(arm, rows)
            self.assertIn(p.choose(arm, m, p.dev_inputs(seed)[0], 0), (0,1,2))

    def test_credit_ablation_relabels_only_fit_action(self):
        rows = [
            ((0, 0, 0, 0, 0, 0), 0, 1),
            ((1, 0, 0, 0, 0, 0), 1, 0),
            ((0, 1, 0, 0, 0, 0), 2, 1),
        ]
        copy = tuple(rows)
        m = p.train("pair_credit_ablated", rows)
        self.assertEqual(tuple(rows), copy)
        self.assertEqual(len(m), 3)
        self.assertEqual(len(p.train("sparse_pair_credit", rows)), 3)

    def test_one_original_source_reward_per_dev_action(self):
        task = p.run_task("N", 1)
        self.assertEqual(task["source_real_fit_steps"], p.FIT)
        self.assertEqual(task["source_real_dev_steps"], p.DEV * len(p.ARMS))
        self.assertEqual(len(task["fit_public_trace_sha256"]), 64)
        for arm in p.ARMS:
            a = task["arms"][arm]
            self.assertEqual(len(a["real_chosen_actions"]), p.DEV)
            self.assertEqual(len(a["real_source_rewards"]), p.DEV)
            self.assertEqual(sum(a["real_source_rewards"]) / p.DEV, a["score"])
            self.assertEqual(a["fit_updates"], 0 if arm == "random_policy" else p.FIT)

    def test_negative_remains_negative_without_resource_parity_and_replication(self):
        tasks = [p.run_task(f, r) for f in p.FAMILIES for r in p.REPLICAS]
        disposition = p.finish(tasks)
        self.assertEqual(disposition["scientific_classification"], "PAD01_PUBLIC_DEVELOPMENT_NO_GO")
        self.assertEqual(disposition["model_isolated_process_resource_parity"], "NOT_MEASURED")
        self.assertEqual(disposition["independent_replication"], "NOT_PERFORMED")


if __name__ == "__main__":
    unittest.main()
