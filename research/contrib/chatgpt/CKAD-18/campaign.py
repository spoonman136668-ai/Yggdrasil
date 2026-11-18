"""CKAD18: isolated tokenless causal overhypothesis development experiment.

Synthetic rules are evaluator-only. Learner sees public x and revealed y, never
family/pair/sign. No native integration, protected source use, or promotion.
"""
import argparse
import hashlib
import itertools
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PAIRS = tuple(itertools.combinations(range(4), 2))
RULES = tuple((f, i, j, si, sj) for f in range(2) for i, j in PAIRS
              for si in range(2) for sj in range(2))
SEEDS = (101, 202, 303, 404, 505)
EPS = .001
SCHEMA = 'yggdrasil.ckad18.sidecar.v1'


def pack(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def law(h, x):
    f, i, j, si, sj = h
    u, v = ((x >> i) & 1) ^ si, ((x >> j) & 1) ^ sj
    return u & v if f == 0 else u | v


def family_posterior(tasks):
    weights = [.5, .5]
    for obs in tasks:
        likelihoods = [sum(all(law(h, x) == y for x, y in obs)
                           for h in RULES if h[0] == f) / 24 for f in (0, 1)]
        unnormalized = [weights[f] * likelihoods[f] + EPS for f in (0, 1)]
        weights = [u / sum(unnormalized) for u in unnormalized]
    return weights


def forecast(prior, obs, x):
    weights = [prior[h[0]] / 24 if all(law(h, a) == y for a, y in obs)
               else 0 for h in RULES]
    total = sum(weights)
    if not total:
        raise ValueError('CKAD18_CONTRADICTORY_EVIDENCE')
    return sum(w * law(h, x) for w, h in zip(weights, RULES)) / total


def exact_control(prior, obs, x):
    numerator = denominator = 0.
    for f in (0, 1):
        for i in range(4):
            for j in range(i+1, 4):
                for a in (0, 1):
                    for b in (0, 1):
                        h = f, i, j, a, b
                        if any(law(h, u) != y for u, y in obs):
                            continue
                        weight = prior[f] / 24
                        denominator += weight
                        numerator += weight * law(h, x)
    return numerator / denominator


def query(prior, obs, random_policy, rng):
    options = [x for x in range(16) if x not in {a for a, _ in obs}]
    if random_policy:
        return rng.choice(options)
    return max(options, key=lambda x: (forecast(prior, obs, x) *
                                     (1 - forecast(prior, obs, x)), -x))


def brier(prior, obs, hidden):
    return sum((forecast(prior, obs, x) - law(hidden, x))**2 for x in range(16))/16


def regret(prior, obs, hidden):
    misses = 0
    for ctx in range(8):
        action = int(forecast(prior, obs, ctx|8) > forecast(prior, obs, ctx))
        misses += max(law(hidden, ctx), law(hidden, ctx|8)) - law(hidden, ctx|(action<<3))
    return misses/8


def world(seed, f, hold, pair, flipped=False):
    i, j = PAIRS[pair]
    rng = random.Random(seed*100003+f*10007+hold*101+pair*11)
    return (1-f if flipped else f), i, j, rng.randrange(2), rng.randrange(2)


def trained(seed, f, hold):
    tasks = []
    for pair in range(6):
        if pair == hold:
            continue
        rng = random.Random(seed*65537+f*4099+hold*257+pair*19)
        hidden = world(seed, f, hold, pair)
        tasks.append([(x, law(hidden, x)) for x in rng.sample(range(16), 6)])
    return tasks


def checkpoint(tasks):
    return pack({'schema': SCHEMA, 'tasks': tasks, 'prior': family_posterior(tasks),
                 'scientific_pass': False})


def restore(raw, expected):
    if sha(raw) != expected:
        raise ValueError('CKAD18_BAD_CHECKPOINT_PIN')
    d = json.loads(raw)
    if set(d) != {'schema', 'tasks', 'prior', 'scientific_pass'} or \
       d['schema'] != SCHEMA or d['scientific_pass'] is not False or pack(d) != raw or \
       len(d['tasks']) != 5 or any(len(t) != 6 for t in d['tasks']):
        raise ValueError('CKAD18_BAD_CHECKPOINT_SCHEMA')
    for task in d['tasks']:
        if len(set(x for x, _ in task)) != 6 or any(type(x) is not int or type(y) is not int
                or not 0 <= x < 16 or y not in (0, 1) for x, y in task):
            raise ValueError('CKAD18_BAD_CHECKPOINT_DATA')
    if max(abs(a-b) for a, b in zip(d['prior'], family_posterior(d['tasks']))) > 1e-15:
        raise ValueError('CKAD18_BAD_CHECKPOINT_COUNTS')
    return d['prior']


def run():
    start = time.monotonic()
    traces, negatives, cold = [], {'shuffled_prior_true_family': [], 'flipped_brier0': []}, 0
    for seed in SEEDS:
        for fam in (0, 1):
            for held in range(6):
                tasks = trained(seed, fam, held)
                raw = checkpoint(tasks)
                prior = restore(raw, sha(raw))
                if cold < 2:
                    with tempfile.TemporaryDirectory() as tmp:
                        path = Path(tmp)/'state.json'; path.write_bytes(raw)
                        subprocess.run([sys.executable, '-B', __file__, '--cold', str(path), '--pin', sha(raw)],
                                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
                    cold += 1
                try:
                    restore(raw[:-1] + b'!', sha(raw))
                    raise AssertionError('CKAD18_TAMPER_WAS_ACCEPTED')
                except ValueError:
                    pass
                hidden = world(seed, fam, held, held)
                for arm in ('meta_active', 'no_meta_active', 'meta_random'):
                    p = [.5, .5] if arm == 'no_meta_active' else prior
                    obs, rng = [], random.Random(seed*991+fam*41+held)
                    metrics = {'brier_at_0': brier(p, obs, hidden)}
                    for k in range(1, 5):
                        x = query(p, obs, arm == 'meta_random', rng)
                        obs.append((x, law(hidden, x)))
                        if k in (2, 4):
                            metrics[f'brier_at_{k}'] = brier(p, obs, hidden)
                        if any(abs(forecast(p, obs, q) - exact_control(p, obs, q)) > 1e-12
                               for q in range(16)):
                            raise AssertionError('CKAD18_EXACT_CONTROL_MISMATCH')
                    metrics['decision_regret_at_4'] = regret(p, obs, hidden)
                    traces.append({'seed': seed, 'family': fam, 'held_pair': held,
                                   'arm': arm, 'interventions': obs, **metrics})
                shuffled = []
                for i, task in enumerate(tasks):
                    ys = [y for _, y in task]
                    random.Random(seed*71+i*811+fam*101+held).shuffle(ys)
                    shuffled.append([(x, ys[k]) for k, (x, _) in enumerate(task)])
                negatives['shuffled_prior_true_family'].append(family_posterior(shuffled)[fam])
                negatives['flipped_brier0'].append(brier(prior, [], world(seed, fam, held, held, flipped=True)))
    metrics = ('brier_at_0', 'brier_at_2', 'brier_at_4', 'decision_regret_at_4')
    arms = {arm: {k: sum(t[k] for t in traces if t['arm'] == arm)/60 for k in metrics}
            for arm in ('meta_active', 'no_meta_active', 'meta_random')}
    gates = {'brier_gain': arms['meta_active']['brier_at_2'] <= .85*arms['no_meta_active']['brier_at_2'],
             'regret_gate_numeric': arms['meta_active']['decision_regret_at_4'] <= .85*arms['meta_random']['decision_regret_at_4']}
    meaningful_regret = arms['meta_random']['decision_regret_at_4'] > 0
    output = {'schema':'yggdrasil.ckad18.result.v1', 'classification':
              'DEVELOPMENT_PREDICTION_GAIN_ACTION_INCONCLUSIVE' if gates['brier_gain'] and not meaningful_regret
              else 'EXPLORATORY_DEVELOPMENT_NO_GO', 'cases':60, 'seeds':list(SEEDS),
              'training_tasks_per_case':5, 'train_queries_per_task':6, 'test_queries_per_case':4,
              'held_pair_training_overlap':0, 'cold_restores':cold, 'independent_exact_bayes_parity':True,
              'arms':arms, 'development_gates':gates, 'action_effect_non_degenerate':meaningful_regret,
              'negative':{k:sum(v)/len(v) for k,v in negatives.items()}, 'traces':traces,
              'scientific_pass':False, 'accepted_native':False, 'deployment':'NONE'}
    output['stable_sha256'] = sha(pack(output))
    output['whole_wall_seconds'] = time.monotonic()-start
    if output['whole_wall_seconds'] >= 120:
        raise RuntimeError('CKAD18_WALL_BUDGET')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-directory', type=Path)
    parser.add_argument('--cold', type=Path)
    parser.add_argument('--pin', type=str)
    args = parser.parse_args()
    if args.cold:
        assert len(restore(args.cold.read_bytes(), args.pin)) == 2
        print('COLD_RESTORE_PASS')
    else:
        if args.output_directory is None:
            parser.error('--output-directory required')
        args.output_directory.mkdir(parents=True, exist_ok=True)
        result = run()
        (args.output_directory/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps({k:result[k] for k in ('classification','cases','arms','development_gates','negative',
                                              'action_effect_non_degenerate','stable_sha256','whole_wall_seconds')},sort_keys=True))
