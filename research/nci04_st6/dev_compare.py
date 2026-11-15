"""ST6 frozen authentic public-action compositional transfer evaluator.

Only SOURCE holds hidden private law IDs, actuator masks and operator mode.
Every model predicts BEFORE world.step and fits only AFTER real public
consequence. True held A/B combinations and alternate OR mechanism NEVER
fit any model. Seven same-information model variants train ONCE on Linux,
their exact checkpoint restored identically on both OS.

Synthetic in-house DEV only; no protected first-use or scientific promotion.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st6.original_world import OriginalWorld,ACTIONS,TRIALS
from research.nci04_st6.source_audit import (
    audit,verify_prereg,PREREG_BLOB,TRAIN,SEEDS,HELD,NEG
)
from research.nci04_st6.native_operator import NativeOperator8,canonical
from research.nci04_st6.matched_controls import (
    create_models,restored_models,restore_one,brier
)

SOURCE_BLOB="99cbda9f502920b64ac4f44521d8c6e262e0e463"
AUDIT_BLOB="b81334a0e62202b84bff2e9bc779321217a48140"
MODEL_BLOB="06362fca957cb9cf42f6c8cf482c2e77c578803d"
CONTROLS_BLOB="e1c49ad95a7017b1b1d11709a6fc160eb102dca5"
TRAIN_SCHEMA="yggdrasil.nci04.st6.frozen-common-training.v1"
DEV_SCHEMA="yggdrasil.nci04.st6.frozen-composition-dev.v1"
MODELS=tuple(create_models())
INTERFERENCE=(53,59,61,67,71,73,79,83)
HELDS=tuple(range(201,209))
MAX_CHECKPOINT=3500000
PROCESS=psutil.Process()


def guard():
    prereg=verify_prereg()
    files=(
        ("research/nci04_st6/original_world.py",SOURCE_BLOB),
        ("research/nci04_st6/source_audit.py",AUDIT_BLOB),
        ("research/nci04_st6/native_operator.py",MODEL_BLOB),
        ("research/nci04_st6/matched_controls.py",CONTROLS_BLOB)
    )
    for path,blob in files:
        got=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
        if got!=blob:
            raise ValueError("ST6_EXACT_PRE_HELD_SOURCE_MODEL_DRIFT_"+path)
    return prereg


def persistent_state(model):
    if hasattr(model,"mismatches"):
        return canonical([model.mismatches,model.support])
    if hasattr(model,"loss"):
        return canonical([model.loss,model.samples])
    if hasattr(model,"banks"):
        return canonical(model.banks)
    return canonical([model.local,model.shared])


def run_original(law,seed,trial,models,phase,train,*,cold=False):
    if phase not in ("train","held","negative","recall","interference"):
        raise ValueError("ST6_EVALUATOR_BAD_PHASE")
    if type(train) is not bool or set(models)!=set(MODELS):
        raise ValueError("ST6_EVALUATOR_MODEL_BOUNDARY")
    world=OriginalWorld(law,seed,trial)
    for m in models.values():m.reset_episode()
    events=bytearray()
    t_cost={n:{"wall_ns":0,"cpu_ns":0} for n in MODELS}
    source_wall=0;source_cpu=0;actor_wall=0
    delayed={n:None for n in MODELS}
    cold_checks=0
    peak_rss=PROCESS.memory_info().rss
    for index in range(5):
        ts=time.perf_counter_ns()
        act=ACTIONS[index]
        actor_wall+=time.perf_counter_ns()-ts
        public=world.public()
        forecast={}
        for n,m in models.items():
            ts=time.perf_counter_ns();cpu=time.process_time_ns()
            forecast[n]=m.predict(public,act)
            t_cost[n]["wall_ns"]+=time.perf_counter_ns()-ts
            t_cost[n]["cpu_ns"]+=time.process_time_ns()-cpu
        ts=time.perf_counter_ns();cpu=time.process_time_ns()
        after,target=world.step(act)
        source_wall+=time.perf_counter_ns()-ts
        source_cpu+=time.process_time_ns()-cpu
        if tuple(x^y for x,y in zip(public,after))!=target:
            raise ValueError("ST6_AUTHENTIC_SOURCE_TARGET_DRIFT")
        events.extend(bytes((*public,act,*after,*target)))
        if index==4:
            for n in MODELS:
                delayed[n]=brier(forecast[n],target)
        for n,m in tuple(models.items()):
            ts=time.perf_counter_ns();cpu=time.process_time_ns()
            returned=m.observe(public,act,target,after,train=train)
            t_cost[n]["wall_ns"]+=time.perf_counter_ns()-ts
            t_cost[n]["cpu_ns"]+=time.process_time_ns()-cpu
            if returned!=forecast[n]:
                raise ValueError("ST6_FUTURE_ORACLE_LABEL_LEAK_"+n)
        if cold and index==2:
            for n,m in tuple(models.items()):
                ts=time.perf_counter_ns();cpu=time.process_time_ns()
                blob=m.snapshot()
                restored=restore_one(n,blob)
                if restored.snapshot()!=blob:
                    raise ValueError("ST6_COLD_CHECKPOINT_INEXACT_"+n)
                models[n]=restored
                cold_checks+=1
                t_cost[n]["wall_ns"]+=time.perf_counter_ns()-ts
                t_cost[n]["cpu_ns"]+=time.process_time_ns()-cpu
        peak_rss=max(peak_rss,PROCESS.memory_info().rss)
    ts=time.perf_counter_ns();cpu=time.process_time_ns()
    native_sha=sha256(models["candidate"].snapshot().encode("utf-8")).hexdigest()
    t_cost["candidate"]["wall_ns"]+=time.perf_counter_ns()-ts
    t_cost["candidate"]["cpu_ns"]+=time.process_time_ns()-cpu
    return {
        "original_event_bytes_hex":events.hex(),
        "original_event_sha256":sha256(events).hexdigest(),
        "original_source_steps":5,
        "preaction_probe_brier":delayed,
        "native_integer_state_sha256":native_sha,
        "model_cpu_wall_ns":t_cost,
        "source_wall_ns":source_wall,"source_cpu_ns":source_cpu,
        "blind_actor_wall_ns":actor_wall,
        "all_model_cold_restores":cold_checks,
        "shared_worker_peak_rss_bytes":peak_rss,
        "source_private_law_or_rule_passed_to_learner":False,
        "protected_scientific_first_use":False
    }


def train_once(path):
    guard()
    gate=audit(path.with_name("st6-original-source-gate.json"))
    if gate["gate"]["disposition"]!="SOURCE_COMPOSITION_IDENTIFIABLE_DEV_ONLY":
        raise ValueError("ST6_TRAIN_REFUSED_UNIDENTIFIABLE_SOURCE")
    started=time.perf_counter_ns()
    models=create_models()
    source_receipts=[]
    times={n:{"wall_ns":0,"cpu_ns":0} for n in MODELS}
    source_wall=0;actor_wall=0
    count=0
    for law in TRAIN:
        source_trace=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                rec=run_original(law,seed,trial,models,"train",True,
                                 cold=(trial==0))
                source_trace.update(bytes.fromhex(
                    rec["original_event_bytes_hex"]))
                count+=rec["original_source_steps"]
                source_wall+=rec["source_wall_ns"]
                actor_wall+=rec["blind_actor_wall_ns"]
                for n in MODELS:
                    for part in ("wall_ns","cpu_ns"):
                        times[n][part]+=rec["model_cpu_wall_ns"][n][part]
        stage0=next(x for x in gate["original_source_law_action_receipts"]
                    if x["source_law_evaluator_only"]==law)
        if stage0["actual_source_sha256"]!=source_trace.hexdigest():
            raise ValueError("ST6_TRAINING_ACTUAL_EVENTS_NOT_SOURCE_AUDIT")
        source_receipts.append({
            "law_evaluator_only":law,
            "original_action_sha256":source_trace.hexdigest()
        })
    if count!=7680:
        raise ValueError("ST6_TRAINING_ORIGINAL_ACTION_COVERAGE")
    report={
        "schema":TRAIN_SCHEMA,
        "frozen_protocol_blob":PREREG_BLOB,
        "original_source_blob":SOURCE_BLOB,
        "native_model_blob":MODEL_BLOB,
        "matched_controls_blob":CONTROLS_BLOB,
        "training_laws":list(TRAIN),
        "training_seeds":list(SEEDS),
        "original_training_actions":count,
        "original_training_episodes":len(TRAIN)*len(SEEDS)*TRIALS,
        "actual_source_law_trace_receipts":source_receipts,
        "trained_public_models":{n:models[n].snapshot() for n in MODELS},
        "model_capacity_receipts":{n:models[n].accounting() for n in MODELS},
        "model_training_cpu_wall_ns":times,
        "training_source_wall_ns":source_wall,
        "training_actor_wall_ns":actor_wall,
        "worker_training_wall_ns":time.perf_counter_ns()-started,
        "held_dev_unopened":True,
        "negative_new_mechanism_unopened":True,
        "protected_scientific_first_use":False
    }
    path.write_text(canonical(report)+"\n",encoding="utf-8")
    print("ST6_ORIGINAL_TRAINING_ACTIONS="+str(count))
    print("ST6_TRAIN_CHECKPOINT_SHA256="+sha256(path.read_bytes()).hexdigest())
    print("ST6_TRAIN_HELD_NEGATIVE_NOT_OPENED=PASS")
    return report


def load_checkpoint(path):
    raw=path.read_bytes()
    if len(raw)>MAX_CHECKPOINT:
        raise ValueError("ST6_CHECKPOINT_OVERSIZED")
    obj=json.loads(raw)
    if (obj.get("schema")!=TRAIN_SCHEMA or
        obj.get("frozen_protocol_blob")!=PREREG_BLOB or
        obj.get("original_source_blob")!=SOURCE_BLOB or
        obj.get("native_model_blob")!=MODEL_BLOB or
        obj.get("matched_controls_blob")!=CONTROLS_BLOB or
        obj.get("training_laws")!=list(TRAIN) or
        obj.get("training_seeds")!=list(SEEDS) or
        obj.get("original_training_actions")!=7680 or
        obj.get("original_training_episodes")!=1536 or
        obj.get("held_dev_unopened") is not True or
        obj.get("negative_new_mechanism_unopened") is not True or
        obj.get("protected_scientific_first_use") is not False or
        raw.decode("utf-8")!=canonical(obj)+"\n"):
        raise ValueError("ST6_FROZEN_SINGLE_TRAIN_CHECKPOINT_CUSTODY")
    restored_models(obj["trained_public_models"])
    return obj,sha256(raw).hexdigest()


def cold_original(models):
    frozen={n:persistent_state(models[n]) for n in MODELS}
    rows=[run_original(3,100,t,models,"recall",False,cold=(t==0))
          for t in range(TRIALS)]
    for n in MODELS:
        if n=="erase":
            continue
        if persistent_state(models[n])!=frozen[n]:
            raise ValueError("ST6_ORIGINAL_RECALL_FITTED_"+n)
    return {
        "original_law_evaluator_only":3,
        "original_source_steps":80,
        "original_source_sha256":sha256(b"".join(
            bytes.fromhex(r["original_event_bytes_hex"]) for r in rows
        )).hexdigest(),
        "probe_brier":{n:sum(x["preaction_probe_brier"][n] for x in rows)/TRIALS
                       for n in MODELS},
        "all_original_cold_model_restarts":
            sum(x["all_model_cold_restores"] for x in rows),
        "original_model_counter_training_during_recall":False,
        "model_cost":{
            n:{part:sum(x["model_cpu_wall_ns"][n][part] for x in rows)
               for part in ("wall_ns","cpu_ns")} for n in MODELS
        },
        "source_actor_wall_ns":sum(
            x["source_wall_ns"]+x["blind_actor_wall_ns"] for x in rows
        ),
        "native_cold_state_sha256":rows[-1]["native_integer_state_sha256"]
    }


def retention(checkpoint):
    models=restored_models(checkpoint["trained_public_models"])
    pre=cold_original(models)
    receipts=[]
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in MODELS}
    common=0
    for law in INTERFERENCE:
        sha=sha256()
        for t in range(TRIALS):
            rec=run_original(law,111,t,models,"interference",True,
                             cold=(t==0))
            sha.update(bytes.fromhex(rec["original_event_bytes_hex"]))
            common+=rec["source_wall_ns"]+rec["blind_actor_wall_ns"]
            for n in MODELS:
                for part in ("wall_ns","cpu_ns"):
                    costs[n][part]+=rec["model_cpu_wall_ns"][n][part]
        receipts.append({
            "law_evaluator_only":law,
            "genuine_source_sha256":sha.hexdigest(),
            "real_original_action_steps":TRIALS*5
        })
    post=cold_original(models)
    initial=pre["probe_brier"]["candidate"]
    final=post["probe_brier"]["candidate"]
    gain=max(0.,.25-initial)
    retained=(max(0.,1.-max(0.,final-initial)/gain) if gain else 0.)
    return {
        "before":pre,"after":post,
        "interference_law_action_receipts":receipts,
        "interference_real_original_actions":sum(
            x["real_original_action_steps"] for x in receipts
        ),
        "candidate_retained_gain_fraction":retained,
        "candidate_absolute_brier_change":final-initial,
        "training_without_original_law_rehearsal":True,
        "interference_model_cost":costs,
        "interference_source_actor_wall_ns":common,
        "protected_scientific_first_use":False
    }


def test_family(checkpoint,laws,seeds,phase):
    models=restored_models(checkpoint["trained_public_models"])
    rows=[];count=0
    for law in laws:
        for seed in seeds:
            digest=sha256()
            scores={n:0. for n in MODELS}
            wall={n:{"wall_ns":0,"cpu_ns":0} for n in MODELS}
            common=0;max_rss=PROCESS.memory_info().rss
            cold_total=0
            states=[]
            for trial in range(TRIALS):
                rec=run_original(law,seed,trial,models,phase,False,
                                 cold=(trial==0))
                count+=rec["original_source_steps"]
                digest.update(bytes.fromhex(rec["original_event_bytes_hex"]))
                for n in MODELS:
                    scores[n]+=rec["preaction_probe_brier"][n]
                    for part in ("wall_ns","cpu_ns"):
                        wall[n][part]+=rec["model_cpu_wall_ns"][n][part]
                common+=rec["source_wall_ns"]+rec["blind_actor_wall_ns"]
                cold_total+=rec["all_model_cold_restores"]
                max_rss=max(max_rss,rec["shared_worker_peak_rss_bytes"])
                states.append(rec["native_integer_state_sha256"])
            rows.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "source_actions":80,
                "original_source_sha256":digest.hexdigest(),
                "preaction_probe_brier":{
                    n:scores[n]/TRIALS for n in MODELS
                },
                "native_integer_state_sha_chain":sha256(
                    bytes.fromhex("".join(states))
                ).hexdigest(),
                "model_cpu_wall_ns":wall,
                "source_actor_wall_ns":common,
                "all_model_cold_restarts":cold_total,
                "peak_shared_process_rss_bytes":max_rss,
                "model_private_source_fields_received":False
            })
    if count!=len(laws)*len(seeds)*TRIALS*5:
        raise ValueError("ST6_FROZEN_REAL_SOURCE_COHORT_INCOMPLETE")
    return {
        "phase":phase,"original_source_steps":count,
        "source_receipts":rows,
        "pooled_probe_brier":{
            n:sum(row["preaction_probe_brier"][n] for row in rows)/len(rows)
            for n in MODELS
        }
    }


def classify(held,negative,recall,checkpoint):
    if (held["original_source_steps"]!=2560 or
        len(held["source_receipts"])!=32 or
        negative["original_source_steps"]!=160 or
        len(negative["source_receipts"])!=2 or
        recall["interference_real_original_actions"]!=640):
        raise ValueError("ST6_FROZEN_SOURCE_SCOPES_MISSING")
    score=held["pooled_probe_brier"]
    strong=score["symbolic8"]
    bylaw={
        str(law):sum(r["preaction_probe_brier"]["candidate"]
                     for r in held["source_receipts"]
                     if r["law_evaluator_only"]==law)/len(HELDS)
        for law in HELD
    }
    eval_rows=(held["source_receipts"]+
               negative["source_receipts"])
    costs={n:(
        checkpoint["model_training_cpu_wall_ns"][n]["wall_ns"]+
        recall["interference_model_cost"][n]["wall_ns"]+
        recall["before"]["model_cost"][n]["wall_ns"]+
        recall["after"]["model_cost"][n]["wall_ns"]+
        sum(r["model_cpu_wall_ns"][n]["wall_ns"] for r in eval_rows)
    ) for n in MODELS}
    common=(checkpoint["training_source_wall_ns"]+
            checkpoint["training_actor_wall_ns"]+
            recall["interference_source_actor_wall_ns"]+
            recall["before"]["source_actor_wall_ns"]+
            recall["after"]["source_actor_wall_ns"]+
            sum(r["source_actor_wall_ns"] for r in eval_rows))
    best=min(costs["symbolic8"],costs["recurrent45"])
    ratio=(common+costs["candidate"])/max(1,common+best)
    checks={
        "novel_component_held_pooled_brier_le_0_04":
            score["candidate"]<=.04,
        "novel_component_all_4_laws_brier_le_0_08":
            all(x<=.08 for x in bylaw.values()),
        "candidate_vs_exact_law_memory_gain_ge_0_10":
            score["candidate"]<=score["st5_exact_key"]-.10,
        "candidate_vs_no_B_diagnostic_gain_ge_0_10":
            score["candidate"]<=score["no_b"]-.10,
        "candidate_vs_shuffle_and_erasure_negative_gain_ge_0_10":
            score["candidate"]<=min(score["shuffle"],score["erase"])-.10,
        "candidate_noninferior_to_strong_equal_hypothesis_control":
            score["candidate"]<=strong+.01,
        "different_operator_negative_Brier_ge_0_10":
            negative["pooled_probe_brier"]["candidate"]>=.10,
        "same_family_8_law_retained_chance_gain_ge_0_95":
            recall["candidate_retained_gain_fraction"]>=.95,
        "same_family_cold_recall_absolute_deterioration_le_0_02":
            recall["candidate_absolute_brier_change"]<=.02,
        "all_7_models_share_same_64_byte_hypothesis_evidence_capacity":
            checkpoint["model_capacity_receipts"]["candidate"][
                "learned_uint32_error_support_bytes"]==
            checkpoint["model_capacity_receipts"]["symbolic8"][
                "learned_uint32_error_support_bytes"]==64,
        "all_original_held_actions_true_preaction_and_cold":
            all(r["all_model_cold_restarts"]==len(MODELS)
                for r in eval_rows),
        "whole_source_actor_model_wall_ratio_le_1_5":
            ratio<=1.5
    }
    return {
        "frozen_checks":checks,
        "by_held_law_probe_brier":bylaw,
        "pooled_held_probe_brier":score,
        "different_rule_negative_probe_brier":
            negative["pooled_probe_brier"],
        "native_vs_strong_symbolic_absolute_gap":
            abs(score["candidate"]-strong),
        "native_unique_advantage_over_strong_symbolic":
            score["candidate"]<strong-1e-12,
        "same_family_retention":recall[
            "candidate_retained_gain_fraction"],
        "source_actor_and_training_charged_wall_ratio":ratio,
        "per_model_source_included_wall_ns":costs,
        "total_common_original_source_actor_wall_ns":common,
        "peak_shared_worker_rss_bytes":max(
            r["peak_shared_process_rss_bytes"] for r in eval_rows
        ),
        "isolated_per_model_rss":"UNVERIFIED",
        "full_final_G29":"UNVERIFIED_OR_FAILED",
        "development_disposition":(
            "COMPOSITIONAL_DEV_SIGNAL_NOT_SCIENTIFIC_PASS"
            if all(checks.values()) else "DEV_NO_GO"
        )
    }


def compare(training_path,result_path):
    guard()
    checkpoint,sha=load_checkpoint(training_path)
    # At this point the trained bytes and frozen original source are
    # already pinned. Evaluate no-fit genuine unfamiliar law combinations.
    held=test_family(checkpoint,HELD,HELDS,"held")
    negative=test_family(checkpoint,NEG,(205,),"negative")
    retained=retention(checkpoint)
    metrics=classify(held,negative,retained,checkpoint)
    report={
        "schema":DEV_SCHEMA,
        "evidence_class":"INHOUSE_SYNTHETIC_DEV_ONLY",
        "frozen_protocol_git_blob":PREREG_BLOB,
        "original_source_blob":SOURCE_BLOB,
        "native_model_blob":MODEL_BLOB,
        "strong_control_blob":CONTROLS_BLOB,
        "shared_training_sha256":sha,
        "held":held,"different_rule":negative,
        "cold_retention":retained,
        "metrics":metrics,
        "held_laws_read_once":list(HELD),
        "negative_rule_laws_read_once":list(NEG),
        "no_unfamiliar_law_fitting":True,
        "protected_scientific_first_use":False,
        "scientific_pass":False,
        "compositional_advantage_uniquely_native":
            metrics["native_unique_advantage_over_strong_symbolic"],
        "source_or_model_tuned_after_held":False,
        "development_disposition":metrics["development_disposition"]
    }
    result_path.write_text(canonical(report)+"\n",encoding="utf-8")
    print("ST6_HELD_NOVEL_COMBINATION_BRIER="+canonical(
        metrics["pooled_held_probe_brier"]))
    print("ST6_UNSEEN_MECHANISM_NEGATIVE_BRIER="+canonical(
        metrics["different_rule_negative_probe_brier"]))
    print("ST6_POST_EIGHT_LAWS_COLD_RETENTION="+str(
        metrics["same_family_retention"]))
    print("ST6_FROZEN_DEV_CHECKS="+canonical(metrics["frozen_checks"]))
    print("ST6_DEVELOPMENT_DISPOSITION="+metrics["development_disposition"])
    print("ST6_PROTECTED_FIRST_USE=NOT_RUN")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    subs=p.add_subparsers(dest="action",required=True)
    tr=subs.add_parser("train");tr.add_argument("--out",type=Path,required=True)
    ev=subs.add_parser("compare")
    ev.add_argument("--checkpoint",type=Path,required=True)
    ev.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.action=="train":
        train_once(args.out)
    else:
        compare(args.checkpoint,args.out)
