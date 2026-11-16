"""FKP-23 support/update ONLY negative and mechanical tests.

All focused tests are forbidden to physically open the new SHIFT_EVAL or
RETURN_EVAL cohorts. Those are prospectively first used ONLY in a future
exact-source qualified primary score after full Ubuntu/Windows regression.
"""
from collections import Counter
from pathlib import Path
import json
import unittest

import prior_repair as repair
import public_repair_source as source
import run_repair as experiment

FAKE_SHA="3"*64
FAMILIAR=(0,3,12,15)
SHIFTED=(0,5,10,15)


def public_support_models():
    trained={mode:repair.PhysicalPriorRepair(mode) for mode in repair.MODES}
    for sig in FAMILIAR*4:
        for model in trained.values():
            model.observe_public_world("support",sig,FAKE_SHA)
    for sig in SHIFTED*2:
        for model in trained.values():
            model.observe_public_world("update",sig,FAKE_SHA)
    for model in trained.values():
        model.freeze()
    return trained


def complete_virtual_probe(model,signature):
    # Mathematical unit test of a COMPLETELY PUBLIC, already learned relation;
    # no protected future-world episode or source-private label is accessed.
    for _ in range(3):
        i=model.choose_physical_query()
        model.observe_selected_consequence(i,(signature>>i)&1,FAKE_SHA)
    other=next(i for i in range(4) if i not in model.queried)
    return other,model.predict_last_unqueried(other),((signature>>other)&1)


class ContradictionAndRetentionTests(unittest.TestCase):
    def test_all_roles_and_protected_seed_separation(self):
        self.assertEqual(source.SUPPORT,tuple(range(995000,995016)))
        self.assertEqual(source.UPDATE,tuple(range(995100,995108)))
        self.assertEqual(source.SHIFT_EVAL,tuple(range(995200,995216)))
        self.assertEqual(source.RETURN_EVAL,tuple(range(995300,995316)))
        self.assertEqual(len(set(source.ALL)),56)
        self.assertEqual(source.BASE_INPUTS,(3,4,5,6,8,9,10,11,12,13,14,15))
        self.assertEqual(source.RESIDUAL_INPUTS,(0,1,2,7))
        self.assertEqual(set(source.BASE_INPUTS)&set(source.RESIDUAL_INPUTS),set())
        for seed in (995500,995531,995600,995663,994500,993500,
                     992500,991500,978500,976500,995316,False,
                     -1,995000.0):
            with self.subTest(seed=seed),self.assertRaises(PermissionError):
                source.PhysicalEpisode(seed,0)

    def test_fourth_physical_action_only_returns_actual_outcome(self):
        s=source.PhysicalEpisode(995000,1)
        for invalid in (-1,2,True,1.0):
            with self.assertRaises(ValueError):
                s.apply(invalid)
        rows=[]
        for phase,a in enumerate((1,0,1,0)):
            public_state=s.public_state
            item=s.apply(a)
            self.assertEqual(item.before,public_state)
            self.assertEqual(item.before[1],phase)
            self.assertEqual(item.after[1],phase+1)
            self.assertEqual(item.action,a)
            self.assertEqual(len(item.history),phase)
            if phase<3:
                self.assertEqual(item.reward,0.0)
                self.assertFalse(item.done)
            else:
                self.assertIn(item.reward,(-1.0,1.0))
                self.assertTrue(item.done)
            rows.append(item)
        self.assertTrue(s.done)
        with self.assertRaises(ValueError):
            s.apply(0)
        self.assertEqual(len(rows),4)

    def test_real_public_support_update_signatures_without_eval_first_use(self):
        signatures=[]
        for cohort in (source.SUPPORT,source.UPDATE):
            signs=[]
            for seed in cohort:
                sig,sha,proof=experiment._support_signature(seed)
                self.assertEqual(len(sha),64)
                self.assertEqual(proof["physically_observed_signature"],sig)
                signs.append(sig)
            signatures.append(signs)
        self.assertEqual(Counter(signatures[0]),Counter(FAMILIAR*4))
        self.assertEqual(Counter(signatures[1]),Counter(SHIFTED*2))

    def test_evidence_public_equal_across_independent_all_arms(self):
        checkpoints,custody,novel=experiment._same_public_population()
        self.assertEqual(len(checkpoints),len(repair.MODES))
        self.assertEqual(len(custody),24)
        self.assertEqual(tuple(novel),(5,10))
        self.assertTrue(all(x["physical_episode_count"]==16 for x in custody))
        for name,raw in checkpoints.items():
            obj=repair.PhysicalPriorRepair.restore(raw)
            self.assertEqual(obj.support_count,16)
            self.assertEqual(obj.update_count,8)
            self.assertEqual(obj.novel_signatures,(5,10))
            self.assertLessEqual(obj.learned_logical_bytes,65536)
            self.assertEqual(obj.checkpoint(),raw)

    def test_novelty_only_from_evidence_and_keeps_old_relations(self):
        models=public_support_models()
        candidate=models["SPARSE_CONTRADICTION_REPAIR"]
        self.assertEqual(candidate.novel_signatures,(5,10))
        self.assertEqual(set(candidate._hypotheses()),set(FAMILIAR)|set(SHIFTED))
        self.assertEqual(len(candidate._hypotheses()),24)
        self.assertEqual(set(models["FROZEN_OLD_PRIOR"]._hypotheses()),set(FAMILIAR))
        self.assertEqual(set(models["RECENT_ONLY_PRIOR"]._hypotheses()),set(SHIFTED))
        self.assertEqual(models["NO_MEMORY"]._hypotheses(),())

    def test_sparse_and_independent_exact_bayesian_tie_on_all_known_signatures(self):
        models=public_support_models()
        for sig in set(FAMILIAR)|set(SHIFTED):
            c=repair.PhysicalPriorRepair.restore(
                models["SPARSE_CONTRADICTION_REPAIR"].checkpoint())
            b=repair.PhysicalPriorRepair.restore(
                models["EXACT_BAYES_ALL_HISTORY"].checkpoint())
            chosen,guess,actual=complete_virtual_probe(c,sig)
            strong,other_guess,other_actual=complete_virtual_probe(b,sig)
            self.assertEqual((chosen,guess,actual),(strong,other_guess,other_actual))
            self.assertEqual(guess,actual)
            self.assertEqual(c.distinct_posterior_relations,1)
            self.assertEqual(b.distinct_posterior_relations,1)

    def test_frozen_old_fails_new_specific_consequence(self):
        old=public_support_models()["FROZEN_OLD_PRIOR"]
        outcomes=[complete_virtual_probe(repair.PhysicalPriorRepair.restore(
            old.checkpoint()),s) for s in SHIFTED]
        self.assertEqual(sum(int(pred==actual) for i,pred,actual in outcomes),3)
        self.assertEqual(outcomes[2][1:],(0,1))
        self.assertEqual(outcomes[2][0],3)

    def test_recent_only_forgets_one_old_consequence(self):
        recent=public_support_models()["RECENT_ONLY_PRIOR"]
        outcomes=[complete_virtual_probe(repair.PhysicalPriorRepair.restore(
            recent.checkpoint()),s) for s in FAMILIAR]
        self.assertEqual(sum(int(pred==actual) for i,pred,actual in outcomes),3)
        self.assertEqual(outcomes[2][1:],(0,1))

    def test_no_prior_has_no_evidence_to_predict_old_or_new(self):
        base=public_support_models()["NO_MEMORY"]
        self.assertEqual(sum(int((p==y)) for s in FAMILIAR
                             for i,p,y in [complete_virtual_probe(
                                 repair.PhysicalPriorRepair.restore(base.checkpoint()),s)]),2)
        self.assertEqual(sum(int((p==y)) for s in SHIFTED
                             for i,p,y in [complete_virtual_probe(
                                 repair.PhysicalPriorRepair.restore(base.checkpoint()),s)]),2)

    def test_cannot_act_twice_without_outcome_or_forge_future(self):
        obj=public_support_models()["SPARSE_CONTRADICTION_REPAIR"]
        before=obj.state_sha()
        with self.assertRaises(ValueError):
            obj.observe_selected_consequence(0,1,FAKE_SHA)
        self.assertEqual(obj.state_sha(),before)
        idx=obj.choose_physical_query()
        before=obj.state_sha()
        with self.assertRaises(ValueError):
            obj.choose_physical_query()
        for bad in ((1-idx,0,FAKE_SHA),(idx,True,FAKE_SHA),
                    (idx,0,"notsha"),(idx,2,FAKE_SHA)):
            with self.assertRaises(ValueError):
                obj.observe_selected_consequence(*bad)
            self.assertEqual(obj.state_sha(),before)
        obj.observe_selected_consequence(idx,0,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.observe_selected_consequence(idx,0,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.predict_last_unqueried(1)

    def test_ordered_source_stages_and_record_budget(self):
        obj=repair.PhysicalPriorRepair("SPARSE_CONTRADICTION_REPAIR")
        with self.assertRaises(ValueError):
            obj.observe_public_world("update",0,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.freeze()
        with self.assertRaises(ValueError):
            obj.observe_public_world("support",16,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.observe_public_world("support",0,"forged")
        for sig in FAMILIAR*4:
            obj.observe_public_world("support",sig,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.observe_public_world("support",0,FAKE_SHA)
        for sig in SHIFTED*2:
            obj.observe_public_world("update",sig,FAKE_SHA)
        with self.assertRaises(ValueError):
            obj.observe_public_world("update",5,FAKE_SHA)
        obj.freeze()
        with self.assertRaises(ValueError):
            obj.observe_public_world("update",5,FAKE_SHA)

    def test_cold_replay_after_actual_paired_probe_evidence(self):
        model=public_support_models()["SPARSE_CONTRADICTION_REPAIR"]
        for b in (1,0,1):
            q=model.choose_physical_query()
            model.observe_selected_consequence(q,b,FAKE_SHA)
        raw=model.checkpoint()
        cold=repair.PhysicalPriorRepair.restore(raw)
        self.assertEqual(cold.state_sha(),model.state_sha())
        self.assertEqual(cold.checkpoint(),raw)
        self.assertEqual(cold.queried,model.queried)
        unknown=next(k for k in range(4) if k not in model.queried)
        self.assertEqual(cold.predict_last_unqueried(unknown),
                         model.predict_last_unqueried(unknown))

    def test_json_cold_integrity_and_no_pickle_or_duplicate(self):
        model=public_support_models()["SPARSE_CONTRADICTION_REPAIR"]
        raw=model.checkpoint()
        for corrupt in (b"\x80\x04pickle",b"not-json",
                        b"{" + b"x"*65536+b"}",
                        raw.replace(b'"sha256":',b'"sha256":"bad","sha256":')):
            with self.assertRaises(ValueError):
                repair.PhysicalPriorRepair.restore(corrupt)
        changed=json.loads(raw)
        changed["body"]["update"][0][0]=7
        with self.assertRaises(ValueError):
            repair.PhysicalPriorRepair.restore(json.dumps(changed).encode())

    def test_source_independent_no_hardcoded_masks_or_hidden_cohorts(self):
        policy=Path(repair.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import public_repair_source",policy)
        self.assertNotIn("def _true_consequence",policy)
        self.assertNotIn("995200",policy)
        self.assertNotIn("995300",policy)
        self.assertNotIn("995500",policy)
        self.assertNotIn("allow_dev=True",policy)

    def test_cost_and_inherited_gf2_complete_source_safe_scope(self):
        self.assertEqual((16+8)*16*4+(16+16)*5*16*4,11776)
        self.assertEqual(len(repair.MODES),5)
        with self.assertRaises(ValueError):
            experiment._resample([])


if __name__=="__main__":
    unittest.main()
