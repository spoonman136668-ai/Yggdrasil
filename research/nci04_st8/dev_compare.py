"""ST8 frozen in-house DEV evaluator for genuine substrate growth.

A single original public-only training checkpoint produced once on Linux
must be loaded byte-identically on Linux and Windows before ANY
unfamiliar-law or alternate-rule source. All seven model variants see
only current public preaction observation, announced action, and prior
genuine afteraction 8-bit public consequences. No private source
coefficients/law ID/trial/seed/future labels reach learner APIs.

Internal synthetic DEV only; no SCIENTIFIC_PASS or protected first use.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st8.private_world import PrivateCubicWorld,ACTIONS,TRIALS
from research.nci04_st8.source_audit import (
    audit,verify,PREREG_BLOB,TRAIN,SEEDS,HELD
)
from research.nci04_st8.native_growth import canonical
from research.nci04_st8.matched_controls import models,restored_models,restore_one
from research.nci04_st5.matched_controls import brier

WORLD_BLOB="39502f081e85ff0d3f7a5c22101a7bf3c1f3629a"
AUDIT_BLOB="b8bdfd1ca0106605485cb345ab0d96de10c19027"
NATIVE_BLOB="1ce8095fdb4e50f2685d51b507da99786ede580c"
CONTROLS_BLOB="d335b57f8da18052019dbc63dc6ef0385aa6650a"
TRAIN_SCHEMA="yggdrasil.nci04.st8.single-original-public-training.v1"
RESULT_SCHEMA="yggdrasil.nci04.st8.frozen-structural-growth-dev.v1"
NAMES=tuple(models())
HELD_SEEDS=tuple(range(201,209))
NEG=(43,47)
INTERFERENCE=(53,59,61,67,71,73,79,83)
MAX_TRAIN_FILE=3000000
PROCESS=psutil.Process()


def guard():
    frozen=verify()
    for path,git_blob in (
        ("research/nci04_st8/private_world.py",WORLD_BLOB),
        ("research/nci04_st8/source_audit.py",AUDIT_BLOB),
        ("research/nci04_st8/native_growth.py",NATIVE_BLOB),
        ("research/nci04_st8/matched_controls.py",CONTROLS_BLOB),
    ):
        found=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
        if found!=git_blob:
            raise ValueError("ST8_FROZEN_SOURCE_MODEL_CONTROL_GIT_DRIFT_"+path)
    return frozen


def learned_data(model):
    if hasattr(model,"basis"):
        return canonical([model.degree if hasattr(model,"degree") else 2,
                          model.basis])
    if hasattr(model,"rows"):
        return canonical([model.degree,model.rows])
    raise ValueError("ST8_UNKNOWN_FROZEN_MODEL_STORAGE")


def episode(law,seed,trial,cohort,phase,train,*,cold=False):
    if (phase not in ("train","held","negative","interference","recall") or
        type(train) is not bool or set(cohort)!=set(NAMES)):
        raise ValueError("ST8_EVALUATOR_INVALID_SOURCE_OR_COHORT")
    world=PrivateCubicWorld(law,seed,trial)
    for m in cohort.values():
        m.reset_episode()
    bytes_seen=bytearray()
    source_wall=0;actor_wall=0
    model_cost={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    score={}
    native_hashes=sha256()
    cold_count=0
    max_rss=PROCESS.memory_info().rss
    for step,action in enumerate(ACTIONS):
        t0=time.perf_counter_ns()
        public=world.public()
        actor_wall+=time.perf_counter_ns()-t0
        forecast={}
        for name,m in cohort.items():
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            forecast[name]=m.predict(public,action)
            model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
            model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
        t0=time.perf_counter_ns()
        after,target=world.step(action)
        source_wall+=time.perf_counter_ns()-t0
        if tuple(x^y for x,y in zip(public,after))!=target:
            raise ValueError("ST8_GENUINE_SOURCE_ACTION_NOT_PUBLIC")
        bytes_seen.extend(bytes((*public,action,*after,*target)))
        if step==4:
            score={n:brier(forecast[n],target) for n in NAMES}
        for name,m in tuple(cohort.items()):
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            result=m.observe(public,action,target,after,train=train)
            model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
            model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
            if result!=forecast[name]:
                raise ValueError("ST8_PREACTION_FUTURE_TARGET_LEAK_"+name)
        if cold and step==2:
            for name,m in tuple(cohort.items()):
                t0=time.perf_counter_ns();cpu=time.process_time_ns()
                snap=m.snapshot()
                copy=restore_one(name,snap)
                if copy.snapshot()!=snap:
                    raise ValueError("ST8_COLD_RESTORE_NONCANONICAL_"+name)
                cohort[name]=copy
                cold_count+=1
                model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
                model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
        t0=time.perf_counter_ns();cpu=time.process_time_ns()
        native_hashes.update(sha256(
            cohort["candidate"].snapshot().encode("utf-8")
        ).digest())
        model_cost["candidate"]["wall_ns"]+=time.perf_counter_ns()-t0
        model_cost["candidate"]["cpu_ns"]+=time.process_time_ns()-cpu
        max_rss=max(max_rss,PROCESS.memory_info().rss)
    return {
        "actual_original_source_actions":len(ACTIONS),
        "original_public_action_bytes_hex":bytes_seen.hex(),
        "original_public_action_sha256":sha256(bytes_seen).hexdigest(),
        "genuine_preaction_probe_Brier":score,
        "native_integer_state_sha256":native_hashes.hexdigest(),
        "model_cpu_wall_ns":model_cost,
        "source_wall_ns":source_wall,
        "actor_wall_ns":actor_wall,
        "all_model_true_cold_restores":cold_count,
        "shared_worker_max_rss_bytes":max_rss,
        "private_source_rule_or_future_seen_by_model":False,
        "scientific_first_use_protected":False,
    }


def train_once(out):
    guard()
    stage0=audit(out.with_name("st8-original-stage0.json"))
    if stage0["source_gate"]["disposition"]!=(
            "SOURCE_CUBIC_FALSIFIES_QUADRATIC_DEV_ONLY"):
        raise ValueError("ST8_SOURCE_GATE_NO_GO_REFUSE_MODEL")
    cohort=models()
    model_cost={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    source_wall=0;actor_wall=0;count=0
    receipts=[]
    started=time.perf_counter_ns()
    for law in TRAIN:
        h=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                row=episode(law,seed,trial,cohort,"train",True,
                            cold=(trial==0))
                h.update(bytes.fromhex(row["original_public_action_bytes_hex"]))
                count+=row["actual_original_source_actions"]
                source_wall+=row["source_wall_ns"]
                actor_wall+=row["actor_wall_ns"]
                for name in NAMES:
                    for m in ("wall_ns","cpu_ns"):
                        model_cost[name][m]+=row["model_cpu_wall_ns"][name][m]
        stage=next(v for v in stage0["real_source_law_action_history_records"]
                   if v["evaluator_law_only"]==law)
        if stage["source_real_public_action_sha256"]!=h.hexdigest():
            raise ValueError("ST8_TRAINED_SOURCE_ACTIONS_DIFFER_FROM_STAGE0")
        receipts.append({
            "law_evaluator_only":law,
            "original_source_action_sha256":h.hexdigest()
        })
    if count!=7680:
        raise ValueError("ST8_TRAINING_ACTUAL_ACTION_COVERAGE")
    candidate=cohort["candidate"]
    controls=cohort["adaptive_conventional"]
    data={
        "schema":TRAIN_SCHEMA,
        "protocol_blob":PREREG_BLOB,"source_blob":WORLD_BLOB,
        "native_blob":NATIVE_BLOB,"controls_blob":CONTROLS_BLOB,
        "training_laws":list(TRAIN),"training_seeds":list(SEEDS),
        "training_episodes":1536,"original_training_actions":count,
        "source_receipts":receipts,
        "states":{n:cohort[n].snapshot() for n in NAMES},
        "capacity":{n:cohort[n].accounting() for n in NAMES},
        "model_training_cpu_wall_ns":model_cost,
        "source_training_wall_ns":source_wall,
        "actor_training_wall_ns":actor_wall,
        "whole_worker_training_wall_ns":time.perf_counter_ns()-started,
        "candidate_actual_original_genuine_contradictions":
            candidate.contradictions,
        "candidate_growth_on_original_step":candidate.first_growth_on_update,
        "candidate_post_growth_conflicts":candidate.post_growth_conflicts,
        "candidate_train_public_feature_rank":candidate.rank,
        "candidate_growth_events":candidate.growths,
        "independent_adaptive_full_cubic_rank":controls.rank,
        "held_development_unopened":True,
        "alternate_rule_negative_unopened":True,
        "protected_first_use":False,
    }
    out.write_text(canonical(data)+"\n",encoding="utf-8")
    print("ST8_TRAIN_ORIGINAL_ACTIONS="+str(count))
    print("ST8_NATIVE_ACTUAL_CONTRADICTIONS="+str(candidate.contradictions))
    print("ST8_NATIVE_TRIGGERS="+str(candidate.growths))
    print("ST8_NATIVE_GROWN_FEATURE_RANK="+str(candidate.rank))
    print("ST8_CONVENTIONAL_ADAPTIVE_RANK="+str(controls.rank))
    print("ST8_SHARED_TRAIN_CHECKPOINT_SHA256="+sha256(out.read_bytes()).hexdigest())
    print("ST8_HELD_AND_PROTECTED_FIRST_USE_UNOPENED=PASS")
    return data


def load_training(path):
    raw=path.read_bytes()
    if len(raw)>MAX_TRAIN_FILE:
        raise ValueError("ST8_TRAINING_CHECKPOINT_TOO_LARGE")
    x=json.loads(raw)
    if (x.get("schema")!=TRAIN_SCHEMA or
        x.get("protocol_blob")!=PREREG_BLOB or
        x.get("source_blob")!=WORLD_BLOB or
        x.get("native_blob")!=NATIVE_BLOB or
        x.get("controls_blob")!=CONTROLS_BLOB or
        x.get("training_laws")!=list(TRAIN) or
        x.get("training_seeds")!=list(SEEDS) or
        x.get("training_episodes")!=1536 or
        x.get("original_training_actions")!=7680 or
        x.get("held_development_unopened") is not True or
        x.get("alternate_rule_negative_unopened") is not True or
        x.get("protected_first_use") is not False or
        raw.decode("utf-8")!=canonical(x)+"\n"):
        raise ValueError("ST8_TRAINED_EXACT_SOURCE_CUSTODY_INVALID")
    restored_models(x["states"])
    return x,sha256(raw).hexdigest()


def no_fit_set(training,laws,seeds,phase):
    cohort=restored_models(training["states"])
    frozen={n:learned_data(m) for n,m in cohort.items()}
    count=0;rows=[]
    for law in laws:
        for seed in seeds:
            sha=sha256();native_sha=sha256()
            scores={n:0. for n in NAMES}
            model_cost={n:{"cpu_ns":0,"wall_ns":0} for n in NAMES}
            source_actor=0;cold_count=0;max_rss=PROCESS.memory_info().rss
            for trial in range(TRIALS):
                row=episode(law,seed,trial,cohort,phase,False,
                            cold=(trial==0))
                count+=row["actual_original_source_actions"]
                sha.update(bytes.fromhex(row["original_public_action_bytes_hex"]))
                native_sha.update(bytes.fromhex(row["native_integer_state_sha256"]))
                for n in NAMES:
                    scores[n]+=row["genuine_preaction_probe_Brier"][n]
                    for key in ("cpu_ns","wall_ns"):
                        model_cost[n][key]+=row["model_cpu_wall_ns"][n][key]
                source_actor+=row["source_wall_ns"]+row["actor_wall_ns"]
                cold_count+=row["all_model_true_cold_restores"]
                max_rss=max(max_rss,row["shared_worker_max_rss_bytes"])
            rows.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "original_source_actions":TRIALS*5,
                "original_public_action_sha256":sha.hexdigest(),
                "preaction_probe_Brier":{
                    n:scores[n]/TRIALS for n in NAMES
                },
                "native_cold_integer_state_sha256":native_sha.hexdigest(),
                "model_cpu_wall_ns":model_cost,
                "source_actor_wall_ns":source_actor,
                "all_model_cold_restores":cold_count,
                "shared_peak_rss_bytes":max_rss,
                "private_fields_seen_by_model":False
            })
    if count!=len(laws)*len(seeds)*TRIALS*5:
        raise ValueError("ST8_HELD_OR_NEGATIVE_SOURCE_COVERAGE_DRIFT")
    for n,m in cohort.items():
        if n!="erase" and learned_data(m)!=frozen[n]:
            raise ValueError("ST8_UNFAMILIAR_SOURCE_RETRAINED_MODEL_"+n)
    return {
        "phase":phase,"actual_original_source_actions":count,
        "receipts":rows,
        "pooled_Brier":{
            n:sum(v["preaction_probe_Brier"][n] for v in rows)/len(rows)
            for n in NAMES
        },
        "model_updated_on_unfamiliar_source":False
    }


def recall_original(cohort):
    frozen={n:learned_data(m) for n,m in cohort.items()}
    rows=[episode(3,100,i,cohort,"recall",False,cold=(i==0))
          for i in range(TRIALS)]
    for n,m in cohort.items():
        if n!="erase" and frozen[n]!=learned_data(m):
            raise ValueError("ST8_ORIGINAL_RECALL_RETRAINING_"+n)
    return {
        "original_law_evaluator_only":3,"original_steps":80,
        "original_source_sha256":sha256(b"".join(
            bytes.fromhex(z["original_public_action_bytes_hex"]) for z in rows
        )).hexdigest(),
        "native_integer_trace_sha256":sha256(b"".join(
            bytes.fromhex(z["native_integer_state_sha256"]) for z in rows
        )).hexdigest(),
        "preaction_probe_Brier":{
            n:sum(z["genuine_preaction_probe_Brier"][n] for z in rows)/TRIALS
            for n in NAMES
        },
        "model_cpu_wall_ns":{
            n:{k:sum(z["model_cpu_wall_ns"][n][k] for z in rows)
               for k in ("wall_ns","cpu_ns")} for n in NAMES
        },
        "source_actor_wall_ns":sum(z["source_wall_ns"]+z["actor_wall_ns"]
                                  for z in rows),
        "cold_restores":sum(z["all_model_true_cold_restores"] for z in rows),
        "original_rehearsal_or_fit":False
    }


def retention(training):
    cohort=restored_models(training["states"])
    before=recall_original(cohort)
    summaries=[];num=0
    cost={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    common=0
    for law in INTERFERENCE:
        h=sha256()
        for trial in range(TRIALS):
            x=episode(law,111,trial,cohort,"interference",True,
                      cold=(trial==0))
            num+=x["actual_original_source_actions"]
            h.update(bytes.fromhex(x["original_public_action_bytes_hex"]))
            common+=x["source_wall_ns"]+x["actor_wall_ns"]
            for n in NAMES:
                for k in ("wall_ns","cpu_ns"):
                    cost[n][k]+=x["model_cpu_wall_ns"][n][k]
        summaries.append({
            "law_evaluator_only":law,
            "real_action_sha256":h.hexdigest(),
            "original_steps":80
        })
    after=recall_original(cohort)
    pre=before["preaction_probe_Brier"]["candidate"]
    post=after["preaction_probe_Brier"]["candidate"]
    gain=max(0.,.25-pre)
    retained=max(0.,1.-max(0.,post-pre)/gain) if gain else 0.
    return {
        "before":before,"after":after,
        "eight_interference_law_original_receipts":summaries,
        "real_interference_actions":num,
        "candidate_retained_gain_fraction":retained,
        "candidate_cold_Brier_increase":post-pre,
        "interference_model_cpu_wall_ns":cost,
        "interference_source_actor_wall_ns":common,
        "retrained_during_original_recall":False
    }


def classify(held,negative,recalled,training):
    if (held["actual_original_source_actions"]!=2560 or
        len(held["receipts"])!=32 or
        negative["actual_original_source_actions"]!=160 or
        len(negative["receipts"])!=2 or
        recalled["real_interference_actions"]!=640):
        raise ValueError("ST8_FROZEN_EXPERIMENT_SOURCE_INCOMPLETE")
    h=held["pooled_Brier"]
    bylaw={
        str(law):sum(row["preaction_probe_Brier"]["candidate"]
                     for row in held["receipts"] if row["law_evaluator_only"]==law)/8
        for law in HELD
    }
    evalrows=held["receipts"]+negative["receipts"]
    costs={n:(
        training["model_training_cpu_wall_ns"][n]["wall_ns"]+
        recalled["interference_model_cpu_wall_ns"][n]["wall_ns"]+
        recalled["before"]["model_cpu_wall_ns"][n]["wall_ns"]+
        recalled["after"]["model_cpu_wall_ns"][n]["wall_ns"]+
        sum(row["model_cpu_wall_ns"][n]["wall_ns"] for row in evalrows)
    ) for n in NAMES}
    common=(training["source_training_wall_ns"]+
            training["actor_training_wall_ns"]+
            recalled["interference_source_actor_wall_ns"]+
            recalled["before"]["source_actor_wall_ns"]+
            recalled["after"]["source_actor_wall_ns"]+
            sum(row["source_actor_wall_ns"] for row in evalrows))
    ratio=(common+costs["candidate"])/max(
        1,common+min(costs["full_cubic"],costs["adaptive_conventional"])
    )
    checks={
        "genuine_original_quadratic_contradiction_triggered_growth":
            training["candidate_actual_original_genuine_contradictions"]>=1 and
            training["candidate_growth_events"]==1 and
            training["candidate_growth_on_original_step"] is not None,
        "candidate_full_cubic_rank92_no_postgrowth_conflicts":
            training["candidate_train_public_feature_rank"]==92 and
            training["candidate_post_growth_conflicts"]==0,
        "held_new_worlds_pooled_preaction_Brier_le_0_02":
            h["candidate"]<=.02,
        "each_held_new_world_law_Brier_le_0_04":
            all(x<=.04 for x in bylaw.values()),
        "candidate_beats_fixed_ST7_quadratic_by_0_10":
            h["candidate"]<=h["st7_quadratic"]-.10,
        "candidate_beats_no_growth_by_0_10":
            h["candidate"]<=h["no_growth"]-.10,
        "candidate_beats_no_replay_by_0_10":
            h["candidate"]<=h["no_replay"]-.10,
        "candidate_beats_episode_erasure_by_0_10":
            h["candidate"]<=h["erase"]-.10,
        "candidate_noninferior_to_fully_fitted_full_cubic_GF2_by_0_01":
            h["candidate"]<=h["full_cubic"]+.01,
        "candidate_noninferior_to_exact_adaptive_conventional_by_0_01":
            h["candidate"]<=h["adaptive_conventional"]+.01,
        "native_and_adaptive_max_augmented_GF2_budget_equal":
            training["capacity"]["candidate"]["learned_GF2_augmented_bits_max"]==
            training["capacity"]["adaptive_conventional"][
                "learned_augmented_bits_max"]==92*100,
        "new_rule_negative_Brier_ge_0_10":
            negative["pooled_Brier"]["candidate"]>=.10,
        "cold_same_rule_retention_gain_ge_0_95":
            recalled["candidate_retained_gain_fraction"]>=.95,
        "cold_original_law_absolute_Brier_increase_le_0_02":
            recalled["candidate_cold_Brier_increase"]<=.02,
        "all_seven_cold_restored_on_each_held_and_negative_lawseed":
            all(x["all_model_cold_restores"]==len(NAMES)
                for x in evalrows),
        "measured_total_original_process_ratio_le_1_5":
            ratio<=1.5
    }
    return {
        "frozen_checks":checks,
        "new_world_pooled_preaction_Brier":h,
        "four_held_world_per_law_Brier":bylaw,
        "different_rule_negative_preaction_Brier":negative["pooled_Brier"],
        "exact_native_vs_adaptive_conventional_gap":
            abs(h["candidate"]-h["adaptive_conventional"]),
        "native_unique_performance_advantage_over_adaptive":
            h["candidate"]<h["adaptive_conventional"]-1e-12,
        "chance_adjusted_retention":recalled["candidate_retained_gain_fraction"],
        "source_actor_training_eval_wall_ratio":ratio,
        "full_original_model_wall_cost_ns":costs,
        "common_original_source_actor_wall_ns":common,
        "max_shared_rss_bytes":max(
            x["shared_peak_rss_bytes"] for x in evalrows
        ),
        "isolated_model_rss":"UNVERIFIED",
        "full_final_G29":"UNVERIFIED",
        "development_disposition":(
            "STRUCTURAL_GROWTH_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE"
            if all(checks.values()) else "DEV_NO_GO"
        )
    }


def compare(checkpoint,output):
    guard()
    t,train_sha=load_training(checkpoint)
    held=no_fit_set(t,HELD,HELD_SEEDS,"held")
    negative=no_fit_set(t,NEG,(205,),"negative")
    cold=retention(t)
    result=classify(held,negative,cold,t)
    report={
        "schema":RESULT_SCHEMA,
        "class":"FROZEN_INHOUSE_SYNTHETIC_DEVELOPMENT_ONLY",
        "frozen_protocol_blob":PREREG_BLOB,
        "private_source_blob":WORLD_BLOB,
        "native_model_blob":NATIVE_BLOB,
        "conventional_controls_blob":CONTROLS_BLOB,
        "shared_training_artifact_sha256":train_sha,
        "held":held,"different_rule":negative,"cold_retention":cold,
        "metrics":result,
        "held_laws_opened_once":list(HELD),
        "held_seeds_opened_once":list(HELD_SEEDS),
        "different_rule_laws_opened_once":list(NEG),
        "no_model_fitted_on_held_or_negative":True,
        "private_rule_or_law_id_seen_by_models":False,
        "scientific_first_use_protected":False,
        "independent_scientific_pass":False,
        "source_and_candidate_unmodified_after_held":True,
        "development_disposition":result["development_disposition"]
    }
    output.write_text(canonical(report)+"\n",encoding="utf-8")
    print("ST8_HELD_BRIER="+canonical(
        result["new_world_pooled_preaction_Brier"]))
    print("ST8_DIFFERENT_RULE_NEGATIVE_BRIER="+canonical(
        result["different_rule_negative_preaction_Brier"]))
    print("ST8_COLD_RETENTION="+str(result["chance_adjusted_retention"]))
    print("ST8_WHOLE_PROCESS_COST_RATIO="+str(
        result["source_actor_training_eval_wall_ratio"]))
    print("ST8_FROZEN_DEV_PREDICATES="+canonical(result["frozen_checks"]))
    print("ST8_DEV_DISPOSITION="+result["development_disposition"])
    print("ST8_PROTECTED_FIRST_USE=NOT_RUN")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="mode",required=True)
    a=sub.add_parser("train");a.add_argument("--out",type=Path,required=True)
    b=sub.add_parser("compare");b.add_argument("--checkpoint",type=Path,required=True)
    b.add_argument("--out",type=Path,required=True)
    z=p.parse_args()
    if z.mode=="train":
        train_once(z.out)
    else:
        compare(z.checkpoint,z.out)
