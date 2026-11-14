"""WSP98 source-blind prospective PUBLIC evaluation. No reserved evaluator here.

No PR/test imports invoke evaluate_public. The only first-use entrypoint is
--public-only after source commit and independent qualification decision.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from core import ACTIONS, N, PASSIVE_ROWS, DirectWeights, World, canonical, digest, random_query, phi
from controls import PolynomialGradient, SymbolicInducer, TanhGradient

PREREG = json.loads(Path(__file__).with_name('prereg.json').read_text(encoding='utf-8'))
PUBLIC = range(98011, 98031)
if (PREREG.get('experiment_id') != 'WSP-98' or PREREG['world']['nodes'] != N or
        PREREG['frozen_design']['seeds']['public_world_ids'] !=
        '98011..98030 inclusive (20 distinct worlds)'):
    raise ValueError('registered experiment identity or public split drift')
METHODS = ('direct_active', 'direct_random', 'passive_only', 'symbolic', 'polynomial_gradient',
           'tanh_neural', 'shuffled_effect', 'no_edit')


def passive_predict(model, x):
    """Uses the SAME direct RLS coefficients with 24 observed rows only."""
    f = phi(x)
    return tuple(int(sum(w[j] * f[j] for j in range(len(f))) > 0) for w in model.w)


def one_world(world_id):
    start_wall = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    world = World(world_id)
    passive = world.passive()
    original_x = tuple(r['x'] for r in passive)
    source = tuple((r['x'], r['y']) for r in passive)
    direct, random, passive_only, shuffled = (DirectWeights() for _ in range(4))
    for i, (x, y) in enumerate(source):
        for m in (direct, random, passive_only, shuffled):
            m.observe(x, y, expected_index=i)
    source_sha = digest(source)
    active_rows = []
    random_rows = []
    active_plans = []
    random_plans = []
    cpu_actions_start = time.process_time_ns()
    for i in range(ACTIONS):
        plan = direct.choose(original_x, world_id, i)
        response = world.intervene('active', i, *plan)
        active_plans.append(plan)
        active_rows.append((response['x'], response['y']))
        direct.observe(response['x'], response['y'], expected_index=PASSIVE_ROWS + i)
    for i in range(ACTIONS):
        plan = random_query(world_id, i, original_x)
        response = world.intervene('random', i, *plan)
        random_plans.append(plan)
        random_rows.append((response['x'], response['y']))
        random.observe(response['x'], response['y'], expected_index=PASSIVE_ROWS + i)
    cpu_actions = time.process_time_ns() - cpu_actions_start
    for i, (x, _) in enumerate(active_rows):
        # Fixed cyclic mismatch; negative control, not an information-matched comparator.
        shuffled.observe(x, active_rows[(i + 1) % ACTIONS][1], expected_index=PASSIVE_ROWS + i)
    active_source = source + tuple(active_rows)
    t = time.process_time_ns()
    symbolic = SymbolicInducer(active_source)
    passive_symbolic = SymbolicInducer(source)
    symbolic_cpu = time.process_time_ns() - t
    t = time.process_time_ns()
    poly = PolynomialGradient(active_source)
    poly_cpu = time.process_time_ns() - t
    t = time.process_time_ns()
    neural = TanhGradient(active_source, world_id)
    neural_cpu = time.process_time_ns() - t
    targets = world.heldout()
    preds = {
        'direct_active': tuple(direct.predict(q) for q in targets),
        'direct_random': tuple(random.predict(q) for q in targets),
        'passive_only': tuple(passive_predict(passive_only,q) for q in targets),
        'symbolic': tuple(symbolic.predict(q) for q in targets),
        'polynomial_gradient': tuple(poly.predict(q) for q in targets),
        'tanh_neural': tuple(neural.predict(q) for q in targets),
        'shuffled_effect': tuple(shuffled.predict(q) for q in targets),
        'no_edit': tuple((0,) * N for _ in targets),
    }
    snap = direct.snapshot()
    cold = DirectWeights.restore(snap)
    exact_cold = cold.snapshot() == snap and tuple(cold.predict(x) for x in targets) == preds['direct_active']
    forged = json.loads(snap)
    forged['data']['w'][0][0] += 1
    rejected_tamper = False
    try: DirectWeights.restore(canonical(forged))
    except ValueError: rejected_tamper = True
    rejected_replay = False
    try: direct.observe(*active_rows[0], expected_index=PASSIVE_ROWS+ACTIONS)
    except ValueError: rejected_replay = True
    unknown_refused = direct.predict((7, 0, 0, 0, 0, 0)) is None
    target_hash = digest(targets)
    pred_hash = digest({'source': source_sha, 'active_plans': active_plans,
                        'random_plans': random_plans, 'active_rows': digest(active_rows),
                        'random_rows': digest(random_rows), 'targets': target_hash,
                        'predictions': preds, 'memory': digest(snap)})
    # Evaluator-only truth and identifiability labels accessed only after pre-score hash.
    true = world.score_after_prediction_freeze(targets)
    identifiable_active = sum(sum(symbolic.identifiable(x)) for x in targets)
    identifiable_passive = sum(sum(passive_symbolic.identifiable(x)) for x in targets)
    counts = {method: sum(a == b for guess, truth in zip(preds[method], true)
                          for a, b in zip(guess, truth)) for method in METHODS}
    diagnostic = {method: sum(a == b for x, guess, truth in zip(targets, preds[method], true)
                                   if x[0] != x[1] for a,b in zip(guess,truth)) for method in METHODS}
    return {'world_id': world_id, 'queries': len(targets), 'diagnostic_queries': sum(x[0]!=x[1] for x in targets),
            'predictions_correct': counts, 'diagnostic_correct': diagnostic,
            'identifiable_active': identifiable_active, 'identifiable_passive': identifiable_passive,
            'source_sha256': source_sha, 'active_plans_sha256': digest(active_plans),
            'random_plans_sha256': digest(random_plans), 'original_targets_sha256': target_hash,
            'pre_scoring_predictions_sha256': pred_hash, 'cold_restore': exact_cold,
            'tamper_rejected': rejected_tamper, 'replay_rejected': rejected_replay,
            'unknown_refused': unknown_refused, 'source_fit': {
                'direct': sum(direct.predict(x) == y for x,y in active_source),
                'gradient': poly.train_fit, 'neural': neural.train_fit},
            'hypotheses_remaining': symbolic.ambiguity(),
            'cpu_ns': {'actions_and_selection': cpu_actions, 'symbolic': symbolic_cpu,
                       'polynomial_gradient': poly_cpu, 'tanh_neural': neural_cpu,
                       'whole_world': time.process_time_ns() - start_cpu},
            'wall_ns': time.perf_counter_ns() - start_wall,
            'memory_snapshot': snap}


def evaluate_public():
    start = time.process_time_ns()
    worlds = []
    for world_id in PUBLIC:
        worlds.append(one_world(world_id))
    previous = worlds[0]['memory_snapshot']
    interleaved = DirectWeights.restore(previous).snapshot() == previous
    out = {'schema': 'wsp98.original-public-first-use.v1',
           'cohort': 'PUBLIC_ORIGINAL', 'world_ids': list(PUBLIC),
           'worlds': len(worlds), 'passive_rows': len(worlds)*PASSIVE_ROWS,
           'active_actions': len(worlds)*ACTIONS, 'random_actions': len(worlds)*ACTIONS,
           'queries': sum(w['queries'] for w in worlds),
           'diagnostic_queries': sum(w['diagnostic_queries'] for w in worlds),
           'identifiable_active': sum(w['identifiable_active'] for w in worlds),
           'identifiable_passive': sum(w['identifiable_passive'] for w in worlds),
           'correct': {m: sum(w['predictions_correct'][m] for w in worlds) for m in METHODS},
           'diagnostic_correct': {m: sum(w['diagnostic_correct'][m] for w in worlds) for m in METHODS},
           'cold_restores': sum(w['cold_restore'] for w in worlds),
           'tamper_rejections': sum(w['tamper_rejected'] for w in worlds),
           'replay_rejections': sum(w['replay_rejected'] for w in worlds),
           'unknown_refusals': sum(w['unknown_refused'] for w in worlds),
           'interleaved_memory': interleaved, 'source_fit': {m: sum(w['source_fit'][m] for w in worlds) for m in ('direct','gradient','neural')},
           'cpu_ns': {'whole_process': time.process_time_ns()-start,
                      **{m: sum(w['cpu_ns'][m] for w in worlds) for m in worlds[0]['cpu_ns']}},
           'wall_ns': sum(w['wall_ns'] for w in worlds),
           'receipts': [{k: w[k] for k in ('world_id','source_sha256','active_plans_sha256','random_plans_sha256',
                         'original_targets_sha256','pre_scoring_predictions_sha256','hypotheses_remaining')}
                        for w in worlds]}
    for w in worlds: del w['memory_snapshot']
    return classify(out)


def classify(r):
    total = r['queries']*N
    coverage = r['identifiable_active']/total
    diff = (r['identifiable_active']-r['identifiable_passive'])/total
    valid = r['worlds'] == 20 and r['queries'] == 400 and r['passive_rows'] == 480 and r['active_actions'] == 160 and r['random_actions'] == 160 and r['diagnostic_queries'] >= 200 and coverage >= .25 and diff >= .10
    accuracy = r['correct']['direct_active']/total
    advantage_passive = (r['correct']['direct_active']-r['correct']['passive_only'])/total
    advantage_random = (r['correct']['direct_active']-r['correct']['direct_random'])/total
    integrity = r['cold_restores'] == 20 and r['tamper_rejections'] == 20 and r['replay_rejections'] == 20 and r['unknown_refusals'] == 20 and r['interleaved_memory']
    positive = valid and integrity and accuracy >= .80 and advantage_passive >= .05 and advantage_random >= .03
    r['classification'] = ('INVALID_UNINFORMATIVE' if not valid else
                           'INVALID_CUSTODY' if not integrity else
                           'PUBLIC_FEASIBLE' if positive else 'SCIENTIFIC_NEGATIVE_OR_MIXED')
    r['checks'] = {'identifiable_opportunity': valid, 'custody': integrity,
                   'candidate_accuracy': accuracy >= .80,
                   'active_vs_passive': advantage_passive >= .05,
                   'active_vs_random': advantage_random >= .03}
    r['science_superiority'] = 'UNVERIFIED'
    r['reserved_untouched'] = True
    r['cost_parity'] = 'UNVERIFIED'
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--public-only', action='store_true', required=True)
    args = ap.parse_args()
    result = evaluate_public()
    print('WSP98_PUBLIC_RESULT=' + canonical(result), flush=True)

if __name__ == '__main__': main()
