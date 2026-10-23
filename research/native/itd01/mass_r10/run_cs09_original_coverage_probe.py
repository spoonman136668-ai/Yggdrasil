#!/usr/bin/env python3
"""CS09 original POBAX RockSample: coverage-constrained versus classical active sensing.

PUBLIC source experiment: source-known 40-state Bayesian laws; no novel
native learner, no protected independent first use, no original source edits.
Original source-private truth used ONLY by an evaluator after all policies act.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

from run_cs08_original_active_rock_probe import (
    Posterior, POSITIONS, ARMS as OLD_ARMS, source_position, navigate,
    legal_step, source_identity, original_scoped_modules, array, UPSTREAM,
    entropy,
)

FIRST="26ac88d753816180b22b5ecc8c8e1b3dc42838f7"
MAP_KEYS=(7517,7531,7541)
RESET_SEEDS=(1600400,1600401,1600402,1600403)
POLICIES=("coverage_movement_penalized_MI","unconstrained_MI","uniform_row_major","seeded_random")
BLOCKS=20
READINGS=8
CHECKS=BLOCKS*READINGS

def need(test,why):
    if not test:
        raise RuntimeError(why)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def mdist(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])

def new_coverage_choice(block,posterior,current,counts):
    """Use only public positions, previous probes and source-known posterior."""
    need(len(counts)==20 and sum(counts)==block,"PUBLIC_COVERAGE_HISTORY_DRIFT")
    if block<10:
        unseen=[i for i in range(20) if counts[i]==0]
        need(unseen,"INSUFFICIENT_UNVISITED_PUBLIC_POSITIONS")
        if block==0:
            return min(unseen,key=lambda i:(mdist(current,POSITIONS[i]),i))
        visited=[POSITIONS[i] for i in range(20) if counts[i]>0]
        mind={i:min(mdist(POSITIONS[i],old) for old in visited) for i in unseen}
        farthest=max(mind.values())
        return min((i for i in unseen if mind[i]==farthest),
                   key=lambda i:(mdist(current,POSITIONS[i]),i))
    allowed=[i for i in range(20) if counts[i]<=1]
    need(allowed,"COVERAGE_CAP_EXHAUSTED")
    # Frozen source-law known information targeting plus explicit travel penalty.
    scores={i:posterior.coordinate_information(i)-0.001*mdist(current,POSITIONS[i])
            for i in allowed}
    best=max(scores.values())
    return min((i for i in allowed if best-scores[i]<=1e-12),
               key=lambda i:(mdist(current,POSITIONS[i]),i))

def select(policy,block,posterior,current,counts,rng):
    if policy==POLICIES[0]:
        return new_coverage_choice(block,posterior,current,counts)
    if policy==POLICIES[1]:
        # Exact CS08 unconstrained original-law coordinate MI selector,
        # without any coverage cap or private rock-map access.
        from run_cs08_original_active_rock_probe import choose
        return choose(OLD_ARMS[0],block,posterior,current,rng)
    if policy==POLICIES[2]:
        return block
    need(policy==POLICIES[3],"NOT_AN_AUTHORIZED_FROZEN_POLICY")
    return rng.randrange(20)

def original_episode(env,imap,trial,policy,reset_seed):
    import jax
    obs,state=env.reset_env(jax.random.PRNGKey(reset_seed),env.default_params)
    need(array(obs).shape==(15,) and all(float(x)==0. for x in array(obs)[10:]),
         "ORIGINAL_RESET_PUBLIC_OBSERVATION_DRIFT")
    initial=source_position(obs)
    prior=Posterior()
    rng=random.Random(6300000+1000*imap+trial)
    counts=[0]*20
    movements=[]
    blocks=[]
    t0=time.process_time_ns()
    for block in range(BLOCKS):
        current=source_position(obs)
        idx=select(policy,block,prior,current,counts,rng)
        need(type(idx) is int and 0<=idx<20,"OUTSIDE_LEGAL_PUBLIC_PROBE_SET")
        coordinate=POSITIONS[idx]
        obs,state,move_count=navigate(env,obs,state,coordinate,imap,trial,movements)
        counts[idx]+=1
        signs=[]
        for j in range(READINGS):
            check_num=prior.updates
            obs,state=legal_step(
                env,state,5,4500000+100000*imap+1000*trial+check_num)
            v=array(obs)
            need(v.shape==(15,) and source_position(v)==coordinate
                 and float(v[10]) in (-1.,1.)
                 and all(float(x)==0. for x in v[11:]),
                 "ORIGINAL_NONDESTRUCTIVE_CHECK_OUTPUT_INVALID")
            sign=int(v[10])
            prior.update(idx,sign)
            signs.append(sign)
        need(len(signs)==8,"FROZEN_SENSOR_READINGS_PER_BLOCK_DRIFT")
        blocks.append({"block":block,"original_public_position":coordinate,
                       "native_moves_to_position":move_count,
                       "original_public_rock0_sensor_signs":signs})
    need(len(blocks)==20 and prior.updates==160
         and sum(counts)==20 and len(movements)<=200,
         "SOURCE_PUBLIC_BUDGET_OR_ACTION_DRIFT")
    if policy==POLICIES[0]:
        need(len([x for x in counts if x>0])>=10 and max(counts)<=2,
             "FROZEN_COVERAGE_CONSTRAINT_VIOLATION")
    chosen,hidden_bit,coords=prior.estimate()
    # All public policy choices frozen here. No inference from private map.
    private_true_coord=tuple(int(v) for v in array(env.rock_positions)[0])
    private_true_bit=int(array(state.rock_morality)[0])
    need(private_true_coord in POSITIONS and private_true_bit in (0,1),
         "AUDITOR_ONLY_ORIGINAL_SOURCE_TRUTH_DRIFT")
    truth_idx=POSITIONS.index(private_true_coord)
    posterior_prob=coords[truth_idx]
    return {
        "source_constructor_key_public_cohort":MAP_KEYS[imap],
        "source_reset_seed_public_cohort":reset_seed,
        "policy":policy,"original_source_reset_calls":1,
        "original_source_CHECK_action_calls":prior.updates,
        "original_source_move_action_calls":len(movements),
        "original_source_total_actions":prior.updates+len(movements),
        "original_source_check_and_move_reward":0.,
        "original_public_start_position":initial,
        "public_original_sensor_and_location_trace":blocks,
        "public_original_movement_trace_sha256":digest(movements),
        "public_original_unique_locations":sum(x>0 for x in counts),
        "public_location_visitation_blocks":counts,
        "posterior_final_40_hypotheses_sha256":digest(prior.state()),
        "posterior_final_joint_40_hypotheses":prior.p,
        "public_predicted_rock0_coordinate":chosen,
        "public_predicted_rock0_hidden_value":hidden_bit,
        "public_final_coordinate_entropy_nats":entropy(coords),
        "auditor_only_native_true_coordinate":private_true_coord,
        "auditor_only_native_true_hidden_rock0":private_true_bit,
        "auditor_only_correct_location":int(chosen==private_true_coord),
        "auditor_only_correct_hidden_bit":int(hidden_bit==private_true_bit),
        "auditor_only_probability_true_location":posterior_prob,
        "auditor_only_negative_log_probability_true_location_nats":
            -math.log(max(1e-300,posterior_prob)),
        "cpu_ns_including_original_JAX_and_policy":time.process_time_ns()-t0,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    source=Path(args.upstream).resolve()
    receipt={
        "schema":"mass.cs09.original_source_coverage_placement.v1",
        "frozen_FIRST_commit":FIRST,"original_POBAX_source":UPSTREAM,
        "source_role":"PUBLIC_DEVELOPMENT_ONLY",
        "source_original_unmodified":False,
        "only_source_known_conventional_bayesian_policies":True,
        "model_acting_on_original_hidden_map_or_state":False,
        "native_Wingless_or_Yggdrasil_cognitive_model_trained":False,
        "genuine_sealed_unfamiliar_source_first_use":False,
        "CKB_scientific_controller_admission":False,
        "source_reward_or_rock_consumption":0,
        "model_CPU_RSS_isolation_qualified":False,
        "disposition":"PUBLIC_CS09_SOURCE_OR_PROTOCOL_INVALID",
        "original_public_cases":[]}
    total_start=time.process_time_ns()
    try:
        receipt["source_identity"]=source_identity(source)
        RockSample,_=original_scoped_modules(source)
        need(Path(inspect.getfile(RockSample)).resolve() ==
             source/"pobax/envs/jax/rocksample.py","SOURCE_ROCKSAMPLE_CLASS_IS_NOT_ORIGINAL")
        import jax
        original_map_identities=[]
        for imap,key in enumerate(MAP_KEYS):
            cfg=source/"pobax/envs/configs/rocksample_5_5_config.json"
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            need(env.size==5 and env.k==5
                 and float(env.half_efficiency_distance)==20.0,
                 "ORIGINAL_ENVIRONMENT_CONFIG_CHANGED")
            coords=[tuple(int(x) for x in r) for r in array(env.rock_positions)]
            need(len(set(coords))==5 and set(coords)<=set(POSITIONS),
                 "ORIGINAL_SOURCE_MAP_INVALID")
            original_map_identities.append(tuple(coords))
            for trial,reset_seed in enumerate(RESET_SEEDS):
                cohort=[original_episode(env,imap,trial,policy,reset_seed)
                        for policy in POLICIES]
                native_truth={(tuple(z["auditor_only_native_true_coordinate"]),
                               z["auditor_only_native_true_hidden_rock0"]) for z in cohort}
                need(len(native_truth)==1,
                     "PAIRED_ORIGINAL_RESETS_DID_NOT_MATCH_HIDDEN_STATE")
                receipt["original_public_cases"].append({
                    "constructor_source_key":key,
                    "original_reset_public_seed":reset_seed,
                    "four_original_source_policy_episodes":cohort})
            print("CS09_MAP_COMPLETED="+str(key),flush=True)
        need(len(set(original_map_identities))==3 and len(receipt["original_public_cases"])==12,
             "SOURCE_MAP_ROLE_COLLISION_OR_MISSING_CASES")
        scores={}
        for policy in POLICIES:
            rows=[next(z for z in c["four_original_source_policy_episodes"]
                       if z["policy"]==policy) for c in receipt["original_public_cases"]]
            need(len(rows)==12 and all(z["original_source_CHECK_action_calls"]==160 for z in rows),
                 "SENSOR_CHECK_BUDGET_NOT_IDENTICAL")
            scores[policy]={
                "original_source_episode_count":len(rows),
                "correct_native_rock0_location_out_of_12":sum(z["auditor_only_correct_location"] for z in rows),
                "correct_native_rock0_value_out_of_12":sum(z["auditor_only_correct_hidden_bit"] for z in rows),
                "mean_true_coordinate_NLL_nats":sum(z["auditor_only_negative_log_probability_true_location_nats"] for z in rows)/12.,
                "mean_posterior_probability_true_rock0_coordinate":sum(z["auditor_only_probability_true_location"] for z in rows)/12.,
                "mean_coordinate_entropy_nats":sum(z["public_final_coordinate_entropy_nats"] for z in rows)/12.,
                "source_native_CHECK_actions":sum(z["original_source_CHECK_action_calls"] for z in rows),
                "source_native_movement_actions":sum(z["original_source_move_action_calls"] for z in rows),
                "total_source_native_actions":sum(z["original_source_total_actions"] for z in rows),
                "mean_source_native_total_actions_per_episode":sum(z["original_source_total_actions"] for z in rows)/12.,
                "mean_distinct_probe_positions":sum(z["public_original_unique_locations"] for z in rows)/12.,
                "cpu_ns_including_original_JAX_source_and_policy":sum(z["cpu_ns_including_original_JAX_and_policy"] for z in rows),
                "individual_original_case_auditor_MAP_correct":[z["auditor_only_correct_location"] for z in rows],
                "individual_original_case_true_coordinate_NLL_nats":[z["auditor_only_negative_log_probability_true_location_nats"] for z in rows],
            }
        receipt["policy_comparison"]=scores
        candidate=scores[POLICIES[0]]
        controls=[scores[p] for p in POLICIES[1:]]
        criterion=all(candidate["correct_native_rock0_location_out_of_12"] >=
                      x["correct_native_rock0_location_out_of_12"]+3 and
                      candidate["mean_true_coordinate_NLL_nats"] <=
                      x["mean_true_coordinate_NLL_nats"]-.10 for x in controls)
        criterion=criterion and candidate["mean_source_native_total_actions_per_episode"] <= scores[POLICIES[2]]["mean_source_native_total_actions_per_episode"]
        receipt["preregistered_all_metric_criterion_met"]=criterion
        receipt["original_source_reset_calls"]=48
        receipt["original_source_CHECK_actions"]=sum(z["source_native_CHECK_actions"] for z in scores.values())
        receipt["original_source_movement_actions"]=sum(z["source_native_movement_actions"] for z in scores.values())
        receipt["original_source_total_actions"]=sum(z["total_source_native_actions"] for z in scores.values())
        need(receipt["original_source_CHECK_actions"]==7680,
             "FROZEN_TOTAL_NATIVE_CHECK_ACTION_DRIFT")
        receipt["original_public_case_evidence_SHA256"]=digest(receipt["original_public_cases"])
        receipt["disposition"]=("PUBLIC_CS09_COVERAGE_ADAPTIVE_ALL_METRIC_GAIN" if criterion
                               else "PUBLIC_CS09_NO_COVERAGE_ADAPTIVE_ADVANCEMENT")
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:900]
    finally:
        receipt["process_cpu_ns_all_including_original_source"]=time.process_time_ns()-total_start
        receipt["process_inclusive_max_RSS_KiB_not_model_isolation"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs09-original-source-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS09_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS09_SOURCE_OR_PROTOCOL_INVALID" else 0

if __name__=="__main__":
    sys.exit(main())
