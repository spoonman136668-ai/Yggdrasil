"""SFI-04 frozen structure-free relationship information limit diagnostic."""
from __future__ import annotations
from hashlib import sha256
import json
import random
import statistics
import time

from public_source import World, SEEDS, CONTEXTS, ACTIONS, public_tape
from learners import DirectWeights, ExactBayes, ShuffledCredit, NoUpdate

BUDGETS = (24, 128, 512, 1024, 2048)
BOOTSTRAP_SEED = 40415


def per_world(seed):
    world = World(seed)
    direct, bayes, shuffled, noop = DirectWeights(), ExactBayes(), ShuffledCredit(), NoUpdate()
    learners = dict(DIRECT=direct, EXACT_BAYES=bayes, SHUFFLED=shuffled, NO_UPDATE=noop)
    collected = []
    evidence = []
    results = {}
    for t, attempt in enumerate(public_tape(seed), 1):
        row = world.step(attempt.context, attempt.action)
        collected.append([row.context, row.action, row.reward,
                          [[h.context, h.action] for h in row.history]])
        for agent in learners.values():
            agent.observe(row)
        if len(row.history) == 2:
            evidence.append(row.history[0].context)
        if t in BUDGETS:
            visited = set(evidence)
            outputs = {}
            for name, agent in learners.items():
                correct = 0
                unseen_correct = 0
                for context in range(CONTEXTS):
                    hit = world.probe(context, agent.choose(context)) == 1
                    correct += hit
                    if context not in visited:
                        unseen_correct += hit
                outputs[name] = dict(correct=correct, unseen_correct=unseen_correct)
            if outputs['DIRECT'] != outputs['EXACT_BAYES']:
                raise AssertionError('SFI04_DIRECT_BAYES_NOT_EQUAL')
            results[str(t)] = dict(visited=len(visited),
                                    unvisited=CONTEXTS-len(visited),
                                    observed_upper_expected=(len(visited)+(CONTEXTS-len(visited))/ACTIONS)/CONTEXTS,
                                    outputs=outputs)
    if len(results) != len(BUDGETS):
        raise AssertionError('SFI04_CHECKPOINT_INCOMPLETE')
    return dict(seed=seed, results=results,
                direct_mask_sha256=sha256(direct.checkpoint()).hexdigest(),
                public_transcript_sha256=sha256(json.dumps(collected, separators=(',', ':')).encode()).hexdigest(),
                actual_world_steps=world.steps)


def study():
    started = time.perf_counter()
    worlds = [per_world(s) for s in SEEDS]
    means = {}
    observed = {}
    for budget in BUDGETS:
        key = str(budget)
        means[key] = {
            arm: statistics.mean(w['results'][key]['outputs'][arm]['correct']/CONTEXTS for w in worlds)
            for arm in ('DIRECT', 'EXACT_BAYES', 'SHUFFLED', 'NO_UPDATE')
        }
        observed[key] = statistics.mean(w['results'][key]['visited'] for w in worlds)
    first_unseen = sum(w['results']['24']['outputs']['DIRECT']['unseen_correct'] for w in worlds)
    first_unseen_total = sum(w['results']['24']['unvisited'] for w in worlds)
    diffs = [(w['results']['2048']['outputs']['DIRECT']['correct']-
              w['results']['2048']['outputs']['EXACT_BAYES']['correct'])/CONTEXTS for w in worlds]
    rng = random.Random(BOOTSTRAP_SEED)
    trials = sorted(statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(1000))
    upper_at24 = (22 + (CONTEXTS - 22)/ACTIONS)/CONTEXTS
    predicates = {
        'high_budget_accuracy_at_least_0_90': means['2048']['DIRECT'] >= .9,
        'high_minus_24_at_least_0_30': means['2048']['DIRECT']-means['24']['DIRECT'] >= .30,
        'unseen_24_accuracy_at_most_0_20': first_unseen/first_unseen_total <= .20,
        'exact_22_delivered_after_24': all(w['results']['24']['visited'] == 22 for w in worlds),
        'new_algorithm_strong_control_gain_gt_0_02': statistics.mean(diffs) > .02,
        'paired_lower_95_gt_0_01': trials[24] > .01,
    }
    stable = json.dumps(worlds, separators=(',', ':'), sort_keys=True).encode('ascii')
    return {
        'schema':'yggdrasil.sfi04.public-information-bound-result.v1',
        'classification':'PUBLIC_DEV_NO_FREE_LUNCH_AND_EQUAL_BAYES_NO_GO',
        'worlds':len(worlds), 'real_public_training_steps':len(worlds)*BUDGETS[-1],
        'real_readonly_scored_interventions':len(worlds)*len(BUDGETS)*4*CONTEXTS,
        'info_upper_expected_24':upper_at24,
        'first_24_unseen_accuracy':first_unseen/first_unseen_total,
        'first_24_unseen_correct':first_unseen,
        'first_24_unseen_trials':first_unseen_total,
        'means':means, 'mean_contexts_with_delivered_feedback':observed,
        'candidate_minus_bayes_2048_mean':statistics.mean(diffs),
        'paired_bootstrap_95':[trials[24],trials[975]],
        'predicates':predicates,
        'scientific_pass':False, 'protected_held_first_use':False,
        'per_world_sha256':sha256(stable).hexdigest(),
        'elapsed_seconds':time.perf_counter()-started,
        'world_results':worlds,
    }

if __name__ == '__main__':
    print(json.dumps(study(), indent=2, sort_keys=True))
