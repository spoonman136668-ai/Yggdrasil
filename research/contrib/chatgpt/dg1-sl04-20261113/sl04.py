"""SL04 frozen selective-consolidation transfer challenge.

Independent HMM-style and recent-window controls. All arms see the same 64
charged physical actions. Frozen SL03 implementation is imported unchanged.
No oracle/audit answers, hidden phases or dream transitions enter training.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import random
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PARENT_SHA = "dacb637b034189029d6b22a885c63d520aedf1fd"
SEAL = "7ca7da2595727ebf719d77c51c1c97be7c9d892c"
SEEDS = {"ABA":range(96001,96009),"ABC_capacity":range(96009,96017),
         "OOD_cubic":range(96017,96025)}
ARMS = ("frozen_sl03_selective_sleep","sl03_native_no_sleep",
        "sl03_conventional_selective","sl03_online_same_compute",
        "conventional_hmm_masks","conventional_recent_window")
M = (1 << 40) - 1
FLIPS = (5,13,21,29,37,45,53,61)
SCHEMA = "ygg.dg1-sl04.baseline-checkpoint.v1"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, BASE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

sl03 = load("sl04_frozen_sl03", "dg1-sl03-20261113/sl03.py")
conv = sl03.conventional
native = sl03.native

def encode(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")

def checked_event(before, action, after):
    native.valid_state(before)
    native.valid_action(action)
    native.valid_state(after)
    if after not in (before, before ^ (1 << action)):
        raise ValueError("SL04_NONLOCAL_EVENT")
    return [before, action, after]

def surviving(mask, before, effect):
    return sum(1 << h for h in range(40)
               if mask & (1 << h) and conv.eval_rule(before,h) == effect)

def counts(mask, state):
    return conv.posterior_counts(mask,state) if mask else (0,0)

def prediction(mask, state, action):
    n0,n1=counts(mask,state)
    if not n0 and not n1 or n0 and n1:
        return None
    return state ^ (int(bool(n1)) << action)

class PhysicalWorld:
    def __init__(self, seed, group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("SL04_UNREGISTERED_WORLD")
        self.seed,self.group,self.paid=seed,group,0
        self.sign=[];self.slope=[];self.csign=[]
        for a in range(4):
            r=random.Random(seed*101+a*31)
            self.sign.append(r.randrange(2));self.slope.append(r.randrange(2))
            c=random.Random(seed*307+a*59)
            self.csign.append(c.randrange(2))
    def phase(self, step):
        if self.group=="ABA":
            return "B" if 20<=step<40 else "A"
        if self.group=="ABC_capacity":
            return "A" if step<20 else "B" if step<40 else "C"
        return "OOD"
    def true_next_evaluator_only(self, state, action, phase):
        native.valid_state(state);native.valid_action(action)
        if phase not in ("A","B","C","OOD"):
            raise ValueError("BAD_PHASE")
        left=(state >> ((action+1)%4)) & 1
        right=(state >> ((action+2)%4)) & 1
        own=(state >> action)&1
        if phase=="OOD":
            bit=int(state==15)^self.sign[action]
        elif phase=="C":
            bit=((left^own) if action%2==0 else int(left+right+own>=2))^self.csign[action]
        else:
            bit=left^right^(own&self.slope[action])^self.sign[action]
            if phase=="B":
                bit^=1
        return state ^ (bit << action)
    def step(self, state, step):
        if not (0<=step<64) or step!=self.paid:
            raise ValueError("SL04_UNCHARGED_ACTION")
        self.paid+=1
        if step in FLIPS:
            bit=(self.seed//4+step//8)%4
            return ("flip",bit,state^(1<<bit))
        action=(self.seed+step)%4
        return ("causal",action,self.true_next_evaluator_only(state,action,self.phase(step)))
    def audit_truth(self, state, action, point):
        if point not in (20,40,64):
            raise ValueError("SL04_AUDIT_PHASE")
        return self.true_next_evaluator_only(state,action,self.phase(point-1))

class BayesianTwoBank:
    """Separate conventional 2-regime hazard filter over Boolean version spaces.

    Masks: 320 logical hypothesis bits. Two continuous confidence scores are
    ADDITIONAL state; this is an HMM-style approximation, not full BOCPD.
    """
    def __init__(self):
        self.banks=[[M]*4]
        self.weights=[1.0]
        self.active=0
        self.unresolved=False
        self.observations=0
        self.switches=0
        self.events=[]
    def predict(self, state, action):
        native.valid_state(state);native.valid_action(action)
        if self.unresolved or self.weights[self.active]<0.60:
            return None
        return prediction(self.banks[self.active][action],state,action)
    def observe(self,before,action,after):
        event=checked_event(before,action,after)
        observed=int(before != after)
        self.events.append(event)
        self.events=self.events[-48:]
        prior=(self.weights[:] if len(self.banks)==1 else
               [(15*self.weights[0]+self.weights[1])/16,
                (15*self.weights[1]+self.weights[0])/16])
        options=[]
        emissions=[]
        for bank in self.banks:
            mask=bank[action]
            next_mask=surviving(mask,before,observed)
            options.append(next_mask)
            n=mask.bit_count()
            emissions.append((next_mask.bit_count()+1)/(n+2) if next_mask else 0)
        if not any(options) and len(self.banks)==1:
            self.banks.append([M]*4)
            self.weights=[0.01,0.99]
            prior=[0.01,0.99]
            options.append(surviving(M,before,observed))
            emissions.append((options[1].bit_count()+1)/42)
        if not any(options):
            self.unresolved=True
            self.observations+=1
            return
        scores=[prior[i]*emissions[i] for i in range(len(options))]
        total=sum(scores)
        self.weights=[v/total for v in scores]
        selected=max(range(len(options)),key=lambda i:(self.weights[i],-i))
        if selected!=self.active:self.switches+=1
        self.active=selected
        self.banks[selected][action]=options[selected]
        self.unresolved=False
        self.observations+=1
    def rest(self):
        pass
    def snapshot(self):
        body={"schema":SCHEMA,"kind":"hmm","banks":self.banks,
              "weights":self.weights,"active":self.active,"unresolved":self.unresolved,
              "observations":self.observations,"switches":self.switches,"events":self.events}
        return seal(body)

class RecentWindow:
    """Independent fixed-window conventional rule fit; zero mask = abstain."""
    def __init__(self):
        self.events=[]
        self.masks=[M]*4
        self.observations=0
    def predict(self,state,action):
        native.valid_state(state);native.valid_action(action)
        return prediction(self.masks[action],state,action)
    def observe(self,before,action,after):
        self.events.append(checked_event(before,action,after))
        self.events=self.events[-48:]
        self.observations+=1
        for a in range(4):
            relevant=[e for e in self.events if e[1]==a][-12:]
            mask=M
            for s,_,n in relevant:
                mask=surviving(mask,s,int(s!=n))
            self.masks[a]=mask
    def rest(self):
        pass
    def snapshot(self):
        return seal({"schema":SCHEMA,"kind":"recent","events":self.events,
                     "masks":self.masks,"observations":self.observations})

def seal(body):
    out=encode({"payload":body,"sha256":hashlib.sha256(encode(body)).hexdigest()})
    if len(out)>8192:
        raise ValueError("SL04_OVERSIZE_CHECKPOINT")
    return out

def restore_control(data):
    try:
        if type(data) is not bytes or not 0<len(data)<=8192:
            raise ValueError("SL04_SNAPSHOT_TYPE")
        env=json.loads(data)
        if type(env) is not dict or set(env)!={"payload","sha256"}:
            raise ValueError("SL04_ENVELOPE")
        body=env["payload"]
        if type(body) is not dict or body.get("schema")!=SCHEMA or \
           env["sha256"]!=hashlib.sha256(encode(body)).hexdigest():
            raise ValueError("SL04_CUSTODY")
        kind=body["kind"]
        if kind=="hmm":
            expected={"schema","kind","banks","weights","active","unresolved",
                      "observations","switches","events"}
            if set(body)!=expected:
                raise ValueError("SL04_FIELDS")
            banks=body["banks"];weights=body["weights"];active=body["active"]
            if (type(banks) is not list or not 1<=len(banks)<=2 or
                any(type(bank) is not list or len(bank)!=4 or
                any(type(v) is not int or not 0<v<=M for v in bank) for bank in banks)
                or type(weights) is not list or len(weights)!=len(banks)
                or any(type(w) not in (float,int) or not 0<=w<=1 for w in weights)
                or abs(sum(weights)-1)>1e-10 or
                type(active) is not int or not 0<=active<len(banks)
                or type(body["unresolved"]) is not bool
                or type(body["switches"]) is not int or body["switches"]<0):
                raise ValueError("SL04_BANKS")
            out=BayesianTwoBank()
            out.banks=[bank[:] for bank in banks]
            out.weights=weights[:];out.active=active
            out.unresolved=body["unresolved"];out.switches=body["switches"]
        elif kind=="recent":
            if set(body)!={"schema","kind","events","masks","observations"}:
                raise ValueError("SL04_RECENT_SCHEMA")
            masks=body["masks"]
            if type(masks) is not list or len(masks)!=4 or any(
                type(x) is not int or not 0<=x<=M for x in masks):
                raise ValueError("SL04_RECENT_MASKS")
            out=RecentWindow()
            out.masks=masks[:]
        else:
            raise ValueError("SL04_UNKNOWN_KIND")
        events=body["events"]
        if type(events) is not list or len(events)>48:
            raise ValueError("SL04_BAD_EVENTS")
        for e in events:
            if type(e) is not list or len(e)!=3:
                raise ValueError("SL04_BAD_EVENT")
            checked_event(*e)
        count=body["observations"]
        if type(count) is not int or not 0<=count<=64 or count<len(events):
            raise ValueError("SL04_BAD_OBSERVATIONS")
        out.events=[e[:] for e in events]
        out.observations=count
        if out.snapshot()!=data:
            raise ValueError("SL04_NONCANONICAL")
        return out
    except (TypeError,ValueError,OverflowError,KeyError,UnicodeError):
        raise ValueError("SL04_BAD_SNAPSHOT") from None

def new_learner(arm):
    return {
        "frozen_sl03_selective_sleep":lambda:sl03.Learner("selective_sleep"),
        "sl03_native_no_sleep":lambda:sl03.Learner("native_no_sleep"),
        "sl03_conventional_selective":lambda:sl03.Learner("conventional_selective_sleep"),
        "sl03_online_same_compute":lambda:sl03.Learner("online_same_compute"),
        "conventional_hmm_masks":BayesianTwoBank,
        "conventional_recent_window":RecentWindow
    }[arm]()

def audit(agent,world,seen,point):
    out={k:0 for k in ("correct","wrong_confident","abstained",
                       "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for action in range(4):
            truth=world.audit_truth(state,action,point)
            got=agent.predict(state,action)
            k="abstained" if got is None else "correct" if got==truth else "wrong_confident"
            out[k]+=1
            if (state,action) not in seen:
                out["unseen_"+k]+=1
    return out

def one_world(seed,group):
    world=PhysicalWorld(seed,group)
    agents={arm:new_learner(arm) for arm in ARMS}
    times_ns={arm:0 for arm in ARMS}
    seen=set()
    state=seed%16
    ledger=[]
    prequential={arm:{"correct":0,"wrong_confident":0,"abstained":0} for arm in ARMS}
    checks={arm:{} for arm in ARMS}
    for step in range(64):
        before=state
        kind,action,after=world.step(state,step)
        if kind=="causal":
            seen.add((before,action))
            for arm,agent in agents.items():
                t0=time.perf_counter_ns()
                got=agent.predict(before,action)
                prequential[arm]["abstained" if got is None else
                               "correct" if got==after else "wrong_confident"]+=1
                agent.observe(before,action,after)
                times_ns[arm]+=time.perf_counter_ns()-t0
        state=after
        ledger.append([before,kind,action,after])
        if (step+1)%8==0:
            for arm,agent in agents.items():
                t0=time.perf_counter_ns()
                agent.rest()
                times_ns[arm]+=time.perf_counter_ns()-t0
        if step+1 in (20,40,64):
            for arm,agent in agents.items():
                checks[arm][str(step+1)]=audit(agent,world,seen,step+1)
    if world.paid!=64 or sum(e[1]=="flip" for e in ledger)!=8:
        raise AssertionError("SL04_BUDGET_MISMATCH")
    lengths={}
    for arm,agent in agents.items():
        snap=agent.snapshot()
        cold=(sl03.Learner.restore(snap) if arm.startswith(("frozen_","sl03_"))
              else restore_control(snap))
        if cold.snapshot()!=snap or any(agent.predict(s,a)!=cold.predict(s,a)
                                        for s in range(16) for a in range(4)):
            raise AssertionError("SL04_COLD_RETENTION")
        lengths[arm]=len(snap)
        if len(snap)>8192:
            raise AssertionError("SL04_CAPACITY")
    return {"seed":seed,"group":group,"physical_actions":world.paid,
            "mechanism_observations":56,"paid_flips":8,
            "physical_ledger_sha256":hashlib.sha256(encode(ledger)).hexdigest(),
            "prequential":prequential,"audits":checks,
            "cold_restore_identical":True,"snapshot_bytes":lengths,
            "whole_inference_update_ns":times_ns}

def run():
    worlds=[one_world(seed,group) for group,seeds in SEEDS.items() for seed in seeds]
    keys=("correct","wrong_confident","abstained","unseen_correct",
          "unseen_wrong_confident","unseen_abstained")
    agg={group:{arm:{k:sum(w["audits"][arm]["64"][k] for w in worlds if w["group"]==group)
                         for k in keys} for arm in ARMS} for group in SEEDS}
    candidate=agg["ABA"]["frozen_sl03_selective_sleep"]
    controls=("sl03_conventional_selective","conventional_hmm_masks","conventional_recent_window")
    floor={group:{k:(max if k in ("correct","unseen_correct") else min)
                  (agg[group][arm][k] for arm in controls)
                  for k in ("correct","unseen_correct","wrong_confident")}
           for group in SEEDS}
    ok=(candidate["correct"]-floor["ABA"]["correct"]>=24 and
        candidate["unseen_correct"]-floor["ABA"]["unseen_correct"]>=16 and
        candidate["wrong_confident"]<=floor["ABA"]["wrong_confident"]+4 and
        agg["ABC_capacity"]["frozen_sl03_selective_sleep"]["wrong_confident"]
        <=floor["ABC_capacity"]["wrong_confident"]+4 and
        agg["OOD_cubic"]["frozen_sl03_selective_sleep"]["wrong_confident"]
        <=floor["OOD_cubic"]["wrong_confident"]+4)
    gain=candidate["correct"]>floor["ABA"]["correct"] or \
         candidate["unseen_correct"]>floor["ABA"]["unseen_correct"]
    native_tie=all(agg[g]["frozen_sl03_selective_sleep"]==
                   agg[g]["sl03_conventional_selective"] for g in SEEDS)
    timing_tie=all(agg[g]["frozen_sl03_selective_sleep"]==
                   agg[g]["sl03_online_same_compute"] for g in SEEDS)
    return {"schema":"ygg.dg1-sl04.prospective-dev.v1","prereg_sha":SEAL,
            "source_parent_sha":PARENT_SHA,"classification":
            ("DEV_SIGNAL_NOT_SCIENCE" if ok else "MIXED_DEV" if gain else "NEGATIVE_DEV"),
            "primary_pass":ok,"scientific_acceptance":"UNVERIFIED",
            "strong_conventional_control_envelope":floor,
            "conventional_sl03_tie":native_tie,"online_same_compute_tie":timing_tie,
            "same_physical_actions":True,"same_total_compute":False,
            "charged_physical_actions":sum(w["physical_actions"] for w in worlds),
            "cohort_aggregates":agg,"worlds":worlds}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,separators=(",",":")))
