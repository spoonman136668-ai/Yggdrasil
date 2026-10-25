"""C28 strictly source-free schema tests; no original environment actions."""
import copy
import unittest
from research.mass_r7c28.run import P, validate_episode

FAMILY="MiniGrid-FourRooms-v0"
SEED=P["new_fit_episodes"][FAMILY][0]


def legal_history():
    # Synthetic grammar only. NOT external world evidence or fitted learning.
    return [
      [2,3,0,6,6,0,0,1,2,3,3,1,0.,0,0],
      [2,3,3,6,6,1,1,0,2,3,0,0,0.,0,0],
      [2,3,0,6,6,0,2,0,3,3,0,0,1.,1,0]
    ]


class FrozenSourcePublicFitReceipt(unittest.TestCase):
    def test_all_three_action_families_and_true_return_are_recorded(self):
        events,r=validate_episode(FAMILY,SEED,legal_history(),256)
        self.assertEqual(r["action_family_counts"],{"left":1,"right":1,"forward":1})
        self.assertEqual(r["information_turn_returned_front"],{"clear":0,"blocked":1})
        self.assertEqual([x["chosen_action"] for x in events],[0,1,2])
        self.assertTrue(events[-1]["terminated"])

    def test_nonfrozen_family_or_seed_fails(self):
        with self.assertRaises(ValueError):
            validate_episode("NonOriginal",SEED,legal_history(),256)
        with self.assertRaises(ValueError):
            validate_episode(FAMILY,123456,legal_history(),256)

    def test_action_return_pose_invalid_fails(self):
        rows=legal_history();rows[0][10]=0
        with self.assertRaisesRegex(ValueError,"TURN_SOURCE_EFFECT"):
            validate_episode(FAMILY,SEED,rows,256)
        rows=legal_history();rows[2][8]=8
        with self.assertRaisesRegex(ValueError,"FORWARD_SOURCE_EFFECT"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_returned_state_cannot_be_replaced_silently(self):
        rows=legal_history();rows[1][0]=4
        with self.assertRaisesRegex(ValueError,"BROKEN_ACTION"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_malformed_extra_metadata_rejected(self):
        rows=legal_history();rows[0].append({"hidden_map":"forbidden"})
        with self.assertRaisesRegex(ValueError,"PUBLIC_EVENT_SCHEMA"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_illegal_bool_int_or_action_rejected(self):
        rows=legal_history();rows[0][6]=True
        with self.assertRaisesRegex(ValueError,"NONINTEGER_OR_BOOL"):
            validate_episode(FAMILY,SEED,rows,256)
        rows=legal_history();rows[0][6]=7
        with self.assertRaisesRegex(ValueError,"ILLEGAL_ACTION"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_no_missing_steps_after_terminal(self):
        rows=legal_history();rows[1][13]=1
        with self.assertRaisesRegex(ValueError,"AFTER_TERMINAL"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_no_probe_metadata_on_forward_action(self):
        rows=legal_history();rows[2][7]=1
        with self.assertRaisesRegex(ValueError,"INFORMATION_TURN"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_goal_drift_and_nonfinite_rewards_refused(self):
        rows=legal_history();rows[1][3]=7
        with self.assertRaisesRegex(ValueError,"GOAL_CHANGED"):
            validate_episode(FAMILY,SEED,rows,256)
        rows=legal_history();rows[0][12]=float("nan")
        with self.assertRaisesRegex(ValueError,"SOURCE_REWARD"):
            validate_episode(FAMILY,SEED,rows,256)

    def test_step_budget_and_termination_consistency(self):
        with self.assertRaisesRegex(ValueError,"EVENT_COUNT"):
            validate_episode(FAMILY,SEED,legal_history(),2)
        rows=legal_history();rows[2][14]=1
        with self.assertRaisesRegex(ValueError,"INCONSISTENT"):
            validate_episode(FAMILY,SEED,rows,256)


if __name__=="__main__":
    unittest.main()
