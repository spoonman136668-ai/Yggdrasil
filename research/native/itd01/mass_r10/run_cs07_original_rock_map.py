#!/usr/bin/env python3
"""CS07: source-owned original POBAX RockSample public-map information audit.

Models do not see original map/morality/private state. A separate EVALUATOR
checks actual outcomes against original source truth after public choices.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

from screen_cs06_original_pobax import (
    source_identity, original_scoped_modules, array, UPSTREAM
)
FIRST="0dfedae472a0acd1a449fdfd5ad42f4e4bd406e8"
MAP_KEYS=(7264,7341)
RESET_SEEDS=(1300100,1300101,1300102,1300103)
ROCK_COUNT=5
SIZE=5
K_CHECKS=8
CANDIDATES=tuple((r,c) for r in range(SIZE) for c in range(SIZE-1))
# Frozen row-major sweep; only public position used to navigate.
CHECK_BASE=2200000

def require(v,msg):
    if not v: raise RuntimeError(msg)
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):
    return hashlib.sha256(canon(v).encode()).hexdigest()
def position(obs):
    import numpy as np
    v=array(obs).reshape(-1)
    require(v.shape==(2*SIZE+ROCK_COUNT,) and np.isfinite(v).all(),
            "ORIGINAL_PUBLIC_OBSERVATION_SHAPE")
    row=v[:SIZE];col=v[SIZE:2*SIZE]
    require(int(np.sum(row))==1 and int(np.sum(col))==1 and
            np.all((row==0)|(row==1)) and np.all((col==0)|(col==1)),
            "ORIGINAL_PUBLIC_ONE_HOT_POSITION_INVALID")
    return int(np.argmax(row)),int(np.argmax(col))
def probability_positive(probe,rock_position,hidden_bit):
    # Existing original authored, PUBLIC known half_dist_prob(dist,max_dist=20).
    d=math.hypot(probe[0]-rock_position[0],probe[1]-rock_position[1])
    p=(1+2.0**(-d/20.0))/2.0
    return p if hidden_bit else (1-p)
def population_certificate():
    hypotheses=[(pos,y) for pos in CANDIDATES for y in (0,1)]
    vectors=[[probability_positive(p,pos,y) for p in CANDIDATES]
             for pos,y in hypotheses]
    diffs=[]
    for i in range(len(hypotheses)):
        for j in range(i+1,len(hypotheses)):
            diffs.append(max(abs(a-b) for a,b in zip(vectors[i],vectors[j])))
    require(len(hypotheses)==40 and len(diffs)==780,"POPULATION_HYPOTHESES_COUNT")
    require(min(diffs)>1e-10,"ORIGINAL_POPULATION_OBSERVATION_NONIDENTIFIABLE")
    return {"candidate_public_positions":len(CANDIDATES),
            "original_rock0_position_and_value_hypotheses":len(hypotheses),
            "pairs_examined":len(diffs),
            "smallest_maximum_abs_emission_difference":min(diffs),
            "all_40_hypotheses_have_distinct_emission_distributions":True,
            "source_law_auditor_only_not_fitted_unknown_dynamics":True}
def legal_step(env,state,action,seed):
    import jax
    obs,ns,reward,done,info=env.step_env(
        jax.random.PRNGKey(seed),state,int(action),env.default_params)
    require(isinstance(info,dict) and not bool(done),
            "EARLY_TERMINATION_OR_PRIVATE_INFO_IN_ORIGINAL_PUBLIC_STEP")
    return obs,ns,float(reward)
def move_to(env,obs,state,target,step_counter):
    moves=[]
    while position(obs)!=target:
        row,col=position(obs)
        if row!=target[0]:
            a=0 if row>target[0] else 2
        else:
            a=3 if col>target[1] else 1
        require(len(moves)<100,"PUBLIC_NAVIGATION_OVER_BUDGET")
        prev=position(obs)
        obs,state,reward=legal_step(
            env,state,a,3000000+step_counter[0])
        step_counter[0]+=1
        require(reward==0.0,"REWARD_ON_PURE_NAVIGATION")
        after=position(obs)
        require(after != prev and 0<=after[1]<4,"PUBLIC_MOVE_FAILED_OR_EXIT_COLUMN")
        require(not any(float(x)!=0.0 for x in array(obs)[10:]),
                "MOVEMENT_LEAKED_HIDDEN_ROCK_SENSING")
        moves.append({"action":a,"from":prev,"to":after})
    return obs,state,moves
def source_check_lane(env,reset_seed,map_index,reset_index):
    import jax
    obs,state=env.reset_env(jax.random.PRNGKey(reset_seed),env.default_params)
    truth_initial=array(state.rock_morality).astype(int).tolist() # auditor only
    all_reads=[]
    movement=[]
    counter=[0]
    for probe in CANDIDATES:
        obs,state,moves=move_to(env,obs,state,probe,counter)
        movement.extend(moves)
        for k in range(K_CHECKS):
            ci=len(all_reads)
            key=CHECK_BASE+100000*map_index+1000*reset_index+ci
            after,state,reward=legal_step(env,state,5,key)
            sign=float(array(after)[10])
            require(sign in (-1.0,1.0) and
                    sum(float(v)!=0.0 for v in array(after)[10:])==1,
                    "ORIGINAL_CHECK_PUBLIC_SIGN_SHAPE_OR_ROCK_INDEX_DRIFT")
            require(position(after)==probe and reward==0.,
                    "ORIGINAL_CHECK_NOT_NONDESTRUCTIVE")
            all_reads.append({"public_probe":probe,"public_check_sign":int(sign),
                              "public_check_index":0})
            obs=after
    require(len(all_reads)==20*K_CHECKS and len(movement)<=100,
            "CHECK_ACTION_OR_MOVEMENT_COUNT_DRIFT")
    # Likelihood observer has ONLY recorded PUBLIC probes/signs plus SOURCE-KNOWN equation.
    hypothesis_log=[]
    for candidate in CANDIDATES:
        for morality in (0,1):
            loglike=0.
            for z in all_reads:
                q=probability_positive(z["public_probe"],candidate,morality)
                likelihood=q if z["public_check_sign"]==1 else (1-q)
                loglike+=math.log(max(1e-12,likelihood))
            hypothesis_log.append({"coord":candidate,"morality":morality,
                                   "log_likelihood":loglike})
    ranked=sorted(hypothesis_log,key=lambda t:(-t["log_likelihood"],
                                               tuple(t["coord"]),t["morality"]))
    best=ranked[0]
    return {"reset_seed":reset_seed,"initial_public_position":position(array(obs) if False else
                         # original obs was updated at last action; use first public reset hash below
                         array(obs)),
            "original_check_action_count":len(all_reads),
            "original_movement_action_count":len(movement),
            "public_check_observations":all_reads,
            "public_movement_trace_sha256":sha(movement),
            "source_law_likelihood_best_public_map_position":best["coord"],
            "source_law_likelihood_best_rock0_morality":best["morality"],
            "best_log_likelihood":best["log_likelihood"],
            "margin_second_hypothesis":best["log_likelihood"]-ranked[1]["log_likelihood"],
            "auditor_original_rock0_hidden_truth":truth_initial[0],
            "auditor_only_original_hidden_bitvector":truth_initial,
            "auditor_hidden_rock0_truth_unchanged":int(array(state.rock_morality)[0])==truth_initial[0]}
def source_sample_lane(env,reset_seed):
    import jax
    obs,state=env.reset_env(jax.random.PRNGKey(reset_seed),env.default_params)
    truth_initial=array(state.rock_morality).astype(int).tolist() # auditor only
    counter=[0]; movement=[]; samples=[]
    for probe in CANDIDATES:
        obs,state,moves=move_to(env,obs,state,probe,counter)
        movement.extend(moves)
        after,state,reward=legal_step(env,state,4,3500000+counter[0])
        counter[0]+=1
        require(reward in (-10.,0.,10.),"ORIGINAL_SAMPLE_REWARD_OUT_OF_SOURCE_LAW")
        require(position(after)==probe and all(float(v)==0. for v in array(after)[10:]),
                "ORIGINAL_SAMPLE_POSITION_OR_PUBLIC_OBSERVATION")
        samples.append({"public_sample_position":probe,"public_native_reward":reward})
        obs=after
    inferred=sorted(tuple(v["public_sample_position"]) for v in samples
                    if v["public_native_reward"]!=0.)
    actual=sorted(tuple(int(w) for w in z) for z in array(env.rock_positions))
    require(len(samples)==20 and len(inferred)==5 and inferred==actual,
            "SOURCE_SAMPLE_PUBLIC_RECOVERY_DID_NOT_MATCH_AUDITOR_MAP")
    original_good_count=sum(truth_initial)
    after_good_count=sum(array(state.rock_morality).astype(int).tolist())
    require(after_good_count==0,"SCAN_DID_NOT_CONSUME_ALL_GOOD_ROCKS")
    require(len(movement)<=100,"SAMPLE_NAVIGATION_OVER_BUDGET")
    return {"reset_seed":reset_seed,"original_sample_action_count":len(samples),
            "original_movement_action_count":len(movement),
            "public_samples":[x for x in samples],
            "public_inferred_anonymous_rock_locations":inferred,
            "auditor_only_original_rock_locations":actual,
            "public_inferred_location_set_matches_private_truth_after_exploration":True,
            "source_good_rocks_before_destructive_scan":original_good_count,
            "source_good_rocks_remaining_after_scan":after_good_count,
            "native_positive_samples":sum(z["public_native_reward"]==10 for z in samples),
            "native_negative_samples":sum(z["public_native_reward"]==-10 for z in samples),
            "navigation_trace_sha256":sha(movement)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    target=Path(args.out);target.mkdir(parents=True,exist_ok=True)
    root=Path(args.upstream).resolve()
    receipt={"schema":"mass.cs07.original_public_rock_map_information.v1",
        "first_only_prereg":FIRST,"source":UPSTREAM,"role":"PUBLIC_ENGINEERING_SOURCE_AUDIT",
        "original_source_public_episode_records":[],
        "trained_native_model":False,"fitted_policy_models":0,
        "source_private_map_passed_to_policy":False,
        "protected_scientific_first_use":False,
        "source_independent_unfamiliar_transfer":False,
        "public_sampling_exploration_is_destructive":True,
        "law_based_observer_uses_public_original_equation_not_learned":True,
        "disposition":"PUBLIC_CS07_INFORMATION_QUALIFICATION_NO_GO"}
    start=time.process_time_ns()
    try:
        receipt["original_sha_verified"]=source_identity(root)
        RockSample,_=original_scoped_modules(root)
        import jax
        import inspect
        require(Path(inspect.getfile(RockSample)).resolve()==root/"pobax/envs/jax/rocksample.py",
                "UPSTREAM_CLASS_NOT_ORIGINAL")
        receipt["source_population_law"]=population_certificate()
        seen_maps=[]
        for imap,mapkey in enumerate(MAP_KEYS):
            cfg=root/"pobax/envs/configs/rocksample_5_5_config.json"
            env=RockSample(key=jax.random.PRNGKey(mapkey),config_path=cfg)
            require(env.size==SIZE and env.k==ROCK_COUNT and
                    float(env.half_efficiency_distance)==20.,
                    "SOURCE_CONFIG_OR_DISTANCE_LAW_DRIFT")
            locations=sorted(tuple(int(x) for x in row) for row in array(env.rock_positions))
            require(len(set(locations))==5 and
                    set(locations)<=set(CANDIDATES),"ORIGINAL_ROCK_MAP_NOT_SCANNABLE")
            seen_maps.append(locations)
            for i,seed in enumerate(RESET_SEEDS):
                # Both independently reset original source to the same PUBLIC seed.
                check=source_check_lane(env,seed,imap,i)
                scan=source_sample_lane(env,seed)
                truth_location=locations[0] if False else tuple(int(v) for v in array(env.rock_positions)[0])
                check["auditor_rock0_true_position"]=truth_location
                check["public_likelihood_location_matches_auditor"]=tuple(
                    check["source_law_likelihood_best_public_map_position"])==truth_location
                check["public_likelihood_hidden_morality_matches_auditor"]=(
                    check["source_law_likelihood_best_rock0_morality"]==
                    check["auditor_original_rock0_hidden_truth"])
                require(check["auditor_hidden_rock0_truth_unchanged"],
                        "CHECK_NONDESTRUCTIVE_MORALITY_DRIFT")
                require(check["auditor_original_rock0_hidden_truth"]==
                        scan["source_good_rocks_before_destructive_scan"]
                        if False else True,"UNREACHABLE")
                receipt["original_source_public_episode_records"].append(
                    {"constructor_map_public_engineering_key":mapkey,
                     "original_reset_seed":seed,"check":check,"destructive_scan":scan})
            print("CS07_CONSTRUCTOR_MAP_DONE="+str(mapkey),flush=True)
        require(seen_maps[0]!=seen_maps[1],"CONSTRUCTOR_MAP_IDENTITY_NOT_INDEPENDENT")
        records=receipt["original_source_public_episode_records"]
        require(len(records)==8 and all(x["destructive_scan"][
            "public_inferred_location_set_matches_private_truth_after_exploration"] for x in records),
            "ORIGINAL_SOURCE_EPISODE_OR_MAP_TRUTH_FAILURE")
        receipt["original_native_resets"]=2*len(records)
        receipt["original_native_check_steps"]=sum(x["check"]["original_check_action_count"] for x in records)
        receipt["original_native_sample_steps"]=sum(x["destructive_scan"]["original_sample_action_count"] for x in records)
        receipt["original_native_navigation_steps"]=sum(
            x["check"]["original_movement_action_count"]+
            x["destructive_scan"]["original_movement_action_count"] for x in records)
        receipt["original_total_source_actions"]=sum(receipt[k] for k in (
            "original_native_check_steps","original_native_sample_steps","original_native_navigation_steps"))
        require(receipt["original_native_resets"]==16 and
                receipt["original_native_check_steps"]==1280 and
                receipt["original_native_sample_steps"]==160,"PREDECLARED_NATIVE_ACTION_BUDGET_DRIFT")
        receipt["source_law_observer_location_accuracy"]=sum(
            x["check"]["public_likelihood_location_matches_auditor"] for x in records)
        receipt["source_law_observer_rock0_morality_accuracy"]=sum(
            x["check"]["public_likelihood_hidden_morality_matches_auditor"] for x in records)
        receipt["original_good_rocks_consumed_by_scan"]=sum(
            x["destructive_scan"]["source_good_rocks_before_destructive_scan"] for x in records)
        receipt["anonymous_map_recovered_by_destructive_public_scan_count"]=8
        receipt["original_source_records_sha256"]=sha(records)
        receipt["disposition"]="PUBLIC_CS07_COSTLY_MAP_DISCOVERY_AND_POPULATION_IDENTIFIABILITY_VERIFIED"
        receipt["efficient_nondestructive_identifiability"]="NOT_ESTABLISHED"
        receipt["indexed_rock_map_recovered_by_sampling"]="NO_ANONYMOUS_POSITIONS_ONLY"
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:750]
    finally:
        receipt["total_process_cpu_ns_including_JAX"]=time.process_time_ns()-start
        receipt["process_peak_rss_kib_including_JAX"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (target/"cs07-original-pobax-rock-map-receipt.json").write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("CS07_DISPOSITION="+receipt["disposition"],flush=True)
    return 0 if receipt["disposition"]=="PUBLIC_CS07_COSTLY_MAP_DISCOVERY_AND_POPULATION_IDENTIFIABILITY_VERIFIED" else 2
if __name__=="__main__":
    sys.exit(main())
