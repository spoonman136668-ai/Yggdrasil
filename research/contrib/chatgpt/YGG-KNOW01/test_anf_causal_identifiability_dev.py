"""KNOW24 frozen native-free causal identifiability, source and controls."""
import math
import unittest

from anf_causal_identifiability_dev import (
    SCHEMA,PROTOCOL,PREREG,MODE,FIT,PAIRS,POLICIES,
    ANF,HYPOTHESES,OP_TABLE,KNOWN_PAIR_TABLES,
    source_protocol,hidden_bit,op_table,source_context,effective,
    private_coin,consequence,probability,coeffs,expected_brier,
    TruthPosterior,ContextBeta,Constant,fitted_prior,
    make_policy,run_world,prove,canonical,digest,
)


class Know24Tests(unittest.TestCase):
    def test_prereg_and_fresh_causal_pair_worlds(self):
        p=source_protocol()
        self.assertEqual(p["schema"],PROTOCOL)
        self.assertEqual(PREREG,"1454d7b58875f5a50429e33979b0edfa5a1c7e88")
        self.assertEqual(FIT,((11021,"x0",24),(11029,"x1",24),
                              (11047,"xor01",24)))
        self.assertEqual(len(PAIRS),3)
        self.assertEqual(sum(len(z) for a,b,z in PAIRS)*2,18)
        self.assertEqual(p["budget"]["held_witnesses_per_policy"],288)
        self.assertEqual(p["budget"]["held_high_eval_queries_per_policy"],216)
        old={10201,10207,10211,10301,10303,10313,
             10401,10409,10427,10501,10513,10529}
        new={seed for a,b,seeds in PAIRS for seed in seeds}
        self.assertTrue(new.isdisjoint(old))
        self.assertTrue(new.isdisjoint({z[0] for z in FIT}))
        self.assertEqual(len(new),9)

    def test_all_256_hypotheses_have_unique_exact_anf(self):
        self.assertEqual(len(ANF),256)
        self.assertEqual(len(set(ANF)),256)
        for h in HYPOTHESES:
            self.assertEqual(ANF[h],coeffs(h))
            for context in range(8):
                bit=0
                for mask,coefficient in enumerate(ANF[h]):
                    if mask & context == mask and coefficient:
                        bit^=1
                self.assertEqual(bit,(h>>context)&1)
        self.assertEqual(len(KNOWN_PAIR_TABLES),6)

    def test_perfect_low_equivalence_and_high_complement(self):
        for a,b,seeds in PAIRS:
            for c in range(4):
                for action in range(3):
                    self.assertEqual(probability(a,c,action),
                                     probability(b,c,action))
                    self.assertLess(effective(c,action),4)
            for c in range(4,8):
                for action in range(3):
                    self.assertEqual(probability(a,c,action)+
                                     probability(b,c,action),1)
                    self.assertGreaterEqual(effective(c,action),4)
            for seed in seeds:
                for t in range(16):
                    for action in (0,1,2):
                        c=source_context(t)
                        self.assertEqual(
                            consequence(seed,a,t,c,action),
                            consequence(seed,b,t,c,action))
        for p in (.05,.25,.5,.85,.95):
            self.assertAlmostEqual(
                (expected_brier(p,.85)+expected_brier(p,.15))/2,
                .25+(p-.5)**2,places=12)

    def test_learning_is_only_from_one_witness_and_strict_source(self):
        z=TruthPosterior([.25]*8)
        c=source_context(0)
        a=0
        z0=TruthPosterior([.25]*8)
        z1=TruthPosterior([.25]*8)
        z0.observe(0,c,a,0)
        z1.observe(0,c,a,1)
        self.assertLess(z0.prob(c,a),z1.prob(c,a))
        self.assertEqual(len(z0.events),1)
        with self.assertRaisesRegex(ValueError,"WITNESS_OR_REPLAY"):
            z0.observe(0,c,a,0)
        with self.assertRaisesRegex(ValueError,"WITNESS_OR_REPLAY"):
            z0.observe(1,source_context(1),a,1,source_mode="owner_accepted")
        with self.assertRaises(ValueError):
            z.observe(0,0,3,1)
        for invalid in (-1,True,2):
            with self.assertRaises(ValueError):
                z.observe(0,0,0,invalid)
        self.assertNotIn("private_role",z.__dict__)
        self.assertEqual(MODE,"engineering_fixture_only")

    def test_cold_immutability_and_rejects_tampering(self):
        z=TruthPosterior([.25]*8)
        for t in range(16):
            c=source_context(t)
            z.observe(t,c,0,int(t%3==0))
        raw=z.checkpoint()
        cold=TruthPosterior.restore(raw,digest(raw))
        self.assertEqual(raw,cold.checkpoint())
        for c in range(8):
            for a in range(3):
                self.assertEqual(z.prob(c,a),cold.prob(c,a))
        with self.assertRaises(ValueError):
            TruthPosterior.restore(raw,"0"*64)
        edited=raw.replace(b'"accepted_native":false',
                           b'"accepted_native":true')
        with self.assertRaises(ValueError):
            TruthPosterior.restore(edited,digest(edited))
        duplicate=raw.replace(b'"mode":',b'"mode":"owner","mode":')
        with self.assertRaises(ValueError):
            TruthPosterior.restore(duplicate,digest(duplicate))
        self.assertLess(len(raw),8192)

    def test_fit_learns_structural_prior_from_only_three_worlds(self):
        prior,fit=fitted_prior()
        self.assertEqual(len(prior),8)
        self.assertEqual(len(fit),3)
        self.assertTrue(all(.08<=p<=.92 for p in prior))
        self.assertTrue(all(len(m.events)==24 for m in fit))
        for f in fit:
            raw=f.checkpoint()
            self.assertEqual(
                TruthPosterior.restore(raw,digest(raw)).checkpoint(),raw)
        for i,m in enumerate(fit):
            self.assertEqual(m.checkpoint(),fit[i].checkpoint())

    def test_policy_budgets_and_traces_exact_on_pairs(self):
        prior,fit=fitted_prior()
        for i,(a,b,seeds) in enumerate(PAIRS):
            seed=seeds[0]
            for name in POLICIES:
                x=run_world(name,seed,a,i*3,prior)
                y=run_world(name,seed,b,i*3,prior)
                self.assertEqual(x["trace"],y["trace"])
                self.assertEqual(x["high"],y["high"])
                self.assertEqual(x["witnesses"],16)
                self.assertEqual(sum(x["counts"]),16)
                self.assertGreaterEqual(
                    (x["high_sum"]+y["high_sum"])/24,
                    .25-1e-10)
        self.assertEqual(make_policy("source_only",prior).prob(0,0),.5)

    def test_frozen_trial_complete_and_no_owner_promotion(self):
        a,b=prove(),prove()
        self.assertEqual(a["schema"],SCHEMA)
        self.assertEqual(a["prereg_commit"],PREREG)
        self.assertEqual(a["fit_witnesses"],72)
        self.assertEqual(a["held_worlds"],18)
        self.assertEqual(a["held_witnesses_per_policy"],288)
        self.assertEqual(a["high_expected_queries_per_policy"],216)
        self.assertEqual(a["low_expected_queries_per_policy"],216)
        self.assertEqual(a["held_policy_metrics"],b["held_policy_metrics"])
        self.assertEqual(a["frozen_predicates"],b["frozen_predicates"])
        self.assertEqual(set(a["held_policy_metrics"]),set(POLICIES))
        self.assertEqual(a["engineering_gate"],"PASS")
        self.assertTrue(a["frozen_predicates"]["H1_pairs_identical"])
        self.assertTrue(a["frozen_predicates"]["H2_paired_lower_bound"])
        self.assertEqual(a["scientific_gate"],
             "SCIENCE_NO_GO_SYNTHETIC_EXACT_CAUSAL_NONIDENTIFIABILITY")
        self.assertFalse(a["native_modified"])
        self.assertFalse(a["accepted_checkpoint_changed"])
        self.assertFalse(a["protected_original_first_use"])
        self.assertEqual(a["deployment"],"NONE")
        for name,metrics in a["held_policy_metrics"].items():
            self.assertGreaterEqual(metrics["high_expected_brier"],.25-1e-8)
            self.assertEqual(sum(metrics["action_counts"]),288)
            self.assertLessEqual(metrics["high_expected_brier"],1)
            self.assertEqual(len(a["per_pair"][name]),3)
        self.assertAlmostEqual(a["held_policy_metrics"]["source_only"]
                               ["high_expected_brier"],.25)
        self.assertAlmostEqual(a["held_policy_metrics"]["source_only"]
                               ["low_expected_brier"],.25)


if __name__=="__main__":
    unittest.main()
