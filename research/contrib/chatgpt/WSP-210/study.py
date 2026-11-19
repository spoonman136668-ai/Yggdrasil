"""WSP-210 preregistered regularization/transfer experiment; fabricated data only.

The original GFP source and native Yggdrasil owner are never read or invoked.
The primary seeds were frozen in prereg commit f5667a959708e016b136fea00b08f3d56ff66024.
"""
from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "WSP-200"))
import learner as core
from learner import Learner, Sample, pair_group, group_bucket, fit_stage
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse

SCHEMA = "wsp210.regularization-transfer.source-free.v1"
PREREG_SHA = "f5667a959708e016b136fea00b08f3d56ff66024"
WORLDS = ((21011, "hub", 64), (21012, "hub", 64),
          (21013, "complete", 16), (21014, "complete", 16))
SMOKE = (21001, "complete", 10)
LAMBDAS = (10.0, 2.0, 0.2)
RANK = 4
ADAM_MAX = 2500
ADAM_MIN = 300
ADAM_LR = 0.03


@contextmanager
def ridge_scope(lam: float):
    """Restore upstream WSP200 constant unconditionally; no source modification."""
    if lam not in LAMBDAS or core.LAMBDA != 10.0:
        raise ValueError("unfrozen or nested ridge context")
    core.LAMBDA = lam
    try:
        yield
    finally:
        core.LAMBDA = 10.0


def _pairs(kind: str, n: int):
    if kind == "hub":
        return [(1, j) for j in range(2, n+1)] + [
            (j, j+1) for j in range(2, n-1, 2)]
    if kind == "complete":
        return [(i, j) for i in range(1, n+1) for j in range(i+1, n+1)]
    raise ValueError("unfrozen topology")


def _factor(seed: int, pos: int, allele: str) -> tuple[float, ...]:
    if allele not in ("C", "D"):
        raise ValueError("unfrozen alternate allele")
    shift = 0.7 if allele == "D" else 0.0
    return tuple(
        math.sin((pos+shift)*(k+1)*0.37+seed*0.013)
        + 0.5*math.cos((pos+shift)*(k+2)*0.19+seed*0.007)
        for k in range(RANK)
    )


def _target(seed: int, i: int, j: int, allele: str) -> float:
    return sum(a*b for a, b in zip(_factor(seed, i, allele),
                                  _factor(seed, j, allele)))


def metadata(world):
    if world != SMOKE and world not in WORLDS:
        raise ValueError("unfrozen world")
    seed, kind, n = world
    gene = f"FABRICATED_WSP210_{seed}"
    out = defaultdict(list)
    for i, j in _pairs(kind, n):
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        stage = fit_stage(group) if bucket == "FIT" else None
        out[(bucket,stage)].append((i,j,group))
    if not all(out[("FIT",s)] for s in range(4)) or not out[("PUBLIC_DEV",None)]:
        raise ValueError("frozen split has empty FIT stage or PUBLIC_DEV")
    return gene, out


def _samples(seed, gene, groups):
    for i,j,group in groups:
        for alt in ("C","D"):
            yield Sample(f"{seed}_{i}_{j}_{alt}",group,
                         f"{gene}\0{i}\0A\0{alt}",
                         f"{gene}\0{j}\0A\0{alt}",
                         _target(seed,i,j,alt))


def _mse(rows, predict, mean, sd):
    return sum((predict(x.left,x.right)-(x.target-mean)/sd)**2
               for x in rows)/len(rows)


def _zero_score(rows, mean, sd):
    buckets=defaultdict(list)
    for x in rows:
        buckets[x.group].append(((x.target-mean)/sd)**2)
    return math.sqrt(sum(sum(v)/len(v) for v in buckets.values())/len(buckets))


class AdamRank4:
    """Conventional full-batch gradient learner on exactly the same rank4 loss."""

    def __init__(self, lam: float):
        if lam not in LAMBDAS:
            raise ValueError("unfrozen lambda")
        self.lam = lam
        self.stage = -1
        self.mean = None
        self.sd = None
        self.samples = []
        self.weights = {}
        self.history = []

    def predict(self, a, b):
        x = self.weights[a] if a in self.weights else core._initial(a, RANK)
        y = self.weights[b] if b in self.weights else core._initial(b, RANK)
        return sum(v*w for v,w in zip(x,y))

    def _loss_grad(self):
        grad = {a:[0.0]*RANK for a in self.weights}
        value=0.0
        for obs in self.samples:
            x,y=self.weights[obs.left],self.weights[obs.right]
            delta=sum(x[k]*y[k] for k in range(RANK))-(obs.target-self.mean)/self.sd
            value+=delta*delta
            for k in range(RANK):
                grad[obs.left][k]+=2*delta*y[k]
                grad[obs.right][k]+=2*delta*x[k]
        for a,w in self.weights.items():
            for k in range(RANK):
                value+=self.lam*w[k]*w[k]
                grad[a][k]+=2*self.lam*w[k]
        if not math.isfinite(value):
            raise ArithmeticError("nonfinite conventional objective")
        return value,grad

    def checkpoint(self):
        return json.dumps({
            "schema":"wsp210.adam-r4.v1", "lam":self.lam, "stage":self.stage,
            "mean":self.mean,"sd":self.sd,"weights":self.weights,
            "samples":[vars(x) for x in self.samples],"history":self.history,
            "source_digest":SYNTHETIC_DIGEST
        },sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

    @classmethod
    def cold(cls, data):
        value=json.loads(data)
        if value.get("schema")!="wsp210.adam-r4.v1" or value.get("source_digest")!=SYNTHETIC_DIGEST:
            raise ValueError("foreign Adam checkpoint")
        out=cls(value["lam"])
        out.stage=value["stage"]
        out.mean=value["mean"]
        out.sd=value["sd"]
        out.weights=value["weights"]
        out.samples=[Sample(**x) for x in value["samples"]]
        out.history=value["history"]
        if out.checkpoint()!=data:
            raise ValueError("Adam checkpoint noncanonical")
        return out

    def advance(self, stage, batch):
        if stage!=self.stage+1 or stage not in range(4) or not batch:
            raise ValueError("Adam stage invalid")
        new=sorted(batch,key=lambda s:s.sample_id)
        if len({x.sample_id for x in new})!=len(new) or any(
            x.sample_id in {y.sample_id for y in self.samples} for x in new):
            raise ValueError("Adam evidence replay")
        for x in new:
            x.validate(stage)
        if stage==0:
            self.mean=fmean(x.target for x in new)
            self.sd=math.sqrt(fmean((x.target-self.mean)**2 for x in new))
            if not math.isfinite(self.sd) or self.sd<=1e-12:
                raise ValueError("bad shared B0 scaling")
        for x in new:
            for addr in (x.left,x.right):
                if addr not in self.weights:
                    self.weights[addr]=core._initial(addr,RANK)
        self.samples.extend(new)
        m={a:[0.0]*RANK for a in self.weights}
        v={a:[0.0]*RANK for a in self.weights}
        start=time.perf_counter_ns()
        initial,_=self._loss_grad()
        old_window=initial
        last_loss=initial
        stable=False
        for epoch in range(1,ADAM_MAX+1):
            _,grads=self._loss_grad()
            bc1=1-.9**epoch
            bc2=1-.999**epoch
            for a in sorted(self.weights):
                for k,g in enumerate(grads[a]):
                    m[a][k]=.9*m[a][k]+.1*g
                    v[a][k]=.999*v[a][k]+.001*g*g
                    self.weights[a][k]-=ADAM_LR*(m[a][k]/bc1)/(math.sqrt(v[a][k]/bc2)+1e-8)
            if epoch%100==0:
                last_loss,_=self._loss_grad()
                if epoch>=ADAM_MIN:
                    change=abs(old_window-last_loss)/max(1.0,abs(old_window))
                    if change<=1e-6:
                        stable=True
                        break
                old_window=last_loss
        self.stage=stage
        self.history.append({"stage":stage,"epochs":epoch,"plateau":stable,
                             "objective":last_loss,
                             "elapsed_wall_ns":time.perf_counter_ns()-start})
        return self.history[-1]


def _classification(world_results):
    if len(world_results)!=4:
        return "INVALID"
    if any(not w["valid_conventional"] for w in world_results):
        return "INVALID"
    recovered=competitive=memorized=still_zero=0
    for w in world_results:
        hi=w["arms"]["10.0"]
        lo=w["arms"]["0.2"]
        baseline=w["zero_rmse"]
        r=lo["refit"]
        a=lo["adam"]
        c=lo["direct"]
        control=(r["b0_mse"][-1]<=.70*hi["refit"]["b0_mse"][-1] and
                 a["b0_mse"][-1]<=.70*hi["adam"]["b0_mse"][-1] and
                 r["held_rmse"]<=.90*baseline and a["held_rmse"]<=.90*baseline)
        if control:
            recovered+=1
            if (c["b0_mse"][-1]<=1.05*r["b0_mse"][-1] and
                c["held_rmse"]<=1.05*r["held_rmse"]):
                competitive+=1
        if r["b0_mse"][-1]<=.70*hi["refit"]["b0_mse"][-1] and r["held_rmse"]>.90*baseline:
            memorized+=1
        if (r["b0_mse"][-1]>.80*hi["refit"]["b0_mse"][-1] and
            a["b0_mse"][-1]>.80*hi["adam"]["b0_mse"][-1] and
            r["held_rmse"]>.95*baseline and a["held_rmse"]>.95*baseline):
            still_zero+=1
    if recovered>=3 and competitive>=3:return "REGULARIZATION_RECOVERS_ALL"
    if recovered>=3:return "REGULARIZATION_RECOVERS_CONTROLS_ONLY"
    if memorized>=3:return "LOW_LAMBDA_MEMORIZATION_ONLY"
    if still_zero>=3:return "PERSISTENT_LOW_LAMBDA_FAILURE"
    return "MIXED"


def run_world(world):
    gene,groups=metadata(world)
    seed=world[0]
    models={(lam,mode):Learner(SYNTHETIC_DIGEST,mode,RANK)
            for lam in LAMBDAS for mode in ("contradiction","full_refit")}
    adams={lam:AdamRank4(lam) for lam in LAMBDAS}
    no_update=Learner(SYNTHETIC_DIGEST,"no_update",RANK)
    traces={str(lam):{mode:{"b0_mse":[],"write_counts":[],"cost_wall_ns":[],
                          "checkpoint_sha256":[],"objective":[]} for mode in
                    ("direct","refit","adam")} for lam in LAMBDAS}
    first=None
    used=set()
    for stage in range(4):
        batch=list(_samples(seed,gene,groups[("FIT",stage)]))
        for s in batch:
            if s.sample_id in used:raise ValueError("FIT replay")
            used.add(s.sample_id)
        if stage==0:first=tuple(batch)
        for lam in LAMBDAS:
            data=traces[str(lam)]
            for mode,key in (("contradiction","direct"),("full_refit","refit")):
                model=models[(lam,mode)]
                with ridge_scope(lam):
                    start=time.perf_counter_ns()
                    receipt=model.advance(stage,batch)
                    objective=model._objective()
                    chk=model.checkpoint()
                    cold=Learner.restore(chk,SYNTHETIC_DIGEST)
                    wall=time.perf_counter_ns()-start
                if cold.checkpoint()!=chk or any(
                    cold.predict(x.left,x.right)!=model.predict(x.left,x.right) for x in first):
                    raise ValueError("factor cold restore mismatch")
                t=data[key]
                t["b0_mse"].append(_mse(first,model.predict,model.mean,model.sd))
                t["write_counts"].append(receipt["address_writes"])
                t["objective"].append(objective)
                t["cost_wall_ns"].append(wall)
                t["checkpoint_sha256"].append(hashlib.sha256(chk).hexdigest())
            am=adams[lam]
            hist=am.advance(stage,batch)
            chk=am.checkpoint()
            cold=AdamRank4.cold(chk)
            if any(cold.predict(x.left,x.right)!=am.predict(x.left,x.right) for x in first):
                raise ValueError("conventional cold restore mismatch")
            t=data["adam"]
            t["b0_mse"].append(_mse(first,am.predict,am.mean,am.sd))
            t["write_counts"].append(len(am.weights))
            t["objective"].append(hist["objective"])
            t["cost_wall_ns"].append(hist["elapsed_wall_ns"])
            t["checkpoint_sha256"].append(hashlib.sha256(chk).hexdigest())
        with ridge_scope(.2):
            no_update.advance(stage,batch)
    held=list(_samples(seed,gene,groups[("PUBLIC_DEV",None)]))
    held_groups={x.group for x in held}
    fit_groups={pair_group(gene,i,j) for k,v in groups.items() if k[0]=="FIT"
                for i,j,_ in v}
    if held_groups & fit_groups:
        raise ValueError("held-group leakage")
    for lam in LAMBDAS:
        data=traces[str(lam)]
        for mode,key in (("contradiction","direct"),("full_refit","refit")):
            mod=models[(lam,mode)]
            data[key]["held_rmse"]=group_weighted_rmse(
                held,mod.predict,mod.mean,mod.sd)
            data[key]["stage_convergence"]=mod.convergence
        am=adams[lam]
        data["adam"]["held_rmse"]=group_weighted_rmse(
            held,am.predict,am.mean,am.sd)
        data["adam"]["stage_convergence"]=am.history
    mean=models[(.2,"contradiction")].mean
    sd=models[(.2,"contradiction")].sd
    zero=_zero_score(held,mean,sd)
    # Privileged exact generator oracle is merely a ceiling, not matched.
    oracle=0.0
    return {
        "world":world, "b0_rows":len(first),"FIT_groups":len(fit_groups),
        "held_groups":len(held_groups),"zero_rmse":zero,
        "privileged_oracle_rmse":oracle,"oracle_equal_information":False,
        "reserved_labels_generated":False,
        "no_update_b0_mse_after_b3":_mse(first,no_update.predict,
                                         no_update.mean,no_update.sd),
        "valid_conventional":all(all(s["plateau"] for s in adams[lam].history)
                                   for lam in LAMBDAS),
        "arms":traces
    }


def run_primary():
    results=[run_world(w) for w in WORLDS]
    return {"schema":SCHEMA,"prereg_commit":PREREG_SHA,
            "classification":_classification(results),
            "source":"FABRICATED_ONLY_NO_ORIGINAL_GFP",
            "reserved_outcomes_accessed":False,
            "worlds":results}
