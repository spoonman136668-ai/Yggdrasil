"""CKAD46: actual online grounding of unseen intervention symbols.

Private balanced action semantics exist only in World / evaluator. The native
binary learner is not modified. An isolated adapter maps witnessed new action
symbols to learned binary causal primitives, preserving a raw-source ledger.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
EXACT=HERE.parent/"CKAD-42"/"campaign.py"
spec=importlib.util.spec_from_file_location("ckad46_exact_source",EXACT)
E=importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
C=E.C

SCHEMA="yggdrasil.ckad46.unseen-intervention-grounding.dev.v1"
PREREG="1fcd7e165e87561cc4f47ef7a0f71ebc3e1873ba"
DEV=(46111,46112)
PILOT=(46211,46212)
PRIMARY=(46311,46312,46313)
EXCLUDED=(45111,45112,44111,44112,43111,43112,42111,42112,41101,41102)
SOURCE=96
TRANSFER_END=240
TOTAL=288
WARM=48
TOKENS=(10,11,12,13)
STAGES=("unseen_early","unseen_late","cold_return")
ARMS=("native_likelihood_grounding","exact_balanced_mapping",
      "independent_raw_beta","native_hash","frozen_uniform","oracle_known_mapping")
BALANCED=tuple(p for p in itertools.product((0,1),repeat=4) if sum(p)==2)
HYPOTHESES=tuple(itertools.product(BALANCED,repeat=2))
assert len(BALANCED)==6 and len(HYPOTHESES)==36


def _phase(t):
    if t<SOURCE:return "known_anchor"
    if t<SOURCE+32:return "unseen_early"
    if t<TRANSFER_END:return "unseen_late"
    return "cold_return"


def _actual_prob(world,c,a,s,b):
    if world==0:
        tx=c^a
        ty=(c&a)^(s&b)
    elif world==1:
        tx=c&(1-a)
        ty=c^(s|b)
    else:
        raise ValueError("CKAD46_PRIVATE_WORLD")
    return (.85 if tx else .15),(.90 if ty else .10)


def private_world(seed,world):
    if seed not in DEV and seed!=999:raise ValueError("CKAD46_ONLY_REGISTERED_DEV_WORLD")
    rng=random.Random(C.seedint("ckad46-new-token-source",seed,world))
    m1=list((0,0,1,1))
    m2=list((0,0,1,1))
    rng.shuffle(m1);rng.shuffle(m2)
    events=[]
    for t in range(TOTAL):
        ctx,v1,v2=(rng.randrange(2) for _ in range(3))
        x1=rng.choice((0,1) if t<SOURCE or t>=TRANSFER_END else TOKENS)
        x2=rng.choice((0,1) if t<SOURCE or t>=TRANSFER_END else TOKENS)
        true_a=x1 if x1 in (0,1) else m1[TOKENS.index(x1)]
        true_b=x2 if x2 in (0,1) else m2[TOKENS.index(x2)]
        noise1=rng.random()
        noise2=rng.random()
        pt,_=_actual_prob(world,ctx,true_a,0,0)
        s=int(noise1<pt)
        _,py=_actual_prob(world,ctx,true_a,s,true_b)
        y=int(noise2<py)
        identifier=hashlib.sha256(f"ckad46|{seed}|{world}|{t}".encode()).hexdigest()
        views=((ctx,v1),(ctx,v2))
        raw={"s1":ctx,"x1":x1,"s2":s,"x2":x2,"y":y}
        events.append((identifier,views,raw,_phase(t)))
    return events,{"stage1":m1,"stage2":m2,"world":world}


def _prob_of_observation(p,observed):
    return p if observed else 1-p


def _binary_mix(x,y,weight_one):
    return x*(1-weight_one)+y*weight_one


def _sigmoid(logodds):
    z=max(-64.0,min(64.0,logodds))
    return 1/(1+E._portable_exp(-z))


def _source_grid(model,view,s):
    p=[model.read("short",view,a) for a in (0,1)]
    q=[[model.read("short",view,a,s,b) for b in (0,1)] for a in (0,1)]
    return p,q


class GroundingBase:
    def __init__(self,mode):
        if mode not in ("native_likelihood_grounding","exact_balanced_mapping","native_hash"):
            raise ValueError("CKAD46_INVALID_BINDER")
        self.mode=mode
        self.native=NativeEpisodeExperience(repair=True)
        self.causal=E.NativeInterventionRelations()
        self.frozen=None
        self.raw_receipts={}
        self.n=0
        self.first48_sha=None
        self.frozen_sha=None
        self.logodds=[{},{}]
        self.weights=[1/36]*36
        self.novel_stage_counts=[[0]*4,[0]*4]

    def _prior_bit(self,token,stage):
        if token in (0,1):return float(token)
        if token not in TOKENS:raise ValueError("CKAD46_UNKNOWN_ACTION_TOKEN")
        if self.mode=="native_hash":return float(token&1)
        if self.mode=="native_likelihood_grounding":
            return _sigmoid(self.logodds[stage].get(token,0.0))
        return sum(w*h[stage][TOKENS.index(token)] for w,h
                   in zip(self.weights,HYPOTHESES))

    def _map_for_source(self,token,stage):
        if token in (0,1):return token
        return int(self._prior_bit(token,stage)>.5)

    def forecast(self,view,x1,s2=None,x2=None):
        if self.mode=="native_hash":
            a=self._map_for_source(x1,0)
            if s2 is None:return self.causal.read("short",view,a)
            return self.causal.read("short",view,a,s2,self._map_for_source(x2,1))
        if s2 is None:
            p0=self.causal.read("short",view,0)
            p1=self.causal.read("short",view,1)
            if self.mode=="exact_balanced_mapping" and x1 in TOKENS:
                return sum(w*([p0,p1][h[0][TOKENS.index(x1)]]) for w,h
                           in zip(self.weights,HYPOTHESES))
            return _binary_mix(p0,p1,self._prior_bit(x1,0))
        if type(s2) is not int or s2 not in (0,1):
            raise ValueError("CKAD46_UNOBSERVED_TRANSITION")
        grid1,grid2=_source_grid(self.causal,view,s2)
        if self.mode=="exact_balanced_mapping" and (x1 in TOKENS or x2 in TOKENS):
            v=[]
            for w,h in zip(self.weights,HYPOTHESES):
                a=x1 if x1 in (0,1) else h[0][TOKENS.index(x1)]
                b=x2 if x2 in (0,1) else h[1][TOKENS.index(x2)]
                v.append(w*_prob_of_observation(grid1[a],s2))
            den=sum(v)
            return sum(vv*grid2[(x1 if x1 in (0,1) else h[0][TOKENS.index(x1)])]
                                [(x2 if x2 in (0,1) else h[1][TOKENS.index(x2)])]
                       for vv,h in zip(v,HYPOTHESES))/den
        pa=self._prior_bit(x1,0)
        pb=self._prior_bit(x2,1)
        v0=(1-pa)*_prob_of_observation(grid1[0],s2)
        v1=pa*_prob_of_observation(grid1[1],s2)
        post=v1/(v0+v1)
        return _binary_mix(_binary_mix(grid2[0][0],grid2[0][1],pb),
                           _binary_mix(grid2[1][0],grid2[1][1],pb),post)

    def _update_mapping_from_observed(self,view,row):
        if self.frozen is None:return
        x1,x2,s,y=(row[k] for k in ("x1","x2","s2","y"))
        if x1 in (0,1) and x2 in (0,1):return
        pt,qt=_source_grid(self.frozen,view,s)
        if self.mode=="native_hash":return
        if self.mode=="native_likelihood_grounding":
            if x1 in TOKENS:
                ratio=_prob_of_observation(pt[1],s)/_prob_of_observation(pt[0],s)
                self.logodds[0][x1]=self.logodds[0].get(x1,0.0)+math.log(ratio)
                self.novel_stage_counts[0][TOKENS.index(x1)]+=1
            if x2 in TOKENS:
                pa=self._prior_bit(x1,0)
                a0=(1-pa)*_prob_of_observation(pt[0],s)
                a1=pa*_prob_of_observation(pt[1],s)
                d=a0+a1
                like0=(a0*_prob_of_observation(qt[0][0],y)+
                       a1*_prob_of_observation(qt[1][0],y))/d
                like1=(a0*_prob_of_observation(qt[0][1],y)+
                       a1*_prob_of_observation(qt[1][1],y))/d
                self.logodds[1][x2]=self.logodds[1].get(x2,0.0)+math.log(like1/like0)
                self.novel_stage_counts[1][TOKENS.index(x2)]+=1
            return
        likelihood=[]
        for w,h in zip(self.weights,HYPOTHESES):
            a=x1 if x1 in (0,1) else h[0][TOKENS.index(x1)]
            b=x2 if x2 in (0,1) else h[1][TOKENS.index(x2)]
            likelihood.append(w*_prob_of_observation(pt[a],s)*
                             _prob_of_observation(qt[a][b],y))
        normalizer=sum(likelihood)
        if normalizer<=0:raise AssertionError("CKAD46_ZERO_EXACT_POSTERIOR")
        self.weights=[v/normalizer for v in likelihood]
        if x1 in TOKENS:self.novel_stage_counts[0][TOKENS.index(x1)]+=1
        if x2 in TOKENS:self.novel_stage_counts[1][TOKENS.index(x2)]+=1

    def observe(self,identifier,views,row):
        if not isinstance(identifier,str) or len(identifier)!=64:
            raise ValueError("CKAD46_SOURCE_ID")
        if type(row) is not dict or set(row)!={"s1","x1","s2","x2","y"}:
            raise ValueError("CKAD46_RAW_ROW")
        raw_receipt=canonical([views,row]).decode()
        if identifier in self.raw_receipts:
            if self.raw_receipts[identifier]!=raw_receipt:
                raise ValueError("CKAD46_CONFLICTING_RAW_SOURCE_ID")
            return self
        if self.n>=TOTAL:raise ValueError("CKAD46_SOURCE_CAP")
        a=self._map_for_source(row["x1"],0)
        b=self._map_for_source(row["x2"],1)
        projected=dict(row,x1=a,x2=b)
        self._update_mapping_from_observed(views[0],row)
        # Both original native and exact native causal state learn ONE genuinely
        # observed consequence, with pre-outcome inferred action class ONLY.
        self.native=self.native.observe(identifier,views,projected)
        self.causal.observe(identifier,views,projected)
        self.raw_receipts[identifier]=raw_receipt
        self.n+=1
        if self.n==SOURCE:
            raw=self.causal.checkpoint()
            self.frozen=E.NativeInterventionRelations.restore(raw,digest(raw))
            self.frozen_sha=digest(raw)
        if self.n!=len(self.native._ledger) or self.n!=self.causal.n:
            raise AssertionError("CKAD46_SOURCE_COUNT")
        return self

    def begin_stream(self):
        if self.n!=WARM:raise AssertionError("CKAD46_WARM_WRONG_BOUNDARY")
        self.native=self.native.begin_stream()
        self.first48_sha=digest(canonical(self.native._ledger[:WARM]))

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"mode":self.mode,"n":self.n,
                 "native":json.loads(self.native.checkpoint()),
                 "causal":json.loads(self.causal.checkpoint()),
                 "frozen":None if self.frozen is None else json.loads(self.frozen.checkpoint()),
                 "raw_receipts":self.raw_receipts,
                 "logodds":self.logodds,
                 "weights":self.weights,
                 "counts":self.novel_stage_counts,
                 "first48_sha":self.first48_sha,"frozen_sha":self.frozen_sha})

    @classmethod
    def restore(cls,raw,sha):
        if digest(raw)!=sha:raise ValueError("CKAD46_COLD_DIGEST")
        d=json.loads(raw)
        if d["schema"]!=SCHEMA:raise ValueError("CKAD46_COLD_SCHEMA")
        obj=cls(d["mode"])
        n=canonical(d["native"])
        obj.native=NativeEpisodeExperience.restore(n,digest(n))
        c=canonical(d["causal"])
        obj.causal=E.NativeInterventionRelations.restore(c,digest(c))
        if d["frozen"] is not None:
            f=canonical(d["frozen"])
            obj.frozen=E.NativeInterventionRelations.restore(f,digest(f))
        obj.n=d["n"];obj.raw_receipts=d["raw_receipts"]
        obj.logodds=[{int(k):v for k,v in bank.items()} for bank in d["logodds"]]
        obj.weights=d["weights"]
        obj.novel_stage_counts=d["counts"]
        obj.first48_sha=d["first48_sha"]
        obj.frozen_sha=d["frozen_sha"]
        if obj.n!=len(obj.raw_receipts) or obj.n!=obj.causal.n:
            raise ValueError("CKAD46_COLD_SOURCE_COUNT")
        if obj.checkpoint()!=raw:raise ValueError("CKAD46_COLD_BYTES")
        return obj


class RawSymbolBeta:
    def __init__(self):
        self.t={};self.y={};self.n=0
    @staticmethod
    def _rate(bank,key):
        fail,succ=bank.get(key,(0,0))
        return (succ+1)/(2+fail+succ)
    def forecast(self,view,x1,s2=None,x2=None):
        if s2 is None:return self._rate(self.t,(view[0],x1))
        return self._rate(self.y,(view[0],x1,s2,x2))
    def observe(self,row):
        for bank,key,outcome in (
           (self.t,(row["s1"],row["x1"]),row["s2"]),
           (self.y,(row["s1"],row["x1"],row["s2"],row["x2"]),row["y"])):
            fail,succ=bank.get(key,(0,0))
            bank[key]=(fail+int(outcome==0),succ+int(outcome==1))
        self.n+=1


def _loss(p,q,row):
    u=p-row["s2"]
    v=q-row["y"]
    return (u*u+v*v)*.5


def run(seed):
    if seed not in DEV:raise ValueError("CKAD46_ONLY_REGISTERED_DEV")
    start=time.perf_counter();start_cpu=time.process_time()
    all_rows=[];worlds=[]
    for world in (0,1):
        events,hidden=private_world(seed,world)
        agents={arm:GroundingBase(arm) for arm in
                ("native_likelihood_grounding","exact_balanced_mapping","native_hash")}
        beta=RawSymbolBeta()
        rawids=set()
        last=None
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==WARM:
                for agent in agents.values():agent.begin_stream()
            view=views[0]
            preds={}
            for arm,agent in agents.items():
                p=agent.forecast(view,row["x1"])
                q=agent.forecast(view,row["x1"],row["s2"],row["x2"])
                preds[arm]=(p,q)
            preds["independent_raw_beta"]=(beta.forecast(view,row["x1"]),
                                          beta.forecast(view,row["x1"],row["s2"],row["x2"]))
            if t<SOURCE:
                preds["frozen_uniform"]=preds["native_likelihood_grounding"]
                preds["oracle_known_mapping"]=preds["native_likelihood_grounding"]
            else:
                prototype=agents["native_likelihood_grounding"].frozen
                a=row["x1"] if row["x1"] in (0,1) else hidden["stage1"][TOKENS.index(row["x1"])]
                b=row["x2"] if row["x2"] in (0,1) else hidden["stage2"][TOKENS.index(row["x2"])]
                if row["x1"] in TOKENS:
                    p=(prototype.read("short",view,0)+prototype.read("short",view,1))*.5
                else:p=prototype.read("short",view,a)
                if row["x1"] in TOKENS or row["x2"] in TOKENS:
                    q=sum(prototype.read("short",view,aa,row["s2"],bb)
                          for aa in ((0,1) if row["x1"] in TOKENS else (a,))
                          for bb in ((0,1) if row["x2"] in TOKENS else (b,)))/(
                              (2 if row["x1"] in TOKENS else 1)*
                              (2 if row["x2"] in TOKENS else 1))
                else:q=prototype.read("short",view,a,row["s2"],b)
                preds["frozen_uniform"]=(p,q)
                preds["oracle_known_mapping"]=(
                    prototype.read("short",view,a),
                    prototype.read("short",view,a,row["s2"],b))
            losses={arm:_loss(*pr,row) for arm,pr in preds.items()}
            if phase in STAGES:
                all_rows.append({"world":world,"t":t,"phase":phase,
                                 "losses":losses})
            # The source outcome was actually witnessed. Labels in 'hidden'
            # are evaluator-only and never provided to agents.observe().
            for agent in agents.values():agent.observe(identifier,views,row)
            beta.observe(row)
            if identifier in rawids:raise AssertionError("CKAD46_DUPLICATED_PUBLIC_EPISODE")
            rawids.add(identifier)
            last=(identifier,views,row)
        for mode,model in agents.items():
            raw=model.checkpoint()
            if GroundingBase.restore(raw,digest(raw)).checkpoint()!=raw:
                raise AssertionError("CKAD46_COLD_EXACT")
            if model.frozen.checkpoint()!=canonical(json.loads(model.frozen.checkpoint())):
                raise AssertionError("CKAD46_FROZEN_NONCANONICAL")
            if (digest(model.frozen.checkpoint())!=model.frozen_sha or
                    digest(canonical(model.native._ledger[:WARM]))!=model.first48_sha):
                raise AssertionError("CKAD46_NATIVE_PRIOR_SOURCE_ERASED")
            if model.n!=TOTAL or len(model.raw_receipts)!=TOTAL:
                raise AssertionError("CKAD46_RAW_SOURCE_INCOMPLETE")
            before=model.checkpoint()
            if model.observe(*last) is not model or model.checkpoint()!=before:
                raise AssertionError("CKAD46_DUPLICATE_NOT_IDEMPOTENT")
            changed=dict(last[2]);changed["y"]^=1
            try:model.observe(last[0],last[1],changed)
            except ValueError:pass
            else:raise AssertionError("CKAD46_CONFLICTING_RAW_SOURCE_ACCEPTED")
            if model.checkpoint()!=before:
                raise AssertionError("CKAD46_CONFLICT_MUTATED_WEIGHTS")
            worlds.append({"world":world,"arm":mode,"source_episodes":model.n,
                "native_sha256":digest(model.native.checkpoint()),
                "causal_sha256":digest(model.causal.checkpoint()),
                "raw_receipt_sha256":digest(canonical(model.raw_receipts)),
                "full_checkpoint_sha256":digest(raw),
                "source_prefix48_preserved":True,"frozen_source96_exact":True,
                "cold_exact":True,"duplicate_idempotent":True,"conflict_atomic":True,
                "distinct_stage1_novel_symbols_witnessed":sum(v>0 for v in model.novel_stage_counts[0]),
                "distinct_stage2_novel_symbols_witnessed":sum(v>0 for v in model.novel_stage_counts[1]),
                "native_and_causal_witnesses":model.n,
                "frozen_checkpoint_bytes":len(model.frozen.checkpoint()),
                "complete_checkpoint_bytes":len(raw)})
    groups={}
    for phase in (*STAGES,"unseen_late_plus_return"):
        chosen=[r for r in all_rows if (r["phase"] in ("unseen_late","cold_return")
                    if phase=="unseen_late_plus_return" else r["phase"]==phase)]
        if not chosen:raise AssertionError("CKAD46_PHASE_EMPTY")
        groups[phase]={"episodes":len(chosen),
            "brier":{name:sum(r["losses"][name] for r in chosen)/len(chosen)
                for name in ARMS}}
    return {"seed":seed,"worlds":worlds,
            "source_events_actual":2*TOTAL,
            "authentic_outcomes":4*TOTAL,
            "groups":groups,
            "wall_seconds":round(time.perf_counter()-start,6),
            "cpu_seconds":round(time.process_time()-start_cpu,6)}


def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:
        raise AssertionError("CKAD46_DEV_COHORT_ORDER")
    for c in cases:
        for w in c["worlds"]:
            if not all(w[k] for k in
                ("source_prefix48_preserved","frozen_source96_exact",
                 "cold_exact","duplicate_idempotent","conflict_atomic")):
                return "SOURCE_INVALID"
            if w["arm"]!="native_hash" and (w["distinct_stage1_novel_symbols_witnessed"]!=4
                                             or w["distinct_stage2_novel_symbols_witnessed"]!=4):
                return "SOURCE_INVALID"
        g=c["groups"];pooled=g["unseen_late_plus_return"]["brier"]
        candidate=pooled["native_likelihood_grounding"]
        best=min(pooled[k] for k in ("exact_balanced_mapping",
                                     "independent_raw_beta","native_hash",
                                     "frozen_uniform"))
        if candidate>.150 or candidate>best-.015:
            return "DEV_NO_GO"
        early=g["unseen_early"]["brier"]
        if early["native_likelihood_grounding"]>min(early[k] for k in
             ("exact_balanced_mapping","independent_raw_beta","native_hash",
              "frozen_uniform"))+.015:
            return "DEV_NO_GO"
        ret=g["cold_return"]["brier"]
        if ret["native_likelihood_grounding"]>ret["native_hash"]+.005:
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("preflight","dev"))
    p.add_argument("--seed",type=int)
    x=p.parse_args()
    if x.mode=="preflight":
        if x.seed is not None:raise ValueError("CKAD46_PREFLIGHT_NO_SEED")
        print(json.dumps({"schema":SCHEMA,"prereg":PREREG,
            "dev":DEV,"pilot_reserved":PILOT,"primary_reserved":PRIMARY,
            "known_anchor_episodes":SOURCE,"unknown_symbol_tokens":TOKENS,
            "science_pass":False,"first_use":False},sort_keys=True))
        return
    if x.seed not in DEV:raise ValueError("CKAD46_ONLY_REGISTERED_DEV")
    print("CKAD46_CASE="+json.dumps(run(x.seed),sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
