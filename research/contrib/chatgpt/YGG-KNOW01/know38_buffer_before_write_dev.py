"""KNOW38 buffered-before-write, synthetic-only prospective research.
Protocol commit 585a15b00a1c2237753c1c426b456f00b68100ff was frozen
before this code. Unit tests must never open private_y or proof.
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
from know36_noisy_retention_dev import Comparator, brier, fit_hazard, q_for, x_for
from know37_local_hysteresis_dev import Mem, cold as old_cold

PREREG = "585a15b00a1c2237753c1c426b456f00b68100ff"
PROTO_BLOB = "b672bb9efc6e178c470ec4a13cb43cead5695d95"
SCHEMA = "yggdrasil.know38.buffer-before-write-result.dev.v1"
ARMS = ("candidate", "hmm", "random", "no_switch", "no_quarantine", "rolling")
KINDS = ("candidate", "random", "no_switch")

def need(v, label):
    if not v:
        raise ValueError("YGG_KNOW38_" + label)

def protocol():
    raw=Path(__file__).with_name("know38_buffer_before_write_protocol.json").read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    need(blob==PROTO_BLOB,"PROTOCOL_BLOB")
    p=json.loads(raw)
    s=p["source"]
    need(p["schema"]=="yggdrasil.know38.buffer-before-write-regime-memory-prereg.v1"
         and s["fit_source_events"]==3072
         and s["held_unique_source_events"]==9216
         and s["model_occurrences_per_arm_held_total"]==10752
         and p["mechanism"]["physical_cells"]==8
         and p["mechanism"]["adjacent_pair_groups"]==4
         and p["mechanism"]["banks_per_cell"]==2
         and p["scope"]["protected_new_original_world_first_use"] is False
         and p["scope"]["native_model_changed"] is False, "PROTOCOL")
    seeds=sum(s["fit"].values(),[])+sum(s["held"].values(),[])
    need(len(seeds)==36 and len(set(seeds))==36
         and all(len(s["fit"][f])==6 and len(s["held"][f])==12
                 for f in ("B1","B2")),"SPLIT")
    return p

class BufferBank:
    """Freeze pending (x,y) until 8-input pair batch has selected a bank."""
    def __init__(self,kind="candidate"):
        need(kind in KINDS,"KIND")
        self.kind=kind
        self.banks=[[Beta() for _ in range(8)] for _ in range(2)]
        self.seen=[[0]*8 for _ in range(2)]
        self.active=[0]*4
        self.pending=[[] for _ in range(4)]
        self.group_events=[0]*4
        self.received=0
        self.switches=0

    def prob(self,x):
        need(type(x) is int and 0<=x<8,"READOUT")
        return self.banks[self.active[x//2]][x].prob()

    def observe(self,t,x,y):
        need(type(t) is int and t==self.received and t<256
             and type(x) is int and 0<=x<8
             and type(y) is int and y in (0,1),"EVENT")
        g=x//2
        self.pending[g].append([x,y])
        self.group_events[g]+=1
        self.received+=1
        if len(self.pending[g])<8:
            return
        cur=self.active[g]
        # Initial 64-event A prefix trains bank zero to 6 observations per x.
        init=cur==0 and any(self.seen[0][xx]<6 for xx in (2*g,2*g+1))
        if not init:
            other=1-cur
            values=[]
            for xx,yy in self.pending[g]:
                a=self.banks[cur][xx].prob()
                b=self.banks[other][xx].prob()
                v=math.log((b if yy else 1-b)/(a if yy else 1-a))
                values.append(max(-3.0,min(3.0,v)))
            if self.kind=="candidate":
                flip=sum(v>0 for v in values)>=4 and sum(values)>=3.0
            elif self.kind=="random":
                token=f"know38:random:v1:{g}:{self.group_events[g]}".encode()
                flip=int.from_bytes(hashlib.sha256(token).digest()[:8],"big")%32==0
            else:
                flip=False
            if flip:
                cur=other
                self.active[g]=other
                self.switches+=1
        # Single atomic write destination, never during tentative detection.
        for xx,yy in self.pending[g]:
            if self.seen[cur][xx]<6:
                self.banks[cur][xx].update(yy,1.0)
                self.seen[cur][xx]+=1
        self.pending[g]=[]

    def state(self):
        return {"schema":"yggdrasil.know38.buffer-state.dev.v1",
                "kind":self.kind,
                "banks":[[v.state() for v in b] for b in self.banks],
                "seen":self.seen,"active":self.active,"pending":self.pending,
                "group_events":self.group_events,"received":self.received,
                "switches":self.switches,"original_source":False}

    def checkpoint(self):
        raw=canonical(self.state())
        need(len(raw)<4096,"CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls,raw,sha):
        need(type(raw) is bytes and len(raw)<4096 and digest(raw)==sha,"CHECKSUM")
        def unique(items):
            d={}
            for k,v in items:
                need(k not in d,"DUPLICATE")
                d[k]=v
            return d
        try:
            d=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            need(type(d) is dict and d.get("kind") in KINDS,"TYPE")
            m=cls(d["kind"])
            need(set(d)==set(m.state()) and d["schema"]==m.state()["schema"]
                 and d["original_source"] is False
                 and type(d["received"]) is int and 0<=d["received"]<=256
                 and type(d["switches"]) is int and 0<=d["switches"]<=d["received"]
                 and type(d["active"]) is list and len(d["active"])==4
                 and all(type(x) is int and x in (0,1) for x in d["active"])
                 and type(d["group_events"]) is list and len(d["group_events"])==4
                 and all(type(x) is int and 0<=x<=256 for x in d["group_events"])
                 and sum(d["group_events"])==d["received"]
                 and type(d["pending"]) is list and len(d["pending"])==4,
                 "SHAPE")
            for g in range(4):
                q=d["pending"][g]
                need(type(q) is list and len(q)==d["group_events"][g]%8
                     and all(type(z) is list and len(z)==2
                             and type(z[0]) is int and z[0]//2==g
                             and type(z[1]) is int and z[1] in (0,1)
                             for z in q),"PENDING")
            need(type(d["banks"]) is list and len(d["banks"])==2
                 and type(d["seen"]) is list and len(d["seen"])==2,
                 "BANKS")
            for b in range(2):
                need(type(d["banks"][b]) is list and len(d["banks"][b])==8
                     and type(d["seen"][b]) is list and len(d["seen"][b])==8,
                     "BANK_SHAPE")
                for xx in range(8):
                    n=d["seen"][b][xx]
                    need(type(n) is int and 0<=n<=6
                         and type(d["banks"][b][xx]) is list
                         and len(d["banks"][b][xx])==2,"CELL")
                    beta=Beta(*d["banks"][b][xx])
                    need(beta.a+beta.b==2+n,"WITNESS_COUNT")
                    m.banks[b][xx]=beta
            need(sum(map(sum,d["seen"]))<=d["received"],"WITNESS_BUDGET")
            for key in ("seen","active","pending","group_events","received","switches"):
                setattr(m,key,d[key])
            need(m.checkpoint()==raw,"NONCANONICAL")
            return m
        except (ValueError,TypeError,UnicodeError,OverflowError,KeyError) as e:
            raise ValueError("YGG_KNOW38_BAD_COLD_STATE") from e

def cold(m):
    if isinstance(m,BufferBank):
        raw=m.checkpoint()
        copy_model=BufferBank.restore(raw,digest(raw))
        need(copy_model.checkpoint()==raw and
             all(copy_model.prob(x)==m.prob(x) for x in range(8)),
             "COLD_READBACK")
        return copy_model
    return old_cold(m)

def models(hazard):
    return {"candidate":BufferBank(),
            "hmm":Comparator("hmm",hazard),
            "random":BufferBank("random"),
            "no_switch":BufferBank("no_switch"),
            "no_quarantine":Mem("candidate"),
            "rolling":Comparator("rolling")}

def private_y(seed,t,law):
    need(os.environ.get("YGG_KNOW38_HELD_ONE_SHOT")=="1","SOURCE_DENIED")
    need(type(seed) is int and type(t) is int and 0<=t<256
         and law in ("A","B1","B2"),"SOURCE")
    q=q_for(law,x_for(t))
    h=hashlib.sha256(f"know38:synthetic:noise:v1:{seed}:{t}:{law}".encode()).digest()
    return int(int.from_bytes(h[:8],"big")/(1<<64)<q)

def held_world(seed,family,hazard,witness=private_y):
    A=[witness(seed,t,"A") for t in range(256)]
    B={t:witness(seed,t,family)
       for t in list(range(64,128))+list(range(192,256))}
    prefix=models(hazard)
    for t in range(64):
        for m in prefix.values():
            m.observe(t,x_for(t),A[t])
    prefix={k:cold(m) for k,m in prefix.items()}
    pre=sum(brier(prefix["candidate"].prob(x),q_for("A",x)) for x in range(8))/8
    old_A=prefix["candidate"].state()["banks"][0]
    branches={}
    for branch in ("treatment","control_A"):
        ms={k:cold(m) for k,m in prefix.items()}
        scores={stage:{k:[] for k in ARMS}
                for stage in ("B_first","A_return","B_second")}
        cost={k:0 for k in ARMS}
        start_switch=ms["candidate"].switches
        preserved_A=True
        B128=B192=None
        for t in range(64,256):
            stage="B_first" if t<128 else ("A_return" if t<192 else "B_second")
            law=family if branch=="treatment" and stage!="A_return" else "A"
            y=B[t] if law==family else A[t]
            x=x_for(t)
            for k,m in ms.items():
                scores[stage][k].append(brier(m.prob(x),q_for(law,x)))
                begin=time.perf_counter_ns()
                m.observe(t,x,y)
                cost[k]+=time.perf_counter_ns()-begin
            if t+1 in (128,192,256):
                ms={k:cold(m) for k,m in ms.items()}
                if branch=="treatment":
                    preserved_A &= ms["candidate"].state()["banks"][0]==old_A
                    if t+1==128: B128=ms["candidate"].state()["banks"][1]
                    if t+1==192: B192=ms["candidate"].state()["banks"][1]
        need(all(m.received==256 for m in ms.values()),"ARM_EVENTS")
        branches[branch]={
            "scores":{stage:{k:sum(v)/64 for k,v in row.items()}
                      for stage,row in scores.items()},
            "switches":ms["candidate"].switches-start_switch,
            "bytes":{k:len(m.checkpoint()) for k,m in ms.items()},
            "cost_ns":cost,
        }
    return {"seed":seed,"family":family,"A_prefix":pre,
            "scores":branches["treatment"]["scores"],
            "A_retained":preserved_A,"B_retained":B128==B192,
            "sham_switch":branches["control_A"]["switches"]>0,
            "bytes":branches["treatment"]["bytes"],
            "cost_ns":branches["treatment"]["cost_ns"],
            "source_calls":384,"model_events_per_arm":448}

def proof():
    need(os.environ.get("YGG_KNOW38_HELD_ONE_SHOT")=="1","FIRST_USE_DENIED")
    p=protocol()
    for base in range(0,256,16):
        xs=[x_for(t) for t in range(base,base+16)]
        need(all(xs.count(x)==2 for x in range(8)),"TAPE_SUPPORT")
    hazard,fit=fit_hazard({"source":{"fit_seeds":p["source"]["fit"]}},
                          witness=private_y)
    worlds=[held_world(seed,family,hazard) for family in ("B1","B2")
            for seed in p["source"]["held"][family]]
    need(len(worlds)==24 and sum(w["source_calls"] for w in worlds)==9216
         and all(w["model_events_per_arm"]==448 for w in worlds),
         "SOURCE_BUDGET")
    cohorts={}
    for family in ("B1","B2"):
        rows=[w for w in worlds if w["family"]==family]
        scores={phase:{k:sum(w["scores"][phase][k] for w in rows)/12
                       for k in ARMS}
                for phase in ("B_first","A_return","B_second")}
        cohorts[family]={"scores":scores,
            "A_prefix":sum(w["A_prefix"] for w in rows)/12,
            "wins_vs_hmm":sum(w["scores"]["B_second"]["candidate"]<
                              w["scores"]["B_second"]["hmm"] for w in rows)}
    H={
      "P0":len(worlds)==24,
      "P1":all(cohorts[f]["A_prefix"]<=.23 for f in ("B1","B2")),
      "H1":all(cohorts[f]["scores"]["B_second"]["candidate"]<=
               cohorts[f]["scores"]["B_second"]["hmm"]-.005 and
               cohorts[f]["wins_vs_hmm"]>=9 for f in ("B1","B2")),
      "H2":all(cohorts[f]["scores"]["B_second"]["candidate"]<=
               min(cohorts[f]["scores"]["B_second"][k] for k in
                   ("random","no_switch","no_quarantine"))-.005
               for f in ("B1","B2")),
      "H3":all(cohorts[f]["scores"]["A_return"]["candidate"]<=
               cohorts[f]["scores"]["A_return"]["hmm"]+.005
               for f in ("B1","B2")),
      "H4":all(w["A_retained"] and w["B_retained"] for w in worlds),
      "H5":sum(w["sham_switch"] for w in worlds)<=2 and
            all(w["bytes"]["candidate"]<4096 for w in worlds),
    }
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTO_BLOB,
      "fit_worlds":12,"held_worlds":24,"fit_source_calls":3072,
      "held_unique_source_events":9216,"model_events_per_arm":10752,
      "selected_hmm_hazard":hazard,"fit_hmm_briers":fit,
      "families":cohorts,"frozen_hypotheses":H,
      "sham_false_switch_worlds":sum(w["sham_switch"] for w in worlds),
      "A_retained_worlds":sum(w["A_retained"] for w in worlds),
      "B_retained_worlds":sum(w["B_retained"] for w in worlds),
      "worlds":worlds,"compute_note":"Python timings exploratory, not equal compute",
      "development_verdict":"DEVELOPMENT_SUPPORTED" if all(H.values()) else "DEVELOPMENT_MIXED_OR_NO_GO",
      "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "protected_original_world_first_use":False,
      "native_model_changed":False,"deployment":"NONE",
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
