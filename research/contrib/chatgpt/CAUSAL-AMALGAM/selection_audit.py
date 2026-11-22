"""Audit matched development forecasts and restore the continuation in a new process."""

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys
from time import monotonic

from selection_trial import configuration, restore, SCALE
from specialist_selection import SpecialistSelection
from yggdrasil.native_context_basis import canonical, digest

ARMS = (
    "native", "direct", "temporal", "selector", "fixed_blend",
    "misaligned_selector", "trailing", "change_point",
)


def losses(records):
    return {
        name: Fraction(
            sum((record["prediction"][name] - record["row"]["s2"] * SCALE) ** 2
                for record in records),
            len(records) * SCALE**2,
        )
        for name in ARMS
    }


def audit(directory, protocol, output):
    started = monotonic()
    report = json.loads((output / "producer.json").read_bytes())
    raw_trace = (output / "trace.json").read_bytes()
    if digest(raw_trace) != report["trace_sha256"]:
        raise ValueError("Trace digest mismatch")
    records = json.loads(raw_trace)
    actual = Counter(record["phase"] for record in records)
    expected = {i: phase["episodes"] for i, phase in enumerate(protocol["phases"])}
    if actual != expected or len({record["id"] for record in records}) != len(records):
        raise ValueError("Unexpected phase coverage or repeated witness")
    if report["episodes"] != len(records) or report["actions"] != 2 * len(records):
        raise ValueError("Invalid action accounting")
    for record in records:
        forecasts = record["prediction"]
        if set(forecasts) != set(ARMS) or any(
                type(value) is not int or not 0 <= value <= SCALE for value in forecasts.values()):
            raise ValueError("Invalid matched forecasts")
        origin = record["origin"]
        if origin not in (0, 1, 2) or forecasts["selector"] != forecasts[ARMS[origin]]:
            raise ValueError("Selector forecast disagrees with its recorded source")
    phases = [losses([r for r in records if r["phase"] == i])
              for i in range(len(protocol["phases"]))]
    scored = [r for r in records if protocol["phases"][r["phase"]]["score"]]
    scores = losses(scored)
    uses = Counter(record["origin"] for record in scored)
    strongest = min((score, name) for name, score in scores.items() if name != "selector")
    gain = strongest[0] - scores["selector"]
    return_loss = phases[-1]["selector"] - phases[-1]["native"]
    gates = {
        "beats_all_controls": gain >= Fraction(protocol["go_minimum_gain_vs_each_control"]),
        "specialist_used": uses[1] + uses[2] >= protocol["go_minimum_specialist_uses"],
        "return_loss_bound": return_loss <= Fraction(protocol["go_maximum_return_loss_vs_native"]),
    }
    anchor = restore(directory, protocol)
    descendant_path = (output / "joint-descendant.json").resolve()
    descendant = restore(directory, protocol, descendant_path, report["checkpoint_sha256"])
    replayed = SpecialistSelection.replay(anchor, descendant, **configuration(protocol))
    old = anchor.native._episode_reader()._ledger
    new = replayed.system.native._episode_reader()._ledger
    expected_events = [
        [r["id"], r["views"], *(r["row"][k] for k in ("x1", "s2", "x2", "y"))]
        for r in records
    ]
    if canonical(new[len(old):]) != canonical(expected_events):
        raise ValueError("Restored witness suffix differs from the matched trace")
    if report["head_gradient_steps"] != [3 * len(records)] * 4:
        raise ValueError("Unexpected head update count")
    return {
        "development": "DEV_GO" if all(gates.values()) else "DEV_NO_GO",
        "gates": gates, "strongest_control": strongest[1], "gain": float(gain),
        "scored": len(scored), "brier": {name: float(p) for name, p in scores.items()},
        "brier_by_phase": [{name: float(p) for name, p in phase.items()} for phase in phases],
        "specialist_origin_counts": dict(uses), "cold_replay_exact": True,
        "audit_wall_seconds": monotonic() - started,
    }


if __name__ == "__main__":
    directory, manifest, output = (Path(arg) for arg in sys.argv[1:])
    result = audit(directory, json.loads(manifest.read_bytes()), output)
    print(json.dumps(result, indent=2, sort_keys=True))
