"""Frozen CKAD21 context retrieval campaign from three complete CKAD20 models."""

import argparse
from fractions import Fraction
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CKAD20 = HERE.parent / "CKAD-20"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CKAD20))
sys.path.insert(0, str(HERE))

from independent_audit import Mixture
from synthetic_world import make_episode, public_views, rollout
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner


def load_legacy_controls():
    spec = importlib.util.spec_from_file_location("ckad20_frozen_campaign", CKAD20 / "campaign.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEGACY = load_legacy_controls()
BITS = (0, 1)
VIEWS = tuple(product(BITS, repeat=2))
TERMINAL_HISTORIES = tuple(product(BITS, repeat=3))
ARMS = (
    "context_active", "context_random", "pooled_replay", "beta",
    "trailing_mle", "exact_mixture", "frozen_ckad20", "untrained",
)


def check(condition, reason):
    if not condition:
        raise RuntimeError(f"CKAD21: {reason}")


def event_id(cohort, seed, index, arm):
    return digest(canonical(["ckad21", EXPERIENCE_SOURCE, cohort, seed, index, arm]))


def random_actions(cohort, stream, seed, index):
    key = f"ckad21/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")
    draw = bytes.fromhex(digest(key))
    return draw[0] & 1, draw[1] & 1


def legacy_and_experience(raw):
    state = json.loads(raw)
    experience = json.loads(state.pop("experience_ascii"))
    return state, experience


def receipts_from_events(events):
    return [(views, {"x1": first, "s2": state, "x2": second, "y": reward})
            for _, views, first, state, second, reward in events]


def retain_event(identifier, views, row):
    return [identifier, [list(v) for v in views], row["x1"], row["s2"], row["x2"], row["y"]]


def admit(model, identifier, views, row):
    return model.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=digest(canonical([identifier, views, row])),
    )


def forecast_table(forecast, view):
    transition = [forecast(view, action) for action in BITS]
    terminal = [forecast(view, *history) for history in TERMINAL_HISTORIES]
    return transition + terminal


def require_parity(model, mixture, counts):
    """Compare every public structural query, including hypothetical decisions as readouts."""
    for view in VIEWS:
        native = forecast_table(model.experience_context_forecast, view)
        reference = forecast_table(mixture.forecast, view)
        check(native == reference, "independent mixture probability drift")
        plan = model.experience_context_plan(view)
        expected = mixture.plan(view)
        check(canonical(plan) == canonical(expected), "independent mixture dream decision drift")
        counts["forecasts"] += len(native) + 2
        counts["decisions"] += 5
        for args in ((), *product(BITS, repeat=2)):
            check(model.experience_context_explore(view, *args) == mixture.explore(view, *args),
                  "independent mixture acquisition decision drift")
            counts["decisions"] += 1


def acquire(models, retained, seed, session, specification, count):
    cohort = f"ckad21-probe-{session}"
    mixture = Mixture(retained)
    parity = {"forecasts": 0, "decisions": 0, "mismatches": 0}
    for arm in ("context_active", "context_random"):
        models[arm] = models[arm].begin_experience_context()

    for index in range(count):
        active = models["context_active"]
        require_parity(active, mixture, parity)
        episode = make_episode(cohort=cohort, seed=seed, index=index, **specification)
        views = public_views(episode)
        view = views[0]
        active_row = rollout(
            episode,
            lambda _initial: active.experience_context_explore(view),
            lambda _initial, first, state: active.experience_context_explore(view, first, state),
        )
        active_id = event_id(cohort, seed, index, "active")
        models["context_active"] = admit(active, active_id, views, active_row)
        models["pooled_replay"] = admit(models["pooled_replay"], active_id, views, active_row)
        event = retain_event(active_id, views, active_row)
        retained.append(event)
        mixture.add(event)

        random_row = LEGACY.fixed_rollout(episode, random_actions(cohort, "probe-random", seed, index))
        random_id = event_id(cohort, seed, index, "random")
        models["context_random"] = admit(models["context_random"], random_id, views, random_row)

    require_parity(models["context_active"], mixture, parity)
    context = models["context_active"].info()["episode_experience"]["context"]
    check(context == mixture.info(), "independent context posterior or source window drift")
    return mixture, parity


def evaluators(models, mixture, parent, retained):
    evidence = receipts_from_events(retained)
    beta = LEGACY.ConventionalControl(evidence)
    mle = LEGACY.ConventionalControl(evidence, mle=True)
    active = models["context_active"]
    random = models["context_random"]
    pooled = models["pooled_replay"]
    return {
        "context_active": (active.experience_context_plan, active.experience_context_forecast),
        "context_random": (random.experience_context_plan, random.experience_context_forecast),
        "pooled_replay": (pooled.experience_plan, pooled.experience_forecast),
        "beta": (beta.plan, beta.forecast),
        "trailing_mle": (mle.plan, mle.forecast),
        "exact_mixture": (mixture.plan, mixture.forecast),
        "frozen_ckad20": (parent.experience_plan, parent.experience_forecast),
        "untrained": (lambda _view: {"first_action": 0, "second_actions": ((0, 0), (0, 0))},
                      lambda *_args: Fraction(1, 2)),
    }


def evaluate(models, mixture, parent, retained, seed, session, specification, count):
    cohort = f"ckad21-held-{session}"
    estimates = {}
    for arm, (plan, forecast) in evaluators(models, mixture, parent, retained).items():
        plans = {view: plan(view) for view in VIEWS}
        trans = {(view, first): forecast(view, first) for view in VIEWS for first in BITS}
        terminal = {(view, *h): forecast(view, *h) for view in VIEWS for h in TERMINAL_HISTORIES}
        estimates[arm] = plans, trans, terminal

    totals = {arm: [0, Fraction(0), Fraction(0), 0] for arm in ARMS}
    different_views = 0
    for index in range(count):
        episode = make_episode(cohort=cohort, seed=seed, index=index, **specification)
        view, alternative = public_views(episode)
        different_views += view != alternative
        sample = LEGACY.fixed_rollout(episode, random_actions(cohort, "held-matched", seed, index))
        first, state, second, target = (sample[key] for key in ("x1", "s2", "x2", "y"))
        for arm, (plans, transition, terminal) in estimates.items():
            result = LEGACY.planned_rollout(episode, plans[view])
            t = transition[view, first]
            r = terminal[view, first, state, second]
            total = totals[arm]
            total[0] += result["y"]
            total[1] += (t - state) ** 2
            total[2] += (r - target) ** 2
            total[3] += int(t != transition[alternative, first]) + int(
                r != terminal[alternative, first, state, second]
            )

    scores = {
        arm: {"episodes": count, "reward_sum": reward,
              "transition_brier": LEGACY.ratio(transition_loss / count),
              "terminal_brier": LEGACY.ratio(terminal_loss / count),
              "pooled_brier": LEGACY.ratio((transition_loss + terminal_loss) / (2 * count)),
              "view_disagreements": disagreements, "view_comparisons": 2 * count,
              "distinct_view_episodes": different_views}
        for arm, (reward, transition_loss, terminal_loss, disagreements) in totals.items()
    }
    check(scores["context_active"] == scores["exact_mixture"], "held exact mixture parity")
    return scores


def context_readout_pin(model):
    readings = []
    for view in VIEWS:
        p = [LEGACY.ratio(item) for item in forecast_table(model.experience_context_forecast, view)]
        actions = [model.experience_context_explore(view, *args)
                   for args in ((), *product(BITS, repeat=2))]
        readings.append([p, model.experience_context_plan(view), actions])
    return digest(canonical(readings))


def preserve(models, legacy, previous, initial_events, retained, budget):
    states = {}
    for arm, model in models.items():
        raw = model.checkpoint()
        header, experience = legacy_and_experience(raw)
        check(header == legacy, "legacy trained context changed")
        events = experience["episodes"]
        old_events = previous[arm]
        check(events[:len(old_events)] == old_events and events[:len(initial_events)] == initial_events,
              "retained public evidence changed")
        check(len(events) == len(old_events) + budget and len({item[0] for item in events}) == len(events),
              "probe count or identity drift")
        if arm != "context_random":
            check(events == retained, "same-evidence control drift")
        previous[arm] = events
        pin = digest(raw)
        restored = NativeCumulativeLearner.restore(raw, pin)
        check(restored.checkpoint() == raw, "saved training state continuation drift")
        # Use restored states for the next session, retaining all previous evidence.
        models[arm] = restored
        states[arm] = {
            "checkpoint_sha256": pin, "checkpoint_bytes": len(raw),
            "experience": restored.info()["episode_experience"], "roundtrip_verified": True,
        }
        if arm != "pooled_replay":
            check(context_readout_pin(model) == context_readout_pin(restored),
                  "context re-read after roundtrip changed planning")
            states[arm]["readout_sha256"] = context_readout_pin(restored)
    return states


def cold_check(arguments):
    path, pin, readout_pin = arguments
    sys.modules["scipy"] = None
    started = time.process_time()
    raw = Path(path).read_bytes()
    model = NativeCumulativeLearner.restore(raw, pin)
    check(model.checkpoint() == raw and context_readout_pin(model) == readout_pin,
          "fresh-process full-checkpoint or planner mismatch")
    print(json.dumps({"sha256": pin, "readout_sha256": readout_pin,
                      "cpu_seconds": time.process_time() - started}, sort_keys=True))


def verify_cold(path, pin, readout_pin):
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--cold-check", str(path), pin, readout_pin]
    proof = json.loads(subprocess.check_output(command, cwd=ROOT, timeout=75, text=True))
    check(proof["sha256"] == pin and proof["readout_sha256"] == readout_pin, "cold proof drift")
    return proof


def run_seed(seed, protocol, output):
    filename = f"seed-{seed}-unified-native.json"
    path = CKAD20 / filename
    if not path.exists():
        path = ROOT.parent / "ckad20-artifact" / filename
    raw = path.read_bytes()
    pin = protocol["parent_pins"][str(seed)]
    parent = NativeCumulativeLearner.restore(raw, pin)
    check(parent.checkpoint() == raw, "qualified CKAD20 state failed byte-exact restore")
    legacy, experience = legacy_and_experience(raw)
    original_events = experience["episodes"]
    check(len(original_events) == 224, "expected the accumulated 224-episode parent")
    retained = original_events.copy()
    models = {arm: parent for arm in ("context_active", "context_random", "pooled_replay")}
    previous = {arm: original_events for arm in models}
    budgets = protocol["budgets"]
    n_probes = budgets["probe_episodes_per_session_per_acquisition_arm"]
    n_held = budgets["held_episodes_per_session"]
    sessions = []
    for session, specification in enumerate(protocol["sessions"]):
        mixture, parity = acquire(models, retained, seed, session, specification, n_probes)
        states = preserve(models, legacy, previous, original_events, retained, n_probes)
        scores = evaluate(models, mixture, parent, retained, seed, session, specification, n_held)
        check(all(digest(models[arm].checkpoint()) == detail["checkpoint_sha256"]
                  for arm, detail in states.items()), "held evaluation changed trained state")
        sessions.append({
            "session": session, **specification, "probe_cohort": f"ckad21-probe-{session}",
            "held_cohort": f"ckad21-held-{session}", "states": states,
            "training_episodes": len(retained), "evaluation": scores, "parity": parity,
        })

    name = f"seed-{seed}-context-native.json"
    raw = models["context_active"].checkpoint()
    final_state = sessions[-1]["states"]["context_active"]
    check(digest(raw) == final_state["checkpoint_sha256"], "final state changed")
    (output / name).write_bytes(raw)
    cold = verify_cold(output / name, final_state["checkpoint_sha256"], final_state["readout_sha256"])
    check(len(retained) <= budgets["max_ledger_episodes"], "retained capacity exceeded")
    return {
        "seed": seed, "parent_checkpoint_sha256": pin, "sessions": sessions,
        "final_checkpoint_name": name, "final_checkpoint_sha256": digest(raw), "cold": cold,
    }


def mean_reward(seeds, indices, arm):
    rows = [item["sessions"][index]["evaluation"][arm] for index in indices for item in seeds]
    return Fraction(sum(row["reward_sum"] for row in rows), sum(row["episodes"] for row in rows))


def development(seeds):
    returning = mean_reward(seeds, (0, 3), "context_active")
    shifted = mean_reward(seeds, (1, 4), "context_active")
    delta_pooled = returning - mean_reward(seeds, (0, 3), "pooled_replay")
    delta_mle = returning - mean_reward(seeds, (0, 3), "trailing_mle")
    return {
        "returning_reward": returning >= Fraction(4, 5),
        "shifted_reward": shifted >= Fraction(4, 5),
        "returning_vs_pooled": delta_pooled >= Fraction(1, 20),
        "returning_vs_mle": delta_mle >= 0,
    }, {
        "returning_reward": LEGACY.ratio(returning),
        "shifted_reward": LEGACY.ratio(shifted),
        "returning_delta_pooled": LEGACY.ratio(delta_pooled),
        "returning_delta_mle": LEGACY.ratio(delta_mle),
        "terminal_switch_reward": LEGACY.ratio(mean_reward(seeds, (5,), "context_active")),
    }


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
    check(digest((CKAD20 / "synthetic_world.py").read_bytes()) ==
          protocol["source_sha256"] == EXPERIENCE_SOURCE, "frozen world source mismatch")
    budgets = protocol["budgets"]
    check(len(protocol["sessions"]) == budgets["sessions"], "frozen session count drift")
    seeds = [run_seed(seed, protocol, output) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    stages = len(seeds) * budgets["sessions"]
    probe_rollouts = stages * 2 * budgets["probe_episodes_per_session_per_acquisition_arm"]
    matched_held_rollouts = stages * budgets["held_episodes_per_session"]
    parity = {
        key: sum(s["parity"][key] for seed in seeds for s in seed["sessions"])
        for key in ("forecasts", "decisions", "mismatches")
    }
    result = {
        "schema": "yggdrasil.ckad21.context-retrieval.result.v1",
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
             "bytes": seed["sessions"][-1]["states"]["context_active"]["checkpoint_bytes"]}
            for seed in seeds
        ],
        "scope": {"probe_rollouts": probe_rollouts, "probe_synthetic_actions": 2 * probe_rollouts,
                  "matched_held_rollouts": matched_held_rollouts, "held_policy_rollouts": matched_held_rollouts * len(ARMS),
                  "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0},
        "whole_wall_seconds": time.monotonic() - started,
        "parent_cpu_seconds": time.process_time() - cpu_started,
        "child_cpu_seconds": sum(seed["cold"]["cpu_seconds"] for seed in seeds),
        "parent_peak_rss_bytes": LEGACY.parent_peak_rss(),
    }
    check(result["whole_wall_seconds"] < budgets["max_wall_seconds"], "campaign exceeded wall budget")
    result["stable_sha256"] = digest(stable(result))
    (output / "campaign-result.json").write_bytes(
        (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii"),
    )
    receipt = {"classification": result["classification"], "development_pass": passed,
               "stable_sha256": result["stable_sha256"]}
    line = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(line)
    if args.verify_env:
        check(receipt == json.loads(os.environ["CKAD21_EXPECTED_RESULT"]), "cross-platform result drift")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("result=" + line + "\n")


if __name__ == "__main__":
    main()
