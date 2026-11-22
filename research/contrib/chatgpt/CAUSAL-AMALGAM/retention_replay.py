"""Rebuild the existing negative selector descendant from its admitted evidence."""

from argparse import ArgumentParser
from fractions import Fraction
import json
from pathlib import Path
from time import monotonic

from retention_guard import reversible_candidate
from selection_trial import restore
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve().parent


def run(directory, evidence):
    started = monotonic()
    protocol = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    producer = json.loads((evidence / "producer.json").read_bytes())
    plan = json.loads((HERE / "retention_probe.json").read_bytes())
    if plan["anchor_sha256"] != protocol["joint_sha256"] or (
            plan["candidate_sha256"] != producer["checkpoint_sha256"]):
        raise ValueError("Retention stage requires the exact historical checkpoint pair")
    trace = (evidence / "trace.json").read_bytes()
    if digest(trace) != producer["trace_sha256"]:
        raise ValueError("Historical accepted trace digest mismatch")
    anchor = restore(directory, protocol)
    candidate = anchor
    for event in json.loads(trace):
        identifier = event["id"]
        views = tuple(tuple(view) for view in event["views"])
        row = event["row"]
        candidate = candidate.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=digest(canonical([identifier, views, row])),
        )
    if digest(candidate.checkpoint()) != producer["checkpoint_sha256"]:
        raise ValueError("Exact candidate reconstruction failed")
    selected, result = reversible_candidate(
        anchor, candidate, plan["windows"], max_brier_drift=Fraction(plan["max_brier_drift"]),
    )
    return dict(result, original_joint_sha256=protocol["joint_sha256"],
                tested_joint_sha256=producer["checkpoint_sha256"],
                guard_readout_sha256=digest(selected.checkpoint()),
                replayed_existing_witnesses=producer["episodes"], new_world_actions=0,
                wall_seconds=monotonic()-started)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("checkpoints", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.checkpoints, args.evidence), indent=2, sort_keys=True))
