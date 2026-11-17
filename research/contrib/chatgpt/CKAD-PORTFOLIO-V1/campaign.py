"""CKAD-PORTFOLIO-V1: cumulative native structure hypotheses + interventions.

Synthetic source-free development only. Frozen populations, no original source
actions, no real causal-world first-use and no accepted Yggdrasil changes.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_hypothesis_portfolio import (
    NativeHypothesisPortfolio,ALL_CANDIDATES,GATES,grammar,votes,
    canonical,digest,evaluate_program,SOURCE_MODE)
from yggdrasil.native_context_basis import NativeContextBasis,feature_row
from yggdrasil.native_context_basis import canonical as native_canonical
from yggdrasil.native_context_basis import digest as native_digest
from yggdrasil.native_context_basis import require as native_require

IN_SEEDS=tuple(range(701,733))
SHIFT_SEEDS=tuple(range(801,817))
CORRUPT_SEEDS=tuple(range(901,917))
CONDITIONS=(("IN_FAMILY",IN_SEEDS),("SHIFT",SHIFT_SEEDS),
            ("CORRUPT",CORRUPT_SEEDS))
POLICIES=("tournament","rank2","random","two_step")
INITIAL=8
EXTRA=8
HELD_N=32
MAX_SLOTS=64
VOTES=votes()
BANK=grammar()

def require(ok,code):
    if not ok:
        raise ValueError("CKAD_PORTFOLIO_V1_"+code)

def key(label,*parts):
    b="ckad-portfolio-v1:"+label+":" + ":".join(str(v) for v in parts)
    return hashlib.sha256(b.encode("ascii")).digest()

def split_inputs():
    order=sorted(range(64),key=lambda m:key("held",m))
    held=tuple(sorted(order[:HELD_N]))
    pool=tuple(sorted(order[HELD_N:],key=lambda m:key("initial",m)))
    init=pool[:INITIAL]
    pending=pool[INITIAL:]
    require(len(set(held))==32 and len(set(pool))==32
            and not set(held)&set(pool) and len(pending)==24,
            "FROZEN_SPLIT")
    return held,pool,init,pending

class FabricatedWorld:
    """Private generated synthetic program; held labels guarded by a latch."""
    __slots__=("seed","condition","_lin","_gate","_bias","_held","_pool",
               "_sealed","_used","effect_calls")
    def __init__(self,seed,condition,held,pool):
        require(condition in ("IN_FAMILY","SHIFT","CORRUPT"),"WORLD_CLASS")
        self.seed=seed
        self.condition=condition
        self._lin=int.from_bytes(key("linear",seed)[:4],"big")%64
        options=[m for m in range(1,32) if m.bit_count()==3] if condition=="SHIFT" else GATES
        self._gate=options[int.from_bytes(key("gate",seed)[:4],"big")%len(options)]
        self._bias=key("bias",seed)[0]&1
        self._held=frozenset(held);self._pool=frozenset(pool)
        self._sealed=False;self._used=set();self.effect_calls=0

    def _truth(self,m):
        return evaluate_program(m,self._lin,self._gate,self._bias)

    def observe(self,m):
        require(type(m) is int and m in self._pool
                and m not in self._held and not self._sealed
                and m not in self._used,"SOURCE_EFFECT_RIGHTS")
        self._used.add(m)
        self.effect_calls+=1
        return self._truth(m)

    def unlock(self):
        require(self.effect_calls==16 and not self._sealed,"EARLY_EVALUATION")
        self._sealed=True

    def held_truth(self,m):
        require(self._sealed and type(m) is int and m in self._held,
                "HELD_OUTCOME_NOT_RELEASED")
        return self._truth(m)

    def identity(self):
        # Not available to any learning or action-choice method.
        return digest(canonical([self.seed,self.condition,self._lin,self._gate,
                                 self._bias]))

def corrupt_initial(seed,inputs,values):
    """Exactly two preregistered spurious labels, never later real effects."""
    require(len(inputs)==len(values)==INITIAL,"CORRUPT_INITIAL")
    order=sorted(range(INITIAL),key=lambda i:key("tamper",seed,inputs[i]))
    altered=list(values)
    for i in order[:2]:
        altered[i]^=1
    return tuple(altered)

def rank_add(basis,m,degree=2):
    b=feature_row(m,degree)
    while b:
        pivot=b.bit_length()-1
        if pivot not in basis:
            basis[pivot]=b
            return True
        b ^= basis[pivot]
    return False

def pick_rank(anonymous_slot,seen,remaining):
    basis={}
    for m in seen:
        rank_add(basis,m)
    order=sorted(remaining,key=lambda m:key("rank",anonymous_slot,m))
    for m in order:
        if rank_add(dict(basis),m):
            return m
    return order[0]

def pick_tournament(anonymous_slot,state,remaining):
    count=state.bit_count()
    best=None
    for m in remaining:
        positives=(state&VOTES[m]).bit_count()
        split=min(positives,count-positives)
        candidate=(-split,key("tournament",anonymous_slot,m),m)
        if best is None or candidate<best:
            best=candidate
    return best[-1]

def pick_two_step(anonymous_slot,state,remaining):
    """Two-action expected remaining count with optimal adaptive second step."""
    full=ALL_CANDIDATES
    best=None
    for first in remaining:
        parts=(state&(full^VOTES[first]),state&VOTES[first])
        second_candidates=[m for m in remaining if m!=first]
        score=0
        for part in parts:
            n=part.bit_count()
            if n==0:
                continue
            if not second_candidates:
                score += n*n
                continue
            score += min(
                (part&VOTES[m]).bit_count()**2+
                (n-(part&VOTES[m]).bit_count())**2
                for m in second_candidates)
        candidate=(score,key("two_step",anonymous_slot,first),first)
        if best is None or candidate<best:
            best=candidate
    return best[-1]

def pick(policy,slot,model,seen,remaining):
    require(remaining and all(m not in seen for m in remaining),"POOL")
    if policy=="random":
        return min(remaining,key=lambda m:key("random",slot,m))
    if policy=="rank2":
        return pick_rank(slot,seen,remaining)
    state=model._state(slot)[0]
    if policy=="tournament":
        return pick_tournament(slot,state,remaining)
    require(policy=="two_step","POLICY")
    return pick_two_step(slot,state,remaining)

def independent_symbolic_predict(observations):
    """Separate explicit expression enumeration, never using the bitset cache."""
    eligible=[]
    for linear in range(64):
        for gate in (m for m in range(1,32) if m.bit_count() in (1,2)):
            for bias in (0,1):
                def f(x):
                    return (((x&linear).bit_count()&1)
                            ^int(bool(x&32) and (x&gate)==gate)^bias)
                if all(f(mask)==value for mask,value in observations):
                    eligible.append((linear,gate,bias))
    answers=[]
    for mask in range(64):
        first=None
        same=True
        for linear,gate,bias in eligible:
            v=(((mask&linear).bit_count()&1)
               ^int(bool(mask&32) and (mask&gate)==gate)^bias)
            if first is None:first=v
            elif v!=first:
                same=False
                break
        answers.append(first if same else None)
    return tuple(answers),len(eligible)

def cart_predict(seed,observations):
    from sklearn.tree import DecisionTreeClassifier
    x=[[((m>>bit)&1) for bit in range(6)] for m,_ in observations]
    labels=[y for _,y in observations]
    clf=DecisionTreeClassifier(criterion="gini",random_state=seed,
                               max_depth=None,min_samples_leaf=1)
    clf.fit(x,labels)
    require(all(int(y)==int(v) for y,v in zip(clf.predict(x),labels)),
            "CONVENTIONAL_NOT_FULLY_FIT")
    return tuple(int(v) for v in clf.predict(
        [[(mask>>bit)&1 for bit in range(6)] for mask in range(64)]))

def score(vector,held,truth):
    answers=[vector[m] for m in held]
    correct=sum(v is not None and v==y for v,y in zip(answers,truth))
    wrong=sum(v is not None and v!=y for v,y in zip(answers,truth))
    return {"correct":correct,"wrong":wrong,
            "abstained":len(held)-correct-wrong,"questions":len(held),
            "answers_sha256":digest(canonical(answers))}

def audit_control(seed,condition,held,pool,initial,pending):
    """A3-style fixed-degree2 contradiction gate on equal16 effects."""
    world=FabricatedWorld(seed,condition,held,pool)
    observed=list(initial)
    raw=[world.observe(m) for m in initial]
    observed_labels=list(corrupt_initial(seed,initial,raw)
                         if condition=="CORRUPT" else raw)
    for _ in range(4):
        m=pick_rank(seed,observed,[x for x in pending if x not in observed])
        observed.append(m);observed_labels.append(world.observe(m))
    try:
        fit=NativeContextBasis(5).stage_fit(
            0,[[m&31,m>>5,y] for m,y in zip(observed,observed_labels)],
            native_digest(native_canonical([[m&31,m>>5,y]
                for m,y in zip(observed,observed_labels)])),max_degree=2)
        pre=tuple(fit.predict(0,m&31,m>>5) for m in range(64))
    except ValueError as exc:
        require(str(exc)=="CKAD_NATIVE_MODEL_CLASS_INADEQUATE",
                "AUDIT_SOURCE_ERROR")
        pre=(None,)*64
    remaining=[m for m in pending if m not in observed]
    # Target identified diagnostics; rank3 as tie, never use outcomes.
    basis={}
    for m in observed:rank_add(basis,m,3)
    probe=[]
    for _ in range(4):
        def ordered(m):
            return (0 if pre[m] is not None else 1,
                    0 if rank_add(dict(basis),m,3) else 1,
                    key("audit",seed,m))
        m=min(remaining,key=ordered)
        remaining.remove(m);probe.append(m);rank_add(basis,m,3)
    labels=[world.observe(m) for m in probe]
    confirmations=sum(pre[m] is not None for m in probe)
    contradictions=sum(pre[m] is not None and pre[m]!=y
                       for m,y in zip(probe,labels))
    can_admit=confirmations==4 and contradictions==0
    allm=observed+probe
    ally=observed_labels+labels
    try:
        complete=NativeContextBasis(5).stage_fit(
            0,[[m&31,m>>5,y] for m,y in zip(allm,ally)],
            native_digest(native_canonical([[m&31,m>>5,y]
                for m,y in zip(allm,ally)])),max_degree=2)
        outputs=tuple(complete.predict(0,m&31,m>>5) for m in range(64))
    except ValueError as exc:
        require(str(exc)=="CKAD_NATIVE_MODEL_CLASS_INADEQUATE",
                "AUDIT_REFIT_SOURCE")
        outputs=(None,)*64
        can_admit=False
    if not can_admit:
        outputs=(None,)*64
    require(world.effect_calls==16,"AUDIT_EFFECTS")
    return {"world":world,"outputs":outputs,"admitted":can_admit,
            "compared":confirmations,"contradictions":contradictions,
            "intervention_trace_sha256":digest(canonical(allm))}

def bootstrap_lower(deltas):
    require(len(deltas)==32,"BOOTSTRAP_WORLD_COUNT")
    means=[]
    for rep in range(1000):
        tot=0.0
        for j in range(32):
            i=int.from_bytes(key("bootstrap",rep,j)[:8],"big")%32
            tot+=deltas[i]
        means.append(tot/32)
    return sorted(means)[24]

def execute(out):
    held,pool,initial,pending=split_inputs()
    started=time.perf_counter()
    portfolios={name:NativeHypothesisPortfolio() for name in POLICIES}
    previous={name:{} for name in POLICIES}
    cases=[]
    arm_time={name:0.0 for name in POLICIES}
    for condition,seeds in CONDITIONS:
        for seed in seeds:
            slot=len(cases)
            require(slot<MAX_SLOTS,"MAX_WORLD_SLOTS")
            reports={}
            world_objects={}
            prediction_vectors={}
            for policy in POLICIES:
                start=time.perf_counter()
                actor=FabricatedWorld(seed,condition,held,pool)
                world_objects[policy]=actor
                state=portfolios[policy]
                witness=[]
                init_real=tuple(actor.observe(m) for m in initial)
                init_labels=(corrupt_initial(seed,initial,init_real)
                             if condition=="CORRUPT" else init_real)
                for m,y in zip(initial,init_labels):
                    state=state.observe(slot,m,y,digest(canonical(
                        [slot,m,y,SOURCE_MODE])))
                    witness.append((m,y))
                selected=[]
                for _ in range(EXTRA):
                    available=[m for m in pending if m not in selected]
                    chosen=pick(policy,slot,state,
                                [m for m,_ in witness],available)
                    selected.append(chosen)
                    y=actor.observe(chosen)
                    state=state.observe(slot,chosen,y,digest(canonical(
                        [slot,chosen,y,SOURCE_MODE])))
                    witness.append((chosen,y))
                require(actor.effect_calls==INITIAL+EXTRA
                        and len({m for m,_ in witness})==16,
                        "BUDGET_OR_REPLAY")
                vec=state.vector(slot)
                independent,ref_count=independent_symbolic_predict(witness)
                require(vec==independent and state.count(slot)==ref_count,
                        "INDEPENDENT_SYMBOLIC_PARITY")
                cart=cart_predict(seed,witness)
                require(not actor._sealed,"HELD_SOURCE_PREMATURE")
                portfolios[policy]=state
                prediction_vectors[policy]=(vec,cart)
                prior=previous[policy]
                for old_slot,old_vec in prior.items():
                    require(state.vector(old_slot)==old_vec,
                            "CUMULATIVE_INTERFERENCE")
                prior[slot]=vec
                reports[policy]={
                    "effects":actor.effect_calls,"unique_effects":16,
                    "action1_effects":sum(m>>5 for m,_ in witness),
                    "witness_input_sha256":digest(canonical([m for m,_ in witness])),
                    "witness_outcome_sha256":digest(canonical([y for _,y in witness])),
                    "candidate_count":state.count(slot),
                    "observations":state.details(slot)["observations"],
                    "elapsed_seconds":time.perf_counter()-start}
                arm_time[policy]+=reports[policy]["elapsed_seconds"]
            audit=audit_control(seed,condition,held,pool,initial,pending)
            require(all(a.effect_calls==16 for a in world_objects.values())
                    and audit["world"].effect_calls==16,
                    "MATCHED_ACTION_EFFECTS")
            # Original held truth is inaccessible to all arms until now.
            require(all(not actor._sealed for actor in world_objects.values())
                    and not audit["world"]._sealed,"HELD_BEFORE_SEAL")
            for actor in world_objects.values():
                actor.unlock()
            audit["world"].unlock()
            truth=tuple(world_objects["tournament"].held_truth(m) for m in held)
            require(all(tuple(x.held_truth(m) for m in held)==truth
                        for x in list(world_objects.values())+[audit["world"]]),
                        "INDEPENDENT_ACTOR_TRUTH_DRIFT")
            for name in POLICIES:
                vec,cart=prediction_vectors[name]
                reports[name]["native"]=score(vec,held,truth)
                reports[name]["cart"]=score(cart,held,truth)
            reports["audit"]={
                "effects":16,"admitted":audit["admitted"],
                "identified_probes":audit["compared"],
                "contradictions":audit["contradictions"],
                "native":score(audit["outputs"],held,truth),
                "witness_input_sha256":audit["intervention_trace_sha256"]}
            cases.append({"slot":slot,"seed":seed,"condition":condition,
                          "source_sha256":world_objects["tournament"].identity(),
                          "held_input_sha256":digest(canonical(held)),
                          "held_truth_sha256":digest(canonical(truth)),
                          "arms":reports})
    require(len(cases)==64,"ALL_WORLDS")
    checkpoints={}
    for name,state in portfolios.items():
        raw=state.checkpoint()
        checkpoints[name]={"checkpoint_ascii":raw.decode("ascii"),
                           "sha256":digest(raw),
                           "expected_vectors_sha256":digest(canonical(
                               [state.vector(slot) for slot in range(64)])),
                           "bytes":len(raw)}
        require(len(previous[name])==64,"CUMULATIVE_SLOTS")
    path=out/"native-checkpoints.json"
    path.write_bytes(canonical({"schema":"ckad.portfolio-v1.bundle.v1",
                                "states":checkpoints}))
    code="""import json,sys
from pathlib import Path
from yggdrasil.native_hypothesis_portfolio import NativeHypothesisPortfolio,canonical,digest
d=json.loads(Path(sys.argv[1]).read_bytes())
for name,item in d["states"].items():
    raw=item["checkpoint_ascii"].encode("ascii")
    assert digest(raw)==item["sha256"]
    state=NativeHypothesisPortfolio.restore(raw,item["sha256"])
    values=[state.vector(slot) for slot in range(64)]
    assert digest(canonical(values))==item["expected_vectors_sha256"]
print("CKAD_PORTFOLIO_COLD_PASS="+str(len(d["states"])*64))
"""
    cp=subprocess.run([sys.executable,"-B","-c",code,str(path)],
                      cwd=ROOT,capture_output=True,text=True,check=True,
                      timeout=90,env=dict(os.environ,PYTHONPATH=str(ROOT),
                                          PYTHONDONTWRITEBYTECODE="1"))
    require(cp.stdout.strip()=="CKAD_PORTFOLIO_COLD_PASS=256",
            "COLD_RESTORE")
    summary={}
    for condition,_ in CONDITIONS:
        group=[c for c in cases if c["condition"]==condition]
        arms={}
        for name in POLICIES+("audit",):
            selected=[c["arms"][name] for c in group]
            arms[name]={"effects":sum(a["effects"] for a in selected),
                        "worlds":len(group),
                        "native":{k:sum(a["native"][k] for a in selected)
                                  for k in ("correct","wrong","abstained","questions")}}
            if name in POLICIES:
                arms[name]["cart"]={k:sum(a["cart"][k] for a in selected)
                                   for k in ("correct","wrong","abstained","questions")}
                arms[name]["candidates_remaining"]=[a["candidate_count"]
                                                      for a in selected]
            else:
                arms[name]["admitted_worlds"]=sum(a["admitted"] for a in selected)
                arms[name]["contradictions"]=sum(a["contradictions"] for a in selected)
        summary[condition]={"worlds":len(group),"arms":arms}
    fam=[c for c in cases if c["condition"]=="IN_FAMILY"]
    def pair_gain(comp):
        diffs=[(c["arms"]["tournament"]["native"]["correct"]-
                c["arms"][comp]["native"]["correct"])/HELD_N for c in fam]
        return sum(diffs)/len(diffs),bootstrap_lower(diffs)
    rank_gain,rank_lower=pair_gain("rank2")
    rand_gain,rand_lower=pair_gain("random")
    p=summary["IN_FAMILY"]["arms"]["tournament"]["native"]
    def wrong_answered(con):
        z=summary[con]["arms"]["tournament"]["native"]
        return z["wrong"]/(z["wrong"]+z["correct"]) if z["wrong"]+z["correct"] else 0.0
    safety_shift=wrong_answered("SHIFT")
    safety_corrupt=wrong_answered("CORRUPT")
    gates={
        "gain_rank2_5pp":rank_gain>=0.05,
        "bootstrap_rank2_positive":rank_lower>0,
        "gain_random_5pp":rand_gain>=0.05,
        "bootstrap_random_positive":rand_lower>0,
        "familiar_coverage_60pct":10*p["correct"]>=6*p["questions"],
        "familiar_zero_wrong":p["wrong"]==0,
        "shift_wrong_answered_le5pct":safety_shift<=0.05,
        "corrupt_wrong_answered_le5pct":safety_corrupt<=0.05,
        "action_budget_equal":all(c["arms"][name]["effects"]==16
                                  for c in cases for name in POLICIES+("audit",)),
        "independent_symbolic_parity":True,
        "cumulative_cold_unchanged":True
    }
    return {"schema":"yggdrasil.ckad.portfolio-v1.result.v1",
            "classification":"CUMULATIVE_NATIVE_STRUCTURE_DEVELOPMENT_SUPPORTED"
              if all(gates.values()) else "CUMULATIVE_NATIVE_STRUCTURE_DEVELOPMENT_NO_GO",
            "scientific_pass":False,"accepted_native":False,
            "new_original_source_actions":0,"original_source_generators_called":0,
            "simulated_action_effects":sum(c["arms"][name]["effects"]
                 for c in cases for name in POLICIES+("audit",)),
            "worlds":len(cases),"cold_retained_world_models":256,
            "paired_gain_rank":rank_gain,"bootstrap_lower_rank":rank_lower,
            "paired_gain_random":rand_gain,"bootstrap_lower_random":rand_lower,
            "shift_wrong_answered_rate":safety_shift,
            "corrupt_wrong_answered_rate":safety_corrupt,
            "gates":gates,"summary":summary,"cases":cases,
            "memory_bytes":{p:v["bytes"] for p,v in checkpoints.items()},
            "arm_wall_seconds":arm_time,
            "whole_wall_seconds":time.perf_counter()-started}

def stable(x):
    if isinstance(x,dict):
        return {k:stable(v) for k,v in x.items()
                if k not in ("whole_wall_seconds","arm_wall_seconds",
                             "elapsed_seconds","environment","stable_sha256")}
    if isinstance(x,list):
        return [stable(a) for a in x]
    return x

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--verify-stable")
    opts=parser.parse_args()
    opts.out.mkdir(parents=True,exist_ok=True)
    result=execute(opts.out)
    result["environment"]={"python":platform.python_version(),
                           "platform":platform.platform()}
    result["stable_sha256"]=digest(canonical(stable(result)))
    if opts.verify_stable:
        require(result["stable_sha256"]==opts.verify_stable,
                "PLATFORM_STABLE_DRIFT")
    (opts.out/"result.json").write_bytes(canonical(result))
    receipt={"classification":result["classification"],"gates":result["gates"],
             "summary":result["summary"],
             "paired_gain_rank":result["paired_gain_rank"],
             "paired_gain_random":result["paired_gain_random"],
             "bootstrap_lower_rank":result["bootstrap_lower_rank"],
             "bootstrap_lower_random":result["bootstrap_lower_random"],
             "shift_wrong_rate":result["shift_wrong_answered_rate"],
             "corrupt_wrong_rate":result["corrupt_wrong_answered_rate"],
             "simulated_effects":result["simulated_action_effects"],
             "cold_models":result["cold_retained_world_models"]}
    print("CKAD_PORTFOLIO_STABLE_SHA256="+result["stable_sha256"],flush=True)
    print("CKAD_PORTFOLIO_RECEIPT="+canonical(receipt).decode("ascii"),flush=True)
