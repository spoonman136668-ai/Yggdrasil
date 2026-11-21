"""TGAP25 bounded structural intervention learning: frozen source controls."""
import json
import unittest
from tgap25_structural_action_dev import (
    PREREG, SCHEMA, MODE, FIT, HELD, ARMS, GROUPS, Posterior,
    Archive, ContextualBeta, fixed_action, public, consequence, truth,
    affine_law, fit, evaluate_world, proof, canonical, sha,
)


class Tgap25Tests(unittest.TestCase):
    def test_frozen_causal_rule_split_and_action_budget(self):
        self.assertEqual(FIT,((11101,"x0"),(11107,"x1")))
        self.assertEqual(len(HELD),12)
        self.assertEqual(len(set(s for s,_ in HELD)),12)
        self.assertTrue({s for s,_ in HELD}.isdisjoint(
            {s for s,_ in FIT}))
        self.assertEqual({x[1] for x in HELD},set(GROUPS))
        self.assertEqual(len({(public(t),fixed_action(t))
                              for t in range(16)}),16)
        for law in ("x0","x1","parity3"):
            pattern=tuple(truth(law,c) for c in range(8))
            self.assertTrue(any(
                tuple(affine_law(i,c) for c in range(8)) == pattern
                for i in range(16)))
        majority=tuple(truth("majority3",c) for c in range(8))
        self.assertFalse(any(
            tuple(affine_law(i,c) for c in range(8))==majority
            for i in range(16)))

    def test_one_factual_witness_per_chosen_action(self):
        for seed,law in HELD:
            for step in range(64):
                for action in (0,1):
                    result=consequence(seed,law,step,action)
                    self.assertIn(result,(0,1))
                    self.assertEqual(result,consequence(seed,law,step,action))

    def test_fitted_archive_is_not_private_law_lookup(self):
        d=fit()
        self.assertEqual(d["source_fit_actions"],128)
        self.assertEqual([p.seen for p in d["archive"].archives],[64,64])
        self.assertTrue(all(p.size==16 for p in d["archive"].archives))
        self.assertNotIn("x0",d["archive"].__dict__)
        raw=d["archive"].checkpoint()
        cold=Archive.restore(raw,sha(raw))
        self.assertEqual(raw,cold.checkpoint())
        self.assertEqual(cold.archived_sha(),d["old_archive"])
        self.assertNotIn("majority3",raw.decode("ascii"))

    def test_cold_replay_forged_source_tamper_duplicate_fail(self):
        p=Archive([Posterior(16),Posterior(16)])
        p.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            p.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            p.observe(2,2,0,1)
        with self.assertRaises(ValueError):
            p.observe(1,1,1,1,mode="claimed_real")
        raw=p.checkpoint()
        self.assertEqual(Archive.restore(raw,sha(raw)).checkpoint(),raw)
        with self.assertRaises(ValueError):
            Archive.restore(raw+b" ",sha(raw+b" "))
        with self.assertRaises(ValueError):
            Archive.restore(raw,"0"*64)
        bad=raw.replace(b'"accepted_native":false',b'"accepted_native":true')
        with self.assertRaises(ValueError):
            Archive.restore(bad,sha(bad))
        duplicate=raw.replace(b'"mode":',b'"mode":"x","mode":')
        with self.assertRaises(ValueError):
            Archive.restore(duplicate,sha(duplicate))

    def test_contextual_controls_fully_fit_same_information(self):
        d=fit()
        self.assertEqual(d["contextual"].seen,128)
        self.assertEqual(d["rolling"].seen,128)
        self.assertEqual(d["plain"].seen,128)
        self.assertEqual(sum(len(d["contextual"].rows[c][a])
                             for c in range(8) for a in (0,1)),128)
        w=evaluate_world(d,HELD[0])
        self.assertEqual(w["actions_per_policy"],64)
        self.assertEqual(w["scored_per_policy"],48)
        self.assertEqual(set(w["regret_sum"]),set(ARMS))
        self.assertTrue(w["archive_unchanged"])

    def test_frozen_result_and_explicit_science_no_go(self):
        r=proof()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["prereg_commit"],PREREG)
        self.assertEqual(r["mode"],MODE)
        self.assertEqual(r["fit_actions_per_policy"],128)
        self.assertEqual(r["held_actions_per_policy"],768)
        self.assertEqual(r["held_warmup_per_policy"],192)
        self.assertEqual(r["held_scored_per_policy"],576)
        self.assertEqual(len(r["frozen_hypotheses"]),5)
        self.assertEqual(set(r["mean_expected_regret"]),set(ARMS))
        self.assertEqual(r["mean_expected_regret"]["privileged_oracle"],0)
        self.assertEqual(r["engineering_gate"],"PASS")
        self.assertEqual(r["science_gate"],"SCIENCE_NO_GO_SYNTHETIC")
        self.assertFalse(r["native_model_changed"])
        self.assertFalse(r["protected_first_use"])
        self.assertEqual(r["deploy"],"NONE")
        self.assertTrue(r["archive_A_B_retention_by_construction"])
        print("YGG_TGAP25_FROZEN_RECEIPT="+json.dumps({
            "expected_regret":r["mean_expected_regret"],
            "family_regret":r["regret_by_hidden_family_scoring_only"],
            "hypotheses":r["frozen_hypotheses"],
            "verdict":r["development_verdict"],
        },sort_keys=True))


if __name__ == "__main__":
    unittest.main()
