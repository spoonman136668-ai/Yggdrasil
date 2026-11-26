"""UJ07A E0: bounded local residual correction, isolated synthetic DEV."""
import argparse
import math
import re
import time
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
import uj05a_stability_pilot as a
import uj06a_local_pilot as c
import uj06b_transfer_pilot as d
import uj04x_dynamics_pilot as x
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

CANDIDATE='residual_aligned'
DIRECT='residual_direct'
SHUFFLED='residual_shuffled'
NEW=(CANDIDATE,DIRECT,SHUFFLED)
ARMS=d.ARMS+NEW
CONTROLS=tuple(k for k in ARMS if k not in (CANDIDATE,d.NEGATIVE))
POSITIVE=d.POSITIVE+(CANDIDATE,DIRECT)
NEGATIVE=d.NEGATIVE
SEEDS=(3501,3502,3503)
FIT_SEED=351100
FAMILIAR_SEED=351200
TRANSFER_SEED=351300
EPOCHS=d.EPOCHS
BATCH=d.BATCH
HORIZON=d.HORIZON
ARM_SECONDS=360
TOTAL_SECONDS=15600
BOUND=.5
cases=d.cases
prepare=d.prepare
datahash=d.datahash
evaluate=d.evaluate
batch=a.batch

class ResidualCell(x.Cell):
    def __init__(self):
        super().__init__(False)
        self.correct=nn.Sequential(nn.Linear(24,32),nn.SiLU(),nn.Linear(32,2))
        nn.init.zeros_(self.correct[-1].weight)
        nn.init.zeros_(self.correct[-1].bias)
        self.enabled=True

    def parts(self,own,other):
        base,z=super().heads(own,other)
        # The local corrector sees only current state/action, latent and provisional prediction.
        corr=BOUND*self.correct(torch.cat((own,z.detach(),base.detach()),-1)).tanh()
        finite(base,corr)
        return base,z,corr

    def heads(self,own,other):
        base,z,corr=self.parts(own,other)
        return base+(corr if self.enabled else torch.zeros_like(corr)),z

def schedule(arm,epoch):
    return a.schedule('relational_decay_full',epoch) if arm in NEW else d.schedule(arm,epoch)

def emit(event,**fields):
    print('UJ07A '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    history=set()
    for bases in ((301100,301200,301300),(311100,311200,311300),(321100,321200,321300),(331100,331200,331300),(341100,341200,341300)):
        for start,n in zip(bases,(6,6,16)):history.update(range(start,start+n))
    if any(r & history for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&set(range(3001,3404)):
        raise RuntimeError('training seed overlap')

def trace_residual(model,s,p,i,m,actions,o,truth,deadline):
    state=s
    states=[];corrections=[];targets=[]
    for t,action in enumerate(actions.unbind(1)):
        check_deadline(deadline)
        own,other=x.features(state,action,p,i,m)
        other=other.gather(2,o[:,None,:,None].expand(len(state),state.shape[1],3,3))
        base,_,corr=model.parts(own,other)
        provisional=state+x.DT*base
        # Target is a training-only observed consequence, never an inference input.
        target=((truth[:,t]-provisional.detach())/x.DT).clamp(-BOUND,BOUND)
        state=provisional+x.DT*corr
        states.append(state);corrections.append(corr);targets.append(target)
        finite(state,target)
    return tuple(torch.stack(v,1) for v in (states,corrections,targets))

def loss_for(model,arm,row,perm,deadline,chunk):
    if arm not in NEW or chunk!=8 or sorted(perm.tolist())!=list(range(len(row[1]))):
        raise ValueError('arm, schedule or permutation')
    _,s,p,i,m,u,v,o,ta,tb=row
    pa,ca,ra=trace_residual(model,s,p,i,m,u,o,ta,deadline)
    pb,cb,rb=trace_residual(model,s,p,i,m,v,o,tb,deadline)
    q,r=pa[:,a.SELECT]-s[:,None],pb[:,a.SELECT]-s[:,None]
    t,z=ta[:,a.SELECT]-s[:,None],tb[:,a.SELECT]-s[:,None]
    power=lambda u,v:.5*(u.square().mean()+v.square().mean())
    contrast=t-z
    endpoint=.5*(F.mse_loss(q,t)+F.mse_loss(r,z))/power(t,z).detach().clamp_min(1e-6)
    pair=F.mse_loss(q-r,contrast)/contrast.square().mean().detach().clamp_min(1e-6)
    rec=.5*(F.mse_loss(model.reconstruct(model.outcome(t).tanh()),t)+F.mse_loss(model.reconstruct(model.outcome(z).tanh()),z))
    la,lb=(ra[perm],rb[perm]) if arm==SHUFFLED else (ra,rb)
    aux=.5*(F.mse_loss(ca,la)+F.mse_loss(cb,lb))
    loss=endpoint+.25*pair+rec+(.0 if arm==DIRECT else .25)*aux
    finite(loss)
    return loss,(float((t-t[perm]).square().sum()+(z-z[perm]).square().sum()),
        float(t.square().sum()+z.square().sum()),
        float((contrast-contrast[perm]).square().sum()),float(contrast.square().sum()),
        float((ra-ra[perm]).square().sum()+(rb-rb[perm]).square().sum()),
        float(ra.square().sum()+rb.square().sum()))

def train_residual(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=ResidualCell()
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
    if arm in NEW:return train_residual(arm,seed,fit,familiar,root,overall)
    return d.train(arm,seed,fit,familiar,root,overall)

def valid_training(r):
    if r['arm'] not in NEW:return d.valid_training(r)
    return (r['steps']==24*EPOCHS and r['endpoint_steps_exposed']==2*384*HORIZON*EPOCHS
        and len(r['fit_history'])==5 and all(d.valid_number(v) for v in r['fit_history'])
        and len(r['shuffle_ratios'])==3 and all(d.valid_number(v) and v>=.5 for v in r['shuffle_ratios'])
        and all(d.valid_number(r['after'][split][metric]) for split in ('fit','familiar') for metric in ('rollout','effect'))
        and bool(re.fullmatch('[0-9a-f]{64}',r['checkpoint_sha256'])) and r['checkpoint_bytes']>0
        and d.valid_number(r['wall_seconds']) and d.valid_number(r['cpu_seconds']))

def eligibility(rows,seeds=SEEDS):
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        custody=all(valid_training(r) for r in by.values())
        positive=all(by[k]['adequate'] and by[k]['after']['familiar']['rollout']<=.15 for k in POSITIVE)
        aux=all(by[k]['after']['fit']['rollout']<=.10 and by[k]['after']['familiar']['rollout']<=.15 for k in (d.CORRUPTED[0],SHUFFLED))
        checks.append(dict(seed=seed,matched_training=custody,positive_mastery=positive,corrupted_aux_prediction_bound=aux,
                           primary=custody and positive and aux))
    return checks,all(r['primary'] for r in checks)

def disabled_score(model,data,deadline):
    if not isinstance(model,ResidualCell) or not model.enabled:raise ValueError('invalid ablation model')
    model.enabled=False
    try:return evaluate(model,data,deadline)
    finally:model.enabled=True

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
                  correction_bound=BOUND,protected_evaluation_accessed=False)
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
            disabled=disabled_score(models[seed,CANDIDATE],data,deadline)
            row=dict(seed=seed,arm='residual_disabled_inference',score=disabled);scores.append(row);emit('transfer_score',**row)
            gates.append(dict(seed=seed,primary=eligible and y.screen(rr,controls+(disabled,),neg)))
    if len(rows)!=39 or sum(r['steps'] for r in rows)!=112320 or sum(r['endpoint_steps_exposed'] for r in rows)!=28753920:
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
