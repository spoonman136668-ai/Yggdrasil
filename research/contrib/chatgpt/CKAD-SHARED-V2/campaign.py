"""CKAD-SHARED-V2: source-free cumulative operator-level causal transfer.

A private shared gate is learned *from separate public consequence histories*.
Per-world XOR/bias change; program class is supplied, correct gate is NOT.
All labels are synthetic, source-owner first-use and original actions = ZERO.
"""
import argparse
import hashlib
import importlib.util
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
    NativeHypothesisPortfolio,GATES,grammar,canonical,digest,SOURCE_MODE,
    evaluate_program,votes)
from yggdrasil.native_shared_operator_memory import (
    NativeSharedOperatorMemory,FIT_WORLDS,FULL_GATE_SUPPORT,
    gate_support,program_scope,unanimous)
from yggdrasil.native_context_basis import feature_row

TRAIN=tuple(range(701,717))
TRANSFER=tuple(range(717,733))
SHIFT=tuple(range(801,817))
CORRUPT=tuple(range(901,917))
REGIMES=(("TRANSFER",TRANSFER),("SHIFT",SHIFT),("CORRUPT",CORRUPT))
HELD=32
INITIAL_TRAIN=8
EXTRA_TRAIN=8
INITIAL_EVAL=4
EXTRA_EVAL=4
ALL_INPUTS=64

def require(ok,code):
    if not ok:
        raise ValueError("CKAD_SHARED_V2_"+code)

def hash_key(label,*parts):
    text="ckad-shared-v2:"+label+":" + ":".join(str(x) for x in parts)
    return hashlib.sha256(text.encode("ascii")).digest()

def held_split():
    order=sorted(range(ALL_INPUTS),key=lambda x:hash_key("held",x))
    held=tuple(sorted(order[:HELD]))
    pool=tuple(sorted(order[HELD:],key=lambda x:hash_key("initial",x)))
    require(len(set(held))==len(set(pool))==32 and
            not(set(held)&set(pool)),"INPUT_SPLIT")
    return held,pool

def source_truth(seed,regime):
    """Only fabricated source actor may access the private selected program."""
    shared=GATES[int.from_bytes(hash_key("shared-gate")[:8],"big")%len(GATES)]
    if regime=="SHIFT":
        triple=tuple(x for x in range(1,32) if x.bit_count()==3)
        gate=triple[int.from_bytes(hash_key("shift-gate",seed)[:8],"big")%len(triple)]
    else:
        gate=shared
    linear=int.from_bytes(hash_key("world-linear",seed)[:8],"big")%64
    bias=hash_key("world-bias",seed)[0]&1
    return linear,gate,bias

class SimulatedWorld:
    __slots__=("seed","regime","_parameters","_held","_pool","_used",
               "_evaluation_unlocked","budget","calls")
    def __init__(self,seed,regime,held,pool,budget):
        self.seed=seed
        self.regime=regime
        self._parameters=source_truth(seed,regime)
        self._held=frozenset(held)
        self._pool=frozenset(pool)
        self._used=set()
        self._evaluation_unlocked=False
        self.budget=budget
        self.calls=0

    def _truth(self,mask):
        linear,gate,bias=self._parameters
        return evaluate_program(mask,linear,gate,bias)

    def effect(self,mask):
        require(type(mask) is int and mask in self._pool
                and mask not in self._held and mask not in self._used
                and self.calls<self.budget and not self._evaluation_unlocked,
                "EFFECT_BOUNDARY")
        self._used.add(mask)
        self.calls+=1
        return self._truth(mask)

    def unlock_held(self):
        require(not self._evaluation_unlocked and self.calls==self.budget,
                "PREMATURE_HELD_UNLOCK")
        self._evaluation_unlocked=True

    def held_truth(self,mask):
        require(self._evaluation_unlocked and mask in self._held,
                "HELD_NOT_RELEASED")
        return self._truth(mask)

    def identity(self):
        return digest(canonical((self.seed,self.regime,self._parameters)))

def corruption(seed,masks,labels):
    require(len(masks)==len(labels)==4,"CORRUPT_FIT_INPUT")
    order=sorted(range(4),key=lambda i:hash_key("corrupt",seed,masks[i]))
    out=list(labels)
    for i in order[:2]:
        out[i]^=1
    return tuple(out)

def rank_add(basis,mask):
    val=feature_row(mask,2)
    while val:
        p=val.bit_length()-1
        if p not in basis:
            basis[p]=val
            return True
        val ^= basis[p]
    return False

def input_rank_choose(slot,seen,remaining):
    basis={}
    for mask in seen:
        rank_add(basis,mask)
    ordered=sorted(remaining,key=lambda m:hash_key("rank",slot,m))
    for m in ordered:
        if rank_add(dict(basis),m):
            return m
    return ordered[0]

def split_choose(slot,remaining,bank):
    require(len(remaining)>0 and bank>=0,"CHOOSER")
    count=bank.bit_count()
    best=None
    ballot=votes()
    for m in remaining:
        n=(bank&ballot[m]).bit_count()
        score=min(n,count-n)
        order=(-score,hash_key("split",slot,m),m)
        if best is None or order<best:
            best=order
    return best[-1]

def independent_program(linear,gate,bias,mask):
    """Separate arithmetic, no native state/bitset/votes call."""
    return (((mask&linear).bit_count()&1)
            ^int(bool(mask&32) and (mask&gate)==gate)^bias)

def independent_gate_support(histories):
    """Complete explicit per-world enumeration, not native support bitsets."""
    allowed=set(GATES)
    for rows in histories:
        world_gates=set()
        for gate in GATES:
            found=False
            for linear in range(64):
                for bias in (0,1):
                    if all(independent_program(linear,gate,bias,m)==y
                           for m,y in rows):
                        found=True
                        break
                if found:break
            if found:
                world_gates.add(gate)
        allowed &= world_gates
    return sum(1<<i for i,g in enumerate(GATES) if g in allowed)

def independent_predictions(rows,allowed_gate_mask):
    options=[]
    for index,gate in enumerate(GATES):
        if not (allowed_gate_mask&(1<<index)):
            continue
        for linear in range(64):
            for bias in (0,1):
                if all(independent_program(linear,gate,bias,m)==y
                       for m,y in rows):
                    options.append((linear,gate,bias))
    prediction=[]
    for m in range(64):
        if not options:
            prediction.append(None)
            continue
        first=independent_program(*options[0],m)
        prediction.append(first if all(independent_program(*q,m)==first
                                       for q in options) else None)
    return tuple(prediction),len(options)

def cart_predict(seed,rows):
    from sklearn.tree import DecisionTreeClassifier
    x=[[((m>>i)&1) for i in range(6)] for m,_ in rows]
    y=[v for _,v in rows]
    tree=DecisionTreeClassifier(criterion="gini",random_state=seed,
                                max_depth=None,min_samples_leaf=1)
    tree.fit(x,y)
    require(list(tree.predict(x))==y,"CART_NOT_FULLY_FITTED")
    return tuple(int(v) for v in tree.predict(
        [[((m>>i)&1) for i in range(6)] for m in range(64)]))

def score(pred,held,truth):
    vals=[pred[m] for m in held]
    correct=sum(p is not None and p==y for p,y in zip(vals,truth))
    wrong=sum(p is not None and p!=y for p,y in zip(vals,truth))
    return {"correct":correct,"wrong":wrong,
            "abstained":len(held)-correct-wrong,"questions":len(held),
            "answers_sha256":digest(canonical(vals))}

def bootstrap_lower(deltas):
    require(len(deltas)==16,"BOOTSTRAP_WORLD_COUNT")
    outputs=[]
    for rep in range(1000):
        values=[]
        for index in range(16):
            chosen=int.from_bytes(hash_key("bootstrap",rep,index)[:8],"big")%16
            values.append(deltas[chosen])
        outputs.append(sum(values)/16)
    return sorted(outputs)[24]

def train_shared(held,pool):
    model=NativeSharedOperatorMemory()
    histories=[]
    receipt=[]
    for slot,seed in enumerate(TRAIN):
        actor=SimulatedWorld(seed,"FIT",held,pool,16)
        observed=[]
        rows=[]
        for mask in pool[:INITIAL_TRAIN]:
            y=actor.effect(mask)
            model=model.observe(slot,mask,y,
                digest(canonical([slot,mask,y,SOURCE_MODE])))
            observed.append(mask)
            rows.append((mask,y))
        for _ in range(EXTRA_TRAIN):
            remain=[m for m in pool if m not in observed]
            mask=input_rank_choose(slot,observed,remain)
            y=actor.effect(mask)
            model=model.observe(slot,mask,y,
                digest(canonical([slot,mask,y,SOURCE_MODE])))
            observed.append(mask)
            rows.append((mask,y))
        model=model.seal_fit_world(slot)
        require(actor.calls==16,"FIT_ACTION_COST")
        histories.append(tuple(rows))
        receipt.append({"seed":seed,"slot":slot,
                        "source_sha256":actor.identity(),
                        "action_sha256":digest(canonical(observed)),
                        "outcome_sha256":digest(canonical([v for _,v in rows])),
                        "global_gate_count":model.global_gate_support.bit_count(),
                        "native_candidate_count":model.count(slot,False)})
        # No original or simulated FIT held-out queries consumed.
        require(not actor._evaluation_unlocked,"FIT_HELD_UNUSED")
    model=model.freeze()
    independent=independent_gate_support(histories)
    require(independent==model.global_gate_support and independent>0,
            "INDEPENDENT_TRAIN_GATE_PARITY")
    frozen_vectors=tuple(model.vector(i) for i in range(16))
    return model,histories,receipt,frozen_vectors

def evaluate_world(seed,regime,slot,held,pool,trained):
    actors={name:SimulatedWorld(seed,regime,held,pool,8)
            for name in ("target","no_memory_active","shared_random")}
    rows={name:[] for name in actors}
    models={}
    shared_target=trained
    naked=NativeHypothesisPortfolio()
    shared_random=trained
    initial=pool[:INITIAL_EVAL]
    for mask in initial:
        effects={name:actor.effect(mask) for name,actor in actors.items()}
        require(len(set(effects.values()))==1,"ACTOR_INITIAL_MISMATCH")
        for name in actors:
            y=effects[name]
            if regime=="CORRUPT":
                # Corruption is applied only after exactly four true effects.
                rows[name].append((mask,y))
            else:
                rows[name].append((mask,y))
    if regime=="CORRUPT":
        for name in actors:
            labels=corruption(seed,initial,[y for _,y in rows[name]])
            rows[name]=list(zip(initial,labels))
    for name in actors:
        for mask,y in rows[name]:
            receipt=digest(canonical([slot,mask,y,SOURCE_MODE]))
            if name=="target":
                shared_target=shared_target.observe(slot,mask,y,receipt)
            elif name=="no_memory_active":
                naked=naked.observe(slot,mask,y,receipt)
            else:
                shared_random=shared_random.observe(slot,mask,y,receipt)
    for _ in range(EXTRA_EVAL):
        for name,actor in actors.items():
            observed=[m for m,_ in rows[name]]
            remain=[m for m in pool if m not in observed]
            if name=="target":
                mask=split_choose(slot,remain,shared_target.candidate_bits(slot,True))
            elif name=="no_memory_active":
                mask=split_choose(slot,remain,naked._state(slot)[0])
            else:
                mask=min(remain,key=lambda m:hash_key("random",slot,m))
            y=actor.effect(mask)
            rows[name].append((mask,y))
            receipt=digest(canonical([slot,mask,y,SOURCE_MODE]))
            if name=="target":
                shared_target=shared_target.observe(slot,mask,y,receipt)
            elif name=="no_memory_active":
                naked=naked.observe(slot,mask,y,receipt)
            else:
                shared_random=shared_random.observe(slot,mask,y,receipt)
    require(all(actor.calls==8 for actor in actors.values()),
            "MATCHED_EIGHT_EFFECTS")
    vectors={
       "shared":shared_target.vector(slot,True),
       "no_memory_matched":shared_target.vector(slot,False),
       "no_memory_active":naked.vector(slot),
       "shared_random":shared_random.vector(slot,True)}
    rotated=sum(1<<((i+7)%15) for i in range(15)
                if trained.global_gate_support&(1<<i))
    vectors["rotated_prior"]=shared_target.vector(slot,True,rotated)
    independent,compatible=independent_predictions(
        rows["target"],trained.global_gate_support)
    require(vectors["shared"]==independent and compatible==
            shared_target.count(slot,True),"INDEPENDENT_TARGET_PARITY")
    no_memory_independent,_=independent_predictions(rows["target"],(1<<15)-1)
    require(no_memory_independent==vectors["no_memory_matched"],
            "INDEPENDENT_MEMORY_ABLATION_PARITY")
    vectors["independent_symbolic"]=independent
    vectors["CART"]=cart_predict(seed,rows["target"])
    require(all(not actor._evaluation_unlocked for actor in actors.values()),
            "HELD_PEEK")
    for actor in actors.values():
        actor.unlock_held()
    truth=tuple(actors["target"].held_truth(m) for m in held)
    require(all(tuple(actor.held_truth(m) for m in held)==truth
                for actor in actors.values()),"ACTOR_HELD_DRIFT")
    metrics={name:score(vec,held,truth) for name,vec in vectors.items()}
    log={name:{"effects":actors[name].calls,
               "input_sha256":digest(canonical([x for x,_ in rows[name]])),
               "witnessed_outcome_sha256":digest(canonical([y for _,y in rows[name]]))}
         for name in actors}
    return shared_target,{
       "slot":slot,"seed":seed,"regime":regime,
       "source_sha256":actors["target"].identity(),
       "held_input_sha256":digest(canonical(held)),
       "held_outcome_sha256":digest(canonical(truth)),
       "candidate_count":shared_target.count(slot,True),
       "raw_candidate_count":shared_target.count(slot,False),
       "trained_global_gates":trained.global_gate_support.bit_count(),
       "metrics":metrics,"charged_actors":log}

def run(output):
    held,pool=held_split()
    begun=time.perf_counter()
    shared,history,fit_receipts,pretrained_vectors=train_shared(held,pool)
    frozen_sha=digest(shared.checkpoint())
    frozen_gates=shared.global_gate_support
    cases=[]
    for regime,seeds in REGIMES:
        for seed in seeds:
            slot=16+len(cases)
            shared,case=evaluate_world(seed,regime,slot,held,pool,shared)
            require(shared.global_gate_support==frozen_gates
                    and shared.fit_worlds==16
                    and all(shared.vector(i)==pretrained_vectors[i]
                            for i in range(16)),"COLD_RETENTION_INTERFERENCE")
            cases.append(case)
    require(len(cases)==48 and all(len(c["charged_actors"])==3
            and all(x["effects"]==8 for x in c["charged_actors"].values())
            for c in cases),"EVAL_ACTION_ACCOUNTING")
    raw=shared.checkpoint()
    checkpoint=output/"native-shared-checkpoint.json"
    checkpoint.write_bytes(canonical({
        "schema":"ckad.shared-v2.native-checkpoint-bundle.v1",
        "native_ascii":raw.decode("ascii"),"checkpoint_sha256":digest(raw),
        "all_world_vector_sha256":digest(canonical([shared.vector(i) for i in range(64)])),
        "fit_global_gate_mask":frozen_gates}))
    script="""import json,sys
from pathlib import Path
from yggdrasil.native_shared_operator_memory import NativeSharedOperatorMemory
from yggdrasil.native_hypothesis_portfolio import canonical,digest
d=json.loads(Path(sys.argv[1]).read_bytes())
raw=d["native_ascii"].encode("ascii")
m=NativeSharedOperatorMemory.restore(raw,d["checkpoint_sha256"])
assert m.global_gate_support==d["fit_global_gate_mask"]
vec=[m.vector(i) for i in range(64)]
assert digest(canonical(vec))==d["all_world_vector_sha256"]
print("CKAD_SHARED_V2_COLD_RETAINED=64")"""
    cold=subprocess.run([sys.executable,"-B","-c",script,str(checkpoint)],
           cwd=ROOT,capture_output=True,text=True,check=True,timeout=90,
           env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    require(cold.stdout.strip()=="CKAD_SHARED_V2_COLD_RETAINED=64",
            "COLD_CHECKPOINT")
    names=("shared","no_memory_matched","no_memory_active",
           "shared_random","rotated_prior","independent_symbolic","CART")
    summary={}
    for regime,_ in REGIMES:
        rows=[c for c in cases if c["regime"]==regime]
        arms={name:{metric:sum(row["metrics"][name][metric] for row in rows)
                    for metric in ("correct","wrong","abstained","questions")}
              for name in names}
        summary[regime]={"worlds":len(rows),"arms":arms}
    in_family=[c for c in cases if c["regime"]=="TRANSFER"]
    deltas=[(c["metrics"]["shared"]["correct"]-
             c["metrics"]["no_memory_matched"]["correct"])/32
            for c in in_family]
    gain=sum(deltas)/len(deltas)
    lower=bootstrap_lower(deltas)
    transfer=summary["TRANSFER"]["arms"]["shared"]
    shift=summary["SHIFT"]["arms"]["shared"]
    corrupt=summary["CORRUPT"]["arms"]["shared"]
    def wrong_answered(a):
        count=a["wrong"]+a["correct"]
        return a["wrong"]/count if count else 0.0
    gates={
      "transfer_gain_10pp":gain>=0.10,
      "paired_bootstrap_lower_positive":lower>0,
      "transfer_correct_60pct":transfer["correct"]>=308,
      "transfer_zero_wrong":transfer["wrong"]==0,
      "shift_wrong_answered_le5pct":wrong_answered(shift)<=0.05,
      "corrupt_wrong_answered_le5pct":wrong_answered(corrupt)<=0.05,
      "independent_shared_symbolic_parity":True,
      "cold_training_retention":True,
      "matched_effect_calls":True}
    return {
       "schema":"yggdrasil.ckad.shared-v2.result.v1",
       "classification":"SHARED_OPERATOR_DEV_SUPPORTED"
        if all(gates.values()) else "SHARED_OPERATOR_DEV_NO_GO",
       "scientific_pass":False,"accepted_native":False,
       "original_source_actions":0,"original_first_use":False,
       "worlds_total":64,"fit_worlds":16,"evaluation_worlds":48,
       "fit_sourcefree_effects":16*16,"evaluation_sourcefree_effects":48*3*8,
       "total_sourcefree_effects":16*16+48*3*8,
       "global_fit_gate_count":frozen_gates.bit_count(),
       "global_fit_gate_mask":frozen_gates,
       "global_fit_gate_sha256":digest(canonical(frozen_gates)),
       "candidate_grammar":1920,"training_memory_bytes":len(raw),
       "cold_retained_worlds":64,
       "paired_gain":gain,"bootstrap_lower_95":lower,
       "wrong_answered_shift":wrong_answered(shift),
       "wrong_answered_corrupt":wrong_answered(corrupt),
       "gates":gates,"summary":summary,"fit_receipts":fit_receipts,
       "fit_history_sha256":digest(canonical(history)),
       "frozen_pretransfer_checkpoint_sha256":frozen_sha,
       "cases":cases,"whole_wall_seconds":time.perf_counter()-begun}

def stable_view(obj):
    if isinstance(obj,dict):
        return {k:stable_view(v) for k,v in obj.items()
                if k not in ("whole_wall_seconds","environment","stable_sha256")}
    if isinstance(obj,list):
        return [stable_view(x) for x in obj]
    return obj

if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",required=True,type=Path)
    arg.add_argument("--expected-stable")
    args=arg.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    result=run(args.out)
    result["environment"]={"platform":platform.platform(),
                           "python":platform.python_version()}
    receipt=digest(canonical(stable_view(result)))
    result["stable_sha256"]=receipt
    if args.expected_stable:
        require(receipt==args.expected_stable,"CROSS_PLATFORM_DRIFT")
    (args.out/"result.json").write_bytes(canonical(result))
    print("CKAD_SHARED_V2_STABLE_SHA256="+receipt,flush=True)
    print("CKAD_SHARED_V2_SUMMARY="+canonical({
       "classification":result["classification"],"gates":result["gates"],
       "global_gate_count":result["global_fit_gate_count"],
       "paired_gain":result["paired_gain"],"lower":result["bootstrap_lower_95"],
       "summary":result["summary"],"cold_worlds":result["cold_retained_worlds"],
       "sourcefree_effects":result["total_sourcefree_effects"]
    }).decode("ascii"),flush=True)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("stable="+receipt+"\n")
