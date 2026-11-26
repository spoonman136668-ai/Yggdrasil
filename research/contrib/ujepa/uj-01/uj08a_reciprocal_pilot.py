"""UJ08A F0: learned reciprocal edges; factorial transfer, synthetic DEV only."""
import argparse
import itertools
import re
import time
from pathlib import Path
import torch
from torch import nn
import uj05a_stability_pilot as a
import uj06a_local_pilot as c
import uj07a_residual_pilot as e
import uj04x_dynamics_pilot as x
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

CANDIDATE='reciprocal_edges'
DIRECT='directed_edges'
NEGATIVE='reciprocal_shuffled_outcomes'
NEW=(CANDIDATE,DIRECT,NEGATIVE)
ARMS=e.ARMS+NEW
NEGATIVES=(e.NEGATIVE,NEGATIVE)
CONTROLS=tuple(k for k in ARMS if k not in (CANDIDATE,)+NEGATIVES)
POSITIVE=e.POSITIVE+(CANDIDATE,DIRECT)
SEEDS=(3601,3602,3603)
FIT_SEED=361100
FAMILIAR_SEED=361200
TRANSFER_SEED=361300
EPOCHS=e.EPOCHS
BATCH=e.BATCH
HORIZON=e.HORIZON
ARM_SECONDS=360
TOTAL_SECONDS=19200
prepare=e.prepare
datahash=e.datahash
evaluate=e.evaluate
batch=e.batch

class InteractionCell(x.Cell):
    """Antisymmetric edge output, with unrestricted learned local dynamics."""
    def __init__(self,reciprocal):
        super().__init__(False)
        self.reciprocal=reciprocal
        # Replace, rather than retain, the unused original interaction trunk.
        self.edge=nn.Sequential(nn.Linear(7,32),nn.SiLU(),nn.Linear(32,32),nn.SiLU(),nn.Linear(32,2))
        self.trunk=nn.Sequential(nn.Linear(6,64),nn.SiLU(),nn.Linear(64,64),nn.SiLU())
        self.predict=nn.Linear(66,16)

    def edge_messages(self,own,other):
        mask=other[...,2:3]
        if not bool(((mask==0)|(mask==1)).all()):raise ValueError('mask')
        center=own[...,None,:2].expand(*other.shape[:-1],2)
        context=own[...,None,3:6].expand(*other.shape[:-1],3)
        neighbor=other[...,:2]
        forward=self.edge(torch.cat((center,neighbor,context),-1))
        reverse=self.edge(torch.cat((neighbor,center,context),-1))
        # Same feature access, parameters, two evaluations and tensor shape.
        messages=(forward-reverse)*.5 if self.reciprocal else forward+0.*reverse
        return messages*mask

    def heads(self,own,other):
        finite(own,other)
        if own.shape[-1]!=6 or other.shape!=own.shape[:-1]+(3,3):
            raise ValueError('feature shape')
        h=self.trunk(own)
        edges=self.edge_messages(own,other).sum(-2)
        pred=self.result(h)+edges
        z=self.predict(torch.cat((h,edges),-1)).tanh()
        finite(pred,z)
        return pred,z

def schedule(arm,epoch):
    return a.schedule('relational_teacher',epoch) if arm in NEW else e.schedule(arm,epoch)

def emit(event,**fields):
    print('UJ08A '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    history=set()
    for bases in ((301100,301200,301300),(311100,311200,311300),(321100,321200,321300),(331100,331200,331300),(341100,341200,341300),(351100,351200,351300)):
        for start,n in zip(bases,(6,6,16)):history.update(range(start,start+n))
    if any(r & history for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&set(range(3001,3504)):
        raise RuntimeError('training seed overlap')

def graph(n,novel):
    if not novel:return x.graph(n,'path')
    if n not in (4,8):raise ValueError('factorial size')
    # Same topology construction at both sizes, not confounded by size.
    edges=[(i,i+1) for i in range(n-1)]+[(0,n-1),(0,2)]
    neighbors=[[] for _ in range(n)]
    for i,j in edges:
        neighbors[i].append(j);neighbors[j].append(i)
    if any(not 1<=len(v)<=3 or len(v)!=len(set(v)) for v in neighbors):
        raise ValueError('graph degree')
    return (torch.tensor([v+[0]*(3-len(v)) for v in neighbors]),
            torch.tensor([[1.]*len(v)+[0.]*(3-len(v)) for v in neighbors]))

def cases(seed,count,transfer=False):
    if not transfer:return e.cases(seed,count)
    if count%4:raise ValueError('balanced factorial count')
    out=[]
    for n,novel,shift,intermediate in itertools.product((4,8),(False,True),(False,True),(False,True)):
        g=torch.Generator().manual_seed(seed+len(out))
        idx,mask=graph(n,novel)
        s,_,params=x.sample(count,n,0.,g,shift=shift)
        # Both regimes and both intervention durations balanced within each stratum.
        params[:,2]=torch.tensor([(.25,.75)[(j//2)%2] if intermediate else (0.,1.)[(j//2)%2] for j in range(count)])
        actions=torch.rand(count,16,n,1,generator=g)*2-1
        site=torch.randint(n,(count,),generator=g)
        plus=actions.clone();minus=actions.clone()
        for j in range(count):
            duration=1 if j%2==0 else 4
            value=actions[j,:duration,site[j],0]*.6
            plus[j,:duration,site[j],0]=value+.4
            minus[j,:duration,site[j],0]=value-.4
        order=torch.rand(count,3,generator=g).argsort(-1)
        name=f'{n}:{int(novel)}:{int(shift)}:{int(intermediate)}'
        out.append((name,s,params,idx,mask,plus,minus,order))
    return out

def loss_for(model,arm,row,perm,deadline,chunk):
    if arm not in NEW or chunk!=1 or not isinstance(model,InteractionCell):
        raise ValueError('interaction arm/schedule')
    if model.reciprocal!=(arm!=DIRECT):raise ValueError('architecture mismatch')
    # Reuse the exact local-only objective and corrupted endpoint control.
    mapped=c.NEGATIVE if arm==NEGATIVE else c.LOCAL[0]
    return c.loss_for(model,mapped,row,perm,deadline,chunk)

def train_interaction(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=InteractionCell(arm!=DIRECT)
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
    if arm in NEW:return train_interaction(arm,seed,fit,familiar,root,overall)
    return e.train(arm,seed,fit,familiar,root,overall)

def valid_training(row):
    if row['arm'] not in NEW:return e.valid_training(row)
    # New trainer retains the exact three mismatch statistics of UJ06A.
    return e.valid_training(dict(row,arm=e.CANDIDATE))

def eligibility(rows,seeds=SEEDS):
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        custody=all(valid_training(r) for r in by.values())
        positive=all(by[k]['adequate'] and by[k]['after']['familiar']['rollout']<=.15 for k in POSITIVE)
        aux=all(by[k]['after']['fit']['rollout']<=.10 and by[k]['after']['familiar']['rollout']<=.15 for k in (e.d.CORRUPTED[0],e.SHUFFLED))
        capacity=by[CANDIDATE]['trainable_params']==by[DIRECT]['trainable_params']==by[NEGATIVE]['trainable_params']
        checks.append(dict(seed=seed,matched_training=custody,positive_mastery=positive,corrupted_aux_prediction_bound=aux,
                           matched_interaction_capacity=capacity,primary=custody and positive and aux and capacity))
    return checks,all(r['primary'] for r in checks)

def prefix(data,horizon):
    if horizon not in (8,16):raise ValueError('horizon')
    return [(name,s,p,i,m,u[:,:horizon],v[:,:horizon],o,ta[:,:horizon],tb[:,:horizon])
            for name,s,p,i,m,u,v,o,ta,tb in data]

def screen(results):
    candidate=results[CANDIDATE]
    controls=tuple(results[k] for k in CONTROLS)+ (results['residual_disabled_inference'],)
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
    if len(rows)!=48 or sum(r['steps'] for r in rows)!=138240 or sum(r['endpoint_steps_exposed'] for r in rows)!=35389440:
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
