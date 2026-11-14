"""WSP97 observationally equivalent structural causal worlds.

Causal SCM:     U -> A, A -> Y=f(context,setting,A)
Confounded SCM: U -> A, U -> Y=f(context,setting,U)

In PASSIVE data A=U, so both SCMs have literally byte-identical source
observations. Under real do(A=a), A is set independently of U, separating
the two causal explanations. Source methods never see private U or regime.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random

CONTEXTS=8
ALLOWED_PROBE_CONTEXTS=(0,1)
HELDOUT_CONTEXTS=(2,3,4,5,6,7)
PROB_U_ONE=.20
MEASUREMENT_FLIP=.02
DO_BUDGET=3
REGIMES=("action_causal","hidden_proxy")

def digest(key:str)->str:
    return hashlib.sha256(key.encode("ascii")).hexdigest()

def rng(key:str)->random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(key.encode("ascii")).digest()[:8],"big"))

@dataclass(frozen=True)
class Query:
    context_id:int
    setting:int
    action:int

    def as_input(self)->dict:
        return {"context_id":self.context_id,"setting":self.setting,"action":self.action}

class PairedSCM:
    def __init__(self,pair_seed:int,regime:str):
        if type(pair_seed) is not int or pair_seed<=0:
            raise ValueError("invalid causal world source identity")
        if regime not in REGIMES:
            raise ValueError("unknown observational equivalence regime")
        self.pair_seed=pair_seed
        self._regime=regime
        r=rng(f"WSP97/private-function/{pair_seed}")
        self._phase=tuple(r.getrandbits(1) for _ in range(CONTEXTS))
        self._constant=tuple(r.getrandbits(1) for _ in range(CONTEXTS))
        self._informative_setting=tuple(r.getrandbits(1) for _ in range(CONTEXTS))
        self._used={"active":set(),"random":set()}

    def _f(self,context:int,setting:int,input_bit:int)->int:
        if (type(context) is not int or not(0<=context<CONTEXTS) or
            type(setting) is not int or setting not in (0,1) or
            type(input_bit) is not int or input_bit not in (0,1)):
            raise ValueError("world source function domain invalid")
        if setting==self._informative_setting[context]:
            return input_bit ^ self._phase[context]
        return self._constant[context]

    def passive(self)->tuple[dict,...]:
        """Exact same source records for both causal regimes, no U exposed."""
        rows=[]
        for context in range(CONTEXTS):
            for setting in (0,1):
                for action in (0,1):
                    # U=action in this OBSERVATIONAL regime; do(A) not invoked.
                    rows.append({"context_id":context,"setting":setting,
                                 "action":action,
                                 "observed_y":self._f(context,setting,action)})
        if len(rows)!=32:raise AssertionError("passive source completeness")
        return tuple(rows)

    def randomized_do(self,policy:str,query:dict,probe_index:int)->dict:
        if policy not in self._used:
            raise ValueError("unknown policy source lane")
        if type(probe_index) is not int or not(0<=probe_index<DO_BUDGET):
            raise ValueError("intervention index out of fixed budget")
        if probe_index in self._used[policy] or probe_index!=len(self._used[policy]):
            raise ValueError("replayed, unordered or uncertain-effect intervention")
        if not isinstance(query,dict) or set(query)!={"context_id","setting","action"}:
            raise ValueError("invalid intervention input schema")
        c,b,a=query["context_id"],query["setting"],query["action"]
        if (type(c) is not int or c not in ALLOWED_PROBE_CONTEXTS or
            type(b) is not int or b not in (0,1) or
            type(a) is not int or a not in (0,1)):
            raise ValueError("reserved context or unregistered probe action")
        # Potential U and measurement noise depend ONLY on pair, trial and
        # intervention query; active and random policies therefore see the
        # identical source realization if selecting the same intervention.
        potential=rng(f"WSP97/potential/{self.pair_seed}/{probe_index}/{c}/{b}/{a}")
        u=1 if potential.random()<PROB_U_ONE else 0
        source_input=a if self._regime=="action_causal" else u
        measured=self._f(c,b,source_input)
        if potential.random()<MEASUREMENT_FLIP:
            measured^=1
        self._used[policy].add(probe_index)
        return {"context_id":c,"setting":b,"action":a,
                "observed_y":measured,"probe_index":probe_index}

    def eval_queries(self)->tuple[Query,...]:
        return tuple(Query(c,b,a) for c in HELDOUT_CONTEXTS
                     for b in (0,1) for a in (0,1))

    def majority_do_result(self,query:Query)->int:
        """Evaluator-only do-marginal mode, never seen by any model."""
        input_bit=query.action if self._regime=="action_causal" else 0
        return self._f(query.context_id,query.setting,input_bit)

    def diagnostic(self,query:Query)->bool:
        return (query.context_id in HELDOUT_CONTEXTS and
                query.action==1 and
                self._f(query.context_id,query.setting,0)!=
                self._f(query.context_id,query.setting,1))

    def audit(self)->dict:
        """Private true regime is available to the SCORER only."""
        return {
            "regime":self._regime,
            "private_function_fingerprint":digest(
                f"WSP97/truth/{self.pair_seed}/"
                f"{self._phase}/{self._constant}/{self._informative_setting}"),
            "used_probe_indices":{p:sorted(v) for p,v in self._used.items()},
        }
