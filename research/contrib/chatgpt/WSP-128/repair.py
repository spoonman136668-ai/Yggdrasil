"""WSP128 numerical, contradiction-gated *residual* weight programming.

Supplied rank-one residual grammar is an inductive bias, not invented physics.
No source imports. Original rank8 weights stay immutable; evidence and repair
weights are cold-replay verified separately. Unsupported rows abstain.
"""
from __future__ import annotations
from hashlib import sha256
from types import SimpleNamespace
import json

SCHEMA="wsp128.direct-residual-repair.v1"

def _canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))

def _hash(value):
    return sha256(_canon(value).encode("utf8")).hexdigest()

class _ResidualLaw:
    def __init__(self, prior, view):
        self.prior=prior
        self.view=view
        self.events=[]
        self.observed=[{} for _ in range(64)]
        self.residual=[{} for _ in range(64)]
        self.anchor=None
        self._cached=None

    def choose_pair(self):
        if len(self.events)>=512:
            return None
        if self.anchor is None:
            for row in range(6):
                if len(self.observed[row])<64:
                    for col in range(64):
                        if col not in self.observed[row]:
                            return row,col
        else:
            col=self.pivot()
            for row in range(64):
                if col not in self.observed[row]:
                    return row,col
        # Every remaining source action is explicit and charged.
        for row in range(64):
            for col in range(64):
                if col not in self.observed[row]:
                    return row,col
        raise AssertionError("WSP128_UNEXPECTED_COMPLETE_WORLD")

    def pivot(self):
        if self.anchor is None:
            raise ValueError("WSP128_NO_ANCHOR")
        positives=[b for b,v in self.residual[self.anchor].items() if v==1]
        if not positives or len(self.observed[self.anchor])!=64:
            raise ValueError("WSP128_NO_COMPLETE_DIAGNOSTIC_ANCHOR")
        return min(positives)

    def ingest(self, event):
        if (type(event) is not list or len(event)!=7 or
                any(type(v) is not int for v in event[:6]) or
                type(event[6]) is not str or len(event[6])!=64 or
                not all(c in "0123456789abcdef" for c in event[6]) or
                event[0]!=self.view.seed or event[1]!=self.view.law_id or
                event[5] not in (0,1)):
            raise ValueError("WSP128_BAD_EVIDENCE")
        seed,law,subject,a,b,effect,receipt=event
        if self.view.subject(a,b)!=subject or (a,b)!=self.choose_pair():
            raise ValueError("WSP128_INVALID_OR_REPLAYED_ACTION")
        self.events.append(event[:])
        self.observed[a][b]=effect
        old=self.prior.infer(self.view,subject)
        if old is not None:
            self.residual[a][b]=effect^old
        if (self.anchor is None and a<6 and len(self.observed[a])==64 and
                any(v==1 for v in self.residual[a].values()) and
                len(self.residual[a])==64):
            self.anchor=a
        self._cached=None

    def _compiled(self):
        if self._cached is not None:
            return self._cached
        contradictions=sum(value==1 for row in self.residual for value in row.values())
        if self.anchor is None:
            state={"status":"SUSPECT_UNRESOLVED" if contradictions else "NO_CONTRADICTION",
                   "factor":None,"support":{},"contradictions":contradictions,
                   "inconsistent":False}
            self._cached=state
            return state
        v=sum(bit<<b for b,bit in self.residual[self.anchor].items())
        support={}
        inconsistent=False
        for row in range(64):
            votes=set()
            for b,bit in self.residual[row].items():
                if (v>>b)&1:
                    votes.add(bit)
            if len(votes)>1:
                inconsistent=True
            elif len(votes)==1:
                support[row]=next(iter(votes))
        if support.get(self.anchor)!=1:
            raise ValueError("WSP128_ANCHOR_NOT_A_CHANGED_ROW")
        for row in range(64):
            if row not in support:
                continue
            bit=support[row]
            for b,observed_delta in self.residual[row].items():
                if observed_delta!=(bit & ((v>>b)&1)):
                    inconsistent=True
        state={"status":"INCOMPATIBLE_RESIDUALS" if inconsistent else "REPAIRED",
               "factor":v,"support":support,
               "contradictions":contradictions,"inconsistent":inconsistent}
        self._cached=state
        return state

    def infer(self,subject):
        a,b=self.view.pair(subject)
        if b in self.observed[a]:
            return self.observed[a][b]
        old=self.prior.infer(self.view,subject)
        state=self._compiled()
        if state["status"]=="NO_CONTRADICTION":
            return old
        if (state["status"]!="REPAIRED" or old is None or
                a not in state["support"]):
            return None
        residual=(state["support"][a]&((state["factor"]>>b)&1))
        return old^residual

    def payload(self):
        state=self._compiled()
        return {"seed":self.view.seed,"law_id":self.view.law_id,
                "events":self.events,"status":state["status"],
                "anchor":self.anchor,"factor":state["factor"],
                "support":{str(k):v for k,v in sorted(state["support"].items())},
                "contradictions":state["contradictions"],
                "inconsistent":state["inconsistent"]}

class DirectResidualRepair:
    def __init__(self,prior):
        self.prior=prior
        self.states={}

    def _state(self,view):
        if (getattr(view,"cohort",None)!="probe" or
                type(getattr(view,"seed",None)) is not int or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<64):
            raise PermissionError("WSP128_INVALID_REPAIR_VIEW")
        if view.seed not in self.states:
            self.states[view.seed]=_ResidualLaw(self.prior,view)
        st=self.states[view.seed]
        if st.view is not view:
            raise ValueError("WSP128_PUBLIC_VIEW_CHANGED")
        return st

    def choose(self,view,available):
        st=self._state(view)
        pair=st.choose_pair()
        if pair is None:
            return None
        action=view.subject(*pair)
        if action not in available:
            raise ValueError("WSP128_QUERY_UNAVAILABLE")
        return action

    def observe(self,view,evidence):
        if (getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                type(getattr(evidence,"subject",None)) is not int or
                evidence.subject not in view.legal or
                view.pair(evidence.subject)!=
                    (getattr(evidence,"left",None),getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP128_UNVERIFIED_TYPED_FEEDBACK")
        self._state(view).ingest([evidence.seed,evidence.law_id,
            evidence.subject,evidence.left,evidence.right,
            evidence.effect,evidence.receipt])

    def infer(self,view,subject):
        return self._state(view).infer(subject)

    def snapshot(self):
        body={"schema":SCHEMA,
              "states":{str(k):self.states[k].payload()
                        for k in sorted(self.states)}}
        return _canon({"payload":body,"sha256":_hash(body)})

    @classmethod
    def restore(cls,prior,snapshot,view_resolver):
        try:
            outer=json.loads(snapshot)
            body=outer["payload"]
            if body["schema"]!=SCHEMA or _hash(body)!=outer["sha256"]:
                raise ValueError("WSP128_SNAPSHOT_DIGEST_INVALID")
            model=cls(prior)
            for key in sorted(body["states"],key=int):
                if str(int(key))!=key:
                    raise ValueError("WSP128_SNAPSHOT_SEED_FORMAT")
                original=body["states"][key]
                view=view_resolver(int(key))
                state=model._state(view)
                for raw in original["events"]:
                    e=SimpleNamespace(seed=raw[0],law_id=raw[1],subject=raw[2],
                                      left=raw[3],right=raw[4],effect=raw[5],
                                      receipt=raw[6])
                    model.observe(view,e)
                if state.payload()!=original:
                    raise ValueError("WSP128_SNAPSHOT_FORGED_REPAIR_COEFFICIENT")
            return model
        except (KeyError,TypeError,AttributeError,IndexError) as exc:
            raise ValueError("WSP128_INVALID_SNAPSHOT") from exc
