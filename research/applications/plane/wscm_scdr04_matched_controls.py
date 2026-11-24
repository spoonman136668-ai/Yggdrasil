"""Frozen synthetic matched-control screen of the original SCDR04 observer.
No original simulator, protected source seed, action authority or model promotion.
"""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys

from wscm_scdr04_witness_bound import (
    ROOT, SIDE, ACTIONS, NativeGrid5Evidence, SCDRGrid5Observer, receipt,
    witness_bound_readout, move, check, verify_pins,
)
from scdr_grid5_observer import GRID5_DELTAS

EXPERIMENT = "WSCM-SCDR04-MATCHED-CONTROLS-01"
SEEDS = (741103, 741107, 741109)
FAMILIES = ("permutation", "alias", "checkerboard_novel")
ARMS = ("scdr", "row", "joint", "grammar")
STEPS = (5, 10, 20)
NOVEL = 5
MAPS = tuple(m for m in itertools.product(range(6), repeat=5)
             if len([x for x in m if x != NOVEL]) ==
             len(set(x for x in m if x != NOVEL)))
LAWS = tuple((i, i) for i in range(5)) + tuple(
    (i, j) for i in range(5) for j in range(5) if i != j)


def rng_for(seed, family, index):
    key = f"{EXPERIMENT}/{seed}/{family}/{index}".encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest(), "big"))


def world(seed, family, index):
    rng = rng_for(seed, family, index)
    perm = list(range(5))
    rng.shuffle(perm)
    laws = [(role, role) for role in perm]
    if family == "alias":
        a, b = rng.sample(range(5), 2)
        laws[a] = laws[b]
    if family == "checkerboard_novel":
        a = rng.randrange(5)
        old = laws[a][0]
        other = rng.choice([i for i in range(5) if i != old])
        laws[a] = (old, other)
    actions = []
    for _ in range(4):
        block = list(range(5))
        rng.shuffle(block)
        actions.extend(block)
    return laws, actions


def joint_posterior(rows):
    # Exact marginalization of the same row factors with the partial
    # one-to-one familiar-role prior; novel has no exclusivity constraint.
    out = [[0.0] * 6 for _ in range(5)]
    weights = [math.prod(rows[a][role] for a, role in enumerate(m)) for m in MAPS]
    norm = math.fsum(weights)
    check(norm > 0, "JOINT_EMPTY")
    for m, w in zip(MAPS, weights):
        for a, role in enumerate(m):
            out[a][role] += w / norm
    return out


def grammar_posterior(rows):
    # Deterministic, evaluator-disclosed grammar upper-bound comparator.
    # Same observed receipts; no actual hidden world law is supplied.
    result = []
    for a in range(5):
        obs = [r for r in rows if r[4] == a]
        masses = [0.0] * 6
        for law in LAWS:
            fixed = law[0] == law[1]
            if all(move(tuple(r[3]), GRID5_DELTAS[law[(r[3][0] + r[3][1]) % 2]])
                   == tuple(r[5]) for r in obs):
                masses[law[0] if fixed else NOVEL] += .18 if fixed else .005
        norm = math.fsum(masses)
        check(norm > 0, "GRAMMAR_EMPTY")
        result.append([v / norm for v in masses])
    return result


def readouts(evidence, episode_id):
    raw = evidence.checkpoint()
    records = json.loads(raw)["records"]
    validated = NativeGrid5Evidence.restore(raw, hashlib.sha256(raw).hexdigest())
    check(validated.checkpoint() == raw, "RECEIPT_RESTORE_DRIFT")
    rows = [r for r in records if r[1] == episode_id]
    check(len(rows) == len(records), "SCOPE_DRIFT")
    obs = SCDRGrid5Observer(grid_size=SIDE)
    for row in rows:
        obs.observe_transition(tuple(row[3]), row[4], tuple(row[5]))
    base = [list(row) for row in obs.beliefs]
    eff = obs.effective_beliefs()
    for a in range(5):
        guard = witness_bound_readout(validated, [4, 4], a, episode_id=episode_id)
        check(guard["scdr_per_action_distribution"] == [round(x, 6) for x in eff[a]],
              "WITNESS_BOUND_READOUT_MISMATCH")
        check(guard["action_admissible"] is False and guard["family_authenticated"] is False,
              "ACTION_AUTHORITY_DRIFT")
        check(eff[a][NOVEL] == base[a][NOVEL], "NOVEL_MASS_DRIFT")
    result = {"scdr": eff, "row": base, "joint": joint_posterior(base),
              "grammar": grammar_posterior(rows)}
    for matrix in result.values():
        for row in matrix:
            check(abs(math.fsum(row) - 1) < 1e-10 and all(0 <= x <= 1 + 1e-12 for x in row),
                  "INVALID_PROBABILITY")
    check(evidence.checkpoint() == raw, "NATIVE_MUTATION")
    return result


def score(matrix, truth):
    brier = math.fsum(math.fsum((p - (k == t)) ** 2 for k, p in enumerate(row))
                      for row, t in zip(matrix, truth)) / 5
    novel = math.fsum((row[NOVEL] - (t == NOVEL)) ** 2
                      for row, t in zip(matrix, truth)) / 5
    accuracy = sum(max(range(6), key=lambda k: row[k]) == t
                   for row, t in zip(matrix, truth)) / 5
    return (brier, novel, accuracy)


def summarize(values):
    return {arm: {name: round(math.fsum(v[i] for v in values[arm]) / len(values[arm]), 9)
                  for i, name in enumerate(("brier", "novel_brier", "map_accuracy"))}
            for arm in ARMS}


def run():
    verify_pins()
    pin = subprocess.check_output(
        ["git", "hash-object", "--no-filters",
         "research/applications/plane/wscm_scdr04_witness_bound.py"],
        cwd=ROOT, text=True).strip()
    check(pin == "492de744158f1d56b7176ae1d411614fb5b6bad8", "WRAPPER_DRIFT")
    check(SIDE == 9 and ACTIONS == 5, "NATIVE_DIMENSION_DRIFT")
    groups = defaultdict(lambda: defaultdict(list))
    world_rows = []
    max_col = 0.0
    cap_exceed_count = 0
    charged = 0
    cold_checks = 0
    for seed in SEEDS:
        for family in FAMILIES:
            for index in range(8):
                laws, actions = world(seed, family, index)
                truth = [law[0] if law[0] == law[1] else NOVEL for law in laws]
                episode = hashlib.sha256(f"{EXPERIMENT}/{seed}/{family}/{index}/episode".encode()).hexdigest()
                evidence = NativeGrid5Evidence()
                state = (0, 0)
                local = defaultdict(list)
                for step, action in enumerate(actions):
                    after = move(state, GRID5_DELTAS[laws[action][sum(state) % 2]])
                    sid = hashlib.sha256(f"{episode}/{step}".encode()).hexdigest()
                    evidence = evidence.observe_public_receipt(*receipt(
                        step, act=action, before=state, after=after, episode=episode, sid=sid))
                    state = after
                    charged += 1
                    if step + 1 not in STEPS:
                        continue
                    matrices = readouts(evidence, episode)
                    if index == 0 and step + 1 == 20:
                        raw = evidence.checkpoint()
                        cold = NativeGrid5Evidence.restore(raw, hashlib.sha256(raw).hexdigest())
                        check(readouts(cold, episode) == matrices, "COLD_SCORE_DRIFT")
                        cold_checks += 1
                    col = max(math.fsum(r[k] for r in matrices["scdr"]) for k in range(5))
                    max_col = max(max_col, col)
                    cap_exceed_count += col > 1 + 1e-9
                    for arm in ARMS:
                        value = score(matrices[arm], truth)
                        local[arm].append(value)
                        for group in ("all", f"seed/{seed}", f"family/{family}", f"step/{step+1}"):
                            groups[group][arm].append(value)
                world_rows.append({"seed": seed, "family": family, "world": index,
                                   "receipt_checkpoint_sha256": hashlib.sha256(evidence.checkpoint()).hexdigest(),
                                   "scores": summarize(local)})
    check(charged == 1440 and len(world_rows) == 72 and cold_checks == 9, "BUDGET_DRIFT")
    results = {group: summarize(values) for group, values in sorted(groups.items())}
    # Evaluate prespecified thresholds without rounded metrics.
    def mean(group, arm, metric):
        vals = groups[group][arm]
        return math.fsum(v[metric] for v in vals) / len(vals)
    seed_gain = {str(seed): min(mean(f"seed/{seed}", c, 0) for c in ("row", "joint"))
                 - mean(f"seed/{seed}", "scdr", 0) for seed in SEEDS}
    family_harm = {f: mean(f"family/{f}", "scdr", 0)
                   - min(mean(f"family/{f}", c, 0) for c in ("row", "joint")) for f in FAMILIES}
    novelty_difference = mean("all", "scdr", 1) - mean("all", "row", 1)
    gates = {"all_seed_gains_ge_0_02": all(x >= .02 for x in seed_gain.values()),
             "all_family_harms_le_0_01": all(x <= .01 for x in family_harm.values()),
             "novelty_no_worse_than_row": novelty_difference <= 1e-15}
    return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT,
            "status": "MATCHED_CONTROLS_DEV_COMPLETE", "scientific_pass": False,
            "scientific_gain_verified": False, "source_first_use": False,
            "metrics": {"disposition": "DEV_SIGNAL" if all(gates.values()) else "DEV_NO_GO",
                        "gates": gates, "seed_gain_vs_best_row_joint": seed_gain,
                        "family_harm_vs_best_row_joint": family_harm,
                        "novelty_brier_difference": novelty_difference,
                        "groups": results, "worlds": world_rows, "world_count": 72,
                        "synthetic_charged_actions": charged, "original_source_actions": 0,
                        "readout_rounds": len(world_rows) * len(STEPS),
                        "scored_action_roles": len(world_rows) * len(STEPS) * 5,
                        "cold_parity_checks": cold_checks, "exact_joint_assignments": len(MAPS),
                        "exact_grammar_laws_per_action": len(LAWS),
                        "sinkhorn_iterations": 3, "max_familiar_column_sum": max_col,
                        "rounds_exceeding_column_cap": cap_exceed_count,
                        "all_novel_masses_equal_to_independent_row": True,
                        "action_authorized": False, "full_final_regression": "NOT_RUN",
                        "compute_timing": "NOT_MEASURED", "closed_loop_selection": False}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode())
