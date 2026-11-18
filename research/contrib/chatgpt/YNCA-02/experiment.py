"""YNCA-02: independently preregistered source-free all-expert-failure diagnostic.

This is a deterministic synthetic contributor DEVELOPMENT test, NOT native Yggdrasil
training or protected scientific first-use. Scores/labels never enter inference.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RANGES = {'train': (100001, 104097), 'dev': (110001, 111025), 'heldout': (120001, 122049)}
EXPERTS = ('observational', 'interventional', 'proxy_adjusted')
PRIOR_STRENGTH = 50.0
LOGISTIC_STEPS = 250
LOGISTIC_RIDGE = 0.05
LOGISTIC_RATE = 0.3
RETAIN_FRACTION = 0.8
BOOTSTRAP_DRAWS = 1000


def rng(*parts):
    digest = hashlib.sha256(': '.join(map(str, parts)).encode('ascii')).digest()
    return random.Random(int.from_bytes(digest[:16], 'big'))


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, z))))


def world(seed, split):
    r = rng('world', seed, split)
    edge = int(r.random() < 0.5)
    regime = r.randrange(4)
    shift = split != 'train'
    x_rho = ((0.0, 0.80, -0.80, 0.50) if not shift else
             (0.2, 0.60, -0.60, -0.35))[regime]
    hidden_effect = ((0.0, 0.48, 0.48, -0.48) if not shift else
                     (0.08, 0.58, -0.58, 0.42))[regime]
    n_obs = (90, 120, 140, 110)[regime]
    n_do_each = ((14, 10, 12, 24) if not shift else (8, 16, 20, 10))[regime]
    cause_effect = .38 if not shift else .29
    proxy_accuracy = .83 if not shift else .70

    def outcome(x, u):
        probability = min(.94, max(.06, .30 + cause_effect * edge * x + hidden_effect * (u - .5)))
        return int(r.random() < probability)

    observational = []
    for _ in range(n_obs):
        u = int(r.random() < .5)
        x = int(r.random() < .5 + x_rho * (u - .5))
        z = u if r.random() < proxy_accuracy else 1 - u
        observational.append((x, z, outcome(x, u)))
    interventions = []
    for x in (0, 1):
        for _ in range(n_do_each):
            u = int(r.random() < .5)
            interventions.append((x, outcome(x, u)))
    r.shuffle(observational)
    r.shuffle(interventions)
    return edge, observational, interventions


def contrast(pairs):
    outcomes = {x: [y for xx, y in pairs if xx == x] for x in (0, 1)}
    if not outcomes[0] or not outcomes[1]:
        return 0.0, 1.0
    a, b = (statistics.mean(outcomes[x]) for x in (0, 1))
    variance = sum(max(.05, m * (1 - m)) / len(outcomes[x])
                   for x, m in ((0, a), (1, b)))
    return b - a, variance


def effect_probability(diff, variance):
    expected = .36
    return sigmoid((2 * expected * diff - expected ** 2) / (2 * max(variance, .003)))


def experts(observational, interventions):
    d, v = contrast([(x, y) for x, z, y in observational])
    p_obs = effect_probability(d, v)
    d, v = contrast(interventions)
    p_do = effect_probability(d, v)
    strata = []
    for z in (0, 1):
        strata.append(contrast([(x, y) for x, zz, y in observational if zz == z]))
    p_adjusted = effect_probability(sum(d for d, v in strata) / 2,
                                    sum(v for d, v in strata) / 4)
    return (p_obs, p_do, p_adjusted)


def observable_features(predictions, num_interventions):
    # No ground-truth edge, hidden U or world regime is available to the referee.
    obs, do, adjusted = predictions
    votes = [int(p >= .5) for p in predictions]
    agree = int(votes[0] == votes[1] == votes[2])
    majority = int(sum(votes) >= 2)
    confidence = sum(abs(p - .5) for p in predictions) / 3
    confidence_bin = 0 if confidence < .20 else 1 if confidence < .35 else 2
    do_short = int(num_interventions <= 24)
    proxy_conflict = int(abs(adjusted - do) > .30)
    key = (majority, confidence_bin, 1 - agree, do_short, proxy_conflict)
    features = (1.0, obs, do, adjusted, abs(obs - do), num_interventions / 48)
    return key, confidence_bin, features


def cases(split):
    for seed in range(*RANGES[split]):
        label, observations, interventions = world(seed, split)
        probabilities = experts(observations, interventions)
        key, conf_bin, features = observable_features(probabilities, len(interventions))
        all_wrong = int(all((p >= .5) != bool(label) for p in probabilities))
        yield (seed, all_wrong, key, conf_bin, features)


def fit(train_rows):
    n = len(train_rows)
    positive = sum(row[1] for row in train_rows)
    global_rate = (positive + 1) / (n + 2)
    memory = defaultdict(lambda: [0, 0])
    confidence = defaultdict(lambda: [0, 0])
    for _, label, key, conf_bin, _ in train_rows:
        memory[key][0] += label
        memory[key][1] += 1
        confidence[conf_bin][0] += label
        confidence[conf_bin][1] += 1
    # Fully trained matched-feature ridge logistic baseline (fixed steps and hyperparameters).
    bias = math.log(global_rate / (1 - global_rate))
    beta = [bias] + [0.0] * 5
    for step in range(LOGISTIC_STEPS):
        gradient = [0.0] * 6
        for _, label, _, _, features in train_rows:
            error = sigmoid(sum(w * x for w, x in zip(beta, features))) - label
            for j in range(6):
                gradient[j] += error * features[j]
        for j in range(6):
            gradient[j] = gradient[j] / n + (LOGISTIC_RIDGE * beta[j] if j else 0)
            beta[j] -= LOGISTIC_RATE * gradient[j]
    return {'global_rate': global_rate, 'memory': dict(memory),
            'confidence': dict(confidence), 'logistic': beta, 'trained_worlds': n,
            'failure_count': positive}


def risk(model, row):
    seed, _, key, conf_bin, features = row
    count = model['memory'].get(key, (0, 0))
    conf_count = model['confidence'].get(conf_bin, (0, 0))
    native = (count[0] + PRIOR_STRENGTH * model['global_rate']) / (count[1] + PRIOR_STRENGTH)
    conf = (conf_count[0] + PRIOR_STRENGTH * model['global_rate']) / (conf_count[1] + PRIOR_STRENGTH)
    logistic = sigmoid(sum(a * b for a, b in zip(model['logistic'], features)))
    return {'native': native, 'global': model['global_rate'], 'confidence': conf,
            'logistic': logistic, 'disagreement': float(key[2]),
            'random': rng('random-ranking', seed).random()}


def selection_risk(labels, predictions, coverage=RETAIN_FRACTION):
    retain = int(len(labels) * coverage)
    assert retain > 0
    ids = sorted(range(len(labels)), key=lambda i: (predictions[i], i))[:retain]
    return sum(labels[i] for i in ids) / retain


def auc(labels, scores):
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        raise ValueError('no positive/negative cases')
    ordered = sorted(zip(scores, labels))
    ranks = 0.0
    start = 0
    while start < len(ordered):
        stop = start + 1
        while stop < len(ordered) and ordered[stop][0] == ordered[start][0]:
            stop += 1
        ranks += sum(label for _, label in ordered[start:stop]) * ((start + stop + 1) / 2)
        start = stop
    return (ranks - positives * (positives + 1) / 2) / (positives * negatives)


def evaluate(model, data, split):
    labels = [row[1] for row in data]
    predictions = [risk(model, row) for row in data]
    methods = ('native', 'global', 'confidence', 'logistic', 'disagreement', 'random')
    metrics = {}
    for method in methods:
        estimates = [item[method] for item in predictions]
        metrics[method] = {
            'selective_failure_rate_80pct': round(selection_risk(labels, estimates), 8),
            'brier': round(sum((y - p) ** 2 for y, p in zip(labels, estimates)) / len(data), 8),
            'auc': round(auc(labels, estimates), 8)}
    baseline = min(('global', 'confidence', 'logistic'),
                   key=lambda m: (metrics[m]['selective_failure_rate_80pct'], m))
    delta = metrics[baseline]['selective_failure_rate_80pct'] - metrics['native']['selective_failure_rate_80pct']
    interval = []
    rr = rng('bootstrap', split)
    for _ in range(BOOTSTRAP_DRAWS):
        sampled = [rr.randrange(len(data)) for _ in range(len(data))]
        ys = [labels[i] for i in sampled]
        native = [predictions[i]['native'] for i in sampled]
        best = [predictions[i][baseline] for i in sampled]
        interval.append(selection_risk(ys, best) - selection_risk(ys, native))
    interval.sort()
    low, high = interval[24], interval[974]
    target = metrics['native']['selective_failure_rate_80pct'] <= .85 * metrics[baseline]['selective_failure_rate_80pct']
    if delta > 0 and target and low > 0:
        verdict = 'DEVELOPMENT_SUPPORTED_NOT_SCIENTIFIC_PASS'
    elif delta < 0 or not target:
        verdict = 'DEVELOPMENT_NO_GO'
    else:
        verdict = 'DEVELOPMENT_MIXED'
    return {'cases': len(data), 'all_expert_failure_count': sum(labels),
            'all_expert_failure_prevalence': round(sum(labels) / len(data), 8),
            'retain_fraction': RETAIN_FRACTION, 'metrics': metrics,
            'strongest_nonprivileged_baseline': baseline, 'gain_over_baseline': round(delta, 8),
            'gain_paired_bootstrap_ci95': [round(low, 8), round(high, 8)], 'verdict': verdict}


def integrity(train_rows, evaluation, split):
    spans = [set(range(*r)) for r in RANGES.values()]
    assert all(spans[i].isdisjoint(spans[j]) for i in range(3) for j in range(i + 1, 3))
    assert len(train_rows) == 4096
    assert len(evaluation) == (1024 if split == 'dev' else 2048)
    assert all(len(row[4]) == 6 and len(row[2]) == 5 for row in evaluation)
    assert all(row[2][1] in (0, 1, 2) and 0 <= row[2][0] <= 1 for row in evaluation)
    # Risk model receives only row metadata, not its second (scoring label) item.
    assert risk(fit(train_rows[:32]), (123, 0, *train_rows[0][2:])) == risk(
        fit(train_rows[:32]), (123, 1, *train_rows[0][2:]))
    return {'seed_disjoint': True, 'observable_only_inference': True,
            'fixed_budget': True, 'no_external_sources': True}


def main(argv):
    if argv not in (['--dev'], ['--heldout']):
        raise SystemExit('Usage: experiment.py --dev|--heldout')
    split = 'dev' if argv == ['--dev'] else 'heldout'
    train_rows = list(cases('train'))
    model = fit(train_rows)
    rows = list(cases(split))
    audit = integrity(train_rows, rows, split)
    outcome = evaluate(model, rows, split)
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result = {'schema': 'yggdrasil.ynca02.synthetic-development.v1',
              'source_sha256': source_sha, 'split': split, 'train_worlds': len(train_rows),
              'train_all_expert_failures': model['failure_count'],
              'frozen_config': {'ranges': RANGES, 'experts': EXPERTS,
                 'prior_strength': PRIOR_STRENGTH, 'logistic_steps': LOGISTIC_STEPS,
                 'logistic_ridge': LOGISTIC_RIDGE, 'logistic_rate': LOGISTIC_RATE,
                 'retain_fraction': RETAIN_FRACTION, 'bootstrap_draws': BOOTSTRAP_DRAWS},
              'audits': audit, 'outcome': outcome,
              'claims': {'native_yggdrasil_integrated': False, 'scientific_pass': False,
                         'owner_acceptance': False, 'production_deployed': False}}
    sys.stdout.write(json.dumps(result, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
