"""C33 zero-environment-step tests of already archived C32 physical trace grammar."""
import copy
import hashlib
import unittest

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c33.audit import (
    validate_action_event,summarize_physical_episode,first_divergence
)


def state(x=2,y=3,d=0,front=False):
    return {"x":x,"y":y,"goal_x":6,"goal_y":6,"direction":d,
            "front_blocked":front}


def event(t,before,action,after,baseline=None,reward=0.,done=False,trunc=False):
    return {"t":t,"before":before,"original_r3_proposed":action if baseline is None else baseline,
            "executed":action,"after":after,"reward":reward,
            "terminated":done,"truncated":trunc}


def episode(rows,arm="native",seed=62021,family="MiniGrid-FourRooms-v0"):
    return {"family":family,"seed":seed,"arm":arm,
       "steps":len(rows),"native_real_turn_changes":
          sum(x["executed"]!=x["original_r3_proposed"] for x in rows),
       "source_goal":bool(rows[-1]["terminated"] and rows[-1]["reward"]>0),
       "source_collision":bool(rows[-1]["terminated"] and rows[-1]["reward"]<0),
       "source_horizon":rows[-1]["truncated"],
       "reward_sum":sum(x["reward"] for x in rows),
       "source_actual_actions":rows,
       "source_trace_sha256":hashlib.sha256(canonical(rows)).hexdigest()}


class PhysicalC32NegativeEvidence(unittest.TestCase):
    def test_adjacent_opposite_real_turns_have_reversal_receipt(self):
        a=event(0,state(d=0),0,state(d=3))
        b=event(1,state(d=3),1,state(d=0))
        result=summarize_physical_episode(episode([a,b]))
        self.assertEqual(result["adjacent_turn_undo_pairs"],1)
        self.assertEqual(result["longest_consecutive_turns_without_translation"],2)
        self.assertEqual(result["source_public_pose_revisits_within_4_steps"],1)

    def test_correct_real_source_forward_movement(self):
        a=event(0,state(d=0),2,state(x=3,d=0),reward=.7,done=True)
        report=summarize_physical_episode(episode([a]))
        self.assertEqual(report["steps"],1)
        self.assertEqual(report["goals"],1)
        self.assertEqual(report["unique_source_public_agent_poses"],2)

    def test_turn_vs_forward_physically_illegal_transition_fails(self):
        a=event(0,state(d=0),0,state(x=3,d=3))
        with self.assertRaisesRegex(ValueError,"ILLEGAL_ORIGINAL_TURN"):
            summarize_physical_episode(episode([a]))
        b=event(0,state(d=0),2,state(x=2,d=1))
        with self.assertRaisesRegex(ValueError,"ILLEGAL_ORIGINAL_FORWARD"):
            summarize_physical_episode(episode([b]))

    def test_original_forward_cannot_be_claimed_substituted_turn(self):
        a=event(0,state(d=0),0,state(d=3),baseline=2)
        with self.assertRaisesRegex(ValueError,"R3_FORWARD_OVERRIDE"):
            summarize_physical_episode(episode([a]))

    def test_source_episode_chain_gap_or_privileged_map_is_rejected(self):
        a=event(0,state(d=0),0,state(d=3))
        b=event(1,state(d=1),1,state(d=2))
        with self.assertRaisesRegex(ValueError,"UNLINKED"):
            summarize_physical_episode(episode([a,b]))
        a=event(0,state(d=0),0,state(d=3))
        a["after"]["hidden_map"]=True
        with self.assertRaisesRegex(ValueError,"PRIVILEGED"):
            summarize_physical_episode(episode([a]))

    def test_original_event_hash_and_selected_action_must_match(self):
        a=event(0,state(d=0),0,state(d=3))
        ep=episode([a])
        ep["source_trace_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
            summarize_physical_episode(ep)
        ep=episode([a])
        ep["native_real_turn_changes"]=2
        with self.assertRaisesRegex(ValueError,"REWARD_OR_TURN_DRIFT"):
            summarize_physical_episode(ep)

    def test_no_action_after_original_termination(self):
        a=event(0,state(d=0),0,state(d=3),done=True,reward=1.)
        b=event(1,state(d=3),1,state(d=0))
        with self.assertRaisesRegex(ValueError,"AFTER_TERMINATION"):
            summarize_physical_episode(episode([a,b]))

    def test_first_action_divergence_not_fictitious_later_state_pair(self):
        base=[event(0,state(d=0),0,state(d=3)),
              event(1,state(d=3),1,state(d=0))]
        native=[event(0,state(d=0),1,state(d=1))]
        d=first_divergence(episode(base,arm="r3_original"),episode(native))
        self.assertEqual(d["first_action_difference_at_step"],0)
        self.assertEqual(d["source_r3"],0)
        self.assertEqual(d["alternate"],1)

    def test_identical_action_different_physics_detected(self):
        base=[event(0,state(d=0),2,state(x=3,d=0))]
        native=[event(0,state(d=0),2,state(x=2,d=0))]
        with self.assertRaisesRegex(ValueError,"PHYSICS_UNEXPECTEDLY_DIVERGED"):
            first_divergence(episode(base,arm="r3_original"),episode(native))

    def test_observed_first_divergence_fails_on_bad_original_input(self):
        base=[event(0,state(d=0),0,state(d=3))]
        bad=[event(0,state(x=4,d=0),1,state(x=4,d=1))]
        with self.assertRaisesRegex(ValueError,"STATES_DIVERGED_BEFORE"):
            first_divergence(episode(base,arm="r3_original"),episode(bad))


if __name__=="__main__":
    unittest.main()
