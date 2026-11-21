"""KNOW36: noisy A/B/A/B comparison, source-only, owner-safe.
Preregistered at 01e9ca76e7b358ea3d414fd22450b90910d6f2d4.
Never call proof()/private_y() in unit tests; protected #426 excluded.
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
from know34_local_contradiction_dev import private_law_bit
from know35_two_regime_bank_dev import TwoBankCells

PREREG="01e9ca76e7b358ea3d414fd22450b90910d6f2d4"
PROTO_BLOB="af1769f93a78b89f3f76577033787643f1185efe"
CANDIDATE_BLOB="8aa74ada276748faa7b32f834d406a9293ef40e0"
SCHEMA="yggdrasil.know36.noisy-two-regime-result.dev.v1"
HAZARDS=(.0078125,.03125,.125)
ARMS=("candidate","hmm","random","rolling","single")
LIMIT=256

def require(x,label):
    if not x: raise ValueError("YGG_KNOW36_"+label)

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def protocol():
    d=Path(__file__).parent
    raw=(d/"know36_noisy_retention_protocol.json").read_bytes()
    require(blob(raw)==PROTO_BLOB,"PROTOCOL_BLOB")
    require(blob((d/"know35_two_regime_bank_dev.py").read_bytes())==CANDIDATE_BLOB,
            "CANDIDATE_BLOB")
    p=json.loads(raw)
    s=p["source"]
    require(p["schema"]=="yggdrasil.know36.noisy-two-regime-retention-prereg.v1"
            and s["fit_unique_events"]==3072 and s["held_unique_events"]==9216
            and s["model_observations_per_arm_held_total"]==10752
            and p["methods"]["hmm_hazards"]==list(HAZARDS)
            and p["authority"]["protected_original_world_first_use"] is False
            and p["authority"]["native_model_changed"] is False,"PROTOCOL")
    fs=sum(s["fit_seeds"].values(),[])
    hs=sum(s["held_seeds"].values(),[])
    require(len(fs)==12 and len(hs)==24 and len(set(fs+hs))==36,"SEEDS")
    return p

def x_for(t):
    require(type(t) is int and 0<=t<LIMIT,"PUBLIC_TIME")
    return (t%8)^(((t//8)%2)<<1)

def q_for(law,x):
    return .85 if private_law_bit(law,x) else .15

def brier(p,q):
    require(0<=p<=1 and 0<=q<=1,"SCORE")
    return q*(1-q)+(p-q)**2

class Comparator:
    """Conventional global two-head switching HMM or simple controls."""
    def __init__(self,kind,hazard=.03125):
        require(kind in ("hmm","rolling","single"),"KIND")
        require(kind!="hmm" or hazard in HAZARDS,"HAZARD")
        self.kind=kind
        self.hazard=hazard
        self.banks=[[Beta() for _ in range(8)] for _ in range(2)]
        self.p_a=.95
        self.n=[0]*8
        self.history=[[] for _ in range(8)]
        self.received=0
    def prob(self,x):
        require(type(x) is int and 0<=x<8,"READOUT")
        if self.kind=="rolling":
            h=self.history[x]
            return (1+sum(h))/(2+len(h))
        if self.kind=="single":
            return self.banks[0][x].prob()
        w=self.p_a*(1-self.hazard)+(1-self.p_a)*self.hazard
        return w*self.banks[0][x].prob()+(1-w)*self.banks[1][x].prob()
    def observe(self,t,x,y):
        require(type(t) is int and t==self.received and t<LIMIT
                and type(x) is int and 0<=x<8
                and type(y) is int and y in (0,1),"EVENT")
        if self.kind=="single":
            self.banks[0][x].update(y,1.0)
        elif self.kind=="rolling":
            self.history[x].append(y)
            self.history[x]=self.history[x][-8:]
        elif self.n[x]<6:
            self.banks[0][x].update(y,1.0)
        else:
            prior=self.p_a*(1-self.hazard)+(1-self.p_a)*self.hazard
            pa,pb=[z[x].prob() for z in self.banks]
            la=pa if y else 1-pa
            lb=pb if y else 1-pb
            post=prior*la/(prior*la+(1-prior)*lb)
            self.p_a=post
            self.banks[0][x].update(y,float(post))
            self.banks[1][x].update(y,float(1-post))
        self.n[x]+=1
        self.received+=1
    def state(self):
        return {"kind":self.kind,"hazard":self.hazard,"p_a":self.p_a,
                "received":self.received,"n":self.n,"history":self.history,
                "banks":[[z.state() for z in b] for b in self.banks],
                "original_source":False}
    def checkpoint(self):
        raw=canonical(self.state())
        require(len(raw)<4096,"CHECKPOINT_BYTES")
        return raw

class RandomBank(TwoBankCells):
    """Equal state budget to candidate; fixed noninformative hash gate."""
    def observe(self,t,x,y):
        require(type(t) is int and t==self.received and t<LIMIT
                and type(x) is int and 0<=x<8
                and type(y) is int and y in (0,1),"RANDOM_EVENT")
        g=x//2
        cur=self.active[g]
        h=hashlib.sha256(f"know36:random-gate:v1:{t}:{x}".encode()).digest()
        if self.seen[cur][x]==6 and int.from_bytes(h[:8],"big")%32==0:
            cur=1-cur
            self.active[g]=cur
            self.switches+=1
        if self.seen[cur][x]<6:
            self.banks[cur][x].update(y,1.0)
            self.seen[cur][x]+=1
        self.received+=1
    @classmethod
    def restore(cls,raw,sha):
        original=TwoBankCells.restore(raw,sha)
        m=cls()
        m.__dict__=original.__dict__
        return m

def cold(m):
    raw=m.checkpoint()
    if isinstance(m,TwoBankCells):
        restored=type(m).restore(raw,digest(raw))
    else:
        restored=copy.deepcopy(m)
    require(restored.checkpoint()==raw
            and [restored.prob(x) for x in range(8)]==
                [m.prob(x) for x in range(8)],"COLD_READBACK")
    return restored

def models(h):
    return {"candidate":TwoBankCells(),"hmm":Comparator("hmm",h),
            "random":RandomBank(),"rolling":Comparator("rolling"),
            "single":Comparator("single")}

def private_y(seed,t,law):
    require(os.environ.get("YGG_KNOW36_HELD_ONE_SHOT")=="1","HELD_DENIED")
    require(type(seed) is int and type(t) is int and 0<=t<LIMIT
            and law in ("A","B1","B2"),"SOURCE")
    q=q_for(law,x_for(t))
    coin=hashlib.sha256(f"know36:synthetic:noise:v1:{seed}:{t}".encode()).digest()
    return int(int.from_bytes(coin[:8],"big")/(1<<64)<q)

def fit_hazard(p, witness=private_y):
    costs={h:[] for h in HAZARDS}
    calls=0
    for family in ("B1","B2"):
        for seed in p["source"]["fit_seeds"][family]:
            ys=[]
            for t in range(LIMIT):
                law=family if (64<=t<128 or 192<=t<256) else "A"
                ys.append(witness(seed,t,law))
                calls+=1
            for h in HAZARDS:
                m=Comparator("hmm",h)
                score=0.0
                for t,y in enumerate(ys):
                    x=x_for(t)
                    law=family if (64<=t<128 or 192<=t<256) else "A"
                    if t>=64: score+=brier(m.prob(x),q_for(law,x))
                    m.observe(t,x,y)
                costs[h].append(score/192)
    require(calls==3072 and all(len(v)==12 for v in costs.values()),"FIT_COUNT")
    h=min(HAZARDS,key=lambda h:(sum(costs[h])/12,h))
    return h,{str(k):sum(v)/12 for k,v in costs.items()}

def held_world(seed,family,h,witness=private_y):
    # Exactly 384 unique source requests. Reuse shared A outcomes for both forks.
    source_A=[witness(seed,t,"A") for t in range(LIMIT)]
    source_B={t:witness(seed,t,family)
              for t in list(range(64,128))+list(range(192,256))}
    prefix=models(h)
    for t in range(64):
        for m in prefix.values(): m.observe(t,x_for(t),source_A[t])
    prefix={name:cold(m) for name,m in prefix.items()}
    a_prefix=sum(brier(prefix["candidate"].prob(x),q_for("A",x))
                 for x in range(8))/8
    old_a=prefix["candidate"].state()["banks"][0]
    forks={}
    for branch in ("control_A","treatment_B"):
        ms={name:cold(m) for name,m in prefix.items()}
        stats={stage:{name:[] for name in ARMS}
               for stage in ("B_first","A_return","B_second")}
        prefix_switches=ms["candidate"].switches
        elapsed_ns={name:0 for name in ARMS}
        bank_b_128=None
        bank_b_192=None
        keep_a=True
        for t in range(64,LIMIT):
            stage="B_first" if t<128 else ("A_return" if t<192 else "B_second")
            law=family if branch=="treatment_B" and stage!="A_return" else "A"
            y=source_B[t] if law==family else source_A[t]
            x=x_for(t)
            for name,m in ms.items():
                stats[stage][name].append(brier(m.prob(x),q_for(law,x)))
                started=time.perf_counter_ns()
                m.observe(t,x,y)
                elapsed_ns[name]+=time.perf_counter_ns()-started
            if t+1 in (128,192,256):
                ms={name:cold(m) for name,m in ms.items()}
                if branch=="treatment_B":
                    keep_a &= ms["candidate"].state()["banks"][0]==old_a
                    if t+1==128: bank_b_128=ms["candidate"].state()["banks"][1]
                    if t+1==192: bank_b_192=ms["candidate"].state()["banks"][1]
        require(all(m.received==LIMIT for m in ms.values()),"MODEL_EVENTS")
        forks[branch]={
            "scores":{stage:{name:sum(v)/64 for name,v in row.items()}
                      for stage,row in stats.items()},
            "sham_switches":ms["candidate"].switches-prefix_switches,
            "candidate_bytes":len(ms["candidate"].checkpoint()),
            "checkpoint_bytes":{name:len(m.checkpoint()) for name,m in ms.items()},
            "observation_ns":elapsed_ns,
        }
    return {
      "seed":seed,"family":family,"A_prefix":a_prefix,
      "scores":forks["treatment_B"]["scores"],
      "old_A_preserved":keep_a,"old_B_preserved":bank_b_128==bank_b_192,
      "sham_switch_delta":forks["control_A"]["sham_switches"],
      "candidate_bytes":forks["treatment_B"]["candidate_bytes"],
      "checkpoint_bytes":forks["treatment_B"]["checkpoint_bytes"],
      "observation_ns":forks["treatment_B"]["observation_ns"],
      "source_calls":384,"model_events_per_arm":448,
    }

def proof():
    require(os.environ.get("YGG_KNOW36_HELD_ONE_SHOT")=="1","FIRST_USE_GATE")
    p=protocol()
    for base in range(0,LIMIT,16):
        cells=[x_for(t) for t in range(base,base+16)]
        require(all(cells.count(x)==2 for x in range(8)),"SUPPORT")
    h,cost=fit_hazard(p)
    worlds=[held_world(seed,family,h) for family in ("B1","B2")
            for seed in p["source"]["held_seeds"][family]]
    require(len(worlds)==24 and sum(w["source_calls"] for w in worlds)==9216
            and all(w["model_events_per_arm"]==448 for w in worlds),
            "SOURCE_MODEL_BUDGET")
    families={}
    for family in ("B1","B2"):
        rows=[w for w in worlds if w["family"]==family]
        means={stage:{name:sum(w["scores"][stage][name] for w in rows)/12
                     for name in ARMS}
               for stage in ("B_first","A_return","B_second")}
        families[family]={"scores":means,
          "A_prefix":sum(w["A_prefix"] for w in rows)/12,
          "B_second_paired_wins_vs_hmm":sum(
             w["scores"]["B_second"]["candidate"] <
             w["scores"]["B_second"]["hmm"] for w in rows)}
    f=families
    H={}
    H["P0"]=len(worlds)==24
    H["P1"]=all(f[x]["A_prefix"]<=.23 for x in ("B1","B2"))
    H["H1"]=all(f[x]["scores"]["B_second"]["candidate"]<=
                f[x]["scores"]["B_second"]["hmm"]-.005 and
                f[x]["B_second_paired_wins_vs_hmm"]>=9 for x in ("B1","B2"))
    H["H2"]=all(f[x]["scores"]["B_second"]["candidate"]<=
                f[x]["scores"]["B_second"]["random"]-.005 for x in ("B1","B2"))
    H["H3"]=all(f[x]["scores"]["A_return"]["candidate"]<=
                f[x]["scores"]["A_return"]["hmm"]+.005 for x in ("B1","B2"))
    H["H4"]=all(w["old_A_preserved"] and w["old_B_preserved"]
                for w in worlds)
    sham=sum(w["sham_switch_delta"]>0 for w in worlds)
    H["H5"]=sham<=2 and all(w["candidate_bytes"]<4096 for w in worlds)
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTO_BLOB,
      "fit_worlds":12,"held_worlds":24,"fit_source_calls":3072,
      "held_unique_source_events":9216,"model_events_per_arm":10752,
      "selected_hmm_hazard":h,"fit_hmm_briers":cost,
      "family_metrics":families,"frozen_hypotheses":H,
      "sham_false_switch_worlds":sham,
      "live_A_retained_worlds":sum(w["old_A_preserved"] for w in worlds),
      "B_retained_worlds":sum(w["old_B_preserved"] for w in worlds),
      "worlds":worlds,
      "measurement_note":"Python per-observe nanoseconds exploratory; not controlled equal compute",
      "development_verdict":("DEVELOPMENT_SUPPORTED" if all(H.values())
                             else "DEVELOPMENT_MIXED_OR_NO_GO"),
      "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "original_first_use_426":False,"native_changed":False,
      "deployment":"NONE"
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
