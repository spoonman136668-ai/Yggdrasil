"""WSP84 data-learned 3-input Boolean operator compiled into numeric weights.

No source/evaluator import. Learner is given only a GENERIC finite grammar:
60 balanced action-membership atoms across current/last/second-last slots,
and a three-variable numeric ReLU truth-table representation. Which
features and which 8-bit Boolean function govern an output are inferred
from 384 continuously charged public action consequences. No name like
'majority' or source secret appears in training/inference code.

NOT open-ended discovery: partitions, k<=3, table compiler were authored
by researchers and finite exhaustive inference ties symbolic control.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations,product
from math import isfinite
import json

ACTIONS=tuple(range(6))
STATES=frozenset(product((0,1),repeat=6))
BALANCED=tuple(combinations(ACTIONS,3))
FEATURES=tuple((slot,mask) for slot in range(3) for mask in BALANCED)
assert len(BALANCED)==20 and len(FEATURES)==60
SCHEMA="wsp84.numeric-learned-3input-operator.v1"
MAX_POSSIBILITIES=64
MAX_PAYLOAD_CHARS=250000


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def _valid(state,action,history):
    return (type(state) is tuple and state in STATES
            and type(action) is int and action in ACTIONS
            and type(history) in (tuple,list)
            and all(type(x) is int and x in ACTIONS for x in history))


def _relu(x):
    return max(0.0,x)


def _signals(action,history):
    slots=(action,history[-1] if history else None,
           history[-2] if len(history)>=2 else None)
    return [float(slots[slot] is not None and slots[slot] in mask)
            for slot,mask in FEATURES]


def _read(program,state_bit,action_bit,action,history):
    support=program["support"]
    table=program["table"]
    slots=(action,history[-1] if history else None,
           history[-2] if len(history)>=2 else None)
    indicators=[]
    for atom in support:
        observed=slots[atom["slot"]]
        x=([float(observed==i) for i in ACTIONS]
           if observed is not None else [0.0]*6)
        val=sum(w*v for w,v in zip(atom["mask_weights"],x))
        if val not in (0.0,1.0):
            raise ArithmeticError("non-Boolean learned partition")
        indicators.append(val)
    n=len(indicators)
    if n==0:
        effect=float(table[0])
    else:
        effect=0.0
        for pattern,enabled in enumerate(table):
            if enabled:
                literals=[indicators[k] if pattern&(1<<k)
                          else 1.0-indicators[k] for k in range(n)]
                effect+=_relu(sum(literals)-(n-1))
    if effect not in (0.0,1.0) or not isfinite(effect):
        raise ArithmeticError("non-Boolean learned minterm program")
    toggled=float(state_bit)+float(action_bit)
    toggled-=2.0*_relu(toggled-1.0)
    flipped=toggled+effect
    out=flipped-2.0*_relu(flipped-1.0)
    if not isfinite(out) or out not in (0.0,1.0):
        raise ArithmeticError("bad cold numeric parity readout")
    return int(out)


def _pack(selection,table):
    return {"support":[
        {"slot":FEATURES[j][0],
         "mask_weights":[float(i in FEATURES[j][1]) for i in ACTIONS]}
        for j in selection],
        "table":list(table)}


class PaidOperatorInducer:
    def __init__(self):
        self.current=(0,)*6
        self.charges=0
        self._rows=[]
        self._history=[]
        self._compiled=None

    def charge(self,before,action,after,cost=1):
        if (self._rows is None or self._history is None
                or not _valid(before,action,self._history)
                or type(after) is not tuple or after not in STATES
                or type(cost) is not int or cost!=1
                or before!=self.current or self.charges>=384):
            raise ValueError("unpaid, discontinuous, or overbudget public trajectory")
        self._rows.append((before,action,after,tuple(self._history)))
        self._history.append(action)
        self.current=after
        self.charges+=1
        self._compiled=None

    def compile(self):
        if self._rows is None or self.charges!=384:
            raise ValueError("exactly 384 physically charged rows required")
        allbits=(1<<384)-1
        signatures=[0]*len(FEATURES)
        targets=[0]*6
        for position,(before,action,after,history) in enumerate(self._rows):
            gates=_signals(action,history)
            for j,gate in enumerate(gates):
                if gate==1.0:
                    signatures[j]|=1<<position
            for bit in ACTIONS:
                if before[bit]^after[bit]^int(action==bit):
                    targets[bit]|=1<<position
        out=[]
        diag=[]
        for target in targets:
            # Learn exact Boolean function of <=3 predeclared *generic*
            # partition atoms; require all table cells witnessed, never
            # invent output values for unobserved truth combinations.
            if target in (0,allbits):
                chosen=[_pack((),(int(target==allbits),))]
                k=0
            else:
                chosen=[]
                k=None
                for dimension in (1,2,3):
                    for support in combinations(range(len(FEATURES)),dimension):
                        buckets=[allbits]
                        for index in support:
                            positive=signatures[index]
                            negative=allbits^positive
                            buckets=([bucket&negative for bucket in buckets]
                                     +[bucket&positive for bucket in buckets])
                        if 0 in buckets:
                            continue  # Not every operator table entry observed.
                        table=[]
                        for bucket in buckets:
                            overlap=bucket&target
                            if overlap!=0 and overlap!=bucket:
                                break  # This support cannot explain public data.
                            table.append(int(overlap==bucket))
                        else:
                            chosen.append(_pack(support,table))
                            if len(chosen)>MAX_POSSIBILITIES:
                                raise ValueError("operator identification ambiguous beyond frozen bound")
                    if chosen:
                        k=dimension
                        break
                if not chosen:
                    raise ValueError("missing learned operator is outside k<=3 grammar")
            out.append(chosen)
            diag.append({
                "minimal_input_support":k,
                "operator_candidates":len(chosen),
                "all_truth_table_cells_paid":True,
                "frozen_boolean_tables_sha256":sha256(_canonical([
                    p["table"] for p in chosen]).encode("ascii")).hexdigest(),
            })
        self._compiled={"schema":SCHEMA,"charges":384,
                        "outputs":out}
        return {
            "charged_public_actions":384,
            "candidate_public_partition_atoms":60,
            "selected_support_cardinalities":[x["minimal_input_support"] for x in diag],
            "three_input_operator_output_count":sum(
                x["minimal_input_support"]==3 for x in diag),
            "all_selected_table_cells_physically_observed":True,
            "learned_operator_receipts":diag,
            "numerical_programs":sum(len(x) for x in out),
        }

    def predict(self,state,action,history=()):
        if not _valid(state,action,history) or self._compiled is None:
            raise ValueError("invalid or uncompiled numeric operator query")
        bits=[]
        for bit,programs in enumerate(self._compiled["outputs"]):
            candidates={_read(program,state[bit],action==bit,action,history)
                        for program in programs}
            if len(candidates)!=1:
                return None
            bits.append(next(iter(candidates)))
        return tuple(bits)

    def snapshot(self):
        if self._compiled is None:
            raise ValueError("uncompiled operator")
        payload=self._compiled
        sealed=_canonical({"payload":payload,"sha256":sha256(
            _canonical(payload).encode("ascii")).hexdigest()})
        if len(sealed)>MAX_PAYLOAD_CHARS:
            raise ValueError("operator program exceeds bounded memory")
        return sealed

    @classmethod
    def restore(cls,sealed):
        if type(sealed) is not str or len(sealed)>MAX_PAYLOAD_CHARS:
            raise ValueError("invalid cold operator snapshot size/type")
        try:
            box=json.loads(sealed)
            if type(box) is not dict or set(box)!={"payload","sha256"}:
                raise ValueError("bad envelope")
            payload=box["payload"]
            if (type(payload) is not dict or
                    set(payload)!={"schema","charges","outputs"} or
                    payload["schema"]!=SCHEMA or
                    type(payload["charges"]) is not int or
                    payload["charges"]!=384 or
                    type(payload["outputs"]) is not list or
                    len(payload["outputs"])!=6):
                raise ValueError("invalid snapshot schema")
            for programs in payload["outputs"]:
                if (type(programs) is not list or
                        not 1<=len(programs)<=MAX_POSSIBILITIES):
                    raise ValueError("invalid output candidate count")
                for program in programs:
                    if (type(program) is not dict or
                            set(program)!={"support","table"}):
                        raise ValueError("invalid numeric program keys")
                    support,table=program["support"],program["table"]
                    if (type(support) is not list or len(support)>3 or
                            type(table) is not list or
                            len(table)!=(1<<len(support)) or
                            any(type(v) is not int or v not in (0,1) for v in table)):
                        raise ValueError("incomplete truth table")
                    used=set()
                    for atom in support:
                        if (type(atom) is not dict or
                                set(atom)!={"slot","mask_weights"} or
                                type(atom["slot"]) is not int or
                                atom["slot"] not in (0,1,2)):
                            raise ValueError("invalid slot")
                        weights=atom["mask_weights"]
                        if (type(weights) is not list or len(weights)!=6 or
                                any(type(w) not in (int,float) or w not in (0,1)
                                    for w in weights) or sum(weights)!=3):
                            raise ValueError("invalid mask weights")
                        identity=(atom["slot"],tuple(weights))
                        if identity in used:
                            raise ValueError("duplicate input mask")
                        used.add(identity)
            expected=sha256(_canonical(payload).encode("ascii")).hexdigest()
            if box["sha256"]!=expected:
                raise ValueError("tampered numeric operator checksum")
            result=cls()
            result._rows=None
            result._history=None
            result.current=None
            result.charges=384
            result._compiled=payload
            if result.snapshot()!=sealed:
                raise ValueError("noncanonical weight program")
            return result
        except (TypeError,ValueError,OverflowError,KeyError) as exc:
            raise ValueError("invalid or tampered cold numerical operator") from exc
