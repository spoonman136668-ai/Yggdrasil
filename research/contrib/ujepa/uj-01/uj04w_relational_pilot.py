"""UJ04W W0: learned ordinal role relation and matched controls, DEV only."""
import argparse
from collections import defaultdict, Counter
import copy
from pathlib import Path
import random
import re
import time

import torch
from torch import nn
from torch.nn import functional as F
from uj03a_pilot import canonical, digest, check_deadline
from uj04u_stability_pilot import finite

RADIX=11
SEEDS=(2701,2702,2703)
ARMS=('jepa','no_latent','shuffled_aux','shuffled_result','dense')
WIDTHS=(2,8,32,128)
EPOCHS=800
BATCH=64
ARM_SECONDS=180
TOTAL_SECONDS=3600

def emit(event, **fields):
    print('UJ04W '+canonical(dict(event=event, **fields)).decode(),flush=True)

def reference_step(op,c,x,y):
    if op==0:
        carry,digit=divmod(x+y+c,RADIX)
    else:
        z=x-y-c
        digit,carry=z%RADIX,int(z<0)
    return digit,carry

def split():
    fit,test=[],[]
    for op in (0,1):
        for c in (0,1):
            pairs=sorted(((x,y) for x in range(RADIX) for y in range(RADIX)),
                key=lambda xy:(digest(('W0:20261127:%d:%d:%d:%d'%(op,c,*xy)).encode()),xy))
            rows=[(op,c,x,y,*reference_step(op,c,x,y)) for x,y in pairs]
            fit.extend(rows[:96]); test.extend(rows[96:])
    if len(fit)!=384 or len(test)!=100 or {r[:4] for r in fit}&{r[:4] for r in test}:
        raise RuntimeError('split custody')
    return tuple(fit),tuple(test)

def pack(rows):
    op=torch.tensor([r[0] for r in rows],dtype=torch.long)
    features=torch.tensor([[r[2]/(RADIX-1),r[3]/(RADIX-1),float(r[1])] for r in rows],dtype=torch.float32)
    return op,features,torch.tensor([r[4] for r in rows]),torch.tensor([r[5] for r in rows])

class Cell(nn.Module):
    def __init__(self,dense=False):
        super().__init__()
        self.dense=dense
        if not dense:
            self.roles=nn.Parameter(torch.empty(2,3))
            nn.init.uniform_(self.roles,-.5,.5)
        self.trunk=nn.Sequential(nn.Linear(4 if dense else 2,128),nn.SiLU(),nn.Linear(128,128),nn.SiLU())
        self.digit=nn.Linear(128,RADIX)
        self.state=nn.Linear(128,2)
        self.predict=nn.Linear(128,16)
        self.outcome=nn.Embedding(2*RADIX,16)
        self.reconstruct=nn.Linear(16,2*RADIX)
        self.target=copy.deepcopy(self.outcome).requires_grad_(False)

    def heads(self,op,features):
        finite(features)
        if op.ndim!=1 or features.shape!=(len(op),3) or not bool(((op==0)|(op==1)).all()):
            raise ValueError('operation/features')
        if not bool(((features[:,2]==0)|(features[:,2]==1)).all()):
            raise ValueError('state')
        relation=features if self.dense else (self.roles[op]*features).sum(-1,keepdim=True)
        h=self.trunk(torch.cat((relation,op[:,None].float()),dim=-1))
        d,n,z=self.digit(h),self.state(h),self.predict(h).tanh()
        finite(h,d,n,z)
        return d,n,z

    @torch.no_grad()
    def ema(self):
        self.target.weight.mul_(.99).add_(self.outcome.weight,alpha=.01)

def loss_for(model,op,x,d,n,arm,perm):
    if arm not in ARMS or model.dense!=(arm=='dense') or sorted(perm.tolist())!=list(range(len(op))):
        raise ValueError('arm/permutation')
    pd,pn=d[perm],n[perm]
    ld,ln=(pd,pn) if arm=='shuffled_result' else (d,n)
    label=2*ld+ln
    target=2*pd+pn if arm in ('shuffled_aux','shuffled_result') else label
    dl,cl,z=model.heads(op,x)
    emb=model.outcome(label).tanh()
    reconstruction=model.reconstruct(emb)
    with torch.no_grad():
        expected=model.target(target).tanh()
    loss=F.cross_entropy(dl,ld)+F.cross_entropy(cl,ln)+F.cross_entropy(reconstruction,label)
    loss=loss+(0. if arm in ('no_latent','dense') else .5)*F.smooth_l1_loss(z,expected)
    finite(loss,emb,reconstruction,expected)
    return loss,int((n!=pn).sum()),int(((d!=pd)|(n!=pn)).sum())

@torch.no_grad()
def predict(model,op,c,x,y):
    if isinstance(model,Memory):
        return [model.predict(*q) for q in zip(op,c,x,y)]
    a=torch.tensor([[a/(RADIX-1),b/(RADIX-1),float(k)] for k,a,b in zip(c,x,y)],dtype=torch.float32)
    d,n,_=model.heads(torch.tensor(op,dtype=torch.long),a)
    return list(zip(d.argmax(-1).tolist(),n.argmax(-1).tolist()))

class Memory:
    def __init__(self,fit):
        self.fit={r[:4]:r[4:] for r in fit}
        self.groups=defaultdict(list)
        for k in self.fit: self.groups[k[:2]].append(k)
    def predict(self,op,c,x,y):
        k=(op,c,x,y)
        if k not in self.fit:
            k=min(self.groups[op,c],key=lambda q:((x-q[2])**2+(y-q[3])**2,q))
        return self.fit[k]

@torch.no_grad()
def local(model,rows):
    pred=predict(model,*zip(*(r[:4] for r in rows)))
    counts=Counter(); correct=Counter()
    for r,q in zip(rows,pred):
        k='%d:%d'%r[:2]; counts[k]+=1; correct[k]+=int(q==r[4:])
    return dict(exact=sum(correct.values())/len(rows),worst=min(correct[k]/n for k,n in counts.items()),
        counts=dict(counts),correct={k:correct[k] for k in counts})

def train_arm(arm,seed,fit,test,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic(); cpu=time.process_time()
    torch.manual_seed(seed)
    model=Cell(arm=='dense')
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    op,x,d,n=pack(fit)
    before=dict(fit=local(model,fit),excluded=local(model,test))
    hist=[]; steps=cm=pm=exposures=0
    for epoch in range(EPOCHS):
        ids=torch.randperm(len(fit),generator=torch.Generator().manual_seed(seed*1000+epoch))
        total=0.
        for ii in ids.split(BATCH):
            check_deadline(deadline)
            perm=torch.randperm(len(ii),generator=torch.Generator().manual_seed(seed*100000+steps))
            opt.zero_grad()
            loss,a,b=loss_for(model,op[ii],x[ii],d[ii],n[ii],arm,perm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
            opt.step(); model.ema(); finite(*params,*model.target.parameters())
            steps+=1; cm+=a; pm+=b; exposures+=len(ii); total+=float(loss.detach())*len(ii)
        hist.append(total/len(fit))
    if steps!=4800 or exposures!=EPOCHS*len(fit) or cm/exposures<.25 or pm/exposures<.80:
        raise RuntimeError('exposure/mismatch')
    after=dict(fit=local(model,fit),excluded=local(model,test))
    last=hist[-10:]; delta=max(last)-min(last)
    plateau=delta<=.001 or delta/max(abs(last[0]),1e-12)<=.03
    with torch.no_grad():
        separation=float(torch.pdist(model.target.weight.tanh()).min())
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if digest(path.read_bytes())!=h: raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,plateau=plateau,steps=steps,
        examples_exposed=exposures,carry_mismatch=cm/exposures,pair_mismatch=pm/exposures,
        loss_first=hist[0],loss_last_ten=last,target_separation=separation,
        roles=None if model.dense else model.roles.detach().tolist(),
        trainable_params=sum(p.numel() for p in params),checkpoint_sha256=h,
        checkpoint_bytes=path.stat().st_size,wall_seconds=time.monotonic()-start,
        cpu_seconds=time.process_time()-cpu),model

def gate(rows,seeds=SEEDS):
    checks=[]
    for seed in seeds:
        a={r['arm']:r for r in rows if r['seed']==seed}
        if set(a)!=set(ARMS): raise RuntimeError('incomplete arms')
        j,n,s,d,z=(a[k] for k in ARMS)
        score=lambda r:r['after']['excluded']['exact']
        checks.append(dict(seed=seed,controls_adequate=all(r['after']['fit']['exact']>=.98 and r['plateau'] for r in (n,s,z)),
            jepa_fit=j['after']['fit']['exact']>=.98,
            structural_mastery=n['after']['excluded']['worst']>=.95,
            jepa_mastery=j['after']['excluded']['worst']>=.95,
            structural_margin=score(n)-score(z),jepa_margin=score(j)-max(score(n),score(s),score(z)),
            structural_negative=score(n)-score(d),jepa_negative=score(j)-score(d)))
    eligible=all(c['controls_adequate'] and c['jepa_fit'] for c in checks) and (
        all(c['structural_mastery'] for c in checks) or all(c['jepa_mastery'] for c in checks))
    return checks,eligible

def digits(n,w):
    out=[]
    for _ in range(w):
        n,d=divmod(n,RADIX); out.append(d)
    if n: raise ValueError('width')
    return out

def cases_for(deadline):
    out=[]
    for w in WIDTHS:
        cap=RADIX**w; mid=RADIX**(w-1)
        for op in (0,1):
            stress=((cap-1,1),(cap-1,cap-1),(mid-1,1),(0,0)) if op==0 else (
                (mid,1),(cap-1,cap-1),(mid,mid-1),(0,0))
            seen=set(stress)
            out.extend((op,w,'stress',a,b) for a,b in stress)
            rng=random.Random(20261127+100*w+op)
            for _ in range(10000):
                check_deadline(deadline)
                if len(seen)==132: break
                a,b=rng.randrange(cap),rng.randrange(cap)
                if op and a<b:a,b=b,a
                if (a,b) in seen:continue
                seen.add((a,b)); out.append((op,w,'random',a,b))
            if len(seen)!=132:raise RuntimeError('word exhaustion')
    if len(out)!=1056 or len(set(out))!=1056:raise RuntimeError('word accounting')
    return tuple(out)

def value(op,trace):
    if op and trace[-1][1]: return None
    return sum(d*RADIX**i for i,(d,c) in enumerate(trace))+(0 if op else trace[-1][1]*RADIX**len(trace))

def reference(case):
    op,w,_,a,b=case
    c=0; trace=[]
    for x,y in zip(digits(a,w),digits(b,w)):
        d,c=reference_step(op,c,x,y); trace.append((d,c))
    if value(op,trace)!=(a-b if op else a+b): raise RuntimeError('reference mismatch')
    return tuple(trace)

@torch.no_grad()
def composition(model,cases,truth,deadline):
    groups=defaultdict(list); stats=defaultdict(Counter)
    for q in cases:groups[q[:2]].append(q)
    for (op,w),group in groups.items():
        xs=[digits(q[3],w) for q in group]; ys=[digits(q[4],w) for q in group]
        c=[0]*len(group); traces=[[] for q in group]
        for i in range(w):
            check_deadline(deadline)
            p=predict(model,[op]*len(group),c,[x[i] for x in xs],[y[i] for y in ys])
            c=[n for d,n in p]
            for tr,q in zip(traces,p):tr.append(q)
        for q,tr in zip(group,traces):
            k='%d:%d:%s'%q[:3]; row=stats[k]; row['count']+=1
            row['trace_correct']+=int(tuple(tr)==truth[q])
            row['value_correct']+=int(value(op,tr)==(q[3]-q[4] if op else q[3]+q[4]))
    count=sum(r['count'] for r in stats.values())
    return dict(trace_accuracy=sum(r['trace_correct'] for r in stats.values())/count,
        value_accuracy=sum(r['value_correct'] for r in stats.values())/count,
        worst=min(r['trace_correct']/r['count'] for r in stats.values()),strata={k:dict(v) for k,v in stats.items()})

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args(); root=a.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',a.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source SHA or exclusive receipt directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    fit,test=split()
    manifest=dict(source_sha=a.source_sha,radix=RADIX,fit_sha256=digest(canonical(fit)),
        excluded_sha256=digest(canonical(test)),seeds=SEEDS,arms=ARMS,epochs=EPOCHS,batch=BATCH,
        torch=str(torch.__version__),protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[];models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',seed=seed,arm=arm)
            row,model=train_arm(arm,seed,fit,test,root,deadline)
            rows.append(row);models[seed,arm]=model;emit('arm_completed',**row)
    checks,eligible=gate(rows);emit('mastery_gate',checks=checks,composition_eligible=eligible)
    scores=[]; composition_checks=[]; structural=False;jepa=False;memory=None;word_hash=None
    if eligible:
        cases=cases_for(deadline);truth={q:reference(q) for q in cases}
        word_hash=digest(canonical(cases));emit('composition_manifest',word_sha256=word_hash,word_count=len(cases))
        memory=composition(Memory(fit),cases,truth,deadline)
        emit('reference',memory=memory,symbolic_exact=1.)
        for c in checks:
            seed=c['seed'];a={}
            for arm in ARMS:
                a[arm]=composition(models[seed,arm],cases,truth,deadline)
                row=dict(seed=seed,arm=arm,score=a[arm]);scores.append(row);emit('composition_score',**row)
            j,n,s,d,z=(a[k] for k in ARMS)
            metric=lambda r:r['trace_accuracy']
            composition_checks.append(dict(seed=seed,
                structural_pass=c['structural_mastery'] and c['structural_margin']>=.05 and c['structural_negative']>=.10
                    and n['worst']>=.90 and metric(n)-max(metric(z),metric(memory))>=.05 and metric(n)-metric(d)>=.10,
                jepa_pass=c['jepa_mastery'] and c['jepa_margin']>=.05 and c['jepa_negative']>=.10
                    and j['worst']>=.90 and metric(j)-max(metric(n),metric(s),metric(z),metric(memory))>=.05 and metric(j)-metric(d)>=.10))
        structural=all(c['structural_pass'] for c in composition_checks)
        jepa=all(c['jepa_pass'] for c in composition_checks)
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),examples_exposed=sum(r['examples_exposed'] for r in rows),
        mastery_checks=checks,composition_executed=eligible,composition_checks=composition_checks,
        structural_screen=structural,jepa_screen=jepa,scientific_gain_verified=False,compute_parity_verified=False,
        cold_retention_verified=False,protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,word_sha256=word_hash,memory=memory,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
