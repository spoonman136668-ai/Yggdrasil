"""AAI-04R1 invariant checks. Does not qualify a scientific result."""
import importlib.util
import json
from pathlib import Path
import unittest

HOME = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aai04r1", HOME / "run.py")
aai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aai)


class AAI04R1Tests(unittest.TestCase):
    def test_partition_and_identifiability(self):
        self.assertTrue(aai.audit())

    def test_distinct_family_generalization_split(self):
        train_families = {aai.world(seed)["law"] // 3 for seed in aai.TRAIN}
        dev_families = {aai.world(seed)["law"] // 3 for seed in aai.DEV}
        transfer_families = {aai.world(seed, True)["law"] // 3 for seed in aai.TRANSFER}
        self.assertEqual(train_families, {0, 1})
        self.assertEqual(dev_families, {0, 1})
        self.assertEqual(transfer_families, {2, 3})

    def test_observation_likelihood(self):
        for predicted in range(8):
            self.assertAlmostEqual(sum(aai.observation_likelihood(y, predicted)
                                       for y in range(8)), 1.0)
            self.assertAlmostEqual(aai.observation_likelihood(predicted, predicted), .65)

    def test_passive_law_independence(self):
        for seed in (92000, 93000, 94000):
            w = aai.world(seed, seed >= 93000)
            alt = dict(w, law=(w["law"] + 5) % 12)
            self.assertEqual([aai.passive_event(w, i) for i in range(aai.DISTRACTORS)],
                             [aai.passive_event(alt, i) for i in range(aai.DISTRACTORS)])
            self.assertEqual(w["terminal_start"], alt["terminal_start"])
            self.assertEqual(w["terminal_target"], alt["terminal_target"])

    def test_online_bounded_retention(self):
        w = aai.world(92000)
        memory = []
        for step in range(2):
            aai.retain(memory, aai.observe(w, 2, step, step), "utility")
        for i in range(aai.DISTRACTORS):
            aai.retain(memory, aai.passive_event(w, i), "utility")
        self.assertEqual(len(memory), aai.CAPACITY)
        self.assertEqual(sum(e["kind"] == "do" for e in memory), 2)
        self.assertTrue(all("law" not in e and "terminal_target" not in e for e in memory))

    def test_recent_buffer_is_negative_control(self):
        w = aai.world(92000)
        memory = []
        for step in range(2):
            aai.retain(memory, aai.observe(w, 2, step, step), "recent")
        for i in range(aai.DISTRACTORS):
            aai.retain(memory, aai.passive_event(w, i), "recent")
        self.assertEqual(sum(e["kind"] == "do" for e in memory), 0)

    def test_two_step_nontrivial_terminal(self):
        w = aai.world(82001)
        options = aai.all_plan_rewards(w)
        self.assertEqual((len(options), len(options[0])), (16, 12))
        belief = [1 / 12] * 12
        plan, value = aai.best_plan(belief, options)
        self.assertIn(plan[0], aai.ACTIONS)
        self.assertIn(plan[1], aai.ACTIONS)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 1)

    def test_supervised_table_fit_restores(self):
        model = aai.fit_tabular([aai.world(s) for s in list(aai.TRAIN)[:32]])
        self.assertEqual(len(model), 12)
        self.assertEqual(json.loads(json.dumps(model)), model)

    def test_sham_observations_are_supported(self):
        # Reserved mechanical diagnostic seeds, disjoint from every science split.
        for seed in range(99000, 99032):
            world = aai.world(seed, True)
            obs = [aai.observe(world, *aai.random_probe(world, i), i, sham=True)
                   for i in range(aai.PROBES)]
            self.assertAlmostEqual(sum(aai.posterior(obs)), 1.0)

    def test_protocol_without_science_first_use(self):
        self.assertEqual((aai.PROBES, aai.CAPACITY, aai.DISTRACTORS), (2, 4, 32))
        self.assertEqual(aai.PREREG, "d9b8d86593a23b32dcf87e74490fb65f5dae8e6c")
        w = aai.world(92000)
        self.assertEqual(aai.run_arm(w, "no_probe")["probe_count"], 0)
