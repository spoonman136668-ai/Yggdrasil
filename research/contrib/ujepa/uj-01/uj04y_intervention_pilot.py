"""UJ04Y Y0: matched action-effect learning and independent auxiliary ablation."""
import argparse
from pathlib import Path
import re
import time

import torch
from torch import nn
from torch.nn import functional as F
import uj04x_dynamics_pilot as x
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

ARMS=('dense_pair','relational_no_pair','relational_pair','factorized_no_pair',
      'factorized_pair','factorized_jepa','factorized_shuffled_aux','factorized_shuffled_result')
CORE=ARMS[:5]
SEEDS=(2901,2902,2903)
EPOCHS=80
BATCH=64
ARM_SECONDS=180
TOTAL_SECONDS=3600

def emit(event,**fields):
    print('UJ04Y '+canonical(dict(event=event,**fields)).decode(),flush=True)

class Factorized(x.Cell):
    def __init__(self):
        super().__init__(False)
        self.action_effect=nn.Sequential(nn.Linear(6,32),nn.SiLU(),nn.Linear(32,2))
        self.action_latent=nn.Linear(19,16)

    def heads(self,own,other):
        zero=own.clone()
        zero[...,2]=0
        base,z=super().heads(zero,other)
        effect=self.action_effect(own)-self.action_effect(zero)
        result=base+effect
        latent=self.action_latent(torch.cat((z,effect,own[...,2:3]),-1)).tanh()
        finite(result,latent,effect)
        return result,latent

def make_model(arm):
    if arm not in ARMS:raise ValueError('arm')
    return Factorized() if arm.startswith('factorized') else x.Cell(arm=='dense_pair')

def paired_features(state,plus,minus,params,idx,mask,order):
    a,other=x.features(state,plus,params,idx,mask)
    b,other_b=x.features(state,minus,params,idx,mask)
    if not torch.equal(other,other_b):raise RuntimeError('pair neighbor mismatch')
    other=other.gather(2,order[:,None,:,None].expand(len(state),state.shape[1],3,3))
    return a,b,other

def dataset(seed,count):
    g=torch.Generator().manual_seed(seed)
    rows=[]
    for mix in (0.,1.):
        for kind in ('path','ring','star'):
            idx,mask=x.graph(4,kind)
            state,action,params=x.sample(count,4,mix,g)
            site=torch.randint(4,(count,),generator=g)
            ii=torch.arange(count)
            action[ii,site,0]*=.5
            amplitude=torch.rand(count,generator=g)*.25+.25
            plus=action.clone();minus=action.clone()
            plus[ii,site,0]+=amplitude;minus[ii,site,0]-=amplitude
            order=torch.rand(count,3,generator=g).argsort(-1)
            a,b,other=paired_features(state,plus,minus,params,idx,mask,order)
            ya,yb=x.reference(a,other),x.reference(b,other)
            rows.append((a.reshape(-1,6),b.reshape(-1,6),other.reshape(-1,3,3),ya.reshape(-1,2),yb.reshape(-1,2)))
    return tuple(torch.cat([r[i] for r in rows]) for i in range(5))

def loss_for(model,a,b,other,ya,yb,arm,perm):
    if arm not in ARMS or sorted(perm.tolist())!=list(range(len(ya))):
        raise ValueError('arm or permutation')
    if isinstance(model,Factorized)!=arm.startswith('factorized') or model.dense!=(arm=='dense_pair'):
        raise ValueError('model arm mismatch')
    if not torch.equal(a[...,:2],b[...,:2]) or not torch.equal(a[...,3:],b[...,3:]):
        raise ValueError('unmatched intervention')
    shuffled_a,shuffled_b=ya[perm],yb[perm]
    la,lb=(shuffled_a,shuffled_b) if arm=='factorized_shuffled_result' else (ya,yb)
    ta,tb=(shuffled_a,shuffled_b) if arm in ('factorized_shuffled_aux','factorized_shuffled_result') else (la,lb)
    pa,za=model.heads(a,other);pb,zb=model.heads(b,other)
    ea,eb=model.outcome(la).tanh(),model.outcome(lb).tanh()
    ra,rb=model.reconstruct(ea),model.reconstruct(eb)
    with torch.no_grad():
        target=model.target(ta).tanh()-model.target(tb).tanh()
    contrast=la-lb
    pair_loss=F.mse_loss(pa-pb,contrast)/contrast.square().mean().detach().clamp_min(1e-6)
    aux_loss=F.smooth_l1_loss(za-zb,target)
    endpoint=.5*(F.mse_loss(pa,la)+F.mse_loss(pb,lb))
    reconstruction=.5*(F.mse_loss(ra,la)+F.mse_loss(rb,lb))
    pair_weight=0. if arm.endswith('no_pair') else .25
    aux_weight=.5 if arm in ('factorized_jepa','factorized_shuffled_aux','factorized_shuffled_result') else 0.
    loss=endpoint+reconstruction+pair_weight*pair_loss+aux_weight*aux_loss
    finite(loss,pa,pb,ra,rb,target)
    diff=ya-yb; shuffled_diff=shuffled_a-shuffled_b
    return loss,dict(endpoint_mismatch=float((ya-shuffled_a).square().sum()+(yb-shuffled_b).square().sum()),
        endpoint_power=float(ya.square().sum()+yb.square().sum()),
        contrast_mismatch=float((diff-shuffled_diff).square().sum()),contrast_power=float(diff.square().sum()))

@torch.no_grad()
def errors(model,data):
    a,b,other,ya,yb=data
    pa,_=model.heads(a,other);pb,_=model.heads(b,other)
    den=float(ya.square().sum()+yb.square().sum());effect=ya-yb;ed=float(effect.square().sum())
    if min(den,ed)<=0:raise RuntimeError('zero normalization')
    return dict(endpoint=float((pa-ya).square().sum()+(pb-yb).square().sum())/den,
                effect=float(((pa-pb)-effect).square().sum())/ed)

def train_arm(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=make_model(arm)
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    n=len(fit[0]);before=dict(fit=errors(model,fit),familiar=errors(model,familiar))
    hist=[];steps=exposures=0;totals={}
    for epoch in range(EPOCHS):
        ids=torch.randperm(n,generator=torch.Generator().manual_seed(seed*1000+epoch))
        for ii in ids.split(BATCH):
            check_deadline(deadline)
            perm=torch.randperm(len(ii),generator=torch.Generator().manual_seed(seed*100000+steps))
            opt.zero_grad()
            loss,m=loss_for(model,*(t[ii] for t in fit),arm,perm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
            opt.step();model.ema();finite(*params,*model.target.parameters())
            steps+=1;exposures+=2*len(ii)
            for k,v in m.items():totals[k]=totals.get(k,0.)+v
        if epoch+1 in (40,50,60,70,80):hist.append(errors(model,fit))
    ratios={k:totals[k+'_mismatch']/max(totals[k+'_power'],1e-12) for k in ('endpoint','contrast')}
    if steps!=1920 or exposures!=2*EPOCHS*n or min(ratios.values())<.5:
        raise RuntimeError('exposure or negative mismatch')
    after=dict(fit=hist[-1],familiar=errors(model,familiar))
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if h!=digest(path.read_bytes()):raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,adequate=x.adequate([v['endpoint'] for v in hist]),
        fit_history=hist,steps=steps,examples_exposed=exposures,shuffle_ratios=ratios,
        trainable_params=sum(p.numel() for p in params),checkpoint_sha256=h,
        checkpoint_bytes=path.stat().st_size,wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu),model

def gate(rows,seeds=SEEDS):
    checks=[]
    for seed in seeds:
        a={r['arm']:r for r in rows if r['seed']==seed}
        if set(a)!=set(ARMS):raise RuntimeError('incomplete arms')
        def ok(arm):return a[arm]['adequate'] and a[arm]['after']['familiar']['endpoint']<=.15
        core=all(ok(arm) for arm in CORE)
        checks.append(dict(seed=seed,pair=core,structural=core,
            jepa=core and ok('factorized_jepa') and ok('factorized_shuffled_aux')))
    return checks,{k:all(c[k] for c in checks) for k in ('pair','structural','jepa')}

def cohort():
    out=[]
    for n in (6,8):
        for kind in ('tree','chord'):
            for mix in (.25,.75):
                for duration in (1,4):
                    g=torch.Generator().manual_seed(291003+len(out))
                    idx,mask=x.graph(n,kind)
                    initial,_,params=x.sample(24,n,mix,g,shift=True)
                    actions=torch.rand(16,24,n,1,generator=g)*2-1
                    site=torch.randint(n,(24,),generator=g);ii=torch.arange(24)
                    actions[:duration,ii,site,0]*=.6
                    plus=actions.clone();minus=actions.clone()
                    plus[:duration,ii,site,0]+=.4;minus[:duration,ii,site,0]-=.4
                    out.append(('%d:%s:%s:%d'%(n,kind,mix,duration),initial,params,idx,mask,plus,minus))
    return out

def screen(candidate,controls,negative):
    return (all(v[k]<=.15 for v in candidate['strata'].values() for k in ('rollout','effect'))
        and all(candidate['effect']<=.8*c['effect'] and candidate['rollout']<=1.1*c['rollout'] for c in controls)
        and all(candidate[k]<=.8*negative[k] for k in ('rollout','effect')))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-sha',required=True);p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args();root=a.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',a.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source or exclusive trial directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    fit=dataset(291001,64);familiar=dataset(291002,16)
    if len(fit[0])!=1536 or len(familiar[0])!=384:raise RuntimeError('pair count')
    manifest=dict(source_sha=a.source_sha,fit_sha256=x.tensor_hash(fit),familiar_sha256=x.tensor_hash(familiar),
        seeds=SEEDS,arms=ARMS,epochs=EPOCHS,batch=BATCH,torch=str(torch.__version__),protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[];models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',seed=seed,arm=arm)
            row,model=train_arm(arm,seed,fit,familiar,root,deadline)
            rows.append(row);models[seed,arm]=model;emit('arm_completed',**row)
    checks,eligible=gate(rows);emit('mastery_gate',checks=checks,eligible=eligible)
    scores=[];gates=[];cohort_hash=None
    if any(eligible.values()):
        cases=cohort()
        cohort_hash=digest(canonical([[name,[v.tolist() for v in vals]] for name,*vals in cases]))
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(cases),paired_scenarios=24*len(cases))
        truth=x.targets(cases,deadline)
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=x.evaluate(models[seed,arm],cases,truth,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            d,rn,rp,fn,fp,j,sh,negative=(results[k] for k in ARMS)
            gates.append(dict(seed=seed,pair_pass=eligible['pair'] and screen(fp,(fn,),negative),
                structural_pass=eligible['structural'] and screen(fp,(rp,d),negative),
                jepa_pass=eligible['jepa'] and screen(j,(fp,fn,rp,rn,d,sh),negative)))
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
        examples_exposed=sum(r['examples_exposed'] for r in rows),mastery_checks=checks,eligible=eligible,
        transfer_executed=bool(scores),transfer_checks=gates,
        **{k+'_screen':bool(gates) and all(c[k+'_pass'] for c in gates) for k in ('pair','structural','jepa')},
        scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
        protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
