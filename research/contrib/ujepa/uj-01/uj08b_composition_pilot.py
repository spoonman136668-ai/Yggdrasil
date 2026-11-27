"""UJ08B G0: endpoint composition with reciprocal interactions; synthetic DEV only."""
import argparse
import re
import time
from pathlib import Path
import torch
from torch.nn import functional as F
import uj08a_reciprocal_pilot as f
import uj05a_stability_pilot as a
import uj07a_residual_pilot as e
import uj04x_dynamics_pilot as x
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

CANDIDATE='composed_full'
COMPOSED_TEACHER='composed_teacher'
DIRECT_FULL='unrestricted_full'
DIRECT_TEACHER='unrestricted_teacher'
NEGATIVE='composed_corrupted'
NEW=(CANDIDATE,COMPOSED_TEACHER,DIRECT_FULL,DIRECT_TEACHER,NEGATIVE)
ARMS=f.ARMS+NEW
NEGATIVES=f.NEGATIVES+(NEGATIVE,)
CONTROLS=tuple(k for k in ARMS if k not in (CANDIDATE,)+NEGATIVES)
POSITIVE=f.POSITIVE+NEW[:-1]
SEEDS=(3701,3702,3703)
FIT_SEED=371100
FAMILIAR_SEED=371200
TRANSFER_SEED=371300
EPOCHS=f.EPOCHS
BATCH=f.BATCH
HORIZON=f.HORIZON
ARM_SECONDS=360
TOTAL_SECONDS=24000
prepare=f.prepare
datahash=f.datahash
evaluate=f.evaluate
batch=f.batch
cases=f.cases
prefix=f.prefix

class CompositionCell(f.InteractionCell):
    """Shared weights; explicit interpolation vs unrestricted context control."""
    def __init__(self,composed):
        super().__init__(True)
        self.composed=composed

    def heads(self,own,other):
        finite(own,other)
        m=own[...,5:6]
        if not bool(((m>=0)&(m<=1)).all()):raise ValueError('regime range')
        core=own[...,:5]
        left=torch.cat((core,torch.zeros_like(m) if self.composed else m),-1)
        right=torch.cat((core,torch.ones_like(m) if self.composed else m),-1)
        p0,z0=super().heads(left,other)
        p1,z1=super().heads(right,other)
        # Both arms evaluate the identical shared network twice.
        # At endpoints the selected prediction and its gradients coincide.
        pred=(1-m)*p0+m*p1
        z=(1-m)*z0+m*z1
        finite(pred,z)
        return pred,z

def schedule(arm,epoch):
    if arm in NEW:
        return a.schedule('relational_teacher' if arm in (COMPOSED_TEACHER,DIRECT_TEACHER) else 'relational_decay_full',epoch)
    return f.schedule(arm,epoch)

def emit(event,**fields):
    print('UJ08B '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    f.assert_disjoint_seeds()
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    history=set()
    for bases in ((301100,301200,301300),(311100,311200,311300),(321100,321200,321300),(331100,331200,331300),(341100,341200,341300),(351100,351200,351300),(361100,361200,361300)):
        for start,n in zip(bases,(6,6,16)):history.update(range(start,start+n))
    if any(r & history for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&set(range(3001,3604)):
        raise RuntimeError('training seed overlap')

def loss_for(model,arm,row,perm,deadline,chunk):
    if arm not in NEW or not isinstance(model,CompositionCell) or chunk!=schedule(arm,0)[0]:
        raise ValueError('composition arm/schedule')
    if model.composed!=(arm in (CANDIDATE,COMPOSED_TEACHER,NEGATIVE)):
        raise ValueError('composition mismatch')
    _,s,p,i,m,u,v,o,ta,tb=row
    if u.shape!=v.shape or u.shape[1]!=HORIZON or ta.shape!=tb.shape or sorted(perm.tolist())!=list(range(len(s))):
        raise ValueError('pair shape or permutation')
    pa,_=a.trace(model,s,p,i,m,u,o,deadline,ta if chunk<8 else None,chunk)
    pb,_=a.trace(model,s,p,i,m,v,o,deadline,tb if chunk<8 else None,chunk)
    prev_a=torch.cat((s[:,None],ta[:,:-1]),1)
    prev_b=torch.cat((s[:,None],tb[:,:-1]),1)
    delta=(ta-prev_a)-(tb-prev_b)
    pa,pb=pa[:,a.SELECT]-s[:,None],pb[:,a.SELECT]-s[:,None]
    ta,tb=ta[:,a.SELECT]-s[:,None],tb[:,a.SELECT]-s[:,None]
    sa,sb=ta[perm],tb[perm]
    la,lb=(sa,sb) if arm==NEGATIVE else (ta,tb)
    power=lambda u,v:.5*(u.square().mean()+v.square().mean())
    endpoint=.5*(F.mse_loss(pa,la)+F.mse_loss(pb,lb))/power(la,lb).detach().clamp_min(1e-6)
    contrast=la-lb
    pair=F.mse_loss(pa-pb,contrast)/contrast.square().mean().detach().clamp_min(1e-6)
    rec=.5*(F.mse_loss(model.reconstruct(model.outcome(la).tanh()),la)+F.mse_loss(model.reconstruct(model.outcome(lb).tanh()),lb))
    loss=endpoint+.25*pair+rec
    finite(loss)
    return loss,(float((ta-sa).square().sum()+(tb-sb).square().sum()),float(ta.square().sum()+tb.square().sum()),
        float(((ta-tb)-(sa-sb)).square().sum()),float((ta-tb).square().sum()),
        float((delta-delta[perm]).square().sum()),float(delta.square().sum()))

def train_composition(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=CompositionCell(arm in (CANDIDATE,COMPOSED_TEACHER,NEGATIVE))
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
    if arm in NEW:return train_composition(arm,seed,fit,familiar,root,overall)
    return f.train(arm,seed,fit,familiar,root,overall)

def valid_training(row):
    if row['arm'] not in NEW:return f.valid_training(row)
    return e.valid_training(dict(row,arm=e.CANDIDATE))

def eligibility(rows,seeds=SEEDS):
    historical=[r for r in rows if r['arm'] in f.ARMS]
    prior,prior_ok=f.eligibility(historical,seeds)
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        custody=all(valid_training(r) for r in by.values())
        positive=all(by[k]['adequate'] and by[k]['after']['familiar']['rollout']<=.15 for k in POSITIVE)
        capacity=len({by[k]['trainable_params'] for k in NEW})==1 and by[CANDIDATE]['trainable_params']==by[f.CANDIDATE]['trainable_params']
        previous=next(r['primary'] for r in prior if r['seed']==seed)
        checks.append(dict(seed=seed,matched_training=custody,positive_mastery=positive,matched_capacity=capacity,
                           previous_controls=previous,primary=custody and positive and capacity and previous))
    return checks,prior_ok and all(r['primary'] for r in checks)

def screen(results):
    candidate=results[CANDIDATE]
    controls=tuple(results[k] for k in CONTROLS)+(results['residual_disabled_inference'],)
    return all(y.screen(candidate,controls,results[k]) for k in NEGATIVES)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha',required=True);parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args();root=args.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source or exclusive trial directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    assert_disjoint_seeds()
    fit=prepare(cases(FIT_SEED,64),deadline);familiar=prepare(cases(FAMILIAR_SEED,16),deadline)
    if sum(len(r[1]) for r in fit)!=384 or sum(len(r[1]) for r in familiar)!=96:raise RuntimeError('dataset count')
    manifest=dict(source_sha=args.source_sha,fit_sha256=datahash(fit),familiar_sha256=datahash(familiar),
        seeds=SEEDS,data_seed_bases=(FIT_SEED,FAMILIAR_SEED,TRANSFER_SEED),arms=ARMS,epochs=EPOCHS,batch=BATCH,horizon=HORIZON,
        schedules={arm:[schedule(arm,ep) for ep in (0,15,30,45,59,119)] for arm in ARMS},torch=str(torch.__version__),
        transfer_factors=['size','topology','coefficient_shift','intermediate_regime'],protected_evaluation_accessed=False)
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
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(data),paired_scenarios=24*len(data),horizons=[8,16])
        short=prefix(data,8)
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],data,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm],score8=evaluate(models[seed,arm],short,deadline))
                scores.append(row);emit('transfer_score',**row)
            model=models[seed,e.CANDIDATE]
            results['residual_disabled_inference']=e.disabled_score(model,data,deadline)
            row=dict(seed=seed,arm='residual_disabled_inference',score=results['residual_disabled_inference'],
                     score8=e.disabled_score(model,short,deadline))
            scores.append(row);emit('transfer_score',**row)
            gates.append(dict(seed=seed,primary=screen(results)))
    if len(rows)!=63 or sum(r['steps'] for r in rows)!=181440 or sum(r['endpoint_steps_exposed'] for r in rows)!=46448640:
        raise RuntimeError('aggregate exposure mismatch')
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
        endpoint_steps_exposed=sum(r['endpoint_steps_exposed'] for r in rows),mastery_checks=checks,eligible=eligible,
        transfer_executed=bool(scores),transfer_checks=gates,primary_screen=bool(gates) and all(g['primary'] for g in gates),
        scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with args.receipt.open('xb') as f:f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
