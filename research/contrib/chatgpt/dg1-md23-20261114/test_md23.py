"""MD23 pre-first-use tests. The registered primary seed ranges are never touched."""
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("md23.py")
spec = importlib.util.spec_from_file_location("md23", str(SOURCE))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m = d.m


class RewardedBoxToyPrefirstuse(unittest.TestCase):
    def test_exact_prereg_and_disjoint_seed_fence(self):
        d.verify_prereg()
        self.assertEqual(len(d.ARMS), 6)
        self.assertEqual(d.FROZEN_PREREG, "ea927ae080aee59d2dc0783f45eb703735dfb52f")
        self.assertEqual(d.EXACT_PARENT, "155cb5c3c3f4802166ffb26695b7f7353384cb42")
        with self.assertRaisesRegex(AssertionError, "ONLY_PREREG_TOY"):
            d.teacher_episode(d.BOX_ENV, 981001)
        with self.assertRaisesRegex(AssertionError, "ONLY_PREREG_TOY"):
            d.teacher_episode(d.DOOR_ENV, 985001)

    def test_public_partial_observation_and_task_free_input(self):
        import gymnasium as gym
        import minigrid
        for env_name in (d.DOOR_ENV, d.BOX_ENV):
            env = gym.make(env_name)
            try:
                obs, _ = env.reset(seed=17)
                self.assertEqual(obs["image"].shape, (7, 7, 3))
                changed = dict(obs)
                changed["mission"] = "DO NOT PARSE THE MISSION"
                actor = d.GraphPolicy("fixed_scripted")
                actor.start(17)
                self.assertEqual(actor.act(obs, 0), actor.act(changed, 0))
            finally:
                env.close()

    def test_reward_requires_real_box_pickup(self):
        import numpy as np
        from minigrid.core.constants import OBJECT_TO_IDX
        fake0 = {"image": np.zeros((7, 7, 3), dtype=np.uint8), "direction": 0}
        fake1 = {"image": np.zeros((7, 7, 3), dtype=np.uint8), "direction": 0}
        fake0["image"][3, 5, 0] = OBJECT_TO_IDX["box"]
        fake1["image"][3, 5, 0] = OBJECT_TO_IDX["empty"]
        model = d.GraphPolicy("causal_graph")
        model.episode_unlock = True
        model.feedback(fake0, 3, fake1, 0., training=True)
        self.assertEqual(model.train_events["rewarded_box"], 0)
        self.assertEqual(model.edges["unlock_before_rewarded_box"], 0)
        model.feedback(fake0, 3, fake1, 0.5, training=True)
        self.assertEqual(model.train_events["rewarded_box"], 1)
        self.assertEqual(model.edges["unlock_before_rewarded_box"], 1)

    def test_shared_training_and_edge_sham_ablation(self):
        agents = {name: d.make_agent(name) for name in d.ARMS}
        for env, seed in ((d.DOOR_ENV, 11), (d.BOX_ENV, 17)):
            d.train_shared(agents, d.teacher_episode(env, seed))
        causal = agents["causal_graph"]
        sham = agents["shuffled_graph"]
        self.assertEqual(causal.edges, sham.edges)
        self.assertEqual(causal.train_events, sham.train_events)
        self.assertEqual(causal.failed_without_key, sham.failed_without_key)
        self.assertEqual(causal.unlocked_with_key, sham.unlocked_with_key)
        self.assertEqual(causal.train_calls, sham.train_calls)
        self.assertGreater(agents["tabular_q"].count, 0)
        self.assertEqual(agents["tabular_q"].count, agents["recurrent_imitation"].count)
        for a in agents.values():
            self.assertEqual(d.save(d.restore(d.save(a))), d.save(a))

    def test_no_heldout_weights_leak_during_public_action_scoring(self):
        agents = {name: d.make_agent(name) for name in d.ARMS}
        d.train_shared(agents, d.teacher_episode(d.DOOR_ENV, 11))
        before = {name: d.save(agent) for name, agent in agents.items()}
        # Disjoint from the toy training episode, still from preregistered toy seeds.
        for name, agent in agents.items():
            outcome = m.make_trace(d.DOOR_ENV, 19, agent)
            self.assertGreater(outcome["steps"], 0)
            self.assertEqual(before[name], d.save(agent), name)

    def test_toy_paid_action_reward_coverage(self):
        data = d.toy_qualification()
        self.assertFalse(data["registered_first_use"])
        self.assertEqual(data["teacher"]["door"]["episodes"], 6)
        self.assertEqual(data["teacher"]["box"]["episodes"], 6)
        print("MD23_TOY_TEACHER_COVERAGE:" + json.dumps(
            data["teacher"], sort_keys=True), flush=True)
        print("MD23_TOY_LEARNED_EVENTS:" + json.dumps(
            data["learned_edges"], sort_keys=True), flush=True)
        if data["teacher"]["box"]["goals"] == 0:
            from minigrid.core.constants import OBJECT_TO_IDX
            for seed in (11, 17):
                episode = d.teacher_episode(d.BOX_ENV, seed)
                pairs = episode["transitions"]
                visible = [i for i, (before, act, _, after, _) in enumerate(pairs)
                           if (m.objects(before) == OBJECT_TO_IDX["box"]).any()]
                front_box = [i for i, (before, act, _, after, _) in enumerate(pairs)
                             if m.front_type(before) == OBJECT_TO_IDX["box"]]
                pickups = [i for i, (before, act, _, after, _) in enumerate(pairs)
                           if act == 3 and m.front_type(before) == OBJECT_TO_IDX["box"]]
                drop_actions = [i for i, (_, act, _, _, _) in enumerate(pairs) if act == 4]
                print("MD23_BOX_TOY_DIAGNOSTIC:" + json.dumps({
                    "seed": seed, "steps": episode["steps"], "box_visible": len(visible),
                    "first_box_visible": visible[0] if visible else None,
                    "box_front": len(front_box), "box_pickup_attempts": len(pickups),
                    "drop_attempts": len(drop_actions),
                    "drop_transitions": [
                        {"step": i, "before_front": m.front_type(pairs[i][0]),
                         "after_front": m.front_type(pairs[i][3]),
                         "before_carry_tile": int(m.objects(pairs[i][0])[3,6]),
                         "after_carry_tile": int(m.objects(pairs[i][3])[3,6])}
                        for i in drop_actions],
                    "first_box_attempt": ({
                         "step": pickups[0],
                         "before_carry_tile": int(m.objects(pairs[pickups[0]][0])[3,6]),
                         "after_carry_tile": int(m.objects(pairs[pickups[0]][3])[3,6]),
                         "front_after": m.front_type(pairs[pickups[0]][3])
                    } if pickups else None),
                    "last_16_action_and_front": [(a, m.front_type(b)) for b,a,_,_,_ in pairs[-16:]],
                    "no_key_probe": episode["no_key_probe"],
                    "with_key_unlock": episode["with_key_unlock"]}, sort_keys=True), flush=True)
        self.assertGreater(data["teacher"]["door"]["goals"], 0,
                           "MD23_TOY_DOOR_TEACHER_NO_OFFICIAL_REWARD")
        self.assertGreater(data["teacher"]["box"]["goals"], 0,
                           "MD23_TOY_BOX_TEACHER_NO_OFFICIAL_REWARD")
        self.assertGreater(data["teacher"]["box"]["rewarded_box"], 0,
                           "MD23_TOY_NO_ACTUAL_REWARDED_BOX_PICKUP")
        self.assertGreater(data["teacher"]["door"]["no_key_probe"] +
                           data["teacher"]["box"]["no_key_probe"], 0,
                           "MD23_TOY_NO_PHYSICAL_NEGATIVE_CONTROL")
        self.assertGreater(data["teacher"]["door"]["with_key_unlock"] +
                           data["teacher"]["box"]["with_key_unlock"], 0,
                           "MD23_TOY_NO_POSITIVE_UNLOCK")
        self.assertGreater(data["learned_edges"]["unlock_before_rewarded_box"], 0,
                           "MD23_TOY_NO_LEARNED_REWARDED_BOX_CONSEQUENCE")


if __name__ == "__main__":
    unittest.main()
