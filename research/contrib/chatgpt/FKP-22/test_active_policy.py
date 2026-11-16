"""FKP-22 source-safe support-world tests; NO evaluation worlds are opened.

Frozen 16 SUPPORT worlds (994000..994015) are available for engineering.
The first known-family and prior-shift TRAIN outcomes must only be opened in
the qualified one-shot primary evaluator, AFTER both OS regressions succeed.
"""
from collections import Counter
from pathlib import Path
import json
import unittest

import active_policy as policy
import public_active_source as source
import run_active_eval as evaluate


SUPPORT_SIGNATURES=tuple((0,3,12,15)*4)


class PublicActiveInterventionTests(unittest.TestCase):
    def test_exact_disjoint_source_roles_and_held_denials(self):
        self.assertEqual(source.SUPPORT,tuple(range(994000,994016)))
        self.assertEqual(source.KNOWN,tuple(range(994100,994116)))
        self.assertEqual(source.SHIFT,tuple(range(994200,994208)))
        self.assertFalse(set(source.SUPPORT)&set(source.KNOWN))
        self.assertFalse(set(source.SHIFT)&set(source.KNOWN))
        self.assertEqual(len(source.TRAIN),12)
        self.assertEqual(source.PROBES,(0,1,2,7))
        self.assertEqual(set(source.TRAIN)&set(source.PROBES),set())
        for seed in (994500,994531,994600,994663,993500,
                     992500,991500,978500,976500,994208,
                     -1,True,994000.0):
            with self.subTest(seed=seed),self.assertRaises(PermissionError):
                source.PublicChosenSession(seed,0)

    def test_only_physical_fourth_action_reveals_outcome(self):
        s=source.PublicChosenSession(source.SUPPORT[0],0)
        for bad in (-1,2,True,1.0):
            with self.assertRaises(ValueError):
                s.apply(bad)
        rows=[]
        for phase,action in enumerate((1,0,1,0)):
            before=s.public_state
            row=s.apply(action)
            self.assertEqual(row.before,before)
            self.assertEqual(row.action,action)
            self.assertEqual(len(row.history),phase)
            self.assertEqual(row.after[1],phase+1)
            if phase<3:
                self.assertEqual(row.reward,0.0)
                self.assertFalse(row.done)
            else:
                self.assertTrue(row.done)
                self.assertIn(row.reward,(-1.0,1.0))
            rows.append(row)
        self.assertTrue(s.done)
        with self.assertRaises(ValueError):
            s.apply(0)
        self.assertEqual(evaluate._bit(tuple(rows)),1 if rows[-1].reward==1.0 else 0)

    def test_frozen_public_support_requires_real_actions_and_masks(self):
        signatures,evidence,_=evaluate._physical_support()
        self.assertEqual(Counter(signatures),Counter(SUPPORT_SIGNATURES))
        self.assertEqual(len(evidence),16)
        self.assertTrue(all(x["all_four_support_interventions_physically_applied"]
                            for x in evidence))
        self.assertEqual({len(x["public_train_sha256"]) for x in evidence},{64})

    def test_sparse_candidate_identifies_balanced_query_then_nonredundant(self):
        for mode in ("SPARSE_PARTITION_GAIN","INDEPENDENT_BAYES_ENTROPY"):
            with self.subTest(mode=mode):
                p=policy.ActiveResidualPolicy(mode,SUPPORT_SIGNATURES,
                                              public_ordinal=0)
                self.assertEqual(p.choose_query(),0)
                with self.assertRaises(ValueError):
                    p.choose_query()
                p.observe_actual_query(0,0)
                self.assertEqual(p.choose_query(),2)
                p.observe_actual_query(2,0)
                self.assertEqual(p.chosen_queries,(0,2))
                self.assertEqual(p.posterior_support_count,4)
                self.assertEqual(p.predict_unqueried(1),0)
                self.assertEqual(p.predict_unqueried(3),0)
                self.assertLessEqual(p.logical_bytes,65536)

    def test_fixed_queries_are_redundant_even_with_all_support_data(self):
        p=policy.ActiveResidualPolicy("FIXED_0_1",SUPPORT_SIGNATURES,public_ordinal=0)
        self.assertEqual(p.choose_query(),0)
        p.observe_actual_query(0,1)
        self.assertEqual(p.choose_query(),1)
        p.observe_actual_query(1,1)
        self.assertEqual(p.posterior_support_count,8)
        self.assertEqual(p.predict_unqueried(2),0)
        self.assertEqual(p.predict_unqueried(3),0)

    def test_no_support_ablation_cannot_infer_missing_signature(self):
        p=policy.ActiveResidualPolicy("NO_SUPPORT_ABLATION",SUPPORT_SIGNATURES,
                                      public_ordinal=0)
        for idx in (0,1):
            self.assertEqual(p.choose_query(),idx)
            p.observe_actual_query(idx,1)
        self.assertIsNone(p.posterior_support_count)
        self.assertEqual(p.predict_unqueried(2),0)
        self.assertEqual(p.predict_unqueried(3),0)

    def test_random_two_queries_reproducible_not_outcome_driven(self):
        a=policy.ActiveResidualPolicy("DETERMINISTIC_RANDOM_TWO",
                                      SUPPORT_SIGNATURES,public_ordinal=3)
        b=policy.ActiveResidualPolicy("DETERMINISTIC_RANDOM_TWO",
                                      SUPPORT_SIGNATURES,public_ordinal=3)
        for i in range(2):
            x=a.choose_query()
            self.assertEqual(x,b.choose_query())
            a.observe_actual_query(x,i)
            b.observe_actual_query(x,1-i)
        self.assertEqual(a.chosen_queries,b.chosen_queries)
        self.assertEqual(len(set(a.chosen_queries)),2)

    def test_future_outcome_without_query_and_duplicate_refused_atomically(self):
        p=policy.ActiveResidualPolicy("SPARSE_PARTITION_GAIN",SUPPORT_SIGNATURES,
                                      public_ordinal=0)
        before=p.semantic_receipt()
        with self.assertRaises(ValueError):
            p.observe_actual_query(0,1)
        self.assertEqual(p.semantic_receipt(),before)
        self.assertEqual(p.choose_query(),0)
        before=p.semantic_receipt()
        for idx,b in ((1,0),(0,2),(0,True),(0,-1)):
            with self.assertRaises(ValueError):
                p.observe_actual_query(idx,b)
            self.assertEqual(p.semantic_receipt(),before)
        p.observe_actual_query(0,1)
        with self.assertRaises(ValueError):
            p.observe_actual_query(0,1)
        with self.assertRaises(ValueError):
            p.predict_unqueried(1)

    def test_exact_cold_replay_after_actual_query_evidence(self):
        p=policy.ActiveResidualPolicy("SPARSE_PARTITION_GAIN",SUPPORT_SIGNATURES,
                                      public_ordinal=5)
        for bit in (1,0):
            selected=p.choose_query()
            p.observe_actual_query(selected,bit)
        snapshot=p.checkpoint()
        restored=policy.ActiveResidualPolicy.restore(snapshot)
        self.assertEqual(restored.checkpoint(),snapshot)
        self.assertEqual(restored.semantic_receipt(),p.semantic_receipt())
        self.assertEqual(restored.chosen_queries,p.chosen_queries)
        for idx in range(4):
            if idx not in p.chosen_queries:
                self.assertEqual(restored.predict_unqueried(idx),
                                 p.predict_unqueried(idx))

    def test_snapshot_tamper_future_label_duplicate_key_and_pickle_denied(self):
        p=policy.ActiveResidualPolicy("INDEPENDENT_BAYES_ENTROPY",
                                      SUPPORT_SIGNATURES,public_ordinal=0)
        p.observe_actual_query(p.choose_query(),0)
        raw=p.checkpoint()
        a=json.loads(raw)
        a["body"]["actual_query_evidence"][0][1]^=1
        with self.assertRaises(ValueError):
            policy.ActiveResidualPolicy.restore(json.dumps(a).encode())
        for altered in (b"\x80\x04pickle",b"not-json",raw.replace(
                b'"sha256":',b'"sha256":"broken","sha256":')):
            with self.assertRaises(ValueError):
                policy.ActiveResidualPolicy.restore(altered)
        self.assertEqual(policy.ActiveResidualPolicy.restore(raw).checkpoint(),raw)

    def test_public_prior_validation_and_no_source_import(self):
        for bad in (None,[],(0,)*15,(0,)*17,
                    tuple([0]*15+[16]),tuple([0]*15+[True])):
            with self.assertRaises(ValueError):
                policy.ActiveResidualPolicy("SPARSE_PARTITION_GAIN",bad,public_ordinal=0)
        for mode in ("MALICIOUS",None):
            with self.assertRaises(ValueError):
                policy.ActiveResidualPolicy(mode,SUPPORT_SIGNATURES,public_ordinal=0)
        for ordinal in (24,-1,True,1.0):
            with self.assertRaises(ValueError):
                policy.ActiveResidualPolicy("SPARSE_PARTITION_GAIN",
                                            SUPPORT_SIGNATURES,public_ordinal=ordinal)
        content=Path(policy.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import public_active_source",content)
        self.assertNotIn("def _private_bit",content)
        self.assertNotIn("994500",content)
        self.assertNotIn("allow_dev=True",content)

    def test_scoring_protocol_without_eval_world_first_use(self):
        self.assertEqual(len(policy.MODES),5)
        with self.assertRaises(ValueError):
            evaluate._bootstrap([])
        self.assertEqual((16*16+5*(16+8)*16)*4,8704)


if __name__=="__main__":
    unittest.main()
