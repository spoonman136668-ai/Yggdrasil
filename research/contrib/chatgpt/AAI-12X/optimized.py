"""AAI-12X exact-reference lossless symmetry-pruned ternary causal learner.

The allowed hypothesis family is unchanged from AAI-12W; only its redundant
input-role permutation search and precomputable public residuals are removed.
"""
import hashlib
import itertools
import json
import reference_w

METHOD = 'ternary_causal'
TRIPLES = tuple((k,abc) for k in range(8)
                for abc in itertools.combinations((i for i in range(8) if i!=k),3))
assert len(TRIPLES)==280

def fit(rows):
    if type(rows) not in (tuple,list) or len(rows)!=48:
        raise ValueError('source public transition budget drift')
    public = []
    for r in rows:
        x, xx=reference_w.check(r)
        public.append((x,r['y']^r['ynext'],r['flipped_index']))
    best=None
    for k,abc in TRIPLES:
        a,b,c=abc
        zero=[0]*8; one=[0]*8
        for x,output_change,flipped in public:
            cell=(x[a]<<2)|(x[b]<<1)|x[c]
            if output_change^(flipped==k):one[cell]+=1
            else:zero[cell]+=1
        mask=0;errors=0;covered=0
        for i in range(8):
            n0=zero[i];n1=one[i]
            errors+=n1 if n1<n0 else n0
            covered+=int((n0+n1)>0)
            mask |= int(n1>n0)<<i
        candidate=(errors,-covered,k,a,b,c,mask)
        if best is None or candidate<best:best=candidate
    _,_,k,a,b,c,mask=best
    return {'k':k,'abc':[a,b,c],'mask':mask}

def train(rows):
    model=fit(rows)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'aai12w.cold.v1','name':METHOD,'model':model,'training_sha256':digest}

def checkpoint(state):return reference_w.checkpoint(state)
def restore(snapshot):return reference_w.restore(snapshot)
def forecast(state,x,y,actions):return reference_w.forecast(state,x,y,actions)
