"""FKP-19 public-only delayed-causal credit test controls and failure fences.

No original FKP17 or FKP19 protected source is accessed. Engineering-only
toy TRAIN seed 991100 is intentionally non-blind and may be reused for tests.
"""
from collections import namedtuple
import json
from pathlib import Path
import unittest

import lag_credit as learner
import public_delayed_source as source


def trained_seed(seed=991100):
    arms={name:(
        learner.ExactBayesContext() if name=="EXACT_BAYES_CONTEXT" else
        learner.FullyFittedInteractionLogistic()
        if name=="FULLY_FITTED_INTERACTION_LOGISTIC" else
        learner.SparseLagCredit(name))
        for name in ("ELIGIBILITY_CONTRAST","EXACT_BAYES_CONTEXT",
                     "FULLY_FITTED_INTERACTION_LOGISTIC","CURRENT_ACTION_ONLY",
                     "CONTEXT_BLIND","EARLY_ACTION_SHUFFLED","NO_UPDATE")}
    for ep in range(8):
        early,late=source.exploratory_actions(seed,ep)
        rows=source.public_episode(seed,ep,early,late)
        for arm in arms.values():
            arm.observe_episode(rows,learn=True)
    arms["FULLY_FITTED_INTERACTION_LOGISTIC"].fit_after_exploration()
    return arms


class DelayedLearningTests(unittest.TestCase):
    def test_no_protected_or_unseen_world_first_use(self):
        for seed in (991500,991531,991600,991663,978500,978663,
                     976500,991116,-1,True,991100.0):
            with self.subTest(seed=seed), self.assertRaises(PermissionError):
                source.PublicDelayedSession(seed,0)
        for ep in (-1,24,True,0.0):
            with self.assertRaises(ValueError):
                source.PublicDelayedSession(991100,ep)
        self.assertEqual(len(source.TRAIN),16)

    def test_balanced_full_factorial_public_early_late_context(self):
        for seed in (source.TRAIN[0],source.TRAIN[-1]):
            triplets=[(source.context_at(seed,i),*source.exploratory_actions(seed,i))
                      for i in range(source.TRAIN_EPISODES)]
            self.assertEqual(len(set(triplets)),8)
            self.assertEqual(set(triplets),{(c,a,b) for c in (0,1)
                                           for a in (0,1) for b in (0,1)})
            self.assertEqual([source.scored_distractor(seed,i)
                              for i in range(8,24)].count(0),8)

    def test_reward_only_after_physically_chosen_distractor(self):
        s=source.PublicDelayedSession(source.TRAIN[0],0)
        ctx=s.public_state[0]
        self.assertEqual(s.public_state[1],0)
        for invalid in (-1,2,True,1.0):
            with self.assertRaises(ValueError):
                s.apply(invalid)
        before=s.public_state
        first=s.apply(0)
        self.assertEqual(first.before,before)
        self.assertEqual(first.reward,0.0)
        self.assertFalse(first.done)
        self.assertEqual(s.public_state[1],1)
        self.assertFalse(s.done)
        second=s.apply(1)
        self.assertEqual(second.reward in (-1.0,1.0),True)
        self.assertTrue(second.done)
        self.assertEqual(second.history[-1].action,0)
        self.assertEqual(second.action,1)
        self.assertEqual(second.before[0],ctx)
        self.assertTrue(s.done)
        with self.assertRaises(ValueError):
            s.apply(1)

    def test_actual_matched_interventions_identify_earlier_action(self):
        seed=source.TRAIN[0]
        for ep in range(8):
            _,late=source.exploratory_actions(seed,ep)
            zero=source.public_episode(seed,ep,0,late)
            one=source.public_episode(seed,ep,1,late)
            self.assertEqual(zero[0].before,one[0].before)
            self.assertEqual(zero[1].action,one[1].action)
            self.assertEqual(zero[1].reward,-one[1].reward)
            self.assertEqual(zero[0].reward,0.0)
            self.assertEqual(one[0].reward,0.0)

    def test_lag_credit_is_identified_by_balanced_physical_outcomes(self):
        arms=trained_seed()
        m=arms["ELIGIBILITY_CONTRAST"]
        self.assertEqual(m.explored_episodes,8)
        self.assertEqual(m.inferred_reward_cause_lag(0),1)
        self.assertEqual(m.inferred_reward_cause_lag(1),1)
        self.assertLess(m.learned_logical_bytes,65536)
        for ctx in (0,1):
            self.assertEqual(m.choose_early(ctx),
                             arms["EXACT_BAYES_CONTEXT"].choose_early(ctx))
            self.assertEqual(m.choose_early(ctx),
                             arms["FULLY_FITTED_INTERACTION_LOGISTIC"].choose_early(ctx))
        self.assertLessEqual(arms["FULLY_FITTED_INTERACTION_LOGISTIC"].training_bce,0.05)
        self.assertLessEqual(arms["FULLY_FITTED_INTERACTION_LOGISTIC"].fit_epochs,1024)

    def test_shams_do_not_recover_early_contextual_cause(self):
        m=trained_seed()
        self.assertEqual([m["CURRENT_ACTION_ONLY"].choose_early(c) for c in (0,1)],[0,0])
        self.assertEqual([m["CONTEXT_BLIND"].choose_early(c) for c in (0,1)],[0,0])
        self.assertEqual([m["NO_UPDATE"].choose_early(c) for c in (0,1)],[0,0])
        candidate=[m["ELIGIBILITY_CONTRAST"].choose_early(c) for c in (0,1)]
        shuffled=[m["EARLY_ACTION_SHUFFLED"].choose_early(c) for c in (0,1)]
        self.assertEqual(shuffled,[1-a for a in candidate])
        self.assertNotEqual(candidate[0],candidate[1])

    def test_real_selected_scored_actions_do_not_change_frozen_state(self):
        m=trained_seed()
        seed=source.TRAIN[0]
        for arm in m.values():
            frozen=arm.state_receipt()
            total=0.0
            for ep in range(8,24):
                chosen=arm.choose_early(source.context_at(seed,ep))
                rows=source.public_episode(seed,ep,chosen,source.scored_distractor(seed,ep))
                arm.observe_episode(rows,learn=False)
                total+=rows[-1].reward
            self.assertEqual(arm.state_receipt(),frozen)
            self.assertTrue(-16<=total<=16)
        candidate=m["ELIGIBILITY_CONTRAST"]
        self.assertEqual(sum(
            source.public_episode(seed,ep,
              candidate.choose_early(source.context_at(seed,ep)),
              source.scored_distractor(seed,ep))[-1].reward for ep in range(8,24)),16)

    def test_cold_checkpoint_bit_exact_and_tamper_resistant(self):
        model=trained_seed()["ELIGIBILITY_CONTRAST"]
        raw=model.checkpoint()
        restored=learner.SparseLagCredit.restore(raw)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.state_receipt(),model.state_receipt())
        for ctx in (0,1):
            self.assertEqual(restored.choose_early(ctx),model.choose_early(ctx))
        data=json.loads(raw)
        data["body"]["count"]=7
        with self.assertRaises(ValueError):
            learner.SparseLagCredit.restore(json.dumps(data).encode())
        with self.assertRaises(ValueError):
            learner.SparseLagCredit.restore(b"\x80\x04malicious")
        with self.assertRaises(ValueError):
            learner.SparseLagCredit.restore(b"{" + b"x"*65536 + b"}")

    def test_forged_private_data_invalid_history_or_reward_denied(self):
        row=source.public_episode(991100,0,0,1)
        outer=namedtuple("Private",(*row[1]._fields,"future_reward"))
        forged=outer(*row[1],1.0)
        invalids=[(row[0],forged),
                  (row[0],row[1]._replace(history=())),
                  (row[0],row[1]._replace(reward=0.0)),
                  (row[0],row[1]._replace(done=False)),
                  (row[0],row[1]._replace(after=(16,)*8))]
        arm=learner.SparseLagCredit()
        state=arm.state_receipt()
        for invalid in invalids:
            with self.assertRaises(ValueError):
                arm.observe_episode(invalid,learn=True)
            self.assertEqual(arm.state_receipt(),state)

    def test_after_eight_public_observations_cannot_refit_or_replay(self):
        model=trained_seed()["ELIGIBILITY_CONTRAST"]
        row=source.public_episode(991100,0,0,0)
        frozen=model.state_receipt()
        with self.assertRaises(ValueError):
            model.observe_episode(row,learn=True)
        self.assertEqual(frozen,model.state_receipt())
        logistic=trained_seed()["FULLY_FITTED_INTERACTION_LOGISTIC"]
        with self.assertRaises(ValueError):
            logistic.fit_after_exploration()

    def test_only_original_fkp18_trace_reused_without_copying_source(self):
        text=Path(learner.__file__).read_text("utf-8")
        self.assertIn("from temporal_trace import",text)
        self.assertIn("SparseTemporalTrace()",text)
        self.assertNotIn("import public_delayed_source",text)
        self.assertNotIn("def _polarity(",text)
        self.assertNotIn("991500",text)
        self.assertNotIn("allow_dev=True",text)


if __name__=="__main__":
    unittest.main()
