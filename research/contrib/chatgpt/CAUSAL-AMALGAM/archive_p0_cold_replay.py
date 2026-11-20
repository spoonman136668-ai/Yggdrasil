"""Restore original archived experimental P0 and check source-free Quine replay.

This is not owner-controlled restore, learned selector qualification or science.
The joint file and its two trained parents are pinned to original CI artifacts.
No world, source, first-use, weight update or live model is executed.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from specialist_selection import SpecialistSelection
import quine_retention as guard
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import digest

PROTOCOL = HERE / "selection_protocol_dev.json"
EXPECTED_NATIVE = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
EXPECTED_LEDGER = "55697acbbe953b5cf6878cecfd3286b068f665fc3c6f78334d241466c4beb274"
EXPECTED_EPISODES = 1025
EXPECTED_VIEWS = 8
MODES = {"native": 0, "direct": 1, "temporal": 2}


def checked(directory, name, pin):
    """Read pinned original artifact members; refuse substitutions."""
    content = (directory / name).read_bytes()
    if sha256(content).hexdigest() != pin:
        raise ValueError("P0_ARCHIVE_MEMBER_PIN_MISMATCH:" + name)
    return content


def route_evidence(mode):
    """Artificial routing *fixture*; never presented as learned selector state."""
    if mode == "native":
        return {}
    if mode not in ("direct", "temporal"):
        raise ValueError("Unknown bounded routing fixture")
    sign = 1 if mode == "direct" else -1
    value = (Fraction(sign, 8), Fraction(-sign, 8))
    # Existing public two-stage policy addresses: 4 first-stage, 16 terminal.
    keys = (
        [(context, first) for context, first in product((0, 1), repeat=2)]
        + list(product((0, 1), repeat=4))
    )
    return {key: (value,) * 4 for key in keys}


def restore_core(directory, protocol):
    native = checked(directory, protocol["native_name"], protocol["native_sha256"])
    donor_raw = checked(directory, protocol["donor_name"], protocol["donor_sha256"])
    donor = json.loads(donor_raw)
    joint = checked(directory, protocol["joint_name"], protocol["joint_sha256"])
    system = NativeCausalAmalgam.restore(
        joint, protocol["joint_sha256"],
        native_parent=native, native_pin=protocol["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"),
        donor_pin=donor["state_sha256"],
    )
    if system.checkpoint() != joint:
        raise ValueError("P0_ARCHIVE_JOINT_RESTORE_DRIFT")
    if digest(system.native.checkpoint()) != EXPECTED_NATIVE:
        raise ValueError("P0_ARCHIVE_NATIVE_DRIFT")
    ledger = system.native._episode_reader()._ledger
    from yggdrasil.native_context_basis import canonical
    if len(ledger) != EXPECTED_EPISODES or digest(canonical(ledger)) != EXPECTED_LEDGER:
        raise ValueError("P0_ARCHIVE_LEDGER_DRIFT")
    return system


def make_policy(system, mode):
    policy = SpecialistSelection(
        system, window=16, minimum_count=4,
        minimum_gain=Fraction(1, 100), enable_reward=True,
        evidence=route_evidence(mode),
    )
    if mode != "native":
        for key in policy._evidence:
            if policy.selection(((key[0], 0), (key[0], 1)), key[1], *key[2:]) != MODES[mode]:
                raise ValueError("P0_ARCHIVE_ROUTING_FIXTURE_DRIFT")
    return policy


def replay_consumed_selector(start, source_directory):
    """Reconstruct selector evidence from an already-consumed 96-event trace.

    This is a source-free historical replay, not new knowledge acquisition.
    The original P0 archive contains no independently authenticated trained
    selector checkpoint; the evidence is derived here from public trace rows.
    """
    from collections import Counter
    from specialist_selection import SpecialistSelection
    from selection_trial import configuration
    from yggdrasil.native_context_basis import canonical
    from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

    protocol = json.loads(PROTOCOL.read_bytes())
    evidence = HERE / "selection-dev-01"
    producer = json.loads((evidence / "producer.json").read_bytes())
    report = json.loads((evidence / "audit.json").read_bytes())
    raw_trace = (evidence / "trace.json").read_bytes()
    if digest(raw_trace) != producer["trace_sha256"]:
        raise ValueError("P0_CONSUMED_SELECTOR_TRACE_PIN")
    records = json.loads(raw_trace)
    if (len(records) != 96 or producer["episodes"] != 96
            or producer["parent_sha256"] != protocol["joint_sha256"]
            or report["development"] != "DEV_NO_GO"):
        raise ValueError("P0_CONSUMED_SELECTOR_PROTOCOL")
    original_ledger = start.native._episode_reader()._ledger
    known = {event[0] for event in original_ledger}
    if len(known) != len(original_ledger):
        raise ValueError("P0_CONSUMED_SELECTOR_DUPLICATE_PARENT")

    gate = SpecialistSelection(start, **configuration(protocol))
    counts = Counter()
    for index, event in enumerate(records):
        identifier, row = event["id"], event["row"]
        views = tuple(tuple(view) for view in event["views"])
        if (identifier in known or len(views) != 2
                or views[0][0] != views[1][0]
                or set(row) != {"s1", "x1", "s2", "x2", "y"}
                or row["s1"] != views[0][0]
                or event["phase"] != index // 32):
            raise ValueError("P0_CONSUMED_SELECTOR_EVENT")
        known.add(identifier)
        actions = (row["x1"],)
        before = gate._forecasts(views, actions)
        origin = gate.selection(views, *actions)
        prediction = event["prediction"]
        if origin != event["origin"] or prediction["selector"] != prediction[
                ("native", "direct", "temporal")[origin]]:
            raise ValueError("P0_CONSUMED_SELECTOR_ROUTING_DRIFT")
        for value, key in zip(before, ("native", "direct", "temporal"), strict=True):
            if abs(round(value * 1_000_000) - prediction[key]) > 1:
                raise ValueError("P0_CONSUMED_SELECTOR_PREDICTION_DRIFT")
        counts[origin] += 1
        gate = gate.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=digest(canonical([identifier, views, row])))

    checkpoint = gate.system.checkpoint()
    native = gate.system.native.checkpoint()
    if (len(gate.system.native._episode_reader()._ledger) != 1121
            or digest(native) != producer["native_sha256"]
            or [new.steps - old.steps
                for new, old in zip(gate.system._heads, start._heads, strict=True)]
            != producer["head_gradient_steps"]):
        raise ValueError("P0_CONSUMED_SELECTOR_RECONSTRUCTION_DRIFT")

    # Re-open the reconstructed core through the original, existing source-
    # authenticated native+JEPA cold restore. Rebuild the non-persisted selector
    # evidence only from the exact same already-consumed accepted suffix.
    original_native = checked(source_directory, protocol["native_name"],
                              protocol["native_sha256"])
    donor = json.loads(checked(source_directory, protocol["donor_name"],
                               protocol["donor_sha256"]))
    reopened_core = NativeCausalAmalgam.restore(
        checkpoint, digest(checkpoint), native_parent=original_native,
        native_pin=protocol["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"),
        donor_pin=donor["state_sha256"])
    reopened = SpecialistSelection.replay(start, reopened_core,
                                          **configuration(protocol))
    if (guard._checkpoint(gate) != guard._checkpoint(reopened)
            or gate.system.checkpoint() != reopened.system.checkpoint()):
        raise ValueError("P0_CONSUMED_SELECTOR_COLD_POLICY_DRIFT")
    policy_check = guard.verify_selector_replay(gate, reopened)
    if (policy_check["readout_witnesses"] != 1121
            or policy_check["policy_queries"] != 80
            or dict(counts) != {0: 96}
            or report["specialist_origin_counts"] != {"0": 64}):
        raise ValueError("P0_CONSUMED_SELECTOR_ORIGINAL_NEGATIVE_DRIFT")
    return {
        "gate": "P0_CONSUMED_SELECTOR_POLICY_REPLAY_PASS",
        "selection_original_development": "DEV_NO_GO",
        "replayed_consumed_events": len(records),
        "prequential_selection_counts": dict(sorted(counts.items())),
        "historical_checkpoint_linux_pin": producer["checkpoint_sha256"],
        "reconstructed_core_sha256": digest(checkpoint),
        "reconstructed_native_sha256": digest(native),
        "linux_exact_core_bytes_required_on_windows": False,
        "policy_check": policy_check,
        "selector_evidence_from_original_public_trace": True,
        "independently_saved_trained_selector_authenticated": False,
        "new_world_actions": 0,
        "fresh_training": False,
        "scientific_pass": False,
        "owner_cold_restore_verified": False,
    }


def run(directory):
    """Archive-only cold replay, no scientific source actions or owner custody."""
    protocol = json.loads(PROTOCOL.read_bytes())
    if protocol["joint_sha256"] != "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8":
        raise ValueError("P0_ARCHIVE_PROTOCOL_PIN_MISMATCH")
    original = restore_core(directory, protocol)
    reopened = restore_core(directory, protocol)
    before = original.checkpoint()
    views = tuple(dict.fromkeys(row[1] for row in original.native._episode_reader()._ledger))
    if len(views) != EXPECTED_VIEWS:
        raise ValueError("P0_ARCHIVE_PUBLIC_VIEW_COVERAGE")
    checks = {}
    for mode in MODES:
        first, second = make_policy(original, mode), make_policy(reopened, mode)
        result = guard.verify_selector_replay(first, second)
        if result["readout_witnesses"] != EXPECTED_EPISODES or result["policy_queries"] != 80:
            raise ValueError("P0_ARCHIVE_POLICY_READBACK_COVERAGE")
        checks[mode] = result
    if original.checkpoint() != before or reopened.checkpoint() != before:
        raise ValueError("P0_ARCHIVE_SOURCE_FREE_MUTATION")
    consumed_selector = replay_consumed_selector(original, directory)
    return {
        "consumed_selector": consumed_selector,
        "gate": "P0_ARCHIVED_RESEARCH_COLD_POLICY_READBACK_PASS",
        "experimental_joint_sha256": protocol["joint_sha256"],
        "native_sha256": EXPECTED_NATIVE,
        "ledger_sha256": EXPECTED_LEDGER,
        "witnesses": EXPECTED_EPISODES,
        "seen_public_view_pairs": len(views),
        "modes": checks,
        "selector_routing_fixture_is_trained": False,
        "owner_cold_restore_verified": False,
        "science_first_use": False,
        "source_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: archive_p0_cold_replay.py EXTRACTED_ARCHIVE_DIR")
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
