"""Prospective evaluator library. No executable primary runner or score admission.

Only the evaluator sees family/phase and probability laws. Learner interface
is (cursor, public key, pattern, four observed bits). No protected source.
"""
import hashlib
import itertools
import math
import sys
import time
from pathlib import Path

from adaptive_contract import AdaptiveContract, PAIRS
from transfer_prior import TransferContract
from quadratic_controls import QuadraticControl

# Import existing conventional control without copying or modifying its source.
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"ACE03-WSCM-CONTROL"))
from shared_count_control import SharedCountControl

DOMAIN = "ACE03-XFER01-DEV-A1"
SEEDS = (97001,97003,97009,97021,97027,97031,97033,97039)
FAMILIES = ("related","conflicting_C","null","unobservable_AB_alias")
PHASES = ((0,1024),(1,1024),(0,512),(2,256))
ARMS = ("candidate","local-only","count","quadratic","shared-quadratic","replay","fixed-prior")
CONVENTIONAL = ("count","quadratic","shared-quadratic","replay")
BUDGET = 16384


def digest(seed,*parts):
    return hashlib.sha256(":".join(map(str,(DOMAIN,seed,*parts))).encode("ascii")).digest()


def u64(seed,*parts):
    return int.from_bytes(digest(seed,*parts)[:8],"big")


def split(seed):
    ordered = sorted(range(512),key=lambda p:(digest(seed,"split",p),p))
    return tuple(ordered[:384]),tuple(ordered[384:])


def pairs(seed,j):
    order = sorted(range(36),key=lambda i:(digest(seed,"pair",j,i),i))
    return PAIRS[order[0]],PAIRS[order[1]]


def probability_tenths(seed,family,phase,pattern,j):
    if family=="null":
        return 5
    a,b = pairs(seed,j)
    i,k = b if phase==1 and family!="unobservable_AB_alias" else a
    v = 9 if ((pattern>>i)^(pattern>>k))&1 else 1
    if (phase==1 and family=="unobservable_AB_alias") or (phase==3 and family=="conflicting_C"):
        v = 10-v
    return v


def events(seed,family,phase,train,*,alter_prior=False):
    key,n = PHASES[phase]
    if family=="unobservable_AB_alias" and phase==1:
        key = 0
    for i in range(n):
        p = train[u64(seed,"pattern",phase,i)%len(train)]
        y = tuple(int(u64(seed,"label",phase,i,j) <
                      (probability_tenths(seed,family,phase,p,j)*(1<<64))//10)
                  for j in range(4))
        if alter_prior and phase<3:
            y = tuple(1-v for v in y)
        yield key,p,y


class FixedPrior(TransferContract):
    """Same capacity and update state, but no use of learned mixing weights."""
    def predict(self,key,pattern):
        if key is None:
            return super().predict(key,pattern)
        self._check(key,pattern)
        p,q = self._components(key,pattern)
        return tuple((a+b)/2 for a,b in zip(p,q))


def make_arm(name,seed):
    if name=="candidate":
        return TransferContract()
    if name=="local-only":
        return AdaptiveContract()
    if name=="count":
        return SharedCountControl()
    if name=="fixed-prior":
        return FixedPrior()
    if name in ("quadratic","shared-quadratic","replay"):
        return QuadraticControl({"quadratic":"local","shared-quadratic":"shared","replay":"replay"}[name],seed)
    raise ValueError("unknown arm")


def forecast(model,key,p):
    # Uniform unknown-key policy for all controls, charged as abstention.
    if key is None:
        return (.5,)*4,1
    raw = model.predict(key,p)
    if raw is None:
        return (.5,)*4,1
    q = tuple(float(x) for x in raw)
    if len(q)!=4 or any(not math.isfinite(x) or not 0<=x<=1 for x in q):
        raise ValueError("invalid forecast")
    return q,0


def expected_brier(model,key,patterns,law):
    scores,abstentions = [],0
    for p in patterns:
        q,a = forecast(model,key,p)
        abstentions += a
        for j,v in enumerate(q):
            t = law(p,j)/10
            scores.append(t*(1-v)**2+(1-t)*v*v)
    return math.fsum(scores)/len(scores),abstentions


def checkpoint(model):
    raw = model.checkpoint()
    if len(raw)>BUDGET:
        raise ValueError("persistent budget")
    if type(model).restore(raw).checkpoint()!=raw:
        raise ValueError("checkpoint roundtrip")
    return raw


def run_world_arm(seed,family,name,*,alter_prior=False):
    """Library only; primary execution admission and external resource wrapper pending."""
    if seed not in SEEDS or family not in FAMILIES or name not in ARMS:
        raise ValueError("study identity")
    train,held = split(seed)
    if set(train)&set(held):
        raise ValueError("split leakage")
    model = make_arm(name,seed)
    a_scores,early,checkpoints = [],[],[]
    update_seconds,predict_seconds = 0.,0.
    started = time.perf_counter()
    cold = None
    for phase in range(4):
        if phase==3:
            cold,_ = expected_brier(model,2,held,lambda p,j: probability_tenths(seed,family,3,p,j))
        for key,p,y in events(seed,family,phase,train,alter_prior=alter_prior):
            t = time.perf_counter()
            q,_ = forecast(model,key,p)
            predict_seconds += time.perf_counter()-t
            if phase==3:
                early.append(math.fsum((a-b)**2 for a,b in zip(q,y))/4)
            t = time.perf_counter()
            model.observe(model.cursor,key,p,y)
            update_seconds += time.perf_counter()-t
        # A retention targets original observable A; alias diagnostic scored separately.
        loss,_ = expected_brier(model,0,held,lambda p,j: probability_tenths(seed,family,0,p,j))
        a_scores.append(loss)
        raw = checkpoint(model)
        checkpoints.append({"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
        if time.perf_counter()-started>60:
            raise TimeoutError("per-arm budget")
    final,_ = expected_brier(model,2,held,lambda p,j: probability_tenths(seed,family,3,p,j))
    negative_key = 0 if family=="unobservable_AB_alias" else 2
    null_loss,_ = expected_brier(model,negative_key,held,lambda p,j:5)
    return {"seed":seed,"family":family,"arm":name,"alter_prior":alter_prior,
            "c_cold":cold,"c_early":math.fsum(early)/len(early),"c_final":final,
            "a_boundaries":a_scores,"a_max_drift":max(a_scores)-a_scores[0],
            "balanced_null_brier":null_loss,"checkpoint_boundaries":checkpoints,
            "cursor":model.cursor,"update_seconds":update_seconds,
            "predict_seconds":predict_seconds,"wall_seconds":time.perf_counter()-started,
            "qualification":"PARTIAL_LIBRARY_ONLY; subprocess cold continuation, resource wrapper, and admission not implemented"}


def paired_primary(rows):
    """Require complete related family, compare per-seed strongest conventional."""
    gains = []
    for seed in SEEDS:
        by = {}
        for row in rows:
            if row["seed"]==seed and row["family"]=="related" and not row["alter_prior"]:
                if row["arm"] in by:
                    raise ValueError("duplicate row")
                by[row["arm"]] = row
        if set(by)!=set(ARMS):
            raise ValueError("incomplete arms")
        winner = min(CONVENTIONAL,key=lambda n:by[n]["c_final"])
        gains.append({"seed":seed,"winner":winner,"gain":by[winner]["c_final"]-by["candidate"]["c_final"]})
    mean = math.fsum(x["gain"] for x in gains)/len(gains)
    return {"gains":gains,"mean_gain":mean,
            "primary_threshold_only":mean>=.005 and all(x["gain"]>0 for x in gains)}
