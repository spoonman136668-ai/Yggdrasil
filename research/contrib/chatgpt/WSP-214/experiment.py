"""WSP-214: preregistered gate-admission diagnostic and fixed-budget controls.

SYNTHETIC SOURCE-FREE ONLY. This code has no original GFP loader, no native
checkpoint, no owner, and no use of the retired WSP210--WSP213 cohorts.
Pre-result preregistration SHA 905cbef5df7d1cace00231ea4bcd079c0780a1ef.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import fmean
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / "WSP-200"))
from learner import (Learner, Sample, pair_group, group_bucket, fit_stage,
                     VERSION as CORE_SCHEMA)
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse

# Reuse source-exact WSP213 helper module by private name. Do not modify its
# frozen cohort or run its primary; only import helper definitions/classes.
_spec = importlib.util.spec_from_file_location(
    "wsp213_inherited_helpers_for_214", BASE / "WSP-213" / "study.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("inherited exact-source comparator unavailable")
_previous = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_previous)
_pairs = _previous._pairs
_mse = _previous._mse
_zero_score = _previous._zero_score
_digest = _previous._digest
ridge_scope = _previous.ridge_scope
BlockedFullRefit = _previous.BlockedFullRefit

SCHEMA = "wsp214.gate-admission.source-free.v1"
PREREG = "905cbef5df7d1cace00231ea4bcd079c0780a1ef"
WORLDS = ((21401, "hub", 24), (21402, "complete", 12),
          (21403, "hub", 24), (21404, "complete", 12))
FORBIDDEN = frozenset((21011, 21012, 21013, 21014, 21101, 21102,
                       21201, 21202, 21203, 21204,
                       21301, 21302, 21303, 21304))
POLICY_SCHEMA = "wsp214.policy-bound-gate.v1"
MODELS = ("full_refit", "strict_original", "budgeted_consensus",
          "budgeted_surprise", "budgeted_random", "always", "no_update")
RIDGE = 0.2
RANK = 4


def metadata(world):
    if world not in WORLDS or world[0] in FORBIDDEN:
        raise ValueError("world is not frozen WSP214 new synthetic primary")
    seed, topology, n = world
    gene = f"FABRICATED_WSP214_{seed}"
    groups = defaultdict(list)
    for i, j in _pairs(topology, n):
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        if bucket == "FIT":
            groups[(bucket, fit_stage(group))].append((i, j, group))
        elif bucket == "PUBLIC_DEV":
            groups[(bucket, None)].append((i, j, group))
    if any(not groups[("FIT", s)] for s in range(4)):
        raise ValueError("one or more frozen FIT stages empty")
    if not groups[("PUBLIC_DEV", None)]:
        raise ValueError("frozen whole-group held set empty")
    return gene, groups


def _factor(seed, alt, pos, k):
    if seed not in {x[0] for x in WORLDS} or alt not in ("C", "D") or pos < 1 or k not in range(RANK):
        raise ValueError("source-free factor source not allowlisted")
    key = f"WSP214\0{seed}\0{alt}\0{pos}\0{k}".encode("utf-8")
    return hashlib.sha256(key).digest()[0] % 7 - 3


def _target(seed, i, j, alt):
    return sum(_factor(seed, alt, i, k)*_factor(seed, alt, j, k)
               for k in range(RANK))/9.0


def _samples(seed, gene, pairs):
    for i, j, g in pairs:
        for alt in ("C", "D"):
            yield Sample(f"{seed}_{i}_{j}_{alt}", g,
                         f"{gene}\0{i}\0A\0{alt}",
                         f"{gene}\0{j}\0A\0{alt}", _target(seed, i, j, alt))


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _sha(obj):
    return hashlib.sha256(_canonical(obj)).hexdigest()


def gate_inputs(model, batch):
    """Read only newly seen FIT observations before current-stage writes.

    Return coverage partition and per-address ranking evidence. This does not
    inspect an oracle or heldout target, or train a model.
    """
    if model.sd is None or model.mean is None:
        raise ValueError("gate cannot use unnormalized model")
    addresses = {s.left for s in batch} | {s.right for s in batch}
    by_addr = {a: [] for a in addresses}
    for s in batch:
        r = (s.target-model.mean)/model.sd-model.predict(s.left, s.right)
        for a in (s.left, s.right):
            by_addr[a].append((s.sample_id, r))
    eligible = []
    sign_only = mean_only = both = 0
    for address in sorted(addresses):
        evidence = by_addr[address]
        if len({x for x, _ in evidence}) < 2:
            continue
        errs = [v for _, v in evidence]
        nz = [v for v in errs if v != 0]
        agreement = (max(sum(v > 0 for v in nz), sum(v < 0 for v in nz)) /
                     len(nz)) if nz else 0.0
        signed_mean = fmean(errs)
        abs_mean = fmean(map(abs, errs))
        sign_ok = bool(nz) and agreement >= .75
        mean_ok = abs(signed_mean) >= 1
        sign_only += int(sign_ok)
        mean_only += int(mean_ok)
        both += int(sign_ok and mean_ok)
        eligible.append((address, agreement, signed_mean, abs_mean))
    budget = (len(addresses)+3)//4
    k = min(budget, len(eligible))
    return {
        "new_addresses": len(addresses), "eligible": len(eligible),
        "sign_pass": sign_only, "mean_pass": mean_only,
        "both_pass": both, "quarter_budget": budget, "k": k
    }, eligible


class PolicyBoundGate(Learner):
    """Same WSP200 normal equations; policy is stored in checkpoint domain.

    Different policies MUST NOT be cross-restorable. Source, rank, B0 full
    training, B1..B3 two-sweep update, and evidence validation are unchanged.
    """
    POLICY = None

    def __init__(self, source_digest, mode="always", rank=4):
        if mode != "always" or rank != 4 or self.POLICY not in (
                "consensus", "surprise", "random"):
            raise ValueError("wrong policy gate mode/rank")
        super().__init__(source_digest, mode, rank)

    def checkpoint(self):
        state = json.loads(super().checkpoint())
        state.pop("state_sha256")
        state["schema"] = POLICY_SCHEMA
        state["wsp214_policy"] = self.POLICY
        state["state_sha256"] = _sha(state)
        return _canonical(state)

    @classmethod
    def restore(cls, data, expected_source_digest):
        state = json.loads(data)
        checksum = state.pop("state_sha256", None)
        if (state.get("schema") != POLICY_SCHEMA or
                state.get("wsp214_policy") != cls.POLICY or
                state.get("source_digest") != expected_source_digest or
                checksum != _sha(state)):
            raise ValueError("invalid / wrong-policy WSP214 checkpoint")
        state["schema"] = CORE_SCHEMA
        del state["wsp214_policy"]
        state["state_sha256"] = _sha(state)
        original = Learner.restore(_canonical(state), expected_source_digest)
        restored = cls(expected_source_digest, original.mode, original.rank)
        restored.__dict__.update(original.__dict__)
        if restored.checkpoint() != data:
            raise ValueError("noncanonical policy-bound cold checkpoint")
        return restored

    def _choose(self, new, stage, reference_write_count):
        if reference_write_count is not None or stage == 0:
            raise ValueError("budget policy cannot override count or B0")
        stats, eligible = gate_inputs(self, new)
        k = stats["k"]
        if self.POLICY == "consensus":
            ordered = sorted(eligible, key=lambda e:
                             (-e[1], -abs(e[2]), -e[3], e[0].encode("utf-8")))
        elif self.POLICY == "surprise":
            ordered = sorted(eligible, key=lambda e: (-e[3], e[0].encode("utf-8")))
        else:
            ordered = sorted(eligible, key=lambda e: (
                hashlib.sha256(
                    f"WSP214-RANDOM-v1\0{stage}\0{e[0]}".encode("utf-8")
                ).digest(), e[0].encode("utf-8")))
        selected = {e[0] for e in ordered[:k]}
        if len(selected) != k:
            raise ValueError("bad eligible budget")
        return selected


class ConsensusGate(PolicyBoundGate):
    POLICY = "consensus"


class SurpriseGate(PolicyBoundGate):
    POLICY = "surprise"


class RandomGate(PolicyBoundGate):
    POLICY = "random"


def _cold_check(model, first):
    checkpoint = model.checkpoint()
    restored = type(model).restore(checkpoint, SYNTHETIC_DIGEST)
    if (restored.checkpoint() != checkpoint or
            any(restored.predict(s.left, s.right) !=
                model.predict(s.left, s.right) for s in first)):
        raise ValueError("cold restore function or bytes changed")
    return hashlib.sha256(checkpoint).hexdigest()


def run_world(world):
    gene, groups = metadata(world)
    models = {
        "full_refit": BlockedFullRefit(SYNTHETIC_DIGEST, "full_refit", RANK),
        "strict_original": Learner(SYNTHETIC_DIGEST, "contradiction", RANK),
        "budgeted_consensus": ConsensusGate(SYNTHETIC_DIGEST),
        "budgeted_surprise": SurpriseGate(SYNTHETIC_DIGEST),
        "budgeted_random": RandomGate(SYNTHETIC_DIGEST),
        "always": Learner(SYNTHETIC_DIGEST, "always", RANK),
        "no_update": Learner(SYNTHETIC_DIGEST, "no_update", RANK)
    }
    first = None
    used_ids = set()
    fit_groups = set()
    trajectories = {m: [] for m in MODELS}
    diagnosis = []
    for stage in range(4):
        batch = sorted(_samples(world[0], gene, groups[("FIT", stage)]),
                       key=lambda s: s.sample_id)
        if stage == 0:
            first = tuple(batch)
        ids = {s.sample_id for s in batch}
        new_groups = {s.group for s in batch}
        if len(ids) != len(batch) or ids & used_ids or new_groups & fit_groups:
            raise ValueError("FIT evidence replay")
        used_ids.update(ids)
        fit_groups.update(new_groups)
        if stage:
            strict = models["strict_original"]
            with ridge_scope(RIDGE):
                counts, _ = gate_inputs(strict, batch)
                original_selected = strict._choose(batch, stage, None)
            counts["stage"] = stage
            counts["strict_selected"] = len(original_selected)
            if counts["strict_selected"] != min(counts["both_pass"],counts["quarter_budget"]):
                raise AssertionError("original gate count different from diagnostic")
            diagnosis.append(counts)
        for name in MODELS:
            model = models[name]
            before = model.solves
            start = time.perf_counter_ns()
            try:
                with ridge_scope(RIDGE):
                    receipt = model.advance(stage, batch)
                    objective = model._objective()
                    sha = _cold_check(model, first)
            except ArithmeticError as err:
                if name != "full_refit":
                    raise
                return {"world": world, "status": "INVALID",
                        "reason": "unconverged qualified control: " + str(err),
                        "stages_completed": stage, "diagnostics": diagnosis,
                        "original_source_accessed": False,
                        "reserved_labels_generated": False}
            elapsed = time.perf_counter_ns()-start
            solves = model.solves - before
            if name == "full_refit":
                cv = model.convergence[-1]
                if (not cv["converged"] or
                        solves != len(model.weights)*8*cv["sweeps"] or
                        cv["sweeps"] > 100):
                    raise AssertionError("qualified refit convergence mismatch")
            if stage and name.startswith("budgeted_"):
                if receipt["address_writes"] != diagnosis[-1]["k"] or solves != 2*diagnosis[-1]["k"]:
                    raise AssertionError("matched budget or solve count differs")
            if not math.isfinite(objective):
                raise ArithmeticError("nonfinite objective")
            retention = _mse(first, model.predict, model.mean, model.sd)
            if not math.isfinite(retention):
                raise ArithmeticError("nonfinite B0 retention")
            trajectories[name].append({
                "stage":stage, "new_rows":len(batch),
                "cumulative_rows":len(model.samples),
                "address_writes":receipt["address_writes"],
                "coordinate_solves":solves, "objective":objective,
                "b0_mse":retention, "source_sha256":_digest(model.samples),
                "checkpoint_sha256":sha, "wall_ns":elapsed
            })
        if len({_digest(models[name].samples) for name in MODELS}) != 1:
            raise ValueError("arms received unequal FIT samples")
        if len({(models[name].mean,models[name].sd) for name in MODELS}) != 1:
            raise ValueError("arms have different B0 scaler")
    # Unseen whole-pair held labels produced only once after B3.
    held = list(_samples(world[0], gene, groups[("PUBLIC_DEV", None)]))
    if fit_groups & {s.group for s in held}:
        raise ValueError("held FIT pair-group leakage")
    scores = {}
    for name in MODELS:
        score = group_weighted_rmse(
            held, models[name].predict, models[name].mean, models[name].sd)
        if not math.isfinite(score):
            raise ArithmeticError("nonfinite held score")
        scores[name] = {
            "held_rmse":score, "b3_b0_mse":trajectories[name][-1]["b0_mse"],
            "total_coordinate_solves":sum(x["coordinate_solves"] for x in trajectories[name]),
            "total_address_writes":sum(x["address_writes"] for x in trajectories[name]),
            "total_wall_ns":sum(x["wall_ns"] for x in trajectories[name])
        }
    zero = _zero_score(held, models["full_refit"].mean,models["full_refit"].sd)
    c = scores["budgeted_consensus"]
    strict = scores["strict_original"]
    refit = scores["full_refit"]
    best = min(scores["budgeted_surprise"]["held_rmse"],
               scores["budgeted_random"]["held_rmse"])
    consensus_better_strict = c["held_rmse"] <= 0.90*strict["held_rmse"]
    strong_gain = (
        consensus_better_strict and
        c["held_rmse"] <= 0.95*refit["held_rmse"] and
        c["held_rmse"] <= 0.95*best and
        c["b3_b0_mse"] <= 1.05*refit["b3_b0_mse"] and
        c["total_coordinate_solves"] < refit["total_coordinate_solves"])
    return {"world":world, "status":"VALID", "stages_completed":4,
            "held_groups":len({s.group for s in held}),
            "fit_groups":len(fit_groups),
            "fit_source_sha256":_digest(models["full_refit"].samples),
            "held_source_sha256":_digest(held),
            "diagnostics":diagnosis, "trace":trajectories, "scores":scores,
            "zero_held_rmse":zero,
            "consensus_better_strict":consensus_better_strict,
            "strong_gain":strong_gain,
            "original_source_accessed":False, "reserved_labels_generated":False}


def classify(worlds):
    if len(worlds) != 4 or any(w.get("status") != "VALID" for w in worlds):
        return "INVALID"
    low = sum(d["k"] > 0 and
              d["strict_selected"] <= d["k"]//2
              for w in worlds for d in w["diagnostics"])
    recovered = sum(w["consensus_better_strict"] for w in worlds)
    strong = sum(w["strong_gain"] for w in worlds)
    if strong >= 3:
        return "GATE_ADVANTAGE"
    if low >= 8 and recovered >= 3:
        return "LOW_ADMISSION_DIAGNOSTIC"
    if low >= 8:
        return "UNDERSELECTION_OBSERVED"
    return "NO_GAIN"


def run_primary():
    worlds = [run_world(w) for w in WORLDS]
    return {"schema":SCHEMA,"prereg_commit":PREREG,
            "classification":classify(worlds),"worlds":worlds,
            "retired_cohorts_reused":False,
            "original_gfp_labels_accessed":False,
            "reserved_labels_accessed":False,
            "native_amalgam_accessed":False,"research_only":True}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = run_primary()
    Path(args.output).write_text(json.dumps(result,sort_keys=True,
        indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("WSP214_CLASSIFICATION="+result["classification"])
    for w in result["worlds"]:
        print("WSP214_WORLD="+str(w["world"])+" STATUS="+w["status"]+
              " GAIN="+str(w.get("strong_gain",False))+
              " RECOVER="+str(w.get("consensus_better_strict",False))+
              " STRICT_WRITES="+str(sum(d["strict_selected"] for d in w["diagnostics"]))+
              " SOFT_BUDGET="+str(sum(d["k"] for d in w["diagnostics"])))
