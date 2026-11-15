"""ST4 one-checkpoint, actual in-house action-consequence comparison.

The frozen training/held law IDs are EVALUATOR-ONLY, never passed into
NativeCausal8, Recurrent45, or LagAwareCount. Both counterfactual arms take
real private-source steps in independently reset worlds. Every learner
predicts BEFORE env.step, and each sees ONLY its arm's public trajectory.
No model receives trial IDs, arm labels, hidden masks, law IDs or paired
counterfactual outcomes. The source is synthetic DEV, NOT original external
science, protected first-use or unfamiliar real-world transfer.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st4.paired_world import (
    PrivatePairedWorld,blind_design,TRIALS,source_paired_trial
)
from research.nci04_st4.native_credit import NativeCausal8,canonical
from research.nci04_st4.matched_controls import (
    Recurrent45,LagAwareCount,brier
)
from research.nci04_st4.source_audit import (
    TRAIN_LAWS,TRAIN_SEEDS,HELD_DEV_LAWS,HELD_DEV_SEEDS,
    verify_freeze,audit,FREEZE_BLOB
)

SCHEMA_TRAIN="yggdrasil.nci04.st4.single-original-training-checkpoint.v1"
SCHEMA_RESULT="yggdrasil.nci04.st4.frozen-inhouse-development-result.v1"
MODELS=("candidate","recurrent45","lag_count","no_delay","sham",
        "erase","label_shuffle")
SOURCE_BLOB="447b946ee03c725902ce4d96f17bbc22aaeb814d"
SOURCE_AUDIT_BLOB="ce3677964459efab1b783387d43bb2e4d63a8054"
MAX_CHECKPOINT_BYTES=1200000
PROCESS=psutil.Process()


def guard_source():
    frozen=verify_freeze()
    for path,expected in (
        ("research/nci04_st4/paired_world.py",SOURCE_BLOB),
        ("research/nci04_st4/source_audit.py",SOURCE_AUDIT_BLOB)
    ):
        got=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True
        ).strip()
        if got!=expected:
            raise ValueError("ST4_AUTHENTIC_FROZEN_SOURCE_DRIFT_"+path)
    return frozen


def create_models():
    return {
        "candidate":NativeCausal8("causal"),
        "recurrent45":Recurrent45(),
        "lag_count":LagAwareCount(),
        "no_delay":NativeCausal8("no_delay"),
        "sham":NativeCausal8("sham"),
        "erase":NativeCausal8("erase"),
        "label_shuffle":NativeCausal8("label_shuffle"),
    }


def restore_model(name,payload):
    if name=="recurrent45":
        return Recurrent45.restore(payload)
    if name=="lag_count":
        return LagAwareCount.restore(payload)
    obj=NativeCausal8.restore(payload)
    expected={"candidate":"causal"}.get(name,name)
    if obj.variant!=expected:
        raise ValueError("ST4_WRONG_ABLATION_SNAPSHOT_"+name)
    return obj


def restore_models(checkpoint):
    if type(checkpoint) is not dict or set(checkpoint)!=set(MODELS):
        raise ValueError("ST4_BAD_SHARED_TRAINED_MODEL_SET")
    models={n:restore_model(n,checkpoint[n]) for n in MODELS}
    if any(models[n].snapshot()!=checkpoint[n] for n in MODELS):
        raise ValueError("ST4_SINGLE_CHECKPOINT_RESTORE_DRIFT")
    return models


def observe(name,model,public,action,target,after,training):
    return model.observe(
        public,action,target,after,train=training
    )


def run_law_seed(evaluator_law,evaluator_seed,models,phase,train,
                 *,state_sha=False):
    """Causal pair world is private to THIS evaluator, not a model call."""
    if phase not in ("train","held","cold","interference"):
        raise ValueError("ST4_BAD_EXPERIMENT_PHASE")
    if type(train) is not bool or not models:
        raise ValueError("ST4_BAD_EVALUATION_MODE")
    source_sha=sha256()
    candidate_sha=sha256()
    sums={n:{"all":0.0,"probe":0.0,"treat_probe":0.0,
             "control_probe":0.0} for n in models}
    times={n:{"wall_ns":0,"cpu_ns":0} for n in models}
    source_wall=0
    actor_wall=0
    source_cpu=0
    cold=0
    total_actions=0
    contrast_correct=0
    contrast_total=0
    contrast_prob_distance=0.0
    process_rss=PROCESS.memory_info().rss
    pairs=[]
    for trial in range(TRIALS):
        ts=time.perf_counter_ns()
        design=blind_design(evaluator_seed,trial)
        actor_wall+=time.perf_counter_ns()-ts
        pair_sha=sha256()
        arm_probe={}
        for arm in design["arm_order"]:
            world=PrivatePairedWorld(evaluator_law,evaluator_seed,trial)
            for model in models.values():
                model.reset_episode()
            action0=2 if arm=="treatment" else 3
            for t,action in enumerate((action0,design["probe_action"])):
                public=world.public()
                preds={}
                for n,model in models.items():
                    ts=time.perf_counter_ns();cpu=time.process_time_ns()
                    preds[n]=model.predict(public,action)
                    times[n]["wall_ns"]+=time.perf_counter_ns()-ts
                    times[n]["cpu_ns"]+=time.process_time_ns()-cpu
                ts=time.perf_counter_ns();cpu=time.process_time_ns()
                after,target=world.step(action)
                source_wall+=time.perf_counter_ns()-ts
                source_cpu+=time.process_time_ns()-cpu
                if tuple(a^b for a,b in zip(public,after))!=target:
                    raise ValueError("ST4_ORIGINAL_INHOUSE_ACTION_DRIFT")
                if t==0:
                    first_step=(public,action,after,target)
                else:
                    # Mirror the ORIGINAL source_paired_trial digest exactly:
                    # its second action does not repeat the pre-probe public
                    # frame already recorded as the first step's successor.
                    a0,chosen,x1,y1=first_step
                    pair_sha.update(bytes((
                        *a0,chosen,*x1,*y1,action,*after,*target
                    )))
                if t==1:
                    arm_probe[arm]={"preds":preds,"target":target,
                                    "public":public,"action":action}
                if phase in ("held","cold"):
                    for n in models:
                        val=brier(preds[n],target)
                        sums[n]["all"]+=val
                        if t==1:
                            sums[n]["probe"]+=val
                            key=("treat_probe" if arm=="treatment"
                                 else "control_probe")
                            sums[n][key]+=val
                for n,model in tuple(models.items()):
                    ts=time.perf_counter_ns();cpu=time.process_time_ns()
                    returned=observe(n,model,public,action,target,after,train)
                    times[n]["wall_ns"]+=time.perf_counter_ns()-ts
                    times[n]["cpu_ns"]+=time.process_time_ns()-cpu
                    if returned!=preds[n]:
                        raise ValueError("ST4_PREACTION_OUTCOME_LEAK_"+n)
                if state_sha and "candidate" in models:
                    # Debug/determinism custody has real compute cost and
                    # must not be excluded from candidate cost comparisons.
                    ts=time.perf_counter_ns();cpu=time.process_time_ns()
                    candidate_sha.update(sha256(
                        models["candidate"].snapshot().encode("utf-8")
                    ).digest())
                    times["candidate"]["wall_ns"]+=time.perf_counter_ns()-ts
                    times["candidate"]["cpu_ns"]+=time.process_time_ns()-cpu
                # Same bounded cold check each law/seed, for ALL models,
                # only after original first source consequence was observed.
                if t==0 and trial==0:
                    for n,model in tuple(models.items()):
                        ts=time.perf_counter_ns();cpu=time.process_time_ns()
                        payload=model.snapshot()
                        restored=restore_model(n,payload)
                        if restored.snapshot()!=payload:
                            raise ValueError("ST4_COLD_MODEL_DRIFT_"+n)
                        models[n]=restored
                        cold+=1
                        times[n]["wall_ns"]+=time.perf_counter_ns()-ts
                        times[n]["cpu_ns"]+=time.process_time_ns()-cpu
                total_actions+=1
                process_rss=max(process_rss,PROCESS.memory_info().rss)
        if set(arm_probe)!={"treatment","control"}:
            raise ValueError("ST4_SOURCE_PAIR_MISSING_ARM")
        a=arm_probe["treatment"]
        b=arm_probe["control"]
        if a["public"]!=b["public"] or a["action"]!=b["action"]:
            raise ValueError("ST4_NONMATCHED_ORIGINAL_PUBLIC_PAIR")
        for i,(ya,yb) in enumerate(zip(a["target"],b["target"])):
            if ya==yb:
                continue
            contrast_total+=1
            if "candidate" in models:
                pa=a["preds"]["candidate"][i]
                pb=b["preds"]["candidate"][i]
                contrast_prob_distance+=abs(pa-pb)
                contrast_correct+=int(
                    (pa>.5)==bool(ya) and (pb>.5)==bool(yb)
                )
        pair_sha_final=pair_sha.hexdigest()
        if phase=="train":
            # Stage0's ORIGINAL source-only trial computed this digest
            # independently; it is read only for comparison, not fitted.
            original=source_paired_trial(evaluator_law,evaluator_seed,trial)
            if original["paired_original_action_consequence_sha256"]!=pair_sha_final:
                raise ValueError("ST4_CONSUMED_TRAIN_ACTOR_SOURCE_SHA_MISMATCH")
        pairs.append(pair_sha_final)
        source_sha.update(bytes.fromhex(pair_sha_final))
    if total_actions!=TRIALS*4:
        raise ValueError("ST4_INCOMPLETE_SOURCE_ACTION_COHORT")
    nsteps=total_actions
    result={
        "law_evaluator_only":evaluator_law,"seed_evaluator_only":evaluator_seed,
        "phase":phase,"source_real_actions":nsteps,
        "original_paired_source_sha256":source_sha.hexdigest(),
        "original_pair_sha256":pairs,
        "candidate_per_actual_action_state_hash":
            candidate_sha.hexdigest() if state_sha else None,
        "preaction_brier":(
            {n:{"all":sums[n]["all"]/nsteps,
                "probe":sums[n]["probe"]/(TRIALS*2),
                "treat_probe":sums[n]["treat_probe"]/TRIALS,
                "control_probe":sums[n]["control_probe"]/TRIALS}
             for n in models} if phase in ("held","cold") else None
        ),
        "paired_true_opposing_bits":contrast_total,
        "paired_candidate_directionally_correct_bits":contrast_correct,
        "paired_mean_candidate_probability_separation":
            contrast_prob_distance/contrast_total if contrast_total else 0.0,
        "model_cost_ns":times,
        "source_wall_ns":source_wall,"source_cpu_ns":source_cpu,
        "blind_actor_wall_ns":actor_wall,
        "shared_process_peak_rss_bytes":process_rss,
        "cold_restarts":cold,
        "model_received_private_source_fields":False,
        "protected_scientific_first_use":False,
    }
    return result


def train_once(out):
    guard_source()
    source_gate_path=out.with_name("st4-original-source-gate.json")
    gate=audit(source_gate_path)
    if gate["result"]["disposition"]!=(
            "SOURCE_BALANCED_INTERVENTIONS_IDENTIFIABLE_DEV_ONLY"):
        raise ValueError("ST4_TRAINING_REFUSED_INVALID_SOURCE")
    start=time.perf_counter_ns()
    models=create_models()
    training=[]
    for law in TRAIN_LAWS:
        d=sha256()
        for seed in TRAIN_SEEDS:
            rec=run_law_seed(law,seed,models,"train",True)
            training.append(rec)
            for pair in rec["original_pair_sha256"]:
                d.update(bytes.fromhex(pair))
        saved=next(
            row for row in gate["source_law_receipts"]
            if row["law_evaluator_only"]==law
        )
        if d.hexdigest()!=saved["original_source_pair_action_history_sha256"]:
            raise ValueError("ST4_TRAIN_SOURCE_AND_AUDIT_DISAGREE")
    checkpoint={
        "schema":SCHEMA_TRAIN,
        "frozen_protocol_blob":FREEZE_BLOB,
        "original_source_git_blob":SOURCE_BLOB,
        "train_laws":list(TRAIN_LAWS),
        "train_seeds":list(TRAIN_SEEDS),
        "training_source_action_steps":sum(
            r["source_real_actions"] for r in training
        ),
        "training_original_per_law_source_receipts":
            gate["source_law_receipts"],
        "native_and_control_models":{
            n:models[n].snapshot() for n in MODELS
        },
        "capacity":{
            n:models[n].accounting()
            for n in ("candidate","recurrent45","lag_count")
        },
        "protected_scientific_first_use":False,
        "held_development_opened":False,
        "training_cpu_accounting":{
            n:sum(r["model_cost_ns"][n]["cpu_ns"] for r in training)
            for n in MODELS
        },
        "training_wall_accounting":{
            n:sum(r["model_cost_ns"][n]["wall_ns"] for r in training)
            for n in MODELS
        },
        "worker_training_wall_ns":time.perf_counter_ns()-start,
    }
    if checkpoint["training_source_action_steps"]!=6144:
        raise ValueError("ST4_TRAIN_ACTION_COUNT_DRIFT")
    out.write_text(canonical(checkpoint)+"\n",encoding="utf-8")
    print("ST4_SHARED_TRAIN_EPISODES="+str(len(training)))
    print("ST4_SHARED_TRAIN_SOURCE_ACTIONS=6144")
    print("ST4_TRAIN_CHECKPOINT_SHA256="+sha256(out.read_bytes()).hexdigest())
    print("ST4_TRAIN_FROZEN_HELD_NOT_OPENED=PASS")
    return checkpoint


def read_checkpoint(path):
    raw=path.read_bytes()
    if len(raw)>MAX_CHECKPOINT_BYTES:
        raise ValueError("ST4_OVERSIZED_TRAIN_CHECKPOINT")
    c=json.loads(raw)
    if (c.get("schema")!=SCHEMA_TRAIN or
        c.get("frozen_protocol_blob")!=FREEZE_BLOB or
        c.get("original_source_git_blob")!=SOURCE_BLOB or
        c.get("train_laws")!=list(TRAIN_LAWS) or
        c.get("train_seeds")!=list(TRAIN_SEEDS) or
        c.get("training_source_action_steps")!=6144 or
        c.get("protected_scientific_first_use") is not False or
        c.get("held_development_opened") is not False or
        raw.decode("utf-8")!=canonical(c)+"\n"):
        raise ValueError("ST4_TRAIN_CUSTODY_MISMATCH")
    restore_models(c["native_and_control_models"])
    return c,sha256(raw).hexdigest()


def cold_retention():
    """Private evaluator law ID never transmitted into native model."""
    model=NativeCausal8("causal")
    suite={"candidate":model}
    for seed in TRAIN_SEEDS[:3]:
        run_law_seed(3,seed,suite,"interference",True)
    def recall():
        trained_counts=canonical(suite["candidate"].banks)
        prior_updates=suite["candidate"].updates
        rec=run_law_seed(3,TRAIN_SEEDS[0],suite,"cold",False)
        if (suite["candidate"].updates!=prior_updates or
            canonical(suite["candidate"].banks)!=trained_counts):
            raise ValueError("ST4_COLD_RECALL_TRAINING_LEAK")
        return rec["preaction_brier"]["candidate"]["probe"]
    before=recall()
    unrelated=(5,7,11,13,17,19,23,43)
    for law in unrelated:
        run_law_seed(law,TRAIN_SEEDS[0],suite,"interference",True)
    after=recall()
    baseline_gain=max(0.0,.25-before)
    ratio=(max(0.0,1.0-max(0.0,after-before)/baseline_gain)
           if baseline_gain>0 else 0.0)
    return {
        "original_law_evaluator_only":3,
        "unrelated_interfering_training_laws":list(unrelated),
        "before_cold_probe_brier":before,
        "after_cold_probe_brier":after,
        "chance_corrected_gain_retained_ratio":ratio,
        "frozen_minimum_retained_ratio":.95,
        "passed":ratio>=.95,
        "cold_recall_fitted_original_law":False,
        "protected_scientific_first_use":False
    }


def classify(episodes,retention,capacity):
    if (len(episodes)!=32 or
        sum(r["source_real_actions"] for r in episodes)!=2048):
        raise ValueError("ST4_UNQUALIFIED_HELD_COHORT")
    per_law={}
    for law in HELD_DEV_LAWS:
        rows=[r for r in episodes if r["law_evaluator_only"]==law]
        if len(rows)!=len(HELD_DEV_SEEDS):
            raise ValueError("ST4_MISSING_HELD_LAW")
        per_law[str(law)]={
            n:sum(r["preaction_brier"][n]["probe"] for r in rows)/len(rows)
            for n in MODELS
        }
    metric={
        kind:{
            n:sum(r["preaction_brier"][n][kind] for r in episodes)/
              len(episodes)
            for n in MODELS
        } for kind in ("all","probe","treat_probe","control_probe")
    }
    total_opposed=sum(r["paired_true_opposing_bits"] for r in episodes)
    total_right=sum(r["paired_candidate_directionally_correct_bits"]
                    for r in episodes)
    total_distance=sum(
        r["paired_mean_candidate_probability_separation"]*
        r["paired_true_opposing_bits"] for r in episodes
    )
    if total_opposed<=0:
        raise ValueError("ST4_NO_REAL_HELD_CAUSAL_CONTRASTS")
    best=min(metric["probe"]["lag_count"],
             metric["probe"]["recurrent45"])
    win_laws=sum(
        per_law[str(law)]["candidate"]<
        min(per_law[str(law)]["recurrent45"],
            per_law[str(law)]["lag_count"])
        for law in HELD_DEV_LAWS
    )
    model_wall={
        n:sum(r["model_cost_ns"][n]["wall_ns"] for r in episodes)
        for n in MODELS
    }
    model_cpu={
        n:sum(r["model_cost_ns"][n]["cpu_ns"] for r in episodes)
        for n in MODELS
    }
    common=sum(r["source_wall_ns"]+r["blind_actor_wall_ns"]
               for r in episodes)
    ratio=(common+model_wall["candidate"])/max(1,common+min(
        model_wall["lag_count"],model_wall["recurrent45"]
    ))
    equal_bytes=(
        capacity["candidate"]["learned_uint8_counter_bytes"]==
        capacity["lag_count"]["learned_uint8_counter_bytes"]==
        3456
    )
    fraction=total_right/total_opposed
    separation=total_distance/total_opposed
    checks={
        "pooled_candidate_beats_strongest_conventional_by_0_02":
            metric["probe"]["candidate"]<=best-.02,
        "wins_best_conventional_in_3_of_4_held_laws":win_laws>=3,
        "causal_credit_beats_both_frozen_ablations_by_0_02":
            metric["treat_probe"]["candidate"]<=min(
                metric["treat_probe"]["no_delay"],
                metric["treat_probe"]["sham"])-.02,
        "paired_consequence_direction_correct_over_60pct":
            fraction>=.60,
        "paired_consequence_predicted_separation_over_0_12":
            separation>=.12,
        "cold_interference_retained_95pct_chance_corrected_gain":
            retention["passed"],
        "candidate_and_lag_count_counter_byte_budget_equal":
            equal_bytes,
        "every_original_source_episode_cold_restores_all_models":
            all(r["cold_restarts"]==2*len(MODELS) for r in episodes),
        "authentic_online_model_updates_nonzero":
            all(r["source_real_actions"]==64 for r in episodes),
        "whole_source_actor_model_wall_ratio_under_1_5":
            ratio<=1.5,
    }
    return {
        "per_held_law_probe_brier":per_law,
        "pooled_preaction_brier":metric,
        "strict_held_law_wins":win_laws,
        "true_pair_opposed_outcome_bits":total_opposed,
        "correctly_predicted_opposed_direction_bits":total_right,
        "paired_direction_correct_fraction":fraction,
        "paired_probability_separation":separation,
        "candidate_vs_best_control_total_wall_ratio":ratio,
        "model_cpu_ns":model_cpu,
        "model_wall_ns":model_wall,
        "shared_source_actor_wall_ns":common,
        "peak_shared_process_rss_bytes":max(
            r["shared_process_peak_rss_bytes"] for r in episodes
        ),
        "candidate_and_control_counter_byte_parity":equal_bytes,
        "extra_state_capacity_including_metadata_identical":
            "NOT_PROVEN",
        "independently_measured_model_RSS":"NOT_PROVEN",
        "full_final_regression":"NOT_QUALIFIED",
        "frozen_checks":checks,
        "development_disposition":(
            "DEV_SIGNAL_PENDING_CROSS_OS_NOT_SCIENTIFIC"
            if all(checks.values()) else "DEV_NO_GO"
        ),
    }


def compare(checkpoint_path,out):
    guard_source()
    p,ck_sha=read_checkpoint(checkpoint_path)
    models=restore_models(p["native_and_control_models"])
    # Only now, AFTER reading frozen model bytes and source constraints,
    # consume predeclared in-house DEV law IDs.
    begin=time.perf_counter_ns()
    held=[]
    for law in HELD_DEV_LAWS:
        for seed in HELD_DEV_SEEDS:
            held.append(run_law_seed(law,seed,models,"held",True,
                                     state_sha=True))
    retention=cold_retention()
    metrics=classify(held,retention,p["capacity"])
    doc={
        "schema":SCHEMA_RESULT,"source_kind":"IN_HOUSE_DEVELOPMENT_ONLY",
        "frozen_protocol_blob":FREEZE_BLOB,
        "source_original_blob":SOURCE_BLOB,
        "training_checkpoint_sha256":ck_sha,
        "training_source_per_law_receipts":
            p["training_original_per_law_source_receipts"],
        "held_source_receipts":held,
        "retention":retention,"metrics":metrics,
        "held_laws_opened_once":list(HELD_DEV_LAWS),
        "held_seeds_opened_once":list(HELD_DEV_SEEDS),
        "candidate_or_control_saw_private_law_or_pair_id":False,
        "protected_first_use":False,"independent_source":False,
        "scientific_pass":False,
        "frozen_hypothesis_changed_after_held":False,
        "worker_eval_wall_ns":time.perf_counter_ns()-begin,
        "cross_os_native_integer_state":"PENDING_PARITY",
        "development_disposition":metrics["development_disposition"]
    }
    out.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST4_HELD_DEV_PROBE_BRIER="+canonical(
        metrics["pooled_preaction_brier"]["probe"]))
    print("ST4_HELD_DEV_TREAT_PROBE_BRIER="+canonical(
        metrics["pooled_preaction_brier"]["treat_probe"]))
    print("ST4_HELD_COLD_RETENTION="+canonical(retention))
    print("ST4_FROZEN_CHECKS="+canonical(metrics["frozen_checks"]))
    print("ST4_DEV_DISPOSITION="+metrics["development_disposition"])
    print("ST4_PROTECTED_FIRST_USE=NOT_RUN")
    return doc


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    mode=parser.add_subparsers(dest="mode",required=True)
    t=mode.add_parser("train")
    t.add_argument("--output",type=Path,required=True)
    e=mode.add_parser("compare")
    e.add_argument("--checkpoint",type=Path,required=True)
    e.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.mode=="train":
        train_once(a.output)
    else:
        compare(a.checkpoint,a.output)
