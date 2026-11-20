#!/usr/bin/env python3
"""ENERGY-33: bounded Bayesian single-change-point hypothesis construction.

External synthetic research only. Rules are generated from a fixed grammar;
not open-ended concept invention, not native Yggdrasil training.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
ERROR = 0.15
HAZARD = 1.0 / 48.0
SEEDS = [6067, 6073, 6089, 6101]
SCENARIOS = ('stationary', 'novel_change', 'familiar_switch')
ARMS = ('cp_energy', 'cp_bayes', 'fixed_hazard', 'recent16', 'full_history')
ACTION_BITS = np.array([[(i >> j) & 1 for j in range(6)] for i in range(64)], dtype=np.int8)
RULES = [(triple, None, sign) for triple in combinations(range(6), 3) for sign in (0, 1)]
# Explicit, witness-testable grammar: signed XOR3 plus AND2 on unused coordinates.
RULES += [(triple, pair, sign) for triple in combinations(range(6), 3)
          for pair in combinations([x for x in range(6) if x not in triple], 2)
          for sign in (0, 1)]
assert len(RULES) == 160
TRUTH = np.array([[int(sum(a[list(triple)]) % 2) ^
                   (int(a[pair[0]] & a[pair[1]]) if pair else 0) ^ sign
                   for a in ACTION_BITS] for triple, pair, sign in RULES], dtype=np.int8)
PRIOR = np.array([7 / (8 * 40)] * 40 + [1 / (8 * 120)] * 120)
OLD_PRIOR = np.ones(40) / 40

def digest(*parts):
    return sha256('/'.join(map(str, ('energy33-v1', *parts))).encode('ascii')).digest()

def pick(*parts, n):
    return int.from_bytes(digest(*parts)[:8], 'big') % n

def make_case(seed, old, scenario):
    shuffled = sorted(range(64), key=lambda a: digest('split', seed, old, scenario, a))
    before, after, held = shuffled[:24], shuffled[24:40], shuffled[40:52]
    target = (old if scenario == 'stationary' else
              40 + pick('new', seed, old, n=120) if scenario == 'novel_change' else
              (old + 2 + 2 * pick('switch', seed, old, n=19)) % 40)
    assert scenario == 'stationary' or target != old
    rows = []
    for phase, actions, rule in [('prior', before, old), ('post', after, target)]:
        for i, action in enumerate(actions):
            noise = int.from_bytes(digest('noise', seed, old, scenario, phase, i, action)[:8], 'big') / 2**64 < ERROR
            rows.append([action, int(TRUTH[rule, action]) ^ int(noise)])
    return rows, held, target

def logsumexp(x):
    m = float(np.max(x))
    return m + np.log(np.exp(x - m).sum())

def posterior(evidence, prior, count):
    logw = np.log(prior) + evidence[:count]
    w = np.exp(logw - logsumexp(logw))
    return w, float(logsumexp(logw))

def energy_cp(rows):
    """Energy E(r)= -log prior(r) -sum witnessed log P(y|r,x).
    Enumerate all possible single change points; no phase marker supplied.
    Candidate composites are generated from the XOR3+AND2 grammar at inference.
    """
    n = len(rows)
    a = np.array([r[0] for r in rows], dtype=int)
    y = np.array([r[1] for r in rows], dtype=int)
    likelihood = np.where(TRUTH[:, a] == y[None, :], 1 - ERROR, ERROR)
    accum = np.c_[np.zeros(160), np.cumsum(np.log(likelihood), axis=1)]
    scores = []
    predictive = []
    no_post, logz = posterior(accum[:, n], OLD_PRIOR, 40)
    scores.append(n * np.log1p(-HAZARD) + logz)
    predictive.append(no_post @ TRUTH[:40, :])
    for k in range(8, n):
        _, old_logz = posterior(accum[:, k], OLD_PRIOR, 40)
        # Composites are generated from the grammar and scored using only k..n witnesses.
        post, new_logz = posterior(accum[:, n] - accum[:, k], PRIOR, 160)
        scores.append(k * np.log1p(-HAZARD) + np.log(HAZARD) + old_logz + new_logz)
        predictive.append(post @ TRUTH)
    masses = np.exp(np.array(scores) - logsumexp(np.array(scores)))
    return masses @ np.array(predictive), float(masses[1:].sum())

def bayes_cp_reference(rows):
    """Independent factor-product Bayesian reference to crosscheck log-energy math."""
    n = len(rows)
    lhood = np.array([[1-ERROR if TRUTH[r, a] == y else ERROR for a, y in rows]
                       for r in range(160)])
    def part(begin, stop, prior):
        logs = np.log(prior)
        for t in range(begin, stop):
            logs += np.log(lhood[:len(prior), t])
        z = logsumexp(logs)
        return float(z), np.exp(logs - z)
    z, p = part(0, n, OLD_PRIOR)
    scores = [n * np.log1p(-HAZARD) + z]
    preds = [p @ TRUTH[:40]]
    for k in range(8, n):
        zold, _ = part(0, k, OLD_PRIOR)
        znew, pnew = part(k, n, PRIOR)
        scores.append(k * np.log1p(-HAZARD) + np.log(HAZARD) + zold + znew)
        preds.append(pnew @ TRUTH)
    weights = np.exp(np.array(scores)-logsumexp(np.array(scores)))
    return weights @ np.array(preds), float(weights[1:].sum())

def conventional(rows, mode):
    if mode == 'recent16': rows = rows[-16:]
    w = PRIOR.copy()
    for a, y in rows:
        if mode == 'fixed_hazard': w = (1 - HAZARD) * w + HAZARD * PRIOR
        w *= np.where(TRUTH[:, a] == y, 1 - ERROR, ERROR)
        w /= w.sum()
    return w @ TRUTH

def score_case(seed, old, scenario):
    rows, held, target = make_case(seed, old, scenario)
    start = time.perf_counter()
    energy, alarm = energy_cp(rows)
    t_energy = time.perf_counter() - start
    start = time.perf_counter()
    bayes, balarm = bayes_cp_reference(rows)
    t_bayes = time.perf_counter() - start
    parity = float(max(np.max(abs(energy - bayes)), abs(alarm-balarm)))
    if parity > 1e-10: raise AssertionError(f'Bayesian/energy parity broken: {parity}')
    predictions = {'cp_energy': energy, 'cp_bayes': bayes}
    for arm in ARMS[2:]: predictions[arm] = conventional(rows, arm)
    correct = {a: sum(int(predictions[a][k] > 0.5 + 1e-12) == int(TRUTH[target, k])
                      for k in held) for a in ARMS}
    return {'seed': seed, 'old': old, 'scenario': scenario, 'target_family': 'novel' if target >= 40 else 'familiar',
            'correct': correct, 'alarm': alarm, 'parity_error': parity,
            'seconds': {'cp_energy': t_energy, 'cp_bayes': t_bayes}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    seeds = [99013] if args.smoke else SEEDS
    olds = [0, 2] if args.smoke else list(range(0, 40, 2))
    started = time.perf_counter()
    cases = [score_case(s, old, scen) for s in seeds for old in olds for scen in SCENARIOS]
    totals = {scenario: {arm: sum(c['correct'][arm] for c in cases if c['scenario'] == scenario)
                         for arm in ARMS} for scenario in SCENARIOS}
    denominators = {s: sum(c['scenario'] == s for c in cases) * 12 for s in SCENARIOS}
    nstationary = sum(c['scenario']=='stationary' for c in cases)
    false_alarm = sum(c['alarm'] > 0.5 for c in cases if c['scenario'] == 'stationary')
    gates = {
        'novel_gain_over_strongest': (totals['novel_change']['cp_energy']-
            max(totals['novel_change'][arm] for arm in ARMS[2:])) / denominators['novel_change'] >= 0.03,
        'familiar_gain_over_strongest': (totals['familiar_switch']['cp_energy']-
            max(totals['familiar_switch'][arm] for arm in ARMS[2:])) / denominators['familiar_switch'] >= 0.03,
        'stationary_retention': totals['stationary']['cp_energy'] / denominators['stationary'] >= 0.95 and
            totals['stationary']['cp_energy'] >= totals['stationary']['full_history'] - 0.01*denominators['stationary'],
        'false_alarm_at_most_10pct': false_alarm / nstationary <= 0.10,
        'exact_energy_bayes_parity': max(c['parity_error'] for c in cases) <= 1e-10,
        'energy_distinctive': False  # mathematical equivalence is not new learning advantage
    }
    summary = {'schema':'yggdrasil.energy33.score.v1','mode':'smoke' if args.smoke else 'primary',
               'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
               'seeds':seeds,'cases': len(cases),'observations_per_world': 40,'held_per_world': 12,
               'scenario_totals':totals,'scenario_denominators':denominators,
               'false_alarms':false_alarm,'false_alarm_worlds':nstationary,'gates':gates,
               'max_parity_error': max(c['parity_error'] for c in cases),
               'timings_seconds': {arm:sum(c['seconds'][arm] for c in cases) for arm in ('cp_energy','cp_bayes')},
               'wall_seconds': time.perf_counter()-started,'details':cases,
               'native_checkpoint_run':False,'scientific_pass':False,'deployment':'NONE',
               'classification': 'DEVELOPMENT_NO_GO' if not all(gates.values()) else 'DEVELOPMENT_GO'}
    Path(args.out).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='details'},indent=2,sort_keys=True))
if __name__ == '__main__': main()
