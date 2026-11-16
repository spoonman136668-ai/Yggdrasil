"""FKP-23 source-independent tokenless prior correction & retention.

Receives only compact residual signatures derived from physically witnessed
public intervention transcripts (and SHA receipts), not private law IDs,
world seeds, source helpers, counterfactuals or future outcomes.

The candidate retains all prior signatures; newly *observed* incompatible
signatures allocate a separate sparse contradiction record. It then uses
physical action-consequence partitioning to pick three informative probes.
An independent exact Bayesian entropy arm uses the same entire public
history. Any tie is evidence AGAINST unique architecture superiority.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math

SUPPORT_COUNT=16
UPDATE_COUNT=8
MAX_BYTES=65536
MODES=("SPARSE_CONTRADICTION_REPAIR","EXACT_BAYES_ALL_HISTORY",
       "FROZEN_OLD_PRIOR","RECENT_ONLY_PRIOR","NO_MEMORY")


def _json(x):
    return json.dumps(x,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _fail_constant(_):
    raise ValueError("FKP23_COLD_NONFINITE")


def _unique(pairs):
    x={}
    for k,v in pairs:
        if k in x:
            raise ValueError("FKP23_COLD_DUPLICATE_JSON_KEY")
        x[k]=v
    return x


def _sha(s):
    if type(s) is not str or len(s)!=64 or any(
            c not in "0123456789abcdef" for c in s):
        raise ValueError("FKP23_SOURCE_PUBLIC_SHA_MISSING")
    return s


def _bit(b):
    if type(b) is not int or b not in (0,1):
        raise ValueError("FKP23_UNTRUSTED_PUBLIC_BIT")
    return b


def _position(i):
    if type(i) is not int or not 0<=i<4:
        raise ValueError("FKP23_INTERVENTION_NOT_PUBLIC")
    return i


def _signature(s):
    if type(s) is not int or not 0<=s<16:
        raise ValueError("FKP23_WITNESSED_RESIDUAL_SIGNATURE")
    return s


def _entropy(counts):
    total=sum(counts)
    return -sum((n/total)*math.log2(n/total)
                for n in counts if n>0) if total else 0.0


class PhysicalPriorRepair:
    def __init__(self,mode):
        if type(mode) is not str or mode not in MODES:
            raise ValueError("FKP23_UNKNOWN_POLICY_ARM")
        self.mode=mode
        self._support=[]
        self._update=[]
        self._novel=[]
        self._ready=False
        self._selected=[]
        self._feedback={}
        self._pending=None

    @property
    def support_count(self):
        return len(self._support)

    @property
    def update_count(self):
        return len(self._update)

    @property
    def novel_signatures(self):
        return tuple(self._novel)

    @property
    def learned_logical_bytes(self):
        # Typed compact source-visible relation ledger. NOT Python RSS.
        return (len(self._support)+len(self._update))*34+(
            len(self._novel)*2)+len(self._selected)*34+24

    def observe_public_world(self,stage,signature,physical_receipt):
        signature=_signature(signature)
        _sha(physical_receipt)
        if self._ready or self._pending is not None:
            raise ValueError("FKP23_TRAIN_LOCKED_OR_ACTION_PENDING")
        if stage=="support":
            if self._update or len(self._support)>=SUPPORT_COUNT:
                raise ValueError("FKP23_SUPPORT_ORDER_OR_BUDGET")
            self._support.append([signature,physical_receipt])
        elif stage=="update":
            if len(self._support)!=SUPPORT_COUNT or len(self._update)>=UPDATE_COUNT:
                raise ValueError("FKP23_UPDATE_BEFORE_FULL_SUPPORT")
            if signature not in {e[0] for e in self._support} and (
                    signature not in self._novel):
                self._novel.append(signature)
            self._update.append([signature,physical_receipt])
        else:
            raise ValueError("FKP23_UNKNOWN_SOURCE_STAGE")
        if self.learned_logical_bytes>MAX_BYTES:
            # The frozen caps are far from close, but changes commit atomically.
            if stage=="support":
                self._support.pop()
            else:
                self._update.pop()
                self._novel=[s for s in self._novel if
                    any(u[0]==s for u in self._update)]
            raise ValueError("FKP23_LOGICAL_CAPACITY_EXCEEDED")

    def freeze(self):
        if self._ready or len(self._support)!=SUPPORT_COUNT or (
            len(self._update)!=UPDATE_COUNT):
            raise ValueError("FKP23_SUPPORT_AND_UPDATE_NOT_COMPLETE")
        self._ready=True
        return self

    def _hypotheses(self):
        if self.mode=="NO_MEMORY":
            return ()
        if self.mode=="FROZEN_OLD_PRIOR":
            return tuple(s for s,r in self._support)
        if self.mode=="RECENT_ONLY_PRIOR":
            return tuple(s for s,r in self._update)
        return tuple(s for s,r in self._support+self._update)

    def _posterior(self):
        if self.mode=="NO_MEMORY":
            return Counter()
        return Counter(s for s in self._hypotheses() if all(
            ((s>>i)&1)==b for i,b in self._feedback.items()))

    def _sparse_selection(self,available):
        counts=self._posterior()
        if not counts:
            return min(available)
        def balance(i):
            one=sum(n for s,n in counts.items() if (s>>i)&1)
            return min(one,sum(counts.values())-one)
        return max(available,key=balance)

    def _exact_bayes(self,available):
        # Separate, independently implemented exact entropy of a hypothesis
        # multiset. No reuse of candidate's sparse balance score.
        samples=[s for s in self._support+self._update if all(
            ((s[0]>>i)&1)==b for i,b in self._feedback.items())]
        samples=[x[0] for x in samples]
        if not samples:
            return min(available)
        base=_entropy(Counter(samples).values())
        def gain(i):
            expected=0.0
            for b in (0,1):
                group=[s for s in samples if ((s>>i)&1)==b]
                if group:
                    expected+=(len(group)/len(samples))*_entropy(
                        Counter(group).values())
            return round(base-expected,12)
        return max(available,key=gain)

    def choose_physical_query(self):
        if not self._ready or self._pending is not None or (
                len(self._selected)>=3):
            raise ValueError("FKP23_PREVIOUS_ACTION_NOT_OBSERVED_OR_FROZEN")
        remaining=[i for i in range(4) if i not in self._feedback]
        if self.mode=="EXACT_BAYES_ALL_HISTORY":
            q=self._exact_bayes(remaining)
        elif self.mode=="NO_MEMORY":
            q=min(remaining)
        else:
            q=self._sparse_selection(remaining)
        if q not in remaining:
            raise AssertionError("FKP23_SELECTED_REPEATED_QUERY")
        self._pending=q
        return q

    def observe_selected_consequence(self,index,actual_residual_bit,physical_sha):
        _position(index)
        _bit(actual_residual_bit)
        _sha(physical_sha)
        if self._pending!=index or index in self._feedback:
            raise ValueError("FKP23_UNEARNED_FUTURE_OUTCOME")
        self._selected.append([index,actual_residual_bit,physical_sha])
        self._feedback[index]=actual_residual_bit
        self._pending=None
        if self.learned_logical_bytes>MAX_BYTES:
            self._selected.pop()
            del self._feedback[index]
            self._pending=index
            raise ValueError("FKP23_LEARNED_CAPACITY")

    @property
    def queried(self):
        return tuple(row[0] for row in self._selected)

    @property
    def distinct_posterior_relations(self):
        if len(self._selected)!=3 or self._pending is not None:
            raise ValueError("FKP23_INSUFFICIENT_TRUE_ACTIONS")
        return len(self._posterior())

    @property
    def supporting_example_count(self):
        if len(self._selected)!=3 or self._pending is not None:
            raise ValueError("FKP23_INSUFFICIENT_TRUE_ACTIONS")
        return sum(self._posterior().values())

    def predict_last_unqueried(self,index):
        _position(index)
        if len(self._selected)!=3 or self._pending is not None or (
                index in self._feedback):
            raise ValueError("FKP23_UNQUERIED_PREACTION_ONLY")
        possible=self._posterior()
        total=sum(possible.values())
        if not total:
            return 0
        one=sum(n for s,n in possible.items() if (s>>index)&1)
        return int(2*one>total)  # ties fixed 0, prospectively

    def _state(self):
        return {"schema":"fkp23.physical-prior.v1","mode":self.mode,
                "support":self._support,"update":self._update,
                "novel":self._novel,"ready":self._ready,
                "selected":self._selected,"pending":self._pending}

    def state_sha(self):
        return sha256(_json(self._state())).hexdigest()

    def checkpoint(self):
        s=self._state()
        packed=_json(s)
        if len(packed)>MAX_BYTES:
            raise ValueError("FKP23_COLD_SNAPSHOT_SIZE")
        return _json({"body":s,"sha256":sha256(packed).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)>MAX_BYTES:
            raise ValueError("FKP23_COLD_INVALID_BYTES")
        try:
            e=json.loads(raw,object_pairs_hook=_unique,
                         parse_constant=_fail_constant)
        except (TypeError,ValueError,UnicodeError) as exc:
            raise ValueError("FKP23_COLD_INVALID_JSON") from exc
        if type(e) is not dict or set(e)!={"body","sha256"}:
            raise ValueError("FKP23_BAD_COLD_ENVELOPE")
        b=e["body"]
        if type(b) is not dict or set(b)!={
            "schema","mode","support","update","novel",
            "ready","selected","pending"} or (
                b["schema"]!="fkp23.physical-prior.v1"):
            raise ValueError("FKP23_BAD_COLD_SCHEMA")
        if sha256(_json(b)).hexdigest()!=e["sha256"]:
            raise ValueError("FKP23_COLD_SHA_MISMATCH")
        if type(b["support"]) is not list or type(b["update"]) is not list or (
                type(b["novel"]) is not list or type(b["selected"]) is not list or
                type(b["ready"]) is not bool):
            raise ValueError("FKP23_COLD_TYPES")
        obj=cls(b["mode"])
        for stage,rows in (("support",b["support"]),("update",b["update"])):
            for row in rows:
                if type(row) is not list or len(row)!=2:
                    raise ValueError("FKP23_COLD_WORLD_RECEIPT")
                obj.observe_public_world(stage,row[0],row[1])
        if obj._novel!=b["novel"]:
            raise ValueError("FKP23_COLD_CONTRADICTION_MISMATCH")
        if b["ready"]:
            obj.freeze()
        if type(b["selected"]) is not list or len(b["selected"])>3:
            raise ValueError("FKP23_COLD_ACTION_EVIDENCE")
        for row in b["selected"]:
            if type(row) is not list or len(row)!=3:
                raise ValueError("FKP23_COLD_ACTION_ENTRY")
            choice=obj.choose_physical_query()
            if choice!=row[0]:
                raise ValueError("FKP23_COLD_ACTION_CHOICE_NOT_CONSEQUENTIAL")
            obj.observe_selected_consequence(row[0],row[1],row[2])
        if b["pending"] is not None:
            if obj.choose_physical_query()!=b["pending"]:
                raise ValueError("FKP23_COLD_PENDING_NOT_MATCHED")
        if obj.checkpoint()!=raw:
            raise ValueError("FKP23_COLD_NONCANONICAL")
        return obj
