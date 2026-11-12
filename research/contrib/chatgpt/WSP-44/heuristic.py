"""Frozen WSP43 exact acquisition baseline, unchanged logic/ceilings."""
import random
from model import NumericModel

def acquire(width,probe,budget):
    if width not in (8,16,32,64,128) or type(budget) is not int or not width+1<=budget<=1024:raise ValueError('width/budget')
    groups,basis_groups,transcript,stats=[],[],[],[]
    rng=random.Random(2333+width)
    for action in range(2):
        cache,terms={},{}
        batches,reads,draws,subset_states=0,0,0,0
        stop='query_budget'
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
            for mask,c in terms.items():
                if x&mask==mask:out^=c
            return out
        bias=query(0)
        if bias:terms[0]=bias
        for bit in range(width):
            coefficient=query(1<<bit)^bias
            if coefficient:terms[1<<bit]=coefficient
        basis_groups.append(tuple(sorted(terms.items())))
        while len(cache)<budget and batches<256:
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
            selected=(query(witness)^predict(witness))
            selected&=-selected
            try:
                while True:
                    previous=witness
                    for bit in range(width):
                        if witness&(1<<bit):
                            smaller=witness^(1<<bit)
                            if (query(smaller)^predict(smaller))&selected:witness=smaller
                    if previous==witness:break
                inputs=[i for i in range(width) if witness>>i&1]
                if len(inputs)>8:
                    stop='local_subset_degree_screen';break
                states=[sum((1<<bit) for j,bit in enumerate(inputs) if code>>j&1) for code in range(1<<len(inputs))]
                values=[query(x) for x in states]
            except StopIteration:
                stop='budget_during_exact_interrogation';break
            subset_states+=len(states)
            # In-place Boolean Mobius transform of actual FULL output replies.
            for j in range(len(inputs)):
                for code in range(len(states)):
                    if code>>j&1:values[code]^=values[code^(1<<j)]
            changed=dict(terms)
            for mask,c in zip(states,values):
                if c:changed[mask]=c
                else:changed.pop(mask,None)
            if len(changed)>width+33:
                stop='capacity';break
            if changed==terms:
                # With a real residual witness, a complete subcube must change.
                raise AssertionError('exact batch did not explain its witness')
            terms=changed;batches+=1
        if batches==256:stop='update_budget'
        groups.append(tuple(sorted(terms.items())))
        transcript.extend((action,x,y) for x,y in cache.items())
        stats.append(dict(queries=len(cache),reads=reads,batches=batches,subset_states=subset_states,cells=len(terms),degrees=sorted(m.bit_count() for m in terms),cached_errors=sum(y!=predict(x) for x,y in cache.items()),stop=stop))
    return NumericModel(width,tuple(groups)),NumericModel(width,tuple(basis_groups)),tuple(transcript),stats

