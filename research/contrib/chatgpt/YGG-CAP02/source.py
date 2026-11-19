"""YGG-CAP02: fresh disjoint A/B/A causal continuation with public clock.

No accepted owner first-use. Input start state is the EXACT previously witnessed
CAP01 terminal public post, retaining complete native state continuity.
New source phase/family labels are restricted to the evaluator.
"""
from __future__ import annotations
import hashlib

SEEDS=(99721,99739)
EPISODES=32

def check(x,code):
    if not x:
        raise ValueError("CAP02_FRESH_SOURCE_"+code)

def bit(seed,t,tag):
    return hashlib.sha256(
        f"YGG-CAP02/unseen-continue/{seed}/{t}/{tag}".encode("ascii")
    ).digest()[0]&1

def announced(seed,t):
    check(seed in SEEDS and type(t) is int and 0<=t<EPISODES,
          "ANNOUNCED_ACTION")
    return bit(seed,t,"first"),bit(seed,t,"second")

def phase(t):
    check(type(t) is int and 0<=t<EPISODES,"PHASE")
    return "A" if t<12 else "B" if t<22 else "A_return"

def generate(seed, previous_post):
    check(seed in SEEDS,"SEED")
    check(type(previous_post) is tuple and len(previous_post)==3 and
          all(type(x) is int and x in (0,1) for x in previous_post),
          "EXACT_PREVIOUS_POST")
    family=SEEDS.index(seed)
    u,v,w=previous_post
    latent=bit(seed,-1,"private_mediator")
    tape=[]
    for t in range(EPISODES):
        a,b=announced(seed,t)
        shift=int(12<=t<22)
        noise=bit(seed,t,"rare")&bit(seed,t,"shock")
        views=((u,v),(v,w))
        if family==0:
            nu=w^(a&v)^(shift&latent)
            nv=u^(a&w)^(b&v)^(shift&w)^noise
            nw=v^(b&latent)^(a&u)
            y=(nu&b)^nw^(shift&a)^(v&latent)
            latent_next=latent^(b&v)^(a&w)
        else:
            nu=v^(a&latent)^(shift&w)
            nv=w^(a&v)^(shift&latent)^noise
            nw=u^(b&nv)^(shift&a)
            y=(nv&b)^nu^(shift&latent)^(a&w)
            latent_next=latent^(a&u)^(b&v)
        check(all(type(z) is int and z in (0,1) for z in
                  (nu,nv,nw,y)),"BIT_RESULT")
        tape.append({
            "id":hashlib.sha256(
                f"YGG-CAP02/new-witness/{seed}/{t}".encode("ascii")
            ).hexdigest(),
            "views":views,
            "row":{"s1":u,"x1":a,"s2":nv,"x2":b,"y":y},
            "post":(nu,nv,nw),
            "phase":phase(t), # evaluator only
            "family":family, # evaluator only
            "seed":seed, # evaluator only
            "index":t,
        })
        u,v,w,latent=nu,nv,nw,latent_next
    check(len({e["id"] for e in tape})==EPISODES,"DUPLICATE_ID")
    check(all(e["post"]==(n["views"][0][0],
                         n["views"][0][1],n["views"][1][1])
              for e,n in zip(tape,tape[1:])),"CONTINUITY")
    return tuple(tape)
