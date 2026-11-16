"""FKP-19 native sparse delayed-action credit and independent conventional arms.

All evidence is physically selected source-public before/action/after/reward
transitions. The policy sees no source law, private polarity, future result,
unrealized alternative, held world, or privileged trainer. The FKP18 trace is
reused (not copied) for every two-action witnessed episode. No transformers.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "FKP-18"))
from temporal_trace import PublicStep, PublicTransition, SparseTemporalTrace, _valid

MAX_BYTES = 65536
MODES = ("ELIGIBILITY_CONTRAST", "CURRENT_ACTION_ONLY",
         "CONTEXT_BLIND", "EARLY_ACTION_SHUFFLED", "NO_UPDATE")


def _canonical(x):
    return json.dumps(x, sort_keys=True, allow_nan=False,
                      separators=(",", ":")).encode("ascii")


def _pair(steps):
    if type(steps) is not tuple or len(steps) != 2:
        raise ValueError("FKP19_PUBLIC_TWO_ACTION_EPISODE_REQUIRED")
    first, second = map(_valid, steps)
    if any(type(row.action) is not int or row.action not in (0, 1)
           for row in (first, second)):
        raise ValueError("FKP19_BINARY_ACTION_ONLY")
    if (first.before[0] not in (0,1) or first.before[1] != 0 or
            first.after[1] != 1 or first.reward != 0 or first.done or first.history or
            first.before[0] != first.after[0] or
            second.before != first.after or second.after[1] != 2 or
            second.before[0] != second.after[0] or not second.done or
            len(second.history) != 1 or
            second.history[0] != PublicTransition(
                first.before, first.action, first.reward, first.after, first.done) or
            second.reward not in (-1.0, 1.0)):
        raise ValueError("FKP19_PUBLIC_DELAYED_TRANSCRIPT_INVALID")
    return (first.before[0], first.action, second.action, int(second.reward))


def _sorted_counts(d):
    return sorted((*k, sum_reward, n) for k, (sum_reward, n) in d.items())


class SparseLagCredit:
    """Selects which of two actually intervened action lags predicts reward."""

    def __init__(self, mode="ELIGIBILITY_CONTRAST"):
        if mode not in MODES:
            raise ValueError("FKP19_UNKNOWN_LEARNING_ARM")
        self.mode = mode
        self.begin_world()

    def begin_world(self):
        self._counts = {}
        self._train_episodes = 0
        self._trace_hashes = []
        return self

    def observe_episode(self, steps, *, learn=True):
        ctx, early, late, reward = _pair(steps)
        if type(learn) is not bool:
            raise ValueError("FKP19_LEARN_FLAG")
        trace = SparseTemporalTrace()
        for index, row in enumerate(steps):
            trace.observe_public(row, event_id=index)
        if trace.public_observations != 2:
            raise AssertionError("FKP19_TRACE_PHYSICAL_EVENTS")
        if not learn:
            return None
        if self._train_episodes >= 8:
            raise ValueError("FKP19_FROZEN_EIGHT_EXPLORATION_EPISODES")
        staged = dict(self._counts)
        if self.mode != "NO_UPDATE":
            key_ctx = 0 if self.mode == "CONTEXT_BLIND" else ctx
            events = []
            if self.mode == "CURRENT_ACTION_ONLY":
                events.append((key_ctx, 0, late))
            else:
                prior = (1-early) if self.mode == "EARLY_ACTION_SHUFFLED" else early
                events.append((key_ctx, 1, prior))
                if self.mode == "ELIGIBILITY_CONTRAST":
                    events.append((key_ctx, 0, late))
            for key in events:
                total, n = staged.get(key, (0, 0))
                staged[key] = (total + reward, n + 1)
        receipt = trace.semantic_receipt()
        expected_bytes = len(staged) * 24 + (len(self._trace_hashes)+1) * 32
        if expected_bytes > MAX_BYTES:
            raise ValueError("FKP19_LEARNED_CAPACITY_EXCEEDED")
        # Commit AFTER complete public validation and all capacity checks.
        self._counts = staged
        self._trace_hashes.append(receipt)
        self._train_episodes += 1
        return receipt

    @property
    def learned_logical_bytes(self):
        return len(self._counts)*24 + len(self._trace_hashes)*32

    @property
    def explored_episodes(self):
        return self._train_episodes

    def _contrast(self, context, lag):
        results = []
        for action in (0, 1):
            total, n = self._counts.get((context, lag, action), (0, 0))
            if not n:
                return None
            results.append(total/n)
        return results[1]-results[0]

    def inferred_reward_cause_lag(self, context):
        if self.mode == "NO_UPDATE":
            return None
        if self.mode == "CURRENT_ACTION_ONLY":
            return 0
        if self.mode in ("CONTEXT_BLIND","EARLY_ACTION_SHUFFLED"):
            return 1
        if type(context) is not int or context not in (0,1):
            raise ValueError("FKP19_PUBLIC_CONTEXT")
        first = self._contrast(context, 1)
        last = self._contrast(context, 0)
        if first is None or last is None or abs(first) == abs(last):
            return None
        return 1 if abs(first)>abs(last) else 0

    def choose_early(self, context):
        if type(context) is not int or context not in (0,1):
            raise ValueError("FKP19_PUBLIC_CONTEXT")
        if self._train_episodes != 8:
            raise ValueError("FKP19_NOT_FITTED_BEFORE_ACTION")
        if self.mode == "NO_UPDATE":
            return 0
        ctx = 0 if self.mode=="CONTEXT_BLIND" else context
        if self.inferred_reward_cause_lag(context) != 1:
            return 0
        contrast = self._contrast(ctx, 1)
        return 1 if contrast is not None and contrast > 0 else 0

    def state_receipt(self):
        return sha256(_canonical(self._state())).hexdigest()

    def _state(self):
        return {"schema":"fkp19.sparse-lag-credit.v1",
                "mode":self.mode,"count":self._train_episodes,
                "observed":_sorted_counts(self._counts),
                "public_trace_shas":list(self._trace_hashes)}

    def checkpoint(self):
        body = self._state()
        raw = _canonical(body)
        if len(raw)>MAX_BYTES:
            raise ValueError("FKP19_CHECKPOINT_TOO_LARGE")
        return _canonical({"body":body,"sha256":sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw)>MAX_BYTES:
            raise ValueError("FKP19_CHECKPOINT_INVALID")
        try:
            e = json.loads(raw,object_pairs_hook=_unique_pairs,
                           parse_constant=lambda _: _fail())
        except (ValueError,TypeError,UnicodeError) as exc:
            raise ValueError("FKP19_CHECKPOINT_INVALID") from exc
        if type(e) is not dict or set(e)!={"body","sha256"}:
            raise ValueError("FKP19_CHECKPOINT_ENVELOPE")
        b=e["body"]
        if type(b) is not dict or set(b)!={"schema","mode","count","observed","public_trace_shas"}:
            raise ValueError("FKP19_CHECKPOINT_SCHEMA")
        if sha256(_canonical(b)).hexdigest()!=e["sha256"] or b["schema"]!="fkp19.sparse-lag-credit.v1":
            raise ValueError("FKP19_CHECKPOINT_HASH_OR_VERSION")
        obj=cls(b["mode"])
        if type(b["count"]) is not int or not 0<=b["count"]<=8:
            raise ValueError("FKP19_CHECKPOINT_COUNT")
        if type(b["observed"]) is not list or type(b["public_trace_shas"]) is not list:
            raise ValueError("FKP19_CHECKPOINT_RECORDS")
        if len(b["public_trace_shas"])!=b["count"] or any(type(x) is not str or len(x)!=64 or
             any(c not in "0123456789abcdef" for c in x) for x in b["public_trace_shas"]):
            raise ValueError("FKP19_CHECKPOINT_TRACE_CUSTODY")
        d={}
        for item in b["observed"]:
            if type(item) is not list or len(item)!=5 or any(type(v) is not int for v in item):
                raise ValueError("FKP19_CHECKPOINT_ENTRY")
            ctx,lag,action,total,n=item
            if ctx not in (0,1) or lag not in (0,1) or action not in (0,1) or (
                not 1<=n<=8 or abs(total)>n):
                raise ValueError("FKP19_CHECKPOINT_ENTRY_RANGE")
            key=ctx,lag,action
            if key in d:
                raise ValueError("FKP19_CHECKPOINT_DUPLICATE_ENTRY")
            d[key]=(total,n)
        obj._counts=d
        obj._train_episodes=b["count"]
        obj._trace_hashes=list(b["public_trace_shas"])
        if obj.learned_logical_bytes>MAX_BYTES or obj.state_receipt()!=sha256(_canonical(b)).hexdigest():
            raise ValueError("FKP19_CHECKPOINT_COLD_MISMATCH")
        if obj.checkpoint()!=raw:
            raise ValueError("FKP19_CHECKPOINT_NONCANONICAL")
        return obj


class ExactBayesContext:
    """Independent closed-form Beta(1,1) model of directly observed rewards."""

    def __init__(self):
        self._wins={(ctx,act):0 for ctx in (0,1) for act in (0,1)}
        self._total={(ctx,act):0 for ctx in (0,1) for act in (0,1)}
        self._events=0

    def observe_episode(self,steps,*,learn=True):
        ctx,early,_late,reward=_pair(steps)
        if learn:
            if self._events>=8:
                raise ValueError("FKP19_BAYES_TRAINING_FROZEN")
            self._wins[(ctx,early)]+=reward==1
            self._total[(ctx,early)]+=1
            self._events+=1

    def choose_early(self,ctx):
        if self._events!=8 or type(ctx) is not int or ctx not in (0,1):
            raise ValueError("FKP19_BAYES_NOT_FIT")
        vals=[(self._wins[(ctx,a)]+1)/(self._total[(ctx,a)]+2) for a in (0,1)]
        return 1 if vals[1]>vals[0] else 0

    @property
    def learned_logical_bytes(self):
        return 4*2*4

    def state_receipt(self):
        return sha256(_canonical([sorted((*k,v) for k,v in self._wins.items()),
                                  sorted((*k,v) for k,v in self._total.items())])).hexdigest()


def _features(ctx,early,late):
    if any(type(x) is not int or x not in (0,1) for x in (ctx,early,late)):
        raise ValueError("FKP19_LOGISTIC_FEATURE")
    c,e,l=2*ctx-1,2*early-1,2*late-1
    return (1.0,float(c),float(e),float(c*e),float(l))


def _logistic(margin):
    if margin>=0:
        return 1/(1+math.exp(-margin))
    z=math.exp(margin)
    return z/(1+z)


class FullyFittedInteractionLogistic:
    """Conventional, wholly refitted logistic interaction model; no oracle."""

    def __init__(self):
        self._records=[]
        self._weights=None
        self.fit_epochs=0
        self.training_bce=None

    def observe_episode(self,steps,*,learn=True):
        ctx,early,late,reward=_pair(steps)
        if learn:
            if len(self._records)>=8 or self._weights is not None:
                raise ValueError("FKP19_LOGISTIC_TRAINING_FROZEN")
            self._records.append((_features(ctx,early,late),reward))

    def fit_after_exploration(self):
        if len(self._records)!=8 or self._weights is not None:
            raise ValueError("FKP19_LOGISTIC_EXPLORATION_INCOMPLETE")
        weights=[0.0]*5
        for epoch in range(1,1025):
            grad=[0.0]*5
            loss=0.0
            for x,y in self._records:
                margin=y*sum(w*f for w,f in zip(weights,x))
                loss+=math.log1p(math.exp(-margin)) if margin>-700 else -margin
                factor= -y*_logistic(-margin)
                for k,f in enumerate(x):
                    grad[k]+=factor*f/8
            loss/=8
            if loss<=0.05:
                self._weights=tuple(weights)
                self.fit_epochs=epoch
                self.training_bce=loss
                return self
            weights=[w-0.5*g for w,g in zip(weights,grad)]
        raise ValueError("FKP19_FULLY_TRAINED_CONVENTIONAL_NOT_CONVERGED")

    def choose_early(self,ctx):
        if self._weights is None:
            raise ValueError("FKP19_LOGISTIC_NOT_FULLY_TRAINED")
        expected=[]
        for early in (0,1):
            mean=0
            for late in (0,1):
                x=_features(ctx,early,late)
                margin=sum(w*f for w,f in zip(self._weights,x))
                mean+=_logistic(margin)/2
            expected.append(mean)
        return 1 if expected[1]>expected[0] else 0

    @property
    def learned_logical_bytes(self):
        return 5*8

    def state_receipt(self):
        if self._weights is None:
            raise ValueError("FKP19_LOGISTIC_NO_WEIGHTS")
        return sha256(_canonical({"weights":self._weights,
            "epochs":self.fit_epochs,"training_bce":self.training_bce})).hexdigest()


def _fail():
    raise ValueError("FKP19_JSON_NONFINITE")


def _unique_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:
            raise ValueError("FKP19_JSON_DUPLICATE")
        d[k]=v
    return d
