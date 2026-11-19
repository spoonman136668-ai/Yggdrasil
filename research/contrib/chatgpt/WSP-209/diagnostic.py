"""WSP-209: preregistered, independently fabricated update-suppression falsifier.

NO ORIGINAL GFP NUMERIC LABELS, no first-use or native Yggdrasil authority.
The fixed cohort and thresholds are frozen at prereg commit
da819cdc4f0883a71fd6e3c044e6a1489d69c893.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time

WSP200 = Path(__file__).resolve().parent.parent / "WSP-200"
sys.path.insert(0, str(WSP200))
from learner import Learner, Sample, pair_group, group_bucket, fit_stage
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse

WORLDS = ((20911, "hub"), (20912, "hub"),
          (20913, "complete"), (20914, "complete"))
ARMS = ("contradiction", "always", "full_refit", "no_update")
SCHEMA = "wsp209.synthetic-update-suppression.v1"


def _pairs(kind: str):
    if kind == "hub":
        return ([(1, j) for j in range(2, 73)] +
                [(j, j+1) for j in range(2, 71, 2)])
    if kind == "complete":
        return [(i, j) for i in range(1, 19)
                for j in range(i+1, 19)]
    raise ValueError("unfrozen graph topology")


def _latent(seed: int, position: int, allele: str):
    """Self-authored synthetic hidden rank4 ground truth; no donor knowledge."""
    if allele not in ("C", "D"):
        raise ValueError("unfrozen allele")
    shift = .75 if allele == "D" else 0.
    return tuple(math.sin((position+shift)*(axis+1)*.41 +
                          seed*.003) +
                 .6*math.cos((position+shift)*(axis+2)*.23 +
                             seed*.011) for axis in range(4))


def _label(seed: int, i: int, j: int, allele: str):
    x, y = _latent(seed, i, allele), _latent(seed, j, allele)
    return float(sum(a*b for a, b in zip(x, y)))


def metadata(seed: int, kind: str):
    if (seed,kind) not in WORLDS:
        raise ValueError("unfrozen world")
    gene = "FABRICATED_WSP209_" + str(seed)
    pairs = _pairs(kind)
    buckets = defaultdict(list)
    for i, j in pairs:
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        index = fit_stage(group) if bucket == "FIT" else None
        buckets[(bucket,index)].append((i,j,group))
    if any(not buckets[("FIT",k)] for k in range(4)):
        raise ValueError("empty frozen FIT batch")
    if not buckets[("PUBLIC_DEV",None)]:
        raise ValueError("empty frozen PUBLIC_DEV")
    for key in buckets:
        buckets[key].sort()
    return gene,buckets


def _samples(seed: int, gene: str, pairs, *, stage: int | None):
    for i, j, group in pairs:
        for allele in ("C", "D"):
            left = f"{gene}\0{i}\0A\0{allele}"
            right = f"{gene}\0{j}\0A\0{allele}"
            yield Sample(f"{seed}_{i}_{j}_{allele}",
                         group, left, right, _label(seed,i,j,allele))


def _mse(witnesses, model: Learner):
    if not witnesses or model.mean is None or model.sd is None:
        raise ValueError("no B0 evidence")
    return sum((model.predict(s.left,s.right) -
                (s.target-model.mean)/model.sd)**2 for s in witnesses)/len(witnesses)


def _zero_rmse(held, mean, sd):
    groups=defaultdict(list)
    for s in held:
        groups[s.group].append(((s.target-mean)/sd)**2)
    return math.sqrt(sum(sum(v)/len(v) for v in groups.values())/len(groups))


def run_world(seed: int, kind: str):
    gene, buckets = metadata(seed,kind)
    models = {name:Learner(SYNTHETIC_DIGEST,name) for name in ARMS}
    b0 = None
    receipt_ids = set()
    trace = {name:{"b0_mse":[], "write_counts":[], "solve_counts":[],
                   "stage_wall_ns":[], "checkpoint_sha256":[]}
             for name in ARMS}
    for stage in range(4):
        # Materialize FIT *only when its stage opens*. All held labels remain
        # uncomputed and RESERVED labels have no code path whatsoever.
        batch=list(_samples(seed,gene,buckets[("FIT",stage)],stage=stage))
        if any(s.sample_id in receipt_ids for s in batch):
            raise ValueError("duplicate staged evidence")
        receipt_ids.update(s.sample_id for s in batch)
        if stage==0:
            b0=tuple(batch)
        for name,model in models.items():
            start=time.perf_counter_ns()
            receipt=model.advance(stage,batch)
            checkpoint=model.checkpoint()
            restored=Learner.restore(checkpoint,SYNTHETIC_DIGEST)
            wall=time.perf_counter_ns()-start
            if checkpoint!=restored.checkpoint():
                raise ValueError("nonidentical cold restoration")
            for s in b0:
                if model.predict(s.left,s.right)!=restored.predict(s.left,s.right):
                    raise ValueError("function changed on cold restoration")
            if name=="full_refit" and not model.convergence[-1]["converged"]:
                raise ValueError("nonconverged conventional control")
            t=trace[name]
            t["b0_mse"].append(_mse(b0,model))
            t["write_counts"].append(receipt["address_writes"])
            t["solve_counts"].append(receipt["solves"])
            t["stage_wall_ns"].append(wall)
            t["checkpoint_sha256"].append(hashlib.sha256(checkpoint).hexdigest())
    # Crucially only after all model updates and checkpoints are frozen.
    held=list(_samples(seed,gene,buckets[("PUBLIC_DEV",None)],stage=None))
    fit_groups={s.group for s in b0}
    for stage in range(1,4):
        fit_groups.update(pair_group(gene,i,j)
                          for i,j,_ in buckets[("FIT",stage)])
    if fit_groups & {s.group for s in held}:
        raise ValueError("held group leakage")
    for name,model in models.items():
        t=trace[name]
        t["dev_group_rmse"]=group_weighted_rmse(
            held,model.predict,model.mean,model.sd)
        t["cost_wall_ms"]=round(sum(t["stage_wall_ns"])/1e6,3)
    candidate, refit, always=(trace[n] for n in ("contradiction","full_refit","always"))
    frac=lambda t: (t["b0_mse"][0]-t["b0_mse"][-1])/max(t["b0_mse"][0],1e-12)
    refit_gain=frac(refit)
    cand_gain=frac(candidate)
    writes_c=sum(candidate["write_counts"][1:])
    writes_a=sum(always["write_counts"][1:])
    return {
        "seed":seed,"topology":kind,
        "fit_groups":len(fit_groups),
        "public_dev_groups":len({s.group for s in held}),
        "reserved_labels_computed":False,
        "b0_fit_rows":len(b0),
        "world_model_count":len(models),
        "candidate_gain":cand_gain,"refit_gain":refit_gain,
        "candidate_to_always_write_ratio":writes_c/max(1,writes_a),
        "zero_rmse":_zero_rmse(held,models["contradiction"].mean,
                              models["contradiction"].sd),
        "trace":trace
    }


def classify(worlds):
    if len(worlds)!=4 or {(w["seed"],w["topology"]) for w in worlds}!=set(WORLDS):
        return "INVALID"
    suppressed=sum(w["refit_gain"]>=.20 and w["candidate_gain"]<.05
                   and w["candidate_to_always_write_ratio"]<=.10
                   for w in worlds)
    limited=sum(w["refit_gain"]<.20 and w["candidate_gain"]<.20
                for w in worlds)
    supported=sum(w["candidate_gain"]>=.20 and
                  w["trace"]["contradiction"]["b0_mse"][-1] <=
                      1.05*w["trace"]["full_refit"]["b0_mse"][-1] and
                  w["trace"]["contradiction"]["dev_group_rmse"] <=
                      1.02*w["trace"]["full_refit"]["dev_group_rmse"]
                  for w in worlds)
    if suppressed>=3: return "UPDATE_SUPPRESSION"
    if limited>=3: return "INFORMATION_LIMIT"
    if supported>=3: return "CANDIDATE_SUPPORTED_DEV"
    return "MIXED"


def evaluate():
    worlds=[run_world(seed,kind) for seed,kind in WORLDS]
    return {
        "schema":SCHEMA,
        "status":"SOURCE_FREE_DEVELOPMENT_ONLY_NO_SCIENTIFIC_PROMOTION",
        "prereg_commit":"da819cdc4f0883a71fd6e3c044e6a1489d69c893",
        "original_source_labels_accessed":False,
        "reserved_labels_accessed":False,
        "classification":classify(worlds),
        "worlds":worlds
    }


if __name__=="__main__":
    print("WSP209_FABRICATED_MECHANISM_RESULT="+json.dumps(evaluate(),sort_keys=True))
