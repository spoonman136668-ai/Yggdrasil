"""Independently authored ENERGY-67 refit auditor, no import of experiment module."""
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np
from scipy.linalg import solve
from sklearn.linear_model import ElasticNet

P=list(itertools.combinations(range(9),2))
Q=list(itertools.combinations(range(9),4))
F=list(itertools.combinations(range(9),5))
POLICIES=('adaptive_growth','cv_growth','fixed_two','fixed_five','matched_elasticnet','full_omp_five','old_support_only','old_frozen','shuffled_negative')


def fmat(x,index):
    a=np.asarray(x,dtype=np.int8)
    return np.asarray([np.prod(a[:,list(t)],axis=1) for t in index],dtype=float).T


def regression(x,y):
    a=np.concatenate((np.ones((len(x),1)),x),axis=1)
    t=a.T@a+np.diag([0]+[.3]*x.shape[1])
    return solve(t,a.T@y,assume_a='pos')


def runreg(x,coeff):
    return coeff[0]+x@coeff[1:]


def order(features,truth,prior,n):
    selected=[]
    for _ in range(n):
        basis=np.column_stack((prior,features[:,selected])) if len(selected) else prior
        residual=truth-runreg(basis,regression(basis,truth))
        values=np.abs(features.T@residual)
        if selected: values[np.asarray(selected,dtype=int)] = -np.inf
        selected.append(int(np.argmax(values)))
    return selected


def close(x,y,source,names,checks):
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    assert a.shape==b.shape,(source,a.shape,b.shape)
    if not np.allclose(a,b,atol=1e-9,rtol=1e-9):
        raise AssertionError(f'{source} max_abs_error={np.max(np.abs(a-b))}')
    checks[0]+=int(a.size)


def assert_equal(a,b,source,checks):
    if a!=b:raise AssertionError(f'{source}: {a} != {b}')
    checks[0]+=1


def reconstruct(seed,family,wid):
    h=hashlib.sha256(f'ENERGY-67:v1:{seed}:{family}:{wid}'.encode()).digest()
    rng=np.random.default_rng(int.from_bytes(h[:8],'little'))
    binary=(1-2*((np.arange(512,dtype=np.uint16)[:,None]>>np.arange(9))&1)).astype(np.int8)
    rng.shuffle(binary,axis=0)
    a,b,ha,hb,hc=binary[:80],binary[80:144],binary[144:192],binary[192:240],binary[240:288]
    ids=rng.choice(36,size=3,replace=False)
    coefficients=rng.choice([-1,1],3)*rng.uniform(.85,1.25,3)
    changed=coefficients*rng.uniform(.92,1.08,3)
    quad_ids=rng.choice(126,size=4,replace=False)
    qcoef=rng.choice([-1,1],4)*rng.uniform(.85,1.2,4)
    count=2 if family=='two_quad' else 4
    fifth_id=int(rng.integers(126))
    fifth_coef=float(rng.choice([-1,1])*1.2) if family=='four_quad_plus_fifth' else 0.
    def y(x,new):
        val=fmat(x,[P[j] for j in ids])@(changed if new else coefficients)
        if new:
            val += fmat(x,[Q[j] for j in quad_ids[:count]])@qcoef[:count]
            if fifth_coef:val+=fifth_coef*fmat(x,[F[fifth_id]]).ravel()
        return val+rng.normal(0,.18,size=len(x))
    return dict(xo=a.tolist(),xn=b.tolist(),ho=ha.tolist(),hn=hb.tolist(),hc=hc.tolist(),
                yo=y(a,False).tolist(),yn=y(b,True).tolist(),yho=y(ha,False).tolist(),
                yhn=y(hb,True).tolist(),yhc=y(hc,True).tolist(),
                planted_pair_ids=ids.tolist(),planted_quad_ids=quad_ids[:count].tolist(),
                planted_fifth_id=fifth_id if fifth_coef else None)


def verify_case(c,checks):
    key=f"{c['seed']}:{c['family']}:{c['world_id']}"
    world=c['world']
    independent=reconstruct(c['seed'],c['family'],c['world_id'])
    for fld in independent:
        if isinstance(independent[fld],list) and fld not in ('planted_pair_ids','planted_quad_ids'):
            close(independent[fld],world[fld],f'{key}/generator/{fld}',[],checks)
        else:assert_equal(independent[fld],world[fld],f'{key}/generator/{fld}',checks)
    ids_all=[tuple(row) for label in ('xo','xn','ho','hn','hc') for row in world[label]]
    assert_equal(len(ids_all),len(set(ids_all)),f'{key}/action_disjoint',checks)
    xold,xnew,xho,xhn,xhc=[np.asarray(world[q],dtype=float) for q in ('xo','xn','ho','hn','hc')]
    yo,yn,yho,yhn,yhc=[np.asarray(world[q],dtype=float) for q in ('yo','yn','yho','yhn','yhc')]
    oldpair=fmat(xold,P)
    learned=order(oldpair,yo,np.empty((len(xold),0)),3)
    assert_equal(learned,c['old_selection']['terms'],f'{key}/oldterms',checks)
    oldweights=regression(oldpair[:,learned],yo)
    close(oldweights,c['old_selection']['coeff'],f'{key}/oldcoef',[],checks)
    oldhold=runreg(fmat(xho,[P[j] for j in learned]),oldweights)
    pairnew=fmat(xnew,[P[j] for j in learned]);pnew=fmat(xhn,[P[j] for j in learned]);pcold=fmat(xhc,[P[j] for j in learned])
    qnew=fmat(xnew,Q);qhn=fmat(xhn,Q);qcold=fmat(xhc,Q)
    steps=order(qnew[:48],yn[:48],pairnew[:48],5)
    assert_equal(steps,c['growth_path'],f'{key}/growth_order',checks)
    scores=[]
    for n in range(6):
        tr=np.column_stack((pairnew[:48],qnew[:48,steps[:n]]))
        va=np.column_stack((pairnew[48:],qnew[48:,steps[:n]]))
        beta=regression(tr,yn[:48]);scores.append(float(np.mean((yn[48:]-runreg(va,beta))**2)))
    close(scores,c['validation_losses'],f'{key}/val_losses',[],checks)
    growing=0
    for k in range(1,6):
        if scores[k]<=.97*scores[k-1]:growing=k
        else:break
    choices={'adaptive_growth':growing,'cv_growth':int(np.argmin(scores)),'fixed_two':2,'fixed_five':5}
    computed={}
    for tag,k in choices.items():
        actual=c['selection'][tag];assert_equal(actual['k'],k,f'{key}/{tag}/capacity',checks)
        assert_equal(actual['terms'],steps[:k],f'{key}/{tag}/support',checks)
        matrix=np.column_stack((pairnew,qnew[:,steps[:k]])); beta=regression(matrix,yn)
        new=runreg(np.column_stack((pnew,qhn[:,steps[:k]])),beta)
        cold=runreg(np.column_stack((pcold,qcold[:,steps[:k]])),beta)
        computed[tag]=(new,cold)
    matrix=np.column_stack((pairnew,qnew))
    values=[]
    for alpha in (.01,.03,.1,.3,1.):
        fit=ElasticNet(alpha=alpha,l1_ratio=.8,max_iter=3000,tol=1e-6,selection='cyclic').fit(matrix[:48],yn[:48])
        values.append(float(np.mean((fit.predict(matrix[48:])-yn[48:])**2)))
    alpha=(.01,.03,.1,.3,1.)[int(np.argmin(values))]
    assert_equal(alpha,c['selection']['matched_elasticnet']['alpha'],f'{key}/elastic_alpha',checks)
    model=ElasticNet(alpha=alpha,l1_ratio=.8,max_iter=3000,tol=1e-6,selection='cyclic').fit(matrix,yn)
    computed['matched_elasticnet']=(model.predict(np.column_stack((pnew,qhn))),model.predict(np.column_stack((pcold,qcold))))
    full=np.column_stack((fmat(xnew,P),qnew))
    path=order(full,yn,np.empty((len(xnew),0)),5)
    assert_equal(path,c['selection']['full_omp_five']['terms'],f'{key}/fullomp_path',checks)
    beta=regression(full[:,path],yn)
    computed['full_omp_five']=(runreg(np.column_stack((fmat(xhn,P),qhn))[:,path],beta),runreg(np.column_stack((fmat(xhc,P),qcold))[:,path],beta))
    beta=regression(pairnew,yn)
    computed['old_support_only']=(runreg(pnew,beta),runreg(pcold,beta))
    computed['old_frozen']=(runreg(pnew,oldweights),runreg(pcold,oldweights))
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(f"ENERGY-67:v1:{c['seed']}:{c['family']}:{c['world_id']}".encode()).digest()[:8],'little')+999)
    sham=yn[rng.permutation(64)]
    bad=order(qnew[:48],sham[:48],pairnew[:48],5)
    assert_equal(bad,c['selection']['shuffled_negative']['terms'],f'{key}/negative_terms',checks)
    beta=regression(np.column_stack((pairnew,qnew[:,bad])),sham)
    computed['shuffled_negative']=(runreg(np.column_stack((pnew,qhn[:,bad])),beta),runreg(np.column_stack((pcold,qcold[:,bad])),beta))
    for name,(pred_new,pred_cold) in computed.items():
        out=c['arms'][name]
        close(pred_new,out['new_predictions'],f'{key}/{name}/pred_new',[],checks)
        close(pred_cold,out['cold_predictions'],f'{key}/{name}/pred_cold',[],checks)
        close(oldhold,out['old_predictions'],f'{key}/{name}/pred_old',[],checks)
        for flag,pred,truth in [('new',pred_new,yhn),('cold',pred_cold,yhc),('old',oldhold,yho)]:
            close([float(np.mean((pred-truth)**2))],[out[flag+'_mse']],f'{key}/{name}/{flag}_loss',[],checks)


def main():
    arg=argparse.ArgumentParser();arg.add_argument('scores');arg.add_argument('--out',required=True);args=arg.parse_args()
    source=json.loads(Path(args.scores).read_text());checks=[0];
    assert len(source['cases'])==12*len(source['seeds']) if source['worlds']==4 else len(source['cases'])==3*source['worlds']*len(source['seeds'])
    for c in source['cases']: verify_case(c,checks)
    # Independently re-aggregate without importing scorer
    for name in POLICIES:
        for metric in ('old_mse','new_mse','cold_mse'):
            observed=float(np.mean([case['arms'][name][metric] for case in source['cases']]))
            close([observed],[source['aggregate']['metrics'][name][metric]],'aggregate/'+name+'/'+metric,[],checks)
    receipt=dict(schema='energy67.audit.v1',audit_result='PASS',worlds=len(source['cases']),checks=checks[0],source_sha256=hashlib.sha256(Path(args.scores).read_bytes()).hexdigest(),scorer_imported=False,independence='independently authored auditor, shared numpy/sklearn and same source-defined synthetic generator semantics')
    Path(args.out).write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
