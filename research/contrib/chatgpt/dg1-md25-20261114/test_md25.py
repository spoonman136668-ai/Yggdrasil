"""MD25 toy-only negative controls and shared scaffold acceptance tests."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).with_name("md25.py")
spec=importlib.util.spec_from_file_location("dg1_md25_toy",str(SOURCE))
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class CausalSiteDev(unittest.TestCase):
    def test_freeze_and_reserved_original_cohort_forbidden(self):
        p=d.verify_protocol()
        self.assertEqual(d.FROZEN_PREREG_SHA,
                         "f8b4d11855918a987144885f4885f0598d271136")
        self.assertEqual(p["status"],
                         "FROZEN_PREREGISTRATION_ONLY_NO_PRIMARY_EXECUTION")
        self.assertEqual(d.ARMS,tuple(p["arms"]))
        for s in (996001,997001,998001,999001,1000001,1001001):
            with self.assertRaisesRegex(AssertionError,"NO_REGISTERED_SEEDS"):
                d.physical_teacher(d.NOVEL,s)

    def test_no_ball_rule_or_mission_or_privileged_world_state(self):
        code=SOURCE.read_text()
        for term in ('OBJECT_TO_IDX["ball"]',"env.unwrapped",
                     'obs["mission"]',"env.agent_pos","env.grid"):
            self.assertNotIn(term,code)
        import gymnasium as gym
        import minigrid
        env=gym.make(d.NOVEL)
        try:
            obs,_=env.reset(seed=41)
            actor=d.SiteChoice("causal_site")
            expected=actor.act(obs,0)
            changed=dict(obs,mission="DO NOT READ MISSION")
            actor.start(41)
            self.assertEqual(expected,actor.act(changed,0))
        finally:
            env.close()

    def test_shared_postobstruction_and_box_completion_logic(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        for name in d.ARMS[:3]:
            x=d.SiteChoice(name)
            x.opened_door=True
            x.tiles={}
            self.assertEqual(x.preferred_subgoal(),"box")
            x.tiles[(1,1)]=OBJECT_TO_IDX["goal"]
            self.assertEqual(x.preferred_subgoal(),"goal")
            x.tiles={}
            x.phase=None
            x.complete_clearance=True
            # All arms dispatch to the identical inherited route scaffold.
            import numpy as np
            obs={"image":np.zeros((7,7,3),dtype=np.uint8),"direction":0}
            with patch.object(d.graph.GraphPolicy,"act",return_value=1) as spy:
                self.assertEqual(x.act(obs,1),1)
                spy.assert_called_once()

    def test_frozen_effect_gate_and_counterfactual_site_chooser(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        import numpy as np
        a,b,c=[d.SiteChoice(k) for k in d.ARMS[:3]]
        self.assertFalse(a.gate())
        self.assertTrue(b.gate())
        self.assertFalse(c.gate())
        for obj in (a,b,c):
            obj.effects={"pickup_clear":10,"drop_place":10,"toggle_shift":0}
        self.assertTrue(a.gate())
        self.assertTrue(b.gate())
        self.assertFalse(c.gate())
        image=np.full((7,7,3),OBJECT_TO_IDX["empty"],dtype=np.uint8)
        # Both sides are free; nearest door is on the right. The learned
        # occupancy effect predicts left as safer; blind chooses nearest-free
        # default right. This is a synthetic unit decision test, not a result.
        obs={"image":image,"direction":0}
        for obj in (a,b,c):
            obj.pose=(0,0)
            obj.tiles={(0,1):OBJECT_TO_IDX["door"]}
        self.assertEqual(a.predicted_drop_side(obs),"left")
        self.assertEqual(b.predicted_drop_side(obs),"right")
        self.assertEqual(c.predicted_drop_side(obs),"right")

    def test_toy_real_actions_and_sham_trace_comparison(self):
        out=d.toy_study()
        self.assertEqual(out["schema"],"yggdrasil.dg1-md25-toy.v1")
        self.assertFalse(out["registered_seeds_used"])
        self.assertFalse(out["eligible_for_registered_first_use"])
        self.assertEqual(set(out["metrics"]),set(d.ARMS))
        self.assertEqual(out["teacher"]["door_goals"],6)
        self.assertEqual(out["teacher"]["box_goals"],6)
        self.assertGreater(out["learned_counts"]["pickup_clear"],0)
        self.assertGreater(out["learned_counts"]["drop_place"],0)
        self.assertEqual(len(out["toy_traces"]["causal_site"]),6)
        self.assertEqual(out["paired_identical"]+out["paired_different"],6)
        print("MD25_TOY_CLASSIFICATION:"+out["classification"],flush=True)
        print("MD25_TOY_TRAIN:"+json.dumps(out["teacher"],sort_keys=True),flush=True)
        print("MD25_TOY_LEARNED_COUNTS:"+json.dumps(out["learned_counts"],sort_keys=True),flush=True)
        print("MD25_TOY_METRICS:"+json.dumps(out["metrics"],sort_keys=True),flush=True)
        print("MD25_TOY_PAIRED:"+json.dumps({
            "identical":out["paired_identical"],
            "different":out["paired_different"],
            "total_goals":out["novel_goals_all_arms"]},sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
