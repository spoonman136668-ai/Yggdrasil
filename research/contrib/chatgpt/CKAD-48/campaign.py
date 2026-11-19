"""CKAD48 — online state-dependent causal effect composition, tokenless.

Research-only 4-state/4-action native learner, not accepted Yggdrasil binary
NativeEpisodeExperience. All predictors train exclusively on genuine observed
two-transition, one-reward source episodes. Only the private simulator and
read-only examiner know the true state-dependent action operator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time

SCHEMA="yggdrasil.ckad48.state-conditioned-causal.v1"
PREREG="dba16e4e3a1c7f51ea18b45b15da84761de9e5ba"
DEV=(48111,48112)
PILOT=(48211,48212)
PRIMARY=(48311,48312,48313)
OLD=80
NOVEL_END=192
TOTAL=256
ALPHA=.25
TRANS_PROB=.90
ERROR_PROB=.10/3
PARTITIONS=("invariant","lowbit","highbit","parity")
ARMS=("state_partition_native","exact_structure_BMA","unrestricted_tabular",
      "false_XOR_invariant","uniform_sham")
PROBE_TIMES=(80,96,112,128,144,160,176,192,208,224,240)
PHASES={
  "early_novel":(80,96),
  "late_novel":(144,160,176),
  "cold_return":(192,208,224,240),
  "pooled_late_and_return":(144,160,176,192,208,224,240)}
MAX_EPISODES=TOTAL


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def sha256(value):
    if type(value) is not str:raise ValueError("CKAD48_DIGEST_TEXT")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def quad(value):
    if type(value) is not int or value not in (0,1,2,3):
        raise ValueError("CKAD48_QUAD")
    return value


def bit(value):
    if type(value) is not int or value not in (0,1):
        raise ValueError("CKAD48_BIT")
    return value


def group(which,state):
    s=quad(state)
    if which=="invariant":return 0
    if which=="lowbit":return s&1
    if which=="highbit":return (s>>1)&1
    if which=="parity":return (s&1)^((s>>1)&1)
    raise ValueError("CKAD48_UNKNOWN_RELATION")


def transition_probs(state,delta):
    correct=quad(state)^quad(delta)
    return tuple(TRANS_PROB if s==correct else ERROR_PROB for s in range(4))


def reward_true(world,state):
    s=quad(state)
    if world==0:return (s&1)^((s>>1)&1)
    if world==1:return (s&1)|((s>>1)&1)
    raise ValueError("CKAD48_WORLD_PRIVATE")


def private_true_action_effect(world,mapping,state,action):
    which="highbit" if world==0 else "parity"
    return mapping[group(which,state)][quad(action)]


def private_expected_reward(world,mapping,s0,a1,a2):
    """True physical simulator expectation. Never passed to a learner."""
    total=0.0
    for s1,p1 in enumerate(transition_probs(s0,private_true_action_effect(
        world,mapping,s0,a1))):
        for s2,p2 in enumerate(transition_probs(s1,private_true_action_effect(
            world,mapping,s1,a2))):
            chance=.9 if reward_true(world,s2) else .1
            total+=p1*p2*chance
    return total


def world_source(seed,world):
    if seed not in DEV and seed!=0:raise ValueError("CKAD48_ONLY_REGISTERED_DEV")
    if world not in (0,1):raise ValueError("CKAD48_WORLD_PRIVATE")
    rng=random.Random(int(sha256(f"ckad48-state-dependent-source|{seed}|{world}"),16))
    p=list(range(4));rng.shuffle(p)
    # A derangement: every action's physical effect really depends on the
    # public starting state class. The exact mapping is private.
    mapping=(tuple(p),tuple(p[(i+1)%4] for i in range(4)))
    rows=[]
    for t in range(TOTAL):
        s0=rng.randrange(4)
        pool=(0,1) if t<OLD or t>=NOVEL_END else (2,3)
        a1=rng.choice(pool)
        a2=rng.choice(pool)
        u1,u2,uy=rng.random(),rng.random(),rng.random()
        wrong1,wrong2=rng.randrange(3),rng.randrange(3)
        intended1=s0^private_true_action_effect(world,mapping,s0,a1)
        s1=intended1 if u1<TRANS_PROB else tuple(q for q in range(4) if q!=intended1)[wrong1]
        intended2=s1^private_true_action_effect(world,mapping,s1,a2)
        s2=intended2 if u2<TRANS_PROB else tuple(q for q in range(4) if q!=intended2)[wrong2]
        y=int(uy<(.9 if reward_true(world,s2) else .1))
        row={"s0":s0,"a1":a1,"s1":s1,"a2":a2,"s2":s2,"y":y}
        identifier=sha256(f"ckad48-public-real-source|{seed}|{world}|{t}")
        rows.append((identifier,row))
    return rows,{"world":world,"private_action_effect_mappings":mapping,
                 "private_state_partition":"highbit" if world==0 else "parity"}


def dirichlet(counts,category):
    x=counts[category]
    return (x+ALPHA)/(sum(counts)+4*ALPHA)


class NativeStateEffects:
    """One real source learner: 4 native state-group candidates retained.

    The exact structural BMA retains all posterior uncertainty. The proposed
    native gate uses the same SOURCE-TRAINED weights, but commits to the most
    supported mechanism only if the evidence posterior reaches >=0.90.
    """
    def __init__(self,mode):
        if mode not in ARMS[:4]:raise ValueError("CKAD48_UNKNOWN_LEARNER")
        self.mode=mode
        self.relations=[[[[0,0,0,0] for _ in range(2)]
                          for _ in range(4)] for _ in PARTITIONS]
        self.tabular=[[[0,0,0,0] for _ in range(4)] for _ in range(4)]
        self.invariant=[[0,0,0,0] for _ in range(4)]
        self.reward=[[0,0] for _ in range(4)]
        self.posterior=[.25]*4
        self.records={}
        self.source=[]
        self.n=0
        self.initial_80_sha=None

    def _transition_under(self,partition,state,action):
        counts=self.relations[partition][action][
            group(PARTITIONS[partition],state)]
        den=sum(counts)+4*ALPHA
        return tuple((counts[state^s]+ALPHA)/den for s in range(4))

    def transition(self,state,action):
        s,a=quad(state),quad(action)
        if self.mode=="unrestricted_tabular":
            counts=self.tabular[s][a]
            total=sum(counts)+4*ALPHA
            return tuple((v+ALPHA)/total for v in counts)
        if self.mode=="false_XOR_invariant":
            counts=self.invariant[a]
            total=sum(counts)+4*ALPHA
            return tuple((counts[s^dest]+ALPHA)/total for dest in range(4))
        mix=self._read_weights()
        return tuple(sum(weight*self._transition_under(i,s,a)[dest]
                         for i,weight in enumerate(mix)) for dest in range(4))

    def _read_weights(self):
        if self.mode=="state_partition_native":
            best=max(range(4),key=lambda i:self.posterior[i])
            if self.posterior[best]>=.90:
                return tuple(1.0 if i==best else 0.0 for i in range(4))
        return tuple(self.posterior)

    def predict_reward(self,state,first,second):
        s,a,b=quad(state),quad(first),quad(second)
        reward=tuple((pos+1)/(neg+pos+2) for neg,pos in self.reward)
        if self.mode in ("state_partition_native","exact_structure_BMA"):
            # Joint model averaging uses ONE partition across both actions.
            weights=self._read_weights()
            return sum(
                weight*sum(
                    p1*p2*reward[s2]
                    for s1,p1 in enumerate(self._transition_under(i,s,a))
                    for s2,p2 in enumerate(self._transition_under(i,s1,b)))
                for i,weight in enumerate(weights))
        return sum(
            p1*p2*reward[s2]
            for s1,p1 in enumerate(self.transition(s,a))
            for s2,p2 in enumerate(self.transition(s1,b)))

    def _learn_transition(self,state,action,observed):
        s,a,z=quad(state),quad(action),quad(observed)
        delta=s^z
        # Exact structure posterior from PREVIOUS source, before this row.
        updated=[weight*self._transition_under(i,s,a)[z]
                 for i,weight in enumerate(self.posterior)]
        total=sum(updated)
        if total<=0 or not math.isfinite(total):
            raise AssertionError("CKAD48_STRUCTURE_EVIDENCE_ZERO")
        self.posterior=[w/total for w in updated]
        for i,which in enumerate(PARTITIONS):
            self.relations[i][a][group(which,s)][delta]+=1
        self.tabular[s][a][z]+=1
        self.invariant[a][delta]+=1

    def observe(self,ident,row):
        if type(ident) is not str or len(ident)!=64 or any(ch not in
            "0123456789abcdef" for ch in ident):
            raise ValueError("CKAD48_SOURCE_ID")
        if type(row) is not dict or set(row)!={"s0","a1","s1","a2","s2","y"}:
            raise ValueError("CKAD48_SOURCE_ROW_SCHEMA")
        for key in ("s0","a1","s1","a2","s2"):
            quad(row[key])
        bit(row["y"])
        receipt=sha256(canonical(row))
        if ident in self.records:
            if self.records[ident]!=receipt:raise ValueError("CKAD48_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=MAX_EPISODES:raise ValueError("CKAD48_SOURCE_BUDGET")
        # All controls can have identical source-memory bookkeeping but
        # each is a separate trained model, with no cross-model weight reuse.
        self._learn_transition(row["s0"],row["a1"],row["s1"])
        self._learn_transition(row["s1"],row["a2"],row["s2"])
        self.reward[row["s2"]][row["y"]]+=1
        self.records[ident]=receipt
        self.source.append([ident,receipt])
        self.n+=1
        if self.n==OLD:self.initial_80_sha=sha256(canonical(self.source))
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"mode":self.mode,"relations":self.relations,
            "tabular":self.tabular,"invariant":self.invariant,"reward":self.reward,
            "posterior":self.posterior,"records":self.records,
            "source":self.source,"n":self.n,"initial80":self.initial_80_sha})

    @classmethod
    def restore(cls,raw,hash_value):
        if sha256(raw)!=hash_value:raise ValueError("CKAD48_CHECKPOINT_SHA")
        obj=json.loads(raw)
        if obj["schema"]!=SCHEMA:raise ValueError("CKAD48_CHECKPOINT_SCHEMA")
        m=cls(obj["mode"])
        for field in ("relations","tabular","invariant","reward","posterior",
                      "records","source","n"):
            setattr(m,field,obj[field])
        m.initial_80_sha=obj["initial80"]
        if m.n!=len(m.records) or m.n!=len(m.source) or m.n>MAX_EPISODES:
            raise ValueError("CKAD48_SOURCE_CUSTODY_BAD")
        if not math.isfinite(sum(m.posterior)) or abs(sum(m.posterior)-1)>1e-12:
            raise ValueError("CKAD48_STRUCTURE_POSTERIOR_INVALID")
        if m.n>=OLD and sha256(canonical(m.source[:OLD]))!=m.initial_80_sha:
            raise ValueError("CKAD48_OLD_SOURCE_NOT_RETAINED")
        if sum(sum(a) for a in m.reward)!=m.n:
            raise ValueError("CKAD48_REWARD_COUNT")
        if sum(sum(sum(a) for a in v) for v in m.tabular)!=2*m.n:
            raise ValueError("CKAD48_TRANSITION_SOURCE_COUNT")
        if m.checkpoint()!=raw:raise ValueError("CKAD48_COLD_ROUNDTRIP_CHANGED")
        return m

    def check_custody(self,last):
        raw=self.checkpoint()
        if NativeStateEffects.restore(raw,sha256(raw)).checkpoint()!=raw:
            raise AssertionError("CKAD48_EXACT_COLD")
        if self.n!=TOTAL or sha256(canonical(self.source[:OLD]))!=self.initial_80_sha:
            raise AssertionError("CKAD48_WITNESSED_SOURCE_INCOMPLETE")
        if self.observe(*last) is not self or self.checkpoint()!=raw:
            raise AssertionError("CKAD48_DUPLICATE_NOT_IDEMPOTENT")
        ident,row=last
        fake=dict(row,y=1-row["y"])
        try:self.observe(ident,fake)
        except ValueError:pass
        else:raise AssertionError("CKAD48_CONFLICT_ACCEPTED")
        if self.checkpoint()!=raw:raise AssertionError("CKAD48_CONFLICT_MUTATED_SOURCE")
        # Both new actions must genuinely have been seen in the source,
        # not merely enumerated during an evaluator-only probe.
        counts=[sum(self.invariant[a]) for a in range(4)]
        return {"arm":self.mode,"source_episodes":self.n,
                "genuine_transitions":2*self.n,"genuine_rewards":self.n,
                "per_action_transition_counts":counts,
                "full_checkpoint_sha256":sha256(raw),
                "source_sha256":sha256(canonical(self.source)),
                "prior80_sha256":self.initial_80_sha,
                "checkpoint_bytes":len(raw),"posterior_structure_weights":self.posterior,
                "cold_exact":True,"duplicate_idempotent":True,
                "conflict_atomic":True,"old_source_retained":True}


def expected_brier(p,truth):
    if not(0<=p<=1 and 0<=truth<=1):raise ValueError("CKAD48_BRIER_DOMAIN")
    d=p-truth
    return d*d+truth*(1-truth)


def score_seed(seed):
    if seed not in DEV:raise ValueError("CKAD48_ONLY_REGISTERED_DEV")
    start=time.perf_counter()
    cpu=time.process_time()
    all_probes=[];world_receipts=[]
    for world in (0,1):
        events,private=world_source(seed,world)
        models={arm:NativeStateEffects(arm) for arm in ARMS[:4]}
        world_probes=[]
        for t,event in enumerate(events):
            if t in PROBE_TIMES:
                before={name:m.checkpoint() for name,m in models.items()}
                for arm in ARMS:
                    score=0.0
                    for s in range(4):
                        for a in range(4):
                            for b in range(4):
                                truth=private_expected_reward(world,
                                  private["private_action_effect_mappings"],s,a,b)
                                p=.5 if arm=="uniform_sham" else models[arm].predict_reward(s,a,b)
                                score+=expected_brier(p,truth)
                    world_probes.append({"t":t,"arm":arm,"expected_brier":score/64})
                if any(before[name]!=m.checkpoint() for name,m in models.items()):
                    raise AssertionError("CKAD48_PROBE_TOUCHED_TRAINED_SOURCE")
            for m in models.values():m.observe(*event)
        for name,m in models.items():
            details=m.check_custody(events[-1])
            details["world"]=world
            details["true_partition_evaluator_only"]=private["private_state_partition"]
            world_receipts.append(details)
        all_probes.extend(world_probes)
    groups={}
    for phase,times in PHASES.items():
        data=[r for r in all_probes if r["t"] in times]
        expected=len(times)*2
        if len(data)!=expected*len(ARMS):
            raise AssertionError("CKAD48_PROBE_SCOPE_INCOMPLETE")
        groups[phase]={"fixed_probe_instances":expected,
            "expected_brier":{arm:sum(r["expected_brier"] for r in data
                              if r["arm"]==arm)/expected for arm in ARMS}}
    return {"seed":seed,"groups":groups,"world_model_receipts":world_receipts,
            "public_source_episodes":2*TOTAL,
            "observed_public_consequences":2*TOTAL*3,
            "read_only_probe_records":len(all_probes),
            "probe_inputs_per_record":64,
            "wall_seconds":round(time.perf_counter()-start,5),
            "cpu_seconds":round(time.process_time()-cpu,5)}


def classify(cases):
    if tuple(r["seed"] for r in cases)!=DEV:
        raise AssertionError("CKAD48_DEV_ORDER")
    for r in cases:
        if len(r["world_model_receipts"])!=8:
            return "SOURCE_INVALID"
        for meta in r["world_model_receipts"]:
            if not all(meta[key] is True for key in (
                "cold_exact","duplicate_idempotent","conflict_atomic",
                "old_source_retained")):
                return "SOURCE_INVALID"
            if min(meta["per_action_transition_counts"])==0:
                return "SOURCE_INVALID"
        pool=r["groups"]["pooled_late_and_return"]["expected_brier"]
        early=r["groups"]["early_novel"]["expected_brier"]
        cold=r["groups"]["cold_return"]["expected_brier"]
        cand=pool["state_partition_native"]
        if (cand>.19 or
            cand>pool["unrestricted_tabular"]-.010 or
            cand>pool["false_XOR_invariant"]-.025 or
            cand>pool["exact_structure_BMA"]+.004 or
            early["state_partition_native"]>early["exact_structure_BMA"]+.015 or
            cold["state_partition_native"]>cold["exact_structure_BMA"]+.008):
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("preflight","dev"))
    p.add_argument("--seed",type=int)
    args=p.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD48_NO_SEED_DURING_PREFLIGHT")
        print(canonical({"schema":SCHEMA,"prereg":PREREG,"dev":DEV,
          "held_pilots":PILOT,"held_primaries":PRIMARY,
          "accepted_native_Yggdrasil_changed":False,
          "first_use":False}))
        return
    if args.seed not in DEV:raise ValueError("CKAD48_ONLY_REGISTERED_DEV")
    print("CKAD48_CASE="+canonical(score_seed(args.seed)))


if __name__=="__main__":
    main()
