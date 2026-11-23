"""CCE06 DEV-only on-policy intervention frontier; no CAL or PRIMARY first-use.

The evaluation driver holds the environment and common terminal audit data.
A policy receives only its own public observations and action consequences.
Every alternative is fitted freshly from identical public TRAIN sequences.
This code *cannot* authenticate independent custody or scientific comparison.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from calibration_active_bayes import ActiveBayesianPolicy, COST
from calibration_controls import code, validated, multichannel_brier


@dataclass(frozen=True)
class PolicySpec:
    name: str
    kind: str = "active"
    alpha: float = 0.5
    probe_penalty: float = 0.05


class FixedSchedulePolicy(ActiveBayesianPolicy):
    """Explicitly weaker no-action or alternating-action references."""
    def __init__(self, schedule, *, alpha):
        super().__init__(alpha=alpha, probe_penalty=0)
        if type(schedule) is not tuple or not schedule or any(
            type(a) is not int or a not in COST for a in schedule
        ):
            raise ValueError("CCE06_BAD_REFERENCE_SCHEDULE")
        self.schedule = schedule

    def choose(self):
        if self.current is None or self.pending is not None:
            raise ValueError("CCE06_REFERENCE_NOT_READY")
        action = self.schedule[self.actions_taken % len(self.schedule)]
        if COST[action] + self.spent > self.budget:
            action = 0
        self.pending = (self.current[:], action)
        self.spent += COST[action]
        return action


def _digest(sequences):
    return hashlib.sha256(json.dumps(sequences, sort_keys=True,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()


def _fresh_policy(spec, train):
    if type(spec) is not PolicySpec or type(spec.name) is not str or not spec.name or \
            type(spec.kind) is not str or spec.kind not in ("active", "noop", "alternating"):
        raise ValueError("CCE06_BAD_POLICY_SPEC")
    if spec.kind == "active":
        policy = ActiveBayesianPolicy(alpha=spec.alpha, probe_penalty=spec.probe_penalty)
    else:
        if spec.probe_penalty != 0:
            raise ValueError("CCE06_REFERENCE_PENALTY_FORBIDDEN")
        policy = FixedSchedulePolicy((0,) if spec.kind == "noop" else (1, 2), alpha=spec.alpha)
    return policy.fit(train)


def _terminal_brier(policy, terminal):
    total, n = 0.0, 0
    for events in terminal:
        for e in events:
            # The policy never observes the target before this prediction.
            p = policy.posterior(e["observation"], e["action"])
            total += multichannel_brier(p, e["next_observation"])
            n += 1
    return total / n


def _episode(policy, env, *, steps, budget, terminal):
    obs = env.reset()
    code(obs)
    policy.start(obs[:], paid_budget=budget)
    actions = []
    for t in range(steps):
        action = policy.choose()
        if type(action) is not int or action not in COST:
            raise ValueError("CCE06_INVALID_CHOSEN_ACTION")
        # Calling step with the *selected* action is mandatory: never replay
        # the outcome of another action or a logged off-policy trajectory.
        following = env.step(action)
        code(following)  # rejects hidden/oracle fields and nonpublic signals
        public_event = dict(observation=obs[:], action=action,
                            next_observation=following[:])
        policy.update(public_event)
        obs = following[:]
        actions.append(action)
    if policy.pending is not None or policy.actions_taken != steps or \
            policy.spent != sum(COST[a] for a in actions) or policy.spent > budget:
        raise ValueError("CCE06_POLICY_COST_OR_WITNESS_MISMATCH")
    return dict(paid_actions=policy.spent, actions=tuple(actions),
                terminal_brier=_terminal_brier(policy, terminal))


def run_dev_frontier(train, terminal, env_factory, *, specs, budgets,
                     seeds=(997, 998, 999), steps=40):
    """Development-only descriptive frontier, with no scientific GO authority.

    The caller must independently prove TRAIN/terminal/family custody before
    using the method for actual science. Digests only reject exact duplicates.
    Inspecting the returned frontier to change experimental model selection is
    forbidden for preregistered CAL or PRIMARY first-use.
    """
    if type(train) not in (tuple, list) or not train or \
            type(terminal) not in (tuple, list) or not terminal or \
            not callable(env_factory) or type(specs) is not tuple or not specs or \
            type(budgets) is not tuple or not budgets or type(seeds) is not tuple or \
            not seeds or type(steps) is not int or not 1 <= steps <= 512 or \
            len(seeds) > 16 or len(set(seeds)) != len(seeds) or \
            any(type(seed) is not int or seed < 0 for seed in seeds) or \
            any(type(b) is not int or not 0 <= b <= steps for b in budgets) or \
            len(set(budgets)) != len(budgets):
        raise ValueError("CCE06_FRONTIER_INVALID_INPUT")
    for e in (*train, *terminal):
        validated(e)
    train_sha, audit_sha = _digest(train), _digest(terminal)
    if train_sha == audit_sha:
        raise ValueError("CCE06_TRAIN_TERMINAL_IDENTICAL")
    if len(set(s.name for s in specs)) != len(specs):
        raise ValueError("CCE06_DUPLICATE_POLICY_NAME")
    results = []
    for spec in specs:
        # Fail closed on invalid configuration even when no costed probes remain.
        _fresh_policy(spec, train)
        for budget in sorted(budgets):
            rows = []
            for seed in seeds:
                # Fresh policy prevents knowledge leaking across independent
                # evaluation episodes, except for the shared TRAIN baseline.
                policy = _fresh_policy(spec, train)
                env = env_factory(seed)
                rows.append(_episode(policy, env, steps=steps, budget=budget,
                                     terminal=terminal))
            spent = sum(row['paid_actions'] for row in rows) / len(rows)
            brier = sum(row['terminal_brier'] for row in rows) / len(rows)
            if not math.isfinite(brier) or not 0 <= brier <= 1 or spent > budget:
                raise ValueError("CCE06_NONFINITE_FRONTIER")
            results.append(dict(policy=spec.name, kind=spec.kind, budget=budget,
                                mean_paid_actions=spent, mean_terminal_brier=brier,
                                per_seed=tuple(dict(seed=s, **row)
                                               for s, row in zip(seeds, rows))))
    # Descriptive Pareto comparisons, NOT approval or model selection.
    frontier = tuple(row['policy'] + '@' + str(row['budget']) for row in results
                     if not any((other['mean_paid_actions'] <= row['mean_paid_actions'] and
                                 other['mean_terminal_brier'] <= row['mean_terminal_brier'] and
                                 (other['mean_paid_actions'] < row['mean_paid_actions'] or
                                  other['mean_terminal_brier'] < row['mean_terminal_brier']))
                                for other in results))
    return dict(status="DEV_FIXTURE_ONLY_SCIENCE_UNVERIFIED", steps=steps,
                seeds=seeds, terminal_sha256=audit_sha, train_sha256=train_sha,
                terminal_events=sum(len(e) for e in terminal),
                train_events=sum(len(e) for e in train),
                results=tuple(results), nondominated=frontier,
                custody_verified=False, gain_verified=False)
