"""Frozen synthetic CCE05 evaluator. One original primary DEV execution only.

All learners see public observations/actions. A fully trained four-state
Baum-Welch HMM is the strongest structured comparator; its state count is a
control advantage, not a label or property supplied to the CCE learner.
"""
import argparse
import json
import math
import random
import time
from pathlib import Path
from cce05 import PredictiveEcology, FullSuffixTable, EPISODES, HORIZON

SEEDS = (31, 59, 101, 149, 211)
EVAL_EPISODES = 80
EVAL_HORIZON = 30
HMM_STATES = 4
HMM_RESTARTS = 2
HMM_ITERATIONS = 12
MODELS = ('cce', 'hmm4', 'full_depth3', 'depth1', 'iid')


def actions_for(rng, length, evaluation):
    if evaluation:
        actions = [rng.randrange(3) for _ in range(length)]
        actions[7:10] = (2, 1, 2)
        return tuple(actions)
    result = []
    while len(result) < length:
        a = rng.randrange(3)
        if len(result) >= 2 and result[-2:] == [2, 1] and a == 2:
            continue
        result.append(a)
    return tuple(result)


def observe_episode(rng, actions, positive):
    if not positive:
        return tuple(rng.randrange(2) for _ in range(len(actions) + 1))
    hidden = rng.randrange(4)
    def observe():
        return (((hidden & 1) ^ ((hidden >> 1) & 1)) ^ int(rng.random() < 0.08))
    out = [observe()]
    for action in actions:
        u = hidden & 1
        v = (hidden >> 1) & 1
        if action == 0:
            u ^= 1
        elif action == 1:
            v ^= 1
        else:
            u ^= v
        hidden = u | (v << 1)
        out.append(observe())
    return tuple(out)


def dataset(seed, positive, evaluation):
    rng = random.Random(seed + 500000 if evaluation else seed)
    count = EVAL_EPISODES if evaluation else EPISODES
    length = EVAL_HORIZON if evaluation else HORIZON
    return tuple((obs := observe_episode(rng, actions := actions_for(rng, length, evaluation), positive), actions)
                 for _ in range(count))


def emission(o, p):
    return p if o else (1.0 - p)


class FittedActionHMM:
    """Four-state public-only 12-step EM with two fixed random starts."""
    def __init__(self, restart):
        rng = random.Random(104729 + restart * 13)
        self.pi = [0.25] * HMM_STATES
        self.emit = [0.15 + 0.7 * rng.random() for _ in range(HMM_STATES)]
        self.transitions = []
        for a in range(3):
            rows = []
            for i in range(HMM_STATES):
                raw = [0.1 + rng.random() for _ in range(HMM_STATES)]
                total = sum(raw)
                rows.append([v / total for v in raw])
            self.transitions.append(rows)

    def forward(self, obs, actions):
        alpha = [[self.pi[i] * emission(obs[0], self.emit[i]) for i in range(HMM_STATES)]]
        scale = [sum(alpha[0])]
        alpha[0] = [v / scale[0] for v in alpha[0]]
        for t, action in enumerate(actions):
            next_alpha = [emission(obs[t+1], self.emit[j]) *
                          sum(alpha[-1][i] * self.transitions[action][i][j]
                              for i in range(HMM_STATES))
                          for j in range(HMM_STATES)]
            norm = sum(next_alpha)
            scale.append(norm)
            alpha.append([v / norm for v in next_alpha])
        return alpha, scale

    def train_iteration(self, episodes):
        pi_acc = [0.0] * HMM_STATES
        emit_one = [0.0] * HMM_STATES
        emit_n = [0.0] * HMM_STATES
        t_acc = [[[0.0] * HMM_STATES for _ in range(HMM_STATES)] for _ in range(3)]
        for obs, actions in episodes:
            alpha, scales = self.forward(obs, actions)
            beta = [[1.0] * HMM_STATES for _ in range(len(obs))]
            for t in range(len(actions) - 1, -1, -1):
                a, observation = actions[t], obs[t+1]
                beta[t] = [sum(self.transitions[a][i][j] * emission(observation, self.emit[j]) *
                               beta[t+1][j] for j in range(HMM_STATES)) / scales[t+1]
                           for i in range(HMM_STATES)]
            for t, observation in enumerate(obs):
                gamma = [alpha[t][i] * beta[t][i] for i in range(HMM_STATES)]
                total = sum(gamma)
                gamma = [v / total for v in gamma]
                for i in range(HMM_STATES):
                    if t == 0:
                        pi_acc[i] += gamma[i]
                    emit_n[i] += gamma[i]
                    emit_one[i] += gamma[i] * observation
                if t < len(actions):
                    a = actions[t]
                    xi = [[alpha[t][i] * self.transitions[a][i][j] *
                           emission(obs[t+1], self.emit[j]) * beta[t+1][j]
                           for j in range(HMM_STATES)] for i in range(HMM_STATES)]
                    norm = sum(sum(row) for row in xi)
                    for i in range(HMM_STATES):
                        for j in range(HMM_STATES):
                            t_acc[a][i][j] += xi[i][j] / norm
        n = len(episodes)
        self.pi = [(value + 0.1) / (n + 0.4) for value in pi_acc]
        self.emit = [(emit_one[i] + 0.1) / (emit_n[i] + 0.2)
                     for i in range(HMM_STATES)]
        for a in range(3):
            for i in range(HMM_STATES):
                row = t_acc[a][i]
                self.transitions[a][i] = [(v + 0.1) / (sum(row) + 0.4) for v in row]

    def log_likelihood(self, episodes):
        return sum(sum(math.log(x) for x in self.forward(obs, acts)[1])
                   for obs, acts in episodes)

    @classmethod
    def fit(cls, episodes):
        best = None
        winner_score = float('-inf')
        for restart in range(HMM_RESTARTS):
            candidate = cls(restart)
            for _ in range(HMM_ITERATIONS):
                candidate.train_iteration(episodes)
            score = candidate.log_likelihood(episodes)
            if score > winner_score:
                best, winner_score = candidate, score
        return best, winner_score

    def predict(self, obs, actions, new_action):
        alpha = self.forward(obs, actions)[0][-1]
        return sum(alpha[i] * self.transitions[new_action][i][j] *
                   self.emit[j] for i in range(HMM_STATES)
                   for j in range(HMM_STATES))


def one_world(seed, positive):
    train = dataset(seed, positive, False)
    val = dataset(seed, positive, True)
    missing = sum(tuple(acts[i:i+3]) == (2, 1, 2)
                  for _, acts in train for i in range(len(acts)-2))
    if missing:
        raise ValueError('CCE05_TRAIN_ACTION_SPLIT_LEAKAGE')
    times = {}
    start = time.perf_counter()
    learner = PredictiveEcology()
    full = FullSuffixTable(3)
    depth1 = FullSuffixTable(1)
    for obs, acts in train:
        learner.observe_episode(obs, acts)
        full.observe_episode(obs, acts)
        depth1.observe_episode(obs, acts)
    learner.freeze()
    times['cce_and_history_tables'] = time.perf_counter()-start
    start = time.perf_counter()
    hmm, hmm_train_ll = FittedActionHMM.fit(train)
    times['hmm4'] = time.perf_counter()-start
    checkpoint = learner.snapshot()
    restored = PredictiveEcology.restore(checkpoint)
    totals = {name: 0.0 for name in MODELS}
    equal_cold = checkpoint == restored.snapshot()
    withheld = 0
    for observations, actions in val:
        withheld += sum(tuple(actions[i:i+3]) == (2,1,2)
                        for i in range(len(actions)-2))
        for t, action in enumerate(actions):
            obs_so_far = observations[:t+1]
            actions_so_far = actions[:t]
            options = {
                'cce': learner.predict(obs_so_far, actions_so_far, action),
                'hmm4': hmm.predict(obs_so_far, actions_so_far, action),
                'full_depth3': full.predict(obs_so_far, actions_so_far, action),
                'depth1': depth1.predict(obs_so_far, actions_so_far, action),
                'iid': 0.5,
            }
            if restored.predict(obs_so_far, actions_so_far, action) != options['cce']:
                equal_cold = False
            for name, p in options.items():
                totals[name] += (p - observations[t+1])**2
    return {
        'seed': seed, 'world': 'positive' if positive else 'null',
        'brier': {name: value/(EVAL_EPISODES*EVAL_HORIZON)
                  for name, value in totals.items()},
        'selected_cells': len(learner.selected), 'cells_per_action': [
            sum(key[0]==a for key in learner.selected) for a in range(3)],
        'full_table_entries': len(full.counts),
        'checkpoint_bytes': len(checkpoint),
        'cold_equal': equal_cold, 'withheld_212_substrings': withheld,
        'train_episodes': len(train), 'eval_episodes': len(val),
        'hmm_train_loglik': hmm_train_ll, 'training_seconds_diagnostic': times,
    }


def benchmark():
    positive = [one_world(s, True) for s in SEEDS]
    null = [one_world(s, False) for s in SEEDS]
    averages = {name: sum(r['brier'][name] for r in positive)/len(SEEDS)
                for name in MODELS}
    strongest = min(averages[n] for n in MODELS if n != 'cce')
    margin = strongest-averages['cce']
    null_small = sum(r['selected_cells']<=3 for r in null)
    cold_exact = sum(r['cold_equal'] for r in positive)
    withheld = sum(r['withheld_212_substrings'] for r in positive)
    supported = (margin>=0.01 and null_small==5 and cold_exact==5
                 and withheld>=50)
    mixed = any(averages['cce'] < averages[n] for n in MODELS if n != 'cce')
    return {'schema': 'yggdrasil.y2.cce05.dev-result.v1',
            'classification': 'DEVELOPMENT_SIGNAL' if supported else 'MIXED' if mixed else 'NEGATIVE',
            'scientific_gain_verified': False, 'native_science_accepted': False,
            'preregistered_required_margin': 0.01, 'seeds': list(SEEDS),
            'positive': positive, 'null': null, 'average_positive_brier': averages,
            'strongest_trained_control_brier': strongest, 'margin_vs_strongest': margin,
            'null_small_cell_seeds': null_small, 'cold_equal_seeds': cold_exact,
            'heldout_212_substrings_positive': withheld,
            'limitations': ['Predictive public history cells are not independently identified hidden causal entities.',
                            'The depth=3 and structural admission thresholds are fixed before training.',
                            'The HMM control has a priori four states; no matched compute or physical energy gain claimed.',
                            'No unusual domain transfer, retained learning under interference, or AGI evidence.']}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    out = json.dumps(benchmark(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(out, encoding='utf-8')
    print(out, end='')
