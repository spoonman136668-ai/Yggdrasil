"""HC06 preregistered disjoint-source falsification and independent Bayesian challenge.

Source physics and phase labels never enter either learner. Every training
observation follows one physically executed action on a continuous trajectory.
Evaluator-only all-state tests happen after learning, without model updates.
"""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
from time import perf_counter
import tracemalloc

from bayesian_control import BayesianEntropyPlanner, canonical

HERE=Path(__file__).resolve().parent
HC05_MODEL=HERE.parent/"dg1-hc05-20261113"/"model.py"
module_spec=importlib.util.spec_from_file_location("hc05_immutable",HC05_MODEL)
hc05=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(hc05)

FAMILIES={
    "iid":tuple(range(41001,41009)),
    "rewired":tuple(range(41009,41017)),
    "majority":tuple(range(41017,41025)),
    "return_A":tuple(range(41025,41033)),
}
POLICIES=("hc05_lookahead","bayesian_entropy","hc05_greedy","round_robin","seeded_random")

class SourceWorld:
    def __init__(self,seed,family):
        if family not in FAMILIES or seed not in FAMILIES[family]:
            raise ValueError("HC06_UNKNOWN_FROZEN_SOURCE")
        self.seed=seed
        self.family=family
        self.rules=[]
        for action in range(4):
            r=random.Random(seed*97+action*37)
            self.rules.append((r.randrange(3),r.randrange(2)))
        self.physical_actions=0

    def source_next_for_evaluator(self,before,action,phase):
        left_idx=(action+1)%4 if self.family=="rewired" else (action-1)%4
        right_idx=(action+2)%4 if self.family=="rewired" else (action+1)%4
        left=(before>>left_idx)&1
        right=(before>>right_idx)&1
        own=(before>>action)&1
        rule,sign=self.rules[action]
        if self.family=="majority":
            effect=int((left+right+own)>=2)
        elif rule==0:
            effect=left^right
        elif rule==1:
            effect=left^right^own
        else:
            effect=left&right
        effect^=sign
        if self.family=="return_A" and phase==1:
            effect^=1
        return before^(effect<<action)

    def charge(self,before,action,phase):
        self.physical_actions+=1
        return self.source_next_for_evaluator(before,action,phase)


def audit(model,source,seen):
    d={k:0 for k in (
        "correct","wrong_confident","abstained",
        "unseen_correct","unseen_wrong_confident","unseen_abstained"
    )}
    for s in range(16):
        for a in range(4):
            expected=source.source_next_for_evaluator(s,a,phase=0)
            got=model.predict(s,a)
            label=("abstained" if got is None else
                   "correct" if got==expected else "wrong_confident")
            d[label]+=1
            if (s,a) not in seen:
                d["unseen_"+label]+=1
    d["unseen_total"]=sum(d["unseen_"+x] for x in (
        "correct","wrong_confident","abstained"))
    assert sum(d[x] for x in ("correct","wrong_confident","abstained"))==64
    return d


def one_policy(seed,family,policy):
    w=SourceWorld(seed,family)
    m=(BayesianEntropyPlanner() if policy=="bayesian_entropy"
       else hc05.CausalProbeCells())
    start=seed%16
    rng=random.Random(seed+1919)
    ledger=[]
    observed=set()
    action_ns=0
    t0=perf_counter()
    budget=25 if family=="return_A" else 12
    for t in range(budget):
        phase=0 if family!="return_A" or t<16 or t==24 else 1
        p0=perf_counter()
        if policy=="hc05_lookahead":
            action=m.choose_lookahead(start)
        elif policy=="bayesian_entropy":
            action=m.choose(start)
        elif policy=="hc05_greedy":
            action=m.choose_greedy(start)
        elif policy=="round_robin":
            action=t%4
        elif policy=="seeded_random":
            action=rng.randrange(4)
        else:
            raise ValueError("HC06_INVALID_POLICY")
        action_ns+=round((perf_counter()-p0)*1e9)
        after=w.charge(start,action,phase)
        m.observe(start,action,after)
        ledger.append([start,action,after])
        observed.add((start,action))
        start=after
    wall_ms=round((perf_counter()-t0)*1000,5)
    assert w.physical_actions==budget
    assert m.observations==budget if policy!="bayesian_entropy" else m.charged==budget
    checkpoint=m.snapshot()
    if policy=="bayesian_entropy":
        restored=BayesianEntropyPlanner.restore(checkpoint)
    else:
        restored=hc05.CausalProbeCells.restore(checkpoint)
    assert restored.snapshot()==checkpoint
    assert all(m.predict(s,a)==restored.predict(s,a)
               for s in range(16) for a in range(4))
    assert len(checkpoint)<=1024
    return {
        "accuracy":audit(m,w,observed),
        "source_actions":w.physical_actions,
        "ledger_sha256":sha256(canonical(ledger)).hexdigest(),
        "distinct_public_state_action_pairs":len(observed),
        "cold_restore":True,
        "checkpoint_bytes":len(checkpoint),
        "logical_prior_mask_bits":24,
        "policy_decision_ns":action_ns,
        "whole_learning_ms":wall_ms,
    }


def one_world(seed,family):
    arms={p:one_policy(seed,family,p) for p in POLICIES}
    assert all(a["source_actions"]==(25 if family=="return_A" else 12)
               for a in arms.values())
    return {"seed":seed,"family":family,"arms":arms}


def run():
    tracemalloc.start()
    worlds=[one_world(seed,family) for family,seeds in FAMILIES.items()
            for seed in seeds]
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(worlds)==32
    def total(group,policy,field):
        return sum(w["arms"][policy]["accuracy"][field] for w in worlds
                   if w["family"]==group)
    iid_pass=(
        total("iid","hc05_lookahead","wrong_confident")==0 and
        total("iid","hc05_lookahead","correct")>=
        total("iid","bayesian_entropy","correct")+8*4 and
        all(w["arms"]["hc05_lookahead"]["cold_restore"] for w in worlds)
    )
    rewired_pass=(
        total("rewired","hc05_lookahead","wrong_confident")==0 and
        total("rewired","hc05_lookahead","correct")>=256
    )
    return_pass=(
        total("return_A","hc05_lookahead","wrong_confident")==0 and
        total("return_A","hc05_lookahead","correct")>=256
    )
    majority_errors=total("majority","hc05_lookahead","wrong_confident")
    if iid_pass and rewired_pass and return_pass and majority_errors==0:
        verdict="DEV_SUPPORTED_NOT_SCIENCE"
    elif iid_pass or rewired_pass or return_pass:
        verdict="MIXED_DEV"
    else:
        verdict="NEGATIVE_DEV"
    result={
        "schema":"yggdrasil.dg1-hc06.independent-bayesian-dev.v1",
        "classification":verdict,
        "scientific_acceptance":"UNVERIFIED",
        "iid_primary_pass":iid_pass,
        "rewired_ood_pass":rewired_pass,
        "return_A_cold_retention_pass":return_pass,
        "majority_confident_wrong":majority_errors,
        "negative_retained":True,
        "baseline_independent_source":True,
        "matched_physical_actions":True,
        "matched_logical_hypothesis_capacity":True,
        "matched_compute":False,
        "gradient_steps":0,
        "external_model_calls":0,
        "whole_process_peak_tracemalloc_bytes":peak,
        "total_real_physical_actions":sum(
            r["source_actions"] for w in worlds for r in w["arms"].values()),
        "cohort_metrics":{
            f:{p:{k:total(f,p,k) for k in (
                "correct","wrong_confident","abstained",
                "unseen_correct","unseen_wrong_confident","unseen_abstained")}
                for p in POLICIES} for f in FAMILIES
        },
        "worlds":worlds,
    }
    return result

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
