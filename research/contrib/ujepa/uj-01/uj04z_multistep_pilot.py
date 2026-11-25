"""UJ04Z: paired self-fed trajectories, matched teacher and JEPA controls."""
import argparse
from pathlib import Path
import re
import time
import torch
from torch.nn import functional as F
import uj04x_dynamics_pilot as x
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical, digest, check_deadline
from uj04u_stability_pilot import finite

ARMS=('dense_teacher','dense_rollout','relational_teacher','relational_rollout',
      'relational_jepa','relational_shuffled_aux','relational_shuffled_result')
SEEDS=(3001,3002,3003)
EPOCHS=40
BATCH=16
HORIZON=8
FIT_SEED=301100
FAMILIAR_SEED=301200
TRANSFER_SEED=301300
SELECT=(0,1,3,7)
ARM_SECONDS=360
TOTAL_SECONDS=9000

def emit(event,**fields):
    print('UJ04Z '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    if any(a & b for i,a in enumerate(ranges) for b in ranges[i+1:]):
        raise RuntimeError('split seed overlap')

def cases(seed,count,transfer=False):
    out=[]
    sizes=(6,8) if transfer else (4,)
    kinds=('tree','chord') if transfer else ('path','ring','star')
    mixes=(.25,.75) if transfer else (0.,1.)
    for n in sizes:
        for kind in kinds:
            for mix in mixes:
                for duration in ((1,4) if transfer else (None,)):
                    g=torch.Generator().manual_seed(seed+len(out))
                    idx,mask=x.graph(n,kind)
                    initial,_,params=x.sample(count,n,mix,g,shift=transfer)
                    actions=torch.rand(count,16 if transfer else HORIZON,n,1,generator=g)*2-1
                    site=torch.randint(n,(count,),generator=g)
                    plus=actions.clone();minus=actions.clone()
                    for i in range(count):
                        d=duration if transfer else (1 if i%2==0 else 4)
                        v=actions[i,:d,site[i],0]*.6
                        plus[i,:d,site[i],0]=v+.4
                        minus[i,:d,site[i],0]=v-.4
                    order=torch.rand(count,3,generator=g).argsort(-1)
                    name=f'{n}:{kind}:{mix}:{duration}'
                    out.append((name,initial,params,idx,mask,plus,minus,order))
    return out

def trace(model,initial,params,idx,mask,actions,order,deadline,teacher=None):
    state=initial
    states=[];latents=[]
    for t,action in enumerate(actions.unbind(1)):
        check_deadline(deadline)
        if teacher is not None and t:
            state=teacher[:,t-1]
        own,other=x.features(state,action,params,idx,mask)
        other=other.gather(2,order[:,None,:,None].expand(len(state),state.shape[1],3,3))
        if model is None:
            delta=x.reference(own,other)
        else:
            delta,z=model.heads(own,other)
            latents.append(z)
        state=state+x.DT*delta
        finite(state)
        states.append(state)
    return torch.stack(states,1), torch.stack(latents,1) if latents else None

@torch.no_grad()
def prepare(raw,deadline):
    out=[]
    for name,s,p,i,m,a,b,o in raw:
        pa,_=trace(None,s,p,i,m,a,o,deadline)
        pb,_=trace(None,s,p,i,m,b,o,deadline)
        out.append((name,s,p,i,m,a,b,o,pa,pb))
    return out

def datahash(raw):
    return digest(canonical([[r[0],[v.tolist() for v in r[1:]]] for r in raw]))

def loss_for(model,arm,row,perm,deadline):
    _,s,p,i,m,a,b,o,ta,tb=row
    if arm not in ARMS or model.dense!=arm.startswith('dense') or sorted(perm.tolist())!=list(range(len(s))):
        raise ValueError('arm or permutation')
    if a.shape!=b.shape or a.shape[1]!=HORIZON or ta.shape!=tb.shape:
        raise ValueError('pair shape')
    teacher=arm.endswith('teacher')
    pa,za=trace(model,s,p,i,m,a,o,deadline,ta if teacher else None)
    pb,zb=trace(model,s,p,i,m,b,o,deadline,tb if teacher else None)
    pa,pb=pa[:,SELECT]-s[:,None],pb[:,SELECT]-s[:,None]
    ta,tb=ta[:,SELECT]-s[:,None],tb[:,SELECT]-s[:,None]
    za,zb=za[:,SELECT],zb[:,SELECT]
    sa,sb=ta[perm],tb[perm]
    la,lb=(sa,sb) if arm.endswith('shuffled_result') else (ta,tb)
    aa,ab=(sa,sb) if arm in ('relational_shuffled_aux','relational_shuffled_result') else (la,lb)
    power=lambda u,v: .5*(u.square().mean()+v.square().mean())
    endpoint=.5*(F.mse_loss(pa,la)+F.mse_loss(pb,lb))/power(la,lb).detach().clamp_min(1e-6)
    contrast=la-lb
    pair=F.mse_loss(pa-pb,contrast)/contrast.square().mean().detach().clamp_min(1e-6)
    rec_a=model.reconstruct(model.outcome(la).tanh())
    rec_b=model.reconstruct(model.outcome(lb).tanh())
    rec=.5*(F.mse_loss(rec_a,la)+F.mse_loss(rec_b,lb))
    with torch.no_grad():
        target=model.target(aa).tanh()-model.target(ab).tanh()
    aux=F.smooth_l1_loss(za-zb,target)
    loss=endpoint+.25*pair+rec+(.5 if arm in ('relational_jepa','relational_shuffled_aux','relational_shuffled_result') else 0.)*aux
    finite(loss,target)
    return loss, (float((ta-sa).square().sum()+(tb-sb).square().sum()),
                  float(ta.square().sum()+tb.square().sum()),
                  float(((ta-tb)-(sa-sb)).square().sum()),
                  float((ta-tb).square().sum()))

def batch(row,ids):
    name,s,p,i,m,a,b,o,ta,tb=row
    return name,s[ids],p[ids],i,m,a[ids],b[ids],o[ids],ta[ids],tb[ids]

@torch.no_grad()
def evaluate(model,data,deadline):
    strata={}
    for name,s,p,i,m,a,b,o,ta,tb in data:
        pa,_=trace(model,s,p,i,m,a,o,deadline)
        pb,_=trace(model,s,p,i,m,b,o,deadline)
        denom=float((ta-s[:,None]).square().sum()+(tb-s[:,None]).square().sum())
        effect=ta-tb; ed=float(effect.square().sum())
        if min(denom,ed)<=0:raise RuntimeError('zero denominator')
        strata[name]=dict(rollout=float((pa-ta).square().sum()+(pb-tb).square().sum())/denom,
                          effect=float(((pa-pb)-effect).square().sum())/ed)
    return dict(strata=strata,**{k:sum(v[k] for v in strata.values())/len(strata) for k in ('rollout','effect')})

def train(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=x.Cell(arm.startswith('dense'))
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    before=dict(fit=evaluate(model,fit,deadline),familiar=evaluate(model,familiar,deadline))
    hist=[];steps=exposure=0;totals=[0.]*4
    for epoch in range(EPOCHS):
        g=torch.Generator().manual_seed(seed*1000+epoch)
        for j in torch.randperm(len(fit),generator=g).tolist():
            row=fit[j]
            for ids in torch.randperm(len(row[1]),generator=g).split(BATCH):
                check_deadline(deadline)
                perm=torch.randperm(len(ids),generator=torch.Generator().manual_seed(seed*100000+steps))
                opt.zero_grad()
                loss,metrics=loss_for(model,arm,batch(row,ids),perm,deadline)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
                opt.step();model.ema();finite(*params,*model.target.parameters())
                steps+=1;exposure+=2*len(ids)*HORIZON
                totals=[a+b for a,b in zip(totals,metrics)]
        if epoch+1 in (20,25,30,35,40):
            hist.append(evaluate(model,fit,deadline)['rollout'])
    if steps!=960 or exposure!=2*384*HORIZON*EPOCHS or min(totals[1],totals[3])<=0:
        raise RuntimeError('exposure mismatch')
    ratios=(totals[0]/totals[1],totals[2]/totals[3])
    if min(ratios)<.5:raise RuntimeError('negative mismatch')
    after=dict(fit=evaluate(model,fit,deadline),familiar=evaluate(model,familiar,deadline))
    path=root/f'{arm}-{seed}.pt'
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if h!=digest(path.read_bytes()):raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,adequate=x.adequate(hist),
                fit_history=hist,steps=steps,endpoint_steps_exposed=exposure,
                shuffle_ratios=ratios,trainable_params=sum(p.numel() for p in params),
                checkpoint_sha256=h,checkpoint_bytes=path.stat().st_size,
                wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu),model

def eligibility(rows,seeds=SEEDS):
    checks=[]
    for seed in seeds:
        a={r['arm']:r for r in rows if r['seed']==seed}
        if set(a)!=set(ARMS):raise RuntimeError('incomplete arms')
        def ok(k):return a[k]['adequate'] and a[k]['after']['familiar']['rollout']<=.15
        core=all(ok(k) for k in ARMS[:4])
        checks.append(dict(seed=seed,primary=core,jepa=core and ok(ARMS[4]) and ok(ARMS[5])))
    return checks,{k:all(c[k] for c in checks) for k in ('primary','jepa')}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha',required=True);parser.add_argument('--receipt',type=Path,required=True)
    a=parser.parse_args();root=a.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',a.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source or exclusive trial directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    assert_disjoint_seeds()
    fit=prepare(cases(FIT_SEED,64),deadline);familiar=prepare(cases(FAMILIAR_SEED,16),deadline)
    if sum(len(r[1]) for r in fit)!=384 or sum(len(r[1]) for r in familiar)!=96:
        raise RuntimeError('dataset count')
    manifest=dict(source_sha=a.source_sha,fit_sha256=datahash(fit),familiar_sha256=datahash(familiar),
                  seeds=SEEDS,data_seed_bases=(FIT_SEED,FAMILIAR_SEED,TRANSFER_SEED),arms=ARMS,epochs=EPOCHS,batch=BATCH,horizon=HORIZON,torch=str(torch.__version__),
                  protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[];models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',arm=arm,seed=seed)
            row,model=train(arm,seed,fit,familiar,root,deadline)
            rows.append(row);models[seed,arm]=model;emit('arm_completed',**row)
    checks,eligible=eligibility(rows);emit('mastery_gate',checks=checks,eligible=eligible)
    scores=[];gates=[];cohort_hash=None
    if any(eligible.values()):
        data=prepare(cases(TRANSFER_SEED,24,True),deadline);cohort_hash=datahash(data)
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(data),paired_scenarios=24*len(data))
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],data,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            dt,dr,rt,rr,j,sh,neg=(results[k] for k in ARMS)
            gates.append(dict(seed=seed,primary=eligible['primary'] and y.screen(rr,(dt,dr,rt),neg),
                              jepa=eligible['jepa'] and y.screen(j,(dt,dr,rt,rr,sh),neg)))
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
               endpoint_steps_exposed=sum(r['endpoint_steps_exposed'] for r in rows),
               mastery_checks=checks,eligible=eligible,transfer_executed=bool(scores),transfer_checks=gates,
               **{k+'_screen':bool(gates) and all(g[k] for g in gates) for k in ('primary','jepa')},
               scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
               protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
