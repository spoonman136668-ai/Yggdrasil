"""Independently implemented equal-information symbolic sparse polynomial solver.
No import or call into WSP142 numerical direct-weight learner or any source.
A three-term lookup uses a collision-indexed pair search rather than numerical
candidate's brute-force combinations; this independently checks representational
equivalence, and any tie defeats a unique numerical advantage claim.
"""
from collections import defaultdict
from itertools import combinations

def symbolic_fit(paid_rows):
    if len(paid_rows)!=32 or len(set(x for x,_ in paid_rows))!=32:
        raise ValueError("SYMBOLIC_EXPECTS_32_DISTINCT_EFFECTS")
    if any(type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1) for x,y in paid_rows):
        raise ValueError("SYMBOLIC_TYPED_EFFECT_INVALID")
    samples=[x for x,y in paid_rows]
    label=0
    for position,(x,y) in enumerate(paid_rows):
        if y:label|=1<<position
    if not label:return ((),)
    sig={}
    inv=defaultdict(list)
    for factor in range(63):
        response=0
        for position,x in enumerate(samples):
            if (x&factor)==factor:response|=1<<position
        sig[factor]=response
        inv[response].append(factor)

    def rank_and_keep(models):
        if not models:return ()
        minimum=min(sum(f.bit_count() for f in model) for model in models)
        return tuple(sorted(x for x in models if sum(f.bit_count() for f in x)==minimum))
    singles=[(m,) for m in range(63) if sig[m]==label]
    if singles:return rank_and_keep(singles)
    doubles=[]
    for left in range(63):
        target=sig[left]^label
        for right in inv.get(target,()):
            if right>left:doubles.append((left,right))
    if doubles:return rank_and_keep(doubles)
    triples=[]
    for left in range(63):
        for middle in range(left+1,63):
            remaining=label^sig[left]^sig[middle]
            for right in inv.get(remaining,()):
                if right>middle:triples.append((left,middle,right))
    return rank_and_keep(triples)

def symbolic_predict(fits,x):
    if type(x) is not int or not 0<=x<64:
        raise ValueError("SYMBOLIC_BAD_PUBLIC_INPUT")
    if not fits:return None
    first=None
    for model in fits:
        v=0
        for factor in model:v^=int((x&factor)==factor)
        if first is None:first=v
        elif first!=v:return None
    return first
