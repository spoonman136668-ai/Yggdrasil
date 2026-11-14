"""WSP99 fixture-only source/action construction and blind prediction-first evaluation.

This module permits ONLY the eight public development fixtures, NOT original
PUBLIC/RESERVED scientific worlds. It never reads simulator hidden state,
programs, triggers or evaluator-only witnesses to select actions.
"""
from __future__ import annotations

import hashlib
import json
import time

from task import ACTIONS, EPISODE_LIMIT, FixtureWorld, bits, rank, valid_state
from controls import validate_episodes

PASSIVE_EPISODES = 24
INVESTIGATIVE_EPISODES = 8
HELDOUT_TARGETS = 24
HELDOUT_STEPS = 3
SOURCE_SCHEMA = "wsp99.fixture-source.v1"
EVAL_SCHEMA = "wsp99.fixture-blind-evaluation.v1"


def _check_fixture(fixture_id):
    if type(fixture_id) is not int or not 0 <= fixture_id < 8:
        raise PermissionError("original public/reserved worlds are not admitted")
    return fixture_id


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256(data):
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _episode(world, initial, choose):
    x = world.reset(initial)
    rows = []
    prev_action = -1
    for step in range(EPISODE_LIMIT):
        action = choose(step, x, prev_action)
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("source policy generated invalid action")
        result = world.step(action)
        if set(result) != {"observation", "reward"}:
            raise ValueError("source received unexpected oracle fields")
        next_x = valid_state(result["observation"])
        if result["reward"] != (next_x[0] & next_x[1]):
            raise ValueError("reward not determined by next visible state")
        rows.append((x, action, next_x))
        x = next_x
        prev_action = action
    return tuple(rows)


class _VisibleCoverage:
    """Uses prior observed visible/action history only; no evaluator oracle."""

    def __init__(self, passive, fixture_id):
        self.fixture_id = fixture_id
        self.seen_pairs = set()
        self.seen_links = set()
        self.action_counts = [0] * ACTIONS
        for episode in passive:
            previous = -1
            for x, action, _next in episode:
                self._remember(x, action, previous)
                previous = action

    def _remember(self, x, action, previous):
        self.seen_pairs.add((x, action))
        self.seen_links.add((previous, action))
        self.action_counts[action] += 1

    def choose(self, global_step, visible, previous):
        min_count = min(self.action_counts)
        choices = []
        for action in range(ACTIONS):
            merit = (
                16 * int((visible, action) not in self.seen_pairs)
                + 4 * int((previous, action) not in self.seen_links)
                + int(self.action_counts[action] == min_count)
            )
            tie = rank(self.fixture_id, "ACTIVE-TIE", ACTIONS * global_step + action)
            choices.append((-merit, tie, action))
        return min(choices)[2]

    def remember(self, x, action, previous):
        self._remember(x, action, previous)


def make_fixture_sources(fixture_id):
    """One frozen 96-transition common passive source plus 32 actions per arm."""
    fixture_id = _check_fixture(fixture_id)
    passive_world = FixtureWorld(fixture_id)
    passive = []
    for index in range(PASSIVE_EPISODES):
        initial = bits(rank(fixture_id, "PASSIVE-INIT", index) % 64)
        episode = _episode(
            passive_world, initial,
            lambda step, _x, _prev, i=index: rank(
                fixture_id, "PASSIVE-ACT", EPISODE_LIMIT * i + step
            ) % ACTIONS,
        )
        passive.append(episode)
    passive = tuple(passive)
    coverage = _VisibleCoverage(passive, fixture_id)
    active_world = FixtureWorld(fixture_id)
    random_world = FixtureWorld(fixture_id)
    active, random = [], []
    for index in range(INVESTIGATIVE_EPISODES):
        initial = bits(rank(fixture_id, "INVESTIGATE-INIT", index) % 64)

        def choose_active(step, visible, previous, i=index):
            return coverage.choose(EPISODE_LIMIT * i + step, visible, previous)

        # Only record coverage after acquiring a genuine observation.
        # _episode invokes choose before the oracle transition. A separate
        # passive, visible-only replay below updates the policy per step.
        def active_episode():
            x = active_world.reset(initial)
            rows = []
            previous = -1
            for step in range(EPISODE_LIMIT):
                action = choose_active(step, x, previous)
                outcome = active_world.step(action)
                if set(outcome) != {"observation", "reward"}:
                    raise ValueError("oracle field leakage")
                next_x = valid_state(outcome["observation"])
                if outcome["reward"] != next_x[0] & next_x[1]:
                    raise ValueError("invalid visible reward")
                rows.append((x, action, next_x))
                coverage.remember(x, action, previous)
                x, previous = next_x, action
            return tuple(rows)

        active.append(active_episode())
        random.append(_episode(
            random_world, initial,
            lambda step, _x, _prev, i=index: rank(
                fixture_id, "RANDOM-ACT", EPISODE_LIMIT * i + step
            ) % ACTIONS,
        ))
    active, random = tuple(active), tuple(random)
    for name, arm in (("passive", passive), ("active", active), ("random", random)):
        validate_episodes(arm)
        if len(arm) != (PASSIVE_EPISODES if name == "passive" else INVESTIGATIVE_EPISODES):
            raise ValueError("source episode count changed")
    if any(a[0][0] != r[0][0] for a, r in zip(active, random)):
        raise ValueError("active/random initial states differ")
    doc = {
        "schema": SOURCE_SCHEMA, "fixture_id": fixture_id,
        "passive": passive, "active": active, "random": random,
    }
    return {
        **doc,
        "source_sha256": _sha256(doc),
        "passive_sha256": _sha256(passive),
        "active_sha256": _sha256(active),
        "random_sha256": _sha256(random),
        "active_action_count": EPISODE_LIMIT * len(active),
        "random_action_count": EPISODE_LIMIT * len(random),
    }


def verify_sources(bundle):
    if not isinstance(bundle, dict) or bundle.get("schema") != SOURCE_SCHEMA:
        raise ValueError("unknown source schema")
    _check_fixture(bundle.get("fixture_id"))
    if set(bundle) != {
        "schema", "fixture_id", "passive", "active", "random",
        "source_sha256", "passive_sha256", "active_sha256",
        "random_sha256", "active_action_count", "random_action_count"
    }:
        raise ValueError("unregistered source fields")
    for name, expected in (
        ("passive", PASSIVE_EPISODES),
        ("active", INVESTIGATIVE_EPISODES),
        ("random", INVESTIGATIVE_EPISODES),
    ):
        arm = validate_episodes(bundle[name])
        if len(arm) != expected or _sha256(arm) != bundle[name + "_sha256"]:
            raise ValueError("source count or digest invalid")
    if bundle["active_action_count"] != 32 or bundle["random_action_count"] != 32:
        raise ValueError("unequal action budget")
    if any(a[0][0] != r[0][0] for a, r in zip(bundle["active"], bundle["random"])):
        raise ValueError("different investigative starting states")
    expected = _sha256({k: bundle[k] for k in
        ("schema", "fixture_id", "passive", "active", "random")})
    if expected != bundle["source_sha256"]:
        raise ValueError("source receipt mismatch")
    return True


def make_fixture_heldout_plan(bundle):
    """Fix plans WITHOUT asking for any target outcomes."""
    verify_sources(bundle)
    fixture_id = bundle["fixture_id"]
    observed_starts = set(
        episode[0][0] for name in ("passive", "active", "random")
        for episode in bundle[name]
    )
    candidates = [bits(i) for i in range(64) if bits(i) not in observed_starts]
    candidates.sort(key=lambda x: rank(
        fixture_id, "HELDOUT-INIT", sum(bit << i for i, bit in enumerate(x))
    ))
    if len(candidates) < HELDOUT_TARGETS:
        raise ValueError("not enough disjoint heldout initial states")
    plans = []
    for index, initial in enumerate(candidates[:HELDOUT_TARGETS]):
        a = rank(fixture_id, "HELDOUT-A", index) % ACTIONS
        b = (a + 1 + rank(fixture_id, "HELDOUT-B", index) % (ACTIONS - 1)) % ACTIONS
        second = rank(fixture_id, "HELDOUT-C", 3 * index + 1) % ACTIONS
        third = rank(fixture_id, "HELDOUT-C", 3 * index + 2) % ACTIONS
        plans.append((initial, (a, second, third), (b, second, third)))
    return {
        "fixture_id": fixture_id,
        "source_sha256": bundle["source_sha256"],
        "targets": tuple(plans),
        "plan_sha256": _sha256(plans),
    }


def _validated_prediction_set(plan, predictions):
    if not isinstance(predictions, (tuple, list)) or len(predictions) != HELDOUT_TARGETS:
        raise ValueError("must predict all 24 heldout target pairs before scoring")
    clean = []
    for index, pair in enumerate(predictions):
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("both counterfactual branches required")
        branches = []
        for trajectory in pair:
            if not isinstance(trajectory, (tuple, list)) or len(trajectory) != HELDOUT_STEPS:
                raise ValueError("three prediction steps required per branch")
            branches.append(tuple(valid_state(bits) for bits in trajectory))
        clean.append(tuple(branches))
    return tuple(clean)


def make_predictions(plan, rollout):
    """Adapter for any source-only learner's forward rollout.

    The rollout callback gets a visible initial state and actions ONLY; it must
    return three predicted visible 6-bit states and may not call the evaluator.
    """
    predictions = []
    for initial, branch_a, branch_b in plan["targets"]:
        predictions.append((tuple(rollout(initial, branch_a)),
                            tuple(rollout(initial, branch_b))))
    return _validated_prediction_set(plan, predictions)


def score_fixture_predictions(bundle, plan, predictions):
    """Prediction hashes are computed BEFORE evaluator exposes heldout truth.

    This is a fixture diagnostic, not sealed independent scientific first use.
    """
    verify_sources(bundle)
    fixture_id = bundle["fixture_id"]
    expected = make_fixture_heldout_plan(bundle)
    if plan != expected or plan["fixture_id"] != fixture_id:
        raise ValueError("heldout plan drift")
    frozen = _validated_prediction_set(plan, predictions)
    frozen_source = bundle["source_sha256"]
    frozen_plan = plan["plan_sha256"]
    prediction_hash = _sha256(frozen)
    seal = _sha256({"source": frozen_source, "plan": frozen_plan,
                    "predictions": prediction_hash})
    # No original world factory exists. The evaluator is called only after
    # every prediction has been validated, serialized and hashed.
    truth = []
    tick0 = time.process_time_ns()
    for initial, branch_a, branch_b in plan["targets"]:
        trajectories = []
        for sequence in (branch_a, branch_b):
            world = FixtureWorld(fixture_id)
            world.reset(initial)
            trajectories.append(tuple(
                valid_state(world.step(action)["observation"]) for action in sequence
            ))
        truth.append(tuple(trajectories))
    cpu_time_ns = time.process_time_ns() - tick0
    per_step = [0] * HELDOUT_STEPS
    delayed_pairs = 0
    reward_brier_sum = 0.0
    for truth_pair, prediction_pair in zip(truth, frozen):
        if truth_pair[0][0] != truth_pair[1][0]:
            raise ValueError("immediate action effect invalid")
        delayed_pairs += int(truth_pair[0][1] != truth_pair[1][1])
        for actual, guessed in zip(truth_pair, prediction_pair):
            for step, (target_state, predicted_state) in enumerate(zip(actual, guessed)):
                per_step[step] += sum(int(y == p)
                                      for y, p in zip(target_state, predicted_state))
                target_reward = target_state[0] & target_state[1]
                predicted_reward = predicted_state[0] & predicted_state[1]
                reward_brier_sum += (target_reward - predicted_reward) ** 2
    denominator = HELDOUT_TARGETS * 2 * 6
    return {
        "schema": EVAL_SCHEMA, "fixture_id": fixture_id,
        "source_sha256": frozen_source, "plan_sha256": frozen_plan,
        "prediction_sha256": prediction_hash, "pre_score_sha256": seal,
        "target_truth_sha256": _sha256(truth),
        "predictions_frozen_before_truth": True,
        "per_step_correct": tuple(per_step),
        "per_step_total": denominator,
        "terminal_accuracy": per_step[-1] / denominator,
        "delayed_pair_count": delayed_pairs,
        "delayed_pair_total": HELDOUT_TARGETS,
        "reward_brier": reward_brier_sum / (HELDOUT_TARGETS * 2 * HELDOUT_STEPS),
        "evaluator_cpu_ns": cpu_time_ns,
        "scientific_superiority": False,
        "classification": "FIXTURE_DEVELOPMENT_ONLY",
    }
