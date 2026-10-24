"""Reward-only learner algebra tests with synthetic public fixtures, no env use."""
import unittest
import numpy as np
from test_public_scaffold import public_obs
from public_scaffold import KEY, BALL, PublicView, ProtocolBlocked
from learners import (
    Episode, LearnedTrace17, ConventionalRNN57, ObservationOnly3,
    verify_capacity, fit_only_donor_cue,
)


def fixture(cue=KEY, fork=BALL, gap=5):
    events=[(PublicView.from_observation(public_obs(3,cue)), "PUBLIC_CUE_EXPOSURE")]
    events.extend((PublicView.from_observation(public_obs(3)), "") for _ in range(gap))
    events.append((PublicView.from_observation(public_obs(3,1,fork)),"PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE"))
    return Episode.from_public_events(events)


class LearnerUnitTests(unittest.TestCase):
    def test_capacity_exact(self):
        self.assertEqual(verify_capacity(), {"LearnedTrace17":17,"ConventionalRNN57":57,"ObservationOnly3":3})

    def test_public_episode_order_and_scope(self):
        ep=fixture(KEY,BALL,gap=7)
        self.assertEqual(ep.intervening,7)
        self.assertEqual(ep.cue.tolist(),[1.,0.])
        self.assertEqual(ep.fork.tolist(),[0.,1.])
        for events in ([], [(PublicView.from_observation(public_obs(3,1,BALL)), "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")]):
            with self.assertRaises(ProtocolBlocked):Episode.from_public_events(events)

    def test_deterministic_roundtrip_and_reward_only(self):
        ep=fixture()
        for cls in (LearnedTrace17,ConventionalRNN57,ObservationOnly3):
            a=cls(123)
            self.assertEqual(a.snapshot(),cls.restore(a.snapshot()).snapshot())
            self.assertEqual(a.action(ep,evaluation=True),cls.restore(a.snapshot()).action(ep,evaluation=True))
            selected,p=a.action(ep)
            self.assertTrue(0.<p<1.)
            before=a.snapshot()
            a.update(ep,selected,1.)
            self.assertNotEqual(a.snapshot(),before)
            b=cls.restore(a.snapshot())
            self.assertEqual(a.action(ep,evaluation=True),b.action(ep,evaluation=True))
            with self.assertRaises(ProtocolBlocked):a.update(ep,"north",-1.)
            with self.assertRaises(ProtocolBlocked):a.update(ep,"up",1.)

    def test_gradient_matches_finite_difference(self):
        ep=fixture(KEY,BALL,gap=3)
        for cls in (LearnedTrace17, ConventionalRNN57, ObservationOnly3):
            policy=cls(999)
            z,grad=policy.logit_and_gradient(ep)
            self.assertTrue(np.isfinite(z))
            for k in sorted(policy.weights):
                original=policy.weights[k]
                for index in np.ndindex(original.shape):
                    old=original[index].item()
                    original[index]=old+1e-6
                    plus=policy.logit_and_gradient(ep)[0]
                    original[index]=old-1e-6
                    minus=policy.logit_and_gradient(ep)[0]
                    original[index]=old
                    self.assertAlmostEqual((plus-minus)/(2e-6),grad[k][index],places=5,msg=f"{cls.__name__}/{k}/{index}")

    def test_trace_gap_and_cue_dependence(self):
        a=LearnedTrace17(3)
        self.assertNotEqual(a.logit_and_gradient(fixture(KEY,BALL))[0], a.logit_and_gradient(fixture(BALL,BALL))[0])
        self.assertNotEqual(a.logit_and_gradient(fixture(KEY,BALL,gap=0))[0], a.logit_and_gradient(fixture(KEY,BALL,gap=20))[0])

    def test_navigation_observations_in_non_north_headings_are_allowed(self):
        sequence=[(PublicView.from_observation(public_obs(0)), ""),
                  (PublicView.from_observation(public_obs(2)), ""),
                  (PublicView.from_observation(public_obs(3,KEY)), "PUBLIC_CUE_EXPOSURE"),
                  (PublicView.from_observation(public_obs(0)), ""),
                  (PublicView.from_observation(public_obs(3,1,BALL)), "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")]
        self.assertEqual(Episode.from_public_events(sequence).intervening, 1)

    def test_ablation_dev_and_held_share_canonical_sealed_fit_donor(self):
        from source_attempt_intent import fit_only_donor_index, seeds
        fit = tuple((1., 0.) if i % 2 else (0., 1.) for i in range(768))
        for phase in ('DEV','HELD'):
            for seed in seeds(phase):
                self.assertEqual(fit_only_donor_cue(fit, seed), fit[fit_only_donor_index(seed)])
                self.assertEqual(fit_only_donor_cue(fit, seed), fit_only_donor_cue(fit, seed))
        with self.assertRaises(ProtocolBlocked):fit_only_donor_cue(fit[:1],seeds('HELD')[0])
        for seed in (-10, seeds('FIT')[0], seeds('PREFLIGHT')[0], 3_200_999):
            with self.subTest(seed=seed),self.assertRaises(ProtocolBlocked):
                fit_only_donor_cue(fit,seed)
        with self.assertRaises(ProtocolBlocked):
            fit_only_donor_cue(fit,seeds('DEV')[0],salt=341304)

    def test_cold_restore_and_rng_stream(self):
        ep=fixture()
        for cls in (LearnedTrace17,ConventionalRNN57):
            a=cls(1301)
            b=cls.restore(a.snapshot())
            self.assertEqual([a.action(ep)[0] for _ in range(20)],[b.action(ep)[0] for _ in range(20)])

if __name__=="__main__":unittest.main()
