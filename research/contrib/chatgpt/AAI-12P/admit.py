"""AAI-12P preregistered source-only heterogeneous causal benchmark admission.

Eight fully fitted independent public-data controls, common training/actions,
cold restoration, real action consequences, oracle scoring evaluator only.
NO new native model and NO primary scientific world/seed first use.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import world,controls


def mean(values):
    if not values:raise ValueError("empty source condition")
    return sum(values)/len(values)


def digest(value):
    return hashlib.sha256(controls.canonical(value).encode()).hexdigest()


def train(key):
    world.fixture(key)
    actors={name:controls.Control(name) for name in controls.METHODS}
    evidence=[]
    durations={name:0. for name in controls.METHODS}
    for law in world.FIT:
        for i in range(8):
            for row in world.pair(law,key,"fit",i):
                evidence.append(row)
                for name,actor in actors.items():
                    tic=time.perf_counter()
                    actor.observe(world.copy_public(row))
                    durations[name]+=time.perf_counter()-tic
    if len(evidence)!=64 or any(set(r)!=world.PUBLIC_KEYS for r in evidence):
        raise AssertionError("unequal or private public training budget")
    saved={}
    for name,actor in actors.items():
        tic=time.perf_counter()
        actor.fit_checkpoint()
        saved[name]=controls.checkpoint(actor)
        if controls.checkpoint(controls.restore(name,saved[name]))!=saved[name]:
            raise AssertionError("post-training independent cold provenance drift")
        durations[name]+=time.perf_counter()-tic
    return saved,tuple(evidence),durations


def challenge(name,after_fit,law,key,corrupt=False):
    if name not in controls.METHODS:
        raise ValueError("unapproved conventional control")
    world.law_name(law)
    actor=controls.restore(name,after_fit)
    pairs=[world.pair(law,key,"challenge",i) for i in range(4)]
    if corrupt:
        # Deliberately destroy which actual intervention caused which output,
        # preserving the exact multiset of resulting observed mediators.
        labels=[tuple(p[1]["mediators"]) for p in pairs]
        permuted=[labels[(i+1)%len(labels)] for i in range(len(labels))]
        if sorted(labels)!=sorted(permuted):
            raise AssertionError("negative changed mediator marginal multiset")
        altered=[]
        for (pre,post),fake in zip(pairs,permuted):
            post=world.copy_public(post)
            post["mediators"]=list(fake)
            post["reward"]=world.reward(fake,post["goal"],post["actions_taken"])
            world.visible(post)
            altered.append((pre,post))
        pairs=altered
    for pre,post in pairs:
        actor.observe(world.copy_public(pre))
        actor.observe(world.copy_public(post))
    actor.fit_checkpoint()
    frozen=controls.checkpoint(actor)
    if controls.checkpoint(controls.restore(name,frozen))!=frozen:
        raise AssertionError("challenge cold structural model changed")
    return frozen


def episode(name,snapshot,law,x,goal):
    actor=controls.restore(name,snapshot)
    row=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(row))
    actions=[]
    for _ in range(2):
        selected=actor.choose(world.copy_public(row))
        if selected is None:break
        if selected not in world.ACTIONS:
            raise AssertionError("control invented invalid do-action")
        row=world.copy_public(world.do(law,row,selected))
        actions.append(world.ACTIONS.index(selected))
        actor.observe(world.copy_public(row))
    if len(actions)!=row["actions_taken"]:
        raise AssertionError("real intervention budget exceeded")
    return row["reward"],int(tuple(row["mediators"])==tuple(goal)),actions


def source_oracle(law,positions):
    # NEVER feed exact law/optimal actions or attainable flag into any model.
    return tuple(world.exact_oracle(law,x,goal) for x,goal in positions)


def _flatten(records):
    valid=[v for v in records if v["reachable"]]
    impossible=[v for v in records if not v["reachable"]]
    if not records or len(valid)+len(impossible)!=len(records):
        raise AssertionError("missing baseline evaluation records")
    if any(v["hit"] and not v["reachable"] for v in records):
        raise AssertionError("model hit a mathematically impossible exact goal")
    if any(v["reward"]>v["oracle"]+1e-9 for v in records):
        raise AssertionError("matched model exceeded exact-law privileged oracle")
    return {
        "mean_reward":round(mean([r["reward"] for r in records]),9),
        "exact_goals_reached":sum(int(r["hit"]) for r in records),
        "oracle_reachable_goals":len(valid),
        "oracle_relative_goal_recovery":round(
            sum(int(r["hit"]) for r in valid)/len(valid),9) if valid else None,
        "oracle_unreachable_goal_regret":round(
            mean([r["oracle"]-r["reward"] for r in impossible]),9
        ) if impossible else None,
        "oracle_reward_regret":round(mean([r["oracle"]-r["reward"] for r in records]),9),
        "average_real_actions":round(mean([len(r["actions"]) for r in records]),9)
    }


def admission():
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (p["id"]!="AAI-12P" or p["safety"]["science_cohorts_used"] or
        not p["safety"]["no_scientific_first_use"]):
        raise PermissionError("AAI12P SCIENTIFIC FIRST USE DISARMED")
    frozen=p["pre_registered_admission"]
    if (tuple(p["controls"]["eligible"])!=controls.METHODS or
        tuple(p["world_design"]["source_only_transfer_worlds"])!=world.TRANSFER or
        tuple(p["world_design"]["source_only_fit_worlds"])!=world.FIT or
        tuple(p["world_design"]["fixture_names"])!=world.FIXTURES):
        raise AssertionError("pre-registered models, worlds or fixtures changed")
    start=time.perf_counter()
    mechanic=world.mechanical_probe()
    structural={
        "source_structural_signature_uniqueness":
            mechanic["source_world_truth_signature_count"]>=frozen["structural_signature_uniqueness_min"],
        "pairwise_one_step_identifiability":
            mechanic["all_law_pairwise_distinguishability_min"]>=
            frozen["minimum_pairwise_one_step_observable_distinguishability_fraction"],
        "actual_do_actions_consequential":
            mechanic["real_first_action_outcome_change_fraction"]>=
            frozen["minimum_fraction_real_first_actions_change_a_mediator"],
        "real_intervention_reward_opportunities":
            mechanic["positive_intervention_opportunity_fraction"]>=
            frozen["minimum_fraction_contexts_with_positive_oracle_intervention_reward_gain"]
    }
    # For structural fail, do not consume even mechanical matched-control scoring.
    if not all(structural.values()):
        return {"schema":"yggdrasil.aai12p.source-only-benchmark-admission.v1",
                "classification":"BENCHMARK_NO_GO_STRUCTURAL",
                "checks":structural,"mechanics":mechanic,
                "science_cohorts_consumed":0,
                "source_only_wall_seconds":round(time.perf_counter()-start,5)}

    trace=[]
    training=[]
    all_scores={name:[] for name in controls.METHODS}
    familiar={name:[] for name in controls.METHODS}
    wall={name:0. for name in controls.METHODS}
    matched_oracle=[]
    stop_rewards=[]
    reactive_rewards=[]
    negative_recent16=[]
    corpus_digest=[]
    for key in world.FIXTURES:
        saved,evidence,cost=train(key)
        corpus_digest.append(digest(evidence))
        for name in controls.METHODS:
            wall[name]+=cost[name]
        training.append([key,*[digest(saved[name]) for name in controls.METHODS]])
        for law in world.TRANSFER:
            positions=world.contexts(key,law)
            if len(positions)!=8 or len(set(positions))!=8:
                raise AssertionError("fixed source context selection changed")
            privileged=source_oracle(law,positions)
            snapshots={}
            for name in controls.METHODS:
                tick=time.perf_counter()
                snapshots[name]=challenge(name,saved[name],law,key)
                wall[name]+=time.perf_counter()-tick
            negative_snap=challenge("causal_structure_recent16",
                                    saved["causal_structure_recent16"],law,key,True)
            for (x,goal),(optimum,reachable) in zip(positions,privileged):
                matched_oracle.append((optimum,reachable))
                stop_rewards.append(world.start(law,x,goal)["reward"])
                chosen=world.ACTIONS[(sum(x)+3*sum(goal))%len(world.ACTIONS)]
                reactive_rewards.append(world.do(law,world.start(law,x,goal),
                                                 chosen)["reward"])
                for name in controls.METHODS:
                    tic=time.perf_counter()
                    reward,hit,actions=episode(name,snapshots[name],law,x,goal)
                    wall[name]+=time.perf_counter()-tic
                    all_scores[name].append({
                        "reward":reward,"hit":hit,"actions":actions,
                        "oracle":optimum,"reachable":reachable,"law":law
                    })
                    trace.append([key,law,name,list(x),list(goal),
                                  round(reward,9),hit,actions,reachable])
                score,_,_=episode("causal_structure_recent16",negative_snap,
                                  law,x,goal)
                negative_recent16.append(score)
        # Hold out original familiar laws by cold restoration, no source replay.
        for law in world.FIT:
            positions=world.contexts(key,law)
            for name in controls.METHODS:
                tick=time.perf_counter()
                after=challenge(name,saved[name],law,key)
                for x,goal in positions:
                    reward,_,_=episode(name,after,law,x,goal)
                    familiar[name].append(reward)
                wall[name]+=time.perf_counter()-tick
        for name in controls.METHODS:
            if controls.checkpoint(controls.restore(name,saved[name]))!=saved[name]:
                raise AssertionError("original familiar/transfer episodes polluted training")

    if (len(matched_oracle)!=frozen["source_transfer_episodes"] or
        any(len(s)!=frozen["source_transfer_episodes"] for s in all_scores.values()) or
        any(len(s)!=frozen["source_familiar_episodes"] for s in familiar.values())):
        raise AssertionError("frozen world×condition×method budget drift")
    eligible={name:_flatten(records) for name,records in all_scores.items()}
    strongest=max(controls.METHODS,key=lambda name:eligible[name]["mean_reward"])
    best_recovery=max(controls.METHODS,key=lambda name:
                      eligible[name]["oracle_relative_goal_recovery"] or 0.)
    strongest_mean=eligible[strongest]["mean_reward"]
    oracle_reward=mean([reward for reward,_ in matched_oracle])
    attainable=sum(int(reachable) for _,reachable in matched_oracle)
    oracle_headroom=oracle_reward-strongest_mean
    recovery_headroom=1-(eligible[best_recovery]["oracle_relative_goal_recovery"] or 0.)
    negative_actual_mean=mean(negative_recent16)
    original_structural_mean=eligible["causal_structure_recent16"]["mean_reward"]
    gates={
        **structural,
        "exact_eight_eligible_fully_fitted_controls":len(eligible)==frozen["controls_count"],
        "oracle_reward_headroom":
            oracle_headroom>=frozen["minimum_oracle_reward_headroom_over_best_fully_trained_conventional"],
        "attainable_exact_goal_headroom":
            recovery_headroom>=frozen["minimum_oracle_reachable_goal_recovery_headroom_over_best_control"],
        "nontrivial_exact_goal_reachability":
            (frozen["minimum_exact_goals_reachable_fraction"]<=
             attainable/len(matched_oracle)<=
             frozen["maximum_exact_goals_reachable_fraction"]),
        "strongest_beats_actual_STOP":
            strongest_mean-mean(stop_rewards)>=frozen["minimum_strong_control_reward_above_STOP"],
        "strongest_beats_blind_reactive":
            strongest_mean-mean(reactive_rewards)>=frozen["minimum_strong_control_reward_above_reactive"],
        "broken_intervention_association_negative_not_better":
            original_structural_mean>=negative_actual_mean-1e-10
    }
    classification=("BENCHMARK_ADMITTED_FOR_NEW_PROSPECTIVE_SOURCE_DEVELOPMENT"
                    if all(gates.values()) else "BENCHMARK_NO_GO_NO_SCIENCE")
    return {
        "schema":"yggdrasil.aai12p.source-only-benchmark-admission.v1",
        "classification":classification,"checks":gates,
        "source_mechanics":mechanic,
        "strongest_matched_fully_trained_control":strongest,
        "strongest_reachable_goal_control":best_recovery,
        "mean_privileged_exact_law_0_to_2_action_oracle":round(oracle_reward,9),
        "mean_actual_STOP_without_do":round(mean(stop_rewards),9),
        "mean_blind_one_do_reactive":round(mean(reactive_rewards),9),
        "source_oracle_reward_headroom":round(oracle_headroom,9),
        "source_oracle_reachable_goal_fraction":round(attainable/len(matched_oracle),9),
        "source_oracle_reachable_goal_headroom":round(recovery_headroom,9),
        "corrupted_do_outcome_association_causal_recent16_mean_reward":round(negative_actual_mean,9),
        "intact_causal_recent16_mean_reward":round(original_structural_mean,9),
        "frozen_controls":eligible,
        "familiar_cold_return":{k:round(mean(v),9) for k,v in familiar.items()},
        "measured_source_train_fit_challenge_cold_actual_action_seconds_by_method":{
            k:round(v,5) for k,v in wall.items()},
        "source_training_public_corpus_sha256":digest(corpus_digest),
        "public_training_cold_checkpoint_sha256":digest(training),
        "all_matched_actual_action_reward_trace_sha256":digest(trace),
        "actual_transfer_episodes_per_method":len(matched_oracle),
        "actual_familiar_episodes_per_method":64,
        "all_worlds_source_only":True,"science_cohorts_consumed":0,
        "new_learner_or_native_model_changed":False,
        "source_only_wall_seconds":round(time.perf_counter()-start,4)
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-admission",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("AAI12P SCIENTIFIC FIRST USE DISARMED")
    if not args.source_admission:
        p.error("only frozen source-only mechanical evaluation; no scientific first use")
    print("AAI12P_ADMISSION="+json.dumps(admission(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
