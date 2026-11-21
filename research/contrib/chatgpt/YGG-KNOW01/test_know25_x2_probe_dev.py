"""Frozen KNOW25 x2-flip identification tests; synthetic-source only."""
import json
import unittest
from know25_x2_probe_dev import (
    SCHEMA,PROTO_SCHEMA,PREREG,MODE,FIT,PAIRS,FAMILIES,POLICIES,
    canonical,digest,context,effective,coin,prob_law,witnessed,
    TruthPosterior,ContextBeta,Passive,fit,model_for,run_world,
    protocol,proof,score
)

class KNOW25Tests(unittest.TestCase):
    def test_frozen_worlds_actions_and_source(self):
        d=protocol()
        self.assertEqual(d["schema"],PROTO_SCHEMA)
        self.assertEqual(PREREG,"219e59cdff6c26383fa4fb5277cad459f9caf0cf")
        self.assertEqual(len(PAIRS),3)
        self.assertEqual(len({seed for a,b,seeds in PAIRS for seed in seeds}),9)
        self.assertEqual({x[0] for x in FIT},{12021,12029,12047})
        self.assertEqual(MODE,"engineering_fixture_only")
        self.assertEqual(effective(0,3),4)
        self.assertEqual(effective(3,3),7)
        for c in range(4):
            for a in range(3):
                self.assertLess(effective(c,a),4)
                self.assertGreaterEqual(effective(c,3),4)
    def test_paired_worlds_indistinguishable_without_x2(self):
        for a,b,seeds in PAIRS:
            for c in range(4):
                for action in range(3):
                    self.assertEqual(prob_law(a,c,action),prob_law(b,c,action))
                self.assertAlmostEqual(prob_law(a,c,3)+prob_law(b,c,3),1)
            for seed in seeds:
                for t in range(48):
                    c=context(t)
                    for action in range(3):
                        self.assertEqual(witnessed(seed,a,t,c,action),
                                         witnessed(seed,b,t,c,action))
    def test_exact_paired_loss_floor_and_positive_high_probe(self):
        for q in (.15,.35,.5,.85):
            self.assertAlmostEqual((score(q,.85)+score(q,.15))/2,
                                    .25+(q-.5)**2)
        d=fit()
        self.assertEqual(d["fit_witnesses"],72)
        self.assertTrue(all(abs(x-.25)<1e-12
                            for x in d["fit_x2_coefficients"]))
        a,b,seeds=PAIRS[0]
        original=run_world("trained_anf_no_x2",(seeds[0],a),0,d)
        counterpart=run_world("trained_anf_no_x2",(seeds[0],b),0,d)
        self.assertEqual(original["trace"],counterpart["trace"])
        self.assertEqual(original["high"],counterpart["high"])
        probe=run_world("trained_anf_fixed_x2",(seeds[0],a),0,d)
        self.assertEqual(probe["choices"][3],16)
        self.assertEqual(sum(probe["choices"]),48)
    def test_source_typing_and_replay(self):
        z=TruthPosterior([.25]*8)
        t=0;c=context(t)
        with self.assertRaises(ValueError):
            z.observe(t,c,3,1,mode="owner_original")
        with self.assertRaises(ValueError):
            z.observe(t,c,3,2)
        with self.assertRaises(ValueError):
            z.observe(t,c,True,1)
        z.observe(t,c,3,1)
        with self.assertRaises(ValueError):
            z.observe(t,c,3,1)
        for bad in ((99999,"x0"),(PAIRS[0][2][0],"x1"),
                    (True,PAIRS[0][0])):
            with self.assertRaises(ValueError):
                run_world("trained_anf_fixed_x2",bad,0,fit())
    def test_cold_round_trip_and_tamper(self):
        z=TruthPosterior([.25]*8)
        for t in range(12):
            z.observe(t,context(t),3,int(t%3==0))
        raw=z.checkpoint()
        self.assertEqual(TruthPosterior.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaises(ValueError):
            TruthPosterior.restore(raw,"0"*64)
        tampered=raw.replace(b'"accepted_native":false',b'"accepted_native":true')
        with self.assertRaises(ValueError):
            TruthPosterior.restore(tampered,digest(tampered))
        duplicate=raw.replace(b'"prior":',b'"prior":[],"prior":')
        with self.assertRaises(ValueError):
            TruthPosterior.restore(duplicate,digest(duplicate))
    def test_frozen_complete_receipt(self):
        r=proof()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["prereg_commit"],PREREG)
        self.assertEqual(r["fit_witnesses"],72)
        self.assertEqual(r["held_worlds"],18)
        self.assertEqual(r["held_witnesses_per_policy"],864)
        self.assertEqual(r["high_eval_queries_per_policy"],216)
        self.assertEqual(r["low_eval_queries_per_policy"],216)
        self.assertEqual(set(r["metrics"]),set(POLICIES))
        self.assertTrue(r["frozen_hypotheses"]["H1_no_x2_pairs_identical_and_floor"])
        self.assertEqual(r["science_gate"],"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE")
        self.assertEqual(r["engineering_gate"],"PASS")
        self.assertFalse(r["accepted_native_modified"])
        self.assertFalse(r["first_use_426"])
        self.assertEqual(r["deployment"],"NONE")
        for name,v in r["metrics"].items():
            self.assertEqual(sum(v["action_counts"]),864)
            self.assertLessEqual(v["high_expected_brier"],1.0)
            if name.endswith("fixed_x2") or name in ("uninformed_p05",):
                self.assertEqual(v["action_counts"][3],18*16)
        print("YGG_KNOW25_FROZEN_RECEIPT="+json.dumps({
             "brier":{k:v["high_expected_brier"] for k,v in r["metrics"].items()},
             "hypotheses":r["frozen_hypotheses"],
             "margins":r["frozen_margins"],
             "verdict":r["development_verdict"],
             "science":r["science_gate"]
             },sort_keys=True))

if __name__=="__main__":
    unittest.main()
