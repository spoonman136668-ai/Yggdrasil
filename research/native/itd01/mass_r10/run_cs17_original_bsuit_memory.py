#!/usr/bin/env python3
"""CS17: real original DeepMind MemoryChain, native R7 cue cells and CS14
action-owned reward learning; strong equally original-FIT-trained controls.

PUBLIC development only: hand-designed capture/gating NOT learned memory routing.
Source public reset/step only, no source-private cue or query access.
"""
from __future__ import annotations
from dataclasses import asdict
import argparse
import hashlib
import importlib
import inspect
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time
import types

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from cs14_action_owned_native_cells import ActionOwnedNativeCells,LocalCell

FIRST="618364d18ee36ee24c50c80161530248527ddf79"
BSUITE_COMMIT="8109eb23291b1b8d9f55b3753ccb9f222f18eff2"
SOURCE_BLOB="2fc3544ee9fbb29cab19fa22f311f8bc40409d52"
SOURCE_BASE_BLOB="6c28a9d672c00cae1f420b85bbcbe8ca31cdcd6c"
NATIVE_BLOB="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
ACTION_NATIVE_BLOB="33bdae91b5aa9697f01c3b41a62ce824c9a9e61b"
LENGTHS=(9,25)
FIT_N,VALID_N,DEV_N=192,32,96
REPLICAS=(0,1,2)
BITS=6
ARMS=("authentic_native_cue_cells_plus_action_owned",
      "trained_full_episodic_action_table",
      "trained_contextual_logistic_action_reward",
      "trained_recurrent_cue_and_reward_table",
      "native_retained_cue_erased",
      "trained_current_frame_query_only",
      "source_known_replay_oracle")

def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def gitblob(path):
    r=subprocess.run(["git","hash-object",str(path)],capture_output=True,
                     text=True,timeout=20)
    need(r.returncode==0,"GIT_BLOB_IDENTITY_CHECK_UNAVAILABLE")
    return r.stdout.strip()
def source_class(root):
    source=root/"bsuite/environments/memory_chain.py"
    base=root/"bsuite/environments/base.py"
    need(gitblob(source)==SOURCE_BLOB and gitblob(base)==SOURCE_BASE_BLOB,
         "ORIGINAL_DEEPMIND_EXTERNAL_SOURCE_BLOB_IDENTITY_DRIFT")
    native=HERE.parent/"r7"/"native_cells.py"
    action=HERE/"cs14_action_owned_native_cells.py"
    need(gitblob(native)==NATIVE_BLOB and gitblob(action)==ACTION_NATIVE_BLOB,
         "ACTUAL_UNMODIFIED_YGG_NATIVE_SOURCE_DRIFT")
    # Avoid bsuite's top-level import of unrelated benchmark/baseline families.
    # This only creates the original package namespace; importlib loads the
    # EXACT untouched original memory_chain and base module files off disk.
    if "bsuite" in sys.modules:
        del sys.modules["bsuite"]
    package=types.ModuleType("bsuite")
    package.__path__=[str(root/"bsuite")]
    package.__package__="bsuite"
    sys.modules["bsuite"]=package
    for name in ("bsuite.environments.memory_chain","bsuite.environments.base",
                 "bsuite.environments"):
        sys.modules.pop(name,None)
    original=importlib.import_module("bsuite.environments.memory_chain")
    need(Path(inspect.getfile(original.MemoryChain)).resolve()==source.resolve(),
         "IMPORTED_SOURCE_NOT_ORIGINAL_DEEPMIND_MEMORY_CHAIN")
    need(Path(inspect.getfile(original.MemoryChain.__mro__[1])).resolve()==base.resolve(),
         "IMPORTED_ORIGINAL_BASE_SOURCE_NOT_AUTHENTIC")
    return original.MemoryChain

def source_seed(role,delay_index,rep,index):
    base={"FIT":3400000,"VALID":3500000,"DEV":3600000}[role]
    return base+300000*delay_index+10000*rep+index

def cue_from_public(observation,length,first=False):
    import numpy as np
    obs=np.asarray(observation)
    need(obs.shape==(1,BITS+2) and obs.dtype==np.float32,
         "ORIGINAL_SOURCE_PUBLIC_OBS_SHAPE_DTYPE_DRIFT")
    v=obs[0]
    need(math.isfinite(float(v[0])) and all(math.isfinite(float(z)) for z in v),
         "ORIGINAL_SOURCE_PUBLIC_OBS_NAN")
    if first:
        need(abs(float(v[0])-1.)<1e-7 and all(float(z) in (-1.,1.) for z in v[2:]),
             "ORIGINAL_RESET_FIRST_CUE_ORIGINAL_OBS_INVALID")
        return tuple(int(float(z)>0) for z in v[2:])
    need(all(float(z)==0 for z in v[2:]),
         "ORIGINAL_MIDSTREAM_CUE_LEAK_OR_SOURCE_STEP_DRIFT")
    return None

def query_from_preterminal(obs,length):
    import numpy as np
    x=np.asarray(obs)
    need(x.shape==(1,BITS+2) and
         abs(float(x[0,0])-1./length)<2e-6 and
         all(float(z)==0 for z in x[0,2:]),
         "ORIGINAL_PRETERMINAL_QUERY_TIME_OR_BLANK_CUE_INVALID")
    q=float(x[0,1])
    need(q in tuple(float(i) for i in range(BITS)),
         "ORIGINAL_PRETERMINAL_QUERY_INVALID")
    return int(q)

class NativeTransientCue:
    def __init__(self):
        self.cells=[LocalCell() for _ in range(BITS)]
    def capture(self,cue):
        need(len(cue)==BITS and all(type(b) is int and b in (0,1) for b in cue),
             "NATIVE_FIRST_ORIGINAL_CUE_INVALID")
        for cell,bit in zip(self.cells,cue):
            cell.feel(True,bool(bit))
        need(all(c.updates==1 for c in self.cells),"ORIGINAL_R7_CUE_MEMORY_NOT_CAPTURED")
    def at(self,q):
        need(q in range(BITS),"NATIVE_LATE_PUBLIC_QUERY_INDEX_INVALID")
        return int(self.cells[q].signal(True)>0)
    def source_state(self):return [asdict(x) for x in self.cells]
class PlainCue:
    def __init__(self):self.bits=None
    def capture(self,bits):self.bits=tuple(bits)
    def at(self,q):return self.bits[q]

class LearnedNative:
    def __init__(self):
        self.cells=ActionOwnedNativeCells()
        self.updates=0
    def fit(self,record):
        b=record["original_source_public_queried_cue_bit"]
        a=record["original_source_terminal_action"]
        y=int(record["original_source_terminal_reward"]==1.)
        self.cells.learn_completed_public_consequence(b,a,y,1,delay_steps=2)
        self.updates+=1
    def choose(self,bit,query):return self.cells.choose(bit)
    def trained_state(self):return self.cells.checkpoint().hex()
    def cold_restore(self):
        blob=self.cells.checkpoint()
        self.cells=ActionOwnedNativeCells.restore(blob)
        need(blob==self.cells.checkpoint(),"ACTUAL_CS14_ACTION_OWNED_COLD_RESTORE_NOT_EXACT")
        return {"checkpoint_SHA256":hashlib.sha256(blob).hexdigest(),
                "checkpoint_bytes":len(blob),
                "genuine_original_terminal_feedback_updates":self.cells.completed_feedback_updates}
class Episodic:
    def __init__(self):self.events=[];self.updates=0
    def fit(self,z):
        self.events.append((z["original_source_public_queried_cue_bit"],
                            z["original_source_terminal_action"],
                            z["original_source_terminal_reward"]))
        self.updates+=1
    def choose(self,b,query):
        def success(a):
            wins=1;losses=1
            for cb,act,r in self.events:
                if cb==b and act==a:
                    wins+=int(r==1);losses+=int(r==-1)
            return wins/(wins+losses)
        return int(success(1)>success(0))
    def trained_state(self):return canon(self.events)
class Tabular:
    def __init__(self):
        self.counts={(b,a):[1,1] for b in (0,1) for a in (0,1)}
        self.updates=0
    def fit(self,z):
        key=(z["original_source_public_queried_cue_bit"],
             z["original_source_terminal_action"])
        self.counts[key][int(z["original_source_terminal_reward"]==1.)]+=1
        self.updates+=1
    def choose(self,b,query):
        def value(a):
            loss,win=self.counts[(b,a)]
            return win/(win+loss)
        return int(value(1)>value(0))
    def trained_state(self):return canon({str(k):v for k,v in self.counts.items()})
class Logistic:
    def __init__(self):self.w=[0.]*4;self.updates=0
    @staticmethod
    def f(b,a):return (1.,float(b),float(a),float(b*a))
    def fit(self,z):
        b=z["original_source_public_queried_cue_bit"];a=z["original_source_terminal_action"]
        f=self.f(b,a)
        pred=sum(w*v for w,v in zip(self.w,f))
        p=1/(1+math.exp(-max(-30,min(30,pred))))
        target=float(z["original_source_terminal_reward"]==1.)
        self.w=[w+.08*((target-p)*v-.003*w) for w,v in zip(self.w,f)]
        self.updates+=1
    def choose(self,b,query):
        def logit(a):return sum(w*x for w,x in zip(self.w,self.f(b,a)))
        return int(logit(1)>logit(0))
    def trained_state(self):return canon({"w":self.w,"updates":self.updates})
class QueryOnly:
    def __init__(self):
        self.counts={(q,a):[1,1] for q in range(BITS) for a in (0,1)}
        self.updates=0
    def fit(self,z):
        key=(z["original_source_public_final_query"],
             z["original_source_terminal_action"])
        self.counts[key][int(z["original_source_terminal_reward"]==1.)]+=1
        self.updates+=1
    def choose(self,b,query):
        def win(a):
            neg,pos=self.counts[(query,a)]
            return pos/(neg+pos)
        return int(win(1)>win(0))
    def trained_state(self):return canon({str(k):v for k,v in self.counts.items()})
class Oracle:
    def fit(self,z):pass
    def choose(self,b,query):return b
    def trained_state(self):return "privileged_publicly_known_source_rule"
def build_models(records):
    models={
       ARMS[0]:LearnedNative(),
       ARMS[1]:Episodic(),
       ARMS[2]:Logistic(),
       ARMS[3]:Tabular(),
       ARMS[4]:LearnedNative(),
       ARMS[5]:QueryOnly(),
       ARMS[6]:Oracle()}
    meta={}
    for name,agent in models.items():
        t=time.process_time_ns()
        if name==ARMS[2]:
            for _ in range(25):
                for z in records:agent.fit(z)
        else:
            for z in records:agent.fit(z)
        elapsed=time.process_time_ns()-t
        cold=agent.cold_restore() if isinstance(agent,LearnedNative) else {}
        state=agent.trained_state()
        meta[name]={"FIT_source_owned_examples":FIT_N if name!=ARMS[6] else 0,
                    "FIT_training_cpu_ns":elapsed,
                    "serialized_persistent_state_bytes":len(state.encode()),
                    "persisted_model_state_SHA256":hashlib.sha256(state.encode()).hexdigest(),
                    "cold_original_native_checkpoint":cold,
                    "learning_update_operations":getattr(agent,"updates",0)}
    need(models[ARMS[0]].trained_state()==models[ARMS[4]].trained_state(),
         "FROZEN_NATIVE_SOURCE_FIT_ERASURE_MODEL_NOT_EQUAL")
    n=models[ARMS[0]].cells
    groups={str(b)+":"+str(a):n.buckets[(b,a)]["count"] for b in (0,1) for a in (0,1)}
    need(n.completed_feedback_updates==FIT_N and all(k>=25 for k in groups.values()),
         "ORIGINAL_SOURCE_FIT_STATE_ACTION_TRUE_SUPPORT_TOO_LOW")
    meta["actual_source_FIT_native_bit_action_support"]=groups
    return models,meta

def original_episode(cls,length,seed,role,i,agent=None,arm=None):
    env=cls(memory_length=length,num_bits=BITS,seed=seed)
    begin=time.process_time_ns()
    ts=env.reset()
    need(ts.first() and ts.reward is None,"ORIGINAL_DEEPMIND_RESET_NOT_REAL_FIRST")
    cue=cue_from_public(ts.observation,length,first=True)
    if agent is not None:
        if arm==ARMS[0]:mem=NativeTransientCue()
        elif arm==ARMS[4]:mem=NativeTransientCue()
        elif arm==ARMS[5]:mem=None
        else:mem=PlainCue()
        if mem is not None and arm!=ARMS[4]:
            mem.capture(cue)
    else:
        mem=None
    original_pub_obs=[ts.observation.tolist()]
    for step in range(length):
        ts=env.step(0)
        need(not ts.last() and float(ts.reward)==0. and
             ts.discount==1.,"ORIGINAL_NONTERMINAL_ACTION_REWARD_DRIFT")
        original_pub_obs.append(ts.observation.tolist())
        if step==0:
            first_repeat=cue_from_public(ts.observation,length,first=True)
            need(first_repeat==cue,"ORIGINAL_FIRST_STEP_DUPLICATED_PUBLIC_CUE_CHANGED")
        else:
            cue_from_public(ts.observation,length,first=False)
    q=query_from_preterminal(ts.observation,length)
    if agent is None:
        action=int(i%2)
    else:
        bit=0 if mem is None or arm==ARMS[4] else int(mem.at(q))
        action=int(agent.choose(bit,q))
    need(action in (0,1),"ILLEGAL_ORIGINAL_SOURCE_BINARY_ACTION")
    final=env.step(action)
    need(final.last() and final.reward in (-1.,1.) and final.discount==0.,
         "ORIGINAL_DEEPMIND_TERMINAL_REWARD_OR_DONE_DRIFT")
    r=float(final.reward)
    original_pub_obs.append(final.observation.tolist())
    d={"original_role":role,"original_source_seed":seed,
       "original_source_memory_length":length,
       "original_source_public_initial_cue_bits":cue,
       "original_source_public_final_query":q,
       "original_source_public_queried_cue_bit":cue[q], # AUDIT field not fed to DEV model
       "original_source_terminal_action":action,
       "original_source_terminal_reward":r,
       "original_source_episode_genuine_step_calls":length+1,
       "original_source_first_to_last_public_obs_SHA256":sha(original_pub_obs),
       "source_and_agent_process_CPU_ns":time.process_time_ns()-begin}
    return d

def score(cls,length,di,rep,role,name,agent):
    n=VALID_N if role=="VALID" else DEV_N
    original=[original_episode(cls,length,source_seed(role,di,rep,i),
                               role,i,agent=agent,arm=name) for i in range(n)]
    wins=sum(int(z["original_source_terminal_reward"]==1.) for z in original)
    return {"real_original_source_episodes":n,
            "original_source_terminal_reward_mean":sum(z["original_source_terminal_reward"] for z in original)/n,
            "original_source_correct_decision_rate":wins/n,
            "original_source_legal_step_calls":sum(z["original_source_episode_genuine_step_calls"] for z in original),
            "original_source_ACTUAL_step_env_and_policy_CPU_ns":sum(z["source_and_agent_process_CPU_ns"] for z in original),
            "original_source_public_role_trace_SHA256":sha(original),
            "source_native_public_episode_records":original}

def main():
    p=argparse.ArgumentParser();p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    o=p.parse_args()
    root=Path(o.upstream).resolve()
    dest=Path(o.out);dest.mkdir(parents=True,exist_ok=True)
    result={"schema":"mass.cs17.real_original_bsuit_memory_action.v1",
            "frozen_FIRST_only_prospective_protocol":FIRST,
            "actual_original_external_source":"google-deepmind/bsuite@"+BSUITE_COMMIT,
            "source_only_original_public_reset_step":True,
            "original_private_hidden_cue_or_query_policy_access":False,
            "actual_R7_native_LocalCell_source_unchanged":True,
            "actual_CS14_action_owned_source_unchanged":True,
            "handcoded_first_cue_capture_not_learned_memory_gating":True,
            "original_heldout_independent_source_first_use":False,
            "native_r7_historical_integration":"FAIL_PRESERVED",
            "disposition":"PUBLIC_CS17_SOURCE_NATIVE_PROTOCOL_INVALID",
            "scenarios":[]}
    fitarchive={"schema":"mass.cs17.original_DeepMind_public_original_fit.v1",
                "scenarios":[]}
    t0=time.process_time_ns()
    try:
        cls=source_class(root)
        for di,length in enumerate(LENGTHS):
            for rep in REPLICAS:
                fittime=time.process_time_ns()
                shared=[original_episode(cls,length,source_seed("FIT",di,rep,i),
                                         "FIT",i) for i in range(FIT_N)]
                fitcpu=time.process_time_ns()-fittime
                need(len(shared)==FIT_N and
                     all(d["original_source_terminal_action"]==i%2
                         for i,d in enumerate(shared)),
                     "FROZEN_FIT_ORIGINAL_SOURCE_ACTION_SCHEDULE_CHANGED")
                fitarchive["scenarios"].append({
                    "delay":length,"replica":rep,
                    "original_source_192_shared_FIT_episodes":shared})
                models,meta=build_models(shared)
                model_state={name:agent.trained_state() for name,agent in models.items()}
                valid={name:score(cls,length,di,rep,"VALID",name,models[name]) for name in ARMS}
                dev={name:score(cls,length,di,rep,"DEV",name,models[name]) for name in ARMS}
                need(all(agent.trained_state()==model_state[name] for name,agent in models.items()),
                     "SOURCE_VALID_DEV_UPDATED_FROZEN_ORIGINAL_FIT_MODEL")
                for role_data in (valid,dev):
                    for i in range(VALID_N if role_data is valid else DEV_N):
                        original_observations={
                            z["source_native_public_episode_records"][i][
                                "original_source_first_to_last_public_obs_SHA256"]
                            for z in role_data.values()}
                        # This trace includes original terminal observations;
                        # in source MemoryChain they do not depend on chosen
                        # action, and all arms must share identical source reset.
                        need(len(original_observations)==1,
                             "PUBLIC_SOURCE_ORIGINAL_PAIRED_ROLE_OBSERVATIONS_DRIFT")
                native=dev[ARMS[0]]["original_source_terminal_reward_mean"]
                source_best=max(dev[name]["original_source_terminal_reward_mean"]
                                for name in (ARMS[1],ARMS[2],ARMS[3],ARMS[6]))
                erased=dev[ARMS[4]]["original_source_terminal_reward_mean"]
                current=dev[ARMS[5]]["original_source_terminal_reward_mean"]
                qualified=(native>=.9 and native-erased>=.5 and
                           native-current>=.5 and native>=source_best-.05)
                result["scenarios"].append({
                    "memory_length":length,"source_replica":rep,
                    "FIT_original_source_training_episodes":FIT_N,
                    "FIT_source_genuine_actions":FIT_N*(length+1),
                    "FIT_original_source_cpu_ns":fitcpu,
                    "source_192_shared_public_FIT_SHA256":sha(shared),
                    "fitted_model_source_action_support_and_resources":meta,
                    "original_source_actual_VALID":valid,
                    "original_source_actual_DEV":dev,
                    "native_minus_native_cue_erased_original_reward":native-erased,
                    "native_minus_trained_current_frame_original_reward":native-current,
                    "native_minus_best_fitted_or_source_oracle_original_reward":native-source_best,
                    "prospective_original_native_retained_cue_condition":qualified})
                print("CS17_SOURCE_LENGTH="+str(length)+" REP="+str(rep)+
                      " DEV_TRUE_REWARD="+canon({name:round(z["original_source_terminal_reward_mean"],4)
                        for name,z in dev.items()}),flush=True)
        for rep in REPLICAS:
            shorter=next(x for x in result["scenarios"] if x["memory_length"]==9 and x["source_replica"]==rep)
            longer=next(x for x in result["scenarios"] if x["memory_length"]==25 and x["source_replica"]==rep)
            need(longer["original_source_actual_DEV"][ARMS[0]]["original_source_terminal_reward_mean"] >=
                 shorter["original_source_actual_DEV"][ARMS[0]]["original_source_terminal_reward_mean"]-.05,
                 "ORIGINAL_SOURCE_LONG_DELAY_NATIVE_RETENTION_REGRESSION")
        result["original_source_FIT_episodes"]=len(REPLICAS)*len(LENGTHS)*FIT_N
        result["original_source_VALID_episodes"]=len(REPLICAS)*len(LENGTHS)*len(ARMS)*VALID_N
        result["original_source_DEV_episodes"]=len(REPLICAS)*len(LENGTHS)*len(ARMS)*DEV_N
        result["real_original_source_resets"]=sum(result[k] for k in (
            "original_source_FIT_episodes","original_source_VALID_episodes",
            "original_source_DEV_episodes"))
        result["real_original_source_action_calls"]=sum(
            (FIT_N+len(ARMS)*(VALID_N+DEV_N))*(length+1)
            for length in LENGTHS for _ in REPLICAS)
        need(result["real_original_source_resets"]==6528 and
             result["real_original_source_action_calls"]==117504,
             "PROSPECTIVE_TRUE_EXTERNAL_SOURCE_EPISODE_COUNT_DRIFT")
        result["shared_original_source_FIT_transcript_SHA256"]=sha(fitarchive)
        result["disposition"]=(
            "PUBLIC_CS17_NATIVE_SOURCE_PARTIAL_OBSERVATION_AND_REWARDED_MEMORY_SUPPORTED"
            if all(x["prospective_original_native_retained_cue_condition"]
                   for x in result["scenarios"])
            else "PUBLIC_CS17_NATIVE_PARTIAL_OBS_NO_QUALIFIED_ADVANTAGE")
        result["novel_native_superiority_over_strong_conventional"]="NOT_ESTABLISHED"
        result["independent_unfamiliar_source_family_first_use"]="NONE_PREINSPECTED_PUBLIC"
        result["general_action_consequence_transition_cognition"]="NOT_TESTED_TERMINAL_FLAG_CONSTANT"
    except Exception as e:
        result["first_failure"]=type(e).__name__+":"+str(e)[:1050]
    finally:
        result["original_source_plus_model_process_CPU_ns"]=time.process_time_ns()-t0
        result["original_source_plus_model_peak_process_RSS_KiB"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (dest/"cs17-real-original-bsuite-native-memory-receipt.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n")
        (dest/"cs17-original-public-FIT-source.json").write_text(canon(fitarchive)+"\n")
    print("CS17_DISPOSITION="+result["disposition"],flush=True)
    return 2 if result["disposition"]=="PUBLIC_CS17_SOURCE_NATIVE_PROTOCOL_INVALID" else 0
if __name__=="__main__":
    raise SystemExit(main())
