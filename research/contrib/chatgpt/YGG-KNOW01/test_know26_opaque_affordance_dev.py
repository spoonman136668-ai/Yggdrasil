"""KNOW26: frozen opaque-affordance source and negative controls."""
import unittest
from know26_opaque_affordance_dev import (
    SCHEMA,PREREG,SOURCE,GROUPS,MAPS,FIT,HELD_SEEDS,RULES,ARMS,
    protocol,context,action,private_law,source_tuple,consequence,
    fit_rows,held_rows,FitState,action_scores,label_from_scores,
    conventional_label,held_forecast,high_true_prob,expected_brier,
    proof,digest
)

class KNOW26Tests(unittest.TestCase):
    def test_prereg_and_frozen_action_budget(self):
        p=protocol()
        self.assertEqual(p["schema"],"yggdrasil.know26.opaque-action-affordance-transfer-prereg.v1")
        self.assertEqual(PREREG,"116f42959cf4ccbf57713444785a4f5f45fd2b3f")
        self.assertEqual(p["fit"]["total_actions"],384)
        self.assertEqual(p["held"]["held_actions_per_arm"],1152)
        self.assertEqual(p["held"]["queries_per_arm"],96)
        self.assertEqual(set(GROUPS),set(FIT))
        self.assertEqual(len({seed for g in GROUPS for seed,ph in FIT[g]}),6)
        self.assertEqual(len({seed for g in GROUPS for seed in HELD_SEEDS[g]}),6)
        self.assertEqual(SOURCE,"engineering_fixture_only")
    def test_private_opaque_maps_and_one_witness(self):
        self.assertEqual({tuple(sorted(MAPS[g])) for g in GROUPS},{(0,1,2,4)})
        self.assertEqual(len({tuple(MAPS[g]) for g in GROUPS}),3)
        for g in GROUPS:
            for seed,phase in FIT[g]:
                records=fit_rows(g)
                self.assertEqual(len(records),128)
                self.assertTrue(all(y in (0,1) for ep,t,c,a,y in records))
                break
            for seed in HELD_SEEDS[g]:
                for ri in range(4):
                    rows=held_rows(g,seed,ri)
                    self.assertEqual(len(rows),48)
                    self.assertEqual(len({(c,a) for t,c,a,y in rows}),16)
                    self.assertEqual(rows[0][3],consequence(g,seed,"H"+str(ri),0,0))
        for t in range(48):
            self.assertEqual(context(t,48),t%4)
            self.assertEqual(action(t),(t//4)%4)
    def test_causal_negative_source_reject(self):
        with self.assertRaises(ValueError):
            source_tuple("G0",True,"FIT_A",0,0)
        with self.assertRaises(ValueError):
            source_tuple("G0",13101,"H0",0,0)
        with self.assertRaises(ValueError):
            source_tuple("G0",13401,"FIT_A",0,0)
        with self.assertRaises(ValueError):
            source_tuple("G0",13401,"H0",48,1)
        with self.assertRaises(ValueError):
            source_tuple("G0",13401,"H0",0,True)
        with self.assertRaises(ValueError):
            source_tuple("unknown",13401,"H0",0,0)
    def test_fit_cold_tamper_replay_and_functional_readout(self):
        rows=fit_rows("G0")
        model=FitState(rows)
        original=model.checkpoint()
        cold=FitState.restore(original,digest(original))
        self.assertEqual(original,cold.checkpoint())
        self.assertEqual([model.mean(ep,c,a) for ep in range(2) for c in range(4) for a in range(4)],
                         [cold.mean(ep,c,a) for ep in range(2) for c in range(4) for a in range(4)])
        with self.assertRaises(ValueError):
            FitState(rows,source_mode="owner_original")
        with self.assertRaises(ValueError):
            FitState(rows+[rows[0]])
        with self.assertRaises(ValueError):
            FitState.restore(original,"0"*64)
        edited=original.replace(b'"accepted_native":false',b'"accepted_native":true')
        with self.assertRaises(ValueError):
            FitState.restore(edited,digest(edited))
        duplicate=original.replace(b'"rows":',b'"rows":[],"rows":')
        with self.assertRaises(ValueError):
            FitState.restore(duplicate,digest(duplicate))
        modified=[list(z) for z in rows]
        modified[1][1]=0
        with self.assertRaises(ValueError):
            FitState(modified)
    def test_action_selection_reads_only_public_records(self):
        fit_state=FitState(fit_rows("G1"))
        label=label_from_scores(action_scores(fit_state.rows,"episode"))
        self.assertIn(label,(1,2,3))
        self.assertEqual(label,conventional_label(fit_state.rows))
        for method in ("episode","pooled","rolling"):
            self.assertEqual(len(action_scores(fit_state.rows,method)),3)
        h=held_rows("G1",13501,0)
        for c in range(4):
            self.assertTrue(0<held_forecast(h,label,c)<1)
        for q in (.15,.85):
            for p in (.15,.4,.5,.85):
                self.assertAlmostEqual(expected_brier(p,q),q*(1-q)+(p-q)**2)
    def test_full_frozen_result_and_no_promotion(self):
        r,s=proof(),proof()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["prereg_commit"],PREREG)
        self.assertEqual(r["fit_worlds"],6)
        self.assertEqual(r["fit_witnesses"],384)
        self.assertEqual(r["held_worlds"],24)
        self.assertEqual(r["held_witnesses_per_arm"],1152)
        self.assertEqual(r["held_evaluator_queries_per_arm"],96)
        self.assertEqual(set(r["per_arm_high_expected_brier"]),set(ARMS))
        self.assertEqual(r["per_arm_high_expected_brier"],s["per_arm_high_expected_brier"])
        self.assertEqual(r["frozen_hypotheses"],s["frozen_hypotheses"])
        self.assertTrue(r["frozen_hypotheses"]["H5_cold_FIT_functional_state"])
        self.assertTrue(r["frozen_hypotheses"]["H6_matched_conventional_parity"])
        self.assertEqual(r["engineering_gate"],"PASS")
        self.assertEqual(r["scientific_gate"],"SCIENCE_NO_GO_SYNTHETIC")
        self.assertFalse(r["native_modified"])
        self.assertFalse(r["original_first_use_426"])
        self.assertEqual(r["deployment"],"NONE")

if __name__=="__main__":
    unittest.main()
