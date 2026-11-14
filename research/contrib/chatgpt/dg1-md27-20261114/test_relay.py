"""DG1-MD27 frozen pre-first-use consequential physical action tests."""
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("relay.py")
spec=importlib.util.spec_from_file_location("md27_causal_relay",SOURCE)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class CausalRelayPhysicalScience(unittest.TestCase):
    def test_prereg_before_code_disjoint_no_registered_seed_execution(self):
        x=r.validate()
        self.assertEqual(r.PREREG_SHA,"148e20fedcea143344a9c596dd84d7ebe8fa6c93")
        self.assertEqual(x["parent_sha"],r.EXACT_PARENT)
        self.assertEqual(x["world"]["unseen_context"],[0,1])
        self.assertEqual(len(r.TRAIN_SEEDS),240)
        self.assertEqual(len(r.TOY_SEEDS),24)
        self.assertEqual(len(r.REGISTERED),96)
        for seed in (1030001,1030024,1030096):
            for role in ("toy","cold","train","registered"):
                with self.assertRaisesRegex(AssertionError,"REGISTERED_FIRSTUSE_FORBIDDEN"):
                    r.seed_fence(seed,role)
        self.assertFalse(set(r.TRAIN_SEEDS)&set(r.TOY_SEEDS))
        self.assertFalse(set(r.TOY_SEEDS)&set(r.COLD_SEEDS))

    def test_public_initial_causal_aliasing_and_consequential_intervention(self):
        # The same public initial observation has opposite hidden laws. No
        # policy can infer the preferred irreversible actuator without probe.
        plus=r.RelayWorld(121,r.HOLDOUT,forced_polarity=1)
        minus=r.RelayWorld(121,r.HOLDOUT,forced_polarity=-1)
        self.assertEqual(plus.observe(),minus.observe())
        self.assertNotIn("_polarity",plus.observe())
        self.assertNotIn("seed",plus.observe())
        ob1,rew1,done1=plus.step("probe")
        ob2,rew2,done2=minus.step("probe")
        self.assertFalse(done1 or done2)
        self.assertEqual(rew1,rew2)
        self.assertEqual(ob1["probe_effect"],-ob2["probe_effect"])
        self.assertEqual(ob1["phase"],"probed")
        a="apply_A"
        out1,reward1,done1=plus.step(a)
        out2,reward2,done2=minus.step(a)
        self.assertTrue(done1 and done2)
        self.assertEqual(out1["terminal_effect"],-out2["terminal_effect"])
        self.assertNotEqual(plus.receipt()["goal_success"],minus.receipt()["goal_success"])
        self.assertNotEqual(reward1,reward2)
        for world in (plus,minus):
            with self.assertRaisesRegex(AssertionError,"ILLEGAL_UNCHARGED_ACTION"):
                world.step("apply_B")

    def test_teacher_is_public_experiment_not_privileged_oracle(self):
        rows,coverage,sha=r.train_dataset()
        self.assertEqual(len(rows),240)
        self.assertEqual(sum(coverage.values()),240)
        self.assertEqual(sorted(coverage.values()),[80,80,80])
        self.assertEqual(sum(x["charged_steps"] for x in rows),480)
        self.assertTrue(all(x["probe_effect"] in (-1,1) for x in rows))
        self.assertTrue(all(x["terminal_effect"] in (-1,1) for x in rows))
        self.assertTrue(all(len(x["physical_trace_sha256"])==64 for x in rows))
        self.assertTrue(all(tuple(x["context"])!=r.HOLDOUT for x in rows))
        self.assertEqual(len(sha),64)
        # With fixed context, public target independent of latent polarity.
        self.assertEqual(set(x["action"] for x in rows),{"apply_A","apply_B"})

    def test_strong_fully_trained_conventional_not_an_oracle_leak(self):
        rows,coverage,sha=r.train_dataset()
        models=r.fit_models(rows)
        self.assertEqual(set(models),set(r.ARMS))
        self.assertTrue(all(x.trained_count==240 for x in models.values()))
        c=models["causal_composition"]
        b=models["trained_factorized_mle"]
        q=models["trained_joint_lookup"]
        expected=-1
        self.assertEqual(c.predict_relative(0,1),expected)
        self.assertEqual(b.predict_relative(0,1),expected)
        self.assertEqual(q.predict_relative(0,1),1)
        self.assertEqual(set(c.counts),{"00","10","11"})
        self.assertEqual(b.mle["probe_flip"],-1)
        self.assertEqual(b.mle["act_flip"],-1)
        for name,model in models.items():
            snapshot=model.checkpoint()
            self.assertEqual(r.Policy.restore(snapshot).checkpoint(),snapshot,name)
        public=r.RelayWorld(121,r.HOLDOUT).observe()
        self.assertEqual(c.act(public),"probe")
        self.assertIn(models["no_probe"].act(public),("apply_A","apply_B"))

    def test_real_agent_cannot_read_hidden_world_state_from_public_frame(self):
        model=r.Policy("causal_composition")
        rows,_,_=r.train_dataset()
        model.train(rows)
        plus=r.RelayWorld(121,r.HOLDOUT,forced_polarity=1)
        minus=r.RelayWorld(121,r.HOLDOUT,forced_polarity=-1)
        self.assertEqual(model.act(plus.observe()),model.act(minus.observe()))
        self.assertEqual(model.act(plus.observe()),"probe")
        for w in (plus,minus):w.step("probe")
        # Only after the physically paid observation can model change choice.
        a=model.act(plus.observe())
        b=model.act(minus.observe())
        self.assertNotEqual(a,b)
        for w,act in ((plus,a),(minus,b)):
            w.step(act)
            self.assertEqual(w.receipt()["goal_success"],1)
            self.assertEqual(w.receipt()["steps"],2)
            self.assertEqual(w.receipt()["utility"],0.89)

    def test_complete_frozen_toy_evaluation_and_cold_retention(self):
        out=r.toy_study()
        self.assertFalse(out["registered_seeds_touched"])
        self.assertEqual(out["schema"],"yggdrasil.dg1-md27-toy.v1")
        self.assertEqual(out["train_physical_steps"],480)
        self.assertTrue(out["cold_exact_trace_parity"])
        self.assertEqual(len(out["by_arm"]),7)
        self.assertEqual(len(out["toy_episodes"]),7)
        self.assertEqual(out["paired_goal_wins"],
                         sum(a["goal_success"]>b["goal_success"]
                             for a,b in zip(out["toy_episodes"]["causal_composition"],
                                            out["toy_episodes"]["trained_joint_lookup"])))
        for name,rows in out["toy_episodes"].items():
            self.assertEqual(len(rows),24)
            for x in rows:
                self.assertEqual(x["steps"],len(x["actions"]))
                self.assertEqual(x["steps"],len(x["trace"]))
                self.assertLessEqual(x["steps"],2)
                self.assertEqual(len(x["physical_trace_sha256"]),64)
        print("MD27_TOY_CLASSIFICATION:"+out["classification"],flush=True)
        print("MD27_TOY_GATES:"+json.dumps(out["toy_gates"],sort_keys=True),flush=True)
        print("MD27_TOY_RESULTS:"+json.dumps({
            "trainer_coverage":out["teacher_coverage"],
            "training_sha256":out["training_trace_sha256"],
            "scores":out["by_arm"],
            "paired_wins":out["paired_goal_wins"],
            "gain_joint":out["candidate_margin_over_joint"],
            "gain_no_probe":out["candidate_margin_over_no_probe"],
            "gain_strong":out["candidate_margin_over_strong"],
            "gain_oracle":out["candidate_margin_over_oracle"],
            "cold_parity":out["cold_exact_trace_parity"]},sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
