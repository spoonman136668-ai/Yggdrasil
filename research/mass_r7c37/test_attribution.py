"""C37 source-free synthetic contract tests; NOT an original MiniGrid execution."""
import hashlib
import copy
import unittest
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c37.attribution import audit_episode, first_divergence


def state(x=2,y=2,d=0,front=False):
    return {"x":x,"y":y,"goal_x":6,"goal_y":6,"direction":d,
       "front_blocked":front}


def step(t,b,a,after,proposed=None,reward=0.,terminal=False,trunc=False,option=False,second=False):
    return {"t":t,"before":copy.deepcopy(b),"R3_proposed":a if proposed is None else proposed,
       "real_selected":a,"real_after":copy.deepcopy(after),
       "reward":reward,"terminal":terminal,"trunc":trunc,
       "two_step_option_started":option,"option_second_action":second}


def episode(steps,arm="causal_two_step"):
    return {"family":"MiniGrid-FourRooms-v0","seed":86101,"arm":arm,
       "actual_source_steps":len(steps),"real_true_source_actions":steps,
       "trace_sha256":hashlib.sha256(canonical(steps)).hexdigest(),
       "checkpoint_cold":{"fresh_os":True},
       "real_goal":bool(steps[-1]["terminal"] and steps[-1]["reward"]>0),
       "real_collision":bool(steps[-1]["terminal"] and steps[-1]["reward"]<0),
       "real_horizon":steps[-1]["trunc"],
       "real_reward":sum(q["reward"] for q in steps),
       "actually_executed_overrides":sum(q["real_selected"]!=q["R3_proposed"] for q in steps)}


class OriginalSelectedPolicyMechanisticUnit(unittest.TestCase):
    def test_real_turn_pair_undo_and_recent_public_pose_revisit(self):
        first=step(0,state(d=0),0,state(d=3))
        second=step(1,state(d=3),1,state(d=0))
        r=audit_episode(episode([first,second]))
        self.assertEqual(r["adjacent_opposite_turn_undo"],1)
        self.assertEqual(r["source_pose_revisits_within_four_physical_steps"],1)
        self.assertEqual(r["max_source_turn_run_without_translation"],2)

    def test_physical_original_turn_override_and_model_option(self):
        s=step(0,state(d=0),0,state(d=3),proposed=1,option=True)
        x=audit_episode(episode([s]))
        self.assertEqual(x["R3_turn_overrides"],1)
        self.assertEqual(x["observed_two_step_option_starts"],1)

    def test_real_goal_reward_terminal(self):
        e=step(0,state(d=0),2,state(x=3,d=0),reward=.8,terminal=True)
        x=audit_episode(episode([e]))
        self.assertEqual(x["goal"],1)
        self.assertAlmostEqual(x["reward"],.8)
        self.assertEqual(x["steps"],1)

    def test_physical_chosen_action_difference_same_source_before(self):
        a=episode([step(0,state(d=0),0,state(d=3))],arm="original_r3")
        b=episode([step(0,state(d=0),1,state(d=1))])
        diff=first_divergence(a,b)
        self.assertEqual(diff["first_physical_selected_action_difference_at"],0)

    def test_do_not_compare_different_source_states_after_policy_divergence(self):
        a=episode([step(0,state(d=0),2,state(x=3,d=0))],arm="original_r3")
        b=episode([step(0,state(d=0),2,state(x=2,d=0))])
        with self.assertRaisesRegex(ValueError,"PHYSICS_DIVERGED"):
            first_divergence(a,b)

    def test_reject_private_source_grid_leak(self):
        s=step(0,state(),0,state(d=3))
        s["before"]["full_grid"]=[[2,3]]
        with self.assertRaisesRegex(ValueError,"UNQUALIFIED"):
            audit_episode(episode([s]))

    def test_reject_action_trace_tamper(self):
        e=step(0,state(),0,state(d=3))
        q=episode([e]);q["trace_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"DIGEST_DRIFT"):
            audit_episode(q)

    def test_reject_original_forward_turn_override(self):
        e=step(0,state(d=0),1,state(d=1),proposed=2)
        with self.assertRaisesRegex(ValueError,"FORWARD_GUARD"):
            audit_episode(episode([e]))

    def test_reject_impossible_source_turn_displacement(self):
        e=step(0,state(d=0),0,state(x=3,d=3))
        with self.assertRaisesRegex(ValueError,"PHYSICAL_TURN"):
            audit_episode(episode([e]))

    def test_reject_post_terminal_selected_action(self):
        a=step(0,state(d=0),0,state(d=3),terminal=True,reward=1.)
        b=step(1,state(d=3),1,state(d=0))
        with self.assertRaisesRegex(ValueError,"TERMINAL_BREAK"):
            audit_episode(episode([a,b]))

    def test_reject_missing_genuine_original_cold_restart(self):
        e=step(0,state(d=0),0,state(d=3))
        x=episode([e]);x["checkpoint_cold"]["fresh_os"]=False
        with self.assertRaisesRegex(ValueError,"COLD_POLICY"):
            audit_episode(x)

    def test_false_source_rewards_cannot_be_silent(self):
        e=step(0,state(d=0),0,state(d=3))
        x=episode([e]);x["real_reward"]=6.0
        with self.assertRaisesRegex(ValueError,"REWARD_DRIFT"):
            audit_episode(x)

if __name__=="__main__":
    unittest.main()
