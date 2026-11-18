"""Cached DTR planning qualification from the retained integrated learner."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from independent_audit import fixed, reference, source_rows, stable
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

PREFIXES = (0, 64, 128, 192)
FINAL_PINS = {
    101: "f8eb0c4dd92ca3e8a9ca2a70e21d337a28612101f3eec4ff807e584b7eacc91a",
    202: "da9c8f63d0f5f150d6fdb6a7f86bbba431c7f11bba33042f20c0308fad58db26",
    303: "d4074d6cf205a0dbc87b7cba8660d99415b4f981a951ef947073413a55e536c7",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plans(model):
    return json.loads(json.dumps([model.dtr_plan(s) for s in (0, 1)]))


def recommendation(policy, row, terminal_only):
    plan = policy[row["s1"]]
    first = row["x1"] if terminal_only else plan["first_action"]
    return first, plan["second_actions"][first]


def payoff_bounds(row, policy, terminal_only):
    first, second = recommendation(policy, row, terminal_only)
    if first == row["x1"] and second[row["s2"]] == row["x2"]:
        return row["y"], row["y"]
    return 0, 1


def shared_path(row, a, b, terminal_only):
    first_a, second_a = recommendation(a, row, terminal_only)
    first_b, second_b = recommendation(b, row, terminal_only)
    if first_a != first_b:
        return False
    if first_a == row["x1"]:
        return second_a[row["s2"]] == second_b[row["s2"]]
    return second_a == second_b


def bounds(held, a, controls, terminal_only):
    intervals = [payoff_bounds(row, a, terminal_only) for row in held]
    paired = {}
    for name, b in controls.items():
        low = high = agreement = 0
        for row, (a_lo, a_hi) in zip(held, intervals):
            if shared_path(row, a, b, terminal_only):
                agreement += 1
                continue
            b_lo, b_hi = payoff_bounds(row, b, terminal_only)
            low += a_lo - b_hi
            high += a_hi - b_lo
        paired[name] = {"difference_numerator": [low, high], "guaranteed_agreements": agreement}
    return {
        "episodes": len(held),
        "observed_matches": sum(lo == hi for lo, hi in intervals),
        "observed_successes": sum(lo for lo, _ in intervals),
        "return_numerator": [sum(lo for lo, _ in intervals), sum(hi for _, hi in intervals)],
        "paired": paired,
    }


def score(held, a, mle):
    fixed_arms = {f"fixed_{i}{j}": fixed(i, j) for i in (0, 1) for j in (0, 1)}
    arms = {"native_beta": a, "empirical_mle": mle, **fixed_arms}
    terminal = {"fixed_0": fixed(0, 0), "fixed_1": fixed(0, 1), "empirical_mle": mle}
    return {
        "two_stage": {name: bounds(held, policy, {**fixed_arms, "empirical_mle": mle}, False)
                      for name, policy in arms.items()},
        "logged_history_terminal": bounds(held, a, terminal, True),
    }


def check_negatives():
    row = {"s1": 0, "x1": 0, "s2": 1, "x2": 1, "y": 1}
    unobserved = fixed(1, 1)
    assert payoff_bounds(row, unobserved, False) == (0, 1)
    assert payoff_bounds(row, unobserved, True) == (1, 1)
    assert bounds([row], unobserved, {"same": unobserved}, False)["paired"]["same"] == {
        "difference_numerator": [0, 0], "guaranteed_agreements": 1}
    model = NativeCumulativeLearner.__new__(NativeCumulativeLearner)
    model._dtr = None
    assert model.dtr_plan(0) is None
    for invalid in (True, False, 2, -1, "0"):
        try:
            model.dtr_plan(invalid)
        except ValueError:
            continue
        raise AssertionError("admitted invalid public state")


def cold_plan(checkpoint, pin):
    program = """import json,sys
from pathlib import Path
sys.modules['scipy'] = None
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
raw = Path(sys.argv[1]).read_bytes()
m = NativeCumulativeLearner.restore(raw,sys.argv[2])
assert m.checkpoint() == raw
print(json.dumps([m.dtr_plan(i) for i in (0,1)],sort_keys=True))
"""
    output = subprocess.check_output(
        [sys.executable, "-B", "-c", program, str(checkpoint), pin],
        cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT)), timeout=45,
    )
    return json.loads(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--verify-env", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    cpu_started = time.process_time()
    check_negatives()
    cache, replicas, held = source_rows()
    legacy = json.loads((HERE.parent / "CKAD-16" / "result.json").read_bytes())
    parent = HERE.parent / "CKAD-15" / legacy["parent_checkpoint_name"]
    parent_raw = parent.read_bytes()
    assert sha(parent_raw) == legacy["parent_checkpoint_sha256"]
    model = NativeCumulativeLearner.restore(parent_raw, sha(parent_raw))
    stages = []
    for n, old in zip(PREFIXES, legacy["stages"], strict=True):
        assert n == old["prefix_episodes_per_replica"]
        if n:
            model = model.observe_cached_dtr(cache, sha(cache), n)
        raw = model.checkpoint()
        assert sha(raw) == old["checkpoint_sha256"]
        native = plans(model)
        training = [row for replica in replicas for row in replica[:n]]
        beta = reference(training, 1)
        mle = reference(training, 0)
        if n:
            assert native == beta
        else:
            assert native == [None, None]
            native = fixed(0, 0)
        assert model.checkpoint() == raw
        stages.append({"prefix": n, "training_episodes": len(training), "checkpoint_sha256": sha(raw),
                       "native": native, "exact_beta": beta, "empirical_mle": mle,
                       "native_available": bool(n), "bounds": score(held, native, mle)})
    final = []
    for seed, pin in FINAL_PINS.items():
        path = HERE.parent / "CKAD-18" / f"seed-{seed}-full-scope-native.json"
        raw = path.read_bytes()
        assert sha(raw) == pin
        replica = NativeCumulativeLearner.restore(raw, pin)
        assert plans(replica) == cold_plan(path, pin) == stages[-1]["native"]
        assert replica.checkpoint() == raw
        final.append({"seed": seed, "sha256": pin, "cold_plan": plans(replica)})
    last = stages[-1]["bounds"]
    two_stage = all(x["difference_numerator"][0] > 0
                    for x in last["two_stage"]["native_beta"]["paired"].values())
    terminal = all(last["logged_history_terminal"]["paired"][f"fixed_{i}"]["difference_numerator"][0] > 0
                   for i in (0, 1))
    result = {
        "schema": "yggdrasil.ckad19.dtr-composed-decision.result.v1",
        "classification": "CACHED_DTR_COMPOSED_READOUT_SUPPORTED",
        "stages": stages, "final_ckad18_checkpoints": final,
        "two_stage_empirical_gain": two_stage, "logged_history_terminal_empirical_gain": terminal,
        "original_source_actions": 0, "held_training_updates": 0,
        "scientific_pass": False, "accepted_native": False, "deployment": "NONE",
        "source_candidate_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "whole_wall_seconds": time.monotonic() - started,
        "learner_and_evaluation_parent_cpu_seconds": time.process_time() - cpu_started,
    }
    assert result["whole_wall_seconds"] < 180
    result["stable_sha256"] = sha(stable(result))
    args.output_directory.mkdir(parents=True, exist_ok=True)
    (args.output_directory / "campaign-result.json").write_bytes(
        (json.dumps(result, sort_keys=True, indent=2) + "\n").encode())
    receipt = {"stable_sha256": result["stable_sha256"], "two_stage_empirical_gain": two_stage,
               "logged_history_terminal_empirical_gain": terminal}
    print(json.dumps(receipt, sort_keys=True))
    if args.verify_env:
        assert receipt == json.loads(os.environ["CKAD19_EXPECTED_RESULT"]), "exact replica drift"
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write("result=" + json.dumps(receipt, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
