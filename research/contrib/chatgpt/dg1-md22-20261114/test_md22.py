"""MD22 prospective toy-only structural/negative tests, no registered cohort."""
import importlib.util
import json
from pathlib import Path
import unittest

path=Path(__file__).with_name("md22.py")
spec=importlib.util.spec_from_file_location("md22",path)
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m=d.m


class PhysicalInterventionPrefirstuse(unittest.TestCase):
    def test_original_registered_identity_without_using_primary_seeds(self):
        d.verify_manifest()
        self.assertEqual(d.FREEZE,"ada17791db5ba3892f2d8012e38dffd024b55dbb")
        self.assertEqual(d.MANIFEST_HASH,"839a7d4f6e6731d93b012527bb1fdde9ddeaa9f18d541f87d73a4a96f542fbb7")
        self.assertEqual(len(d.ARMS),5)
        self.assertTrue(all(seed not in group for seed in (11,17,19)
            for group in (d.TRAIN_SEEDS,d.INTERFERENCE_SEEDS,d.COLD_SEEDS,
                          d.SIZE_SEEDS,d.FAMILY_SEEDS)))
        self.assertEqual(m.MAX_STEPS,256)

    def test_official_partial_view_goal_conditions(self):
        import gymnasium as gym
        import minigrid
        envs=d.TRAIN_ENVS+(d.SIZE_ENV,d.FAMILY_ENV)
        for name in envs:
            env=gym.make(name)
            try:
                obs,_=env.reset(seed=11)
                self.assertEqual(tuple(obs["image"].shape),(7,7,3))
                self.assertEqual(len(m.public_features(obs,6,0)),m.FEATURES)
                changed=dict(obs)
                changed["mission"]="UNRELATED SECRET MISSION MUST NOT ENTER LEARNER"
                self.assertEqual(m.public_features(obs,6,0),
                                 m.public_features(changed,6,0))
            finally:env.close()

    def test_paid_interventions_on_toy_keydoor_worlds(self):
        trials=[d.teacher_episode(env,seed) for env in d.TRAIN_ENVS
                for seed in (11,17,19)]
        self.assertEqual(len(trials),6)
        self.assertTrue(all(0<e["steps"]<=256 for e in trials))
        self.assertTrue(all(e["steps"]==len(e["transitions"]) for e in trials))
        self.assertTrue(all(len(e["sha256"])==64 for e in trials))
        print("MD22_TOY_PUBLIC_ACTION_COVERAGE:"+json.dumps({
            "episodes":len(trials),
            "official_goal_successes":sum(e["success"] for e in trials),
            "negative_locked_door_probes":sum(e["failed_without_key_probe_count"] for e in trials),
            "positive_with_key_unlocks":sum(e["unlocked_with_key_probe_count"] for e in trials)},sort_keys=True),flush=True)
        self.assertTrue(any(e["failed_without_key_probe_count"]>0 for e in trials),
                        "MD22_TOY_NO_NEGATIVE_INTERVENTION")
        self.assertTrue(any(e["unlocked_with_key_probe_count"]>0 for e in trials),
                        "MD22_TOY_NO_WITH_KEY_INTERVENTION")
        self.assertTrue(any(e["success"]>0 for e in trials),
                        "MD22_TOY_NO_GOAL_REWARD")

    def test_policy_changes_only_due_to_learned_intervention_relation(self):
        a=d.AffordancePlanner("causal_affordance")
        b=d.AffordancePlanner("sham_affordance")
        for x in (a,b):
            x.failed_without_key=6
            x.unlocked_with_key=6
            x.start(19)
        self.assertTrue(a.used_affordance_at_start)
        self.assertFalse(b.used_affordance_at_start)
        self.assertEqual(a.preferred_subgoal(),"key")
        self.assertEqual(b.preferred_subgoal(),"door")
        self.assertEqual(a.dump()["failed_without_key"],b.dump()["failed_without_key"])

    def test_training_intervention_counters_record_genuine_physical_feedback(self):
        import gymnasium as gym
        import minigrid
        from minigrid.core.constants import OBJECT_TO_IDX
        obj=OBJECT_TO_IDX
        e=gym.make(d.TRAIN_ENVS[0])
        try:
            observation,_=e.reset(seed=17)
            agent=d.AffordancePlanner("causal_affordance")
            fake0=dict(observation)
            fake1=dict(observation)
            import numpy as np
            a=np.zeros_like(observation["image"])
            a[3,5,0]=obj["door"];a[3,5,2]=2
            b=a.copy()
            fake0["image"]=a;fake1["image"]=b
            agent.feedback(fake0,5,fake1,0.,training=True)
            self.assertEqual(agent.failed_without_key,1)
            self.assertTrue(agent.probed_without_key)
            agent.has_key=True
            b[3,5,2]=0
            agent.feedback(fake0,5,fake1,0.,training=True)
            self.assertEqual(agent.unlocked_with_key,1)
            self.assertTrue(agent.opened_door)
        finally:e.close()

    def test_training_all_five_arms_exact_same_physical_toy_trajectory(self):
        agents={arm:d.make_agent(arm) for arm in d.ARMS}
        ep=d.teacher_episode(d.TRAIN_ENVS[0],17)
        d.train_on_shared(agents,ep)
        self.assertEqual(agents["tabular_q"].count,ep["steps"])
        self.assertEqual(agents["recurrent_imitation"].count,ep["steps"])
        self.assertEqual(agents["causal_affordance"].train_calls,
                         agents["sham_affordance"].train_calls)
        self.assertEqual(agents["causal_affordance"].failed_without_key,
                         agents["sham_affordance"].failed_without_key)
        for model in agents.values():
            self.assertEqual(d.save(model),d.save(d.restore(d.save(model))))

    def test_read_only_episode_scoring_preserves_persistent_model(self):
        agents={arm:d.make_agent(arm) for arm in d.ARMS}
        ep=d.teacher_episode(d.TRAIN_ENVS[0],11)
        d.train_on_shared(agents,ep)
        before={k:d.save(v) for k,v in agents.items()}
        data=d.score(agents,d.COLD_ENV,(17,19))
        self.assertEqual(len(data["episodes"]),5)
        self.assertEqual(data["episode_count"],10)
        self.assertEqual(data["charged_env_steps"],
                         sum(x["steps"] for arr in data["episodes"].values() for x in arr))
        for key,model in agents.items():
            self.assertEqual(d.save(model),before[key])

    def test_map_and_cold_checkpoint_bounded_without_hidden_global_pose(self):
        import gymnasium as gym
        import minigrid
        env=gym.make(d.TRAIN_ENVS[0])
        try:
            o,_=env.reset(seed=11)
            actor=d.AffordancePlanner("causal_affordance")
            actor.start(11)
            for i in range(50):
                action=actor.act(o,i)
                self.assertIn(action,m.ACTIONS)
                o2,reward,term,trunc,_=env.step(action)
                actor.feedback(o,action,o2,reward,training=False)
                self.assertLessEqual(len(actor.tiles),256)
                self.assertLessEqual(len(d.save(actor)),65536)
                o=o2
                if term or trunc:break
        finally:env.close()

    def test_negative_model_and_invalid_context_guards(self):
        with self.assertRaises(ValueError):
            d.make_agent("global_environment_oracle")
        with self.assertRaises(ValueError):
            d.AffordancePlanner("fake_god_mode")
        with self.assertRaises(ValueError):
            m.RecurrentImitation().forward([])


if __name__=="__main__":
    unittest.main()
