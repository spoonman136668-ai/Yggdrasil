#!/usr/bin/env python3
"""F50 evaluator-only novel target admission and sealed scoring.

This module is never imported by F50 learners. Importing it constructs no
development target laws or outcomes. Development first use is explicitly
interlocked and requires independently verified exact-source CI/authority.
Fixtures exercise the evaluator without consuming a DEV-world target.
"""
from hashlib import sha256
import json
import math

import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.private-target-evaluator.v1"
FROZEN_PREREG_BLOB = "4bd3c4e0d3de0e3910094e38c14a0141c97ad380"
FAMILY = {
    4013: "context_dependent_conjunctive_cross_step_gate",
    4057: "two_lag_inhibition_delay",
    4099: "unseen_modular_composition_under_context_switch",
}
CHECKPOINTS = (16, 32, 64)
MAX_PUBLIC_EVENTS = 64


class TargetAdmissionRejected(world.F50Rejected):
    pass


def _derivative(terms, variable):
    """Exact Boolean derivative ANF; nonempty proves an intervention witness."""
    bit = 1 << variable
    return frozenset(term ^ bit for term in terms if term & bit)


def _admit_exact(size, rule):
    """Exact full-domain novelty and causal-contrast proof; returns no target."""
    world._check_bank_size(size)
    try:
        depth = world.ast_depth(rule)
        if not 4 <= depth <= 6:
            raise TargetAdmissionRejected("F50_TARGET_DEPTH_OUT_OF_CONTRACT")
        terms = world.anf(rule)
        if terms in set(map(world.anf, world.source_bank(size))):
            raise TargetAdmissionRejected("F50_TARGET_EXACT_SOURCE_COLLISION")
        deps = world.dependencies(rule)
        action_ids = {bit % 10 for bit in deps if bit < 30}
        contexts = [bit for bit in deps if bit >= 30]
        lagged = [bit for bit in deps if 10 <= bit < 30]
        if len(action_ids) < 3 or not contexts or not lagged:
            raise TargetAdmissionRejected("F50_TARGET_MISSING_CAUSAL_DEPENDENCY")
        # A single true ANF interaction must jointly involve context, delayed
        # cause, and >=3 *different* action identities; not merely a union of
        # separate unrelated effects.
        connected = any(
            (mask >> 30) != 0
            and (mask & (((1 << 30) - 1) ^ ((1 << 10) - 1))) != 0
            and len({i % 10 for i in range(30) if (mask >> i) & 1}) >= 3
            for mask in terms
        )
        if not connected:
            raise TargetAdmissionRejected("F50_TARGET_NO_HIGH_ORDER_COMPOSITION")
        if any(not _derivative(terms, bit) for bit in deps):
            raise TargetAdmissionRejected("F50_TARGET_NO_POSITIVE_INTERVENTION_CONTRAST")
    except (RecursionError, MemoryError) as exc:
        raise TargetAdmissionRejected("F50_TASK_INVALID_EXACT_ADMISSION_RESOURCE_STOP") from exc
    return {
        "full_domain_exact_nonmembership": True,
        "boolean_derivative_witnesses": len(deps),
        "distinct_action_identities": len(action_ids),
        "has_context_contrast": True,
        "has_lagged_contrast": True,
        "high_order_context_lag_interaction": True,
        "target_outcomes_consumed": 0,
        "scientific_pass": False,
    }


def _development_law(size, seed):
    """Evaluator-private deterministic construction. Never call in CI tests."""
    world._check_bank_size(size)
    world._check_dev_seed(seed)
    order = sorted(range(10),
                   key=lambda i: (world.digest("F50/target-development/v1",
                                              size, seed, "action-id", i), i))
    a, b, c = (world.leaf(i) for i in order[:3])
    context = world.leaf(30 + world.random_uint("F50/target-development/v1", size, seed) % 3)
    lag1a = world.leaf(10 + order[0])
    lag1b = world.leaf(10 + order[1])
    lag2c = world.leaf(20 + order[2])
    core = ("and", context, ("and", ("and", a, b), lag2c))
    if seed == 4013:
        return ("xor", core, ("and", ("not", context), ("xor", c, lag1a)))
    if seed == 4057:
        return ("xor", core,
                ("and", ("not", ("and", lag2c, b)),
                 ("xor", ("and", context, c), ("xor", a, lag1b))))
    return ("xor",
            ("and", context,
             ("xor", ("and", a, lag1b), ("or", b, lag2c))),
            ("xor", ("and", ("not", context), ("or", c, lag1a)), core))


def _canonical_episodes(candidates):
    if type(candidates) not in (tuple, list) or not candidates:
        raise TargetAdmissionRejected("F50_PRIVATE_INPUTS_INVALID")
    seen = set()
    out = []
    for candidate in candidates:
        episode = world.validate_trajectory(candidate)
        if episode in seen:
            raise TargetAdmissionRejected("F50_PRIVATE_INPUT_REPLAY")
        seen.add(episode)
        out.append(episode)
    return tuple(out)


def _check_release(ticket):
    """An interlock only. External controller must verify CI and authority."""
    if (type(ticket) is not dict
        or set(ticket) != {"candidate_sha", "ubuntu_pass", "windows_pass",
                           "protocol_blob", "operator_first_use"}
        or type(ticket["candidate_sha"]) is not str
        or len(ticket["candidate_sha"]) != 40
        or any(c not in "0123456789abcdef" for c in ticket["candidate_sha"])
        or ticket["protocol_blob"] != FROZEN_PREREG_BLOB
        or ticket["ubuntu_pass"] is not True
        or ticket["windows_pass"] is not True
        or ticket["operator_first_use"] is not True):
        raise TargetAdmissionRejected("F50_DEV_TARGET_FIRST_USE_BLOCKED")
    return ticket["candidate_sha"]


class PrivateTargetEvaluator:
    """Evaluator API: public noisy feedback, held-out inputs, aggregate scores.

    No target program, ANF, signature, or clean labels returned by its methods.
    Python object introspection is not a security boundary: run in a separate
    evaluator process/container from learner code when scientific first-used.
    """
    __slots__ = ("_size", "_seed", "_rule", "_public", "_heldout",
                 "_used", "_scored", "_source_sha", "_fixture")

    def __init__(self, size, seed, rule, public, heldout, source_sha, fixture):
        self._size = size
        self._seed = seed
        self._rule = rule
        self._public = _canonical_episodes(public)
        self._heldout = _canonical_episodes(heldout)
        if set(self._public) & set(self._heldout):
            raise TargetAdmissionRejected("F50_PRIVATE_EVAL_PUBLIC_OVERLAP")
        self._used = set()
        self._scored = set()
        self._source_sha = source_sha
        self._fixture = fixture

    @classmethod
    def open_development(cls, size, seed, *, externally_verified_release=None):
        world.freeze()
        world._check_bank_size(size)
        world._check_dev_seed(seed)
        source_sha = _check_release(externally_verified_release)
        # No target formula or outcome is constructed before this line.
        rule = _development_law(size, seed)
        _admit_exact(size, rule)
        public = world.public_candidate_pool(size, seed)
        heldout = world.sealed_heldout_inputs_for_evaluator_only(size, seed)
        if len(public) != 512 or len(heldout) != 512:
            raise TargetAdmissionRejected("F50_TASK_INVALID_TRAJECTORY_COUNT")
        return cls(size, seed, rule, public, heldout, source_sha, False)

    @classmethod
    def synthetic_fixture(cls, size, rule, public, heldout):
        """Only caller-supplied synthetic law/inputs, no DEV seed/namespace."""
        world.freeze()
        _admit_exact(size, rule)
        return cls(size, None, rule, public, heldout, None, True)

    def public_candidates(self):
        return self._public

    def heldout_inputs_for_prediction(self):
        """Evaluation inputs only, never clean evaluator truth."""
        return self._heldout

    def public_event(self, index, trajectory):
        if (type(index) is not int or not 0 <= index < len(self._public)
            or len(self._used) >= MAX_PUBLIC_EVENTS
            or index in self._used
            or world.validate_trajectory(trajectory) != self._public[index]):
            raise TargetAdmissionRejected("F50_PRIVATE_PUBLIC_EVENT_NOT_ADMITTED")
        truth = world._episode_truth(self._rule, self._public[index])
        namespace = "F50/synthetic-fixture-only/v1" if self._fixture else world.NOISE_NS
        bits = tuple(
            outcome ^ int(world.random_uint(namespace, "target", self._size,
                                           self._seed if not self._fixture else 0,
                                           index, step, 0) < world.NOISE_BOUND)
            for step, outcome in enumerate(truth)
        )
        self._used.add(index)
        return bits

    def score_once(self, predictions):
        budget = len(self._used)
        if budget not in CHECKPOINTS or budget in self._scored:
            raise TargetAdmissionRejected("F50_PRIVATE_SCORE_NOT_AT_FROZEN_CHECKPOINT")
        if type(predictions) not in (list, tuple) or len(predictions) != len(self._heldout):
            raise TargetAdmissionRejected("F50_PRIVATE_SCORE_INPUT_COUNT")
        checked = []
        for row in predictions:
            if (type(row) not in (list, tuple) or len(row) != 3
                or any(type(x) not in (float, int) or not math.isfinite(x)
                       or not 0 <= x <= 1 for x in row)):
                raise TargetAdmissionRejected("F50_PRIVATE_SCORE_PROBABILITIES_INVALID")
            checked.append(tuple(float(x) for x in row))
        correct, total = 0, 0
        for episode, probs in zip(self._heldout, checked):
            truth = world._episode_truth(self._rule, episode)
            correct += sum((p >= 0.5) == bool(y) for p, y in zip(probs, truth))
            total += 3
        self._scored.add(budget)
        return {"schema": SCHEMA, "query_budget": budget,
                "clean_heldout_accuracy": correct / total,
                "scored_clean_bits": total, "fixture_only": self._fixture,
                "target_law_disclosed": False, "scientific_pass": False}

    def public_receipt(self):
        return {"schema": SCHEMA, "source_candidate_sha": self._source_sha,
                "public_events_used": len(self._used),
                "observed_public_bits": 3 * len(self._used),
                "scored_checkpoints": sorted(self._scored),
                "fixture_only": self._fixture,
                "protected_cohorts_consumed": 0}


if __name__ == "__main__":
    world.freeze()
    print("F50_PRIVATE_TARGET_EVALUATOR_CODE_READY_NO_DEV_FIRST_USE")
