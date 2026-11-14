"""MD24 public-observation blocked-family toy tests; registered cohorts forbidden."""
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("md24.py")
spec=importlib.util.spec_from_file_location("md24",str(SOURCE))
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m=d.m


class BlockerCausalTransferToy(unittest.TestCase):
    def test_original_prereg_before_firstuse_and_strict_disjoint_seeds(self):
        data=d.verify_manifest()
        self.assertEqual(d.FREEZE,"81e167c174097df83e50e57e0ae6494231cbd032")
        self.assertEqual(data["status"],"PREREGISTRATION_ONLY_NO_PRIMARY_FIRST_USE")
        self.assertEqual(len(d.ARMS),6)
        with self.assertRaisesRegex(AssertionError,"REGISTERED_SEED_USE_FORBIDDEN"):
            d.physical_teacher(d.NOVEL,994001)

    def test_no_named_ball_specific_rule_or_hidden_oracle_input(self):
        src=SOURCE.read_text()
        self.assertNotIn('OBJECT_TO_IDX["ball"]',src)
        self.assertNotIn("env.unwrapped",src)
        self.assertNotIn('obs["mission"]',src)
        self.assertNotIn("get_full_grid",src)
        import gymnasium as gym
        import minigrid
        env=gym.make(d.NOVEL)
        try:
            obs,_=env.reset(seed=11)
            self.assertEqual(obs["image"].shape,(7,7,3))
            actor=d.TransferPolicy("blind_generic")
            a=actor.act(obs,0)
            altered=dict(obs)
            altered["mission"]="INACCESSIBLE MISSION SECRET"
            actor.start(11)
            self.assertEqual(a,actor.act(altered,0))
        finally:env.close()

    def test_opaque_identity_is_not_hardcoded_object_label(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        o=d.TransferPolicy("learned_transfer")
        self.assertTrue(o.opaque_type(OBJECT_TO_IDX["ball"]))
        for k in ("key","box","wall","door","goal","empty","unseen"):
            self.assertFalse(o.opaque_type(OBJECT_TO_IDX[k]))

    def test_training_effect_gate_and_permutation_ablation(self):
        import numpy as np
        from minigrid.core.constants import OBJECT_TO_IDX
        empty=OBJECT_TO_IDX["empty"]
        key=OBJECT_TO_IDX["key"]
        p=d.TransferPolicy("learned_transfer")
        sham=d.TransferPolicy("permuted_effect")
        blind=d.TransferPolicy("blind_generic")
        self.assertFalse(p.gate())
        self.assertFalse(sham.gate())
        self.assertTrue(blind.gate())
        before={"image":np.zeros((7,7,3),dtype=np.uint8),"direction":0}
        after={"image":np.zeros((7,7,3),dtype=np.uint8),"direction":0}
        before["image"][3,5,0]=key
        before["image"][3,6,0]=empty
        after["image"][3,5,0]=empty
        after["image"][3,6,0]=key
        for x in (p,sham):
            for _ in range(8):
                x.feedback(before,3,after,0,training=True)
            self.assertEqual(x.effects["pickup_clear"],8)
            self.assertEqual(x.effects["drop_place"],0)
            self.assertFalse(x.gate())
        before2={"image":after["image"].copy(),"direction":0}
        after2={"image":before["image"].copy(),"direction":0}
        for x in (p,sham):
            for _ in range(8):
                x.feedback(before2,4,after2,0,training=True)
        self.assertEqual(p.effects,sham.effects)
        self.assertTrue(p.gate())
        self.assertFalse(sham.gate())

    def test_toy_shared_experience_and_real_unknown_task_probe(self):
        data=d.toy_study()
        self.assertFalse(data["original_seeds_touched"])
        self.assertEqual(data["classification"],"TOY_ONLY")
        self.assertGreater(data["training"]["door_goals"],0)
        self.assertGreater(data["training"]["box_goals"],0)
        self.assertGreater(data["learned_effects"]["pickup_clear"],0)
        self.assertGreater(data["learned_effects"]["drop_place"],0)
        self.assertEqual(data["learned_effects"],data["control_effects"])
        self.assertEqual(set(data["novel"]),set(d.ARMS))
        self.assertTrue(all(len(rows)==6 for rows in data["novel_traces"].values()))
        print("MD24_TOY_TRAIN:"+json.dumps(data["training"],sort_keys=True),flush=True)
        print("MD24_TOY_EFFECTS:"+json.dumps(data["learned_effects"],sort_keys=True),flush=True)
        print("MD24_TOY_NOVEL:"+json.dumps(data["novel"],sort_keys=True),flush=True)
        for name in ("learned_transfer","blind_generic"):
            print("MD24_TOY_DEBUG_"+name+":"+json.dumps(
                data["novel_traces"][name][0].get("toy_debug",[]),
                sort_keys=True),flush=True)
        self.assertGreater(sum(x["goals"] for x in data["novel"].values()),0,
                           "MD24_NO_TOY_NOVEL_GOAL_COVERAGE")


if __name__=="__main__":
    unittest.main()
