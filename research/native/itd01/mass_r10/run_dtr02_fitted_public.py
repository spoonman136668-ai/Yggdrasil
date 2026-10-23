#!/usr/bin/env python3
"""DTR02 prospective PUBLIC source-native trained reference models; not Yggdrasil."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import resource
import sys
import time
from collections import defaultdict

from isolated_original_dtr_import import original_dtr_classes
from preflight_original_dtr import PIN, BLOBS, command

PREREG = "af6f18730af20fb6a5821f69fde14bbe6757fffa"
REPS = (0, 1, 2)
FIT_N, VALID_N, DEV_N = 256, 64, 128
TRAIN_PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))
CANDIDATE = "learned_logistic_public_state"
TABULAR = "trained_tabular_world"
EPISODIC = "trained_episodic_k3"
FIXED = "fixed_00"
ERASED = "candidate_erased_weights"
ARMS = (CANDIDATE, TABULAR, EPISODIC, FIXED, ERASED)
EPS = 0.08
L2 = 0.003
PASSES = 6

def check(c, reason):
    if not c:
        raise RuntimeError(reason)

def encoded(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(o):
    return hashlib.sha256(encoded(o).encode()).hexdigest()

def bit(n):
    check(type(n) is int and n in (0,1), "NONBINARY_PUBLIC_FIELD")
    return n

def fitseed(rep, i):
    return 1100000 + rep*10000 + i

def validseed(rep, i):
    return 1200000 + rep*10000 + i

def devseed(rep, i):
    return 1300000 + rep*10000 + i

def next_features(s1,x1):
    return [1,bit(s1),bit(x1),s1*x1]

def reward_features(s1,x1,s2,x2):
    a,b,c,d=map(bit,(s1,x1,s2,x2))
    return [1,a,b,c,d,a*b,a*c,a*d,b*c,b*d,c*d,a*b*c,a*b*d,a*c*d,b*c*d,a*b*c*d]

def sigmoid(x):
    return 1/(1+math.exp(-max(-30., min(30.,x))))

def dot(w,x):
    return sum(a*b for a,b in zip(w,x))

class LogisticCandidate:
    name=CANDIDATE
    def __init__(self):
        self.transition=[0.]*4
        self.reward=[0.]*16
        self.updates=0

    def train(self, rows):
        for _ in range(PASSES):
            for row in rows:
                s1,x1,s2,x2,y=row["s1"],row["x1"],row["s2"],row["x2"],row["y"]
                for weights,inputs,target in (
                    (self.transition,next_features(s1,x1),s2),
                    (self.reward,reward_features(s1,x1,s2,x2),y)):
                    p=sigmoid(dot(weights,inputs))
                    for j,val in enumerate(inputs):
                        weights[j]+= EPS * ((target-p)*val - L2*weights[j])
                    self.updates+=1
        check(self.updates==len(rows)*PASSES*2, "CANDIDATE_TRAIN_BUDGET")
        check(any(abs(z)>1e-8 for z in self.reward), "UNTRAINED_REWARD_MODEL")
    def next_prob(self,s1,x1):
        return sigmoid(dot(self.transition,next_features(s1,x1)))
    def reward_prob(self,s1,x1,s2,x2):
        return sigmoid(dot(self.reward,reward_features(s1,x1,s2,x2)))
    def export(self):
        return {"kind":self.name,"transition":self.transition,"reward":self.reward,
                "updates":self.updates,"passes":PASSES,"eta":EPS,"l2":L2}
    def erased(self):
        return LogisticCandidate()

class TabularModel:
    name=TABULAR
    def __init__(self):
        self.transitions=defaultdict(lambda:[1,1])
        self.outcomes=defaultdict(lambda:[1,1])
        self.updates=0
    def train(self,rows):
        for row in rows:
            s1,x1,s2,x2,y=(row[k] for k in ("s1","x1","s2","x2","y"))
            self.transitions[(s1,x1)][s2]+=1
            self.outcomes[(s1,x1,s2,x2)][y]+=1
            self.updates+=2
        check(self.updates==len(rows)*2,"TABULAR_UNTRAINED")
    def next_prob(self,s1,x1):
        a,b=self.transitions[(s1,x1)]
        return b/(a+b)
    def reward_prob(self,s1,x1,s2,x2):
        a,b=self.outcomes[(s1,x1,s2,x2)]
        return b/(a+b)
    def export(self):
        return {"kind":self.name,"transition":sorted((list(k),v) for k,v in self.transitions.items()),
                "reward":sorted((list(k),v) for k,v in self.outcomes.items()),"updates":self.updates}

class EpisodicK3:
    name=EPISODIC
    def __init__(self):
        self.memory=[]
        self.transitions=defaultdict(lambda:[1,1])
        self.updates=0
    def train(self,rows):
        for row in rows:
            tup=tuple(row[k] for k in ("s1","x1","s2","x2","y"))
            self.memory.append(tup)
            self.transitions[tup[0:2]][tup[2]]+=1
            self.updates+=1
        check(len(self.memory)==len(rows),"EPISODIC_UNTRAINED")
    def next_prob(self,s1,x1):
        a,b=self.transitions[(s1,x1)]
        return b/(a+b)
    def reward_prob(self,s1,x1,s2,x2):
        target=(s1,x1,s2,x2)
        scored=sorted(((sum(x!=y for x,y in zip(tup[:4],target)),i,tup[4])
                        for i,tup in enumerate(self.memory)))
        check(len(scored)>=3,"EPISODIC_MISSING_FIT")
        return sum(x[2] for x in scored[:3])/3
    def export(self):
        return {"kind":self.name,"memory":self.memory,
                "transitions":sorted((list(k),v) for k,v in self.transitions.items()),
                "updates":self.updates,"nearest_k":3}

class Fixed:
    name=FIXED
    def train(self,rows): pass
    def choose_first(self,s1): return 0
    def choose_second(self,s1,x1,s2): return 0
    def export(self): return {"kind":self.name,"updates":0}

class Planner:
    def __init__(self,m):
        self.m=m
    def choose_second(self,s1,x1,s2):
        v0=self.m.reward_prob(s1,x1,s2,0)
        v1=self.m.reward_prob(s1,x1,s2,1)
        return int(v1>v0)
    def choose_first(self,s1):
        def value(x1):
            p=self.m.next_prob(s1,x1)
            y0=max(self.m.reward_prob(s1,x1,0,x2) for x2 in (0,1))
            y1=max(self.m.reward_prob(s1,x1,1,x2) for x2 in (0,1))
            return (1-p)*y0+p*y1
        return int(value(1)>value(0))

def original_source_identity(root):
    got=command(["git","rev-parse","HEAD"],root)
    check(got["exit"]==0 and got["stdout"].strip()==PIN,"UPSTREAM_SHA_INVALID")
    for p,h in sorted(BLOBS.items()):
        v=command(["git","hash-object","--",p],root)
        check(v["exit"]==0 and v["stdout"].strip()==h,"UPSTREAM_BLOB_DRIFT:"+p)
    clean=command(["git","diff","--exit-code","--","causal_gym","setup.py"],root)
    check(clean["exit"]==0,"UPSTREAM_SOURCE_NOT_CLEAN")
    return {"commit":PIN,"original_blob_hashes":BLOBS}

def episode(DTRPCH,seed,chooser):
    """Whitelist only caller-provided public policy callbacks: never raw info."""
    check(0<seed<9000000,"INVALID_PUBLIC_SEED")
    env=DTRPCH()
    s1,_=env.reset(seed=seed)
    bit(s1)
    cb0=[]
    def action0(public_s1):
        check(public_s1==s1,"PUBLIC_STAGE0_CONTEXT_MISMATCH")
        a=bit(chooser.choose_first(public_s1))
        cb0.append((public_s1,a))
        return a
    s2,r0,t0,tr0,_=env.do(action0)
    bit(s2)
    check(r0==0 and t0 is False and tr0 is False and len(cb0)==1,
          "PUBLIC_FIRST_STAGE_INVALID")
    x1=cb0[0][1]
    cb1=[]
    def action1(public_s1,public_x1,public_s2):
        check((public_s1,public_x1,public_s2)==(s1,x1,s2),
              "PUBLIC_STAGE1_CONTEXT_MISMATCH")
        a=bit(chooser.choose_second(public_s1,public_x1,public_s2))
        cb1.append((public_s1,public_x1,public_s2,a))
        return a
    final,y,t1,tr1,_=env.do(action1)
    bit(y)
    check(final is None and t1 is True and tr1 is False and len(cb1)==1,
          "PUBLIC_FINAL_STAGE_INVALID")
    return {"seed":seed,"s1":s1,"x1":x1,"s2":s2,"x2":cb1[0][3],"y":y}

class PairChooser:
    def __init__(self,a,b): self.a,self.b=a,b
    def choose_first(self,s1): return self.a
    def choose_second(self,s1,x1,s2): return self.b

def freeze_state(model):
    return digest(model.export())

def evaluate(DTRPCH,rep,role,models):
    size=VALID_N if role=="VALID" else DEV_N
    seed_fn=validseed if role=="VALID" else devseed
    stats={key:{"successes":0,"episodes":0,"cpu_ns":0,"action_pairs":[],"transcript_hashes":[]}
           for key in ARMS}
    immutable={key:freeze_state(m) for key,m in models.items()}
    for i in range(size):
        seed=seed_fn(rep,i)
        actions={}
        for key in ARMS:
            m=models[key]
            chooser=Planner(m) if key not in (FIXED,) else m
            start=time.process_time_ns()
            row=episode(DTRPCH,seed,chooser)
            ns=time.process_time_ns()-start
            stats[key]["cpu_ns"]+=ns
            stats[key]["successes"]+=row["y"]
            stats[key]["episodes"]+=1
            stats[key]["action_pairs"].append([row["x1"],row["x2"]])
            stats[key]["transcript_hashes"].append(digest(row))
            actions[key]=[row["x1"],row["x2"]]
        check(actions[ERASED]==actions[FIXED],
              "ERASED_WEIGHTS_NOT_NEUTRAL_FIXED_POLICY")
    for key,m in models.items():
        check(freeze_state(m)==immutable[key],"EVALUATION_ALTERED_MODEL_STATE:"+key)
    report={}
    for key in ARMS:
        s=stats[key]
        check(s["episodes"]==size,"EVAL_ROLE_COUNT_DRIFT")
        report[key]={
            "successes":s["successes"],"episodes":size,
            "reward_rate":s["successes"]/size,
            "evaluation_process_cpu_ns":s["cpu_ns"],
            "public_transcripts_sha256":digest(s["transcript_hashes"]),
            "action_trace_sha256":digest(s["action_pairs"]),
            "state_bytes":len(encoded(models[key].export()).encode())
        }
    # Public action changes are legal exploratory signals, not causal proof.
    diff=sum(a!=b for a,b in zip(stats[CANDIDATE]["action_pairs"],
                                   stats[ERASED]["action_pairs"]))
    return report,diff

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=pathlib.Path(args.upstream).resolve()
    target=pathlib.Path(args.out)
    target.mkdir(parents=True,exist_ok=True)
    summary={
       "schema":"mass.dtr02.fitted-public-original-source.v1",
       "frozen_first_prereg":PREREG,
       "source_role":"PUBLIC_DEVELOPMENT_ONLY",
       "native_yggdrasil_model_executed":False,
       "independently_sealed_unfamiliar_transfer":False,
       "scientific_first_use":False,
       "protected_source_consumed":False,
       "ckb_controller_admission_observed":False,
       "original_dtr01_smoke_seeds_reused":False,
       "canonical_whole_package_import_claim":False,
       "true_per_model_rss_isolated":False,
       "resource_parity_scientifically_qualified":False,
       "disposition":"PUBLIC_DTR02_INVALID_SOURCE_OR_PARITY",
       "replicas":[]
    }
    raw={"schema":"mass.dtr02.fit-public-traces.v1","replicas":[]}
    try:
        summary["source"]=original_source_identity(root)
        original_scm,DTRPCH,_=original_dtr_classes(root)
        check(original_scm.__name__=="DTRSCM","SOURCE_NATIVE_CLASS_DRIFT")
        seen=set()
        for r in REPS:
            fit=[]
            for i in range(FIT_N):
                seed=fitseed(r,i)
                check(seed not in seen,"ROLE_SEED_COLLISION")
                seen.add(seed)
                fixed=TRAIN_PAIRS[i%len(TRAIN_PAIRS)]
                fit.append(episode(DTRPCH,seed,PairChooser(*fixed)))
            raw["replicas"].append({"index":r,"fit":fit})
            check(len(fit)==FIT_N and
                  all(fit[i]["x1"]==TRAIN_PAIRS[i%4][0] and
                      fit[i]["x2"]==TRAIN_PAIRS[i%4][1] for i in range(FIT_N)),
                  "FIT_EXPLORATION_DRIFT")
            candidate=LogisticCandidate()
            tab=TabularModel()
            episodic=EpisodicK3()
            cpu={}
            for key,model in ((CANDIDATE,candidate),(TABULAR,tab),(EPISODIC,episodic)):
                a=time.process_time_ns()
                model.train(fit)
                cpu[key]=time.process_time_ns()-a
            models={
                CANDIDATE:candidate,TABULAR:tab,EPISODIC:episodic,
                FIXED:Fixed(),ERASED:candidate.erased()}
            pre={name:freeze_state(m) for name,m in models.items()}
            valid,valid_action_diff=evaluate(DTRPCH,r,"VALID",models)
            dev,dev_action_diff=evaluate(DTRPCH,r,"DEV",models)
            check(pre=={n:freeze_state(m) for n,m in models.items()},
                  "MODEL_DRIFT_AFTER_SCORE")
            for i in range(VALID_N):
                seed=validseed(r,i)
                check(seed not in seen,"VALID_SEED_COLLISION")
                seen.add(seed)
            for i in range(DEV_N):
                seed=devseed(r,i)
                check(seed not in seen,"DEV_SEED_COLLISION")
                seen.add(seed)
            strongest=max((TABULAR,EPISODIC),key=lambda name:dev[name]["successes"])
            item={"replica":r,"fit_episodes":len(fit),
                  "fit_public_transcript_sha256":digest(fit),
                  "fit_reward_successes":sum(t["y"] for t in fit),
                  "model_fit_cpu_ns":cpu,
                  "model_updates":{
                      CANDIDATE:candidate.updates,
                      TABULAR:tab.updates,EPISODIC:episodic.updates,
                      FIXED:0,ERASED:0
                  },
                  "model_sha256":pre,"valid":valid,"dev":dev,
                  "valid_candidate_erasure_action_changes":valid_action_diff,
                  "dev_candidate_erasure_action_changes":dev_action_diff,
                  "strongest_trained_control":strongest,
                  "candidate_minus_best_trained_reward_rate":
                     (dev[CANDIDATE]["successes"]-dev[strongest]["successes"])/DEV_N,
                  "process_maxrss_linux_kib_not_model_rss":
                     resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            summary["replicas"].append(item)
            print("DTR02_REPLICA="+str(r)+" "+json.dumps({
                k:dev[k]["successes"] for k in ARMS},sort_keys=True),flush=True)
        check(len(seen)==len(REPS)*(FIT_N+VALID_N+DEV_N),"ROLE_GLOBAL_SEED_COLLISION")
        diffs=[x["candidate_minus_best_trained_reward_rate"] for x in summary["replicas"]]
        changes=[x["dev_candidate_erasure_action_changes"] for x in summary["replicas"]]
        exploratory=(all(d>=0 for d in diffs) and sum(d>0 for d in diffs)>=2
                     and all(v>0 for v in changes))
        summary["disposition"]=("PUBLIC_DTR02_EXPLORATORY_POSITIVE_NOT_TRANSFER" if exploratory
                                else "PUBLIC_DTR02_NO_GAIN")
        summary["complete_original_fit_episodes"]=len(REPS)*FIT_N
        summary["complete_validation_original_episodes"]=len(REPS)*VALID_N*len(ARMS)
        summary["complete_dev_original_episodes"]=len(REPS)*DEV_N*len(ARMS)
        summary["original_native_episode_instances"]=len(REPS)*(FIT_N+(VALID_N+DEV_N)*len(ARMS))
        summary["original_native_action_calls"]=2*summary["original_native_episode_instances"]
        summary["all_fit_public_traces_sha256"]=digest(raw)
        summary["resource_nonregression_claim"]=False
    except Exception as exc:
        summary["disposition"]="PUBLIC_DTR02_INVALID_SOURCE_OR_PARITY"
        summary["first_failure"]=type(exc).__name__+":"+str(exc)[:700]
    finally:
        (target/"fit-public-traces.json").write_text(json.dumps(raw,indent=2,sort_keys=True)+"\n")
        (target/"dtr02-receipt.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("DTR02_DISPOSITION="+summary["disposition"],flush=True)
    return 2 if summary["disposition"]=="PUBLIC_DTR02_INVALID_SOURCE_OR_PARITY" else 0

if __name__=="__main__":
    sys.exit(main())
