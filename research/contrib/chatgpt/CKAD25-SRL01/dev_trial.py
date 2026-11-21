"""SRL01 frozen synthetic development test of source-witnessed shared risk.

Original-world first-use: NONE. Exactly three past worlds are observed by each
policy, two actions per world. All target outcomes are evaluator-only; no
policy is allowed to update from target evaluation labels.
"""
from __future__ import annotations

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import platform
import sys
from statistics import mean

from yggdrasil.native_shared_fault_risk import (NativeSharedFaultRisk,
    independent_beta_risks, Q_GRID)

STATIONARY_SEEDS = tuple(530001 + 37*i for i in range(48))
NEGATIVE_SEEDS = tuple(540001 + 41*i for i in range(24))
MASKS = tuple(range(4))
TRAIN_WORLDS = 3
TARGET_WORLDS = 32
ARMS = ('native_beta', 'conventional_beta', 'learned_shared_risk',
        'independent_exact_joint_bayes', 'dirichlet_positives',
        'beta_trailing_2', 'fixed', 'random')
SOURCE_SHA = '655f13033c7ce8e9699af697437fcb9bd5a06f1e'


def h(tag, *parts):
    value = json.dumps(['CKAD25-SRL01', tag, *parts], separators=(',',':'),
                       ensure_ascii=True).encode('ascii')
    return int.from_bytes(sha256(value).digest()[:8], 'big')


def world(seed, world_index, *, negative):
    hot = h('nhot', seed, world_index) % 4 if negative else h('hot', seed) % 4
    # Frozen categorical single-defect generator. Hidden hot & q never sent to arms.
    roll = h('fault', seed, world_index) % (2**56)
    if roll < 3 * (2**56) // 4:
        fault = hot
    else:
        other = [x for x in MASKS if x != hot]
        fault = other[h('other', seed, world_index) % 3]
    return tuple(int(mask == fault) for mask in MASKS)


def training_history(seed, *, negative):
    result = []
    for index in range(TRAIN_WORLDS):
        truth = world(seed, index, negative=negative)
        order = sorted(MASKS, key=lambda mask:(h('probe', seed,index,mask),mask))
        result.append(tuple((mask, truth[mask]) for mask in order[:2]))
    return tuple(result)


def independent_exact_joint(history):
    # Independent conventional Bayes, no import of candidate training method.
    states = []
    for hot in MASKS:
        for rate in (F(1,4), F(1,2), F(3,4), F(9,10)):
            likelihood = F(1,16)
            for observed in history:
                obs = dict(observed)
                yes = [a for a,v in observed if v == 1]
                if len(yes) > 1:
                    raise ValueError('EXCLUSIVE_FAULT_VIOLATION')
                if yes:
                    p = rate if hot == yes[0] else (1-rate)/3
                else:
                    p = sum((rate if hot==a else (1-rate)/3)
                            for a in MASKS if a not in obs)
                likelihood *= p
            states.append((hot, rate, likelihood))
    denom = sum((w for _,_,w in states), F(0))
    if denom <= 0:
        raise ValueError('INDEPENDENT_POSTERIOR_ZERO')
    return tuple(sum((w/denom * (q if hot == a else (1-q)/3)
                      for hot,q,w in states), F(0)) for a in MASKS)


def to_categorical(values):
    full = sum(values, F(0))
    if full == 0: return (F(1,4),)*4
    return tuple(x/full for x in values)


def dirichlet_positives(history):
    # Fully fitted conventional one-hot categorical frequency with Laplace 1.
    hits = [sum(value for w in history for addr,value in w if addr==a)
            for a in MASKS]
    return to_categorical(tuple(F(1+n) for n in hits))


def select(probs):
    return tuple(sorted(MASKS, key=lambda a:(-probs[a],a))[:2])


def fitted(seed, *, negative=False):
    history = training_history(seed, negative=negative)
    candidate = NativeSharedFaultRisk(MASKS, history)
    # Cold rederive from the exact saved historical rows, not from a hidden label.
    cold = NativeSharedFaultRisk(MASKS, json.loads(json.dumps(history)))
    if cold.checkpoint_fingerprint() != candidate.checkpoint_fingerprint():
        raise RuntimeError('COLD_SOURCE_REPLAY_MISMATCH')
    evidence = json.dumps(history, separators=(',',':'), ensure_ascii=True).encode('ascii')
    pin = sha256(evidence).hexdigest()
    exact = independent_exact_joint(history)
    if candidate.risks != exact:
        raise RuntimeError('INDEPENDENT_TRAINED_BAYES_PARITY_FAIL')
    beta = tuple(independent_beta_risks(MASKS,history)[a] for a in MASKS)
    rolling = tuple(independent_beta_risks(MASKS,history,trailing_worlds=2)[a]
                    for a in MASKS)
    predictions = {
        'native_beta':to_categorical(beta),
        'conventional_beta':to_categorical(beta),
        'learned_shared_risk':candidate.risks,
        'independent_exact_joint_bayes':exact,
        'dirichlet_positives':dirichlet_positives(history),
        'beta_trailing_2':to_categorical(rolling),
        'fixed':to_categorical(beta),
        'random':to_categorical(beta),
    }
    decisions = {k:select(v) for k,v in predictions.items()}
    decisions['fixed'] = (0,1)
    decisions['random'] = tuple(sorted(sorted(MASKS,
              key=lambda a:(h('random_action',seed,a),a))[:2]))
    # Only model-visible public evidence persisted: no hot, unseen role or truth.
    receipt = {'seed':seed,'source_history_sha256':pin,
        'source_history':[[list(x) for x in row] for row in history],
        'checkpoint_cold_parity':True,
        'selected':{k:list(v) for k,v in decisions.items()},
        'forecast':{k:[str(x) for x in v] for k,v in predictions.items()}}
    return receipt,predictions,decisions


def score(seed, *, negative):
    source,predictions,decisions = fitted(seed,negative=negative)
    results={k:{'detections':0,'squared_error':F(0),'target_actions':0}
             for k in ARMS}
    target_hash=sha256()
    for i in range(TRAIN_WORLDS,TRAIN_WORLDS+TARGET_WORLDS):
        truth = world(seed,i,negative=negative)
        target_hash.update(bytes(truth))
        for k in ARMS:
            selected = decisions[k]
            p = predictions[k]
            if len(selected)!=2 or len(set(selected))!=2:
                raise RuntimeError('UNEQUAL_TARGET_ACTIONS')
            results[k]['detections'] += int(any(truth[a] for a in selected))
            results[k]['squared_error'] += sum(((q-y)**2 for q,y in zip(p,truth)),F(0))/4
            results[k]['target_actions'] += 2
    source['target_hash_evaluator_only']=target_hash.hexdigest()
    source['synthetic_negative_no_stable_role']=negative
    source['source_history_witness_actions']=6
    source['score']={k:{'detected':r['detections'], 'brier':float(r['squared_error']/TARGET_WORLDS),
                         'charged_target_actions':r['target_actions']}
                      for k,r in results.items()}
    source['score_exact_fraction']={k:{'brier':str(r['squared_error']/TARGET_WORLDS)}
                                    for k,r in results.items()}
    return source


def aggregate(rows):
    n = len(rows)*TARGET_WORLDS
    return {arm:{'detected':sum(s['score'][arm]['detected'] for s in rows),
                 'detection_rate':sum(s['score'][arm]['detected'] for s in rows)/n,
                 'mean_brier':mean(s['score'][arm]['brier'] for s in rows),
                 'charged_actions':sum(s['score'][arm]['charged_target_actions'] for s in rows)}
            for arm in ARMS}


def evaluate():
    stationary=[score(seed,negative=False) for seed in STATIONARY_SEEDS]
    negative=[score(seed,negative=True) for seed in NEGATIVE_SEEDS]
    positive_agg=aggregate(stationary)
    negative_agg=aggregate(negative)
    a=positive_agg['learned_shared_risk']
    b=positive_agg['native_beta']
    fixed=positive_agg['fixed']
    null_a=negative_agg['learned_shared_risk']
    null_b=negative_agg['native_beta']
    targets=['learned_shared_risk','independent_exact_joint_bayes']
    parity=all(s['selected'][targets[0]]==s['selected'][targets[1]] and
           s['forecast'][targets[0]]==s['forecast'][targets[1]] for s in stationary+negative)
    gates={
      'source_evidence_action_budget_and_cold_parity': all(s['checkpoint_cold_parity']
          and s['source_history_witness_actions']==6 and
          all(v['charged_target_actions']==64 for v in s['score'].values())
          for s in stationary+negative),
      'independent_fully_trained_exact_bayes_parity':parity,
      'detection_over_native_beta_ge_0_020':a['detection_rate']-b['detection_rate']>=.020-1e-12,
      'detection_over_fixed_ge_0_020':a['detection_rate']-fixed['detection_rate']>=.020-1e-12,
      'brier_over_beta_ge_0_010':b['mean_brier']-a['mean_brier']>=.010-1e-12,
      'no_mapping_negative_brier_noninferior_0_020':null_a['mean_brier']-null_b['mean_brier']<=.020+1e-12,
    }
    return {
      'schema':'yggdrasil.ckad25.srl01.dev-result.v1',
      'parent':SOURCE_SHA,
      'source_free_dev':True,'scientific_gain_verified':False,
      'source_first_use':'NONE','native_true_checkpoint':'NOT_RUN',
      'controls_fully_matched':True,'consumed_primary_trials':1,
      'stationary_seeds':list(STATIONARY_SEEDS),'negative_seeds':list(NEGATIVE_SEEDS),
      'witnessed_train_actions':len(stationary+negative)*6,
      'evaluated_target_action_budget_per_arm':len(stationary+negative)*TARGET_WORLDS*2,
      'stationary':positive_agg,'negative_no_stable_mapping':negative_agg,
      'gates':gates,
      'classification':'DEV_GO_FOCUSED_ONLY' if all(gates.values()) else 'DEV_NO_GO',
      'per_seed_stationary':stationary,'per_seed_negative':negative,
      'runtime':{'python':sys.version.split()[0],'platform':platform.platform()},
      'native_cpu_ratio':'UNVERIFIED','full_linux_windows_regression':'NOT_RUN',
    }

if __name__=='__main__':print(json.dumps(evaluate(),sort_keys=True,indent=2))
