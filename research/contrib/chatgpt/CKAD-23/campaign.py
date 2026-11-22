"""Frozen CKAD23 unsignaled causal-context development, one native cumulative learner."""
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
PREVIOUS = HERE.parent / "CKAD-22"
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(ROOT))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BASE = load("ckad22_qualified", PREVIOUS / "campaign.py")
REFERENCE, LEGACY, B = BASE.REFERENCE, BASE.LEGACY, BASE.BASE
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE

ARMS = ("detector_active", "detector_random", "no_reset", "periodic32",
        "pooled_replay", "trailing_mle", "exact_mixture", "frozen_ckad22")

def check(condition, reason):
    if not condition:
        raise RuntimeError("CKAD23: " + reason)

def ratio(value):
    return [value.numerator, value.denominator]

def random_actions(cohort, kind, seed, index):
    key = f"ckad23/actions-v1/{cohort}/{kind}/{seed}/{index}".encode("ascii")
    hashed = bytes.fromhex(digest(key))
    return hashed[0] & 1, hashed[1] & 1

def event_id(cohort, seed, index, arm):
    return digest(canonical(["ckad23", EXPERIENCE_SOURCE, cohort, seed, index, arm]))

class Monitor:
    """Conventional replay, separate from native stream scoring/state."""
    def __init__(self, initial):
        self.events = initial.copy()
        self.mixture = REFERENCE.Mixture(initial, novel=True)
        self.start = len(initial)
        self.score = Fraction(1)
        self.detections = []

    def add(self, event):
        _, views, first, state, second, reward = event
        view = tuple(views[0])
        p = self.mixture.forecast(view, first)
        q = self.mixture.forecast(view, first, state, second)
        likelihood = (p if state else 1 - p) * (q if reward else 1 - q)
        check(likelihood > 0, "independent joint likelihood positive")
        self.events.append(event)
        self.mixture.add(event)
        self.score = max(Fraction(1), self.score / (4 * likelihood))
        if self.score >= 16 and len(self.events) - self.mixture.start >= 8:
            self.detections.append({
                "event_id": event[0], "evidence_count": len(self.events),
                "score": ratio(self.score),
            })
            self.mixture = REFERENCE.Mixture(self.events, novel=True)
            self.score = Fraction(1)

    def assert_native(self, native):
        info = native.info()["episode_experience"]
        check(info["context"] == self.mixture.info(), "independent mixture posterior mismatch")
        check(info["stream"] == {
            "stream_start": self.start, "score": ratio(self.score),
            "detections": self.detections,
        }, "independent consequence change detector mismatch")

def estimate(models, monitor, parent):
    mle = LEGACY.ConventionalControl(B.receipts_from_events(monitor.events), mle=True)
    experts = {
        key: (models[key].experience_context_plan, models[key].experience_context_forecast)
        for key in ("detector_active", "detector_random", "no_reset", "periodic32")
    }
    experts.update({
        "pooled_replay": (models["pooled_replay"].experience_plan,
                          models["pooled_replay"].experience_forecast),
        "trailing_mle": (mle.plan, mle.forecast),
        "exact_mixture": (monitor.mixture.plan, monitor.mixture.forecast),
        "frozen_ckad22": (parent.experience_context_plan,
                          parent.experience_context_forecast),
    })
    return {key: (
        {view: plan(view) for view in B.VIEWS},
        {(view, a): forecast(view, a) for view in B.VIEWS for a in B.BITS},
        {(view, *h): forecast(view, *h) for view in B.VIEWS
         for h in B.TERMINAL_HISTORIES},
    ) for key, (plan, forecast) in experts.items()}

def evaluate(models, monitor, parent, source_seed, count, world, held_count):
    cohort = f"ckad23-held-{count}"
    before = {name: digest(model.checkpoint()) for name, model in models.items()}
    tables = estimate(models, monitor, parent)
    totals = {arm: [0, Fraction(), Fraction(), 0] for arm in ARMS}
    distinct = 0
    for index in range(held_count):
        episode = B.make_episode(cohort=cohort, seed=source_seed, index=index, **world)
        view, alternate = B.public_views(episode)
        distinct += view != alternate
        sample = LEGACY.fixed_rollout(
            episode, random_actions(cohort, "held-matched", source_seed, index))
        first, state, second, reward = (sample[k] for k in ("x1", "s2", "x2", "y"))
        for arm, (plans, transitions, terminals) in tables.items():
            planned = LEGACY.planned_rollout(episode, plans[view])
            p = transitions[view, first]
            q = terminals[view, first, state, second]
            cells = totals[arm]
            cells[0] += planned["y"]
            cells[1] += (p - state) ** 2
            cells[2] += (q - reward) ** 2
            cells[3] += int(p != transitions[alternate, first]) + int(
                q != terminals[alternate, first, state, second])
    result = {arm: {
        "episodes": held_count, "reward_sum": scores[0],
        "transition_brier": ratio(scores[1] / held_count),
        "terminal_brier": ratio(scores[2] / held_count),
        "pooled_brier": ratio((scores[1] + scores[2]) / (2 * held_count)),
        "view_disagreements": scores[3], "view_comparisons": 2 * held_count,
        "distinct_view_episodes": distinct,
    } for arm, scores in totals.items()}
    check(result["detector_active"] == result["exact_mixture"], "held reference mismatch")
    check(before == {name: digest(model.checkpoint()) for name, model in models.items()},
          "held learning state changed")
    return result

def cold_check(arguments):
    path, pin, readout = arguments
    raw = Path(path).read_bytes()
    model = NativeCumulativeLearner.restore(raw, pin)
    check(model.checkpoint() == raw, "cold native checkpoint bytes")
    check(B.context_readout_pin(model) == readout, "cold readout")
    check(model.info()["episode_experience"]["count"] == 640, "cold witness continuity")
    print(json.dumps({"sha256": pin, "readout_sha256": readout}, sort_keys=True))

def cold_proof(path, pin, readout):
    result = json.loads(subprocess.check_output(
        [sys.executable, "-B", str(HERE / "campaign.py"), "--cold-check",
         str(path), pin, readout], cwd=ROOT, timeout=120, text=True))
    check(result == {"sha256": pin, "readout_sha256": readout}, "child cold report")
    return result

def run_seed(seed, protocol, output):
    path = PREVIOUS / f"seed-{seed}-expanded-native.json"
    pin = protocol["parent_pins"][str(seed)]
    raw = path.read_bytes()
    parent = NativeCumulativeLearner.restore(raw, pin)
    legacy, old = B.legacy_and_experience(raw)
    prefix = old["episodes"]
    check(len(prefix) == 448, "CKAD22 parent prefix length")
    models = {
        "detector_active": parent.begin_experience_stream(),
        "detector_random": parent.begin_experience_stream(),
        "no_reset": parent.begin_experience_context(novel=True),
        "periodic32": parent.begin_experience_context(novel=True),
        "pooled_replay": parent,
    }
    active, random = Monitor(prefix), Monitor(prefix)
    source_seed = seed + protocol["source_seed_offset"]
    budget = protocol["budgets"]
    count = budget["stream_episodes_per_seed_per_acquisition_arm"]
    phase_length = budget["phase_episodes"]
    held_count = budget["held_episodes_per_checkpoint"]
    parity = {"forecasts": 0, "decisions": 0, "mismatches": 0}
    checkpoints = []

    def score(n):
        world = protocol["phases"][0 if n == 0 else (n - 1) // phase_length]
        outcome = evaluate(models, active, parent, source_seed, n, world, held_count)
        active.assert_native(models["detector_active"])
        random.assert_native(models["detector_random"])
        checkpoints.append({
            "count": n, "evaluation": outcome,
            "active_detections": list(active.detections),
            "random_detections": list(random.detections),
            "active_score": ratio(active.score), "random_score": ratio(random.score),
            "context_start": models["detector_active"].info()[
                "episode_experience"]["context"]["context_start"],
            "checkpoint_sha256": digest(models["detector_active"].checkpoint()),
        })

    score(0)
    cohort = "ckad23-stream"
    for index in range(count):
        world = protocol["phases"][index // phase_length]
        if index and index % 32 == 0:
            models["periodic32"] = models["periodic32"].begin_experience_context(novel=True)
        episode = B.make_episode(cohort=cohort, seed=source_seed, index=index, **world)
        views = B.public_views(episode)
        view = views[0]
        B.require_parity(models["detector_active"], active.mixture, parity)
        if index % 4 == 3:
            observed = LEGACY.planned_rollout(
                episode, models["detector_active"].experience_context_plan(view))
        else:
            current = models["detector_active"]
            observed = B.rollout(
                episode,
                lambda _: current.experience_context_explore(view),
                lambda _, first, state: current.experience_context_explore(view, first, state),
            )
        identifier = event_id(cohort, source_seed, index, "active")
        event = B.retain_event(identifier, views, observed)
        for arm in ("detector_active", "no_reset", "periodic32", "pooled_replay"):
            models[arm] = B.admit(models[arm], identifier, views, observed)
        active.add(event)
        active.assert_native(models["detector_active"])
        random_row = LEGACY.fixed_rollout(
            episode, random_actions(cohort, "probe-random", source_seed, index))
        random_id = event_id(cohort, source_seed, index, "random")
        random_event = B.retain_event(random_id, views, random_row)
        models["detector_random"] = B.admit(models["detector_random"], random_id, views, random_row)
        random.add(random_event)
        random.assert_native(models["detector_random"])
        if (index + 1) % 16 == 0:
            score(index + 1)

    check([c["count"] for c in checkpoints] == budget["checkpoints"],
          "frozen evaluation checkpoint schedule")
    for arm, model in models.items():
        recovered_legacy, recovered = B.legacy_and_experience(model.checkpoint())
        episodes = recovered["episodes"]
        check(recovered_legacy == legacy, f"{arm} original legacy state drift")
        check(episodes[:448] == prefix, f"{arm} historical prefix drift")
        check(len(episodes) == 448 + count and len({e[0] for e in episodes}) == len(episodes),
              f"{arm} witness identity/count drift")
        check(episodes == (random.events if arm == "detector_random" else active.events),
              f"{arm} same-budget receipts drift")
    final = models["detector_active"].consolidate_experience()
    payload = final.checkpoint()
    final_pin = digest(payload)
    filename = f"seed-{seed}-stream-native.json"
    destination = output / filename
    destination.write_bytes(payload)
    readout = B.context_readout_pin(final)
    cold = cold_proof(destination, final_pin, readout)
    return {
        "seed": seed, "source_seed": source_seed,
        "parent_checkpoint_sha256": pin, "stream": checkpoints,
        "final_checkpoint_name": filename,
        "final_checkpoint_sha256": final_pin,
        "final_checkpoint_bytes": len(payload), "final_context_sha256": readout,
        "active_detections": active.detections, "random_detections": random.detections,
        "parity": parity, "cold": cold,
    }

def development(seeds):
    points = (64, 112, 160)
    def mean(arm):
        values = [next(s for s in seed["stream"] if s["count"] == count)["evaluation"][arm]
                  for seed in seeds for count in points]
        return Fraction(sum(v["reward_sum"] for v in values),
                        sum(v["episodes"] for v in values))
    active = mean("detector_active")
    no_reset, periodic, mle = mean("no_reset"), mean("periodic32"), mean("trailing_mle")
    last = Fraction(sum(s["stream"][-1]["evaluation"]["detector_active"]["reward_sum"]
                        for s in seeds), 96 * len(seeds))
    changes = (48, 96, 144)
    false_alarms = {str(s["seed"]): sum(
        not any(change < event["evidence_count"] - 448 <= change + 16
                for change in changes)
        for event in s["active_detections"]) for s in seeds}
    gates = {
        "held_gain_vs_no_reset": active - no_reset >= Fraction(1, 20),
        "held_vs_periodic32": active >= periodic,
        "held_vs_trailing_mle": active >= mle,
        "final_returning_invariant": last >= Fraction(4, 5),
        "max_three_false_alarms": all(n <= 3 for n in false_alarms.values()),
    }
    metrics = {
        "held_detector_reward": ratio(active), "held_no_reset_reward": ratio(no_reset),
        "held_periodic32_reward": ratio(periodic), "held_trailing_mle_reward": ratio(mle),
        "gain_vs_no_reset": ratio(active - no_reset),
        "final_returning_invariant_reward": ratio(last),
        "false_alarms": false_alarms,
    }
    return gates, metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--verify-env", action="store_true")
    parser.add_argument("--cold-check", nargs=3)
    args = parser.parse_args()
    if args.cold_check:
        cold_check(args.cold_check)
        return
    if args.output_directory is None:
        parser.error("--output-directory required")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    start, cpu = time.monotonic(), time.process_time()
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    check(digest(SOURCE.read_bytes()) == protocol["source_sha256"] == EXPERIENCE_SOURCE,
          "source generator pin")
    check(protocol["seeds"] == [101, 202, 303] and len(protocol["phases"]) == 4,
          "frozen source protocol")
    seeds = [run_seed(seed, protocol, output) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    budget = protocol["budgets"]
    parity = {key: sum(seed["parity"][key] for seed in seeds)
              for key in ("forecasts", "decisions", "mismatches")}
    result = {
        "schema": "yggdrasil.ckad23.unsignaled-context-development.result.v1",
        "classification": "DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO",
        "development_pass": passed, "development_gates": gates,
        "development_metrics": metrics, "source_candidate_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": EXPERIENCE_SOURCE, "scientific_pass": False,
        "accepted_native": False, "deployment": "NONE",
        "seeds": seeds, "parity": parity,
        "scope": {
            "active_stream_episodes": 3 * budget["stream_episodes_per_seed_per_acquisition_arm"],
            "random_stream_episodes": 3 * budget["stream_episodes_per_seed_per_acquisition_arm"],
            "synthetic_actions": 12 * budget["stream_episodes_per_seed_per_acquisition_arm"],
            "held_episodes": 3 * len(budget["checkpoints"]) * budget["held_episodes_per_checkpoint"],
            "held_updates": 0, "original_source_actions": 0,
            "protected_first_use": 0,
        },
        "whole_wall_seconds": time.monotonic() - start,
        "parent_cpu_seconds": time.process_time() - cpu,
        "parent_peak_rss_bytes": LEGACY.parent_peak_rss(),
    }
    check(result["whole_wall_seconds"] <= budget["max_wall_seconds"],
          "frozen wall budget exceeded")
    result["stable_sha256"] = digest(LEGACY.stable(result))
    (output / "campaign-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "stable_sha256": result["stable_sha256"]}, sort_keys=True))
    if args.verify_env:
        check(os.environ["CKAD23_EXPECTED_HASH"] == result["stable_sha256"],
              "cross-platform result drift")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("stable=" + result["stable_sha256"] + "\n")

if __name__ == "__main__":
    main()
