"""FKP-03 tokenless relation-grammar posterior and information-seeking interventions.

All numerical weights/hypothesis masks are constructed from public experiences
and deterministic generic binary composition; no source law or protected keys.
The family-aware posterior is an explicitly privileged conventional ceiling.
"""
from __future__ import annotations
from itertools import combinations,permutations
import hashlib
import json
import math
import random
import time

from source import CausalWorld,N_INPUT,N_POOL,N_PAID

TRIPLES=tuple(combinations(range(N_INPUT),3))
assert len(TRIPLES)==220
TRUTH_MASK=(1<<256)-1
FILTERS=tuple((
    sum(1<<fn for fn in range(256) if not (fn>>row)&1),
    sum(1<<fn for fn in range(256) if (fn>>row)&1)
) for row in range(8))


def acquire_foundation():
    """Read exactly 16,384 historical public action-consequence experiences."""
    hist={}
    observed=0
    digest=hashlib.sha256()
    t0=time.perf_counter()
    for seed in range(10000,10256):
        world=CausalWorld(seed)
        history=tuple((a,world.observe(a))
                      for a in world.public_view().intervention_choices)
        observed+=len(history)
        for a,y in history:
            digest.update(a.to_bytes(2,"big")+bytes((y,)))
        compatible=[]
        for pa,pb in combinations(range(N_INPUT),2):
            rows=[-1]*4
            for a,y in history:
                row=((a>>pa)&1)|(((a>>pb)&1)<<1)
                if rows[row] not in (-1,y):
                    break
                rows[row]=y
            else:
                if -1 not in rows:
                    compatible.append((pa,pb,sum(v<<i for i,v in enumerate(rows))))
        if len(compatible)!=1:
            raise AssertionError("FKP03_FOUNDATION_NOT_IDENTIFIABLE")
        table=compatible[0][2]
        hist[table]=hist.get(table,0)+1
    if observed!=16384:
        raise AssertionError("FKP03_FOUNDATION_COUNT_INVALID")
    checkpoint=json.dumps(hist,sort_keys=True,separators=(",",":"))
    return {"schema":"fkp03.foundation-learned.v1",
            "observations":observed,"worlds":256,"learned_gate_counts":dict(sorted(hist.items())),
            "source_history_sha256":digest.hexdigest(),
            "checkpoint_sha256":hashlib.sha256(checkpoint.encode()).hexdigest(),
            "learn_elapsed_seconds_local_dev":time.perf_counter()-t0}


def apply_2input(fn:int,a:int,b:int)->int:
    return sum(((fn>>(((a>>state)&1)|(((b>>state)&1)<<1)))&1)<<state for state in range(8))


def compose_generic_functions(learned_gates:tuple[int,...])->dict[int,int]:
    """Minimal depth for each constructible 3-variable truth table."""
    if len(learned_gates)!=4 or any(not 0<=g<16 for g in learned_gates):
        raise ValueError("FKP03_BAD_LEARNED_BASIS")
    known={}
    for input_idx in range(3):
        function=sum(((state>>input_idx)&1)<<state for state in range(8))
        known[function]=0
    for depth in (1,2,3,4):
        found={}
        current=tuple(known)
        for a in current:
            for b in current:
                for g in learned_gates:
                    function=apply_2input(g,a,b)
                    if function not in known and function not in found:
                        found[function]=depth
        known.update(found)
        if len(known)==256:
            return known
    return known


def truly3(fn:int)->bool:
    return all(any(((fn>>i)^(fn>>(i^(1<<bit))))&1 for i in range(8))
               for bit in range(3))


def generic_mask(compositions:dict[int,int])->int:
    return sum(1<<fn for fn in compositions if truly3(fn))


def family_mask()->int:
    """Privileged source-family ceiling; not a learned foundation."""
    functions=set()
    for state_rule in ("mux","maj"):
        for order in (permutations(range(3)) if state_rule=="mux" else ((0,1,2),)):
            table=0
            for state in range(8):
                bits=[(state>>p)&1 for p in order]
                y=(bits[1] if bits[0] else bits[2]) if state_rule=="mux" else int(sum(bits)>=2)
                table|=y<<state
            functions.add(table)
    if len(functions)!=7:
        raise AssertionError("FKP03_FAMILY_CARDINALITY_INVALID")
    return sum(1<<fn for fn in functions)


class Posterior:
    __slots__=("masks","available","observations")

    def __init__(self, function_mask:int):
        if type(function_mask) is not int or function_mask<=0 or function_mask>TRUTH_MASK:
            raise ValueError("FKP03_BAD_POSTERIOR_PRIOR")
        self.masks=[function_mask]*len(TRIPLES)
        self.available=function_mask
        self.observations=[]

    @staticmethod
    def pattern(action:int,trip:tuple[int,int,int])->int:
        a,b,c=trip
        return ((action>>a)&1)|(((action>>b)&1)<<1)|(((action>>c)&1)<<2)

    def counts(self,action:int)->tuple[int,int]:
        if type(action) is not int or not 0<=action<1<<N_INPUT:
            raise ValueError("FKP03_PUBLIC_ACTION_INVALID")
        total=0; ones=0
        for triple,mask in zip(TRIPLES,self.masks):
            total+=mask.bit_count()
            ones+=(mask&FILTERS[self.pattern(action,triple)][1]).bit_count()
        if total==0:raise ValueError("FKP03_ZERO_COMPATIBLE_HYPOTHESES")
        return total,ones

    def add(self,action:int,outcome:int)->None:
        if type(action) is not int or not 0<=action<1<<N_INPUT:
            raise ValueError("FKP03_PUBLIC_ACTION_INVALID")
        if type(outcome) is not int or outcome not in (0,1):
            raise ValueError("FKP03_BAD_OBSERVED_EFFECT")
        if action in (a for a,y in self.observations):
            raise ValueError("FKP03_DUPLICATE_EVIDENCE")
        new=[m&FILTERS[self.pattern(action,t)][outcome]
             for t,m in zip(TRIPLES,self.masks)]
        if sum(m.bit_count() for m in new)==0:
            raise ValueError("FKP03_OBSERVATION_OUTSIDE_HYPOTHESIS_GRAMMAR")
        self.masks=new
        self.observations.append((action,outcome))

    def choose(self,pool:tuple[int,...],policy:str,prior_chosen:tuple[int,...]=())->int:
        remaining=[x for x in pool if x not in prior_chosen]
        if not remaining:raise ValueError("FKP03_ACTION_POOL_EXHAUSTED")
        if policy=="information":
            # Maximum predictive-uncertainty split; no evaluator-private rule.
            # Exact numerator p*(1-p), total hypotheses fixed at a step.
            scored=[(lambda total,ones: (ones*(total-ones),-idx,a))(*self.counts(a))
                    for idx,a in enumerate(remaining)]
            return max(scored)[2]
        if policy=="coverage":
            # Public input geometry only, no access to outcomes or posterior.
            def score(a):
                return min((a^b).bit_count() for b in prior_chosen) if prior_chosen else min(a.bit_count(),N_INPUT-a.bit_count())
            return max(remaining,key=lambda a:(score(a),-pool.index(a)))
        if policy=="random":
            # Frozen public-seeded sampling independently of hidden law.
            seed=int.from_bytes(hashlib.sha256(str(pool).encode()).digest()[:8],"big")^711
            order=tuple(random.Random(seed).sample(pool,len(pool)))
            return next(x for x in order if x not in prior_chosen)
        raise ValueError("FKP03_UNKNOWN_ACTION_POLICY")

    def probabilities(self,held:tuple[int,...])->tuple[float,...]:
        return tuple(self.counts(x)[1]/self.counts(x)[0] for x in held)

    def checkpoint(self)->tuple[dict,str]:
        encoded=json.dumps({"masks":[str(x) for x in self.masks],
                            "observations":self.observations,"available":str(self.available)},
                           sort_keys=True,separators=(",",":"))
        result=json.loads(encoded)
        restored=Posterior(int(result["available"]))
        restored.masks=[int(v) for v in result["masks"]]
        restored.observations=[tuple(v) for v in result["observations"]]
        assert restored.masks==self.masks and restored.observations==self.observations
        return {"restored":restored,"bytes":len(encoded)},hashlib.sha256(encoded.encode()).hexdigest()


def execute_policy(seed:int,mask:int,policy:str)->dict:
    """One distinct source instance per policy, max 16 real consequences."""
    world=CausalWorld(seed)
    view=world.public_view()
    p=Posterior(mask)
    queries=[]
    outcomes=[]
    t0=time.perf_counter()
    for _ in range(N_PAID):
        action=p.choose(view.intervention_choices,policy,tuple(queries))
        answer=world.observe(action)
        p.add(action,answer)
        queries.append(action);outcomes.append(answer)
    if world.charged_actions!=N_PAID or len(set(queries))!=N_PAID:
        raise AssertionError("FKP03_POLICY_ACTION_BUDGET_DRIFT")
    saved,sha=p.checkpoint()
    probs=saved["restored"].probabilities(view.held_inputs)
    return {"p":p,"prediction":tuple(int(v>0.5) for v in probs),
            "probabilities":probs,"queries":tuple(queries),"answers":tuple(outcomes),
            "surviving_hypotheses":sum(m.bit_count() for m in p.masks),
            "checkpoint_sha256":sha,"checkpoint_bytes":saved["bytes"],
            "elapsed_seconds_local_dev":time.perf_counter()-t0}


def replay_exact_prior(queries:tuple[int,...],outcomes:tuple[int,...],held:tuple[int,...])->tuple[int,...]:
    """Full Bayesian-like exact-family posterior on identical actual transcript."""
    p=Posterior(family_mask())
    for action,answer in zip(queries,outcomes):
        p.add(action,answer)
    return tuple(int(v>0.5) for v in p.probabilities(held))
