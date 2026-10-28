"""V11: preregistered, all-eight-cell local calibration acting ablation.

Development synthetic source only. The law stays with the evaluator; actors
get public (observation, their own action reward) only. No original source,
no protected first use, no tuning on output, no scientific acceptance.
"""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tracemalloc

ACTIONS = ("TurnAround", "GoForward", "Backup")
OBS = ("LRV", "MRV", "docked_LRV", "docked_MRV")
PHASES = ("initial", "unfamiliar", "shift")
FAMILIES = tuple(range(260, 266))
SEEDS = (1237, 1277)
PHASE_STEPS = 48
VARIANTS = ("v8", "v11", "count_mean", "ema_half", "rolling_six")
SOURCE_REFS = {
    "v8": "658b855d1b217d20ed9d431fe99b2e866469b7e9",
    "v11": "c99145851681de375854cb89c1d4af185abf043b",
}
PERMS = tuple(itertools.permutations(ACTIONS))
assert len(PERMS) == 6 and len(VARIANTS) == 5

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def laws(family):
    assert family in FAMILIES
    a, b, c = PERMS[family - 260]
    return {
        "initial": {"LRV": a, "MRV": b},
        "unfamiliar": {"docked_LRV": b, "docked_MRV": c},
        "shift": {"LRV": c, "MRV": a},
    }

def observations(phase):
    return OBS[:2] if phase != "unfamiliar" else OBS[2:]

def earned(law, obs, action):
    return 10 if law[obs] == action else -3

def fitted_choice(actor, obs):
    scores = []
    for action in ACTIONS:
        key = obs + "|" + action
        history = actor["rewards"].get(key, [])
        if not history:
            scores.append(0.0)
        elif actor["variant"] == "ema_half":
            value = history[0]
            for r in history[1:]:
                value = .5 * value + .5 * r
            scores.append(value)
        elif actor["variant"] == "rolling_six":
            recent = history[-6:]
            scores.append(sum(recent) / len(recent))
        else:
            scores.append(sum(history) / len(history))
    return ACTIONS[max(range(3), key=lambda idx: scores[idx])]

def control_choose(actor, obs, seed):
    v = actor["visits"].get(obs, 0)
    if v < 3:
        action = ACTIONS[(v + seed) % 3]
    elif (v + 1) % 9 == 0:
        action = ACTIONS[(((v + seed) // 9) + seed) % 3]
    else:
        action = fitted_choice(actor, obs)
    actor["visits"][obs] = v + 1
    return action

def native_frozen_choices(model, labels, cls):
    raw = model.checkpoint()
    out = {}
    for observation in labels:
        probe = cls.restore(raw)
        ids = probe.model_identities()
        probe.start_frozen_evaluation(ids["native"], ids["memory"])
        probe.start_observation(observation)
        choice = probe.choose()
        assert probe.model_identities() == ids, "FROZEN_PARAMETER_CHANGE"
        out[observation] = choice
    assert raw == model.checkpoint(), "PROBE_MUTATED_FITTED_CHECKPOINT"
    return out

def external_restore(raw, root):
    script = ("import hashlib,sys;"
              "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev as N;"
              "b=sys.stdin.buffer.read(); m=N.restore(b);"
              "assert m.checkpoint()==b;"
              "print(hashlib.sha256(m.checkpoint()).hexdigest())")
    env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run((sys.executable, "-B", "-c", script),
                          input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=env, cwd=root, timeout=30, check=True)
    assert done.stdout.decode().strip() == hashlib.sha256(raw).hexdigest()
    return True

def run_trial(variant, family, seed, native_class=None, root=None):
    law = laws(family)
    if native_class:
        actor = native_class()
        orig = actor.model_identities()
    else:
        actor = {"variant": variant, "rewards": {}, "visits": {}}
    result = {"family": family, "seed": seed, "rewards": {}, "frozen": {},
              "cold_restore_verified": {}, "checkpoint_bytes": {}, "updates": {},
              "native_identities": {}, "site_residual_state": {}}
    for index, phase in enumerate(PHASES, 1):
        labels = observations(phase)
        score = 0
        for t in range(PHASE_STEPS):
            obs = labels[(t + seed) % 2]
            if native_class:
                actor.start_observation(obs)
                action = actor.choose()
            else:
                action = control_choose(actor, obs, seed)
            assert action in ACTIONS, "INVALID_ACTING_CHOICE"
            reward = earned(law[phase], obs, action)
            score += reward
            if native_class:
                actor.accept_public_transition(action, "Nothing", reward,
                                               learning=True, terminal=True)
            else:
                actor["rewards"].setdefault(obs + "|" + action, []).append(reward)
        result["rewards"][phase] = score
        if native_class:
            assert actor.transitions == index * PHASE_STEPS
            assert actor.memory.updates == actor.transitions
            assert actor.memory.pending is False and actor._observation is None
            raw = actor.checkpoint()
            assert len(raw) < 65536
            external_restore(raw, root)
            actor = native_class.restore(raw)
            result["cold_restore_verified"][phase] = True
            result["checkpoint_bytes"][phase] = len(raw)
            result["updates"][phase] = actor.transitions
            result["native_identities"][phase] = actor.model_identities()
            if variant == "v11":
                assert len(actor.site_residual) == 8
                assert all(-2. <= x <= 2. for x in actor.site_residual)
                result["site_residual_state"][phase] = list(actor.site_residual)
            frozen = native_frozen_choices(actor, OBS, native_class)
        else:
            raw = canon(actor)
            actor = json.loads(raw)
            assert canon(actor) == raw
            result["cold_restore_verified"][phase] = True
            result["checkpoint_bytes"][phase] = len(raw)
            result["updates"][phase] = index * PHASE_STEPS
            frozen = {obs: fitted_choice(actor, obs) for obs in OBS}
        if phase == "initial":
            # Unfamiliar labels have had zero source interactions so far.
            result["frozen"]["initial_seen"] = sum(
                earned(law["initial"], o, frozen[o]) for o in OBS[:2])
            result["frozen"]["zero_shot_unfamiliar"] = sum(
                earned(law["unfamiliar"], o, frozen[o]) for o in OBS[2:])
        elif phase == "unfamiliar":
            result["frozen"]["adapted_unfamiliar"] = sum(
                earned(law["unfamiliar"], o, frozen[o]) for o in OBS[2:])
            result["frozen"]["pre_shift"] = sum(
                earned(law["shift"], o, frozen[o]) for o in OBS[:2])
        else:
            result["frozen"]["post_shift"] = sum(
                earned(law["shift"], o, frozen[o]) for o in OBS[:2])
    if native_class:
        assert result["native_identities"]["shift"] != orig, "NO_NATIVE_LEARNING"
    return result

def run_worker(variant, root, output):
    assert variant in VARIANTS
    if output.exists():
        raise RuntimeError("REFUSE_OVERWRITE_EVIDENCE")
    native_class = None
    if variant in SOURCE_REFS:
        assert root and (root / ".git").exists(), "NATIVE_SOURCE_MISSING"
        sha = subprocess.check_output(("git", "rev-parse", "HEAD"),
                                      cwd=root, text=True).strip()
        assert sha == SOURCE_REFS[variant], "NATIVE_SOURCE_IDENTITY_DRIFT"
        sys.path.insert(0, str(root))
        from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
        native_class = NativeTaskRingBridgeDev
    tracemalloc.start()
    cpu = time.process_time()
    wall = time.perf_counter()
    trials = [run_trial(variant, family, seed, native_class, root)
              for family in FAMILIES for seed in SEEDS]
    elapsed_cpu = time.process_time() - cpu
    elapsed_wall = time.perf_counter() - wall
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    try:
        import resource
        highwater = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        highwater_units = "KiB on Ubuntu runner"
    except ImportError:
        highwater = None
        highwater_units = "unavailable on Windows; no guessed value"
    metrics = ("initial_seen", "zero_shot_unfamiliar", "adapted_unfamiliar",
               "pre_shift", "post_shift")
    phases = PHASES
    report = {
        "schema": "ygg.itd02.v11.cell-local-calibration.v1",
        "classification": "SOURCE_FREE_DEV_ONLY__SCIENCE_NOT_ACCEPTED",
        "variant": variant, "source_sha": SOURCE_REFS.get(variant),
        "families": list(FAMILIES), "seeds": list(SEEDS),
        "events_per_trial": 144,
        "selected_public_feedback_events": len(trials) * 144,
        "trials": trials,
        "means": {key: statistics.mean(x["frozen"][key] for x in trials)
                  for key in metrics},
        "phase_earned_mean": {key: statistics.mean(x["rewards"][key] for x in trials)
                              for key in phases},
        "max_checkpoint_bytes": max(max(x["checkpoint_bytes"].values())
                                    for x in trials),
        "cpu_seconds": elapsed_cpu, "wall_seconds": elapsed_wall,
        "peak_python_allocated_bytes": peak, "process_maxrss": highwater,
        "process_maxrss_units": highwater_units,
        "platform": sys.platform, "machine": os.environ.get("RUNNER_OS", "unknown"),
        "native_model_locality": variant in SOURCE_REFS,
        "retail_pc_resource_evidence": False,
        "protected_first_use": False, "promotion_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canon(report) + b"\n")
    print("ITD02_V11_CALIBRATION_ARM="+json.dumps({
        "variant": variant, "means": report["means"],
        "phase_earned_mean": report["phase_earned_mean"],
        "cpu_seconds": elapsed_cpu, "peak_alloc": peak,
        "events": report["selected_public_feedback_events"],
        "classification": report["classification"]}, sort_keys=True))
    return report

def aggregate(folder, output):
    if output.exists():
        raise RuntimeError("REFUSE_OVERWRITE_AGGREGATE")
    docs = [json.loads((folder / (v + ".json")).read_text("utf-8")) for v in VARIANTS]
    assert [x["variant"] for x in docs] == list(VARIANTS), "ACTOR_MISSING"
    assert all(x["selected_public_feedback_events"] == 1728
               and len(x["trials"]) == 12 for x in docs), "UNBALANCED_FEEDBACK"
    assert all(all(t["cold_restore_verified"].values())
               for d in docs for t in d["trials"]), "RESTORE_NOT_VERIFIED"
    keys = tuple((x["family"], x["seed"]) for x in docs[0]["trials"])
    assert all(tuple((x["family"], x["seed"]) for x in d["trials"]) == keys
               for d in docs), "UNMATCHED_FAMILIES"
    assert len(set(keys)) == 12
    by_name = {d["variant"]: d for d in docs}
    best_native = "v8"
    best_conventional = max(("count_mean", "ema_half", "rolling_six"),
                            key=lambda x: by_name[x]["means"]["post_shift"])
    composite = by_name["v11"]
    verdict = "DEVELOPMENT_NEGATIVE_OR_MIXED__NO_SCIENCE"
    primary = "post_shift"
    comparison = {
        "best_native_control": best_native, "best_conventional": best_conventional,
        "v11_minus_v8_post_shift":
            composite["means"][primary] - by_name[best_native]["means"][primary],
        "v11_minus_best_conventional_post_shift":
            composite["means"][primary] - by_name[best_conventional]["means"][primary],
    }
    strongest_acting = {
        p: max(by_name[c]["phase_earned_mean"][p]
               for c in ("count_mean", "ema_half", "rolling_six"))
        for p in PHASES
    }
    comparison["strongest_conventional_acting_by_phase"] = strongest_acting
    comparison["v11_minus_v8_unfamiliar_acting"] = (
        composite["phase_earned_mean"]["unfamiliar"] -
        by_name[best_native]["phase_earned_mean"]["unfamiliar"])
    comparison["v11_minus_v8_reversal_acting"] = (
        composite["phase_earned_mean"]["shift"] -
        by_name[best_native]["phase_earned_mean"]["shift"])
    comparison["v11_cpu_ratio_same_host"] = (
        composite["cpu_seconds"] / max(1.e-9, by_name[best_native]["cpu_seconds"]))
    comparison["v11_checkpoint_ratio"] = (
        composite["max_checkpoint_bytes"] / by_name[best_native]["max_checkpoint_bytes"])
    if (all(composite["phase_earned_mean"][p] >
            max(by_name[best_native]["phase_earned_mean"][p],
                strongest_acting[p])
            for p in ("unfamiliar", "shift"))
            and composite["phase_earned_mean"]["initial"] >=
            by_name[best_native]["phase_earned_mean"]["initial"]
            and all(composite["means"][p] >= by_name[best_native]["means"][p]
                for p in ("adapted_unfamiliar", "post_shift"))
            and comparison["v11_checkpoint_ratio"] <= 1.10
            and comparison["v11_cpu_ratio_same_host"] <= 1.25):
        verdict = "SOURCE_FREE_DEVELOPMENT_SIGNAL_ONLY__NO_SCIENCE"
    results = {"schema": "ygg.itd02.v11.cell-local-calibration-aggregate.v1",
               "classification": verdict, "source_free_only": True,
               "protected_science": "NOT_ACCEPTED",
               "all_families": list(FAMILIES), "seeds": list(SEEDS),
               "events_per_arm": 1728, "events_all_arms": 8640,
               "comparison": comparison,
               "means": {d["variant"]: d["means"] for d in docs},
               "phase_earned": {d["variant"]: d["phase_earned_mean"] for d in docs},
               "cpu_seconds": {d["variant"]: d["cpu_seconds"] for d in docs},
               "python_peak_bytes": {d["variant"]: d["peak_python_allocated_bytes"] for d in docs},
               "max_checkpoint_bytes": {d["variant"]: d["max_checkpoint_bytes"] for d in docs},
               "retail_pc_evidence": False, "scientific_first_use_authorized": False,
               "promotion_authorized": False}
    output.write_bytes(canon(results) + b"\n")
    print("ITD02_V11_CALIBRATION_AGGREGATE="+json.dumps(results, sort_keys=True))
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--aggregate", type=Path)
    arg = parser.parse_args()
    if arg.aggregate:
        assert not arg.variant and not arg.root
        aggregate(arg.aggregate, arg.output)
    else:
        assert arg.variant and (arg.variant not in SOURCE_REFS or arg.root)
        run_worker(arg.variant, arg.root.resolve() if arg.root else None, arg.output)

if __name__ == "__main__":
    main()
