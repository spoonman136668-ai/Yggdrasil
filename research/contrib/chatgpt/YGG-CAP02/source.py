"""CAP02 disjoint action sequence continuing ACTUAL CAP01 public causal source.

Existing original CAP01 32 interventions are authenticated by an unchanged git
blob. This new synthetic development future is generated only for seeds in the
frozen prereg; hidden dynamics/phase never enter native learning.
"""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"YGG-CAP01"/"source.py"
PARENT_BLOB="9e34144de876778d8931b7dacce9b990bb36716a"
SEED_MAP={99811:99601,99829:99603}
EVENTS=48
PHASES=("A","B","A_return")

def require(ok,tag):
    if not ok:
        raise ValueError("CAP02_SOURCE_"+tag)

def parent():
    spec=importlib.util.spec_from_file_location("cap02_pinned_parent_source",PARENT)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def bit(seed,t,tag):
    return hashlib.sha256(
        f"YGG-CAP02/disjoint-interventions/{seed}/{t}/{tag}".encode("ascii")
    ).digest()[0]&1

def phase(t):
    require(type(t) is int and 0<=t<EVENTS,"INDEX")
    return "A" if t<16 else "B" if t<32 else "A_return"

def announced_plan(seed,t):
    require(seed in SEED_MAP and type(t) is int and 0<=t<EVENTS,
            "PUBLIC_ANNOUNCED_PLAN")
    return bit(seed,t,"x1"),bit(seed,t,"x2")

def generate(seed):
    require(seed in SEED_MAP,"SEED")
    p=parent()
    parent_seed=SEED_MAP[seed]
    old=p.generate(parent_seed)
    require(len(old)==32 and
            len({e["identifier"] for e in old})==32,
            "PINNED_PARENT_OLD_TAPE")
    family=p.SEEDS.index(parent_seed)
    latent=p.bit(parent_seed,-1,"latent")
    for event in old:
        u=event["views"][0][0]
        w=event["views"][1][1]
        a,b=event["actions"]
        latent^=(a&w)^(b&u)
    u,v,w=old[-1]["post"]
    original=(u,v,w)
    result=[]
    for t in range(EVENTS):
        a,b=announced_plan(seed,t)
        shift=int(16<=t<32)
        shock=bit(seed,t,"shock")&bit(seed,t,"rare")
        views=((u,v),(v,w))
        if family==0:
            nu=v^(a&u)^(shift&latent)
            nv=u^(b&latent)^(a&w)^shock
            nw=w^(a&latent)^(shift&b)^(u&v)
            reward=nw^(nv&b)^(latent&a)
        else:
            nu=w^(a&v)^(shift&latent)
            nv=v^(b&u)^(a&latent)^shock
            nw=u^(b&v)^(shift&latent)
            reward=nu^(nv&b)^(nw&a)^latent
        latent^=(a&w)^(b&u)
        require(all(type(k) is int and k in (0,1)
                    for k in (nu,nv,nw,reward)), "SOURCE_BITS")
        identifier=hashlib.sha256(
            f"YGG-CAP02/public-id/{seed}/{t}".encode("ascii")
        ).hexdigest()
        result.append({
            "identifier":identifier,
            "views":views,
            "actions":(a,b),
            "post":(nu,nv,nw),
            "row":{"s1":u,"x1":a,"s2":nv,"x2":b,"y":reward},
            "seed":seed,           # evaluator only
            "family":family,       # evaluator only
            "phase":phase(t),      # evaluator only
            "index":t,
        })
        u,v,w=nu,nv,nw
    require(len(result)==EVENTS and
            len({e["identifier"] for e in result})==EVENTS and
            original==old[-1]["post"], "DISJOINT_SOURCE_COUNT")
    for a,b in zip(result,result[1:]):
        require(a["post"]==(b["views"][0][0],b["views"][0][1],
                            b["views"][1][1]),"CONTIGUOUS_PUBLIC_SOURCE")
    require(result[0]["views"]==((original[0],original[1]),
                                 (original[1],original[2])),
            "ACTUAL_CAP01_PUBLIC_CONTINUITY")
    return tuple(result)
