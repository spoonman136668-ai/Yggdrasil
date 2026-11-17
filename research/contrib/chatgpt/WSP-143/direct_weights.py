"""WSP143: source-blind four-term direct binary weight programmer.

Given 32 paid source effects, solve exactly for a <=4-term XOR of generic
AND-of-public-raw-bit features. Minimize feature count then total bit degree;
retain ALL equally ranked explanations. At inference time withhold confidence
if any active degree-5 conjunction lacks a paid positive activation witness.
No complete source laws, grammar labels, held effects or original source import.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json

FEATURES=tuple(range(63)) # zero=constant1, masks1..62 generic raw input AND
FIVE_MASKS=tuple(i for i in FEATURES if i.bit_count()==5)
SCHEMA="wsp143.direct-fourterm-witness-gated.v1"

def sig(mask,xs):
    return sum(int((x&mask)==mask)<<i for i,x in enumerate(xs))
def rank(models):
    if not models:return ()
    best=min(sum(m.bit_count() for m in v) for v in models)
    return tuple(sorted(v for v in models if sum(m.bit_count() for m in v)==best))

def fit(rows):
    if len(rows)!=32 or len({x for x,y in rows})!=32 or any(
        type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1)
        for x,y in rows):
        raise ValueError("WSP143_BAD_ACTUAL_PAID_EFFECTS")
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(x,y) in enumerate(rows))
    if target==0:return (((),),tuple(sorted(xs)))
    signs=tuple(sig(mask,xs) for mask in FEATURES)
    inv=defaultdict(list)
    for i,v in enumerate(signs):inv[v].append(i)
    singles=tuple((i,) for i in FEATURES if signs[i]==target)
    if singles:return (rank(singles),tuple(sorted(xs)))
    doubles=tuple((i,j) for i in FEATURES
                  for j in inv.get(target^signs[i],()) if j>i)
    if doubles:return (rank(doubles),tuple(sorted(xs)))
    triples=[]
    for i in FEATURES:
        for j in range(i+1,63):
            for k in inv.get(target^signs[i]^signs[j],()):
                if k>j:triples.append((i,j,k))
    if triples:return (rank(triples),tuple(sorted(xs)))
    # Pair-signature meet-in-the-middle construction: all 63 choose 4
    # canonical 4-term supports represented without a top-K approximation.
    bypair=defaultdict(list)
    for i in FEATURES:
        for j in range(i+1,63):bypair[signs[i]^signs[j]].append((i,j))
    fours=[]
    best_degree=None
    for i in FEATURES:
        for j in range(i+1,63):
            for k,l in bypair.get(target^signs[i]^signs[j],()):
                if k<=j:continue
                d=i.bit_count()+j.bit_count()+k.bit_count()+l.bit_count()
                if best_degree is None or d<best_degree:
                    best_degree=d
                    fours=[]
                if d==best_degree:fours.append((i,j,k,l))
    return (tuple(fours),tuple(sorted(xs)))

def witness_missing(x,observed):
    if type(x) is not int or not 0<=x<64:raise ValueError("WSP143_BAD_PUBLIC_INPUT")
    # Same generic condition for EVERY one of the six five-way AND features.
    # No hidden source family mask, rare-event label, held-input or truth.
    for mask in FIVE_MASKS:
        if (x&mask)==mask and all((seen&mask)!=mask for seen in observed):
            return True
    return False

def predict(fitted,x):
    if type(x) is not int or not 0<=x<64:raise ValueError("WSP143_BAD_PUBLIC_INPUT")
    models,observed=fitted
    if not models or witness_missing(x,observed):return None
    result=None
    for model in models:
        bit=0
        for mask in model:bit^=int((x&mask)==mask)
        if result is None:result=bit
        elif result!=bit:return None
    return result

def fingerprint(fitted):
    return sha256(json.dumps(fitted,sort_keys=True,separators=(",",":")).encode()).hexdigest()
