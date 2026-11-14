"""Source-blind public-evidence-only intervention policy for WSP80.

Never imports the private source, hidden roles, evaluator or transition oracle.
Scores only candidate disagreement at the *current* public state and
unobserved paid state/action coverage; all tie-breaking is deterministic.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from structural_weights import ACTIONS,LOW,HIGH,_survivors,valid_state


class InterventionPolicy:
    def __init__(self):
        self.rows=[{} for _ in ACTIONS]
        self.cached=[None]*6
        self.turn=0

    def observe(self,experience):
        s,a,y=experience.before,experience.action,experience.after
        valid_state(s)
        valid_state(y)
        if type(a) is not int or a not in ACTIONS or experience.action_cost!=1:
            raise ValueError('unpaid or invalid public observation')
        old=self.rows[a].get(s)
        if old is not None and old!=y:
            raise ValueError('inconsistent public observation')
        self.rows[a][s]=y
        self.cached[a]=None
        self.turn+=1

    def _options(self,a):
        if self.cached[a] is None:
            low=_survivors(self.rows[a],LOW)
            if any(not o for o in low):
                high=_survivors(self.rows[a],HIGH)
                self.cached[a]=tuple((high[b],HIGH) if not low[b]
                                     else (low[b],LOW) for b in range(6))
            else:
                self.cached[a]=tuple((o,LOW) for o in low)
        return self.cached[a]

    def choose(self,current):
        valid_state(current)
        scores=[]
        for a in ACTIONS:
            disagreement=0
            for options,terms in self._options(a):
                if not options:
                    disagreement+=1
                    continue
                mask=sum(1<<j for j,t in enumerate(terms) if all(current[k] for k in t))
                first=(options[0]&mask).bit_count()&1
                if any(((alternative&mask).bit_count()&1)!=first for alternative in options[1:]):
                    disagreement+=1
            scores.append(((int(current not in self.rows[a]),
                            disagreement,
                            -len(self.rows[a]),
                            -(a-self.turn)%6),a))
        return max(scores)[1]


class UniformRandomPolicy:
    def __init__(self,seed):
        digest=sha256(f'WSP80|SELFTEST|{seed}|equal-paid-uniform-random'.encode('ascii')).digest()
        self.rng=Random(int.from_bytes(digest,'big'))
    def observe(self,experience):
        valid_state(experience.before)
        valid_state(experience.after)
        if experience.action_cost!=1:
            raise ValueError('unpaid action')
    def choose(self,current):
        valid_state(current)
        return self.rng.randrange(6)


def stage_a_action(seed,index):
    if type(index) is not int or not 0<=index<144:
        raise ValueError('invalid StageA index')
    digest=sha256(f'WSP80|SELFTEST|{seed}|shared-stageA|{index}'.encode('ascii')).digest()
    return int.from_bytes(digest[:8],'big')%6
