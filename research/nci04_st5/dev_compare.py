"""Frozen ST5 public-only native causal memory development evaluator.

Authentic original ST5 DiagnosticWorld takes five REAL actions. Every
model predicts before world.step and learns only afterward. Hidden
source law ID / trial / seed belong to EVALUATOR ONLY, never model API.

Train 8 laws once on Linux, export ONE exact shared checkpoint to both OS.
Cold recall tests original law 3 without fitting, before and after eight
unrelated intervening training laws. Held unfamiliar laws are read only
AFTER the checkpoint is established, with learn=False (zero-shot).
This synthetic test is DEVELOPMENT ONLY; no protected scientific first use.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

import psutil

from research.nci04_st5.diagnostic_world import (
    DiagnosticWorld,run_original_episode,ACTIONS,TRIALS
)
from research.nci04_st5.native_memory import (
    NativeCausalRecall8,canonical
)
from research.nci04_st5.matched_controls import (
    Recurrent45,SignatureCount8,brier
)
from research.nci04_st5.source_audit import (
    verify_freeze,audit,TRAIN_LAWS,TRAIN_SEEDS,
    INTERFERENCE_LAWS,HELD_LAWS,HELD_SEEDS,
    PREREG_BLOB
)

TRAIN_SCHEMA="yggdrasil.nci04.st5.single-training-models.v1"
RESULT_SCHEMA="yggdrasil.nci04.st5.cold-retention-unfamiliar-dev.v1"
NAMES=("candidate","recurrent45","raw_count","residual_count",
       "no_cue","erase","sham_key")
SOURCE_FILE="research/nci04_st5/diagnostic_world.py"
SOURCE_SHA="052072234fedf4c2ef7fe42fe138e7a10837d3c4"
MODEL_SOURCE="research/nci04_st5/native_memory.py"
MODEL_SHA="90195b8e45e67d8ad9235dde7a520a0ad7eda220"
CONTROLS_SOURCE="research/nci04_st5/matched_controls.py"
CONTROLS_SHA="28b0d61b14f2d2305db74e8b34376b2fb5a53952"
MAX_TRAIN_BLOB=2000000
PROCESS=psutil.Process()


def guard_provenance():
    p=verify_freeze()
    for path,sha in (
        (SOURCE_FILE,SOURCE_SHA),
        (MODEL_SOURCE,MODEL_SHA),
        (CONTROLS_SOURCE,CONTROLS_SHA),
    ):
        if sha.startswith("TO_BE_PINNED"):
            raise ValueError("ST5_MODEL_OR_SOURCE_UNPINNED")
        got=subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
        if got!=sha:
            raise ValueError("ST5_FROZEN_RESEARCH_BLOB_DRIFT_"+path)
    return p


def make_models():
    return {
        "candidate":NativeCausalRecall8("causal"),
        "recurrent45":Recurrent45(),
        "raw_count":SignatureCount8("raw"),
        "residual_count":SignatureCount8("residual"),
        "no_cue":NativeCausalRecall8("no_cue"),
        "erase":NativeCausalRecall8("erase"),
        "sham_key":NativeCausalRecall8("sham_key")
    }


def restore_one(name,blob):
    if name=="recurrent45":
        return Recurrent45.restore(blob)
    if name in ("raw_count","residual_count"):
        obj=SignatureCount8.restore(blob)
        expected="raw" if name=="raw_count" else "residual"
        if obj.mode!=expected:
            raise ValueError("ST5_WRONG_COUNT_COMPARATOR_MODE")
        return obj
    obj=NativeCausalRecall8.restore(blob)
    expected="causal" if name=="candidate" else name
    if obj.variant!=expected:
        raise ValueError("ST5_WRONG_NATIVE_ABLATION_MODE")
    return obj


def restored_suite(snapshots):
    if type(snapshots) is not dict or set(snapshots)!=set(NAMES):
        raise ValueError("ST5_MISSING_PRETRAINED_MODEL")
    models={name:restore_one(name,snapshots[name]) for name in NAMES}
    if any(models[n].snapshot()!=snapshots[n] for n in NAMES):
        raise ValueError("ST5_TRAINING_CHECKPOINT_RESTORE_NOT_EXACT")
    return models


def model_counters(model):
    if hasattr(model,"banks"):
        return canonical(model.banks)
    return canonical({
        "local":model.local,
        "shared":model.shared,
    })


def actual_episode(law,seed,trial,models,phase,train=True,
                   *,cold_check=False):
    """Source law/seed/trial NEVER get passed to any learner method."""
    if type(train) is not bool or phase not in (
        "train","interference","recall","unfamiliar","source_fixture"
    ):
        raise ValueError("ST5_EVALUATOR_BAD_PHASE")
    world=DiagnosticWorld(law,seed,trial)
    for model in models.values():
        model.reset_episode()
    source_sha=sha256()
    scores={n:None for n in models}
    costs={n:{"wall_ns":0,"cpu_ns":0} for n in models}
    source_wall=0;source_cpu=0;actor_wall=0
    restores=0
    max_rss=PROCESS.memory_info().rss
    for step,action in enumerate(ACTIONS):
        before=world.public()
        predictions={}
        for name,m in models.items():
            ts=time.perf_counter_ns();cpu=time.process_time_ns()
            predictions[name]=m.predict(before,action)
            costs[name]["wall_ns"]+=time.perf_counter_ns()-ts
            costs[name]["cpu_ns"]+=time.process_time_ns()-cpu
        ts=time.perf_counter_ns();cpu=time.process_time_ns()
        after,target=world.step(action)
        source_wall+=time.perf_counter_ns()-ts
        source_cpu+=time.process_time_ns()-cpu
        if tuple(a^b for a,b in zip(before,after))!=target:
            raise ValueError("ST5_ACTUAL_SOURCE_CONSEQUENCE_MISMATCH")
        source_sha.update(bytes((*before,action,*after,*target)))
        if step==len(ACTIONS)-1 and phase in ("recall","unfamiliar"):
            for name in models:
                scores[name]=brier(predictions[name],target)
        for name,m in tuple(models.items()):
            ts=time.perf_counter_ns();cpu=time.process_time_ns()
            returned=m.observe(before,action,target,after,train=train)
            costs[name]["wall_ns"]+=time.perf_counter_ns()-ts
            costs[name]["cpu_ns"]+=time.process_time_ns()-cpu
            if returned!=predictions[name]:
                raise ValueError("ST5_FUTURE_LABEL_LEAK_"+name)
        if cold_check and step==2:
            for name,m in tuple(models.items()):
                ts=time.perf_counter_ns();cpu=time.process_time_ns()
                snap=m.snapshot()
                restored=restore_one(name,snap)
                if restored.snapshot()!=snap:
                    raise ValueError("ST5_COLD_RESTORE_DRIFT_"+name)
                models[name]=restored
                restores+=1
                costs[name]["wall_ns"]+=time.perf_counter_ns()-ts
                costs[name]["cpu_ns"]+=time.process_time_ns()-cpu
        max_rss=max(max_rss,PROCESS.memory_info().rss)
    return {
        "source_sha256":source_sha.hexdigest(),
        "genuine_original_source_steps":len(ACTIONS),
        "preaction_delayed_probe_brier":scores if phase in
            ("recall","unfamiliar") else None,
        "model_cost_ns":costs,
        "source_wall_ns":source_wall,
        "source_cpu_ns":source_cpu,
        "actor_wall_ns":actor_wall,
        "shared_worker_peak_rss_bytes":max_rss,
        "cold_restarts":restores,
        "private_source_fields_given_to_model":False,
        "protected_first_use":False
    }


def train_once(output):
    guard_provenance()
    gate_path=output.with_name("st5-actual-source-stage0.json")
    gate=audit(gate_path)
    if gate["source_disposition"]["disposition"]!=(
            "SOURCE_LAW_RETRIEVAL_IDENTIFIABLE_DEV_ONLY"):
        raise ValueError("ST5_TRAIN_REFUSED_UNIDENTIFIABLE_SOURCE")
    started=time.perf_counter_ns()
    models=make_models()
    original_hashes=[]
    training_cost={n:{"cpu_ns":0,"wall_ns":0} for n in NAMES}
    actual_count=0
    original_episodes=0
    for law in TRAIN_LAWS:
        law_sha=sha256()
        for seed in TRAIN_SEEDS:
            for trial in range(TRIALS):
                outcome=actual_episode(
                    law,seed,trial,models,"train",True,
                    cold_check=(trial==0)
                )
                original_episodes+=1
                actual_count+=outcome["genuine_original_source_steps"]
                law_sha.update(bytes.fromhex(outcome["source_sha256"]))
                for n in NAMES:
                    for part in ("cpu_ns","wall_ns"):
                        training_cost[n][part]+=outcome["model_cost_ns"][n][part]
        audit_law=next(
            d for d in gate["training_source_law_records"]
            if d["law_source_evaluator_only"]==law
        )
        if law_sha.hexdigest()!=audit_law["real_source_action_history_sha256"]:
            raise ValueError("ST5_ACTUAL_CONSUMED_SOURCE_NOT_SOURCE_ONLY_AUDIT")
        original_hashes.append({
            "law_evaluator_only":law,
            "genuine_source_sha256":law_sha.hexdigest(),
            "episodes":len(TRAIN_SEEDS)*TRIALS
        })
    if actual_count!=7680 or original_episodes!=1536:
        raise ValueError("ST5_ORIGINAL_TRAINING_ACTION_OR_EPISODE_COUNT")
    doc={
        "schema":TRAIN_SCHEMA,
        "frozen_protocol_git_blob":PREREG_BLOB,
        "source_git_blob":SOURCE_SHA,
        "candidate_git_blob":MODEL_SHA,
        "conventional_git_blob":CONTROLS_SHA,
        "training_laws":list(TRAIN_LAWS),
        "training_seeds":list(TRAIN_SEEDS),
        "original_source_episodes":original_episodes,
        "original_source_action_steps":actual_count,
        "original_source_per_law_sha256":original_hashes,
        "trained_models":{n:models[n].snapshot() for n in NAMES},
        "model_accounting":{n:models[n].accounting() for n in NAMES},
        "training_model_cpu_wall_ns":training_cost,
        "training_wall_ns":time.perf_counter_ns()-started,
        "original_source_identifiability_pass":True,
        "held_development_unopened":True,
        "protected_first_use":False
    }
    output.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST5_TRAIN_ORIGINAL_EPISODES="+str(original_episodes))
    print("ST5_TRAIN_ACTUAL_ACTIONS="+str(actual_count))
    print("ST5_TRAIN_CHECKPOINT_SHA256="+sha256(output.read_bytes()).hexdigest())
    print("ST5_TRAIN_HELD_FIRST_USE_NOT_CONSUMED=PASS")
    return doc


def load_checkpoint(path):
    raw=path.read_bytes()
    if len(raw)>MAX_TRAIN_BLOB:
        raise ValueError("ST5_TRAINED_CUSTODY_SIZE_OVERFLOW")
    c=json.loads(raw)
    if (c.get("schema")!=TRAIN_SCHEMA or
        c.get("frozen_protocol_git_blob")!=PREREG_BLOB or
        c.get("source_git_blob")!=SOURCE_SHA or
        c.get("candidate_git_blob")!=MODEL_SHA or
        c.get("conventional_git_blob")!=CONTROLS_SHA or
        c.get("training_laws")!=list(TRAIN_LAWS) or
        c.get("training_seeds")!=list(TRAIN_SEEDS) or
        c.get("original_source_episodes")!=1536 or
        c.get("original_source_action_steps")!=7680 or
        c.get("held_development_unopened") is not True or
        c.get("protected_first_use") is not False or
        raw.decode("utf-8")!=canonical(c)+"\n"):
        raise ValueError("ST5_EXACT_SINGLE_TRAINING_CUSTODY_DRIFT")
    restored_suite(c["trained_models"])
    return c,sha256(raw).hexdigest()


def aggregate(rows):
    if len(rows)!=TRIALS:
        raise ValueError("ST5_INCOMPLETE_16_TRIAL_RECALL")
    if any(r["genuine_original_source_steps"]!=5 or
           r["preaction_delayed_probe_brier"] is None for r in rows):
        raise ValueError("ST5_RECALL_NOT_ORIGINAL_PUBLIC_ACTIONS")
    return {
        n:sum(r["preaction_delayed_probe_brier"][n] for r in rows)/TRIALS
        for n in NAMES
    }


def original_recall(models,seed=100,*,record_state=False):
    frozen={n:model_counters(models[n]) for n in NAMES}
    result=[]
    start=time.perf_counter_ns()
    for trial in range(TRIALS):
        rec=actual_episode(3,seed,trial,models,"recall",False,
                           cold_check=(trial==0))
        result.append(rec)
    for n in NAMES:
        # Erasure is an explicit negative: reset_episode wipes its OWN
        # bank even when train=False. That is not outcome fitting.
        if n=="erase":
            if any(b is not None for b in models[n].banks):
                raise ValueError("ST5_COLD_ERASURE_NEGATIVE_STORED_LAW")
            continue
        if frozen[n]!=model_counters(models[n]):
            raise ValueError("ST5_COLD_RECALL_RETRAINED_ORIGINAL_"+n)
    scores=aggregate(result)
    trace=sha256()
    for r in result:
        trace.update(bytes.fromhex(r["source_sha256"]))
    return {
        "untrained_original_law":3,
        "untrained_original_seed":seed,
        "genuine_original_source_sha256":trace.hexdigest(),
        "actual_original_source_actions":TRIALS*5,
        "preaction_delayed_probe_brier":scores,
        "learned_bank_write_during_recall":False,
        "cold_model_restarts":sum(r["cold_restarts"] for r in result),
        "read_only_recall_wall_ns":time.perf_counter_ns()-start,
        "source_model_cost_ns":{
            n:{
                part:sum(r["model_cost_ns"][n][part] for r in result)
                for part in ("wall_ns","cpu_ns")
            } for n in NAMES
        },
        "source_actor_wall_ns":sum(r["source_wall_ns"]+
                                   r["actor_wall_ns"] for r in result),
        "native_integer_cold_state_sha256":(
            sha256(models["candidate"].snapshot().encode("utf-8")).hexdigest()
            if record_state else None
        )
    }


def evaluate_retention(checkpoint):
    suite=restored_suite(checkpoint["trained_models"])
    before=original_recall(suite,record_state=True)
    interfered_actions=0
    interference_receipts=[]
    for law in INTERFERENCE_LAWS:
        trace=sha256()
        for trial in range(TRIALS):
            rec=actual_episode(
                law,111,trial,suite,"interference",True,
                cold_check=(trial==0)
            )
            interfered_actions+=rec["genuine_original_source_steps"]
            trace.update(bytes.fromhex(rec["source_sha256"]))
        interference_receipts.append({
            "law_evaluator_only":law,
            "original_source_sha256":trace.hexdigest()
        })
    if interfered_actions!=len(INTERFERENCE_LAWS)*TRIALS*5:
        raise ValueError("ST5_INCOMPLETE_EIGHT_CAUSAL_INTERFERENCES")
    after=original_recall(suite,record_state=True)
    baseline=.25
    pre=before["preaction_delayed_probe_brier"]["candidate"]
    post=after["preaction_delayed_probe_brier"]["candidate"]
    gain=max(0.,baseline-pre)
    retained=(max(0.,1.-max(0.,post-pre)/gain) if gain>0 else 0.)
    return {
        "original_before":before,"original_after":after,
        "interfering_law_receipts":interference_receipts,
        "interfering_genuine_source_actions":interfered_actions,
        "frozen_chance_brier":baseline,
        "candidate_before_probe_brier":pre,
        "candidate_after_probe_brier":post,
        "candidate_retained_chance_corrected_gain":retained,
        "frozen_min_retained_gain":.95,
        "frozen_max_absolute_brier_increase":.02,
        "post_interference_causal_bank_count":sum(
            b is not None for b in suite["candidate"].banks
        ),
        "same_16_profile_uint8_counter_budget":(
            suite["candidate"].accounting()[
                "learned_uint8_counter_capacity_bytes"]==
            suite["residual_count"].accounting()[
                "learned_uint8_counter_capacity_bytes"]==
            suite["raw_count"].accounting()[
                "learned_uint8_counter_capacity_bytes"]==256
        ),
        "retention_pass":retained>=.95 and post<=pre+.02,
        "no_original_law_retraining_during_recall":True,
        "protected_first_use":False,
    }


def evaluate_unfamiliar(checkpoint):
    models=restored_suite(checkpoint["trained_models"])
    rows=[]
    total=0
    for law in HELD_LAWS:
        for seed in HELD_SEEDS:
            trace=sha256()
            scores={n:0. for n in NAMES}
            model_cost={n:{"wall_ns":0,"cpu_ns":0} for n in NAMES}
            source_actor_wall=0
            peak_rss=PROCESS.memory_info().rss
            cold_total=0
            for trial in range(TRIALS):
                rec=actual_episode(
                    law,seed,trial,models,"unfamiliar",False,
                    cold_check=(trial==0)
                )
                total+=rec["genuine_original_source_steps"]
                trace.update(bytes.fromhex(rec["source_sha256"]))
                for n in NAMES:
                    scores[n]+=rec["preaction_delayed_probe_brier"][n]
                    for part in ("wall_ns","cpu_ns"):
                        model_cost[n][part]+=rec["model_cost_ns"][n][part]
                source_actor_wall+=rec["source_wall_ns"]+rec["actor_wall_ns"]
                peak_rss=max(peak_rss,rec["shared_worker_peak_rss_bytes"])
                cold_total+=rec["cold_restarts"]
            rows.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "actual_source_steps":TRIALS*5,
                "actual_source_sha256":trace.hexdigest(),
                "probe_brier":{n:scores[n]/TRIALS for n in NAMES},
                "model_cpu_wall_ns":model_cost,
                "source_actor_wall_ns":source_actor_wall,
                "peak_shared_worker_rss_bytes":peak_rss,
                "all_models_cold_restarts":cold_total,
                "native_integer_cold_state_sha256":
                    sha256(models["candidate"].snapshot().encode(
                        "utf-8")).hexdigest(),
                "protected_scientific_first_use":False
            })
    if len(rows)!=32 or total!=2560:
        raise ValueError("ST5_HELD_SOURCE_ACTION_COVERAGE_DRIFT")
    scores={
        n:sum(r["probe_brier"][n] for r in rows)/len(rows)
        for n in NAMES
    }
    return {
        "held_development_source_receipts":rows,
        "held_development_probe_brier":scores,
        "original_held_source_actions":total,
        "model_never_fitted_unfamiliar_laws":True,
        "real_world_transfer":"NOT_TESTED",
        "independent_scientific_first_use":False
    }


def classify(retention,unfamiliar):
    pre=retention["original_before"]["preaction_delayed_probe_brier"]
    after=retention["original_after"]["preaction_delayed_probe_brier"]
    candidate=after["candidate"]
    original_gain=retention["candidate_retained_chance_corrected_gain"]
    equivalence_diff=abs(candidate-after["residual_count"])
    held=unfamiliar["held_development_source_receipts"]
    wall={n:sum(row["model_cpu_wall_ns"][n]["wall_ns"]
                for row in held) for n in NAMES}
    cpu={n:sum(row["model_cpu_wall_ns"][n]["cpu_ns"]
               for row in held) for n in NAMES}
    common=sum(row["source_actor_wall_ns"] for row in held)
    strongest_baseline=min(
        wall["recurrent45"],wall["raw_count"],wall["residual_count"]
    )
    ratio=(common+wall["candidate"])/max(1,common+strongest_baseline)
    checks={
        "cold_original_retains_95pct_chance_corrected_gain":
            original_gain>=.95,
        "cold_original_absolute_brier_increase_le_0_02":
            candidate<=pre["candidate"]+.02,
        "original_cold_candidate_beats_no_cue_by_0_02":
            candidate<=after["no_cue"]-.02,
        "original_cold_candidate_beats_erase_by_0_02":
            candidate<=after["erase"]-.02,
        "all_original_public_cues_reproducible_after_eight_laws":
            retention["post_interference_causal_bank_count"]==16,
        "equal_256_learned_counter_bytes":
            retention["same_16_profile_uint8_counter_budget"],
        "all_2560_held_zero_shot_public_source_steps":
            unfamiliar["original_held_source_actions"]==2560 and
            unfamiliar["model_never_fitted_unfamiliar_laws"],
        "all_seven_models_cold_restored_per_held_lawseed":
            all(r["all_models_cold_restarts"]==len(NAMES) for r in held),
        "whole_source_actor_model_wall_ratio_le_1_5":
            ratio<=1.5,
    }
    return {
        "frozen_checks":checks,
        "pre_interference_original_probe_brier":pre,
        "post_interference_original_probe_brier":after,
        "original_post_candidate_vs_exact_residual_count_abs_gap":
            equivalence_diff,
        "native_method_unique_vs_equal_info_residual_count":
            equivalence_diff>1e-12,
        "held_unfamiliar_zero_shot_probe_brier":
            unfamiliar["held_development_probe_brier"],
        "model_cumulative_eval_cpu_ns":cpu,
        "model_cumulative_eval_wall_ns":wall,
        "source_actor_wall_ns":common,
        "whole_source_actor_model_wall_ratio":ratio,
        "peak_shared_process_rss_bytes":max(
            r["peak_shared_worker_rss_bytes"] for r in held
        ),
        "independently_isolated_per_model_rss":"UNVERIFIED",
        "total_auxiliary_state_byte_parity":"UNVERIFIED",
        "full_final_regression":"UNVERIFIED",
        "development_disposition":(
            "MEMORY_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE"
            if all(checks.values()) else "DEV_NO_GO"
        )
    }


def compare(train_path,result_path):
    guard_provenance()
    c,hash=load_checkpoint(train_path)
    # Retention is evaluated FIRST on only original trained and declared
    # interference laws. Held unfamiliar source is not accessed until after
    # all frozen model bytes are loaded and the primary retention is recorded.
    start=time.perf_counter_ns()
    retention=evaluate_retention(c)
    unfamiliar=evaluate_unfamiliar(c)
    scores=classify(retention,unfamiliar)
    doc={
        "schema":RESULT_SCHEMA,
        "origin":"ST5_IN_HOUSE_DEVELOPMENT_ONLY",
        "frozen_protocol_git_blob":PREREG_BLOB,
        "source_git_blob":SOURCE_SHA,
        "candidate_git_blob":MODEL_SHA,
        "controls_git_blob":CONTROLS_SHA,
        "common_training_sha256":hash,
        "train_laws_used":list(TRAIN_LAWS),
        "original_retention":retention,
        "unfamiliar_zero_shot":unfamiliar,
        "science_metrics":scores,
        "held_dev_laws_opened_once":list(HELD_LAWS),
        "held_dev_seeds_opened_once":list(HELD_SEEDS),
        "model_passed_private_world_identity":False,
        "protected_first_use":False,
        "independent_science":False,
        "scientific_pass":False,
        "frozen_mechanism_changed_after_outcome":False,
        "worker_eval_wall_ns":time.perf_counter_ns()-start,
        "development_disposition":scores["development_disposition"]
    }
    result_path.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST5_ORIGINAL_COLD_PRE_BRIER="+canonical(
        retention["original_before"]["preaction_delayed_probe_brier"]))
    print("ST5_ORIGINAL_COLD_POST_BRIER="+canonical(
        retention["original_after"]["preaction_delayed_probe_brier"]))
    print("ST5_INTERFERENCE_RETENTION_RATIO="+str(
        retention["candidate_retained_chance_corrected_gain"]))
    print("ST5_UNFAMILIAR_ZERO_SHOT_BRIER="+canonical(
        unfamiliar["held_development_probe_brier"]))
    print("ST5_FROZEN_DEV_CHECKS="+canonical(scores["frozen_checks"]))
    print("ST5_DEV_DISPOSITION="+scores["development_disposition"])
    print("ST5_PROTECTED_SCIENTIFIC_FIRST_USE=NOT_RUN")
    return doc


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    modes=cli.add_subparsers(dest="mode",required=True)
    train=modes.add_parser("train")
    train.add_argument("--out",type=Path,required=True)
    comp=modes.add_parser("compare")
    comp.add_argument("--checkpoint",type=Path,required=True)
    comp.add_argument("--out",type=Path,required=True)
    args=cli.parse_args()
    if args.mode=="train":
        train_once(args.out)
    else:
        compare(args.checkpoint,args.out)
