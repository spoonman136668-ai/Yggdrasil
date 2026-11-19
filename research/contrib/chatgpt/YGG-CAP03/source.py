"""CAP03: matched synthetic branch-reset causal interventions, source-bound.

At a frozen simulated state, perform all four public (a,b) interventions
from that SAME state. Each branch produces an actually witnessed synthetic
consequence; only one preannounced chosen branch advances the world and
cumulative Yggdrasil's sequential native ledger. This is a synthetic
development diagnostic, not physical-world causal evidence.
"""
from __future__ import annotations
import hashlib

SEEDS=(99811,99829)
EPISODES=32
ARMS=((0,0),(0,1),(1,0),(1,1))

def check(ok,reason):
    if not ok:
        raise ValueError("CAP03_SOURCE_"+reason)

def bit(seed,t,name):
    return hashlib.sha256(
        f"YGG-CAP03/paired-fork/{seed}/{t}/{name}".encode("ascii")
    ).digest()[0]&1

def chosen(seed,t):
    check(seed in SEEDS and type(t) is int and 0<=t<EPISODES,
          "REGISTERED_PLAN")
    return bit(seed,t,"choose-a"),bit(seed,t,"choose-b")

def phase(t):
    check(type(t) is int and 0<=t<EPISODES,"PHASE_INDEX")
    return "A" if t<12 else "B" if t<22 else "A_return"

def fork(family,world,latent,a,b,shift,noise):
    u,v,w=world
    ae=a^shift
    if family==0:
        nv=u^(ae&v)^(b&w)^(latent&u)^noise
        y=nv^(ae&w)^b^(latent&v)
        nu=v^(ae&u)^(latent&b)
        nw=w^(ae&latent)^(b&u)
        next_latent=latent^(a&w)^(b&v)
    else:
        nv=w^(ae&u)^b^(latent&v)^noise
        y=(nv&ae)^u^b^(latent&w)
        nu=u^(b&v)^(ae&latent)
        nw=v^(ae&w)^(b&u)
        next_latent=latent^(b&u)^(a&v)
    check(all(type(i) is int and i in (0,1)
              for i in (nu,nv,nw,y,next_latent)),"BINARY_CONSEQUENCE")
    return (nu,nv,nw),y,next_latent

def generate(seed,previous_post):
    check(seed in SEEDS,"REGISTERED_SEED")
    check(type(previous_post) is tuple and len(previous_post)==3 and
          all(type(v) is int and v in (0,1) for v in previous_post),
          "PRIOR_WITNESSED_PUBLIC_POST")
    family=SEEDS.index(seed)
    u,v,w=previous_post
    latent=bit(seed,-1,"private-latent")
    tape=[]
    for t in range(EPISODES):
        public=((u,v),(v,w))
        action=chosen(seed,t)
        switch=int(12<=t<22)
        noise=bit(seed,t,"rare")&bit(seed,t,"shock")
        forks=[]
        for a,b in ARMS:
            post,y,newlatent=fork(family,(u,v,w),latent,a,b,switch,noise)
            forks.append({"action":(a,b),"s2":post[1],
                          "y":y,"post":post,"latent_next":newlatent})
        main=next(f for f in forks if f["action"]==action)
        witness_id=hashlib.sha256(
            f"YGG-CAP03/matched-witness/{seed}/{t}".encode("ascii")
        ).hexdigest()
        tape.append({
            "id":witness_id,"index":t,
            "views":public,"chosen":action,
            # All four alternate branches are witnessed after forecasts.
            # Forks are *not* additional chronological native episodes.
            "forks":tuple({
                "action":f["action"],"s2":f["s2"],
                "y":f["y"],"post":f["post"]
            } for f in forks),
            "selected":{
                "s1":u,"x1":action[0],"s2":main["s2"],
                "x2":action[1],"y":main["y"]
            },
            "post":main["post"],
            "phase":phase(t), # evaluator only, no model input
            "family":family, # evaluator only, no model input
        })
        u,v,w=main["post"]
        latent=main["latent_next"]
    check(len(tape)==EPISODES and
          len({x["id"] for x in tape})==EPISODES,
          "SAMPLED_SOURCE_IDENTITY")
    check(all(
        e["post"]==(n["views"][0][0],n["views"][0][1],
                    n["views"][1][1])
        for e,n in zip(tape,tape[1:])),
        "EXACT_PRIMARY_BRANCH_CONTINUITY")
    return tuple(tape)
