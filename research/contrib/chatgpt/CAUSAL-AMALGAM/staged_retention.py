"""Forecast, train, and validate reversible readouts from the CKAD26 lineage."""

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import monotonic, process_time

from retention_guard import evaluate
from selection_trial import SCALE, TransitionControls, restore, source_module
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve().parent
ARMS = ("pinned", "unguarded", "guarded", "fit_full", "fit_trailing", "fit_change_point")


class Controls:
    """Fully fit conditional Beta and online abrupt-change controls."""

    def __init__(self):
        self.full = defaultdict(lambda: [0, 0])
        self.online = TransitionControls(32, 1 / 32)

    def observe(self, views, row):
        for key, outcome in keys(views, row):
            self.full[key][outcome] += 1
            self.online.update(key, outcome)

    def forecast(self, key):
        zero, one = self.full[key]
        return ((one + 0.5) / (zero + one + 1), *self.online.forecast(key))


def keys(views, row):
    view = views[0]
    first, state, second, reward = (row[k] for k in ("x1", "s2", "x2", "y"))
    return (((view[0], first), state), ((view[0], first, state, second), reward))


def row_scores(views, row, systems, controls):
    view = views[0]
    first, state, second, reward = (row[k] for k in ("x1", "s2", "x2", "y"))
    probabilities = {}
    for name, system in zip(ARMS[:3], systems, strict=True):
        prediction = system.native.experience_context_forecast
        probabilities[name] = prediction(view, first), prediction(view, first, state, second)
    control_predictions = [controls.forecast(key) for key, _ in keys(views, row)]
    probabilities.update(zip(ARMS[3:], zip(*control_predictions, strict=True), strict=True))
    forecasts = {name: [round(p * SCALE) for p in pair] for name, pair in probabilities.items()}
    truth = state * SCALE, reward * SCALE
    return forecasts, {
        name: [(point - outcome)**2 for point, outcome in zip(pair, truth, strict=True)]
        for name, pair in forecasts.items()
    }


def scores(cases, systems, controls):
    totals = {arm: [0, 0] for arm in ARMS}
    for views, row in cases:
        _, result = row_scores(views, row, systems, controls)
        for arm, pair in result.items():
            for target, squared_error in enumerate(pair):
                totals[arm][target] += squared_error
    scale = len(cases) * SCALE**2
    return {arm: [Fraction(value, scale) for value in pair] for arm, pair in totals.items()}


def encode(losses):
    return {arm: [float(value) for value in pair] for arm, pair in losses.items()}


def cases(source, cohort, seed, phase, count):
    """Keep structural parameters and hidden draws in the evaluator."""
    for index in range(count):
        episode = source.make_episode(cohort=cohort, seed=seed, index=index,
                                      family=phase["family"], regime=phase["regime"])
        views = source.public_views(episode)
        first, second = index % 2, (index // 2) % 2
        commanded = first ^ phase["swap"]
        state = episode.transition(commanded)
        if phase["mask_by_context"]:
            state ^= commanded & views[0][0]
        reward = episode._reward(commanded, state, second)
        yield views, dict(s1=views[0][0], x1=first, s2=state, x2=second, y=reward)


def average(losses):
    return sum(losses) / len(losses)


def admit(system, identifier, views, row):
    return system.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=digest(canonical([identifier, views, row])),
    )


def compare_replica(seed, anchor, source, plan, output):
    wall, cpu = monotonic(), process_time()
    base = anchor.native._episode_reader()._ledger
    prospect = selected = anchor
    selected_stage = 0
    control = Controls()
    for _, views, first, state, second, reward in base:
        control.observe(views, dict(x1=first, s2=state, x2=second, y=reward))
    traces, decisions = [], []
    tolerance = Fraction(plan["max_brier_drift"])
    margin = Fraction(plan["min_novel_gain"])
    probe_count = plan["probe_count"]
    familiar = plan["familiar"]
    fixed_validation = list(cases(source, plan["id"] + "-old-val", seed, familiar, probe_count))
    fixed_report = list(cases(source, plan["id"] + "-old-report", seed, familiar, probe_count))
    for stage, phase in enumerate(plan["phases"], 1):
        name = plan["id"] + "-" + phase["name"]
        before_count = len(prospect.native._episode_reader()._ledger)
        for index, (views, row) in enumerate(cases(source, name + "-train", seed, phase, phase["n"])):
            if monotonic() - wall > plan["wall_seconds_per_seed"]:
                raise TimeoutError("Replica reached its frozen wall cap")
            identifier = digest(canonical([name, seed, index]))
            forecast, _ = row_scores(views, row, (anchor, prospect, selected), control)
            traces.append(dict(stage=stage, id=identifier, views=views, row=row, forecast=forecast))
            prospect = admit(prospect, identifier, views, row)
            control.observe(views, row)
        if len(prospect.native._episode_reader()._ledger) != before_count + phase["n"]:
            raise RuntimeError("Witness accounting mismatch")
        preselection = (anchor, prospect, selected)
        history = evaluate(anchor, prospect, plan["historical_windows"], max_brier_drift=tolerance)
        old_validation = scores(fixed_validation, preselection, control)
        new_validation = scores(
            list(cases(source, name + "-new-val", seed, phase, probe_count)),
            preselection, control,
        )
        predicates = {
            "historical_limit": history["pass"],
            "fresh_old_limit": all(new-old <= tolerance for old,new in
                                   zip(old_validation["pinned"], old_validation["unguarded"], strict=True)),
            "new_validation_gain": average(new_validation["guarded"]) -
                                   average(new_validation["unguarded"]) >= margin,
        }
        if all(predicates.values()):
            selected, selected_stage = prospect, stage
        views = anchor, prospect, selected
        old_report = scores(fixed_report, views, control)
        new_report = scores(list(cases(source, name + "-new-report", seed, phase, probe_count)),
                            views, control)
        decisions.append(dict(stage=stage, name=phase["name"], selected_stage=selected_stage,
                              gates=predicates, history=history, new_validation=encode(new_validation),
                              old_validation=encode(old_validation), new_report=encode(new_report),
                              old_report=encode(old_report)))
    final = prospect.checkpoint()
    if prospect.native._episode_reader()._ledger[:len(base)] != base:
        raise RuntimeError("Original witness prefix changed")
    revised = output / f"seed-{seed}"
    revised.mkdir()
    (revised / "trace.json").write_bytes(canonical(traces))
    (revised / "native-joint.json").write_bytes(final)
    return {"seed":seed, "full_joint_sha256":digest(final),
            "selected_joint_sha256":digest(selected.checkpoint()), "trace_sha256":digest(canonical(traces)),
            "selected_stage":selected_stage, "witnesses_added":len(traces),
            "head_steps":[new.steps-old.steps for old,new in zip(anchor._heads,prospect._heads,strict=True)],
            "historical_witnesses":len(base), "training_actions":2*len(traces),
            "validation_and_report_actions":4*probe_count*(1+len(decisions)),
            "decisions":decisions, "wall_seconds":monotonic()-wall, "cpu_seconds":process_time()-cpu}


def classification(replicas, plan):
    margin = float(Fraction(plan["min_novel_gain"]))
    maximum = float(Fraction(plan["max_brier_drift"]))
    noninferiority = float(Fraction(plan["max_new_loss_vs_unguarded"]))
    gates = []
    for replica in replicas:
        for stage in replica["decisions"]:
            if stage["name"] == "return":
                continue
            scores = stage["new_report"]
            guarded = average(scores["guarded"])
            best = min(average(scores[arm]) for arm in ("pinned", *ARMS[3:]))
            gates.append(dict(
                seed=replica["seed"], stage=stage["stage"],
                new_vs_strongest_fixed_or_fitted=best-guarded,
                new_loss_vs_unguarded=guarded-average(scores["unguarded"]),
                retained=all(new-old <= maximum for old,new in zip(
                    stage["old_report"]["pinned"], stage["old_report"]["guarded"], strict=True)),
            ))
    result = all(g["retained"] and g["new_vs_strongest_fixed_or_fitted"] >= margin
                 and g["new_loss_vs_unguarded"] <= noninferiority for g in gates)
    return ("DEV_GO" if result else "DEV_NO_GO"), gates


def run(checkpoints, plan_path, output):
    plan_raw = plan_path.read_bytes()
    plan = json.loads(plan_raw)
    if sha256(Path(__file__).read_bytes()).hexdigest() != plan["producer_sha256"]:
        raise ValueError("Producer code differs from the frozen protocol")
    protocol = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    anchor = restore(checkpoints, protocol)
    source = source_module(protocol["world_sha256"])
    total = sum(phase["n"] for phase in plan["phases"])
    reader = anchor.native._episode_reader()
    if total + len(reader._ledger) > reader._episode_limit:
        raise ValueError("Staged budget exceeds witness capacity")
    output.mkdir(exist_ok=False)
    wall, cpu = monotonic(), process_time()
    replicas = [compare_replica(seed, anchor, source, plan, output) for seed in plan["seeds"]]
    outcome, gates = classification(replicas, plan)
    return dict(development=outcome, protocol_sha256=digest(plan_raw),
                parent_ckpt_sha256=protocol["joint_sha256"], replicas=replicas,
                decision_gates=gates, wall_seconds=monotonic()-wall, cpu_seconds=process_time()-cpu,
                max_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    checkpoint_directory, plan_path, output = map(Path, sys.argv[1:])
    print(json.dumps(run(checkpoint_directory, plan_path, output), indent=2, sort_keys=True))
