#!/usr/bin/env python3
"""CS11: original-source rewarded new-map few-shot adaptation and transfer failure.

This is a prospective PUBLIC DEVELOPMENT original POBAX RockSample test.
The actor reads ONLY genuine original public observations/rewards and saved FIT
histories; true rock positions/morality are auditor-only after all test actions.
Nothing here trains a native Wingless/Yggdrasil cognitive architecture.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import resource
import sys
import time

from screen_cs06_original_pobax import (
    source_identity, original_scoped_modules, array, UPSTREAM
)
from run_cs10_original_rewarded_cross_episode import (
    NativeEpisode, SOURCE_MAP_CELLS, OnlineLocal, BatchCov, RawEpisodic,
    InventoryBlind, ExitOnly, create_training_rows, correlation_matrix,
    map_from_weights, need, canonical, digest
)

FIRST="443139b861888816cf26156cef8a26a4a41b546c"
SOURCE_MAP_KEYS=(7673,7687)
TARGET_MAP_KEYS=(7811,7823,7841)
SOURCE_FIT_N=24
TARGET_FIT_N=12
TARGET_BUDGETS=(1,4,12)
DEV_N=48
ARMS=(
    "source_warm_prior","target_online","target_batch",
    "target_raw_episodic","source_map_zero_shot",
    "target_inventory_blind","exit_only"
)

def original_episode_seed(group,map_i,i):
    base={"source_fit":2100000,"target_fit":2200000,"target_dev":2300000}[group]
    return base+10000*map_i+i

class PublicSourceEpisode(NativeEpisode):
    """Reuse exact CS10 source action/check/movement/exit implementation.

    Only swap the public-cohort original reset seed at construction; do NOT run
    an incidental CS10 reset or read any source-private state/rock metadata.
    """
    def __init__(self,env,source_seed,role,map_i,idx):
        import jax
        need(role in ("FIT","DEV"),"SOURCE_ACTION_ROLE_INVALID")
        self.env=env
        self.role=role
        self.map_idx=map_i
        self.idx=idx
        self.seed=source_seed
        self.obs,self.state=env.reset_env(jax.random.PRNGKey(source_seed),env.default_params)
        need(array(self.obs).shape==(15,) and
             all(float(x)==0. for x in array(self.obs)[10:]),
             "ORIGINAL_SOURCE_RESET_PUBLIC_OBS_DRIFT")
        from run_cs08_original_active_rock_probe import source_position
        self.initial_public_position=source_position(self.obs)
        self.check_calls=0
        self.sample_calls=0
        self.move_calls=0
        self.exit_calls=0
        self.reward_checks=0.
        self.reward_samples=0.
        self.reward_exit=0.
        self.steps=[]

def original_training_episode(env,group,map_i,i):
    source_seed=original_episode_seed(group,map_i,i)
    e=PublicSourceEpisode(env,source_seed,"FIT",map_i,i)
    public_signs=[e.check(rock_i) for rock_i in range(5)]
    samples=[]
    for position in SOURCE_MAP_CELLS:
        e.move_to(position)
        reward=e.sample()
        samples.append({"public_sample_coordinate":position,
                        "original_public_source_reward":reward})
    e.exit()
    receipt=e.result()
    need(receipt["original_check_actions"]==5 and
         receipt["original_sample_actions"]==20 and
         receipt["original_source_exit_reward"]==10.,
         "ORIGINAL_DESTRUCTIVE_FIT_EPISODE_DRIFT")
    return {"public_role":group,"public_map_id":map_i,"public_episode_i":i,
            "public_CHECK_signs_5":public_signs,
            "public_SAMPLED_all_20":samples,
            "native_real_episode_result":receipt}

def run_public_fits(env,group,map_i,count):
    start=time.process_time_ns()
    fit=[original_training_episode(env,group,map_i,i) for i in range(count)]
    rows=create_training_rows(fit)
    need(len(rows)==count,"SOURCE_FIT_TUPLE_COUNT_DRIFT")
    return fit,rows,time.process_time_ns()-start

class WarmSourcePrior:
    """Frozen 4 pseudo-episodes from two old independent source map histories."""
    def __init__(self,source_a,source_b):
        need(len(source_a)==SOURCE_FIT_N and len(source_b)==SOURCE_FIT_N,
             "PRETRAINING_SOURCE_SHARED_HISTORIES_INCOMPLETE")
        ca=correlation_matrix(source_a)
        cb=correlation_matrix(source_b)
        self.prior=[[4.0*0.5*(ca[i][j]/SOURCE_FIT_N+
                                cb[i][j]/SOURCE_FIT_N)
                     for j in range(20)] for i in range(5)]
        self.weights=[[float(w) for w in row] for row in self.prior]
        self.target_updates=0
    def fit(self,target_rows):
        for row in target_rows:
            for i in range(5):
                for p in range(20):
                    self.weights[i][p]+=row["checks"][i]*row["reward10"][p]
            self.target_updates+=1
    def mapping(self):
        return map_from_weights(self.weights)
    def state(self):
        return {"method":"frozen_old_map_prior_strength_4_plus_target_covariance",
                "prior":self.prior,"updated_weights":self.weights,
                "source_training_episodes_per_map":SOURCE_FIT_N,
                "target_training_episodes":self.target_updates}

class SourceMapZeroShot:
    def __init__(self,source_rows):
        self.source=BatchCov()
        self.source.fit(source_rows)
    def mapping(self):
        return self.source.mapping()
    def state(self):
        return {"method":"zero_shot_old_source_map_only",
                "old_source_fit_history_episodes":self.source.updates,
                "source_weights":self.source.weights,
                "target_updates":0}

def fit_target_models(source_histories,target_rows):
    n=len(target_rows)
    need(n in TARGET_BUDGETS and len(source_histories)==2,
         "TARGET_BUDGET_OR_PRETRAINING_INVALID")
    model={
        ARMS[0]:WarmSourcePrior(source_histories[0],source_histories[1]),
        ARMS[1]:OnlineLocal(),
        ARMS[2]:BatchCov(),
        ARMS[3]:RawEpisodic(),
        ARMS[4]:SourceMapZeroShot(source_histories[0]),
        ARMS[5]:InventoryBlind(),
        ARMS[6]:ExitOnly(),
    }
    training={}
    for kind in (ARMS[0],ARMS[1],ARMS[2],ARMS[3],ARMS[5]):
        start=time.process_time_ns()
        model[kind].fit(target_rows)
        training[kind]={
            "training_cpu_ns_excludes_original_FIT_source_cost":time.process_time_ns()-start,
            "target_fit_updates":(model[kind].target_updates if kind==ARMS[0]
                                  else model[kind].updates),
            "model_state_sha256":digest(model[kind].state()),
            "serialized_model_state_bytes":len(canonical(model[kind].state()).encode())
        }
    for kind in (ARMS[4],ARMS[6]):
        training[kind]={
            "training_cpu_ns_excludes_original_FIT_source_cost":0,
            "target_fit_updates":0,
            "model_state_sha256":digest(model[kind].state()),
            "serialized_model_state_bytes":len(canonical(model[kind].state()).encode())
        }
    # Strong independent conventional controls must be exactly equally FIT-trained.
    a=model[ARMS[1]].weights
    b=model[ARMS[2]].weights
    need(a==b and
         model[ARMS[1]].mapping()==model[ARMS[2]].mapping() and
         model[ARMS[1]].mapping()==model[ARMS[3]].mapping(),
         "CONVENTIONAL_TARGET_TRAINED_CONTROL_EQUIVALENCE_DRIFT")
    need(all(z["target_fit_updates"]==n for k,z in training.items()
             if k in (ARMS[0],ARMS[1],ARMS[2],ARMS[3],ARMS[5])),
         "SAME_TARGET_FIT_INFORMATION_NOT_GRANTED")
    return model,training

def source_rewarded_dev_episode(env,map_i,i,budget,kind,model):
    # Three budgets and all seven arms deliberately start the exact SAME
    # original source reset seed for a given new map and DEV case.
    t0=time.process_time_ns()
    public_seed=original_episode_seed("target_dev",map_i,i)
    e=PublicSourceEpisode(env,public_seed,"DEV",map_i,i)
    public_checks=[]
    chosen=[]
    if kind!=ARMS[6]:
        # Every non-exit arm has the same original source-native CHECK rights.
        public_checks=[[e.check(j) for _ in range(3)] for j in range(5)]
        need(len(public_checks)==5 and all(len(q)==3 for q in public_checks),
             "THREE_PUBLIC_CHECKS_EACH_INDEX_REQUIRED")
        public_good=[sum(signs)>0 for signs in public_checks]
        index_map=model.mapping()
        need(len(index_map)==5 and all(tuple(x) in SOURCE_MAP_CELLS for x in index_map),
             "LEARNED_TARGET_PREDICTED_MAP_OUTSIDE_LEGAL_CELLS")
        used=set()
        for rock_i,coord in enumerate(index_map):
            # The inventory-only arm deliberately does not use the 15 checks.
            should_sample=(kind==ARMS[5] or public_good[rock_i])
            if should_sample and tuple(coord) not in used:
                used.add(tuple(coord))
                e.move_to(tuple(coord))
                chosen.append({"rock_index_from_model":rock_i,
                               "public_predicted_coordinate":coord,
                               "original_native_sample_reward":e.sample()})
    e.exit()
    ret=e.result()
    if kind==ARMS[6]:
        need(ret["original_check_actions"]==0 and
             ret["original_sample_actions"]==0,"EXIT_CONTROL_ACTIONS_INVALID")
    else:
        need(ret["original_check_actions"]==15 and
             ret["original_sample_actions"]==len(chosen) and
             0<=len(chosen)<=5,"DEV_PUBLIC_SENSOR_OR_SAMPLE_COUNT_INVALID")
    ret.update({
        "public_role":"DEV","target_budget":budget,"target_map_replica":map_i,
        "policy":kind,
        "public_repeated_CHECK_signs_by_index":public_checks,
        "public_predicted_sampled_locations_and_reward":chosen,
        "public_model_index_to_coordinate_predictions":
            model.mapping() if kind!=ARMS[6] else (),
        "CPU_ns_original_source_plus_policy":time.process_time_ns()-t0,
    })
    return ret

def evaluate_all(env,map_i,budget,models):
    frozen={k:digest(m.state()) for k,m in models.items()}
    result={}
    for kind in ARMS:
        records=[source_rewarded_dev_episode(env,map_i,i,budget,kind,models[kind])
                 for i in range(DEV_N)]
        result[kind]={
            "original_source_episodes":DEV_N,
            "mean_actual_original_total_reward":sum(x["original_source_total_reward"] for x in records)/DEV_N,
            "mean_actual_original_SAMPLE_reward":sum(x["original_source_sample_reward"] for x in records)/DEV_N,
            "original_native_total_reward":sum(x["original_source_total_reward"] for x in records),
            "original_native_SAMPLE_reward":sum(x["original_source_sample_reward"] for x in records),
            "original_source_CHECK_calls":sum(x["original_check_actions"] for x in records),
            "original_source_SAMPLE_calls":sum(x["original_sample_actions"] for x in records),
            "original_source_MOVE_calls_including_exit":sum(x["original_movement_including_exit"] for x in records),
            "original_source_all_action_calls":sum(x["original_native_action_count"] for x in records),
            "original_source_CPU_and_policy_ns":sum(x["CPU_ns_original_source_plus_policy"] for x in records),
            "original_PUBLIC_trace_SHA256":digest(records),
            "individual_original_source_rewarded_episodes":records,
        }
    need(frozen=={k:digest(m.state()) for k,m in models.items()},
         "DEV_MUTATED_FITTED_MODEL_OR_TRANSFER_PRIOR")
    # Because mapping and initial sensors are exactly the same, the three
    # trained target-only controls should match actual source reward exactly.
    names=(ARMS[1],ARMS[2],ARMS[3])
    need(len({result[n]["original_native_total_reward"] for n in names})==1,
         "EQUAL_INFORMATION_CONVENTIONAL_REWARDED_CONTROLS_DIVERGED")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    path=Path(args.upstream).resolve()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rec={
        "schema":"mass.cs11.original_POBAX_new_map_rewarded_transfer.v1",
        "frozen_FIRST_prereg_commit":FIRST,
        "source_git_SHA":UPSTREAM,
        "source_role":"PUBLIC_DEVELOPMENT_ORIGINAL_UNFAMILIAR_MAP_WITHIN_FAMILIAR_SOURCE",
        "independent_unfamiliar_source_family_test":False,
        "protected_first_use_consumed":False,
        "native_Wingless_Yggdrasil_model_tested":False,
        "CKB_scientific_controller_admission":False,
        "original_private_map_available_to_policy_or_fit":False,
        "original_private_rock_goodness_available_to_policy_or_fit":False,
        "resource_isolation_per_model_qualified":False,
        "old_source_original_fits":[],
        "new_target_map_results":[],
        "disposition":"PUBLIC_CS11_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID"}
    original_fit={"schema":"mass.cs11.original_source_PUBLIC_source_and_target_FIT.v1",
                  "source_map_FIT":[],"new_target_map_FIT":[]}
    start=time.process_time_ns()
    try:
        rec["upstream_original_source_verified"]=source_identity(path)
        RockSample,_=original_scoped_modules(path)
        need(Path(inspect.getfile(RockSample)).resolve()==path/"pobax/envs/jax/rocksample.py",
             "LOADED_ORIGINAL_ROCKSAMPLE_CLASS_NOT_AUTHENTIC")
        import jax
        cfg=path/"pobax/envs/configs/rocksample_5_5_config.json"
        old_envs=[]
        source_histories=[]
        fit_native_total=0
        for m,key in enumerate(SOURCE_MAP_KEYS):
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            need(env.size==5 and env.k==5,"ORIGINAL_UPSTREAM_CONFIG_CHANGED")
            old_envs.append(env)
            fit,rows,cpu=run_public_fits(env,"source_fit",m,SOURCE_FIT_N)
            source_histories.append(rows)
            fit_actions=sum(x["native_real_episode_result"]["original_native_action_count"] for x in fit)
            fit_native_total+=fit_actions
            rec["old_source_original_fits"].append({
                "already_inspected_original_source_map_constructor":key,
                "original_public_fit_episode_count":len(fit),
                "original_source_PUBLIC_FIT_SHA256":digest(fit),
                "real_original_source_CHECK_actions":sum(x["native_real_episode_result"]["original_check_actions"] for x in fit),
                "real_original_source_SAMPLE_actions":sum(x["native_real_episode_result"]["original_sample_actions"] for x in fit),
                "real_original_source_total_actions":fit_actions,
                "real_original_source_training_reward":sum(x["native_real_episode_result"]["original_source_total_reward"] for x in fit),
                "original_source_CPU_including_navigation_ns":cpu})
            original_fit["source_map_FIT"].append({
                "map":m,"original_source_constructor_key":key,"source_original_PUBLIC_episodes":fit})
        all_target_envs=[]
        for t,key in enumerate(TARGET_MAP_KEYS):
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            need(env.size==5 and env.k==5,"NEW_TARGET_UPSTREAM_CONFIG_CHANGED")
            all_target_envs.append(env)
            fit,target_rows,fitcpu=run_public_fits(env,"target_fit",t,TARGET_FIT_N)
            original_fit["new_target_map_FIT"].append({
                "map":t,"fresh_target_constructor_key":key,
                "original_public_new_target_FIT_episodes":fit})
            target_fit_actions=sum(x["native_real_episode_result"]["original_native_action_count"] for x in fit)
            fit_native_total+=target_fit_actions
            item={
                "new_target_original_constructor_key":key,
                "target_map_index":t,
                "shared_target_public_fit_episodes":len(fit),
                "original_TARGET_FIT_source_native_CHECK_actions":sum(x["native_real_episode_result"]["original_check_actions"] for x in fit),
                "original_TARGET_FIT_source_native_SAMPLE_actions":sum(x["native_real_episode_result"]["original_sample_actions"] for x in fit),
                "original_TARGET_FIT_native_action_calls":target_fit_actions,
                "original_TARGET_FIT_native_total_reward":sum(x["native_real_episode_result"]["original_source_total_reward"] for x in fit),
                "original_TARGET_FIT_CPU_ns_including_source":fitcpu,
                "target_public_fit_sha256":digest(fit),
                "adaptation_budgets":[],
            }
            for n in TARGET_BUDGETS:
                models,training=fit_target_models(source_histories,target_rows[:n])
                before={k:digest(x.state()) for k,x in models.items()}
                dev=evaluate_all(env,t,n,models)
                need(before=={k:digest(x.state()) for k,x in models.items()},
                     "PUBLIC_DEV_BUDGET_LEARNED_MODEL_MUTATION")
                item["adaptation_budgets"].append({
                    "number_cumulative_real_target_FIT_episodes":n,
                    "same_public_source_pretraining_episodes":len(source_histories[0])+len(source_histories[1]),
                    "models_training_and_state":training,
                    "public_predicted_index_to_location_by_model":{
                        k:models[k].mapping() for k in ARMS},
                    "real_original_DEV_source_reward_and_actions":dev,
                })
            rec["new_target_map_results"].append(item)
            print("CS11_TARGET_MAP="+str(key)+" REWARD_BUDGETS="+canonical([
                {str(q["number_cumulative_real_target_FIT_episodes"]):
                    {n:round(q["real_original_DEV_source_reward_and_actions"][n]
                             ["mean_actual_original_total_reward"],4) for n in ARMS}}
                for q in item["adaptation_budgets"]]),flush=True)
        # AUDITOR source truth only after ALL actions/evaluations across roles are finished.
        auditor_source_maps=[tuple(tuple(int(x) for x in row)
                          for row in array(env.rock_positions)) for env in old_envs]
        auditor_target_maps=[tuple(tuple(int(x) for x in row)
                          for row in array(env.rock_positions)) for env in all_target_envs]
        need(len(set(auditor_source_maps+auditor_target_maps))==5,
             "SOURCE_TARGET_MAP_COLLISION_OR_INVALID_INDEPENDENCE")
        for target_i,item in enumerate(rec["new_target_map_results"]):
            true_map=auditor_target_maps[target_i]
            need(len(true_map)==5 and len(set(true_map))==5 and
                 set(true_map)<=set(SOURCE_MAP_CELLS),"PRIVATE_AUDITOR_MAP_INVALID")
            item["auditor_only_original_target_rock_index_map"]=true_map
            for q in item["adaptation_budgets"]:
                q["auditor_only_correct_index_to_coordinate_counts"]={
                    k:sum(tuple(models_coord[i])==true_map[i]
                          for i in range(5))
                    for k,models_coord in q["public_predicted_index_to_location_by_model"].items()
                    if k!=ARMS[6]}
        # Strict exact strong conventional controls over all maps and budgets.
        for item in rec["new_target_map_results"]:
            for q in item["adaptation_budgets"]:
                ms=q["public_predicted_index_to_location_by_model"]
                need(ms[ARMS[1]]==ms[ARMS[2]]==ms[ARMS[3]],
                     "SAME_FIT_STRONG_BASELINE_PREDICTED_STATE_DIVERGED")
                rewards=q["real_original_DEV_source_reward_and_actions"]
                need(rewards[ARMS[1]]["original_native_total_reward"]==
                     rewards[ARMS[2]]["original_native_total_reward"]==
                     rewards[ARMS[3]]["original_native_total_reward"],
                     "SAME_FIT_STRONG_BASELINE_REAL_REWARD_DIVERGED")
        # Future choice limits frozen n=1/4/12 cohorts, no posthoc tuning.
        qual=[]
        for idx in range(3):
            item=rec["new_target_map_results"][idx]
            first=item["adaptation_budgets"][0]
            rewards=first["real_original_DEV_source_reward_and_actions"]
            candidate=rewards[ARMS[0]]["mean_actual_original_total_reward"]
            baseline=rewards[ARMS[2]]["mean_actual_original_total_reward"]
            correct=first["auditor_only_correct_index_to_coordinate_counts"]
            qual.append({
                "map_constructor":item["new_target_original_constructor_key"],
                "candidate_minus_trained_target_batch_mean_reward":candidate-baseline,
                "candidate_minus_batch_correct_map_associations":
                    correct[ARMS[0]]-correct[ARMS[2]]})
        candidate_plus4=sum(z["candidate_minus_trained_target_batch_mean_reward"]>=4. for z in qual)
        pooled_first=sum(z["candidate_minus_trained_target_batch_mean_reward"] for z in qual)/3.
        pooled_count=sum(z["candidate_minus_batch_correct_map_associations"] for z in qual)/3.
        later={}
        for stage in (1,2):
            n=TARGET_BUDGETS[stage]
            diffs=[]
            for item in rec["new_target_map_results"]:
                q=item["adaptation_budgets"][stage]
                scores=q["real_original_DEV_source_reward_and_actions"]
                diffs.append(scores[ARMS[0]]["mean_actual_original_total_reward"]-
                             scores[ARMS[2]]["mean_actual_original_total_reward"])
            later[str(n)]={"per_original_new_map_transfer_minus_batch":diffs,
                           "pooled_transfer_minus_batch":sum(diffs)/3.}
        criterion=(candidate_plus4>=2 and pooled_first>=4. and pooled_count>=1.
                   and all(later[str(n)]["pooled_transfer_minus_batch"]>=-2.
                           for n in (4,12)))
        rec["prospectively_frozen_transfer_result"]={
            "individual_target_map_deltas_at_budget1":qual,
            "candidate_maps_beat_target_batch_by_4_reward_at_budget1":candidate_plus4,
            "pooled_budget1_new_map_reward_gain":pooled_first,
            "pooled_budget1_new_map_index_association_gain":pooled_count,
            "other_budget_stability_deltas":later,
            "ALL_preregistered_criterion_pass":criterion}
        rec["public_source_original_pretrain_episodes"]=len(SOURCE_MAP_KEYS)*SOURCE_FIT_N
        rec["public_source_original_new_map_FIT_episodes"]=len(TARGET_MAP_KEYS)*TARGET_FIT_N
        rec["public_source_original_DEV_episodes"]=len(TARGET_MAP_KEYS)*len(TARGET_BUDGETS)*len(ARMS)*DEV_N
        rec["public_source_original_total_resets"]=(
            rec["public_source_original_pretrain_episodes"]+
            rec["public_source_original_new_map_FIT_episodes"]+
            rec["public_source_original_DEV_episodes"])
        rec["source_native_destructive_original_FIT_sample_calls"]=(len(SOURCE_MAP_KEYS)*SOURCE_FIT_N+
                                                  len(TARGET_MAP_KEYS)*TARGET_FIT_N)*20
        rec["source_native_all_FIT_action_calls"]=fit_native_total
        rec["source_native_all_DEV_action_calls"]=sum(
            reward["original_source_all_action_calls"]
            for item in rec["new_target_map_results"]
            for q in item["adaptation_budgets"]
            for reward in q["real_original_DEV_source_reward_and_actions"].values())
        rec["source_native_all_real_original_action_calls"]=(
            rec["source_native_all_FIT_action_calls"]+
            rec["source_native_all_DEV_action_calls"])
        rec["all_public_source_FIT_histories_SHA256"]=digest(original_fit)
        need(rec["public_source_original_total_resets"]==84+3*3*7*48 and
             rec["source_native_destructive_original_FIT_sample_calls"]==1680,
             "PUBLIC_FIT_OR_DEV_SOURCE_EPISODE_COUNT_INVALID")
        rec["disposition"]=(
            "PUBLIC_CS11_QUALIFIED_NEW_MAP_WARM_TRANSFER_GAIN"
            if criterion else "PUBLIC_CS11_NO_QUALIFIED_NEW_MAP_TRANSFER_GAIN")
        rec["native_new_learning_architecture_advantage"]="NOT_TESTED_ALL_MODELS_CONVENTIONAL"
        rec["unfamiliar_source_family_transfer"]="NOT_TESTED_PUBLIC_PREVIOUSLY_INSPECTED_POBAX"
        rec["training_source_original_fully_accounted"]="84_REAL_ORIGINAL_FIT_EPISODES"
    except Exception as err:
        rec["first_failure"]=type(err).__name__+":"+str(err)[:1000]
    finally:
        rec["original_source_and_policy_total_CPU_ns"]=time.process_time_ns()-start
        rec["peak_process_RSS_KiB_including_JAX"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs11-original-new-map-source-receipt.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
        (out/"cs11-all-original-source-public-FIT.json").write_text(canonical(original_fit)+"\n")
    print("CS11_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS11_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID" else 0

if __name__=="__main__":
    sys.exit(main())
