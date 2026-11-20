"""KNOW19: source-free, noncanonical single-witness candidate-aware probing.

Frozen protocol: know19_protocol.json at commit dfd1dd6c536c25e9fdaf99884ee9973b86fce16b.
The original native accumulator is trained on one *actual synthetic outcome*
per (public candidate mask, probe pattern, action), not a four-world teacher.
Candidate enumeration/consistency and the finite probe grammar remain analytic.
Neither this module nor its evidence are an accepted Yggdrasil model.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

TRAIN_A = 3119
TRAIN_B = 3251
HELD = (3371, 3463, 3593)
SEEDS = (TRAIN_A, TRAIN_B) + HELD
ROLES = (0, 1, 2, 3)
PREDICATES = (981, 982, 983, 984)
BASE_SUBJECT = 4_260_000_000
BASE_OBJECT = 4_275_000_000
PREREG_SHA = "dfd1dd6c536c25e9fdaf99884ee9973b86fce16b"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def require(condition, tag):
    if not condition:
        raise ValueError("YGG_KNOW19_" + tag)


def subject(seed, entity):
    require(type(seed) is int and seed in SEEDS
            and type(entity) is int and 0 <= entity < 16, "SOURCE_ID")
    raw = f"know19:public:subject:{seed}:{entity}".encode("ascii")
    return BASE_SUBJECT + int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % 9_999_983


def object_id(feature, bit):
    require(type(feature) is int and feature in ROLES
            and type(bit) is int and bit in (0, 1), "OBJECT_ID")
    raw = f"know19:public:object:{feature}:{bit}".encode("ascii")
    return BASE_OBJECT + int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % 9_999_983


def probe_patterns(seed):
    require(type(seed) is int and seed in SEEDS, "PATTERNS")
    result = list(range(16))
    random.Random(seed * 109 + 31).shuffle(result)
    return tuple(result)


def source_rows(seed):
    values = probe_patterns(seed)
    require(len(set(subject(seed, i) for i in range(16))) == 16
            and len(set(object_id(j, b) for j in ROLES for b in (0, 1))) == 8,
            "SOURCE_COLLISION")
    return tuple(sorted(
        (subject(seed, e), PREDICATES[j], object_id(j, (values[e] >> j) & 1))
        for e in range(16) for j in ROLES
    ))


class Facts:
    """Minimal typed synthetic factual source; never a real-source admission."""

    def __init__(self, mode="engineering_fixture_only",
                 provenance="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"):
        self.mode = mode
        self.provenance = provenance
        self.rows = {seed: set(source_rows(seed)) for seed in SEEDS}

    def fact(self, seed, q, p, o):
        observed = (q, p, o) in self.rows[seed]
        return {"classification": "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if observed else "UNKNOWN_ABSTAIN",
                "witnessed": observed, "source_mode": self.mode,
                "source_provenance": self.provenance,
                "native_accepted": False, "verified_new_real_knowledge": False,
                "can_write_causal_consequence": False}


def public_pattern(facts, seed, e):
    require(type(facts) is Facts and type(seed) is int and seed in SEEDS,
            "FACT_SOURCE")
    q = subject(seed, e)
    values = []
    for j in ROLES:
        items = [facts.fact(seed, q, PREDICATES[j], object_id(j, b))
                 for b in (0, 1)]
        valid = [
            x.get("classification") == "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
            and x.get("witnessed") is True
            and x.get("source_mode") == "engineering_fixture_only"
            and x.get("source_provenance") == "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
            and x.get("native_accepted") is False
            and x.get("verified_new_real_knowledge") is False
            and x.get("can_write_causal_consequence") is False
            for x in items
        ]
        require(valid.count(True) == 1, "MISSING_CONFLICTING_OR_FORGED_SOURCE")
        values.append(valid.index(True))
    return sum(v << i for i, v in enumerate(values))


def candidates(mask):
    require(type(mask) is int and 0 < mask < 16, "CANDIDATE_MASK")
    return tuple(k for k in ROLES if mask & (1 << k))


def pack_context(mask, pattern):
    require(type(pattern) is int and 0 <= pattern < 16, "PROBE_PATTERN")
    return (mask << 4) | pattern


def consequence(action, pattern, hidden_role):
    require(type(action) is int and action in (0, 1)
            and type(pattern) is int and 0 <= pattern < 16
            and type(hidden_role) is int and hidden_role in ROLES,
            "WITNESS")
    return action * ((pattern >> hidden_role) & 1)


def disclosed_feedback(mask, pattern, action, witnessed):
    """Post-action reduction from ONE witnessed consequence, not 4 worlds."""
    require(type(witnessed) is int and witnessed in (0, 1), "DISCLOSURE")
    prior = candidates(mask)
    remaining = tuple(k for k in prior
                      if consequence(action, pattern, k) == witnessed)
    require(0 < len(remaining) <= len(prior), "IMPOSSIBLE_WITNESS")
    return int(len(remaining) < len(prior)), sum(1 << k for k in remaining)


def private_training_role(seed, mask, pattern, action):
    """Only the simulator observes the role; no role enters native features."""
    options = candidates(mask)
    raw = f"know19:v1:{seed}:{mask}:{pattern}:{action}".encode("ascii")
    index = int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % len(options)
    return options[index]


def training_rows(facts, seed):
    require(seed in (TRAIN_A, TRAIN_B), "FIT_SEED")
    masks = tuple(m for m in range(1, 16)
                  if m.bit_count() >= 3) if seed == TRAIN_A else tuple(
                  m for m in range(1, 16) if m.bit_count() == 2)
    rows = []
    for mask in masks:
        for e in range(16):
            pattern = public_pattern(facts, seed, e)
            for action in (0, 1):
                role = private_training_role(seed, mask, pattern, action)
                response = consequence(action, pattern, role)
                label, remaining_mask = disclosed_feedback(mask, pattern, action, response)
                require(remaining_mask & (1 << role), "ROLE_LOST")
                rows.append([pack_context(mask, pattern), action, label])
    require(len(rows) == (160 if seed == TRAIN_A else 192)
            and len({(x, a) for x, a, y in rows}) == len(rows),
            "FROZEN_FIT_BUDGET")
    return sorted(rows)


def symbolic_fit(rows):
    table = {}
    for x, a, y in rows:
        require((x, a) not in table, "SYMBOLIC_DUPLICATE")
        table[x, a] = y
    return lambda x, a: table.get((x, a))


def tree_fit(rows):
    """Independent fully trained, deterministic CART-style binary tree."""
    examples = tuple((x | (a << 8), y) for x, a, y in rows)
    require(len({x for x, y in examples}) == len(examples), "TREE_UNIQUE")

    def fit(records, allowed):
        values = {y for x, y in records}
        if len(values) == 1:
            return next(iter(values))
        require(bool(allowed), "TREE_INADEQUATE")
        candidates_splits = []
        for bit in allowed:
            left = tuple(row for row in records if not row[0] & (1 << bit))
            right = tuple(row for row in records if row[0] & (1 << bit))
            if not left or not right:
                continue
            def impurity(group):
                ones = sum(v for _, v in group)
                return ones * (len(group) - ones) / len(group)
            candidates_splits.append((impurity(left) + impurity(right),
                                      bit, left, right))
        require(bool(candidates_splits), "TREE_UNSPLITTABLE")
        _, bit, left, right = min(candidates_splits, key=lambda x: (x[0], x[1]))
        other = tuple(i for i in allowed if i != bit)
        return (bit, fit(left, other), fit(right, other))

    root = fit(examples, tuple(range(9)))

    def predict(context, action):
        state = root
        key = context | (action << 8)
        while type(state) is tuple:
            bit, lo, hi = state
            state = hi if key & (1 << bit) else lo
        return state
    return predict


def select_query(facts, seed, remain, used, scorer, *, rng=None, singleton_only=False):
    require(type(remain) is tuple and 1 < len(remain) <= 4
            and len(set(remain)) == len(remain)
            and all(type(k) is int and k in ROLES for k in remain),
            "CURRENT_CANDIDATES")
    if scorer == "zero":
        return None
    permitted = []
    for e in range(16):
        pattern = public_pattern(facts, seed, e)
        if singleton_only and pattern.bit_count() != 1:
            continue
        for action in (0, 1):
            if (e, action) not in used:
                permitted.append((e, action, pattern))
    if scorer == "random":
        require(type(rng) is random.Random, "RNG")
        return rng.choice(permitted)[:2] if permitted else None
    if scorer == "passive":
        return next(((e, a) for e, a, p in permitted if a == 0), None)
    require(scorer == "oracle" or callable(scorer), "POLICY")
    mask = sum(1 << k for k in remain)
    scored = []
    for e, action, pattern in permitted:
        if scorer == "oracle":
            yes = sum(consequence(action, pattern, k) for k in remain)
            utility = min(yes, len(remain) - yes)
        else:
            utility = scorer(pack_context(mask, pattern), action)
        if utility is None:
            continue
        require(type(utility) is int and utility >= 0, "SCORER_OUTPUT")
        if utility > 0:
            scored.append((-utility, subject(seed, e), action, e))
    if not scored:
        return None
    _, _, action, entity = min(scored)
    return entity, action


def evaluate(facts, seed, hidden_role, scorer, singleton_only=False):
    require(type(seed) is int and seed in HELD and hidden_role in ROLES,
            "HELD_WORLD")
    remaining = ROLES
    used = set()
    transcript = []
    rng = random.Random(seed * 37 + 73)
    for step in range(2):
        if len(remaining) == 1:
            break
        query = select_query(facts, seed, remaining, used, scorer, rng=rng,
                             singleton_only=singleton_only)
        if query is None:
            break
        e, action = query
        used.add(query)
        pattern = public_pattern(facts, seed, e)
        response = consequence(action, pattern, hidden_role)
        previous = len(remaining)
        _, mask = disclosed_feedback(sum(1 << k for k in remaining),
                                     pattern, action, response)
        remaining = candidates(mask)
        require(hidden_role in remaining, "TRUE_ROLE_DISCARDED")
        transcript.append([e, action, response, previous, len(remaining)])
    return {"selected": remaining[0] if len(remaining) == 1 else None,
            "remaining": len(remaining), "entropy_bits": math.log2(len(remaining)),
            "witnessed_actions": len(transcript), "transcript": transcript}


def prove():
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_context_basis import NativeContextBasis
    started = time.monotonic()
    frozen = json.loads(Path(__file__).with_name("know19_protocol.json").read_text())
    require(frozen["schema"] == "yggdrasil.know19.single-witness-posterior-aware-probe-frozen-dev.v1"
            and frozen["seeds"]["train_A"] == TRAIN_A
            and frozen["seeds"]["train_B"] == TRAIN_B
            and frozen["seeds"]["held"] == list(HELD), "PREREG_DRIFT")
    facts = Facts()
    a = training_rows(facts, TRAIN_A)
    b = training_rows(facts, TRAIN_B)
    native = NativeContextAccumulator(context_bits=8).stage_update(
        0, a, digest(canonical(a)), max_degree=9)
    old = [native.predict(0, x, action) for x, action, y in a]
    require(all(o == y for o, (_, _, y) in zip(old, a)), "A_FIT")
    native = native.stage_update(0, b, digest(canonical(b)), max_degree=9)
    now = [native.predict(0, x, action) for x, action, y in a]
    drift = sum(before != after for before, after in zip(old, now))
    require(drift == 0, "A_DRIFT")
    ckpt = native.checkpoint()
    cold = NativeContextAccumulator.restore(ckpt, digest(ckpt))
    require(cold.checkpoint() == ckpt
            and [cold.predict(0, x, action) for x, action, y in a] == old,
            "COLD_RETENTION")
    combined = a + b
    require(all(cold.predict(0, x, act) == label for x, act, label in combined),
            "FULL_NATIVE_FIT")
    refit = NativeContextBasis(context_bits=8).stage_fit(
        0, combined, digest(canonical(combined)), max_degree=9)
    symbolic = symbolic_fit(combined)
    tree = tree_fit(combined)
    policies = {"native": lambda x, act: cold.predict(0, x, act),
                "refit": lambda x, act: refit.predict(0, x, act),
                "symbolic": symbolic, "tree": tree,
                "oracle": "oracle", "random": "random",
                "passive": "passive", "zero": "zero"}
    for context, action, label in combined:
        require(all(policy(context, action) == label
                    for name, policy in policies.items()
                    if name in ("native", "refit", "symbolic", "tree")),
                "FULLY_FITTED_CONTROL")
    held_scores = {}
    for name, policy in policies.items():
        runs = [evaluate(facts, seed, role, policy)
                for seed in HELD for role in ROLES]
        held_scores[name] = {
            "correct": sum(x["selected"] == role for x, role in
                           zip(runs, ROLES * len(HELD))),
            "actions": sum(x["witnessed_actions"] for x in runs),
            "remaining_candidates": sum(x["remaining"] for x in runs),
            "posterior_entropy_bits": sum(x["entropy_bits"] for x in runs),
        }
    singleton_runs = [evaluate(facts, seed, role, policies["native"], True)
                      for seed in HELD for role in ROLES]
    singleton = {
        "correct": sum(x["selected"] == role for x, role in
                       zip(singleton_runs, ROLES * len(HELD))),
        "actions": sum(x["witnessed_actions"] for x in singleton_runs),
        "zero_action_abstentions": sum(x["witnessed_actions"] == 0
                                     for x in singleton_runs),
    }
    engineering_pass = (
        held_scores["native"]["correct"] >= 10
        and singleton["zero_action_abstentions"] == 0
        and drift == 0
    )
    return {
        "schema": "yggdrasil.know19.synthetic-dev-result.v1",
        "prereg_commit": PREREG_SHA,
        "source_mode": "engineering_fixture_only",
        "training_witnessed_actions": len(combined),
        "train_A_actions": len(a), "train_B_actions": len(b),
        "new_B_public_input_cells": len(b),
        "old_A_predictions_changed": drift,
        "candidate_checkpoint_bytes": len(ckpt),
        "candidate_checkpoint_sha256": digest(ckpt),
        "held": held_scores, "singleton_1v3_diagnostic": singleton,
        "engineering_gate": "PASS" if engineering_pass else "FAIL",
        "scientific_gate": "DEV_NO_GO_SYNTHETIC_AND_STRONGEST_CONTROL",
        "accepted_checkpoint_changed": False, "original_world_first_use": False,
        "deployment": "NONE",
        "isolated_wall_seconds_excluding_repository_checkout": round(
            time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    print(json.dumps(prove(), sort_keys=True, indent=2))
