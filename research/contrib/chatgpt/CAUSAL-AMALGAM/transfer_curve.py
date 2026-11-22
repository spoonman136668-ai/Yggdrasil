"""Measure development transfer through held-out public intervention cells."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
from time import monotonic, process_time

from selection_trial import SCALE, configuration, restore, source_module
from shadow_preflight import checked_bytes
from specialist_selection import SpecialistSelection
from staged_retention import Controls
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve().parent
CONVENTIONAL = ("full", "trailing", "change_point", "structural")


class StructuralControl:
    """Bayesian averaging of public Boolean partitions with learned group rates."""

    def __init__(self):
        self.counts = [Counter() for _ in range(7)]
        self.mass = [1 / 7] * 7

    @staticmethod
    def groups(context, action):
        return (0, context, action, context ^ action, context & action,
                context | action, 2 * context + action)

    def rates(self, key):
        return [(counts[group, 1] + 0.5) /
                (counts[group, 0] + counts[group, 1] + 1)
                for group, counts in zip(self.groups(*key), self.counts, strict=True)]

    def forecast(self, key):
        return sum(p * weight for p, weight in zip(self.rates(key), self.mass, strict=True))

    def observe(self, key, outcome):
        weights = [weight * (p if outcome else 1 - p)
                   for p, weight in zip(self.rates(key), self.mass, strict=True)]
        total = sum(weights)
        self.mass = [weight / total for weight in weights]
        for group, counts in zip(self.groups(*key), self.counts, strict=True):
            counts[group, outcome] += 1


def generate(source, plan, case):
    """Choose actions from public contexts and the fixed experimental schedule."""
    held_context, held_action = case["omitted"]
    for split, count, family, orientation in (
        ("train", plan["milestones"][-1], "context_switch", case["orientation"]),
        ("transfer", plan["held_episodes"], "context_switch", case["orientation"]),
        ("retention", plan["held_episodes"], "invariant", 0),
    ):
        domain = plan["id"] + "-" + split
        records = []
        coverage = Counter()
        for index in range(8 * count):
            episode = source.make_episode(cohort=domain, seed=case["seed"], index=index,
                                          family=family, regime=orientation)
            views = source.public_views(episode)
            context = views[0][0]
            if split == "transfer" and context != held_context:
                continue
            first = coverage[context] % 2
            if split == "transfer":
                first = held_action
            elif split == "train" and context == held_context:
                first = 1 - held_action
            second = (coverage[context] // 2) % 2
            coverage[context] += 1
            row = source.rollout(episode, lambda _: first, lambda *_: second)
            identifier = digest(canonical([domain, case["seed"], index]))
            records.append([identifier, views, row])
            if len(records) == count:
                break
        if len(records) != count:
            raise ValueError("Frozen draw budget could not cover the public context")
        yield split, records


def error(probability, outcome):
    return (round(probability * SCALE) - SCALE * outcome) ** 2


def forecasts(gate, anchor, controls, structural, views, row):
    first = row["x1"]
    key = views[0][0], first
    native, direct, temporal = gate._forecasts(views, (first,))
    return dict(
        anchor=anchor.native.experience_context_forecast(views[0], first),
        native=native, direct=direct, temporal=temporal,
        gated=gate.forecast(views, first), uniform=(native + direct + temporal) / 3,
        **dict(zip(CONVENTIONAL, (*controls.forecast(key), structural.forecast(key)), strict=True)),
    )


def measure(anchor, proof, plan, case, trace, deadline):
    original = anchor.native._episode_reader()
    if len(original._ledger) + plan["milestones"][-1] > original._episode_limit:
        raise ValueError("Frozen trial exceeds checkpoint capacity")
    expected_counts = (plan["milestones"][-1], plan["held_episodes"], plan["held_episodes"])
    if set(trace) != {"train", "transfer", "retention"} or tuple(map(len, (
            trace["train"], trace["transfer"], trace["retention"]))) != expected_counts:
        raise ValueError("Frozen trace counts differ")
    trace = {split: [(identifier, tuple(tuple(v) for v in views), row)
                     for identifier, views, row in records]
             for split, records in trace.items()}
    ids = [identifier for records in trace.values() for identifier, _, _ in records]
    if len(ids) != len(set(ids)) or set(ids) & {record[0] for record in original._ledger}:
        raise ValueError("Witness custody overlap")
    omitted = tuple(case["omitted"])
    training_cells = {tuple(row[k] for k in ("s1", "x1")) for _, _, row in trace["train"]}
    transfer_cells = {tuple(row[k] for k in ("s1", "x1")) for _, _, row in trace["transfer"]}
    if transfer_cells != {omitted} or omitted in training_cells or len(training_cells) != 3:
        raise ValueError("Held intervention cell has the wrong coverage")
    gate = SpecialistSelection(anchor, **configuration(proof))
    controls = Controls()
    structural = StructuralControl()
    for _, views, first, state, second, reward in original._ledger:
        controls.observe(views, dict(x1=first, s2=state, x2=second, y=reward))
    checkpoints, online = [], Counter()

    def points():
        transfer, retention = Counter(), Counter()
        origins = Counter()
        for _, views, row in trace["transfer"]:
            for name, p in forecasts(gate, anchor, controls, structural, views, row).items():
                transfer[name] += error(p, row["s2"])
            origins[gate.selection(views, row["x1"])] += 1
        for _, views, row in trace["retention"]:
            for name, system in (("anchor", anchor), ("native", gate.system)):
                predict = system.native.experience_context_forecast
                retention[name + "_transition"] += error(predict(views[0], row["x1"]), row["s2"])
                retention[name + "_reward"] += error(
                    predict(views[0], row["x1"], row["s2"], row["x2"]), row["y"])
        return dict(transfer=dict(transfer), retention=dict(retention),
                    held_gate_origins={str(k): v for k, v in origins.items()},
                    prequential=dict(online))

    checkpoints.append(dict(n=0, **points()))
    for n, (identifier, views, row) in enumerate(trace["train"], 1):
        if monotonic() >= deadline:
            raise TimeoutError("Frozen runtime budget expired")
        for name, p in forecasts(gate, anchor, controls, structural, views, row).items():
            online[name] += error(p, row["s2"])
        gate = gate.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=digest(canonical([identifier, views, row])),
        )
        controls.observe(views, row)
        structural.observe((views[0][0], row["x1"]), row["s2"])
        if n in plan["milestones"]:
            checkpoints.append(dict(n=n, **points()))
    final = gate.system
    current = final.native._episode_reader()._ledger
    expected_suffix = tuple((identifier, tuple(tuple(v) for v in views),
                             *(row[k] for k in ("x1", "s2", "x2", "y")))
                            for identifier, views, row in trace["train"])
    steps = [b.steps - a.steps for a, b in zip(anchor._heads, final._heads, strict=True)]
    if current != original._ledger + expected_suffix or steps != [3 * len(expected_suffix)] * 4:
        raise ValueError("Continued state differs from exact witnessed update")
    return dict(seed=case["seed"], trace_sha256=digest(canonical(trace)),
                joint_sha256=digest(final.checkpoint()), specialist_gradient_steps=steps,
                original_witnesses=len(original._ledger), final_witnesses=len(current),
                training_actions=2 * len(trace["train"]),
                held_actions=2 * (len(trace["transfer"]) + len(trace["retention"])),
                milestones=checkpoints)


def classify(reports, plan):
    denominator = plan["held_episodes"] * SCALE**2
    margin = Fraction(plan["min_brier_advantage"])
    retention = Fraction(plan["max_historical_brier_drift"])
    rows = []
    for points in zip(*(r["milestones"] for r in reports), strict=True):
        gains, retained = [], []
        for point in points:
            values = point["transfer"]
            best = min(values[name] for name in ("anchor", *CONVENTIONAL))
            gains.append(Fraction(best - values["native"], denominator))
            retained.append(all(Fraction(point["retention"]["native_" + k] -
                                          point["retention"]["anchor_" + k], denominator)
                                <= retention for k in ("transition", "reward")))
        rows.append(dict(n=points[0]["n"], mean_advantage=float(sum(gains) / len(gains)),
                         seeds_at_margin=sum(g >= margin for g in gains),
                         pooled_at_margin=sum(gains) >= len(gains) * margin,
                         retain_all=all(retained)))
    late = all(row["pooled_at_margin"] and row["retain_all"] for row in rows[-2:])
    late &= rows[-1]["seeds_at_margin"] >= plan["min_seeds_at_margin"]
    early = any(row["pooled_at_margin"] for row in rows[:-2])
    result = "EARLY_OR_IMMEDIATE_DEV_SIGNAL" if late and early else (
        "DELAYED_DEV_SIGNAL" if late else "DEV_NO_GO")
    return result, rows


def run(checkpoints, protocol_path, output, *, replay=False):
    began, cpu = monotonic(), process_time()
    raw = protocol_path.read_bytes()
    plan = json.loads(raw)
    for name, pin in plan["source_files"].items():
        checked_bytes(HERE / name, pin)
    proof = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    anchor = restore(checkpoints, proof)
    if replay:
        saved = json.loads((output / "result.json").read_bytes())
        if saved["protocol_sha256"] != digest(raw):
            raise ValueError("The result refers to different frozen source")
        indexed = {report["seed"]: report for report in saved["replicas"]}
    else:
        output.mkdir(exist_ok=False)
        source = source_module(proof["world_sha256"])
    deadline = began + plan["wall_budget_seconds"]
    reports = []
    for case in plan["cases"]:
        path = output / f"trace-{case['seed']}.json"
        if replay:
            trace = json.loads(checked_bytes(path, indexed[case["seed"]]["trace_sha256"]))
        else:
            trace = dict(generate(source, plan, case))
        report = measure(anchor, proof, plan, case, trace, deadline)
        if not replay:
            path.write_bytes(canonical(trace))
        reports.append(report)
    result, curve = classify(reports, plan)
    payload = dict(result=result, curve=curve, replicas=reports,
                   parent_sha256=proof["joint_sha256"], protocol_sha256=digest(raw))
    if replay:
        if any(saved[key] != value for key, value in payload.items()):
            raise ValueError("Receipt-only replay differs from the producer")
        payload = dict(result=result, exact_receipt_replay=True, verified_replicas=len(reports))
    return dict(payload, new_synthetic_actions=0 if replay else sum(
                p["training_actions"] + p["held_actions"] for p in reports),
                wall_seconds=monotonic() - began, cpu_seconds=process_time() - cpu,
                max_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("checkpoints", type=Path)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.checkpoints, args.protocol, args.output, replay=args.replay),
                     indent=2, sort_keys=True))
