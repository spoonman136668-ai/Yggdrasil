"""UJ-04A: multi-prefix JEPA representation and covariance ablation, DEV only."""
import argparse
from collections import Counter
import math
import random
import re
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

from uj03a_pilot import SHA256, BYTES, select, digest, canonical, group, check_deadline
from uj03b_pilot import FastJEPA, model_for as prior_model, loss_for as prior_loss, scores as prior_scores
from grounded_eval import evaluate
from checkpoint import representation_health
from symbolic_control import scores as symbolic_scores

ARMS = ('prior','pooled','slots','slots_cov','shuffled','recurrent','attention')
SEEDS = (1901,1902,1903)
SKIP, TRAIN, DIAG, BATCH, EPOCHS = 1664,512,128,8,8
ARM_SECONDS, TOTAL_SECONDS = 150,3400

def emit(event, **fields):
    print('UJ04A '+canonical(dict(event=event,**fields)).decode(),flush=True)

def fresh(raw,expected=SHA256,skip=SKIP,ntrain=TRAIN,ndiag=DIAG):
    prior,di,_=select(raw,expected,skip+ntrain,ndiag)
    parts=(prior[:skip],prior[skip:],di)
    gs=[set(group(r[2].decode()) for r in part) for part in parts]
    if any(a&b for i,a in enumerate(gs) for b in gs[i+1:]):
        raise RuntimeError('group leakage')
    manifest=[dict(count=len(g),groups_sha256=digest(canonical(sorted(g))),
                   ids_sha256=digest(canonical([r[0] for r in part])))
              for g,part in zip(gs,parts)]
    return parts[1],parts[2],manifest

def signal(rows):
    if not 2<=len(rows)<=64 or any(type(r) is not bytes or not 1<=len(r)<=256 for r in rows):
        raise ValueError('signal bounds')
    lengths=torch.tensor([len(r) for r in rows],dtype=torch.long)
    x=torch.zeros(len(rows),int(lengths.max()),8)
    bits=torch.arange(8)
    for i,row in enumerate(rows):
        x[i,:len(row)]=2*((torch.tensor(list(row))[:,None]>>bits)&1)-1
    return x,lengths

class MultiPrefix(FastJEPA):
    """Shared recurrent encoder, four causal prefix states; no learned token IDs."""
    def __init__(self,pooled=False):
        super().__init__()
        self.pooled=pooled

    def prefixes(self,rows,target=False):
        x,lens=signal(rows)
        enc=self.target if target else self.online
        packed=nn.utils.rnn.pack_padded_sequence(x,lens,batch_first=True,enforce_sorted=False)
        h,_=enc.recurrent(packed)
        h,_=nn.utils.rnn.pad_packed_sequence(h,batch_first=True)
        idx=((lens[:,None]*torch.arange(1,5)[None,:]+3)//4-1).clamp_min(0)
        return enc.project(h[torch.arange(len(rows))[:,None],idx]).tanh(),idx

    def encode(self,rows,target=False):
        return self.prefixes(rows,target)[0].mean(1)

    def distribution(self,z):
        shape=z.shape
        logp,means=self._components(z.reshape(-1,self.latent))
        return logp.reshape(*shape[:-1],2),means.reshape(*shape[:-1],2,self.latent)

    def choices(self,rows):
        z,idx=self.prefixes(tuple(r[2] for r in rows))
        opts=tuple(o for r in rows for o in r[3])
        with torch.no_grad():
            target,_=self.prefixes(opts,target=True)
            y=target.mean(1).reshape(len(rows),5,self.latent)
        source=z.mean(1,keepdim=True) if self.pooled else z
        logp,means=self.distribution(source)
        dist=(means[:,:,None,:,:]-y[:,None,:,None,:]).square().sum(-1)
        score=torch.logsumexp(logp[:,:,None,:]-dist/.5,dim=-1)
        return torch.logsumexp(score,dim=1)-math.log(source.shape[1]),z,idx

def penalty(v,cov):
    centered=v-v.mean(0)
    std=(centered.square().mean(0)+1e-4).sqrt()
    var=F.relu(.2-std).mean()
    norm=centered/std
    corr=norm.T@norm/v.shape[0]
    off=corr-torch.diag(torch.diagonal(corr))
    return 5*var+(.25*off.square().sum()/(v.shape[1]*(v.shape[1]-1)) if cov else 0)

def model_for(arm,seed):
    if arm not in ARMS:
        raise ValueError('unknown arm')
    if arm in ('prior','recurrent','attention'):
        return prior_model('contrastive' if arm=='prior' else arm,seed)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        return MultiPrefix(pooled=arm=='pooled')

def scores(model,rows):
    if isinstance(model,MultiPrefix):
        return model.choices(rows)[0]
    return prior_scores(model,rows)[0]

def objective(model,rows,labels,arm):
    if not isinstance(model,MultiPrefix):
        return prior_loss(model,rows,labels,'contrastive' if arm=='prior' else arm)
    logits,z,idx=model.choices(rows)
    labels=torch.tensor(labels,dtype=torch.long)
    pos=-logits.gather(1,labels[:,None]).mean()
    with torch.no_grad():
        future,_=model.prefixes(tuple(r[2] for r in rows),target=True)
    logp,means=model.distribution(z[:,:-1])
    prediction=(logp.exp()[...,None]*means).sum(-2)
    mask=idx[:,1:]>idx[:,:-1]
    local=((prediction-future[:,1:]).square().mean(-1)*mask).sum()/mask.sum().clamp_min(1)
    options,_=model.prefixes(tuple(o for r in rows for o in r[3]))
    views=[z.mean(1),options.mean(1)]+[z[:,i] for i in range(4)]
    regularizer=sum(penalty(v,arm in ('slots_cov','shuffled')) for v in views)/len(views)
    return pos+F.cross_entropy(logits,labels)+local+regularizer

def fit(model,rows,arm,seed,deadline,epochs=EPOCHS):
    if len(rows)%BATCH or not 1<=epochs<=EPOCHS:
        raise ValueError('budget')
    original=[r[4] for r in rows]
    labels=original.copy()
    if arm=='shuffled':
        random.Random(seed+991).shuffle(labels)
        if labels==original:
            raise ValueError('degenerate shuffle')
    if Counter(labels)!=Counter(original):
        raise RuntimeError('label marginal mismatch')
    opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=.001,weight_decay=0.)
    rng=random.Random(seed)
    order=list(range(len(rows)))
    history=[]
    model.train()
    for _ in range(epochs):
        rng.shuffle(order)
        losses=[]
        for offset in range(0,len(rows),BATCH):
            check_deadline(deadline)
            ids=order[offset:offset+BATCH]
            opt.zero_grad(set_to_none=True)
            loss=objective(model,[rows[i] for i in ids],[labels[i] for i in ids],arm)
            if not torch.isfinite(loss):
                raise RuntimeError('nonfinite loss')
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad):
                raise RuntimeError('gradient')
            opt.step()
            model.update_target()
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise RuntimeError('parameter')
            losses.append(float(loss.detach()))
        history.append(sum(losses)/len(losses))
    model.eval()
    check_deadline(deadline)
    plateau=len(history)>=3 and max(abs(a-b)/max(abs(a),1e-8) for a,b in zip(history[-3:-1],history[-2:]))<=.01
    return dict(steps=epochs*len(rows)//BATCH,observations=epochs*len(rows),
        exposure_bytes=epochs*sum(len(r[2])+sum(map(len,r[3])) for r in rows),
        changed_labels=sum(a!=b for a,b in zip(labels,original)),
        epoch_loss=history,plateau_screen=plateau)

@torch.no_grad()
def measure(model,rows,deadline,rotate=False):
    cached={}
    for i in range(0,len(rows),BATCH):
        check_deadline(deadline)
        chunk=rows[i:i+BATCH]
        inputs=[r[:2]+(rows[(i+j+1)%len(rows)][2],)+r[3:] for j,r in enumerate(chunk)] if rotate else chunk
        logits=scores(model,inputs)
        for r,v in zip(chunk,logits):
            cached[(r[2],r[3])]=v.tolist()
    return evaluate(rows,lambda c,o:cached[(c,o)])['all']

def rank_stats(x):
    x=x.detach().cpu().double()
    x=x-x.mean(0)
    energy=torch.linalg.svdvals(x).square()
    total=energy.sum()
    rank=float(total.square()/energy.square().sum()) if total>0 else 0.
    return dict(rank=rank,min_std=float(x.square().mean(0).sqrt().min()))

@torch.no_grad()
def health(model,rows):
    if not isinstance(model,FastJEPA):
        return None
    result={}
    for target in (False,True):
        name='target' if target else 'online'
        if isinstance(model,MultiPrefix):
            z=torch.cat([model.prefixes(rows[i:i+BATCH],target)[0] for i in range(0,len(rows),BATCH)])
            result[name]=dict(global_state=rank_stats(z.mean(1)),slots=[rank_stats(z[:,i]) for i in range(4)])
        else:
            z=torch.cat([model.encode(rows[i:i+BATCH],target=target) for i in range(0,len(rows),BATCH)])
            result[name]=dict(global_state=rank_stats(z))
    return result

def run_arm(arm,seed,tr,di,overall):
    t0,c0=time.monotonic(),time.process_time()
    deadline=min(overall,t0+ARM_SECONDS)
    model=model_for(arm,seed).eval()
    before=measure(model,di,deadline)
    before_health=health(model,[r[2] for r in di])
    accounting=fit(model,tr,arm,seed,deadline)
    after=measure(model,di,deadline)
    rotated=measure(model,di,deadline,rotate=True)
    after_health=health(model,[r[2] for r in di])
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,rotated=rotated,
        before_health=before_health,after_health=after_health,accounting=accounting,
        parameters=sum(p.numel() for p in model.parameters() if p.requires_grad),
        cpu_seconds=time.process_time()-c0,wall_seconds=time.monotonic()-t0)

def summarize(out):
    means={a:sum(r['after']['accuracy'] for r in out if r['arm']==a)/len(SEEDS) for a in ARMS}
    briers={a:sum(r['after']['brier'] for r in out if r['arm']==a)/len(SEEDS) for a in ARMS}
    primary=[r for r in out if r['arm']=='slots_cov']
    controls=('prior','pooled','slots','recurrent','attention')
    strongest=max(controls,key=lambda a:means[a])
    paired=[r['after']['accuracy']-max(q['after']['accuracy'] for q in out if q['seed']==r['seed'] and q['arm'] in controls) for r in primary]
    ranks=[r['after_health'][k]['global_state']['rank'] for r in primary for k in ('online','target')]
    stds=[r['after_health'][k]['global_state']['min_std'] for r in primary for k in ('online','target')]
    cov_gain=[r['after_health']['online']['global_state']['rank']-next(q['after_health']['online']['global_state']['rank'] for q in out if q['seed']==r['seed'] and q['arm']=='slots') for r in primary]
    screen=(means['slots_cov']-means['shuffled']>=.10 and means['slots_cov']-means[strongest]>=.05
        and min(paired)>0 and min(ranks)>=4 and min(stds)>=.05 and min(cov_gain)>0
        and briers['slots_cov']-briers[strongest]<=.02
        and all(r['accounting']['plateau_screen'] for r in out if r['arm'] in ('recurrent','attention')))
    return dict(mean_accuracy=means,mean_brier=briers,strongest=strongest,paired_margin=paired,
        minimum_global_rank=min(ranks),minimum_global_std=min(stds),cov_rank_gain=cov_gain,
        continuation_screen=screen,scientific_gain_verified=False,baseline_convergence_verified=False,
        compute_parity_verified=False,protected_evaluation_accessed=False,
        mathematical_transformation_learning_verified=False)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train',type=Path,required=True)
    p.add_argument('--source-sha',required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.train.stat().st_size!=BYTES:
        raise ValueError('custody')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    tr,di,manifest=fresh(args.train.read_bytes())
    emit('manifest',source_sha=args.source_sha,train_sha256=SHA256,groups=manifest,arms=ARMS,seeds=SEEDS,
         epochs=EPOCHS,batch=BATCH,torch=str(torch.__version__),scope='TRAIN_SOURCE_ONLY_DEVELOPMENT_NOT_SCIENCE')
    counts=Counter(r[3][r[4]] for r in tr)
    covered=[0]
    def symbolic(c,o):
        v,ok=symbolic_scores(c,o)
        covered[0]+=int(ok)
        return v
    emit('reference',uniform=evaluate(di,lambda c,o:[0.]*len(o))['all'],
         frequency=evaluate(di,lambda c,o:[math.log1p(counts[x]) for x in o])['all'],
         symbolic=evaluate(di,symbolic)['all'],symbolic_coverage=covered[0]/len(di))
    out=[]
    for seed in SEEDS:
        for arm in ARMS:
            check_deadline(deadline)
            emit('arm_started',arm=arm,seed=seed)
            r=run_arm(arm,seed,tr,di,deadline)
            emit('arm_completed',**r)
            out.append(r)
    emit('complete',arms_completed=len(out),**summarize(out))

if __name__=='__main__':
    main()
