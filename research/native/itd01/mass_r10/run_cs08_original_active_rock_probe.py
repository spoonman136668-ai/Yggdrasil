#!/usr/bin/env python3
"""CS08 original-source JAX RockSample: public Bayesian adaptive-location challenge.

Original source-native reset_env/step_env only, no source reconstruction.
All policies operate on source-public observations, original published sensor
law and their own retained public histories, NEVER on source-private map bits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

from screen_cs06_original_pobax import source_identity, original_scoped_modules, array, UPSTREAM

FIRST="1a8593e10ed41b8dff6df1ea0eb2d81f789b0913"
MAP_KEYS=(7411,7429)
RESET_SEEDS=(1400200,1400201,1400202,1400203)
POSITIONS=tuple((row,col) for row in range(5) for col in range(4))
ARMS=("adaptive_location_information_gain","uniform_row_major","random_equal_budget")
BLOCKS=20
CHECKS_PER_BLOCK=8
CHECKS_TOTAL=BLOCKS*CHECKS_PER_BLOCK
HYPOTHESES=tuple((position,hidden_bit) for position in POSITIONS for hidden_bit in (0,1))
K=40
def need(cond,why):
    if not cond: raise RuntimeError(why)
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def source_position(obs):
    import numpy as np
    x=array(obs).reshape(-1)
    need(x.shape==(15,) and np.isfinite(x).all(),"ORIGINAL_PUBLIC_OBSERVATION_INVALID")
    rows,cols=x[:5],x[5:10]
    need(np.all((rows==0)|(rows==1)) and
         np.all((cols==0)|(cols==1)) and
         int(rows.sum())==1 and int(cols.sum())==1,"PUBLIC_SOURCE_POSITION_NOT_ONEHOT")
    return int(rows.argmax()),int(cols.argmax())
def p_report_positive(probe,location,bit):
    d=math.hypot(probe[0]-location[0],probe[1]-location[1])
    reliability=(1+2.0**(-d/20.0))/2.0
    return reliability if bit else (1-reliability)
Q=tuple(tuple(p_report_positive(probe,loc,bit) for loc,bit in HYPOTHESES)
        for probe in POSITIONS)
def entropy(probabilities):
    return -sum(p*math.log(p) for p in probabilities if p>0.)
class Posterior:
    def __init__(self):
        self.p=[1/K]*K
        self.updates=0
    def marginal(self):
        return [self.p[2*i]+self.p[2*i+1] for i in range(len(POSITIONS))]
    def _updated(self,idx,sign):
        q=Q[idx]
        v=[weight*(prob if sign==1 else (1-prob))
           for weight,prob in zip(self.p,q)]
        total=sum(v)
        need(total>0 and math.isfinite(total),"IMPOSSIBLE_PUBLIC_CHECK_UNDER_KNOWN_LAW")
        return [z/total for z in v],total
    def update(self,idx,sign):
        need(0<=idx<20 and sign in (-1,1),"ILLEGAL_PUBLIC_SENSOR_PROBE")
        self.p,prob=self._updated(idx,sign)
        self.updates+=1
        need(abs(sum(self.p)-1)<1e-10,"POSTERIOR_NORMALIZATION_FAILURE")
    def coordinate_information(self,idx):
        before=entropy(self.marginal())
        postplus,pplus=self._updated(idx,1)
        postminus,pminus=self._updated(idx,-1)
        need(abs(pplus+pminus-1)<1e-9,"SOURCE_SENSOR_PROB_MASS_INVALID")
        def marginal(h):
            return [h[2*i]+h[2*i+1] for i in range(20)]
        gain=before-(pplus*entropy(marginal(postplus))+
                     pminus*entropy(marginal(postminus)))
        need(math.isfinite(gain) and gain>-1e-10,"EXPECTED_INFORMATION_INVALID")
        return max(0.,gain)
    def estimate(self):
        marg=self.marginal()
        loc=max(range(len(POSITIONS)),key=lambda i:(marg[i],-i))
        bit1=sum(self.p[1::2])
        return POSITIONS[loc],int(bit1>0.5),marg
    def state(self):
        return {"hypotheses":K,"posterior_joint":self.p,"n_updates":self.updates,
                "source_law_known_conventional_control":True}
def choose(arm,block_index,posterior,current_public_position,rng):
    if arm==ARMS[1]:return block_index
    if arm==ARMS[2]:return rng.randrange(20)
    need(arm==ARMS[0],"POLICY_IDENTITY_INVALID")
    gains=[posterior.coordinate_information(i) for i in range(20)]
    top=max(gains)
    tied=[i for i,g in enumerate(gains) if top-g<=1e-12]
    return min(tied,key=lambda i:(abs(current_public_position[0]-POSITIONS[i][0])+
                                   abs(current_public_position[1]-POSITIONS[i][1]),i))
def legal_step(env,state,action,key):
    import jax
    obs,new_state,reward,done,info=env.step_env(
        jax.random.PRNGKey(key),state,int(action),env.default_params)
    need(not bool(done) and float(reward)==0.0 and isinstance(info,dict) and not info,
         "ORIGINAL_ACTION_TERMINATED_OR_REWARDED")
    return obs,new_state
def navigate(env,obs,state,target,map_idx,trial_idx,movements):
    start=len(movements)
    while source_position(obs)!=target:
        row,col=source_position(obs)
        if row!=target[0]:
            action=0 if row>target[0] else 2
        else:
            action=3 if col>target[1] else 1
        need(len(movements)<200,"SOURCE_PUBLIC_TRAVEL_EXCEEDS_BUDGET")
        before=(row,col)
        key=5000000+100000*map_idx+1000*trial_idx+len(movements)
        obs,state=legal_step(env,state,action,key)
        after=source_position(obs)
        need(after!=before and 0<=after[1]<4,"INVALID_NATIVE_PUBLIC_NAVIGATION")
        need(all(float(x)==0. for x in array(obs)[10:]),
             "MOVE_RETURNED_UNEXPECTED_ORIGINAL_ROCK_REPORT")
        movements.append((action,before,after))
    return obs,state,len(movements)-start
def original_public_episode(env,map_idx,trial_idx,arm,reset_seed):
    import jax
    obs,state=env.reset_env(jax.random.PRNGKey(reset_seed),env.default_params)
    need(array(obs).shape==(15,) and all(float(x)==0. for x in array(obs)[10:]),
         "ORIGINAL_SOURCE_RESET_OBSERVATION_MALFORMED")
    init_public_position=source_position(obs)
    posterior=Posterior()
    rng=random.Random(6100000+1000*map_idx+trial_idx)
    trace=[]
    moves=[]
    before=time.process_time_ns()
    for block in range(BLOCKS):
        idx=choose(arm,block,posterior,source_position(obs),rng)
        dest=POSITIONS[idx]
        obs,state,move_count=navigate(env,obs,state,dest,map_idx,trial_idx,moves)
        block_reads=[]
        for _ in range(CHECKS_PER_BLOCK):
            check_index=posterior.updates
            key=4100000+100000*map_idx+1000*trial_idx+check_index
            obs,state=legal_step(env,state,5,key)
            vals=array(obs)
            need(source_position(vals)==dest and vals.shape==(15,) and
                 int(sum(float(x)!=0. for x in vals[10:]))==1 and
                 all(float(v)==0. for v in vals[11:]) and
                 float(vals[10]) in (-1.,1.),"ORIGINAL_CHECK_PUBLIC_OUTPUT_INVALID")
            sign=int(vals[10])
            posterior.update(idx,sign)
            block_reads.append(sign)
        trace.append({"block":block,"public_probe":dest,
                      "native_travel_steps":move_count,
                      "public_original_signs":block_reads})
    need(len(trace)==20 and posterior.updates==160 and len(moves)<=200,
         "SOURCE_CHECK_OR_MOVEMENT_BUDGET_INVALID")
    chosen,bit,coord_prob=posterior.estimate()
    # EVALUATOR ONLY, AFTER all policy choices and posterior fit are frozen.
    true_coord=tuple(int(x) for x in array(env.rock_positions)[0])
    true_bit=int(array(state.rock_morality)[0])
    need(true_coord in POSITIONS and true_bit in (0,1),"SOURCE_AUDITOR_TRUTH_INVALID")
    true_i=POSITIONS.index(true_coord)
    return {
        "map_constructor_public_engineering_key":MAP_KEYS[map_idx],
        "reset_public_engineering_seed":reset_seed,"policy":arm,
        "source_native_reset_calls":1,
        "source_native_check_calls":posterior.updates,
        "source_native_movement_calls":len(moves),
        "source_native_total_action_calls":posterior.updates+len(moves),
        "initial_public_position":init_public_position,
        "number_distinct_public_probe_locations":len({tuple(z["public_probe"]) for z in trace}),
        "public_probe_signs_and_move_counts":trace,
        "public_navigation_sha256":digest(moves),
        "public_posterior_state_sha256":digest(posterior.state()),
        "public_final_joint_posterior":posterior.p,
        "public_inferred_rock0_location":chosen,
        "public_inferred_rock0_hidden_value":bit,
        "public_final_coordinate_entropy_nats":entropy(coord_prob),
        "auditor_only_true_rock0_location":true_coord,
        "auditor_only_true_rock0_hidden_value":true_bit,
        "auditor_only_MAP_location_correct":int(chosen==true_coord),
        "auditor_only_MAP_hidden_value_correct":int(bit==true_bit),
        "auditor_only_final_p_true_coordinate":coord_prob[true_i],
        "auditor_only_true_coordinate_NLL_nats":-math.log(max(1e-300,coord_prob[true_i])),
        "process_cpu_ns_policy_including_original_simulator":time.process_time_ns()-before,
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    opt=ap.parse_args()
    root=Path(opt.upstream).resolve()
    out=Path(opt.out);out.mkdir(parents=True,exist_ok=True)
    rec={"schema":"mass.cs08.original_POBAX_public_adaptive_rock0_information.v1",
         "frozen_first_prereg_commit":FIRST,"original_source_commit":UPSTREAM,
         "public_source_dev_only":True,"all_models_source_law_privileged_conventional":True,
         "source_private_map_or_morality_available_to_policy":False,
         "native_Wingless_Yggdrasil_model_trained":False,
         "independent_sealed_first_use_consumed":False,
         "protected_holdout_consumed":False,
         "controller_science_admission_observed":False,
         "source_reward_collected":0,"source_good_rocks_consumed":0,
         "model_resource_isolation_qualified":False,
         "disposition":"PUBLIC_CS08_SOURCE_OR_BUDGET_INVALID","original_public_records":[]}
    start=time.process_time_ns()
    try:
        rec["source_identity"]=source_identity(root)
        RockSample,_=original_scoped_modules(root)
        import jax,inspect
        need(Path(inspect.getfile(RockSample)).resolve()==root/"pobax/envs/jax/rocksample.py",
             "NOT_ORIGINAL_SOURCE_CLASS")
        maps=[]
        for map_i,key in enumerate(MAP_KEYS):
            cfg=root/"pobax/envs/configs/rocksample_5_5_config.json"
            env=RockSample(key=jax.random.PRNGKey(key),config_path=cfg)
            need(env.size==5 and env.k==5 and float(env.half_efficiency_distance)==20.,
                 "ORIGINAL_CONFIG_SOURCE_DRIFT")
            raw_map=[tuple(int(w) for w in x) for x in array(env.rock_positions)]
            need(len(set(raw_map))==5 and set(raw_map)<=set(POSITIONS),
                 "SOURCE_MAP_CONFIG_DRIFT")
            maps.append(tuple(raw_map))
            for trial_i,s in enumerate(RESET_SEEDS):
                cohort=[]
                for arm in ARMS:
                    x=original_public_episode(env,map_i,trial_i,arm,s)
                    need(x["source_native_check_calls"]==160 and
                         x["source_native_reset_calls"]==1,
                         "FROZEN_EQUAL_CHECK_BUDGET_INVALID")
                    cohort.append(x)
                truths={(tuple(z["auditor_only_true_rock0_location"]),
                         z["auditor_only_true_rock0_hidden_value"]) for z in cohort}
                need(len(truths)==1,"PAIRED_SOURCE_HIDDEN_STATE_NOT_IDENTICAL")
                rec["original_public_records"].append({
                    "map_constructor_key":key,"original_reset_seed":s,
                    "three_original_source_public_policy_episodes":cohort})
            print("CS08_ORIGINAL_CONSTRUCTOR_MAP_DONE="+str(key),flush=True)
        need(maps[0]!=maps[1],"FRESH_ORIGINAL_MAPS_NOT_DISTINCT")
        need(len(rec["original_public_records"])==8,"EIGHT_PAIRED_CASES_BUDGET")
        policies={}
        for arm in ARMS:
            rows=[next(z for z in item["three_original_source_public_policy_episodes"]
                       if z["policy"]==arm) for item in rec["original_public_records"]]
            policies[arm]={
                "public_source_episodes":len(rows),
                "original_public_CHECK_interventions":sum(z["source_native_check_calls"] for z in rows),
                "source_native_movement_interventions":sum(z["source_native_movement_calls"] for z in rows),
                "auditor_correct_index0_location_out_of_8":sum(z["auditor_only_MAP_location_correct"] for z in rows),
                "auditor_correct_index0_morality_out_of_8":sum(z["auditor_only_MAP_hidden_value_correct"] for z in rows),
                "mean_true_rock0_coordinate_NLL_nats":sum(z["auditor_only_true_coordinate_NLL_nats"] for z in rows)/8.,
                "mean_prob_correct_rock0_coordinate":sum(z["auditor_only_final_p_true_coordinate"] for z in rows)/8.,
                "mean_coordinate_entropy_nats":sum(z["public_final_coordinate_entropy_nats"] for z in rows)/8.,
                "process_cpu_ns_including_source_simulator":sum(z["process_cpu_ns_policy_including_original_simulator"] for z in rows)}
        rec["arm_score_summary"]=policies
        rec["original_reset_calls"]=8*3
        rec["original_native_CHECK_calls"]=8*3*160
        rec["original_native_movement_calls"]=sum(policies[a]["source_native_movement_interventions"] for a in ARMS)
        rec["original_native_action_calls"]=rec["original_native_CHECK_calls"]+rec["original_native_movement_calls"]
        need(rec["original_reset_calls"]==24 and rec["original_native_CHECK_calls"]==3840,
             "TRIAL_NATIVE_PUBLIC_INTERVENTION_BUDGET_INVALID")
        a,u,r=(policies[x] for x in ARMS)
        gain=(a["auditor_correct_index0_location_out_of_8"]>=u["auditor_correct_index0_location_out_of_8"]+2 and
              a["auditor_correct_index0_location_out_of_8"]>=r["auditor_correct_index0_location_out_of_8"]+2 and
              a["mean_true_rock0_coordinate_NLL_nats"]<=u["mean_true_rock0_coordinate_NLL_nats"]-.10 and
              a["mean_true_rock0_coordinate_NLL_nats"]<=r["mean_true_rock0_coordinate_NLL_nats"]-.10)
        rec["prospectively_defined_robust_adaptive_advantage"]=gain
        rec["disposition"]=("PUBLIC_CS08_ACTIVE_PROBING_GAIN_ON_ORIGINAL_PUBLIC_DEV" if gain
             else "PUBLIC_CS08_NO_ROBUST_ACTIVE_LOCATION_GAIN")
        rec["reward_efficiency"]="NOT_TESTED_ZERO_NATIVE_SAMPLE_ACTIONS"
        rec["rock_index_location_finite_accuracy"]="OBSERVED_NOT_GUARANTEED"
        rec["frozen_source_native_public_records_sha256"]=digest(rec["original_public_records"])
    except Exception as e:
        rec["first_failure"]=type(e).__name__+":"+str(e)[:900]
    finally:
        rec["process_cpu_ns_total_original_source_and_bayesian"]=time.process_time_ns()-start
        rec["process_inclusive_peak_RSS_kib_not_isolated_models"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs08-original-pobax-adaptive-source-receipt.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print("CS08_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS08_SOURCE_OR_BUDGET_INVALID" else 0
if __name__=="__main__":
    sys.exit(main())
