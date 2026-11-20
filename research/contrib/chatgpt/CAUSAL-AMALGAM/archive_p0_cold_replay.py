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
    return {
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
