#!/usr/bin/env python3
"""CS10: reward-bearing cross-episode learned map on original POBAX RockSample.

Original source native ONLY. Actor uses ordinary source-public onehot position,
CHECK signs, SAMPLE rewards and persistent FIT-earned association weights.
Native source rock map and hidden morality NEVER enter learner/policy inputs.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import hashlib
import inspect
import json
import math
import resource
import sys
import time

from screen_cs06_original_pobax import source_identity, original_scoped_modules, array, UPSTREAM
from run_cs08_original_active_rock_probe import source_position, POSITIONS

FIRST="2000868632a0dab106a20c0375d74fe560ec9f05"
MAP_KEYS=(7673,7687)
FIT_N,VALID_N,DEV_N=96,24,48
ARMS=("online_local_association","conventional_batch_covariance",
      "trained_raw_episodic_correlation","association_erased",
      "trained_inventory_blind_goodness","exit_only")
ROLE_CODES={"FIT":0,"VALID":1,"DEV":2}
SOURCE_MAP_CELLS=tuple(POSITIONS)
def need(cond,why):
    if not cond: raise RuntimeError(why)
def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(data):
    return hashlib.sha256(canonical(data).encode()).hexdigest()
def native_seed(role,map_idx,episode_index):
    return {"FIT":1700000,"VALID":1800000,"DEV":1900000}[role]+10000*map_idx+episode_index
def legal(env,state,action,seed,allow_end=False):
    import jax
    out,new_state,reward,done,info=env.step_env(
        jax.random.PRNGKey(seed),state,int(action),env.default_params)
    need(isinstance(info,dict) and len(info)==0,"SOURCE_PRIVATE_INFO_RETURNED")
    if not allow_end:
        need(not bool(done),"ORIGINAL_SOURCE_EARLY_TERMINATION")
    return out,new_state,float(reward),bool(done)
class NativeEpisode:
    def __init__(self,env,role,map_idx,idx):
        import jax
        self.env=env
        self.role=role
        self.map_idx=map_idx
        self.idx=idx
        self.seed=native_seed(role,map_idx,idx)
        self.obs,self.state=env.reset_env(jax.random.PRNGKey(self.seed),env.default_params)
        need(array(self.obs).shape==(15,) and all(float(x)==0 for x in array(self.obs)[10:]),
             "SOURCE_RESET_PUBLIC_OBSERVATION_INVALID")
        self.initial_public_position=source_position(self.obs)
        self.check_calls=0;self.sample_calls=0;self.move_calls=0;self.exit_calls=0
        self.reward_checks=0.;self.reward_samples=0.;self.reward_exit=0.
        self.steps=[]
    def key(self,family,index):
        return ((4000000 if family=="check" else 8000000 if family=="sample" else 7000000)
                + ROLE_CODES[self.role]*1000000+self.map_idx*100000+self.idx*1000+index)
    def check(self,rock_idx):
        need(0<=rock_idx<5,"ILLEGAL_SOURCE_CHECK_INDEX")
        pos=source_position(self.obs)
        o,s,r,done=legal(self.env,self.state,5+rock_idx,self.key("check",self.check_calls))
        need(r==0. and not done and source_position(o)==pos,
             "ORIGINAL_SOURCE_CHECK_REWARD_POSITION_DRIFT")
        bits=array(o)[10:]
        need(sum(float(x)!=0 for x in bits)==1 and
             float(bits[rock_idx]) in (-1.,1.) and
             all(float(bits[j])==0 for j in range(5) if j!=rock_idx),
             "ORIGINAL_SOURCE_CHECK_SENSOR_INVALID")
        self.obs,self.state=o,s
        self.check_calls+=1;self.steps.append(("check",rock_idx,int(bits[rock_idx])))
        return int(bits[rock_idx])
    def move_to(self,goal):
        need(goal in SOURCE_MAP_CELLS,"ILLEGAL_PUBLIC_COORDINATE")
        while source_position(self.obs)!=goal:
            r,c=source_position(self.obs)
            action=(0 if r>goal[0] else 2) if r!=goal[0] else (3 if c>goal[1] else 1)
            need(self.move_calls<150,"EXCESSIVE_PUBLIC_MOVEMENT_BUDGET")
            o,s,reward,done=legal(self.env,self.state,action,self.key("move",self.move_calls))
            need(reward==0 and not done and source_position(o)!= (r,c)
                 and source_position(o)[1]<4,"SOURCE_NAVIGATION_POSITION_DRIFT")
            need(all(float(x)==0 for x in array(o)[10:]),
                 "SOURCE_NAV_RETURNED_NONZERO_CHECK_OUTPUT")
            self.obs,self.state=o,s
            self.move_calls+=1;self.steps.append(("move",action,source_position(o)))
    def sample(self):
        pos=source_position(self.obs)
        need(pos in SOURCE_MAP_CELLS,"SOURCE_SAMPLE_AT_ILLEGAL_COORD")
        o,s,reward,done=legal(self.env,self.state,4,self.key("sample",self.sample_calls))
        need(not done and source_position(o)==pos
             and reward in (-10.,0.,10.)
             and all(float(x)==0 for x in array(o)[10:]),
             "SOURCE_NATIVE_SAMPLE_INVALID")
        self.obs,self.state=o,s
        self.sample_calls+=1;self.reward_samples+=reward
        self.steps.append(("sample",pos,reward))
        return reward
    def exit(self):
        # Exit via original real eastward step into column4, never before.
        need(self.exit_calls==0,"REPEAT_EXIT")
        attempts=0
        while source_position(self.obs)[1]<4:
            pos=source_position(self.obs)
            o,s,r,done=legal(self.env,self.state,1,
                             self.key("move",self.move_calls),allow_end=True)
            need(source_position(o)[1]==pos[1]+1,
                 "ORIGINAL_EXIT_PUBLIC_POSITION_NOT_MOVED_EAST")
            if pos[1]==3:
                need(done and r==10.,"SOURCE_EXIT_TERMINAL_REWARD_CHANGED")
            else:
                need(not done and r==0.,"SOURCE_EARLY_EXIT_REWARD_DRIFT")
            self.obs,self.state=o,s
            self.move_calls+=1;attempts+=1;self.steps.append(("exit_step",source_position(o),r))
            need(attempts<=4,"SOURCE_EXIT_STEP_BUDGET_INVALID")
        self.exit_calls+=1;self.reward_exit=10.
    def result(self):
        need(self.exit_calls==1 and self.reward_exit==10.,
             "REAL_ORIGINAL_EXIT_NOT_COMPLETED")
        return {
          "original_seed":self.seed,"initial_public_position":self.initial_public_position,
          "original_check_actions":self.check_calls,
          "original_sample_actions":self.sample_calls,
          "original_movement_including_exit":self.move_calls,
          "original_native_action_count":self.check_calls+self.sample_calls+self.move_calls,
          "original_source_sample_reward":self.reward_samples,
          "original_source_exit_reward":self.reward_exit,
          "original_source_total_reward":self.reward_samples+self.reward_exit,
          "source_public_action_trace_sha256":digest(self.steps),
          "source_public_first_actions":self.steps[:20],
        }
def fit_episode(env,map_idx,i):
    e=NativeEpisode(env,"FIT",map_idx,i)
    reports=[e.check(j) for j in range(5)]
    public_samples=[]
    for coord in SOURCE_MAP_CELLS:
        e.move_to(coord)
        native_reward=e.sample()
        public_samples.append({"public_sample_coordinate":coord,
                               "original_public_source_reward":native_reward})
    e.exit()
    ret=e.result()
    need(ret["original_check_actions"]==5 and ret["original_sample_actions"]==20,
         "FROZEN_SOURCE_FIT_CHECK_SAMPLE_COUNT_INVALID")
    return {"role":"FIT","map":map_idx,"episode":i,
            "public_CHECK_signs_5":reports,
            "public_SAMPLED_all_20":public_samples,
            "native_real_episode_result":ret}
def create_training_rows(fit_rows):
    data=[]
    for x in fit_rows:
        signs=x["public_CHECK_signs_5"]
        samples=x["public_SAMPLED_all_20"]
        need(len(signs)==5 and set(signs)<={-1,1}
             and len(samples)==20,"FIT_PUBLIC_DATA_SHAPE")
        rewards=[int(s["original_public_source_reward"]/10) for s in samples]
        need(all(tuple(s["public_sample_coordinate"])==SOURCE_MAP_CELLS[p]
                 for p,s in enumerate(samples)),"FIT_PUBLIC_CELLS_NOT_IN_FROZEN_ORDER")
        need(sum(v!=0 for v in rewards)==5 and set(rewards)<={-1,0,1},
             "ORIGINAL_FIT_FIVE_ROCKS_NOT_SEEN")
        data.append({"checks":list(signs),"reward10":rewards})
    return data
def correlation_matrix(rows):
    # Explicit independent batch baseline; both learn identical FIT sufficient statistic.
    return [[sum(row["checks"][i]*row["reward10"][p] for row in rows)
             for p in range(20)] for i in range(5)]
def map_from_weights(weights):
    need(len(weights)==5 and all(len(row)==20 for row in weights),
         "INVALID_PUBLIC_FIT_ASSOCIATION")
    # Each rock index chooses its highest learned source-native reward correlation.
    # Ties always row-major; source truth not used for this mapping.
    ids=[max(range(20),key=lambda p:(weights[i][p],-p)) for i in range(5)]
    return tuple(SOURCE_MAP_CELLS[p] for p in ids)
class OnlineLocal:
    def __init__(self):
        self.weights=[[0 for _ in range(20)] for i in range(5)]
        self.updates=0
    def fit(self,rows):
        for row in rows:
            for i in range(5):
                for p in range(20):
                    self.weights[i][p]+=row["checks"][i]*row["reward10"][p]
            self.updates+=1
    def mapping(self):return map_from_weights(self.weights)
    def state(self):
        return {"kind":"online_local_association","weights":self.weights,
                "updates":self.updates}
class BatchCov:
    def __init__(self):self.weights=[];self.updates=0
    def fit(self,rows):
        self.weights=correlation_matrix(rows)
        self.updates=len(rows)
    def mapping(self):return map_from_weights(self.weights)
    def state(self):
        return {"kind":"conventional_batch_covariance","weights":self.weights,
                "updates":self.updates}
class RawEpisodic:
    def __init__(self):self.events=[];self.updates=0
    def fit(self,rows):
        self.events=[{"checks":list(x["checks"]),"reward10":list(x["reward10"])}
                     for x in rows]
        self.updates=len(self.events)
    def mapping(self):return map_from_weights(correlation_matrix(self.events))
    def state(self):
        return {"kind":"trained_raw_episodic_correlation","FIT_records":self.events,
                "updates":self.updates}
class InventoryBlind:
    def __init__(self):self.counts=[0]*20;self.updates=0
    def fit(self,rows):
        for row in rows:
            for p,y in enumerate(row["reward10"]):
                self.counts[p]+=int(y!=0)
            self.updates+=1
    def mapping(self):
        chosen=sorted(range(20),key=lambda p:(-self.counts[p],p))[:5]
        return tuple(SOURCE_MAP_CELLS[p] for p in chosen)
    def state(self):
        return {"kind":"trained_inventory_blind_goodness","counts":self.counts,
                "updates":self.updates}
class Rotated:
    def __init__(self,online):self.online=online
    def mapping(self):
        m=self.online.mapping()
        return tuple(m[(i+1)%5] for i in range(5))
    def state(self):
        return {"kind":"association_erased_inference_index_rotation",
                "original_fitted_weights_sha256":digest(self.online.state()),
                "no_retraining":True}
class ExitOnly:
    def mapping(self):return ()
    def state(self):return {"kind":"exit_only","updates":0}
def fit_models(rows):
    models={}
    report={}
    for kind,obj in ((ARMS[0],OnlineLocal()),(ARMS[1],BatchCov()),
                     (ARMS[2],RawEpisodic()),(ARMS[4],InventoryBlind())):
        t=time.process_time_ns()
        obj.fit(rows)
        report[kind]={"train_cpu_ns":time.process_time_ns()-t,
                      "trained_updates":obj.updates,"state_sha256":digest(obj.state()),
                      "serialized_state_bytes":len(canonical(obj.state()).encode())}
        need(obj.updates==len(rows),"FROZEN_96_FIT_UPDATES_INVALID")
        models[kind]=obj
    models[ARMS[3]]=Rotated(models[ARMS[0]])
    models[ARMS[5]]=ExitOnly()
    for kind in (ARMS[3],ARMS[5]):
        report[kind]={"train_cpu_ns":0,"trained_updates":0,
                      "state_sha256":digest(models[kind].state()),
                      "serialized_state_bytes":len(canonical(models[kind].state()).encode())}
    # Candidate and equally trained strong batch/episodic correlation must be EXACT.
    a=models[ARMS[0]].weights;b=models[ARMS[1]].weights
    need(a==b and models[ARMS[0]].mapping()==models[ARMS[1]].mapping()
         and models[ARMS[0]].mapping()==models[ARMS[2]].mapping(),
         "EQUAL_FIT_CONVENTIONAL_CONTROLS_NOT_EQUIVALENT")
    need(len(set(models[ARMS[0]].mapping()))==5,"LEARNED_INDEX_LOCATION_COLLISION")
    need(len(set(models[ARMS[4]].mapping()))==5,"FIT_INVENTORY_NOT_FIVE_CELLS")
    return models,report
def heldout_episode(env,role,map_idx,i,name,model):
    need(role in ("VALID","DEV"),"PUBLIC_ROLE_INVALID")
    start=time.process_time_ns()
    e=NativeEpisode(env,role,map_idx,i)
    if name==ARMS[5]:
        e.exit()
        d=e.result()
        need(d["original_check_actions"]==0 and d["original_sample_actions"]==0,
             "EXIT_ONLY_MORE_THAN_ORIGINAL_EXIT")
        d["public_selected_rock_index_signs"]=[]
        d["public_source_sampled_selected_coordinates"]=[]
    else:
        check_repeats=[[e.check(j) for _ in range(3)] for j in range(5)]
        bits=[int(sum(v)>0) for v in check_repeats]
        current_map=model.mapping()
        expected_map_len=5
        need(len(current_map)==expected_map_len and
             len(set(current_map))==5,"LEARNED_FIT_MAPPING_INVALID")
        selected=[]
        used=set()
        for rockidx in range(5):
            coord=current_map[rockidx]
            if name==ARMS[4] or bits[rockidx]:
                if coord not in used:
                    selected.append(coord);used.add(coord)
        sampled=[]
        for coord in selected:
            e.move_to(coord)
            sampled.append({"public_coordinate":coord,
                            "source_native_reward":e.sample()})
        e.exit()
        d=e.result()
        need(d["original_check_actions"]==15 and
             d["original_sample_actions"]==len(selected),"FROZEN_DEV_CHECK_BUDGET_INVALID")
        d["public_selected_rock_index_signs"]=check_repeats
        d["public_source_sampled_selected_coordinates"]=sampled
        d["persistent_fit_map_for_action_only"]=current_map
    d["evaluation_CPU_ns_including_original_source"]=time.process_time_ns()-start
    d["role"]=role;d["map_replica"]=map_idx;d["model"]=name
    return d
def evaluate(env,role,map_idx,n,models):
    frozen={name:digest(m.state()) for name,m in models.items()}
    result={}
    for name in ARMS:
        original=[]
        for i in range(n):
            original.append(heldout_episode(env,role,map_idx,i,name,models[name]))
        result[name]={
            "original_episode_count":n,
            "total_source_reward":sum(r["original_source_total_reward"] for r in original),
            "mean_native_original_episode_reward":sum(r["original_source_total_reward"] for r in original)/n,
            "total_native_original_SAMPLE_reward":sum(r["original_source_sample_reward"] for r in original),
            "total_source_CHECK_actions":sum(r["original_check_actions"] for r in original),
            "total_source_SAMPLE_actions":sum(r["original_sample_actions"] for r in original),
            "total_source_MOVEMENT_actions":sum(r["original_movement_including_exit"] for r in original),
            "total_source_action_calls":sum(r["original_native_action_count"] for r in original),
            "total_policy_and_original_source_CPU_ns":sum(r["evaluation_CPU_ns_including_original_source"] for r in original),
            "original_source_public_role_trace_sha256":digest(original),
            "each_actual_original_source_episode":original
        }
    need(frozen=={name:digest(m.state()) for name,m in models.items()},
         "VALID_DEV_MODEL_MUTATED")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    root=Path(a.upstream).resolve()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs10.original_POBAX_rewarded_cross_episode_association.v1",
      "frozen_first_prereg":FIRST,"original_upstream":UPSTREAM,
      "role":"PUBLIC_SOURCE_NATIVE_FIT_VALID_DEV",
      "native_yggdrasil_or_wingless_cognitive_model_executed":False,
      "novel_learned_architecture_claim":False,"independent_sealed_unfamiliar_first_use":False,
      "protected_H1_H2_consumed":False,"controller_science_admission_observed":False,
      "source_private_rock_map_input_to_models":False,
      "source_private_rock_morality_input_to_models":False,
      "resource_measurements_isolated_by_model":False,
      "disposition":"PUBLIC_CS10_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID",
      "map_replicas":[]}
    all_fits={"schema":"mass.cs10.original_shared_public_FIT_rewarded_episode_history.v1",
              "map_replicas":[]}
    start=time.process_time_ns()
    try:
        receipt["original_source_identity"]=source_identity(root)
        RockSample,_=original_scoped_modules(root)
        need(Path(inspect.getfile(RockSample)).resolve()==root/"pobax/envs/jax/rocksample.py",
             "ORIGINAL_CLASS_IDENTITY_DRIFT")
        import jax
        public_map_values=set()
        for m,map_key in enumerate(MAP_KEYS):
            cfg=root/"pobax/envs/configs/rocksample_5_5_config.json"
            env=RockSample(key=jax.random.PRNGKey(map_key),config_path=cfg)
            need(env.size==5 and env.k==5 and
                 float(env.half_efficiency_distance)==20.,"ORIGINAL_CONFIG_NOT_MATCHED")
            fit=[]
            t0=time.process_time_ns()
            for i in range(FIT_N):
                fit.append(fit_episode(env,m,i))
            fitcpu=time.process_time_ns()-t0
            need(len(fit)==FIT_N and len({x["native_real_episode_result"]["original_seed"] for x in fit})==FIT_N,
                 "FROZEN_FIT_EPISODE_COUNT_IDENTITY_INVALID")
            all_fits["map_replicas"].append({"map":m,"public_source_FIT_episodes":fit})
            rows=create_training_rows(fit)
            models,training=fit_models(rows)
            frozen={name:digest(x.state()) for name,x in models.items()}
            valid=evaluate(env,"VALID",m,VALID_N,models)
            dev=evaluate(env,"DEV",m,DEV_N,models)
            need(frozen=={name:digest(x.state()) for name,x in models.items()},
                 "EVALUATION_LEARNER_STATE_DRIFT")
            # AUDITOR-only ground truth read AFTER FIT/VALID/DEV action choices.
            true_map=tuple(tuple(int(v) for v in c) for c in array(env.rock_positions))
            need(len(set(true_map))==5 and set(true_map)<=set(SOURCE_MAP_CELLS),
                 "AUDITOR_ORIGINAL_NATIVE_MAP_INVALID")
            public_map_values.add(true_map)
            learned=models[ARMS[0]].mapping()
            inventory=set(models[ARMS[4]].mapping())
            mapping_hits=sum(learned[i]==true_map[i] for i in range(5))
            score=lambda name:dev[name]["mean_native_original_episode_reward"]
            success=(mapping_hits==5 and
                     score(ARMS[0])-score(ARMS[4])>=8 and
                     score(ARMS[0])-score(ARMS[5])>=8 and
                     score(ARMS[0])-score(ARMS[3])>=8)
            need(models[ARMS[0]].mapping()==models[ARMS[1]].mapping()==
                 models[ARMS[2]].mapping(),"STRONG_EQUAL_FIT_CONTROL_CHANGED")
            need(set(true_map)==inventory,"FROZEN_FIT_SOURCE_PUBLIC_INVENTORY_DISCOVERY_FAILED")
            receipt["map_replicas"].append({
                "map_replica":m,"original_map_constructor_key":map_key,
                "public_FIT_original_episodes":FIT_N,
                "public_FIT_native_CHECK_actions":sum(x["native_real_episode_result"]["original_check_actions"] for x in fit),
                "public_FIT_native_SAMPLE_actions":sum(x["native_real_episode_result"]["original_sample_actions"] for x in fit),
                "public_FIT_native_total_actions":sum(x["native_real_episode_result"]["original_native_action_count"] for x in fit),
                "public_FIT_original_total_reward":sum(x["native_real_episode_result"]["original_source_total_reward"] for x in fit),
                "public_FIT_original_source_CPU_ns":fitcpu,
                "public_FIT_sha256":digest(fit),
                "trained_models":training,
                "learned_source_public_rock_index_mapping":learned,
                "learned_fitted_public_inventory_coordinates":models[ARMS[4]].mapping(),
                "auditor_only_native_true_rock_index_to_coord_map":true_map,
                "auditor_only_learned_mapping_matches_original_index_correct":mapping_hits,
                "valid":valid,"dev":dev,
                "candidate_minus_inventory_native_DEV_mean_reward":score(ARMS[0])-score(ARMS[4]),
                "candidate_minus_exit_native_DEV_mean_reward":score(ARMS[0])-score(ARMS[5]),
                "candidate_minus_permuted_native_DEV_mean_reward":score(ARMS[0])-score(ARMS[3]),
                "frozen_all_conditions_passed":success,
                "process_inclusive_peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
            print("CS10_ORIGINAL_MAP="+str(m)+" FIT_INDEX_MAPPING_CORRECT="+str(mapping_hits)+
                  " DEV_MEAN_REWARDS="+canonical({n:score(n) for n in ARMS}),flush=True)
        need(len(public_map_values)==len(MAP_KEYS),"ORIGINAL_SOURCE_MAPS_NOT_DISTINCT")
        receipt["fit_source_original_episodes"]=len(MAP_KEYS)*FIT_N
        receipt["valid_source_original_episodes"]=len(MAP_KEYS)*VALID_N*len(ARMS)
        receipt["dev_source_original_episodes"]=len(MAP_KEYS)*DEV_N*len(ARMS)
        receipt["total_native_original_source_resets"]=sum(receipt[k] for k in
             ("fit_source_original_episodes","valid_source_original_episodes","dev_source_original_episodes"))
        receipt["total_native_original_source_actions"]=sum(
            m["public_FIT_native_total_actions"]+
            sum(x["total_source_action_calls"] for role in ("valid","dev")
                for x in m[role].values())
            for m in receipt["map_replicas"])
        need(receipt["total_native_original_source_resets"]==2*(96+6*(24+48)),
             "SOURCE_ORIGINAL_ROLE_TOTAL_DRIFT")
        receipt["full_shared_PUBLIC_FIT_history_sha256"]=digest(all_fits)
        receipt["disposition"]=(
           "PUBLIC_CS10_CROSS_EPISODE_LEARNED_MAP_REWARD_GAIN_SUPPORTED"
           if all(m["frozen_all_conditions_passed"] for m in receipt["map_replicas"])
           else "PUBLIC_CS10_NO_CROSS_EPISODE_REWARD_GAIN")
        receipt["native_novel_model_advantage"]="NOT_ESTABLISHED_CONVENTIONAL_CONTROLS_TIE"
        receipt["genuine_unfamiliar_new_map_transfer"]="NOT_TESTED_SOURCE_MAPS_STABLE_WITHIN_REPLICA"
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:850]
    finally:
        receipt["process_cpu_ns_all_original_source_and_models"]=time.process_time_ns()-start
        receipt["process_peak_RSS_KiB_including_JAX"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs10-source-native-reward-receipt.json").write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        (out/"cs10-public-original-shared-FIT.json").write_text(canonical(all_fits)+"\n")
    print("CS10_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS10_ORIGINAL_SOURCE_OR_PROTOCOL_INVALID" else 0

if __name__=="__main__":
    raise SystemExit(main())
