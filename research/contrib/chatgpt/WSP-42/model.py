"""Whole hidden vector map acquisition: no supplied transition background."""
import hashlib
import itertools
import json
import math
import random


class NumericModel:
    def __init__(self,width,groups):
        if type(width) is not int or width not in (8,16,32):raise ValueError('width')
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
        body=json.dumps(['wsp42.fullmap.v1',self.width,self.groups],separators=(',',':')).encode()
        return body+b'|'+hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls,data):
        try:
            body,digest=data.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            schema,width,groups=json.loads(body)
            if schema!='wsp42.fullmap.v1':raise ValueError('schema')
            model=cls(width,tuple(tuple(tuple(pair) for pair in g) for g in groups))
            if model.snapshot()!=data:raise ValueError('canonical')
            return model
        except (TypeError,ValueError,AttributeError):raise ValueError('checkpoint') from None


def acquire(width,probe,budget):
    if width not in (8,16,32) or budget not in (64,128):raise ValueError('width/budget')
    rng=random.Random(1997+width)
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


class SymbolicExecution:
    def __init__(self,model):
        self.width=model.width
        self.rules=tuple(tuple((tuple(i for i in range(model.width) if m>>i&1),c) for m,c in g) for g in model.groups)

    def apply(self,action,state):
        out=0
        for inputs,coefficient in self.rules[action]:
            if all(state>>i&1 for i in inputs):out^=coefficient
        return out

    rollout=NumericModel.rollout
    plan=NumericModel.plan


class KernelRegression:
    """One shared fully fitted RBF Gram matrix, width binary output heads."""
    def __init__(self,width,transcript):
        self.width,self.centers,self.alphas,self.max_errors=width,[],[],[]
        for action in range(2):
            rows=[(x,y) for a,x,y in transcript if a==action]
            xs,ys=zip(*rows);n=len(xs)
            matrix=[[2.0**(-(x^z).bit_count()) for z in xs] for x in xs]
            lower=[[0.0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1):
                    value=matrix[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
                    if i==j:
                        if value<=1e-12:raise ValueError('kernel')
                        lower[i][j]=math.sqrt(value)
                    else:lower[i][j]=value/lower[j][j]
            heads=[];max_error=0.0
            for bit in range(width):
                targets=[float(y>>bit&1) for y in ys]
                forward=[]
                for i in range(n):forward.append((targets[i]-sum(lower[i][k]*forward[k] for k in range(i)))/lower[i][i])
                alpha=[0.0]*n
                for i in range(n-1,-1,-1):alpha[i]=(forward[i]-sum(lower[k][i]*alpha[k] for k in range(i+1,n)))/lower[i][i]
                max_error=max(max_error,max(abs(sum(v*a for v,a in zip(row,alpha))-y) for row,y in zip(matrix,targets)))
                heads.append(alpha)
            self.centers.append(xs);self.alphas.append(heads);self.max_errors.append(max_error)

    def apply(self,action,state):
        features=[2.0**(-(state^x).bit_count()) for x in self.centers[action]]
        return sum(int(round(sum(v*a for v,a in zip(features,head)),12)>=.5)<<bit for bit,head in enumerate(self.alphas[action]))

    rollout=NumericModel.rollout
    plan=NumericModel.plan
