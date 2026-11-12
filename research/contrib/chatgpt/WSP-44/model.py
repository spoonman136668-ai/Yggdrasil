"""Exact local finite-difference construction of unknown nonlinear vector maps."""
import hashlib
import itertools
import json
import random

class NumericModel:
    def __init__(self,width,groups):
        if type(width) is not int or width not in (8,16,32,64,128):raise ValueError('width')
        if type(groups) is not tuple or len(groups)!=2:raise ValueError('groups')
        for group in groups:
            if type(group) is not tuple or len(group)>width+33 or tuple(sorted(group))!=group or len(set(m for m,c in group))!=len(group):raise ValueError('canonical')
            if any(type(m) is not int or type(c) is not int or not 0<=m<1<<width or not 0<c<1<<width for m,c in group):raise ValueError('coefficient')
        self.width,self.groups=width,groups

    def apply(self,action,state):
        if type(action) is not int or action not in (0,1) or type(state) is not int or not 0<=state<1<<self.width:raise ValueError('state/action')
        out=0
        for mask,coefficient in self.groups[action]:
            if (state&mask).bit_count()>=mask.bit_count():out^=coefficient
        return out

    def rollout(self,state,actions):
        for action in actions:state=self.apply(action,state)
        return state

    def plan(self,start,goal):
        for actions in itertools.product(range(2),repeat=3):
            if self.rollout(start,actions)==goal:return actions
        return None

    def snapshot(self):
        body=json.dumps(['wsp44.fullmap.v1',self.width,self.groups],separators=(',',':')).encode()
        return body+b'|'+hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls,data):
        try:
            body,digest=data.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            schema,width,groups=json.loads(body)
            if schema!='wsp44.fullmap.v1':raise ValueError('schema')
            model=cls(width,tuple(tuple(tuple(pair) for pair in g) for g in groups))
            if model.snapshot()!=data:raise ValueError('canonical')
            return model
        except (TypeError,ValueError,AttributeError):raise ValueError('checkpoint') from None


def acquire(width,probe,budget):
    if width not in (8,16,32,64,128) or type(budget) is not int or not width+1<=budget<=1024:raise ValueError('width/budget')
    groups,basis_groups,transcript,stats=[],[],[],[]
    rng=random.Random(2333+width)
    for action in range(2):
        cache,terms={},{}
        batches,reads,draws,subset_states=0,0,0,0
        halving_trials,halving_shrinks=0,0
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
                failed,trials=0,0
                while witness.bit_count()>8 and failed<32 and trials<128:
                    trials+=1;halving_trials+=1
                    smaller=sum((1<<bit) for bit in range(width) if witness>>bit&1 and rng.random()<.5)
                    if (query(smaller)^predict(smaller))&selected:
                        witness=smaller;failed=0;halving_shrinks+=1
                    else:failed+=1
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
        stats.append(dict(queries=len(cache),reads=reads,batches=batches,subset_states=subset_states,halving_trials=halving_trials,halving_shrinks=halving_shrinks,cells=len(terms),degrees=sorted(m.bit_count() for m in terms),cached_errors=sum(y!=predict(x) for x,y in cache.items()),stop=stop))
    return NumericModel(width,tuple(groups)),NumericModel(width,tuple(basis_groups)),tuple(transcript),stats


class GF2Regression(NumericModel):
    """Independent fully fitted GF2 system ID on the discovered vocabulary."""
    def __init__(self,width,transcript,vocabulary):
        groups=[];self.ranks=[];self.inconsistent=[]
        for action in range(2):
            features=tuple(m for m,c in vocabulary.groups[action])
            pivots={};inconsistent=0
            for a,x,y in transcript:
                if a!=action:continue
                row=sum(int(x&m==m)<<j for j,m in enumerate(features))
                rhs=y
                while row:
                    pivot=(row&-row).bit_length()-1
                    if pivot in pivots:
                        other,value=pivots[pivot];row^=other;rhs^=value
                    else:
                        pivots[pivot]=(row,rhs);break
                if row==0 and rhs:inconsistent+=1
            solution=[0]*len(features)
            for pivot in sorted(pivots,reverse=True):
                row,rhs=pivots[pivot];rest=row^(1<<pivot)
                while rest:
                    low=rest&-rest;rhs^=solution[low.bit_length()-1];rest^=low
                solution[pivot]=rhs
            groups.append(tuple((m,c) for m,c in zip(features,solution) if c))
            self.ranks.append(len(pivots));self.inconsistent.append(inconsistent)
        super().__init__(width,tuple(groups))
        self.training_errors=[sum(self.apply(a,x)!=y for aa,x,y in transcript if aa==a) for a in range(2)]

