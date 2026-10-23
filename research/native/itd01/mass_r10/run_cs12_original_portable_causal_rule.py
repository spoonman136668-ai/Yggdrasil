#!/usr/bin/env python3
"""CS12: prospective original POBAX rewarded portable causal matching.

Authentic original-source reset_env/step_env reward episodes only; all public
FIT observations/rewards. Source-private map and morality AUDITOR ONLY after
every source-native acting policy is finished. No native cognitive agent.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
import resource
import sys
import time

from screen_cs06_original_pobax import (
    source_identity,original_scoped_modules,array,UPSTREAM,
)
from run_cs10_original_rewarded_cross_episode import (
    SOURCE_MAP_CELLS,correlation_matrix,map_from_weights,
    need,canonical,digest,
)
from run_cs11_original_new_map_transfer import PublicSourceEpisode

FIRST="4ba9cda4083d8c0bc9c622e0828ee5d9edec2195"
OLD_MAP_KEYS=(7673,7687)
NEW_MAP_KEYS=(7919,7933,7949)
SOURCE_N=24
TARGET_N=4
DEV_N=48
BUDGETS=(1,2,4)
H_GRID=(5.,10.,20.,40.,80.)
ARMS=(
    "source_fitted_causal_assignment",
    "exact_source_law_bayesian_assignment",
    "target_batch_covariance",
    "target_episodic_correlation",
    "source_prior_coordinates",
    "target_inventory_no_goodness",
    "exit_only",
)
ALL_PERMUTATIONS=tuple(itertools.permutations(range(5)))
assert len(ALL_PERMUTATIONS)==120
def source_seed(group,mi,episode):
    return {"source":2400000,"target":2500000,"dev":2600000}[group]+10000*mi+episode
def sha(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def public_fit_episode(env,group,mi,i):
    e=PublicSourceEpisode(env,source_seed(group,mi,i),"FIT",mi,i)
    start_position=e.initial_public_position
    public_signs=[e.check(j) for j in range(5)]
    samples=[]
    for cell in SOURCE_MAP_CELLS:
        e.move_to(cell)
        r=e.sample()
        samples.append({"public_position":cell,"original_source_reward":r})
    e.exit()
    end=e.result()
    need(end["original_check_actions"]==5 and
         end["original_sample_actions"]==20 and
         end["original_source_exit_reward"]==10,
         "PUBLIC_FIT_SOURCE_ACTION_DRIFT")
    return {
        "source_role":group,"map":mi,"episode":i,
        "public_initial_position":start_position,
        "public_source_check_sign_by_index":public_signs,
        "public_native_sample_rewards_by_position":samples,
        "original_source_reward_and_actions":end,
    }
def public_rows(fits):
    out=[]
    for z in fits:
        signs=z["public_source_check_sign_by_index"]
        sample=z["public_native_sample_rewards_by_position"]
        need(len(signs)==5 and set(signs)<=set((-1,1)) and len(sample)==20,
             "FIT_SOURCE_DATA_INVALID")
        rews=[]
        for p,entry in enumerate(sample):
            need(tuple(entry["public_position"])==SOURCE_MAP_CELLS[p],
                 "PUBLIC_FIT_LOCATION_ORDER_DRIFT")
            r=entry["original_source_reward"]
            need(r in (-10.,0.,10.),"PUBLIC_FIT_ORIGINAL_REWARD_NOT_NATIVE")
            rews.append(int(r/10))
        need(sum(x!=0 for x in rews)==5,"PUBLIC_FIT_NOT_FIVE_REAL_ROCKS")
        out.append({"checks":signs,"reward10":rews,
                    "position":z["public_initial_position"]})
    return out
def public_inventory(rows):
    positions=[i for i in range(20) if rows[0]["reward10"][i]!=0]
    need(len(positions)==5,"FIT_ANONYMOUS_ROCK_INVENTORY_INVALID")
    for row in rows:
        need([i for i in range(20) if row["reward10"][i]!=0]==positions,
             "SOURCE_CHANGED_ROCK_COORDINATES_BETWEEN_FIT_EPISODES")
    return tuple(positions)
def original_law_probability(public_probe,coordinate,good_bit,h):
    d=math.hypot(public_probe[0]-coordinate[0],
                 public_probe[1]-coordinate[1])
    reliability=(1.0+2.0**(-d/h))/2.
    return reliability if good_bit else (1.-reliability)
def sign_log_likelihood(sign,truth,p,h):
    coord=SOURCE_MAP_CELLS[p]
    q=original_law_probability(tuple(truth["position"]),coord,
                                int(truth["reward10"][p]>0),h)
    likelihood=q if sign==1 else (1.-q)
    return math.log(likelihood) if likelihood>0 else -math.inf
def fitted_source_scale(source_records):
    """Fit ONE portable scalar from source publicly inferred assignments.

    Public source-map assignments are learned from genuine FIT source rewards,
    never read from the true env private rock map.
    """
    need(len(source_records)==2 and
         all(len(rows)==SOURCE_N for rows in source_records),
         "PUBLIC_SOURCE_META_FIT_ROLE_DRIFT")
    records=[]
    maps=[]
    for rows in source_records:
        weights=correlation_matrix(rows)
        inferred=map_from_weights(weights)
        need(len(set(inferred))==5,"OLD_SOURCE_PUBLIC_ASSOCIATION_COLLISION")
        map_indices=[SOURCE_MAP_CELLS.index(tuple(coord)) for coord in inferred]
        need(set(map_indices)==set(public_inventory(rows)),
             "SOURCE_INFERRED_MAP_NOT_IN_PUBLIC_REWARD_INVENTORY")
        maps.append(inferred)
        for row in rows:
            for rockidx,index_position in enumerate(map_indices):
                records.append((row["checks"][rockidx],row,index_position))
    options={}
    for h in H_GRID:
        total=0.
        for sign,row,p in records:
            value=sign_log_likelihood(sign,row,p,h)
            total+=value
        options[str(int(h))]=total
    # If a source-known model predicts an impossible check due to an erroneous
    # estimated map, preserve negative; no source-truth rescue.
    need(any(math.isfinite(v) for v in options.values()),
         "ALL_SOURCE_FITTED_NOISE_LIKELIHOODS_INVALID")
    best=max(H_GRID,key=lambda h:(options[str(int(h))],-abs(h-20.),-h))
    return best,{"source_calibration_grid_log_likelihood":options,
                 "FIT_learned_source_index_maps":maps,
                 "chosen_source_fitted_sensor_half_distance":best,
                 "source_original_public_training_check_likelihood_count":len(records),
                 "meta_model_fitted_from_original_source_public_data":True}
def score_permutation(perm,rows,h,inventory):
    # One-to-one assignment from original public CHECK index -> the five
    # *anonymous* coordinates recovered by real FIT sampling.
    score=0.
    for row in rows:
        for i,j in enumerate(perm):
            value=sign_log_likelihood(row["checks"][i],row,inventory[j],h)
            score+=value
    return score
def infer_assignment(rows,h):
    inventory=public_inventory(rows)
    scored=[(score_permutation(perm,rows,h,inventory),perm)
            for perm in ALL_PERMUTATIONS]
    bestscore=max(scored,key=lambda a:a[0])[0]
    need(math.isfinite(bestscore),"FIT_PERMUTATION_NO_FINITE_SOURCE_LIKELIHOOD")
    winner=min(p for value,p in scored if abs(value-bestscore)<=1e-10)
    assigned=tuple(SOURCE_MAP_CELLS[inventory[j]] for j in winner)
    need(len(set(assigned))==5,"FITTED_CAUSAL_ASSIGNMENT_COLLISION")
    return assigned,{
        "method":"exact_120_public_reward_likelihood_assignments",
        "sensor_h":h,"target_fitted_episodes":len(rows),
        "public_inventory":[SOURCE_MAP_CELLS[i] for i in inventory],
        "winning_public_assignment_permutation":winner,
        "winning_log_likelihood":bestscore,
        "public_fitted_assignment":assigned,
        "candidate_permutations_evaluated":len(scored),
    }
class FrozenMap:
    def __init__(self,name,mapping,learned_state):
        self.name=name
        self._mapping=tuple(tuple(p) for p in mapping)
        self._state=learned_state
    def mapping(self):
        return self._mapping
    def state(self):
        return {"name":self.name,"learned":self._state,
                "fitted_index_map":self._mapping}
def make_models(source_rows,target_rows,h,source_meta):
    n=len(target_rows)
    inventory=public_inventory(target_rows)
    def eligible(coords):
        return tuple(tuple(coord) for coord in coords)
    model={}
    assigned,meta=infer_assignment(target_rows,h)
    model[ARMS[0]]=FrozenMap(ARMS[0],assigned,meta)
    assigned_exact,exactmeta=infer_assignment(target_rows,20.)
    model[ARMS[1]]=FrozenMap(ARMS[1],assigned_exact,exactmeta)
    batch=correlation_matrix(target_rows)
    # Explicitly restrict target-only classifier to reward-discovered legal
    # positions, unlike unstructured 20-cell coordinate guessing.
    c_map=tuple(SOURCE_MAP_CELLS[
        max(inventory,key=lambda p:(batch[i][p],-p))]
        for i in range(5))
    model[ARMS[2]]=FrozenMap(ARMS[2],c_map,{
        "method":"trained_batch_public_sign_reward_covariance",
        "public_weights":batch,"trained_episodes":n})
    epis=[{"checks":row["checks"],"reward10":row["reward10"],
           "initial_public_position":row["position"]} for row in target_rows]
    ebatch=correlation_matrix(epis)
    e_map=tuple(SOURCE_MAP_CELLS[
        max(inventory,key=lambda p:(ebatch[i][p],-p))]
        for i in range(5))
    model[ARMS[3]]=FrozenMap(ARMS[3],e_map,{
        "method":"trained_raw_public_episodic_replay",
        "public_target_FIT_events":epis,"trained_episodes":n})
    need(c_map==e_map,"TARGET_BATCH_EPISODIC_NOT_SAME_FULL_FIT")
    sourceweights=[correlation_matrix(sr) for sr in source_rows]
    oldprior=[[4.*.5*(sourceweights[0][i][p]/SOURCE_N+
                       sourceweights[1][i][p]/SOURCE_N)+batch[i][p]
               for p in range(20)] for i in range(5)]
    old_map=tuple(SOURCE_MAP_CELLS[
        max(inventory,key=lambda p:(oldprior[i][p],-p))]
        for i in range(5))
    model[ARMS[4]]=FrozenMap(ARMS[4],old_map,{
        "method":"frozen_CS11_source_coordinate_prior_4_plus_target",
        "prior_plus_target_weights":oldprior,"trained_target_episodes":n})
    inv_map=tuple(SOURCE_MAP_CELLS[p] for p in inventory)
    model[ARMS[5]]=FrozenMap(ARMS[5],inv_map,{
        "method":"original_public_source_reward_inventory",
        "source_reward_discovered_public_cells":inv_map,
        "trained_target_episodes":n,"ignores_goodness":True})
    model[ARMS[6]]=FrozenMap(ARMS[6],(),{
        "method":"original_terminal_exit_only","trained_episodes":0})
    return model
def dev_episode(env,mi,ep,kind,model):
    t0=time.process_time_ns()
    e=PublicSourceEpisode(env,source_seed("dev",mi,ep),"DEV",mi,ep)
    checks=[]
    sample_actions=[]
    if kind!=ARMS[6]:
        checks=[[e.check(j) for _ in range(3)] for j in range(5)]
        goodness=[sum(z)>0 for z in checks]
        mapping=model.mapping()
        need(len(mapping)==5 and
             all(tuple(v) in SOURCE_MAP_CELLS for v in mapping),
             "FROZEN_LEARNER_PUBLIC_INDEX_MAP_INVALID")
        visited=set()
        for idx,coord in enumerate(mapping):
            if kind==ARMS[5] or goodness[idx]:
                if tuple(coord) not in visited:
                    visited.add(tuple(coord))
                    e.move_to(tuple(coord))
                    reward=e.sample()
                    sample_actions.append({
                        "public_predicted_idx":idx,
                        "public_legal_sample_position":coord,
                        "source_native_sample_reward":reward})
    e.exit()
    result=e.result()
    need((result["original_check_actions"]==15 if kind!=ARMS[6]
          else result["original_check_actions"]==0) and
         result["original_sample_actions"]==len(sample_actions),
         "ORIGINAL_SOURCE_DEV_ACTION_RIGHTS_INVALID")
    result["public_source_check_signs_by_index"]=checks
    result["public_source_sampled_actions"]=sample_actions
    result["CPU_ns_including_original_JAX_and_policy"]=time.process_time_ns()-t0
    return result
def evaluate(env,mi,n,models):
    frozen={k:digest(m.state()) for k,m in models.items()}
    out={}
    for name in ARMS:
        originals=[dev_episode(env,mi,i,name,models[name]) for i in range(DEV_N)]
        out[name]={
            "original_native_episodes":DEV_N,
            "original_source_mean_total_reward":sum(r["original_source_total_reward"]
                                                    for r in originals)/DEV_N,
            "original_source_mean_SAMPLE_reward":sum(r["original_source_sample_reward"]
                                                     for r in originals)/DEV_N,
            "source_native_check_calls":sum(r["original_check_actions"] for r in originals),
            "source_native_sample_calls":sum(r["original_sample_actions"] for r in originals),
            "source_native_move_calls_including_exit":sum(
                r["original_movement_including_exit"] for r in originals),
            "source_native_total_action_calls":sum(r["original_native_action_count"] for r in originals),
            "full_source_and_policy_CPU_ns":sum(r["CPU_ns_including_original_JAX_and_policy"]
                                                for r in originals),
            "public_original_source_episodes_SHA256":digest(originals),
            "original_public_rewarded_episode_records":originals,
        }
    need(frozen=={k:digest(m.state()) for k,m in models.items()},
         "PUBLIC_DEV_CHANGED_FROZEN_FIT_MODEL")
    need(out[ARMS[2]]["original_source_mean_total_reward"]==
         out[ARMS[3]]["original_source_mean_total_reward"],
         "EQUAL_SOURCE_FIT_BATCH_EPISODIC_REWARD_DIVERGED")
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    path=Path(args.upstream).resolve()
    outdir=Path(args.out);outdir.mkdir(parents=True,exist_ok=True)
    rec={
        "schema":"mass.cs12.original_source_portable_causal_assignment.v1",
        "frozen_FIRST_prereg":FIRST,"source":UPSTREAM,
        "source_role":"PUBLIC_SOURCE_NATIVE_DEVELOPMENT_ONLY",
        "original_private_map_exposed_to_learning_or_policy":False,
        "actual_native_Yggdrasil_or_Wingless_learner_executed":False,
        "independent_unfamiliar_source_first_use":False,
        "protected_source_seal_consumed":False,
        "CKB_controller_science_admission":False,
        "resource_parity_model_isolated":False,
        "disposition":"PUBLIC_CS12_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID",
        "source_PRETRAIN":[],"new_target_map_results":[]}
    history={"schema":"mass.cs12_original_public_FIT_source_native.v1",
             "source_original_PRETRAIN":[],"target_original_FIT":[]}
    start=time.process_time_ns()
    try:
        rec["original_upstream_git_and_blobs"]=source_identity(path)
        RockSample,_=original_scoped_modules(path)
        need(Path(inspect.getfile(RockSample)).resolve()==path/"pobax/envs/jax/rocksample.py",
             "UPSTREAM_ORIGINAL_CLASS_NOT_EXACT")
        import jax
        cfg=path/"pobax/envs/configs/rocksample_5_5_config.json"
        original_source_envs=[]
        source_rows=[]
        fit_actions=0
        for si,key in enumerate(OLD_MAP_KEYS):
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            original_source_envs.append(env)
            source_fit=[public_fit_episode(env,"source",si,i) for i in range(SOURCE_N)]
            rows=public_rows(source_fit)
            source_rows.append(rows)
            history["source_original_PRETRAIN"].append({
                "old_map_key":key,"source_original_public_FIT_records":source_fit})
            actions=sum(x["original_source_reward_and_actions"]["original_native_action_count"]
                        for x in source_fit)
            fit_actions+=actions
            rec["source_PRETRAIN"].append({
                "old_map_constructor_key":key,"native_source_FIT_episodes":len(rows),
                "original_source_NATIVE_FIT_action_count":actions,
                "original_source_public_FIT_sha256":digest(source_fit)})
        fitted_h,source_calibration=fitted_source_scale(source_rows)
        rec["transferred_source_calibration"]=source_calibration
        new_envs=[]
        for ti,key in enumerate(NEW_MAP_KEYS):
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            new_envs.append(env)
            raw=[public_fit_episode(env,"target",ti,i) for i in range(TARGET_N)]
            target_rows=public_rows(raw)
            inv=public_inventory(target_rows)
            target_original_actions=sum(
                x["original_source_reward_and_actions"]["original_native_action_count"]
                for x in raw)
            fit_actions+=target_original_actions
            history["target_original_FIT"].append({
                "new_constructor_key":key,"original_source_target_FIT_records":raw})
            item={
                "new_target_constructor_key":key,"target_map_index":ti,
                "public_new_target_FIT_total_episodes":TARGET_N,
                "original_native_FIT_action_count":target_original_actions,
                "original_native_FIT_source_sha256":digest(raw),
                "public_anonymous_reward_discovered_target_inventory":
                    [SOURCE_MAP_CELLS[p] for p in inv],
                "budgets":[]}
            for n in BUDGETS:
                tn=time.process_time_ns()
                models=make_models(source_rows,target_rows[:n],fitted_h,source_calibration)
                fitcpu=time.process_time_ns()-tn
                before={name:digest(m.state()) for name,m in models.items()}
                dev=evaluate(env,ti,n,models)
                need(before=={name:digest(m.state()) for name,m in models.items()},
                     "MODEL_MUTATED_BY_HELDOUT_REWARDED_DEV")
                item["budgets"].append({
                    "target_FIT_episodes_count":n,
                    "transferred_source_calibration_h":fitted_h,
                    "source_calibrated_and_exact_law_learner_fit_CPU_ns":fitcpu,
                    "frozen_model_state_bytes":{
                        k:len(canonical(m.state()).encode()) for k,m in models.items()},
                    "frozen_model_SHA256":{
                        k:digest(m.state()) for k,m in models.items()},
                    "original_public_fitted_index_maps":{
                        k:m.mapping() for k,m in models.items()},
                    "real_original_source_native_DEV_rewarded_results":dev,
                })
            rec["new_target_map_results"].append(item)
            print("CS12_ORIGINAL_TARGET_KEY="+str(key)+" REWARDS="+canonical(
                [{str(q["target_FIT_episodes_count"]):
                  {k:round(z["original_source_mean_total_reward"],4)
                   for k,z in q["real_original_source_native_DEV_rewarded_results"].items()}}
                 for q in item["budgets"]]),flush=True)
        # Original evaluator map truth read ONLY AFTER all 3*3*7*48 dev episodes complete.
        source_true_maps=[tuple(tuple(int(z) for z in coord)
                       for coord in array(env.rock_positions)) for env in original_source_envs]
        target_true_maps=[tuple(tuple(int(z) for z in coord)
                       for coord in array(env.rock_positions)) for env in new_envs]
        need(len(set(source_true_maps+target_true_maps))==5,
             "INDEPENDENT_CONSTRUCTOR_MAPS_COLLIDED")
        for si,source in enumerate(rec["source_PRETRAIN"]):
            true=source_true_maps[si]
            learned=tuple(tuple(c) for c in source_calibration["FIT_learned_source_index_maps"][si])
            source["auditor_only_source_fit_mapping_correct"]=sum(learned[i]==true[i] for i in range(5))
            need(source["auditor_only_source_fit_mapping_correct"]==5,
                 "SOURCE_FITTED_CALIBRATION_USED_WRONG_PUBLIC_INDEXED_MAP")
        for ti,item in enumerate(rec["new_target_map_results"]):
            correct=target_true_maps[ti]
            item["auditor_only_original_true_target_map"]=correct
            for q in item["budgets"]:
                q["auditor_only_native_correct_index_associations_by_model"]={
                    name:sum(tuple(coords[i])==correct[i] for i in range(5))
                    for name,coords in q["original_public_fitted_index_maps"].items()
                    if name!=ARMS[6]}
        one=[]
        for item in rec["new_target_map_results"]:
            q=item["budgets"][0]
            rewards=q["real_original_source_native_DEV_rewarded_results"]
            accuracy=q["auditor_only_native_correct_index_associations_by_model"]
            one.append({
                "source_constructor_key":item["new_target_constructor_key"],
                "candidate_mean_source_reward_minus_target_batch":
                    rewards[ARMS[0]]["original_source_mean_total_reward"]-
                    rewards[ARMS[2]]["original_source_mean_total_reward"],
                "candidate_source_original_correct_rock_indices":accuracy[ARMS[0]],
                "candidate_minus_exact_law_original_source_reward":
                    rewards[ARMS[0]]["original_source_mean_total_reward"]-
                    rewards[ARMS[1]]["original_source_mean_total_reward"],
                "candidate_minus_prior_source_reward":
                    rewards[ARMS[0]]["original_source_mean_total_reward"]-
                    rewards[ARMS[4]]["original_source_mean_total_reward"],
                "candidate_minus_exit_only_source_reward":
                    rewards[ARMS[0]]["original_source_mean_total_reward"]-
                    rewards[ARMS[6]]["original_source_mean_total_reward"],
            })
        pooled=lambda k:sum(x[k] for x in one)/3.
        budget1_hits=sum(z["candidate_mean_source_reward_minus_target_batch"]>=4 for z in one)
        later={}
        for idx in (1,2):
            n=BUDGETS[idx]
            rows=[]
            for item in rec["new_target_map_results"]:
                d=item["budgets"][idx]["real_original_source_native_DEV_rewarded_results"]
                rows.append({
                    "candidate_minus_exact":
                        d[ARMS[0]]["original_source_mean_total_reward"]-
                        d[ARMS[1]]["original_source_mean_total_reward"],
                    "candidate_minus_target_batch":
                        d[ARMS[0]]["original_source_mean_total_reward"]-
                        d[ARMS[2]]["original_source_mean_total_reward"]})
            later[str(n)]={
                "per_map_source_native_reward_delta":rows,
                "pooled_candidate_minus_exact":sum(z["candidate_minus_exact"] for z in rows)/3.,
                "pooled_candidate_minus_target_batch":sum(z["candidate_minus_target_batch"] for z in rows)/3.}
        passed=(all(z["candidate_source_original_correct_rock_indices"]>=3 for z in one)
                and budget1_hits>=2
                and pooled("candidate_mean_source_reward_minus_target_batch")>=4
                and pooled("candidate_minus_exact_law_original_source_reward")>=-2
                and pooled("candidate_minus_prior_source_reward")>=4
                and pooled("candidate_minus_exit_only_source_reward")>=4
                and all(later[str(n)]["pooled_candidate_minus_exact"]>=-2 and
                        later[str(n)]["pooled_candidate_minus_target_batch"]>=-2
                        for n in (2,4)))
        rec["preregistered_scientific_gain_check"]={
            "map_cases_n1":one,
            "maps_beating_conventional_batch_by_at_least_4":budget1_hits,
            "pooled_n1_candidate_minus_batch":pooled("candidate_mean_source_reward_minus_target_batch"),
            "pooled_n1_candidate_minus_exact_source_law":pooled("candidate_minus_exact_law_original_source_reward"),
            "pooled_n1_candidate_minus_prior":pooled("candidate_minus_prior_source_reward"),
            "pooled_n1_candidate_minus_exit_only":pooled("candidate_minus_exit_only_source_reward"),
            "budgets_n2_n4":later,
            "all_frozen_criteria_passed":passed}
        rec["original_public_FIT_source_resets"]=2*SOURCE_N+3*TARGET_N
        rec["original_public_DEV_source_resets"]=3*len(BUDGETS)*len(ARMS)*DEV_N
        rec["real_original_reset_calls_total"]=rec["original_public_FIT_source_resets"]+rec["original_public_DEV_source_resets"]
        rec["original_FIT_native_irreversible_SAMPLE_calls"]=rec["original_public_FIT_source_resets"]*20
        rec["original_FIT_source_native_actions_total"]=fit_actions
        rec["original_DEV_source_native_actions_total"]=sum(
            v["source_native_total_action_calls"]
            for item in rec["new_target_map_results"] for q in item["budgets"]
            for v in q["real_original_source_native_DEV_rewarded_results"].values())
        rec["all_original_source_step_env_actions"]=fit_actions+rec["original_DEV_source_native_actions_total"]
        need(rec["real_original_reset_calls_total"]==60+3*3*7*48 and
             rec["original_FIT_native_irreversible_SAMPLE_calls"]==1200,
             "ORIGINAL_PROSPECTIVE_SOURCE_ROLE_ACTION_BUDGET_DRIFT")
        rec["original_source_all_PUBLIC_FIT_SHA256"]=digest(history)
        rec["disposition"]=(
            "PUBLIC_CS12_PORTABLE_CAUSAL_RULE_SOURCE_GAIN"
            if passed else "PUBLIC_CS12_NO_QUALIFIED_PORTABLE_CAUSAL_RULE_GAIN")
        rec["native_cognitive_architecture_advantage"]="NOT_ESTABLISHED_ALL_MODELS_CONVENTIONAL"
        rec["independent_unfamiliar_source_transfer"]="NONE_PUBLIC_SINGLE_POBAX_FAMILY"
    except Exception as exc:
        rec["first_failure"]=type(exc).__name__+":"+str(exc)[:1050]
    finally:
        rec["original_source_plus_models_process_CPU_ns"]=time.process_time_ns()-start
        rec["process_inclusive_peak_RSS_KiB_not_isolated"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (outdir/"cs12-original-source-portable-rule-receipt.json").write_text(
            json.dumps(rec,sort_keys=True,indent=2)+"\n")
        (outdir/"cs12-original-public-FIT-histories.json").write_text(canonical(history)+"\n")
    print("CS12_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS12_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID" else 0
if __name__=="__main__":
    sys.exit(main())
