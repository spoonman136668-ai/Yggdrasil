"""Prospective MG19 pre-first-use tests. Only nonregistered toy seeds."""
import importlib.util
import json
from pathlib import Path
import unittest

root=Path(__file__).parent
spec=importlib.util.spec_from_file_location("mg19",root/"mg19.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MG19PreFirstUse(unittest.TestCase):
    def test_preregistration_ancestor_manifest(self):
        m.require_manifest()
        self.assertEqual(m.FREEZE,"f9c531011f36d3a9150397f462a681f094657b28")
        self.assertEqual(m.MANIFEST_HASH,"e8b825254d1b7e90fe9c4eb6f12643f87066d50e1ee04970ca14a1fbd0400184")
        self.assertEqual(m.HORIZON,12)
        self.assertEqual(m.CAPACITY,256)
        self.assertEqual(len(m.ARMS),5)
        self.assertNotIn(11,m.TRAIN_SEEDS)
        self.assertNotIn(19,m.COLD_SEEDS)

    def test_actual_minigrid_partial_image_only(self):
        import gymnasium as gym
        import minigrid
        for env_name in (m.TRAIN_ENVS[0],m.TRAIN_ENVS[1],m.INTERFERENCE_ENV,
                         m.LARGER_ENV,m.TRANSFER_ENV):
            env=gym.make(env_name)
            try:
                o,_=env.reset(seed=11)
                self.assertEqual(o["image"].shape,(7,7,3))
                a=m.encoded(o,6)
                self.assertEqual(len(a),m.DIMS)
                self.assertEqual(len(m.image_features(o)),7)
                mutated=dict(o)
                mutated["mission"]="SECRET ARBITRARY MISSION MUST NOT ENTER MODEL"
                self.assertEqual(m.encoded(o,6),m.encoded(mutated,6))
            finally:
                env.close()

    def test_unregistered_real_environment_actions_are_charged_and_deterministic(self):
        a=m.collect(m.TRAIN_ENVS[0],11)
        b=m.collect(m.TRAIN_ENVS[0],11)
        self.assertEqual(a["trajectory_sha256"],b["trajectory_sha256"])
        self.assertEqual(a["steps"],b["steps"])
        self.assertLessEqual(a["steps"],128)
        self.assertGreater(a["steps"],m.HORIZON)
        self.assertEqual(len(a["rows"]),a["steps"]-m.HORIZON+1)
        for seq,y,changed in a["rows"]:
            self.assertEqual(len(y),m.OUT)
            self.assertEqual(len(seq[-1]),m.DIMS)
            self.assertLessEqual(len(seq),m.HISTORY)
            self.assertIsInstance(changed,bool)

    def test_public_observation_policy_never_reads_private_map(self):
        import gymnasium as gym
        import random
        env=gym.make(m.TRAIN_ENVS[0])
        try:
            o,_=env.reset(seed=19)
            a=m.policy(o,0,random.Random(33),env.action_space.n)
            b=m.policy(o,0,random.Random(33),env.action_space.n)
            self.assertEqual(a,b)
            self.assertGreaterEqual(a,0)
            self.assertLess(a,env.action_space.n)
        finally:
            env.close()

    def test_negative_shuffled_history_cannot_keep_previous_sequence(self):
        a=[[0.1]*m.DIMS,[0.2]*m.DIMS,[0.3]*m.DIMS]
        b=[[0.9]*m.DIMS,[0.7]*m.DIMS,[0.3]*m.DIMS]
        self.assertNotEqual(m.context(a),m.context(b))
        self.assertEqual(m.context(a,True),m.context(b,True))
        self.assertEqual(m.context(a)[0:m.DIMS],m.context(b)[0:m.DIMS])

    def test_all_arms_train_on_identical_bounded_toy_observations(self):
        rows=m.collect(m.TRAIN_ENVS[0],17)
        arms={name:m.make_model(name) for name in m.ARMS}
        clock={name:0 for name in arms}
        m.train(arms,rows,"train",clock)
        for name,model in arms.items():
            self.assertLessEqual(len(m.snapshot(model)),65536)
            self.assertEqual(m.snapshot(m.restore(m.snapshot(model))),m.snapshot(model))
            self.assertEqual(model.predict(rows["rows"][0][0]),
                             m.restore(m.snapshot(model)).predict(rows["rows"][0][0]))
            self.assertGreaterEqual(clock[name],0)
        self.assertTrue(arms["episodic_history"].seen>0)
        self.assertEqual(arms["memoryless_sgd"].count,arms["recurrent_sgd"].count)

    def test_fully_trainable_recurrent_groups_and_cold_parity(self):
        model=m.Recurrent()
        before=model.dump()
        initial=json.dumps(before,sort_keys=True)
        for i in range(45):
            x=[[round((i+j+k)%9/10,8) for k in range(m.DIMS)]
               for j in range(8)]
            y=tuple(round((i*j+1)%13/14,8) for j in range(m.OUT))
            model.learn(x,y,"train")
        self.assertNotEqual(initial,json.dumps(model.dump(),sort_keys=True))
        for key in ("wx","wh","v","b","c"):
            self.assertNotEqual(before[key],model.dump()[key],key)
        self.assertEqual(m.snapshot(model),m.snapshot(m.restore(m.snapshot(model))))

    def test_cold_eval_never_trains_any_arm(self):
        toy=m.collect(m.TRAIN_ENVS[0],17)
        arms={name:m.make_model(name) for name in m.ARMS}
        clock={name:0 for name in arms}
        m.train(arms,toy,"train",clock)
        raw={name:m.snapshot(model) for name,model in arms.items()}
        result=m.evaluate(arms,[m.collect(m.TRAIN_ENVS[1],19)],clock)
        self.assertEqual(result["episode_count"],1)
        self.assertGreater(result["forecast_count"],0)
        for name,model in arms.items():
            self.assertEqual(raw[name],m.snapshot(model))

    def test_invalid_models_and_bad_input_fail_closed(self):
        with self.assertRaises(ValueError):
            m.make_model("oracle_hidden_map")
        with self.assertRaises(ValueError):
            m.context([])
        with self.assertRaises(ValueError):
            m.context([[1.,2.]])
        with self.assertRaises(ValueError):
            m.encoded({"direction":4,"image":None},3)


if __name__=="__main__":
    unittest.main()
