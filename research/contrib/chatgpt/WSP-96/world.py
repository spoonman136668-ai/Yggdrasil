"""WSP96 hidden U is a genuine common cause of LOGGED action and outcome.

Randomized do(a) breaks that assignment confounding. There is no U, latent
mask or true action effect in any method's source observation. Original
finite synthetic XOR world only; not a general nonparametric causal oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import hashlib
import random

BITS=5
MASK=(1<<BITS)-1
N_ACTIONS=6
PROB_U=.25
PROB_NOISE=.04
DO_PER_ACTION=24
OBS_COUNT=N_ACTIONS*DO_PER_ACTION

def _rng(key:str)->random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(key.encode("ascii")).digest()[:8],"big"))

def _id(key:str)->str:
    return hashlib.sha256(key.encode("ascii")).hexdigest()[:16]

def rank_gf2(items:tuple[int,...])->int:
    basis={}
    for bitvec in items:
        x=bitvec
        while x:
            p=x.bit_length()-1
            if p in basis:x^=basis[p]
            else:
                basis[p]=x
                break
    return len(basis)

@dataclass(frozen=True)
class Goal:
    id:int
    start:int
    target:int
    max_actions:int=3
    def request(self):
        return {"start":self.start,"target":self.target,"max_actions":self.max_actions}

class HiddenConfoundedWorld:
    def __init__(self,seed:int):
        if type(seed) is not int or not (1<=seed<=1000000):
            raise ValueError("invalid original world seed")
        self.seed=seed
        rng=_rng(f"WSP96/hidden-world/{seed}")
        null=_id(f"WSP96/null/{seed}")
        active=sorted(_id(f"WSP96/active/{seed}/{i}") for i in range(5))
        self.actions=tuple(sorted((null,)+tuple(active)))
        self.control_id=null
        self.active_actions=tuple(active)
        self._favorite=rng.choice(active)
        self._latent_mask=sum(1<<i for i in rng.sample(range(BITS),2))
        for attempt in range(1024):
            effects=tuple(rng.randrange(1,MASK+1) for _ in range(5))
            if rank_gf2(effects)==5:
                break
        else:
            raise RuntimeError("failed to construct full-rank actions")
        self._effects={null:0}
        self._effects.update(dict(zip(active,effects)))
        self._observational_hidden=[]
        self._goals=None

    def _outcome(self,action:str,u:bool,rng:random.Random)->int:
        y=self._effects[action]^(self._latent_mask if u else 0)
        for bit in range(BITS):
            if rng.random()<PROB_NOISE:y^=1<<bit
        return y

    def randomized_interventions(self)->tuple[dict,...]:
        """Twenty-four real randomized do observations for every action."""
        rows=[]
        for action in self.actions:
            for index in range(DO_PER_ACTION):
                r=_rng(f"WSP96/do/{self.seed}/{action}/{index}")
                u=r.random()<PROB_U
                rows.append({"action_id":action,"trial":index,
                             "observed_outcome":self._outcome(action,u,r)})
        return tuple(rows)

    def biased_observational_log(self)->tuple[dict,...]:
        """U is hidden from the return value but influences assignment and Y."""
        rows=[]
        hidden=[]
        for index in range(OBS_COUNT):
            r=_rng(f"WSP96/observation/{self.seed}/{index}")
            u=r.random()<PROB_U
            favor=r.random()<(0.90 if u else 0.04)
            others=[a for a in self.actions if a!=self._favorite]
            action=self._favorite if favor else r.choice(others)
            rows.append({"action_id":action,"trial":index,
                         "observed_outcome":self._outcome(action,u,r)})
            hidden.append((action,u))
        self._observational_hidden=tuple(hidden)
        return tuple(rows)

    def goals(self)->tuple[Goal,...]:
        if self._goals is None:
            r=_rng(f"WSP96/frozen-goals/{self.seed}")
            goals=[]
            for n in (2,3):
                for generating_actions in combinations(self.active_actions,n):
                    start=r.randrange(0,MASK+1)
                    target=start
                    for a in generating_actions:
                        target^=self._effects[a]
                    goals.append(Goal(len(goals),start,target))
            if len(goals)!=20:
                raise AssertionError("not the frozen 10 pairs + 10 triples")
            self._goals=tuple(goals)
        return self._goals

    def execute(self,start:int,plan:tuple[str,...]|None)->int|None:
        if (plan is None or type(start) is not int or not(0<=start<=MASK) or
            not isinstance(plan,tuple) or len(plan)>3 or len(set(plan))!=len(plan) or
            any(a not in self._effects for a in plan)):
            return None
        state=start
        for action in plan:
            state^=self._effects[action]
        return state

    def audit_after_scoring(self)->dict:
        """Evaluator-only private hidden-world truth, NEVER sent to methods."""
        if len(self._observational_hidden)!=OBS_COUNT:
            raise ValueError("original observational source not yet produced")
        favored=[u for a,u in self._observational_hidden if a==self._favorite]
        others=[u for a,u in self._observational_hidden if a!=self._favorite]
        if not favored or not others:raise ValueError("missing observational policy overlap")
        p_favorite=sum(favored)/len(favored)
        p_other=sum(others)/len(others)
        fingerprint=_id(f"WSP96/audit/{self.seed}/{self._favorite}/{self._latent_mask}/"
                        +"/".join(f"{a}:{x}" for a,x in sorted(self._effects.items())))
        return {
            "hidden_fingerprint":fingerprint,
            "favorite":self._favorite,
            "latent_mask":self._latent_mask,
            "true_effects":dict(self._effects),
            "observed_prevalence_u_favorite":p_favorite,
            "observed_prevalence_u_others":p_other,
            "genuine_common_cause_observed":p_favorite-p_other>.45,
            "favored_records":len(favored),
            "other_records":len(others),
        }
