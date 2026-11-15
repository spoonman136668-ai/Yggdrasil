"""Independent fixed synthetic evaluator, not learned native knowledge."""
import hashlib
SEEDS=tuple(range(7001,7009))
def check(seed):
    if type(seed) is not int or seed not in SEEDS: raise ValueError("BAD_SEED")
def optimal(seed,source):
    check(seed)
    if type(source) is not int or not 0<=source<4: raise ValueError("BAD_SOURCE")
    return hashlib.sha256(f"QTR01-F10|{seed}|{source}".encode("ascii")).digest()[0]&1
def events(seed):
    check(seed)
    return tuple((s,a,int(a==optimal(seed,s))) for s in range(4) for a in (0,1) for _ in range(4))
def relation(seed):
    check(seed)
    return {t:((t+seed)%4,(t+seed)%2) for t in range(4)}
def truth(seed,t):
    if type(t) is not int or not 0<=t<4: raise ValueError("BAD_TARGET")
    s,flip=relation(seed)[t]
    return optimal(seed,s)^flip
def shuffled(seed):
    return {t:(s,flip^int(t%2==0)) for t,(s,flip) in relation(seed).items()}
