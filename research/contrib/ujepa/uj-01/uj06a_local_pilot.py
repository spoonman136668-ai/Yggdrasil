"""UJ06A C0: local transition and intervention consistency, synthetic DEV only."""
import argparse
import re
import time
from pathlib import Path
import torch
from torch.nn import functional as F
import uj05a_stability_pilot as a
import uj05b_transfer_pilot as b
import uj04x_dynamics_pilot as x
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

CANDIDATE='relational_local_consistency'
LOCAL=('relational_local_only',CANDIDATE,'relational_local_shuffled')
NEGATIVE='relational_shuffled_outcomes'
CORE=b.CORE
ARMS=CORE+LOCAL+(NEGATIVE,)
CONTROLS=tuple(k for k in ARMS if k not in (CANDIDATE,NEGATIVE))
SEEDS=(3301,3302,3303)
FIT_SEED=331100
FAMILIAR_SEED=331200
TRANSFER_SEED=331300
EPOCHS=a.EPOCHS
BATCH=a.BATCH
HORIZON=a.HORIZON
ARM_SECONDS=360
TOTAL_SECONDS=12000
cases=a.cases
prepare=a.prepare
datahash=a.datahash
evaluate=a.evaluate
batch=a.batch

def schedule(arm,epoch):
    if arm in CORE:return a.schedule(arm,epoch)
    if arm in LOCAL:return a.schedule('relational_teacher',epoch)
    if arm==NEGATIVE:return a.schedule('relational_decay_curriculum',epoch)
    raise ValueError('unknown arm')

def emit(event,**fields):
    print('UJ06A '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    historical=set()
    for bases in ((301100,301200,301300),(311100,311200,311300),(321100,321200,321300)):
        for start,n in zip(bases,(6,6,16)):historical.update(range(start,start+n))
    if any(r & historical for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split seed overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&(set(a.SEEDS)|set(b.SEEDS)|{3001,3002,3003}):
        raise RuntimeError('training seed overlap')

def loss_for(model,arm,row,perm,deadline,chunk):
    if arm not in LOCAL+(NEGATIVE,) or model.dense or sorted(perm.tolist())!=list(range(len(row[1]))):
        raise ValueError('local arm or permutation')
    _,s,p,i,m,u,v,o,ta,tb=row
    if u.shape!=v.shape or u.shape[1]!=HORIZON or ta.shape!=tb.shape:raise ValueError('pair shape')
    if arm in LOCAL and chunk!=1:raise ValueError('local requires teacher resets')
    pa,_=a.trace(model,s,p,i,m,u,o,deadline,ta if chunk<8 else None,chunk)
    pb,_=a.trace(model,s,p,i,m,v,o,deadline,tb if chunk<8 else None,chunk)
    prev_a=torch.cat((s[:,None],ta[:,:-1]),1)
    prev_b=torch.cat((s[:,None],tb[:,:-1]),1)
    da,db=ta-prev_a,tb-prev_b
    delta=da-db
    pd=(pa-prev_a)-(pb-prev_b)
    power=lambda u,v:.5*(u.square().mean()+v.square().mean())
    q,r=pa[:,a.SELECT]-s[:,None],pb[:,a.SELECT]-s[:,None]
    t,z=ta[:,a.SELECT]-s[:,None],tb[:,a.SELECT]-s[:,None]
    st,sz=t[perm],z[perm]
    la,lb=(st,sz) if arm==NEGATIVE else (t,z)
    contrast=la-lb
    endpoint=.5*(F.mse_loss(q,la)+F.mse_loss(r,lb))/power(la,lb).detach().clamp_min(1e-6)
    paired=F.mse_loss(q-r,contrast)/contrast.square().mean().detach().clamp_min(1e-6)
    rec=.5*(F.mse_loss(model.reconstruct(model.outcome(la).tanh()),la)+F.mse_loss(model.reconstruct(model.outcome(lb).tanh()),lb))
    loss=endpoint+.25*paired+rec
    if arm in LOCAL:
        local=.5*(F.mse_loss(pa-prev_a,da)+F.mse_loss(pb-prev_b,db))/power(da,db).detach().clamp_min(1e-6)
        target=delta[perm] if arm=='relational_local_shuffled' else delta
        consistency=F.mse_loss(pd,target)/target.square().mean().detach().clamp_min(1e-6)
        loss=loss+.25*local+(.25 if arm!=LOCAL[0] else 0.)*consistency
    finite(loss)
    return loss,(float((t-st).square().sum()+(z-sz).square().sum()),float(t.square().sum()+z.square().sum()),
        float(((t-z)-(st-sz)).square().sum()),float((t-z).square().sum()),
        float((delta-delta[perm]).square().sum()),float(delta.square().sum()))

def train_local(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=x.Cell(False)
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    before=dict(fit=evaluate(model,fit,deadline),familiar=evaluate(model,familiar,deadline))
    hist=[];steps=exposure=0;totals=[0.]*6
    for epoch in range(EPOCHS):
        chunk,lr=schedule(arm,epoch)
        for group in opt.param_groups:group['lr']=lr
        g=torch.Generator().manual_seed(seed*1000+epoch)
        for j in torch.randperm(len(fit),generator=g).tolist():
            row=fit[j]
            for ids in torch.randperm(len(row[1]),generator=g).split(BATCH):
                check_deadline(deadline)
                perm=torch.randperm(len(ids),generator=torch.Generator().manual_seed(seed*100000+steps))
                opt.zero_grad()
                loss,metrics=loss_for(model,arm,batch(row,ids),perm,deadline,chunk)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
                opt.step();model.ema();finite(*params,*model.target.parameters())
                steps+=1;exposure+=2*len(ids)*HORIZON
                totals=[a+b for a,b in zip(totals,metrics)]
        if epoch+1 in (100,105,110,115,120):
            hist.append(evaluate(model,fit,deadline)['rollout'])
    if steps!=24*EPOCHS or exposure!=2*384*HORIZON*EPOCHS or min(totals[1],totals[3],totals[5])<=0:
        raise RuntimeError('exposure mismatch')
    ratios=(totals[0]/totals[1],totals[2]/totals[3],totals[4]/totals[5])
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

def train(arm,seed,fit,familiar,root,overall):
    if arm in CORE:return a.train(arm,seed,fit,familiar,root,overall)
    return train_local(arm,seed,fit,familiar,root,overall)

def eligibility(rows,seeds=SEEDS):
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        ok=all(by[k]['adequate'] and 0<=by[k]['after']['familiar']['rollout']<=.15 for k in ARMS if k!=NEGATIVE)
        checks.append(dict(seed=seed,primary=ok))
    return checks,all(c['primary'] for c in checks)

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
                  seeds=SEEDS,data_seed_bases=(FIT_SEED,FAMILIAR_SEED,TRANSFER_SEED),arms=ARMS,epochs=EPOCHS,batch=BATCH,horizon=HORIZON,schedules={a:[schedule(a,e) for e in (0,15,30,45,59,119)] for a in ARMS},torch=str(torch.__version__),
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
    if eligible:
        data=prepare(cases(TRANSFER_SEED,24,True),deadline);cohort_hash=datahash(data)
        if len(data)!=16 or sum(len(r[1]) for r in data)!=384:raise RuntimeError('transfer count')
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(data),paired_scenarios=24*len(data))
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],data,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            controls=tuple(results[k] for k in CONTROLS)
            rr=results[CANDIDATE];neg=results[NEGATIVE]
            gates.append(dict(seed=seed,primary=eligible and y.screen(rr,controls,neg)))
    if len(rows)!=30 or sum(r['steps'] for r in rows)!=86400 or sum(r['endpoint_steps_exposed'] for r in rows)!=22118400:
        raise RuntimeError('aggregate exposure mismatch')
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
               endpoint_steps_exposed=sum(r['endpoint_steps_exposed'] for r in rows),
               mastery_checks=checks,eligible=eligible,transfer_executed=bool(scores),transfer_checks=gates,
               primary_screen=bool(gates) and all(g['primary'] for g in gates),
               scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
               protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
