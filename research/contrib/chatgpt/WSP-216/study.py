"""WSP-216 frozen paired delayed-intervention causal-credit experiment.

Synthetic only; no original data, external model inference, owner checkpoint or
native learner. Preregistration committed BEFORE this source at
3df95400fb43875c4e1856a9f0e1cbbadf44b54c.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time

SCHEMA = "wsp216.delayed-paired-credit.source-free.v1"
PREREG = "3df95400fb43875c4e1856a9f0e1cbbadf44b54c"
WORLDS = (21601, 21602, 21603, 21604)
STAGE_COUNT = 4
FIT_PER_STAGE = 32
HELD_COUNT = 64
OUTPUTS = 3
SLOTS = (0, 1)
ACTIONS = (1, 2, 3, 4)
POLICIES = ("credit", "full_mle", "last_action", "no_lag", "swap_lag")
SOURCE_DIGEST = hashlib.sha256(
    (SCHEMA + "|" + PREREG).encode("ascii")).hexdigest()


def _hash(seed, *parts):
    if seed not in WORLDS:
        raise ValueError("WSP216 world not in frozen cohort")
    blob = "\0".join(map(str, ("WSP216", seed, *parts))).encode("utf-8")
    return hashlib.sha256(blob).digest()


def _effect(seed, slot, action, output):
    # Hidden world law is only called by synthetic environment generator,
    # never by a fitted learner or a prediction method.
    if slot not in SLOTS or action not in (0, *ACTIONS) or output not in range(OUTPUTS):
        raise ValueError("invalid synthetic effect coordinate")
    if action == 0:
        return 0.0
    active_slot = _hash(seed, "hidden-active-slot")[0] % 2
    if slot != active_slot:
        return 0.0
    d = _hash(seed, "hidden-effect", slot, action, output)
    return (1 if d[1] % 2 else -1) * (1 + d[0] % 4) / 4.0


def _outcome(seed, phase, index, context, actions, branch, output):
    nuisance = (_hash(seed, "context", context, output)[0] % 7 - 3) / 4.0
    noise = (_hash(seed, "noise", phase, index, branch, output)[0] % 3 - 1) / 16.0
    return nuisance + noise + sum(
        _effect(seed, lag, action, output) for lag, action in enumerate(actions))


@dataclass(frozen=True)
class Episode:
    event_id: str
    context: int
    changed_lag: int
    changed_action: int
    t0_before: int
    t1_before: int
    t0_after: int
    t1_after: int
    reference: tuple[float, ...]
    treatment: tuple[float, ...]

    def contrast(self):
        return tuple(a - b for a, b in zip(self.treatment, self.reference))


def _episode(seed, phase, index):
    if phase not in ("FIT", "HELD") or index < 0:
        raise ValueError("bad episode phase/index")
    if phase == "FIT" and index >= FIT_PER_STAGE * STAGE_COUNT:
        raise ValueError("future or outside FIT episodes")
    if phase == "HELD" and index >= HELD_COUNT:
        raise ValueError("held episode outside sealed allocation")
    changed_lag = index % 2
    changed_action = (index // 2) % len(ACTIONS) + 1
    context = index % 8 if phase == "FIT" else 8 + index % 8
    if phase == "FIT":
        distractor = 1 + ((index // 8 + changed_action) % 4)
    else:
        distractor = 1 + ((3 * changed_action + context) % 4)
    reference_actions = (0, distractor) if changed_lag == 0 else (distractor, 0)
    treatment_actions = (changed_action, distractor) if changed_lag == 0 else (distractor, changed_action)
    reference = tuple(_outcome(seed, phase, index, context, reference_actions,
                               "reference", j) for j in range(OUTPUTS))
    treatment = tuple(_outcome(seed, phase, index, context, treatment_actions,
                               "treatment", j) for j in range(OUTPUTS))
    return Episode(f"WSP216/{seed}/{phase}/{index:04d}", context, changed_lag,
                   changed_action, *reference_actions, *treatment_actions,
                   reference, treatment)


def batch(seed, stage):
    if seed not in WORLDS or stage not in range(STAGE_COUNT):
        raise ValueError("unfrozen stage/world")
    return tuple(_episode(seed, "FIT", stage * FIT_PER_STAGE + n)
                 for n in range(FIT_PER_STAGE))


def held(seed, *, all_stages_finished=False):
    if not all_stages_finished:
        raise ValueError("WSP216 HELD first-use requires completed frozen FIT")
    return tuple(_episode(seed, "HELD", i) for i in range(HELD_COUNT))


def _canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _evidence_id(episodes):
    return hashlib.sha256(_canon([(x.event_id, x.context, x.changed_lag,
                                   x.changed_action, x.t0_before, x.t1_before,
                                   x.t0_after, x.t1_after,
                                   x.reference, x.treatment) for x in episodes])).hexdigest()


def _cell(policy, row):
    if policy in ("credit", "full_mle"):
        return f"{row.changed_lag}:{row.changed_action}"
    if policy == "swap_lag":
        return f"{1-row.changed_lag}:{row.changed_action}"
    if policy == "no_lag":
        return str(row.changed_action)
    if policy == "last_action":
        return str(row.t1_after)
    raise ValueError("unknown control mode")


def _read_cell(policy, row):
    if policy in ("credit", "full_mle", "swap_lag"):
        return f"{row.changed_lag}:{row.changed_action}"
    if policy == "no_lag":
        return str(row.changed_action)
    if policy == "last_action":
        return str(row.t1_after)
    raise ValueError("unknown predictor")


class LocalMemory:
    """Durable, bounded direct accumulators; no learned oracle or teacher."""

    def __init__(self, seed, policy="credit"):
        if seed not in WORLDS or policy not in POLICIES:
            raise ValueError("invalid source/policy")
        self.seed = seed
        self.policy = policy
        self.stage = -1
        self.counts = {}
        self.totals = {}
        self.fit_digest = SOURCE_DIGEST
        self.ops = 0
        self.history = []  # only full_mle retains complete paired FIT rows

    def predict(self, row):
        key = _read_cell(self.policy, row)
        n = self.counts.get(key, 0)
        return tuple(v / n for v in self.totals[key]) if n else (0.0,) * OUTPUTS

    def _add(self, key, contrast):
        count = self.counts.get(key, 0)
        old = self.totals.get(key, [0.0] * OUTPUTS)
        self.counts[key] = count + 1
        self.totals[key] = [old[i] + contrast[i] for i in range(OUTPUTS)]
        self.ops += OUTPUTS

    def checkpoint(self):
        state = {"schema": SCHEMA, "source_digest": SOURCE_DIGEST, "seed": self.seed,
                 "policy": self.policy, "stage": self.stage, "counts": self.counts,
                 "totals": self.totals, "fit_digest": self.fit_digest,
                 "ops": self.ops, "history": self.history}
        state["state_sha256"] = hashlib.sha256(_canon(state)).hexdigest()
        return _canon(state)

    @classmethod
    def restore(cls, payload, seed, policy):
        state = json.loads(payload)
        digest = state.pop("state_sha256", "")
        if (state.get("schema") != SCHEMA or
                state.get("source_digest") != SOURCE_DIGEST or
                state.get("seed") != seed or state.get("policy") != policy or
                digest != hashlib.sha256(_canon(state)).hexdigest()):
            raise ValueError("wrong source/policy or checkpoint corrupted")
        new = cls(seed, policy)
        new.stage = state["stage"]
        new.counts = state["counts"]
        new.totals = state["totals"]
        new.fit_digest = state["fit_digest"]
        new.ops = state["ops"]
        new.history = state["history"]
        if (new.stage not in range(-1, 4) or
                any(type(n) is not int or n < 1 for n in new.counts.values()) or
                new.counts.keys() != new.totals.keys() or
                any(len(v) != OUTPUTS or not all(map(math.isfinite, v))
                    for v in new.totals.values()) or
                (policy != "full_mle" and new.history) or
                new.checkpoint() != payload):
            raise ValueError("invalid noncanonical model snapshot")
        return new

    def advance(self, stage, episodes):
        if stage != self.stage + 1 or stage not in range(STAGE_COUNT):
            raise ValueError("cannot skip or replay stage")
        if len(episodes) != FIT_PER_STAGE or len({x.event_id for x in episodes}) != FIT_PER_STAGE:
            raise ValueError("missing/duplicate stage episodes")
        for i, x in enumerate(episodes):
            if x.event_id != f"WSP216/{self.seed}/FIT/{stage*FIT_PER_STAGE+i:04d}":
                raise ValueError("FIT episode source/order mismatch")
            if not all(math.isfinite(y) for y in (*x.reference, *x.treatment)):
                raise ValueError("nonfinite paired source evidence")
        prepared = type(self).restore(self.checkpoint(), self.seed, self.policy)
        digest = _evidence_id(episodes)
        prepared.fit_digest = hashlib.sha256(
            (prepared.fit_digest + "|" + digest).encode("ascii")).hexdigest()
        if self.policy == "full_mle":
            prepared.history.extend((x.changed_lag, x.changed_action,
                                     x.contrast()) for x in episodes)
            prepared.counts = {}
            prepared.totals = {}
            for lag, action, delta in prepared.history:
                prepared._add(f"{lag}:{action}", delta)
        else:
            for x in episodes:
                prepared._add(_cell(self.policy, x), x.contrast())
        prepared.stage = stage
        self.__dict__.update(prepared.__dict__)
        return {"stage": stage, "fit_episode_digest": digest,
                "cumulative_digest": self.fit_digest,
                "operations": self.ops,
                "count_total": sum(self.counts.values()),
                "checkpoint_sha256": hashlib.sha256(self.checkpoint()).hexdigest()}


def rmse(rows, fn):
    errors = [((x.contrast()[j] - fn(x)[j]) ** 2)
              for x in rows for j in range(OUTPUTS)]
    return math.sqrt(sum(errors) / len(errors))


def evaluate_world(seed):
    models = {p: LocalMemory(seed, p) for p in POLICIES}
    traces = {p: [] for p in POLICIES}
    first = None
    initial_rmse = None
    for stage in range(STAGE_COUNT):
        rows = batch(seed, stage)
        if stage == 0:
            first = rows
        receipt = _evidence_id(rows)
        for name, model in models.items():
            start = time.perf_counter_ns()
            step = model.advance(stage, rows)
            if step["fit_episode_digest"] != receipt:
                raise ValueError("matched source evidence violation")
            clone = LocalMemory.restore(model.checkpoint(), seed, name)
            if (clone.checkpoint() != model.checkpoint() or
                    any(clone.predict(x) != model.predict(x) for x in first)):
                raise ValueError("functional cold checkpoint retention failed")
            r = rmse(first, model.predict)
            traces[name].append({"stage": stage, "b0_historical_rmse": r,
                                 "cumulative_writes": step["count_total"],
                                 "cumulative_scalar_ops": step["operations"],
                                 "fit_source_digest": step["cumulative_digest"],
                                 "checkpoint_sha256": step["checkpoint_sha256"],
                                 "wall_ns": time.perf_counter_ns() - start})
        if stage == 0:
            initial_rmse = traces["credit"][0]["b0_historical_rmse"]
        if len({models[p].fit_digest for p in POLICIES}) != 1:
            raise ValueError("source knowledge mismatch")
    # All stages are complete; held targets have NOT been created before now.
    evaluation = held(seed, all_stages_finished=all(
        m.stage == 3 for m in models.values()))
    if {x.event_id for x in evaluation} & {
        f"WSP216/{seed}/FIT/{n:04d}" for n in range(FIT_PER_STAGE * STAGE_COUNT)
    }:
        raise ValueError("held/FIT contamination")
    metrics = {p: {"held_rmse": rmse(evaluation, models[p].predict),
                   "b3_b0_rmse": traces[p][-1]["b0_historical_rmse"],
                   "cumulative_scalar_ops": models[p].ops,
                   "model_weight_cells": len(models[p].counts)}
               for p in POLICIES}
    zero_rmse = rmse(evaluation, lambda row: (0.0,)*OUTPUTS)
    credit = metrics["credit"]
    mle = metrics["full_mle"]
    supported = bool(
        credit["held_rmse"] <= max(1.02*mle["held_rmse"], mle["held_rmse"]+1e-10) and
        credit["held_rmse"] <= .75*metrics["last_action"]["held_rmse"] and
        credit["held_rmse"] <= .75*metrics["no_lag"]["held_rmse"] and
        credit["held_rmse"] <= .75*zero_rmse and
        credit["b3_b0_rmse"] <= max(1.5*initial_rmse, .1) and
        all(models["credit"].counts.get(f"{lag}:{action}", 0) >= 4
            for lag in SLOTS for action in ACTIONS))
    if not all(math.isfinite(x["held_rmse"]) for x in metrics.values()):
        raise ValueError("nonfinite evaluated metric")
    return {"world": seed, "status": "VALID", "stages_completed": 4,
            "fit_rows": FIT_PER_STAGE * STAGE_COUNT, "held_rows": HELD_COUNT,
            "held_source_sha256": _evidence_id(evaluation),
            "fit_source_sha256": models["credit"].fit_digest,
            "metrics": metrics, "traces": traces,
            "zero_held_rmse": zero_rmse, "b0_initial_rmse": initial_rmse,
            "credit_supported": supported, "source_original_accessed": False,
            "reserved_accessed": False}


def run_primary():
    worlds = [evaluate_world(seed) for seed in WORLDS]
    result = ("INVALID" if any(w["status"] != "VALID" for w in worlds)
              else "CREDIT_SUPPORTED" if sum(w["credit_supported"] for w in worlds) >= 3
              else "NO_GAIN")
    return {"schema": SCHEMA, "prereg": PREREG, "status": result,
            "worlds": worlds, "native_amalgam_accessed": False,
            "original_gfp_accessed": False, "reserved_accessed": False,
            "prior_cohorts_reused": False, "research_only": True}


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--output", required=True)
    cfg = a.parse_args()
    result = run_primary()
    Path(cfg.output).write_text(json.dumps(result, sort_keys=True, indent=2,
                                           allow_nan=False)+"\n", encoding="utf-8")
    print("WSP216_CLASSIFICATION="+result["status"])
    for w in result["worlds"]:
        print("WSP216_WORLD="+str(w["world"])+" STATUS="+w["status"]+
              " CREDIT_SUPPORTED="+str(w["credit_supported"])+
              " CREDIT_RMSE="+str(w["metrics"]["credit"]["held_rmse"])+
              " CONVENTIONAL_RMSE="+str(w["metrics"]["full_mle"]["held_rmse"]))
