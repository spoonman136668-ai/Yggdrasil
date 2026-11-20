#!/usr/bin/env python3
"""Independent, source-free ENERGY-49 primary source/solver/refit audit (no candidate imports)."""
import argparse,hashlib,json,itertools,time,warnings
from pathlib import Path
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit,ElasticNet

G=[('p',v) for k in (1,2,3) for v in itertools.combinations(range(12),k)]+[('a',v) for v in itertools.combinations(range(12),2)]
POL=('contradiction_energy','contradiction_dense','committee','diverse','random','shuffled_contradiction','fixed')
methods=('elasticnet','omp7')
checks=0

def check(v,expected,msg):
    global checks
    checks+=1
    if isinstance(v,(float,np.floating)) or isinstance(expected,(float,np.floating)):
        if not np.isclose(v,expected,rtol=2e-9,atol=1e-10,equal_nan=True):raise AssertionError((msg,v,expected))
    elif v!=expected:raise AssertionError((msg,v,expected))

def gen(*key):
    raw='ENERGY48-v1|'+'|'.join(map(str,key))
    return np.random.default_rng(int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8],'big'))

def transforms(X):
    v=np.empty((X.shape[0],364),float)
    for j,(typ,idx) in enumerate(G):
        col=X[:,tuple(idx)]
        if typ=='p':v[:,j]=np.prod(1-2*col,axis=1)
        else:v[:,j]=2*np.prod(col,axis=1)-1
    return v

def origin(case,family,idx):
    g=gen(case,'latent')
    if family=='parity2':pool=[i for i,(k,src) in enumerate(G) if k=='p' and len(src)==2 and max(src)<10]
    elif family=='parity3':pool=[i for i,(k,src) in enumerate(G) if k=='p' and len(src)==3 and max(src)<10]
    else:pool=[i for i,(k,src) in enumerate(G) if len(src)>=2 and max(src)<10]
    ids=[int(t) for t in g.choice(pool,5,replace=False)]
    weights=[float((-1 if g.random()<.5 else 1)*g.uniform(.85,1.15)) for _ in range(5)]
    if idx==3:ids[4]=ids[3];weights[4]=weights[3]
    return ids,weights

def action(case,tag,stage,num):
    g=gen(case,tag,'actions');X=g.integers(0,2,(num,12),dtype=np.int8)
    if tag!='cold_held':
        a=X[:,0].copy() if stage==0 else 1-X[:,0]
        b=X[:,1].copy() if stage==0 else X[:,2].copy()
        X[:,10]=np.bitwise_xor(a,(g.random(num)<.08).astype(np.int8))
        X[:,11]=np.bitwise_xor(b,(g.random(num)<.08).astype(np.int8))
    return X

def outcomes(case,ids,coef,X,tag,stage):
    Z=transforms(X)
    w=np.asarray(coef)
    label=Z[:,ids[:3]]@w[:3]+Z[:,ids[3+stage]]*w[3+stage]
    return label+gen(case,tag,'noise').normal(0,.3,len(X))

def fitted(A,y,how):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if how=='omp4':return OrthogonalMatchingPursuit(n_nonzero_coefs=4,fit_intercept=True).fit(A,y)
        if how=='omp7':return OrthogonalMatchingPursuit(n_nonzero_coefs=7,fit_intercept=True).fit(A,y)
        if how=='elasticnet':return ElasticNet(alpha=.025,l1_ratio=.85,max_iter=4000,tol=1e-5,fit_intercept=True).fit(A,y)
    raise ValueError(how)

def greedy(scores,pool,train,lam):
    n=len(pool);s=np.asarray(scores,dtype=float);s=s/max(float(np.max(np.abs(s))),1e-8)
    available=np.ones(n,dtype=bool)
    dist=np.count_nonzero(pool[:,None,:]!=train[None,:,:],axis=2).min(axis=1)
    chosen=[]
    for _ in range(24):
        weight=np.where(available,s+lam*dist/12.,-np.inf)
        ix=int(weight.argmax());chosen.append(ix);available[ix]=False
        dist=np.minimum(dist,np.count_nonzero(pool!=pool[ix],axis=1))
    return chosen

def audit_policy(policy,case,Xold,Yold,Xnew,Ynew,pool):
    if policy=='fixed':return list(range(24))
    if policy=='random':return [int(i) for i in gen(case,'random_selector').choice(192,24,replace=False)]
    if policy=='diverse':return greedy(np.zeros(192),pool,Xnew,1.)
    a=transforms(Xold);b=transforms(Xnew);c=transforms(pool)
    if policy=='committee':
        draws=[]
        for rep in range(4):
            sampled=gen(case,'bootstrap',rep).integers(0,48,48)
            draws.append(fitted(b[sampled],Ynew[sampled],'elasticnet').predict(c))
        score=np.std(draws,axis=0)
    else:
        if policy in ('contradiction_energy','shuffled_contradiction'):
            old=fitted(a,Yold,'omp4')
            y=Ynew if policy=='contradiction_energy' else gen(case,'shuffled').permutation(Ynew)
            fresh=fitted(b,y,'omp4')
        elif policy=='contradiction_dense':old=fitted(a,Yold,'elasticnet');fresh=fitted(b,Ynew,'elasticnet')
        else:raise ValueError(policy)
        score=np.abs(old.predict(c)-fresh.predict(c))
    return greedy(score,pool,Xnew,.18)

def do_case(c):
    case=c['case'];seed=c['seed'];idx=c['idx'];family=c['family']
    check(case,f'{seed}:{idx}:{family}','case key')
    check(bool(c['changed']),idx!=3,'changed')
    ids,w=origin(case,family,idx)
    check(c['truth_sha256'],hashlib.sha256(json.dumps({'ids':ids,'w':w},sort_keys=True).encode()).hexdigest(),'truth hash')
    Xold=action(case,'old_train',0,96);Yold=outcomes(case,ids,w,Xold,'old_train',0)
    Xnew=action(case,'new_train',1,48);Ynew=outcomes(case,ids,w,Xnew,'new_train',1)
    P=action(case,'candidate_pool',1,192)
    check(c['pool_x_sha256'],hashlib.sha256(P.tobytes()).hexdigest(),'public candidate pool')
    held=[(tag,stage,action(case,tag,stage,128)) for tag,stage in (('old_held',0),('new_held',1),('cold_held',1))]
    target=[outcomes(case,ids,w,X,tag,stage) for tag,stage,X in held]
    for i,y in enumerate(target):check(c['held_sha256'][i],hashlib.sha256(np.asarray(y,dtype='<f8').tobytes()).hexdigest(),'held truth hash')
    # no outcome or hidden truth passed into audit_policy; verify selectors independently
    for p in POL:
        selected=audit_policy(p,case,Xold,Yold,Xnew,Ynew,P)
        check(c['selected'][p],selected,'selected intervention list')
        check(len(set(selected)),24,'selected unique')
        Yp=outcomes(case,ids,w,P,'candidate_pool',1)
        Xn=np.concatenate([Xnew,P[selected]])
        Yn=np.concatenate([Ynew,Yp[selected]])
        o=transforms(Xold);n=transforms(Xn)
        V=np.vstack([np.column_stack([o,np.zeros_like(o)]),np.column_stack([np.zeros_like(n),n])])
        y=np.concatenate([Yold,Yn])
        for how in methods:
            name=f'{p}:{how}'
            model=fitted(V,y,how)
            for t,(_,stage,T) in enumerate(held):
                feats=transforms(T)
                Vt=np.column_stack([feats,np.zeros_like(feats)]) if stage==0 else np.column_stack([np.zeros_like(feats),feats])
                pred=model.predict(Vt)
                expected=c['arms'][name]
                check(expected['pred_sha256'][t],hashlib.sha256(np.asarray(pred,dtype='<f8').tobytes()).hexdigest(),name+' predicted bytes')
                check(expected['mse_'+('old','new','cold')[t]],np.mean((pred-target[t])**2),name+' MSE')

def audit(record):
    global checks
    checks=0
    assert record['schema']=='yggdrasil.energy48.v1'
    assert record['mode']=='primary'
    assert tuple(record['seeds'])==(9109,9127,9137)
    assert len(record['cases'])==len(record['seeds'])*len(record['ids'])*len(record['families'])
    for c in record['cases']:do_case(c)
    check(record['summary']['gates_total'],9,'legacy scorer gate count')
    check(record['summary']['gates_passed'],sum(record['summary']['gates'].values()),'legacy scorer gate count same')
    return {'schema':'yggdrasil.energy49.independent-audit.v1','status':'PASS','checks':checks,'cases':len(record['cases']),
            'primary_scored':True,'source_free':True,'all_7_intervention_selections_recomputed':True,
            'all_14_models_refit':True,'all_held_pred_sha_and_mse_recomputed':True,
            'libs_shared':'numpy and sklearn; no candidate source import','audit_time_s':None}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('record');p.add_argument('--out',required=True);args=p.parse_args()
    start=time.perf_counter();r=audit(json.loads(Path(args.record).read_text()));r['audit_time_s']=time.perf_counter()-start
    Path(args.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps(r,sort_keys=True))
