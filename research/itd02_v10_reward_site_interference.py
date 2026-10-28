"""V10: preregistered, source-only native output-cell credit isolation.

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
FAMILIES = tuple(range(240, 246))
SEEDS = (1181, 1193)
PHASE_STEPS = 48
VARIANTS = ("full8", "reward3", "count_mean", "ema_half", "rolling_six")
SOURCE_REFS = {
    "full8": "658b855d1b217d20ed9d431fe99b2e866469b7e9",
    "reward3": "658b855d1b217d20ed9d431fe99b2e866469b7e9",
}
PERMS = tuple(itertools.permutations(ACTIONS))
assert len(PERMS) == 6 and len(VARIANTS) == 5

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def laws(family):
    assert family in FAMILIES
    a, b, c = PERMS[family - 240]
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


def reward3_accept(actor, action, reward):
    """Temporarily mask the ORIGINAL public native observe invocation.

    No new native implementation, local genome or accepted source is edited.
    Each genuinely chosen action still creates one native core event.
    """
    native = actor.native
    if "observe" in native.__dict__:
        raise RuntimeError("UNEXPECTED_NATIVE_OBSERVE_OVERRIDE")
    from yggdrasil.developmental import valid
    from yggdrasil.itd02_local_ring_memory_dev import ACTION_SITES
    def selected_output_sites(bits, outcomes, rate=.035):
        valid(bits)
        valid(outcomes)
        if native.damaged or len(ACTION_SITES) != 3 or tuple(ACTION_SITES) != (0, 2, 5):
            raise ValueError("NATIVE_CUSTODY_OR_SOURCE_TOPOLOGY_DRIFT")
        before = native.core.events
        for site in ACTION_SITES:
            native.core.train_cell(bits, site, outcomes[site], rate)
        # One original public action has one learning event, not three.
        assert native.core.events == before + len(ACTION_SITES)
        native.core.events = before + 1
    native.observe = selected_output_sites
    try:
        actor.accept_public_transition(action, "Nothing", reward,
                                       learning=True, terminal=True)
    finally:
        if "observe" in native.__dict__:
            del native.observe

def first_public_gradient_diagnostic(actor, action, obs, reward, native_class):
    """Paired counterfactual source-free clones, never acting or giving feedback."""
    from yggdrasil.itd02_native_task_bridge_dev import (
        _temporal_public_bits, public_outcome
    )
    immutable_actor = actor.checkpoint()
    full = native_class.restore(immutable_actor)
    masked = native_class.restore(immutable_actor)
    bits = _temporal_public_bits(obs, action, actor.transitions % 2)
    target = public_outcome("Nothing", reward)
    before = full.native.predict(bits)
    full.accept_public_transition(action,"Nothing",reward,learning=True,terminal=True)
    reward3_accept(masked, action, reward)
    a = full.native.predict(bits)
    b = masked.native.predict(bits)
    assert actor.checkpoint() == immutable_actor, "CAUSAL_PROBE_TOUCHED_ACTING_MODEL"
    assert full.native.core.events == masked.native.core.events == actor.native.core.events+1
    output = (0,2,5)
    other = (1,3,4,6,7)
    return {
        "reward_output_mae_full8":sum(abs(target[i]-a[i]) for i in output)/3,
        "reward_output_mae_reward3":sum(abs(target[i]-b[i]) for i in output)/3,
        "nonreward_cell_mean_abs_shift_full8":sum(abs(a[i]-before[i]) for i in other)/5,
        "nonreward_cell_mean_abs_shift_reward3":sum(abs(b[i]-before[i]) for i in other)/5,
        "full8_genome_delta":sum(abs(x-y) for row0,row1 in zip(
            full.native.core.genome,actor.native.core.genome) for x,y in zip(row0,row1)),
        "reward3_genome_delta":sum(abs(x-y) for row0,row1 in zip(
            masked.native.core.genome,actor.native.core.genome) for x,y in zip(row0,row1)),
    }

def self_test(root):
    sys.path.insert(0,str(root))
    from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
    raw = NativeTaskRingBridgeDev()
    expected=raw.native.core.events
    roles=[list(row) for row in raw.native.core.roles]
    raw.start_observation("LRV")
    state=raw.checkpoint()
    reward3_accept(raw, "GoForward", 10)
    assert raw.native.core.events == expected+1 and raw.transitions==1
    assert raw.memory.updates==1
    assert "observe" not in raw.native.__dict__
    assert all(raw.native.core.roles[i] == roles[i] for i in (1,3,4,6,7))
    assert raw.native.core.genome != NativeTaskRingBridgeDev().native.core.genome
    external_restore(raw.checkpoint(),root)
    clone=NativeTaskRingBridgeDev.restore(state)
    assert clone.native.core.events==expected and clone.memory.pending
    gradient=first_public_gradient_diagnostic(clone,"GoForward","LRV",10,NativeTaskRingBridgeDev)
    assert set(gradient)=={
        "reward_output_mae_full8","reward_output_mae_reward3",
        "nonreward_cell_mean_abs_shift_full8",
        "nonreward_cell_mean_abs_shift_reward3",
        "full8_genome_delta","reward3_genome_delta"}
    assert all(0<=v<100 for v in gradient.values())
    print("ITD02_V10_NATIVE_ORIGINAL_SOURCE_MASKED_PUBLIC_CREDIT_SELFCHECK_PASS")

def run_trial(variant, family, seed, native_class=None, root=None):
    law = laws(family)
    if native_class:
        actor = native_class()
        orig = actor.model_identities()
    else:
        actor = {"variant": variant, "rewards": {}, "visits": {}}
    result = {"family": family, "seed": seed, "rewards": {}, "frozen": {},
              "cold_restore_verified": {}, "checkpoint_bytes": {}, "updates": {},
              "native_identities": {}, "gradient_pair": {}}
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
                if t == 0:
                    result["gradient_pair"][phase] = first_public_gradient_diagnostic(
                        actor,action,obs,reward,native_class)
                if variant == "reward3":
                    reward3_accept(actor,action,reward)
                else:
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
        "schema": "ygg.itd02.v10.reward-site-interference.v1",
        "classification": "SOURCE_FREE_DEV_ONLY__SCIENCE_NOT_ACCEPTED",
        "variant": variant, "source_sha": SOURCE_REFS.get(variant),
        "families": list(FAMILIES), "seeds": list(SEEDS),
        "events_per_trial": 144,
        "selected_public_feedback_events": len(trials) * 144,
        "trials": trials,
        "gradient_pair_summary": ({phase:{measure: statistics.mean(
            x["gradient_pair"][phase][measure] for x in trials)
            for measure in trials[0]["gradient_pair"][phase]}
            for phase in PHASES} if native_class else None),
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
    print("ITD02_V10_REWARD_SITE_ARM="+json.dumps({
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
    best_native = "full8"
    best_conventional = max(("count_mean", "ema_half", "rolling_six"),
                            key=lambda x: by_name[x]["means"]["post_shift"])
    composite = by_name["reward3"]
    verdict = "DEVELOPMENT_NEGATIVE_OR_MIXED__NO_SCIENCE"
    primary = "post_shift"
    comparison = {
        "best_native_control": best_native, "best_conventional": best_conventional,
        "reward3_minus_full8_post_shift":
            composite["means"][primary] - by_name[best_native]["means"][primary],
        "reward3_minus_best_conventional_post_shift":
            composite["means"][primary] - by_name[best_conventional]["means"][primary],
    }
    if (composite["phase_earned_mean"]["unfamiliar"] >
            max(by_name[best_native]["phase_earned_mean"]["unfamiliar"],
                by_name[best_conventional]["phase_earned_mean"]["unfamiliar"])
            and composite["phase_earned_mean"]["shift"] >
            max(by_name[best_native]["phase_earned_mean"]["shift"],
                by_name[best_conventional]["phase_earned_mean"]["shift"])
            and composite["phase_earned_mean"]["initial"] >=
            by_name[best_native]["phase_earned_mean"]["initial"]
            and composite["max_checkpoint_bytes"] <
            1.2 * by_name[best_native]["max_checkpoint_bytes"]):
        verdict = "SOURCE_FREE_DEVELOPMENT_SIGNAL_ONLY__NO_SCIENCE"
    results = {"schema": "ygg.itd02.v10.reward-site-interference-aggregate.v1",
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
               "gradient_pairs": {d["variant"]: d["gradient_pair_summary"]
                                  for d in docs if d["gradient_pair_summary"] is not None},
               "retail_pc_evidence": False, "scientific_first_use_authorized": False,
               "promotion_authorized": False}
    output.write_bytes(canon(results) + b"\n")
    print("ITD02_V10_REWARD_SITE_AGGREGATE="+json.dumps(results, sort_keys=True))
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--aggregate", type=Path)
    arg = parser.parse_args()
    if arg.self_test:
        assert arg.root and not arg.variant and not arg.aggregate and not arg.output
        self_test(arg.root.resolve())
    elif arg.aggregate:
        assert not arg.variant and not arg.root and arg.output
        aggregate(arg.aggregate, arg.output)
    else:
        assert arg.variant and arg.output and (arg.variant not in SOURCE_REFS or arg.root)
        run_worker(arg.variant, arg.root.resolve() if arg.root else None, arg.output)

if __name__ == "__main__":
    main()
