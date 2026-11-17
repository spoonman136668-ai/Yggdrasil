"""WSP-143: tokenless coarse-to-fine causal concept induction.

Public input bits -> primitive features -> conjunction concepts through depth 5.
Each stage fits a sparse XOR composition from ONLY 32 paid consequences.
No complete source-law grammar, family identifier, hidden outcome or evaluator
is imported. This is a bounded demonstration, not the NCM paper architecture.
"""
from collections import defaultdict
from itertools import combinations
from hashlib import sha256
import json

SCHEMA='wsp143.hierarchical-causal-concept-state.v1'
MAX_TIED=10000

def concept_lattice():
    levels={0:(0,),1:tuple(1<<i for i in range(6))}
    prior=set(levels[1])
    for depth in range(2,6):
        new={m|(1<<i) for m in prior for i in range(6)
             if not m&(1<<i) and (m|(1<<i)).bit_count()==depth}
        if len(new)!={2:15,3:20,4:15,5:6}[depth]:
            raise AssertionError('WSP143_CONCEPT_LATTICE_BROKEN')
        levels[depth]=tuple(sorted(new))
        prior=new
    return levels

LEVELS=concept_lattice()

def signature(mask,xs):
    return sum(1<<i for i,x in enumerate(xs) if (x&mask)==mask)

def _solve(features,sig,target):
    """Exact 0..4-term collision-indexed XOR solve, retaining all tied minima.
    Stop retention after MAX_TIED best-ranked representations; ambiguous results
    then abstain rather than silently selecting an arbitrary subset.
    """
    if target==0:
        return {'fits':((),),'overflow':False,'count':1,'terms':0,'degree':0}
    n=len(features)
    inv=defaultdict(list)
    for i,s in enumerate(sig):inv[s].append(i)
    pairs=None
    for terms in (1,2,3,4):
        best_degree=None
        kept=[]
        count=0
        overflow=False
        def offer(indices):
            nonlocal best_degree,kept,count,overflow
            d=sum(features[i].bit_count() for i in indices)
            if best_degree is None or d<best_degree:
                best_degree=d;kept=[];count=0;overflow=False
            if d==best_degree:
                count+=1
                if count<=MAX_TIED:
                    kept.append(tuple(features[i] for i in indices))
                else:overflow=True
        if terms==1:
            for i in inv.get(target,()):offer((i,))
        if terms==2:
            for i in range(n):
                for j in inv.get(target^sig[i],()):
                    if j>i:offer((i,j))
        if terms==3:
            for i in range(n):
                for j in range(i+1,n):
                    for k in inv.get(target^sig[i]^sig[j],()):
                        if k>j:offer((i,j,k))
        if terms==4:
            if pairs is None:
                pairs=defaultdict(list)
                for k in range(n):
                    for l in range(k+1,n):
                        pairs[sig[k]^sig[l]].append((k,l))
            for i in range(n):
                for j in range(i+1,n):
                    for k,l in pairs.get(target^sig[i]^sig[j],()):
                        if k>j:offer((i,j,k,l))
        if best_degree is not None:
            return {'fits':tuple(kept) if not overflow else (),
                    'overflow':overflow,'count':count,
                    'terms':terms,'degree':best_degree}
    return {'fits':(), 'overflow':False,'count':0,'terms':None,'degree':None}

def fit(rows,max_depth=5):
    if (type(max_depth) is not int or not 2<=max_depth<=5 or
        len(rows)!=32 or len({x for x,y in rows})!=32 or
        any(type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1)
            for x,y in rows)):
        raise ValueError('WSP143_UNQUALIFIED_PUBLIC_OBSERVATION_OR_DEPTH')
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(_,y) in enumerate(rows))
    stages=[]
    for depth in range(2,max_depth+1):
        features=tuple(sorted(m for d in range(depth+1) for m in LEVELS[d]))
        if len(features)!={2:22,3:42,4:57,5:63}[depth]:
            raise AssertionError('WSP143_LEVEL_SIZE_MISMATCH')
        result=_solve(features,tuple(signature(m,xs) for m in features),target)
        stages.append([depth,len(features),result['count']])
        if result['count']:
            return {'schema':SCHEMA,'level':depth,'programs':result['fits'],
                    'overflow':result['overflow'],'tied_count':result['count'],
                    'terms':result['terms'],'degree':result['degree'],
                    'observed_sha256':digest(rows),'stages':stages}
    return {'schema':SCHEMA,'level':None,'programs':(),
            'overflow':False,'tied_count':0,'terms':None,'degree':None,
            'observed_sha256':digest(rows),'stages':stages}

def predict(state,x):
    if type(x) is not int or not 0<=x<64:
        raise ValueError('WSP143_BAD_TYPED_STATE')
    if state['schema']!=SCHEMA or state['overflow'] or not state['programs']:
        return None
    answer=None
    for factors in state['programs']:
        value=0
        for factor in factors:value^=int((x&factor)==factor)
        if answer is None:answer=value
        elif answer!=value:return None
    return answer

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'))
def digest(obj):
    return sha256(canon(obj).encode()).hexdigest()
def restore(saved,rows):
    value=json.loads(saved)
    state=fit(rows)
    if canon(state)!=canon(value):
        raise ValueError('WSP143_NONCANONICAL_OR_FOREIGN_COLD_STATE')
    return state
