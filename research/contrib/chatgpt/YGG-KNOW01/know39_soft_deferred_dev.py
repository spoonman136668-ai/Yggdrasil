"""KNOW39 frozen synthetic-only fast posterior readout + deferred posterior writes.

Preregression f38313a69d029595b7d382ea2e7e1bab2b80030b; no native
model or protected original-world source. Unit tests MUST inject mock y.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import time
import copy
from pathlib import Path
from know33_local_metaplastic_dev import Beta,canonical,digest
from know36_noisy_retention_dev import Comparator,brier,fit_hazard,q_for,x_for
from know38_buffer_before_write_dev import BufferBank,cold as prior_cold

PREREG="f38313a69d029595b7d382ea2e7e1bab2b80030b"
PROTO_BLOB="5eb63f3fbb1edc87665e9a23525386eb90765a48"
SCHEMA="yggdrasil.know39.soft-deferred-result.dev.v1"
ARMS=("candidate","hmm","hard_readout","no_buffer","no_switch","know38","rolling")
KINDS=("soft","hard_readout","no_buffer","no_switch")
HAZARDS=(.0078125,.03125,.125)

def need(ok,label):
    if not ok: raise ValueError("YGG_KNOW39_"+label)

def protocol():
    raw=Path(__file__).with_name("know39_soft_deferred_protocol.json").read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    need(blob==PROTO_BLOB,"PROTOCOL_BLOB")
    p=json.loads(raw)
    s=p["source"]
    need(p["schema"]=="yggdrasil.know39.fast-posterior-deferred-memory-prereg.v1"
         and s["fit_unique_events"]==3072 and s["held_unique_events"]==9216
         and s["arm_events_total"]==10752
         and p["authority"]["original_source_426"]=="NO_NEW_FIRST_USE"
         and p["authority"]["native_weights_changed"] is False,
         "PROTOCOL")
    seeds=sum(s["fit"].values(),[])+sum(s["held"].values(),[])
    need(len(seeds)==36 and len(set(seeds))==36
         and all(len(s["fit"][f])==6 and len(s["held"][f])==12 for f in ("B1","B2")),
         "SPLIT")
    return p

class SoftDeferred:
    """Instantaneous global two-state Bayesian belief and isolated capped banks."""
    def __init__(self,kind="soft",hazard=.03125):
        need(kind in KINDS and type(hazard) is float and hazard in HAZARDS,"KIND")
        self.kind=kind
        self.hazard=hazard
        self.banks=[[Beta() for _ in range(8)] for _ in range(2)]
        self.seen=[[0]*8 for _ in range(2)]
        self.pA=.95
        self.pending=[]
        self.received=0
        self.b_admissions=0

    def prior(self):
        return self.pA*(1-self.hazard)+(1-self.pA)*self.hazard

    def prob(self,x):
        need(type(x) is int and 0<=x<8,"READOUT")
        if self.kind=="no_switch":
            return self.banks[0][x].prob()
        w=self.prior()
        if self.kind=="hard_readout":
            return self.banks[0 if w>=.5 else 1][x].prob()
        return w*self.banks[0][x].prob()+(1-w)*self.banks[1][x].prob()

    def commit(self,observed,bank):
        need(bank in (0,1) and type(observed) is list,"COMMIT")
        for x,y in observed:
            if self.seen[bank][x]<6:
                self.banks[bank][x].update(y,1.0)
                self.seen[bank][x]+=1
        if bank==1:
            self.b_admissions+=1

    def observe(self,t,x,y):
        need(type(t) is int and t==self.received and t<256
             and type(x) is int and 0<=x<8
             and type(y) is int and y in (0,1),"EVENT")
        if self.kind!="no_switch":
            prior=self.prior()
            pa,pb=[bank[x].prob() for bank in self.banks]
            la=pa if y else 1-pa
            lb=pb if y else 1-pb
            den=prior*la+(1-prior)*lb
            need(den>0,"LIKELIHOOD")
            self.pA=prior*la/den
        # A separate fast belief update never writes the long-term banks.
        self.received+=1
        self.pending.append([x,y])
        bootstrap=any(self.seen[0][xx]<6 for xx in range(8))
        if self.kind=="no_buffer":
            events=self.pending
            self.pending=[]
        elif len(self.pending)==8:
            events=self.pending
            self.pending=[]
        else:
            return
        if bootstrap or self.kind=="no_switch":
            self.commit(events,0)
        elif self.pA>=.9:
            self.commit(events,0)
        elif self.pA<=.1:
            self.commit(events,1)
        # Ambiguous batches are discarded; stored memories remain unchanged.

    def state(self):
        return {"schema":"yggdrasil.know39.soft-deferred-state.dev.v1",
                "kind":self.kind,"hazard":self.hazard,
                "banks":[[v.state() for v in bank] for bank in self.banks],
                "seen":self.seen,"pA":self.pA,"pending":self.pending,
                "received":self.received,"b_admissions":self.b_admissions,
                "original_source":False}

    def checkpoint(self):
        raw=canonical(self.state())
        need(len(raw)<4096,"CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls,raw,sha):
        need(type(raw) is bytes and len(raw)<4096 and digest(raw)==sha,
             "CHECKSUM")
        def no_duplicate(pairs):
            d={}
            for k,v in pairs:
                need(k not in d,"DUPLICATE_KEY")
                d[k]=v
            return d
        try:
            d=json.loads(raw.decode("ascii"),object_pairs_hook=no_duplicate)
            need(type(d) is dict and d.get("kind") in KINDS
                 and type(d.get("hazard")) is float and d["hazard"] in HAZARDS,
                 "STATE_KIND")
            m=cls(d["kind"],d["hazard"])
            need(set(d)==set(m.state()) and d["schema"]==m.state()["schema"]
                 and d["original_source"] is False
                 and type(d["received"]) is int and 0<=d["received"]<=256
                 and type(d["b_admissions"]) is int
                 and 0<=d["b_admissions"]<=d["received"]
                 and type(d["pA"]) is float and math.isfinite(d["pA"])
                 and 0<=d["pA"]<=1
                 and type(d["pending"]) is list
                 and len(d["pending"])==(0 if d["kind"]=="no_buffer"
                                          else d["received"]%8)
                 and all(type(z) is list and len(z)==2
                         and type(z[0]) is int and 0<=z[0]<8
                         and type(z[1]) is int and z[1] in (0,1)
                         for z in d["pending"]),"STATE_LAYOUT")
            need(type(d["banks"]) is list and len(d["banks"])==2
                 and type(d["seen"]) is list and len(d["seen"])==2,"BANKS")
            for b in range(2):
                need(type(d["banks"][b]) is list and len(d["banks"][b])==8
                     and type(d["seen"][b]) is list and len(d["seen"][b])==8,
                     "BANK_SIZE")
                for x in range(8):
                    n=d["seen"][b][x]
                    need(type(n) is int and 0<=n<=6
                         and type(d["banks"][b][x]) is list
                         and len(d["banks"][b][x])==2,"CELL")
                    cell=Beta(*d["banks"][b][x])
                    need(cell.a+cell.b==n+2,"WITNESSES")
                    m.banks[b][x]=cell
            need(sum(map(sum,d["seen"]))<=d["received"],"OBS_BUDGET")
            for k in ("seen","pA","pending","received","b_admissions"):
                setattr(m,k,d[k])
            need(m.checkpoint()==raw,"NONCANONICAL")
            return m
        except (ValueError,KeyError,TypeError,UnicodeError,OverflowError) as e:
            raise ValueError("YGG_KNOW39_RESTORE_REJECT") from e

def cold(m):
    if isinstance(m,SoftDeferred):
        raw=m.checkpoint()
        new=SoftDeferred.restore(raw,digest(raw))
        need(new.checkpoint()==raw and
             all(new.prob(x)==m.prob(x) for x in range(8)),
             "COLD_READBACK")
        return new
    return prior_cold(m)

def models(h):
    return {
      "candidate":SoftDeferred("soft",h),
      "hmm":Comparator("hmm",h),
      "hard_readout":SoftDeferred("hard_readout",h),
      "no_buffer":SoftDeferred("no_buffer",h),
      "no_switch":SoftDeferred("no_switch",h),
      "know38":BufferBank(),
      "rolling":Comparator("rolling"),
    }

def private_y(seed,t,law):
    need(os.environ.get("YGG_KNOW39_HELD_ONE_SHOT")=="1",
         "SOURCE_DENIED")
    need(type(seed) is int and type(t) is int and 0<=t<256
         and law in ("A","B1","B2"),"SOURCE_ID")
    q=q_for(law,x_for(t))
    h=hashlib.sha256(f"know39:synthetic:coin:v1:{seed}:{t}:{law}".encode()).digest()
    return int(int.from_bytes(h[:8],"big")/(1<<64)<q)

def held_world(seed,family,hazard,witness=private_y):
    # Exactly 384 distinct evaluator-only source outcomes per world.
    A=[witness(seed,t,"A") for t in range(256)]
    B={t:witness(seed,t,family)
       for t in list(range(64,128))+list(range(192,256))}
    ms=models(hazard)
    for t in range(64):
        for m in ms.values():
            m.observe(t,x_for(t),A[t])
    prefix={k:cold(m) for k,m in ms.items()}
    pre=sum(brier(prefix["candidate"].prob(x),q_for("A",x))
            for x in range(8))/8
    oldA=copy.deepcopy(prefix["candidate"].state()["banks"][0])
    results={}
    for branch in ("treatment","sham"):
        active={k:cold(m) for k,m in prefix.items()}
        scores={stage:{k:[] for k in ARMS}
                for stage in ("B_first","A_return","B_second")}
        ns={k:0 for k in ARMS}
        B128=B192=None
        keepA=True
        start_admit=active["candidate"].b_admissions
        for t in range(64,256):
            stage="B_first" if t<128 else ("A_return" if t<192 else "B_second")
            law=family if branch=="treatment" and stage!="A_return" else "A"
            y=B[t] if law==family else A[t]
            x=x_for(t)
            for k,m in active.items():
                scores[stage][k].append(brier(m.prob(x),q_for(law,x)))
                start=time.perf_counter_ns()
                m.observe(t,x,y)
                ns[k]+=time.perf_counter_ns()-start
            if t+1 in (128,192,256):
                active={k:cold(m) for k,m in active.items()}
                if branch=="treatment":
                    keepA &= active["candidate"].state()["banks"][0]==oldA
                    if t+1==128:
                        B128=copy.deepcopy(active["candidate"].state()["banks"][1])
                    elif t+1==192:
                        B192=copy.deepcopy(active["candidate"].state()["banks"][1])
        need(all(m.received==256 for m in active.values()),"MODEL_EVENTS")
        results[branch]={
          "scores":{stage:{k:sum(v)/64 for k,v in group.items()}
                    for stage,group in scores.items()},
          "B_admissions":active["candidate"].b_admissions-start_admit,
          "bytes":{k:len(m.checkpoint()) for k,m in active.items()},
          "ns":ns,
        }
    return {
      "seed":seed,"family":family,"A_prefix":pre,
      "scores":results["treatment"]["scores"],
      "A_retained":keepA,"B_retained":B128==B192,
      "sham_B_admission":results["sham"]["B_admissions"]>0,
      "B_admissions":results["treatment"]["B_admissions"],
      "bytes":results["treatment"]["bytes"],"elapsed_ns":results["treatment"]["ns"],
      "source_calls":384,"arm_events":448
    }

def proof():
    need(os.environ.get("YGG_KNOW39_HELD_ONE_SHOT")=="1",
         "FIRST_USE_DENIED")
    p=protocol()
    for base in range(0,256,16):
        xx=[x_for(t) for t in range(base,base+16)]
        need(all(xx.count(x)==2 for x in range(8)),"PUBLIC_SUPPORT")
    h,fit=fit_hazard({"source":{"fit_seeds":p["source"]["fit"]}},
                     witness=private_y)
    worlds=[held_world(seed,f,h) for f in ("B1","B2")
            for seed in p["source"]["held"][f]]
    need(len(worlds)==24 and sum(x["source_calls"] for x in worlds)==9216
         and all(x["arm_events"]==448 for x in worlds),"COUNTS")
    cohorts={}
    for f in ("B1","B2"):
        rows=[z for z in worlds if z["family"]==f]
        scores={stage:{k:sum(z["scores"][stage][k] for z in rows)/12
                       for k in ARMS}
                for stage in ("B_first","A_return","B_second")}
        cohorts[f]={
          "A_prefix":sum(z["A_prefix"] for z in rows)/12,
          "scores":scores,
          "wins_vs_hmm":sum(z["scores"]["B_second"]["candidate"]<
                            z["scores"]["B_second"]["hmm"] for z in rows),
        }
    f=cohorts
    H={
      "P0":len(worlds)==24,
      "P1":all(f[x]["A_prefix"]<=.23 for x in ("B1","B2")),
      "H1":all(f[x]["scores"]["B_second"]["candidate"]<=
               f[x]["scores"]["B_second"]["hmm"]-.005
               and f[x]["wins_vs_hmm"]>=9 for x in ("B1","B2")),
      "H2":all(f[x]["scores"]["B_second"]["candidate"]<=
               min(f[x]["scores"]["B_second"][k] for k in
                   ("hard_readout","no_buffer","know38"))-.005
               for x in ("B1","B2")),
      "H3":all(f[x]["scores"]["A_return"]["candidate"]<=
               f[x]["scores"]["A_return"]["hmm"]+.005
               for x in ("B1","B2")),
      "H4":all(z["A_retained"] and z["B_retained"] for z in worlds),
      "H5":sum(z["sham_B_admission"] for z in worlds)<=2
           and all(z["bytes"]["candidate"]<4096 for z in worlds)
    }
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTO_BLOB,
      "fit_worlds":12,"held_worlds":24,"fit_source_calls":3072,
      "held_unique_source_events":9216,"arm_events_total":10752,
      "fit_hazard":h,"fit_hmm_briers":fit,"families":cohorts,
      "frozen_hypotheses":H,
      "A_retained_worlds":sum(z["A_retained"] for z in worlds),
      "B_retained_worlds":sum(z["B_retained"] for z in worlds),
      "sham_false_B_admission_worlds":sum(z["sham_B_admission"] for z in worlds),
      "worlds":worlds,
      "development_verdict":"DEVELOPMENT_SUPPORTED" if all(H.values())
                            else "DEVELOPMENT_MIXED_OR_NO_GO",
      "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "protected_original_world_first_use":False,
      "native_model_changed":False,"deployment":"NONE",
      "cost_notice":"Python interpreted per-observation timings are not matched compute"
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
