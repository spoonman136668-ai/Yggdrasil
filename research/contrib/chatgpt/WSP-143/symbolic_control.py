"""WSP143 independent source-blind symbolic four-term constraint solver.

Separately written triple-then-complement search, not importing candidate
numerical weights, witness function, source generator, future truth or oracle.
Same expression language and min term/min summed-degree all-tie policy.
"""
from collections import defaultdict
from itertools import combinations

def solve(rows):
    if len(rows)!=32 or len({x for x,y in rows})!=32 or any(
        type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1)
        for x,y in rows):
        raise ValueError("WSP143_SYMBOLIC_BAD_PAID_SOURCE")
    inputs=[x for x,y in rows]
    target=sum(y<<i for i,(_,y) in enumerate(rows))
    if target==0:return (((),),tuple(sorted(inputs)))
    signatures={}
    buckets=defaultdict(tuple)
    for mask in range(63):
        signature=0
        for i,x in enumerate(inputs):
            if (x&mask)==mask:signature|=1<<i
        signatures[mask]=signature
        buckets[signature]=buckets[signature]+(mask,)
    def best(xs):
        if not xs:return ()
        rank=min(sum(m.bit_count() for m in model) for model in xs)
        return tuple(sorted(model for model in xs
                            if sum(m.bit_count() for m in model)==rank))
    singles=[(x,) for x in range(63) if signatures[x]==target]
    if singles:return (best(singles),tuple(sorted(inputs)))
    doubles=[]
    for a,b in combinations(range(63),2):
        if signatures[a]^signatures[b]==target:doubles.append((a,b))
    if doubles:return (best(doubles),tuple(sorted(inputs)))
    triples=[]
    for a,b,c in combinations(range(63),3):
        if signatures[a]^signatures[b]^signatures[c]==target:
            triples.append((a,b,c))
    if triples:return (best(triples),tuple(sorted(inputs)))
    # Distinct from the candidate's pair meet-in-middle: each sorted
    # triple looks up the unique larger fourth index by XOR signature.
    fours=[]
    minimum=None
    for a,b,c in combinations(range(63),3):
        missing=target^signatures[a]^signatures[b]^signatures[c]
        for d in buckets.get(missing,()):
            if d<=c:continue
            model=(a,b,c,d)
            cost=sum(mask.bit_count() for mask in model)
            if minimum is None or cost<minimum:
                minimum=cost
                fours=[]
            if cost==minimum:fours.append(model)
    return (tuple(fours),tuple(sorted(inputs)))

def infer(fitted,x):
    if type(x) is not int or not 0<=x<64:
        raise ValueError("WSP143_SYMBOLIC_BAD_TYPED_INPUT")
    models,original_inputs=fitted
    if not models:return None
    for mask in range(63):
        if mask.bit_count()!=5 or (mask&x)!=mask:continue
        witnessed=False
        for observed in original_inputs:
            if (mask&observed)==mask:
                witnessed=True
                break
        if not witnessed:return None
    vote=None
    for solution in models:
        bit=0
        for mask in solution:
            if (mask&x)==mask:bit^=1
        if vote is None:vote=bit
        elif bit!=vote:return None
    return vote
