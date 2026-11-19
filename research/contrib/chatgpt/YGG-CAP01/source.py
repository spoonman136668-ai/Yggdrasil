"""YGG-CAP01: disjoint public causal development actions for capacity proof.

These are new *synthetic development* interventions, not protected original
owner first-use, externally grounded observations, or scientific acceptance.
Private family/phase/mediator are evaluator-only; learners see only paired public
views, publicly announced actions and subsequently observed public outcomes.
"""
from __future__ import annotations
import hashlib

SEEDS=(99601,99603)
EVENTS=32
PHASES=("A","B","A_return")

def require(value,code):
    if not value:
        raise ValueError("CAP01_SOURCE_"+code)

def bit(seed,t,tag):
    return hashlib.sha256(
        f"YGG-CAP01/disjoint-development/{seed}/{t}/{tag}".encode("ascii")
    ).digest()[0]&1

def phase(t):
    require(type(t) is int and 0<=t<EVENTS,"INDEX")
    return "A" if t<12 else "B" if t<22 else "A_return"

def announced_plan(seed,t):
    require(seed in SEEDS and type(t) is int and 0<=t<EVENTS,
            "PUBLIC_PLAN")
    return (bit(seed,t,"x1"),bit(seed,t,"x2"))

def generate(seed):
    require(seed in SEEDS,"SEED")
    family=SEEDS.index(seed)
    u,v,w=[bit(seed,-1,k) for k in ("u","v","w")]
    latent=bit(seed,-1,"latent")
    events=[]
    for t in range(EVENTS):
        a,b=announced_plan(seed,t)
        shift=1 if 12<=t<22 else 0
        disturbance=bit(seed,t,"shock")&bit(seed,t,"rare")
        views=((u,v),(v,w))
        if family==0:
            nu=v^(a&u)^(shift&latent)
            nv=u^(b&latent)^(a&w)^disturbance
            nw=w^(a&latent)^(shift&b)^(u&v)
            y=nw^(nv&b)^(latent&a)
            latent_next=latent^(a&w)^(b&u)
        else:
            nu=w^(a&v)^(shift&latent)
            nv=v^(b&u)^(a&latent)^disturbance
            nw=u^(b&v)^(shift&latent)
            y=nu^(nv&b)^(nw&a)^latent
            latent_next=latent^(b&u)^(a&w)
        require(all(type(x) is int and x in (0,1) for x in
                    (nu,nv,nw,y)),"OUTCOME")
        identifier=hashlib.sha256(
            f"YGG-CAP01/public-id/{seed}/{t}".encode("ascii")
        ).hexdigest()
        events.append({
            "identifier":identifier,
            "views":views,
            "actions":(a,b),
            "post":(nu,nv,nw),
            "row":{"s1":u,"x1":a,"s2":nv,"x2":b,"y":y},
            "phase":phase(t), # evaluator ONLY
            "seed":seed, # evaluator ONLY
            "family":family, # evaluator ONLY
            "index":t,
        })
        u,v,w,latent=nu,nv,nw,latent_next
    require(len(events)==EVENTS and
            len({e["identifier"] for e in events})==EVENTS,
            "SOURCE_COUNT")
    for e,f in zip(events,events[1:]):
        require(e["post"]==
                (f["views"][0][0],f["views"][0][1],f["views"][1][1]),
                "OBSERVED_STATE_CONTINUITY")
    return tuple(events)
