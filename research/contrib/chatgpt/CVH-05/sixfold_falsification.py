"""CVH-05 retrospective *robustness falsification* of CVH04 authentic public reward learning.

No import/construction/reset/do of original CausalGym. The independent
original external MDP ran exactly 124 do actions in FKP26. This code only
reads the immutable already-consumed and hash-checked public source tapes.
All 6 train/held combinations were preregistered BEFORE sixfold scoring.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CVH04 = HERE.parent / "CVH-04"
if str(CVH04) not in sys.path:
    sys.path.insert(0, str(CVH04))
import real_public_retrospective as cvh04

SEEDS = (996100, 996101, 996102, 996103)
PAIRS = tuple(itertools.combinations(SEEDS, 2))
FROZEN_PAIRS = (
    (996100, 996101), (996100, 996102), (996100, 996103),
    (996101, 996102), (996101, 996103), (996102, 996103))
SOURCE_SHA = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
PARENT = "5836c5dcdb74a8a1a7c5c32097d02ee955a4b2c3"
PREREG_FIRST = "75abed7e43f04d23cf54ae2ed34130c8a4c46a54"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(obj):
    return sha256(canonical(obj)).hexdigest()


def mse(prediction, target):
    if not prediction or len(prediction) != len(target):
        return None
    return sum((p-y)*(p-y) for p,y in zip(prediction, target))/len(target)


def _public_fourcell_fit(worlds, train, prior):
    """Independent conditional return fit, with two frozen prior pseudo-counts."""
    observations = defaultdict(list)
    for seed in train:
        rows = worlds[seed]
        for row, total in zip(rows, cvh04.four_step_targets(rows)):
            observations[(row.before, row.action)].append(total)
    cells = {}
    for state in (0,1):
        for action in (0,1):
            values = observations[(state,action)]
            cells[(state,action)] = (
                (sum(values) + 2 * prior) / (len(values) + 2))
    return cells


def off_policy_nonidentifiability(worlds):
    """Data-only witness, NOT two simulated original MDP mechanisms.

    For each unique public realized history (seed, chronological event index),
    two arbitrary completions of the unperformed opposite-action immediate
    reward are possible: 0 and 1. Every observed outcome is unchanged.
    This is a partial-identification proof for logged data only; it does not
    assert both completions satisfy unknown original CausalGym SCM dynamics.
    """
    observed = []
    hypothetical_zero = []
    hypothetical_one = []
    for seed in SEEDS:
        rows = worlds[seed]
        for idx, row in enumerate(rows):
            if row.action != ((row.before+idx) % 2):
                raise AssertionError("CVH05_ORIGINAL_FIXED_BEHAVIOR_POLICY_DRIFT")
            key = (seed,idx,row.before,row.action,row.reward,row.after)
            # Worlds agree *exactly* on the observed source action/reward.
            observed.append(key)
            hypothetical_zero.append(key + (1-row.action,0))
            hypothetical_one.append(key + (1-row.action,1))
    if len(observed)!=124 or len(set(tuple(k[:2]) for k in observed))!=124:
        raise AssertionError("CVH05_ORIGINAL_PUBLIC_HISTORY_SET_DRIFT")
    assert len(hypothetical_zero)==len(hypothetical_one)==124
    return {
        "original_source_observed_actions":124,
        "source_actions_executed_by_this_test":0,
        "unknown_opposite_action_immediate_reward_slots":124,
        "possible_counterfactual_bit_values_per_slot":[0,1],
        "counterfactual_disagreements_between_compatible_log_completions":124,
        "known_original_source_outcomes_changed":0,
        "hypothetical_not_original_source_mechanisms":True,
        "off_policy_action_effect_identifiable_from_this_fixed_policy_log":False,
        "original_observed_log_sha256":digest(observed),
        "hypothetical_zero_digest":digest(hypothetical_zero),
        "hypothetical_one_digest":digest(hypothetical_one),
    }


def _learn_fold(worlds,train):
    held = tuple(s for s in SEEDS if s not in train)
    if len(train)!=2 or len(held)!=2 or any(s in train for s in held):
        raise AssertionError("CVH05_SPLIT_DISJOINTNESS_DRIFT")
    training = tuple(r for seed in train for r in worlds[seed])
    if len(training)!=62:
        raise AssertionError("CVH05_TRAIN_ACTION_BUDGET_DRIFT")
    prior_labels = tuple(y for seed in train for y in cvh04.four_step_targets(worlds[seed]))
    prior = sum(prior_labels)/len(prior_labels)
    # Inherited unmodified CVH01 *native* candidate. No new local learner.
    model = cvh04.EarnedReturnMemory()
    for row in training:
        model.observe(row)
    cold_raw = model.snapshot()
    restored = cvh04.EarnedReturnMemory.restore(cold_raw)
    if restored.snapshot()!=cold_raw or model.seen!=62:
        raise AssertionError("CVH05_COLD_TRAIN_MEMORY_NOT_VALID")
    # Independently fitted exact conventional batch from identical tape.
    counts,totals=cvh04.batch_public_returns(training)
    if counts!=model.count or totals!=model.total:
        raise AssertionError("CVH05_STRONG_INFORMATION_MATCHED_CONVENTIONAL_PARITY")
    fourcell = _public_fourcell_fit(worlds,train,prior)

    prediction=[]
    for seed in held:
        rows=worlds[seed]
        keys=cvh04.context_keys(rows)
        for row,key in zip(rows,keys):
            pa=(key//4)//3
            pr=(key//4)%3
            if (key%2)!=row.action or ((key//2)%2)!=row.before:
                raise AssertionError("CVH05_PUBLIC_CONTEXT_DECODE_DRIFT")
            native = (model.estimate(row.before,pa,pr,row.action)
                      if model.count[key]>=2 else None)
            exact = (totals[key]/(8*counts[key])
                     if counts[key]>=2 else None)
            bayes = ((totals[key]/8 + 2*prior)/(counts[key]+2))
            if native!=exact:
                raise AssertionError("CVH05_EXACT_CONVENTIONAL_TIE_VIOLATION")
            prediction.append({
                "seed":seed, "support":model.count[key],
                "native":native, "symbolic":exact,
                "prior":prior,"bayes":bayes,
                "fourcell":fourcell[(row.before,row.action)],
            })
    # Nothing from held reward targets entered the training or predictions.
    labels=tuple(y for seed in held for y in cvh04.four_step_targets(worlds[seed]))
    if len(prediction)!=62 or len(labels)!=62:
        raise AssertionError("CVH05_HISTORICAL_HELD_62_DRIFT")
    supported=tuple((p,y) for p,y in zip(prediction,labels) if p["native"] is not None)
    native_s=mse([p["native"] for p,y in supported],[y for p,y in supported])
    prior_s=mse([p["prior"] for p,y in supported],[y for p,y in supported])
    delta=None if native_s is None else prior_s-native_s
    fold={
        "train_seeds":list(train),"historically_consumed_held_seeds":list(held),
        "train_real_source_actions_reused":62,
        "retrospective_held_real_source_actions_reused":62,
        "new_external_source_actions":0,
        "held_supported_n":len(supported),
        "held_unsupported_n":62-len(supported),
        "native_supported_mse":native_s,
        "train_global_supported_mse":prior_s,
        "native_minus_global_mse_advantage":delta,
        "native_with_global_fallback_all_held_mse":
            mse([p["native"] if p["native"] is not None else p["prior"]
                 for p in prediction],labels),
        "train_global_all_held_mse":mse([p["prior"] for p in prediction],labels),
        "bayes_two_pseudocount_all_held_mse":
            mse([p["bayes"] for p in prediction],labels),
        "fitted_fourcell_all_held_mse":
            mse([p["fourcell"] for p in prediction],labels),
        "independent_exact_conventional_supported_predictions":len(supported),
        "independent_exact_conventional_disagreements":0,
        "train_cold_snapshot_sha256":sha256(cold_raw).hexdigest(),
        "train_cold_snapshot_bytes":len(cold_raw),
    }
    # Historical same-tape exposure is not independent science. A separate
    # cold continuation check must not mutate the original frozen candidate.
    continuation=cvh04.EarnedReturnMemory.restore(cold_raw)
    for seed in held:
        for row in worlds[seed]:
            continuation.observe(row)
    all_events=training+tuple(r for seed in held for r in worlds[seed])
    bc,bt=cvh04.batch_public_returns(all_events)
    if (continuation.seen!=124 or continuation.count!=bc
            or continuation.total!=bt
            or any(a<b for a,b in zip(continuation.count,model.count))
            or any(a<b for a,b in zip(continuation.total,model.total))
            or restored.snapshot()!=cold_raw
            or cvh04.EarnedReturnMemory.restore(continuation.snapshot()).snapshot()
                !=continuation.snapshot()):
        raise AssertionError("CVH05_FOLD_CUMULATIVE_COLD_RETENTION_FAIL")
    fold["posteval_old_train_counts_and_totals_preserved"]=True
    fold["posteval_cold_snapshot_sha256"]=sha256(continuation.snapshot()).hexdigest()
    return fold, tuple((p,y) for p,y in supported)


def run_sixfold():
    if PAIRS != FROZEN_PAIRS:
        raise AssertionError("CVH05_FROZEN_SPLIT_SCHEDULE_DRIFT")
    worlds=cvh04.load_original_public()
    if tuple(worlds)!=SEEDS or sum(len(r) for r in worlds.values())!=124:
        raise AssertionError("CVH05_ORIGINAL_CONSUMED_PUBLIC_SOURCE_MISSING")
    identifiability=off_policy_nonidentifiability(worlds)
    folds=[]
    all_native=[]
    all_global=[]
    all_targets=[]
    for train in PAIRS:
        fold,supported=_learn_fold(worlds,train)
        folds.append(fold)
        for p,y in supported:
            all_native.append(p["native"])
            all_global.append(p["prior"])
            all_targets.append(y)
    pooled_native=mse(all_native,all_targets)
    pooled_global=mse(all_global,all_targets)
    pooled_delta=pooled_global-pooled_native
    fold_deltas=[v["native_minus_global_mse_advantage"] for v in folds]
    positives=sum(d is not None and d>0 for d in fold_deltas)
    all_equal=all(v["independent_exact_conventional_disagreements"]==0 for v in folds)
    original_fold=folds[0]
    prior=cvh04.run_retrospective()
    if (original_fold["train_seeds"]!=[996100,996101]
            or original_fold["held_supported_n"]!=55
            or round(original_fold["native_supported_mse"],12)!=0.278320065227
            or round(original_fold["train_global_supported_mse"],12)!=0.293237912094
            or round(original_fold["native_minus_global_mse_advantage"],12)!=0.014917846867
            or prior["metric_receipt_sha256"]!="44f3f62ad48369448d2126154a482b2d215d94a6c19f8c3ad8024339ec5123f7"):
        raise AssertionError("CVH05_FROZEN_CVH04_ORIGINAL_SPLIT_RESULT_CHANGED")
    robust=(all(v["held_supported_n"]>=16 for v in folds)
            and positives>=5 and pooled_delta>=0.01
            and min(fold_deltas)>=-0.02 and all_equal)
    summary={
        "schema":"yggdrasil.cvh05.authentic-consumed-source-sixfold-robustness.v1",
        "prereg_first":PREREG_FIRST,"cvh04_parent_exact_sha":PARENT,
        "original_upstream_sha":SOURCE_SHA,"fkp26_run":43930489602,
        "cvh04_original_metric_receipt_sha256":prior["metric_receipt_sha256"],
        "original_real_source_interventions_reused":124,
        "new_original_source_actions":0,
        "source_original_first_use":False,
        "historical_cohort_previously_consumed":True,
        "new_prospectively_blind_science":False,
        "native_model":"unchanged CVH01 EarnedReturnMemory",
        "strongest_equal_information_control":"independently fitted exact batch return estimator, exact tie",
        "frozen_robustness_pass":robust,
        "classification":("RETROSPECTIVE_SIXFOLD_DEVELOPMENT_ROBUSTNESS_PASS_ONLY" if robust
                          else "RETROSPECTIVE_SIXFOLD_DEVELOPMENT_ROBUSTNESS_NO_GO"),
        "scientific_pass":False,"native_accepted":False,"deployment":False,
        "off_policy_identification":identifiability,
        "metrics":{
            "n_unique_splits":6,"scored_held_predictions_total":372,
            "selected_supported_total":len(all_native),
            "unsupported_total":372-len(all_native),
            "mean_fold_supported_n":sum(f["held_supported_n"] for f in folds)/6,
            "minimum_fold_supported_n":min(f["held_supported_n"] for f in folds),
            "positive_mse_advantage_folds":positives,
            "negative_mse_advantage_folds":6-positives,
            "pooled_supported_native_mse":pooled_native,
            "pooled_supported_global_mse":pooled_global,
            "pooled_native_vs_global_mse_advantage":pooled_delta,
            "worst_fold_mse_advantage":min(fold_deltas),
            "best_fold_mse_advantage":max(fold_deltas),
            "independent_exact_conventional_supported_ties":len(all_native),
            "independent_exact_conventional_disagreements":0,
            "all_folds_cold_and_cumulative_retention":True,
        },
        "folds":folds
    }
    # Report-only 12 decimals after raw preregistered decisions to ensure
    # Python 3.11/3.12 bit-stable result bytes across operating systems.
    summary=cvh04.canonicalize_report_precision(summary)
    summary["result_sha256"]=digest(summary)
    return summary


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-json",required=True)
    x=parser.parse_args()
    out=run_sixfold()
    p=Path(x.output_json)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CVH05_AUTHENTIC_SOURCE_SIXFOLD="+json.dumps({
        "classification":out["classification"],
        "summary":out["metrics"],
        "off_policy_identifiable":out["off_policy_identification"]["off_policy_action_effect_identifiable_from_this_fixed_policy_log"],
        "source_new_actions":0,
        "result_sha256":out["result_sha256"],
        "scientific_pass":False
    },sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    main()
