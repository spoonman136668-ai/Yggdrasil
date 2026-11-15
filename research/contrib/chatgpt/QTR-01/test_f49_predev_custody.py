"""F49 no-target cold-retention and equal-budget ablation qualification."""
import unittest
import numpy as np

import f49_predev_custody as g
import f49_discrete_learners as d
import f49_conventional_controls as c


class F49PredevGuardTests(unittest.TestCase):
    def test_prereg_ablations_and_fixed_candidate_budget(self):
        self.assertEqual(g.ABLATIONS, ("no_retained_memory", "shuffled_public_outcomes", "random_proposals"))
        self.assertEqual(d.PROPOSALS_PER_EVENT, 1024)
        self.assertNotIn("target_ast", g.__dict__)

    def test_all_five_discrete_arms_retain_public_evidence(self):
        for kind in d.KINDS:
            with self.subTest(kind=kind):
                arm = d.PublicArm(kind, 256, 163)
                index, _ = arm.select()
                arm.observe(index, (0, 1))
                saved = g.cold_public(arm)
                clone = g.restore_public(saved)
                self.assertEqual(g.cold_public(clone), saved)
                self.assertEqual(clone.used, arm.used)
                self.assertEqual(clone.observed_bits, 2)
                self.assertEqual(clone.engine.probability((13, 29, 1)),
                                 arm.engine.probability((13, 29, 1)))
                self.assertEqual(clone.select(), arm.select())
                tampered = saved[:-1] + bytes((saved[-1] ^ 1,))
                with self.assertRaises(d.ControlRejected):
                    g.restore_public(tampered)

    def test_both_conventional_arms_restore_weights_and_optimizer_moments(self):
        for kind in ("conventional_mlp", "conventional_logistic"):
            with self.subTest(kind=kind):
                model = c.MLP(seed=11) if kind == "conventional_mlp" else c.Logistic()
                # A small synthetic API fixture; not a substitute for the
                # six full source fits already qualified at the pinned SHA.
                pretrained = c.Pretrained(kind, 256, model, 32768, 0.1, {"fixture_only": True})
                arm = c.ConventionalArm(pretrained, 163)
                index, _ = arm.select()
                arm.observe(index, (0, 1))
                saved = g.cold_conventional(arm, pretrained)
                source_sha = g._source_fingerprint(pretrained)
                clone = g.restore_conventional(saved, pretrained)
                self.assertEqual(g.cold_conventional(clone, pretrained), saved)
                self.assertEqual(clone.used, arm.used)
                self.assertEqual(clone.observed_bits, 2)
                self.assertEqual(clone.model.steps, arm.model.steps)
                self.assertEqual(source_sha, g._source_fingerprint(pretrained))
                query = c.pair_features((3, 17, 2))
                self.assertTrue(np.array_equal(clone.model.probabilities(query),
                                               arm.model.probabilities(query)))
                tampered = saved[:-1] + bytes((saved[-1] ^ 1,))
                with self.assertRaises(d.ControlRejected):
                    g.restore_conventional(tampered, pretrained)
                wrong = c.Pretrained(kind, 256,
                        c.MLP(seed=13) if kind == "conventional_mlp" else c.Logistic(),
                        32768, 0.1, {"fixture_only": True})
                if kind == "conventional_logistic":
                    wrong.model.w[0] = 1.0
                with self.assertRaises(d.ControlRejected):
                    g.restore_conventional(saved, wrong)

    def test_all_ablations_have_equal_observation_and_proposal_accounting(self):
        for mode in g.ABLATIONS:
            with self.subTest(mode=mode):
                ab = g.NativeAblation(mode, 256, 163)
                index, _ = ab.select()
                ab.observe(index, (0, 1))
                self.assertEqual(ab.observed_bits, 2)
                self.assertEqual(ab.charged_proposals, 1024)
                self.assertEqual(ab.arm.observed_bits, 2)
                if mode == "no_retained_memory":
                    self.assertEqual(ab.arm.engine.history, [])
                elif mode == "shuffled_public_outcomes":
                    self.assertEqual(ab.arm.engine.history[0][1], (1, 0))
                else:
                    self.assertTrue(ab.arm.engine.random_proposals)
                    self.assertEqual(ab.arm.engine.proposals, 1024)

    def test_random_proposal_ablation_actually_removes_evidence_steering(self):
        a = d.GrammarLearner(256, random_proposals=False)
        b = d.GrammarLearner(256, random_proposals=True)
        tr = (11, 23, 2)
        a.observe(tr, (0, 1))
        b.observe(tr, (0, 1))
        self.assertEqual(a.proposals, b.proposals)
        self.assertTrue(any(a._proposal(1, i) != b._proposal(1, i)
                            for i in range(1, 64)))
        for outcomes in ((True, 1), (0, 3)):
            with self.assertRaises(d.ControlRejected):
                a.observe(tr, outcomes)

    def test_malformed_and_pending_checkpoints_fail_closed(self):
        with self.assertRaises(d.ControlRejected):
            g.NativeAblation("unexpected", 256, 163)
        arm = d.PublicArm("native", 256, 163)
        arm.select()
        with self.assertRaises(d.ControlRejected):
            g.cold_public(arm)
        for bad in (b"", b"F49P1{}", b"F49P1{}." + b"0" * 64):
            with self.assertRaises(d.ControlRejected):
                g.restore_public(bad)


if __name__ == "__main__":
    unittest.main()
