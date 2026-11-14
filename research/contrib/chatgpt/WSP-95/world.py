"""WSP95 hidden causal sensor membership with stochastic partial observations.

Development-only deterministic simulator. Real do(action) probes are
independent resets with stable action effects, after-measurement bit corruption,
and two exogenous nuisance channels. True effect/channel membership never
crosses the model interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import hashlib
import random

N_ACTIONS=6
N_CHANNELS=7
N_CAUSAL=5
NOISE=0.12
MASK=(1<<N_CHANNELS)-1

def digest(value:str)->str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()

def seeded(value:str)->random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(value.encode("ascii")).digest()[:8],"big"))

@dataclass(frozen=True)
class Goal:
    index:int
    start:int
    target:int
    max_actions:int=3

    def request(self)->dict:
        return {"start":self.start,"target":self.target,"max_actions":self.max_actions}

class NoisyWorld:
    def __init__(self,seed:int):
        if type(seed) is not int or seed<=0:
            raise ValueError("world seed must be positive integer")
        self.seed=seed
        r=seeded(f"WSP95/world/{seed}")
        self.actions=tuple(sorted(
            digest(f"WSP95/action/{seed}/{i}")[:16] for i in range(N_ACTIONS)))
        positions=list(range(N_CHANNELS))
        r.shuffle(positions)
        self._causal=tuple(sorted(positions[:N_CAUSAL]))
        self._nuisance=tuple(sorted(positions[N_CAUSAL:]))
        signatures=r.sample(range(1,1<<N_CAUSAL),N_ACTIONS)
        self._effects={}
        for action,value in zip(self.actions,signatures):
            effect=0
            for bit,channel in enumerate(self._causal):
                if (value>>bit)&1:
                    effect|=1<<channel
            self._effects[action]=effect
        self._goal_set=None

    def probe(self,action:str,index:int)->dict:
        if action not in self._effects or type(index) is not int or not(0<=index<30):
            raise ValueError("probe action or per-action index invalid")
        r=seeded(f"WSP95/potential/{self.seed}/{action}/{index}")
        before=r.randrange(0,1<<N_CHANNELS)
        after=before^self._effects[action]
        for pos in self._causal:
            if r.random()<NOISE:
                after^=1<<pos
        for pos in self._nuisance:
            # Replace nuisance AFTER reading with independent values.
            if r.getrandbits(1):after|=1<<pos
            else:after&=~(1<<pos)
        return {"action_id":action,"probe_index":index,
                "sensor_before":before,"sensor_after":after}

    def goals(self)->tuple[Goal,...]:
        if self._goal_set is None:
            r=seeded(f"WSP95/goals/{self.seed}")
            result=[]
            for cardinality in (2,3):
                for hidden_original_subset in combinations(self.actions,cardinality):
                    start=r.randrange(0,1<<N_CHANNELS)
                    target=start
                    for act in hidden_original_subset:
                        target^=self._effects[act]
                    result.append(Goal(len(result),start,target))
            if len(result)!=35:
                raise AssertionError("frozen pair/triple goal count")
            self._goal_set=tuple(result)
        return self._goal_set

    def execute(self,start:int,plan:tuple[str,...]|None)->int|None:
        if (plan is None or not isinstance(plan,tuple) or len(plan)>3 or
            len(set(plan))!=len(plan) or any(a not in self._effects for a in plan)):
            return None
        actual=start
        for action in plan:
            actual^=self._effects[action]
        return actual

    def actual_signature(self,action:str)->int:
        """Evaluator-only ground truth; never call in learner or controls."""
        return self._effects[action]

    def actual_causal_channels(self)->tuple[int,...]:
        """Evaluator-only sensor membership after prediction freeze."""
        return self._causal

    def audit_fingerprint(self)->str:
        """Receipted only after model predictions are fixed."""
        content=f"{self.seed}/{self._causal}/{sorted(self._effects.items())}"
        return digest("WSP95/hidden-audit/"+content)
