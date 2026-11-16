"""CVH-06 fully fitted four-cell public-only conventional online policy.

Source-free reusable experiment control, NOT a genuine source owner/executor.
Reads only original FKP24-compatible public (before,action,reward,after,
terminated,truncated). No environment imports, seed selection, reset, do,
future labels, source-private graph or counterfactual.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
UPSTREAM_PUBLIC=HERE.parent/"CVH-02"
if str(UPSTREAM_PUBLIC) not in sys.path:
    sys.path.insert(0,str(UPSTREAM_PUBLIC))
from public_policy import _event, PublicEarnedPolicy  # inherited unchanged

SCHEMA="yggdrasil.cvh06.four-cell-online-public-earned-return.v1"
HORIZON=4
SCALE=8
MAX_STEPS_PER_EPISODE=32
MAX_SEEN=1_000_000
PUBLIC_FIELDS=("before","action","reward","after","terminated","truncated")


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      allow_nan=False,ensure_ascii=True).encode("ascii")


def _cell(b,a):
    if type(b) is not int or b not in (0,1) or type(a) is not int or a not in (0,1):
        raise ValueError("CVH06_PUBLIC_FOURCELL_NONBINARY")
    return 2*b+a


class FourCellEarnedPolicy:
    """Conventional fitted 2x2 (public state,action) 4-step return policy.

    Learned return is based ONLY on actual observed future rewards. An earlier
    action receives 1,1/2,1/4,1/8 reward credit from four successive original
    public outcomes; observation after step, never before. Unknown contexts
    explore by already observed action counts; enough-support ties select 0.
    """
    def __init__(self,min_support=2):
        if type(min_support) is not int or not 1<=min_support<=100:
            raise ValueError("CVH06_BAD_MIN_SUPPORT")
        self.min_support=min_support
        self.count=[0]*4
        self.total=[0]*4
        self.attempts=[0]*4
        self.pending=[]
        self.previous_after=None
        self.episode_history=[]
        self.outstanding=None
        self.seen=0
        self.digest=hashlib.sha256(b"CVH06-FOURCELL-INIT").hexdigest()

    def choose(self,state,history):
        if type(state) is not int or state not in (0,1) or type(history) is not tuple:
            raise ValueError("CVH06_CHOOSE_PUBLIC_STATE_AND_TUPLE_ONLY")
        if self.outstanding is not None:
            raise ValueError("CVH06_UNOBSERVED_SELECTED_ACTION_NO_REPLAY")
        rows=[_event(x) for x in history]
        if rows!=self.episode_history:
            raise ValueError("CVH06_PUBLIC_EPISODE_HISTORY_DRIFT")
        if len(rows)>=MAX_STEPS_PER_EPISODE:
            raise ValueError("CVH06_PUBLIC_EPISODE_ACTION_BUDGET")
        if (self.previous_after is None and rows) or (
                self.previous_after is not None and state!=self.previous_after):
            raise ValueError("CVH06_PUBLIC_STATE_CONTINUITY")
        k0=_cell(state,0)
        k1=_cell(state,1)
        if min(self.count[k0],self.count[k1])>=self.min_support:
            # Compare integers without floating-point drift or source details.
            action=1 if self.total[k1]*self.count[k0]>self.total[k0]*self.count[k1] else 0
        else:
            action=0 if self.attempts[k0]<=self.attempts[k1] else 1
        self.outstanding=(state,action)
        return action

    def observe(self,row):
        event=_event(row)  # exact inherited six-field public validator
        if self.outstanding is None or tuple(event[:2])!=self.outstanding:
            raise ValueError("CVH06_NO_SELECTED_ACTION_OR_WRONG_SOURCE_REPLY")
        if self.previous_after is not None and event[0]!=self.previous_after:
            raise ValueError("CVH06_RESULT_PUBLIC_CONTINUITY")
        if len(self.episode_history)>=MAX_STEPS_PER_EPISODE:
            raise ValueError("CVH06_RESULT_OVER_BUDGET")
        done,trunc=event[4:]
        if len(self.episode_history)==MAX_STEPS_PER_EPISODE-1 and not (done or trunc):
            raise ValueError("CVH06_UNCLOSED_MAXIMUM_ACTION")
        if self.seen>=MAX_SEEN:
            raise ValueError("CVH06_OBSERVATION_BOUND")
        key=_cell(event[0],event[1])
        pending=[v[:] for v in self.pending]+[[key,0,0]]
        completed=[]
        for item in pending:
            age=item[2]
            if not 0<=age<HORIZON:
                raise ValueError("CVH06_PENDING_AGE_INVALID")
            item[1]+=event[2]*(SCALE>>age)
            item[2]+=1
            if item[2]==HORIZON or done or trunc:
                completed.append(item)
        remain=[] if done or trunc else [v for v in pending if v[2]<HORIZON]
        if len(remain)>=HORIZON:
            raise ValueError("CVH06_PENDING_LIMIT")
        next_count=self.count[:]
        next_total=self.total[:]
        for slot,ret,age in completed:
            if next_count[slot]>=MAX_SEEN or next_total[slot]+ret>15*MAX_SEEN:
                raise ValueError("CVH06_NUMERIC_RETURN_OVERFLOW")
            next_count[slot]+=1
            next_total[slot]+=ret
        next_attempts=self.attempts[:]
        if next_attempts[key]>=MAX_SEEN:
            raise ValueError("CVH06_ACTION_ATTEMPT_OVERFLOW")
        next_attempts[key]+=1
        next_digest=hashlib.sha256(bytes.fromhex(self.digest)+_canonical(event)).hexdigest()
        # All validations are complete: commit atomically, then ACK action.
        self.count,self.total,self.attempts=next_count,next_total,next_attempts
        self.pending=remain
        self.previous_after=None if done or trunc else event[3]
        self.episode_history=[] if done or trunc else self.episode_history+[event]
        self.digest=next_digest
        self.seen+=1
        self.outstanding=None

    def estimate(self,before,action):
        key=_cell(before,action)
        return None if not self.count[key] else self.total[key]/(SCALE*self.count[key])

    def snapshot(self):
        if self.outstanding is not None:
            raise ValueError("CVH06_PENDING_SOURCE_ACTION_CANNOT_COLD_SNAPSHOT")
        state={"schema":SCHEMA,"min_support":self.min_support,
               "count":self.count,"total":self.total,"attempts":self.attempts,
               "pending":self.pending,"previous_after":self.previous_after,
               "episode_history":self.episode_history,"seen":self.seen,
               "digest":self.digest}
        return _canonical({"payload":state,"sha256":hashlib.sha256(_canonical(state)).hexdigest()})

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<16_000:
            raise ValueError("CVH06_BAD_COLD_PAYLOAD_LENGTH")
        try:
            document=json.loads(blob)
            if type(document) is not dict or set(document)!={"payload","sha256"}:
                raise ValueError("CVH06_COLD_BAD_ENVELOPE")
            state=document["payload"]
            if (type(state) is not dict or set(state)!={
                    "schema","min_support","count","total","attempts","pending",
                    "previous_after","episode_history","seen","digest"}
                    or state["schema"]!=SCHEMA or _canonical(document)!=blob
                    or hashlib.sha256(_canonical(state)).hexdigest()!=document["sha256"]):
                raise ValueError("CVH06_COLD_SCHEMA_OR_INTEGRITY")
            count,total,attempts=state["count"],state["total"],state["attempts"]
            seen=state["seen"]
            if (any(type(v) is not list or len(v)!=4 for v in (count,total,attempts))
                    or type(seen) is not int or not 0<=seen<=MAX_SEEN
                    or any(type(x) is not int or not 0<=x<=MAX_SEEN for x in count+attempts)
                    or any(type(v) is not int or not 0<=v<=15*n for n,v in zip(count,total))
                    or sum(attempts)!=seen):
                raise ValueError("CVH06_COLD_NUMERIC_CUSTODY")
            pending=state["pending"]
            if (type(pending) is not list or len(pending)>HORIZON-1
                    or any(type(v) is not list or len(v)!=3 or
                           any(type(z) is not int for z in v) or not 0<=v[0]<4 or
                           not 0<=v[1]<=15 or not 1<=v[2]<HORIZON for v in pending)
                    or [p[2] for p in pending]!=list(range(len(pending),0,-1))
                    or sum(count)+len(pending)!=seen):
                raise ValueError("CVH06_COLD_PENDING_ACCOUNTING")
            history=state["episode_history"]
            last=state["previous_after"]
            if type(history) is not list or len(history)>=MAX_STEPS_PER_EPISODE:
                raise ValueError("CVH06_COLD_HISTORY")
            if bool(history)!=(last is not None) or bool(pending)!=bool(history):
                raise ValueError("CVH06_COLD_HISTORY_STATE_MISMATCH")
            if last is not None and (type(last) is not int or last not in (0,1)):
                raise ValueError("CVH06_COLD_NEXT_STATE_TYPE")
            for ix,e in enumerate(history):
                if (type(e) is not list or len(e)!=6 or
                        any(type(v) is not int or v not in (0,1) for v in e[:4])
                        or any(type(v) is not bool for v in e[4:])
                        or e[4] or e[5] or
                        (ix>0 and history[ix-1][3]!=e[0])):
                    raise ValueError("CVH06_COLD_PUBLIC_HISTORY_INVALID")
            if history and history[-1][3]!=last:
                raise ValueError("CVH06_COLD_LAST_STATE_DRIFT")
            if (type(state["digest"]) is not str or len(state["digest"])!=64):
                raise ValueError("CVH06_COLD_EVENT_SHA")
            bytes.fromhex(state["digest"])
            obj=cls(state["min_support"])
            obj.count=count[:];obj.total=total[:];obj.attempts=attempts[:]
            obj.pending=[v[:] for v in pending]
            obj.previous_after=last
            obj.episode_history=[r[:] for r in history]
            obj.seen=seen
            obj.digest=state["digest"]
            if obj.snapshot()!=blob:
                raise ValueError("CVH06_COLD_NOT_CANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError("CVH06_COLD_REJECTED") from exc


def independent_fourcell_public_batch(events):
    """Independent offline exact conventional fit. No control-model import.

    Only already witnessed full episodes or completed 4-step forward windows
    contribute; never look ahead beyond the provided public tape.
    """
    if type(events) not in (list,tuple):
        raise ValueError("CVH06_BATCH_EXPECTS_PUBLIC_SEQUENCE")
    counts=[0]*4;totals=[0]*4
    episode=[]
    previous_after=None
    def close(rows,closed):
        for t,(b,a,_) in enumerate(rows):
            if not closed and len(rows)-t<HORIZON:
                continue
            value=sum(rows[t+k][2]*(SCALE>>k)
                      for k in range(min(HORIZON,len(rows)-t)))
            key=2*b+a
            counts[key]+=1;totals[key]+=value
    for row in events:
        values=_event(row)
        before,action,reward,after,done,truncated=values
        if previous_after is not None and before!=previous_after:
            raise ValueError("CVH06_BATCH_BAD_PUBLIC_CONTINUITY")
        episode.append((before,action,reward))
        if done or truncated:
            close(episode,True)
            episode=[]
            previous_after=None
        else:
            previous_after=after
    close(episode,False)
    return counts,totals
