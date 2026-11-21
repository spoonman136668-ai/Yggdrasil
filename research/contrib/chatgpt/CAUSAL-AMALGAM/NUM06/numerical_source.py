"""NUM06 prospective numerical source. Engineering fixtures ONLY.

The law and roster are defined before any reserved score. All reserved seeds
are explicitly denied, even for short previews. No admission or execution
authority comes from this module. An independently admitted source actor must
implement the reserved realization in a later source-pinned handoff.
"""
from __future__ import annotations
import random
from num05 import digest, public_row

EPISODES = 448
SCALE = 10000
FIXTURES = {620001:(145,305,False), 620003:(165,325,True)}
REGISTERED = {
    "fit": {620101:(145,305),620103:(165,325)},
    "validation": {620111:(177,337),620113:(145,305)},
    "held": {620201:(145,305),620203:(165,325),620207:(177,337)},
    "null": {620211:(165,325),620213:(177,337)},
}
FORBIDDEN_NUM05 = frozenset((520117,520131,520211,520311,520331,520411,520431,520451))
RESERVED = frozenset(seed for group in REGISTERED.values() for seed in group) | FORBIDDEN_NUM05


def _consequence(x,y,a,variant,novel):
    # Integer ticks: deterministic nonlinear response, with within-quadrant
    # variation, cross-coordinate interaction, and action-sensitive slopes.
    xy=x*y//SCALE
    xx=x*x//SCALE
    yy=y*y//SCALE
    k=a-2
    m=variant-3
    if not novel:
        dx=1600*k + 3*x//10 + (a+1)*xy//14 - yy//9 + 120*m
        dy=-900*k + 2*y//5 - (5-a)*xx//18 + xy//7 - 80*m
        reward=(dx-dy)//4 + (a-1)*xy//10 + yy//8
    else:
        dx=-1700*k - 2*x//5 + (5-a)*xy//10 + yy//6 - 130*m
        dy=1100*k - y//2 + (a+1)*xx//10 - xy//5 + 100*m
        reward=-(dx+dy)//3 - (a+1)*xy//13 - xx//7
    return dx,dy,reward


def fixture_world(seed):
    if type(seed) is not int or seed not in FIXTURES or seed in RESERVED:
        raise ValueError("NUM06_SOURCE_NOT_ADMITTED_FIXTURE_ONLY")
    t1,t2,null=FIXTURES[seed]
    rng=random.Random(seed)
    variant=seed%7
    rows=[]
    while len(rows)<EPISODES:
        # Random block lengths, factorial coverage within each complete
        # block, independently shuffled. No action-index clock in packets.
        groups=rng.randrange(1,4)
        schedule=[(a,q) for _ in range(groups) for a in range(5) for q in range(4)]
        rng.shuffle(schedule)
        for a,q in schedule:
            i=len(rows)
            if i==EPISODES:
                break
            x=rng.randrange(1600,12001)*(1 if q&1 else -1)
            y=rng.randrange(1600,12001)*(1 if q&2 else -1)
            dx,dy,reward=_consequence(x,y,a,variant,not null and t1<=i<t2)
            dx+=rng.randrange(-300,301)
            dy+=rng.randrange(-300,301)
            reward+=rng.randrange(-300,301)
            # All actual outcomes are witnessed once through the same packet
            # adapter as the original unchanged NUM05 candidate. Cohort/law
            # metadata stays separate; the source tag means compatibility,
            # NOT that any original NUM05 science cohort is reused.
            eid=digest(f"num06-fixture-v1:{seed}:{i}".encode("ascii"))
            rows.append(public_row(eid,(x/SCALE,y/SCALE),a,
                                   ((x+dx)/SCALE,(y+dy)/SCALE),reward/SCALE))
    return rows, {"fixture_seed":seed,"t1":t1,"t2":t2,"null":null,
                  "source_label":"NUM06_AUTHORED_FIXTURE_ONLY",
                  "source_owner_authenticated":False}
