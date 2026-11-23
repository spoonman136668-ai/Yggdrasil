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


def _paired_noise_receipt(env):
    """Caller-reported exogenous-noise commitment, never a custody proof.

    A compliant evaluator draws a fixed, action-independent random tape for
    each episode seed and exposes its digest to the *evaluator*, not the policy.
    """
    digest = getattr(env, "paired_noise_digest", None)
    if (type(digest) is not str or len(digest) != 64 or
            any(c not in "0123456789abcdef" for c in digest)):
        raise ValueError("CCE06_PAIRED_NOISE_RECEIPT_REQUIRED")
    return digest


def _episode(policy, env, *, steps, budget, terminal, paired_noise_required=False):
    obs = env.reset()
    code(obs)
    noise_receipt = _paired_noise_receipt(env) if paired_noise_required else None
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
    if paired_noise_required and _paired_noise_receipt(env) != noise_receipt:
        raise ValueError("CCE06_NOISE_RECEIPT_CHANGED")
    return dict(paid_actions=policy.spent, actions=tuple(actions),
                terminal_brier=_terminal_brier(policy, terminal),
                paired_noise_digest=noise_receipt)


def run_dev_frontier(train, terminal, env_factory, *, specs, budgets,
                     seeds=(997, 998, 999), steps=40,
                     paired_noise_required=False):
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
            type(paired_noise_required) is not bool or \
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
    seen_noise = {}
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
                row = _episode(policy, env, steps=steps, budget=budget,
                               terminal=terminal,
                               paired_noise_required=paired_noise_required)
                if paired_noise_required:
                    digest = row['paired_noise_digest']
                    if seed in seen_noise and seen_noise[seed] != digest:
                        raise ValueError("CCE06_UNPAIRED_EXOGENOUS_NOISE")
                    if seed not in seen_noise:
                        if digest in seen_noise.values():
                            raise ValueError("CCE06_NONINDEPENDENT_NOISE_SEEDS")
                        seen_noise[seed] = digest
                rows.append(row)
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
                paired_noise_receipts_matched=(paired_noise_required and
                                               len(seen_noise) == len(seeds)),
                paired_noise_custody_verified=False,
                custody_verified=False, gain_verified=False)


def matched_target_report(frontier, *, target_brier, reference_policy,
                          require_each_seed=True):
    """DESCRIPTIVE DEV-only minimum probes at a caller-frozen accuracy target.

    Never optimize the threshold from the returned frontier. No lower-bound
    confidence interval, resource matching or independent-custodian claim.
    If reference cost is zero, percent saving is undefined, not a 100% gain.
    """
    if (type(frontier) is not dict or
            frontier.get('status') != 'DEV_FIXTURE_ONLY_SCIENCE_UNVERIFIED' or
            type(target_brier) not in (int, float) or
            not math.isfinite(target_brier) or not 0 <= target_brier <= 1 or
            type(reference_policy) is not str or not reference_policy or
            type(require_each_seed) is not bool):
        raise ValueError('CCE06_UNFROZEN_OR_INVALID_TARGET')
    rows = frontier.get('results')
    if type(rows) not in (tuple, list) or not rows:
        raise ValueError('CCE06_EMPTY_POLICY_FRONTIER')
    if not any(r['policy'] == reference_policy for r in rows):
        raise ValueError('CCE06_MISSING_REFERENCE_POLICY')
    feasible = {}
    for r in rows:
        per_seed = r['per_seed']
        if (not per_seed or not math.isfinite(r['mean_terminal_brier']) or
                not math.isfinite(r['mean_paid_actions'])):
            raise ValueError('CCE06_INVALID_FRONTIER_RECEIPT')
        eligible = all(x['terminal_brier'] <= target_brier for x in per_seed) \
            if require_each_seed else r['mean_terminal_brier'] <= target_brier
        if eligible:
            old = feasible.get(r['policy'])
            if old is None or (r['mean_paid_actions'], r['mean_terminal_brier'], r['budget']) < \
                    (old['mean_paid_actions'], old['mean_terminal_brier'], old['budget']):
                feasible[r['policy']] = r
    reference = feasible.get(reference_policy)
    if reference is None:
        status = 'REFERENCE_TARGET_INFEASIBLE'
    elif reference['mean_paid_actions'] == 0:
        status = 'ZERO_COST_REFERENCE_NO_SAVING_CLAIM'
    else:
        status = 'DESCRIPTIVE_MATCHED_TARGET_ONLY'
    savings = {}
    for name, row in sorted(feasible.items()):
        savings[name] = (None if reference is None or reference['mean_paid_actions'] == 0
                         else (reference['mean_paid_actions'] - row['mean_paid_actions']) /
                         reference['mean_paid_actions'])
    return dict(status=status, target_brier=float(target_brier),
                reference_policy=reference_policy,
                require_each_seed=require_each_seed,
                feasible_costs={k: v['mean_paid_actions'] for k,v in sorted(feasible.items())},
                fractional_probe_savings=savings, scientific_gain_verified=False,
                target_preregistered_and_custody_verified=False)
