"""New disjoint public sequential causal RET01 DEVELOPMENT source.

No protected scientific first-use, private external data, or hidden mediator
supplied to the learner. Regime tags below exist for independent EVALUATION
only; the model sees just identifier, two public projections and actual
observed action/consequence row after making its forecast.
"""
import hashlib

SEEDS=(97241,97259)
WORLDS=(0,1)
EVENTS=32
PHASES=("warm_A","stable_A","early_B","late_B","early_return_A","late_return_A")


def _bit(seed,world,t,tag):
    return hashlib.sha256(
        f"YGG-RET01/development-source/{seed}/{world}/{t}/{tag}".encode()
    ).digest()[0]&1


def _phase(t):
    if t<4:return "warm_A"
    if t<16:return "stable_A"
    if t<20:return "early_B"
    if t<24:return "late_B"
    if t<28:return "early_return_A"
    return "late_return_A"


def generate(seed,world):
    if seed not in SEEDS or world not in WORLDS:
        raise ValueError("RET01_UNREGISTERED_DEVELOPMENT_SEED")
    u,v,w=(_bit(seed,world,-1,k) for k in ("u","v","w"))
    hidden=_bit(seed,world,-1,"hidden")
    events=[]
    for t in range(EVENTS):
        first=_bit(seed,world,t,"intervene1")
        second=_bit(seed,world,t,"intervene2")
        disturbance=_bit(seed,world,t,"shock")&_bit(seed,world,t,"rare")
        regime=int(16<=t<24)
        views=((u,v),(u,w))
        if world==0:
            s2=v^(first&u)^(regime&hidden)
            y=u^(second&s2)^(regime&v)^(hidden&first)
            u,v,w=(v^(first&w),s2,w^(second&u)^disturbance)
            hidden=hidden^(first&w)^(regime&u)
        else:
            s2=u^(first&w)^(regime&v)
            y=w^(second&s2)^(regime&u)^(hidden&second)
            u,v,w=(u^(first&v)^disturbance,s2,v^(second&w))
            hidden=hidden^(second&v)^(regime&w)
        assert all(z in (0,1) for z in (u,v,w,s2,y))
        identifier=hashlib.sha256(
            f"YGG-RET01/public-source/{seed}/{world}/{t}".encode()
        ).hexdigest()
        events.append({
            "source_id":identifier,"views":views,
            "row":{"s1":views[0][0],"x1":first,"s2":s2,"x2":second,"y":y},
            "seed":seed,"world":world,"index":t,
            "phase":_phase(t), # evaluator ONLY
        })
    assert len(events)==EVENTS
    assert len({e["source_id"] for e in events})==EVENTS
    return tuple(events)

