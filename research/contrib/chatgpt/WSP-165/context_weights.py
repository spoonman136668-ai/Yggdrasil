"""WSP165: opt-in, source-free, latent context from public consequence evidence.

This is a bounded, conventional Bayesian two-mode filter whose emission
prototypes are programmed directly as witnessed public residual averages.
It is NOT an original model architecture breakthrough, native integration,
or authority to execute protected Causal-Gymnasium sources.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math

from direct_weights import ProgrammedPublicDynamics
from public_boundary import PublicTransition

SCHEMA = "yggdrasil.wsp165.public-context.direct-prototype.v1"
MAGIC = b"YCP1"
MAX_HISTORY = 5
MAX_FIT_ROWS = 512
MAX_BYTES = 6144


def _dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def _residual(base, row):
    if type(row) is not PublicTransition:
        raise ValueError("WSP165_PUBLIC_RECORD_REQUIRED")
    pred = base.predict(row.observation, row.action)
    out = tuple(row.next_observation[k]-pred[k] for k in range(4))
    if not all(math.isfinite(x) for x in out):
        raise ValueError("WSP165_PUBLIC_RESIDUAL_NONFINITE")
    return out


def _validate_model(base, means, counts, stay, fit_rows):
    if type(base) is not ProgrammedPublicDynamics:
        raise ValueError("WSP165_STATIC_MODEL_REQUIRED")
    if type(fit_rows) is not int or not 0<=fit_rows<=MAX_FIT_ROWS:
        raise ValueError("WSP165_FIT_COUNT")
    if type(counts) not in (list,tuple) or len(counts)!=2 or any(
            type(c) is not int or c<1 or c>MAX_FIT_ROWS for c in counts):
        raise ValueError("WSP165_MODE_COUNTS")
    if sum(counts)!=fit_rows:
        raise ValueError("WSP165_COUNT_MISMATCH")
    if type(means) not in (list,tuple) or len(means)!=2:
        raise ValueError("WSP165_MEAN_SHAPE")
    for row in means:
        if type(row) not in (list,tuple) or len(row)!=4 or any(
                type(v) not in (int,float) or not math.isfinite(v) for v in row):
            raise ValueError("WSP165_MEAN_NONFINITE")
    if type(stay) is not float or not .50<=stay<=.999:
        raise ValueError("WSP165_STAY_PRIOR")
    if means[1][0]<=means[0][0]:
        raise ValueError("WSP165_NONSEPARATED_PROTOTYPES")


def _mode(means, residual):
    # Classification uses ONLY previously observed public residuals.
    # The mode labels are internal inferred prototype indices.
    distance0 = _dot(tuple(residual[i]-means[0][i] for i in range(4)),
                     tuple(residual[i]-means[0][i] for i in range(4)))
    distance1 = _dot(tuple(residual[i]-means[1][i] for i in range(4)),
                     tuple(residual[i]-means[1][i] for i in range(4)))
    return int(distance1<distance0)


class DirectPublicContext:
    """One shared direct-write prototype table and Bayesian public-memory gate.

    The frozen base predicts from (state, selected public action). Previous
    observed consequences reveal a probabilistic regime mode. Without a
    witnessed previous transition, predict exactly as the base; no oracle mode
    labels and no current outcome leakage are possible through this API.
    """
    __slots__=("_base","_means","_counts","_stay","_fit_rows")

    def __init__(self, base, means, counts, stay, fit_rows):
        _validate_model(base, means, counts, stay, fit_rows)
        self._base = ProgrammedPublicDynamics.restore(base.checkpoint())
        self._means=tuple(tuple(float(v) for v in row) for row in means)
        self._counts=tuple(counts)
        self._stay=stay
        self._fit_rows=fit_rows

    @classmethod
    def fit(cls, base, fit_episodes):
        if type(base) is not ProgrammedPublicDynamics:
            raise ValueError("WSP165_STATIC_MODEL_REQUIRED")
        if type(fit_episodes) not in (tuple,list) or len(fit_episodes)!=32:
            raise ValueError("WSP165_EPISODE_COUNT")
        sums=[[0.]*4 for _ in range(2)]
        counts=[0,0]
        same=0
        total=0
        for ep in fit_episodes:
            if type(ep) not in (tuple,list) or len(ep)!=16:
                raise ValueError("WSP165_FIT_EPISODE_SHAPE")
            prev=None
            for i,row in enumerate(ep):
                r=_residual(base,row)
                if i!=15 and (row.terminated or row.truncated):
                    raise ValueError("WSP165_FIT_EARLY_TERMINAL")
                if i==15 and not (row.terminated or row.truncated):
                    raise ValueError("WSP165_FIT_MISSING_TERMINAL")
                mode=int(r[0]>=0.)
                counts[mode]+=1
                for k in range(4):
                    sums[mode][k]+=r[k]
                if prev is not None:
                    same+=int(mode==prev)
                    total+=1
                prev=mode
        if total!=480 or sum(counts)!=512 or min(counts)<1:
            raise ValueError("WSP165_FIT_UNBALANCED")
        means=tuple(tuple(sums[i][k]/counts[i] for k in range(4))
                    for i in range(2))
        if means[1][0]<=means[0][0]:
            raise ValueError("WSP165_FIT_MODE_ORDER")
        stay=min(.999,max(.50,(same+1)/(total+2)))
        return cls(base,means,counts,float(stay),512)

    @property
    def stay_probability(self):
        return self._stay

    @property
    def prototypes(self):
        return self._means

    def static_predict(self, state, action):
        return self._base.predict(state,action)

    def _public_modes(self, history):
        if type(history) not in (tuple,list) or len(history)>MAX_HISTORY:
            raise ValueError("WSP165_HISTORY_WINDOW")
        modes=[]
        for row in history:
            if type(row) is not PublicTransition:
                raise ValueError("WSP165_HISTORY_PUBLIC_ONLY")
            if row.terminated or row.truncated:
                raise ValueError("WSP165_HISTORY_TERMINAL_RESET")
            modes.append(_mode(self._means,_residual(self._base,row)))
        return tuple(modes)

    def inferred_persistence(self, history):
        modes=self._public_modes(history)
        if len(modes)<2:
            return .5
        log_bayes=0.
        for a,b in zip(modes[:-1],modes[1:]):
            event=self._stay if a==b else (1-self._stay)
            log_bayes+=math.log(event/.5)
        if log_bayes>=0:
            return 1/(1+math.exp(-log_bayes))
        positive=math.exp(log_bayes)
        return positive/(1+positive)

    def predict(self, state, action, history=()):
        baseline=self._base.predict(state,action)
        modes=self._public_modes(history)
        if not modes:
            return baseline
        p=self.inferred_persistence(history)
        center=tuple((self._means[0][k]+self._means[1][k])/2
                     for k in range(4))
        shift=self._means[modes[-1]]
        coefficient=p*(2*self._stay-1)
        out=tuple(baseline[k]+center[k]+coefficient*(shift[k]-center[k])
                  for k in range(4))
        if not all(math.isfinite(x) for x in out):
            raise ValueError("WSP165_PREDICT_NONFINITE")
        return out

    def checkpoint(self):
        obj={
            "schema":SCHEMA,
            "base":self._base.checkpoint().hex(),
            "means":[list(row) for row in self._means],
            "counts":list(self._counts),
            "stay":self._stay,
            "fit_rows":self._fit_rows
        }
        payload=json.dumps(obj,sort_keys=True,separators=(",",":"),
                           allow_nan=False).encode("ascii")
        wire=MAGIC+len(payload).to_bytes(4,"big")+payload
        wire+=hashlib.sha256(wire).digest()
        if len(wire)>MAX_BYTES:
            raise ValueError("WSP165_CHECKPOINT_TOO_LARGE")
        return wire

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 40<len(raw)<=MAX_BYTES:
            raise ValueError("WSP165_CHECKPOINT_SIZE")
        if (raw[:4]!=MAGIC or
            int.from_bytes(raw[4:8],"big")!=len(raw)-40 or
            not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(),raw[-32:])):
            raise ValueError("WSP165_CHECKPOINT_DIGEST")
        def no_dupes(pairs):
            result={}
            for k,v in pairs:
                if k in result:
                    raise ValueError("WSP165_DUPLICATE_FIELD")
                result[k]=v
            return result
        try:
            obj=json.loads(raw[8:-32].decode("ascii"),object_pairs_hook=no_dupes)
            if type(obj) is not dict or set(obj)!={
                    "schema","base","means","counts","stay","fit_rows"} or obj["schema"]!=SCHEMA:
                raise ValueError("WSP165_CHECKPOINT_SCHEMA")
            base=ProgrammedPublicDynamics.restore(bytes.fromhex(obj["base"]))
            model=cls(base,obj["means"],obj["counts"],obj["stay"],obj["fit_rows"])
        except (ValueError,UnicodeError,TypeError,OverflowError,KeyError) as exc:
            raise ValueError("WSP165_CHECKPOINT_FIELDS") from exc
        if model.checkpoint()!=raw:
            raise ValueError("WSP165_CHECKPOINT_NONCANONICAL")
        return model
