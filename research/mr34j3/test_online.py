"""Bounded streaming inference + reward-only training tests on synthetic camera frames."""
import unittest
from test_public_scaffold import public_obs
from learners import LearnedTrace17, ConventionalRNN57, ObservationOnly3
from online import PublicPolicySession, PublicRuleSession
from public_scaffold import ProtocolBlocked, PublicView, KEY, BALL


def supply(session, cue=KEY, fork=BALL, gap=6):
    session.observe(PublicView.from_observation(public_obs(2)),"")
    session.observe(PublicView.from_observation(public_obs(3,cue)),"PUBLIC_CUE_EXPOSURE")
    for j in range(gap):
        session.observe(PublicView.from_observation(public_obs(j%4)),"")
    session.observe(PublicView.from_observation(public_obs(3,1,fork)),"PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")


class StreamingOfflineTests(unittest.TestCase):
    def test_live_choice_cold_state_and_reward_training(self):
        for cls in (LearnedTrace17, ConventionalRNN57, ObservationOnly3):
            p=cls(873)
            s=PublicPolicySession(p,fit=True)
            supply(s)
            decision,prob=s.choose(evaluation=False)
            self.assertIn(decision,("north","south"))
            s.update_terminal_reward(1.)
            self.assertEqual(p.episodes_fit,1)
            ev=PublicPolicySession(p,fit=False)
            supply(ev)
            checkpoint=ev.state_receipt()
            cold=PublicPolicySession.restore_state(cls.restore(p.snapshot()),checkpoint)
            self.assertEqual(cold.state_receipt(),checkpoint)
            self.assertEqual(ev.choose(evaluation=True),cold.choose(evaluation=True))
            self.assertIsNone(ev.tape)
            with self.assertRaises(ProtocolBlocked):ev.update_terminal_reward(1.)

    def test_online_memory_is_bounded_not_full_episode_copy(self):
        p=LearnedTrace17(733)
        for gap in (1,50,500):
            s=PublicPolicySession(p,fit=False)
            supply(s,gap=gap)
            receipt=s.state_receipt()
            self.assertLess(len(receipt.encode()),300)
            self.assertEqual(s.cue_age,gap)
            self.assertIsNone(s.tape)

    def test_rule_public_stream_and_perturbation(self):
        for cue,fork,outcome in ((KEY,KEY,"north"),(KEY,BALL,"south"),(BALL,KEY,"south"),(BALL,BALL,"north")):
            s=PublicRuleSession()
            supply(s,cue,fork)
            self.assertEqual(s.choose(),outcome)
        with self.assertRaises(ProtocolBlocked):PublicRuleSession().choose()

    def test_prevent_learning_or_choice_without_exposure(self):
        x=PublicPolicySession(LearnedTrace17(10),fit=False)
        with self.assertRaises(ProtocolBlocked):x.choose(evaluation=True)
        with self.assertRaises(ProtocolBlocked):x.observe(PublicView.from_observation(public_obs(3,1,BALL)),"PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")
        y=PublicPolicySession(LearnedTrace17(10),fit=True)
        supply(y)
        y.choose(evaluation=False)
        with self.assertRaises(ProtocolBlocked):y.choose(evaluation=False)
        with self.assertRaises(ProtocolBlocked):y.observe(PublicView.from_observation(public_obs(3)),"")

if __name__=="__main__":unittest.main()
