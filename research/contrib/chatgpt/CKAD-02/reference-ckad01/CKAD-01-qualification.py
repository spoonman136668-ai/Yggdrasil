"""Independent exploratory checks; does not alter frozen CKAD-01 method."""
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import sklearn

HERE = Path(__file__).resolve().parent
EXP = HERE / 'CKAD-01-experiment.py'
PREREG = HERE / 'CKAD-01-prereg.json'
RESULT = HERE / 'CKAD-01-result.json'
q = importlib.util.spec_from_file_location('ckad01_frozen_dev', EXP)
m = importlib.util.module_from_spec(q)
q.loader.exec_module(m)


def check(c, message):
    if not c:
        raise AssertionError(message)


def semantic_bytes(doc):
    stable = {k: v for k, v in doc.items() if k != 'time_seconds'}
    return json.dumps(stable, sort_keys=True, separators=(',', ':')).encode()

start = time.monotonic()
initial = json.loads(RESULT.read_text())
check(initial['source_facts_per_seed'] == 100000, 'scale')
check(len(initial['results']) == 36, 'arms')
check(initial['scientific_pass'] is False, 'science')
check(initial['actual_original_source_action_calls'] == 0, 'external first use')
check(initial['pre_reg_file_sha256'] == hashlib.sha256(PREREG.read_bytes()).hexdigest(), 'prereg')

# Deliberately shuffle public factual consequences at unchanged action budget.
# Correct source-informed knowledge must not survive an unrelated label shuffle.
negative = []
for seed in m.SEEDS:
    facts, train_ids, fact_sha = m.make_world(seed)
    view = facts.copy()
    x = view[train_ids]
    for family in ('A', 'B', 'C'):
        y = m.effect(facts[train_ids], family)
        y_shuffled = y.copy()
        np.random.default_rng(seed + ord(family)).shuffle(y_shuffled)
        rules = m.fit_pair_native(x, y_shuffled)
        check(len(rules) == 0, 'shuffled causal outcomes incorrectly accepted')
        p = m.predict_pair_native(rules, view[m.TEST_IDS])
        check((p == -1).all(), 'shuffled labels produced false-confidence predictions')
        no_outcomes = m.fit_pair_native(x[:0], y[:0])
        check(not no_outcomes, 'zero observed outcomes yielded rule')
        negative.append({'seed': seed, 'family': family,
                         'shuffled_source_rules': len(rules),
                         'zero_feedback_rules': len(no_outcomes)})

# Fresh-process replay of every arm; wall-time is deliberately excluded
# from the scientific-result identity.
p = subprocess.run([sys.executable, '-B', str(EXP)], text=True,
                   capture_output=True, check=True, timeout=60)
replay = json.loads(RESULT.read_text())
check(semantic_bytes(initial) == semantic_bytes(replay),
      'independent fresh Python process changed frozen outcome')

pairs = [(row['relationships_exposed'], row['family'], row['seed']) for row in initial['results']]
check(len(pairs) == len(set(pairs)), 'replayed/duplicate arm')
check(all(row['selected_public_actions'] == 512 for row in initial['results']), 'actions unequal')
check(all(row['native'] == row['independent_symbolic'] for row in initial['results']),
      'exact strong symbolic mismatch')
check(all(row['original_knowledge_facts_retained'] == row['relationships_exposed']
          for row in initial['results']), 'fact retention')
check(all(row['native']['coverage'] == 0 for row in initial['results']
          if row['family'] == 'C'), 'unseen C family inappropriately supported')

# Preserved full source remains completely distinct from measured effect
# tuples. A synthetic source label is *not* independent real grounding.
summary = {}
for n in m.LEVELS:
    summary[str(n)] = {}
    for fam in m.FAMILIES:
        group = [r for r in initial['results']
                 if r['family'] == fam and r['relationships_exposed'] == n]
        summary[str(n)][fam] = {
            'native_correct': sum(r['native']['correct'] for r in group),
            'native_covered': sum(r['native']['coverage'] for r in group),
            'native_confident_wrong': sum(r['native']['wrong_confident'] for r in group),
            'CART_correct': sum(r['conventional_CART']['correct'] for r in group),
            'holdout_questions': 6144,
            'strong_symbolic_equal': all(r['independent_symbolic'] == r['native'] for r in group),
        }

audit = {
    'schema': 'ckad.exploratory-qualification-v1',
    'check_results': {
        'fresh_process_semantic_replay': 'PASS',
        'synthetic_source_provenance': 'PASS_FOR_SYNTHETIC_ONLY',
        'exact_100k_exposure': 'PASS',
        '9_seed_by_family_shuffled_outcome_negatives': 'PASS',
        '9_seed_by_family_zero_feedback_negatives': 'PASS',
        'cold_unseen_entities': 'PASS',
        'symbolic_equal_information_parity': 'PASS',
        'prior_property_records_non_erasure': 'PASS',
        'unmodeled_majority_abstention': 'PASS',
        'independent_external_science': 'NOT_RUN',
        'native_Yggdrasil_qualification': 'NOT_RUN',
        'cross_platform_final_regression': 'NOT_RUN',
    },
    'semantic_result_sha256': hashlib.sha256(semantic_bytes(initial)).hexdigest(),
    'prereg_sha256': hashlib.sha256(PREREG.read_bytes()).hexdigest(),
    'source_code_sha256': hashlib.sha256(EXP.read_bytes()).hexdigest(),
    'negative_controls': negative,
    'summary': summary,
    'environment': {'python': sys.version.split()[0],
                    'platform': platform.system()+' '+platform.release(),
                    'numpy': np.__version__, 'scikit_learn': sklearn.__version__},
    'qual_time_seconds': time.monotonic() - start,
    'scientific_pass': False,
    'deployment': False,
}
(HERE / 'CKAD-01-audit.json').write_text(json.dumps(audit, indent=2, sort_keys=True) + '\n')
print(json.dumps({
    'checks': audit['check_results'],
    'result_sha256': audit['semantic_result_sha256'],
    'prereg_sha256': audit['prereg_sha256'],
    'source_sha256': audit['source_code_sha256'],
    'qualification_wall_seconds': round(audit['qual_time_seconds'], 3),
}, indent=2))
