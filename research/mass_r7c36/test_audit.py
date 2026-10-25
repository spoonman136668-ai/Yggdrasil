"""C36 source-only tests of physical two-action contrast and provenance.

All constructed states in this file are explicit synthetic validation fixtures.
None are claimed to have been returned by original MiniGrid.
"""
import hashlib
import copy
import unittest
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c36.audit import validate_anchor,contrasted,validate_selected_step


def st(x=4,y=4,d=0,front=False):
    return {"x":x,"y":y,"goal_x":6,"goal_y":6,"direction":d,
            "front_blocked":front}


def action(a,s):
    n=copy.deepcopy(s)
    if a==0:n["direction"]=(s["direction"]-1)%4
    if a==1:n["direction"]=(s["direction"]+1)%4
    if a==2:
        motion=((1,0),(0,1),(-1,0),(0,-1))[s["direction"]]
        n["x"]+=motion[0];n["y"]+=motion[1]
    return {"action":a,"before":copy.deepcopy(s),"after":n,
       "reward":0.0,"term":False,"trunc":False}


def row():
    start=st()
    pairs={}
    distance=lambda x:abs(x["goal_x"]-x["x"])+abs(x["goal_y"]-x["y"])
    for a in range(3):
        for b in range(3):
            first=action(a,start)
            second=action(b,first["after"])
            steps=[first,second]; after=steps[-1]["after"]
            pairs[f"{a}{b}"]={"pair":[a,b],"completed_two_original_actions":True,
                "actual_selected_source_actions":steps,
                "actually_observed_next_front_blocked":after["front_blocked"],
                "real_two_step_goal_distance_improvement":distance(start)-distance(after),
                "actual_source_reward_sum":0.,
                "actual_agent_translation":abs(after["x"]-start["x"])+abs(after["y"]-start["y"]),
                "physical_trace_sha256":hashlib.sha256(canonical(steps)).hexdigest()}
    return {"family":"MiniGrid-FourRooms-v0","seed":74101,"tick":0,
       "public_initial":start,"anchor_source_sha256":"0"*64,
       "original_source_prefix":[],"all_nine_original_physical_pairs":pairs}


class GenuineMatchedInterventionReceiptUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        from pathlib import Path
        cls.protocol=json.loads((Path(__file__).parents[1]/"mass_r7c35"/"PREREG.json").read_text())

    def test_original_two_action_matched_fork_grammar(self):
        seen=validate_anchor(row(),self.protocol,"FIT")
        self.assertEqual(len(seen),9)

    def test_original_same_two_tick_turn_kinematic_controls(self):
        x=validate_anchor(row(),self.protocol,"FIT")
        self.assertTrue(contrasted(x["01"],x["10"])["agent_pose_heading_same"])
        self.assertTrue(contrasted(x["00"],x["11"])["agent_pose_heading_same"])
        self.assertTrue(contrasted(x["01"],x["10"])["full_public_after_same"])

    def test_physical_left_forward_order_is_not_interchangeable(self):
        x=validate_anchor(row(),self.protocol,"FIT")
        q=contrasted(x["02"],x["20"])
        self.assertFalse(q["agent_pose_heading_same"])
        self.assertFalse(q["goal_progress_same"])

    def test_malformed_privileged_after_public_fields_fail_closed(self):
        s=row();s["all_nine_original_physical_pairs"]["01"]["actual_selected_source_actions"][0]["after"]["private_map"]=1
        with self.assertRaisesRegex(ValueError,"SOURCE_SELECTED_RETURN_SHA_DRIFT"):
            validate_anchor(s,self.protocol,"FIT")

    def test_modified_real_source_hash_is_denied(self):
        s=row();s["all_nine_original_physical_pairs"]["12"]["physical_trace_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_SELECTED_RETURN_SHA_DRIFT"):
            validate_anchor(s,self.protocol,"FIT")

    def test_missing_actual_pair_is_not_counterfactual_imputation(self):
        s=row();del s["all_nine_original_physical_pairs"]["22"]
        with self.assertRaisesRegex(ValueError,"ACTUAL_PAIR_MISSING"):
            validate_anchor(s,self.protocol,"FIT")

    def test_original_source_seed_role_cannot_change_after_freeze(self):
        s=row();s["seed"]=75201
        with self.assertRaisesRegex(ValueError,"COHORT_ROLE_DRIFT"):
            validate_anchor(s,self.protocol,"FIT")

    def test_real_selected_forward_action_must_preserve_heading(self):
        r=action(2,st());r["after"]["direction"]=1
        with self.assertRaisesRegex(ValueError,"FORWARD_PHYSICS"):
            validate_selected_step(r,2,r["before"])

    def test_true_source_terminal_must_stop_physical_second_action(self):
        s=row();t=s["all_nine_original_physical_pairs"]["00"]
        t["actual_selected_source_actions"][0]["term"]=True
        t["physical_trace_sha256"]=hashlib.sha256(canonical(t["actual_selected_source_actions"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"AFTER_FIRST_TERMINATION"):
            validate_anchor(s,self.protocol,"FIT")

    def test_same_public_agent_pose_can_have_distinct_source_front_outcome(self):
        x=validate_anchor(row(),self.protocol,"FIT")
        a=dict(x["01"]);b=dict(x["10"])
        b["end"]={**b["end"],"front_blocked":True}
        z=contrasted(a,b)
        self.assertTrue(z["agent_pose_heading_same"])
        self.assertTrue(z["final_front_diff_with_same_agent_pose"])
        self.assertFalse(z["full_public_after_same"])

if __name__=="__main__":
    unittest.main()
