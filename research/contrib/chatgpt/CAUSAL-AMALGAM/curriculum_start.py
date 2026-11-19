"""Compare two orders of the same synthetic action-consequence witnesses."""

import json
from pathlib import Path
import sys
from time import monotonic

from selection_trial import restore, source_module
from shadow_preflight import checked_bytes
from staged_retention import Controls, admit, cases, encode, scores
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
ARMS = ("gradual", "shuffled")
CONTROLS = ("fit_full", "fit_trailing", "fit_change_point")


def collect(source, plan, seed):
    def rows(split, phase, count):
        cohort = plan["id"] + "-" + split
        return [[digest(canonical([cohort, seed, n])), views, row]
                for n, (views, row) in enumerate(cases(source, cohort, seed, phase, count))]
    old, new = (plan["phases"][name] for name in ("familiar", "changed"))
    return {
        "familiar_train": rows("familiar-train", old, plan["train_per_phase"]),
        "changed_train": rows("changed-train", new, plan["train_per_phase"]),
        "familiar_held": rows("familiar-held", old, plan["held_per_phase"]),
        "changed_held": rows("changed-held", new, plan["held_per_phase"]),
    }


def measure(anchor, plan, seed, trace, deadline):
    prefix = anchor.native._episode_reader()._ledger
    required = {"familiar_train", "changed_train", "familiar_held", "changed_held"}
    if set(trace) != required:
        raise ValueError("Incorrect split roster")
    trace = {name: [(i, tuple(tuple(v) for v in views), row) for i, views, row in rows]
             for name, rows in trace.items()}
    for name, rows in trace.items():
        expected = plan["train_per_phase"] if name.endswith("_train") else plan["held_per_phase"]
        if len(rows) != expected:
            raise ValueError("Incorrect split size")
    ids = [i for rows in trace.values() for i, _, _ in rows]
    if len(ids) != len(set(ids)) or set(ids) & {record[0] for record in prefix}:
        raise ValueError("Witness overlap")
    gathered = trace["familiar_train"] + trace["changed_train"]
    if len(prefix) + len(gathered) > anchor.native._episode_reader()._episode_limit:
        raise ValueError("Curriculum exceeds qualified witness capacity")
    orders = (gathered, sorted(gathered, key=lambda record:
                              digest(canonical([plan["id"], seed, record[0], "shuffle"]))))
    details = {}
    for name, order in zip(ARMS, orders, strict=True):
        controls = Controls()
        for _, views, x1, s2, x2, y in prefix:
            controls.observe(views, dict(x1=x1, s2=s2, x2=x2, y=y))
        current = anchor
        for identifier, views, row in order:
            if monotonic() > deadline:
                raise TimeoutError("Frozen wall budget expired")
            current = admit(current, identifier, views, row)
            controls.observe(views, row)
        history = current.native._episode_reader()._ledger
        if (history[:len(prefix)] != prefix or
                [row[0] for row in history[len(prefix):]] != [row[0] for row in order]):
            raise ValueError("Native continuation changed witness custody")
        steps = [new.steps - old.steps for old, new in zip(anchor._heads, current._heads, strict=True)]
        if steps != [3 * len(order)] * 4:
            raise ValueError("Specialist steps differ")
        held = {}
        for split in ("familiar_held", "changed_held"):
            values = encode(scores([(views, row) for _, views, row in trace[split]],
                                   (anchor, current, anchor), controls))
            held[split] = {key: values[key] for key in ("pinned", "unguarded", *CONTROLS)}
        details[name] = dict(held=held, witnesses=len(history), head_steps=steps,
                             checkpoint_sha256=digest(current.checkpoint()))
    return dict(seed=seed, trace_sha256=digest(canonical(trace)), arms=details)


def gate(replicas, plan):
    order_gain, control_gain, retained = [], [], []
    for replica in replicas:
        gradual, shuffled = (replica["arms"][name]["held"] for name in ARMS)
        novel = gradual["changed_held"]
        other = shuffled["changed_held"]
        order_gain.append(other["unguarded"][0] - novel["unguarded"][0])
        control_gain.append(min(arm[key][0] for arm in (novel, other)
                                for key in CONTROLS) - novel["unguarded"][0])
        old = gradual["familiar_held"]
        retained.append(all(after-before <= plan["max_familiar_drift"] for before, after in
                            zip(old["pinned"], old["unguarded"], strict=True)))
    gates = dict(order=sum(order_gain)/len(replicas) >= plan["min_gain"],
                 control=sum(control_gain)/len(replicas) >= plan["min_gain"],
                 retention=all(retained))
    return dict(verdict="DEV_SIGNAL" if all(gates.values()) else "DEV_NO_GO",
                gates=gates, order_gains=order_gain, control_gains=control_gain,
                familiar_retained=retained)


def run(checkpoints, output, replay):
    raw = (HERE / "curriculum_start_protocol.json").read_bytes()
    plan = json.loads(raw)
    for path, pin in plan["source_files"].items():
        checked_bytes(HERE / path, pin)
    proof = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    started = monotonic()
    anchor = restore(checkpoints, proof)
    if replay:
        saved = json.loads((output / "result.json").read_bytes())
    else:
        output.mkdir(exist_ok=False)
        source = source_module(proof["world_sha256"])
    replicas = []
    for n, seed in enumerate(plan["seeds"]):
        path = output / f"trace-{seed}.json"
        trace = (json.loads(checked_bytes(path, saved["replicas"][n]["trace_sha256"]))
                 if replay else collect(source, plan, seed))
        replicas.append(measure(anchor, plan, seed, trace, started + plan["wall_budget_seconds"]))
        if not replay:
            path.write_bytes(canonical(trace))
    result = dict(**gate(replicas, plan), replicas=replicas, protocol_sha256=digest(raw),
                  parent_sha256=proof["joint_sha256"],
                  distinct_actions=4 * len(replicas) * (plan["train_per_phase"] + plan["held_per_phase"]))
    if replay:
        if any(saved[key] != value for key, value in result.items()):
            raise ValueError("Receipt replay did not reproduce the original result")
        return dict(exact_replay=True, source_actions=0, verdict=result["verdict"])
    return dict(result, wall_seconds=monotonic()-started)


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2]), "--replay" in sys.argv[3:]),
                     indent=2, sort_keys=True))
