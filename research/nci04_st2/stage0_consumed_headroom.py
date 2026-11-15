"""ST2 frozen stage-0 source identifiability screen: consumed development only.

No model instantiated, no candidate/held predictions, no protected first-use,
no new original-world seeds. A matching sampled public 3-byte signature is
only an association; it is not a persistent physical entity identifier.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT, PublicViewLocalDelta, public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard
from research.nci04_st2.event_memory import (
    correspondences, cross_position_headroom
)

CONTRACT = Path(__file__).with_name("frozen_protocol.json")
CONTRACT_BLOB = "e7417272ddb9ffb6af183b23ddd78512cde93399"
PREREG_SHA = "8ce9e435dd2e4e67a8a32b44b6124d2d0abf3e51"
ACTOR_BLOB = "89679fad934660866e6dfcb08d26d36093e6d901"
ADAPTER_BLOB = "f8c0e058f08e8d0e5c82b0581fd45f05b6e2ae1c"
REQUIRED_TOTAL = 32
REQUIRED_SEEDS_PER_FAMILY = 2
SEEDS = (827, 829, 839)
FAMILIES = ("DoorKeyEnv(size=8)", "EmptyEnv(size=8)")


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def protocol_preflight(upstream):
    p = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p.get("schema") !=
            "yggdrasil.nci04.st2.event-grounded-entity-state.dev.v1" or
        p.get("status") != "PREREG_FROZEN_BEFORE_ST2_IMPLEMENTATION_OR_OUTCOME" or
        p.get("source", {}).get("exact_sha") != SOURCE_COMMIT or
        p.get("source", {}).get("families") != list(FAMILIES) or
        p.get("source", {}).get("memory_adaptation_previously_consumed") != list(SEEDS) or
        p.get("source", {}).get("cap_actions_per_episode") != 256 or
        ">=32" not in p.get("stage0_headroom", "") or
        ">=2" not in p.get("stage0_headroom", "") or
        p.get("boundaries", {}).get("first_use") is not False or
        p.get("boundaries", {}).get("new_runner_or_controller") is not False):
        raise ValueError("ST2_STAGE0_FROZEN_CONTRACT_DRIFT")
    if git("rev-parse", "HEAD:research/nci04_st2/frozen_protocol.json") != CONTRACT_BLOB:
        raise ValueError("ST2_STAGE0_PREREG_BLOB_DRIFT")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", PREREG_SHA, "HEAD"],
        check=False
    ).returncode:
        raise ValueError("ST2_STAGE0_PREREG_ANCESTRY_MISSING")
    for path, expect in (
        ("research/mr26/public_novelty.py", ACTOR_BLOB),
        ("research/mr15/public_view_delta.py", ADAPTER_BLOB),
    ):
        if git("rev-parse", "HEAD:" + path) != expect:
            raise ValueError("ST2_STAGE0_ORIGINAL_ACTOR_OR_ADAPTER_DRIFT")
    return p, source_guard(upstream)


def headroom_verdict(family_counts):
    """Frozen 32 aggregate plus two nonzero reset seeds per original family."""
    if (type(family_counts) is not dict or
        set(family_counts) != set(FAMILIES) or
        any(type(rows) is not dict or set(rows) != set(SEEDS) or
            any(type(n) is not int or n < 0 for n in rows.values())
            for rows in family_counts.values())):
        raise ValueError("ST2_STAGE0_INVALID_COUNTS")
    total = sum(sum(rows.values()) for rows in family_counts.values())
    eligible_seeds = {
        family: sum(n > 0 for n in family_counts[family].values())
        for family in FAMILIES
    }
    eligible = (total >= REQUIRED_TOTAL and
                all(eligible_seeds[f] >= REQUIRED_SEEDS_PER_FAMILY
                    for f in FAMILIES))
    return {
        "eligible": eligible, "cross_position_total": total,
        "qualified_reset_seeds_per_family": eligible_seeds,
        "necessary_cross_position_total": REQUIRED_TOTAL,
        "necessary_reset_seeds_per_family": REQUIRED_SEEDS_PER_FAMILY,
        "disposition": ("STAGE0_IDENTIFIABLE_DEV_ONLY_NOT_SCIENCE" if eligible
                        else "SOURCE_ENTITY_IDENTIFIABILITY_NO_GO"),
    }


def consumed_episode(factory, family, seed):
    env = factory()
    actor = BoundedPublicNoveltyExplorer(seed)
    sensor = PublicViewLocalDelta()
    previous_raw = None
    cross_matches = 0
    same_matches = 0
    ambiguous_frames = 0
    steps = 0
    trace = sha256()
    start = time.process_time_ns()
    try:
        obs, _ = env.reset(seed=seed)
        sensor.prime(obs["image"])
        for tick in range(256):
            before_image = obs["image"]
            raw = public_raw_view(before_image)
            old_bits = tuple(sensor.bits)
            # CURRENT preaction match sees only previous and current public raw.
            matches = correspondences(previous_raw, raw)
            cross = cross_position_headroom(previous_raw, raw)
            if cross != sum(m is not None and m[1] != i
                            for i, m in enumerate(matches)):
                raise ValueError("ST2_STAGE0_HEADROOM_MATCH_DRIFT")
            cross_matches += cross
            same_matches += sum(m is not None and m[1] == i
                                for i, m in enumerate(matches))
            if previous_raw is not None and all(m is None for m in matches):
                ambiguous_frames += 1
            # The actor is independently frozen and receives full PUBLIC
            # observation only; no model predictions or labels.
            action = actor.choose(before_image)
            next_obs, _reward, terminated, truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(action, next_obs["image"])
            after_image = next_obs["image"]
            next_raw = public_raw_view(after_image)
            target = [int(raw[3*i:3*i+3] != next_raw[3*i:3*i+3])
                      for i in range(8)]
            if (event["observed_action"] != action or
                event["prior_local_bits"] != list(old_bits) or
                event["observed_next_local_bits"] != target or
                event["source_commit"] != SOURCE_COMMIT or
                actor.actions[action] < 1):
                raise ValueError("ST2_STAGE0_ORIGINAL_ACTION_OUTCOME_DRIFT")
            trace.update(bytes((action, *old_bits, *target)))
            trace.update(sha256(before_image.tobytes()).digest())
            trace.update(sha256(after_image.tobytes()).digest())
            # Update history ONLY after the true step, for next tick.
            previous_raw = raw
            actor.observe_original_next_public_image(action, after_image)
            actor.validate()
            obs = next_obs
            steps += 1
            if terminated or truncated:
                break
        if steps <= 0:
            raise ValueError("ST2_STAGE0_ZERO_SOURCE_ACTIONS")
        return {
            "family": family, "seed": seed,
            "previously_consumed_adaptation_only": True,
            "source_steps": steps,
            "unambiguous_cross_position_preaction_matches": cross_matches,
            "unambiguous_same_position_matches": same_matches,
            "frames_without_public_correspondence": ambiguous_frames,
            "original_action_outcome_sha256": trace.hexdigest(),
            "whole_episode_process_cpu_ns": time.process_time_ns() - start,
            "future_public_frame_used_for_preaction_correspondence": False,
            "candidate_or_held_prediction_executed": False,
        }
    finally:
        env.close()


def run(upstream, output):
    started = time.perf_counter_ns()
    _, root = protocol_preflight(upstream)
    sys.path.insert(0, str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories = {
        FAMILIES[0]: lambda: DoorKeyEnv(size=8, render_mode=None),
        FAMILIES[1]: lambda: EmptyEnv(size=8, render_mode=None),
    }
    receipts = []
    counts = {family: {} for family in FAMILIES}
    for family in FAMILIES:
        for seed in SEEDS:
            receipt = consumed_episode(factories[family], family, seed)
            receipts.append(receipt)
            counts[family][seed] = (
                receipt["unambiguous_cross_position_preaction_matches"]
            )
    verdict = headroom_verdict(counts)
    source_guard(root)
    out = {
        "schema": "yggdrasil.nci04.st2.stage0.consumed-source-headroom.v1",
        "frozen_protocol_blob": CONTRACT_BLOB,
        "prereg_commit": PREREG_SHA,
        "original_source_sha": SOURCE_COMMIT,
        "source_actor_blob": ACTOR_BLOB,
        "source_adapter_blob": ADAPTER_BLOB,
        "families": list(FAMILIES),
        "seed_group": list(SEEDS),
        "source_receipts": receipts,
        "headroom": verdict,
        "no_protected_first_use": True,
        "candidate_inference_or_training": False,
        "same_source_actor_and_public_adapter": True,
        "science_admission": "NOT_QUALIFIED",
        "held_evaluation_authorized_by_this_script": False,
        "whole_process_elapsed_ns": time.perf_counter_ns() - started,
    }
    output.write_text(
        json.dumps(out, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n", encoding="utf-8"
    )
    print("ST2_STAGE0_TOTAL_CROSS_POSITION=" +
          str(verdict["cross_position_total"]))
    for family in FAMILIES:
        print("ST2_STAGE0_FAMILY=" + family + " COUNTS=" +
              json.dumps(counts[family], sort_keys=True))
    print("ST2_STAGE0_DISPOSITION=" + verdict["disposition"])
    print("ST2_STAGE0_NO_FIRST_USE=PASS")
    print("ST2_STAGE0_RESULT_SHA256=" +
          sha256(output.read_bytes()).hexdigest())
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("original_source")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.original_source, args.output)
