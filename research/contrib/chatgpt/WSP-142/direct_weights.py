"""Source-blind direct binary-weight composition: discover <=3 XORed raw-bit
conjunctions from 32 *actually observed* consequences. The generic dictionary
is supplied (raw conjunctions up to degree5); no completed causal laws, family
labels, generator seeds or hidden source truths may enter fit or predict.
All minimum #terms and minimum summed-degree consistent weight sets are kept:
never use a top-K truncation to fabricate certainty.
"""
from itertools import combinations
SCHEMA="wsp142.direct-sparse-binary-interaction-weights.v1"
FEATURES=tuple(range(63)) # mask0=constant1, 1..62=generic AND of raw bits

def term(mask,x):
    return int((x&mask)==mask)
def fitted_signature(mask,inputs):
    z=0
    for i,x in enumerate(inputs):
        if (x&mask)==mask:z|=1<<i
    return z
def degree(mask):
    return mask.bit_count()

def fit(rows):
    if len(rows)!=32 or len({x for x,y in rows})!=32 or any(
        type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1)
        for x,y in rows):
        raise ValueError("WSP142_INVALID_OR_INCOMPLETE_SOURCE_EFFECTS")
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(x,y) in enumerate(rows))
    signatures=tuple(fitted_signature(mask,xs) for mask in FEATURES)
    if target==0:return ((),)
    for n in (1,2,3):
        best_degree=None
        candidates=[]
        for masks in combinations(FEATURES,n):
            parity=0
            for mask in masks:parity^=signatures[mask]
            if parity!=target:continue
            total_degree=sum(degree(mask) for mask in masks)
            if best_degree is None or total_degree<best_degree:
                best_degree=total_degree
                candidates=[]
            if total_degree==best_degree:
                candidates.append(masks)
        if candidates:return tuple(candidates)
    return tuple()

def predict(weights,x):
    if type(x) is not int or not 0<=x<64:raise ValueError("WSP142_BAD_TYPED_INPUT")
    if not weights:return None
    expected=None
    for factors in weights:
        value=0
        for mask in factors:value^=term(mask,x)
        if expected is None:expected=value
        elif expected!=value:return None
    return expected

def fingerprint(weights):
    from hashlib import sha256
    import json
    return sha256(json.dumps(weights,sort_keys=True,separators=(",",":")).encode()).hexdigest()
