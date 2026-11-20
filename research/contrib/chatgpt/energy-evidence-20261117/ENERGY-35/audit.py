#!/usr/bin/env python3
"""ENERGY-35 standalone post-score audit; independent finite source + refit.

Does not import experiment.py. Reconstructs each source world, 144 action splits,
independent label flips, the frozen factor grammar, and each learned-policy's
held predictions, using independent literal implementations and sklearn fitting.
Never writes or alters the frozen scored primary file.
"""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json, sys, time, warnings
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit, Ridge, LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

SOURCE_SHA = 'dde9f68ea1f86e7e09b291859adffec78d33cfb6dd1197e8fdf25e92e4bdca9c'
SEEDS=(7307,7331,7349)
FAMILIES=('parity3','mixed','extended4')
REGIMES=('bridge16','no_bridge')
ARMS=('paired_energy','plain_energy','omp12','paired_omp12','paired_ridge','logistic','rbf_svm','decision_tree','shuffled_energy')
CONTROLS=('omp12','paired_omp12','paired_ridge','logistic','rbf_svm','decision_tree')

# Deliberately built without importing the experiment's 190-feature design.
PATTERNS=[[(k>>bit)&1 for bit in range(8)] for k in range(256)]
BASIS=[]
for d in (1,2,3,4):BASIS.extend([('parity',x) for x in combinations(range(8),d)])
BASIS.extend([('and',x) for x in combinations(range(8),2)])
assert len(BASIS)==190

def phi(x):
    a=PATTERNS[x]
    out=[]
    for kind,coord in BASIS:
        if kind=='parity':
            z=1
            for bit in coord:z*=2*a[bit]-1
        else:z=2*(a[coord[0]]&a[coord[1]])-1
        out.append(z)
    return out
PHI=np.array([phi(k) for k in range(256)],dtype=float)

def h(*args):return sha256('/'.join(map(str,('energy35-v1',*args))).encode('ascii')).digest()
def rand(*args,n):return int.from_bytes(h(*args)[:8],'big')%n

# Only source/evaluator has the ground-truth signed factor dictionary.
def rebuild(seed,world,family,regime):
    p={d:[i for i,(kind,c) in enumerate(BASIS) if kind=='parity' and len(c)==d] for d in (2,3,4)}
    ands=[i for i,(kind,c) in enumerate(BASIS) if kind=='and']
    banks=([p[3]]*3 if family=='parity3' else [p[3],p[2],ands] if family=='mixed' else [p[4],p[3],ands])
    selected=[]
    for t,pool in enumerate(banks):
        k=rand('factor',seed,world,family,t,n=len(pool))
        while pool[k] in selected:k=(k+1)%len(pool)
        selected.append(pool[k])
    signs=[1 if rand('sign',seed,world,family,t,n=2) else -1 for t in range(3)]
    truth=np.where(np.sum([s*PHI[:,factor] for s,factor in zip(signs,selected)],axis=0)>0,1,-1)
    zero=sorted((i for i in range(256) if i%2==0), key=lambda i:h('zero',seed,world,family,i))
    one=sorted((i for i in range(256) if i%2==1), key=lambda i:h('one',seed,world,family,i))
    common=zero[:80];pairs_base=common[:16];flipped=[i+1 for i in pairs_base]
    held_old=zero[96:112]
    held_new=[i for i in one if i not in flipped][:48]
    train=common+(flipped if regime=='bridge16' else zero[80:96])
    held=held_old+held_new
    observations=[]
    for i in train:
        flip=int.from_bytes(h('noise',seed,world,family,i)[:8],'big')/2**64 < .1
        observations.append(int(truth[i]) *(-1 if flip else 1))
    pair_indices=[(train.index(i),train.index(i+1)) for i in pairs_base] if regime=='bridge16' else []
    relevance=sum(int(truth[i]!=truth[i+1]) for i in held_old)
    return train, held, np.array(observations,dtype=float), truth, pair_indices, relevance

def direct_energy(x,y,pairs,active):
    weights=np.zeros(x.shape[1],dtype=float)
    if pairs:
        aa=np.array([p[0] for p in pairs]);bb=np.array([p[1] for p in pairs])
        dx=.5*(x[bb]-x[aa]);dy=.5*(y[bb]-y[aa])
    for iteration in range(48):
        margin=y*np.dot(x,weights)
        failed=np.flatnonzero(margin<1.)
        if len(failed)==0:break
        step=(y[failed,None]*x[failed]).mean(axis=0)
        if active and pairs:
            differing=dy!=0
            if np.any(differing):
                xdiff=dx[differing];ydiff=dy[differing]
                weak=np.flatnonzero(ydiff*(xdiff@weights)<.6)
                if len(weak):step+=.2*(ydiff[weak,None]*xdiff[weak]).mean(axis=0)
            same=~differing
            if np.any(same):
                xeq=dx[same]
                step-=.02*((xeq@weights)[:,None]*xeq).mean(axis=0)
        best=np.argsort(-np.abs(step),kind='stable')[:8]
        weights[best]+=.05*step[best]
        keep=np.argsort(-np.abs(weights),kind='stable')[:12]
        preserved=np.zeros(len(weights),dtype=bool);preserved[keep]=True
        weights[~preserved]=0.
    return weights

def preds(train,held,obs,pairs,seed,world,family,regime):
    raw=np.array([PATTERNS[i] for i in train],dtype=int)
    raw_held=np.array([PATTERNS[i] for i in held],dtype=int)
    fit=PHI[train];hold=PHI[held]
    answers={};supports={}
    for arm in ARMS:
        if arm in ('paired_energy','plain_energy','shuffled_energy'):
            y=obs.copy()
            if arm=='shuffled_energy':
                y=np.random.default_rng(rand('sham',seed,world,family,regime,n=2**32)).permutation(y)
            w=direct_energy(fit,y,pairs,arm!='plain_energy')
            score=hold@w; supports[arm]=int(np.count_nonzero(w))
        elif arm in ('omp12','paired_omp12','paired_ridge'):
            features=fit;labels=obs
            if arm in ('paired_omp12','paired_ridge') and pairs:
                base=np.array([v[0] for v in pairs]);flips=np.array([v[1] for v in pairs])
                features=np.concatenate((fit,.5*(fit[flips]-fit[base])),axis=0)
                labels=np.concatenate((obs,.5*(obs[flips]-obs[base])),axis=0)
            if arm=='paired_ridge':
                estimator=Ridge(alpha=3.).fit(features,labels)
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore',RuntimeWarning)
                    estimator=OrthogonalMatchingPursuit(n_nonzero_coefs=12,fit_intercept=True).fit(features,labels)
            score=estimator.predict(hold)
            supports[arm]=int(np.count_nonzero(estimator.coef_))
        elif arm=='logistic':
            estimator=LogisticRegression(C=1.0,max_iter=500,tol=1e-8).fit(fit,obs)
            score=estimator.decision_function(hold)
            supports[arm]=int(np.count_nonzero(estimator.coef_))
        elif arm=='rbf_svm':
            estimator=SVC(C=2.0,gamma='scale',kernel='rbf').fit(raw,obs)
            score=estimator.decision_function(raw_held)
            supports[arm]=-1
        else:
            estimator=DecisionTreeClassifier(max_depth=8,random_state=19).fit(raw,obs)
            score=estimator.predict(raw_held)
            supports[arm]=estimator.tree_.node_count
        answers[arm]=np.where(score>0,1,-1)
    return answers,supports

def audit(path):
    b=Path(path).read_bytes();r=json.loads(b)
    checks=0
    def ok(condition,msg):
        nonlocal checks
        checks+=1
        if not condition:raise AssertionError(msg)
    ok(r['mode']=='primary' and r['schema']=='yggdrasil.energy35.score.v1','schema/mode')
    ok(r['source_sha256']==SOURCE_SHA,'source SHA')
    ok(r['seeds']==list(SEEDS),'seed identity')
    ok(r['worlds']==144==len(r['details']),'population')
    seen=set();total={reg:{arm:{z:0 for z in ('old','new')} for arm in ARMS} for reg in REGIMES}
    runtimes={reg:{arm:0. for arm in ARMS} for reg in REGIMES}
    for case in r['details']:
        seed,world,family,regime=[case[k] for k in ('seed','world','family','regime')]
        ident=(seed,world,family,regime)
        ok(ident not in seen,'duplicate identity'); seen.add(ident)
        ok(seed in SEEDS and world in range(8) and family in FAMILIES and regime in REGIMES,'identity bounds')
        train,held,y,truth,pairs,degree=rebuild(seed,world,family,regime)
        ok(len(train)==96 and len(set(train))==96,'96 distinct train')
        ok(len(held)==64 and len(set(held))==64 and set(train).isdisjoint(held),'disjoint held')
        ok(sum((a&1) for a in train)==(16 if regime=='bridge16' else 0),'bridge allocation')
        ok(all((a&1)==0 for a in held[:16]) and all((a&1)==1 for a in held[16:]),'held context')
        ok(case['flip_relevance']==degree,'independent causal flip source')
        ok((len(pairs)==16 if regime=='bridge16' else len(pairs)==0),'pair count')
        pred,supports=preds(train,held,y,pairs,seed,world,family,regime)
        for arm in ARMS:
            old=int(np.sum(pred[arm][:16]==truth[held[:16]]))
            new=int(np.sum(pred[arm][16:]==truth[held[16:]]))
            ok(case['correct'][arm]=={'old':old,'new':new},'independent full refit score '+str(ident)+'/'+arm)
            ok(case['support'][arm]==supports[arm],'support '+arm)
            ok(case['time_seconds'][arm]>=0,'timing nonnegative')
            total[regime][arm]['old']+=old; total[regime][arm]['new']+=new
            runtimes[regime][arm]+=case['time_seconds'][arm]
    ok(seen=={(seed,w,f,reg) for seed in SEEDS for w in range(8) for f in FAMILIES for reg in REGIMES},'complete world grid')
    ok(total==r['scores'],'aggregate scores')
    ok(r['denominators']=={reg:{'new':3456,'old':1152} for reg in REGIMES},'denominators')
    ok(all(abs(runtimes[reg][arm]-r['fit_inference_seconds'][reg][arm])<1e-8 for reg in REGIMES for arm in ARMS),'timer aggregation')
    bridges=total['bridge16'];no=total['no_bridge']
    seed_margins=[]
    for seed in SEEDS:
        per=[case for case in r['details'] if case['seed']==seed and case['regime']=='bridge16']
        m=sum(c['correct']['paired_energy']['new'] for c in per)-max(sum(c['correct'][a]['new'] for c in per) for a in CONTROLS)
        seed_margins.append(m)
    ok(seed_margins==r['seed_new_correct_margins'],'seed margins')
    derived={
      'shift_vs_strongest':(bridges['paired_energy']['new']-max(bridges[a]['new'] for a in CONTROLS))/3456>=.03,
      'old_retention':bridges['paired_energy']['old']>=max(bridges[a]['old'] for a in CONTROLS)-.01*1152,
      'contrast_ablation':(bridges['paired_energy']['new']-bridges['plain_energy']['new'])/3456>=.02,
      'bridge_value':(bridges['paired_energy']['new']-no['paired_energy']['new'])/3456>=.05,
      'seed_stability':sum(m>0 for m in seed_margins)>=2,
      'shuffled_control':bridges['paired_energy']['new']>bridges['shuffled_energy']['new'],
      'fit_cost':runtimes['bridge16']['paired_energy']<=1.5*min(runtimes['bridge16'][a] for a in CONTROLS)
    }
    ok(derived==r['gates'],'frozen gates')
    ok(r['classification']==('DEVELOPMENT_GO' if all(derived.values()) else 'DEVELOPMENT_NO_GO'),'classification')
    ok(r['scientific_pass'] is False and r['native_checkpoint_run'] is False and r['deployment']=='NONE','authority boundaries')
    return {'audit':'PASS','independent_source_and_full_model_refit':True,'checks':checks,
            'scored_sha256':sha256(b).hexdigest(),'cases':len(seen),'scores':total,
            'gates':derived,'seed_new_correct_margins':seed_margins,
            'source_sha256':SOURCE_SHA,'native_acceptance':'NOT RUN',
            'caveats':'Reuses scikit-learn estimator implementation for conventional controls; local source-free synthetic audit, not native scientific acceptance.'}

if __name__=='__main__':
    started=time.perf_counter()
    result=audit(sys.argv[1] if len(sys.argv)>1 else 'scored.json')
    result['audit_wall_seconds']=time.perf_counter()-started
    Path('audit_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='scores'},indent=2,sort_keys=True))
