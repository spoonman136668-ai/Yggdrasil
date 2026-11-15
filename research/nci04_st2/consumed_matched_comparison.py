"""ST2 authentic previously-consumed DEV trial; matched original-world controls.

All forecasts are made BEFORE original Farama env.step; a source-independent
actor sees only public frames. This is NOT reserved scientific first-use.
This runner refuses a candidate held comparison if frozen stage-0 identifiability
does not qualify. The Linux-built training checkpoint is byte-identical across
operating systems; trained-from-scratch Windows equality is NOT claimed.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import psutil

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard
from research.mr18.native_public_learning import Recurrent45, Native45, PublicCount
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_s1.original_native_messages import (
    models_new, native_episode
)
from research.nci04_st2.event_memory import (
    EventGroundedMemory45, correspondences, canonical
)
from research.nci04_st2.matched_controls import (
    FixedCameraCount45, RecurrentDelta45, shuffled_prediction, brier
)
from research.nci04_st2.stage0_consumed_headroom import (
    FAMILIES, SEEDS, protocol_preflight, headroom_verdict, consumed_episode
)

TRAIN = (263, 269, 271, 277, 281, 283, 293, 307)
HELD = (853, 857, 859)
COHORT = (*SEEDS, *HELD)
NAMES = (
    "candidate", "fixed_camera", "shuffled_track", "episodic_erasure",
    "frozen_s1_ring", "recurrent_delta45", "recurrent45",
    "memoryless45", "unmatched_public_count"
)
SCHEMA = "yggdrasil.nci04.st2.consumed-matched-comparison.v1"
CHECKPOINT_SCHEMA = "yggdrasil.nci04.st2.single-os-trained-checkpoint.v1"
PROCESS = psutil.Process()


def factories():
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    return {
        FAMILIES[0]: lambda: DoorKeyEnv(size=8, render_mode=None),
        FAMILIES[1]: lambda: EmptyEnv(size=8, render_mode=None),
    }


def source_trace_step(trace, action, bits, target, before, after):
    trace.update(bytes((action, *bits, *target)))
    trace.update(sha256(before.tobytes()).digest())
    trace.update(sha256(after.tobytes()).digest())


def train_delta_episode(make, family, seed, delta):
    env = make()
    actor = BoundedPublicNoveltyExplorer(seed)
    sensor = PublicViewLocalDelta()
    delta.reset_episode()
    digest = sha256()
    steps = 0
    try:
        obs, _ = env.reset(seed=seed)
        sensor.prime(obs["image"])
        for tick in range(256):
            image = obs["image"]
            raw, bits = public_raw_view(image), tuple(sensor.bits)
            action = actor.choose(image)
            next_obs, _reward, done, truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(action, next_obs["image"])
            target = event["observed_next_local_bits"]
            after_raw = public_raw_view(next_obs["image"])
            if (target != [
                    int(raw[3*i:3*i+3] != after_raw[3*i:3*i+3])
                    for i in range(8)
                ] or event["source_commit"] != SOURCE_COMMIT or
                event["observed_action"] != action):
                raise ValueError("ST2_TRAIN_DELTA_SOURCE_DRIFT")
            source_trace_step(digest, action, bits, target,
                              image, next_obs["image"])
            delta.observe(raw, bits, action, target, train=True)
            actor.observe_original_next_public_image(action, next_obs["image"])
            actor.validate()
            steps += 1
            obs = next_obs
            if done or truncated:
                break
        return (family, seed, steps, digest.hexdigest())
    finally:
        env.close()


def build_training_checkpoint(upstream, output):
    p, root = protocol_preflight(upstream)
    if p["source"]["training_previously_consumed"] != list(TRAIN):
        raise ValueError("ST2_TRAIN_FROZEN_SEED_DRIFT")
    sys.path.insert(0, str(root))
    builders = factories()
    original = models_new()
    delta = RecurrentDelta45()
    training = []
    independent_delta = []
    for family in FAMILIES:
        for seed in TRAIN:
            training.append(native_episode(
                builders[family], family, seed, True,
                original, {"native_restart_checks": 0}
            ))
            independent_delta.append(train_delta_episode(
                builders[family], family, seed, delta
            ))
            prev = training[-1]
            if (prev["original_environment"], prev["seed"],
                prev["original_native_steps"],
                prev["source_original_public_history_sha256"]) != independent_delta[-1]:
                raise ValueError("ST2_DELTA_TRAIN_ORIGINAL_ACTOR_NOT_PAIRED")
    chk = {
        "schema": CHECKPOINT_SCHEMA,
        "original_source_sha": SOURCE_COMMIT,
        "frozen_protocol_blob": "e7417272ddb9ffb6af183b23ddd78512cde93399",
        "training_seeds": list(TRAIN),
        "source_episode_receipts": [
            {"family": row["original_environment"], "seed": row["seed"],
             "steps": row["original_native_steps"],
             "trace_sha256": row["source_original_public_history_sha256"]}
            for row in training
        ],
        "s1": original["s1_messages"].snapshot(),
        "recurrent45": original["conventional_recurrent"].snapshot(),
        "memoryless45": original["conventional_memoryless"].snapshot(),
        "public_count": original["public_count_unmatched"].snapshot(),
        "recurrent_delta45": delta.snapshot(),
        "additional_new_conventional_coefficients": 45,
        "candidate_extra_neural_coefficients": 0,
        "protected_first_use": False,
    }
    content = canonical(chk) + "\n"
    output.write_text(content, encoding="utf-8")
    print("ST2_TRAIN_ONLY_SOURCE_EPISODES=" + str(len(training)))
    print("ST2_FROZEN_TRAINING_CHECKPOINT_SHA256=" +
          sha256(output.read_bytes()).hexdigest())
    return chk


def read_training_checkpoint(path):
    data = path.read_bytes()
    c = json.loads(data)
    if (len(data) > 1000000 or c.get("schema") != CHECKPOINT_SCHEMA or
        c.get("original_source_sha") != SOURCE_COMMIT or
        c.get("training_seeds") != list(TRAIN) or
        c.get("frozen_protocol_blob") !=
            "e7417272ddb9ffb6af183b23ddd78512cde93399" or
        c.get("protected_first_use") is not False or
        c.get("candidate_extra_neural_coefficients") != 0 or
        c.get("additional_new_conventional_coefficients") != 45 or
        len(c.get("source_episode_receipts", [])) != 16 or
        data.decode("utf-8") != canonical(c) + "\n"):
        raise ValueError("ST2_TRAINED_CHECKPOINT_IDENTITY_INVALID")
    LocalPredictiveMessages45.restore(c["s1"])
    Recurrent45.restore(c["recurrent45"])
    Native45.restore("public", c["memoryless45"])
    RecurrentDelta45.restore(c["recurrent_delta45"])
    return c, sha256(data).hexdigest()


def restore_unmatched_count(snapshot):
    model = PublicCount()
    for row in json.loads(snapshot):
        if (type(row) is not list or len(row) != 7 or
            type(row[2]) is not list or len(row[2]) != 3):
            raise ValueError("ST2_BAD_UNMATCHED_COUNT")
        key = (row[0], row[1], tuple(row[2]), row[3], row[4])
        model.table[key] = (row[5], row[6])
    if model.snapshot() != snapshot:
        raise ValueError("ST2_UNMATCHED_COUNT_RESTORE_DRIFT")
    return model


def family_models(checkpoint):
    s1 = checkpoint["s1"]
    return {
        "candidate": EventGroundedMemory45(s1),
        "fixed": FixedCameraCount45(s1),
        "shuffle": EventGroundedMemory45(s1),
        "erase": EventGroundedMemory45(s1),
        "ring": LocalPredictiveMessages45.restore(s1),
        "delta": RecurrentDelta45.restore(checkpoint["recurrent_delta45"]),
        "recurrent": Recurrent45.restore(checkpoint["recurrent45"]),
        "memoryless": Native45.restore("public", checkpoint["memoryless45"]),
        "unmatched": restore_unmatched_count(checkpoint["public_count"]),
    }


def original_episode(make, family, seed, phase, models, core_sha):
    env = make()
    actor, sensor = BoundedPublicNoveltyExplorer(seed), PublicViewLocalDelta()
    for name in ("candidate", "fixed", "shuffle", "erase", "ring",
                 "delta", "recurrent"):
        models[name].reset_episode()
    # The erasure control deliberately loses prior episode's learned counts.
    if phase != "adapt":
        models["erase"] = EventGroundedMemory45(models["candidate"].native.snapshot())
        models["erase"].reset_episode()
    else:
        models["erase"] = EventGroundedMemory45(models["candidate"].native.snapshot())
        models["erase"].reset_episode()
    trace = sha256()
    state_chain = sha256()
    sums = {name: 0.0 for name in NAMES}
    seen = 0
    source_steps = 0
    updates = 0
    model_cpu_ns = 0
    actor_cpu_ns = 0
    process_rss = PROCESS.memory_info().rss
    cold_checks = 0
    try:
        obs, _ = env.reset(seed=seed)
        sensor.prime(obs["image"])
        for t in range(256):
            image = obs["image"]
            raw, bits = public_raw_view(image), tuple(sensor.bits)
            ts = time.process_time_ns()
            action = actor.choose(image)
            actor_cpu_ns += time.process_time_ns() - ts
            ts = time.process_time_ns()
            pred = {
                "candidate": models["candidate"].predict(raw,bits,action),
                "fixed_camera": models["fixed"].predict(raw,bits,action),
                "shuffled_track": shuffled_prediction(
                    models["shuffle"],raw,bits,action),
                "episodic_erasure": models["erase"].predict(raw,bits,action),
                "frozen_s1_ring": models["ring"].predict(raw,bits,action),
                "recurrent_delta45": models["delta"].predict(raw,bits,action),
                "recurrent45": models["recurrent"].predict(raw,bits,action),
                "memoryless45": models["memoryless"].predict(raw,bits,action),
                "unmatched_public_count": models["unmatched"].predict(
                    raw,bits,action),
            }
            model_cpu_ns += time.process_time_ns() - ts
            nxt, _reward, terminated, truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(action, nxt["image"])
            next_raw = public_raw_view(nxt["image"])
            target = event["observed_next_local_bits"]
            if (event["source_commit"] != SOURCE_COMMIT or
                event["observed_action"] != action or
                event["prior_local_bits"] != list(bits) or
                target != [int(raw[3*i:3*i+3] != next_raw[3*i:3*i+3])
                          for i in range(8)]):
                raise ValueError("ST2_AUTHENTIC_ORIGINAL_SOURCE_DRIFT")
            if phase == "held":
                for name in NAMES:
                    sums[name] += brier(pred[name],target)
            old_counts = canonical(models["candidate"].counts)
            ts = time.process_time_ns()
            for name in ("candidate", "shuffle", "erase"):
                out = models[name].observe(
                    raw,bits,action,target,next_raw,train=True)
                if name != "shuffle" and out != pred[
                    "candidate" if name=="candidate" else "episodic_erasure"
                ]:
                    raise ValueError("ST2_PREACTION_FORECAST_LEAK")
            if models["fixed"].observe(raw,bits,action,target,next_raw) != pred["fixed_camera"]:
                raise ValueError("ST2_FIXED_PREACTION_FORECAST_LEAK")
            if models["ring"].observe(raw,bits,action,target,train=False) != pred["frozen_s1_ring"]:
                raise ValueError("ST2_RING_PREACTION_FORECAST_LEAK")
            if models["delta"].observe(raw,bits,action,target,train=False) != pred["recurrent_delta45"]:
                raise ValueError("ST2_DELTA_PREACTION_FORECAST_LEAK")
            models["recurrent"].advance_public_history(raw)
            model_cpu_ns += time.process_time_ns() - ts
            if canonical(models["candidate"].counts) != old_counts:
                updates += 1
            if models["candidate"].native.state != models["ring"].state:
                raise ValueError("ST2_ORIGINAL_S1_INFERENCE_STATE_DRIFT")
            if sha256(models["candidate"].native.runtime.core.snapshot().encode()).hexdigest() != core_sha:
                raise ValueError("ST2_FROZEN_ORIGINAL_WEIGHTS_MUTATED")
            payload = models["candidate"].snapshot()
            state_chain.update(sha256(payload.encode("utf-8")).digest())
            if t == 11:
                restored = EventGroundedMemory45.restore(payload)
                if restored.snapshot() != payload:
                    raise ValueError("ST2_PHYSICAL_COLD_RESTORE")
                models["candidate"] = restored
                cold_checks += 1
            source_trace_step(trace,action,bits,target,image,nxt["image"])
            actor.observe_original_next_public_image(action,nxt["image"])
            actor.validate()
            process_rss = max(process_rss, PROCESS.memory_info().rss)
            obs = nxt
            source_steps += 1
            seen += 1
            if terminated or truncated:
                break
        if source_steps < 1:
            raise ValueError("ST2_ZERO_SOURCE_ACTIONS")
        return {
            "family": family, "seed": seed, "phase": phase,
            "original_steps": source_steps,
            "source_trace_sha256": trace.hexdigest(),
            "candidate_state_sha_chain": state_chain.hexdigest(),
            "preaction_brier": {n:sums[n]/seen for n in NAMES}
                if phase == "held" else None,
            "candidate_count_update_actions": updates,
            "cold_restore_checks": cold_checks,
            "model_cpu_ns": model_cpu_ns,
            "policy_cpu_ns": actor_cpu_ns,
            "peak_process_rss_bytes": process_rss,
            "protected_source_used": False,
        }
    finally:
        env.close()


def evaluate(upstream, checkpoint_path, output):
    started = time.perf_counter_ns()
    p, root = protocol_preflight(upstream)
    if (p["source"]["held_dev_previously_consumed"] != list(HELD) or
        p["source"]["memory_adaptation_previously_consumed"] != list(SEEDS)):
        raise ValueError("ST2_EVAL_SEED_CONTRACT_DRIFT")
    checkpoint, checkpoint_sha = read_training_checkpoint(checkpoint_path)
    sys.path.insert(0, str(root))
    builds = factories()
    # Re-evaluate stage-0 BEFORE any candidate or held observation.
    eligibility = {f:{} for f in FAMILIES}
    stage0_traces = {}
    for f in FAMILIES:
        for seed in SEEDS:
            r = consumed_episode(builds[f],f,seed)
            eligibility[f][seed] = r["unambiguous_cross_position_preaction_matches"]
            stage0_traces[(f,seed)] = (
                r["source_steps"],r["original_action_outcome_sha256"]
            )
    headroom = headroom_verdict(eligibility)
    if not headroom["eligible"]:
        out = {"schema":SCHEMA,"stage0":headroom,
               "disposition":"SOURCE_ENTITY_IDENTIFIABILITY_NO_GO",
               "candidate_held_evaluated":False,
               "protected_scientific_first_use":False}
        output.write_text(canonical(out)+"\n",encoding="utf-8")
        print("ST2_MATCHED_DEV_DISPOSITION=SOURCE_ENTITY_IDENTIFIABILITY_NO_GO")
        return out
    results = {}
    core_sha = sha256(LocalPredictiveMessages45.restore(
        checkpoint["s1"]).runtime.core.snapshot().encode()).hexdigest()
    for f in FAMILIES:
        m = family_models(checkpoint)
        receipts = []
        for seed in COHORT:
            phase = "adapt" if seed in SEEDS else "held"
            r = original_episode(builds[f],f,seed,phase,m,core_sha)
            if phase == "adapt" and (
                r["original_steps"],r["source_trace_sha256"]
            ) != stage0_traces[(f,seed)]:
                raise ValueError("ST2_ADAPTATION_SOURCE_NOT_STAGE0_IDENTICAL")
            receipts.append(r)
        held = [r for r in receipts if r["phase"]=="held"]
        steps = sum(r["original_steps"] for r in held)
        if steps == 0:
            raise ValueError("ST2_ZERO_HELD_STEPS")
        avg = {
            n: sum(r["original_steps"]*r["preaction_brier"][n]
                   for r in held)/steps for n in NAMES
        }
        winning_resets = sum(
            r["preaction_brier"]["candidate"] <
            min(r["preaction_brier"]["fixed_camera"],
                r["preaction_brier"]["shuffled_track"])
            for r in held
        )
        checks = {
            "beats_fixed_camera_by_0_001":
                avg["candidate"] <= avg["fixed_camera"] - .001,
            "beats_frozen_shuffled_by_0_001":
                avg["candidate"] <= avg["shuffled_track"] - .001,
            "beats_controls_on_two_of_three_held_resets":
                winning_resets >= 2,
            "no_worse_than_original_s1_ring":
                avg["candidate"] <= avg["frozen_s1_ring"],
            "no_worse_than_training_matched_delta45":
                avg["candidate"] <= avg["recurrent_delta45"],
            "nonzero_real_consequence_updates":
                sum(r["candidate_count_update_actions"] for r in receipts) > 0,
            "one_physical_cold_restore_per_original_episode":
                sum(r["cold_restore_checks"] for r in receipts) == len(COHORT),
        }
        results[f] = {
            "original_source_receipts": receipts,
            "held_source_steps": steps,
            "held_preaction_brier_lower_better": avg,
            "strict_held_resets_beating_both_matched_controls": winning_resets,
            "frozen_necessary_checks": checks,
            "candidate_checkpoint_bytes": m["candidate"].accounting()["checkpoint_bytes"],
            "fixed_camera_checkpoint_bytes": m["fixed"].accounting()["checkpoint_bytes"],
            "fixed_control_reserved_count_bytes": 192,
            "candidate_signature_bytes": 24,
            "matched_control_signature_padding_bytes": 24,
        }
    source_guard(root)
    in_family_pass = all(
        all(r["frozen_necessary_checks"].values()) for r in results.values()
    )
    out = {
        "schema": SCHEMA,
        "frozen_protocol_git_blob":
            "e7417272ddb9ffb6af183b23ddd78512cde93399",
        "original_source_sha": SOURCE_COMMIT,
        "single_linux_training_checkpoint_sha256":checkpoint_sha,
        "training_source_receipts": checkpoint["source_episode_receipts"],
        "stage0": headroom,
        "families": results,
        "within_os_frozen_criteria_pass": in_family_pass,
        "cross_os_exact_action_and_candidate_checkpoint_parity": "PENDING_COMPARISON",
        "complete_resource_or_trainable_capacity_equality": False,
        "unfamiliar_world_transfer": False,
        "protected_scientific_first_use": False,
        "scientific_admission": "NOT_QUALIFIED",
        "development_disposition": ("DEV_SIGNAL_NOT_SCIENCE_NEEDS_CROSS_OS"
                                    if in_family_pass else "NO_GO"),
        "worker_total_wall_ns":time.perf_counter_ns()-started,
        "all_post_outcome_thresholds_unchanged":True,
    }
    output.write_text(canonical(out)+"\n",encoding="utf-8")
    for f, r in results.items():
        print("ST2_MATCHED_DEV_FAMILY="+f+" BRIER="+
              canonical(r["held_preaction_brier_lower_better"]))
        print("ST2_MATCHED_DEV_FAMILY_CHECKS="+f+" "+canonical(
            r["frozen_necessary_checks"]))
    print("ST2_MATCHED_DEV_DISPOSITION="+out["development_disposition"])
    print("ST2_PROTECTED_SCIENCE_NOT_RUN=PASS")
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    sub=a.add_subparsers(dest="mode",required=True)
    tr=sub.add_parser("train")
    tr.add_argument("original_source")
    tr.add_argument("--output",type=Path,required=True)
    ev=sub.add_parser("compare")
    ev.add_argument("original_source")
    ev.add_argument("--checkpoint",type=Path,required=True)
    ev.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    if args.mode == "train":
        build_training_checkpoint(args.original_source,args.output)
    else:
        evaluate(args.original_source,args.checkpoint,args.output)
