"""Independent, flat exhaustive Boolean symbolic control for WSP143.

Does NOT import the hierarchical candidate, its concept lattice, fit, readout
or source generator. Uses directly enumerated raw bit subsets and a separate
meet-in-the-middle collision index for the same declared <=4 term grammar.
"""
from collections import defaultdict
from itertools import combinations

def _features(depth):
    a=[0]
    for degree in range(1,depth+1):
        for xs in combinations(range(6),degree):
            a.append(sum(1<<i for i in xs))
    return tuple(sorted(a))

def _eval(f,x):
    return int((x&f)==f)

def symbolic_fit(rows,max_depth=5,cap=10000):
    if (len(rows)!=32 or len({x for x,y in rows})!=32 or
        type(max_depth) is not int or not 2<=max_depth<=5 or
        any(type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1) for x,y in rows)):
        raise ValueError('WSP143_SYMBOLIC_INVALID_OBSERVATIONS')
    xs=[x for x,y in rows]
    target=0
    for i,(_,y) in enumerate(rows):target|=y<<i
    if target==0:
        return {'level':2,'programs':((),),'overflow':False,'count':1,'terms':0,'degree':0}
    for depth in (2,3,4,5):
        if depth>max_depth:break
        feats=_features(depth)
        sig={}
        for f in feats:
            binary=[_eval(f,x) for x in xs]
            sig[f]=sum(1<<i for i,v in enumerate(binary) if v)
        singles=defaultdict(list)
        for f in feats:singles[sig[f]].append(f)
        for nterms in (1,2,3,4):
            best=None
            retained=[]
            count=0
            over=False
            def found(prog):
                nonlocal best,retained,count,over
                complexity=sum(f.bit_count() for f in prog)
                if best is None or complexity<best:
                    best=complexity;retained=[];count=0;over=False
                if complexity==best:
                    count+=1
                    if count<=cap:retained.append(prog)
                    else:over=True
            if nterms==1:
                for f in singles.get(target,()):found((f,))
            elif nterms==2:
                for a in feats:
                    for b in singles.get(sig[a]^target,()):
                        if b>a:found((a,b))
            elif nterms==3:
                for a,b in combinations(feats,2):
                    for c in singles.get(target^sig[a]^sig[b],()):
                        if c>b:found((a,b,c))
            else:
                by_pair=defaultdict(list)
                for a,b in combinations(feats,2):
                    by_pair[sig[a]^sig[b]].append((a,b))
                for a,b in combinations(feats,2):
                    for c,d in by_pair.get(target^sig[a]^sig[b],()):
                        if c>b:found((a,b,c,d))
            if count:
                return {'level':depth,'programs':tuple(sorted(retained)) if not over else (),
                        'overflow':over,'count':count,
                        'terms':nterms,'degree':best}
    return {'level':None,'programs':(),'overflow':False,'count':0,'terms':None,'degree':None}

def symbolic_predict(state,x):
    if type(x) is not int or not 0<=x<64:raise ValueError('WSP143_SYMBOLIC_BAD_INPUT')
    if state['overflow'] or not state['programs']:return None
    predictions={sum(_eval(f,x) for f in fs)%2 for fs in state['programs']}
    return next(iter(predictions)) if len(predictions)==1 else None
