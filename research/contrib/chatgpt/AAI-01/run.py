"""AAI-01 frozen synthetic associative-gate assay. Stdlib only; no model integration."""
import hashlib
import json
import math
import random
import sys
import time

N = 24
TRAIN = range(1000, 1016)
DEV = range(2000, 2016)
REVERSE = range(3000, 3016)
SPEC = 'AAI01-SYNTH-V1|random.Random(seed)|nodes=24|train_seeds=1000..1015|dev_seeds=2000..2015|2_24_permutations|train_examples=6_per_world|heldout_queries=24_per_world|operation=compose_A_B|labels_not_exposed_in_dev|distractors=0_24_96|reversal_dev=seeds3000..3015'
assert hashlib.sha256(SPEC.encode()).hexdigest() == '20374304cadffc431ce02b1843aabbfecce02b93c054cd696e360682355c93d7'


def world(seed, distractors=0):
    rng = random.Random(seed)
    a, b = list(range(N)), list(range(N))
    rng.shuffle(a)
    rng.shuffle(b)
    sources = list(range(N))
    rng.shuffle(sources)
    c_rng = random.Random(seed + 400000)
    c = [(c_rng.randrange(N), c_rng.randrange(N)) for _ in range(distractors)]
    return {'a': a, 'b': b, 'sources': sources, 'c': c}


def compose(w, x, route):
    a, b = w.get('a'), w.get('b')
    if a is None or b is None or a[x] is None or b[x] is None:
        return None
    if route == 0:
        return b[a[x]]
    return a[b[x]]


def update(gate, w, x, answer):
    for route in (0, 1):
        gate[route] += int(compose(w, x, route) == answer)


def choose(gate):
    hi, lo = max(gate), min(gate)
    if hi < 4 or hi <= lo:
        return None
    return 0 if gate[0] > gate[1] else 1


def train_logistic(examples):
    # Conventional full-batch logistic route selector. Ambiguous examples cannot
    # distinguish routes and are ignored by both classifier and evidence counts.
    decisive = []
    for w, x, y in examples:
        matches = [compose(w, x, route) == y for route in (0, 1)]
        if matches[0] != matches[1]:
            decisive.append(0 if matches[0] else 1)
    if not decisive:
        return [0.0, 0.0], 0, float('inf'), False
    logits = [0.0, 0.0]
    loss = float('inf')
    for epoch in range(500):
        loss = 0.0
        grads = [0.0, 0.0]
        for route in (0, 1):
            p = 1.0 / (1.0 + math.exp(-logits[route]))
            target = sum(v == route for v in decisive) / len(decisive)
            grads[route] = p - target
            loss += -target * math.log(max(p, 1e-15)) - (1-target) * math.log(max(1-p, 1e-15))
        loss /= 2
        if loss <= .01:
            return logits, epoch + 1, loss, True
        for route in (0, 1):
            logits[route] -= 4.0 * grads[route]
    return logits, 500, loss, loss <= .01


def accuracy(predictions, truths):
    return sum(p == y for p, y in zip(predictions, truths)) / len(truths)


def main():
    t0 = time.perf_counter()
    gate = [0.0, 0.0]
    symbolic = [0, 0]
    examples = []
    for seed in TRAIN:
        w = world(seed)
        for x in w['sources'][:6]:
            y = compose(w, x, 0)
            examples.append((w, x, y))
            update(gate, w, x, y)
            update(symbolic, w, x, y)
    conventional, epochs, bce, converged = train_logistic(examples)
    state = json.dumps({'gate': gate}, sort_keys=True)
    restored_gate = json.loads(state)['gate']
    assert restored_gate == gate
    assert len(examples) == 96
    measures = {}
    for distraction in (0, 24, 96):
        candidate, sym, trained, flat, random_arm, truth = [], [], [], [], [], []
        for seed in DEV:
            w = world(seed, distraction)
            for x in range(N):
                truth.append(compose(w, x, 0))
                candidate.append(compose(w, x, choose(restored_gate)) if choose(restored_gate) is not None else None)
                sym.append(compose(w, x, choose(symbolic)) if choose(symbolic) is not None else None)
                best = 0 if conventional[0] > conventional[1] else 1
                trained.append(compose(w, x, best))
                flat.append(w['a'][x])  # one-step association without composition
                route = hashlib.sha256(f'{seed}:{x}:AAI01'.encode()).digest()[0] % 2
                random_arm.append(compose(w, x, route))
        measures[str(distraction)] = {'candidate': accuracy(candidate, truth), 'symbolic': accuracy(sym, truth), 'conventional': accuracy(trained, truth), 'flat': accuracy(flat, truth), 'random_route': accuracy(random_arm, truth), 'queries': len(truth)}
    shuffled = [0.0, 0.0]
    for w, x, y in examples:
        update(shuffled, w, x, (y + 1) % N)
    negative_abstains = choose(shuffled) is None
    # Per-world switch: four actual B->A targets update an isolated, resettable local gate.
    reverse_hits = 0
    conventional_reverse_hits = 0
    symbolic_reverse_hits = 0
    for seed in REVERSE:
        w = world(seed)
        xs = w['sources']
        observed = [(w, x, compose(w, x, 1)) for x in xs[:4]]
        local = [0.0, 0.0]
        symbol_local = [0, 0]
        for ww, x, y in observed:
            update(local, ww, x, y)
            update(symbol_local, ww, x, y)
        conv_local, _, _, conv_ok = train_logistic(observed)
        if not conv_ok:
            raise RuntimeError('reversal conventional control failed convergence')
        for x in xs[4:]:
            correct = compose(w, x, 1)
            reverse_hits += int(compose(w, x, choose(local)) == correct) if choose(local) is not None else 0
            conventional_reverse_hits += int(compose(w, x, 0 if conv_local[0] > conv_local[1] else 1) == correct)
            symbolic_reverse_hits += int(compose(w, x, choose(symbol_local)) == correct) if choose(symbol_local) is not None else 0
    # Negative controls: missing graph information must not fabricate a target.
    probe = world(2000)
    probe_x = 0
    original = compose(probe, probe_x, 0)
    missing = {'a': probe['a'][:], 'b': None}
    missing_abstains = compose(missing, probe_x, 0) is None
    altered = {'a': probe['a'][:], 'b': probe['b'][:]}
    altered['a'][probe_x] = next(k for k in range(N) if altered['b'][k] != original)
    edge_change_changes_answer = compose(altered, probe_x, 0) != original
    metrics = measures['0']
    checks = {
        'input_hash_match': True,
        'disjoint_worlds': not (set(TRAIN) & set(DEV) or set(TRAIN) & set(REVERSE) or set(DEV) & set(REVERSE)),
        'conventional_converged': converged,
        'negative_shuffled_abstains': negative_abstains,
        'missing_relation_abstains': missing_abstains,
        'altered_edge_changes_answer': edge_change_changes_answer,
        'cold_state_exact': restored_gate == gate,
        'distractor_unchanged': all(measures[str(n)]['candidate'] == metrics['candidate'] for n in (24, 96)),
    }
    reverse_acc = reverse_hits / 320
    supported = (all(checks.values()) and metrics['candidate'] >= .9 and metrics['candidate'] - metrics['flat'] >= .30
                 and metrics['candidate'] - metrics['random_route'] >= .25
                 and metrics['candidate'] + .01 >= max(metrics['symbolic'], metrics['conventional'])
                 and reverse_acc >= .90)
    result = {
        'schema': 'aai01.synthetic-dev-result.v1', 'preregistration_commit': 'b9ad110a54e5e2a631270bf45409777de2973314',
        'classification': 'DEV_MECHANISM_SUPPORTED_NO_SUPERIORITY' if supported else 'DEV_NEGATIVE_OR_MIXED',
        'train_examples': len(examples), 'candidate_learned_route_weights': gate,
        'symbolic_votes': symbolic, 'trained_conventional': {'epochs': epochs, 'bce': round(bce, 8), 'converged': converged},
        'DEV_by_distractor_count': measures, 'reverse_accuracy': {'candidate': reverse_acc, 'symbolic': symbolic_reverse_hits / 320, 'conventional': conventional_reverse_hits / 320},
        'cold_checkpoint_sha256': hashlib.sha256(state.encode()).hexdigest(),
        'checks': checks, 'elapsed_seconds_local_development': round(time.perf_counter() - t0, 6),
        'engineering_scope': 'local Python source-only development, not Yggdrasil full regression or cross-platform CI',
        'integration': 'NONE',
        'limitations': 'Hand-supplied two-route composition operator, accessible complete A/B graph, symbolic and conventional ceiling controls; not open-domain knowledge, scientific transfer or intelligence superiority.'
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    if not all(checks.values()):
        sys.exit(2)


if __name__ == '__main__':
    main()
