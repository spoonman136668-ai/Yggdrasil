"""WSP83 source-blind direct weight programming: compose missing XOR features.

Reuses the ORIGINAL WSP82 public 135-gate ReLU atom basis unchanged.
Learns from 384 continuously charged public observations either one atom
or a minimum-description two-atom GF(2) composition for each output-bit
residual. Computes signatures by numeric ReLU gates, NOT from source
labels/secret physics, and compiles dense numeric 0/1 readout weights.
The XOR composition operator is researcher-supplied: NO AGI claim.
"""
from __future__ import annotations
from hashlib import sha256
from math import isfinite
import json
from temporal_weights import (
    PaidTemporalFeatureEditor, FEATURES, COST, STATES, ACTIONS,
    _numeric_features, _valid, _relu, canonical
)

SCHEMA="wsp83.numeric-xor-two-public-atoms.v1"
MAX_SNAPSHOT_BYTES=150000
MAX_MODELS_PER_OUTPUT=200


def _onehot_pair(pair):
    row=[0.0]*len(FEATURES)
    for index in pair:
        row[index]=1.0
    return row


class PaidXorComposer(PaidTemporalFeatureEditor):
    def compile(self):
        if self._rows is None or self.charges != 384:
            raise ValueError("exactly 384 paid, unbroken public actions required")
        signatures=[0]*len(FEATURES)
        residual=[0]*6
        for n,(before,action,after,history) in enumerate(self._rows):
            gates=_numeric_features(action,history)
            for j,v in enumerate(gates):
                if v>=0.5:
                    signatures[j]|=1<<n
            for bit in range(6):
                if before[bit]^after[bit]^int(action==bit):
                    residual[bit]|=1<<n
        inverted={}
        for j,signature in enumerate(signatures):
            inverted.setdefault(signature,[]).append(j)
        complexity=[COST[f[0]] for f in FEATURES]
        chosen=[]
        for output in residual:
            options=[]
            for i,signature in enumerate(signatures):
                if signature==output:
                    options.append((complexity[i],(i,)))
                for j in inverted.get(signature^output,()):
                    if j>i:
                        options.append((complexity[i]+complexity[j]+2,(i,j)))
            if not options:
                raise ValueError("missing causal feature not expressible by 2-atom XOR")
            least=min(c for c,_ in options)
            winner=sorted(p for c,p in options if c==least)
            if len(winner)>MAX_MODELS_PER_OUTPUT:
                raise ValueError("ambiguous composite exceeds frozen capacity")
            chosen.append(winner)
        rows=[[_onehot_pair(pair) for pair in candidates]
              for candidates in chosen]
        self._compiled={
            "schema":SCHEMA,
            "charges":384,
            "basis_count":len(FEATURES),
            "numeric_output_weights":rows,
        }
        return {
            "paid_actions":self.charges,
            "basis_primitive_count":len(FEATURES),
            "composed_two_atom_XOR_outputs":sum(
                any(len(pair)==2 for pair in candidates)
                for candidates in chosen),
            "composite_hypotheses_per_bit":[len(x) for x in chosen],
            "numeric_programmed_weights":sum(
                len(row)*len(FEATURES) for row in rows),
            "cold_restorable":True,
        }

    def predict(self,state,action,history=()):
        if not _valid(state,action,history) or self._compiled is None:
            raise ValueError("bad input or uncompiled XOR model")
        gates=_numeric_features(action,history)
        result=[]
        for bit,possibilities in enumerate(
                self._compiled["numeric_output_weights"]):
            effects=set()
            for row in possibilities:
                z=sum(w*v for w,v in zip(row,gates))
                if not isfinite(z) or z not in (0.0,1.0,2.0):
                    raise ArithmeticError("numeric learned XOR gate invalid")
                # One or two learned ReLU atom outputs; 0/1 XOR is
                # implemented as a new numeric ReLU stage.
                effect=z-2.0*_relu(z-1.0)
                effects.add(int(effect))
            if len(effects)!=1:
                return None
            result.append((state[bit]+int(action==bit)+next(iter(effects)))%2)
        return tuple(result)

    def snapshot(self):
        if self._compiled is None:
            raise ValueError("uncompiled XOR program")
        payload=self._compiled
        checksum=sha256(canonical(payload).encode("ascii")).hexdigest()
        envelope=canonical({"payload":payload,"sha256":checksum})
        if len(envelope)>MAX_SNAPSHOT_BYTES:
            raise ValueError("oversize numerical program")
        return envelope

    @classmethod
    def restore(cls,envelope):
        if type(envelope) is not str or len(envelope)>MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid snapshot type/size")
        try:
            data=json.loads(envelope)
            if type(data) is not dict or set(data)!={"payload","sha256"}:
                raise ValueError("invalid payload envelope")
            v=data["payload"]
            if (type(v) is not dict or
                    set(v)!={"schema","charges","basis_count",
                             "numeric_output_weights"} or
                    v["schema"]!=SCHEMA or type(v["charges"]) is not int or
                    v["charges"]!=384 or
                    type(v["basis_count"]) is not int or
                    v["basis_count"]!=len(FEATURES)):
                raise ValueError("schema/charge mismatch")
            weights=v["numeric_output_weights"]
            if type(weights) is not list or len(weights)!=6:
                raise ValueError("missing output weight blocks")
            for possibilities in weights:
                if (type(possibilities) is not list or
                        not 1<=len(possibilities)<=MAX_MODELS_PER_OUTPUT):
                    raise ValueError("bad candidate set")
                for row in possibilities:
                    if (type(row) is not list or len(row)!=len(FEATURES) or
                            any(type(w) not in (int,float) or w not in (0,1)
                                for w in row) or sum(row) not in (1,2)):
                        raise ValueError("bad numeric XOR weights")
            if sha256(canonical(v).encode("ascii")).hexdigest()!=data["sha256"]:
                raise ValueError("checksum mismatch")
            model=cls()
            model._rows=None
            model._history=None
            model.current=None
            model.charges=384
            model._compiled=v
            if model.snapshot()!=envelope:
                raise ValueError("noncanonical snapshot")
            return model
        except (TypeError,ValueError,OverflowError,KeyError) as exc:
            raise ValueError("corrupted WSP83 numeric weights") from exc
