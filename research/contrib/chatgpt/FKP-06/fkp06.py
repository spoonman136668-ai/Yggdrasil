"""FKP-06 public DEV-only four-parent causal source identifiability audit.

This is NOT a native Yggdrasil learner, protected evaluation, or scientific PASS.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
import json
import random
import time

N_BITS = 32
N_HYP = 107880
DEV_SEEDS = range(700, 724)
N_PUBLIC = 128
N_HELD = 256
BUDGET = 12
CEILING_BUDGET = 64


def laws():
    out = []
    for a, b, c, d in combinations(range(N_BITS), 4):
        out.extend(((a, b, c, d), (a, c, b, d), (a, d, b, c)))
    assert len(out) == N_HYP
    return out


def consequence(law, action):
    a, b, c, d = law
    return (((action >> a) & (action >> b) & 1) ^
            ((action >> c) & (action >> d) & 1))


def inputs():
    rng = random.Random(606)
    seen = set()
    ordered = []
    while len(ordered) < N_PUBLIC + N_HELD:
        action = rng.getrandbits(N_BITS)
        if action not in seen:
            seen.add(action)
            ordered.append(action)
    return ordered[:N_PUBLIC], ordered[N_PUBLIC:]


def secret_index(seed):
    assert seed in DEV_SEEDS, "protected and arbitrary worlds excluded"
    x = sha256(f"FKP06_PUBLIC_DEV_ONLY|{seed}".encode()).digest()
    return int.from_bytes(x[:8], 'big') % N_HYP


def response_mask(action, hypotheses):
    """Bit i is the output for public hypothesis i; never queries a world."""
    data = bytearray((len(hypotheses) + 7) // 8)
    for idx, law in enumerate(hypotheses):
        if consequence(law, action):
            data[idx >> 3] |= 1 << (idx & 7)
    return int.from_bytes(data, 'little')


class PublicWorld:
    def __init__(self, seed, hypotheses, paid_limit):
        self._law = hypotheses[secret_index(seed)]
        self.paid_limit = paid_limit
        self.actions = []

    def observe(self, action):
        if type(action) is not int or not 0 <= action < (1 << N_BITS):
            raise ValueError('BAD_ACTION')
        if action in self.actions:
            raise ValueError('DUPLICATE_ACTION')
        if len(self.actions) >= self.paid_limit:
            raise ValueError('ACTION_BUDGET_EXCEEDED')
        self.actions.append(action)
        return consequence(self._law, action)

    def evaluator_truth(self, held):
        if len(self.actions) != self.paid_limit:
            raise ValueError('UNSEALED_INTERVENTIONS')
        return [consequence(self._law, a) for a in held]


def posterior_predictions(alive, held_masks):
    n = alive.bit_count()
    assert n > 0
    return [int(2 * (alive & mask).bit_count() > n) for mask in held_masks]


def evaluate_policy(seed, hypotheses, public, masks, held_masks, budget, policy):
    world = PublicWorld(seed, hypotheses, budget)
    alive = (1 << N_HYP) - 1
    selected = []
    random_indices = random.Random(1000 + seed).sample(range(N_PUBLIC), budget) if policy == 'random' else []
    for step in range(budget):
        if policy == 'random':
            idx = random_indices[step]
        else:
            n = alive.bit_count()
            best, idx = -1, -1
            for j, mask in enumerate(masks):
                if j in selected:
                    continue
                n1 = (alive & mask).bit_count()
                score = min(n1, n - n1)
                if score > best:
                    best, idx = score, j
        assert idx not in selected
        selected.append(idx)
        result = world.observe(public[idx])
        alive = alive & (masks[idx] if result else ~masks[idx])
        if not alive:
            raise AssertionError('TRUTH_ELIMINATED')
    return {'selected': selected, 'remaining': alive.bit_count(),
            'prediction': posterior_predictions(alive, held_masks),
            'truth': world.evaluator_truth, 'world': world}


def run():
    wall = time.perf_counter()
    cpu = time.process_time()
    hypotheses = laws()
    public, held = inputs()
    assert len(set(public + held)) == N_PUBLIC + N_HELD
    public_masks = [response_mask(a, hypotheses) for a in public]
    held_masks = [response_mask(a, hypotheses) for a in held]
    rows = []
    for seed in DEV_SEEDS:
        a = evaluate_policy(seed, hypotheses, public, public_masks, held_masks, BUDGET, 'active')
        b = evaluate_policy(seed, hypotheses, public, public_masks, held_masks, BUDGET, 'random')
        c = evaluate_policy(seed, hypotheses, public, public_masks, held_masks, CEILING_BUDGET, 'active')
        assert c['selected'][:BUDGET] == a['selected'], '12/64 action-prefix drift'
        pred = {name: v['prediction'] for name, v in [('active12', a), ('random12', b), ('active64', c)]}
        truth = c['world'].evaluator_truth(held)
        scores = {name: sum(int(p == t) for p, t in zip(values, truth)) / N_HELD
                  for name, values in pred.items()}
        rows.append({'seed': seed, 'accuracy': scores,
                     'remaining': {name: v['remaining'] for name, v in [('active12', a), ('random12', b), ('active64', c)]},
                     'actions': {name: v['selected'] for name, v in [('active12', a), ('random12', b), ('active64', c)]}})
    means = {name: sum(r['accuracy'][name] for r in rows) / len(rows)
             for name in ('active12', 'random12', 'active64')}
    delta = means['active64'] - means['active12']
    passed = delta >= 0.05 and means['active64'] >= 0.98 and means['active12'] <= 0.95
    return {'schema': 'fkp06.public-source-audit.v1', 'result': 'SOURCE_HEADROOM_PASS' if passed else 'SOURCE_HEADROOM_NO_GO',
            'scientific_pass': False, 'native_model_updated': False, 'protected_source_used': False,
            'source_worlds': len(rows), 'hypotheses': N_HYP, 'public_actions': N_PUBLIC, 'held_actions': N_HELD,
            'mean_held_accuracy': means, 'ceiling_minus_12': delta, 'worlds_with_singleton_64': sum(r['remaining']['active64'] == 1 for r in rows),
            'full_dev_wall_seconds': time.perf_counter() - wall, 'full_dev_cpu_seconds': time.process_time() - cpu, 'per_world': rows}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
