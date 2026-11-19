"""Check dual-platform checkpoint custody for sealed Amalgam witness traces."""

from argparse import ArgumentParser
from itertools import product
import json
from math import isfinite
from pathlib import Path
import platform
from time import monotonic

from shadow_preflight import checked_bytes
from yggdrasil.native_causal_amalgam import KINDS, NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import (
    NUMERIC_SOURCE_TOLERANCE, TemporalLatentSpecialist, _source_equivalent,
)

HERE = Path(__file__).resolve().parent
SCHEMA = "yggdrasil.ckad.amalgam-sealed-replay.v1"
STUDIES = (
    ("staged-retention-dev-01", "staged_retention_protocol.json"),
    ("causal-templates-dev-01", "causal_templates_protocol.json"),
    ("open-set-dev-01", "open_set_protocol.json"),
)


def admit(model, identifier, views, row):
    receipt = canonical([identifier, views, row])
    return model.observe_experience(identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                                    packet_sha256=digest(receipt))


def parents(directory):
    spec = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    donor = json.loads(checked_bytes(directory / spec["donor_name"], spec["donor_sha256"]))
    return spec, dict(
        native_parent=checked_bytes(directory / spec["native_name"], spec["native_sha256"]),
        native_pin=spec["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"),
        donor_pin=donor["state_sha256"],
    )


def archive():
    """Load the frozen roster and each source-bound witness trace."""
    seen_ids = set()
    for study, protocol in STUDIES:
        directory = HERE / study
        report = json.loads((directory / "result.json").read_bytes())
        plan_raw = (HERE / protocol).read_bytes()
        plan = json.loads(plan_raw)
        if report["protocol_sha256"] != digest(plan_raw):
            raise ValueError("Frozen protocol hash mismatch")
        if [r["seed"] for r in report["replicas"]] != plan["seeds"]:
            raise ValueError("Frozen seed roster mismatch")
        stage_sizes = [p.get("n", p.get("count")) for p in plan["phases"]]
        staged = study == "staged-retention-dev-01"
        for replica in report["replicas"]:
            seed = replica["seed"]
            if staged:
                evidence = replica["trace_sha256"], replica["full_joint_sha256"]
            else:
                checkpoint = replica["checkpoints"]
                evidence = checkpoint["trace_sha256"], checkpoint["final_sha256"]
            trace = json.loads(checked_bytes(directory / f"seed-{seed}" / "trace.json", evidence[0]))
            stages = [i for i, size in enumerate(stage_sizes, int(staged)) for _ in range(size)]
            if [record["stage"] for record in trace] != stages:
                raise ValueError("Frozen witness count or stage order mismatch")
            rows = []
            for record in trace:
                identifier = record["id" if staged else "identifier"]
                if identifier in seen_ids:
                    raise ValueError("Repeated witness across sealed replicas")
                seen_ids.add(identifier)
                rows.append((identifier, tuple(tuple(v) for v in record["views"]), record["row"]))
            yield f"{study}/{seed}", evidence, rows


def probes(model):
    """Compare the stored heads on all paired public inputs without a source actor."""
    forecasts = []
    for context, noise_a, noise_b in product((0, 1), repeat=3):
        views = ((context, noise_a), (context, noise_b))
        for first in (0, 1):
            forecasts.extend(model.specialist_forecasts(views, first))
            for state, second in product((0, 1), repeat=2):
                forecasts.extend(model.specialist_forecasts(views, first, state, second))
    return forecasts


def summary(model, raw, trace_sha):
    payload = json.loads(raw)
    return {
        "trace_sha256": trace_sha,
        "native_sha256": digest(model.native.checkpoint()),
        "joint_sha256": digest(raw),
        "witness_count": len(model.native._episode_reader()._ledger),
        "heads": payload["action_heads"] + payload["temporal_heads"],
        "probabilities": probes(model),
    }


def replay(case_directory, candidate):
    started = monotonic()
    if len(candidate) != 40 or not all(
            ch in "0123456789abcdef" for ch in candidate):
        raise ValueError("Expected an exact candidate Git SHA")
    operating_system = platform.system()
    if operating_system not in ("Linux", "Windows"):
        raise ValueError("Expected Linux or Windows runner")
    spec, material = parents(case_directory)
    raw = (case_directory / spec["joint_name"]).read_bytes()
    anchor_sha = digest(raw)
    live = NativeCausalAmalgam.restore(raw, anchor_sha, **material)
    pinned_native = json.loads((HERE / "growth-result.json").read_bytes())["fixture_descendant_sha256"]
    if digest(live.native.checkpoint()) != pinned_native:
        raise ValueError("Platform anchor changed the pinned native state")
    verify_linux_bytes = operating_system == "Linux"
    if verify_linux_bytes and anchor_sha != spec["joint_sha256"]:
        raise ValueError("Linux producer checkpoint does not match the sealed anchor")
    models = {"anchor": summary(live, raw, None)}
    historic = live.native._episode_reader()._ledger
    for label, (trace_sha, expected_linux_sha), records in archive():
        trained = live
        for identifier, views, row in records:
            trained = admit(trained, identifier, views, row)
        transcript = trained.checkpoint()
        sha = digest(transcript)
        if verify_linux_bytes and sha != expected_linux_sha:
            raise ValueError(f"Linux producer digest differs for {label}")
        saved = NativeCausalAmalgam.restore(transcript, sha, **material)
        suffix = tuple((identifier, views, *(row[key] for key in ("x1", "s2", "x2", "y")))
                       for identifier, views, row in records)
        actual = saved.native._episode_reader()._ledger
        if actual != historic + suffix or saved.checkpoint() != transcript:
            raise ValueError(f"Cold reconstruction differs for {label}")
        deltas = [b.steps - a.steps for a, b in zip(live._heads, saved._heads, strict=True)]
        if deltas != [3 * len(records)] * 4:
            raise ValueError(f"Specialist step counts differ for {label}")
        models[label] = summary(saved, transcript, trace_sha)
    if len(models) != 10:
        raise ValueError("Expected the anchor and all nine sealed descendants")
    return {"schema": SCHEMA, "candidate": candidate, "platform": operating_system,
            "models": models, "source_actions": 0, "wall_seconds": monotonic() - started}


def equivalent_heads(left, right):
    largest = 0.0
    kinds = KINDS + KINDS
    types = (ActionLatentSpecialist,) * 2 + (TemporalLatentSpecialist,) * 2
    for first, second, kind, cls in zip(left, right, kinds, types, strict=True):
        _source_equivalent(cls.from_data(first, kind), cls.from_data(second, kind))
        for key in ("encoder", "predictor", "encoder_bias", "predictor_bias"):
            a, b = first[key], second[key]
            if key in ("encoder", "predictor"):
                a = [x for row in a for x in row]
                b = [x for row in b for x in row]
            largest = max(largest, *(abs(x-y) for x, y in zip(a, b, strict=True)))
    return largest


def compare(linux, windows, expected_candidate):
    if (linux["schema"] != SCHEMA or windows["schema"] != SCHEMA or
            linux["platform"] != "Linux" or windows["platform"] != "Windows" or
            linux["candidate"] != expected_candidate or windows["candidate"] != expected_candidate or
            linux["source_actions"] != 0 or windows["source_actions"] != 0):
        raise ValueError("Mismatched source, platforms or execution scope")
    left, right = linux["models"], windows["models"]
    if set(left) != set(right) or len(left) != 10 or "anchor" not in left:
        raise ValueError("Platform model rosters differ")
    results = {}
    for name, a in left.items():
        b = right[name]
        for key in ("native_sha256", "trace_sha256", "witness_count"):
            if a[key] != b[key]:
                raise ValueError(f"Exact checkpoint identity differs for {name}: {key}")
        weight_diff = equivalent_heads(a["heads"], b["heads"])
        probabilities = list(zip(a["probabilities"], b["probabilities"], strict=True))
        if len(probabilities) != 160 or any(not isfinite(x) or not 0 <= x <= 1
                                           for pair in probabilities for x in pair):
            raise ValueError(f"Invalid readout probes for {name}")
        max_diff = max(abs(x-y) for x, y in probabilities)
        if max_diff > NUMERIC_SOURCE_TOLERANCE:
            raise ValueError(f"Specialist readout difference exceeds contract for {name}")
        results[name] = {
            "checkpoint_bytes_equal": a["joint_sha256"] == b["joint_sha256"],
            "linux_joint_sha256": a["joint_sha256"], "windows_joint_sha256": b["joint_sha256"],
            "native_sha256": a["native_sha256"], "witness_count": a["witness_count"],
            "max_parameter_delta": weight_diff, "max_probe_delta": max_diff,
        }
    return {"candidate": expected_candidate, "source_actions": 0,
            "numeric_source_tolerance": NUMERIC_SOURCE_TOLERANCE, "verified": results}


def main():
    parser = ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="verb", required=True)
    capture = subparsers.add_parser("replay")
    capture.add_argument("directory", type=Path)
    capture.add_argument("candidate")
    verify = subparsers.add_parser("compare")
    verify.add_argument("linux", type=Path)
    verify.add_argument("windows", type=Path)
    verify.add_argument("candidate")
    args = parser.parse_args()
    if args.verb == "replay":
        report = replay(args.directory, args.candidate)
    else:
        report = compare(json.loads(args.linux.read_bytes()), json.loads(args.windows.read_bytes()),
                         args.candidate)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
