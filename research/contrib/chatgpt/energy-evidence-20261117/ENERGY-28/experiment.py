#!/usr/bin/env python3
"""ENERGY-28: witnessed causal interaction hypothesis birth, isolated synthetic test.

Input: six binary interventions; revealed actions/outcomes from source-only laws.
Initial bank: signed XOR of three action bits (40 rules). After visible
contradictions, generate a new AND-of-two-remaining-inputs interaction, yielding
120 new rules outside the original bank. No rule/class labels are passed to fit.

Do not interpret a finite-grammar expansion as open-ended invention, native
Yggdrasil execution, or accepted scientific qualification.
"""
import argparse
import hashlib
import itertools
import json
import os
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
N_ACTIONS = 64
N_INPUTS = 6
SEEDS = (1811, 1823, 1831)
SMOKE_SEED = 8009
POLICIES = ('old_bank', 'birth', 'full_grammar', 'conventional_ridge', 'birth_hard_map')


def bit_count(x):
    return int(x).bit_count()


def families():
    old, novel = [], []
    for triple in itertools.combinations(range(N_INPUTS), 3):
        mask = sum(1 << k for k in triple)
        rest = [k for k in range(N_INPUTS) if k not in triple]
        for sign in (0, 1):
            old.append((mask, 0, sign))
            for pair in itertools.combinations(rest, 2):
                novel.append((mask, sum(1 << k for k in pair), sign))
    assert len(old) == 40 and len(novel) == 120
    assert len(set(old + novel)) == 160
    return tuple(old), tuple(novel)


OLD, NOVEL = families()
ALL = OLD + NOVEL
PRED = np.asarray([[int((bit_count(action & triple) % 2) ^ sign ^
             (bool(inter) and (action & inter) == inter)) for action in range(N_ACTIONS)]
             for triple, inter, sign in ALL], dtype=np.uint8)
assert PRED.shape == (160, 64)


def permutation(seed, rule_index):
    # Private source-only split; rule index does NOT seed learner acquisition.
    # No held outcomes enter the learning function.
    pairs = [(hashlib.sha256(f'energy28/split-v1/{seed}/{rule_index}/{action}'.encode()).digest(), action)
             for action in range(N_ACTIONS)]
    return tuple(action for _, action in sorted(pairs))


def corruption(seed, rule_index):
    records = [(hashlib.sha256(f'energy28/corruption-v1/{seed}/{rule_index}/{i}'.encode()).digest(), i)
               for i in range(16)]
    return tuple(i for _, i in sorted(records))


def numeric_weights(indices, observations, grammar='old'):
    # Exactly integer-compatible 7:1 Bernoulli odds; family prior old:new = 7:1.
    errors = np.count_nonzero(PRED[:, indices] != np.asarray(observations)[None, :], axis=1)
    # Max 21*7^16 ~ 7e14; all integer sums < 2^63.
    powers = np.asarray([7 ** (len(indices)-int(e)) for e in errors], dtype=np.int64)
    if grammar == 'old':
        return powers[:40]
    assert grammar == 'full'
    powers[:40] *= 21  # old per-rule mass : novel per-rule mass = (7/40)/(1/120) = 21
    return powers


def decide(weights, idxs, offset=0):
    w = np.asarray(weights, dtype=np.int64)
    out = PRED[offset:offset+len(w), idxs].astype(np.int64)
    positives = np.dot(w, out)
    return (2 * positives > int(w.sum())).astype(np.uint8)


def ridge_fit(train, labels, held):
    # A fully fitted conventional kernel ridge on all 160 candidate-rule features.
    # Kernel dual: 16x16, regularization 1.0, no hidden rule label or held feedback.
    x = 2.0 * PRED[:, train].T.astype(np.float64) - 1.0
    z = 2.0 * PRED[:, held].T.astype(np.float64) - 1.0
    y = 2.0 * np.asarray(labels).astype(np.float64)-1.0
    a = np.linalg.solve(x @ x.T + np.eye(len(train)), y)
    scores = z @ (x.T @ a)
    return (scores > 0).astype(np.uint8)


def evaluate(seed, rid, errors_allowed, *, with_ridge=True):
    order = permutation(seed, rid)
    train, held = np.asarray(order[:16], dtype=np.int64), np.asarray(order[16:32], dtype=np.int64)
    truth = PRED[rid]
    observed = truth[train].copy()
    flips = corruption(seed, rid)[:errors_allowed]
    for i in flips: observed[i] ^= 1
    # Exact old-only mismatch checks at predefined evidence-prefix checkpoints.
    mismatch8 = int(np.count_nonzero(PRED[:40, train[:8]] != observed[None, :8], axis=1).min())
    mismatch16 = int(np.count_nonzero(PRED[:40, train] != observed[None, :], axis=1).min())
    trigger8 = mismatch8 >= 2
    trigger16 = mismatch16 >= 3
    born = bool(trigger8 or trigger16)
    old_weights = numeric_weights(train, observed, grammar='old')
    old_pred = decide(old_weights, held)
    if born:
        full_weights = numeric_weights(train, observed, grammar='full')
        birth_pred = decide(full_weights, held)
        winner = int(np.argmax(full_weights))
        birth_map = PRED[winner, held]
    else:
        full_weights = None
        birth_pred = old_pred
        winner = int(np.argmax(old_weights))
        birth_map = PRED[winner, held]
    # Exact full-Bayes control is ALWAYS fitted, regardless of birth trigger.
    full_true = numeric_weights(train, observed, grammar='full')
    exact_pred = decide(full_true, held)
    ridge_pred = ridge_fit(train, observed, held) if with_ridge else np.zeros(len(held), dtype=np.uint8)
    targets = truth[held]
    predictions = {'old_bank':old_pred, 'birth':birth_pred, 'full_grammar':exact_pred,
                   'conventional_ridge':ridge_pred, 'birth_hard_map':birth_map}
    return {
        'seed':seed, 'rule_index':rid, 'family':'base' if rid<40 else 'novel',
        'corrupted':errors_allowed, 'train_actions':train.tolist(), 'held_actions':held.tolist(),
        'train_observed':observed.astype(int).tolist(), 'flips':list(flips),
        'held_truth':targets.astype(int).tolist(), 'old_min_mismatch8':mismatch8,
        'old_min_mismatch16':mismatch16, 'born':born,
        'posterior_winner_index':winner, 'generated_new_rule':bool(born and winner>=40),
        'predictions':{k:v.astype(int).tolist() for k,v in predictions.items()},
        'correct':{k:int(np.count_nonzero(v == targets)) for k,v in predictions.items()},
    }


def summarize(rows, per_arm_timings):
    strata={}
    for family in ('base','novel'):
        for err in (0,2):
            z=[x for x in rows if x['family']==family and x['corrupted']==err]
            strata[f'{family}/corrupt{err}']={
                'worlds':len(z),'held_predictions_per_arm':16*len(z),
                'born':sum(x['born'] for x in z),
                'generated_new_rule':sum(x['generated_new_rule'] for x in z),
                'correct':{arm:sum(x['correct'][arm] for x in z) for arm in POLICIES},
            }
    return {'worlds':len(rows),'held_predictions_per_arm':16*len(rows),
            'strata':strata,'measured_full_process_wall_seconds':per_arm_timings}


def run(smoke=False):
    seeds=(SMOKE_SEED,) if smoke else SEEDS
    ridx=(0, 6, 39, 40, 80, 159) if smoke else tuple(range(160))
    data=[]
    t0=time.perf_counter()
    for seed in seeds:
        for rid in ridx:
            for flip_count in (0,2):
                data.append(evaluate(seed, rid, flip_count))
    elapsed=time.perf_counter()-t0
    results={
        'schema':'yggdrasil.energy28.causal-hypothesis-birth.v1',
        'scope':'isolated synthetic source-free development, no native model, no first use',
        'mode':'smoke' if smoke else 'score',
        'source_worlds':len(data),
        'candidate_bank':{'initial':40, 'generated_interaction':120, 'full':160},
        'qualification':'DEVELOPMENT_UNVERIFIED_PENDING_FROZEN_GATE',
        'aggregate':summarize(data,{'total':elapsed}),
        'cases':data,
    }
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--output',type=Path,default=ROOT/'scored.json')
    args=ap.parse_args()
    result=run(args.smoke)
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'mode':result['mode'],'worlds':len(result['cases']),
                      'strata':result['aggregate']['strata'],
                      'wall_seconds':result['aggregate']['measured_full_process_wall_seconds']},indent=2))

if __name__=='__main__':main()
