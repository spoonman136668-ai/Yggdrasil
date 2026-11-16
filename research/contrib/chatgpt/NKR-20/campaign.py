"""Three frozen consecutive studies: history, backoff, policy identification.

Reuses already consumed public source observations only. No original source
imports, actions, hidden labels, best-feature search or accepted-state writes.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.public_causal_cells import PublicCausalCells
sys.path.insert(0,str(HERE.parent/"NKR-19"))
import audit as source19

MODES=("state","history","sham")
TARGETS=("reward","after")
TRAIN=range(1,24)
TEST=range(24,31)

def canon(doc):
    return json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(ok,reason):
    if not ok:
        raise ValueError("NKR20_"+reason)

def read_fixture(path):
    d=json.loads(Path(path).read_text())
    need(d["schema"]=="yggdrasil.cvh04.consumed-source-compact-public-fixture.v1"
         and d["source_sha"]==source19.UPSTREAM
         and d["fkp26"]["artifact_zip_sha256"]==source19.ZIP_PIN
         and d["fkp26"]["source_real_first_use_previously_consumed"] is True,
         "SOURCE_FIXTURE_IDENTITY")
    need(type(d["episodes"]) is list and len(d["episodes"])==4,"SOURCE_EPISODES")
    data={}
    for item,seed,pin in zip(d["episodes"],source19.SEEDS,source19.PINS):
        need(item["seed"]==seed and type(item["rows_hex"]) is str,"SEED_ORDER")
        packed=bytes.fromhex(item["rows_hex"])
        need(len(packed)==31 and all(v<64 for v in packed),"SOURCE_PACKING")
        rows=[dict(before=(v>>5)&1,action=(v>>4)&1,reward=(v>>3)&1,
                   after=(v>>2)&1,terminated=bool((v>>1)&1),truncated=bool(v&1))
              for v in packed]
        source19.validate_rows(rows)
        need(sha(canon(rows))==pin==item["public_transitions_sha256"],
             "SOURCE_TRANSITION_SHA")
        need(sum(r["reward"] for r in rows)==item["earned_rewards"],"SOURCE_REWARD")
        data[seed]=rows
    return data

def local(slot):
    return (slot-7,True) if slot>=7 else (slot,False)

def cue(mode,before,previous_reward,world,index):
    need(type(before) is int and before in (0,1),"CURRENT_INPUT")
    need(type(previous_reward) is int and previous_reward in (0,1),"HISTORY_INPUT")
    need(mode in MODES,"FEATURE_MODE")
    if mode=="state":
        bit=0
    elif mode=="history":
        bit=previous_reward
    else:
        bit=hashlib.sha256(f"nkr20-sham:{world}:{index}".encode("ascii")).digest()[0]&1
    return before+2*bit

class NativeHistory:
    """Two unchanged native counter banks, exactly the same capacity per arm."""
    def __init__(self,mode):
        need(mode in MODES,"FEATURE_MODE")
        self.mode=mode
        self.banks=(PublicCausalCells(),PublicCausalCells())

    def observe(self,world,before,action,previous_reward,index,outcomes):
        slot=world*4+cue(self.mode,before,previous_reward,world,index)
        address,retained=local(slot)
        for bank,y in zip(self.banks,outcomes):
            bank.observe(address,action,y,retained=retained)

    def _encoded_counts(self,world,encoded,action):
        slot=world*4+encoded
        # Read the documented fixed native checkpoint representation, not
        # event/source text. Verify via restore before consuming counters.
        import struct
        result=[]
        for bank in self.banks:
            raw=bank.snapshot()
            cold=PublicCausalCells.restore(raw)
            need(cold.snapshot()==raw,"NATIVE_CHECKPOINT_DRIFT")
            counts=struct.unpack(">"+"H"*64,raw[4:-32])
            offset=slot*4+action*2
            result.append((counts[offset],counts[offset+1]))
        return result

    def counts(self,world,before,action,previous_reward,index):
        return self._encoded_counts(world,cue(self.mode,before,previous_reward,world,index),action)

    def parent_predict(self,world,before,action):
        # Pool both child bins from THIS SAME bank. No extra parent memory.
        left=self._encoded_counts(world,before,action)
        right=self._encoded_counts(world,before+2,action)
        return [Fraction(a[1]+b[1]+1,sum(a)+sum(b)+2) for a,b in zip(left,right)]

    def predict(self,world,before,action,previous_reward,index):
        slot=world*4+cue(self.mode,before,previous_reward,world,index)
        address,retained=local(slot)
        return [Fraction(*b.outcome_probability(address,action,retained=retained))
                for b in self.banks]

    def snapshot(self):
        return b"".join(b.snapshot() for b in self.banks)

    @classmethod
    def restore(cls,mode,raw):
        need(type(raw) is bytes and len(raw)==328,"TWO_BANK_BYTES")
        obj=cls(mode)
        obj.banks=(PublicCausalCells.restore(raw[:164]),PublicCausalCells.restore(raw[164:]))
        return obj

def batch_fit(data,mode):
    # Independently aggregate raw public prefixes; never read native weights.
    table={}
    for world,seed in enumerate(source19.SEEDS):
        rows=data[seed]
        for index in TRAIN:
            row,prev=rows[index],rows[index-1]["reward"]
            # Independent context selection, no call to native cue().
            bit=(prev if mode=="history" else 0 if mode=="state" else
                 int(hashlib.sha256(("nkr20-sham:"+str(world)+":"+str(index)).encode()).hexdigest()[:2],16)%2)
            key=(world,row["before"],bit,row["action"])
            values=table.setdefault(key,[[],[]])
            for t,name in enumerate(TARGETS):
                values[t].append(row[name])
    return table

def batch_predict(table,mode,world,before,action,previous_reward,index,*,mle=False):
    bit=(previous_reward if mode=="history" else 0 if mode=="state" else
         int(hashlib.sha256(("nkr20-sham:"+str(world)+":"+str(index)).encode()).hexdigest()[:2],16)%2)
    group=table.get((world,before,bit,action),[[],[]])
    if mle:
        return [Fraction(sum(v),len(v)) if v else Fraction(1,2) for v in group]
    return [Fraction(sum(values)+1,len(values)+2) for values in group]

def fit_native(data,mode):
    model=NativeHistory(mode)
    old=None
    retained=0
    for world,seed in enumerate(source19.SEEDS):
        rows=data[seed]
        for index in TRAIN:
            row=rows[index]
            model.observe(world,row["before"],row["action"],rows[index-1]["reward"],
                          index,[row[n] for n in TARGETS])
        raw=model.snapshot()
        cold=NativeHistory.restore(mode,raw)
        need(cold.snapshot()==raw,"NATIVE_COLD_PARITY")
        if old is not None:
            original,oldworlds=old
            a=[]
            for w in range(oldworlds):
                for before in (0,1):
                    for previous in (0,1):
                        for action in (0,1):
                            a+=cold.predict(w,before,action,previous,1)
            need(a==original,"OLD_WORLD_RETENTION")
            retained+=len(a)
        a=[]
        for w in range(world+1):
            for before in (0,1):
                for previous in (0,1):
                    for action in (0,1):
                        a+=cold.predict(w,before,action,previous,1)
        old=(a,world+1)
    return model,retained

def qdoc(value):
    return {"numerator":value.numerator,"denominator":value.denominator,"value":float(value)}

def scores(trace):
    out={}
    for arm in trace[0]["predictions"]:
        cells={n:[] for n in TARGETS}
        for item in trace:
            for t,n in enumerate(TARGETS):
                p=Fraction(*item["predictions"][arm][t])
                cells[n].append((p-item["truth"][t])**2)
        out[arm]={n:qdoc(sum(v)/len(v)) for n,v in cells.items()}
        both=cells["reward"]+cells["after"]
        out[arm]["pooled"]=qdoc(sum(both)/len(both))
        out[arm]["scored_outputs"]=len(both)
    return out

def value(metric):
    return Fraction(metric["numerator"],metric["denominator"])

def advantage(candidate,control,threshold=Fraction(1,100)):
    return value(control["pooled"])-value(candidate["pooled"])>=threshold

def nonregression(candidate,control):
    return all(value(candidate[n])-value(control[n])<=Fraction(1,100) for n in TARGETS)

def run_history(data):
    models={}
    controls={}
    retention={}
    for mode in MODES:
        models[mode],retention[mode]=fit_native(data,mode)
        controls[mode]=batch_fit(data,mode)
    trace=[]
    for world,seed in enumerate(source19.SEEDS):
        rows=data[seed]
        for i in TEST:
            row,previous=rows[i],rows[i-1]["reward"]
            predictions={}
            for mode in MODES:
                p=models[mode].predict(world,row["before"],row["action"],previous,i)
                b=batch_predict(controls[mode],mode,world,row["before"],row["action"],previous,i)
                need(p==b,"STRONG_BATCH_CONTROL_TIE")
                predictions[mode]=[[q.numerator,q.denominator] for q in p]
                mle=batch_predict(controls[mode],mode,world,row["before"],row["action"],previous,i,mle=True)
                predictions[mode+"_mle"]=[[q.numerator,q.denominator] for q in mle]
            trace.append({"world":world,"index":i,"predictions":predictions,
                          "truth":[row[n] for n in TARGETS]})
    metrics=scores(trace)
    passed=(advantage(metrics["history"],metrics["state"])
            and advantage(metrics["history"],metrics["sham"])
            and nonregression(metrics["history"],metrics["state"]))
    out={"experiment":"NKR-20","classification":"HISTORY_VALUE_SUPPORTED" if passed else
         "HISTORY_VALUE_NOT_ESTABLISHED","scores":metrics,"scientific_pass":False,
         "strongest_control_gain":0,"retained_probability_readouts":retention,
         "native_checkpoint_bytes_each_arm":328,
         "checkpoint_sha256":{m:sha(x.snapshot()) for m,x in models.items()},
         "trace_sha256":sha(canon(trace))}
    return out,models,controls

def run_backoff(data,models,controls):
    trace=[]
    for world,seed in enumerate(source19.SEEDS):
        rows=data[seed]
        for i in TEST:
            row,previous=rows[i],rows[i-1]["reward"]
            parent=models["state"].predict(world,row["before"],row["action"],previous,i)
            predictions={"state":parent,
                         "history":models["history"].predict(world,row["before"],row["action"],previous,i)}
            for mode in ("history","sham"):
                child_counts=models[mode].counts(world,row["before"],row["action"],previous,i)
                pooled=models[mode].parent_predict(world,row["before"],row["action"])
                need(pooled==parent,"POOLED_PARENT_NOT_SAME_INFORMATION")
                shrunk=[(ones+4*pooled[t])/(failures+ones+4)
                        for t,(failures,ones) in enumerate(child_counts)]
                # Fully fitted independent conventional hierarchical reference.
                bit=(previous if mode=="history" else
                     int(hashlib.sha256(f"nkr20-sham:{world}:{i}".encode()).hexdigest()[:2],16)%2)
                raw=controls[mode].get((world,row["before"],bit,row["action"]),[[],[]])
                reference=[(sum(v)+4*batch_predict(controls["state"],"state",world,row["before"],
                           row["action"],previous,i)[t])/(len(v)+4) for t,v in enumerate(raw)]
                need(shrunk==reference,"HIERARCHICAL_EXACT_CONTROL_TIE")
                predictions[mode+"_backoff"]=shrunk
            trace.append({"world":world,"index":i,
                          "predictions":{m:[[q.numerator,q.denominator] for q in p]
                                         for m,p in predictions.items()},
                          "truth":[row[n] for n in TARGETS]})
    metrics=scores(trace)
    passed=(advantage(metrics["history_backoff"],metrics["state"])
            and advantage(metrics["history_backoff"],metrics["history"])
            and nonregression(metrics["history_backoff"],metrics["state"]))
    return {"experiment":"NKR-21","classification":"HIERARCHICAL_VALUE_SUPPORTED" if passed else
            "HIERARCHICAL_VALUE_NOT_ESTABLISHED","fixed_parent_pseudocount_strength":4,
            "scores":metrics,"trace_sha256":sha(canon(trace)),
            "scientific_pass":False,"strongest_control_gain":0}

def policy_bounds(data,indices):
    # No estimated propensities or predicted counterfactual rewards.
    stats={name:{"known_rewards":0,"matched_actions":0,"unknown_rewards":0,"rows":0}
           for name in ("behavior","always0","always1","train_greedy")}
    for world,seed in enumerate(source19.SEEDS):
        rows=data[seed]
        def greedy(before):
            means=[]
            for action in (0,1):
                observed=[rows[i]["reward"] for i in TRAIN
                          if rows[i]["before"]==before and rows[i]["action"]==action]
                means.append(Fraction(sum(observed),len(observed)) if observed else Fraction(1,2))
            return int(means[1]>means[0])
        for i in indices:
            row=rows[i]
            chosen=(row["before"]+i)%2
            need(chosen==row["action"],"ORIGINAL_BEHAVIOR_POLICY_DRIFT")
            actions={"behavior":chosen,"always0":0,"always1":1,
                     "train_greedy":greedy(row["before"])}
            for name,a in actions.items():
                s=stats[name]
                s["rows"]+=1
                if a==row["action"]:
                    s["matched_actions"]+=1
                    s["known_rewards"]+=row["reward"]
                else:
                    s["unknown_rewards"]+=1
    for s in stats.values():
        n=s["rows"]
        s["lower_bound"]=qdoc(Fraction(s["known_rewards"],n))
        s["upper_bound"]=qdoc(Fraction(s["known_rewards"]+s["unknown_rewards"],n))
        s["width"]=qdoc(Fraction(s["unknown_rewards"],n))
    return stats

def run_policy_audit(data):
    total=policy_bounds(data,range(31))
    held=policy_bounds(data,TEST)
    unknown=any(v["unknown_rewards"]>0 for k,v in total.items() if k!="behavior")
    need(total["behavior"]["unknown_rewards"]==0,"BEHAVIOR_NOT_IDENTIFIED")
    return {"experiment":"NKR-22",
            "classification":"POLICY_VALUE_UNIDENTIFIED" if unknown else "ALL_TESTED_ACTIONS_SUPPORTED",
            "bounded_quantity":"One-step binary reward switching at recorded public histories; NOT total reward after a different policy changes future states.",
            "full_sequential_policy_return_identified":False,
            "all_consumed_rows":total,"later_held_rows":held,
            "recorded_policy_propensity":1,"unchosen_action_propensity":0,
            "new_source_actions":0,"counterfactual_rewards_read":0,
            "scientific_pass":False}

def stable(doc):
    out=json.loads(json.dumps(doc))
    for k in ("environment","source_candidate_sha","wall_seconds"):
        out.pop(k,None)
    return out

def campaign(data):
    started=time.monotonic()
    reports=[]
    # Frozen stages execute consecutively even if an earlier hypothesis fails.
    a,models,controls=run_history(data); reports.append(a)
    reports.append(run_backoff(data,models,controls))
    reports.append(run_policy_audit(data))
    out={"schema":"yggdrasil.nkr20-22.campaign.result.v1",
         "experiments":reports,"scientific_pass":False,"accepted_native":False,
         "new_original_source_actions":0,"original_public_rows":124,
         "source_transition_sha256":list(source19.PINS),
         "source_candidate_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
         "environment":{"python":sys.version,"platform":platform.platform()},
         "wall_seconds":time.monotonic()-started}
    need(out["wall_seconds"]<=120,"CAMPAIGN_WALL_BUDGET")
    out["stable_sha256"]=sha(canon(stable(out)))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true")
    args=p.parse_args()
    result=campaign(read_fixture(args.fixture))
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR20_EXPECTED_RESULT"])),
             "WINDOWS_CAMPAIGN_REPLICATION")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR20_22_FROZEN_CAMPAIGN="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
