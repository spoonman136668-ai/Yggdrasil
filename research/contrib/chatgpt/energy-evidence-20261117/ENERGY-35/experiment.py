#!/usr/bin/env python3
"""ENERGY-35: source-free causal-bridge learning with sparse energy constraints.

Isolated development data, fixed grammar; not native Yggdrasil training.
All interventions are actual witnessed action/outcome pairs and every comparator
receives the identical training observations within a regime.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time
import warnings
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit, Ridge, LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).resolve().parent
SEEDS = (7307, 7331, 7349)
FAMILIES = ('parity3', 'mixed', 'extended4')
REGIMES = ('bridge16', 'no_bridge')
ARMS = ('paired_energy', 'plain_energy', 'omp12', 'paired_omp12',
        'paired_ridge', 'logistic', 'rbf_svm', 'decision_tree', 'shuffled_energy')
CONTROLS = ('omp12','paired_omp12','paired_ridge','logistic','rbf_svm','decision_tree')
X = np.array([[(i >> j) & 1 for j in range(8)] for i in range(256)], dtype=np.int8)
S = 2 * X - 1
INDEX = {}
COLS = []
for degree in (1, 2, 3, 4):
    for coords in combinations(range(8), degree):
        INDEX[('parity', coords)] = len(COLS)
        COLS.append(np.prod(S[:,coords], axis=1))
for coords in combinations(range(8), 2):
    INDEX[('and', coords)] = len(COLS)
    COLS.append(2 * (X[:,coords[0]] & X[:,coords[1]]) - 1)
PHI = np.array(COLS, dtype=np.float64).T
assert PHI.shape == (256, 190)
BY_DEG = {k:[v for (kind,coords),v in INDEX.items() if kind=='parity' and len(coords)==k]
          for k in (1,2,3,4)}
AND = [v for (kind,_),v in INDEX.items() if kind=='and']


def hashkey(*items):
    return sha256('/'.join(map(str,('energy35-v1',*items))).encode('ascii')).digest()


def choose(*items,n):
    return int.from_bytes(hashkey(*items)[:8],'big') % n


def make_world(seed,world,family,regime):
    banks = ([BY_DEG[3]]*3 if family == 'parity3' else
             [BY_DEG[3],BY_DEG[2],AND] if family == 'mixed' else
             [BY_DEG[4],BY_DEG[3],AND])
    factors = []
    for t,bank in enumerate(banks):
        pos=choose('factor',seed,world,family,t,n=len(bank))
        while bank[pos] in factors: pos=(pos+1)%len(bank)
        factors.append(bank[pos])
    signs=[1 if choose('sign',seed,world,family,t,n=2) else -1 for t in range(3)]
    truth=np.where(sum(sign * PHI[:,f] for sign,f in zip(signs,factors))>0,1,-1)
    zero = sorted((i for i in range(256) if (i&1)==0),
                  key=lambda i:hashkey('zero',seed,world,family,i))
    one = sorted((i for i in range(256) if (i&1)==1),
                 key=lambda i:hashkey('one',seed,world,family,i))
    common=zero[:80]  # common, witnessed across both regimes
    substituted=zero[80:96]
    held_old=zero[96:112]
    pair_bases=common[:16]
    flips=[i|1 for i in pair_bases]
    held_new=[i for i in one if i not in flips][:48]
    train=common+(flips if regime=='bridge16' else substituted)
    held=held_old+held_new
    assert len(train)==96 and len(held)==64 and not set(train)&set(held)
    obs=[]
    for a in train:
        flip=int.from_bytes(hashkey('noise',seed,world,family,a)[:8],'big')/2**64 < .1
        obs.append(int(truth[a]) * (-1 if flip else 1))
    paired=[(train.index(a),train.index(a|1)) for a in pair_bases] if regime=='bridge16' else []
    changed=int(sum(truth[a]!=truth[a|1] for a in held_old))
    return train,held,np.array(obs,dtype=np.float64),truth,paired,changed


def learn_energy(features,y,paired,contrastive,epochs=48):
    """Learn E(y|x)=-y*w·phi(x) from witnessed labels.

    Bridge contrast uses paired action deltas, not evaluator truth. Hard support
    projection and contrastive hinge updates are distinct from Bayes filtering.
    """
    w=np.zeros(features.shape[1],dtype=np.float64)
    if paired:
        first,second=np.array(paired,dtype=np.int64).T
        delta=(features[second]-features[first])*.5
        target=(y[second]-y[first])*.5
    for _ in range(epochs):
        margin=y*(features@w)
        failed=margin<1.0
        if not np.any(failed): break
        grad=np.mean(y[failed,None]*features[failed],axis=0)
        if contrastive and paired:
            signed=(target!=0)
            if np.any(signed):
                dmargin=target[signed]*(delta[signed]@w)
                bad=dmargin<.6
                if np.any(bad):
                    grad+=.20*np.mean(target[signed][bad,None]*delta[signed][bad],axis=0)
            equal=~signed
            if np.any(equal):
                grad-=.02*np.mean((delta[equal]@w)[:,None]*delta[equal],axis=0)
        picked=np.argsort(-np.abs(grad),kind='stable')[:8]
        w[picked]+=.05*grad[picked]
        keep=np.argsort(-np.abs(w),kind='stable')[:12]
        mask=np.zeros(len(w),bool);mask[keep]=True
        w[~mask]=0
    assert np.count_nonzero(w)<=12
    return w


def predict_all(train,held,y,paired,seed,world,family,regime):
    f=PHI[train];h=PHI[held]
    raw=X[train];hr=X[held]
    output={};time_cost={};capacity={}
    for arm in ARMS:
        start=time.perf_counter()
        if arm in ('paired_energy','plain_energy','shuffled_energy'):
            if arm=='shuffled_energy':
                y0=np.random.default_rng(choose('sham',seed,world,family,regime,n=2**32)).permutation(y)
            else:y0=y
            w=learn_energy(f,y0,paired,contrastive=arm!='plain_energy')
            score=h@w
            capacity[arm]=int(np.count_nonzero(w))
        elif arm in ('omp12','paired_omp12'):
            fitx=f;fity=y
            if arm=='paired_omp12' and paired:
                first,second=np.array(paired,dtype=int).T
                fitx=np.vstack([f,(f[second]-f[first])*.5])
                fity=np.r_[y,(y[second]-y[first])*.5]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',RuntimeWarning)
                model=OrthogonalMatchingPursuit(n_nonzero_coefs=12,fit_intercept=True)
                model.fit(fitx,fity)
            score=model.predict(h)
            capacity[arm]=int(np.count_nonzero(model.coef_))
        elif arm=='paired_ridge':
            fitx=f;fity=y
            if paired:
                first,second=np.array(paired,dtype=int).T
                fitx=np.vstack([f,(f[second]-f[first])*.5])
                fity=np.r_[y,(y[second]-y[first])*.5]
            model=Ridge(alpha=3.0).fit(fitx,fity)
            score=model.predict(h)
            capacity[arm]=int(np.count_nonzero(model.coef_))
        elif arm=='logistic':
            model=LogisticRegression(C=1.0,max_iter=500,tol=1e-8).fit(f,y)
            score=model.decision_function(h)
            capacity[arm]=int(np.count_nonzero(model.coef_))
        elif arm=='rbf_svm':
            model=SVC(C=2.0,gamma='scale',kernel='rbf').fit(raw,y)
            score=model.decision_function(hr)
            capacity[arm]=-1
        else:
            model=DecisionTreeClassifier(max_depth=8,random_state=19).fit(raw,y)
            score=model.predict(hr)
            capacity[arm]=int(model.tree_.node_count)
        output[arm]=np.where(score>0,1,-1).astype(np.int8)
        time_cost[arm]=time.perf_counter()-start
    return output,time_cost,capacity


def run_case(seed,world,family,regime):
    train,held,obs,truth,paired,flip_count=make_world(seed,world,family,regime)
    pred,times,cap=predict_all(train,held,obs,paired,seed,world,family,regime)
    correct={arm:{'old':int((p[:16]==truth[held[:16]]).sum()),
                  'new':int((p[16:]==truth[held[16:]]).sum())} for arm,p in pred.items()}
    return {'seed':seed,'world':world,'family':family,'regime':regime,
            'flip_relevance':flip_count,'correct':correct,'time_seconds':times,'support':cap}


def aggregate(cases):
    scores={r:{a:{z:sum(c['correct'][a][z] for c in cases if c['regime']==r)
                  for z in ('old','new')} for a in ARMS} for r in REGIMES}
    den={r:{'old':sum(c['regime']==r for c in cases)*16,
            'new':sum(c['regime']==r for c in cases)*48} for r in REGIMES}
    timed={r:{a:sum(c['time_seconds'][a] for c in cases if c['regime']==r) for a in ARMS} for r in REGIMES}
    return scores,den,timed


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    seeds=(99079,) if a.smoke else SEEDS
    worlds=range(2) if a.smoke else range(8)
    started=time.perf_counter()
    cases=[run_case(seed,world,family,regime) for seed in seeds for world in worlds
           for family in FAMILIES for regime in REGIMES]
    scores,den,timed=aggregate(cases)
    new=scores['bridge16'];no=scores['no_bridge']
    best_new=max(new[arm]['new'] for arm in CONTROLS)
    best_old=max(new[arm]['old'] for arm in CONTROLS)
    matched_gain_by_seed=[]
    for seed in seeds:
        part=[c for c in cases if c['seed']==seed]
        sc,de,_=aggregate(part)
        matched_gain_by_seed.append(sc['bridge16']['paired_energy']['new']-
                                     max(sc['bridge16'][arm]['new'] for arm in CONTROLS))
    gates={
      'shift_vs_strongest':(new['paired_energy']['new']-best_new)/den['bridge16']['new'] >= .03,
      'old_retention':new['paired_energy']['old']>=best_old-.01*den['bridge16']['old'],
      'contrast_ablation':(new['paired_energy']['new']-new['plain_energy']['new'])/den['bridge16']['new']>=.02,
      'bridge_value':(new['paired_energy']['new']-no['paired_energy']['new'])/den['bridge16']['new']>=.05,
      'seed_stability':sum(v>0 for v in matched_gain_by_seed)>=2,
      'shuffled_control':new['paired_energy']['new']>new['shuffled_energy']['new'],
      'fit_cost':timed['bridge16']['paired_energy']<=1.5*min(timed['bridge16'][arm] for arm in CONTROLS),
    }
    result={'schema':'yggdrasil.energy35.score.v1','mode':'smoke' if a.smoke else 'primary',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'seeds':list(seeds),'worlds':len(cases),'observations_per_world':96,
            'held_per_world':64,'bridged_pairs':16,'feature_count':190,
            'scores':scores,'denominators':den,'fit_inference_seconds':timed,
            'seed_new_correct_margins':matched_gain_by_seed,
            'gates':gates,'classification':'DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO',
            'wall_seconds':time.perf_counter()-started,'details':cases,
            'scientific_pass':False,'native_checkpoint_run':False,'deployment':'NONE'}
    Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True,indent=2))


if __name__=='__main__':main()
