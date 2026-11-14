"""MD28 frozen test controls: live charged observations and adaptive policies only."""
import importlib.util
import json
from pathlib import Path
import unittest
SOURCE=Path(__file__).with_name("shifting_relay.py")
spec=importlib.util.spec_from_file_location("dg1_md28",SOURCE)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class DynamicConsequenceControls(unittest.TestCase):
    def test_frozen_prereg_before_code_and_reserved_original_seeds(self):
        p=r.validate()
        self.assertEqual(r.FREEZE,"3b89e764ee859cc17ebaeea7bef6403cb770e3ea")
        self.assertEqual(p["exact_parent_sha"],r.PARENT)
        self.assertEqual(p["data"]["training_contexts"],[[0,0],[1,0],[1,1]])
        self.assertEqual(len(r.TRAIN),240)
        self.assertEqual(len(r.TOY),48)
        self.assertEqual(len(r.COLD),12)
        self.assertEqual(len(r.REGISTERED),96)
        for seed in (1050001,1050011,1050096):
            for role in ("train","toy","cold","registered"):
                with self.assertRaisesRegex(AssertionError,"REGISTERED_FIRST_USE_FORBIDDEN"):
                    r.seed_fence(seed,role)
        self.assertFalse(set(r.TRAIN)&set(r.TOY))
        self.assertFalse(set(r.TOY)&set(r.COLD))

    def test_same_public_start_opposite_polarity_and_shift_not_revealed_for_free(self):
        plus=r.ShiftingRelay(181,r.HOLDOUT,polarity_override=1,flip_override=True)
        minus=r.ShiftingRelay(181,r.HOLDOUT,polarity_override=-1,flip_override=True)
        self.assertEqual(plus.observe(),minus.observe())
        for secret in ("_latent","_will_flip","seed","flip_event"):
            self.assertNotIn(secret,plus.observe())
        a=r.Agent("causal_adaptive")
        rows,_,_=r.dataset()
        a.train(rows)
        self.assertEqual(a.act(plus.observe()),a.act(minus.observe()))
        self.assertEqual(a.act(plus.observe()),"disturb") # high hazard
        for env in (plus,minus):env.step("disturb")
        self.assertEqual(plus.observe(),minus.observe())
        self.assertEqual(a.act(plus.observe()),"post_probe")
        for env in (plus,minus):env.step("post_probe")
        self.assertEqual(plus.observe()["post_probe_effect"],
                         -minus.observe()["post_probe_effect"])
        self.assertNotEqual(a.act(plus.observe()),a.act(minus.observe()))
        for env in (plus,minus):
            env.step(a.act(env.observe()))
            receipt=env.receipt()
            self.assertEqual(receipt["official_goal"],1)
            self.assertEqual(receipt["paid_steps"],3)
            self.assertEqual(receipt["utility"],0.73)
            with self.assertRaisesRegex(AssertionError,"ILLEGAL_OR_UNCHARGED_ACTION"):
                env.step("post_probe")

    def test_physical_probe_and_hidden_dynamic_transition_under_two_hazards(self):
        for hazard_seed in (182,181):
            for flipped in (False,True):
                env=r.ShiftingRelay(hazard_seed,r.HOLDOUT,
                                    polarity_override=1,flip_override=flipped)
                before,rew,done=env.step("pre_probe")
                self.assertFalse(done)
                self.assertEqual(rew,-0.03)
                first=before["pre_probe_effect"]
                after,rew,done=env.step("disturb")
                self.assertFalse(done)
                self.assertEqual(rew,-0.04)
                self.assertIsNone(after["post_probe_effect"])
                again,rew,done=env.step("post_probe")
                self.assertFalse(done)
                self.assertEqual(rew,-0.20)
                self.assertEqual(again["post_probe_effect"],
                                 -first if flipped else first)
                env.step("apply_A")
                receipt=env.receipt()
                self.assertEqual(receipt["paid_steps"],4)
                self.assertEqual(len(receipt["trace_sha256"]),64)

    def test_public_paid_training_data_balanced_and_strong_baseline_fully_fitted(self):
        rows,coverage,sha=r.dataset()
        self.assertEqual(len(rows),240)
        self.assertEqual(sum(coverage.values()),240)
        self.assertEqual(set(coverage.values()),{40})
        self.assertEqual(sum(x["charged_steps"] for x in rows),960)
        self.assertEqual(set(tuple(x["context"]) for x in rows),set(r.CONTEXTS))
        self.assertNotIn(r.HOLDOUT,set(tuple(x["context"]) for x in rows))
        self.assertEqual(len(sha),64)
        self.assertTrue(all(len(x["trace"])==4 for x in rows))
        models=r.fit(rows)
        self.assertEqual(set(models),set(r.ARMS))
        self.assertTrue(all(x.n_training==240 for x in models.values()))
        c=models["causal_adaptive"]
        m=models["trained_factorized_adaptive_mle"]
        j=models["trained_joint_adaptive"]
        self.assertEqual(c.relative_sign(0,1),-1)
        self.assertEqual(m.relative_sign(0,1),-1)
        self.assertEqual(j.relative_sign(0,1),1)
        self.assertEqual(m.mle,{"base":1,"probe":-1,"actuator":-1})
        for name,model in models.items():
            snap=model.checkpoint()
            self.assertEqual(r.Agent.restore(snap).checkpoint(),snap,name)

    def test_real_adaptive_paid_probe_choice_is_measured_not_counter(self):
        rows,_,_=r.dataset()
        c=r.Agent("causal_adaptive")
        c.train(rows)
        low=r.ShiftingRelay(182,r.HOLDOUT)
        high=r.ShiftingRelay(181,r.HOLDOUT)
        self.assertEqual(c.strategy(low.observe()),"pre_only")
        self.assertEqual(c.strategy(high.observe()),"post_only")
        self.assertEqual(c.act(low.observe()),"pre_probe")
        self.assertEqual(c.act(high.observe()),"disturb")
        low.step(c.act(low.observe()))
        low.step(c.act(low.observe()))
        self.assertIn(c.act(low.observe()),("apply_A","apply_B"))
        high.step(c.act(high.observe()))
        self.assertEqual(c.act(high.observe()),"post_probe")

    def test_frozen_full_toy_result_versus_strongest_conventional_control(self):
        out=r.toy_study()
        self.assertEqual(out["schema"],"yggdrasil.dg1-md28-toy.v1")
        self.assertFalse(out["registered_seeds_used"])
        self.assertTrue(out["cold_trace_parity"])
        self.assertEqual(set(out["scores"]),set(r.ARMS))
        self.assertTrue(all(len(v)==48 for v in out["physical_toy_traces"].values()))
        for name,episodes in out["physical_toy_traces"].items():
            for e in episodes:
                self.assertEqual(len(e["actions"]),e["paid_steps"])
                self.assertLessEqual(e["paid_steps"],4)
                self.assertEqual(len(e["trace_sha256"]),64)
        print("MD28_TOY_CLASSIFICATION:"+out["classification"],flush=True)
        print("MD28_TOY_GATES:"+json.dumps(out["toy_gates"],sort_keys=True),flush=True)
        print("MD28_TOY_RESULTS:"+json.dumps({
            "training":out["training"],
            "scores":out["scores"],
            "paired_strict_reward_wins":out["paired_strict_reward_wins"],
            "gain_post":out["advantage_over_post"],
            "gain_no_probe":out["advantage_over_no_probe"],
            "gain_strong":out["strong_baseline_tie"],
            "cold_trace_parity":out["cold_trace_parity"]},
            sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
