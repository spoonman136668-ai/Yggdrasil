"""YNCA-12: unlabeled two-operator causal-memory development experiment.

Only synthetic A is runnable. The disjoint B reserve is deliberately NOT implemented.
No context IDs, operator IDs, permutations or held truths enter the fitted models.
"""
import argparse
import hashlib
import itertools
import json
import math
import random
import time
import tracemalloc

ACTIONS = tuple(range(8))
PERMS = tuple(itertools.permutations(range(3)))
NOISE = .10
TRAIN_WORLDS = 32
TRAIN_REVEALED = 4
TEST_WORLDS = 64
TEST_REVEALED = 2
TOPK = 6
A_SEED = 171200


def rng(*fields):
    digest = hashlib.sha256(':'.join(map(str,fields)).encode()).digest()
    return random.Random(int.from_bytes(digest[:16], 'big'))


def bit(t, x):
    return (t >> x) & 1


def permute(x, p):
    return sum(((x >> p[i]) & 1) << i for i in range(3))


def perm_table(t, p):
    return sum(bit(t, permute(x, p)) << x for x in ACTIONS)


def vocabulary():
    reps=[]
    for t in range(256):
        orbit=[perm_table(t,p) for p in PERMS]
        if t != min(orbit) or min(t.bit_count(), 8-t.bit_count()) < 2:
            continue
        reps.append(t)
    r=rng('candidate-vocabulary-v1')
    r.shuffle(reps)
    return tuple(sorted(reps[:24]))


CANDIDATES = vocabulary()
PAIRS = tuple((a,b) for i,a in enumerate(CANDIDATES) for b in CANDIDATES[i:])


def chosen_ops():
    return tuple(rng('operator-pair',A_SEED).sample(CANDIDATES,2))


def new_world(kind, idx):
    """Return simulator-private truth and observable intervention evidence separately."""
    a,b=chosen_ops()
    r=rng('world-A',kind,idx,A_SEED)
    op=(a,b)[r.randrange(2)] if kind=='familiar' else r.choice([t for t in CANDIDATES if t not in (a,b)])
    p=r.choice(PERMS)
    actions=r.sample(ACTIONS, TRAIN_REVEALED if kind=='train' else TEST_REVEALED)
    # Training uses a deterministic interference schedule; tags are NEVER returned.
    if kind=='train':
        op=(a,b)[(idx//8)%2]
    revealed=tuple((x,bit(op,permute(x,p)) ^ int(r.random()<NOISE)) for x in actions)
    truth=tuple(bit(op,permute(x,p)) for x in ACTIONS)
    return revealed,truth


def world_likelihoods(obs):
    """Integrate the hidden input permutation with an exact six-way sum."""
    likelihoods=[]
    for t in CANDIDATES:
        weights=[]
        for p in PERMS:
            errors=sum(bit(t,permute(x,p))!=y for x,y in obs)
            weights.append((1-NOISE)**(len(obs)-errors)*NOISE**errors /len(PERMS))
        likelihoods.append(sum(weights))
    return likelihoods


def posterior(log_scores):
    hi=max(log_scores)
    exp=[math.exp(s-hi) for s in log_scores]
    denom=math.fsum(exp)
    return tuple(x/denom for x in exp)


def learn(history):
    # Both pair and single controls use precisely the same unlabeled evidence.
    by_world=[world_likelihoods(obs) for obs in history]
    log_single=[sum(math.log(v[t]) for v in by_world) for t in range(len(CANDIDATES))]
    log_pairs=[sum(math.log((v[i]+v[j])*.5) for v in by_world)
               for i,j in ((CANDIDATES.index(a),CANDIDATES.index(b)) for a,b in PAIRS)]
    pair_posterior=posterior(log_pairs)
    indices=sorted(range(len(PAIRS)),key=lambda i:(-pair_posterior[i],PAIRS[i]))[:TOPK]
    kept=tuple((PAIRS[i],pair_posterior[i]) for i in indices)
    total=math.fsum(w for _,w in kept)
    kept=tuple((pair,w/total) for pair,w in kept)
    freq_counts=[2]*8
    freq_hits=[1]*8
    for obs in history:
        for x,y in obs:
            freq_counts[x]+=1
            freq_hits[x]+=y
    return {'pair_full':pair_posterior,'single':posterior(log_single),
            'top6':kept,'frequency':(freq_hits,freq_counts),
            'last':posterior([math.log(v) for v in by_world[-1]])}


def test_components(obs):
    """Per-operator evidence and withheld noiseless conditional predictions."""
    likelihoods=[]; numerators=[]
    for t in CANDIDATES:
        weights=[]
        for p in PERMS:
            errors=sum(bit(t,permute(x,p))!=y for x,y in obs)
            weights.append((1-NOISE)**(len(obs)-errors)*NOISE**errors/len(PERMS))
        likelihoods.append(math.fsum(weights))
        numerators.append(tuple(math.fsum(w*bit(t,permute(x,p))
                                          for w,p in zip(weights,PERMS)) for x in ACTIONS))
    return likelihoods,numerators


def predict_single(post,components):
    ll,nums=components
    z=math.fsum(p*w for p,w in zip(post,ll))
    return tuple(math.fsum(p*nums[i][x] for i,p in enumerate(post))/z for x in ACTIONS)


def predict_pair(items,components):
    ll,nums=components
    lookup={t:i for i,t in enumerate(CANDIDATES)}
    mass=0.
    out=[0.]*8
    for (a,b),weight in items:
        ia,ib=lookup[a],lookup[b]
        mass+=weight*(ll[ia]+ll[ib])*.5
        for x in ACTIONS:
            out[x]+=weight*(nums[ia][x]+nums[ib][x])*.5
    return tuple(x/mass for x in out)


def pair_items(weights):
    return zip(PAIRS,weights)


def predict_frequency(freq,obs):
    h,c=(list(z) for z in freq)
    for x,y in obs:
        h[x]+=y;c[x]+=1
    return tuple(h[x]/c[x] for x in ACTIONS)


def no_memory(obs_components):
    p=(1/len(CANDIDATES),)*len(CANDIDATES)
    return predict_single(p,obs_components)


def score(kind,models):
    samples={name:[] for name in ('TOP6_PAIR','FULL_PAIR_BAYES','SINGLE_BAYES','FREQUENCY','NO_MEMORY','LAST_WORLD')}
    accuracy={name:[] for name in samples}
    for i in range(TEST_WORLDS):
        obs,truth=new_world(kind,i+10000)
        components=test_components(obs)
        predictions={
            'TOP6_PAIR':predict_pair(models['top6'],components),
            'FULL_PAIR_BAYES':predict_pair(pair_items(models['pair_full']),components),
            'SINGLE_BAYES':predict_single(models['single'],components),
            'FREQUENCY':predict_frequency(models['frequency'],obs),
            'NO_MEMORY':no_memory(components),
            'LAST_WORLD':predict_single(models['last'],components),
        }
        held=set(ACTIONS)-{x for x,_ in obs}
        for label,pred in predictions.items():
            for x in sorted(held):
                samples[label].append((pred[x]-truth[x])**2)
                accuracy[label].append(int((pred[x]>=.5)==truth[x]))
    return {name:{'brier':round(math.fsum(samples[name])/len(samples[name]),9),
                  'accuracy':round(math.fsum(accuracy[name])/len(accuracy[name]),9)} for name in samples}


def evaluate_A():
    start=time.perf_counter();cpu_start=time.process_time();tracemalloc.start()
    a,b=chosen_ops()
    assert a!=b and len(CANDIDATES)==24 and len(PAIRS)==300
    history=[new_world('train',i)[0] for i in range(TRAIN_WORLDS)]
    # Fitter receives the observations only, never labels or source op truths.
    trained=learn(history)
    compact_json=json.dumps(trained['top6'],sort_keys=True,separators=(',',':'))
    saved=json.loads(compact_json)
    restored=tuple(((int(pair[0]),int(pair[1])),weight) for pair,weight in saved)
    same=world_likelihoods(history[0]); assert len(same)==24
    probe=test_components(new_world('familiar',9999)[0])
    maxerr=max(abs(x-y) for x,y in zip(predict_pair(trained['top6'],probe),predict_pair(restored,probe)))
    in_fam=score('familiar',trained)
    novelty=score('novel',trained)
    peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
    conventional=min(in_fam[c]['brier'] for c in ('SINGLE_BAYES','FREQUENCY','NO_MEMORY','LAST_WORLD'))
    top=in_fam['TOP6_PAIR'];exact=in_fam['FULL_PAIR_BAYES'];novel=novelty['TOP6_PAIR'];nomem=novelty['NO_MEMORY']
    gates={
      'familiar_gain_vs_best_non_pair':conventional-top['brier']>=.02,
      'within_1_15x_full_pair_brier':top['brier']<=1.15*exact['brier'],
      'accuracy_within_2pp_full_pair':exact['accuracy']-top['accuracy']<=.02,
      'novel_operator_harm_le_0_02':novel['brier']-nomem['brier']<=.02,
      'cold_parity_le_1e12':maxerr<=1e-12,
      'stored_pairs_le_6':len(restored)<=6
    }
    return {'schema':'ynca12.unlabeled-operator-context.result-A.v1','classification':'EXPLORATORY_DEVELOPMENT_ONLY',
            'seed':A_SEED,'training_worlds':TRAIN_WORLDS,'revealed_training_pairs':TRAIN_WORLDS*TRAIN_REVEALED,
            'test_worlds_per_family':TEST_WORLDS,'held_assignments_per_family':TEST_WORLDS*(8-TEST_REVEALED),
            'candidate_tables':len(CANDIDATES),'candidate_pairs':len(PAIRS),'retained_pairs':len(restored),
            'retained_serialized_bytes':len(compact_json.encode()),
            'retained_sha256':hashlib.sha256(compact_json.encode()).hexdigest(),
            'cold_max_abs_error':maxerr,
            'metrics':{'familiar':in_fam,'novel':novelty},'gates':gates,'development_go':all(gates.values()),
            'resource':{'wall_seconds':round(time.perf_counter()-start,6),'cpu_seconds':round(time.process_time()-cpu_start,6),
                        'tracemalloc_peak_bytes':peak},
            'claims':{'native_trained':False,'scientific_pass':False,'deployed':False,'B_used':False}}


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--split',choices=('A',),required=True)
    p.parse_args()
    print(json.dumps(evaluate_A(),sort_keys=True,indent=2))
