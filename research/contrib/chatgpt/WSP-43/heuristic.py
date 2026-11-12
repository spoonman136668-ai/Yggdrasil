"""Frozen WSP42 heuristic; range and shared policy seed changes only."""
import random
from model import NumericModel

def acquire(width,probe,budget):
    if width not in (8,16,32,64,128) or type(budget) is not int or budget<width+1 or budget>1024:raise ValueError('width/budget')
    rng=random.Random(2333+width)
    groups,basis_groups,transcript,stats=[],[],[],[]
    for action in range(2):
        cache,terms={},{}
        updates,reads,draws=0,0,0
        reason='query_budget'
        def query(x):
            nonlocal reads
            reads+=1
            if x not in cache:
                if len(cache)>=budget:raise StopIteration
                y=probe(action,x)
                if type(y) is not int or not 0<=y<1<<width:raise ValueError('oracle')
                cache[x]=y
            return cache[x]
        def predict(x):
            out=0
            for m,c in terms.items():
                if x&m==m:out^=c
            return out
        bias=query(0)
        if bias:terms[0]=bias
        for bit in range(width):
            coefficient=query(1<<bit)^bias
            if coefficient:terms[1<<bit]=coefficient
        basis_groups.append(tuple(sorted(terms.items())))
        while len(cache)<budget and updates<256:
            witness=next((x for x,y in cache.items() if y!=predict(x)),None)
            if witness is None:
                full=(1<<width)-1
                if full not in cache:witness=full
                else:
                    while True:
                        density=(.5,.75,.875)[draws%3];draws+=1
                        witness=sum((rng.random()<density)<<i for i in range(width))
                        if witness not in cache:break
                if query(witness)==predict(witness):continue
            difference=query(witness)^predict(witness)
            selected=difference&-difference
            try:
                for bit in range(width):
                    if witness&(1<<bit):
                        smaller=witness^(1<<bit)
                        if (query(smaller)^predict(smaller))&selected:witness=smaller
                coefficient=query(witness)^predict(witness)
            except StopIteration:
                reason='budget_during_minimization';break
            if witness not in terms and len(terms)>=width+33:
                reason='capacity';break
            new=terms.get(witness,0)^coefficient
            if new:terms[witness]=new
            else:terms.pop(witness,None)
            updates+=1
        if updates==256:reason='update_budget'
        groups.append(tuple(sorted(terms.items())))
        transcript.extend((action,x,y) for x,y in cache.items())
        stats.append(dict(queries=len(cache),reads=reads,updates=updates,cells=len(terms),degrees=sorted(m.bit_count() for m in terms),cached_errors=sum(y!=predict(x) for x,y in cache.items()),stop=reason))
    return NumericModel(width,tuple(groups)),NumericModel(width,tuple(basis_groups)),tuple(transcript),stats

