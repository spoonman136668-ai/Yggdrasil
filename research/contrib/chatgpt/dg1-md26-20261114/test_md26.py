"""MD26 original pre-first-use controls. Only frozen toy seeds may execute."""
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("md26.py")
spec=importlib.util.spec_from_file_location("md26",str(SOURCE))
q=importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class MD26RealActionControls(unittest.TestCase):
    def test_exact_prereg_disjoint_untouched_md25_and_seed_fence(self):
        p=q.prereg()
        self.assertEqual(q.FREEZE_SHA,"4c4d34f305278fde8132a7be35ecba1ba9baee0d")
        self.assertEqual(q.PARENT_SHA,"563c805f8841e39a8363d76019e86996b611ae14")
        self.assertEqual(p["status"],"PREREGISTRATION_ONLY_NO_PRIMARY_SEEDS_CONSUMED")
        self.assertEqual(p["design"]["toy_evaluation_seeds"],list(q.TOY))
        for s in (1014001,1015001,1016001,1017001,1018001,1019001):
            with self.assertRaisesRegex(AssertionError,"NO_REGISTERED_FIRST_USE"):
                q.seed_fence(s,training=True)
            with self.assertRaisesRegex(AssertionError,"NO_REGISTERED_FIRST_USE"):
                q.seed_fence(s)
        with self.assertRaisesRegex(AssertionError,"NO_REGISTERED_FIRST_USE"):
            q.seed_fence(41)
        with self.assertRaisesRegex(AssertionError,"NO_REGISTERED_FIRST_USE"):
            q.seed_fence(67,training=True)

    def test_public_view_no_named_ball_lookup_or_privileged_state(self):
        code=SOURCE.read_text()
        for forbidden in ('OBJECT_TO_IDX["ball"]','env.unwrapped',
                          'obs["mission"]',"env.agent_pos","env.grid",
                          "random.choice", "env.step("):
            self.assertNotIn(forbidden,code)
        import gymnasium as gym
        import minigrid
        env=gym.make(q.ENV)
        try:
            obs,_=env.reset(seed=67)
            self.assertEqual(obs["image"].shape,(7,7,3))
            model=q.EffectBfsPolicy("learned_effect_bfs")
            a=model.act(obs,0)
            altered=dict(obs,mission="IGNORE UNTRUSTED TEXT")
            model.start(67)
            self.assertEqual(a,model.act(altered,0))
        finally:env.close()

    def test_physical_left_vs_blind_right_when_both_sites_free(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        import numpy as np
        empty=OBJECT_TO_IDX["empty"]
        floor=OBJECT_TO_IDX["floor"]
        door=OBJECT_TO_IDX["door"]
        obs={"image":np.zeros((7,7,3),dtype=np.uint8),"direction":0}
        obs["image"][2,6,0]=empty
        obs["image"][4,6,0]=empty
        candidate=q.EffectBfsPolicy("learned_effect_bfs")
        blind=q.EffectBfsPolicy("blind_site_bfs")
        for model in (candidate,blind):
            model.effects["pickup_clear"]=8
            model.effects["drop_place"]=8
            model.pose=(0,0)
            model.tiles={(0,0):floor,(0,1):empty,(0,-1):empty,
                         (0,2):door}
            model.door_states={(0,2):2}
            model.phase="turn_right"
            model.relobj=6  # opaque carried item identity; not policy rule
            model.complete_clearance=False
        ca=candidate.act(obs,0)
        ba=blind.act(obs,0)
        self.assertEqual(ca,0,"MD26_LEARNED_CANNOT_REALIZE_LEFT_PAID_ACTION")
        self.assertEqual(ba,1,"MD26_BLIND_NOT_STRONG_RIGHT_FIRST")
        self.assertEqual(candidate.effect_selected_at_paid_action,1)
        self.assertEqual(blind.effect_selected_at_paid_action,0)
        self.assertGreater(candidate._route_cost((0,1)),
                           candidate._route_cost((0,-1)),
                           "MD26_COUNTERFACTUAL_ROUTE_NOT_CAUSAL")

    def test_all_policies_cold_snapshot_and_common_training(self):
        agents,train=q.train_toy()
        self.assertEqual(set(agents),set(q.ARMS))
        self.assertEqual(train["door_goals"],6)
        self.assertEqual(train["box_goals"],6)
        self.assertGreater(train["paid_train_steps"],0)
        a,b,c=[agents[x] for x in q.ARMS[:3]]
        self.assertEqual(a.effects,b.effects)
        self.assertEqual(b.effects,c.effects)
        self.assertGreaterEqual(a.effects["pickup_clear"],6)
        self.assertGreaterEqual(a.effects["drop_place"],6)
        for key,model in agents.items():
            snapshot=q.save(model)
            self.assertEqual(q.save(q.restore(snapshot)),snapshot,key)

    def test_toy_study_paid_trace_and_frozen_no_go_classification(self):
        out=q.toy_study()
        self.assertFalse(out["registered_first_use"])
        self.assertEqual(out["schema"],"yggdrasil.dg1-md26-toy.v1")
        self.assertEqual(len(out["charged_evaluation_traces"]),6)
        for name,rows in out["charged_evaluation_traces"].items():
            self.assertEqual(len(rows),6)
            for row in rows:
                self.assertEqual(len(row["actual_actions"]),row["steps"])
                self.assertLessEqual(row["steps"],256)
                self.assertEqual(len(row["physical_sha256"]),64)
        self.assertEqual(out["classification"]=="TOY_READY_PENDING_DUAL_PLATFORM_QUALIFICATION",
                         all(out["toy_gates"].values()))
        print("MD26_FROZEN_TOY_GATES:"+json.dumps(out["toy_gates"],sort_keys=True),flush=True)
        print("MD26_FROZEN_TOY_SUMMARY:"+json.dumps({
            "classification":out["classification"],
            "training":out["shared_training"],
            "learned_effects":out["learned_effects"],
            "arms":out["by_arm"],
            "paired_physical_trace_differences":out["paired_physical_trace_differences"],
            "strict_paired_step_wins":out["strict_paired_step_wins"],
            "mean_paid_steps_saved":out["mean_paid_steps_saved"]},
            sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
