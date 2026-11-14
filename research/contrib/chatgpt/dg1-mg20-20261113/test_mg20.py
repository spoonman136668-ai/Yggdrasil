"""MG20 prefirstuse real action tests on ONLY toy seeds 11,17,19."""
import importlib.util
import json
import random
from pathlib import Path
import unittest

file=Path(__file__).with_name("mg20.py")
spec=importlib.util.spec_from_file_location("mg20",file)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RealGoalPreFirstUse(unittest.TestCase):
    def test_frozen_original_source_identity(self):
        m.verify_manifest()
        self.assertEqual(m.FREEZE,"029bd7e8da15e0512c2a11bba90a9fb322bb751f")
        self.assertEqual(m.MANIFEST_SHA,"c51855a9ab42e2bd5da848cd7eaa0db342fcf167dffa4d3237802d12d1096cff")
        self.assertEqual(len(m.ARMS),5)
        self.assertEqual(m.MAX_STEPS,128)
        self.assertTrue(all(19 not in seeds for seeds in
            (m.TRAIN_SEEDS,m.INTERFERENCE_SEEDS,m.COLD_SEEDS,m.SIZE_SEEDS,m.FAMILY_SEEDS)))

    def test_public_image_and_goal_reward_source(self):
        import gymnasium as gym
        import minigrid
        for e in m.TRAIN_ENVS+(m.INTERFERENCE_ENV,m.SIZE_ENV,m.FAMILY_ENV):
            env=gym.make(e)
            try:
                obs,_=env.reset(seed=11)
                self.assertEqual(obs["image"].shape,(7,7,3))
                self.assertEqual(len(m.public_features(obs,6,0)),m.FEATURES)
                alt=dict(obs);alt["mission"]="DO_NOT_TRAIN_WITH_THIS"
                self.assertEqual(m.public_features(obs,6,0),
                                 m.public_features(alt,6,0))
                self.assertEqual(m.front_type(obs),int(obs["image"][3,5,0]))
            finally:env.close()

    def test_toy_real_physical_action_accounting(self):
        a=m.make_trace(m.TRAIN_ENVS[0],17)
        b=m.make_trace(m.TRAIN_ENVS[0],17)
        self.assertGreater(a["steps"],0)
        self.assertLessEqual(a["steps"],m.MAX_STEPS)
        self.assertEqual(a["steps"],len(a["transitions"]))
        self.assertEqual(a["sha256"],b["sha256"])
        self.assertEqual(a["success"],b["success"])
        self.assertTrue(all(t[1] in m.ACTIONS for t in a["transitions"]))
        self.assertEqual(a["discounted_reward"],b["discounted_reward"])

    def test_all_agents_see_same_training_trace(self):
        training=m.make_trace(m.TRAIN_ENVS[0],19)
        models={arm:m.make_agent(arm) for arm in m.ARMS}
        m.train_on_shared(models,training,"train")
        self.assertEqual(models["recurrent_imitation"].count,training["steps"])
        self.assertEqual(models["tabular_q"].count,training["steps"])
        self.assertEqual(models["causal_map"].passability,
                         models["sham_map"].passability)
        self.assertEqual(models["causal_map"].train_calls,
                         models["sham_map"].train_calls)
        for obj in models.values():
            self.assertLessEqual(len(m.save(obj)),65536)
            self.assertEqual(m.save(m.load(m.save(obj))),m.save(obj))

    def test_pose_transform_and_episode_memory_bound(self):
        model=m.MapPolicy("causal_map")
        self.assertEqual(model.vectors(0),((1,0),(0,1)))
        self.assertEqual(model.vectors(1),((0,1),(-1,0)))
        self.assertEqual(model.vectors(2),((-1,0),(0,-1)))
        self.assertEqual(model.vectors(3),((0,-1),(1,0)))
        import gymnasium as gym
        import minigrid
        env=gym.make(m.TRAIN_ENVS[0])
        try:
            obs,_=env.reset(seed=11)
            for step in range(50):
                a=model.act(obs,step)
                self.assertIn(a,m.ACTIONS)
                after,reward,terminated,truncated,_=env.step(a)
                model.feedback(obs,a,after,reward,training=False)
                obs=after
                self.assertLessEqual(len(model.tiles),m.LIMIT)
                if terminated or truncated:break
        finally:env.close()

    def test_negative_sham_spatial_storage_differs(self):
        import gymnasium as gym
        import minigrid
        env=gym.make(m.TRAIN_ENVS[0])
        try:
            obs,_=env.reset(seed=17)
            good=m.MapPolicy("causal_map")
            sham=m.MapPolicy("sham_map")
            good.start(17);sham.start(17)
            good.ingest(obs);sham.ingest(obs)
            self.assertNotEqual(good.tiles,sham.tiles)
            self.assertEqual(good.dump()["passability"],sham.dump()["passability"])
        finally:env.close()

    def test_trainable_recurrent_all_groups_cold_restore(self):
        model=m.RecurrentImitation()
        before=json.loads(m.canon(model.dump()))
        for i in range(65):
            seq=[[round(((i*17+j*7+k)%23)/24,8)
                  for k in range(m.FEATURES)] for j in range(8)]
            model.learn(seq,m.ACTIONS[i%len(m.ACTIONS)],2.)
        self.assertEqual(model.count,65)
        for field in ("wx","wh","v","b","c"):
            self.assertNotEqual(before[field],model.dump()[field],field)
        self.assertEqual(m.save(model),m.save(m.load(m.save(model))))

    def test_toy_holdout_cannot_train_or_use_hidden_env(self):
        train=m.make_trace(m.TRAIN_ENVS[0],17)
        agents={a:m.make_agent(a) for a in m.ARMS}
        m.train_on_shared(agents,train,"train")
        saved={k:m.save(v) for k,v in agents.items()}
        part=m.score(agents,m.TRAIN_ENVS[1],[11,19])
        self.assertEqual(part["environment"],m.TRAIN_ENVS[1])
        self.assertEqual(len(part["episodes"]),5)
        self.assertEqual(part["counted_env_steps"],
            sum(e["steps"] for v in part["episodes"].values()for e in v))
        for name,obj in agents.items():
            self.assertEqual(saved[name],m.save(obj),name)

    def test_negative_invalid_learners(self):
        with self.assertRaises(ValueError):
            m.make_agent("oracle_position")
        with self.assertRaises(ValueError):
            m.RecurrentImitation().forward([])
        with self.assertRaises(ValueError):
            m.TabularQ().feedback(None,4,None,0,training=True)


if __name__=="__main__":
    unittest.main()
