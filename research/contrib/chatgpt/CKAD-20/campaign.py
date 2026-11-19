"""Run the frozen CKAD20 cumulative development campaign and matched controls."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

from synthetic_world import make_episode, public_views, rollout
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner


BITS = (0, 1)
POLICIES = ("active", "random", "no_repair", "full", "dream_off", "beta", "trailing_mle", "untrained")
TRAINED_COMPARATORS = POLICIES[1:-1]


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def ratio(value):
    return [value.numerator, value.denominator]


def random_actions(cohort, stream, seed, index):
    key = f"ckad20/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")
    hashed = bytes.fromhex(digest(key))
    return hashed[0] & 1, hashed[1] & 1


def event_id(cohort, seed, index, arm):
    return digest(canonical(["ckad20", EXPERIENCE_SOURCE, cohort, seed, index, arm]))


def fixed_rollout(episode, actions):
    first, second = actions
    return rollout(episode, lambda _initial: first, lambda _initial, _first, _state: second)


def planned_rollout(episode, plan, *, first_override=None):
    first = plan["first_action"] if first_override is None else first_override
    return rollout(
        episode, lambda _initial: first,
        lambda _initial, chosen_first, state: plan["second_actions"][chosen_first][state],
    )


def projection(receipts):
    """Fit the conventional readout's paired projection to the same eight witnesses."""
    if len(receipts) < 8:
        return None
    mismatches = [
        sum(views[0][bit] != views[1][bit] for views, _ in receipts[:8]) for bit in BITS
    ]
    return None if mismatches[0] == mismatches[1] else int(mismatches[1] < mismatches[0])


class ConventionalControl:
    """Fit a public history table and compose its expected two-stage reward."""

    def __init__(self, receipts, *, mle=False):
        self.projection = projection(receipts)
        self.pseudocount = int(not mle)
        self.transitions = Counter()
        self.rewards = Counter()
        for views, row in (receipts[-64:] if mle else receipts):
            if self.projection is None:
                context = None
            else:
                a, b = (view[self.projection] for view in views)
                context = a if a == b else None
            first, state, second, reward = (row[field] for field in ("x1", "s2", "x2", "y"))
            self.transitions[None, first, state] += 1
            self.rewards[None, first, state, second, reward] += 1
            if context is not None:
                self.transitions[context, first, state] += 1
                self.rewards[context, first, state, second, reward] += 1

    def forecast(self, view, first, next_state=None, second=None):
        context = None if self.projection is None else view[self.projection]
        if next_state is None:
            counts, key = self.transitions, (context, first)
        else:
            counts, key = self.rewards, (context, first, next_state, second)
        failures = counts[(*key, 0)] + self.pseudocount
        successes = counts[(*key, 1)] + self.pseudocount
        return Fraction(successes, failures + successes) if failures + successes else Fraction(1, 2)

    def plan(self, view):
        actions, values = [], []
        for first in BITS:
            q = self.forecast(view, first)
            best = [max((self.forecast(view, first, state, second), -second)
                        for second in BITS) for state in BITS]
            values.append((1 - q) * best[0][0] + q * best[1][0])
            actions.append([-action for _, action in best])
        return {"first_action": int(values[1] > values[0]), "second_actions": actions}


def evaluators(models, parent, receipts):
    beta = ConventionalControl(receipts)
    mle = ConventionalControl(receipts, mle=True)
    return {
        "active": (models["active"].experience_plan, models["active"].experience_forecast, None),
        "random": (models["random"].experience_plan, models["random"].experience_forecast, None),
        "no_repair": (models["no_repair"].experience_plan, models["no_repair"].experience_forecast, None),
        "full": (lambda view: models["active"].experience_plan(view, full=True),
                 lambda *args: models["active"].experience_forecast(*args, full=True), None),
        "dream_off": (models["active"].experience_plan, models["active"].experience_forecast, 0),
        "beta": (beta.plan, beta.forecast, None),
        "trailing_mle": (mle.plan, mle.forecast, None),
        "untrained": (parent.experience_plan, parent.experience_forecast, None),
    }


def evaluate(models, parent, receipts, seed, specifications):
    public_views_space = list(product(BITS, repeat=2))
    arms = evaluators(models, parent, receipts)
    estimates = {}
    for arm, (plan, forecast, first_override) in arms.items():
        plans = {view: plan(view) for view in public_views_space}
        transition = {(view, first): forecast(view, first)
                      for view in public_views_space for first in BITS}
        terminal = {(view, first, state, second): forecast(view, first, state, second)
                    for view in public_views_space for first, state, second in product(BITS, repeat=3)}
        estimates[arm] = plans, transition, terminal, first_override

    results = {}
    for spec in specifications:
        cohort = spec["cohort"]
        count = spec["count"]
        totals = {arm: [0, Fraction(0), Fraction(0), 0] for arm in POLICIES}
        different_views = 0
        for index in range(count):
            episode = make_episode(cohort=cohort, seed=seed, index=index,
                                   family=spec["family"], regime=spec["regime"])
            view, alternative = public_views(episode)
            different_views += view != alternative
            sample = fixed_rollout(episode, random_actions(cohort, "eval-matched", seed, index))
            first, state, second, target = (sample[key] for key in ("x1", "s2", "x2", "y"))
            for arm, (plans, transition, terminal, override) in estimates.items():
                row = planned_rollout(episode, plans[view], first_override=override)
                t = transition[view, first]
                r = terminal[view, first, state, second]
                total = totals[arm]
                total[0] += row["y"]
                total[1] += (t - state) ** 2
                total[2] += (r - target) ** 2
                total[3] += (int(t != transition[alternative, first])
                             + int(r != terminal[alternative, first, state, second]))
        results[cohort] = {
            arm: {"episodes": count, "reward_sum": rewarded,
                  "transition_brier": ratio(transition_loss / count),
                  "terminal_brier": ratio(terminal_loss / count),
                  "pooled_brier": ratio((transition_loss + terminal_loss) / (2 * count)),
                  "view_disagreements": disagreements, "view_comparisons": 2 * count,
                  "distinct_view_episodes": different_views}
            for arm, (rewarded, transition_loss, terminal_loss, disagreements) in totals.items()
        }
    return results


def observe(model, identifier, views, row, *, repair=None):
    return model.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=digest(canonical([identifier, views, row])), repair=repair,
    )


def reject_corrupt_packet(parent, identifier, views, row):
    try:
        parent.observe_experience(identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                                  packet_sha256="0" * 64)
    except ValueError:
        return
    raise RuntimeError("corrupt public episode packet accepted")


def acquire(models, receipts, seed, spec):
    cohort = spec["cohort"]
    dreams = 0
    n = spec["episodes_per_arm_per_seed"]
    for index in range(n):
        episode = make_episode(cohort=cohort, seed=seed, index=index,
                               family=spec["family"], regime=spec["regime"])
        views = public_views(episode)
        view = views[0]
        active = models["active"]
        if index % 4 == 3:
            active_row = planned_rollout(episode, active.experience_plan(view))
            dreams += 1
        else:
            active_row = rollout(episode, lambda _initial: active.experience_explore(view),
                                 lambda _initial, first, state: active.experience_explore(view, first, state))
        random_row = fixed_rollout(episode, random_actions(cohort, "train-random", seed, index))
        active_id = event_id(cohort, seed, index, "active")
        first_receipt = not receipts
        if first_receipt:
            reject_corrupt_packet(active, active_id, views, active_row)
        models["active"] = observe(active, active_id, views, active_row)
        models["no_repair"] = observe(models["no_repair"], active_id, views, active_row,
                                      repair=False if first_receipt else None)
        models["random"] = observe(models["random"], event_id(cohort, seed, index, "random"),
                                   views, random_row)
        if first_receipt:
            check(observe(models["active"], active_id, views, active_row) is models["active"],
                  "duplicate public receipt changed weights")
        receipts.append((views, active_row))
    return {"dream_acquisitions": dreams, "tournament_acquisitions": n - dreams}


def readout_pin(model):
    states = list(product(BITS, repeat=2))
    transitions = [
        [ratio(model.experience_forecast(view, first)) for first in BITS] for view in states
    ]
    predictions = [
        [ratio(model.experience_forecast(view, first, state, second))
         for first, state, second in product(BITS, repeat=3)]
        for view in states
    ]
    plans = [model.experience_plan(view) for view in states]
    return digest(canonical([transitions, predictions, plans]))


def cold_verify(path, pin, readout_sha):
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--cold-check", str(path), pin, readout_sha]
    evidence = json.loads(subprocess.check_output(command, cwd=ROOT, timeout=75, text=True))
    check(evidence["state_sha256"] == pin and evidence["readout_sha256"] == readout_sha,
          "cold subprocess state/readout drift")
    return evidence["cpu_seconds"]


def cold_child(args):
    started = time.process_time()
    path, pin, readout_sha = args
    sys.modules["scipy"] = None
    raw = Path(path).read_bytes()
    model = NativeCumulativeLearner.restore(raw, pin)
    check(model.checkpoint() == raw and readout_pin(model) == readout_sha,
          "cold subprocess restore drift")
    print(json.dumps({"state_sha256": pin, "readout_sha256": readout_sha,
                      "cpu_seconds": time.process_time() - started}, sort_keys=True))


def preserve_models(models, base, seed, phase, last_phase, output):
    states = {}
    for arm, model in models.items():
        raw = model.checkpoint()
        pin = digest(raw)
        encoded = json.loads(raw)
        if phase:
            encoded.pop("experience_ascii")
            check(encoded.pop("experience_source") == EXPERIENCE_SOURCE, "experience source drift")
            encoded["schema"] = base["schema"]
            check(model.consolidate_experience().checkpoint() == raw, "consolidation drift")
        check(encoded == base, "legacy cumulative checkpoint changed")
        old_readout = readout_pin(model)
        restored = NativeCumulativeLearner.restore(raw, pin)
        check(restored.checkpoint() == raw and readout_pin(restored) == old_readout,
              "serialized restore changed planner or forecasts")
        models[arm] = restored
        evidence = {
            "checkpoint_sha256": pin, "checkpoint_bytes": len(raw),
            "readout_sha256": old_readout, "experience": restored.info().get("episode_experience"),
            "cold_verified": True, "cold_method": "serialized_roundtrip",
        }
        if phase and arm == "active":
            name = f"seed-{seed}-unified-native.json" if phase == last_phase else f".seed-{seed}-stage-{phase}.json"
            path = output / name
            path.write_bytes(raw)
            evidence["cold_process_cpu_seconds"] = cold_verify(path, pin, old_readout)
            evidence["cold_method"] = "fresh_process"
            if phase != last_phase:
                path.unlink()
        states[arm] = evidence
    return states


def run_seed(seed, protocol, output):
    pin = protocol["base_states"][str(seed)]
    raw = (HERE.parent / "CKAD-18" / f"seed-{seed}-full-scope-native.json").read_bytes()
    parent = NativeCumulativeLearner.restore(raw, pin)
    check(parent.checkpoint() == raw, "qualified CKAD18 parent restore drift")
    base = json.loads(raw)
    models = {arm: parent for arm in ("active", "random", "no_repair")}
    receipts = []
    stages = []
    schedule = protocol["training_schedule"]
    for phase, spec in enumerate([None, *schedule]):
        acquisition = acquire(models, receipts, seed, spec) if spec else {
            "dream_acquisitions": 0, "tournament_acquisitions": 0,
        }
        states = preserve_models(models, base, seed, phase, len(schedule), output)
        evaluation = evaluate(models, parent, receipts, seed, protocol["evaluation"])
        for arm, model in models.items():
            evidence = states[arm]
            check(digest(model.checkpoint()) == evidence["checkpoint_sha256"],
                  "held evaluation modified fitted state")
            if phase:
                check(evidence["experience"]["count"] == len(receipts), "episode ledger count drift")
        stages.append({"phase": phase, "training_episodes": len(receipts),
                       "acquisition": acquisition, "states": states, "evaluation": evaluation})
    return {"seed": seed, "parent_checkpoint_sha256": pin, "stages": stages,
            "final_checkpoint_name": f"seed-{seed}-unified-native.json",
            "final_checkpoint_sha256": stages[-1]["states"]["active"]["checkpoint_sha256"]}


def mean_reward(seeds, phase, cohort, arm):
    outcomes = [seed["stages"][phase]["evaluation"][cohort][arm] for seed in seeds]
    return Fraction(sum(o["reward_sum"] for o in outcomes), sum(o["episodes"] for o in outcomes))


def mean_brier(seeds, phase, cohort, arm):
    outcomes = [seed["stages"][phase]["evaluation"][cohort][arm] for seed in seeds]
    total = sum(Fraction(*o["pooled_brier"]) * o["episodes"] for o in outcomes)
    return total / sum(o["episodes"] for o in outcomes)


def development(seeds):
    last = len(seeds[0]["stages"]) - 1
    reward = mean_reward(seeds, last, "eval-2", "active")
    brier = mean_brier(seeds, last, "eval-2", "active")
    reward_deltas = {arm: reward - mean_reward(seeds, last, "eval-2", arm)
                     for arm in TRAINED_COMPARATORS}
    brier_deltas = {arm: mean_brier(seeds, last, "eval-2", arm) - brier
                    for arm in TRAINED_COMPARATORS if arm != "dream_off"}
    retention = (mean_reward(seeds, last, "eval-0", "active") -
                 mean_reward(seeds, 1, "eval-0", "active"))
    gates = {"shift_reward_vs_all": all(d >= Fraction(2, 100) for d in reward_deltas.values()),
             "shift_brier_vs_predictive": all(d >= Fraction(1, 100) for d in brier_deltas.values()),
             "prior_invariant_retention": retention >= -Fraction(5, 100)}
    metrics = {"active_shift_reward": ratio(reward), "active_shift_brier": ratio(brier),
               "shift_reward_deltas": {arm: ratio(delta) for arm, delta in reward_deltas.items()},
               "shift_brier_improvements": {arm: ratio(delta) for arm, delta in brier_deltas.items()},
               "prior_invariant_reward_delta": ratio(retention)}
    return gates, metrics


def _semantic(result):
    if isinstance(result, dict):
        return {key: _semantic(value) for key, value in result.items()
                if not key.endswith("_seconds")
                and key not in {"source_candidate_sha", "stable_sha256", "parent_peak_rss_bytes"}}
    if isinstance(result, list):
        return [_semantic(item) for item in result]
    return result


def stable(result):
    return canonical(_semantic(result))


def parent_peak_rss():
    try:
        import resource
    except ImportError:
        return None
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else 1024 * value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--verify-env", action="store_true")
    parser.add_argument("--cold-check", nargs=3, metavar=("path", "sha256", "readout_sha256"))
    args = parser.parse_args()
    if args.cold_check:
        cold_child(args.cold_check)
        return
    if args.output_directory is None:
        parser.error("--output-directory required")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    cpu_started = time.process_time()
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    check(digest((HERE / "synthetic_world.py").read_bytes()) == protocol["source_sha256"] == EXPERIENCE_SOURCE,
          "frozen synthetic world custody mismatch")
    seeds = [run_seed(seed, protocol, output) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    per_arm = sum(spec["episodes_per_arm_per_seed"] for spec in protocol["training_schedule"])
    training = per_arm * len(seeds) * 2
    held_matched = sum(spec["count"] for spec in protocol["evaluation"]) * len(seeds) * len(seeds[0]["stages"])
    result = {
        "schema": "yggdrasil.ckad20.shared-episode-development.result.v1",
        "classification": "DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO",
        "development_pass": passed, "development_gates": gates, "development_metrics": metrics,
        "source_candidate_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip(),
        "source_sha256": EXPERIENCE_SOURCE, "scientific_pass": False, "accepted_native": False,
        "deployment": "NONE", "seeds": seeds,
        "final_checkpoints": [
            {"seed": seed["seed"], "name": seed["final_checkpoint_name"],
             "sha256": seed["final_checkpoint_sha256"],
             "bytes": seed["stages"][-1]["states"]["active"]["checkpoint_bytes"]}
            for seed in seeds
        ],
        "scope": {"training_rollouts": training, "training_synthetic_actions": 2 * training,
                  "per_seed_per_acquisition_arm": per_arm, "held_updates": 0,
                  "matched_held_rollouts": held_matched, "held_policy_rollouts": held_matched * len(POLICIES),
                  "original_source_actions": 0, "protected_first_use": 0},
        "whole_wall_seconds": time.monotonic() - started,
        "parent_cpu_seconds": time.process_time() - cpu_started,
        "child_cpu_seconds": sum(
            stage["states"]["active"].get("cold_process_cpu_seconds", 0)
            for seed in seeds for stage in seed["stages"]
        ),
        "parent_peak_rss_bytes": parent_peak_rss(),
    }
    check(per_arm == protocol["stops"]["max_unique_training_episodes_per_seed_per_acquisition_arm"]
          and result["whole_wall_seconds"] < protocol["stops"]["max_wall_seconds"], "campaign budget")
    result["stable_sha256"] = digest(stable(result))
    (output / "campaign-result.json").write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii"),
    )
    receipt = {"classification": result["classification"], "development_pass": passed,
               "stable_sha256": result["stable_sha256"]}
    line = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(line)
    if args.verify_env:
        check(receipt == json.loads(os.environ["CKAD20_EXPECTED_RESULT"]), "cross-platform result drift")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("result=" + line + "\n")


if __name__ == "__main__":
    main()
