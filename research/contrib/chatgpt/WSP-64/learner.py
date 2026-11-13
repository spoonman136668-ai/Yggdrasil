"""WSP64 source-blind variable-width sparse numerical causal learner.

No source simulator, physics family, hidden state or oracle access. Learns
dynamic binary sensor dimension from the first charged observation, retains
all degree<=2 GF(2) polynomials with <=3 monomials consistent with physical
consequences, and predicts only if all retained functions agree.
This is deliberately a *preselected sparse Boolean basis*, not a universal
representation grammar or a trained neural network.
"""
from __future__ import annotations
from collections import deque
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json

ACTIONS=tuple(range(4))
MAX_CHARGES=64
MAX_SENSOR_BITS=5
MAX_SNAPSHOT_BYTES=300000


def _canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def _state(value,bits):
    if (type(value) is not tuple or len(value)!=bits or
            any(type(x) is not int or x not in (0,1) for x in value)):
        raise ValueError("invalid public binary sensor state")
    return value


@lru_cache(maxsize=3)
def _terms(n):
    if type(n) is not int or n not in (3,4,5):
        raise ValueError("outside variable-sensor experiment dimensions")
    return tuple(tuple(t) for degree in (0,1,2)
                 for t in combinations(range(n),degree))


@lru_cache(maxsize=3)
def _sparse_candidates(n):
    width=len(_terms(n))
    return tuple(sum(1<<i for i in idx)
                 for degree in range(4)
                 for idx in combinations(range(width),degree))


def _feature_mask(bits):
    terms=_terms(len(bits))
    return sum(1<<index for index,monomial in enumerate(terms)
               if all(bits[i] for i in monomial))


class SparseWorldLearner:
    gradient_updates=0

    def __init__(self):
        self.dimension=None
        self.ledger=[]
        self.state=None
        self.state_visits={}
        self._models={}
        self.last_plan_expansions=0

    def observe(self,observation):
        before=observation.before
        after=observation.after
        action=observation.action
        charge=observation.action_cost
        if (type(before) is not tuple or len(before) not in (3,4,5)):
            raise ValueError("invalid sensor width")
        if self.dimension is None:
            dimension=len(before)
            _state(before,dimension)
            if before!=(0,)*dimension:
                raise ValueError("noninitial physical start")
            self.dimension=dimension
            self.state=before
            self.state_visits={before:1}
        _state(before,self.dimension)
        _state(after,self.dimension)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid channel")
        if type(charge) is not int or charge!=1 or len(self.ledger)>=MAX_CHARGES:
            raise ValueError("invalid/excess physical action charge")
        if before!=self.state:
            raise ValueError("illegal physical teleport in ledger")
        self.ledger.append((before,action,after))
        self.state=after
        self.state_visits[after]=self.state_visits.get(after,0)+1
        self._models.clear()

    def _model(self,action):
        if self.dimension is None:
            return None
        if action in self._models:
            return self._models[action]
        rows=[(b,after) for b,a,after in self.ledger if a==action]
        if not rows:
            self._models[action]=None
            return None
        features=[(_feature_mask(b),after) for b,after in rows]
        universe=_sparse_candidates(self.dimension)
        result=[]
        for bit in range(self.dimension):
            consistent=tuple(mask for mask in universe
                if all(((feature & mask).bit_count() & 1)==after[bit]
                       for feature,after in features))
            result.append(consistent)
        self._models[action]=tuple(result)
        return self._models[action]

    def predict(self,before,action,memory_only=False):
        if self.dimension is None:
            return None
        before=_state(before,self.dimension)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid action")
        if memory_only:
            observed={after for b,a,after in self.ledger
                      if before==b and action==a}
            return next(iter(observed)) if len(observed)==1 else None
        hypotheses=self._model(action)
        if hypotheses is None:
            return None
        f=_feature_mask(before)
        output=[]
        for candidates in hypotheses:
            if not candidates:
                return None
            votes={((f & mask).bit_count() & 1) for mask in candidates}
            if len(votes)!=1:
                return None
            output.append(next(iter(votes)))
        return tuple(output)

    def select_action(self):
        if self.state is None:
            # Before observing any physics only action IDs are known.
            return 0
        observed={(b,a) for b,a,after in self.ledger}
        counts={a:sum(q==a for b,q,y in self.ledger) for a in ACTIONS}
        options=[]
        for action in ACTIONS:
            p=self.predict(self.state,action)
            novel=int((self.state,action) not in observed)
            unexplored=int(p is not None and p not in self.state_visits)
            uncertain=int(p is None)
            options.append((8*unexplored+4*novel+2*uncertain-
                            counts[action]/1000,-action,action))
        return max(options)[2]

    def contradictory_pairs(self):
        observed={}
        for before,action,after in self.ledger:
            observed.setdefault((before,action),set()).add(after)
        return tuple(sorted((before,action) for (before,action),outputs
                            in observed.items() if len(outputs)>1))

    def inconsistent_channels(self):
        return tuple(action for action in ACTIONS
                     if (self._model(action) is not None and
                         any(len(v)==0 for v in self._model(action))))

    def hypothesis_counts(self):
        return tuple(tuple(len(options) for options in (self._model(a) or ()))
                     for a in ACTIONS)

    def numeric_basis_terms(self):
        return len(_terms(self.dimension)) if self.dimension else 0

    def plan(self,start,target,horizon=6,memory_only=False):
        if self.dimension is None:
            return None
        start=_state(start,self.dimension)
        target=_state(target,self.dimension)
        if type(horizon) is not int or horizon!=6:
            raise ValueError("frozen six-step horizon")
        self.last_plan_expansions=0
        if start==target:
            return ()
        q=deque([(start,())])
        seen={start}
        while q:
            before,path=q.popleft()
            if len(path)>=horizon: continue
            self.last_plan_expansions+=1
            for action in ACTIONS:
                next_state=self.predict(before,action,memory_only=memory_only)
                if next_state is None: continue
                candidate=path+(action,)
                if next_state==target:
                    return candidate
                if next_state not in seen:
                    seen.add(next_state)
                    q.append((next_state,candidate))
        return None

    def snapshot(self):
        payload={
            "schema":"wsp64.sparse-variable-state.v1",
            "dimension":self.dimension,
            "ledger":[[list(b),a,list(after)] for b,a,after in self.ledger],
            "gradient_updates":0
        }
        digest=sha256(_canon(payload).encode("ascii")).hexdigest()
        result=_canon({"payload":payload,"sha256":digest})
        if len(result.encode("ascii"))>MAX_SNAPSHOT_BYTES:
            raise OverflowError("knowledge memory ceiling")
        return result

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw.encode("utf-8"))>MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid snapshot bytes")
        try:
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("malformed snapshot envelope")
            p=obj["payload"]
            if (type(p) is not dict or
                    p.get("schema")!="wsp64.sparse-variable-state.v1" or
                    p.get("gradient_updates")!=0 or
                    sha256(_canon(p).encode("ascii")).hexdigest()!=obj["sha256"]):
                raise ValueError("incorrect memory schema/hash")
            if type(p.get("ledger")) is not list or len(p["ledger"])>MAX_CHARGES:
                raise ValueError("bad stored ledger")
            learner=cls()
            for row in p["ledger"]:
                if type(row) is not list or len(row)!=3:
                    raise ValueError("bad stored physical observation")
                b,a,after=row
                class PublicExperience:
                    pass
                x=PublicExperience()
                x.before,x.action,x.after,x.action_cost=(tuple(b),a,tuple(after),1)
                learner.observe(x)
            if learner.dimension!=p["dimension"] or learner.snapshot()!=raw:
                raise ValueError("snapshot state mismatch")
            return learner
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError,
                json.JSONDecodeError) as exc:
            raise ValueError("invalid or tampered knowledge snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
