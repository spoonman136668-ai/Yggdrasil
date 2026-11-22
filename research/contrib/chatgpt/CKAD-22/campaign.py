"""Frozen CKAD22 continuation with an online candidate in the existing learner."""

import argparse
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = HERE.parent / "CKAD-21"
GENERATOR = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(ROOT))

# Exact rational metrics from the pinned, bounded campaign may have large
# denominators. The model's production checkpoint already uses hexadecimal.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


BASE = load_module("ckad21_qualified_campaign", PARENT / "campaign.py")
REFERENCE = load_module("ckad22_exact_control", HERE / "independent_audit.py")
LEGACY = BASE.LEGACY
VIEWS = BASE.VIEWS
BITS = BASE.BITS
TERMINAL_HISTORIES = BASE.TERMINAL_HISTORIES
ARMS = (
    "novel_active", "novel_random", "retrieval_only", "pooled_replay",
    "beta", "trailing_mle", "exact_mixture", "frozen_ckad21",
)

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner


def check(condition, reason):
    if not condition:
        raise RuntimeError(f"CKAD22: {reason}")


def event_id(cohort, seed, index, arm):
    return digest(canonical(["ckad22", EXPERIENCE_SOURCE, cohort, seed, index, arm]))


def random_actions(cohort, stream, seed, index):
    key = f"ckad22/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")
    draw = bytes.fromhex(digest(key))
    return draw[0] & 1, draw[1] & 1


def adaptive_weight(model, mixture):
    native = model.info()["episode_experience"]["context"]["weights"][-1]
    check(Fraction(*native) == mixture.weights[-1], "adaptive candidate weight drift")
    return native


def acquire(models, retained, seed, session, world, count):
    cohort = f"ckad22-probe-{session}"
    mixture = REFERENCE.Mixture(retained, novel=True)
    parity = {"forecasts": 0, "decisions": 0, "mismatches": 0}
    for arm in ("novel_active", "novel_random", "retrieval_only"):
        models[arm] = models[arm].begin_experience_context(novel=(arm != "retrieval_only"))

    weights = [adaptive_weight(models["novel_active"], mixture)]
    for index in range(count):
        active = models["novel_active"]
        BASE.require_parity(active, mixture, parity)
        episode = BASE.make_episode(cohort=cohort, seed=seed, index=index, **world)
        views = BASE.public_views(episode)
        view = views[0]
        observed = BASE.rollout(
            episode,
            lambda _initial: active.experience_context_explore(view),
            lambda _initial, first, state: active.experience_context_explore(view, first, state),
        )
        identifier = event_id(cohort, seed, index, "active")
        for arm in ("novel_active", "retrieval_only", "pooled_replay"):
            models[arm] = BASE.admit(models[arm], identifier, views, observed)
        event = BASE.retain_event(identifier, views, observed)
        retained.append(event)
        mixture.add(event)
        weights.append(adaptive_weight(models["novel_active"], mixture))

        random_row = LEGACY.fixed_rollout(episode, random_actions(cohort, "probe-random", seed, index))
        random_id = event_id(cohort, seed, index, "random")
        models["novel_random"] = BASE.admit(models["novel_random"], random_id, views, random_row)

    active = models["novel_active"]
    BASE.require_parity(active, mixture, parity)
    context = active.info()["episode_experience"]["context"]
    check(context == mixture.info(), "independent posterior, windows or adaptive checkpoint drift")
    adaptive = mixture.models[-1].info()
    check(adaptive["count"] == count, "adaptive candidate may contain only witnessed session probes")
    return mixture, parity, {
        "weight_trace": weights, "training_episodes": adaptive["count"],
        "projection": adaptive["projection"], "transition_hypothesis": adaptive["transition_hypothesis"],
        "terminal_hypothesis": adaptive["terminal_hypothesis"],
        "checkpoint_sha256": context["novel_checkpoint_sha256"],
    }


def readouts(models, mixture, parent, retained):
    receipts = BASE.receipts_from_events(retained)
    beta = LEGACY.ConventionalControl(receipts)
    mle = LEGACY.ConventionalControl(receipts, mle=True)
    pooled = models["pooled_replay"]
    arms = {arm: (models[arm].experience_context_plan, models[arm].experience_context_forecast)
            for arm in ("novel_active", "novel_random", "retrieval_only")}
    arms.update({
        "pooled_replay": (pooled.experience_plan, pooled.experience_forecast),
        "beta": (beta.plan, beta.forecast), "trailing_mle": (mle.plan, mle.forecast),
        "exact_mixture": (mixture.plan, mixture.forecast),
        "frozen_ckad21": (parent.experience_context_plan, parent.experience_context_forecast),
    })
    return arms


def evaluate(models, mixture, parent, retained, seed, session, world, count):
    cohort = f"ckad22-held-{session}"
    estimates = {
        arm: (
            {view: plan(view) for view in VIEWS},
            {(view, first): forecast(view, first) for view in VIEWS for first in BITS},
            {(view, *h): forecast(view, *h) for view in VIEWS for h in TERMINAL_HISTORIES},
        )
        for arm, (plan, forecast) in readouts(models, mixture, parent, retained).items()
    }
    totals = {arm: [0, Fraction(), Fraction(), 0] for arm in ARMS}
    different_views = 0
    for index in range(count):
        episode = BASE.make_episode(cohort=cohort, seed=seed, index=index, **world)
        view, alternative = BASE.public_views(episode)
        different_views += view != alternative
        sample = LEGACY.fixed_rollout(episode, random_actions(cohort, "held-matched", seed, index))
        first, state, second, reward = (sample[key] for key in ("x1", "s2", "x2", "y"))
        for arm, (plans, transitions, terminals) in estimates.items():
            decision = LEGACY.planned_rollout(episode, plans[view])
            next_probability = transitions[view, first]
            reward_probability = terminals[view, first, state, second]
            total = totals[arm]
            total[0] += decision["y"]
            total[1] += (next_probability - state) ** 2
            total[2] += (reward_probability - reward) ** 2
            total[3] += int(next_probability != transitions[alternative, first]) + int(
                reward_probability != terminals[alternative, first, state, second]
            )

    scores = {
        arm: {"episodes": count, "reward_sum": reward_sum,
              "transition_brier": LEGACY.ratio(transition_loss / count),
              "terminal_brier": LEGACY.ratio(terminal_loss / count),
              "pooled_brier": LEGACY.ratio((transition_loss + terminal_loss) / (2 * count)),
              "view_disagreements": disagreements, "view_comparisons": 2 * count,
              "distinct_view_episodes": different_views}
        for arm, (reward_sum, transition_loss, terminal_loss, disagreements) in totals.items()
    }
    check(scores["novel_active"] == scores["exact_mixture"], "held exact mixture score drift")
    return scores


def preserve(models, prior_header, previous, initial_events, retained, count):
    states = {}
    for arm, model in models.items():
        raw = model.checkpoint()
        header, experience = BASE.legacy_and_experience(raw)
        check(header == prior_header, "legacy trained state mutated")
        events = experience["episodes"]
        prior_events = previous[arm]
        check(events[:len(initial_events)] == initial_events
              and events[:len(prior_events)] == prior_events, "historical witness prefix mutated")
        check(len(events) == len(prior_events) + count
              and len({event[0] for event in events}) == len(events), "probe count or identity drift")
        if arm != "novel_random":
            check(events == retained, "same-receipt arms diverged")
        previous[arm] = events
        pin = digest(raw)
        restored = NativeCumulativeLearner.restore(raw, pin)
        check(restored.checkpoint() == raw, "full saved-state roundtrip changed bytes")
        models[arm] = restored
        state = {"checkpoint_sha256": pin, "checkpoint_bytes": len(raw),
                 "experience": restored.info()["episode_experience"], "roundtrip_verified": True}
        if arm != "pooled_replay":
            reading = BASE.context_readout_pin(restored)
            check(reading == BASE.context_readout_pin(model), "cold readout drift")
            state["readout_sha256"] = reading
        states[arm] = state
    return states


def cold_check(args):
    path, pin, readout_pin = args
    started = time.process_time()
    sys.modules["scipy"] = None
    raw = Path(path).read_bytes()
    restored = NativeCumulativeLearner.restore(raw, pin)
    check(restored.checkpoint() == raw and BASE.context_readout_pin(restored) == readout_pin,
          "fresh-process full checkpoint or context readout drift")
    print(json.dumps({"sha256": pin, "readout_sha256": readout_pin,
                      "cpu_seconds": time.process_time() - started}, sort_keys=True))


def cold_proof(path, pin, readout_pin):
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--cold-check", str(path), pin, readout_pin]
    report = json.loads(subprocess.check_output(command, cwd=ROOT, timeout=90, text=True))
    check(report["sha256"] == pin and report["readout_sha256"] == readout_pin, "cold report drift")
    return report


def run_seed(seed, protocol, output):
    source_seed = seed + protocol["source_seed_offset"]
    name = f"seed-{seed}-context-native.json"
    path = PARENT / name
    if not path.exists():
        path = ROOT.parent / "ckad21-artifact" / name
    raw = path.read_bytes()
    pin = protocol["parent_pins"][str(seed)]
    parent = NativeCumulativeLearner.restore(raw, pin)
    check(parent.checkpoint() == raw, "qualified CKAD21 parent did not restore byte for byte")
    core, experience = BASE.legacy_and_experience(raw)
    initial_events = experience["episodes"]
    check(len(initial_events) == 320, "qualified parent must have 320 witnesses")
    retained = initial_events.copy()
    models = {arm: parent for arm in ("novel_active", "novel_random", "retrieval_only", "pooled_replay")}
    previous = dict.fromkeys(models, initial_events)
    budgets = protocol["budgets"]
    n_probes = budgets["probe_episodes_per_session_per_acquisition_arm"]
    n_held = budgets["held_episodes_per_session"]

    sessions = []
    for session, world in enumerate(protocol["sessions"]):
        mixture, parity, adaptive = acquire(models, retained, source_seed, session, world, n_probes)
        states = preserve(models, core, previous, initial_events, retained, n_probes)
        scores = evaluate(models, mixture, parent, retained, source_seed, session, world, n_held)
        check(all(digest(models[arm].checkpoint()) == s["checkpoint_sha256"] for arm, s in states.items()),
              "held scoring changed learned state")
        sessions.append({
            "session": session, **world, "probe_cohort": f"ckad22-probe-{session}",
            "held_cohort": f"ckad22-held-{session}", "states": states, "evaluation": scores,
            "training_episodes": len(retained), "parity": parity, "adaptive_candidate": adaptive,
        })

    check(len(retained) == 320 + budgets["sessions"] * n_probes <= budgets["max_ledger_episodes"],
          "cumulative witness or capacity accounting")
    name = f"seed-{seed}-expanded-native.json"
    final = sessions[-1]["states"]["novel_active"]
    raw = models["novel_active"].checkpoint()
    check(digest(raw) == final["checkpoint_sha256"], "final checkpoint drift")
    (output / name).write_bytes(raw)
    cold = cold_proof(output / name, final["checkpoint_sha256"], final["readout_sha256"])
    return {"seed": seed, "source_seed": source_seed, "parent_checkpoint_sha256": pin,
            "sessions": sessions, "final_checkpoint_name": name,
            "final_checkpoint_sha256": digest(raw), "cold": cold}


def mean_reward(seeds, sessions, arm):
    results = [seed["sessions"][n]["evaluation"][arm] for n in sessions for seed in seeds]
    return Fraction(sum(r["reward_sum"] for r in results), sum(r["episodes"] for r in results))


def development(seeds):
    novel = mean_reward(seeds, (0, 1), "novel_active")
    retrieval_delta = novel - mean_reward(seeds, (0, 1), "retrieval_only")
    mle_delta = novel - mean_reward(seeds, (0, 1), "trailing_mle")
    new_return = mean_reward(seeds, (2,), "novel_active")
    old_return = mean_reward(seeds, (3,), "novel_active")
    old_delta = old_return - mean_reward(seeds, (3,), "retrieval_only")
    gates = {
        "unfamiliar_vs_retrieval": retrieval_delta >= Fraction(1, 20),
        "unfamiliar_vs_mle": mle_delta >= 0,
        "returning_new_reward": new_return >= Fraction(4, 5),
        "returning_old_reward": old_return >= Fraction(4, 5),
        "returning_old_vs_retrieval": old_delta >= -Fraction(1, 20),
    }
    metrics = {
        "unfamiliar_reward": LEGACY.ratio(novel),
        "unfamiliar_delta_retrieval": LEGACY.ratio(retrieval_delta),
        "unfamiliar_delta_mle": LEGACY.ratio(mle_delta),
        "returning_new_reward": LEGACY.ratio(new_return),
        "returning_old_reward": LEGACY.ratio(old_return),
        "returning_old_delta_retrieval": LEGACY.ratio(old_delta),
    }
    return gates, metrics


def stable(result):
    return LEGACY.stable(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--verify-env", action="store_true")
    parser.add_argument("--cold-check", nargs=3, metavar=("path", "sha256", "readout_sha256"))
    args = parser.parse_args()
    if args.cold_check:
        cold_check(args.cold_check)
        return
    if args.output_directory is None:
        parser.error("--output-directory required")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    cpu_started = time.process_time()
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    check(digest(GENERATOR.read_bytes()) == protocol["source_sha256"] == EXPERIENCE_SOURCE,
          "frozen source generator pin")
    budgets = protocol["budgets"]
    check(len(protocol["sessions"]) == budgets["sessions"], "frozen session count")
    seeds = [run_seed(seed, protocol, output) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    stages = len(seeds) * budgets["sessions"]
    probe_rollouts = stages * 2 * budgets["probe_episodes_per_session_per_acquisition_arm"]
    held = stages * budgets["held_episodes_per_session"]
    parity = {
        key: sum(s["parity"][key] for seed in seeds for s in seed["sessions"])
        for key in ("forecasts", "decisions", "mismatches")
    }
    result = {
        "schema": "yggdrasil.ckad22.adaptive-context-development.result.v1",
        "classification": "DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO",
        "development_pass": passed, "development_gates": gates, "development_metrics": metrics,
        "source_candidate_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip(),
        "source_sha256": EXPERIENCE_SOURCE, "scientific_pass": False, "accepted_native": False,
        "deployment": "NONE", "seeds": seeds, "parity": parity,
        "final_checkpoints": [
            {"seed": seed["seed"], "name": seed["final_checkpoint_name"],
             "sha256": seed["final_checkpoint_sha256"],
             "bytes": seed["sessions"][-1]["states"]["novel_active"]["checkpoint_bytes"]}
            for seed in seeds
        ],
        "scope": {"probe_rollouts": probe_rollouts, "probe_synthetic_actions": 2 * probe_rollouts,
                  "matched_held_rollouts": held, "held_policy_rollouts": held * len(ARMS),
                  "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0},
        "whole_wall_seconds": time.monotonic() - started,
        "parent_cpu_seconds": time.process_time() - cpu_started,
        "child_cpu_seconds": sum(seed["cold"]["cpu_seconds"] for seed in seeds),
        "parent_peak_rss_bytes": LEGACY.parent_peak_rss(),
    }
    check(result["whole_wall_seconds"] < budgets["max_wall_seconds"], "frozen wall budget exceeded")
    result["stable_sha256"] = digest(stable(result))
    (output / "campaign-result.json").write_bytes(
        (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii"),
    )
    receipt = {"classification": result["classification"], "development_pass": passed,
               "stable_sha256": result["stable_sha256"]}
    line = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(line)
    if args.verify_env:
        check(receipt == json.loads(os.environ["CKAD22_EXPECTED_RESULT"]), "cross-platform result drift")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("result=" + line + "\n")


if __name__ == "__main__":
    main()
