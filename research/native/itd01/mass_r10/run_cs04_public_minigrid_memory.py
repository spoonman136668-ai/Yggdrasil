#!/usr/bin/env python3
"""CS04: original MiniGrid PUBLIC-only navigation and FIT-trained memory tests.

Never accesses environment-private agent position, grid, correct exit or hidden
source state. Encodes one legal public key/ball observation bit by hand; fits
action consequences from actual original-source FIT episodes. This is NOT a
native Wingless/Yggdrasil model nor independent sealed scientific transfer.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time

PIN="7f5853792ea7f04f75614661006d87fcf949f26d"
FIRST="c5da78ae952babe03cbdd062118ab3a928317ec7"
BLOBS={
 "minigrid/envs/memory.py":"660b0a1b769948034c87bb421759c2b9a4f24548",
 "minigrid/minigrid_env.py":"eb29e9a902de0715ab77ec981a2113576d7664fa",
 "minigrid/__init__.py":"41b4a731255d19bdf61072b7100e752a759a3ae4",
 "pyproject.toml":"61ab88372ca553af255a42564260994be808ac12"
}
REPS=(0,1,2)
ROLE_COUNTS={"FIT":192,"VALID":64,"DEV":128}
ARMS=("learned_history_table","trained_logistic_history","trained_episodic_k3",
      "trained_current_frame_only","trained_history_erased_at_fork","fixed_upper")
ETA,L2,PASSES=0.08,0.003,12

def guard(ok, msg):
    if not ok: raise RuntimeError(msg)
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def seed(role,rep,i):
    bases={"FIT":950000,"VALID":960000,"DEV":970000}
    return bases[role]+1000*rep+i
def check_source(root):
    root=Path(root).resolve()
    def cmd(args):
        p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=25)
        return p.returncode,p.stdout.strip()
    rc,head=cmd(["git","rev-parse","HEAD"])
    guard(rc==0 and head==PIN,"UPSTREAM_SHA_DRIFT")
    for path,expected in sorted(BLOBS.items()):
        rc,got=cmd(["git","hash-object","--",path])
        guard(rc==0 and got==expected,"UPSTREAM_BLOB_DRIFT:"+path)
    rc,_=cmd(["git","diff","--exit-code","--","minigrid","pyproject.toml"])
    guard(rc==0,"UPSTREAM_TRACKED_SOURCE_CHANGED")
    return {"git_commit":PIN,"source_blobs":BLOBS}
def objbit(observation):
    """PUBLIC handcrafted vision, not learned image representation."""
    import numpy as np
    from minigrid.core.constants import OBJECT_TO_IDX
    guard(set(observation)>= {"image","direction","mission"},
          "ORIGINAL_OBSERVATION_MISSING")
    image=observation["image"]
    guard(image.shape==(7,7,3),"NOT_ORIGINAL_7x7_VISION")
    indices=(OBJECT_TO_IDX["key"],OBJECT_TO_IDX["ball"])
    hits=np.argwhere(np.isin(image[:,:,0],indices))
    guard(len(hits)==1,"PUBLIC_OBJECT_UNAVAILABLE_OR_AMBIGUOUS")
    i,j=[int(x) for x in hits[0]]
    return int(image[i,j,0]==indices[0]) # key=1, ball=0
def front_wall(obs):
    from minigrid.core.constants import OBJECT_TO_IDX
    guard(obs["image"].shape==(7,7,3),"PUBLIC_WALL_VISION_INVALID")
    return int(obs["image"][3,5,0])==OBJECT_TO_IDX["wall"]
def public_navigation(env,initial_obs):
    from minigrid.core.actions import Actions
    obs=initial_obs
    guard(obs["image"].shape==(7,7,3) and int(obs["direction"])==0,
          "ORIGINAL_INITIAL_PUBLIC_DIRECTION_INVALID")
    calls=0
    def act(a):
        nonlocal obs,calls
        guard(a in (Actions.left,Actions.right,Actions.forward),
              "NONPUBLIC_NAVIGATION_ACTION")
        new,reward,terminated,truncated,info=env.step(a)
        calls+=1
        guard(terminated is False and truncated is False and float(reward)==0.,
              "ORIGINAL_PRE_FORK_NAVIGATION_TERMINATED")
        guard(isinstance(info,dict),"ORIGINAL_INFO_FORMAT_INVALID")
        obs=new
        return obs
    act(Actions.left)
    act(Actions.left)
    guard(int(obs["direction"])==2,"WESTWARD_NAVIGATION_NOT_PUBLIC")
    west=0
    while not front_wall(obs):
        guard(west<11,"WESTERN_CUE_NOT_REACHABLE_PUBLICLY")
        act(Actions.forward)
        west+=1
    act(Actions.right)
    guard(int(obs["direction"])==3,"NORTH_PUBLIC_DIRECTION_FAIL")
    cue=objbit(obs)
    act(Actions.right)
    guard(int(obs["direction"])==0,"EAST_PUBLIC_DIRECTION_FAIL")
    east=0
    while not front_wall(obs):
        guard(east<12,"PUBLIC_FORK_NOT_REACHABLE")
        act(Actions.forward)
        east+=1
    act(Actions.left)
    guard(int(obs["direction"])==3,"PUBLIC_FORK_ORIENTATION_INVALID")
    upper=objbit(obs)
    guard(calls<=32,"PRE_FORK_STEP_BUDGET")
    return cue,upper,obs,calls
def play(seed_number, fork_policy):
    """fork_policy(cue,upper)-> 0 upper, 1 lower. No other private input."""
    from minigrid.envs.memory import MemoryEnv
    from minigrid.core.actions import Actions
    env=MemoryEnv(size=13,random_length=False,agent_view_size=7,render_mode=None)
    try:
        observation,reset_info=env.reset(seed=seed_number)
        guard(isinstance(reset_info,dict),"RESET_INFO_INVALID")
        cue,upper,obs,count=public_navigation(env,observation)
        choice=fork_policy(cue,upper)
        guard(type(choice) is int and choice in (0,1),"FORK_CHOICE_NOT_BINARY")
        def step(a):
            nonlocal obs,count
            obs,reward,terminated,truncated,info=env.step(a)
            count+=1
            guard(isinstance(info,dict),"FINAL_INFO_INVALID")
            return float(reward),bool(terminated),bool(truncated)
        if choice==1:
            for _ in range(2):
                r,t,ex=step(Actions.left)
                guard(not t and not ex and r==0.0,"PRE_LOWER_EXIT_EARLY_TERMINAL")
        r,t,ex=step(Actions.forward)
        guard(t and not ex,"NO_SOURCE_NATIVE_TERMINAL")
        guard(count<5*13**2,"ORIGINAL_NAV_BUDGET_EXCEEDED")
        return {"seed":seed_number,"cue_public_bit":cue,"upper_public_bit":upper,
                "fork_branch":choice,"success":int(r>0),"original_reward":r,
                "source_native_steps":count}
    finally:
        env.close()
class HistoryTable:
    name=ARMS[0]
    def __init__(self):
        self.counts=[[[[1,1] for a in range(2)] for u in range(2)] for c in range(2)]
        self.updates=0
    def fit(self,rows):
        for r in rows:
            self.counts[r["cue_public_bit"]][r["upper_public_bit"]][r["fork_branch"]][r["success"]]+=1
            self.updates+=1
        guard(self.updates==len(rows),"HISTORY_TABLE_FIT_INVALID")
    def choose(self,c,u):
        q=lambda a:self.counts[c][u][a][1]/sum(self.counts[c][u][a])
        return int(q(1)>q(0)) # action 0 wins ties
    def state(self):
        return {"method":"FIT_history_cue_reward_table","counts":self.counts,"updates":self.updates}
class LogisticHistory:
    name=ARMS[1]
    def __init__(self):
        self.weights=[0.]*8
        self.updates=0
    def _vec(self,c,u,a):
        return (1,c,u,a,c*u,c*a,u*a,c*u*a)
    def predict(self,c,u,a):
        z=sum(w*x for w,x in zip(self.weights,self._vec(c,u,a)))
        return 1/(1+math.exp(-max(-30,min(30,z))))
    def fit(self,rows):
        for _ in range(PASSES):
            for r in rows:
                x=self._vec(r["cue_public_bit"],r["upper_public_bit"],r["fork_branch"])
                p=self.predict(r["cue_public_bit"],r["upper_public_bit"],r["fork_branch"])
                for j,v in enumerate(x):
                    self.weights[j]+=ETA*((r["success"]-p)*v-L2*self.weights[j])
                self.updates+=1
        guard(self.updates==len(rows)*PASSES,"LOGISTIC_TRAIN_UPDATES_INVALID")
    def choose(self,c,u):
        return int(self.predict(c,u,1)>self.predict(c,u,0))
    def state(self):
        return {"method":"public_history_logistic","weights":self.weights,
                "updates":self.updates,"passes":PASSES,"eta":ETA,"l2":L2}
class EpisodicK3:
    name=ARMS[2]
    def __init__(self):
        self.events=[]
        self.updates=0
    def fit(self,rows):
        self.events=[(r["cue_public_bit"],r["upper_public_bit"],
                      r["fork_branch"],r["success"]) for r in rows]
        self.updates=len(self.events)
    def _reward(self,c,u,a):
        tgt=(c,u,a)
        scores=sorted((sum(v!=t for v,t in zip(x[:3],tgt)),i,x[3])
                      for i,x in enumerate(self.events))
        guard(len(scores)>=3,"EPISODIC_FIT_MISSING")
        return sum(x[2] for x in scores[:3])/3
    def choose(self,c,u):
        return int(self._reward(c,u,1)>self._reward(c,u,0))
    def state(self):
        return {"method":"public_history_exact_context_nearest3",
                "events":self.events,"updates":self.updates}
class FrameOnlyTable:
    name=ARMS[3]
    def __init__(self):
        self.counts=[[[1,1] for a in range(2)] for u in range(2)]
        self.updates=0
    def fit(self,rows):
        for r in rows:
            self.counts[r["upper_public_bit"]][r["fork_branch"]][r["success"]]+=1
            self.updates+=1
    def choose(self,c,u):
        q=lambda a:self.counts[u][a][1]/sum(self.counts[u][a])
        return int(q(1)>q(0))
    def state(self):
        return {"method":"FIT_current_fork_image_only","counts":self.counts,
                "updates":self.updates}
class ErasedHistory:
    name=ARMS[4]
    def __init__(self,history):
        self.counts=json.loads(json.dumps(history.counts))
        self.original_updates=history.updates
    def choose(self,c,u):
        q=lambda a:self.counts[0][u][a][1]/sum(self.counts[0][u][a])
        return int(q(1)>q(0))
    def state(self):
        return {"method":"FIT_copy_history_table_inference_erased_to_bit0",
                "counts":self.counts,"original_updates":self.original_updates}
class FixedUpper:
    name=ARMS[5]
    def choose(self,c,u):return 0
    def state(self):return {"method":"fixed_upper","updates":0}
def score(role,rep,models):
    n=ROLE_COUNTS[role]
    result={}
    frozen={k:digest(m.state()) for k,m in models.items()}
    for name in ARMS:
        model=models[name]
        summary={"episode_count":0,"native_step_count":0,"correct_exits":0,
                 "native_shaped_reward_sum":0.0,"process_cpu_ns_including_simulator":0,
                 "fork_choices":[0,0],"public_trace_hash":None}
        traces=[]
        for i in range(n):
            start=time.process_time_ns()
            row=play(seed(role,rep,i),model.choose)
            summary["process_cpu_ns_including_simulator"]+=time.process_time_ns()-start
            summary["episode_count"]+=1
            summary["native_step_count"]+=row["source_native_steps"]
            summary["correct_exits"]+=row["success"]
            summary["native_shaped_reward_sum"]+=row["original_reward"]
            summary["fork_choices"][row["fork_branch"]]+=1
            traces.append(row)
        guard(summary["episode_count"]==n,"VALID_DEV_ROLE_COUNT_DRIFT")
        summary["success_rate"]=summary["correct_exits"]/n
        summary["public_trace_hash"]=digest(traces)
        summary["serial_state_bytes"]=len(canonical(model.state()).encode())
        result[name]=summary
    guard(frozen=={k:digest(m.state()) for k,m in models.items()},
          "EVALUATION_MODIFIED_FITTED_MODEL_STATE")
    return result
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    opts=ap.parse_args()
    out=Path(opts.out)
    out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs04.original-public-minigrid-learned-cue-memory.v1",
       "first_prereg_sha":FIRST,
       "source_role":"PUBLIC_DEVELOPMENT_ONLY",
       "external_original_source":PIN,
       "source_native_navigation_from_public_observations_only":True,
       "hardcoded_handcrafted_cue_bit_from_public_image":True,
       "trained_raw_image_representation":False,
       "navigation_learned":False,
       "retained_cue_bit_action_learning_from_native_rewards":True,
       "native_wingless_or_yggdrasil_learned_agent_executed":False,
       "first_use_independent_sealed_source":False,
       "protected_heldout_consumed":False,
       "controller_science_authority_exercised":False,
       "per_model_rss_isolated":False,
       "disposition":"PUBLIC_CS04_INVALID_OR_SOURCE_NAVIGATION_NO_GO","replicas":[]}
    raw={"schema":"mass.cs04.shared_frozen_public_fit.v1","replicas":[]}
    try:
        receipt["source"]=check_source(opts.upstream)
        from minigrid.envs.memory import MemoryEnv
        import inspect
        guard(Path(inspect.getfile(MemoryEnv)).resolve()==Path(opts.upstream).resolve()/"minigrid"/"envs"/"memory.py",
              "NOT_ORIGINAL_SOURCE_MEMORY_ENV")
        all_seeds=set()
        for rep in REPS:
            fit=[]
            fit_cpu_start=time.process_time_ns()
            for i in range(ROLE_COUNTS["FIT"]):
                s=seed("FIT",rep,i)
                guard(s not in all_seeds,"PUBLIC_ROLE_SEED_OVERLAP")
                all_seeds.add(s)
                action=int(i%2==1) # alternation: even upper=0, odd lower=1
                row=play(s,lambda c,u,a=action:a)
                guard(row["fork_branch"]==action,"FIT_ACTION_CYCLING_INVALID")
                fit.append(row)
            fit_cpu=time.process_time_ns()-fit_cpu_start
            cells=[[[0,0] for u in range(2)] for c in range(2)]
            for row in fit:
                cells[row["cue_public_bit"]][row["upper_public_bit"]][row["fork_branch"]]+=1
            guard(min(cells[c][u][a] for c in range(2) for u in range(2) for a in range(2))>=3,
                  "FROZEN_PUBLIC_FIT_ACTION_CONTEXT_SUPPORT_INSUFFICIENT")
            raw["replicas"].append({"replica":rep,"public_fit_rows":fit})
            history=HistoryTable();logistic=LogisticHistory();episodic=EpisodicK3();frame=FrameOnlyTable()
            fits={}
            for m in (history,logistic,episodic,frame):
                t=time.process_time_ns()
                m.fit(fit)
                fits[m.name]={"update_count":m.updates,
                              "train_cpu_ns":time.process_time_ns()-t,
                              "state_sha256":digest(m.state()),
                              "state_bytes":len(canonical(m.state()).encode())}
                guard(m.updates>0,"MODEL_NOT_TRAINED")
            models={m.name:m for m in (history,logistic,episodic,frame)}
            models[ARMS[4]]=ErasedHistory(history)
            models[ARMS[5]]=FixedUpper()
            for name in (ARMS[4],ARMS[5]):
                fits[name]={"update_count":0,"train_cpu_ns":0,
                            "state_sha256":digest(models[name].state()),
                            "state_bytes":len(canonical(models[name].state()).encode())}
            frozen={name:digest(m.state()) for name,m in models.items()}
            valid=score("VALID",rep,models)
            dev=score("DEV",rep,models)
            guard(frozen=={name:digest(m.state()) for name,m in models.items()},
                  "SCORED_MODEL_STATE_DRIFT")
            for role in ("VALID","DEV"):
                for i in range(ROLE_COUNTS[role]):
                    s=seed(role,rep,i)
                    guard(s not in all_seeds,"ROLE_SEED_OVERLAP")
                    all_seeds.add(s)
            sr=lambda key:dev[key]["success_rate"]
            gain=(sr(ARMS[0])-sr(ARMS[3]))
            erase=(sr(ARMS[0])-sr(ARMS[4]))
            item={"replica":rep,"fit_episodes":len(fit),
                "fit_native_public_step_calls":sum(r["source_native_steps"] for r in fit),
                "fit_total_native_successes":sum(r["success"] for r in fit),
                "fit_public_sha256":digest(fit),
                "fit_action_context_counts":cells,
                "fit_original_source_cpu_ns":fit_cpu,
                "trained_models":fits,"trained_policy_by_cue_upper":{
                    name:[[models[name].choose(c,u) for u in (0,1)] for c in (0,1)]
                    for name in ARMS},
                "valid":valid,"dev":dev,
                "candidate_minus_memoryless_dev_pp":gain*100,
                "candidate_minus_erased_dev_pp":erase*100,
                "candidate_minus_episodic_dev_pp":(sr(ARMS[0])-sr(ARMS[2]))*100,
                "candidate_vs_memoryless_and_ablation_pass":
                    sr(ARMS[0])>=.9 and sr(ARMS[2])>=.9
                    and gain>=.2 and erase>=.2,
                "process_inclusive_peak_rss_kib_not_model_rss":
                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            receipt["replicas"].append(item)
            print("CS04_REPLICA="+str(rep)+" DEV="+canonical({
                key:dev[key]["correct_exits"] for key in ARMS}),flush=True)
        expected=3*(192+64+128)
        guard(len(all_seeds)==expected,"PUBLIC_SPLIT_COUNT_INVALID")
        receipt["original_episodes_total"]=3*(192+6*(64+128))
        receipt["source_native_original_step_calls_total"]=sum(
            sum(row["source_native_steps"] for row in x["public_fit_rows"])
            for x in raw["replicas"])+sum(
            sum(v["native_step_count"] for v in rep[role].values())
            for rep in receipt["replicas"] for role in ("valid","dev"))
        receipt["shared_original_fit_episodes"]=3*192
        receipt["independent_valid_original_episodes"]=3*64*6
        receipt["independent_dev_original_episodes"]=3*128*6
        receipt["original_public_fit_history_sha256"]=digest(raw)
        need=all(rep["candidate_vs_memoryless_and_ablation_pass"] for rep in receipt["replicas"])
        receipt["disposition"]=(
           "PUBLIC_CS04_ONE_BIT_MEMORY_USE_SUPPORTED_NOT_LEARNED_MEMORY_FORMATION"
           if need else "PUBLIC_CS04_NO_VERIFIED_MEMORY_USE_GAIN")
        receipt["new_architecture_advantage"]="NOT_ESTABLISHED_NOT_NATIVE"
        receipt["fully_autonomous_navigation"]="PUBLIC_RULE_BASED_NOT_LEARNED"
        receipt["independently_unfamiliar_transfer"]="NOT_TESTED"
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:800]
    finally:
        (out/"cs04-public-fit-history.json").write_text(canonical(raw)+"\n")
        (out/"cs04-public-source-receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("CS04_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS04_INVALID_OR_SOURCE_NAVIGATION_NO_GO" else 0
if __name__=="__main__":
    raise SystemExit(main())
