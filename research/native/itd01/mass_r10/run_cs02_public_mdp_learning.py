#!/usr/bin/env python3
"""CS02: genuine source-native PUBLIC learning comparison; no protected first use."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

from isolated_original_mdp_import import original_mdp_classes
from preflight_original_dtr import PIN, BLOBS, command

FIRST = "e7b0cc68ddc7974bc26e9f10ee3026bc40daf77e"
UPSTREAM_MDP_BLOB = "6264ec5450754c009e98c3e85f6d5927ece0a9ab"
REPS = (0, 1, 2)
FIT_N, VALID_N, DEV_N, HORIZON = 256, 64, 128, 30
ETA, GAMMA, REGULARIZATION, PASSES = 0.08, 0.95, 0.003, 5
LOG = "fitted_logistic_state_reward"
TAB = "trained_contextual_tabular_reward"
Q = "trained_contextual_tabular_td"
BLIND = "trained_context_blind_action_reward"
MASK = "logistic_current_observation_mask"
FIXED = "fixed_action_zero"
ARMS = (LOG, TAB, Q, BLIND, MASK, FIXED)

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def bit(x):
    try:
        i = int(x)
    except (ValueError, TypeError) as e:
        raise RuntimeError("NONBINARY_PUBLIC_INPUT") from e
    need(i in (0,1) and bool(x == i), "NONBINARY_PUBLIC_INPUT")
    return i

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)

def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()

def seed(role,r,i):
    bases={"FIT":2100000,"VALID":2200000,"DEV":2300000}
    return bases[role]+r*10000+i

def features(s,a):
    return (1,s,a,s*a)

def logistic(z):
    import math
    return 1/(1+math.exp(-max(-30.0,min(30.0,z))))

class FittedLogistic:
    def __init__(self):
        self.w = [0.0]*4
        self.updates=0
    def fit(self,rows):
        for _ in range(PASSES):
            for s,a,y,next_s,final in rows:
                xx=features(s,a)
                p=logistic(sum(v*w for v,w in zip(xx,self.w)))
                for j,v in enumerate(xx):
                    self.w[j]+=ETA*((y-p)*v-REGULARIZATION*self.w[j])
                self.updates+=1
        need(self.updates==len(rows)*PASSES,"LOGISTIC_FIT_BUDGET")
        need(any(abs(x)>1e-6 for x in self.w),"LOGISTIC_UNFITTED")
    def predict(self,s,a):
        xx=features(s,a)
        return logistic(sum(v*w for v,w in zip(xx,self.w)))
    def choose(self,s):
        return int(self.predict(s,1)>self.predict(s,0))
    def state(self):
        return {"kind":LOG,"weights":self.w,"updates":self.updates,
                "eta":ETA,"passes":PASSES,"l2":REGULARIZATION}

class TabularRewards:
    def __init__(self):
        self.cells=[[[1,1] for a in range(2)] for s in range(2)]
        self.updates=0
    def fit(self,rows):
        for s,a,y,n,final in rows:
            self.cells[s][a][y]+=1
            self.updates+=1
        need(self.updates==len(rows),"TABULAR_FIT_BUDGET")
    def choose(self,s):
        score=lambda a:self.cells[s][a][1]/sum(self.cells[s][a])
        return int(score(1)>score(0))
    def state(self):
        return {"kind":TAB,"counts":self.cells,"updates":self.updates}

class TabularTD:
    def __init__(self):
        self.q=[[0.,0.],[0.,0.]]
        self.updates=0
    def fit(self,rows):
        for _ in range(PASSES):
            for s,a,y,ns,final in rows:
                target=y+(0 if final else GAMMA*max(self.q[ns]))
                self.q[s][a]+=ETA*(target-self.q[s][a])
                self.updates+=1
        need(self.updates==len(rows)*PASSES,"Q_FIT_BUDGET")
        need(any(abs(q)>1e-6 for rr in self.q for q in rr),"Q_UNFITTED")
    def choose(self,s):
        return int(self.q[s][1]>self.q[s][0])
    def state(self):
        return {"kind":Q,"q":self.q,"updates":self.updates,
                "eta":ETA,"gamma":GAMMA,"passes":PASSES}

class BlindRewards:
    def __init__(self):
        self.counts=[[1,1],[1,1]]
        self.updates=0
    def fit(self,rows):
        for s,a,y,n,final in rows:
            self.counts[a][y]+=1
            self.updates+=1
        need(self.updates==len(rows),"BLIND_FIT_BUDGET")
    def choose(self,s):
        score=lambda a:self.counts[a][1]/sum(self.counts[a])
        return int(score(1)>score(0))
    def state(self):
        return {"kind":BLIND,"counts":self.counts,"updates":self.updates}

class MaskedLogistic:
    def __init__(self,trained):
        self.w=list(trained.w)
        self.original_fitted_updates=trained.updates
    def choose(self,s):
        # Force public S=0 at INFERENCE ONLY: preserve original learned weights.
        score=lambda a:logistic(sum(v*w for v,w in zip(features(0,a),self.w)))
        return int(score(1)>score(0))
    def state(self):
        return {"kind":MASK,"weights":self.w,"copied_training_updates":self.original_fitted_updates,
                "mask":"inference_public_state_forced_to_zero"}

class FixedZero:
    def choose(self,s): return 0
    def state(self): return {"kind":FIXED,"updates":0}

class ExploreAlternating:
    def __init__(self,index):self.index=index;self.t=0
    def choose(self,s):
        a=(self.t+self.index)%2
        self.t+=1
        return a
    def state(self):return {"mode":"public-context-blind-alternating","episode_index":self.index}

def pinned_source(root):
    x=command(["git","rev-parse","HEAD"],root)
    need(x["exit"]==0 and x["stdout"].strip()==PIN,"UPSTREAM_COMMIT_INVALID")
    pinned={**BLOBS,"causal_gym/envs/mdp.py":UPSTREAM_MDP_BLOB}
    for path,expected in sorted(pinned.items()):
        z=command(["git","hash-object","--",path],root)
        need(z["exit"]==0 and z["stdout"].strip()==expected,"UPSTREAM_BLOB_DRIFT:"+path)
    d=command(["git","diff","--exit-code","--","causal_gym","setup.py"],root)
    need(d["exit"]==0,"UPSTREAM_SOURCE_MODIFIED")
    return {"exact_source_commit":PIN,"verified_original_git_blobs":pinned}

def source_episode(Source,episode_seed,policy):
    env=Source()
    initial,info=env.reset(seed=episode_seed)
    need(isinstance(info,dict),"RESET_INFO_SHAPE")
    s=bit(initial)
    rows=[]
    for i in range(HORIZON):
        callbacks=[]
        def pick(public_s):
            value=bit(public_s)
            need(value==s,"CURRENT_PUBLIC_STATE_MISMATCH")
            a=bit(policy.choose(value))
            callbacks.append([value,a])
            return a
        ns,r,ended,truncated,_hidden_info=env.do(pick)
        ns=bit(ns);reward=bit(r)
        need(len(callbacks)==1,"CALLBACK_ARITY_OR_COUNT_INVALID")
        need(ended is False and truncated is False,
             "UNEXPECTED_ORIGINAL_MDP_STOP_BEFORE_HORIZON")
        action=callbacks[0][1]
        rows.append((s,action,reward,ns,int(i==HORIZON-1)))
        s=ns
    need(len(rows)==HORIZON,"ORIGINAL_MDP_ACTION_BUDGET_DRIFT")
    return rows

def train_all(fit):
    log=FittedLogistic();tab=TabularRewards();q=TabularTD();blind=BlindRewards()
    models={LOG:log,TAB:tab,Q:q,BLIND:blind}
    training={}
    for name,m in models.items():
        start=time.process_time_ns()
        m.fit(fit)
        training[name]={"cpu_ns":time.process_time_ns()-start,
                        "fitted_updates":m.updates}
    models[MASK]=MaskedLogistic(log)
    models[FIXED]=FixedZero()
    for name,m in models.items():
        training.setdefault(name,{"cpu_ns":0,"fitted_updates":0})
        training[name]["serialized_state_bytes"]=len(canon(m.state()).encode())
        training[name]["parameter_sha256"]=sha(m.state())
    return models,training

def score(Source,r,role,models):
    n=VALID_N if role=="VALID" else DEV_N
    cost={name:{"reward":0,"episodes":0,"interventions":0,"cpu_ns":0,
                "public_action_by_state":[[0,0],[0,0]],
                "role_trace_sha256":None} for name in ARMS}
    streams={name:hashlib.sha256() for name in ARMS}
    before={name:sha(m.state()) for name,m in models.items()}
    for i in range(n):
        case_seed=seed(role,r,i)
        for name in ARMS:
            start=time.process_time_ns()
            rows=source_episode(Source,case_seed,models[name])
            dt=time.process_time_ns()-start
            record=cost[name]
            record["cpu_ns"]+=dt
            record["reward"]+=sum(z[2] for z in rows)
            record["episodes"]+=1
            record["interventions"]+=len(rows)
            for s,a,y,ns,t in rows:record["public_action_by_state"][s][a]+=1
            streams[name].update((canon({"seed":case_seed,"rows":rows})+"\n").encode())
    for name,m in models.items():
        need(before[name]==sha(m.state()),"DEV_OR_VALID_MODEL_MUTATED:"+name)
        a=cost[name]
        need(a["episodes"]==n and a["interventions"]==n*HORIZON,
             "SOURCE_ROLE_BUDGET_DRIFT:"+name)
        a["reward_per_decision"]=a["reward"]/a["interventions"]
        a["mean_30_step_return"]=a["reward"]/a["episodes"]
        a["role_trace_sha256"]=streams[name].hexdigest()
        a["model_state_bytes"]=len(canon(m.state()).encode())
    return cost

def main():
    args=argparse.ArgumentParser()
    args.add_argument("--upstream",required=True)
    args.add_argument("--out",required=True)
    opts=args.parse_args()
    root=Path(opts.upstream).resolve()
    out=Path(opts.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs02.original-source-public-learning.v1",
             "first_frozen_prereg_sha":FIRST,
             "source_is_original_external_public_dev":True,
             "trained_native_wingless_or_yggdrasil":False,
             "independently_unfamiliar_task_tested":False,
             "protected_first_use_consumed":False,
             "controller_science_admission_observed":False,
             "reused_dtr01_or_cs01_engineering_seeds":False,
             "costs_are_not_isolated_per_model_memory":True,
             "zero_hard_false_positives_not_qualified":True,
             "disposition":"PUBLIC_CS02_INVALID",
             "replicas":[]}
    full={"schema":"mass.cs02.original-public-fit-history.v1","replicas":[]}
    try:
        receipt["source_identity"]=pinned_source(root)
        OriginalMDPSCM,OriginalMDPPCH=original_mdp_classes(root)
        need(OriginalMDPSCM.__name__=="MDPSCM","MDP_SOURCE_CLASS_MISMATCH")
        seen=set()
        for r in REPS:
            fit=[]
            start=time.process_time_ns()
            for i in range(FIT_N):
                x=seed("FIT",r,i)
                need(x not in seen,"ROLE_OR_REPLICA_SEED_COLLISION")
                seen.add(x)
                rows=source_episode(OriginalMDPPCH,x,ExploreAlternating(i))
                need(all(action==(t+i)%2 for t,(_,action,_,_,_) in enumerate(rows)),
                     "FIXED_FIT_EXPLORATION_DRIFT")
                fit.extend(rows)
            fit_cpu=time.process_time_ns()-start
            need(len(fit)==FIT_N*HORIZON,"FIT_BUDGET_INVALID")
            visits=[[0,0],[0,0]]
            for s,a,y,ns,t in fit:visits[s][a]+=1
            need(all(visits[s][a]>=1 for s in (0,1) for a in (0,1)),
                 "FIT_INFORMATION_SUPPORT_INSUFFICIENT")
            full["replicas"].append({"replica":r,"rows":fit})
            models,training=train_all(fit)
            before={n:sha(m.state()) for n,m in models.items()}
            valid=score(OriginalMDPPCH,r,"VALID",models)
            dev=score(OriginalMDPPCH,r,"DEV",models)
            need(before=={n:sha(m.state()) for n,m in models.items()},
                 "SCORE_MODEL_STATE_DRIFT")
            for role,n in (("VALID",VALID_N),("DEV",DEV_N)):
                for i in range(n):
                    x=seed(role,r,i)
                    need(x not in seen,"ROLE_OR_REPLICA_SEED_COLLISION")
                    seen.add(x)
            rate=lambda key:dev[key]["reward_per_decision"]
            context_condition=(
                rate(LOG)-rate(BLIND)>=0.10 and
                rate(TAB)-rate(BLIND)>=0.10 and
                rate(LOG)-rate(MASK)>=0.10)
            policy_contexts={name:[models[name].choose(0),models[name].choose(1)]
                             for name in ARMS}
            item={"replica":r,"fit_real_source_episodes":FIT_N,
                  "fit_real_source_action_calls":len(fit),
                  "fit_train_public_sha256":sha(fit),
                  "fit_state_action_visits":visits,
                  "fit_return_successes":sum(x[2] for x in fit),
                  "fit_original_source_cpu_ns":fit_cpu,
                  "model_train_and_state":training,
                  "model_action_by_current_state":policy_contexts,
                  "valid":valid,"dev":dev,
                  "dev_candidate_minus_best_fitted_contextual_control":
                        rate(LOG)-max(rate(TAB),rate(Q)),
                  "dev_candidate_minus_trained_blind":rate(LOG)-rate(BLIND),
                  "dev_contextual_tabular_minus_trained_blind":rate(TAB)-rate(BLIND),
                  "dev_candidate_minus_input_masked":rate(LOG)-rate(MASK),
                  "context_criteria_met_in_replica":context_condition,
                  "process_inclusive_peak_rss_kib_not_model_rss":
                     resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            receipt["replicas"].append(item)
            print("CS02_REPLICA="+str(r)+" DEV_REWARDS="+canon({name:dev[name]["reward"] for name in ARMS}),flush=True)
        need(len(seen)==len(REPS)*(FIT_N+VALID_N+DEV_N),
             "TOTAL_PUBLIC_SEED_COUNT_DRIFT")
        receipt["public_fit_original_source_actions"]=len(REPS)*FIT_N*HORIZON
        receipt["public_valid_original_source_actions"]=len(REPS)*VALID_N*HORIZON*len(ARMS)
        receipt["public_dev_original_source_actions"]=len(REPS)*DEV_N*HORIZON*len(ARMS)
        receipt["all_actual_original_mdp_action_calls"]=sum(
            receipt[k] for k in ("public_fit_original_source_actions",
                                  "public_valid_original_source_actions",
                                  "public_dev_original_source_actions"))
        need(receipt["all_actual_original_mdp_action_calls"]==126720,
             "TOTAL_SOURCE_ACTION_BUDGET_DRIFT")
        receipt["all_fit_public_history_sha256"]=sha(full)
        context=all(x["context_criteria_met_in_replica"] for x in receipt["replicas"])
        receipt["disposition"]=(
            "PUBLIC_CS02_CONTEXT_USAGE_SUPPORTED_NOT_TRANSFER" if context
            else "PUBLIC_CS02_NO_CONTEXT_GAIN")
        receipt["native_novel_cognition_advantage"]="NOT_ESTABLISHED_NO_NATIVE_MODEL"
        receipt["persistent_memory_necessity"]="NOT_TESTED_SOURCE_FULLY_MARKOV_OBSERVABLE"
        receipt["resource_nonregression"]="NOT_QUALIFIED_PROCESS_INCLUSIVE_ONLY"
    except Exception as exc:
        receipt["disposition"]="PUBLIC_CS02_INVALID"
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:800]
    finally:
        (out/"cs02-fit-public-history.json").write_text(json.dumps(full,sort_keys=True)+"\n")
        (out/"cs02-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS02_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS02_INVALID" else 0

if __name__=="__main__":raise SystemExit(main())
