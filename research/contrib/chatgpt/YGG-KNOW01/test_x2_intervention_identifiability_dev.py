"""KNOW25 frozen causal probe, paired-law source custody, strong controls."""
import json
import unittest

from x2_intervention_identifiability_dev import (
    SCHEMA,PROTO,PREREG,PAIRINGS,POLICIES,STEPS,
    frozen_protocol,effective4,private_coin,witnessed,q_true,
    ProbePosterior,PublicTargetBeta,SourceOnly,model_for,
    strategy_for,one_world,proof,canonical,digest,
)
from anf_causal_identifiability_dev import (
    fitted_prior,source_context,MODE,
)


class KNOW25Tests(unittest.TestCase):
    def test_frozen_protocol_and_fresh_worlds(self):
        p=frozen_protocol()
        self.assertEqual(p["schema"],PROTO)
        self.assertEqual(PREREG,
           "9155e5d62d6d5a0eb4f79fef22953e9e5e4f25da")
        self.assertEqual(len(PAIRINGS),3)
        self.assertEqual(STEPS,24)
        self.assertEqual(p["scoring"]["held_witnesses_per_policy"],432)
        self.assertEqual(p["scoring"]["high_expected_evaluator_queries_per_policy"],216)
        fresh={seed for a,b,seeds in PAIRINGS for seed in seeds}
        self.assertEqual(len(fresh),9)
        self.assertTrue(fresh.isdisjoint({
            11021,11029,11047,11311,11317,11321,11411,11417,11421,
            11511,11519,11527,10201,10301,10401,10501
        }))
        self.assertEqual(set(POLICIES),set(p["arms"])-{"truth_oracle"})

    def test_x2_probe_new_action_and_complementary_pair_law(self):
        for c in range(4):
            for a in (0,1,2):
                self.assertLess(effective4(c,a),4)
            self.assertEqual(effective4(c,3),c+4)
        for base,variant,seeds in PAIRINGS:
            for c in range(4):
                for a in (0,1,2):
                    self.assertEqual(q_true(base,c,a),q_true(variant,c,a))
                self.assertAlmostEqual(q_true(base,c,3)+
                                       q_true(variant,c,3),1.0)
            for seed in seeds:
                for t in range(STEPS):
                    c=source_context(t)
                    for action in (0,1,2):
                        self.assertEqual(witnessed(seed,base,t,c,action),
                                         witnessed(seed,variant,t,c,action))
        with self.assertRaises(ValueError):
            effective4(0,4)
        with self.assertRaises(ValueError):
            private_coin(11311,24)
        with self.assertRaises(ValueError):
            witnessed(11311,"xor01",0,0,3)

    def test_witness_changes_learned_posterior_without_oracle(self):
        prior=[.25]*8
        lo=ProbePosterior(prior)
        hi=ProbePosterior(prior)
        target=effective4(0,3)
        self.assertEqual(target,4)
        lo.observe(0,0,3,0)
        hi.observe(0,0,3,1)
        self.assertLess(lo.prob(0,3),hi.prob(0,3))
        self.assertEqual(len(lo.events),1)
        self.assertEqual(len(hi.events),1)
        with self.assertRaisesRegex(ValueError,"OBSERVED_WITNESS"):
            hi.observe(0,0,3,1)
        with self.assertRaisesRegex(ValueError,"OBSERVED_WITNESS"):
            hi.observe(1,1,0,1,source_mode="original_world")
        with self.assertRaisesRegex(ValueError,"OBSERVED_WITNESS"):
            lo.observe(1,1,0,True)
        with self.assertRaisesRegex(ValueError,"CHOOSE"):
            hi.choose(True,"active")
        with self.assertRaisesRegex(ValueError,"ACTION"):
            hi.prob(0,True)
        self.assertNotIn("hidden_law",hi.__dict__)
        self.assertNotIn("private_coin",hi.__dict__)

    def test_exact_restore_rejects_tamper_duplicate_and_wrong_source(self):
        z=ProbePosterior([.25]*8)
        for t in range(STEPS):
            c=source_context(t)
            a=t%4
            z.observe(t,c,a,int(t%3==0))
        raw=z.checkpoint()
        restored=ProbePosterior.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        for c in range(8):
            for a in range(4):
                self.assertEqual(restored.prob(c,a),z.prob(c,a))
        with self.assertRaises(ValueError):
            ProbePosterior.restore(raw,"0"*64)
        bad=raw.replace(b'"accepted_native":false',
                        b'"accepted_native":true')
        with self.assertRaises(ValueError):
            ProbePosterior.restore(bad,digest(bad))
        dup=raw.replace(b'"mode":',b'"mode":"owner","mode":')
        with self.assertRaises(ValueError):
            ProbePosterior.restore(dup,digest(dup))
        tamper=json.loads(raw)
        tamper["events"][0][2]=8
        edited=canonical(tamper)
        with self.assertRaises(ValueError):
            ProbePosterior.restore(edited,digest(edited))

    def test_controls_equal_budget_and_negative_pair_equivalence(self):
        prior,fit=fitted_prior()
        self.assertEqual(len(fit),3)
        self.assertTrue(all(len(x.events)==24 for x in fit))
        for i,(base,variant,seeds) in enumerate(PAIRINGS):
            seed=seeds[0]
            for name in POLICIES:
                x=one_world(name,seed,base,i*3,prior)
                z=one_world(name,seed,variant,i*3,prior)
                self.assertEqual(x["witnesses"],STEPS)
                self.assertEqual(z["witnesses"],STEPS)
                self.assertEqual(sum(x["action_counts"]),STEPS)
                self.assertEqual(sum(z["action_counts"]),STEPS)
                self.assertEqual(len(x["forecasts_high"]),12)
                if name in ("learned_anf_no_x2",
                            "learned_anf_passive","source_only"):
                    self.assertEqual(x["action_counts"][3],0)
                    self.assertEqual(x["transcript"],z["transcript"])
                    self.assertEqual(x["forecasts_high"],
                                     z["forecasts_high"])
        with self.assertRaisesRegex(ValueError,"HELD_WORLD"):
            one_world("learned_anf_active_x2",11311,"xor01",0,prior)

    def test_frozen_proof_deterministic_and_unqualified_native(self):
        a=proof()
        b=proof()
        self.assertEqual(a["schema"],SCHEMA)
        self.assertEqual(a["prereg_commit"],PREREG)
        self.assertEqual(a["fit_witnesses"],72)
        self.assertEqual(a["held_worlds"],18)
        self.assertEqual(a["held_witnesses_per_policy"],432)
        self.assertEqual(a["high_expected_queries_per_policy"],216)
        self.assertEqual(a["low_expected_queries_per_policy"],216)
        self.assertEqual(a["held_policy_results"],b["held_policy_results"])
        self.assertEqual(a["frozen_hypotheses"],b["frozen_hypotheses"])
        self.assertEqual(set(a["held_policy_results"]),set(POLICIES))
        self.assertTrue(a["frozen_hypotheses"]["H1_no_x2_pair_identity"])
        self.assertTrue(a["frozen_hypotheses"]["H2_no_x2_pair_bound"])
        self.assertGreaterEqual(a["no_x2_min_pair_expected_brier"],.25-1e-8)
        self.assertEqual(a["engineering_gate"],"PASS")
        self.assertEqual(a["scientific_gate"],
                         "SCIENCE_NO_GO_SYNTHETIC_NOT_ORIGINAL_NATIVE")
        self.assertFalse(a["accepted_native_modified"])
        self.assertFalse(a["protected_original_first_use"])
        self.assertFalse(a["canonical_checkpoint_changed"])
        self.assertEqual(a["deployment"],"NONE")
        self.assertIn(a["development_verdict"],(
            "DEVELOPMENT_X2_IDENTIFICATION_SUPPORTED",
            "DEVELOPMENT_MIXED","DEVELOPMENT_NO_GO"))
        self.assertEqual(a["held_policy_results"]["source_only"]
                         ["high_expected_brier"],.25)
        for values in a["held_policy_results"].values():
            self.assertEqual(sum(values["actions"]),432)
            self.assertTrue(0<=values["worlds_with_x2_probe"]<=18)


if __name__=="__main__":
    unittest.main()
