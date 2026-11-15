"""ST9 one-checkpoint, eight-intervention genuine causal-memory DEV comparison.

This private EVALUATOR may instantiate source worlds and read frozen
evaluator-only law IDs/seed/trial. None enters the model methods. Every
model sees current PUBLIC 8-bit preaction state, announced public action,
then the genuine source's observed changed public bits AFTER world.step.
Train only 8 intervention episodes per arm with differing public actor
probes; held evaluations use identical original source actions for all.

In-house synthetic development only. No protected scientific first use.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st9.private_world import PrivateWorld
from research.nci04_st9.source_audit import (
    audit,verify_freeze,FROZEN_BLOB,SOURCE_BLOB,TRAIN_LAWS,TRAIN_SEEDS,
    ACTIVE,PASSIVE_REPEAT,PASSIVE_DISPERSED
)
from research.nci04_st9.native_repair import canonical
from research.nci04_st9.matched_controls import (
    make_models,restore_all,restore_one,ACTOR_GROUPS,active_plan
)

NATIVE_BLOB="8409f7e3352aabb6a5937a6a7443f2dc4a82f07a"
CONTROLS_BLOB="ff554c1e6cc533ebd0b09d7148baa0abcad4d195"
AUDIT_BLOB="bdf86bafbd166861ec7cd3264de6c87b04f25cfc"
TRAIN_SCHEMA="yggdrasil.nci04.st9.single-eight-intervention-trained.v1"
RESULT_SCHEMA="yggdrasil.nci04.st9.frozen-eight-intervention-dev.v1"
NAMES=tuple(make_models())
GROUPS={
    "active":tuple(name for name in NAMES if ACTOR_GROUPS[name]=="active"),
    "dispersed":("blind_dispersed",),
    "repeat":("blind_repeat",)
}
PROBES={"active":ACTIVE,"dispersed":PASSIVE_DISPERSED,
        "repeat":PASSIVE_REPEAT}
SOURCE_KEYS={"active":"active","dispersed":"passive_dispersed",
             "repeat":"passive_repeat"}
HELD_LAWS=(29,31,37,41)
HELD_SEEDS=(201,202,203,204)
NEGATIVE=(43,47)
INTERFERENCE=(53,59,61,67,71,73,79,83)
ALL_B=tuple(range(16))
MAX_FILE_BYTES=1000000
PROCESS=psutil.Process()


def guard():
    doc=verify_freeze()
    for path,expected in (
        ("research/nci04_st9/source_audit.py",AUDIT_BLOB),
        ("research/nci04_st9/native_repair.py",NATIVE_BLOB),
        ("research/nci04_st9/matched_controls.py",CONTROLS_BLOB)
    ):
        actual=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
        if actual!=expected:
            raise ValueError("ST9_MODEL_PREHELD_GIT_CUSTODY_DRIFT_"+path)
    if active_plan()!=ACTIVE:
        raise ValueError("ST9_PUBLIC_ACTOR_CHANGED_AFTER_PREREG")
    return doc


def scored_brier(guess,target):
    if (type(guess) not in (list,tuple) or len(guess)!=8 or
        type(target) not in (tuple,list) or len(target)!=8 or
        any(type(p) not in (int,float) or
            not 0<=p<=1 for p in guess) or
        any(type(v) is not int or v not in (0,1) for v in target)):
        raise ValueError("ST9_FROZEN_BRIER_INVALID_PREACTION")
    return sum((p-y)**2 for p,y in zip(guess,target))/8.


def evidence(m):
    if hasattr(m,"experiences"):
        return canonical([m.degree,m.rows,m.experiences])
    if hasattr(m,"buffer"):
        return canonical([m.degree,m.rows,m.buffer])
    raise ValueError("ST9_UNKNOWN_LEARNED_COLD_EVIDENCE")


def original_episode(law,seed,trial,B,cohort,train,*,cold=False):
    if (type(B) is not int or B not in range(16) or
        type(train) is not bool or not cohort or
        not set(cohort).issubset(set(NAMES))):
        raise ValueError("ST9_ORIGINAL_OUT_OF_SCOPE_MODEL_OR_ACTION")
    t0=time.perf_counter_ns()
    world=PrivateWorld(law,seed,trial)
    original_wall=time.perf_counter_ns()-t0
    actors_wall=0
    model_cost={name:{"wall_ns":0,"cpu_ns":0} for name in cohort}
    for name,m in cohort.items():
        start=time.perf_counter_ns();cpu=time.process_time_ns()
        m.reset_episode()
        model_cost[name]["wall_ns"]+=time.perf_counter_ns()-start
        model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
    source_events=bytearray()
    native_cold=sha256()
    prediction_score={}
    restarts=0
    peak=PROCESS.memory_info().rss
    for step in range(2):
        t0=time.perf_counter_ns()
        action=0 if step==0 else B+1
        actors_wall+=time.perf_counter_ns()-t0
        public=world.public()
        forecasts={}
        for name,m in cohort.items():
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            forecasts[name]=m.predict(public,action)
            model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
            model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
        t0=time.perf_counter_ns()
        after,target=world.step(action)
        original_wall+=time.perf_counter_ns()-t0
        if tuple(a^b for a,b in zip(public,after))!=target:
            raise ValueError("ST9_UNAUTHENTIC_ORIGINAL_PUBLIC_CONSEQUENCE")
        source_events.extend(bytes((*public,action,*after,*target)))
        if step==1:
            prediction_score={
                name:scored_brier(forecasts[name],target) for name in cohort
            }
        for name,m in tuple(cohort.items()):
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            result=m.observe(public,action,target,after,train=train)
            model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
            model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
            if result!=forecasts[name]:
                raise ValueError("ST9_ORIGINAL_FUTURE_LABEL_USED_IN_PREDICTION")
        if cold and step==0:
            for name,m in tuple(cohort.items()):
                t0=time.perf_counter_ns();cpu=time.process_time_ns()
                original=m.snapshot()
                copy=restore_one(name,original)
                if copy.snapshot()!=original:
                    raise ValueError("ST9_ORIGINAL_COLD_MODEL_CUSTODY_INEXACT")
                cohort[name]=copy
                restarts+=1
                model_cost[name]["wall_ns"]+=time.perf_counter_ns()-t0
                model_cost[name]["cpu_ns"]+=time.process_time_ns()-cpu
        if "candidate" in cohort:
            t0=time.perf_counter_ns();cpu=time.process_time_ns()
            native_cold.update(sha256(cohort[
                "candidate"].snapshot().encode("utf-8")).digest())
            model_cost["candidate"]["wall_ns"]+=time.perf_counter_ns()-t0
            model_cost["candidate"]["cpu_ns"]+=time.process_time_ns()-cpu
        peak=max(peak,PROCESS.memory_info().rss)
    return {
        "genuine_source_steps":2,
        "real_source_action_bytes_hex":source_events.hex(),
        "real_source_action_sha256":sha256(source_events).hexdigest(),
        "preaction_probe_brier":prediction_score,
        "native_integer_state_sha256":native_cold.hexdigest()
            if "candidate" in cohort else None,
        "model_cpu_wall_ns":model_cost,
        "source_wall_ns":original_wall,
        "public_actor_wall_ns":actors_wall,
        "original_cold_model_restores":restarts,
        "shared_worker_peak_rss_bytes":peak,
        "private_source_law_or_coefficients_given_to_models":False,
        "scientific_first_use_protected":False
    }


def train_once(path):
    guard()
    stage0=audit(path.with_name("st9-source-stage0.json"))
    if stage0["source_gate"]["disposition"]!=(
            "SOURCE_BUDGETED_CAUSAL_REPAIR_IDENTIFIABLE_DEV_ONLY"):
        raise ValueError("ST9_REFUSE_TRAIN_NONIDENTIFIABLE_REAL_SOURCE")
    cohort=make_models()
    start=time.perf_counter_ns()
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    source_wall=0;actor_wall=0
    receipts={}
    steps={n:0 for n in NAMES}
    for group,names in GROUPS.items():
        source_hash=sha256()
        probe_sequence=PROBES[group]
        for i,(law,seed,B) in enumerate(zip(
            TRAIN_LAWS,TRAIN_SEEDS,probe_sequence
        )):
            limited={n:cohort[n] for n in names}
            rec=original_episode(law,seed,0,B,limited,True,cold=(i==0))
            source_hash.update(bytes.fromhex(rec[
                "real_source_action_bytes_hex"]))
            source_wall+=rec["source_wall_ns"]
            actor_wall+=rec["public_actor_wall_ns"]
            for n in names:
                steps[n]+=rec["genuine_source_steps"]
                for key in ("wall_ns","cpu_ns"):
                    costs[n][key]+=rec["model_cpu_wall_ns"][n][key]
        previous=stage0["real_source_actor_receipts"][SOURCE_KEYS[group]]
        if source_hash.hexdigest()!=previous["actual_original_source_action_sha256"]:
            raise ValueError("ST9_TRAINED_MODEL_SOURCE_DIFFERENT_FROM_STAGE0_"+group)
        receipts[group]={
            "actual_original_public_action_sha256":source_hash.hexdigest(),
            "eight_frozen_actor_probe_codes":list(probe_sequence),
            "actual_source_action_steps":len(probe_sequence)*2,
            "models":list(names)
        }
    if set(steps.values())!={16}:
        raise ValueError("ST9_UNEQUAL_TRAIN_INTERVENTION_BUDGET")
    c=cohort["candidate"]
    doc={
        "schema":TRAIN_SCHEMA,"frozen_blob":FROZEN_BLOB,
        "original_private_source_blob":SOURCE_BLOB,
        "source_audit_blob":AUDIT_BLOB,
        "native_model_blob":NATIVE_BLOB,
        "strong_control_blob":CONTROLS_BLOB,
        "original_train_episodes_per_arm":8,
        "original_train_source_actions_per_arm":steps,
        "source_actor_training_receipts":receipts,
        "model_states":{n:cohort[n].snapshot() for n in NAMES},
        "capacity_receipts":{n:cohort[n].accounting() for n in NAMES},
        "model_training_cpu_wall_ns":costs,
        "source_train_wall_ns":source_wall,
        "actor_train_wall_ns":actor_wall,
        "worker_total_train_wall_ns":time.perf_counter_ns()-start,
        "native_original_contradictions":c.contradictions,
        "native_actual_growth_events":c.growth_events,
        "native_trigger_on_original_intervention":c.growth_on_update,
        "native_replayed_pre_growth_experiences":c.pre_growth_replay_count,
        "native_learned_quadratic_rank":c.rank,
        "native_post_growth_conflicts":c.post_growth_conflicts,
        "no_replay_control_rank":cohort["no_replay"].rank,
        "adaptive_conventional_rank":cohort["adaptive_conventional"].rank,
        "full_active_conventional_rank":cohort["full_active"].rank,
        "held_worlds_not_opened":True,
        "alternative_rule_not_opened":True,
        "protected_scientific_first_use":False
    }
    path.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST9_EACH_ARM_ACTUAL_SOURCE_STEPS=16")
    print("ST9_NATIVE_REAL_CONTRADICTIONS="+str(c.contradictions))
    print("ST9_NATIVE_GROWTH_EVENTS="+str(c.growth_events))
    print("ST9_NATIVE_REPLAYED_PRIOR_OBSERVATIONS="+str(
        c.pre_growth_replay_count))
    print("ST9_NATIVE_REPAIRED_RANK="+str(c.rank))
    print("ST9_ACTION_MATCHED_NO_REPLAY_RANK="+str(cohort["no_replay"].rank))
    print("ST9_STRONG_CONVENTIONAL_ACTIVE_RANKS="+str([
        cohort["adaptive_conventional"].rank,
        cohort["full_active"].rank
    ]))
    print("ST9_COMMON_TRAIN_CHECKPOINT_SHA256="+sha256(
        path.read_bytes()).hexdigest())
    print("ST9_TRAIN_HELD_AND_NEGATIVE_UNOPENED=PASS")
    return doc


def load_training(path):
    raw=path.read_bytes()
    if len(raw)>MAX_FILE_BYTES:
        raise ValueError("ST9_TRAIN_CHECKPOINT_SIZE_BUDGET")
    obj=json.loads(raw)
    if (obj.get("schema")!=TRAIN_SCHEMA or
        obj.get("frozen_blob")!=FROZEN_BLOB or
        obj.get("original_private_source_blob")!=SOURCE_BLOB or
        obj.get("source_audit_blob")!=AUDIT_BLOB or
        obj.get("native_model_blob")!=NATIVE_BLOB or
        obj.get("strong_control_blob")!=CONTROLS_BLOB or
        obj.get("original_train_episodes_per_arm")!=8 or
        obj.get("original_train_source_actions_per_arm")!=
            {n:16 for n in NAMES} or
        obj.get("held_worlds_not_opened") is not True or
        obj.get("alternative_rule_not_opened") is not True or
        obj.get("protected_scientific_first_use") is not False or
        raw.decode("utf-8")!=canonical(obj)+"\n"):
        raise ValueError("ST9_FROZEN_EXACT_TRAINED_MODEL_CUSTODY_FAIL")
    restore_all(obj["model_states"])
    return obj,sha256(raw).hexdigest()


def unfitted_group(training,laws,seeds,probes,phase):
    cohort=restore_all(training["model_states"])
    frozen={n:evidence(m) for n,m in cohort.items()}
    records=[];count=0
    for law in laws:
        for seed in seeds:
            h=sha256();native_hash=sha256()
            scores={n:0. for n in NAMES}
            model_cost={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
            common=0;cold=0;peak=PROCESS.memory_info().rss
            for trial,B in enumerate(probes):
                rec=original_episode(law,seed,trial,B,cohort,False,
                                     cold=(trial==0))
                h.update(bytes.fromhex(rec["real_source_action_bytes_hex"]))
                native_hash.update(bytes.fromhex(
                    rec["native_integer_state_sha256"]))
                count+=rec["genuine_source_steps"]
                for n in NAMES:
                    scores[n]+=rec["preaction_probe_brier"][n]
                    for field in ("wall_ns","cpu_ns"):
                        model_cost[n][field]+=rec["model_cpu_wall_ns"][n][field]
                common+=rec["source_wall_ns"]+rec["public_actor_wall_ns"]
                cold+=rec["original_cold_model_restores"]
                peak=max(peak,rec["shared_worker_peak_rss_bytes"])
            records.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "real_source_steps":len(probes)*2,
                "real_source_action_sha256":h.hexdigest(),
                "native_integer_cold_state_chain":native_hash.hexdigest(),
                "probe_brier":{n:scores[n]/len(probes) for n in NAMES},
                "model_cpu_wall_ns":model_cost,
                "source_actor_wall_ns":common,
                "all_model_cold_restores":cold,
                "shared_worker_peak_rss":peak,
                "model_saw_private_law_coefficients":False
            })
    if count!=len(laws)*len(seeds)*len(probes)*2:
        raise ValueError("ST9_UNFAMILIAR_ORIGINAL_ACTION_COUNT")
    for n,m in cohort.items():
        if n!="erase" and evidence(m)!=frozen[n]:
            raise ValueError("ST9_MODEL_FITTED_FROM_HELD_OR_NEGATIVE_"+n)
    return {
        "phase":phase,"actual_original_source_actions":count,
        "records":records,
        "pooled_brier":{
            n:sum(row["probe_brier"][n] for row in records)/len(records)
            for n in NAMES
        },
        "any_held_learning":False
    }


def recall_original(cohort):
    frozen={n:evidence(m) for n,m in cohort.items()}
    h=sha256();native=sha256()
    scores={n:0. for n in NAMES}
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    source_actor=0;cold=0
    for trial,B in enumerate(ALL_B):
        row=original_episode(3,100,trial,B,cohort,False,cold=(trial==0))
        h.update(bytes.fromhex(row["real_source_action_bytes_hex"]))
        native.update(bytes.fromhex(row["native_integer_state_sha256"]))
        for n in NAMES:
            scores[n]+=row["preaction_probe_brier"][n]
            for key in ("wall_ns","cpu_ns"):
                costs[n][key]+=row["model_cpu_wall_ns"][n][key]
        source_actor+=row["source_wall_ns"]+row["public_actor_wall_ns"]
        cold+=row["original_cold_model_restores"]
    for n,m in cohort.items():
        if n!="erase" and evidence(m)!=frozen[n]:
            raise ValueError("ST9_ORIGINAL_RECALL_CHANGED_LEARNED_EVIDENCE")
    return {
        "original_source_steps":32,
        "original_source_sha256":h.hexdigest(),
        "native_integer_state_sha256":native.hexdigest(),
        "pooled_brier":{n:scores[n]/len(ALL_B) for n in NAMES},
        "model_cpu_wall_ns":costs,
        "source_actor_wall_ns":source_actor,
        "cold_model_restores":cold,
        "rehearsed_original_law_during_recall":False
    }


def retention(training):
    cohort=restore_all(training["model_states"])
    before=recall_original(cohort)
    history=[];original_steps=0;common=0
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
    for i,(law,B) in enumerate(zip(INTERFERENCE,ACTIVE)):
        row=original_episode(law,111,0,B,cohort,True,cold=(i==0))
        original_steps+=row["genuine_source_steps"]
        common+=row["source_wall_ns"]+row["public_actor_wall_ns"]
        for n in NAMES:
            for key in ("wall_ns","cpu_ns"):
                costs[n][key]+=row["model_cpu_wall_ns"][n][key]
        history.append({
            "law_evaluator_only":law,"B_public_action":B,
            "real_original_action_sha256":row["real_source_action_sha256"]
        })
    after=recall_original(cohort)
    p=before["pooled_brier"]["candidate"]
    q=after["pooled_brier"]["candidate"]
    gain=max(0.,.25-p)
    retained=max(0.,1.-max(0.,q-p)/gain) if gain>0 else 0.
    return {
        "before":before,"after":after,
        "eight_same_rule_interference_receipts":history,
        "real_interference_source_actions":original_steps,
        "native_retained_chance_adjusted_gain":retained,
        "native_cold_original_probe_Brier_change":q-p,
        "interference_model_cpu_wall_ns":costs,
        "interference_source_actor_wall_ns":common,
        "original_recall_fit":False
    }


def classify(held,negative,retained,training):
    if (held["actual_original_source_actions"]!=512 or
        len(held["records"])!=16 or
        negative["actual_original_source_actions"]!=64 or
        len(negative["records"])!=2 or
        retained["real_interference_source_actions"]!=16):
        raise ValueError("ST9_FROZEN_SOURCE_AND_ACTION_BUDGET_MISMATCH")
    h=held["pooled_brier"]
    held_law={
        str(law):sum(r["probe_brier"]["candidate"]
                     for r in held["records"]
                     if r["law_evaluator_only"]==law)/4
        for law in HELD_LAWS
    }
    evalrows=held["records"]+negative["records"]
    charges={
        n:(training["model_training_cpu_wall_ns"][n]["wall_ns"]+
           retained["interference_model_cpu_wall_ns"][n]["wall_ns"]+
           retained["before"]["model_cpu_wall_ns"][n]["wall_ns"]+
           retained["after"]["model_cpu_wall_ns"][n]["wall_ns"]+
           sum(r["model_cpu_wall_ns"][n]["wall_ns"] for r in evalrows))
        for n in NAMES
    }
    common=(training["source_train_wall_ns"]+
            training["actor_train_wall_ns"]+
            retained["interference_source_actor_wall_ns"]+
            retained["before"]["source_actor_wall_ns"]+
            retained["after"]["source_actor_wall_ns"]+
            sum(r["source_actor_wall_ns"] for r in evalrows))
    fastest=min(charges["full_active"],charges["adaptive_conventional"])
    ratio=(common+charges["candidate"])/max(1,common+fastest)
    checks={
        "true_linear_contradiction_triggers_one_repair":
            training["native_original_contradictions"]>=1 and
            training["native_actual_growth_events"]==1 and
            training["native_trigger_on_original_intervention"] is not None,
        "eight_feature_full_repair_rank_and_zero_conflicts":
            training["native_learned_quadratic_rank"]==8 and
            training["native_post_growth_conflicts"]==0,
        "actual_pre_growth_public_experiences_replayed_ge_2":
            training["native_replayed_pre_growth_experiences"]>=2,
        "held_pooled_Brier_le_0_02":h["candidate"]<=.02,
        "each_four_held_laws_Brier_le_0_04":
            all(x<=.04 for x in held_law.values()),
        "replay_improves_matched_no_replay_ge_0_06":
            h["candidate"]<=h["no_replay"]-.06,
        "active_improves_strong_blind_dispersed_ge_0_06":
            h["candidate"]<=h["blind_dispersed"]-.06,
        "active_improves_blind_repeat_ge_0_10":
            h["candidate"]<=h["blind_repeat"]-.10,
        "causal_growth_beats_no_growth_ge_0_10":
            h["candidate"]<=h["no_growth"]-.10,
        "persistent_learning_beats_erasure_ge_0_10":
            h["candidate"]<=h["erase"]-.10,
        "native_matches_full_conventional_within_0_01":
            h["candidate"]<=h["full_active"]+.01,
        "native_matches_exact_adaptive_conventional_within_0_01":
            h["candidate"]<=h["adaptive_conventional"]+.01,
        "identical_eight_action_budget_all_arms":
            training["original_train_source_actions_per_arm"]==
            {n:16 for n in NAMES},
        "matched_max_8x16_bit_learned_evidence":
            training["capacity_receipts"]["candidate"][
                "learned_GF2_evidence_bits_max"]==
            training["capacity_receipts"]["adaptive_conventional"][
                "max_GF2_learned_augmented_bits"]==128,
        "unseen_different_rule_negative_Brier_ge_0_10":
            negative["pooled_brier"]["candidate"]>=.10,
        "after_eight_interferences_retained_gain_ge_0_95":
            retained["native_retained_chance_adjusted_gain"]>=.95,
        "no_original_cold_probe_Brier_deterioration_gt_0_02":
            retained["native_cold_original_probe_Brier_change"]<=.02,
        "all_eight_model_cold_restores_on_held_and_negative":
            all(r["all_model_cold_restores"]==len(NAMES) for r in evalrows),
        "end_to_end_source_actor_training_evaluation_ratio_le_1_5":
            ratio<=1.5
    }
    return {
        "checks":checks,
        "pooled_held_preaction_Brier":h,
        "four_held_world_Brier":held_law,
        "different_rule_negative_Brier":negative["pooled_brier"],
        "native_vs_conventional_adaptive_absolute_gap":
            abs(h["candidate"]-h["adaptive_conventional"]),
        "native_unique_advantage_over_conventional_adaptive":
            h["candidate"]<h["adaptive_conventional"]-1e-12,
        "actual_native_memory_replay_advantage":
            h["no_replay"]-h["candidate"],
        "active_vs_blind_dispersed_absolute_gain":
            h["blind_dispersed"]-h["candidate"],
        "cold_retained_gain_fraction":
            retained["native_retained_chance_adjusted_gain"],
        "charged_source_actor_train_eval_wall_ratio":ratio,
        "whole_model_wall_ns":charges,
        "source_actor_common_wall_ns":common,
        "peak_shared_worker_rss_bytes":max(
            r["shared_worker_peak_rss"] for r in evalrows),
        "isolated_model_rss":"UNVERIFIED",
        "full_G29_final":"UNVERIFIED",
        "development_disposition":(
            "BUDGETED_MEMORY_REPAIR_DEV_SIGNAL_NOT_SCIENTIFIC_PASS"
            if all(checks.values()) else "DEV_NO_GO"
        )
    }


def compare(checkpoint,out):
    guard()
    train,sha=load_training(checkpoint)
    held=unfitted_group(train,HELD_LAWS,HELD_SEEDS,ALL_B,"held")
    negative=unfitted_group(train,NEGATIVE,(205,),ALL_B,"negative")
    cold=retention(train)
    scores=classify(held,negative,cold,train)
    evidence={
        "schema":RESULT_SCHEMA,
        "evidence_class":"INHOUSE_ORIGINAL_SYNTHETIC_DEV_ONLY",
        "frozen_protocol_git_blob":FROZEN_BLOB,
        "original_source_git_blob":SOURCE_BLOB,
        "native_model_git_blob":NATIVE_BLOB,
        "conventional_controls_git_blob":CONTROLS_BLOB,
        "one_trained_checkpoint_sha256":sha,
        "held":held,"different_rule":negative,
        "cold_retention":cold,"metrics":scores,
        "held_laws_opened_once":list(HELD_LAWS),
        "negative_laws_opened_once":list(NEGATIVE),
        "no_held_or_negative_model_fitting":True,
        "private_source_oracle_to_model":False,
        "protected_scientific_first_use":False,
        "independent_scientific_pass":False,
        "protocol_source_model_untuned_after_first_held":True,
        "development_disposition":scores["development_disposition"]
    }
    out.write_text(canonical(evidence)+"\n",encoding="utf-8")
    print("ST9_HELD_PREACTION_BRIER="+canonical(
        scores["pooled_held_preaction_Brier"]))
    print("ST9_NEW_RULE_NEGATIVE_BRIER="+canonical(
        scores["different_rule_negative_Brier"]))
    print("ST9_ACTUAL_REPLAY_GAIN="+str(
        scores["actual_native_memory_replay_advantage"]))
    print("ST9_COLD_RETENTION="+str(scores["cold_retained_gain_fraction"]))
    print("ST9_TOTAL_SOURCE_PROCESS_RATIO="+str(
        scores["charged_source_actor_train_eval_wall_ratio"]))
    print("ST9_FROZEN_DEV_CHECKS="+canonical(scores["checks"]))
    print("ST9_DEV_DISPOSITION="+scores["development_disposition"])
    print("ST9_PROTECTED_FIRST_USE=NOT_RUN")
    return evidence


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    subs=ap.add_subparsers(dest="mode",required=True)
    tr=subs.add_parser("train");tr.add_argument("--out",type=Path,required=True)
    comp=subs.add_parser("compare")
    comp.add_argument("--checkpoint",type=Path,required=True)
    comp.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    if args.mode=="train":
        train_once(args.out)
    else:
        compare(args.checkpoint,args.out)
