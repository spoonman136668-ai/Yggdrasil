"""CKAD37: existing native episodic learner on real sequential synthetic consequences.

The source generator is evaluator-only. Every prediction below precedes the
revealed consequence. No regime IDs, future outcomes, inferred do records,
oracle transitions or model-class labels are passed to either learned arm.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import time
from collections import deque
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
SCHEMA="yggdrasil.ckad37.native-unannounced-rule-shifts.v1"
PREREG="d675309bec3134a91f2fab470d736d490a4e280c"
PILOT=(14071,14072)
PRIMARY=(24071,24072,24073)
DEV=(88411,88412)
WORLDS=(0,1)
ARMS=("native_stream","native_global","beta_full","beta_window24",
      "beta_window48","beta_discount95","sham")
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
DISCOUNT=0.95


def seedint(*parts):
    return int.from_bytes(hashlib.sha256(canonical(["ckad37-source-v1",*parts])).digest()[:8],"big")


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
        trans_bit=(ctx^x1)^int(regime=="B")
        s2=int(noise.random() < (.85 if trans_bit else .15))
        terminal_bit=((ctx&x1)^(s2&x2) if regime=="A"
                      else (ctx&s2)|(x1&x2))
        y=int(noise.random() < (.9 if terminal_bit else .1))
        row={"s1":ctx,"x1":x1,"s2":s2,"x2":x2,"y":y}
        identifier=hashlib.sha256(f"ckad37|{seed}|{world}|{t}".encode("ascii")).hexdigest()
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
    """Independent, fully source-fitted causal-cell Beta controls."""
    def __init__(self):
        self.rows=[]
        self.transition={}
        self.terminal={}

    def p(self,arm,mode,ctx,first,second=None,second_action=None):
        if arm=="beta_full":
            return _cell(self.rows,mode,ctx,first,second,second_action)
        if arm=="beta_window24":
            return _cell(self.rows[-24:],mode,ctx,first,second,second_action)
        if arm=="beta_window48":
            return _cell(self.rows[-48:],mode,ctx,first,second,second_action)
        if arm=="sham":return .5
        if arm!="beta_discount95":raise ValueError("CKAD37_CONVENTIONAL_ARM")
        key=(ctx,first) if mode=="transition" else (ctx,first,second,second_action)
        bank=self.transition if mode=="transition" else self.terminal
        zero,one=bank.get(key,(0.,0.))
        return (one+1)/(zero+one+2)

    def observe(self,row):
        # Discount all preexisting observed source evidence once per new episode;
        # inferred counterfactuals never alter these counts.
        for bank in (self.transition,self.terminal):
            for key,(n0,n1) in list(bank.items()):
                bank[key]=(n0*DISCOUNT,n1*DISCOUNT)
        for key,bank,outcome in (
            ((row["s1"],row["x1"]),self.transition,row["s2"]),
            ((row["s1"],row["x1"],row["s2"],row["x2"]),self.terminal,row["y"])):
            zeros,ones=bank.get(key,(0.,0.))
            bank[key]=(zeros+int(outcome==0),ones+int(outcome==1))
        self.rows.append(row)


def cold(model):
    raw=model.checkpoint()
    restored=NativeEpisodeExperience.restore(raw,digest(raw))
    if restored.checkpoint()!=raw:
        raise AssertionError("CKAD37_NATIVE_COLD_DRIFT")
    return restored,{"bytes":len(raw),"sha256":digest(raw)}


def native_probs(model,view,first,next_state,second,*,stream):
    p=model.context_forecast(view,first) if stream else model.forecast(view,first)
    q=(model.context_forecast(view,first,next_state,second) if stream
       else model.forecast(view,first,next_state,second))
    return float(p),float(q)


def _dev_or_pilot(seed):
    started,cpu=time.perf_counter(),time.process_time()
    all_rows=[]
    world_info=[]
    for world in WORLDS:
        events,private_boundaries=generator(seed,world)
        native=NativeEpisodeExperience(repair=True)
        global_native=NativeEpisodeExperience(repair=True)
        baseline=Conventional()
        witnessed=set()
        old_ranges=None
        checkpoints={}
        detections=[]
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==48:
                native=native.begin_stream()
                old_ranges=tuple(
                    (item["start"],item["stop"],item["sha256"])
                    for item in native.info()["context"]["source_ranges"]
                    if item["stop"]<=48)
                native,checkpoints["start"]=cold(native)
                global_native,_=cold(global_native)
            predictions={}
            for arm in ARMS:
                if arm=="native_stream":
                    p,q=native_probs(native,views[0],row["x1"],row["s2"],row["x2"],
                                     stream=t>=48)
                elif arm=="native_global":
                    p,q=native_probs(global_native,views[0],row["x1"],row["s2"],row["x2"],
                                     stream=False)
                else:
                    p=baseline.p(arm,"transition",row["s1"],row["x1"])
                    q=baseline.p(arm,"terminal",row["s1"],row["x1"],row["s2"],row["x2"])
                if not 0<=p<=1 or not 0<=q<=1:raise AssertionError("CKAD37_PROB_RANGE")
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
            global_native=global_native.observe(identifier,views,row)
            baseline.observe(row)
            if identifier in witnessed:raise AssertionError("CKAD37_DUP_SOURCE_ID")
            witnessed.add(identifier)
            if t in (48,96,160,len(events)-1):
                native,checkpoints[f"at_{t}"]=cold(native)
                global_native,_=cold(global_native)
            if t>=48:
                ranges=tuple((i["start"],i["stop"],i["sha256"]) for i in
                             native.info()["context"]["source_ranges"])
                for old in old_ranges:
                    if old not in ranges:
                        raise AssertionError("CKAD37_OLD_SOURCE_BLOCK_LOST")
        before=native.checkpoint()
        identifier,views,row,phase=events[-1]
        if native.observe(identifier,views,row) is not native:
            raise AssertionError("CKAD37_DUPLICATE_NOT_IDEMPOTENT")
        corrupted=dict(row);corrupted["y"]^=1
        try:native.observe(identifier,views,corrupted)
        except ValueError:pass
        else:raise AssertionError("CKAD37_CONFLICTING_IDENTIFIER_ACCEPTED")
        if native.checkpoint()!=before:
            raise AssertionError("CKAD37_CONTRADICTION_MUTATED_MEMORY")
        consolidated=native.consolidate()
        if consolidated.checkpoint()!=before:
            raise AssertionError("CKAD37_CONSOLIDATION_DIFFERS")
        native,checkpoints["final"]=cold(native)
        info=native.info()
        detections=info.get("stream",{}).get("detections",[])
        if len(native._ledger)!=len(events) or set(native._ids)!=witnessed:
            raise AssertionError("CKAD37_ORDERED_SOURCE_PERSISTENCE")
        world_info.append({
            "world":world,"episodes":len(events),
            "eval_boundaries_private":private_boundaries,
            "checkpoint_records":checkpoints,
            "old_source_ranges":[list(i) for i in old_ranges],
            "old_source_preserved":True,"source_count":len(witnessed),
            "duplicate_idempotent":True,"conflict_atomic":True,
            "consolidated_exact":True,"cold_exact":True,
            "detected_events":detections,
            "final_state_sha256":digest(before)
        })
    metrics={}
    for phase in PHASES:
        observed=[r for r in all_rows if r["phase"]==phase]
        if not observed:raise AssertionError("CKAD37_EMPTY_EVAL_PHASE")
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
    if seed not in PILOT:raise ValueError("CKAD37_ONLY_REGISTERED_PILOT")
    return _dev_or_pilot(seed)


def classify(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD37_SEED_BOUNDARY")
    eligible=[]
    for c in cases:
        m=c["metric_groups"]
        e=m["pooled_late_shift_and_return"]
        native=e["native_stream"]["brier"]
        conventional=min(e[k]["brier"] for k in
                         ("beta_full","beta_window24","beta_window48","beta_discount95"))
        old=e["native_global"]["brier"]
        go=(native<=.16 and native<=conventional-.025
            and native<=old-.025
            and m["early_B"]["native_stream"]["brier"]<=
                m["early_B"]["native_global"]["brier"]
            and m["late_return_A"]["native_stream"]["brier"]<=
                m["late_return_A"]["native_global"]["brier"]
            and all(all(w[k] is True for k in (
                      "old_source_preserved","duplicate_idempotent","conflict_atomic",
                      "consolidated_exact","cold_exact")) for w in c["worlds"]))
        eligible.append(go)
    go=all(eligible)
    return {"decision":"ENGINEERING_FEASIBLE" if go else "SCREEN_NO_GO",
            "engineering_feasible":go,"scientific_pass":False,
            "conventional_superiority_pilot":go,
            "primary_scored":False}


def frozen_lock():
    d=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if d["campaign_blob_sha1"]!=git_blob or d["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD37_SOURCE_LOCK_DRIFT")
    return d


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","pilot"),required=True)
    parser.add_argument("--seed",type=int)
    args=parser.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD37_PREFLIGHT_NEVER_SCORES_SEEDS")
        assert len(ARMS)==7 and len(PHASES)==5
        if (HERE/"source_lock.json").exists():frozen_lock()
        print(json.dumps({"schema":SCHEMA,"status":"PREFLIGHT_OK",
                          "first_use":False,"reserved_primary":list(PRIMARY)},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD37_UNREGISTERED_FIRST_USE")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,
                          "source_lock":frozen_lock(),"primary_scored":False,
                          "case":score(args.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()
