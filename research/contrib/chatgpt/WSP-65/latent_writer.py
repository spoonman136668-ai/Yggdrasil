"""WSP65 source-blind hidden-parity causal memory and matched controls.

Hypothesis space (explicit strong prior): exactly one unknown action channel
flips a latent binary parity bit, or no latent parity. Per action/output bit,
all <=3-term degree<=2 Boolean numerical polynomials over current visible
bits + candidate latent parity are fitted to charged chronological evidence.
Prediction is *unanimity* over all globally consistent latent candidates and
all consistent numerical rules. The source/true hidden bit are never read.
"""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json

ACTIONS=(0,1,2,3)
MAX_TRAIN=128
MAX_SNAPSHOT_BYTES=350000


def _canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def _valid(state,n):
    if (type(state) is not tuple or len(state)!=n or
            any(type(v) is not int or v not in (0,1) for v in state)):
        raise ValueError("bad observable binary sensor input")
    return state


@lru_cache(maxsize=2)
def _terms(n):
    if n not in (3,4):
        raise ValueError("outside WSP65 sensor dimensions")
    dim=n+1  # Last feature is an UNKNOWN candidate latent parity.
    return tuple(term for degree in (0,1,2)
                 for term in combinations(range(dim),degree))


@lru_cache(maxsize=2)
def _masks(n):
    count=len(_terms(n))
    return tuple(sum(1<<col for col in cols)
                 for size in range(4)
                 for cols in combinations(range(count),size))


def _features(state,h):
    vals=state+(h,)
    return sum(1<<i for i,t in enumerate(_terms(len(state)))
               if all(vals[j] for j in t))


def _experience_projection(history,current,n):
    """No hidden signal. Public evaluation prefix used only as context."""
    expected=(0,)*n
    actions=[]
    if type(history) not in (list,tuple):
        raise ValueError("history must be chronological public experiences")
    for row in history:
        _valid(row.before,n)
        _valid(row.after,n)
        if (row.before!=expected or type(row.action) is not int or
                row.action not in ACTIONS or row.action_cost!=1):
            raise ValueError("invalid source-blind public history chain")
        actions.append(row.action)
        expected=row.after
    _valid(current,n)
    if expected!=current:
        raise ValueError("visible state/history mismatch")
    return tuple(actions)


class SourceBlindExplorer:
    """Simple fixed source-blind action-coverage policy, no oracle access.

    Periodically deliberately repeat an already observed visible
    state/action to seek consequences that differ under hidden modes.
    """
    def __init__(self):
        self.ledger=[]

    def select(self,current):
        t=len(self.ledger)
        global_counts=Counter(a for before,a,after in self.ledger)
        pair_counts=Counter((before,a) for before,a,after in self.ledger)
        repeated=[a for a in ACTIONS if pair_counts[current,a]>0]
        if t%11==7 and repeated:
            return min(repeated,key=lambda a:(pair_counts[current,a],
                                               global_counts[a],a))
        return max(ACTIONS,key=lambda a:(
            int(pair_counts[current,a]==0),
            -pair_counts[current,a],-global_counts[a],-a))

    def observe(self,experience):
        if self.ledger and self.ledger[-1][2]!=experience.before:
            raise ValueError("source-blind explorer cannot teleport")
        self.ledger.append(
            (experience.before,experience.action,experience.after))


class HiddenParityWriter:
    gradient_steps=0

    def __init__(self):
        self.dimension=None
        self.state=None
        self.rows=[]
        self._fitted=None
        self.model_candidate_evaluations=0

    def observe(self,row):
        before=row.before
        after=row.after
        if self.dimension is None:
            if (type(before) is not tuple or len(before) not in (3,4) or
                    before!=(0,)*len(before)):
                raise ValueError("noninitial observable source start")
            self.dimension=len(before)
            self.state=before
        _valid(before,self.dimension)
        _valid(after,self.dimension)
        if (type(row.action) is not int or row.action not in ACTIONS or
                type(row.action_cost) is not int or row.action_cost!=1 or
                len(self.rows)>=MAX_TRAIN or self.state!=before):
            raise ValueError("charged no-reset observation invalid")
        self.rows.append((before,row.action,after))
        self.state=after
        self._fitted=None

    def _fit(self):
        if self._fitted is not None:
            return self._fitted
        if self.dimension is None:
            return ()
        hypotheses=[]
        tested=0
        masks=_masks(self.dimension)
        for toggle_action in (*ACTIONS,None):
            parity=0
            charged={a:[] for a in ACTIONS}
            for before,action,after in self.rows:
                charged[action].append((_features(before,parity),after))
                if toggle_action==action:
                    parity ^= 1
            per_action=[]
            admissible=True
            for action in ACTIONS:
                if not charged[action]:
                    admissible=False
                    break
                by_bit=[]
                for output_bit in range(self.dimension):
                    relevant=tuple((feature,after[output_bit])
                                   for feature,after in charged[action])
                    candidates=[]
                    for mask in masks:
                        tested+=1
                        if all(((mask & features).bit_count() & 1)==observed
                               for features,observed in relevant):
                            candidates.append(mask)
                    if not candidates:
                        admissible=False
                        break
                    by_bit.append(tuple(candidates))
                if not admissible:
                    break
                per_action.append(tuple(by_bit))
            if admissible:
                hypotheses.append((toggle_action,tuple(per_action)))
        self.model_candidate_evaluations=tested
        self._fitted=tuple(hypotheses)
        return self._fitted

    def toggler_candidates(self):
        return tuple(toggle for toggle,actions in self._fit())

    def candidate_counts(self):
        return tuple((toggle,tuple(tuple(len(masks) for masks in action)
                                   for action in actions))
                     for toggle,actions in self._fit())

    def predict(self,history,current,action):
        if self.dimension is None:
            return None
        actions=_experience_projection(history,current,self.dimension)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid next public action")
        hypotheses=self._fit()
        if not hypotheses:
            return None
        joint_predictions=set()
        for toggle,by_action in hypotheses:
            h=(sum(a==toggle for a in actions)%2) if toggle is not None else 0
            features=_features(current,h)
            output=[]
            for candidates in by_action[action]:
                possibilities={
                    ((mask & features).bit_count() & 1)
                    for mask in candidates
                }
                if len(possibilities)!=1:
                    return None
                output.append(next(iter(possibilities)))
            joint_predictions.add(tuple(output))
            if len(joint_predictions)>1:
                return None
        return next(iter(joint_predictions))

    def training_visible_conflicts(self):
        source={}
        for before,a,after in self.rows:
            source.setdefault((before,a),set()).add(after)
        return tuple(sorted((before,a) for (before,a),options
                            in source.items() if len(options)>1))

    def snapshot(self):
        payload={
            "schema":"wsp65.hidden-parity-writer.v1",
            "dimension":self.dimension,
            "ledger":[[list(b),a,list(after)] for b,a,after in self.rows],
            "gradient_steps":0
        }
        digest=sha256(_canon(payload).encode("ascii")).hexdigest()
        raw=_canon({"payload":payload,"sha256":digest})
        if len(raw.encode("ascii"))>MAX_SNAPSHOT_BYTES:
            raise OverflowError("knowledge snapshot budget")
        return raw

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw.encode("utf-8"))>MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid memory bytes")
        try:
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("bad memory envelope")
            p=obj["payload"]
            if (type(p) is not dict or
                    p.get("schema")!="wsp65.hidden-parity-writer.v1" or
                    p.get("gradient_steps")!=0 or
                    sha256(_canon(p).encode("ascii")).hexdigest()!=obj["sha256"]):
                raise ValueError("bad memory hash/schema")
            rows=p["ledger"]
            if type(rows) is not list or len(rows)>MAX_TRAIN:
                raise ValueError("invalid charged experience ledger")
            learner=cls()
            for row in rows:
                if type(row) is not list or len(row)!=3:
                    raise ValueError("bad stored observation")
                b,action,after=row
                class Public:
                    pass
                experience=Public()
                experience.before,experience.action,experience.after,experience.action_cost=(
                    tuple(b),action,tuple(after),1)
                learner.observe(experience)
            if learner.dimension!=p["dimension"] or learner.snapshot()!=raw:
                raise ValueError("noncanonical memory")
            return learner
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError,
                json.JSONDecodeError) as e:
            raise ValueError("invalid/tampered memory") from e

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8


class VisibleLookup:
    """Same-experience visible state/action lookup, conflict => abstain."""
    def __init__(self,rows):
        self.table={}
        for before,action,after in rows:
            self.table.setdefault((before,action),set()).add(after)

    def predict(self,history,current,action):
        values=self.table.get((current,action),set())
        return next(iter(values)) if len(values)==1 else None


class Suffix2Lookup:
    """Independent 2-previous-action + visible-state empirical baseline."""
    def __init__(self,rows):
        self.table={}
        action_history=[]
        for before,action,after in rows:
            key=(before,tuple(action_history[-2:]),action)
            self.table.setdefault(key,set()).add(after)
            action_history.append(action)

    def predict(self,history,current,action):
        prior=tuple(row.action for row in history[-2:])
        values=self.table.get((current,prior,action),set())
        return next(iter(values)) if len(values)==1 else None
