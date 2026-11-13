"""WSP66 prospective 48-charge structured-vs-random hidden-mode experiment.

The new evaluator-only source supplies 16 fresh worlds and independent
heldout public action-history episodes. All models use identical unchanged
WSP65 HiddenParityWriter. Training observations come only from their
no-reset stateful session; public heldout prefixes are inference context,
NEVER persistent model updates or additional training observations.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from random import Random
import sys
import time
import json
import unittest

from source import SEEDS, CHANNELS, TRAIN_CHARGES, TEST_CASES, build_world
from balanced_policy import BalancedPairPolicy, CYCLE, debruijn_order2
# Pin unchanged parent WSP65 source-blind learner/controls, not evaluator.
_PARENT = Path(__file__).resolve().parents[1] / "WSP-65"
sys.path.insert(0, str(_PARENT))
from latent_writer import (
    HiddenParityWriter, SourceBlindExplorer, VisibleLookup, Suffix2Lookup
)
from independent_automaton import LatentModeLookup


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,
                  separators=(",",":")).encode("ascii")).hexdigest()


def tally(pred, truth, stat):
    if pred is None:
        stat["abstain"] += 1
    elif pred == truth:
        stat["correct"] += 1
    else:
        stat["wrong_confident"] += 1


def counted_stat():
    return {"correct":0, "wrong_confident":0, "abstain":0}


class PairedActionQualification(unittest.TestCase):
    def test_source_blindness_and_frozen_policy(self):
        src = (Path(__file__).parent/"balanced_policy.py").read_text("utf-8")
        self.assertNotIn("import source", src)
        self.assertNotIn("from source import", src)
        self.assertNotIn("import latent_writer", src)
        self.assertNotIn("from latent_writer import", src)
        self.assertEqual(HiddenParityWriter.gradient_steps, 0)
        self.assertEqual(CYCLE, debruijn_order2())
        self.assertEqual(len(CYCLE), 16)
        self.assertEqual(set((CYCLE[i], CYCLE[(i+1)%16])
                             for i in range(16)),
                         {(a,b) for a in CHANNELS for b in CHANNELS})
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(3201,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(3101)
        p=BalancedPairPolicy()
        with self.assertRaises(ValueError):
            p.select((1,0,0))
        with self.assertRaises(ValueError):
            p.select((0,0,0,0,0))
        self.assertEqual(p.select((0,0,0)), CYCLE[0])
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(w.bits,3 if seed<=3208 else 4)
            self.assertEqual(len(w.test_cases()),64)
            self.assertEqual(w.session().state,(0,)*w.bits)

    def test_sixteen_new_worlds_three_matched_policies(self):
        totals={
            "worlds":0,"heldout":0,
            "balanced_correct":0,"balanced_wrong_confident":0,"balanced_abstain":0,
            "random_correct":0,"random_wrong_confident":0,"random_abstain":0,
            "legacy_correct":0,"legacy_wrong_confident":0,"legacy_abstain":0,
            "independent_symbolic_correct":0,"independent_symbolic_wrong_confident":0,
            "independent_symbolic_abstain":0,
            "visible_correct":0,"visible_wrong_confident":0,"visible_abstain":0,
            "suffix_correct":0,"suffix_wrong_confident":0,"suffix_abstain":0,
            "scrambled_correct":0,"scrambled_wrong_confident":0,"scrambled_abstain":0,
            "balanced_training_collisions_worlds":0,
            "random_training_collisions_worlds":0,
            "balanced_cpu_ns":0,"random_cpu_ns":0,
            "balanced_wall_ns":0,"random_wall_ns":0,
            "heldout_public_context_steps":0,
            "mode_zero_cases":0,"mode_one_cases":0
        }
        family_summary={}
        receipts=[]
        for seed in SEEDS:
            with self.subTest(seed=seed):
                w=build_world(seed)
                balanced=HiddenParityWriter()
                random_model=HiddenParityWriter()
                legacy=HiddenParityWriter()
                paired_policy=BalancedPairPolicy()
                legacy_policy=SourceBlindExplorer()
                live_b=w.session()
                live_r=w.session()
                live_l=w.session()
                random=Random(int.from_bytes(sha256(
                    f"WSP66|random|{seed}".encode("ascii")
                ).digest(),"big"))
                b_cpu=r_cpu=b_wall=r_wall=0
                for _ in range(TRAIN_CHARGES):
                    start_c=time.process_time_ns()
                    start_w=time.perf_counter_ns()
                    action=paired_policy.select(live_b.state)
                    row=live_b.step(action)
                    paired_policy.observe(row)
                    balanced.observe(row)
                    b_cpu += time.process_time_ns()-start_c
                    b_wall += time.perf_counter_ns()-start_w

                    start_c=time.process_time_ns()
                    start_w=time.perf_counter_ns()
                    a_random=random.choice(CHANNELS)
                    rr=live_r.step(a_random)
                    random_model.observe(rr)
                    r_cpu += time.process_time_ns()-start_c
                    r_wall += time.perf_counter_ns()-start_w

                    a_legacy=legacy_policy.select(live_l.state)
                    rl=live_l.step(a_legacy)
                    legacy_policy.observe(rl)
                    legacy.observe(rl)

                    self.assertEqual(balanced.state,live_b.state)
                    self.assertEqual(random_model.state,live_r.state)
                    self.assertEqual(legacy.state,live_l.state)
                self.assertEqual(len(balanced.rows),TRAIN_CHARGES)
                self.assertEqual(len(random_model.rows),TRAIN_CHARGES)
                self.assertEqual(len(legacy.rows),TRAIN_CHARGES)
                self.assertEqual(paired_policy.charged_count(),TRAIN_CHARGES)
                self.assertEqual(balanced.rows[0][0],(0,)*w.bits)
                for model in (balanced,random_model,legacy):
                    self.assertTrue(all(model.rows[i][2]==model.rows[i+1][0]
                                        for i in range(TRAIN_CHARGES-1)))
                pairs=paired_policy.ordered_pairs()
                self.assertEqual(len(set(pairs)),16)
                self.assertEqual(len(pairs),47)
                self.assertEqual(Counter(a for b,a,after in balanced.rows),
                                 {0:12,1:12,2:12,3:12})
                frozen=balanced.snapshot()
                cold=HiddenParityWriter.restore(frozen)
                self.assertEqual(cold.snapshot(),frozen)
                with self.assertRaises(ValueError):
                    HiddenParityWriter.restore(frozen.replace(
                        "wsp65.hidden-parity-writer.v1",
                        "wsp65.hidden-parity-writer.v2"))
                visible=VisibleLookup(balanced.rows)
                suffix=Suffix2Lookup(balanced.rows)
                symbolic=LatentModeLookup(balanced.rows)
                cases=w.test_cases()
                scores={key:counted_stat() for key in (
                    "balanced","random","legacy","independent_symbolic",
                    "visible","suffix","scrambled")}
                eval_public_steps=0
                mode_counts={0:0,1:0}
                source_test_prefixes=[]
                for case in cases:
                    self.assertEqual(case.history[0].before,(0,)*w.bits)
                    self.assertEqual(case.history[-1].after,case.current)
                    self.assertTrue(8<=len(case.history)<=16)
                    self.assertEqual(tuple(x.action for x in case.history),
                                     case._prefix_actions)
                    context=(case.history,case.current,case.action)
                    source_test_prefixes.append(list(case._prefix_actions))
                    eval_public_steps+=len(case.history)
                    mode_counts[case._mode]+=1
                    start_c=time.process_time_ns()
                    start_w=time.perf_counter_ns()
                    pred_b=balanced.predict(*context)
                    b_cpu += time.process_time_ns()-start_c
                    b_wall += time.perf_counter_ns()-start_w
                    start_c=time.process_time_ns()
                    start_w=time.perf_counter_ns()
                    pred_r=random_model.predict(*context)
                    r_cpu += time.process_time_ns()-start_c
                    r_wall += time.perf_counter_ns()-start_w
                    self.assertEqual(cold.predict(*context),pred_b)
                    predictions={
                        "balanced":pred_b,
                        "random":pred_r,
                        "legacy":legacy.predict(*context),
                        "independent_symbolic":symbolic.predict(*context),
                        "visible":visible.predict(*context),
                        "suffix":suffix.predict(*context),
                        "scrambled":balanced.predict(
                            tuple(replace(q,action=(q.action+1)%4)
                                  for q in case.history),
                            case.current,case.action)
                    }
                    for name,pred in predictions.items():
                        tally(pred,case._truth,scores[name])
                self.assertEqual(len(set(tuple(x) for x in source_test_prefixes)),64)
                for name,stat in scores.items():
                    self.assertEqual(sum(stat.values()),TEST_CASES,name)
                b_coll=len(balanced.training_visible_conflicts())
                r_coll=len(random_model.training_visible_conflicts())
                totals["balanced_training_collisions_worlds"]+=int(b_coll>0)
                totals["random_training_collisions_worlds"]+=int(r_coll>0)
                totals["worlds"]+=1
                totals["heldout"]+=TEST_CASES
                totals["balanced_cpu_ns"]+=b_cpu
                totals["random_cpu_ns"]+=r_cpu
                totals["balanced_wall_ns"]+=b_wall
                totals["random_wall_ns"]+=r_wall
                totals["heldout_public_context_steps"]+=eval_public_steps
                totals["mode_zero_cases"]+=mode_counts[0]
                totals["mode_one_cases"]+=mode_counts[1]
                fam=family_summary.setdefault(w.family,{
                    "worlds":0,"balanced_correct":0,"random_correct":0,
                    "legacy_correct":0,"balanced_wrong_confident":0,
                    "random_wrong_confident":0,"balanced_collisions":0})
                fam["worlds"]+=1
                fam["balanced_correct"]+=scores["balanced"]["correct"]
                fam["random_correct"]+=scores["random"]["correct"]
                fam["legacy_correct"]+=scores["legacy"]["correct"]
                fam["balanced_wrong_confident"]+=scores["balanced"]["wrong_confident"]
                fam["random_wrong_confident"]+=scores["random"]["wrong_confident"]
                fam["balanced_collisions"]+=int(b_coll>0)
                for name,stat in scores.items():
                    for metric,value in stat.items():
                        totals[f"{name}_{metric}"]+=value
                receipts.append({
                    "seed":seed,"source":w.receipt(),
                    "balanced_ledger_sha256":digest(balanced.rows),
                    "random_ledger_sha256":digest(random_model.rows),
                    "legacy_ledger_sha256":digest(legacy.rows),
                    "charged_actions_per_arm":TRAIN_CHARGES,
                    "balanced_unique_adjacent_pairs":len(set(pairs)),
                    "random_unique_adjacent_pairs":len(set(
                        zip([a for b,a,y in random_model.rows][:-1],
                            [a for b,a,y in random_model.rows][1:]))),
                    "balanced_train_collisions":b_coll,
                    "random_train_collisions":r_coll,
                    "balanced_toggle_hypotheses":balanced.toggler_candidates(),
                    "random_toggle_hypotheses":random_model.toggler_candidates(),
                    "independent_empirical_togglers":symbolic.candidate_togglers(),
                    "score":scores,
                    "balanced_snapshot_bits":balanced.capacity_bits(),
                    "random_snapshot_bits":random_model.capacity_bits(),
                    "balanced_modeled_candidate_evaluations":
                        balanced.model_candidate_evaluations,
                    "random_modeled_candidate_evaluations":
                        random_model.model_candidate_evaluations,
                    "eval_public_context_steps":eval_public_steps,
                    "balanced_cpu_ns":b_cpu,"random_cpu_ns":r_cpu,
                    "balanced_wall_ns":b_wall,"random_wall_ns":r_wall
                })
        self.assertEqual(totals["worlds"],16)
        self.assertEqual(totals["heldout"],1024)
        self.assertEqual(sum(r["charged_actions_per_arm"] for r in receipts),768)
        self.assertEqual(sum(f["worlds"] for f in family_summary.values()),16)
        cpu_ratio=totals["balanced_cpu_ns"]/max(1,totals["random_cpu_ns"])
        criterion={
            "balanced_correct_ge_650":totals["balanced_correct"]>=650,
            "balanced_minus_random_ge_96":
                totals["balanced_correct"]-totals["random_correct"]>=96,
            "balanced_zero_confident_wrong":totals["balanced_wrong_confident"]==0,
            "observed_conflicts_ge_12_worlds":
                totals["balanced_training_collisions_worlds"]>=12,
            "all_action_pair_contexts_at_48":all(
                r["balanced_unique_adjacent_pairs"]==16 for r in receipts),
            "cpu_ratio_le_2":cpu_ratio<=2.0
        }
        classification=("SELFTEST_SIGNAL" if all(criterion.values())
                        else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP66_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,
            "criteria":criterion,
            "primary_cpu_ratio":round(cpu_ratio,7),
            "totals":totals,
            "by_family":family_summary,
            "worlds":receipts
        },sort_keys=True,separators=(",",":")))
        # A failed preregistered threshold is a valid, recorded negative result.
        # Only structural invariant failures raise Python errors.


if __name__=="__main__":
    unittest.main()
