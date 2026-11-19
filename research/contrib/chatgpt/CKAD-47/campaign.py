"""CKAD47: source-trained tokenless four-state/four-action causal composition.

Isolated research prototype, NOT the accepted binary Yggdrasil episode API.
Private world physics is used ONLY by source generation and read-only examiner.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import time

SCHEMA="yggdrasil.ckad47.fourway-causal.v1"
PREREG="b0d71e48848a92d10ed78019d40dffb7af0f505c"
DEV=(47111,47112)
PILOT=(47211,47212)
PRIMARY=(47311,47312,47313)
OLD=96
NEW_END=192
TOTAL=240
PROBES=(96,112,128,144,160,176,192,208,224)
PHASES={"novel_early":(96,112),"novel_late":(144,160,176),
        "cold_return":(192,208,224),
        "pooled_late_and_return":(144,160,176,192,208,224)}
ARMS=("native_fourway_effect","exact_bijective_bayes",
      "fully_fitted_tabular","uniform_negative")
MAPS=tuple(itertools.permutations(range(4)))
ALPHA=.25
TRANS_PROB=.9
ERROR_PROB=.1/3
MAX_LEDGER=TOTAL


def _json(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def _sha(text):
    if type(text) is not str:raise TypeError("CKAD47_SHA_TEXT")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bit(x):
    if type(x) is not int or x not in (0,1):raise ValueError("CKAD47_BIT")
    return x


def _quad(x):
    if type(x) is not int or x not in (0,1,2,3):raise ValueError("CKAD47_QUAD")
    return x


def _reward_true(world,final):
    if world==0:return (final&1)^((final>>1)&1)
    if world==1:return (final&1)|((final>>1)&1)
    raise ValueError("CKAD47_PRIVATE_WORLD")


def _transition_distribution(state,delta):
    intended=state^delta
    return tuple(TRANS_PROB if x==intended else ERROR_PROB for x in range(4))


def private_two_action_probability(world,mapping,state,a1,a2):
    """Only the evaluator knows mapping and world's latent reward law."""
    _quad(state);_quad(a1);_quad(a2)
    if tuple(sorted(mapping))!=(0,1,2,3):raise ValueError("CKAD47_MAPPING")
    total=0.0
    for s1,p1 in enumerate(_transition_distribution(state,mapping[a1])):
        for s2,p2 in enumerate(_transition_distribution(s1,mapping[a2])):
            y=.9 if _reward_true(world,s2) else .1
            total+=p1*p2*y
    return total


def world_events(seed,world):
    if seed not in DEV and seed!=0:raise ValueError("CKAD47_ONLY_REGISTERED_DEV")
    if world not in (0,1):raise ValueError("CKAD47_WORLD")
    random_seed=int(_sha(f"ckad47-source|{seed}|{world}"),16)
    rng=random.Random(random_seed)
    mapping=list(range(4))
    rng.shuffle(mapping)
    events=[]
    for t in range(TOTAL):
        state=rng.randrange(4)
        pool=(0,1) if t<OLD or t>=NEW_END else (2,3)
        a1=rng.choice(pool)
        a2=rng.choice(pool)
        u1=rng.random()
        noise1=rng.randrange(3)
        u2=rng.random()
        noise2=rng.randrange(3)
        uy=rng.random()
        next1=state^mapping[a1]
        if u1>=TRANS_PROB:
            next1=[x for x in range(4) if x!=next1][noise1]
        next2=next1^mapping[a2]
        if u2>=TRANS_PROB:
            next2=[x for x in range(4) if x!=next2][noise2]
        chance=.9 if _reward_true(world,next2) else .1
        reward=int(uy<chance)
        row={"s0":state,"a1":a1,"s1":next1,"a2":a2,"s2":next2,"y":reward}
        ident=_sha(f"ckad47-public|{seed}|{world}|{t}")
        events.append((ident,row))
    return events,{"mapping_evaluator_only":mapping,"world":world}


class QuadCausalLearner:
    def __init__(self,mode):
        if mode not in ARMS[:3]:raise ValueError("CKAD47_BAD_ARM")
        self.mode=mode
        self.effects=[[0,0,0,0] for _ in range(4)]
        self.tabular=[[[0,0,0,0] for _ in range(4)] for _ in range(4)]
        self.reward=[[0,0] for _ in range(4)]
        self.weights=[1/24]*24
        self.receipts={}
        self.ledger=[]
        self.n=0
        self.first96=None

    def predict_next(self,state,action):
        state=_quad(state);action=_quad(action)
        if self.mode=="native_fourway_effect":
            counts=self.effects[action]
            total=sum(counts)+1.
            return tuple((counts[state^dest]+ALPHA)/total for dest in range(4))
        if self.mode=="fully_fitted_tabular":
            counts=self.tabular[state][action]
            total=sum(counts)+1.
            return tuple((c+ALPHA)/total for c in counts)
        # Strong exact structural model, all 24 equally possible bijections.
        return tuple(sum(w*_transition_distribution(state,perm[action])[dest]
                         for w,perm in zip(self.weights,MAPS))
                     for dest in range(4))

    def predict_reward(self,state,a1,a2):
        state=_quad(state);a1=_quad(a1);a2=_quad(a2)
        post=tuple((success+1)/(failure+success+2)
                    for failure,success in self.reward)
        if self.mode=="exact_bijective_bayes":
            # Marginalize the SAME hypothesis across both actions;
            # product-of-marginals would lose dependence and is weaker.
            return sum(w*sum(p1*p2*post[s2]
                     for s1,p1 in enumerate(_transition_distribution(state,perm[a1]))
                     for s2,p2 in enumerate(_transition_distribution(s1,perm[a2])))
                     for w,perm in zip(self.weights,MAPS))
        first=self.predict_next(state,a1)
        return sum(p1*p2*post[s2]
                   for s1,p1 in enumerate(first)
                   for s2,p2 in enumerate(self.predict_next(s1,a2)))

    def observe(self,identifier,row):
        if type(identifier) is not str or len(identifier)!=64 or not all(
             k in "0123456789abcdef" for k in identifier):
            raise ValueError("CKAD47_SOURCE_ID")
        if type(row) is not dict or set(row)!={"s0","a1","s1","a2","s2","y"}:
            raise ValueError("CKAD47_ROW_SCHEMA")
        for k in ("s0","a1","s1","a2","s2"):_quad(row[k])
        _bit(row["y"])
        record_hash=_sha(_json(row))
        if identifier in self.receipts:
            if self.receipts[identifier]!=record_hash:
                raise ValueError("CKAD47_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=MAX_LEDGER:raise ValueError("CKAD47_SOURCE_BUDGET")
        s,a,u,b,v,y=(row[k] for k in ("s0","a1","s1","a2","s2","y"))
        if self.mode=="native_fourway_effect":
            self.effects[a][s^u]+=1
            self.effects[b][u^v]+=1
        elif self.mode=="fully_fitted_tabular":
            self.tabular[s][a][u]+=1
            self.tabular[u][b][v]+=1
        else:
            updated=[weight*(_transition_distribution(s,perm[a])[u])*
                     (_transition_distribution(u,perm[b])[v])
                     for weight,perm in zip(self.weights,MAPS)]
            norm=sum(updated)
            if norm<=0:raise AssertionError("CKAD47_EXACT_POSTERIOR_ZERO")
            self.weights=[x/norm for x in updated]
        self.reward[v][y]+=1
        self.receipts[identifier]=record_hash
        self.ledger.append([identifier,record_hash])
        self.n+=1
        if self.n==OLD:self.first96=_sha(_json(self.ledger))
        return self

    def checkpoint(self):
        return _json({"schema":SCHEMA,"mode":self.mode,"n":self.n,
                 "effects":self.effects,"tabular":self.tabular,
                 "reward":self.reward,"weights":self.weights,
                 "receipts":self.receipts,"ledger":self.ledger,
                 "first96":self.first96})

    @classmethod
    def restore(cls,raw,sha):
        if _sha(raw)!=sha:raise ValueError("CKAD47_CHECKPOINT_SHA")
        data=json.loads(raw)
        if data["schema"]!=SCHEMA:raise ValueError("CKAD47_CHECKPOINT_SCHEMA")
        obj=cls(data["mode"])
        for key in ("n","effects","tabular","reward","weights",
                    "receipts","ledger","first96"):
            setattr(obj,key,data[key])
        if (obj.n!=len(obj.ledger) or obj.n!=len(obj.receipts) or
            obj.n>MAX_LEDGER or
            sum(sum(x) for x in obj.reward)!=obj.n):
            raise ValueError("CKAD47_CHECKPOINT_SOURCE_CUSTODY")
        if obj.mode=="native_fourway_effect" and sum(sum(x) for x in obj.effects)!=2*obj.n:
            raise ValueError("CKAD47_CHECKPOINT_TRANSITION_COUNT")
        if obj.mode=="fully_fitted_tabular" and sum(sum(sum(x) for x in row) for row in obj.tabular)!=2*obj.n:
            raise ValueError("CKAD47_CHECKPOINT_TRANSITION_COUNT")
        if obj.n>=OLD and _sha(_json(obj.ledger[:OLD]))!=obj.first96:
            raise ValueError("CKAD47_PRIOR_SOURCE_ERASED")
        if obj.checkpoint()!=raw:raise ValueError("CKAD47_CHECKPOINT_BYTES")
        return obj

    def custody(self,last):
        raw=self.checkpoint()
        if QuadCausalLearner.restore(raw,_sha(raw)).checkpoint()!=raw:
            raise AssertionError("CKAD47_COLD_ERROR")
        if self.n!=TOTAL or len(self.receipts)!=TOTAL:
            raise AssertionError("CKAD47_SOURCE_INCOMPLETE")
        if _sha(_json(self.ledger[:OLD]))!=self.first96:
            raise AssertionError("CKAD47_COLD_RETENTION")
        if self.observe(*last) is not self or self.checkpoint()!=raw:
            raise AssertionError("CKAD47_DUPLICATE_NOT_IDEMPOTENT")
        ident,row=last
        altered=dict(row,y=1-row["y"])
        try:self.observe(ident,altered)
        except ValueError:pass
        else:raise AssertionError("CKAD47_CONFLICT_ACCEPTED")
        if self.checkpoint()!=raw:
            raise AssertionError("CKAD47_ATOMICITY_FAILURE")
        return {"mode":self.mode,"checkpoint_sha256":_sha(raw),
                "checkpoint_bytes":len(raw),
                "ledger_sha256":_sha(_json(self.ledger)),
                "prior96_sha256":self.first96,"source_count":self.n,
                "action_counts":[sum(self.effects[a]) if self.mode=="native_fourway_effect"
                     else sum(sum(self.tabular[s][a]) for s in range(4))
                     if self.mode=="fully_fitted_tabular" else None
                     for a in range(4)],
                "cold_exact":True,"conflict_atomic":True,
                "duplicate_idempotent":True,"first96_unchanged":True}


def expected_brier(pred,truth):
    if not(0<=pred<=1 and 0<=truth<=1):
        raise ValueError("CKAD47_BRIER_DOMAIN")
    diff=pred-truth
    return diff*diff+truth*(1-truth)


def evaluate(seed):
    if seed not in DEV:raise ValueError("CKAD47_ONLY_REGISTERED_DEV")
    start=time.perf_counter();cpu=time.process_time()
    cases=[];source_receipts=[]
    for world in (0,1):
        events,private=world_events(seed,world)
        learners={mode:QuadCausalLearner(mode) for mode in ARMS[:3]}
        grid=[]
        first96={}
        for t,(ident,row) in enumerate(events):
            if t in PROBES:
                frozen_before={name:obj.checkpoint() for name,obj in learners.items()}
                for mode in ARMS:
                    total=0.0
                    for s in range(4):
                        for a1 in range(4):
                            for a2 in range(4):
                                truth=private_two_action_probability(world,private["mapping_evaluator_only"],s,a1,a2)
                                p=.5 if mode=="uniform_negative" else learners[mode].predict_reward(s,a1,a2)
                                total+=expected_brier(p,truth)
                    grid.append({"world":world,"t":t,"arm":mode,
                                 "expected_brier":total/64})
                if any(obj.checkpoint()!=frozen_before[name]
                       for name,obj in learners.items()):
                    raise AssertionError("CKAD47_PROBE_LEAKED_INTO_TRAINING")
            for learner in learners.values():learner.observe(ident,row)
            if t==OLD-1:
                first96={name:obj.checkpoint() for name,obj in learners.items()}
        if not first96:raise AssertionError("CKAD47_FIRST96_MISSING")
        for name,obj in learners.items():
            before=obj.checkpoint()
            if obj.first96!=_sha(_json(obj.ledger[:OLD])):
                raise AssertionError("CKAD47_OLD_SOURCE_NOT_RETAINED")
            source_receipts.append({"world":world,**obj.custody(events[-1]),
                "same_original_first96_as_at_source_time":(
                    json.loads(first96[name])["ledger"]==obj.ledger[:OLD])})
            if obj.checkpoint()!=before:raise AssertionError("CKAD47_CUSTODY_MUTATED")
        cases.extend(grid)
    groups={}
    for phase,indices in PHASES.items():
        selected=[x for x in cases if x["t"] in indices]
        groups[phase]={"common_grid_count":len(selected),
                       "expected_brier":{mode:sum(x["expected_brier"] for x in selected
                                              if x["arm"]==mode)/(len(indices)*2)
                                         for mode in ARMS}}
    return {"seed":seed,"groups":groups,"model_receipts":source_receipts,
            "real_source_episodes":TOTAL*2,"real_observed_consequences":TOTAL*2*3,
            "probe_records":len(cases),"probe_inputs_per_record":64,
            "wall_seconds":round(time.perf_counter()-start,5),
            "cpu_seconds":round(time.process_time()-cpu,5)}


def classify(results):
    if tuple(c["seed"] for c in results)!=DEV:
        raise AssertionError("CKAD47_DEV_ORDER")
    for case in results:
        if not all(w["cold_exact"] and w["first96_unchanged"] and
                   w["conflict_atomic"] and w["duplicate_idempotent"] and
                   w["same_original_first96_as_at_source_time"]
                   for w in case["model_receipts"]):
            return "SOURCE_INVALID"
        if len(case["model_receipts"])!=6:
            return "SOURCE_INVALID"
        p=case["groups"]["pooled_late_and_return"]["expected_brier"]
        early=case["groups"]["novel_early"]["expected_brier"]
        cold=case["groups"]["cold_return"]["expected_brier"]
        cand=p["native_fourway_effect"]
        if (cand>.17 or
            cand>p["fully_fitted_tabular"]-.010 or
            cand>p["exact_bijective_bayes"]+.006 or
            early["native_fourway_effect"]>early["exact_bijective_bayes"]+.015 or
            cold["native_fourway_effect"]>cold["exact_bijective_bayes"]+.008):
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","dev"),required=True)
    p.add_argument("--seed",type=int)
    q=p.parse_args()
    if q.mode=="preflight":
        if q.seed is not None:raise ValueError("CKAD47_PREFLIGHT_HAS_SEED")
        print(_json({"schema":SCHEMA,"prereg":PREREG,
                     "dev":DEV,"pilots_untouched":PILOT,
                     "primaries_untouched":PRIMARY,
                     "original_native_accepted_API_modified":False,
                     "scientific_first_use":False}))
        return
    if q.seed not in DEV:raise ValueError("CKAD47_ONLY_REGISTERED_DEV")
    print("CKAD47_CASE="+_json(evaluate(q.seed)))


if __name__=="__main__":
    main()
