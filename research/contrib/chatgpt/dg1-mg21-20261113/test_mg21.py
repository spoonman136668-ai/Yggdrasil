"""MG21 first-use preflight, toy seeds 11/17/19 ONLY."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).with_name("mg21.py")
spec=importlib.util.spec_from_file_location("mg21",path)
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
m=p.m


class PositiveSourcePreflight(unittest.TestCase):
    def test_frozen_source_and_new_seed_manifest(self):
        p.verify_manifest()
        self.assertEqual(p.FREEZE,"36d6155a9b3c254f31c05bdb5f1e3469fcff616b")
        self.assertEqual(p.MANIFEST_HASH,"2f254e2a115fee9bd7d68e130d013479acb3804fd584348cce980dba7802db7f")
        self.assertEqual(p.PARENT,"9477ea4b366f2287eb316460514726cd6d2dfa7e")
        self.assertEqual(len(p.TRAIN_SEEDS),24)
        self.assertEqual(len(p.COLD_SEEDS),12)
        self.assertNotIn(11,p.TRAIN_SEEDS)
        self.assertNotIn(17,p.COLD_SEEDS)
        self.assertNotIn(19,p.FAMILY_SEEDS)

    def test_positive_real_reward_teacher_toy(self):
        trials=[p.teacher_trace(m.TRAIN_ENVS[0],seed) for seed in (11,17,19)]
        self.assertTrue(all(0<ep["steps"]<=128 for ep in trials))
        self.assertTrue(any(ep["success"] for ep in trials),
                        "MG21_PRETEST_TRAIN_TEACHER_NO_GOAL_EVENTS")
        self.assertTrue(all(len(ep["sha256"])==64 for ep in trials))

    def test_frozen_teacher_deterministic_and_no_oracle(self):
        a=p.teacher_trace(m.TRAIN_ENVS[1],17)
        b=p.teacher_trace(m.TRAIN_ENVS[1],17)
        self.assertEqual(a["sha256"],b["sha256"])
        self.assertEqual(a["success"],b["success"])
        self.assertEqual(a["steps"],len(a["transitions"]))
        self.assertTrue(all(t[1] in m.ACTIONS for t in a["transitions"]))

    def test_real_teacher_shared_with_all_controls(self):
        models={name:m.make_agent(name) for name in m.ARMS}
        eps,goals,charged=p.train_on_positive_teacher(models,(11,17),
                                                      m.TRAIN_ENVS[:1],"train")
        self.assertEqual(len(eps),2)
        self.assertEqual(charged,sum(e["steps"] for e in eps))
        self.assertEqual(goals,sum(e["success"] for e in eps))
        self.assertEqual(models["recurrent_imitation"].count,charged)
        self.assertEqual(models["tabular_q"].count,charged)
        self.assertEqual(models["causal_map"].passability,
                         models["sham_map"].passability)
        for a in models.values():
            self.assertEqual(m.save(a),m.save(m.load(m.save(a))))

    def test_all_recurrent_weight_groups_pretrain(self):
        learner=m.RecurrentImitation()
        before=m.canon(learner.dump())
        for i in range(60):
            seq=[[round(((i*13+j*11+k)%19)/20,8)
                  for k in range(m.FEATURES)] for j in range(m.HISTORY)]
            learner.learn(seq,m.ACTIONS[i%len(m.ACTIONS)],2.)
        self.assertNotEqual(before,m.canon(learner.dump()))
        self.assertGreater(learner.count,0)

    def test_both_models_read_only_evaluation(self):
        models={k:m.make_agent(k) for k in m.ARMS}
        p.train_on_positive_teacher(models,(17,),m.TRAIN_ENVS[:1],"train")
        original={k:m.save(v) for k,v in models.items()}
        data=m.score(models,m.COLD_ENV,(11,19))
        self.assertEqual(len(data["episodes"]),5)
        self.assertGreater(data["counted_env_steps"],0)
        for k,v in models.items():
            self.assertEqual(original[k],m.save(v))

    def test_per_seed_wins_real_official_return(self):
        models={k:m.make_agent(k) for k in m.ARMS}
        data=m.score(models,m.TRAIN_ENVS[0],tuple(range(11,23)))
        best,wins=p.per_seed_wins(data)
        self.assertIn(best,m.ARMS)
        self.assertNotEqual(best,"causal_map")
        self.assertGreaterEqual(wins,0)
        self.assertLessEqual(wins,12)

    def test_bounded_cold_memory_not_hidden_goal(self):
        model=m.make_agent("causal_map")
        trial=p.teacher_trace(m.TRAIN_ENVS[0],11)
        for before,a,reward,after,_ in trial["transitions"]:
            model.feedback(before,a,after,reward,training=True)
        self.assertLessEqual(len(m.save(model)),65536)
        self.assertEqual(m.save(model),m.save(m.load(m.save(model))))

    def test_wrong_prereg_and_no_duplicate_original_data(self):
        self.assertEqual(p.CORE_SOURCE,p.PARENT)
        self.assertFalse(set(p.TRAIN_SEEDS)&set(m.TRAIN_SEEDS))
        self.assertFalse(set(p.COLD_SEEDS)&set(m.COLD_SEEDS))
        with self.assertRaises(ValueError):
            m.make_agent("oracle_global_map")


if __name__=="__main__":
    unittest.main()
