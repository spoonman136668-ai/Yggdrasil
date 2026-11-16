"""CVH-01: source-independent, tokenless finite-horizon public consequence memory.

Consumes only six already witnessed FKP24-shaped public consequence fields.
Never imports/opens upstream CausalGym or generates hidden source outcomes.
"""
from __future__ import annotations
from hashlib import sha256
import json

FIELDS = ("before", "action", "reward", "after", "terminated", "truncated")
SCHEMA = "yggdrasil.cvh01.earned-return-memory.v1"
HORIZON = 4
SCALE = 1 << (HORIZON - 1)
CONTEXTS = 36
MAX_OBSERVATIONS = 1000000


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")


def _public(row,previous_after):
    if tuple(getattr(row, "_fields", ())) != FIELDS:
        raise ValueError("CVH01_PUBLIC_SCHEMA_ONLY")
    b,a,r,n,terminated,truncated = row
    if any(type(v) is not int or v not in (0,1) for v in (b,a,r,n)):
        raise ValueError("CVH01_PUBLIC_BINARY_ONLY")
    if type(terminated) is not bool or type(truncated) is not bool or (terminated and truncated):
        raise ValueError("CVH01_INVALID_TERMINAL")
    if previous_after is not None and b != previous_after:
        raise ValueError("CVH01_SOURCE_TRACE_CONTINUITY")
    return b,a,r,n,terminated,truncated


def _slot(prev_action,prev_reward,before,action):
    if any(type(v) is not int for v in (prev_action,prev_reward,before,action)):
        raise ValueError("CVH01_CONTEXT_TYPE")
    if prev_action not in (0,1,2) or prev_reward not in (0,1,2) or before not in (0,1) or action not in (0,1):
        raise ValueError("CVH01_CONTEXT_RANGE")
    if (prev_action == 2) != (prev_reward == 2):
        raise ValueError("CVH01_CONTEXT_SENTINEL_PAIR")
    return (((prev_action * 3 + prev_reward) * 2 + before) * 2 + action)


class EarnedReturnMemory:
    """Online exact binary fixed-point eligibility accumulation.

    Completed samples contribute their observed (not predicted) discounted
    next four rewards to one of 36 public action-context slots.
    """

    def __init__(self):
        self.count = [0] * CONTEXTS
        self.total = [0] * CONTEXTS
        self.pending = [] # [slot, accumulated_units, observed_steps], max3 after observe()
        self.prev_action = 2
        self.prev_reward = 2
        self.previous_after = None
        self.seen = 0
        self.event_digest = sha256(b"CVH01-PUBLIC-INIT").hexdigest()

    def observe(self,row):
        b,a,r,n,ended,truncated = _public(row,self.previous_after)
        if self.seen >= MAX_OBSERVATIONS:
            raise ValueError("CVH01_OBSERVATION_LIMIT")
        key = _slot(self.prev_action,self.prev_reward,b,a)
        # Validate entire current update before any existing state is changed.
        todo = [entry[:] for entry in self.pending] + [[key,0,0]]
        finalized = []
        for item in todo:
            age = item[2]
            if not 0 <= age < HORIZON:
                raise ValueError("CVH01_PENDING_INTERNAL_INVALID")
            item[1] += r * (1 << (HORIZON - 1 - age))
            item[2] += 1
            if item[2] == HORIZON or ended or truncated:
                finalized.append(item)
        stay = [] if ended or truncated else [item for item in todo if item[2] < HORIZON]
        if len(stay) > HORIZON-1:
            raise ValueError("CVH01_PENDING_OVERFLOW")
        newcount=self.count[:]
        newtotal=self.total[:]
        for k,score,_ in finalized:
            if newcount[k] >= MAX_OBSERVATIONS or newtotal[k]+score > MAX_OBSERVATIONS * 15:
                raise ValueError("CVH01_COUNTER_OVERFLOW")
            newcount[k] += 1
            newtotal[k] += score
        newdigest = sha256(bytes.fromhex(self.event_digest) + _canonical(
            [b,a,r,n,ended,truncated])).hexdigest()
        # Commit only after all validation; no uncertain-effect replay.
        self.count,self.total = newcount,newtotal
        self.pending = stay
        self.prev_action = 2 if ended or truncated else a
        self.prev_reward = 2 if ended or truncated else r
        self.previous_after = None if ended or truncated else n
        self.event_digest = newdigest
        self.seen += 1

    def estimate(self,before,prev_action,prev_reward,action):
        key=_slot(prev_action,prev_reward,before,action)
        n=self.count[key]
        return None if n==0 else self.total[key]/(SCALE*n)

    def choose_supported(self,before,prev_action,prev_reward,min_support=2):
        """Read-only suggestion; abstain until *both* public actions supported."""
        if type(min_support) is not int or min_support < 1:
            raise ValueError("CVH01_BAD_MIN_SUPPORT")
        x=_slot(prev_action,prev_reward,before,0)
        y=_slot(prev_action,prev_reward,before,1)
        if min(self.count[x],self.count[y]) < min_support:
            return None
        lhs=self.total[x]*self.count[y]
        rhs=self.total[y]*self.count[x]
        return 1 if rhs>lhs else 0

    def _state(self):
        return dict(schema=SCHEMA,count=self.count,total=self.total,
                    pending=self.pending,prev_action=self.prev_action,
                    prev_reward=self.prev_reward,previous_after=self.previous_after,
                    seen=self.seen,event_digest=self.event_digest)

    def snapshot(self):
        state=self._state()
        raw=_canonical(state)
        return _canonical({"payload":state,"sha256":sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or len(blob)>12000:
            raise ValueError("CVH01_INVALID_SNAPSHOT_BYTES")
        try:
            doc=json.loads(blob)
            if type(doc) is not dict or set(doc)!={"payload","sha256"}:
                raise ValueError("CVH01_BAD_ENVELOPE")
            p=doc["payload"]
            if type(p) is not dict or set(p)!={"schema","count","total","pending",
              "prev_action","prev_reward","previous_after","seen","event_digest"}:
                raise ValueError("CVH01_BAD_PAYLOAD")
            if _canonical(doc)!=blob or sha256(_canonical(p)).hexdigest()!=doc["sha256"]:
                raise ValueError("CVH01_COLD_HASH_INVALID")
            if p["schema"]!=SCHEMA:
                raise ValueError("CVH01_BAD_VERSION")
            cs,ts=p["count"],p["total"]
            if (type(cs) is not list or type(ts) is not list or
                len(cs)!=CONTEXTS or len(ts)!=CONTEXTS or
                any(type(c) is not int or not 0<=c<=MAX_OBSERVATIONS for c in cs) or
                any(type(t) is not int or t<0 or t>15*c for t,c in zip(ts,cs))):
                raise ValueError("CVH01_COLD_COUNTERS_INVALID")
            seen=p["seen"]
            if type(seen) is not int or not 0<=seen<=MAX_OBSERVATIONS:
                raise ValueError("CVH01_COLD_SEEN")
            if type(p["event_digest"]) is not str or len(p["event_digest"])!=64:
                raise ValueError("CVH01_COLD_EVENT_DIGEST")
            bytes.fromhex(p["event_digest"])
            pa,pr,after=p["prev_action"],p["prev_reward"],p["previous_after"]
            if type(pa) is not int or type(pr) is not int or (pa==2)!=(pr==2) or pa not in (0,1,2) or pr not in (0,1,2):
                raise ValueError("CVH01_COLD_PREDECESSOR")
            if (after is None)!=(pa==2) or (after is not None and (type(after) is not int or after not in (0,1))):
                raise ValueError("CVH01_COLD_CONTINUITY")
            pending=p["pending"]
            if (type(pending) is not list or len(pending)>HORIZON-1 or
                (bool(pending)!=(after is not None)) or
                any(type(e) is not list or len(e)!=3 or
                  any(type(i) is not int for i in e) or
                  not 0<=e[0]<CONTEXTS or not 1<=e[2]<HORIZON or
                  not 0<=e[1]<=15 for e in pending) or
                [e[2] for e in pending]!=list(range(len(pending),0,-1))):
                raise ValueError("CVH01_COLD_PENDING")
            if sum(cs)+len(pending)!=seen:
                raise ValueError("CVH01_COLD_ACCOUNTING")
            result=cls()
            result.count=cs[:];result.total=ts[:]
            result.pending=[e[:] for e in pending]
            result.prev_action=pa;result.prev_reward=pr;result.previous_after=after
            result.seen=seen;result.event_digest=p["event_digest"]
            if result.snapshot()!=blob:
                raise ValueError("CVH01_COLD_NONCANONICAL")
            return result
        except (TypeError,ValueError,KeyError,UnicodeDecodeError) as e:
            raise ValueError("CVH01_COLD_REJECTED") from e

    def receipt(self):
        return sha256(self.snapshot()).hexdigest()
