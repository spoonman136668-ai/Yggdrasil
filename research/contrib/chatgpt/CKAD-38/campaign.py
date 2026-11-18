"""CKAD38: existing native episodic learner on real sequential synthetic consequences.

The source generator is evaluator-only. Every prediction below precedes the
revealed consequence. No regime IDs, future outcomes, inferred do records,
oracle transitions or model-class labels are passed to either learned arm.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import time
from collections import deque
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
SCHEMA="yggdrasil.ckad38.native-unannounced-rule-shifts.v1"
PREREG="e06f9ec931f7454b45e05ecd23299c3695e2a40f"
PILOT=(14181,14182)
PRIMARY=(24181,24182,24183)
DEV=(88511,88512)
WORLDS=(0,1)
ARMS=("native_recall","native_stream","native_no_repair","native_global",
      "beta_full","beta_window12","beta_window24","beta_window48",
      "beta_discount85","beta_discount95","beta_hedge","sham")
CONVENTIONAL=("beta_full","beta_window12","beta_window24","beta_window48",
              "beta_discount85","beta_discount95")
HEDGE_ETA=4.0
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
DISCOUNT=0.95


def seedint(*parts):
    return int.from_bytes(hashlib.sha256(canonical(["ckad38-source-v1",*parts])).digest()[:8],"big")


def boundaries(seed,world):
    rng=random.Random(seedint("private-regime-boundaries",seed,world))
    first=96+rng.randrange(-8,9)
    second=first+72+rng.randrange(-8,9)
    return first,second,second+64


def generator(seed,world):
    """Private simulator: only revealed public event tuples reach training."""
    a,b,end=boundaries(seed,world)
    actions=random.Random(seedint("public-input-policy",seed,world))
    noise=random.Random(seedint("hidden-bernoulli-world",seed,world))
    events=[]
    for t in range(end):
        regime="B" if a<=t<b else "A"
        ctx=actions.randrange(2)
        x1=actions.randrange(2)
        x2=actions.randrange(2)
        v1=actions.randrange(2)
        v2=actions.randrange(2)
        views=((ctx,v1),(ctx,v2))
        # Private novel structural family (never passed to any model).
        variant=(seed+world)&1
        if variant==0:
            trans_bit=(ctx^x1)^int(regime=="B")
        else:
            trans_bit=(ctx&x1 if regime=="A" else (ctx ^ (x1 & (1-ctx))))
        s2=int(noise.random() < (.85 if trans_bit else .15))
        if variant==0:
            terminal_bit=((ctx&x1)^(s2&x2) if regime=="A"
                          else (ctx&s2)|(x1&x2))
        else:
            terminal_bit=((ctx^(s2&x2)) if regime=="A"
                          else ((ctx&s2)^(x1|x2)))
        y=int(noise.random() < (.9 if terminal_bit else .1))
        row={"s1":ctx,"x1":x1,"s2":s2,"x2":x2,"y":y}
        identifier=hashlib.sha256(f"ckad38|{seed}|{world}|{t}".encode("ascii")).hexdigest()
        phase=("stable_A" if 48<=t<a else "early_B" if a<=t<a+24
               else "late_B" if a+24<=t<b else "early_return_A"
               if b<=t<b+24 else "late_return_A" if b+24<=t else "warm")
        events.append((identifier,views,row,phase))
    return events,{"world":world,"boundary_A_to_B":a,"boundary_B_to_A":b,
                   "total_episodes":end}


def _cell(rows,mode,ctx,first,second=None,second_action=None):
    if mode=="transition":
        outcomes=[r["s2"] for r in rows if r["s1"]==ctx and r["x1"]==first]
    else:
        outcomes=[r["y"] for r in rows if r["s1"]==ctx and r["x1"]==first and
                  r["s2"]==second and r["x2"]==second_action]
    return (1+sum(outcomes))/(2+len(outcomes))


class Conventional:
    """Matched fully trained source-only Beta and adaptive Hedge controls."""
    def __init__(self):
        self.rows=[]
        self.discount={.85:({"transition":{},"terminal":{}}),
                       .95:({"transition":{},"terminal":{}})}
        self.hedge={k:1.0 for k in CONVENTIONAL}

    def p(self,arm,mode,ctx,first,second=None,second_action=None):
        if arm=="sham":return .5
        if arm=="beta_hedge":
            total=sum(self.hedge.values())
            return sum(self.hedge[k]*self.p(k,mode,ctx,first,second,second_action)
                       for k in CONVENTIONAL)/total
        if arm=="beta_full":
            return _cell(self.rows,mode,ctx,first,second,second_action)
        if arm in ("beta_window12","beta_window24","beta_window48"):
            window={"beta_window12":12,"beta_window24":24,"beta_window48":48}[arm]
            return _cell(self.rows[-window:],mode,ctx,first,second,second_action)
        if arm not in ("beta_discount85","beta_discount95"):
            raise ValueError("CKAD38_CONVENTIONAL_ARM")
        rate=.85 if arm=="beta_discount85" else .95
        bank=self.discount[rate][mode]
        key=(ctx,first) if mode=="transition" else (ctx,first,second,second_action)
        zero,one=bank.get(key,(0.,0.))
        return (one+1)/(zero+one+2)

    def observe(self,row,losses):
        # Exponential Hedge uses only forecasts from PREVIOUSLY witnessed
        # outcomes; the new consequence is incorporated after forecasting.
        for k in CONVENTIONAL:
            self.hedge[k]*=math.exp(-HEDGE_ETA*losses[k])
        scale=max(self.hedge.values())
        for k in CONVENTIONAL:self.hedge[k]/=scale
        for rate,banks in self.discount.items():
            for bank in banks.values():
                for key,(n0,n1) in list(bank.items()):
                    bank[key]=(rate*n0,rate*n1)
            for key,bank,outcome in (
                ((row["s1"],row["x1"]),banks["transition"],row["s2"]),
                ((row["s1"],row["x1"],row["s2"],row["x2"]),
                 banks["terminal"],row["y"])):
                zero,one=bank.get(key,(0.,0.))
                bank[key]=(zero+int(outcome==0),one+int(outcome==1))
        self.rows.append(row)



def cold(model):
    raw=model.checkpoint()
    restored=NativeEpisodeExperience.restore(raw,digest(raw))
    if restored.checkpoint()!=raw:
        raise AssertionError("CKAD38_NATIVE_COLD_DRIFT")
    return restored,{"bytes":len(raw),"sha256":digest(raw)}


def native_probs(model,view,first,next_state,second,*,stream,recall=False):
    method=(model.context_forecast_recall if recall
            else model.context_forecast if stream else model.forecast)
    return float(method(view,first)),float(method(view,first,next_state,second))


def _dev_or_pilot(seed):
    started,cpu=time.perf_counter(),time.process_time()
    all_rows=[]
    world_info=[]
    for world in WORLDS:
        events,private_boundaries=generator(seed,world)
        native=NativeEpisodeExperience(repair=True)
        no_repair=NativeEpisodeExperience(repair=False)
        global_native=NativeEpisodeExperience(repair=True)
        baseline=Conventional()
        witnessed=set()
        old_ranges=None
        checkpoints={}
        detections=[]
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==48:
                native=native.begin_stream()
                no_repair=no_repair.begin_stream()
                # The first complete archival block is immutable even if a
                # later context detector re-partitions the partial 32:48 block.
                first48_pin=digest(canonical(native._ledger[:48]))
                old_ranges=tuple(
                    (item["start"],item["stop"],item["sha256"])
                    for item in native.info()["context"]["source_ranges"]
                    if item["stop"]<=32)
                native,checkpoints["start"]=cold(native)
                global_native,_=cold(global_native)
                no_repair,_=cold(no_repair)
            predictions={}
            for arm in ARMS:
                if arm in ("native_stream","native_recall"):
                    p,q=native_probs(native,views[0],row["x1"],row["s2"],row["x2"],
                                     stream=t>=48,recall=(arm=="native_recall" and t>=48))
                elif arm=="native_no_repair":
                    p,q=native_probs(no_repair,views[0],row["x1"],row["s2"],row["x2"],
                                     stream=t>=48)
                elif arm=="native_global":
                    p,q=native_probs(global_native,views[0],row["x1"],row["s2"],row["x2"],
                                     stream=False)
                else:
                    p=baseline.p(arm,"transition",row["s1"],row["x1"])
                    q=baseline.p(arm,"terminal",row["s1"],row["x1"],row["s2"],row["x2"])
                if not 0<=p<=1 or not 0<=q<=1:raise AssertionError("CKAD38_PROB_RANGE")
                predictions[arm]=[p,q]
            # Score all forecasts BEFORE exposing the authentic public
            # transition and terminal consequences to either native learner.
            losses={a:((p-row["s2"])**2+(q-row["y"])**2)/2
                    for a,(p,q) in predictions.items()}
            all_rows.append({
                "world":world,"index":t,"phase":phase,"source_id":identifier,
                "public_views":[list(v) for v in views],"public_row":row,
                "forecasts":predictions,"prequential_brier":losses})
            native=native.observe(identifier,views,row)
            no_repair=no_repair.observe(identifier,views,row)
            global_native=global_native.observe(identifier,views,row)
            baseline.observe(row,losses)
            if identifier in witnessed:raise AssertionError("CKAD38_DUP_SOURCE_ID")
            witnessed.add(identifier)
            if t in (48,96,160,len(events)-1):
                native,checkpoints[f"at_{t}"]=cold(native)
                global_native,_=cold(global_native)
                no_repair,_=cold(no_repair)
            if t>=48:
                ranges=tuple((i["start"],i["stop"],i["sha256"]) for i in
                             native.info()["context"]["source_ranges"])
                if digest(canonical(native._ledger[:48]))!=first48_pin:
                    raise AssertionError("CKAD38_PRIOR_SOURCE_PREFIX_CHANGED")
                for old in old_ranges:
                    if old not in ranges:
                        raise AssertionError("CKAD38_OLD_SOURCE_BLOCK_LOST")
        before=native.checkpoint()
        identifier,views,row,phase=events[-1]
        if native.observe(identifier,views,row) is not native:
            raise AssertionError("CKAD38_DUPLICATE_NOT_IDEMPOTENT")
        corrupted=dict(row);corrupted["y"]^=1
        try:native.observe(identifier,views,corrupted)
        except ValueError:pass
        else:raise AssertionError("CKAD38_CONFLICTING_IDENTIFIER_ACCEPTED")
        if native.checkpoint()!=before:
            raise AssertionError("CKAD38_CONTRADICTION_MUTATED_MEMORY")
        # Experimental recall is a read-only projection of retained native
        # hypotheses; source/counters/checkpoint must not change on read.
        before_read=native.checkpoint()
        _=native.context_forecast_recall(views[0],row["x1"])
        _=native.context_forecast_recall(views[0],row["x1"],row["s2"],row["x2"])
        if native.checkpoint()!=before_read:
            raise AssertionError("CKAD38_RECALL_READ_MUTATED_WEIGHTS")
        consolidated=native.consolidate()
        if consolidated.checkpoint()!=before:
            raise AssertionError("CKAD38_CONSOLIDATION_DIFFERS")
        native,checkpoints["final"]=cold(native)
        info=native.info()
        detections=info.get("stream",{}).get("detections",[])
        if len(native._ledger)!=len(events) or set(native._ids)!=witnessed:
            raise AssertionError("CKAD38_ORDERED_SOURCE_PERSISTENCE")
        world_info.append({
            "world":world,"episodes":len(events),
            "eval_boundaries_private":private_boundaries,
            "checkpoint_records":checkpoints,
            "old_source_ranges":[list(i) for i in old_ranges],
            "old_source_preserved":True,"original_first48_sha256":first48_pin,
            "source_count":len(witnessed),
            "duplicate_idempotent":True,"conflict_atomic":True,
            "recall_pure_read":True,
            "consolidated_exact":True,"cold_exact":True,
            "detected_events":detections,
            "final_state_sha256":digest(before)
        })
    metrics={}
    for phase in PHASES:
        observed=[r for r in all_rows if r["phase"]==phase]
        if not observed:raise AssertionError("CKAD38_EMPTY_EVAL_PHASE")
        metrics[phase]={a:{"brier":round(sum(r["prequential_brier"][a]
                                         for r in observed)/len(observed),10),
                           "episodes":len(observed)}
                        for a in ARMS}
    pooled=[r for r in all_rows if r["phase"] in ("late_B","late_return_A")]
    metrics["pooled_late_shift_and_return"]={
        a:{"brier":round(sum(r["prequential_brier"][a] for r in pooled)/len(pooled),10),
           "episodes":len(pooled)} for a in ARMS}
    return {
        "seed":seed,"world_count":len(WORLDS),
        "total_authentic_episodes":len(all_rows),
        "total_authentic_consequences":2*len(all_rows),
        "worlds":world_info,"original_episode_receipts":all_rows,
        "metric_groups":metrics,
        "wall_seconds":round(time.perf_counter()-started,6),
        "cpu_seconds":round(time.process_time()-cpu,6),
        "primary_scored":False
    }


def score(seed):
    if seed not in PILOT:raise ValueError("CKAD38_ONLY_REGISTERED_PILOT")
    return _dev_or_pilot(seed)


def classify(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD38_SEED_BOUNDARY")
    good=[]
    for c in cases:
        m=c["metric_groups"]
        pooled=m["pooled_late_shift_and_return"]
        candidate=pooled["native_recall"]["brier"]
        conventional=min(pooled[k]["brier"] for k in CONVENTIONAL+("beta_hedge",))
        old=pooled["native_stream"]["brier"]
        go=(candidate<=.145
            and candidate<=conventional-.025
            and candidate<=old-.025
            and m["early_B"]["native_recall"]["brier"]<=
                m["early_B"]["native_stream"]["brier"]
            and m["late_return_A"]["native_recall"]["brier"]<=
                m["late_return_A"]["native_stream"]["brier"]
            and all(all(w[k] is True for k in (
                "old_source_preserved","duplicate_idempotent","conflict_atomic",
                "consolidated_exact","cold_exact","recall_pure_read"))
                for w in c["worlds"]))
        good.append(go)
    qualified=all(good)
    return {"decision":"ENGINEERING_FEASIBLE" if qualified else "SCREEN_NO_GO",
            "engineering_feasible":qualified,"scientific_pass":False,
            "conventional_superiority_pilot":qualified,"primary_scored":False}



def frozen_lock():
    d=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if d["campaign_blob_sha1"]!=git_blob or d["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD38_SOURCE_LOCK_DRIFT")
    return d


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","pilot"),required=True)
    parser.add_argument("--seed",type=int)
    args=parser.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD38_PREFLIGHT_NEVER_SCORES_SEEDS")
        assert len(ARMS)==7 and len(PHASES)==5
        if (HERE/"source_lock.json").exists():frozen_lock()
        print(json.dumps({"schema":SCHEMA,"status":"PREFLIGHT_OK",
                          "first_use":False,"reserved_primary":list(PRIMARY)},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD38_UNREGISTERED_FIRST_USE")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,
                          "source_lock":frozen_lock(),"primary_scored":False,
                          "case":score(args.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()
