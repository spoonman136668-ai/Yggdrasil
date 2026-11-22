"""Check bounded native continuation with one disjoint engineering fixture."""
from argparse import ArgumentParser
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from shadow_preflight import checked_bytes, MANIFEST, require

CAMPAIGN = MANIFEST.parent.parent / "CKAD-26" / "campaign.py"
sys.path.insert(0, str(CAMPAIGN.parent))

from campaign import BASE, LEGACY, NativeCumulativeLearner, canonical, digest

COHORT, SEED, ACTIONS = "amalgam-growth-engineering-v1", 271991, (0, 1)


def expect_value_error(operation, reason):
    try:
        operation()
    except ValueError as exc:
        require(reason in str(exc), f"WRONG_REJECTION_{reason}")
    else:
        raise RuntimeError(f"EXPECTED_REJECTION_{reason}")


def run(initial):
    start = time.monotonic()
    manifest = json.loads(MANIFEST.read_bytes())
    initial_pin = manifest["native_artifacts_sha256"][initial.name]
    old_raw = checked_bytes(initial, initial_pin)
    old = NativeCumulativeLearner.restore(old_raw, initial_pin)
    require(old.checkpoint() == old_raw, "V5_COLD_BYTES")
    enlarged = old.extend_experience_capacity()
    raw = enlarged.checkpoint()
    require(old.checkpoint() == old_raw, "GROWTH_MUTATED_PARENT")
    require(all(old.experience_context_plan(view) == enlarged.experience_context_plan(view)
                for view in product((0, 1), repeat=2)), "GROWTH_READOUT_DRIFT")
    old_legacy, old_episode = BASE.legacy_and_experience(old_raw)
    enlarged_legacy, enlarged_episode = BASE.legacy_and_experience(raw)
    require(old_legacy == enlarged_legacy and old_episode["episodes"] == enlarged_episode["episodes"],
            "GROWTH_EVIDENCE_DRIFT")
    require(enlarged_episode["episode_limit"] == 1152, "GROWTH_CAPACITY")

    fixture = BASE.make_episode(cohort=COHORT, seed=SEED, index=0, family="invariant", regime=0)
    views = BASE.public_views(fixture)
    row = LEGACY.fixed_rollout(fixture, ACTIONS)
    identifier = LEGACY.event_id(COHORT, SEED, 0, "engineering")
    expect_value_error(lambda: BASE.admit(old, identifier, views, row), "EPISODE_CAPACITY")
    continued = BASE.admit(enlarged, identifier, views, row)
    payload = continued.checkpoint()
    final_legacy, final_episode = BASE.legacy_and_experience(payload)
    require(final_legacy == old_legacy and final_episode["episodes"] ==
            [*old_episode["episodes"], BASE.retain_event(identifier, views, row)],
            "CONTINUATION_PREFIX")
    require(BASE.admit(continued, identifier, views, row) is continued, "DUPLICATE_REPLAY")
    expect_value_error(lambda: BASE.admit(continued, identifier, views, {**row, "y": 1-row["y"]}),
                       "EPISODE_CONFLICTING_REPLAY")
    expect_value_error(continued.extend_experience_capacity, "EPISODE_GROWTH_PARENT")
    require(continued.consolidate_experience().checkpoint() == payload, "CONSOLIDATION")

    with TemporaryDirectory(prefix="amalgam-cold-growth-") as directory:
        parent, packet, output = (Path(directory) / name for name in ("parent.json", "packet.json", "output.json"))
        parent.write_bytes(raw)
        packet.write_bytes(canonical({"identifier":identifier, "views":views, "row":row}))
        report = json.loads(subprocess.check_output(
            [sys.executable, "-B", str(CAMPAIGN), "--cold-update", str(parent), digest(raw),
             BASE.context_readout_pin(enlarged), str(packet), str(output)],
            timeout=180))
        require(output.read_bytes() == payload and report["episode_count"] == 1025
                and report["sha256"] == digest(payload), "FRESH_PROCESS_CONTINUATION")
    return {
        "engineering_preflight": "PASS", "fixture_cohort": COHORT, "fixture_seed": SEED,
        "public_packet_sha256": digest(canonical([identifier, views, row])),
        "parent_checkpoint_sha256": initial_pin, "expanded_checkpoint_sha256": digest(raw),
        "fixture_descendant_sha256": digest(payload), "parent_episodes": 1024,
        "descendant_episodes": 1025, "descendant_bytes": len(payload), "capacity": 1152,
        "saturated_legacy_rejected": True, "fresh_process_byte_match": True,
        "warm_consolidation_byte_match": True, "native_prefix_and_legacy_planes_exact": True,
        "synthetic_engineering_actions": 2, "held_worlds_scored": 0, "scientific_pass": False,
        "child_cost": report["resource_accounting"], "wall_seconds": time.monotonic()-start,
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("ckad26_state", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.ckad26_state), indent=2, sort_keys=True))
