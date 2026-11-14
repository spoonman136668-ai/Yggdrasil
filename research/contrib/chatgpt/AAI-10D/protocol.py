"""AAI-10D: immutable pre-first-use intervention comparison protocol.

ONLY explicitly prefixed mechanical fixtures run here. Science world IDs and
--primary are deliberately unsupported. No model receives a law ID, formula,
world name, unchosen action consequence or oracle recommendation.

The complete statistical protocol is frozen in prereg.json, and its real
science-cohort executor must be a separate, explicitly authorized artifact.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "AAI-10P"))
sys.path.insert(0, str(ROOT / "AAI-10A"))
sys.path.insert(0, str(ROOT / "AAI-10C"))
import benchmark as world
import models as conventional
import compact

FIXTURES = ("handcrafted:one", "handcrafted:two")
MATCHED = tuple(conventional.MATCHED)
CANDIDATE = "aai10c"
ABLATION = "one_slot"
DIAGNOSTIC = "reactive"
LEARNERS = (CANDIDATE, ABLATION, *MATCHED, DIAGNOSTIC)
TRAIN_TRIALS = 16
TRAIN_ROWS = 64
CHALLENGE_TRIALS = (0, 2, 4, 8)
PRIMARY_BUDGETS = (2, 4)
SCIENCE_COHORTS = {"DEV": (991000, 991016),
                   "TRANSFER": (992000, 992064),
                   "NEGATIVE": (993000, 993032)}
PUBLIC_KEYS = frozenset(("x", "mediators", "goal", "reward", "actions_taken"))


def ensure_fixture(key):
    if type(key) is not str or key not in FIXTURES:
        raise PermissionError("AAI10D SCIENCE WORLD FIRST USE DISARMED")
    return key


def deterministic_index(fixture, phase, index, field, modulus):
    """Only fixture labels, no random or science cohort world IDs accepted."""
    ensure_fixture(fixture)
    if type(index) is not int or not 0 <= index <= 1024:
        raise ValueError("bad bounded public trial index")
    if type(modulus) is not int or modulus < 1:
        raise ValueError("bad modulus")
    data = f"AAI-10D|{fixture}|{phase}|{index}|{field}".encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big") % modulus


def design_trial(fixture, scope, number):
    ensure_fixture(fixture)
    x = world.INPUTS[deterministic_index(fixture, scope, number, "x", 8)]
    goal = world.GOALS[deterministic_index(fixture, scope, number, "goal", 4)]
    action = world.ACTIONS[deterministic_index(fixture, scope, number, "do", 6)]
    return x, goal, action


def public_copy(row):
    """Fail closed before any learner sees the state."""
    if type(row) is not dict or set(row) != PUBLIC_KEYS:
        raise ValueError("non-public or missing observation field")
    conventional.visible(row)
    return {
        "x": list(row["x"]),
        "mediators": list(row["mediators"]),
        "goal": list(row["goal"]),
        "reward": row["reward"],
        "actions_taken": row["actions_taken"],
    }


def make_actor(name):
    if name == CANDIDATE:
        return compact.BoundedCausalSignatureBank(3)
    if name == ABLATION:
        return compact.BoundedCausalSignatureBank(1)
    if name in (*MATCHED, DIAGNOSTIC):
        return conventional.create(name)
    raise ValueError("unregistered learner")


def freeze_actor(name, actor):
    if name in (CANDIDATE, ABLATION):
        return compact.checkpoint(actor)
    return conventional.canonical(actor.state())


def restore_actor(name, payload):
    if name in (CANDIDATE, ABLATION):
        actor = compact.cold_restore(payload)
        if actor.max_slots != (3 if name == CANDIDATE else 1):
            raise ValueError("wrong candidate capacity")
    else:
        actor = conventional.cold_restore({name: payload})[name]
    if freeze_actor(name, actor) != payload:
        raise ValueError("non-identical cold restore")
    return actor


def public_pair(law, fixture, scope, index):
    # Simulator law argument stays local to this function. No learner consumes it.
    x, goal, action = design_trial(fixture, scope, index)
    before = world.public_initial(law, x, goal)
    after = world.public_step(law, before, action)
    return (public_copy(before), public_copy(after))


def _apply_pair(actor, pair):
    for observation in pair:
        actor.learn(public_copy(observation))


def common_training(fixture, labels=LEARNERS):
    ensure_fixture(fixture)
    models = {name: make_actor(name) for name in labels}
    phases = (("A", "training-alpha"), ("B", "training-beta"))
    common = []
    for law, scope in phases:
        for index in range(TRAIN_TRIALS):
            pair = public_pair(law, fixture, scope, index)
            common.extend(pair)
            for actor in models.values():
                _apply_pair(actor, pair)
    if len(common) != TRAIN_ROWS:
        raise AssertionError("public training budget violated")
    saved = {name: freeze_actor(name, actor) for name, actor in models.items()}
    # A and B laws are never stored in a learner checkpoint.
    for actor in models.values():
        if getattr(actor, "scratch", []):
            raise AssertionError("partial training update")
    return saved, tuple(common)


def challenge_pairs(law, fixture, n_trials, corrupt=False):
    ensure_fixture(fixture)
    if n_trials not in CHALLENGE_TRIALS or type(n_trials) is not int:
        raise ValueError("unfrozen challenge budget")
    pairs = [public_pair(law, fixture, "challenge-" + law, k)
             for k in range(n_trials)]
    if corrupt:
        if n_trials < 2:
            raise ValueError("feedback shuffle needs multiple trials")
        # Corrupt public mediator x->m associations WITHOUT adding information:
        # circular exchange only the post-action mediator vectors among trials;
        # keep the same multiset of mediator outputs and the same public action x.
        # Recompute public reward to remain internally consistent with the
        # observed corrupted mediator and goal, not true hidden simulator law.
        rotated = [list(q[1]["mediators"]) for q in pairs]
        pairs = [
            (pre, {
                **post,
                "mediators": list(rotated[(i + 1) % n_trials]),
                "reward": world.reward(rotated[(i + 1) % n_trials],
                                       post["goal"], post["actions_taken"]),
            }) for i, (pre, post) in enumerate(pairs)
        ]
        if sorted(tuple(m) for m in rotated) != sorted(
            tuple(p[1]["mediators"]) for p in pairs
        ):
            raise AssertionError("negative control changed mediator marginals")
    return tuple(pairs)


def heldout_contexts(fixture, law, count=16):
    """Evaluation namespace: distinct x/goal pairs within each evaluation fork.

    Namespace and unique contexts do NOT imply zero overlap in small (32-context)
    universe with training: unfamiliarity refers to causal law, not unseen bits.
    """
    ensure_fixture(fixture)
    if type(count) is not int or not 1 <= count <= 16:
        raise ValueError("unfrozen context count")
    combos = [(x, g) for x in world.INPUTS for g in world.GOALS]
    def rank(item):
        x, g = item
        data = "AAI10D|eval-context|"+fixture+"|"+law+"|"+repr(x)+"|"+repr(g)
        return hashlib.sha256(data.encode("ascii")).digest()
    chosen = tuple(sorted(combos, key=rank)[:count])
    if len(set(chosen)) != count:
        raise AssertionError("repeated evaluation context")
    return chosen


def challenge_checkpoint(name, original, law, fixture, n_trials, corrupt=False):
    """Independent challenge continuation; no hidden law or future label to actor."""
    ensure_fixture(fixture)
    actor = restore_actor(name, original)
    for pair in challenge_pairs(law, fixture, n_trials, corrupt):
        _apply_pair(actor, pair)
    final = freeze_actor(name, actor)
    return final


def episode(name, challenge_snapshot, law, x, goal):
    """Independent episode: exactly own observed initial/action feedback.

    A law is supplied solely to the simulator. Learners receive public_copy
    only. No reward of an unchosen intervention or another method's action.
    """
    actor = restore_actor(name, challenge_snapshot)
    current = public_copy(world.public_initial(law, x, goal))
    actor.learn(public_copy(current))
    actions = []
    for _ in range(2):
        action = actor.choose(public_copy(current))
        if action is None:
            break
        if action not in world.ACTIONS:
            raise ValueError("illegal intervention")
        current = public_copy(world.public_step(law, current, action))
        actions.append(action)
        actor.learn(public_copy(current))
    if current["actions_taken"] != len(actions):
        raise AssertionError("episode action count mismatched")
    if len(actions) > 2:
        raise AssertionError("action horizon exceeded")
    return {"terminal_reward": current["reward"],
            "goal_correct": tuple(current["mediators"]) == tuple(goal),
            "actions": len(actions),
            "actual_action_indices": [world.ACTIONS.index(a) for a in actions]}


def oracle_diagnostic(law, x, goal):
    """Privileged simulator-only exact two-action oracle, never a learner."""
    initial = world.public_initial(law, x, goal)
    best = initial["reward"]
    for a in world.ACTIONS:
        after = world.public_step(law, initial, a)
        best = max(best, after["reward"])
        for b in world.ACTIONS:
            terminal = world.public_step(law, after, b)
            best = max(best, terminal["reward"])
    return best


def evaluate_branch(name, saved, law, fixture, n_trials, n_contexts=16,
                    corrupt=False):
    """Publicly common challenge; independently restored held-out episodes."""
    after = challenge_checkpoint(name, saved, law, fixture, n_trials, corrupt)
    contexts = heldout_contexts(fixture, law, n_contexts)
    results = [episode(name, after, law, x, g) for x, g in contexts]
    if freeze_actor(name, restore_actor(name, saved)) != saved:
        raise AssertionError("original B checkpoint changed")
    oracle = [oracle_diagnostic(law, x, g) for x, g in contexts]
    return {
        "n_contexts": len(contexts),
        "mean_reward": sum(r["terminal_reward"] for r in results) / len(results),
        "goal_correct": sum(r["goal_correct"] for r in results) / len(results),
        "mean_interventions": sum(r["actions"] for r in results) / len(results),
        "oracle_mean_reward": sum(oracle)/len(oracle),
        "challenge_snapshot_sha256": hashlib.sha256(after.encode()).hexdigest(),
        "actions_sha256": hashlib.sha256(conventional.canonical([
            r["actual_action_indices"] for r in results
        ]).encode()).hexdigest(),
    }


def paired_bootstrap(differences, n_draws=2048, seed=39092):
    """World-cluster bootstrap, no per-context resampling."""
    import random
    if type(differences) is not list or not differences:
        raise ValueError("at least one paired world is required")
    if not all(type(x) in (int, float) and math.isfinite(x)
               for x in differences):
        raise ValueError("nonfinite pair")
    if n_draws != 2048 or seed != 39092:
        raise ValueError("frozen bootstrap params")
    n = len(differences)
    gen = random.Random(seed)
    estimates = []
    for _ in range(n_draws):
        estimates.append(sum(differences[gen.randrange(n)] for __ in range(n))/n)
    estimates.sort()
    return {"mean": sum(differences)/n,
            "lower95": estimates[int(0.025 * (n_draws - 1))],
            "upper95": estimates[int(0.975 * (n_draws - 1))],
            "cluster_count": n}


def classify_primary(worlds):
    """Pure scoring on externally verified, *whole-world* primary rows.

    Not callable from this repo's CLI for real scientific cohorts. Records
    never contain private law labels or learning internals, only public
    achieved outcomes per world/condition and matched method.
    """
    if type(worlds) is not list or len(worlds) != 64:
        raise ValueError("expected exactly 64 independent TRANSFER worlds")
    ids = [r.get("world_id") for r in worlds]
    if len(set(ids)) != 64 or any(type(i) is not int or
                                i not in range(992000, 992064) for i in ids):
        raise ValueError("expected exact frozen unseen world IDs")
    if set(ids) != set(range(992000, 992064)):
        raise ValueError("missing/extra cohort")
    if any(set(r) != {"world_id", "outcomes"} for r in worlds):
        raise ValueError("wrong summary shape")
    required = {CANDIDATE, ABLATION, *MATCHED, "oracle"}
    for r in worlds:
        outcomes = r["outcomes"]
        if type(outcomes) is not dict or set(outcomes) != required:
            raise ValueError("missing eligible control")
        if any(type(x) not in (int, float) or not math.isfinite(x) or
               x < -0.1 or x > 2.0 for x in outcomes.values()):
            raise ValueError("invalid public reward")
    baseline = max(MATCHED, key=lambda k:
                   sum(r["outcomes"][k] for r in worlds)/len(worlds))
    candidate = [r["outcomes"][CANDIDATE] for r in worlds]
    strong = [r["outcomes"][baseline] for r in worlds]
    oracle = [r["outcomes"]["oracle"] for r in worlds]
    ablation = [r["outcomes"][ABLATION] for r in worlds]
    gain = paired_bootstrap([c-s for c, s in zip(candidate, strong)])
    headroom = paired_bootstrap([o-s for o, s in zip(oracle, strong)])
    memory = paired_bootstrap([c-a for c, a in zip(candidate, ablation)])
    # No scientific success claim: retention, negative control, process-cost
    # and independently qualified inputs are also required later.
    return {
        "strongest_matched": baseline,
        "candidate_vs_strongest": gain,
        "oracle_headroom": headroom,
        "candidate_vs_ablation": memory,
        "preliminary_gain_gate": gain["mean"] >= .08 and gain["lower95"] > 0,
        "headroom_gate": headroom["mean"] >= .15 and headroom["lower95"] > 0
                and sum(strong)/len(strong) < 1.9,
        "ablation_gate": memory["mean"] >= .05 and memory["lower95"] > 0,
        "status": "SUMMARY_ONLY_NOT_QUALIFIED_SCIENTIFIC_RESULT",
    }
