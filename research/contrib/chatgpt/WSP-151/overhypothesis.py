"""Source-free exact hierarchical causal overhypothesis model.

Public-synthetic development only. No source owner, labels, held questions,
scored seed, or native model weight access.
"""
from fractions import Fraction
from hashlib import sha256
from json import dumps
from math import factorial, log2

SCHEMA="wsp151.causal.hypermemory.v1"
MODEL="wsp151.causal.hierarchical.v1"
FORMS=("OR","AND")
SUBSETS=range(1,64)
OBSERVATIONS=frozenset(("do","observed_do"))

def digest(obj):
    return sha256(dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate_rows(rows,max_count=8):
    if type(rows) not in (tuple,list) or not 0<=len(rows)<=max_count:
        raise ValueError("WSP151_BAD_ROW_COUNT")
    out=[]
    for item in rows:
        if (type(item) not in (tuple,list) or len(item)!=3 or
            type(item[0]) is not int or not 0<=item[0]<64 or
            type(item[1]) is not int or item[1] not in (0,1) or
            item[2] not in OBSERVATIONS):
            raise ValueError("WSP151_REQUIRES_REAL_DO_OR_OBSERVED_DO")
        out.append((item[0],item[1],item[2]))
    if len({x for x,_,_ in out})!=len(out):
        raise ValueError("WSP151_DUPLICATE_CHARGED_ACTION")
    return tuple(out)

def law(kind,subset,x):
    if kind=="OR":return int(bool(x&subset))
    if kind=="AND":return int((x&subset)==subset)
    raise ValueError("WSP151_UNKNOWN_FORM")

def _marginals(rows):
    rows=validate_rows(rows)
    if len(rows)!=8:raise ValueError("WSP151_FIT_REQUIRES_8_CHARGED_EFFECTS")
    return tuple(sum(19**sum(law(g,s,x)==y for x,y,_ in rows)
                     for s in SUBSETS) for g in FORMS)

def empty_memory():
    state={"schema":SCHEMA,"worlds":(),"receipts":(),"frozen":False}
    return {**state,"digest":digest(state)}

def _check_memory(mem):
    if (type(mem) is not dict or set(mem)!=
        {"schema","worlds","receipts","frozen","digest"} or
        mem["schema"]!=SCHEMA or type(mem["frozen"]) is not bool or
        type(mem["worlds"]) not in (list,tuple) or len(mem["worlds"])>16 or
        type(mem["receipts"]) not in (list,tuple) or
        len(mem["receipts"])!=len(mem["worlds"])):
        raise ValueError("WSP151_BAD_HYPERMEMORY")
    for pair in mem["worlds"]:
        if (type(pair) not in (tuple,list) or len(pair)!=2 or
            any(type(v) is not int or v<=0 for v in pair)):
            raise ValueError("WSP151_INVALID_WORLD_EVIDENCE")
    if (len(set(mem["receipts"]))!=len(mem["receipts"]) or
        any(type(x) is not str or len(x)!=64 or
            any(c not in "0123456789abcdef" for c in x) for x in mem["receipts"])):
        raise ValueError("WSP151_INVALID_RECEIPTS")
    plain={"schema":SCHEMA,"worlds":tuple(tuple(p) for p in mem["worlds"]),
           "receipts":tuple(mem["receipts"]),"frozen":mem["frozen"]}
    if mem["digest"]!=digest(plain):
        raise ValueError("WSP151_HYPERMEMORY_HASH_MISMATCH")
    return plain

def remember(mem,rows,world_id):
    m=_check_memory(mem)
    if m["frozen"] or len(m["worlds"])>=16:
        raise ValueError("WSP151_MEMORY_CLOSED")
    if type(world_id) is not int or world_id<0:
        raise ValueError("WSP151_BAD_WORLD_ID")
    r=validate_rows(rows)
    pair=_marginals(r)
    receipt=digest((world_id,r))
    if receipt in m["receipts"]:
        raise ValueError("WSP151_DUPLICATE_WORLD")
    update={**m,"worlds":m["worlds"]+(pair,),
            "receipts":m["receipts"]+(receipt,)}
    return {**update,"digest":digest(update)}

def freeze(mem):
    m=_check_memory(mem)
    if len(m["worlds"])!=16:raise ValueError("WSP151_FIT_16_REQUIRED")
    m={**m,"frozen":True}
    return {**m,"digest":digest(m)}

def restore(mem):
    m=_check_memory(mem)
    return {**m,"digest":digest(m)}

def prior_or(mem):
    """Integrate shared OR propensity p under exact Beta(1,1) posterior."""
    m=_check_memory(mem)
    coefficients=[1]
    for like_or,like_and in m["worlds"]:
        new=[0]*(len(coefficients)+1)
        for k,value in enumerate(coefficients):
            new[k]+=value*like_and
            new[k+1]+=value*like_or
        coefficients=new
    n=len(m["worlds"])
    den=sum(v*factorial(k)*factorial(n-k)
            for k,v in enumerate(coefficients))
    num=sum(v*factorial(k+1)*factorial(n-k)
            for k,v in enumerate(coefficients))
    return Fraction(num,(n+2)*den)

def fit(rows,mem=None):
    r=validate_rows(rows)
    if mem is None:mem=empty_memory()
    p=prior_or(mem)
    prior={"OR":p,"AND":1-p}
    scale=2**len(r)
    weights=tuple((g,s,9*prior[g]*scale*
                   19**sum(law(g,s,x)==y for x,y,_ in r))
                  for g in FORMS for s in SUBSETS)
    unknown=Fraction(63*20**len(r),1)
    den=sum((w for _,_,w in weights),Fraction())+unknown
    assert den>0
    return {"schema":MODEL,"rows":r,"memory_digest":mem["digest"],
            "weights":weights,"unknown":unknown,"denominator":den}

def predict_probability(model,x):
    if type(model) is not dict or model.get("schema")!=MODEL:
        raise ValueError("WSP151_BAD_MODEL")
    if type(x) is not int or not 0<=x<64:
        raise ValueError("WSP151_BAD_ACTION")
    positive=sum((w for g,s,w in model["weights"] if law(g,s,x)),Fraction())
    return (positive+model["unknown"]/2)/model["denominator"]

def readout(model,min_confidence=Fraction(99,100)):
    if min_confidence!=Fraction(99,100):
        raise ValueError("WSP151_FROZEN_CONFIDENCE_ONLY")
    out=[]
    for x in range(64):
        p=predict_probability(model,x)
        out.append(1 if p>=min_confidence else
                   (0 if p<=1-min_confidence else None))
    return tuple(out)

def _entropy(probs):
    return -sum(v*log2(v) for v in probs if v>0)

def _outcome_mass(model,x,y):
    mass=[Fraction(),Fraction(),Fraction()]
    for g,s,w in model["weights"]:
        factor=Fraction(19,20) if law(g,s,x)==y else Fraction(1,20)
        mass[0 if g=="OR" else 1]+=w*factor
    mass[2]=model["unknown"]/2
    return tuple(mass)

def propose_next(rows,mem=None):
    """Maximize expected information about OR/AND/UNKNOWN, never ask owner."""
    r=validate_rows(rows)
    if len(r)>=8:raise ValueError("WSP151_ACTION_BUDGET_EXHAUSTED")
    model=fit(r,mem)
    masses=[sum((w for kind,_,w in model["weights"] if kind==g),Fraction())
            for g in FORMS]+[model["unknown"]]
    den=model["denominator"]
    before=_entropy([float(w/den) for w in masses])
    spent={x for x,_,_ in r}
    selected=None
    score=-float("inf")
    for x in range(64):
        if x in spent:continue
        m0,m1=_outcome_mass(model,x,0),_outcome_mass(model,x,1)
        after=0.0
        for v in (m0,m1):
            total=sum(v)
            if total:
                after+=float(total/den)*_entropy([float(t/total) for t in v])
        eig=before-after
        if eig>score+1e-12:
            selected,score=x,eig
    assert selected is not None
    return selected
