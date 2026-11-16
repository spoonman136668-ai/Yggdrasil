"""FKP-20 deterministic source-public negative and matched-control gates.

All source execution here uses only TRAIN seed 992100. The primary 16-world
TRAIN cohort is scored separately *after* dual-OS exact-source qualification.
No protected DEV/TRANSFER first use, unearned counterfactual or native merge.
"""
from collections import namedtuple
from pathlib import Path
import json
import unittest

import public_pair_source as source
import pair_credit as methods


def _episode(seed,ep,actions,d):
    s=source.SelectedPublicEpisode(seed,ep)
    result=tuple(s.apply(a) for a in (*actions,d))
    assert s.done and len(result)==4
    return result


def _fit_one(seed=992100):
    arms={mode:(
        methods.ExactVersionSpace() if mode=="EXACT_VERSION_SPACE" else
        methods.FullyFittedInteractionLogistic() if mode=="FULLY_FITTED_INTERACTION_LOGISTIC" else
        methods.SparsePairCredit(mode))
        for mode in ("SPARSE_CONTRADICTION_PAIRS","EXACT_VERSION_SPACE",
                     "FULLY_FITTED_INTERACTION_LOGISTIC","UNARY_ONLY",
                     "NO_CONTEXT","CURRENT_DISTRACTOR_ONLY",
                     "TIME_PERMUTED_CREDIT","NO_UPDATE")}
    for ep in range(source.EXPLORE):
        ctx,a,b,c,d=source.exploration_tape(seed,ep)
        rows=_episode(seed,ep,(a,b,c),d)
        for arm in arms.values():
            arm.observe_episode(rows,learn=True)
    for a in arms.values():
        a.freeze()
    return arms


class MultiParentPublicTests(unittest.TestCase):
    def test_source_rejects_all_protected_worlds(self):
        self.assertEqual(source.TRAIN,tuple(range(992100,992116)))
        for seed in (992500,992531,992600,992663,991500,991600,
                     978500,978600,976500,992116,-1,True,992100.0):
            with self.subTest(seed=seed),self.assertRaises(PermissionError):
                source.SelectedPublicEpisode(seed,0)
        for ep in (-1,48,True,1.0):
            with self.assertRaises(ValueError):
                source.SelectedPublicEpisode(992100,ep)

    def test_full_factorial_equal_action_information_32_episodes(self):
        allf=[source.exploration_tape(992100,ep) for ep in range(32)]
        self.assertEqual(len(allf),32)
        self.assertEqual(len(set(allf)),32)
        self.assertEqual(set(allf),{(ctx,a,b,c,d) for ctx in (0,1)
                                   for a in (0,1) for b in (0,1)
                                   for c in (0,1) for d in (0,1)})
        self.assertEqual(sum(x[-1] for x in allf),16)
        self.assertEqual(source.EXPLORE,32)
        self.assertEqual(source.SCORE,16)

    def test_reward_only_after_all_four_physically_selected_actions(self):
        s=source.SelectedPublicEpisode(992100,0)
        for invalid in (True,2,-1,1.0):
            with self.assertRaises(ValueError):
                s.apply(invalid)
        rows=[]
        for phase,action in enumerate((1,0,1,0)):
            before=s.public_state
            row=s.apply(action)
            self.assertEqual(row.before,before)
            self.assertEqual(row.action,action)
            self.assertEqual(row.before[1],phase)
            self.assertEqual(row.after[1],phase+1)
            self.assertEqual(len(row.history),phase)
            if phase<3:
                self.assertEqual(row.reward,0.0)
                self.assertFalse(row.done)
            else:
                self.assertTrue(row.done)
                self.assertIn(row.reward,(-1.0,1.0))
            rows.append(row)
        self.assertTrue(s.done)
        with self.assertRaises(ValueError):
            s.apply(1)
        self.assertEqual(tuple(x.action for x in rows),(1,0,1,0))

    def test_same_frozen_training_data_independent_distractor_zero_effect(self):
        seed=992100
        for ep in (0,1,7,8,10,15):
            ctx,a,b,c,_=source.exploration_tape(seed,ep)
            first=_episode(seed,ep,(a,b,c),0)
            second=_episode(seed,ep,(a,b,c),1)
            self.assertEqual(first[-1].reward,second[-1].reward)
            self.assertEqual(first[0].before,second[0].before)
            self.assertEqual(first[-1].action,0)
            self.assertEqual(second[-1].action,1)
            self.assertEqual(first[0].reward,0.0)

    def test_two_parent_credit_allocate_and_infer_from_public_interventions(self):
        arms=_fit_one()
        candidate=arms["SPARSE_CONTRADICTION_PAIRS"]
        self.assertEqual(candidate.observed_episodes,32)
        self.assertEqual(candidate.inferred_pair(),((0,1),1))
        self.assertEqual(len(candidate._allocated_pairs()),3)
        self.assertLessEqual(candidate.learned_logical_bytes,65536)
        for ctx in (0,1):
            self.assertEqual(candidate.choose_plan(ctx),
                             arms["EXACT_VERSION_SPACE"].choose_plan(ctx))
            self.assertEqual(candidate.choose_plan(ctx),
                             arms["FULLY_FITTED_INTERACTION_LOGISTIC"].choose_plan(ctx))
        self.assertEqual(arms["FULLY_FITTED_INTERACTION_LOGISTIC"].fit_epochs,22)
        self.assertLessEqual(arms["FULLY_FITTED_INTERACTION_LOGISTIC"].train_bce,0.05)

    def test_frozen_candidate_matches_independent_controls_on_real_train_feedback(self):
        arms=_fit_one()
        seed=992100
        for name in ("SPARSE_CONTRADICTION_PAIRS","EXACT_VERSION_SPACE",
                     "FULLY_FITTED_INTERACTION_LOGISTIC"):
            arm=arms[name]
            before=arm.state_receipt()
            total=0
            for ep in range(32,48):
                ctx=source.context(seed,ep)
                chosen=arm.choose_plan(ctx)
                actual=_episode(seed,ep,chosen,source.scored_distractor(seed,ep))
                arm.observe_episode(actual,learn=False)
                total+=actual[-1].reward
            self.assertEqual(total,16)
            self.assertEqual(arm.state_receipt(),before)

    def test_all_single_cause_and_no_context_ablations_lack_valid_pair(self):
        arms=_fit_one()
        for name in ("UNARY_ONLY","NO_CONTEXT","CURRENT_DISTRACTOR_ONLY","NO_UPDATE"):
            arm=arms[name]
            self.assertIsNone(arm.inferred_pair())
            self.assertEqual(arm.choose_plan(0),(0,0,0))
            self.assertEqual(arm.choose_plan(1),(0,0,0))
        self.assertNotEqual(arms["SPARSE_CONTRADICTION_PAIRS"].choose_plan(0),
                            arms["SPARSE_CONTRADICTION_PAIRS"].choose_plan(1))
        correct=arms["SPARSE_CONTRADICTION_PAIRS"].inferred_pair()[0]
        reassigned=tuple(sorted((i+1)%3 for i in correct))
        self.assertNotEqual(correct,reassigned)

    def test_cold_copy_restores_exact_conditional_actions_and_frozen_state(self):
        model=_fit_one()["SPARSE_CONTRADICTION_PAIRS"]
        raw=model.checkpoint()
        restored=methods.SparsePairCredit.restore(raw)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.state_receipt(),model.state_receipt())
        self.assertEqual(restored.inferred_pair(),model.inferred_pair())
        for ctx in (0,1):
            self.assertEqual(restored.choose_plan(ctx),model.choose_plan(ctx))
        self.assertLessEqual(len(raw),65536)

    def test_tampered_checkpoint_private_future_or_forged_history_refused(self):
        model=methods.SparsePairCredit()
        rows=_episode(992100,0,(0,0,0),0)
        before=model.state_receipt()
        bad=namedtuple("IllegalPublic",(*rows[3]._fields,"future_oracle"))
        forged=bad(*rows[3],1.0)
        cases=[(*rows[:3],forged),
               (*rows[:3],rows[3]._replace(history=())),
               (*rows[:3],rows[3]._replace(reward=0.0)),
               (*rows[:3],rows[3]._replace(done=False)),
               (*rows[:3],rows[3]._replace(after=(16,)*8))]
        for rows_bad in cases:
            with self.assertRaises(ValueError):
                model.observe_episode(tuple(rows_bad),learn=True)
            self.assertEqual(model.state_receipt(),before)
        model.observe_episode(rows,learn=True)
        blob=model.checkpoint()
        j=json.loads(blob)
        j["body"]["frozen"]=True
        with self.assertRaises(ValueError):
            methods.SparsePairCredit.restore(json.dumps(j).encode())
        with self.assertRaises(ValueError):
            methods.SparsePairCredit.restore(b"\x80\x04pickle-code")

    def test_not_fitted_outcome_cannot_be_chosen_or_forged(self):
        model=methods.SparsePairCredit()
        with self.assertRaises(ValueError):
            model.choose_plan(0)
        with self.assertRaises(ValueError):
            model.freeze()
        for mode in ("bogus","UNKNOWN",None):
            with self.assertRaises(ValueError):
                methods.SparsePairCredit(mode)
        model.observe_episode(_episode(992100,0,(0,0,0),0),learn=True)
        frozen=model.state_receipt()
        with self.assertRaises(ValueError):
            model.observe_episode(_episode(992100,1,(0,0,1),0),learn="yes")
        self.assertEqual(model.state_receipt(),frozen)

    def test_no_source_or_held_imports_in_learned_policy(self):
        text=Path(methods.__file__).read_text("utf-8")
        self.assertIn("from temporal_trace import",text)
        self.assertNotIn("import public_pair_source",text)
        self.assertNotIn("def _private_law",text)
        self.assertNotIn("992500",text)
        self.assertNotIn("978500",text)
        self.assertNotIn("allow_dev=True",text)


if __name__=="__main__":
    unittest.main()
