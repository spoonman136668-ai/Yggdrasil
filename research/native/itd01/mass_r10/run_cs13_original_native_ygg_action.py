#!/usr/bin/env python3
"""CS13: ACTUAL unmodified Yggdrasil R7 native Colony on original POBAX rewards.

Development source only. Original public observations and source-native action
consequences; auditor private rock map never enters learning or action policies.
R7 Colony does NOT learn action-conditioned counterfactuals, only SAMPLE label.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
import math
from pathlib import Path
import resource
import sys
import time

from screen_cs06_original_pobax import source_identity,original_scoped_modules,array,UPSTREAM
from run_cs08_original_active_rock_probe import SOURCE_MAP_CELLS if False else POSITIONS
from run_cs10_original_rewarded_cross_episode import need,canonical,digest
from run_cs11_original_new_map_transfer import PublicSourceEpisode

FIRST="b2d5bec1ca0a36efa4f51d5cd53cc34ec8c61d5a"
ORIGINAL_NATIVE_BLOB="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
MAP_KEYS=(8111,8137)
FIT_N=64
DEV_N=128
ARMS=("authentic_ygg_native_Colony","trained_contextual_reward_table",
      "trained_logistic_reward","conventional_majority_sign",
      "native_cold_erased","sample_both","check_only_skip_both")
CELLS=tuple(POSITIONS)
def original_seed(role,map_idx,i):
    return {"FIT":2700000,"DEV":2800000}[role]+10000*map_idx+i
def actual_native_Colony():
    import native_cells
    original=(Path(__file__).resolve().parent.parent/"r7"/"native_cells.py").resolve()
    need(Path(inspect.getfile(native_cells.Colony)).resolve()==original,
         "NATIVE_YGGDRASIL_CLASS_NOT_ORIGINAL")
    return native_cells.Colony
def public_episode(env,role,m,i):
    return PublicSourceEpisode(env,original_seed(role,m,i),role,m,i)
def raw_fit_episode(env,m,i):
    e=public_episode(env,"FIT",m,i)
    triples=[[e.check(j) for _ in range(3)] for j in (0,1)]
    readings=[tuple(s>0 for s in signs) for signs in triples]
    native_samples=[]
    for coord in CELLS:
        e.move_to(coord)
        reward=e.sample()
        native_samples.append({"public_coordinate":coord,
                               "original_source_native_sample_reward":reward})
    e.exit()
    r=e.result()
    need(r["original_check_actions"]==6 and r["original_sample_actions"]==20,
         "FROZEN_ORIGINAL_FIT_ACTION_COUNT_INVALID")
    return {"seed":original_seed("FIT",m,i),
            "public_original_sensor_triples":triples,
            "public_source_sample_rewards":native_samples,
            "public_original_episode_reward_and_actions":r}
def fit_map_and_rows(fit):
    need(len(fit)==FIT_N,"FIT_SOURCE_EPISODE_COUNT_DRIFT")
    # Public check-sign/reward covariance for index0,1. Never hidden map.
    weights=[[0. for _ in CELLS] for _ in range(2)]
    for row in fit:
        for j in range(2):
            sense=sum(row["public_original_sensor_triples"][j])/3.
            for p,source in enumerate(row["public_source_sample_rewards"]):
                need(tuple(source["public_coordinate"])==CELLS[p],
                     "PUBLIC_FIT_GRID_POSITION_DRIFT")
                weights[j][p]+=sense*(source["original_source_native_sample_reward"]/10)
    picks=[max(range(20),key=lambda p:(weights[j][p],-p)) for j in range(2)]
    coords=tuple(CELLS[p] for p in picks)
    need(coords[0]!=coords[1],
         "CS13_ORIGINAL_FIT_INDEX_MAP_UNIDENTIFIABLE")
    out=[]
    for ep,row in enumerate(fit):
        for j in (0,1):
            s=tuple(x>0 for x in row["public_original_sensor_triples"][j])
            reward=row["public_source_sample_rewards"][picks[j]][
                "original_source_native_sample_reward"]
            need(reward in (-10.,10.),"FIT_ORIGINAL_NATIVE_LABEL_NOT_REAL_ROCK")
            out.append({"FIT_episode":ep,"context":"A" if j==0 else "B",
                        "public_sensors_4":(*s,True),
                        "native_SAMPLE_reward_at_publicly_fitted_location":reward,
                        "public_real_source_label_good":reward>0})
    return coords,weights,out
class TrainedTable:
    def __init__(self):
        self.counts={k:{f"{i:03b}":[1,1] for i in range(8)} for k in ("A","B")}
    def fit(self,rows):
        for x in rows:
            s=x["public_sensors_4"]
            k="".join("1" if b else "0" for b in s[:3])
            self.counts[x["context"]][k][int(x["public_real_source_label_good"])]+=1
    def predict(self,ctx,s):
        k="".join("1" if b else "0" for b in s[:3])
        n=self.counts[ctx][k]
        return n[1]>n[0]
    def state(self):return self.counts
class Logistic:
    def __init__(self):
        self.w={k:[0.]*4 for k in ("A","B")}
        self.updates=0
    def predict_prob(self,ctx,s):
        z=self.w[ctx][0]+sum(self.w[ctx][i+1]*int(s[i]) for i in range(3))
        return 1./(1.+math.exp(-max(-30.,min(30.,z))))
    def fit(self,rows):
        for _ in range(20):
            for x in rows:
                ctx=x["context"];s=x["public_sensors_4"]
                a=[1.,*(float(q) for q in s[:3])]
                error=int(x["public_real_source_label_good"])-self.predict_prob(ctx,s)
                for j in range(4):
                    self.w[ctx][j]+=.08*(error*a[j]-.003*self.w[ctx][j])
                self.updates+=1
    def predict(self,ctx,s):return self.predict_prob(ctx,s)>.5
    def state(self):return {"weights":self.w,"updates":self.updates}
def source_native_fitted_models(rows,Colony):
    need(len(rows)==2*FIT_N,"ORIGINAL_FIT_LABEL_BUDGET_INVALID")
    native=Colony()
    begin=time.process_time_ns()
    for x in rows:
        ctx=x["context"]
        ss=tuple(x["public_sensors_4"])
        need(len(ss)==4 and all(type(y) is bool for y in ss),"NATIVE_PUBLIC_BOOLEAN_SENSE_INVALID")
        # One *completed* real native source FIT episode already returned
        # physical SAMPLE consequence before this update. delay>=2 enforced.
        native.predict(ctx,ss)
        native.learn_completed_public_feedback(ctx,ss,
            bool(x["public_real_source_label_good"]),delay_steps=2)
    native_fit_cpu=time.process_time_ns()-begin
    need(native.feedback_updates==128 and native.neighbor_messages==1024,
         "ORIGINAL_NATIVE_SOURCE_FEEDBACK_COUNT_DRIFT")
    state=native.checkpoint()
    need(0<len(state)<=32768,"ORIGINAL_NATIVE_CHECKPOINT_BOUND_EXCEEDED")
    restored=Colony.restore(state)
    need(restored.checkpoint()==state,"COLD_NATIVE_CHECKPOINT_NOT_EXACT")
    for ctx in ("A","B"):
        for code in range(8):
            ss=(*(bool(code&(1<<k)) for k in range(3)),True)
            need(restored.predict(ctx,ss)==native.predict(ctx,ss),
                 "ORIGINAL_NATIVE_COLD_PREDICTION_DRIFT")
    table=TrainedTable(); t=time.process_time_ns();table.fit(rows)
    table_cpu=time.process_time_ns()-t
    logistic=Logistic();t=time.process_time_ns();logistic.fit(rows)
    logistic_cpu=time.process_time_ns()-t
    return restored,table,logistic,{
        "real_native_FIT_feedback_updates":restored.feedback_updates,
        "real_native_cells_local_update_count":{
            ctx:[c.updates for c in restored.cells[ctx]] for ctx in ("A","B")},
        "real_native_neighbor_messages":restored.neighbor_messages,
        "real_native_source_FIT_training_CPU_ns":native_fit_cpu,
        "real_native_original_checkpoint_SHA256":hashlib.sha256(state).hexdigest(),
        "real_native_cold_checkpoint_exact":True,
        "real_native_checkpoint_bytes":len(state),
        "real_native_original_checkpoint_json":json.loads(state),
        "table_training_cpu_ns":table_cpu,
        "table_state_bytes":len(canonical(table.state()).encode()),
        "logistic_training_cpu_ns":logistic_cpu,
        "logistic_state_bytes":len(canonical(logistic.state()).encode()),
        "logistic_training_updates":logistic.updates,
    }
def decide(name,ctx,s,native,table,logistic,cold):
    if name==ARMS[0]:return native.predict(ctx,s)
    if name==ARMS[1]:return table.predict(ctx,s)
    if name==ARMS[2]:return logistic.predict(ctx,s)
    if name==ARMS[3]:return sum(s[:3])>=2
    if name==ARMS[4]:return cold.predict(ctx,s)
    if name==ARMS[5]:return True
    need(name==ARMS[6],"NOT_PREREGISTERED_CONTROL")
    return False
def source_dev_episode(env,m,i,name,coords,models):
    before=time.process_time_ns()
    e=public_episode(env,"DEV",m,i)
    triples=[[e.check(j) for _ in range(3)] for j in (0,1)]
    public_senses=[(*(z>0 for z in trip),True) for trip in triples]
    decisions=[decide(name,"AB"[j],public_senses[j],*models)
               for j in range(2)]
    taken=[]
    for j,choose in enumerate(decisions):
        if choose:
            e.move_to(coords[j])
            actual_reward=e.sample()
            taken.append({"rock_index":j,"public_fitted_legal_location":coords[j],
                          "actual_original_SOURCE_reward":actual_reward})
    e.exit()
    out=e.result()
    need(out["original_check_actions"]==6 and
         out["original_sample_actions"]==len(taken) and
         out["original_source_exit_reward"]==10.,
         "ORIGINAL_SOURCE_DEV_ACTIONS_REWARDS_NOT_RECORDED")
    out.update({"model":name,"source_role":"DEV","public_check_signs_by_rock":triples,
                "public_bounded_cell_senses":public_senses,
                "source_native_SAMPLE_decisions":decisions,
                "source_original_SAMPLE_actions_and_rewards":taken,
                "model_and_source_CPU_ns":time.process_time_ns()-before})
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    opts=p.parse_args()
    root=Path(opts.upstream).resolve()
    out=Path(opts.out);out.mkdir(parents=True,exist_ok=True)
    rec={"schema":"mass.cs13.original_pobax_actual_native_ygg_r7.v1",
         "FIRST_frozen_prereg":FIRST,"source":UPSTREAM,
         "ACTUAL_native_yggdrasil_R7_cells_executed":False,
         "ACTUAL_real_original_source_rewards_collected":False,
         "native_architecture_automatically_learns_action_outcomes":False,
         "native_R7_action_conditioning_absent":True,
         "native_source_files_modified":False,
         "independent_source_sealed_first_use":False,
         "controller_scientific_admission":False,
         "process_RSS_CPU_model_isolation":False,
         "disposition":"PUBLIC_CS13_INTEGRATION_OR_SOURCE_INVALID",
         "original_source_map_replicas":[]}
    all_fit={"schema":"mass.cs13.original_SOURCE_public_FIT.v1","maps":[]}
    t0=time.process_time_ns()
    try:
        rec["original_external_source"]=source_identity(root)
        Colony=actual_native_Colony()
        rec["ACTUAL_native_yggdrasil_R7_cells_executed"]=True
        RockSample,_=original_scoped_modules(root)
        need(Path(inspect.getfile(RockSample)).resolve()==
             root/"pobax/envs/jax/rocksample.py","ORIGINAL_SOURCE_CLASS_IDENTITY_DRIFT")
        import jax
        cfg=root/"pobax/envs/configs/rocksample_5_5_config.json"
        source_maps=[]
        for m,key in enumerate(MAP_KEYS):
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            need(env.size==5 and env.k==5 and float(env.half_efficiency_distance)==20.,
                 "ORIGINAL_EXTERNAL_ROCKSAMPLE_CONFIG_DRIFT")
            ft=time.process_time_ns()
            fit=[raw_fit_episode(env,m,i) for i in range(FIT_N)]
            fit_cpu=time.process_time_ns()-ft
            all_fit["maps"].append({"constructor_key":key,
                         "original_source_native_FIT_episodes":fit})
            coords,fitweights,rows=fit_map_and_rows(fit)
            native,table,logistic,training=source_native_fitted_models(rows,Colony)
            cold=Colony()
            models=(native,table,logistic,cold)
            pretrained_state={
                "native_checkpoint_SHA256":training["real_native_original_checkpoint_SHA256"],
                "table_sha":digest(table.state()),
                "logistic_sha":digest(logistic.state())}
            scores={}
            for name in ARMS:
                originals=[source_dev_episode(env,m,i,name,coords,models)
                           for i in range(DEV_N)]
                scores[name]={
                    "source_native_original_episode_count":DEV_N,
                    "mean_actual_original_native_total_reward":
                        sum(x["original_source_total_reward"] for x in originals)/DEV_N,
                    "source_original_total_native_reward":
                        sum(x["original_source_total_reward"] for x in originals),
                    "source_original_genuine_sample_reward":
                        sum(x["original_source_sample_reward"] for x in originals),
                    "original_source_sample_action_count":
                        sum(x["original_sample_actions"] for x in originals),
                    "original_source_check_action_count":
                        sum(x["original_check_actions"] for x in originals),
                    "original_source_movement_action_count":
                        sum(x["original_movement_including_exit"] for x in originals),
                    "original_source_step_env_action_count":
                        sum(x["original_native_action_count"] for x in originals),
                    "original_source_plus_model_cpu_ns":
                        sum(x["model_and_source_CPU_ns"] for x in originals),
                    "source_native_original_public_episodes_sha256":digest(originals),
                    "original_source_native_public_episodes":originals,
                }
            need(pretrained_state=={
                "native_checkpoint_SHA256":hashlib.sha256(native.checkpoint()).hexdigest(),
                "table_sha":digest(table.state()),
                "logistic_sha":digest(logistic.state())},
                "NATIVE_OR_CONVENTIONAL_DEV_MUTATED_ORIGINAL_FIT_MODEL")
            # Native true map used solely after all public DEV actions are frozen.
            true=tuple(tuple(int(x) for x in z) for z in array(env.rock_positions))
            need(len(set(true))==5 and set(true)<=set(CELLS),
                 "ORIGINAL_SOURCE_MAP_AUDITOR_INVALID")
            source_maps.append(true)
            accuracy=sum(coords[j]==true[j] for j in (0,1))
            reward=lambda a:scores[a]["mean_actual_original_native_total_reward"]
            conventional=max(reward(x) for x in (ARMS[1],ARMS[2],ARMS[3]))
            qualified=(accuracy==2 and training["real_native_FIT_feedback_updates"]==128
                and training["real_native_cold_checkpoint_exact"]
                and reward(ARMS[0])-reward(ARMS[5])>=4.
                and reward(ARMS[0])-reward(ARMS[4])>=4.
                and reward(ARMS[0])>=conventional-2.)
            rec["original_source_map_replicas"].append({
                "map_replica":m,"constructor_key":key,
                "shared_original_FIT_native_episode_count":len(fit),
                "source_original_FIT_actions":sum(x["public_original_episode_reward_and_actions"]
                                                ["original_native_action_count"] for x in fit),
                "source_original_FIT_genuine_SAMPLE_actions":FIT_N*20,
                "source_original_FIT_CPU_ns":fit_cpu,
                "source_original_full_public_FIT_sha256":digest(fit),
                "public_original_fitted_two_index_locations":coords,
                "public_fitted_association_weights":fitweights,
                "AUDITOR_ONLY_true_source_index_locations":true[:2],
                "AUDITOR_only_two_index_mapping_correct":accuracy,
                "REAL_NATIVE_training_receipt":training,
                "real_original_source_DEV_results":scores,
                "native_reward_minus_sample_both":reward(ARMS[0])-reward(ARMS[5]),
                "native_reward_minus_cold_erased":reward(ARMS[0])-reward(ARMS[4]),
                "native_reward_minus_best_conventional":reward(ARMS[0])-conventional,
                "preregistered_native_source_action_use_passed":qualified})
            print("CS13_REAL_NATIVE_MAP="+str(m)+" scores="+canonical({
                a:round(reward(a),4) for a in ARMS}),flush=True)
        need(len(set(source_maps))==2,"ORIGINAL_INDEPENDENT_MAPS_NOT_DISTINCT")
        rec["ACTUAL_real_original_source_rewards_collected"]=True
        rec["original_source_FIT_episodes"]=2*FIT_N
        rec["original_source_DEV_episodes"]=2*len(ARMS)*DEV_N
        rec["original_source_total_reset_env_episodes"]=(
            rec["original_source_FIT_episodes"]+rec["original_source_DEV_episodes"])
        rec["original_SOURCE_genuine_FIT_destructive_SAMPLE_calls"]=2*FIT_N*20
        rec["original_native_FIT_step_env_calls"]=sum(
            z["source_original_FIT_actions"] for z in rec["original_source_map_replicas"])
        rec["original_native_DEV_step_env_calls"]=sum(
            x["original_source_step_env_action_count"]
            for z in rec["original_source_map_replicas"]
            for x in z["real_original_source_DEV_results"].values())
        rec["total_original_source_step_env_actions"]=(
            rec["original_native_FIT_step_env_calls"]+
            rec["original_native_DEV_step_env_calls"])
        need(rec["original_source_total_reset_env_episodes"]==1920 and
             rec["original_SOURCE_genuine_FIT_destructive_SAMPLE_calls"]==2560 and
             sum(x["original_source_check_action_count"]
               for z in rec["original_source_map_replicas"]
               for x in z["real_original_source_DEV_results"].values())==10752,
             "FROZEN_SOURCE_NATIVE_EPISODE_ACTION_TOTAL_DRIFT")
        rec["original_PUBLIC_FIT_source_SHA256"]=digest(all_fit)
        rec["disposition"]=(
            "PUBLIC_CS13_REAL_NATIVE_REWARDED_ACTION_USE_SUPPORTED"
            if all(z["preregistered_native_source_action_use_passed"]
                   for z in rec["original_source_map_replicas"])
            else "PUBLIC_CS13_NATIVE_SOURCE_ACTION_NO_ADVANTAGE")
        rec["source_family_new_sealed_transfer"]="NONE_PUBLIC_DEVELOPMENT_ONLY"
        rec["native_new_architecture_advantage"]="NO_CLAIM_CONVENTIONAL_CONTROLS_MEASURED"
    except Exception as error:
        rec["first_failure"]=type(error).__name__+":"+str(error)[:850]
    finally:
        rec["source_original_plus_native_policy_process_CPU_ns"]=time.process_time_ns()-t0
        rec["process_peak_RSS_kib_including_original_JAX"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs13-original-source-native-r7-receipt.json").write_text(
            json.dumps(rec,sort_keys=True,indent=2)+"\n")
        (out/"cs13-original-public-FIT-histories.json").write_text(canonical(all_fit)+"\n")
    print("CS13_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS13_INTEGRATION_OR_SOURCE_INVALID" else 0

if __name__=="__main__":
    raise SystemExit(main())
