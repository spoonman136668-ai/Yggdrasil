"""Frozen comparison of local and shared public evidence on crossed shifts."""

from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
import resource
import sys
from time import monotonic, process_time

from external_receipt_preflight import anchor_material
from local_evidence_readout import EvidenceReadout
from selection_trial import source_module
from shadow_preflight import checked_bytes, require
from staged_retention import Controls, keys, SCALE
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import experience_packet_sha256


HERE = Path(__file__).resolve().parent
PLAN = HERE / "local-evidence-dev-02" / "prereg.json"


def evidence(source, plan, seed, split, shift, size):
    cohort = f"{plan['id']}-{split}"
    for index in range(size):
        context, action = divmod(index % 4, 2)
        second = (index // 4) % 2
        for attempt in range(64):
            episode = source.make_episode(cohort=cohort, seed=seed, index=64 * index + attempt,
                                          family="invariant", regime=0)
            if episode.s1 == context:
                break
        else:
            raise RuntimeError("Could not draw the scheduled public context")
        views = source.public_views(episode)
        state = episode.transition(action) ^ int(index % 4 in shift)
        row = dict(s1=context, x1=action, s2=state, x2=second,
                   y=episode._reward(action, state, second))
        yield [digest(canonical([cohort, seed, index])), views, row]


def forecasts(read, view, row):
    first, state, second = (row[k] for k in ("x1", "s2", "x2"))
    return read(view, first), read(view, first, state, second)


def bounded_forecasts(model):
    @lru_cache(maxsize=None)
    def read(view, *public):
        probability = model.native.experience_context_forecast(view, *public)
        return Fraction(round(probability * SCALE), SCALE)
    return read


def replicate(parent, material, source, plan, source_pin, seed, deadline):
    base = parent.native._episode_reader()._ledger
    fit = list(evidence(source, plan, seed, "fit", (0, 3), plan["fit_per_seed"]))
    control = Controls()
    for _, views, first, state, second, reward in base:
        control.observe(views, dict(x1=first, s2=state, x2=second, y=reward))
    candidate = parent
    for identifier, views, row in fit:
        require(monotonic() < deadline, "CELL_LOCAL_WALL_BUDGET")
        candidate = candidate.observe_experience(
            identifier, views, row, source_sha256=source_pin, external_source_sha256=source_pin,
            packet_sha256=experience_packet_sha256(source_pin, identifier, views, row),
        )
        control.observe(views, row)
    raw = candidate.checkpoint()
    restored = NativeCausalAmalgam.restore(raw, digest(raw), external_source_sha256=source_pin,
                                           **material)
    ledger = restored.native._episode_reader()._ledger
    require(ledger[:len(base)] == base and len(ledger) == len(base) + len(fit),
            "CELL_LOCAL_PREFIX")
    steps = [b.steps - a.steps for a, b in zip(parent._heads, restored._heads, strict=True)]
    require(steps == [3 * len(fit)] * 4, "CELL_LOCAL_HEAD_UPDATES")
    old = bounded_forecasts(parent)
    new = bounded_forecasts(restored)
    trace = {"fit": fit}
    initial_ids = {row[0] for row in base}
    evaluations = []
    for index, shift in enumerate(plan["shifts"]):
        baseline = deepcopy(control)
        local = EvidenceReadout(old, new, local=True)
        shared = EvidenceReadout(old, new, local=False)
        for phase, active in (("shift", shift), ("return", [])):
            block = f"{index}-{phase}"
            prefix = list(evidence(source, plan, seed, f"{block}-prefix", active,
                                   plan["prefix_per_phase"]))
            held = list(evidence(source, plan, seed, f"{block}-score", active,
                                 plan["scored_per_phase"]))
            trace[f"{block}-prefix"] = prefix
            trace[f"{block}-score"] = held
            for _, views, row in prefix:
                public = views[0], row["x1"], row["s2"], row["x2"], row["y"]
                local.observe(*public)
                shared.observe(*public)
                baseline.observe(views, row)
            totals = defaultdict(lambda: [0, Fraction(0), Fraction(0)])
            for _, views, row in held:
                require(monotonic() < deadline, "CELL_LOCAL_WALL_BUDGET")
                values = [forecasts(read, views[0], row)
                          for read in (old, new, shared.forecast, local.forecast)]
                values.extend(zip(*(baseline.forecast(key) for key, _ in keys(views, row)),
                                  strict=True))
                cell = 2 * row["s1"] + row["x1"]
                for arm, (transition, reward) in zip(plan["arms"], values, strict=True):
                    total = totals[cell, arm]
                    total[0] += 1
                    total[1] += (round(transition * SCALE) - row["s2"] * SCALE) ** 2
                    total[2] += (round(reward * SCALE) - row["y"] * SCALE) ** 2
            evaluations.append(dict(phase=phase, shifted_cells=active, cells=[
                {arm: [float(err / (n * SCALE**2)) for err in errors]
                 for arm in plan["arms"] for n, *errors in [totals[cell, arm]]}
                for cell in range(4)]))
    ids = [row[0] for rows in trace.values() for row in rows]
    require(len(ids) == len(set(ids)) and not (initial_ids & set(ids)), "CELL_LOCAL_TRACE_JOIN")
    return dict(seed=seed, actions=2 * len(ids), fit_episodes=len(fit), head_steps=steps,
                checkpoint=digest(raw), native_checkpoint=digest(restored.native.checkpoint()),
                trace_sha256=digest(canonical(trace)), evaluations=evaluations)


def run(inputs):
    wall, cpu = monotonic(), process_time()
    raw = PLAN.read_bytes()
    plan = json.loads(raw)
    proof, material = anchor_material(inputs)
    anchor = checked_bytes(inputs / proof["joint_name"], plan["parent_joint_sha256"])
    model = NativeCausalAmalgam.restore(anchor, plan["parent_joint_sha256"], **material)
    source = source_module(plan["source_sha256"])
    # The source contract binds evaluator code, frozen roster and original generator.
    source_pin = digest(canonical([digest(raw), digest(Path(__file__).read_bytes()),
                                   plan["source_sha256"]]))
    replicas = [replicate(model, material, source, plan, source_pin, seed,
                          wall + plan["wall_budget_seconds"]) for seed in plan["seeds"]]
    gains, retained = [], []
    for item in replicas:
        changed, unchanged = [], []
        for evaluation in item["evaluations"]:
            for cell, loss in enumerate(evaluation["cells"]):
                (changed if cell in evaluation["shifted_cells"] else unchanged).append(loss)
        mean_losses = {arm: sum(row[arm][0] for row in changed) / len(changed)
                       for arm in plan["arms"]}
        gains.append(min(score for arm, score in mean_losses.items() if arm != "local")
                     - mean_losses["local"])
        retained.append(max(new - old for row in unchanged for new, old in
                            zip(row["local"], row["anchor"], strict=True)))
    success = (sum(gains) / len(gains) >= plan["min_transition_gain"] and
               all(drift <= plan["max_retention_drift"] for drift in retained))
    return dict(verdict="DEV_SIGNAL" if success else "DEV_NO_GO",
                gain_vs_strongest_by_seed=gains, max_unchanged_drift_by_seed=retained,
                replicas=replicas, parent=plan["parent_joint_sha256"], source_pin=source_pin,
                wall_seconds=monotonic() - wall, cpu_seconds=process_time() - cpu,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
