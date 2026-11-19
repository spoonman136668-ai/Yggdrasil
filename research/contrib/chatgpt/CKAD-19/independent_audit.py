"""Validate CKAD19 from pinned public rows and serialized counters using stdlib only."""

from collections import Counter
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
SOURCE_PIN = "016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d"
STAGE_PINS = {
    0: "e8d4ef72b0749e6f39d88342808460a567465ebdd8fdf4e10c8adca1947f8c2a",
    64: "da6c5f50c2c91675a859d80eefac43f37bca3d50d44b0e068449e1d16d7eefaf",
    128: "572200498c096e4d0bce27aef1318da21531ffd88d016df196e0c284f7e31638",
    192: "1705aca1ea9fba2a6ef1ac81e642c6e180649c47b75fad0890416a55f1c0b1e6",
}
FINAL_PINS = {
    101: "f8eb0c4dd92ca3e8a9ca2a70e21d337a28612101f3eec4ff807e584b7eacc91a",
    202: "da9c8f63d0f5f150d6fdb6a7f86bbba431c7f11bba33042f20c0308fad58db26",
    303: "d4074d6cf205a0dbc87b7cba8660d99415b4f981a951ef947073413a55e536c7",
}
BITS = (0, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def stable(result):
    """Exclude runtime measurements and the separate commit identity from semantic parity."""
    exclude = {"source_candidate_sha", "stable_sha256"}
    return canonical({key: value for key, value in result.items()
                      if key not in exclude and not key.endswith("_seconds")})


def source_rows():
    cache = (HERE.parent / "CKAD-16" / "source_public_fit.json").read_bytes()
    need(sha(cache) == SOURCE_PIN, "DTR cache identity")
    source = json.loads(cache)
    need(source["schema"] == "mass.dtr02.fit-public-traces.v1", "DTR cache schema")
    replicas = []
    seen = set()
    for index, entry in enumerate(source["replicas"]):
        need(index == entry["index"] and len(entry["fit"]) == 256, "DTR replica shape")
        for row in entry["fit"]:
            need(set(row) == {"seed", "s1", "x1", "s2", "x2", "y"}, "DTR row schema")
            need(type(row["seed"]) is int and row["seed"] not in seen, "DTR episode identity")
            need(all(type(row[k]) is int and row[k] in BITS for k in row if k != "seed"),
                 "DTR outcome domain")
            seen.add(row["seed"])
        replicas.append(entry["fit"])
    held = [row for replica in replicas for row in replica[192:]]
    need(len(replicas) == 3 and len(held) == 192, "DTR cohort size")
    return cache, replicas, held


def fixed(first, second):
    return [
        {"first_values": [[1, 2], [1, 2]], "first_action": first,
         "second_actions": [[second, second], [second, second]]}
        for _ in BITS
    ]


def reference(rows, pseudocount):
    """Fit transition and terminal frequencies and maximize public expected return."""
    transitions = Counter((row["s1"], row["x1"], row["s2"]) for row in rows)
    terminal = Counter((row["s1"], row["x1"], row["s2"], row["x2"], row["y"])
                       for row in rows)

    def probability(counts, key, outcome):
        total = sum(counts[(*key, bit)] + pseudocount for bit in BITS)
        if total == 0:
            return Fraction(1, 2)
        return Fraction(counts[(*key, outcome)] + pseudocount, total)

    plans = []
    for s1 in BITS:
        values = []
        actions = []
        for x1 in BITS:
            next_actions = []
            value = Fraction()
            for s2 in BITS:
                history = (s1, x1, s2)
                payoff, action = max(
                    (probability(terminal, (*history, x2), 1), -x2) for x2 in BITS
                )
                next_actions.append(-action)
                value += probability(transitions, history[:2], s2) * payoff
            actions.append(next_actions)
            values.append(value)
        plans.append({"first_values": [[v.numerator, v.denominator] for v in values],
                      "first_action": values.index(max(values)), "second_actions": actions})
    return plans


def compatible_payoffs(row, policies, terminal_only):
    """Enumerate states and payoffs compatible with one factual episode."""
    observed = (row["x1"], row["s2"], row["x2"])
    first = tuple(row["x1"] if terminal_only else policy["first_action"] for policy in policies)
    feasible = set()
    same_path = True
    for unseen_state in BITS:
        paths = []
        for policy, action in zip(policies, first, strict=True):
            state = row["s2"] if action == row["x1"] else unseen_state
            paths.append((action, state, policy["second_actions"][action][state]))
        same_path = same_path and len(set(paths)) == 1
        unknown = sorted(set(paths) - {observed})
        for values in product(BITS, repeat=len(unknown)):
            outcomes = dict(zip(unknown, values, strict=True))
            outcomes[observed] = row["y"]
            feasible.add(tuple(outcomes[path] for path in paths))
    return feasible, same_path


def expected_bounds(held, policy, controls, terminal_only):
    low = high = matches = 0
    paired = {name: {"difference_numerator": [0, 0], "guaranteed_agreements": 0}
              for name in controls}
    for row in held:
        s1 = row["s1"]
        feasible, _ = compatible_payoffs(row, [policy[s1]], terminal_only)
        values = [v[0] for v in feasible]
        low += min(values)
        high += max(values)
        matches += len(feasible) == 1
        for name, other in controls.items():
            possibilities, agreement = compatible_payoffs(row, [policy[s1], other[s1]], terminal_only)
            differences = [a - b for a, b in possibilities]
            paired[name]["difference_numerator"][0] += min(differences)
            paired[name]["difference_numerator"][1] += max(differences)
            paired[name]["guaranteed_agreements"] += agreement
    return {"episodes": len(held), "observed_matches": matches, "observed_successes": low,
            "return_numerator": [low, high], "paired": paired}


def expected_scores(held, native, mle):
    constants = {f"fixed_{a}{b}": fixed(a, b) for a, b in product(BITS, repeat=2)}
    controls = {**constants, "empirical_mle": mle}
    terminal = {"fixed_0": fixed(0, 0), "fixed_1": fixed(0, 1), "empirical_mle": mle}
    return {
        "two_stage": {name: expected_bounds(held, policy, controls, False)
                      for name, policy in {"native_beta": native, **controls}.items()},
        "logged_history_terminal": expected_bounds(held, native, terminal, True),
    }


def audit_bank(raw, replicas, prefix):
    checkpoint = json.loads(raw)
    if prefix == 0:
        need("dtr_ascii" not in checkpoint, "untrained checkpoint unexpectedly contains DTR")
        return
    dtr = json.loads(checkpoint["dtr_ascii"])
    need(dtr["stop"] == prefix and dtr["source_cache_sha256"] == SOURCE_PIN, "DTR state scope")
    counts = [0] * 64
    expected = []
    for replica in replicas:
        packed = bytearray()
        for row in replica[:prefix]:
            s1, x1, s2, x2, y = (row[key] for key in ("s1", "x1", "s2", "x2", "y"))
            packed.append((y << 4) | (x2 << 3) | (s2 << 2) | (x1 << 1) | s1)
            counts[4 * (8 + s1) + 2 * x1 + s2] += 1
            counts[4 * (s1 + 2 * x1 + 4 * s2) + 2 * x2 + y] += 1
        expected.append(packed.hex())
    need(dtr["rows_hex"] == expected, "DTR retained row contents")
    packet = b"YPC1" + struct.pack(">64H", *counts)
    packet += hashlib.sha256(packet).digest()
    need(dtr["native_counters_hex"] == packet.hex(), "DTR retained count contents")


def audit(path):
    result = json.loads(path.read_bytes())
    need(result["schema"] == "yggdrasil.ckad19.dtr-composed-decision.result.v1"
         and result["classification"] == "CACHED_DTR_COMPOSED_READOUT_SUPPORTED",
         "result schema or classification")
    need(result["stable_sha256"] == sha(stable(result)), "stable semantic digest")
    need(result["scientific_pass"] is result["accepted_native"] is False
         and result["original_source_actions"] == result["held_training_updates"] == 0
         and result["deployment"] == "NONE", "result evidence or authority scope")
    _, replicas, held = source_rows()
    for (prefix, pin), stage in zip(STAGE_PINS.items(), result["stages"], strict=True):
        need(stage["prefix"] == prefix and stage["checkpoint_sha256"] == pin
             and stage["native_available"] is bool(prefix), "stage or checkpoint lineage")
        raw = (HERE.parent / "CKAD-16" / f"seed-101-dtr-{prefix:03d}.json").read_bytes()
        need(sha(raw) == pin, "stage checkpoint bytes")
        audit_bank(raw, replicas, prefix)
        rows = [row for replica in replicas for row in replica[:prefix]]
        need(stage["training_episodes"] == len(rows), "training episode count")
        beta = reference(rows, 1)
        mle = reference(rows, 0)
        native = beta if prefix else fixed(0, 0)
        need((stage["native"], stage["exact_beta"], stage["empirical_mle"]) == (native, beta, mle),
             "trained plan or independent reference drift")
        need(stage["bounds"] == expected_scores(held, native, mle), "finite-cohort bounds")
    final = result["stages"][-1]
    stages = final["bounds"]["two_stage"]["native_beta"]["paired"]
    terminal = final["bounds"]["logged_history_terminal"]["paired"]
    need(result["two_stage_empirical_gain"] is all(row["difference_numerator"][0] > 0
                                                   for row in stages.values()), "two-stage gate")
    need(result["logged_history_terminal_empirical_gain"] is all(
        terminal[f"fixed_{i}"]["difference_numerator"][0] > 0 for i in BITS), "terminal gate")
    for (seed, pin), state in zip(FINAL_PINS.items(), result["final_ckad18_checkpoints"], strict=True):
        path = HERE.parent / "CKAD-18" / f"seed-{seed}-full-scope-native.json"
        raw = path.read_bytes()
        need(state["seed"] == seed and state["sha256"] == sha(raw) == pin, "CKAD18 checkpoint identity")
        audit_bank(raw, replicas, 192)
        need(state["cold_plan"] == final["exact_beta"], "cold plan from retained CKAD18 state")
    return {"classification": "INDEPENDENT_CACHED_DTR_POLICY_BOUNDS_VERIFIED",
            "stages": 4, "retained_replicas": 3, "held_episodes_per_stage": len(held),
            "stable_sha256": result["stable_sha256"], "native_imports": 0, "scientific_pass": False}


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "result.json"
    if path.is_dir():
        path = path / "result.json"
    print(json.dumps(audit(path), sort_keys=True))
