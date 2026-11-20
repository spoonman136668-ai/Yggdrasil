"""TGAP26: frozen synthetic boundaries; no protected first use."""
import math
import unittest
from tgap26_learned_probe_dev import (
    FIT, PAIRS, POLICIES, PROTOCOL_BLOB, MODE, SCHEMA,
    consequence, coin, fit, model_for, run_world, choose,
    information_gain, proof, protocol,
)
from know25_x2_probe_dev import TruthPosterior, digest

class TGAP26Tests(unittest.TestCase):
    def test_frozen_protocol_and_disjoint_worlds(self):
        p=protocol()
        self.assertEqual(PROTOCOL_BLOB,"78fd9d3de9e63846f7b823c406b7ae23ab365dba")
        self.assertEqual(p["public_source"]["held_worlds"],24)
        self.assertEqual(MODE,"engineering_fixture_only")
        f={seed for seed,_ in FIT}
        held=[s for _,_,seeds in PAIRS for s in seeds]
        self.assertEqual(len(held),12)
        self.assertEqual(len(set(held)),12)
        self.assertTrue(f.isdisjoint(held))
    def test_exogenous_twin_identifiability_negative(self):
        for low,high,seeds in PAIRS:
            for seed in seeds:
                for t in range(24):
                    self.assertEqual(coin(seed,t),coin(seed,t))
                    for a in (0,1,2):
                        self.assertEqual(consequence(seed,low,t,a),
                                         consequence(seed,high,t,a))
        with self.assertRaises(ValueError):
            consequence(12311,"x0",0,9)
        with self.assertRaises(ValueError):
            consequence(12311,"x0",24,0)
    def test_fit_is_low_only_and_cold_readonly(self):
        data=fit()
        self.assertEqual(data["fit_actions"],72)
        self.assertTrue(all(abs(p-.25)<1e-12 for p in data["trained_prior"][4:]))
        self.assertEqual(sum(x[1] for x in data["beta"]),72)
        rawhash=list(data["fit_cold_hashes"])
        z=run_world("trained_active",PAIRS[0][2][0],PAIRS[0][0],data)
        self.assertEqual(len(z["trace"]),24)
        self.assertEqual(rawhash,data["fit_cold_hashes"])
        self.assertNotIn("private_law",model_for("trained_active",data).__dict__)
    def test_replay_and_source_mode_fail_closed(self):
        p=TruthPosterior([.25]*8)
        p.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            p.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            p.observe(1,1,3,1,mode="owner_original")
        raw=p.checkpoint()
        with self.assertRaises(ValueError):
            TruthPosterior.restore(raw,"0"*64)
        self.assertEqual(choose(p,1,(0,1,2)) in (0,1,2),True)
        self.assertTrue(all(math.isfinite(information_gain(p,1,a))
                            for a in range(4)))
    def test_predeclared_full_source_only_verdict(self):
        r=proof()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["fit_actions"],72)
        self.assertEqual(r["held_actions_per_policy"],576)
        self.assertEqual(r["high_queries_per_policy"],96)
        self.assertEqual(set(r["metrics"]),set(POLICIES))
        self.assertTrue(all(m["held_observations"]==576 and
                            m["high_score_queries"]==96 and
                            sum(m["action_counts"])==576
                            for m in r["metrics"].values()))
        self.assertTrue(r["hypotheses"]["H1_no_x2_identifiability_negative"])
        self.assertFalse(r["accepted_native_modified"])
        self.assertFalse(r["first_use_426"])
        self.assertEqual(r["science_gate"],"SCIENTIFIC_NO_GO_SYNTHETIC")
        self.assertEqual(r["deployment"],"NONE")

if __name__=="__main__":
    unittest.main()
