"""KNOW40 unfamiliar structural causal-graph intervention shadow evaluation.

Frozen prereg e8344c2c3d797fcd304c8c866ac1f1fe7e058e52 precedes
this implementation and all source first use. Model never receives laws,
seeds, graph identity, hidden phase, oracle q, or counterfactual outcomes.
No protected original-world use, native checkpoint changes, or deployment.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import os
import time
from pathlib import Path

from know33_local_metaplastic_dev import Beta, canonical, digest
from know36_noisy_retention_dev import Comparator, brier
from know38_buffer_before_write_dev import BufferBank
from know39_soft_deferred_dev import SoftDeferred, cold as soft_cold

PREREG = "e8344c2c3d797fcd304c8c866ac1f1fe7e058e52"
PROTO_BLOB = "366f96e13a566520d399a78d54e838bf62a551b6"
SCHEMA = "yggdrasil.know40.structural-intervention-shadow-result.dev.v1"
HAZARDS = (0.0078125, 0.03125, 0.125)
ARMS = ("candidate","hmm","symbolic","lookup","know38")
PHASES = ("B_first","A_return","B_second")

def need(v, code):
    if not v:
        raise ValueError("YGG_KNOW40_" + code)

def protocol():
    raw=Path(__file__).with_name("know40_structural_action_protocol.json").read_bytes()
    b=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    need(b==PROTO_BLOB,"PROTOCOL_BLOB")
    p=json.loads(raw)
    s=p["source"]
    need(p["schema"]=="yggdrasil.know40.unfamiliar-causal-intervention-shadow-prereg.v1"
         and s["fit_unique_source_calls"]==3072
         and s["held_unique_source_calls"]==9216
         and s["model_events_total_per_arm"]==10752
         and p["authority"]["protected_original_world_issue_426"]=="NOT_AUTHORIZED"
         and p["authority"]["native_training"] is False
         and p["scm"]["held_templates"]["H1"]=="x0 XOR (x1 AND x2)"
         and p["scm"]["held_templates"]["H2"]=="(x0 AND x1) XOR x2",
         "PROTOCOL")
    seeds=sum(s["fit"].values(),[])+sum(s["held"].values(),[])
    need(len(seeds)==36 and len(set(seeds))==36
         and all(len(s["fit"][f])==6 for f in ("F12","F21"))
         and all(len(s["held"][f])==12 for f in ("B1","B2")),
         "SEED_SPLIT")
    return p

def x_for(t,a=None):
    need(type(t) is int and 0<=t<256,"T")
    c=t%8
    if a is None:
        a=(t//8)%2
    need(type(a) is int and a in (0,1),"ACTION")
    return c^(a<<1)

def structural_bit(graph,x):
    need(graph in ("F1","F2","H1","H2")
         and type(x) is int and 0<=x<8,"LAW")
    b0,b1,b2=(x&1),(x>>1)&1,(x>>2)&1
    if graph=="F1": return b1
    if graph=="F2": return b0^b1^b2
    if graph=="H1": return b0^(b1&b2)
    return (b0&b1)^b2

def q_for(graph,x):
    return .85 if structural_bit(graph,x) else .15

class Lookup:
    def __init__(self):
        self.betas=[Beta() for _ in range(8)]
        self.received=0
    def prob(self,x):
        need(type(x) is int and 0<=x<8,"LOOKUP_X")
        return self.betas[x].prob()
    def observe(self,t,x,y):
        need(type(t) is int and t==self.received and t<256
             and type(x) is int and 0<=x<8
             and type(y) is int and y in (0,1),"LOOKUP_EVENT")
        self.betas[x].update(y,1.0)
        self.received+=1
    def checkpoint(self):
        return canonical({"kind":"lookup","received":self.received,
                          "betas":[z.state() for z in self.betas]})

class Symbolic:
    """Full 256-graph uniform Bayesian filter; no held graph identity supplied."""
    def __init__(self,hazard=0.03125):
        need(type(hazard) is float and hazard in HAZARDS,"SYMBOLIC_H")
        self.hazard=hazard
        self.weights=[1.0/256]*256
        self.received=0
    def prior(self):
        h=self.hazard
        return [(1-h)*w+h/256 for w in self.weights]
    def prob(self,x):
        need(type(x) is int and 0<=x<8,"SYMBOLIC_X")
        prior=self.prior()
        return .15+.70*sum(w for graph,w in enumerate(prior)
                            if (graph>>x)&1)
    def observe(self,t,x,y):
        need(type(t) is int and t==self.received and t<256
             and type(x) is int and 0<=x<8
             and type(y) is int and y in (0,1),"SYMBOLIC_EVENT")
        old=self.prior()
        unnorm=[w*(.85 if (((graph>>x)&1)==y) else .15)
                for graph,w in enumerate(old)]
        den=sum(unnorm)
        need(den>0 and math.isfinite(den),"SYMBOLIC_DENOM")
        self.weights=[z/den for z in unnorm]
        self.received+=1
    def checkpoint(self):
        return canonical({"kind":"full-256-truth-tables","hazard":self.hazard,
                          "received":self.received,"weights":self.weights})

def models(hmm_h,symbolic_h):
    return {
      "candidate":SoftDeferred("soft",float(hmm_h)),
      "hmm":Comparator("hmm",float(hmm_h)),
      "symbolic":Symbolic(float(symbolic_h)),
      "lookup":Lookup(),
      "know38":BufferBank("candidate"),
    }

def cold(m):
    if isinstance(m,(SoftDeferred,BufferBank)):
        return soft_cold(m)
    raw=m.checkpoint()
    out=copy.deepcopy(m)
    need(out.checkpoint()==raw and
         all(out.prob(x)==m.prob(x) for x in range(8)),
         "COLD_READBACK")
    return out

def private_y(seed,t,graph):
    need(os.environ.get("YGG_KNOW40_HELD_ONE_SHOT")=="1",
         "SOURCE_DENIED")
    need(type(seed) is int and type(t) is int and 0<=t<256
         and graph in ("F1","F2","H1","H2"),"SOURCE_ID")
    q=q_for(graph,x_for(t))
    data=f"know40:synthetic:structural:v1:{seed}:{t}:{graph}".encode()
    coin=hashlib.sha256(data).digest()
    return int(int.from_bytes(coin[:8],"big")/(1<<64)<q)

def random_choice(t):
    c=t%8
    z=hashlib.sha256(f"know40:random-action:v1:{t}:{c}".encode()).digest()
    return int.from_bytes(z[:8],"big")%2

def action_regret(model,t,graph):
    c=t%8
    p0=model.prob(x_for(t,0))
    p1=model.prob(x_for(t,1))
    chosen=int(p1>p0) # tie -> action 0
    q0,q1=q_for(graph,x_for(t,0)),q_for(graph,x_for(t,1))
    return max(q0,q1)-(q1 if chosen else q0)

def fit_hazards(p,witness=private_y):
    # Source called exactly 12*256 = 3072 times; each hazard sees SAME y.
    scores={kind:{h:[] for h in HAZARDS} for kind in ("hmm","symbolic")}
    count=0
    for family in ("F12","F21"):
        ga,gb=(("F1","F2") if family=="F12" else ("F2","F1"))
        for seed in p["source"]["fit"][family]:
            labels=[ga if t<64 or 128<=t<192 else gb for t in range(256)]
            observed=[witness(seed,t,labels[t]) for t in range(256)]
            count+=len(observed)
            for kind in ("hmm","symbolic"):
                for h in HAZARDS:
                    m=Comparator("hmm",h) if kind=="hmm" else Symbolic(h)
                    total=0
                    for t,y in enumerate(observed):
                        x=x_for(t)
                        if t>=64:
                            total+=brier(m.prob(x),q_for(labels[t],x))
                        m.observe(t,x,y)
                    scores[kind][h].append(total/192)
    need(count==3072,"FIT_COUNTS")
    selected={}
    report={}
    for kind in ("hmm","symbolic"):
        report[kind]={str(h):sum(scores[kind][h])/12 for h in HAZARDS}
        selected[kind]=min(HAZARDS,key=lambda h:(report[kind][str(h)],h))
    return selected,report,count

def held_world(seed,family,selected,witness=private_y):
    ga,gb=(("H1","H2") if family=="B1" else ("H2","H1"))
    # Exactly 256 A and 128 B source witnesses, common to all 5 arms.
    A=[witness(seed,t,ga) for t in range(256)]
    B={t:witness(seed,t,gb)
       for t in list(range(64,128))+list(range(192,256))}
    base=models(selected["hmm"],selected["symbolic"])
    for t in range(64):
        for m in base.values(): m.observe(t,x_for(t),A[t])
    base={k:cold(m) for k,m in base.items()}
    A_prefix=sum(brier(base["candidate"].prob(x),q_for(ga,x))
                 for x in range(8))/8
    A_bank=copy.deepcopy(base["candidate"].state()["banks"][0])
    reports={}
    for branch in ("treatment","sham"):
        ms={k:cold(m) for k,m in base.items()}
        score={phase:{name:{"brier":[],"regret":[]} for name in ARMS}
               for phase in PHASES}
        initial_admit=ms["candidate"].b_admissions
        A_retained=True
        B128=None;B192=None
        t_ns={name:0 for name in ARMS}
        for t in range(64,256):
            phase="B_first" if t<128 else ("A_return" if t<192 else "B_second")
            graph=gb if branch=="treatment" and phase!="A_return" else ga
            x=x_for(t)
            q=q_for(graph,x)
            y=B[t] if graph==gb else A[t]
            for name,m in ms.items():
                score[phase][name]["brier"].append(brier(m.prob(x),q))
                score[phase][name]["regret"].append(action_regret(m,t,graph))
                start=time.perf_counter_ns()
                m.observe(t,x,y)
                t_ns[name]+=time.perf_counter_ns()-start
            if t+1 in (128,192,256):
                ms={k:cold(m) for k,m in ms.items()}
                if branch=="treatment":
                    A_retained &= ms["candidate"].state()["banks"][0]==A_bank
                    if t+1==128:
                        B128=copy.deepcopy(ms["candidate"].state()["banks"][1])
                    if t+1==192:
                        B192=copy.deepcopy(ms["candidate"].state()["banks"][1])
        need(all(m.received==256 for m in ms.values()),"MODEL_COUNTS")
        reports[branch]={
          "scores":{phase:{name:{metric:sum(v)/64 for metric,v in metrics.items()}
                            for name,metrics in arms.items()}
                    for phase,arms in score.items()},
          "B_admissions":ms["candidate"].b_admissions-initial_admit,
          "bytes":{name:len(m.checkpoint()) for name,m in ms.items()},
          "time_ns":t_ns,
        }
    return {
      "family":family,"seed":seed,"prefix_brier":A_prefix,
      "scores":reports["treatment"]["scores"],
      "A_retained":A_retained,
      "B_retained":B128==B192,
      "sham_false_B_admission":reports["sham"]["B_admissions"]>0,
      "bytes":reports["treatment"]["bytes"],
      "time_ns":reports["treatment"]["time_ns"],
      "source_calls":384,"model_events_per_arm":448,
    }

def proof():
    need(os.environ.get("YGG_KNOW40_HELD_ONE_SHOT")=="1","FIRST_USE_DENIED")
    p=protocol()
    for b in range(0,256,16):
        pairs=[(t%8,(t//8)%2) for t in range(b,b+16)]
        need(len(set(pairs))==16,"TAPE_SUPPORT")
    for law in ("H1","H2"):
        contrasting=sum(q_for(law,c)!=q_for(law,c^2) for c in range(8))
        need(contrasting==4,"INTERVENTION_SUPPORT")
    selected,fit_scores,fit_calls=fit_hazards(p)
    worlds=[held_world(seed,family,selected) for family in ("B1","B2")
            for seed in p["source"]["held"][family]]
    need(len(worlds)==24 and sum(x["source_calls"] for x in worlds)==9216
         and all(x["model_events_per_arm"]==448 for x in worlds),"HELD_COUNTS")
    cohort={}
    for family in ("B1","B2"):
        rows=[x for x in worlds if x["family"]==family]
        means={stage:{name:{metric:sum(x["scores"][stage][name][metric]
                                        for x in rows)/12
                            for metric in ("brier","regret")}
                      for name in ARMS}
               for stage in PHASES}
        wins={metric:sum(
            x["scores"]["B_second"]["candidate"][metric] <
            min(x["scores"]["B_second"][control][metric]
                for control in ("hmm","symbolic")) for x in rows)
            for metric in ("brier","regret")}
        cohort[family]={"prefix_brier":sum(x["prefix_brier"] for x in rows)/12,
                        "means":means,"wins_vs_best_strong":wins}
    H={"P0":len(worlds)==24,
       "P1":all(cohort[f]["prefix_brier"]<=.23 for f in ("B1","B2"))}
    H["H1"]=all(
       cohort[f]["means"]["B_second"]["candidate"]["regret"] <=
       min(cohort[f]["means"]["B_second"][z]["regret"] for z in ("hmm","symbolic"))-.035
       and cohort[f]["wins_vs_best_strong"]["regret"]>=9
       for f in ("B1","B2"))
    H["H2"]=all(
       cohort[f]["means"]["B_second"]["candidate"]["brier"] <=
       min(cohort[f]["means"]["B_second"][z]["brier"] for z in ("hmm","symbolic"))-.005
       and cohort[f]["wins_vs_best_strong"]["brier"]>=9
       for f in ("B1","B2"))
    H["H3"]=all(
       cohort[f]["means"]["A_return"]["candidate"]["regret"] <=
       min(cohort[f]["means"]["A_return"][z]["regret"] for z in ("hmm","symbolic"))+.02
       and cohort[f]["means"]["A_return"]["candidate"]["brier"] <=
           cohort[f]["means"]["A_return"]["hmm"]["brier"]+.005
       for f in ("B1","B2"))
    H["H4"]=all(x["A_retained"] and x["B_retained"] for x in worlds)
    H["H5"]=sum(x["sham_false_B_admission"] for x in worlds)<=2 and all(
             x["bytes"]["candidate"]<4096 for x in worlds)
    H["H6"]=all(
       cohort[f]["means"]["B_second"]["candidate"]["regret"] <=
       min(cohort[f]["means"]["B_second"][z]["regret"] for z in ("lookup","know38"))-.035
       for f in ("B1","B2"))
    return {
       "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTO_BLOB,
       "fit_worlds":12,"held_worlds":24,"fit_source_calls":fit_calls,
       "held_unique_source_calls":9216,"arm_events_total":10752,
       "selected_hazards":selected,"fit_briers":fit_scores,
       "cohorts":cohort,"hypotheses":H,
       "A_retained_worlds":sum(x["A_retained"] for x in worlds),
       "B_retained_worlds":sum(x["B_retained"] for x in worlds),
       "sham_B_admission_worlds":sum(x["sham_false_B_admission"] for x in worlds),
       "worlds":worlds,
       "development_verdict":"DEVELOPMENT_SUPPORTED" if all(H.values()) else "DEVELOPMENT_MIXED_OR_NO_GO",
       "scientific_gain_verified":False,
       "caveat":"Shared forced-action data measure shadow intervention proposals, not chosen-action feedback or native transfer",
       "protected_original_world_first_use":False,
       "native_model_changed":False,"deployment":"NONE",
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
