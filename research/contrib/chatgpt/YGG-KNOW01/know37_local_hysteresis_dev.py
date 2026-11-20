"""KNOW37 preregistered local-evidence hysteresis synthetic development only.
Protocol frozen before this file; no protected original-world or native model.
Tests use injected mock witnesses only; no FIT/HELD first use.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import os
from pathlib import Path
from know33_local_metaplastic_dev import Beta, canonical, digest
from know35_two_regime_bank_dev import TwoBankCells
from know36_noisy_retention_dev import Comparator, brier, fit_hazard, q_for, x_for

PREREG="9d8d55225c217ba9af2a1ca22ee2f50ac16ec468"
PROTOCOL_BLOB="5fdb34aafca11cfd41277dab655b7cbf3667371a"
SCHEMA="yggdrasil.know37.hysteresis-result.dev.v1"
ARMS=("candidate","hmm","random","no_switch","old35","rolling")

def require(v, why):
    if not v:
        raise ValueError("YGG_KNOW37_"+why)

def protocol():
    raw=Path(__file__).with_name("know37_local_hysteresis_protocol.json").read_bytes()
    gitsha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    require(gitsha==PROTOCOL_BLOB,"PROTOCOL")
    p=json.loads(raw)
    s=p["source"]
    require(p["schema"]=="yggdrasil.know37.accumulated-local-evidence-hysteresis-prereg.v1"
            and s["fit_unique_events"]==3072 and s["held_unique_events"]==9216
            and s["held_per_method_model_events"]==10752
            and p["authority"]["protected_original_world_426"] is False
            and p["authority"]["native_training"] is False,"DRIFT")
    seeds=sum(s["fit"].values(),[])+sum(s["held"].values(),[])
    require(len(seeds)==36 and len(set(seeds))==36
            and all(len(s["fit"][f])==6 and len(s["held"][f])==12
                    for f in ("B1","B2")),"SPLIT")
    return p

class Mem:
    def __init__(self,kind="candidate"):
        require(kind in ("candidate","random","no_switch"),"KIND")
        self.kind=kind
        self.banks=[[Beta() for _ in range(8)] for _ in range(2)]
        self.seen=[[0]*8 for _ in range(2)]
        self.active=[0]*4
        self.evidence=[[] for _ in range(4)]
        self.group_events=[0]*4
        self.last_switch=[0]*4
        self.received=0
        self.switches=0

    def prob(self,x):
        require(type(x) is int and 0<=x<8,"READOUT")
        return self.banks[self.active[x//2]][x].prob()

    def observe(self,t,x,y):
        require(type(t) is int and t==self.received and t<256
                and type(x) is int and 0<=x<8
                and type(y) is int and y in (0,1),"EVENT")
        g=x//2
        cur=self.active[g]
        if self.seen[cur][x]>=6:
            p=self.banks[cur][x].prob()
            q=self.banks[1-cur][x].prob()
            term=math.log((q if y else 1-q)/(p if y else 1-p))
            self.evidence[g].append(max(-3.0,min(3.0,term)))
            self.evidence[g]=self.evidence[g][-6:]
            ready=self.group_events[g]-self.last_switch[g]>=6
            if self.kind=="candidate":
                flip=ready and len(self.evidence[g])==6 and (
                    sum(z>0 for z in self.evidence[g])>=3
                    and sum(self.evidence[g])>=4.0)
            elif self.kind=="random":
                h=hashlib.sha256(f"know37:random-gate:v1:{t}:{x}".encode()).digest()
                flip=ready and int.from_bytes(h[:8],"big")%32==0
            else:
                flip=False
            if flip:
                cur=1-cur
                self.active[g]=cur
                self.switches+=1
                self.last_switch[g]=self.group_events[g]
                self.evidence[g]=[]
        if self.seen[cur][x]<6:
            self.banks[cur][x].update(y,1.0)
            self.seen[cur][x]+=1
        self.group_events[g]+=1
        self.received+=1

    def state(self):
        return {
          "schema":"yggdrasil.know37.mem-state.dev.v1",
          "kind":self.kind,
          "banks":[[v.state() for v in bank] for bank in self.banks],
          "seen":self.seen,"active":self.active,"evidence":self.evidence,
          "group_events":self.group_events,"last_switch":self.last_switch,
          "received":self.received,"switches":self.switches,
          "original_source":False
        }

    def checkpoint(self):
        raw=canonical(self.state())
        require(len(raw)<4096,"CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls,raw,sha):
        require(type(raw) is bytes and len(raw)<4096 and digest(raw)==sha,
                "CHECKSUM")
        def unique(pairs):
            d={}
            for k,v in pairs:
                require(k not in d,"DUPLICATE")
                d[k]=v
            return d
        try:
            data=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(data) is dict and data.get("kind") in
                    ("candidate","random","no_switch"),"TYPE")
            m=cls(data["kind"])
            require(set(data)==set(m.state())
                    and data["schema"]==m.state()["schema"]
                    and data["original_source"] is False
                    and type(data["received"]) is int and 0<=data["received"]<=256
                    and type(data["switches"]) is int
                    and 0<=data["switches"]<=data["received"]
                    and type(data["active"]) is list and len(data["active"])==4
                    and all(type(x) is int and x in (0,1) for x in data["active"])
                    and type(data["group_events"]) is list
                    and len(data["group_events"])==4
                    and all(type(x) is int and 0<=x<=256
                            for x in data["group_events"])
                    and sum(data["group_events"])==data["received"]
                    and type(data["last_switch"]) is list
                    and len(data["last_switch"])==4
                    and all(type(x) is int and 0<=x<=n
                            for x,n in zip(data["last_switch"],data["group_events"]))
                    and type(data["evidence"]) is list
                    and len(data["evidence"])==4
                    and all(type(xs) is list and len(xs)<=6 and
                            all(type(v) in (int,float) and math.isfinite(v)
                                and -3<=v<=3 for v in xs)
                            for xs in data["evidence"]),"LAYOUT")
            require(type(data["banks"]) is list and len(data["banks"])==2
                    and type(data["seen"]) is list
                    and len(data["seen"])==2,"BANKS")
            for b in range(2):
                require(type(data["banks"][b]) is list
                        and len(data["banks"][b])==8
                        and type(data["seen"][b]) is list
                        and len(data["seen"][b])==8,"BANK_LEN")
                for x in range(8):
                    n=data["seen"][b][x]
                    require(type(n) is int and 0<=n<=6
                            and type(data["banks"][b][x]) is list
                            and len(data["banks"][b][x])==2,"CELL")
                    cell=Beta(*data["banks"][b][x])
                    require(cell.a+cell.b==2+n,"WITNESS_COUNT")
                    m.banks[b][x]=cell
            require(sum(map(sum,data["seen"]))<=data["received"],
                    "OBSERVATION_BUDGET")
            for name in ("seen","active","evidence","group_events",
                         "last_switch","received","switches"):
                setattr(m,name,data[name])
            require(m.checkpoint()==raw,"NONCANONICAL")
            return m
        except (KeyError,ValueError,TypeError,UnicodeError,OverflowError) as ex:
            raise ValueError("YGG_KNOW37_RESTORE_REJECTED") from ex

def cold(m):
    raw=m.checkpoint()
    if isinstance(m,Mem):
        out=Mem.restore(raw,digest(raw))
    elif isinstance(m,TwoBankCells):
        out=TwoBankCells.restore(raw,digest(raw))
    else:
        out=copy.deepcopy(m)
    require(out.checkpoint()==raw
            and [out.prob(x) for x in range(8)]==
                [m.prob(x) for x in range(8)],"COLD_READBACK")
    return out

def models(hazard):
    return {"candidate":Mem(),"hmm":Comparator("hmm",hazard),
            "random":Mem("random"),"no_switch":Mem("no_switch"),
            "old35":TwoBankCells(),"rolling":Comparator("rolling")}

def private_y(seed,t,law):
    require(os.environ.get("YGG_KNOW37_HELD_ONE_SHOT")=="1",
            "HELD_DENIED")
    require(type(seed) is int and type(t) is int and 0<=t<256
            and law in ("A","B1","B2"),"SOURCE")
    q=q_for(law,x_for(t))
    h=hashlib.sha256(
        f"know37:synthetic:noise:v1:{seed}:{t}:{law}".encode()).digest()
    return int(int.from_bytes(h[:8],"big")/(1<<64)<q)

def held_world(seed,family,hazard,witness=private_y):
    control=[witness(seed,t,"A") for t in range(256)]
    changed={t:witness(seed,t,family)
             for t in list(range(64,128))+list(range(192,256))}
    prefix=models(hazard)
    for t in range(64):
        for m in prefix.values():
            m.observe(t,x_for(t),control[t])
    prefix={name:cold(m) for name,m in prefix.items()}
    A_prefix=sum(brier(prefix["candidate"].prob(x),q_for("A",x))
                 for x in range(8))/8
    old_A=copy.deepcopy(prefix["candidate"].state()["banks"][0])
    result={}
    for branch in ("control_A","treatment_B"):
        ms={k:cold(v) for k,v in prefix.items()}
        stages={stage:{k:[] for k in ARMS}
                for stage in ("B_first","A_return","B_second")}
        initial_switch=ms["candidate"].switches
        kept_A=True
        bank_B_at_128=None
        bank_B_at_192=None
        for t in range(64,256):
            stage="B_first" if t<128 else ("A_return" if t<192 else "B_second")
            law=family if branch=="treatment_B" and stage!="A_return" else "A"
            y=changed[t] if law==family else control[t]
            x=x_for(t)
            for name,m in ms.items():
                stages[stage][name].append(brier(m.prob(x),q_for(law,x)))
                m.observe(t,x,y)
            if t+1 in (128,192,256):
                ms={k:cold(v) for k,v in ms.items()}
                if branch=="treatment_B":
                    kept_A&=ms["candidate"].state()["banks"][0]==old_A
                    if t+1==128:
                        bank_B_at_128=copy.deepcopy(ms["candidate"].state()["banks"][1])
                    if t+1==192:
                        bank_B_at_192=copy.deepcopy(ms["candidate"].state()["banks"][1])
        require(all(m.received==256 for m in ms.values()),"MODEL_EVENTS")
        result[branch]={
           "scores":{stage:{k:sum(v)/64 for k,v in d.items()}
                     for stage,d in stages.items()},
           "switches":ms["candidate"].switches-initial_switch,
           "bytes":{k:len(v.checkpoint()) for k,v in ms.items()}
        }
    return {
       "seed":seed,"family":family,"A_prefix":A_prefix,
       "scores":result["treatment_B"]["scores"],
       "A_retained":kept_A,
       "B_retained":bank_B_at_128==bank_B_at_192,
       "sham_false_switch":result["control_A"]["switches"]>0,
       "bytes":result["treatment_B"]["bytes"],
       "source_calls":384,"model_events_per_arm":448,
    }

def proof():
    require(os.environ.get("YGG_KNOW37_HELD_ONE_SHOT")=="1",
            "FIRST_USE_DENIED")
    p=protocol()
    for start in range(0,256,16):
        cells=[x_for(t) for t in range(start,start+16)]
        require(all(cells.count(x)==2 for x in range(8)),
                "PUBLIC_SUPPORT")
    hazard,fit_scores=fit_hazard(
        {"source":{"fit_seeds":p["source"]["fit"]}},witness=private_y)
    worlds=[held_world(seed,family,hazard) for family in ("B1","B2")
            for seed in p["source"]["held"][family]]
    require(len(worlds)==24 and sum(w["source_calls"] for w in worlds)==9216
            and all(w["model_events_per_arm"]==448 for w in worlds),
            "SOURCE_COUNTS")
    families={}
    for family in ("B1","B2"):
        rows=[w for w in worlds if w["family"]==family]
        stages={stage:{name:sum(w["scores"][stage][name] for w in rows)/12
                        for name in ARMS}
                for stage in ("B_first","A_return","B_second")}
        families[family]={
           "A_prefix":sum(w["A_prefix"] for w in rows)/12,
           "scores":stages,
           "paired_wins_vs_hmm":sum(
               w["scores"]["B_second"]["candidate"]<
               w["scores"]["B_second"]["hmm"] for w in rows)
        }
    F=families
    H={
      "P0":len(worlds)==24,
      "P1":all(F[f]["A_prefix"]<=.23 for f in ("B1","B2")),
      "H1":all(F[f]["scores"]["B_second"]["candidate"]<=
               F[f]["scores"]["B_second"]["hmm"]-.005
               and F[f]["paired_wins_vs_hmm"]>=9 for f in ("B1","B2")),
      "H2":all(F[f]["scores"]["B_second"]["candidate"]<=
               F[f]["scores"]["B_second"]["random"]-.005
               and F[f]["scores"]["B_second"]["candidate"]<=
                   F[f]["scores"]["B_second"]["no_switch"]-.005
               for f in ("B1","B2")),
      "H3":all(F[f]["scores"]["A_return"]["candidate"]<=
               F[f]["scores"]["A_return"]["hmm"]+.005
               for f in ("B1","B2")),
      "H4":all(w["A_retained"] and w["B_retained"] for w in worlds),
      "H5":sum(w["sham_false_switch"] for w in worlds)<=2 and
               all(w["bytes"]["candidate"]<4096 for w in worlds),
    }
    return {
       "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTOCOL_BLOB,
       "fit_worlds":12,"held_worlds":24,"fit_source_calls":3072,
       "held_unique_source_events":9216,"model_events_per_arm":10752,
       "selected_hmm_hazard":hazard,"fit_hmm_briers":fit_scores,
       "families":families,"frozen_hypotheses":H,
       "sham_false_switch_worlds":sum(w["sham_false_switch"] for w in worlds),
       "A_retained_worlds":sum(w["A_retained"] for w in worlds),
       "B_retained_worlds":sum(w["B_retained"] for w in worlds),
       "worlds":worlds,
       "development_verdict":"DEVELOPMENT_SUPPORTED" if all(H.values()) else "DEVELOPMENT_MIXED_OR_NO_GO",
       "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
       "protected_original_world_first_use":False,
       "native_model_changed":False,"deployment":"NONE",
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
