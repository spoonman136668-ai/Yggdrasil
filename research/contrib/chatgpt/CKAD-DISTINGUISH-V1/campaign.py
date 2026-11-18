"""CKAD-DISTINGUISH-V1: prospective simulated counterexplanation interventions.

A source-free comparison of equal-budget causal-action policies. Four
independent private fabricated source actors per world, each with 12 observed
effects. No original-source first-use; no hidden labels enter interventions.
The fitted shared causal gate is learned only from 16 training histories.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_hypothesis_portfolio import (
    NativeHypothesisPortfolio,GATES,grammar,votes,
    canonical,digest,SOURCE_MODE)
from yggdrasil.native_shared_operator_memory import (
    NativeSharedOperatorMemory,FULL_GATE_SUPPORT,program_scope)
from yggdrasil.native_context_basis import feature_row

FIT=tuple(range(1501,1517))
TRANSFER=tuple(range(1601,1633))
SHIFT=tuple(range(1701,1733))
CORRUPT=tuple(range(1801,1833))
REGIMES=(("TRANSFER",TRANSFER),("SHIFT",SHIFT),("CORRUPT",CORRUPT))
POLICIES=("target","ordinary_active","random","random_audit")
EXTRA_GATES=tuple(mask for mask in range(1,32) if mask.bit_count() in (1,2,3))
NARROW_GATES=GATES
BROAD_PROGRAMS=tuple((lin,gate,bias)
  for gate in EXTRA_GATES for lin in range(64) for bias in (0,1))
NARROW_PROGRAMS=tuple((lin,gate,bias)
  for gate in GATES for lin in range(64) for bias in (0,1))
VOTES=votes()
EFFECTS=12
FIT_EFFECTS=16
OBSERVABLE=32
HELD_COUNT=32

def require(condition,reason):
    if not condition:
        raise ValueError("CKAD_DISTINGUISH_V1_"+reason)

def key(label,*args):
    s="ckad-distinguish-v1:"+label+":"+":".join(str(v) for v in args)
    return hashlib.sha256(s.encode("ascii")).digest()

def split_masks():
    xs=sorted(range(64),key=lambda m:key("held",m))
    held=tuple(sorted(xs[:32]))
    pool=tuple(sorted(xs[32:],key=lambda m:key("initial",m)))
    require(len(held)==len(pool)==32 and not set(held)&set(pool),
            "SOURCE_SPLIT")
    return held,pool

def expr(mask,linear,gate,bias):
    """Independent arithmetic; does not inspect private world source."""
    return (((mask&linear).bit_count()&1) ^
            int(bool(mask&32) and (mask&gate)==gate)^bias)

class FabricatedSource:
    __slots__=("seed","regime","_params","_held","_pool",
               "_observed","_unlocked","calls","max_calls")
    def __init__(self,seed,regime,held,pool,max_calls):
        self.seed=seed
        self.regime=regime
        common=GATES[int.from_bytes(key("shared-gate")[:8],"big")%len(GATES)]
        if regime=="SHIFT":
            triples=tuple(g for g in EXTRA_GATES if g.bit_count()==3)
            gate=triples[int.from_bytes(key("shift-gate",seed)[:8],"big")%len(triples)]
        else:
            gate=common
        linear=int.from_bytes(key("world-linear",seed)[:8],"big")%64
        bias=key("world-bias",seed)[0]&1
        self._params=(linear,gate,bias)
        self._held=frozenset(held);self._pool=frozenset(pool)
        self._observed=set();self._unlocked=False
        self.calls=0;self.max_calls=max_calls
    def _effect(self,m):
        return expr(m,*self._params)
    def do(self,m):
        require(type(m) is int and m in self._pool and m not in self._held
                and m not in self._observed and not self._unlocked
                and self.calls<self.max_calls,"SOURCE_DO_BOUNDARY")
        self.calls+=1;self._observed.add(m)
        return self._effect(m)
    def reveal(self):
        require(self.calls==self.max_calls and not self._unlocked,
                "PREMATURE_HELD_RELEASE")
        self._unlocked=True
    def held(self,m):
        require(self._unlocked and m in self._held,"HIDDEN_HELD_ACCESS")
        return self._effect(m)
    def source_hash(self):
        # Only evidence recorder sees this, never any policy.
        return digest(canonical([self.seed,self.regime,self._params]))

def tamper(seed,inputs,labels):
    require(len(inputs)==len(labels)==4,"TAMPER_SCOPE")
    rank=sorted(range(4),key=lambda i:key("corrupt",seed,inputs[i]))
    mutated=list(labels)
    for i in rank[:2]:
        mutated[i]^=1
    return tuple(mutated)

def rank_add(basis,mask):
    value=feature_row(mask,2)
    while value:
        pivot=value.bit_length()-1
        if pivot not in basis:
            basis[pivot]=value;return True
        value^=basis[pivot]
    return False

def rank_choose(slot,observed,available):
    basis={}
    for m in observed:rank_add(basis,m)
    for m in sorted(available,key=lambda m:key("fit-rank",slot,m)):
        if rank_add(dict(basis),m):
            return m
    return min(available,key=lambda m:key("fit-fallback",slot,m))

def split_choose(slot,model,observed,pool):
    available=[m for m in pool if m not in observed]
    require(available,"ACTIVE_POOL_EMPTY")
    beliefs=model.candidate_bits(slot,True)
    total=beliefs.bit_count()
    def rank(m):
        one=(beliefs&VOTES[m]).bit_count()
        return (-min(one,total-one),key("narrow-active",slot,m),m)
    return min(available,key=rank)

def random_choose(seed,policy,observed,pool):
    allowed=[m for m in pool if m not in observed]
    return min(allowed,key=lambda m:key("random",seed,policy,m))

def enumerated(rows,programs):
    return [p for p in programs if all(expr(m,*p)==y for m,y in rows)]

def consensus(programs,m):
    if not programs:return None
    first=expr(m,*programs[0])
    return first if all(expr(m,*p)==first for p in programs) else None

def symbolic_narrow(rows,gate_mask):
    candidates=[p for p in NARROW_PROGRAMS
            if gate_mask&(1<<GATES.index(p[1]))]
    selected=enumerated(rows,candidates)
    return tuple(consensus(selected,m) for m in range(64)),len(selected)

def discriminate(slot,observed,possible,predicted):
    """Four input-only probes maximizing coverage of opposing explanations.

    The *only* program truth used is actual already witnessed public effects.
    Private source structure, held labels and future effects are unavailable.
    """
    pending=tuple(m for m in possible if m not in {x for x,_ in observed})
    require(len(pending)==24 and len(predicted)==64,"PREAUDIT_INPUTS")
    candidates=enumerated(observed,BROAD_PROGRAMS)
    covered=set();choices=[];scores=[]
    for _ in range(4):
        def rank(mask):
            narrow=predicted[mask]
            contrary={j for j,p in enumerate(candidates)
                      if narrow is not None and expr(mask,*p)!=narrow}
            novelty=len(contrary-covered)
            # If no narrow identification, conservatively seek broad split.
            positives=sum(expr(mask,*p) for p in candidates)
            split=min(positives,len(candidates)-positives)
            return (-int(narrow is not None),-novelty,-len(contrary),
                    -split,key("audit-action",slot,mask),mask),contrary
        scored=[rank(m) for m in pending if m not in choices]
        require(scored,"EXHAUSTED_AUDIT_POOL")
        priority,alternative=min(scored,key=lambda pair:pair[0])
        mask=priority[-1]
        novelty=len(alternative-covered)
        choices.append(mask);covered.update(alternative)
        scores.append({"mask":mask,"identified_at_8":predicted[mask] is not None,
                       "opposing_programs":len(alternative),
                       "newly_distinguished_programs":novelty})
    require(len(set(choices))==4,"DUPLICATE_AUDIT_MASK")
    return tuple(choices),{"preaudit_broad_programs":len(candidates),
                           "opposing_coverage":len(covered),
                           "input_only":True,"future_effects_read":0,
                           "chosen":list(choices),"score_trace":scores}

def witness(model,slot,mask,outcome):
    return model.observe(slot,mask,outcome,
            digest(canonical([slot,mask,outcome,SOURCE_MODE])))

def train(held,pool):
    model=NativeSharedOperatorMemory()
    trace=[];start=time.perf_counter()
    for slot,seed in enumerate(FIT):
        actor=FabricatedSource(seed,"FIT",held,pool,FIT_EFFECTS)
        used=[];labels=[]
        for m in pool[:8]:
            y=actor.do(m);model=witness(model,slot,m,y)
            used.append(m);labels.append(y)
        for _ in range(8):
            m=rank_choose(slot,used,[x for x in pool if x not in used])
            y=actor.do(m);model=witness(model,slot,m,y)
            used.append(m);labels.append(y)
        model=model.seal_fit_world(slot)
        require(actor.calls==16,"FIT_BUDGET")
        trace.append({"world":slot,"seed":seed,
           "source_sha256":actor.source_hash(),
           "observed_input_sha256":digest(canonical(used)),
           "observed_outcome_sha256":digest(canonical(labels)),
           "remaining_shared_gates":model.global_gate_support.bit_count()})
    model=model.freeze()
    require(model.fit_worlds==16 and model.global_gate_support>0,
            "FIT_GLOBAL")
    return model,trace,time.perf_counter()-start

def cart_predict(seed,rows):
    from sklearn.tree import DecisionTreeClassifier
    x=[[(m>>bit)&1 for bit in range(6)] for m,_ in rows]
    y=[label for _,label in rows]
    tree=DecisionTreeClassifier(max_depth=None,min_samples_leaf=1,
        criterion="gini",random_state=seed)
    tree.fit(x,y)
    require(list(tree.predict(x))==y,"CONVENTIONAL_NOT_FITTED")
    return tuple(int(t) for t in tree.predict(
        [[(m>>bit)&1 for bit in range(6)] for m in range(64)]))

def metrics(pred,held,truth):
    v=[pred[m] for m in held]
    good=sum(x is not None and x==y for x,y in zip(v,truth))
    bad=sum(x is not None and x!=y for x,y in zip(v,truth))
    return {"correct":good,"wrong":bad,"abstained":32-good-bad,
            "questions":32,"answers_sha256":digest(canonical(v))}

def evaluate(seed,regime,slot,prior_states,held,pool):
    original_global=prior_states["target"].global_gate_support
    require(all(v.global_gate_support==original_global for v in prior_states.values()),
            "POLICY_PRIOR_DRIFT")
    states=dict(prior_states)
    actors={name:FabricatedSource(seed,regime,held,pool,EFFECTS)
            for name in POLICIES}
    witnessed={name:[] for name in POLICIES}
    effects={name:[] for name in POLICIES}
    t0=time.perf_counter()
    init=pool[:4]
    for m in init:
        y={name:actor.do(m) for name,actor in actors.items()}
        require(len(set(y.values()))==1,"ACTOR_INITIAL_TRUTH_DRIFT")
        for name in POLICIES:effects[name].append(y[name])
    common=(tamper(seed,init,effects["target"]) if regime=="CORRUPT"
            else tuple(effects["target"]))
    for name in POLICIES:
        for m,y in zip(init,common):
            states[name]=witness(states[name],slot,m,y)
            witnessed[name].append((m,y))
    # Next four effect calls: target/ordinary_active/random_audit have
    # exactly the same actions and public effects; random explores independently.
    for _ in range(4):
        chosen={}
        for name in POLICIES:
            used=[m for m,_ in witnessed[name]]
            if name=="random":
                m=random_choose(seed,"random",used,pool)
            else:
                m=split_choose(slot,states[name],used,pool)
            chosen[name]=m
        require(chosen["target"]==chosen["ordinary_active"]==
                chosen["random_audit"],"IDENTICAL_EIGHT_PREFIX")
        for name,m in chosen.items():
            y=actors[name].do(m)
            states[name]=witness(states[name],slot,m,y)
            witnessed[name].append((m,y))
    frozen={name:states[name].vector(slot) for name in POLICIES}
    require(frozen["target"]==frozen["random_audit"]==
            frozen["ordinary_active"],"FROZEN_PREFIX_PARITY")
    # Broadened hypothesis bank from publicly witnessed target outcomes only.
    pre_broad=enumerated(witnessed["target"],BROAD_PROGRAMS)
    proposals,trace=discriminate(slot,witnessed["target"],pool,frozen["target"])
    require(trace["preaudit_broad_programs"]==len(pre_broad),
            "BROADER_CANDIDATE_COUNT")
    audit_random=tuple(sorted(
        [m for m in pool if m not in [x for x,_ in witnessed["random_audit"]]],
        key=lambda m:key("random-audit",seed,m))[:4])
    require(len(audit_random)==len(proposals)==4,"POSTFIT_ACTION_COUNT")
    selection_time=time.perf_counter()-t0
    for i in range(4):
        for name in POLICIES:
            used=[m for m,_ in witnessed[name]]
            if name=="target":
                m=proposals[i]
            elif name=="random_audit":
                m=audit_random[i]
            elif name=="ordinary_active":
                m=split_choose(slot,states[name],used,pool)
            else:
                m=random_choose(seed,"random",used,pool)
            y=actors[name].do(m)
            states[name]=witness(states[name],slot,m,y)
            witnessed[name].append((m,y))
    require(all(actor.calls==EFFECTS for actor in actors.values()),
            "EQUAL_SOURCE_CALLS")
    for name in POLICIES:
        require(states[name].global_gate_support==original_global
                and len(witnessed[name])==12 and
                len({m for m,_ in witnessed[name]})==12,
                "EVAL_MEMORY_OR_DUPLICATE")
    identified={}
    contradictions={}
    admitted={}
    for name in ("target","random_audit"):
        checks=[(frozen[name][m],y)
                for m,y in witnessed[name][8:]]
        identified[name]=sum(p is not None for p,y in checks)
        contradictions[name]=sum(p is not None and p!=y for p,y in checks)
        admitted[name]=(identified[name]==4 and contradictions[name]==0
             and states[name].count(slot,True)>0)
    predicted={}
    for name in POLICIES:
        unfiltered=states[name].vector(slot)
        predicted[name]=(unfiltered
          if name in ("ordinary_active","random") or admitted[name]
          else (None,)*64)
    predicted["no_memory_matched"]=states["target"].vector(slot,False)
    independent,correct_count=symbolic_narrow(
        witnessed["target"],original_global)
    require(independent==states["target"].vector(slot)
            and correct_count==states["target"].count(slot,True),
            "EXACT_INDEPENDENT_SYMBOLIC_PARITY")
    predicted["independent_symbolic"]=(
        independent if admitted["target"] else (None,)*64)
    post_broad=enumerated(witnessed["target"],BROAD_PROGRAMS)
    predicted["broad_conservative"]=tuple(
        consensus(post_broad,m) for m in range(64))
    cart_start=time.perf_counter()
    for name in POLICIES:
        predicted["CART_"+name]=cart_predict(seed,witnessed[name])
    cart_time=time.perf_counter()-cart_start
    require(all(not actor._unlocked for actor in actors.values()),
            "HELD_PREMATURE")
    for actor in actors.values():actor.reveal()
    truth=tuple(actors["target"].held(m) for m in held)
    require(all(tuple(a.held(m) for m in held)==truth
                for a in actors.values()),"ACTOR_HELD_PARITY")
    scores={name:metrics(vec,held,truth) for name,vec in predicted.items()}
    actor_receipts={name:{
         "source_effect_calls":actors[name].calls,
         "observed_mask_sha256":digest(canonical([m for m,_ in witnessed[name]])),
         "observed_effect_sha256":digest(canonical([y for _,y in witnessed[name]])),
         "candidate_count":states[name].count(slot,True)}
         for name in POLICIES}
    return states,{
       "seed":seed,"regime":regime,"slot":slot,
       "source_sha256":actors["target"].source_hash(),
       "held_mask_sha256":digest(canonical(held)),
       "held_outcome_sha256":digest(canonical(truth)),
       "scores":scores,"actors":actor_receipts,
       "shared_first_eight_sha256":digest(canonical(witnessed["target"][:8])),
       "target_audit":{**trace,
           "identified":identified["target"],"contradictions":contradictions["target"],
           "admitted":admitted["target"],
           "source_effect_calls":4,
           "audited_masks_sha256":digest(canonical(proposals))},
       "random_audit":{"identified":identified["random_audit"],
           "contradictions":contradictions["random_audit"],
           "admitted":admitted["random_audit"],
           "audited_masks_sha256":digest(canonical(audit_random))},
       "broad_programs_after_twelve":len(post_broad),
       "timings":{"selection_seconds":selection_time,
          "conventional_CART_seconds":cart_time}
    }

def boot_lower(differences):
    require(len(differences)==32,"BOOTSTRAP_N")
    estimates=[]
    for iteration in range(1000):
        total=0
        for j in range(32):
            i=int.from_bytes(key("bootstrap",iteration,j)[:8],"big")%32
            total+=differences[i]
        estimates.append(total/32)
    return sorted(estimates)[24]

def run(out):
    held,pool=split_masks()
    started=time.perf_counter()
    trained,fit_receipts,fit_seconds=train(held,pool)
    gate=trained.global_gate_support
    baseline_vectors=tuple(trained.vector(i) for i in range(16))
    baseline_checkpoint_sha=digest(trained.checkpoint())
    cases=[];models={}
    for regime,seeds in REGIMES:
        # Each regime starts with identical frozen FIT state; no negative
        # cohort contaminates other evaluation cohorts' learned memory.
        states={name:trained for name in POLICIES}
        for i,seed in enumerate(seeds):
            slot=16+i
            states,record=evaluate(seed,regime,slot,states,
                                   held,pool)
            for name in POLICIES:
                require(all(states[name].vector(j)==baseline_vectors[j]
                            for j in range(16)),"COLD_FIT_INTERFERENCE")
                require(states[name].global_gate_support==gate,
                        "FIT_SHARED_MEMORY_DRIFT")
            cases.append(record)
        for name,state in states.items():
            raw=state.checkpoint()
            models[regime+":"+name]={
                "checkpoint_ascii":raw.decode("ascii"),
                "sha256":digest(raw),
                "readouts_sha256":digest(canonical([state.vector(i) for i in range(48)]))}
    require(len(cases)==96 and len(models)==12,"COHORT_ACCOUNTING")
    bundle=out/"native-checkpoint-bundle.json"
    bundle.write_bytes(canonical({"schema":"ckad.distinguish.v1.cold.bundle",
                                  "models":models}))
    cold_code="""import json,sys
from pathlib import Path
from yggdrasil.native_shared_operator_memory import NativeSharedOperatorMemory
from yggdrasil.native_hypothesis_portfolio import canonical,digest
a=json.loads(Path(sys.argv[1]).read_bytes())
for name,item in a['models'].items():
    raw=item['checkpoint_ascii'].encode('ascii')
    assert digest(raw)==item['sha256']
    restored=NativeSharedOperatorMemory.restore(raw,item['sha256'])
    assert digest(canonical([restored.vector(i) for i in range(48)]))==item['readouts_sha256']
print('CKAD_DISTINGUISH_V1_COLD_PASS='+str(len(a['models'])))"""
    proc=subprocess.run([sys.executable,"-B","-c",cold_code,str(bundle)],
        cwd=ROOT,check=True,capture_output=True,text=True,timeout=90,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    require(proc.stdout.strip()=="CKAD_DISTINGUISH_V1_COLD_PASS=12",
            "COLD_RESTORE")
    totals={}
    for regime,seeds in REGIMES:
        rows=[c for c in cases if c["regime"]==regime]
        require(len(rows)==len(seeds),"COHORT_SIZE")
        method_names=tuple(rows[0]["scores"])
        arms={name:{k:sum(c["scores"][name][k] for c in rows)
               for k in ("correct","wrong","abstained","questions")}
              for name in method_names}
        totals[regime]={
           "worlds":len(rows),"arms":arms,
           "target_admissions":sum(c["target_audit"]["admitted"] for c in rows),
           "random_audit_admissions":sum(c["random_audit"]["admitted"] for c in rows),
           "target_contradictions":sum(c["target_audit"]["contradictions"] for c in rows),
           "random_contradictions":sum(c["random_audit"]["contradictions"] for c in rows),
           "target_identified_checks":sum(c["target_audit"]["identified"] for c in rows)}
    trans=[x for x in cases if x["regime"]=="TRANSFER"]
    differences=[(x["scores"]["target"]["correct"]-
                  x["scores"]["random_audit"]["correct"])/32
                 for x in trans]
    diff=sum(differences)/len(differences)
    lower=boot_lower(differences)
    shifted=totals["SHIFT"]["arms"]["target"]
    corrupt=totals["CORRUPT"]["arms"]["target"]
    transfer=totals["TRANSFER"]["arms"]["target"]
    error=lambda z:z["wrong"]/(z["correct"]+z["wrong"]) if z["correct"]+z["wrong"] else 1.0
    totalwrong=shifted["wrong"]+corrupt["wrong"]
    normalwrong=sum(totals[g]["arms"]["ordinary_active"]["wrong"]
                     for g in ("SHIFT","CORRUPT"))
    negatives_have_answers=(shifted["correct"]+shifted["wrong"]+
                            corrupt["correct"]+corrupt["wrong"])>0
    gates={
       "negative_wrong_reduction_90pct":
          normalwrong>0 and totalwrong*10<=normalwrong,
       "shift_wrong_answered_le5pct":error(shifted)<=0.05,
       "corrupt_wrong_answered_le5pct":error(corrupt)<=0.05,
       "negative_meaningful_coverage_30pct":
          max(shifted["correct"]+shifted["wrong"],
              corrupt["correct"]+corrupt["wrong"])>=308,
       "transfer_correct_75pct":transfer["correct"]>=768,
       "transfer_zero_wrong":transfer["wrong"]==0,
       "transfer_vs_random_audit_lower_loss_le5pp":lower>=-0.05,
       "12_effects_each":all(a["source_effect_calls"]==12
            for c in cases for a in c["actors"].values()),
       "no_original_actions":True,
       "native_independent_symbolic_parity":True,
       "cold_memory_retention":True}
    return {
       "schema":"yggdrasil.ckad.distinguishing.v1.result",
       "classification":"COUNTEREXPLANATION_INTERVENTIONS_DEV_SUPPORTED"
          if all(gates.values()) else "COUNTEREXPLANATION_INTERVENTIONS_DEV_NO_GO",
       "scientific_pass":False,"accepted_native":False,
       "original_source_actions":0,"original_first_use":False,
       "new_synthetic_source_calls":16*16+96*4*12,
       "fit_worlds":16,"evaluation_worlds":96,
       "cold_models":len(models),"learned_shared_gate_count":gate.bit_count(),
       "learned_gate_mask":gate,"fit_prior_sha256":baseline_checkpoint_sha,
       "fit_receipts":fit_receipts,"fit_seconds":fit_seconds,
       "transfer_vs_random_audit_gain":diff,"bootstrap_lower_95":lower,
       "gates":gates,"cohorts":totals,"cases":cases,
       "total_checkpoint_bytes":bundle.stat().st_size,
       "whole_wall_seconds":time.perf_counter()-started}

def stable_view(data):
    if isinstance(data,dict):
        return {k:stable_view(v) for k,v in data.items()
                if k not in ("whole_wall_seconds","fit_seconds","timings","environment","stable_sha256")}
    if isinstance(data,list):
        return [stable_view(x) for x in data]
    return data

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--expected-stable")
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    receipt=run(args.out)
    receipt["environment"]={"python":platform.python_version(),
                            "platform":platform.platform()}
    stable=digest(canonical(stable_view(receipt)))
    receipt["stable_sha256"]=stable
    if args.expected_stable:
        require(stable==args.expected_stable,"CROSS_PLATFORM_DRIFT")
    (args.out/"result.json").write_bytes(canonical(receipt))
    print("CKAD_DISTINGUISH_V1_STABLE="+stable,flush=True)
    print("CKAD_DISTINGUISH_V1_SUMMARY="+canonical({
      "classification":receipt["classification"],"cohorts":receipt["cohorts"],
      "gates":receipt["gates"],"lower":receipt["bootstrap_lower_95"],
      "cold_models":receipt["cold_models"],
      "source_calls":receipt["new_synthetic_source_calls"]}).decode("ascii"),flush=True)
