"""UJ04X X0: synthetic continuous graph dynamics, independent structural/JEPA gates."""
import argparse
import copy
from pathlib import Path
import re
import time

import torch
from torch import nn
from torch.nn import functional as F
from uj03a_pilot import canonical,digest,check_deadline
from uj04u_stability_pilot import finite

ARMS=('jepa','no_latent','shuffled_aux','shuffled_result','dense')
SEEDS=(2801,2802,2803)
EPOCHS=80
BATCH=64
DT=.08
ARM_SECONDS=180
TOTAL_SECONDS=3600

def emit(event,**fields):
    print('UJ04X '+canonical(dict(event=event,**fields)).decode(),flush=True)

def graph(n,kind):
    edges=[(i,i+1) for i in range(n-1)]
    if kind=='ring': edges.append((0,n-1))
    elif kind=='star':
        if n!=4: raise ValueError('star size')
        edges=[(0,i) for i in range(1,n)]
    elif kind=='tree':
        if n<6: raise ValueError('tree size')
        edges=[(i,i+1) for i in range(n-3)]+[(1,n-2),(n-3,n-1)]
    elif kind=='chord':
        if n<6: raise ValueError('chord size')
        edges.extend(((0,n-1),(1,n-2)))
    elif kind!='path': raise ValueError('graph')
    neighbors=[[] for _ in range(n)]
    for a,b in edges:
        neighbors[a].append(b);neighbors[b].append(a)
    if any(not 1<=len(a)<=3 for a in neighbors): raise ValueError('degree')
    idx=torch.tensor([a+[0]*(3-len(a)) for a in neighbors])
    mask=torch.tensor([[1.]*len(a)+[0.]*(3-len(a)) for a in neighbors])
    return idx,mask

def features(state,action,params,idx,mask):
    b,n,_=state.shape
    own=torch.cat((state,action,params[:,None,:].expand(b,n,3)),dim=-1)
    m=mask[None,:,:,None].expand(b,n,3,1)
    other=torch.cat((state[:,idx,:]*m,m),dim=-1)
    return own,other

def reference(own,other):
    # Reference only. Learners see the same raw features, not this equation.
    x,v,u,k,d,m=own.unbind(-1)
    diff=((other[...,0]-x.unsqueeze(-1))*other[...,2]).sum(-1)
    flow=k*diff+u-d*x
    accel=k*diff+u-d*v
    return torch.stack(((1-m)*flow+m*v,m*accel-(1-m)*d*v),dim=-1)

def sample(b,n,mix,g,shift=False):
    state=torch.rand(b,n,2,generator=g)*2-1
    action=torch.rand(b,n,1,generator=g)*2-1
    params=torch.rand(b,3,generator=g)
    params[:,0]=params[:,0]*.35+(.55 if shift else .15)
    params[:,1]=params[:,1]*.2+(.35 if shift else .1)
    params[:,2]=mix
    return state,action,params

def dataset(seed,count):
    g=torch.Generator().manual_seed(seed)
    rows=[]
    for mix in (0.,1.):
        for kind in ('path','ring','star'):
            idx,mask=graph(4,kind)
            state,action,params=sample(count,4,mix,g)
            own,other=features(state,action,params,idx,mask)
            # Independently permute neighbor slots per graph; masks move with slots.
            order=torch.rand(count,3,generator=g).argsort(-1)
            other=other.gather(2,order[:,None,:,None].expand(count,4,3,3))
            target=reference(own,other)
            rows.append((own.reshape(-1,6),other.reshape(-1,3,3),target.reshape(-1,2)))
    return tuple(torch.cat([r[i] for r in rows]) for i in range(3))

def tensor_hash(values):
    return digest(canonical([t.tolist() for t in values]))

class Cell(nn.Module):
    def __init__(self,dense=False):
        super().__init__()
        self.dense=dense
        width=72 if dense else 64
        if not dense:
            self.edge=nn.Sequential(nn.Linear(9,32),nn.SiLU(),nn.Linear(32,16))
        self.trunk=nn.Sequential(nn.Linear(15 if dense else 22,width),nn.SiLU(),
            nn.Linear(width,width),nn.SiLU())
        self.result=nn.Linear(width,2)
        self.predict=nn.Linear(width,16)
        self.outcome=nn.Sequential(nn.Linear(2,32),nn.SiLU(),nn.Linear(32,16))
        self.reconstruct=nn.Linear(16,2)
        self.target=copy.deepcopy(self.outcome).requires_grad_(False)

    def heads(self,own,other):
        finite(own,other)
        if own.shape[-1]!=6 or other.shape!=own.shape[:-1]+(3,3):
            raise ValueError('feature shape')
        mask=other[...,2:3]
        if not bool(((mask==0)|(mask==1)).all()):raise ValueError('mask')
        other=other*mask
        if self.dense: info=other.flatten(-2)
        else:
            center=own.unsqueeze(-2).expand(*other.shape[:-1],6)
            info=(self.edge(torch.cat((center,other),-1))*mask).sum(-2)
        h=self.trunk(torch.cat((own,info),-1))
        pred,z=self.result(h),self.predict(h).tanh()
        finite(pred,z)
        return pred,z

    @torch.no_grad()
    def ema(self):
        for target,online in zip(self.target.parameters(),self.outcome.parameters()):
            target.mul_(.99).add_(online,alpha=.01)

def loss_for(model,own,other,y,arm,perm):
    if arm not in ARMS or model.dense!=(arm=='dense') or sorted(perm.tolist())!=list(range(len(y))):
        raise ValueError('arm or permutation')
    shuffled=y[perm]
    label=shuffled if arm=='shuffled_result' else y
    aux_target=shuffled if arm in ('shuffled_result','shuffled_aux') else y
    pred,z=model.heads(own,other)
    emb=model.outcome(label).tanh()
    rec=model.reconstruct(emb)
    with torch.no_grad(): expected=model.target(aux_target).tanh()
    loss=F.mse_loss(pred,label)+F.mse_loss(rec,label)+(
        0. if arm in ('no_latent','dense') else .5)*F.smooth_l1_loss(z,expected)
    finite(loss,emb,rec,expected)
    return loss,float((y-shuffled).square().sum()),float(y.square().sum())

@torch.no_grad()
def error(model,data):
    own,other,y=data
    p,_=model.heads(own,other)
    den=float(y.square().sum())
    if den<=0:raise RuntimeError('zero persistence denominator')
    return float((p-y).square().sum())/den

def adequate(history):
    if len(history)!=5:raise ValueError('fit checkpoints')
    last=history[-1];span=max(history)-min(history)
    return last<=.10 and (last<=.01 or span<=.005 or span/max(abs(last),1e-12)<=.05)

def train_arm(arm,seed,fit,familiar,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic();cpu=time.process_time()
    torch.manual_seed(seed)
    model=Cell(arm=='dense')
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    own,other,y=fit
    before=dict(fit=error(model,fit),familiar=error(model,familiar))
    hist=[];steps=exposures=0;diff=power=0.
    for epoch in range(EPOCHS):
        ids=torch.randperm(len(y),generator=torch.Generator().manual_seed(seed*1000+epoch))
        for ii in ids.split(BATCH):
            check_deadline(deadline)
            perm=torch.randperm(len(ii),generator=torch.Generator().manual_seed(seed*100000+steps))
            opt.zero_grad()
            loss,a,b=loss_for(model,own[ii],other[ii],y[ii],arm,perm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
            opt.step();model.ema();finite(*params,*model.target.parameters())
            steps+=1;exposures+=len(ii);diff+=a;power+=b
        if epoch+1 in (40,50,60,70,80):hist.append(error(model,fit))
    if steps!=1920 or exposures!=EPOCHS*len(y) or power<=0 or diff/power<.5:
        raise RuntimeError('exposure or negative control mismatch')
    after=dict(fit=hist[-1],familiar=error(model,familiar))
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if h!=digest(path.read_bytes()):raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,adequate=adequate(hist),
        fit_history=hist,steps=steps,examples_exposed=exposures,shuffle_ratio=diff/power,
        trainable_params=sum(p.numel() for p in params),checkpoint_sha256=h,
        checkpoint_bytes=path.stat().st_size,wall_seconds=time.monotonic()-start,
        cpu_seconds=time.process_time()-cpu),model

def gate(rows,seeds=SEEDS):
    checks=[]
    for seed in seeds:
        a={r['arm']:r for r in rows if r['seed']==seed}
        if set(a)!=set(ARMS):raise RuntimeError('incomplete arms')
        j,n,s,d,z=(a[k] for k in ARMS)
        structural=n['adequate'] and z['adequate'] and n['after']['familiar']<=.15
        aux=structural and j['adequate'] and s['adequate'] and j['after']['familiar']<=.15
        checks.append(dict(seed=seed,structural=structural,jepa=aux))
    return checks,all(c['structural'] for c in checks),all(c['jepa'] for c in checks)

def cohort():
    out=[]
    for n in (6,8):
        for kind in ('tree','chord'):
            for mix in (0.,.5,1.):
                g=torch.Generator().manual_seed(281003+len(out))
                idx,mask=graph(n,kind)
                initial,_,params=sample(24,n,mix,g,shift=True)
                actions=torch.rand(16,24,n,1,generator=g)*2-1
                plus=actions.clone();minus=actions.clone()
                plus[0,:,0,0]+=.5;minus[0,:,0,0]-=.5
                out.append(('%d:%s:%s'%(n,kind,mix),initial,params,idx,mask,plus,minus))
    return out

@torch.no_grad()
def rollout(model,initial,params,idx,mask,actions,deadline):
    state=initial.clone(); trace=[]
    for action in actions:
        check_deadline(deadline)
        own,other=features(state,action,params,idx,mask)
        delta=reference(own,other) if model is None else model.heads(own,other)[0]
        state=state+DT*delta
        finite(state)
        trace.append(state)
    return torch.stack(trace)

def targets(cases,deadline):
    out=[]
    for name,initial,params,idx,mask,plus,minus in cases:
        p=rollout(None,initial,params,idx,mask,plus,deadline)
        m=rollout(None,initial,params,idx,mask,minus,deadline)
        out.append((p,m))
    return out

@torch.no_grad()
def evaluate(model,cases,truth,deadline):
    strata={}
    for (name,initial,params,idx,mask,plus,minus),(p,m) in zip(cases,truth):
        a=rollout(model,initial,params,idx,mask,plus,deadline)
        b=rollout(model,initial,params,idx,mask,minus,deadline)
        den=float((p-initial).square().sum()+(m-initial).square().sum())
        effect=p-m;ed=float(effect.square().sum())
        if min(den,ed)<=0:raise RuntimeError('zero baseline')
        strata[name]=dict(rollout=float((a-p).square().sum()+(b-m).square().sum())/den,
            effect=float(((a-b)-effect).square().sum())/ed)
    return dict(strata=strata,**{k:sum(v[k] for v in strata.values())/len(strata)
        for k in ('rollout','effect')})

def screen(candidate,controls):
    return (all(v[k]<=.15 for v in candidate['strata'].values() for k in ('rollout','effect'))
        and all(candidate[k]<=.8*c[k] for k in ('rollout','effect') for c in controls))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-sha',required=True);p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args();root=a.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',a.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source or exclusive trial directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    fit=dataset(281001,64);familiar=dataset(281002,16)
    if len(fit[0])!=1536 or len(familiar[0])!=384:raise RuntimeError('dataset count')
    manifest=dict(source_sha=a.source_sha,fit_sha256=tensor_hash(fit),familiar_sha256=tensor_hash(familiar),
        seeds=SEEDS,arms=ARMS,epochs=EPOCHS,batch=BATCH,torch=str(torch.__version__),protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[];models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',seed=seed,arm=arm)
            row,model=train_arm(arm,seed,fit,familiar,root,deadline)
            rows.append(row);models[seed,arm]=model;emit('arm_completed',**row)
    checks,structural,jepa=gate(rows)
    emit('mastery_gate',checks=checks,structural_eligible=structural,jepa_eligible=jepa)
    scores=[];gates=[];cohort_hash=None
    if structural or jepa:
        cases=cohort()
        cohort_hash=digest(canonical([[name,[v.tolist() for v in vals]] for name,*vals in cases]))
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(cases),trajectories=24*len(cases),paired=True)
        truth=targets(cases,deadline)
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],cases,truth,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            j,n,s,d,z=(results[k] for k in ARMS)
            gates.append(dict(seed=seed,structural_pass=structural and screen(n,(z,d)),
                jepa_pass=jepa and screen(j,(n,s,z,d))))
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
        examples_exposed=sum(r['examples_exposed'] for r in rows),mastery_checks=checks,
        transfer_executed=bool(scores),transfer_checks=gates,structural_screen=bool(gates) and all(c['structural_pass'] for c in gates),
        jepa_screen=bool(gates) and all(c['jepa_pass'] for c in gates),scientific_gain_verified=False,
        compute_parity_verified=False,cold_retention_verified=False,protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
