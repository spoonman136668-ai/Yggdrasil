"""DG1-SL07: contradiction-gated, *paid* causal interventions.

Frozen preregistration: 27d0ad88fdb64dda815cfb248cf47faf8b2f8e5a.
Seven arms, four disjoint 8-world cohorts, isolated non-token source-only DEV.
All learning comes from real paid causal actions. Hidden world, regime, seed and
evaluator audits are never inputs to any learner or action-selection policy.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = "27d0ad88fdb64dda815cfb248cf47faf8b2f8e5a"
PARENT = "30f57be961c15915fd1ad1d58f2d39cadf93d581"
SCHEMA = "ygg.dg1-sl07.contradiction-gated-intervention.v1"
COHORTS = {
    "ABCA": tuple(range(100101, 100109)),
    "ABCB": tuple(range(100109, 100117)),
    "STABLE": tuple(range(100117, 100125)),
    "ABCD_OOD": tuple(range(100125, 100133)),
}
ARMS = ("native_witness","native_always","native_passive","native_sham",
        "native_witness_no_gate","conventional_witness","conventional_always")
FLIPS = (6,14,22,30,38,46,54,62,70,78)
AUDITS = (60,64,72,80)

def load(name,relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

sl06=load("sl07_frozen_sl06","dg1-sl06-20261113/sl06.py")
sl05=sl06.sl05
native=sl05.native
conventional=sl05.control

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")

class World(sl06.World):
    """SL06 physics exactly, registered to SL07 prospective disjoint seeds."""
    def __init__(self,seed,group):
        if group not in COHORTS or seed not in COHORTS[group]:
            raise ValueError("SL07_UNREGISTERED_WORLD")
        self.seed=seed
        self.group="STATIONARY" if group=="STABLE" else group
        self.paid=0
        self.rules=[[0]*4 for _ in range(3)]
        for action in range(4):
            used=set()
            for phase in range(3):
                r=random.Random(seed*131+phase*719+action*47)
                h=r.randrange(40)
                while h in used:
                    h=(h+1)%40
                used.add(h)
                self.rules[phase][action]=h

    # SL06.World.step is unchanged, except registration and public seed range.

def bank_unanimity(mask,state,family):
    counts=(native.counts if family=="native" else conventional.posterior_counts)
    z,o=counts(mask,state)
    return (0 if z and not o else 1 if o and not z else None)

def contradiction(model,before,action,after,family):
    """Evidence is a PRE-UPDATE paid physical observation, no prediction oracle."""
    native.valid_state(before);native.valid_action(action);native.valid_state(after)
    if after not in (before,before^(1<<action)):
        raise ValueError("SL07_NONLOCAL_PHYSICAL_EVENT")
    banks=model.banks
    active=model.active
    if not 0<=active<len(banks):
        raise ValueError("SL07_BAD_ACTIVE_BANK")
    active_pred=bank_unanimity(banks[active][action],before,family)
    observed=int(after!=before)
    if active_pred is None or active_pred==observed:
        return False
    return any(bank_unanimity(bank[action],before,family)==observed
               for i,bank in enumerate(banks) if i!=active)

def intervention_action(arm,model,state):
    if arm.startswith("conventional_"):
        return sl06.conventional_information_action(model,state)
    return sl06.native_information_action(model,state)

def learner_for(arm):
    if arm not in ARMS:raise ValueError("SL07_UNKNOWN_ARM")
    if arm.startswith("native_"):
        return sl05.ColdThreeBank(gate=arm!="native_witness_no_gate",evict=False)
    return sl05.ConventionalHMM3(replay=True)

def restore_learner(arm,raw):
    if arm.startswith("native_"):
        m=sl05.ColdThreeBank.restore(raw)
        if m.evict or m.gate!=(arm!="native_witness_no_gate"):
            raise ValueError("SL07_INNER_ARM_MODE")
        return m
    m=sl05.ConventionalHMM3.restore(raw)
    if not m.replay:raise ValueError("SL07_CONVENTIONAL_MODE")
    return m

class Agent:
    """Bounded witness window and original, frozen memory model."""
    def __init__(self,arm):
        self.arm=arm
        self.model=learner_for(arm)
        self.family="control" if arm.startswith("conventional_") else "native"
        self.recent=[]
        self.armed=0
        self.armings=0
        self.active_choices=0
        self.meaningful_witness_events=0
        self.causal_events=0
        self.decisions=0

    def predict(self,state,action):
        return self.model.predict(state,action)

    def choose(self,state,step):
        native.valid_state(state)
        if type(step) is not int or not 60<=step<80 or step in FLIPS:
            raise ValueError("SL07_NOT_CHARGED_CAUSAL_STEP")
        self.decisions+=1
        if self.arm in ("native_always","conventional_always"):
            self.active_choices+=1
            return intervention_action(self.arm,self.model,state)
        if self.arm in ("native_passive",):
            return step%4
        if self.armed:
            self.active_choices+=1
            return intervention_action(self.arm,self.model,state)
        return step%4

    def observe(self,before,action,after,step):
        # Public physical step is the only scheduling input; not a regime label.
        if type(step) is not int or not 0<=step<80 or step in FLIPS:
            raise ValueError("SL07_NOT_A_CAUSAL_OBSERVATION")
        native.valid_state(before);native.valid_action(action);native.valid_state(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("SL07_NONLOCAL_OBSERVATION")
        useful=contradiction(self.model,before,action,after,self.family)
        self.meaningful_witness_events+=int(useful)
        self.causal_events+=1
        if self.arm=="native_sham":
            witness_kind=not useful
        else:
            witness_kind=useful
        # Deterministic window of last 12 *causal* events; distinct physical
        # (state,action) pairs only, not many repeats of the same contradiction.
        self.recent.append([before,action,int(witness_kind)])
        self.recent=self.recent[-12:]
        started_armed=self.armed>0
        self.model.observe(before,action,after)
        if step>=60 and started_armed:
            self.armed-=1
        if (step>=60 and not started_armed and self.armed==0
            and self.arm not in ("native_always","native_passive","conventional_always")):
            pairs={(s,a) for s,a,flag in self.recent if flag}
            if len(pairs)>=2:
                self.armings+=1
                self.armed=4
                self.recent=[]
        # No model training from dreams, evaluator audits or invented outcomes.

    def rest(self):
        self.model.rest()

    def snapshot(self):
        p={"schema":SCHEMA,"arm":self.arm,
           "inner":self.model.snapshot().decode("ascii"),
           "recent":self.recent,"armed":self.armed,"armings":self.armings,
           "active_choices":self.active_choices,
           "meaningful_witness_events":self.meaningful_witness_events,
           "causal_events":self.causal_events,"decisions":self.decisions}
        raw=canonical({"payload":p,"sha256":hashlib.sha256(canonical(p)).hexdigest()})
        if len(raw)>8192:
            raise ValueError("SL07_CHECKPOINT_OVERSIZE")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=8192:
                raise ValueError("SL07_BAD_BYTES")
            val=json.loads(raw)
            if type(val) is not dict or set(val)!={"payload","sha256"}:
                raise ValueError("SL07_BAD_WRAPPER")
            p=val["payload"]
            required={"schema","arm","inner","recent","armed","armings",
                      "active_choices","meaningful_witness_events",
                      "causal_events","decisions"}
            if type(p) is not dict or set(p)!=required or p["schema"]!=SCHEMA:
                raise ValueError("SL07_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest()!=val["sha256"]:
                raise ValueError("SL07_BAD_HASH")
            if p["arm"] not in ARMS or type(p["inner"]) is not str:
                raise ValueError("SL07_BAD_MODEL")
            recent=p["recent"]
            if type(recent) is not list or len(recent)>12 or any(
                type(e) is not list or len(e)!=3 or
                type(e[0]) is not int or not 0<=e[0]<16 or
                type(e[1]) is not int or not 0<=e[1]<4 or
                type(e[2]) is not int or e[2] not in (0,1) for e in recent):
                raise ValueError("SL07_BAD_RECENT_EVENTS")
            for name in ("armed","armings","active_choices",
                         "meaningful_witness_events","causal_events","decisions"):
                if type(p[name]) is not int or not 0<=p[name]<=80:
                    raise ValueError("SL07_BAD_COUNTER")
            if p["armed"]>4 or p["active_choices"]>p["decisions"]:
                raise ValueError("SL07_BAD_RELATION")
            out=cls(p["arm"])
            out.model=restore_learner(p["arm"],p["inner"].encode("ascii"))
            for name in ("recent","armed","armings","active_choices",
                         "meaningful_witness_events","causal_events","decisions"):
                setattr(out,name,p[name])
            if out.snapshot()!=raw:
                raise ValueError("SL07_NOT_CANONICAL")
            return out
        except (TypeError,ValueError,KeyError,OverflowError,UnicodeError) as e:
            raise ValueError("SL07_INVALID_CHECKPOINT") from e

def evaluate(agent,world,seen,point):
    out={name:0 for name in ("correct","wrong_confident","abstained",
                             "unseen_correct","unseen_wrong_confident",
                             "unseen_abstained")}
    for state in range(16):
        for action in range(4):
            ground=world.audit_truth(state,action,point)
            got=agent.predict(state,action)
            k="abstained" if got is None else "correct" if got==ground else "wrong_confident"
            out[k]+=1
            if (state,action) not in seen:out["unseen_"+k]+=1
    return out

def one_world(seed,group):
    out={}
    common={}
    for arm in ARMS:
        world=World(seed,group)
        agent=Agent(arm)
        physical_state=seed%16
        seen=set()
        ledger=[]
        prequential={"correct":0,"wrong_confident":0,"abstained":0}
        after_cold={"correct":0,"wrong_confident":0,"abstained":0}
        costs={"decision_observation_rest_ns":0}
        checkpoints={}
        stage_audits={}
        for step in range(80):
            if step==60:
                raw=agent.snapshot()
                restored=Agent.restore(raw)
                if (raw!=restored.snapshot() or
                    any(agent.predict(s,a)!=restored.predict(s,a)
                        for s in range(16) for a in range(4)) or
                    agent.armed!=restored.armed or
                    agent.armings!=restored.armings):
                    raise AssertionError("SL07_COLD_RESTORE_MISMATCH")
                checkpoints["60"]=len(raw)
                agent=restored
            started=time.perf_counter_ns()
            choice=agent.choose(physical_state,step) \
                   if step>=60 and step not in FLIPS else None
            kind,action,next_state=world.step(physical_state,step,choice)
            if kind=="causal":
                got=agent.predict(physical_state,action)
                verdict=("abstained" if got is None else
                         "correct" if got==next_state else "wrong_confident")
                prequential[verdict]+=1
                if step>=60:after_cold[verdict]+=1
                agent.observe(physical_state,action,next_state,step)
                seen.add((physical_state,action))
            costs["decision_observation_rest_ns"]+=time.perf_counter_ns()-started
            ledger.append([physical_state,kind,action,next_state])
            physical_state=next_state
            if (step+1)%8==0:
                started=time.perf_counter_ns()
                agent.rest()
                costs["decision_observation_rest_ns"]+=time.perf_counter_ns()-started
            if step+1 in AUDITS:
                stage_audits[str(step+1)]=evaluate(agent,world,seen,step+1)
        raw=agent.snapshot()
        retest=Agent.restore(raw)
        if raw!=retest.snapshot() or any(agent.predict(s,a)!=retest.predict(s,a)
                                        for s in range(16) for a in range(4)):
            raise AssertionError("SL07_FINAL_SNAPSHOT_DIVERGED")
        checkpoints["80"]=len(raw)
        if world.paid!=80 or sum(row[1]=="flip" for row in ledger)!=10:
            raise AssertionError("SL07_PHYSICAL_BUDGET_MISMATCH")
        common[arm]=hashlib.sha256(canonical(ledger[:60])).hexdigest()
        out[arm]={
            "charged_physical_actions":world.paid,
            "paid_flips":10,"causal_observations":70,
            "pre_cold_trajectory_sha256":common[arm],
            "full_trajectory_sha256":hashlib.sha256(canonical(ledger)).hexdigest(),
            "post_cold_actions":[r[2] for r in ledger[60:] if r[1]=="causal"],
            "cold_restore_pass":True,
            "checkpoint_bytes":checkpoints,
            "physical_final_state":physical_state,
            "prequential":prequential,"post_cold_prequential":after_cold,
            "stage_audits":stage_audits,
            "witness_events":agent.meaningful_witness_events,
            "intervention_armings":agent.armings,
            "selected_active_actions":agent.active_choices,
            "cpu_ns":costs["decision_observation_rest_ns"]
        }
    if len(set(common.values()))!=1:
        raise AssertionError("SL07_PRE_COLD_PHYSICAL_TRAJECTORY_DRIFT")
    return {"seed":seed,"group":group,
            "shared_pre_cold_trace_sha256":next(iter(common.values())),
            "arms":out}

def run():
    worlds=[one_world(seed,group) for group,ss in COHORTS.items() for seed in ss]
    keys=("correct","wrong_confident","abstained","unseen_correct",
          "unseen_wrong_confident","unseen_abstained")
    agg={group:{arm:{k:sum(w["arms"][arm]["stage_audits"]["80"][k]
                           for w in worlds if w["group"]==group)
                      for k in keys} for arm in ARMS} for group in COHORTS}
    base=("native_always","native_passive","native_sham",
          "conventional_witness","conventional_always")
    reference={group:{
        "correct":max(agg[group][arm]["correct"] for arm in base),
        "unseen_correct":max(agg[group][arm]["unseen_correct"] for arm in base),
        "wrong_confident":min(agg[group][arm]["wrong_confident"] for arm in base)
    } for group in COHORTS}
    firing={group:sum(1 for w in worlds if w["group"]==group and
                      w["arms"]["native_witness"]["intervention_armings"]>0)
            for group in COHORTS}
    n="native_witness"
    x,y,st,ood=(agg[g][n] for g in ("ABCA","ABCB","STABLE","ABCD_OOD"))
    primary=(x["correct"]>=reference["ABCA"]["correct"]+16 and
             x["unseen_correct"]>=reference["ABCA"]["unseen_correct"]+8 and
             x["wrong_confident"]<=reference["ABCA"]["wrong_confident"]+4 and
             y["correct"]>=reference["ABCB"]["correct"]+16 and
             y["unseen_correct"]>=reference["ABCB"]["unseen_correct"]+8 and
             y["wrong_confident"]<=reference["ABCB"]["wrong_confident"]+4 and
             st["correct"]>=reference["STABLE"]["correct"]-16 and
             st["wrong_confident"]<=reference["STABLE"]["wrong_confident"]+4 and
             ood["wrong_confident"]<=reference["ABCD_OOD"]["wrong_confident"]+4 and
             firing["ABCA"]>=4 and firing["ABCB"]>=4)
    mixed=(x["correct"]>reference["ABCA"]["correct"] and
           y["correct"]>reference["ABCB"]["correct"])
    classification=("DEV_SIGNAL_NOT_SCIENCE" if primary else
                    "MIXED_DEV" if mixed else "NEGATIVE_DEV")
    return {
        "schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
        "classification":classification,"primary_pass":primary,
        "scientific_acceptance":"UNVERIFIED",
        "same_paid_steps_not_same_information_after_60":True,
        "native_advantage_established":False,"sleep_timing_gain_established":False,
        "world_count":len(worlds),
        "physical_actions_all_arms":sum(v["charged_physical_actions"]
                        for w in worlds for v in w["arms"].values()),
        "causal_observations_all_arms":sum(v["causal_observations"]
                        for w in worlds for v in w["arms"].values()),
        "witness_triggered_worlds":firing,
        "control_envelope":reference,"aggregate_final":agg,"worlds":worlds
    }
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,separators=(",",":")))
