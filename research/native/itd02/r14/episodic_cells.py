"""R14 opt-in bounded episodic transition memory over unchanged R10/R11/R12/R13.

Only the authenticated, selected R10 event is learned; each before/after state
is an original source-public image/direction/mission digest. No hidden pose,
scripted DoorKey goal, external action selector or unselected reward.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, public_cues, canonical, digest
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r13.explore_choice import propose_native_action

SCHEMA="yggdrasil.itd02.r14.episodic-selected-public-transitions.v1"
MAX_STATES=512
MAX_SAMPLES=4096
MAX_BLOB=400000


class EpisodicCells:
    def __init__(self, native=None):
        self.native=PublicAffordanceCells() if native is None else native
        if type(self.native) is not PublicAffordanceCells:
            raise ValueError("R14_NATIVE_TYPE")
        self.transitions={}
        self.samples=0
        self.visits={}
        self.session=None

    def start_session(self, adapter, name):
        if type(adapter) is not DoorKeyPublicAdapter or adapter.pending is not None or adapter.current is None:
            raise ValueError("R14_SOURCE_SESSION_INVALID")
        if self.session is not None and adapter.events!=0:
            raise ValueError("R14_REUSED_SOURCE_SESSION")
        self.native.start_session(adapter,name)
        self.session=name
        self.visits={digest(adapter.current):1}

    def propose(self, before):
        cues=public_cues(before)
        if self.native.session is None:
            raise ValueError("R14_MISSING_SOURCE_SESSION")
        current=cues["observation_sha256"]
        baseline=propose_native_action(self.native,before)
        if baseline["status"]=="SELECT_NATIVE_OBSERVED_POSITIVE_REWARD":
            return {"schema":SCHEMA,"action":baseline["action"],
                    "status":"SELECT_NATIVE_OBSERVED_POSITIVE_REWARD",
                    "learned_selected_transitions":baseline.get("learned_context_samples",0),
                    "external_fallback":False}
        candidates=[]
        for action in range(7):
            outcomes=self.transitions.get(current,{}).get(str(action),{})
            total=sum(outcomes.values())
            if not total: continue
            novelty=sum(count for dest,count in outcomes.items() if dest!=current)/total
            future_visits=sum(count*self.visits.get(dest,0) for dest,count in outcomes.items())/total
            score=novelty-future_visits/(1+sum(self.visits.values()))
            if novelty>0:
                candidates.append((score,action,total))
        if candidates:
            score,action,total=sorted(candidates,key=lambda r:(-r[0],r[1]))[0]
            return {"schema":SCHEMA,"action":action,
                    "status":"SELECT_NATIVE_LEARNED_PUBLIC_TRANSITION_NOVELTY",
                    "learned_selected_transitions":total,"external_fallback":False}
        return {"schema":SCHEMA,"action":baseline["action"],
                "status":"SELECT_NATIVE_BASE_EXPLORATION",
                "learned_selected_transitions":baseline.get("learned_context_samples",0),
                "external_fallback":False}

    def learn_selected(self, adapter):
        if type(adapter) is not DoorKeyPublicAdapter or adapter.pending is not None or not adapter.ledger:
            raise ValueError("R14_MISSING_SELECTED_SOURCE_EVENT")
        if self.samples>=MAX_SAMPLES:
            raise ValueError("R14_SAMPLE_BOUND")
        event=adapter.ledger[-1]
        if (self.native.session is None or adapter.events!=self.native.cursor+1
            or event["ordinal"]!=adapter.events
            or event["after_public_sha256"]!=digest(adapter.current)):
            raise ValueError("R14_UNAUTHENTICATED_SELECTED_SOURCE")
        before=event["before_public_sha256"];after=event["after_public_sha256"]
        if type(before)is not str or len(before)!=64 or type(after)is not str or len(after)!=64:
            raise ValueError("R14_BAD_ORIGINAL_SOURCE_HASH")
        action=event["action"]
        if type(action)is not int or action not in range(7):
            raise ValueError("R14_INVALID_SOURCE_ACTION")
        if before not in self.transitions and len(self.transitions)>=MAX_STATES:
            raise ValueError("R14_CONTEXT_BOUND")
        # R11 must pass original selected-action authentication before R14 mutates.
        receipt=self.native.learn_selected(adapter)
        entry=self.transitions.setdefault(before,{})
        outcomes=entry.setdefault(str(action),{})
        outcomes[after]=outcomes.get(after,0)+1
        self.samples+=1
        if self.session is not None:
            self.visits[after]=self.visits.get(after,0)+1
        return receipt

    def checkpoint(self):
        state={"schema":SCHEMA,"native":self.native.checkpoint().decode("utf-8"),
               "transitions":self.transitions,"samples":self.samples,
               "session":self.session,"visits":self.visits}
        raw=canonical(state)
        outer=canonical({"state":state,"sha256":hashlib.sha256(raw).hexdigest()})
        if len(outer)>MAX_BLOB: raise ValueError("R14_CHECKPOINT_BOUND")
        return outer

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw)is not bytes or not 0<len(raw)<=MAX_BLOB:
                raise ValueError("R14_CHECKPOINT_BYTES")
            wire=json.loads(raw)
            if type(wire)is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("R14_CHECKPOINT_ENVELOPE")
            state=wire["state"]
            if (type(state)is not dict or set(state)!={"schema","native","transitions",
                "samples","session","visits"} or state["schema"]!=SCHEMA or
                hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
                raise ValueError("R14_CHECKPOINT_SHA")
            native=PublicAffordanceCells.restore(state["native"].encode("utf-8"))
            rows=state["transitions"]
            if (type(rows)is not dict or len(rows)>MAX_STATES
                or type(state["samples"])is not int or not 0<=state["samples"]<=MAX_SAMPLES
                or type(state["visits"])is not dict or len(state["visits"])>MAX_SAMPLES+1
                or state["session"] is not None and type(state["session"])is not str):
                raise ValueError("R14_CHECKPOINT_LIMITS")
            total=0
            for before,arms in rows.items():
                if type(before)is not str or len(before)!=64 or type(arms)is not dict:
                    raise ValueError("R14_BAD_CONTEXT")
                if any(c not in "0123456789abcdef" for c in before):
                    raise ValueError("R14_BAD_CONTEXT_HASH")
                for arm,counts in arms.items():
                    if arm not in [str(n) for n in range(7)] or type(counts)is not dict:
                        raise ValueError("R14_BAD_ARM")
                    for after,count in counts.items():
                        if (type(after)is not str or len(after)!=64 or
                            any(c not in "0123456789abcdef" for c in after) or
                            type(count)is not int or count<1 or count>MAX_SAMPLES):
                            raise ValueError("R14_BAD_NEXT_STATE")
                        total+=count
            if total!=state["samples"] or native.samples!=state["samples"]:
                raise ValueError("R14_UNEQUAL_SELECTED_TOTAL")
            for key,val in state["visits"].items():
                if (type(key)is not str or len(key)!=64 or
                    any(c not in "0123456789abcdef" for c in key) or
                    type(val)is not int or not 1<=val<=MAX_SAMPLES+1):
                    raise ValueError("R14_BAD_VISIT")
            out=cls(native)
            out.transitions=rows;out.samples=state["samples"]
            out.visits=state["visits"];out.session=state["session"]
            if out.checkpoint()!=raw:raise ValueError("R14_NONCANONICAL_SNAPSHOT")
            return out
        except (TypeError,KeyError,UnicodeDecodeError,ValueError) as exc:
            raise ValueError("R14_UNTRUSTED_EPISODIC_CHECKPOINT") from exc
