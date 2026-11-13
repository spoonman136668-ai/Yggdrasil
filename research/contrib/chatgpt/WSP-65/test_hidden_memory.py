"""WSP65 prospective new-action-history hidden-state SELFTEST.

Training: 128 chronological charged actions from one unreset physical session,
and all numerical models fit only this ledger. Heldout episodes provide 8-16
public historical state/action/consequence observations purely as CONTEXT;
never fit/observe on eval prefixes. The evaluator privately selects a
mode-dependent query action, equally supplied by public ID to all controls.
"""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import time
import unittest

from source import SEEDS,CHANNELS,TRAIN_CHARGES,TEST_CASES,build_world
from latent_writer import (
    HiddenParityWriter,SourceBlindExplorer,VisibleLookup,Suffix2Lookup,
    _terms,_masks
)
from independent_automaton import LatentModeLookup


def _digest(ledger):
    return sha256(json.dumps(ledger,sort_keys=True,
                  separators=(",",":")).encode("ascii")).hexdigest()


def _score(pred,truth,counts):
    if pred is None:
        counts["abstain"]+=1
    elif pred==truth:
        counts["correct"]+=1
    else:
        counts["wrong_confident"]+=1


class HistoryConditionedQualification(unittest.TestCase):
    def test_safety_scope_and_source_blindness(self):
        writer_code=(Path(__file__).parent/"latent_writer.py").read_text("utf-8")
        ctrl_code=(Path(__file__).parent/"independent_automaton.py").read_text("utf-8")
        self.assertNotIn("from source import",writer_code)
        self.assertNotIn("import source",writer_code)
        self.assertNotIn("from source import",ctrl_code)
        self.assertNotIn("import source",ctrl_code)
        self.assertEqual(HiddenParityWriter.gradient_steps,0)
        self.assertEqual(len(_terms(3)),11)
        self.assertEqual(len(_terms(4)),16)
        self.assertEqual(len(_masks(4)),697)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(3101,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(3001)
        for seed in SEEDS:
            world=build_world(seed)
            self.assertEqual(world.receipt(),build_world(seed).receipt())
            self.assertEqual(len(world.test_cases()),64)
        w=build_world(3101)
        learner=HiddenParityWriter()
        live=w.session()
        first=live.step(0)
        with self.assertRaises(ValueError):
            learner.observe(replace(first,before=(1,1,1)))
        with self.assertRaises(ValueError):
            learner.observe(replace(first,action_cost=0))
        self.assertEqual(len(learner.rows),0)
        learner.observe(first)
        with self.assertRaises(ValueError):
            learner.observe(replace(first,before=tuple(1-x for x in learner.state)))
        with self.assertRaises(ValueError):
            learner.predict((),(1,1,1),0)

    def test_twelve_world_mode_history_transfer(self):
        records=[]
        total={
            "heldout":0,"candidate_correct":0,"candidate_wrong_confident":0,
            "candidate_abstain":0,"visible_correct":0,"visible_wrong_confident":0,
            "visible_abstain":0,"suffix2_correct":0,"suffix2_wrong_confident":0,
            "suffix2_abstain":0,"symbolic_mode_correct":0,
            "symbolic_mode_wrong_confident":0,"symbolic_mode_abstain":0,
            "random_candidate_correct":0,"random_candidate_wrong_confident":0,
            "random_candidate_abstain":0,"history_scramble_correct":0,
            "history_scramble_wrong_confident":0,"history_scramble_abstain":0,
            "worlds_with_training_collision":0,
            "eval_public_context_steps":0,
            "test_private_modes_zero":0,"test_private_modes_one":0
        }
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                receipt=world.receipt()
                self.assertEqual(receipt,build_world(seed).receipt())
                candidate=HiddenParityWriter()
                random_model=HiddenParityWriter()
                explorer=SourceBlindExplorer()
                current=world.session()
                random_session=world.session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP65|random-channel-training|{seed}".encode("ascii")
                ).digest(),"big"))
                started=time.perf_counter()
                cpu_started=time.process_time()
                policy_seconds=0.
                for _ in range(TRAIN_CHARGES):
                    tick=time.perf_counter()
                    action=explorer.select(current.state)
                    policy_seconds+=time.perf_counter()-tick
                    row=current.step(action)
                    random_row=random_session.step(rng.choice(CHANNELS))
                    candidate.observe(row)
                    explorer.observe(row)
                    random_model.observe(random_row)
                    self.assertEqual(candidate.state,current.state)
                    self.assertEqual(random_model.state,random_session.state)
                self.assertEqual(len(candidate.rows),128)
                self.assertEqual(len(random_model.rows),128)
                self.assertEqual(len(current.charges),128)
                self.assertEqual(len(random_session.charges),128)
                self.assertEqual(candidate.rows[0][0],(0,)*world.bits)
                self.assertEqual(random_model.rows[0][0],(0,)*world.bits)
                self.assertTrue(all(candidate.rows[i][2]==candidate.rows[i+1][0]
                                    for i in range(127)))
                self.assertTrue(all(random_model.rows[i][2]==random_model.rows[i+1][0]
                                    for i in range(127)))
                stored=candidate.snapshot()
                restored=HiddenParityWriter.restore(stored)
                self.assertEqual(restored.snapshot(),stored)
                with self.assertRaises(ValueError):
                    HiddenParityWriter.restore(stored.replace(
                        "wsp65.hidden-parity-writer.v1",
                        "wsp65.hidden-parity-writer.v2"))
                visible=VisibleLookup(candidate.rows)
                suffix=Suffix2Lookup(candidate.rows)
                automaton=LatentModeLookup(candidate.rows)
                # Only these public training rows may fit any model.
                training_prefix=tuple(a for b,a,after in candidate.rows)
                cases=world.test_cases()
                self.assertEqual(len(cases),TEST_CASES)
                scores={
                    name:{"correct":0,"wrong_confident":0,"abstain":0}
                    for name in ("candidate","visible","suffix2","symbolic_mode",
                                 "random_candidate","history_scramble")
                }
                evaluated_prefixes=[]
                context_steps=0
                mode_counts={0:0,1:0}
                for case in cases:
                    self.assertEqual(case.history[0].before,(0,)*world.bits)
                    self.assertEqual(case.history[-1].after,case.current)
                    self.assertEqual(tuple(x.action for x in case.history),
                                     case._prefix_actions)
                    self.assertNotEqual(case._prefix_actions,
                                        training_prefix[:len(case._prefix_actions)])
                    self.assertTrue(8<=len(case.history)<=16)
                    mode_counts[case._mode]+=1
                    context_steps+=len(case.history)
                    query=(case.history,case.current,case.action)
                    predictions={
                        "candidate":candidate.predict(*query),
                        "visible":visible.predict(*query),
                        "suffix2":suffix.predict(*query),
                        "symbolic_mode":automaton.predict(*query),
                        "random_candidate":random_model.predict(*query),
                        "history_scramble":candidate.predict(
                            tuple(replace(row,action=(row.action+1)%4)
                                  for row in case.history),
                            case.current,case.action)
                    }
                    self.assertEqual(restored.predict(*query),
                                     predictions["candidate"])
                    for name,prediction in predictions.items():
                        _score(prediction,case._truth,scores[name])
                    evaluated_prefixes.append(_digest(
                        [[list(x.before),x.action,list(x.after)]
                         for x in case.history]))
                self.assertEqual(len(set(evaluated_prefixes)),64)
                for name,score in scores.items():
                    self.assertEqual(sum(score.values()),64,name)
                contradiction=len(candidate.training_visible_conflicts())
                total["worlds_with_training_collision"]+=int(contradiction>0)
                total["eval_public_context_steps"]+=context_steps
                total["test_private_modes_zero"]+=mode_counts[0]
                total["test_private_modes_one"]+=mode_counts[1]
                total["heldout"]+=64
                for name,score in scores.items():
                    for metric,count in score.items():
                        total[f"{name}_{metric}"]+=count
                family=by_family.setdefault(world.family,{
                    "worlds":0,"candidate_correct":0,"candidate_wrong_confident":0,
                    "visible_correct":0,"suffix2_correct":0,
                    "symbolic_mode_correct":0,"random_candidate_correct":0,
                    "training_collisions":0
                })
                family["worlds"]+=1
                family["candidate_correct"]+=scores["candidate"]["correct"]
                family["candidate_wrong_confident"]+=scores["candidate"]["wrong_confident"]
                family["visible_correct"]+=scores["visible"]["correct"]
                family["suffix2_correct"]+=scores["suffix2"]["correct"]
                family["symbolic_mode_correct"]+=scores["symbolic_mode"]["correct"]
                family["random_candidate_correct"]+=scores["random_candidate"]["correct"]
                family["training_collisions"]+=int(contradiction>0)
                records.append({
                    "seed":seed,"family":world.family,
                    "source":receipt,
                    "charged_candidate_actions":len(candidate.rows),
                    "charged_random_actions":len(random_model.rows),
                    "candidate_training_ledger_sha256":_digest(candidate.rows),
                    "random_training_ledger_sha256":_digest(random_model.rows),
                    "heldout_public_context_steps":context_steps,
                    "training_visible_contradictions":contradiction,
                    "candidate_latent_toggle_hypotheses":candidate.toggler_candidates(),
                    "random_latent_toggle_hypotheses":random_model.toggler_candidates(),
                    "independent_empirical_toggle_hypotheses":automaton.candidate_togglers(),
                    "candidate_model_evaluations":candidate.model_candidate_evaluations,
                    "candidate_snapshot_bits":candidate.capacity_bits(),
                    "scores":scores,
                    "test_private_mode_counts":mode_counts,
                    "active_policy_wall_seconds":round(policy_seconds,6),
                    "whole_experiment_wall_seconds":round(time.perf_counter()-started,6),
                    "whole_experiment_cpu_seconds":round(time.process_time()-cpu_started,6)
                })
        self.assertEqual(total["heldout"],768)
        self.assertEqual(len(records),12)
        self.assertEqual(sum(r["charged_candidate_actions"] for r in records),1536)
        self.assertEqual(sum(r["charged_random_actions"] for r in records),1536)
        criteria={
            "candidate_at_least_576_of_768":total["candidate_correct"]>=576,
            "beats_visible_by_154":
                total["candidate_correct"]-total["visible_correct"]>=154,
            "beats_two_action_suffix_by_77":
                total["candidate_correct"]-total["suffix2_correct"]>=77,
            "candidate_zero_wrong_confident":total["candidate_wrong_confident"]==0,
            "training_collisions_at_least_8_worlds":
                total["worlds_with_training_collision"]>=8
        }
        classification=("SELFTEST_SIGNAL" if all(criteria.values())
                        else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP65_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,"criteria":criteria,
            "totals":total,"by_family":by_family,"worlds":records
        },sort_keys=True,separators=(",",":")))
        # Frozen scientific development criterion is an observation,
        # NEVER a Python test assertion or authority for promotion.


if __name__=="__main__":
    unittest.main()
