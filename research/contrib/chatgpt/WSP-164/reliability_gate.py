"""WSP164: calibrate reliability of public feedback before using learned history.

SOURCE-FREE only. The gate uses five already witnessed public records from
this episode. It neither reads hidden regimes nor peeks at the current
transition outcome. It wraps the unchanged WSP163 direct-weight learner,
with a FIT-only single-scalar public residual consistency threshold.

The code is a bounded heuristic, not a newly discovered neural operator.
Independent Bayesian HMM-style model-selection and conventional controls
must be fitted and scored from identical public observations.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math

from public_boundary import PublicTransition
from history_weights import PublicHistoryWeights

SCHEMA = "yggdrasil.wsp164.public-history-reliability.v1"
MAGIC = b"YGR1"
MAX_BYTES = 12288
WINDOW = 5
LO = .75
HI = .86
MARGIN = .10


def _residual(program, row):
    if type(row) is not PublicTransition:
        raise ValueError("WSP164_PUBLIC_ONLY")
    if row.terminated or row.truncated:
        raise ValueError("WSP164_TERMINAL_HISTORY_FORBIDDEN")
    base = program.static_predict(row.observation, row.action)
    return tuple(row.next_observation[k] - base[k] for k in range(4))


def _observed_residual(program,row):
    if type(row) is not PublicTransition:
        raise ValueError("WSP164_PUBLIC_ONLY")
    base=program.static_predict(row.observation,row.action)
    return tuple(row.next_observation[k]-base[k] for k in range(4))


def _dot(x, y):
    return math.fsum(a*b for a, b in zip(x,y))


def _cosine(x, y):
    xx = _dot(x,x)
    yy = _dot(y,y)
    if min(xx,yy) <= 1e-16:
        return 0.
    value = _dot(x,y)/math.sqrt(xx*yy)
    if not math.isfinite(value):
        raise ValueError("WSP164_COSINE_NONFINITE")
    return max(-1., min(1., value))


def fit_public_threshold(program, fit_episodes):
    if type(program) is not PublicHistoryWeights:
        raise ValueError("WSP164_LEARNER_REQUIRED")
    if type(fit_episodes) not in (tuple,list) or len(fit_episodes) != 32:
        raise ValueError("WSP164_FIT_EPISODE_COUNT")
    similarities = []
    for episode in fit_episodes:
        if type(episode) not in (tuple,list) or len(episode) != 16:
            raise ValueError("WSP164_FIT_EPISODE_SHAPE")
        if any(type(x) is not PublicTransition for x in episode):
            raise ValueError("WSP164_FIT_PUBLIC_ONLY")
        for index in range(1,len(episode)):
            similarities.append(_cosine(_residual(program,episode[index-1]),
                                        _observed_residual(program,episode[index])))
            # The final observed terminal outcome is allowed as the current
            # FIT target; it is never used as a prior for the next episode.
    if len(similarities) != 480:
        raise ValueError("WSP164_FIT_PAIR_COUNT")
    average = math.fsum(similarities)/len(similarities)
    return max(LO,min(HI,average-MARGIN))


class ReliablePublicHistory:
    """One frozen fitted direct-weight learner and one learned coherence gate.

    The base/history coefficients are *not* changed by this module.
    At each episode first step the gate is OFF and the static base prediction
    is used. A memory correction requires five consecutive previous,
    nonterminal public outcomes with mutually coherent residual directions.
    """
    __slots__ = ("_program","_threshold")

    def __init__(self, program, threshold):
        if type(program) is not PublicHistoryWeights:
            raise ValueError("WSP164_PROGRAM_TYPE")
        if type(threshold) is not float or not LO<=threshold<=HI:
            raise ValueError("WSP164_THRESHOLD_INVALID")
        self._program = PublicHistoryWeights.restore(program.checkpoint())
        self._threshold = threshold

    @classmethod
    def from_fit(cls,program,fit_episodes):
        return cls(program,fit_public_threshold(program,fit_episodes))

    @property
    def threshold(self):
        return self._threshold

    def permitted(self,history):
        if type(history) not in (tuple,list) or len(history)>WINDOW:
            raise ValueError("WSP164_HISTORY_WINDOW")
        if any(type(row) is not PublicTransition for row in history):
            raise ValueError("WSP164_PUBLIC_HISTORY_ONLY")
        if any(row.terminated or row.truncated for row in history):
            raise ValueError("WSP164_EPISODE_HISTORY_RESET")
        if len(history)<WINDOW:
            return False
        observed = [_residual(self._program,row) for row in history]
        return all(_cosine(observed[i-1],observed[i])>=self._threshold
                   for i in range(1,WINDOW))

    def predict(self, public_state, chosen_action, history):
        # Validate current state/action through established strict numeric
        # model before evaluating any prior public history.
        baseline = self._program.static_predict(public_state,chosen_action)
        if not self.permitted(history):
            return baseline
        return self._program.predict(public_state,chosen_action,history[-1])

    def checkpoint(self):
        obj={
            "schema":SCHEMA,
            "program":self._program.checkpoint().hex(),
            "threshold":self._threshold,
        }
        payload=json.dumps(obj,sort_keys=True,separators=(",",":"),
                           allow_nan=False).encode("ascii")
        out=MAGIC+len(payload).to_bytes(4,"big")+payload
        out+=hashlib.sha256(out).digest()
        if len(out)>MAX_BYTES:
            raise ValueError("WSP164_CHECKPOINT_LIMIT")
        return out

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 40<len(raw)<=MAX_BYTES:
            raise ValueError("WSP164_CHECKPOINT_SIZE")
        if (raw[:4]!=MAGIC or
            int.from_bytes(raw[4:8],"big")!=len(raw)-40 or
            not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(),raw[-32:])):
            raise ValueError("WSP164_CHECKPOINT_INTEGRITY")
        def pairs_without_duplicates(pairs):
            out={}
            for k,v in pairs:
                if k in out:
                    raise ValueError("WSP164_DUPLICATE_FIELD")
                out[k]=v
            return out
        try:
            o=json.loads(raw[8:-32].decode("ascii"),object_pairs_hook=pairs_without_duplicates)
            if type(o) is not dict or set(o)!={"schema","program","threshold"} or o["schema"]!=SCHEMA:
                raise ValueError("WSP164_CHECKPOINT_SCHEMA")
            candidate=cls(PublicHistoryWeights.restore(bytes.fromhex(o["program"])),
                          o["threshold"])
        except (ValueError,OverflowError,TypeError,UnicodeError,KeyError) as exc:
            raise ValueError("WSP164_CHECKPOINT_FIELDS") from exc
        if candidate.checkpoint()!=raw:
            raise ValueError("WSP164_CHECKPOINT_NONCANONICAL")
        return candidate
