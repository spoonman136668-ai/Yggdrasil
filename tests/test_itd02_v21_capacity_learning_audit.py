"""V21 fixed-source information bottleneck negative controls."""
import unittest

from research.itd02_v21_capacity_learning_audit import (
    CHANNELS, CONTEXTS, PUBLIC_HISTORIES, capacity, design_features,
    leave_one_out, local_channels, rank,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, PUBLIC_CUES, site_pulses,
)
from yggdrasil.itd02_v20_causal_credit_dev import ResponsibilityGatedRingDev


class V21LocalInformationTests(unittest.TestCase):
    def test_original_site_and_no_hop_public_input(self):
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                pulse = site_pulses(cue, first)
                self.assertEqual(sum(sum(x) for x in pulse), 2.0)
                for second in ACTIONS:
                    for count in (0, 1, 2, 3, 4):
                        channels = local_channels(
                            cue, first, second, hops=count,
                            retained=tuple(range(CHANNELS)))
                        self.assertEqual(len(channels), CHANNELS)
                        self.assertTrue(all(x >= 0.0 for x in channels))
                    zero_hop = local_channels(
                        cue, first, second, hops=0,
                        retained=tuple(range(CHANNELS)))
                    site = ACTION_SITES[ACTIONS.index(second)]
                    self.assertEqual(zero_hop, pulse[site])
                    # Cue source is always at original non-action site.
                    self.assertEqual(zero_hop[:4], [0.0] * 4)

    def test_masks_remove_only_named_source_tag(self):
        for cue, first, second in CONTEXTS:
            full = local_channels(
                cue, first, second, hops=4,
                retained=tuple(range(CHANNELS)))
            for masked_out in range(CHANNELS):
                current = local_channels(
                    cue, first, second, hops=4,
                    retained=tuple(j for j in range(CHANNELS)
                                   if j != masked_out))
                self.assertEqual(current[masked_out], 0.)
                self.assertEqual(
                    [current[j] for j in range(CHANNELS) if j != masked_out],
                    [full[j] for j in range(CHANNELS) if j != masked_out])
                self.assertEqual(len(
                    design_features(cue, first, second, hops=4)), 20)
        with self.assertRaises(ValueError):
            local_channels("LRV", "Backup", "GoForward",
                           hops=5, retained=tuple(range(CHANNELS)))
        with self.assertRaises(ValueError):
            local_channels("LRV", "Backup", "GoForward",
                           hops=4, retained=(0,0))
        with self.assertRaises(ValueError):
            local_channels("LRV", "Backup", "GoForward",
                           hops=4, retained=(0,7))

    def test_per_head_linear_capacity_not_global_context_or_science(self):
        self.assertEqual(len(PUBLIC_HISTORIES), 12)
        self.assertEqual(len(CONTEXTS), 36)
        for hops in (0, 2, 4):
            report = capacity(
                hops=hops, retained=tuple(range(CHANNELS)))
            self.assertEqual(len(report), 3)
            for value in report.values():
                self.assertGreaterEqual(value["distinct_local_histories"], 1)
                self.assertLessEqual(value["distinct_local_histories"], 12)
                self.assertGreaterEqual(value["local_feature_rank"], 1)
                self.assertLessEqual(value["local_feature_rank"], 12)
        self.assertEqual(rank([[1,0],[0,1]]),2)
        self.assertEqual(rank([[1,0],[2,0]]),1)
        for nonlinear in (False, True):
            sample = leave_one_out(nonlinear=nonlinear, hops=0)
            self.assertEqual(len(sample),36)
            self.assertTrue(all(
                r["same_head_training_count"]==11 and
                r["other_action_training_count_disallowed"]==24
                for r in sample))
        original = ResponsibilityGatedRingDev()
        raw = original.checkpoint()
        self.assertEqual(
            ResponsibilityGatedRingDev.restore(raw).checkpoint(), raw)


if __name__ == "__main__":
    unittest.main()
