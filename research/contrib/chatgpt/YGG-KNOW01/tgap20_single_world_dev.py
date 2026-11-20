"""TGAP20: bounded sequential single-world probabilistic causal witness research.

Not the canonical Yggdrasil learner. No original source use, model
integration, token processing, world-reset replay, or protected actions.
The frozen protocol precedes this implementation: 74b899e761909940296e1e7bef0d56b8629cc848.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

PREREG_SHA = "74b899e761909940296e1e7bef0d56b8629cc848"
SOURCE_MODE = "engineering_fixture_only"
TRAIN_WORLDS = ((4101, 0, "A"), (4201, 1, "B"))
HELD_WORLDS = (
    (4301, 0), (4311, 1), (4321, 2), (4331, 3),
    (4341, 0), (4351, 1), (4361, 2), (4371, 3),
)
STATES = 8


def require(condition, tag):
    if not condition:
        raise ValueError("YGG_TGAP20_" + tag)


def canonical(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def mechanism_bit(operator, x, action):
    require(type(operator) is int and operator in (0, 1, 2, 3),
            "PRIVATE_MECHANISM")
    require(type(x) is int and 0 <= x < 4
            and type(action) is int and action in (0, 1), "PUBLIC_INPUT")
    x0, x1 = x & 1, (x >> 1) & 1
    unacted = (x0, x1, x0 ^ x1, x0 & x1)[operator]
    return unacted ^ action


def world_events(seed, operator, n, *, evaluation=False):
    """Fixed latent law across all observations; fresh, disjoint noise stream."""
    require(type(seed) is int and type(n) is int and 0 < n <= 64,
            "EVENT_BUDGET")
    rng = random.Random(seed * 10007 + (741 if evaluation else 313))
    shift = seed % STATES
    result = []
    for step in range(n):
        cell = (step + shift) % STATES
        x, action = cell >> 1, cell & 1
        witnessed = mechanism_bit(operator, x, action) ^ int(rng.randrange(8) == 0)
        result.append((step, x, action, witnessed))
    return tuple(result)


class Experience:
    """Numerical native-style sufficient-statistics research candidate.

    Explicitly NOT NativeContextAccumulator, whose GF(2) target is deterministic.
    One public world key has eight cells with zero/one witness counts.
    """

    def __init__(self):
        self._tables = {}
        self._next = {}

    def stage(self, world_id, event, *, source_mode=SOURCE_MODE):
        require(source_mode == SOURCE_MODE, "FORGED_SOURCE")
        require(type(world_id) is str and 0 < len(world_id) <= 48,
                "WORLD_KEY")
        require(type(event) is tuple and len(event) == 4, "WITNESS_SHAPE")
        eid, x, action, consequence = event
        require(type(eid) is int and eid >= 0 and
                type(x) is int and 0 <= x < 4 and
                type(action) is int and action in (0, 1) and
                type(consequence) is int and consequence in (0, 1),
                "TYPED_WITNESS")
        expected = self._next.get(world_id, 0)
        require(eid == expected, "REPLAY_GAP_OR_DUPLICATE")
        if world_id not in self._tables:
            self._tables[world_id] = [[0, 0] for _ in range(STATES)]
        self._tables[world_id][2 * x + action][consequence] += 1
        self._next[world_id] = eid + 1

    def forecast(self, world_id, x, action):
        require(type(x) is int and 0 <= x < 4 and
                type(action) is int and action in (0, 1),
                "PUBLIC_FORECAST_INPUT")
        cells = self._tables.get(world_id)
        if cells is None:
            return 0.5
        n0, n1 = cells[2 * x + action]
        return (n1 + 1) / (n0 + n1 + 2)

    def checkpoint(self):
        return canonical({
            "schema": "yggdrasil.tgap20.numeric-experience.v1",
            "mode": SOURCE_MODE,
            "tables": self._tables,
            "next": self._next,
        })

    @classmethod
    def restore(cls, raw, source_sha256):
        require(type(raw) is bytes and digest(raw) == source_sha256,
                "COLD_SOURCE_DIGEST")
        doc = json.loads(raw)
        require(doc.get("schema") == "yggdrasil.tgap20.numeric-experience.v1"
                and doc.get("mode") == SOURCE_MODE
                and canonical(doc) == raw, "COLD_SCHEMA")
        tables = doc.get("tables")
        next_ids = doc.get("next")
        require(type(tables) is dict and type(next_ids) is dict
                and set(tables) == set(next_ids), "COLD_WORLD_MAP")
        obj = cls()
        for key, cells in tables.items():
            require(type(key) is str and 0 < len(key) <= 48
                    and type(cells) is list and len(cells) == STATES
                    and all(type(c) is list and len(c) == 2
                            and all(type(v) is int and 0 <= v <= 64 for v in c)
                            for c in cells), "COLD_COUNTS")
            seen = next_ids[key]
            require(type(seen) is int and seen == sum(sum(c) for c in cells),
                    "COLD_EVENT_COUNT")
            obj._tables[key] = cells
            obj._next[key] = seen
        require(obj.checkpoint() == raw, "COLD_ROUNDTRIP")
        return obj


def symbolic_beta(events):
    """Separate full batch symbolic categorical maximum posterior predictor."""
    cells = {(x, a): [0, 0] for x in range(4) for a in (0, 1)}
    for _, x, a, y in events:
        cells[x, a][y] += 1
    return lambda x, a: (cells[x, a][1] + 1) / (sum(cells[x, a]) + 2)


def categorical_tree(events):
    """Fully fitted independent depth-three tree with Beta-smoothed leaves."""
    leaves = [[], []]
    for k in range(2):
        leaves[k] = [[], []]
        for j in range(2):
            leaves[k][j] = [[], []]
            for a in range(2):
                leaves[k][j][a] = [0, 0]
    for _, x, a, y in events:
        leaves[x & 1][(x >> 1) & 1][a][y] += 1

    def predict(x, a):
        n0, n1 = leaves[x & 1][(x >> 1) & 1][a]
        return (n1 + 1) / (n0 + n1 + 2)
    return predict


def exact_bayesian(events):
    """Fully updated four-hypothesis likelihood model; same event observations."""
    ll = [0.0 for _ in range(4)]
    for _, x, a, y in events:
        for k in range(4):
            p = 0.875 if mechanism_bit(k, x, a) else 0.125
            ll[k] += math.log(p if y else 1 - p)
    shift = max(ll)
    unscaled = [math.exp(t - shift) for t in ll]
    norm = sum(unscaled)
    weights = [v / norm for v in unscaled]

    def predict(x, a):
        return sum(w * (0.875 if mechanism_bit(k, x, a) else 0.125)
                   for k, w in enumerate(weights))
    return predict


def brier(p, y):
    require(0 <= p <= 1 and type(y) is int and y in (0, 1),
            "SCORING_INPUT")
    return (p - y) ** 2


def prove():
    """Run the ONE frozen synthetic trial and return bounded numerical receipt."""
    t0 = time.monotonic()
    proto = json.loads(Path(__file__).with_name("tgap20_protocol.json")
                       .read_text(encoding="utf-8"))
    require(proto["schema"] ==
            "yggdrasil.tgap20.sequential-single-world-probability-prereg.v1"
            and tuple(proto["seeds"]["held"]) ==
            tuple(s for s, _ in HELD_WORLDS)
            and proto["budgets"]["held_train_witnessed_actions_per_world"] == 24
            and proto["budgets"]["held_eval_queries_per_world"] == 64,
            "PREREG_DRIFT")
    experience = Experience()
    a_events = world_events(4101, 0, 64)
    b_events = world_events(4201, 1, 64)
    for event in a_events:
        experience.stage("world-A", event)
    old = tuple(experience.forecast("world-A", x, a)
                for x in range(4) for a in (0, 1))
    for event in b_events:
        experience.stage("world-B", event)
    after = tuple(experience.forecast("world-A", x, a)
                  for x in range(4) for a in (0, 1))
    drift = sum(x != y for x, y in zip(old, after))
    saved = experience.checkpoint()
    cold = Experience.restore(saved, digest(saved))
    require(drift == 0 and cold.checkpoint() == saved and
            tuple(cold.forecast("world-A", x, a)
                  for x in range(4) for a in (0, 1)) == old,
            "OLD_A_COLD_RETENTION")
    score = {key: [] for key in
             ("experience", "symbolic", "tree", "bayesian", "source_only", "oracle")}
    by_operator = {str(k): [] for k in range(4)}
    calibration = {}
    world_results = []
    for seed, hidden in HELD_WORLDS:
        key = "held-" + str(seed)
        train = world_events(seed, hidden, 24)
        test = world_events(seed, hidden, 64, evaluation=True)
        world_model = Experience()
        for event in train:
            world_model.stage(key, event)
        world_cold_raw = world_model.checkpoint()
        restored = Experience.restore(world_cold_raw, digest(world_cold_raw))
        symbol = symbolic_beta(train)
        tree = categorical_tree(train)
        bayes = exact_bayesian(train)
        metrics = {k: [] for k in score}
        for _, x, action, observed in test:
            p = {
                "experience": restored.forecast(key, x, action),
                "symbolic": symbol(x, action),
                "tree": tree(x, action),
                "bayesian": bayes(x, action),
                "source_only": 0.5,
                "oracle": 0.875 if mechanism_bit(hidden, x, action) else 0.125,
            }
            for name, estimate in p.items():
                loss = brier(estimate, observed)
                score[name].append(loss)
                metrics[name].append(loss)
            by_operator[str(hidden)].append(brier(p["experience"], observed))
            bin_index = min(3, int(p["experience"] * 4))
            calibration.setdefault(bin_index, []).append(
                (p["experience"], observed))
        world_results.append({
            "world_seed": seed,
            "mechanism_scoring_only": hidden,
            "training_interventions": len(train),
            "evaluation_events": len(test),
            "experience_brier": round(sum(metrics["experience"]) / 64, 8),
            "bayesian_brier": round(sum(metrics["bayesian"]) / 64, 8),
            "cold_restored": restored.checkpoint() == world_cold_raw,
        })
    averages = {k: round(sum(xs) / len(xs), 8) for k, xs in score.items()}
    calibration_bins = {
        str(k): {"n": len(xs),
                 "predicted": round(sum(p for p, _ in xs) / len(xs), 6),
                 "observed": round(sum(y for _, y in xs) / len(xs), 6)}
        for k, xs in sorted(calibration.items())
    }
    gate = (averages["experience"] <= 0.23 and
            averages["source_only"] == 0.25 and drift == 0 and
            all(w["cold_restored"] for w in world_results))
    return {
        "schema": "yggdrasil.tgap20.single-world-witness-result.v1",
        "preregistration_sha": PREREG_SHA,
        "source_mode": SOURCE_MODE,
        "native_original_accumulator_modified": False,
        "learner": "independent bounded numeric witness-count research substrate",
        "old_A_witnesses": len(a_events), "new_B_witnesses": len(b_events),
        "held_train_witnesses": len(HELD_WORLDS) * 24,
        "held_scored_witnesses": sum(len(score[k]) for k in ("experience",)),
        "held_brier": averages,
        "held_by_operator_experience_brier": {
            k: round(sum(v) / len(v), 8) for k, v in by_operator.items()
        },
        "calibration": calibration_bins,
        "worlds": world_results,
        "retained_A_8_readouts_drift": drift,
        "old_A_checkpoint_bytes": len(saved),
        "old_A_cold_restore": True,
        "engineering_gate": "PASS" if gate else "FAIL",
        "scientific_gate": "DEV_NO_GO_SYNTHETIC_STRONG_CONTROLS",
        "canonical_trainer": False, "protected_first_use": False,
        "deployment": "NONE",
        "elapsed_seconds_excluding_checkout": round(time.monotonic() - t0, 6),
    }


if __name__ == "__main__":
    print("YGG_TGAP20_RESULT=" + json.dumps(prove(), sort_keys=True))
