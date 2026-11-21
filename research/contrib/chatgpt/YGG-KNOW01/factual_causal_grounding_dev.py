"""KNOW11: witnessed-intervention development over grounded synthetic Q/P/Q facts.

Source-free synthetic only; original 21M historical TRAIN image is read-only.
The candidate is an isolated NativeContextBasis (not Amalgam's owner model).
Q/P/Q facts supply typed PUBLIC context, never counterfactual/outcome labels.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time

SEEDS = (101, 202, 303)
PHASE_P = (910, 911)
SUBJECT_BASE = 4_200_000_000
OBJECT_BASE = 4_201_000_000
ROWS_PER_WORLD = 64
FIT_ROWS = 32
SOURCE_ROWS = 21_343_681
IMAGE_SHA = '6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1'
JOINT_SHA = '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8'

def require(ok, name):
    if not ok:
        raise AssertionError('YGG_KNOW11_'+name)

def canonical(document):
    return json.dumps(document, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def modes(seed, phase):
    require(type(seed) is int and seed in SEEDS and phase in (0, 1), 'FROZEN_COHORT')
    roster = [0] * 32 + [1] * 32
    random.Random(seed * 100 + phase).shuffle(roster)
    return tuple(roster)

def subject(seed_index, entity):
    return SUBJECT_BASE + seed_index * 1000 + entity

def object_id(phase, mode):
    return OBJECT_BASE + phase * 10 + mode

def expected_outcome(phase, mode, action):
    require(all(type(x) is int and x in (0, 1) for x in (phase, mode, action)),
            'ACTION_OUTCOME_DOMAIN')
    return int(action == mode) if phase == 0 else int(action != mode)

def fixture_bundle(seed, seed_index, phase):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    facts = [[subject(seed_index, entity), PHASE_P[phase],
              object_id(phase, mode), f's{seed}:p{phase}:e{entity:03d}']
             for entity, mode in enumerate(modes(seed, phase))]
    require(len(facts) == ROWS_PER_WORLD, 'FIXTURE_ROW_COUNT')
    return canonical({'schema': BUNDLE_SCHEMA,
                      'source_id': f'know11-synthetic-{seed}-phase-{phase}',
                      'source_kind': 'direct_public_observation',
                      'source_mode': 'engineering_fixture_only',
                      'records': sorted(facts, key=lambda row: row[3])})

def witnessed_context(facts, entity_q, predicate):
    """Read direct member identities, never inferred 2-hop path or source label."""
    require(type(entity_q) is int and type(predicate) is int, 'QPQ_QUERY_TYPE')
    require(predicate in PHASE_P, 'QPQ_UNQUALIFIED_PREDICATE')
    phase = PHASE_P.index(predicate)
    statuses = [facts.fact(entity_q, predicate, object_id(phase, m))
                for m in (0, 1)]
    witnessed = [s.get('classification') == 'DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED'
                 and s.get('witnessed') is True
                 and s.get('native_accepted') is False
                 and s.get('can_write_causal_consequence') is False
                 for s in statuses]
    # Fail closed on an ambiguous, unverified, or unknown fact.
    return witnessed.index(True) if witnessed.count(True) == 1 else None

def disclosed_interventions(facts, seed, seed_index, phase):
    """Separate witnessed synthetic action/outcome source, FIT entities only."""
    observed = modes(seed, phase)
    result = []
    for entity in range(FIT_ROWS):
        q = subject(seed_index, entity)
        known = witnessed_context(facts, q, PHASE_P[phase])
        require(known == observed[entity], 'INPUT_FACT_GROUNDING')
        for action in (0, 1):
            result.append([known, action,
                           expected_outcome(phase, observed[entity], action)])
    require(len(result) == 2*FIT_ROWS and set((r[0],r[1]) for r in result)
            == {(0,0),(0,1),(1,0),(1,1)}, 'INTERVENTION_SUPPORT')
    return result

def exact_symbolic_fit(rows):
    # An independent conditional counts model with the same witnessed rows.
    counts = {}
    for mode, action, reward in rows:
        counts.setdefault((mode, action), [0, 0])[reward] += 1
    return {k: Fraction(v[1], sum(v)) for k, v in counts.items()}

def conventional_tree_fit(rows):
    """Exhaustively fit a conventional complete depth-2 binary feature tree.

    Searches both root feature orders and learns every leaf from outcome counts.
    No label is supplied by the graph; only public action/outcome witnesses.
    """
    choices = []
    for root in (0, 1):
        second = 1 - root
        branches = {}
        loss = Fraction(0)
        for first_value in (0, 1):
            leaves = {}
            for second_value in (0, 1):
                outcomes = [r[2] for r in rows if r[root] == first_value
                            and r[second] == second_value]
                require(len(outcomes)>0, 'TREE_TRAIN_LEAF_MISSING')
                fitted = Fraction(sum(outcomes), len(outcomes))
                loss += sum((fitted-y)**2 for y in outcomes)
                leaves[second_value] = fitted
            branches[first_value] = leaves
        choices.append((loss, root, branches))
    _, root, branches = min(choices, key=lambda x: (x[0], x[1]))
    return lambda mode, action: branches[(mode, action)[root]][(mode, action)[1-root]]

def blind_fit(rows):
    counts = {action:[0,0] for action in (0,1)}
    for _mode, action, reward in rows:
        counts[action][reward] += 1
    return {action:Fraction(count[1],sum(count)) for action, count in counts.items()}

def score(facts, seed, seed_index, phase, native, address, symbolic,
          conventional, blind):
    outcomes = {'native':Fraction(0),'symbolic':Fraction(0),
                'conventional':Fraction(0),'blind':Fraction(0),'facts_only':Fraction(0)}
    decisions = {key:0 for key in outcomes}
    readouts = []
    witnesses = modes(seed, phase)
    for entity in range(FIT_ROWS, ROWS_PER_WORLD):
        q = subject(seed_index, entity)
        mode = witnessed_context(facts, q, PHASE_P[phase])
        require(mode == witnesses[entity], 'HELD_SOURCE_GROUNDING')
        predictions = {}
        for action in (0,1):
            prediction = native.predict(address, mode, action)
            require(type(prediction) is int and prediction in (0,1),
                    'NATIVE_UNSUPPORTED_HELD')
            values = {
                'native': Fraction(prediction),
                'symbolic': symbolic[(mode, action)],
                'conventional': conventional(mode, action),
                'blind': blind[action],
                'facts_only': Fraction(1,2),
            }
            reward = expected_outcome(phase, witnesses[entity], action)
            for arm, prob in values.items():
                require(0 <= prob <= 1, 'INVALID_PROBABILITY')
                outcomes[arm] += (prob - reward)**2
            predictions[action] = values
            readouts.append([q,mode,action,prediction])
        for arm in decisions:
            chosen = 1 if predictions[1][arm]>predictions[0][arm] else 0
            decisions[arm] += expected_outcome(phase, witnesses[entity], chosen)
    return {'readouts_sha256':digest(canonical(readouts)),
            'readout_count':len(readouts),
            'brier':{key:[(value / len(readouts)).numerator,
                           (value / len(readouts)).denominator]
                     for key,value in outcomes.items()},
            'rewards':decisions}

def fraction(value):
    return Fraction(value[0], value[1])

def prove(installed_session, joint_checkpoint):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_context_basis import canonical as native_canonical
    from yggdrasil.native_context_basis import digest as native_digest

    start=time.monotonic()
    raw=Path(joint_checkpoint).read_bytes()
    require(digest(raw)==JOINT_SHA, 'ARCHIVED_JOINT_PIN')
    with open_installed_session(installed_session) as base:
        require(len(base._weights)==PINNED_ROWS==SOURCE_ROWS
                and PINNED_PACKED_SHA==IMAGE_SHA, 'HISTORICAL_FULL_SOURCE')
        first,last=(tuple(base._weights.row_at(i)) for i in (0,SOURCE_ROWS-1))
        require(base.fact(*first)['witnessed'] and base.fact(*last)['witnessed'],
                'HISTORICAL_EDGE_SOURCE')
        initial = CumulativeNativeFacts(base)
        initial_bytes=initial.checkpoint()
        staged=initial
        trial=[]
        prior_seen=[]
        synthetic_actions=0
        for i,seed in enumerate(SEEDS):
            native=NativeContextBasis(context_bits=1)
            staged_checkpoints=[]
            before_A=None
            result={}
            for phase in (0,1):
                candidate_raw=fixture_bundle(seed,i,phase)
                require(len(candidate_raw)<=196608, 'SOURCE_BUNDLE_BUDGET')
                for entity,mode in enumerate(modes(seed,phase)):
                    s=subject(i,entity)
                    require(not base.fact(s, PHASE_P[phase],
                                          object_id(phase, mode))['witnessed'],
                            'HISTORICAL_SOURCE_COLLISION')
                staged, receipt=staged.stage(candidate_raw, digest(candidate_raw))
                require(receipt['new_unique_facts']==64, 'CUMULATIVE_ADD')
                staged_checkpoints.append(staged.checkpoint_sha256)
                rows=disclosed_interventions(staged,seed,i,phase)
                synthetic_actions+=len(rows)
                native=native.stage_fit(phase, rows, native_digest(native_canonical(rows)),
                                        max_degree=1)
                symbolic=exact_symbolic_fit(rows)
                conventional=conventional_tree_fit(rows)
                blind=blind_fit(rows)
                metrics=score(staged,seed,i,phase,native,phase,symbolic,
                              conventional,blind)
                result['AB'[phase]]=metrics
                if phase==0:
                    before_A=metrics['readouts_sha256']
                    a_checkpoint=native.checkpoint()
                else:
                    # No refit at the previous slot. Evaluate old A with its own
                    # source facts and identical controls after B's update.
                    old_rows=disclosed_interventions(staged,seed,i,0)
                    returned=score(staged,seed,i,0,native,0,
                                   exact_symbolic_fit(old_rows),
                                   conventional_tree_fit(old_rows),
                                   blind_fit(old_rows))
                    require(returned['readouts_sha256']==before_A,
                            'FAMILIAR_RETURN_FORGETTING')
                    require(native.checkpoint()!=a_checkpoint,
                            'B_NOT_LEARNED')
                    result['A_return_sha256']=returned['readouts_sha256']
            stored=native.checkpoint()
            cold=NativeContextBasis.restore(stored,native_digest(stored))
            require(cold.checkpoint()==stored, 'NATIVE_BASIS_COLD_REPLAY')
            for phase in (0,1):
                rows=disclosed_interventions(staged,seed,i,phase)
                ret=score(staged,seed,i,phase,cold,phase,
                          exact_symbolic_fit(rows),conventional_tree_fit(rows),
                          blind_fit(rows))
                require(ret==result['AB'[phase]], 'COLD_HELD_READOUT_CHANGE')
            require(staged.checkpoint_sha256==staged_checkpoints[-1],
                    'FACTS_QUIET_CHECKPOINT')
            trial.append({'seed':seed,'phases':result,
                          'native_candidate_sha256':native_digest(stored),
                          'candidate_factual_sha256':staged.checkpoint_sha256})
            prior_seen.extend([i])
        restored=CumulativeNativeFacts(base,staged.checkpoint(),
                                     checkpoint_sha256=staged.checkpoint_sha256)
        require(restored.checkpoint()==staged.checkpoint(), 'FACTS_COLD_REPLAY')
        for i, seed in enumerate(SEEDS):
            for phase in (0,1):
                for entity,mode in enumerate(modes(seed,phase)):
                    require(witnessed_context(restored,subject(i,entity),
                                              PHASE_P[phase])==mode,
                            'COLD_TRANSFER_FACT_LOST')
        require(initial.checkpoint()==initial_bytes
                and base.fact(*first)['witnessed'] and base.fact(*last)['witnessed']
                and digest(Path(joint_checkpoint).read_bytes())==JOINT_SHA,
                'HISTORICAL_OR_AMALGAM_MUTATED')
        totals={arm:Fraction(0) for arm in ('native','symbolic','conventional','blind','facts_only')}
        reward_totals={arm:0 for arm in totals}
        for item in trial:
            for phase in ('A','B'):
                block=item['phases'][phase]
                for arm in totals:
                    totals[arm]+=fraction(block['brier'][arm])
                    reward_totals[arm]+=block['rewards'][arm]
        # Two tasks across three seeds, each scored on exactly 64 public actions.
        mean={arm:[(val/6).numerator,(val/6).denominator] for arm,val in totals.items()}
        require(all(fraction(mean[k])==0 for k in ('native','symbolic','conventional')),
                'MATCHED_FITTED_CONTROL_PARITY')
        require(fraction(mean['native'])<fraction(mean['blind']),
                'NO_GROUNDED_DEVELOPMENT_SIGNAL')
        require(all(item['phases']['A']['readouts_sha256']==
                    item['phases']['A_return_sha256'] for item in trial),
                'OLD_TASK_RETENTION_LOSS')
        advantage=min(fraction(mean[x]) - fraction(mean['native'])
                      for x in ('symbolic','conventional'))
        scientific_gain = advantage >= Fraction(1,100)
        return {'schema':'yggdrasil.know11.factual-witness-grounding-dev-result.v1',
                'classification':'SOURCE_FREE_SYNTHETIC_DEVELOPMENT',
                'frozen_protocol_seeds':list(SEEDS),
                'historical_train_rows':SOURCE_ROWS,'historical_image_sha256':IMAGE_SHA,
                'archived_amalgam_joint_unchanged_sha256':JOINT_SHA,
                'candidate_new_synthetic_QPQ_facts':len(SEEDS)*2*ROWS_PER_WORLD,
                'training_witnessed_synthetic_interventions':synthetic_actions,
                'held_cold_entities':len(SEEDS)*2*(ROWS_PER_WORLD-FIT_ROWS),
                'held_action_outcomes':len(SEEDS)*2*(ROWS_PER_WORLD-FIT_ROWS)*2,
                'mean_held_brier_fraction':mean,
                'held_correct_action_rewards':reward_totals,
                'familiar_old_A_readouts_changed':0,
                'original_historical_facts_retained':True,
                'factual_and_native_development_cold_restore':True,
                'equal_information_symbolic_and_tree_tie':True,
                'factual_QPQ_alone_never_classified_as_causal_witness':True,
                'frozen_scientific_gain_over_strongest_control':scientific_gain,
                'scientific_pass':False,
                'development_decision':'DEV_NO_GO_STRONGEST_CONTROL_TIE',
                'real_world_knowledge_learned':0,
                'canonical_amalgam_model_training':False,
                'owner_accepted_checkpoint':'UNVERIFIED',
                'deployment':'NONE',
                'seed_receipts':trial,
                'wall_seconds_excluding_download':round(time.monotonic()-start,6)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--installed-session',required=True,type=Path)
    p.add_argument('--joint-checkpoint',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    x=p.parse_args()
    result=prove(x.installed_session,x.joint_checkpoint)
    x.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('KNOW11_FROZEN_GROUNDING_DEV='+json.dumps({
        'mean_held_brier_fraction':result['mean_held_brier_fraction'],
        'old_readouts_changed':result['familiar_old_A_readouts_changed'],
        'scientific_pass':result['scientific_pass'],
        'decision':result['development_decision']},sort_keys=True),flush=True)

if __name__=='__main__':
    main()
