"""ENERGY-67: prospective external synthetic evidence; not a native Yggdrasil learner.

Frozen source. All learner choices are conditional on train/validation labels only.
The independent auditor is in audit.py and does not import this module.
"""
import argparse, hashlib, itertools, json, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import ElasticNet

BITS=9
PAIRS=list(itertools.combinations(range(BITS),2))
QUADS=list(itertools.combinations(range(BITS),4))
FIFTHS=list(itertools.combinations(range(BITS),5))
FAMILIES=('two_quad','four_quad','four_quad_plus_fifth')
POLICIES=('adaptive_growth','cv_growth','fixed_two','fixed_five','matched_elasticnet','full_omp_five','old_support_only','old_frozen','shuffled_negative')
ALPHAS=(0.01,0.03,0.1,0.3,1.0)


def stream_seed(seed, family, wid):
    h=hashlib.sha256(f'ENERGY-67:v1:{seed}:{family}:{wid}'.encode()).digest()
    return int.from_bytes(h[:8],'little')


def gram(x,combs):
    z=np.asarray(x,dtype=np.int8)
    return np.prod(z[:,np.asarray(combs,dtype=int)],axis=2).astype(float)


def fit_ridge(x,y,lam=.3):
    a=np.column_stack([np.ones(len(x)), x])
    diag=np.eye(a.shape[1]); diag[0,0]=0
    return np.linalg.solve(a.T@a + lam*diag,a.T@y)


def predict_ridge(x,w):
    return np.column_stack([np.ones(len(x)),x])@w


def greedy_path(z,y,fixed,iterations=5):
    """OLS residual greedy path, no ground-truth support information."""
    indices=[]; candidates=np.arange(z.shape[1]);
    for _ in range(iterations):
        used=fixed if not indices else np.column_stack([fixed,z[:,indices]])
        residual=y-predict_ridge(used,fit_ridge(used,y))
        correlations=np.abs(z.T@residual)
        if indices: correlations[indices]=-np.inf
        j=int(np.argmax(correlations));indices.append(j)
    return indices


def fit_old(x,y):
    zp=gram(x,PAIRS)
    idx=greedy_path(zp,y,np.zeros((len(x),0)),3)
    return idx,fit_ridge(zp[:,idx],y)


def gen(seed,family,wid):
    rng=np.random.default_rng(stream_seed(seed,family,wid))
    n=np.arange(512,dtype=np.uint16)[:,None]
    all_x=(1-2*((n>>np.arange(BITS))&1)).astype(np.int8)
    rng.shuffle(all_x,axis=0)
    # OLD80, NEW64, held OLD48, NEW48, COLD48, unused224, all disjoint
    xo,xn,ho,hn,hc=all_x[:80],all_x[80:144],all_x[144:192],all_x[192:240],all_x[240:288]
    old_ids=rng.choice(len(PAIRS),size=3,replace=False)
    pair_weights=rng.choice([-1,1],3)*rng.uniform(.85,1.25,3)
    old_new_weights=pair_weights*rng.uniform(.92,1.08,3)
    quad_ids=rng.choice(len(QUADS),size=4,replace=False)
    quad_weights=rng.choice([-1,1],4)*rng.uniform(.85,1.2,4)
    number=2 if family=='two_quad' else 4
    fifth_id=int(rng.integers(len(FIFTHS)))
    fifth_weight=float(rng.choice([-1,1])*1.2) if family=='four_quad_plus_fifth' else 0.
    def response(x,new):
        support=gram(x,PAIRS)[:,old_ids]
        y=support@(old_new_weights if new else pair_weights)
        if new:
            y=y+gram(x,QUADS)[:,quad_ids[:number]]@quad_weights[:number]
            if fifth_weight:y=y+fifth_weight*gram(x,FIFTHS)[:,[fifth_id]].ravel()
        return y+rng.normal(0,.18,size=len(x))
    yo,yn,yho,yhn,yhc=(response(xo,False),response(xn,True),response(ho,False),response(hn,True),response(hc,True))
    return dict(xo=xo,xn=xn,ho=ho,hn=hn,hc=hc,yo=yo,yn=yn,yho=yho,yhn=yhn,yhc=yhc,
                planted_pair_ids=old_ids.tolist(),planted_quad_ids=quad_ids[:number].tolist(),planted_fifth_id=fifth_id if fifth_weight else None)


def score_case(seed,family,wid):
    d=gen(seed,family,wid)
    xo,xn,ho,hn,hc=[d[k] for k in ('xo','xn','ho','hn','hc')]
    yo,yn,yho,yhn,yhc=[d[k] for k in ('yo','yn','yho','yhn','yhc')]
    old_ids,old_coef=fit_old(xo,yo)
    old_pred=predict_ridge(gram(ho,PAIRS)[:,old_ids],old_coef)
    fo=gram(xn,PAIRS)[:,old_ids]; fhn=gram(hn,PAIRS)[:,old_ids]; fhc=gram(hc,PAIRS)[:,old_ids]
    zn=gram(xn,QUADS); zhn=gram(hn,QUADS); zhc=gram(hc,QUADS)
    xtr,xval=fo[:48],fo[48:]; ztr,zval=zn[:48],zn[48:]; yt,yv=yn[:48],yn[48:]
    path=greedy_path(ztr,yt,xtr,5)
    validations=[]
    for k in range(6):
        z=np.column_stack([xtr,ztr[:,path[:k]]]) if k else xtr
        v=np.column_stack([xval,zval[:,path[:k]]]) if k else xval
        coef=fit_ridge(z,yt)
        validations.append(float(np.mean((yv-predict_ridge(v,coef))**2)))
    # Candidate: independent support evidence stops growth at first <3% relative validation improvement.
    adaptive_k=0
    for k in range(1,6):
        if validations[k] <= 0.97 * validations[k-1]: adaptive_k=k
        else: break
    # Conventional best validation count: identical fits, same features, same witness outcomes.
    cv_k=int(np.argmin(validations))
    policy_k=dict(adaptive_growth=adaptive_k,cv_growth=cv_k,fixed_two=2,fixed_five=5)
    preds={}; selection={}
    for name,k in policy_k.items():
        train=np.column_stack([fo,zn[:,path[:k]]]) if k else fo
        held_new=np.column_stack([fhn,zhn[:,path[:k]]]) if k else fhn
        held_cold=np.column_stack([fhc,zhc[:,path[:k]]]) if k else fhc
        coef=fit_ridge(train,yn)
        preds[name]=(predict_ridge(held_new,coef),predict_ridge(held_cold,coef));selection[name]=dict(k=k,terms=path[:k])
    # Strong conventional matched-bank ElasticNet: fit with same train/validation, frozen predetermined alpha grid.
    en_mat=np.column_stack([fo,zn]); en_tr=en_mat[:48]; en_val=en_mat[48:]
    val_scores=[]
    for alpha in ALPHAS:
        m=ElasticNet(alpha=alpha,l1_ratio=.8,max_iter=3000,tol=1e-6,selection='cyclic')
        m.fit(en_tr,yt)
        val_scores.append(float(np.mean((m.predict(en_val)-yv)**2)))
    best_alpha=ALPHAS[int(np.argmin(val_scores))]
    en=ElasticNet(alpha=best_alpha,l1_ratio=.8,max_iter=3000,tol=1e-6,selection='cyclic').fit(en_mat,yn)
    preds['matched_elasticnet']=(en.predict(np.column_stack([fhn,zhn])),en.predict(np.column_stack([fhc,zhc])))
    selection['matched_elasticnet']=dict(alpha=best_alpha)
    # Conventional OMP5 full pair+quad dictionary, fitted on all 64 NEW outcomes
    zfull=np.column_stack([gram(xn,PAIRS),zn]); full_path=greedy_path(zfull,yn,np.zeros((len(xn),0)),5)
    full_coef=fit_ridge(zfull[:,full_path],yn)
    preds['full_omp_five']=(predict_ridge(np.column_stack([gram(hn,PAIRS),zhn])[:,full_path],full_coef),predict_ridge(np.column_stack([gram(hc,PAIRS),zhc])[:,full_path],full_coef))
    selection['full_omp_five']=dict(terms=full_path)
    old_only_coef=fit_ridge(fo,yn)
    preds['old_support_only']=(predict_ridge(fhn,old_only_coef),predict_ridge(fhc,old_only_coef))
    preds['old_frozen']=(predict_ridge(fhn,old_coef),predict_ridge(fhc,old_coef))
    # Sham uses same candidate pipeline with labels shuffled before selecting new features.
    r=np.random.default_rng(stream_seed(seed,family,wid)+999)
    corrupted=yn[r.permutation(len(yn))];path_bad=greedy_path(ztr,corrupted[:48],xtr,5)
    bad_coef=fit_ridge(np.column_stack([fo,zn[:,path_bad[:5]]]),corrupted)
    preds['shuffled_negative']=(predict_ridge(np.column_stack([fhn,zhn[:,path_bad[:5]]]),bad_coef),predict_ridge(np.column_stack([fhc,zhc[:,path_bad[:5]]]),bad_coef))
    selection['shuffled_negative']=dict(terms=path_bad[:5])
    arms={name:dict(old_mse=float(np.mean((old_pred-yho)**2)),new_mse=float(np.mean((p[0]-yhn)**2)),cold_mse=float(np.mean((p[1]-yhc)**2)),
                    new_predictions=np.round(p[0],12).tolist(),cold_predictions=np.round(p[1],12).tolist(),old_predictions=np.round(old_pred,12).tolist()) for name,p in preds.items()}
    return dict(seed=seed,family=family,world_id=wid,world={k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in d.items()},old_selection=dict(terms=old_ids,coeff=old_coef.tolist()),growth_path=path,validation_losses=validations,selection=selection,arms=arms)


def aggregate(cases):
    metrics={}
    for name in POLICIES:
        metrics[name]={p:float(np.mean([c['arms'][name][p] for c in cases])) for p in ('old_mse','new_mse','cold_mse')}
    cand=metrics['adaptive_growth']['cold_mse']
    strongest=min(metrics[n]['cold_mse'] for n in POLICIES if n not in ('adaptive_growth','old_frozen','shuffled_negative'))
    seeds=sorted(set(c['seed'] for c in cases)); families=sorted(set(c['family'] for c in cases))
    def mean_on(name,cases_):return float(np.mean([c['arms'][name]['cold_mse'] for c in cases_]))
    by_seed={str(s):{n:mean_on(n,[c for c in cases if c['seed']==s]) for n in POLICIES} for s in seeds}
    by_family={s:{n:mean_on(n,[c for c in cases if c['family']==s]) for n in POLICIES} for s in families}
    growth={s:float(np.mean([c['selection']['adaptive_growth']['k'] for c in cases if c['family']==s])) for s in families}
    gates={
        'vs_strongest_5pct':cand <= .95*strongest,
        'vs_matched_cv_3pct':cand <= .97*metrics['cv_growth']['cold_mse'],
        'vs_elasticnet_5pct':cand <= .95*metrics['matched_elasticnet']['cold_mse'],
        'both_seed_strongest':all(by_seed[str(s)]['adaptive_growth']<min(by_seed[str(s)][n] for n in ('cv_growth','fixed_two','fixed_five','matched_elasticnet','full_omp_five','old_support_only')) for s in seeds),
        'family_non_degradation_10pct':all(by_family[s]['adaptive_growth']<=1.1*min(by_family[s][n] for n in ('cv_growth','fixed_two','fixed_five','matched_elasticnet','full_omp_five','old_support_only')) for s in families),
        'adaptive_capacity_response':growth['four_quad']>=growth['two_quad']+1.,
        'old_exact':all(len({tuple(a['old_predictions']) for a in c['arms'].values()})==1 for c in cases),
        'vs_frozen_20pct':cand<=.8*metrics['old_frozen']['cold_mse'],
        'shuffled_negative_20pct':cand<=.8*metrics['shuffled_negative']['cold_mse']
    }
    critical=('vs_strongest_5pct','vs_matched_cv_3pct','both_seed_strongest','family_non_degradation_10pct')
    promote=all(gates[k] for k in critical) and sum(gates.values())>=8
    return dict(metrics=metrics,by_seed=by_seed,by_family=by_family,avg_growth=growth,gates=gates,critical=list(critical),passed=sum(gates.values()),total_gates=len(gates),classification='SCREEN_PROMISING' if promote else 'SCREEN_NO_GO')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,nargs='+',required=True);ap.add_argument('--worlds',type=int,default=4);ap.add_argument('--out',required=True);args=ap.parse_args()
    start=time.perf_counter();cases=[score_case(s,f,i) for s in args.seeds for f in FAMILIES for i in range(args.worlds)]
    result=dict(schema='energy67.screen.v1',seeds=args.seeds,worlds=args.worlds,families=list(FAMILIES),cases=cases,aggregate=aggregate(cases),runtime_seconds=time.perf_counter()-start)
    Path(args.out).write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(dict(worlds=len(cases),result=result['aggregate']['classification'],scores={k:round(v['cold_mse'],6) for k,v in result['aggregate']['metrics'].items()},gates=result['aggregate']['gates'],runtime_seconds=result['runtime_seconds']),indent=2))
if __name__=='__main__':main()
