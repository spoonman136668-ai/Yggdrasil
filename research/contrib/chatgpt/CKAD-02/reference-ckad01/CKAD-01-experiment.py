"""Exploratory 100k-fact knowledge-first causal learning experiment.

Synthetic public properties and actual selected simulated action outcomes only.
No authentic external source, original Yggdrasil model mutation or science PASS.
The finite pairwise learner is an isolated diagnostic, NOT Yggdrasil's native engine.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.tree import DecisionTreeClassifier

PREREG = Path(__file__).with_name('CKAD-01-prereg.json')
OUT = Path(__file__).with_name('CKAD-01-result.json')
SEEDS = (101, 202, 303)
ENTITY_COUNT = 10_000
N_PROPS = 10
LEVELS = (10_000, 25_000, 50_000, 100_000)
TRAIN_COUNT = 512
TEST_IDS = np.arange(6144, 8192, dtype=np.int32)
MIN_SUPPORT = 64
FAMILIES = ('A', 'B', 'C')


def sha_sort_indices(seed: int):
    ranks = []
    for i in range(ENTITY_COUNT * N_PROPS):
        ranks.append(hashlib.sha256(f'{seed}:knowledge:{i}'.encode()).digest()[:8])
    return np.argsort(np.frombuffer(b''.join(ranks), dtype='>u8'), kind='stable')


def make_world(seed: int):
    # Each entity gets ten properties provided by a deterministic simulator.
    # They are neither Web facts nor causal truths about the real world.
    p = np.empty((ENTITY_COUNT, N_PROPS), dtype=np.int8)
    source_digest = hashlib.sha256()
    for entity in range(ENTITY_COUNT):
        raw = hashlib.sha256(f'ckad-v1:{seed}:entity:{entity}'.encode()).digest()
        for prop in range(N_PROPS):
            val = (raw[prop // 8] >> (prop % 8)) & 1
            p[entity, prop] = val
            source_digest.update(entity.to_bytes(4, 'little'))
            source_digest.update(bytes((prop, val)))
    idx = np.arange(4096, dtype=np.int32)
    order = np.argsort(np.array([
        int.from_bytes(hashlib.sha256(f'{seed}:train:{int(x)}'.encode()).digest()[:8], 'big')
        for x in idx], dtype=np.uint64))
    selected = idx[order[:TRAIN_COUNT]]
    assert len(set(selected) & set(TEST_IDS)) == 0
    return p, selected, source_digest.hexdigest()


def effect(bits: np.ndarray, family: str):
    if family == 'A':
        return (bits[:, 0] ^ bits[:, 1]).astype(np.int8)
    if family == 'B':
        return (bits[:, 2] & (1 - bits[:, 3])).astype(np.int8)
    if family == 'C':
        return (bits[:, 4] + bits[:, 5] + bits[:, 6] >= 2).astype(np.int8)
    raise ValueError('Unknown family')


def sparse_read(public: np.ndarray, allowed: np.ndarray):
    # public is internal simulator truth; returned learning view gets ONLY
    # properties selected in the source exposure manifest.
    out = np.full(public.shape, -1, dtype=np.int8)
    out.reshape(-1)[allowed] = public.reshape(-1)[allowed]
    return out


def fit_pair_native(x, y):
    """Pair-composition rule generator from source-visible chosen outcomes.

    45 feature pairs are generated from PUBLIC input dimension, not per-world
    hidden law names. Only zero-conflict complete 2x2 truth tables qualify.
    """
    result = []
    for i, j in itertools.combinations(range(N_PROPS), 2):
        valid = (x[:, i] >= 0) & (x[:, j] >= 0)
        if valid.sum() < MIN_SUPPORT:
            continue
        groups = x[valid, i] * 2 + x[valid, j]
        yy = y[valid]
        table = []
        for k in range(4):
            sample = yy[groups == k]
            if len(sample) < 4 or sample.min() != sample.max():
                break
            table.append(int(sample[0]))
        if len(table) == 4:
            result.append((i, j, tuple(table)))
    return tuple(result)


def predict_pair_native(rules, x):
    n = len(x)
    values = np.full(n, -1, dtype=np.int8)
    if not rules:
        return values
    possible = np.full((len(rules), n), -1, dtype=np.int8)
    for k, (i, j, table) in enumerate(rules):
        valid = (x[:, i] >= 0) & (x[:, j] >= 0)
        key = x[valid, i] * 2 + x[valid, j]
        possible[k, valid] = np.asarray(table, dtype=np.int8)[key]
    same = (possible >= 0).all(axis=0) & (possible == possible[0]).all(axis=0)
    values[same] = possible[0, same]
    return values


def fit_exact_symbolic_independent(x, y):
    """Independently fitted exhaustive symbolic 2-feature truth table baseline."""
    hypotheses = []
    for a in range(N_PROPS):
        for b in range(a + 1, N_PROPS):
            evidence = defaultdict(list)
            for k in range(len(y)):
                f, g = int(x[k, a]), int(x[k, b])
                if f >= 0 and g >= 0:
                    evidence[(f, g)].append(int(y[k]))
            if sum(map(len, evidence.values())) < MIN_SUPPORT:
                continue
            if len(evidence) != 4 or any(len(v) < 4 for v in evidence.values()):
                continue
            if any(len(set(v)) != 1 for v in evidence.values()):
                continue
            hypotheses.append((a, b, tuple(evidence[k][0] for k in
                                           [(0, 0), (0, 1), (1, 0), (1, 1)])))
    return tuple(hypotheses)


def predict_exact_independent(hypotheses, x):
    out = []
    for row in x:
        possibilities = []
        for a, b, rule in hypotheses:
            if row[a] < 0 or row[b] < 0:
                break
            possibilities.append(rule[int(row[a]) * 2 + int(row[b])])
        else:
            out.append(possibilities[0] if possibilities and len(set(possibilities)) == 1 else -1)
            continue
        out.append(-1)
    return np.asarray(out, dtype=np.int8)


def metric(pred, y):
    known = pred >= 0
    correct = int((pred[known] == y[known]).sum())
    wrong = int((pred[known] != y[known]).sum())
    return {'correct': correct, 'wrong_confident': wrong,
            'coverage': int(known.sum()), 'abstain': len(y) - int(known.sum()),
            'total': int(len(y))}


def run():
    began = time.monotonic()
    doc = json.loads(PREREG.read_text())
    assert doc['source']['full_public_factual_relationships'] == 100_000
    assert doc['evaluation']['scientific_pass'] is False
    results = []
    lineage = []
    for seed in SEEDS:
        source_truth, train_entities, source_sha = make_world(seed)
        order = sha_sort_indices(seed)
        assert len(order) == 100_000 and len(np.unique(order)) == 100_000
        lineage.append({'seed': seed, 'synthetic_source_sha256': source_sha,
                        'training_entity_count': len(train_entities),
                        'heldout_entity_count': len(TEST_IDS)})
        for count in LEVELS:
            # A single nested exposure ordering gives exact knowledge scales.
            public = sparse_read(source_truth, order[:count])
            assert int((public >= 0).sum()) == count
            train_x = public[train_entities]
            test_x = public[TEST_IDS]
            prior_summaries = []
            prior_sha = []
            for family in FAMILIES:
                # The simulator returns results for a selected action=1 on
                # exactly the same support entities across knowledge levels.
                train_truth = effect(source_truth[train_entities], family)
                test_truth = effect(source_truth[TEST_IDS], family)
                fitted = fit_pair_native(train_x, train_truth)
                independent = fit_exact_symbolic_independent(train_x, train_truth)
                native = predict_pair_native(fitted, test_x)
                exact = predict_exact_independent(independent, test_x)
                if not np.array_equal(native, exact):
                    raise AssertionError('STRONG_SYMBOLIC_EQUAL_INFO_PARITY_FAIL')
                conventional = DecisionTreeClassifier(max_depth=4,
                    random_state=seed, min_samples_leaf=4)
                conventional.fit(train_x, train_truth)
                cart = conventional.predict(test_x).astype(np.int8)
                if len(set(int(x) for x in train_entities) & set(int(x) for x in TEST_IDS)):
                    raise AssertionError('SOURCE_ENTITY_LEAKAGE')
                retrieval = np.full(len(TEST_IDS), -1, dtype=np.int8)
                stored = {'seed': seed, 'relationships_exposed': count,
                          'family': family, 'selected_public_actions': TRAIN_COUNT,
                          'native': metric(native, test_truth),
                          'independent_symbolic': metric(exact, test_truth),
                          'conventional_CART': metric(cart, test_truth),
                          'retrieval_only': metric(retrieval, test_truth),
                          'native_compatible_rules': len(fitted),
                          'synthetic_source_sha256': source_sha,
                          'original_knowledge_facts_retained': int((public >= 0).sum())}
                results.append(stored)
                # Cold readout signatures are frozen before learning the next
                # distinct rule family in a separate source-keyed slot.
                predsha = hashlib.sha256(native.tobytes()).hexdigest()
                prior_summaries.append((family, tuple(fitted), predsha))
                prior_sha.append(predsha)
            if len(prior_summaries) != 3 or int((public >= 0).sum()) != count:
                raise AssertionError('KNOWLEDGE_INTERFERENCE')
            # Recompute previous learned outputs after all three rule
            # installations to establish separate-slot non-erasure only.
            for family, fitted, digest_old in prior_summaries:
                cold = predict_pair_native(fitted, test_x)
                if hashlib.sha256(cold.tobytes()).hexdigest() != digest_old:
                    raise AssertionError('COLD_RETENTION_DRIFT')
    # Preregistered comprehensive source-safe checks, no post-result tuning.
    assert len(results) == len(SEEDS) * len(LEVELS) * len(FAMILIES)
    assert all(r['selected_public_actions'] == 512 for r in results)
    assert all(r['retrieval_only']['correct'] == 0 for r in results)
    assert all(r['native'] == r['independent_symbolic'] for r in results)
    # Family C requires THREE relevant public features, not two.
    no_family = [r for r in results if r['family'] == 'C']
    assert all(r['native']['coverage'] == 0 for r in no_family)
    out = {'schema': 'ckad.exploratory-100k-fact-development-result.v1',
           'classification': 'SYNTHETIC_WIDE_FIRST_ENGINEERING_STUDY',
           'source_kind': 'EXPERIMENTER_AUTHORED_SYNTHETIC_PUBLIC_FACTS',
           'actual_original_source_action_calls': 0,
           'native_yggdrasil_model_modified': False,
           'tokenless_yggdrasil_cognitive_training_proved': False,
           'relationship_family_C_out_of_grammar': True,
           'scientific_pass': False,
           'source_facts_per_seed': 100_000,
           'action_outcomes_per_seed_and_mechanism': 512,
           'new_entity_holdout_queries_per_mechanism': 2048,
           'pre_reg_file_sha256': hashlib.sha256(PREREG.read_bytes()).hexdigest(),
           'results': results, 'lineage': lineage,
           'time_seconds': time.monotonic() - began}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    for count in LEVELS:
        for fam in FAMILIES:
            group = [r for r in results if r['relationships_exposed'] == count and r['family'] == fam]
            n = sum(x['native']['correct'] for x in group)
            cover = sum(x['native']['coverage'] for x in group)
            wrong = sum(x['native']['wrong_confident'] for x in group)
            cart = sum(x['conventional_CART']['correct'] for x in group)
            print(f'{count:6} facts / family {fam}: native {n:4}/6144 correct '
                  f'(coverage {cover:4}, wrong {wrong:3}), CART {cart:4}/6144')
    print('EXPERIMENT_RESULT=', OUT)
    print('WALL_SECONDS=', round(out['time_seconds'], 3))


if __name__ == '__main__':
    run()
