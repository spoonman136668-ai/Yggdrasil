"""LR-92AB: one-shot, independently seeded external synthetic development test.

This is NOT Yggdrasil native training or accepted science. Commit prereg.json
and this file to GitHub BEFORE running the primary cohort.
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys, time
import numpy as np
from scipy.special import logsumexp
from scipy.stats import binom
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / 'prereg.json'
OUTPUT = HERE / 'result.json'
TABLES = np.array([[i >> j & 1 for j in range(4)] for i in range(16)], dtype=np.uint8)
STEPS = (36, 48, 72, 96, 120, 144)
NOISE = .35

def sha(b): return hashlib.sha256(b).hexdigest()

def balanced(rng, n):
    states = np.tile(np.arange(4, dtype=np.int64), n // 4)
    for offset in range(0, n, 4): rng.shuffle(states[offset:offset + 4])
    return states

def world(rng, group):
    fit_s, val_s = balanced(rng, 144), balanced(rng, 288)
    if group in ('stationary', 'switch', 'foreign'):
        a = int(rng.integers(16))
    else: a = None
    if group == 'stationary':
        b = None
        fit_y = TABLES[a, fit_s] ^ (rng.random(144) < NOISE).astype(np.uint8)
        val_y = TABLES[a, val_s] ^ (rng.random(288) < NOISE).astype(np.uint8)
    elif group == 'switch':
        choices = [i for i in range(16) if np.count_nonzero(TABLES[a] != TABLES[i]) >= 2]
        b = int(rng.choice(choices))
        fit_y = np.r_[TABLES[a, fit_s[:72]] ^ (rng.random(72) < NOISE).astype(np.uint8),
                      TABLES[b, fit_s[72:]] ^ (rng.random(72) < NOISE).astype(np.uint8)]
        val_y = TABLES[b, val_s] ^ (rng.random(288) < NOISE).astype(np.uint8)
    elif group == 'foreign':
        b = None
        fit_y = TABLES[a, fit_s] ^ rng.integers(0, 2, 144, dtype=np.uint8) ^ (rng.random(144) < NOISE).astype(np.uint8)
        val_y = TABLES[a, val_s] ^ rng.integers(0, 2, 288, dtype=np.uint8) ^ (rng.random(288) < NOISE).astype(np.uint8)
    else:
        b = None
        fit_y = rng.integers(0, 2, 144, dtype=np.uint8)
        val_y = rng.integers(0, 2, 288, dtype=np.uint8)
    return fit_s, fit_y, val_s, val_y, a, b

def posterior(prior, states, labels):
    match = (TABLES[:, states] == labels[None, :])
    likelihood = np.where(match, math.log1p(-NOISE), math.log(NOISE)).sum(axis=1)
    log_scores = np.log(prior) + likelihood
    return np.exp(log_scores - logsumexp(log_scores)), float(logsumexp(log_scores))

def fit_bayes(prior, states, labels):
    p, _ = posterior(prior, states, labels)
    ix = int(np.argmax(p))
    return TABLES[ix].tolist(), float(p[ix]), ix

def misfit(table, states, labels):
    return float(binom.sf(np.count_nonzero(np.asarray(table, dtype=np.uint8)[states] != labels)-1, len(states), NOISE))

def assess(table, conf, states, labels, group, truth):
    val_p = misfit(table, states, labels)
    accepted = (conf is None or conf >= .90) and val_p > .01
    exact = group == 'stationary' and accepted and table == TABLES[truth].tolist()
    return {'accepted': bool(accepted), 'exact': bool(exact), 'false': bool(accepted and not exact),
            'validation_p': val_p,
            'validation_accuracy': float(np.mean(np.asarray(table, dtype=np.uint8)[states] == labels))}

def classical(kind, states, labels):
    x = np.c_[states & 1, (states >> 1) & 1]
    model = (DecisionTreeClassifier(max_depth=2, random_state=92) if kind == 'CART'
             else RandomForestClassifier(n_estimators=16, max_depth=3, random_state=92, n_jobs=1))
    model.fit(x, labels)
    return model.predict(np.array([[s & 1, (s >> 1) & 1] for s in range(4)])).astype(int).tolist()

def summarize(rows, arm):
    vals = [r['results'][arm] for r in rows]
    return {'stationary_exact': sum(r['results'][arm]['exact'] for r in rows if r['group']=='stationary'),
            'false_constructions': sum(v['false'] for v in vals),
            'foreign_null_accept': sum(r['results'][arm]['accepted'] for r in rows if r['group'] in ('foreign','null')),
            'accepted': sum(v['accepted'] for v in vals),
            'validation_accuracy': float(np.mean([v['validation_accuracy'] for v in vals])),
            'n_fit': 144*len(rows), 'n_validation': 288*len(rows)}

def main():
    if OUTPUT.exists(): raise RuntimeError('Primary result already exists: no rerun or overwrite')
    pr = json.loads(PROTOCOL.read_text())
    assert pr['schema'] == 'yggdrasil.external-research-prereg.v1'
    assert pr['experiment_id'] == 'LR-92AB'
    assert pr['frozen_design']['seeds'] == [929200201]
    prior = np.asarray(pr['memory_input']['prior_distribution'], dtype=np.float64)
    assert prior.shape == (16,) and np.all(prior > 0) and abs(prior.sum()-1) < 1e-12
    assert sha(prior.tobytes()) == pr['memory_input']['prior_float64_sha256']
    assert sha(pathlib.Path(__file__).read_bytes()) == pr['code_sha256']
    assert pr['cohort'] == {'stationary':52, 'switch':12, 'foreign':8, 'null':8}
    assert pr['frozen_design']['data_budget'] == '144 fit + 288 validation per world, 80 worlds'
    rng = np.random.default_rng(929200201)
    groups = sum(([k]*n for k,n in pr['cohort'].items()), [])
    rng.shuffle(groups)
    uniform = np.ones(16, dtype=np.float64)/16
    scrambled = prior[::-1].copy()
    coin = np.random.default_rng(929290201)
    rows, cost_ns = [], {}
    for i, group in enumerate(groups):
        fit_s, fit_y, val_s, val_y, a, b = world(rng, group)
        _, ev_mem = posterior(prior, fit_s[:36], fit_y[:36])
        _, ev_uni = posterior(uniform, fit_s[:36], fit_y[:36])
        # Frozen likelihood-ratio gate; never sees validation labels.
        select_memory = ev_mem - ev_uni >= math.log(2.0)
        rnd_mem = bool(coin.integers(2))
        policies = {'fixed_memory': prior, 'fixed_uniform':uniform, 'fixed_scrambled':scrambled,
                    'evidence_gate': prior if select_memory else uniform,
                    'random_gate': prior if rnd_mem else uniform}
        scores, chosen = {}, {}
        for name, p in policies.items():
            t = time.process_time_ns()
            table, conf, ix = fit_bayes(p, fit_s, fit_y)
            cost_ns[name] = cost_ns.get(name, 0) + time.process_time_ns()-t
            scores[name] = assess(table, conf, val_s, val_y, group, a)
            chosen[name] = {'table': table, 'posterior':conf, 'hypothesis':ix}
        for name in ('CART', 'RF16'):
            t = time.process_time_ns(); table = classical(name, fit_s, fit_y)
            cost_ns[name] = cost_ns.get(name, 0)+time.process_time_ns()-t
            scores[name] = assess(table, None, val_s, val_y, group, a)
            chosen[name] = {'table':table, 'posterior':None, 'hypothesis':None}
        rows.append({'id':i,'group':group,'truth_table':a if group=='stationary' else None,
                     'switch_table':b,'fit_states':fit_s.tolist(),'fit_labels':fit_y.tolist(),
                     'valid_states':val_s.tolist(),'valid_labels':val_y.tolist(),
                     'log_bayes_factor_36':ev_mem-ev_uni,'gate_used_memory':bool(select_memory),
                     'random_used_memory':rnd_mem,'choices':chosen,'results':scores})
    names = list(rows[0]['results'])
    agg = {name: summarize(rows, name) for name in names}
    gate = agg['evidence_gate']; memory=agg['fixed_memory']; uni=agg['fixed_uniform']; random=agg['random_gate']
    checks = {'gate_exact_ge_uniform_plus_3':gate['stationary_exact']>=uni['stationary_exact']+3,
              'gate_exact_ge_memory':gate['stationary_exact']>=memory['stationary_exact'],
              'gate_false_le_uniform':gate['false_constructions']<=uni['false_constructions'],
              'gate_foreign_null_accept_zero':gate['foreign_null_accept']==0,
              'gate_exact_gt_random':gate['stationary_exact']>random['stationary_exact'],
              'gate_validation_accuracy_ge_uniform':gate['validation_accuracy']>=uni['validation_accuracy']}
    out={'schema':'lr92ab.external-synthetic-development-result.v1','prereg_sha256':sha(PROTOCOL.read_bytes()),
         'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'experiment_id':'LR-92AB',
         'scope':'external synthetic research only; no native Yggdrasil training', 'seed':929200201,
         'rows':rows,'summary':agg,'gate_uses_memory_count':sum(r['gate_used_memory'] for r in rows),
         'cpu_process_seconds_per_arm':{k:v/1e9 for k,v in cost_ns.items()},
         'go_checks':checks,'development_go':all(checks.values()),'first_use_reserved_consumed':0,
         'official_science':'NOT_QUALIFIED','deployment':'HOLD'}
    OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:out[k] for k in ('experiment_id','summary','gate_uses_memory_count','cpu_process_seconds_per_arm','go_checks','development_go')}, indent=2))

if __name__ == '__main__': main()
