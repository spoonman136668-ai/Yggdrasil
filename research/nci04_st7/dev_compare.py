"""ST7 frozen public-only original source training and rule-induction DEV.

All model methods take ONLY 8 public bits, current announced action and
past actual public consequences. Evaluator alone handles private world ID.
Same ONE Linux-trained exact artifact restored for both OS.
Frozen stage0, model/control, protocol Git blobs checked BEFORE held first
use. No independent science or autonomous-loop/accepted-ref mutation.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st7.private_world import (
    PrivateQuadraticWorld,ACTIONS,TRIALS
)
from research.nci04_st7.source_audit import (
    audit,verify_prereg,PREREG_BLOB,TRAIN,SEEDS,HELD
)
from research.nci04_st7.native_induction import (
    NativeInductive8,canonical
)
from research.nci04_st7.matched_controls import (
    models,restored_models,restore_one,brier
)

WORLD_BLOB="ac39c7a5a7a0c3119e5d91872017deee84ecfef4"
AUDIT_BLOB="cf75f25b1640edbf4574940b0a04ab3a2676ecc5"
MODEL_BLOB="TO_PIN_ST7_NATIVE"
CONTROLS_BLOB="TO_PIN_ST7_CONTROLS"
TRAIN_SCHEMA="yggdrasil.nci04.st7.once-trained-original-source.v1"
RESULT_SCHEMA="yggdrasil.nci04.st7.unknown-quadratic-original-dev.v1"
MODEL_NAMES=tuple(models())
HELD_SEEDS=tuple(range(201,209))
INTERFERENCE=(53,59,61,67,71,73,79,83)
NEGATIVE=(43,47)
MAX_CHECKPOINT=2500000
PROCESS=psutil.Process()


def exact_guard():
    p=verify_prereg()
    for path,sha in (
        ("research/nci04_st7/private_world.py",WORLD_BLOB),
        ("research/nci04_st7/source_audit.py",AUDIT_BLOB),
        ("research/nci04_st7/native_induction.py",MODEL_BLOB),
        ("research/nci04_st7/matched_controls.py",CONTROLS_BLOB),
    ):
        if sha.startswith("TO_PIN"):
            raise ValueError("ST7_MODEL_OR_CONTROLS_NOT_FROZEN")
        got=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
        if got!=sha:
            raise ValueError("ST7_PREHELD_GIT_BLOB_DRIFT_"+path)
    return p


def fixed_evidence(model):
    if hasattr(model,"basis"):
        return canonical(model.basis)
    if hasattr(model,"rows"):
        return canonical(model.rows)
    if hasattr(model,"weights"):
        return canonical(model.weights)
    if hasattr(model,"mismatches"):
        return canonical([model.mismatches,model.support])
    raise ValueError("ST7_UNKNOWN_CONTROL_EVIDENCE")


def run_episode(law,seed,trial,cohort,phase,training,*,cold=False):
    if (phase not in ("train","held","negative","interference","recall") or
        type(training) is not bool or set(cohort)!=set(MODEL_NAMES)):
        raise ValueError("ST7_EVALUATOR_ILLEGAL_SOURCE_OR_MODEL_COHORT")
    source=PrivateQuadraticWorld(law,seed,trial)
    for m in cohort.values():m.reset_episode()
    events=bytearray()
    times={n:{"wall_ns":0,"cpu_ns":0} for n in MODEL_NAMES}
    source_wall=0;actor_wall=0;source_cpu=0
    delayed={}
    cold_restarts=0
    peak_rss=PROCESS.memory_info().rss
    state_trace=sha256()
    for step in range(5):
        t0=time.perf_counter_ns()
        action=ACTIONS[step]
        actor_wall+=time.perf_counter_ns()-t0
        public=source.public()
        predicted={}
        for name,m in cohort.items():
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            predicted[name]=m.predict(public,action)
            times[name]["wall_ns"]+=time.perf_counter_ns()-t0
            times[name]["cpu_ns"]+=time.process_time_ns()-cpu
        t0=time.perf_counter_ns();cpu=time.process_time_ns()
        after,target=source.step(action)
        source_wall+=time.perf_counter_ns()-t0
        source_cpu+=time.process_time_ns()-cpu
        if tuple(a^b for a,b in zip(public,after))!=target:
            raise ValueError("ST7_ORIGINAL_AFTERACTION_DELTA_DRIFT")
        events.extend(bytes((*public,action,*after,*target)))
        if step==4:
            for name in MODEL_NAMES:
                delayed[name]=brier(predicted[name],target)
        for name,m in tuple(cohort.items()):
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            returned=m.observe(public,action,target,after,train=training)
            times[name]["wall_ns"]+=time.perf_counter_ns()-t0
            times[name]["cpu_ns"]+=time.process_time_ns()-cpu
            if returned!=predicted[name]:
                raise ValueError("ST7_PREDICTION_AFTERACTION_LABEL_LEAK_"+name)
        if cold and step==2:
            for name,m in tuple(cohort.items()):
                t0=time.perf_counter_ns();cpu=time.process_time_ns()
                state=m.snapshot()
                restored=restore_one(name,state)
                if restored.snapshot()!=state:
                    raise ValueError("ST7_ORIGINAL_COLD_CHECKPOINT_INEXACT_"+name)
                cohort[name]=restored
                cold_restarts+=1
                times[name]["wall_ns"]+=time.perf_counter_ns()-t0
                times[name]["cpu_ns"]+=time.process_time_ns()-cpu
        # Charge exact candidate integer-state hash to candidate wall time.
        t0=time.perf_counter_ns();cpu=time.process_time_ns()
        state_trace.update(sha256(cohort["candidate"].snapshot().encode(
            "utf-8")).digest())
        times["candidate"]["wall_ns"]+=time.perf_counter_ns()-t0
        times["candidate"]["cpu_ns"]+=time.process_time_ns()-cpu
        peak_rss=max(peak_rss,PROCESS.memory_info().rss)
    return {
        "original_actions":5,
        "authentic_source_bytes_hex":events.hex(),
        "authentic_source_sha256":sha256(events).hexdigest(),
        "preaction_probe_brier":delayed,
        "native_integer_state_sha256":state_trace.hexdigest(),
        "model_cpu_wall_ns":times,
        "source_wall_ns":source_wall,"source_cpu_ns":source_cpu,
        "blind_actor_wall_ns":actor_wall,
        "all_model_cold_restarts":cold_restarts,
        "shared_worker_peak_rss_bytes":peak_rss,
        "private_law_coefficient_or_future_given_to_model":False,
        "protected_scientific_first_use":False
    }


def train_once(output):
    exact_guard()
    stage0=audit(output.with_name("st7-source-stage0.json"))
    if stage0["source_gate"]["decision"]!=(
            "SOURCE_UNKNOWN_QUADRATIC_IDENTIFIABLE_DEV_ONLY"):
        raise ValueError("ST7_REFUSE_TRAIN_INVALID_SOURCE_IDENTIFIABILITY")
    start=time.perf_counter_ns()
    cohort=models()
    receipts=[]
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in MODEL_NAMES}
    source_wall=0;actor_wall=0;steps=0
    for law in TRAIN:
        source_digest=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                row=run_episode(law,seed,trial,cohort,"train",True,
                                cold=(trial==0))
                source_digest.update(bytes.fromhex(
                    row["authentic_source_bytes_hex"]))
                steps+=row["original_actions"]
                source_wall+=row["source_wall_ns"]
                actor_wall+=row["blind_actor_wall_ns"]
                for n in MODEL_NAMES:
                    for metric in ("wall_ns","cpu_ns"):
                        costs[n][metric]+=row["model_cpu_wall_ns"][n][metric]
        expected=next(v for v in stage0[
            "per_law_actual_original_source_receipts"]
            if v["evaluator_only_law"]==law)
        if source_digest.hexdigest()!=expected["actual_action_history_sha256"]:
            raise ValueError("ST7_LEARNER_ORIGINAL_ACTIONS_NOT_STAGE0_SHA")
        receipts.append({
            "training_law_evaluator_only":law,
            "actual_original_source_sha256":source_digest.hexdigest()
        })
    if steps!=7680:
        raise ValueError("ST7_ORIGINAL_TRAIN_SOURCE_STEP_COUNT")
    result={
        "schema":TRAIN_SCHEMA,
        "frozen_prereg_git_blob":PREREG_BLOB,
        "original_source_git_blob":WORLD_BLOB,
        "native_model_git_blob":MODEL_BLOB,
        "strong_controls_git_blob":CONTROLS_BLOB,
        "training_laws":list(TRAIN),
        "training_seeds":list(SEEDS),
        "original_training_episodes":1536,
        "original_training_actions":steps,
        "actual_training_source_receipts":receipts,
        "trained_model_states":{
            name:cohort[name].snapshot() for name in MODEL_NAMES
        },
        "capacity":{
            name:cohort[name].accounting() for name in MODEL_NAMES
        },
        "model_training_cpu_wall_ns":costs,
        "source_training_wall_ns":source_wall,
        "actor_training_wall_ns":actor_wall,
        "worker_training_wall_ns":time.perf_counter_ns()-start,
        "held_new_rules_unopened":True,
        "negative_new_mechanism_unopened":True,
        "protected_scientific_first_use":False
    }
    output.write_text(canonical(result)+"\n",encoding="utf-8")
    print("ST7_COMMON_TRAIN_SOURCE_ACTIONS="+str(steps))
    print("ST7_NATIVE_LEARNED_QUADRATIC_RANK="+str(cohort["candidate"].rank))
    print("ST7_NATIVE_REAL_SOURCE_CONTRADICTIONS="+str(cohort["candidate"].conflicts))
    print("ST7_CONVENTIONAL_LEARNED_GAUSSIAN_RANK="+str(cohort["gf2_conventional"].rank))
    print("ST7_ONCE_TRAINED_CHECKPOINT_SHA256="+sha256(output.read_bytes()).hexdigest())
    print("ST7_TRAIN_NO_HELD_OR_PROTECTED_FIRST_USE=PASS")
    return result


def load_checkpoint(path):
    raw=path.read_bytes()
    if len(raw)>MAX_CHECKPOINT:
        raise ValueError("ST7_ONCE_TRAINED_CHECKPOINT_OVERSIZED")
    c=json.loads(raw)
    if (c.get("schema")!=TRAIN_SCHEMA or
        c.get("frozen_prereg_git_blob")!=PREREG_BLOB or
        c.get("original_source_git_blob")!=WORLD_BLOB or
        c.get("native_model_git_blob")!=MODEL_BLOB or
        c.get("strong_controls_git_blob")!=CONTROLS_BLOB or
        c.get("training_laws")!=list(TRAIN) or
        c.get("training_seeds")!=list(SEEDS) or
        c.get("original_training_episodes")!=1536 or
        c.get("original_training_actions")!=7680 or
        c.get("held_new_rules_unopened") is not True or
        c.get("negative_new_mechanism_unopened") is not True or
        c.get("protected_scientific_first_use") is not False or
        raw.decode("utf-8")!=canonical(c)+"\n"):
        raise ValueError("ST7_ONCE_TRAINED_CUSTODY_MISMATCH")
    restored_models(c["trained_model_states"])
    return c,sha256(raw).hexdigest()


def no_learn_family(checkpoint,laws,seeds,phase):
    cohort=restored_models(checkpoint["trained_model_states"])
    baseline={n:fixed_evidence(m) for n,m in cohort.items()}
    count=0;rows=[]
    for law in laws:
        for seed in seeds:
            source_history=sha256()
            scores={n:0. for n in MODEL_NAMES}
            costs={n:{"wall_ns":0,"cpu_ns":0} for n in MODEL_NAMES}
            common=0;peak_rss=PROCESS.memory_info().rss;cold_restarts=0
            state_sha=sha256()
            for trial in range(TRIALS):
                data=run_episode(law,seed,trial,cohort,phase,False,
                                 cold=(trial==0))
                source_history.update(bytes.fromhex(data[
                    "authentic_source_bytes_hex"]))
                count+=data["original_actions"]
                for n in MODEL_NAMES:
                    scores[n]+=data["preaction_probe_brier"][n]
                    for part in ("wall_ns","cpu_ns"):
                        costs[n][part]+=data["model_cpu_wall_ns"][n][part]
                common+=data["source_wall_ns"]+data["blind_actor_wall_ns"]
                peak_rss=max(peak_rss,data["shared_worker_peak_rss_bytes"])
                cold_restarts+=data["all_model_cold_restarts"]
                state_sha.update(bytes.fromhex(data[
                    "native_integer_state_sha256"]))
            rows.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "original_source_actions":TRIALS*5,
                "original_action_history_sha256":source_history.hexdigest(),
                "probe_brier":{
                    n:scores[n]/TRIALS for n in MODEL_NAMES
                },
                "native_integer_state_trace_sha256":state_sha.hexdigest(),
                "model_cpu_wall_ns":costs,
                "source_actor_wall_ns":common,
                "shared_peak_rss_bytes":peak_rss,
                "all_model_cold_restarts":cold_restarts,
                "private_source_fields_given_to_model":False
            })
    for name,m in cohort.items():
        if name!="erase" and fixed_evidence(m)!=baseline[name]:
            raise ValueError("ST7_UNFAMILIAR_SOURCE_CAUSED_FITTING_"+name)
    if count!=len(laws)*len(seeds)*TRIALS*5:
        raise ValueError("ST7_UNFAMILIAR_COHORT_INCOMPLETE")
    return {
        "phase":phase,
        "actual_original_source_actions":count,
        "source_receipts":rows,
        "pooled_probe_brier":{
            n:sum(row["probe_brier"][n] for row in rows)/len(rows)
            for n in MODEL_NAMES
        },
        "model_fitted_on_unfamiliar_source":False
    }


def original_recall(cohort):
    baseline={n:fixed_evidence(m) for n,m in cohort.items()}
    rows=[run_episode(3,100,trial,cohort,"recall",False,
                      cold=(trial==0))
          for trial in range(TRIALS)]
    for n,m in cohort.items():
        if n!="erase" and fixed_evidence(m)!=baseline[n]:
            raise ValueError("ST7_ORIGINAL_COLD_RECALL_FITTED_"+n)
    return {
        "original_law_evaluator_only":3,
        "actual_original_action_steps":80,
        "source_sha256":sha256(b"".join(
            bytes.fromhex(r["authentic_source_bytes_hex"]) for r in rows
        )).hexdigest(),
        "probe_brier":{
            n:sum(r["preaction_probe_brier"][n] for r in rows)/TRIALS
            for n in MODEL_NAMES
        },
        "native_cold_state_trace_sha256":sha256(b"".join(
            bytes.fromhex(r["native_integer_state_sha256"]) for r in rows
        )).hexdigest(),
        "all_cold_model_restores":sum(
            r["all_model_cold_restarts"] for r in rows
        ),
        "model_cost":{
            n:{
                part:sum(r["model_cpu_wall_ns"][n][part] for r in rows)
                for part in ("wall_ns","cpu_ns")
            } for n in MODEL_NAMES
        },
        "source_actor_wall_ns":sum(r["source_wall_ns"]+
                                  r["blind_actor_wall_ns"] for r in rows),
        "model_retrained_original_source":False
    }


def cold_retention(checkpoint):
    cohort=restored_models(checkpoint["trained_model_states"])
    before=original_recall(cohort)
    interfered=0;original_traces=[]
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in MODEL_NAMES}
    common=0
    for law in INTERFERENCE:
        sha=sha256()
        for trial in range(TRIALS):
            r=run_episode(law,111,trial,cohort,"interference",True,
                          cold=(trial==0))
            sha.update(bytes.fromhex(r["authentic_source_bytes_hex"]))
            interfered+=r["original_actions"]
            common+=r["source_wall_ns"]+r["blind_actor_wall_ns"]
            for n in MODEL_NAMES:
                for part in ("wall_ns","cpu_ns"):
                    costs[n][part]+=r["model_cpu_wall_ns"][n][part]
        original_traces.append({
            "interference_law_evaluator_only":law,
            "actual_original_source_sha256":sha.hexdigest()
        })
    after=original_recall(cohort)
    before_brier=before["probe_brier"]["candidate"]
    after_brier=after["probe_brier"]["candidate"]
    gain=max(0.,.25-before_brier)
    retained=max(0.,1.-max(0.,after_brier-before_brier)/gain) if gain>0 else 0.
    return {
        "original_before":before,"original_after":after,
        "eight_distinct_same_rule_interference_receipts":original_traces,
        "interference_original_source_actions":interfered,
        "candidate_chance_adjusted_retention":retained,
        "original_probe_brier_absolute_deterioration":
            after_brier-before_brier,
        "original_rehearsal_during_recall":False,
        "interference_model_cost":costs,
        "interference_source_actor_wall_ns":common,
        "protected_scientific_first_use":False
    }


def classify(held,negative,retention,checkpoint):
    if (held["actual_original_source_actions"]!=2560 or
        len(held["source_receipts"])!=32 or
        negative["actual_original_source_actions"]!=160 or
        len(negative["source_receipts"])!=2 or
        retention["interference_original_source_actions"]!=640):
        raise ValueError("ST7_FROZEN_ORIGINAL_SOURCE_COHORT_MISSING")
    h=held["pooled_probe_brier"]
    nov_laws={
        str(law):sum(row["probe_brier"]["candidate"]
                     for row in held["source_receipts"]
                     if row["law_evaluator_only"]==law)/8
        for law in HELD
    }
    evalrows=held["source_receipts"]+negative["source_receipts"]
    charges={n:(
        checkpoint["model_training_cpu_wall_ns"][n]["wall_ns"]+
        retention["interference_model_cost"][n]["wall_ns"]+
        retention["original_before"]["model_cost"][n]["wall_ns"]+
        retention["original_after"]["model_cost"][n]["wall_ns"]+
        sum(row["model_cpu_wall_ns"][n]["wall_ns"] for row in evalrows)
    ) for n in MODEL_NAMES}
    common=(checkpoint["source_training_wall_ns"]+
            checkpoint["actor_training_wall_ns"]+
            retention["interference_source_actor_wall_ns"]+
            retention["original_before"]["source_actor_wall_ns"]+
            retention["original_after"]["source_actor_wall_ns"]+
            sum(row["source_actor_wall_ns"] for row in evalrows))
    best=min(charges["gf2_conventional"],charges["logistic36"])
    ratio=(common+charges["candidate"])/max(1,common+best)
    checks={
        "held_pooled_new_world_Brier_le_0_02":
            h["candidate"]<=.02,
        "all_4_held_laws_Brier_le_0_04":
            all(v<=.04 for v in nov_laws.values()),
        "causal_quadratic_vs_linear_gain_ge_0_10":
            h["candidate"]<=h["linear_only"]-.10,
        "causal_quadratic_vs_no_B_gain_ge_0_10":
            h["candidate"]<=h["no_b"]-.10,
        "causal_quadratic_vs_erase_gain_ge_0_10":
            h["candidate"]<=h["erase"]-.10,
        "causal_quadratic_vs_fixed_ST6_menu_gain_ge_0_10":
            h["candidate"]<=h["st6_menu"]-.10,
        "native_noninferior_to_strong_fitted_GF2_within_0_01":
            h["candidate"]<=h["gf2_conventional"]+.01,
        "unknown_different_rule_negative_Brier_ge_0_10":
            negative["pooled_probe_brier"]["candidate"]>=.10,
        "eight_interfering_laws_retained_chance_gain_ge_0_95":
            retention["candidate_chance_adjusted_retention"]>=.95,
        "original_cold_absolute_deterioration_le_0_02":
            retention["original_probe_brier_absolute_deterioration"]<=.02,
        "native_and_symbolic_36x44bit_evidence_capacity_matched":
            checkpoint["capacity"]["candidate"]["learned_bit_budget"]==
            checkpoint["capacity"]["gf2_conventional"]["learned_bit_budget"]==
            36*44,
        "all_actual_held_negative_models_cold_restore":
            all(row["all_model_cold_restarts"]==len(MODEL_NAMES)
                for row in evalrows),
        "charged_whole_process_wall_ratio_le_1_5":
            ratio<=1.5,
    }
    return {
        "frozen_checks":checks,
        "novel_world_preaction_Brier":h,
        "four_new_world_Brier":nov_laws,
        "negative_different_rule_preaction_Brier":
            negative["pooled_probe_brier"],
        "native_vs_GF2_conventional_abs_gap":
            abs(h["candidate"]-h["gf2_conventional"]),
        "native_unique_advantage_over_GF2_conventional":
            h["candidate"]<h["gf2_conventional"]-1e-12,
        "retained_chance_adjusted_gain":
            retention["candidate_chance_adjusted_retention"],
        "charged_whole_source_actor_training_eval_wall_ratio":ratio,
        "candidate_vs_strong_model_wall_ns":charges,
        "common_original_source_actor_wall_ns":common,
        "peak_shared_rss_bytes":max(
            r["shared_peak_rss_bytes"] for r in evalrows
        ),
        "per_model_isolated_rss":"UNVERIFIED",
        "full_final_G29":"UNVERIFIED",
        "development_disposition":(
            "QUADRATIC_RULE_DISCOVERY_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE"
            if all(checks.values()) else "DEV_NO_GO"
        )
    }


def compare(checkpoint,result_path):
    exact_guard()
    c,train_sha=load_checkpoint(checkpoint)
    # Frozen pre-training artifact loaded FIRST. No candidate selection or
    # last-minute source edits after first held law is opened.
    held=no_learn_family(c,HELD,HELD_SEEDS,"held")
    negative=no_learn_family(c,NEGATIVE,(205,),"negative")
    retained=cold_retention(c)
    metrics=classify(held,negative,retained,c)
    document={
        "schema":RESULT_SCHEMA,
        "evidence_class":"ORIGINAL_INHOUSE_DEVELOPMENT_ONLY",
        "frozen_protocol_git_blob":PREREG_BLOB,
        "private_world_git_blob":WORLD_BLOB,
        "native_model_git_blob":MODEL_BLOB,
        "strong_control_git_blob":CONTROLS_BLOB,
        "one_original_training_checkpoint_sha256":train_sha,
        "held":held,"different_new_rule":negative,
        "cold_retention":retained,"metrics":metrics,
        "held_new_world_laws_opened_once":list(HELD),
        "held_seeds_opened_once":list(HELD_SEEDS),
        "negative_new_rule_laws_opened_once":list(NEGATIVE),
        "no_fitting_on_unfamiliar_laws":True,
        "model_saw_private_source_law_coefficients_or_labels":False,
        "protected_scientific_first_use":False,
        "independent_scientific_pass":False,
        "development_disposition":metrics["development_disposition"]
    }
    result_path.write_text(canonical(document)+"\n",encoding="utf-8")
    print("ST7_ORIGINAL_HELD_RULE_BRIER="+canonical(
        metrics["novel_world_preaction_Brier"]))
    print("ST7_DIFFERENT_UNKNOWN_RULE_NEGATIVE_BRIER="+canonical(
        metrics["negative_different_rule_preaction_Brier"]))
    print("ST7_COLD_RETENTION_FRACTION="+str(
        metrics["retained_chance_adjusted_gain"]))
    print("ST7_WHOLE_PROCESS_COST_RATIO="+str(
        metrics["charged_whole_source_actor_training_eval_wall_ratio"]))
    print("ST7_FROZEN_CHECKS="+canonical(metrics["frozen_checks"]))
    print("ST7_DEV_DISPOSITION="+metrics["development_disposition"])
    print("ST7_PROTECTED_FIRST_USE=NOT_RUN")
    return document


if __name__=="__main__":
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="mode",required=True)
    a=sub.add_parser("train")
    a.add_argument("--out",type=Path,required=True)
    b=sub.add_parser("compare")
    b.add_argument("--checkpoint",type=Path,required=True)
    b.add_argument("--out",type=Path,required=True)
    cmd=p.parse_args()
    if cmd.mode=="train":
        train_once(cmd.out)
    else:
        compare(cmd.checkpoint,cmd.out)
