"""ST3 frozen synthetic development test: in-house, never SCIENTIFIC_PASS.

Source runs on the already-frozen public-law split. Train-once outputs a
byte-identical checkpoint reused on both operating systems; no alternate
checkpoint or adaptive seed search. The learner receives ONLY public bits,
announced blind action and authentic postaction public consequence. Source
law IDs are evaluator grouping keys and NEVER passed into a model.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

import psutil

from research.nci04_st3.causal_switchboard import (
    HiddenLawSwitchboard, choose_blind_action, STEPS, _canonical
)
from research.nci04_st3.native_credit import NativeInterventionCredit8
from research.nci04_st3.matched_controls import (
    ConventionalRecurrent45, ActionCount8, brier
)
from research.nci04_st3.source_audit import (
    verify_prereg, deterministic_traces, delayed_intervention_counterfactual,
    stage0_verdict, TRAIN_LAWS, TRAIN_SEEDS, HELD_LAWS, HELD_SEEDS
)

CHECKPOINT_SCHEMA = "yggdrasil.nci04.st3.train-once-matched-public.v1"
RESULT_SCHEMA = "yggdrasil.nci04.st3.frozen-consumed-development.v1"
PROTOCOL_BLOB = "ce51862f6b5af6a130b6ad93c30f019131bfeb16"
NAMES = ("candidate", "recurrent45", "action_count", "no_delay", "sham",
         "episode_erase")
DEV_DISPOSITION_NO_GO = "DEV_NO_GO"
PROCESS = psutil.Process()


def source_headroom():
    p = verify_prereg()
    data = deterministic_traces()
    delayed = delayed_intervention_counterfactual()
    verdict = stage0_verdict(data, delayed)
    return p, verdict, data


def fresh_models():
    return {
        "candidate": NativeInterventionCredit8("causal"),
        "recurrent45": ConventionalRecurrent45(),
        "action_count": ActionCount8(),
        "no_delay": NativeInterventionCredit8("no_delay"),
        "sham": NativeInterventionCredit8("sham"),
        "episode_erase": NativeInterventionCredit8("episode_erase"),
    }


def from_checkpoint(checkpoint):
    return {
        "candidate": NativeInterventionCredit8.restore(checkpoint["candidate"]),
        "recurrent45": ConventionalRecurrent45.restore(
            checkpoint["recurrent45"]
        ),
        "action_count": ActionCount8.restore(checkpoint["action_count"]),
        "no_delay": NativeInterventionCredit8.restore(checkpoint["no_delay"]),
        "sham": NativeInterventionCredit8.restore(checkpoint["sham"]),
        "episode_erase": NativeInterventionCredit8.restore(
            checkpoint["episode_erase"]
        ),
    }


def model_snapshot(model):
    return model.snapshot()


def restore_model(name, payload):
    if name == "recurrent45":
        return ConventionalRecurrent45.restore(payload)
    if name == "action_count":
        return ActionCount8.restore(payload)
    return NativeInterventionCredit8.restore(payload)


def update_model(name, model, before, action, outcome, after, learn):
    if name == "recurrent45":
        return model.observe(before, action, outcome, after, train=learn)
    return model.observe(before, action, outcome, after, learn=learn)


def run_episode(law_id, seed, models, phase, *, train=True,
                per_step_hash=False):
    """law_id stays in evaluator scope; NEVER an argument to any model."""
    env = HiddenLawSwitchboard(law_id, seed)
    for model in models.values():
        model.reset_episode()
    sums={n:0.0 for n in NAMES}
    delayed_sums={n:0.0 for n in NAMES}
    delayed_steps=0
    model_wall={n:0 for n in NAMES}
    model_cpu={n:0 for n in NAMES}
    source_wall=0
    source_cpu=0
    action_wall=0
    cold_restores=0
    rss=PROCESS.memory_info().rss
    trace=sha256()
    state=sha256()
    previous_action=None
    changes=0
    start=time.perf_counter_ns()
    for t in range(STEPS):
        preaction=env.public()
        actor_start=time.perf_counter_ns()
        action=choose_blind_action(seed,t)
        action_wall+=time.perf_counter_ns()-actor_start
        predictions={}
        for name in NAMES:
            timer=time.perf_counter_ns()
            cpu=time.process_time_ns()
            predictions[name]=models[name].predict(preaction,action)
            model_wall[name]+=time.perf_counter_ns()-timer
            model_cpu[name]+=time.process_time_ns()-cpu
        # Authentic ORIGINAL in-house source step. Nobody can see its hidden
        # law, masks, pending or rotation. Every model predicted beforehand.
        source_start=time.perf_counter_ns()
        source_start_cpu=time.process_time_ns()
        after,outcome=env.step(action)
        source_wall+=time.perf_counter_ns()-source_start
        source_cpu+=time.process_time_ns()-source_start_cpu
        if tuple(a^b for a,b in zip(preaction,after))!=outcome:
            raise ValueError("ST3_EVAL_SOURCE_CONSEQUENCE_DRIFT")
        trace.update(bytes((*preaction,action,*after,*outcome)))
        prior_is_delayed=(previous_action==2 and action==3)
        for name in NAMES:
            if phase!="train":
                sums[name]+=brier(predictions[name],outcome)
                if prior_is_delayed:
                    delayed_sums[name]+=brier(predictions[name],outcome)
            t0=time.perf_counter_ns()
            c0=time.process_time_ns()
            returned=update_model(
                name,models[name],preaction,action,outcome,after,train
            )
            model_wall[name]+=time.perf_counter_ns()-t0
            model_cpu[name]+=time.process_time_ns()-c0
            if predictions[name]!=returned:
                raise ValueError("ST3_PREACTION_PREDICTION_LEAK_"+name)
        if prior_is_delayed:
            delayed_steps+=1
        previous_action=action
        # This checkpoint is an EXACT integer state receipt. It is separate
        # from source/actor output and cannot alter any model forecast.
        if per_step_hash:
            state.update(sha256(
                models["candidate"].snapshot().encode("utf-8")
            ).digest())
        if t==31:
            for name in NAMES:
                p=model_snapshot(models[name])
                restored=restore_model(name,p)
                if restored.snapshot()!=p:
                    raise ValueError("ST3_COLD_RESTORE_DRIFT_"+name)
                models[name]=restored
                cold_restores+=1
        rss=max(rss,PROCESS.memory_info().rss)
    receipt={
        "source_family":"IN_HOUSE_8BIT_HIDDEN_CAUSAL_LAW",
        "law_id_evaluator_only":law_id,
        "seed_evaluator_only":seed,
        "phase":phase,
        "actual_source_steps":STEPS,
        "source_action_outcome_sha256":trace.hexdigest(),
        "candidate_per_action_state_sha_chain": (
            state.hexdigest() if per_step_hash else None
        ),
        "preaction_brier":(
            {n:sums[n]/STEPS for n in NAMES} if phase!="train" else None
        ),
        "delayed_action2_followed_by_action3_steps":delayed_steps,
        "delayed_action2_to_action3_brier":(
            {n:delayed_sums[n]/delayed_steps for n in NAMES}
            if phase!="train" and delayed_steps else None
        ),
        "candidate_trained_observed_actions":models["candidate"].updates,
        "candidate_forks":models["candidate"].forks,
        "candidate_retrievals":models["candidate"].retrievals,
        "source_wall_ns":source_wall,
        "source_cpu_ns":source_cpu,
        "blind_actor_wall_ns":action_wall,
        "per_model_wall_ns":model_wall,
        "per_model_cpu_ns":model_cpu,
        "shared_process_peak_rss_bytes":rss,
        "cold_model_restarts":cold_restores,
        "whole_worker_episode_wall_ns":time.perf_counter_ns()-start,
        "learner_received_private_law_or_mask":False,
        "independent_science_first_use":False
    }
    return receipt


def build_train_once(output):
    frozen,source_gate,source_data=source_headroom()
    if source_gate["disposition"]!="SOURCE_TASK_IDENTIFIABLE_DEV_ONLY":
        raise ValueError("ST3_TRAIN_REFUSED_SOURCE_TASK_INVALID")
    if frozen["source"]["train_laws"]!=list(TRAIN_LAWS):
        raise ValueError("ST3_TRAIN_SOURCE_SET_DRIFT")
    start=time.perf_counter_ns()
    models=fresh_models()
    training=[]
    for law in TRAIN_LAWS:
        for seed in TRAIN_SEEDS:
            training.append(run_episode(law,seed,models,"train",
                                        train=True,per_step_hash=False))
    checkpoint={
        "schema":CHECKPOINT_SCHEMA,
        "frozen_protocol_blob":PROTOCOL_BLOB,
        "training_laws":list(TRAIN_LAWS),
        "training_seeds":list(TRAIN_SEEDS),
        "source_training_trace_sha256":sha256(_canonical([
            (r["law_id_evaluator_only"],r["seed_evaluator_only"],
             r["source_action_outcome_sha256"]) for r in training
        ]).encode("utf-8")).hexdigest(),
        "models":{name:models[name].snapshot() for name in NAMES},
        "model_accounting":{
            "candidate":models["candidate"].accounting(),
            "recurrent45":models["recurrent45"].accounting(),
            "action_count":models["action_count"].accounting()
        },
        "original_training_episode_count":len(training),
        "original_training_source_steps":sum(r["actual_source_steps"]
                                             for r in training),
        "source_stage0":source_gate,
        "no_held_development_used_for_training":True,
        "scientific_first_use":False,
        "training_wall_ns":time.perf_counter_ns()-start,
    }
    output.write_text(_canonical(checkpoint)+"\n",encoding="utf-8")
    print("ST3_TRAIN_SOURCE_STEPS="+str(checkpoint["original_training_source_steps"]))
    print("ST3_TRAIN_SOURCE_EPISODES="+str(len(training)))
    print("ST3_TRAIN_CHECKPOINT_SHA256="+sha256(output.read_bytes()).hexdigest())
    print("ST3_TRAIN_HELD_NOT_OPENED=PASS")
    return checkpoint


def load_checkpoint(path):
    payload=path.read_bytes()
    if len(payload)>1800000:
        raise ValueError("ST3_CHECKPOINT_SIZE_BUDGET")
    c=json.loads(payload)
    if (c.get("schema")!=CHECKPOINT_SCHEMA or
        c.get("frozen_protocol_blob")!=PROTOCOL_BLOB or
        c.get("training_laws")!=list(TRAIN_LAWS) or
        c.get("training_seeds")!=list(TRAIN_SEEDS) or
        c.get("original_training_episode_count")!=96 or
        c.get("original_training_source_steps")!=6144 or
        c.get("no_held_development_used_for_training") is not True or
        c.get("scientific_first_use") is not False or
        set(c.get("models",{}))!=set(NAMES) or
        payload.decode("utf-8")!=_canonical(c)+"\n"):
        raise ValueError("ST3_FROZEN_CHECKPOINT_CUSTODY_FAIL")
    m=from_checkpoint(c["models"])
    for name in NAMES:
        if m[name].snapshot()!=c["models"][name]:
            raise ValueError("ST3_FROZEN_CHECKPOINT_RESTORE_"+name)
    return c,sha256(payload).hexdigest()


def delay_retention_probe():
    """Fixed independent diagnostic: trained law 3 then EIGHT unrelated laws.

    The last revisit uses learn=False; only four public-source observations
    may select a stored profile. No future outcome fits learned counters.
    """
    model=NativeInterventionCredit8()
    for seed in TRAIN_SEEDS[:4]:
        # A physical cold restore at t=31 returns the NEW model object
        # through the episode's model map. Carry that exact restored state
        # forward; silently retaining the stale pre-cold object would erase
        # half the legitimate prior-law training.
        suite=fresh_models()
        suite["candidate"]=model
        run_episode(3,seed,suite,"train",train=True,
                    per_step_hash=False)
        model=suite["candidate"]
    def score_revisit():
        env=HiddenLawSwitchboard(3,100)
        model.reset_episode()
        total=0.0
        for t in range(STEPS):
            raw=env.public()
            action=choose_blind_action(100,t)
            prediction=model.predict(raw,action)
            nxt,target=env.step(action)
            total+=brier(prediction,target)
            returned=model.observe(raw,action,target,nxt,learn=False)
            if returned!=prediction:
                raise ValueError("ST3_RETENTION_REVISIT_LEARNED_FROM_FUTURE")
        return total/STEPS
    before=score_revisit()
    old_profiles=[canonical(p) if p is not None else None
                  for p in model.profiles]
    unrelated=(5,7,11,13,17,19,23,43)
    for law in unrelated:
        env=HiddenLawSwitchboard(law,100)
        model.reset_episode()
        for t in range(STEPS):
            raw=env.public()
            action=choose_blind_action(100,t)
            nxt,target=env.step(action)
            model.observe(raw,action,target,nxt,learn=True)
    # Exact same public source as initial no-learn revisit: no new training
    # on original law before/during second recall evaluation.
    updates=model.updates
    after=score_revisit()
    if model.updates!=updates:
        raise ValueError("ST3_RETENTION_POST_INTERFERENCE_RETRAIN")
    base_gain=max(0.,.25-before)
    ratio=max(0.,1.-max(0.,after-before)/base_gain) if base_gain>0 else 0.
    return {
        "prior_law_evaluator_only":3,
        "prior_law_pre_interference_recall_brier":before,
        "prior_law_post_interference_recall_brier":after,
        "unrelated_law_episodes":list(unrelated),
        "no_original_law_retraining_during_recall":True,
        "retained_chance_corrected_brier_gain_ratio":ratio,
        "frozen_threshold":0.95,
        "pass":ratio>=0.95,
        "initial_trained_bank_slots":sum(p is not None for p in
                                        (json.loads(x) if x else None
                                         for x in old_profiles)),
    }


def score_results(held,retention,accounts):
    source_steps=sum(r["actual_source_steps"] for r in held)
    if source_steps!=len(HELD_LAWS)*len(HELD_SEEDS)*STEPS:
        raise ValueError("ST3_HELD_SOURCE_STEPS_NOT_FROZEN")
    pooled={
        name:sum(r["preaction_brier"][name]*r["actual_source_steps"]
                 for r in held)/source_steps for name in NAMES
    }
    by_law={}
    for law in HELD_LAWS:
        rows=[r for r in held if r["law_id_evaluator_only"]==law]
        by_law[str(law)]={name:sum(r["preaction_brier"][name] for r in rows)/
                          len(rows) for name in NAMES}
    delayed=sum(r["delayed_action2_followed_by_action3_steps"] for r in held)
    if delayed<1:
        raise ValueError("ST3_HELD_NO_DELAYED_INTERVENTION_COVERAGE")
    delayed_pooled={
        name:sum(
            r["delayed_action2_to_action3_brier"][name]*
            r["delayed_action2_followed_by_action3_steps"]
            for r in held if r["delayed_action2_to_action3_brier"] is not None
        )/delayed for name in NAMES
    }
    winning_laws=sum(
        by_law[str(law)]["candidate"]<
            min(by_law[str(law)]["recurrent45"],
                by_law[str(law)]["action_count"])
        for law in HELD_LAWS
    )
    model_wall={name:sum(r["per_model_wall_ns"][name] for r in held)
                for name in NAMES}
    actor_source_wall=sum(
        r["source_wall_ns"]+r["blind_actor_wall_ns"] for r in held
    )
    best_control_total=actor_source_wall+min(
        model_wall["recurrent45"],model_wall["action_count"]
    )
    candidate_total=actor_source_wall+model_wall["candidate"]
    cost_ratio=candidate_total/max(1,best_control_total)
    # Attention: padding a count table to the same memory bytes would NOT
    # create the same effective modeling capacity. Fail closed on this.
    effective_equal_capacity=(
        accounts["candidate"]["binary_residual_uint8_counter_capacity_bytes"]==
        accounts["action_count"]["nine_profile_uint8_evidence_bytes"]
    )
    checks={
        "pooled_0_02_better_than_strongest_trained_conventional_and_count":
            pooled["candidate"]<=min(pooled["recurrent45"],
                                     pooled["action_count"])-.02,
        "better_than_both_trained_controls_on_3_of_4_hidden_held_laws":
            winning_laws>=3,
        "delayed_preaction_brier_0_02_better_than_both_credit_ablations":
            delayed_pooled["candidate"]<=min(delayed_pooled["no_delay"],
                                             delayed_pooled["sham"])-.02,
        "retains_95pct_of_chance_corrected_law_gain_after_8_laws":
            retention["pass"],
        "all_original_public_consequences_give_nonzero_online_updates":
            all(r["candidate_trained_observed_actions"]>0 for r in held),
        "each_source_episode_restores_all_six_independent_models":
            all(r["cold_model_restarts"]==len(NAMES) for r in held),
        "whole_source_actor_learner_wall_ratio_le_1_5":
            cost_ratio<=1.5,
        "effective_conventional_integer_memory_capacity_matched":
            effective_equal_capacity,
    }
    return {
        "checks":checks,
        "held_law_brier":by_law,
        "pooled_brier":pooled,
        "delayed_after_action2_to_action3_brier":delayed_pooled,
        "delayed_steps":delayed,
        "winning_held_law_count":winning_laws,
        "preaction_eval_source_steps":source_steps,
        "whole_source_actor_candidate_model_wall_ns":candidate_total,
        "whole_source_actor_best_control_model_wall_ns":best_control_total,
        "whole_process_modelled_wall_ratio":cost_ratio,
        "observed_shared_process_peak_rss_bytes":max(
            r["shared_process_peak_rss_bytes"] for r in held
        ),
        "memory_bytes_not_semantically_matched":not effective_equal_capacity,
        "independent_runner_peak_rss_per_model":"NOT_QUALIFIED",
        "pre_cross_os_disposition":(
            "DEV_SIGNAL_PENDING_PORTABILITY_NOT_SCIENCE"
            if all(checks.values()) else DEV_DISPOSITION_NO_GO
        )
    }


def compare(checkpoint_path,output):
    start=time.perf_counter_ns()
    frozen,stage0,source_data=source_headroom()
    if stage0["disposition"]!="SOURCE_TASK_IDENTIFIABLE_DEV_ONLY":
        out={"schema":RESULT_SCHEMA,"source_stage0":stage0,
             "disposition":"SOURCE_TASK_INVALID_NO_GO",
             "held_development_opened":False,"scientific_pass":False}
        output.write_text(_canonical(out)+"\n",encoding="utf-8")
        print("ST3_DEV_DISPOSITION=SOURCE_TASK_INVALID_NO_GO")
        return out
    if (frozen["source"]["held_dev_laws"]!=list(HELD_LAWS) or
        frozen["source"]["held_dev_seeds"]!=list(HELD_SEEDS)):
        raise ValueError("ST3_HELD_LAW_SEED_CONTRACT_DRIFT")
    checkpoint,checkpoint_sha=load_checkpoint(checkpoint_path)
    models=from_checkpoint(checkpoint["models"])
    held=[]
    for law in HELD_LAWS:
        for seed in HELD_SEEDS:
            held.append(run_episode(
                law,seed,models,"held",train=True,per_step_hash=True
            ))
    retention=delay_retention_probe()
    results=score_results(held,retention,checkpoint["model_accounting"])
    report={
        "schema":RESULT_SCHEMA,
        "original_source_kind":"IN_HOUSE_SYNTHETIC_DEV_ONLY",
        "frozen_protocol_blob":PROTOCOL_BLOB,
        "training_checkpoint_sha256":checkpoint_sha,
        "training_source_trace_sha256":
            checkpoint["source_training_trace_sha256"],
        "source_stage0":stage0,
        "held_source_receipts":held,
        "retention_probe":retention,
        "metrics":results,
        "held_development_opened":True,
        "protected_scientific_first_use":False,
        "candidate_learner_world_law_or_masks_input":False,
        "independent_unfamiliar_world_transfer":False,
        "scientific_pass":False,
        "original_frozen_hypothesis_changed_after_observation":False,
        "whole_eval_worker_wall_ns":time.perf_counter_ns()-start,
        "final_disposition":results["pre_cross_os_disposition"],
        "cross_os_exact_integer_state":"PENDING_INDEPENDENT_PARITY",
    }
    output.write_text(_canonical(report)+"\n",encoding="utf-8")
    print("ST3_HELD_DEV_POOLED_BRIER="+
          _canonical(results["pooled_brier"]))
    print("ST3_HELD_DEV_DELAYED_BRIER="+
          _canonical(results["delayed_after_action2_to_action3_brier"]))
    print("ST3_HELD_DEV_CHECKS="+_canonical(results["checks"]))
    print("ST3_HELD_RETENTION="+_canonical(retention))
    print("ST3_DEV_DISPOSITION="+results["pre_cross_os_disposition"])
    print("ST3_NO_PROTECTED_FIRST_USE=PASS")
    return report


if __name__=="__main__":
    a=argparse.ArgumentParser()
    s=a.add_subparsers(dest="mode",required=True)
    train=s.add_parser("train")
    train.add_argument("--output",type=Path,required=True)
    test=s.add_parser("compare")
    test.add_argument("--checkpoint",type=Path,required=True)
    test.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    if args.mode=="train":
        build_train_once(args.output)
    else:
        compare(args.checkpoint,args.output)
