"""WSP63 source-blind compressed physical action-effect learner.

A learned action channel is represented by one affected sensor bit and a
7-dimensional degree<=2 Boolean trigger over the *other three* bits. The
single-affected-bit structural assumption is a declared source-family prior,
not a universal fact; cubic out-of-basis sources explicitly test its safety.
Only charged chronological physical observations update this numerical model.
"""
from __future__ import annotations
from itertools import combinations
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"WSP-61"))
from learner import ReachableCausalLearner, _state, ACTIONS, _canon
sys.path.insert(0,str(HERE/"WSP-62"))
from expanded_learner import _linear_basis, _certain_value

TERMS=((),(0,),(1,),(2,),(0,1),(0,2),(1,2))
COEFFICIENTS=len(TERMS)
MAX_SNAPSHOT_BYTES=300000


def trigger_features(before, other_dims):
    return sum(1<<column for column,term in enumerate(TERMS)
               if all(before[other_dims[j]] for j in term))


class CompressedEffectLearner(ReachableCausalLearner):
    gradient_updates=0

    def __init__(self):
        super().__init__()
        self._effect_cache={}

    def observe(self,experience):
        super().observe(experience)
        self._effect_cache.clear()

    def _effect(self,action):
        if action in self._effect_cache:
            return self._effect_cache[action]
        rows=[(before,after) for before,a,after in self.ledger if a==action]
        if not rows:
            self._effect_cache[action]=None
            return None
        touched=set()
        invalid=False
        for before,after in rows:
            changed=[bit for bit in range(4) if before[bit]!=after[bit]]
            if len(changed)>1:
                invalid=True
            elif changed:
                touched.add(changed[0])
        if invalid or len(touched)!=1:
            # No observed toggle cannot identify the action's target.
            # Multiple changed bits violate the prior; both abstain.
            self._effect_cache[action]=None
            return None
        target=next(iter(touched))
        other=tuple(bit for bit in range(4) if bit!=target)
        equations=[
            (trigger_features(before,other),before[target]^after[target])
            for before,after in rows
        ]
        model=_linear_basis(equations,COEFFICIENTS)
        self._effect_cache[action]=(
            {"target":target,"other":other,"basis":model,
             "consistent":model is not None,
             "rank":len(model) if model is not None else -1}
        )
        return self._effect_cache[action]

    def predict(self,before,action,memory_only=False):
        before=_state(before)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid physical action")
        if memory_only:
            return super().predict(before,action,memory_only=True)
        exact=super().predict(before,action,memory_only=True)
        if exact is not None:
            return exact
        effect=self._effect(action)
        if effect is None or not effect["consistent"]:
            return None
        value=_certain_value(
            effect["basis"],
            trigger_features(before,effect["other"])
        )
        if value is None:
            return None
        out=list(before)
        out[effect["target"]] ^= value
        return tuple(out)

    def rank_receipts(self):
        return tuple({
            "action":action,
            "affected_bit":self._effect(action)["target"]
                           if self._effect(action) is not None else None,
            "identified_equation_rank":self._effect(action)["rank"]
                           if self._effect(action) is not None else 0,
            "candidate_basis_dimensions":COEFFICIENTS
        } for action in ACTIONS)

    def identified_numeric_dimensions(self):
        return sum(max(0,self._effect(action)["rank"])
                   for action in ACTIONS if self._effect(action) is not None)

    def snapshot(self):
        data={
            "schema":"wsp63.compressed-effect.v1",
            "ledger":[[list(b),a,list(y)] for b,a,y in self.ledger],
            "gradient_updates":0
        }
        h=sha256(_canon(data).encode("ascii")).hexdigest()
        raw=_canon({"payload":data,"sha256":h})
        if len(raw.encode("ascii"))>MAX_SNAPSHOT_BYTES:
            raise OverflowError("physical knowledge snapshot too large")
        return raw

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw.encode("utf-8"))>MAX_SNAPSHOT_BYTES:
            raise ValueError("bad snapshot bytes")
        try:
            env=json.loads(raw)
            if type(env) is not dict or set(env)!={"payload","sha256"}:
                raise ValueError("invalid snapshot envelope")
            data=env["payload"]
            if (type(data) is not dict or
                    data.get("schema")!="wsp63.compressed-effect.v1" or
                    data.get("gradient_updates")!=0 or
                    sha256(_canon(data).encode("ascii")).hexdigest()!=env["sha256"]):
                raise ValueError("snapshot schema/hash mismatch")
            rows=data["ledger"]
            if type(rows) is not list or len(rows)>48:
                raise ValueError("invalid experience budget")
            obj=cls()
            for row in rows:
                if type(row) is not list or len(row)!=3:
                    raise ValueError("invalid evidence row")
                before,action,after=row
                class Experience:
                    pass
                e=Experience()
                e.before,e.action,e.after,e.action_cost=tuple(before),action,tuple(after),1
                obj.observe(e)
            if obj.snapshot()!=raw:
                raise ValueError("noncanonical or inconsistent stored evidence")
            return obj
        except (TypeError,KeyError,IndexError,UnicodeError,
                ValueError,json.JSONDecodeError) as ex:
            raise ValueError("malformed/tampered snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
