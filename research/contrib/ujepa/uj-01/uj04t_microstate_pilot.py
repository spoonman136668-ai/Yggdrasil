"""UJ04T T0: synthetic local numerical transition falsification, DEV only."""
import argparse
from collections import Counter,defaultdict
import copy
import math
from pathlib import Path
import random
import re
import time

import torch
from torch import nn
from torch.nn import functional as F

from uj03a_pilot import canonical,digest,check_deadline

SEEDS=(2401,2402,2403)
WIDTHS=(2,8,32,128)
ARMS=('jepa','no_latent','shuffled_aux','shuffled_result')
EPOCHS=400
BATCH=64
ARM_SECONDS=120
TOTAL_SECONDS=1800

def emit(event,**fields):
    print('UJ04T '+canonical(dict(event=event,**fields)).decode(),flush=True)

def teacher(op,c,x,y):
    if op not in (0,1) or c not in (0,1) or not (0<=x<=9 and 0<=y<=9):
        raise ValueError('local domain')
    if op==0:
        n,d=divmod(x+y+c,10)
    else:
        z=x-y-c
        d,n=z%10,int(z<0)
    return d,n

def local_data():
    train,test=[],[]
    for op in (0,1):
        for c in (0,1):
            pairs=sorted(((x,y) for x in range(10) for y in range(10)),
                         key=lambda xy:(digest(('UJ04T:20261124:local:%d:%d:%d:%d'%(op,c,*xy)).encode()),xy))
            rows=[(op,c,x,y,*teacher(op,c,x,y)) for x,y in pairs]
            train.extend(rows[:80]);test.extend(rows[80:])
    a={r[:4] for r in train};b={r[:4] for r in test}
    if len(a)!=320 or len(b)!=80 or a&b:
        raise RuntimeError('local split')
    return tuple(train),tuple(test)

def digits(n,width):
    if not 0<=n<10**width:
        raise ValueError('word width')
    return tuple(map(int,str(n).zfill(width)[::-1]))

def stress_pairs(op,width):
    cap=10**width
    mid=10**(width-1)
    if op==0:
        return ((cap-1,1),(cap-1,cap-1),(mid-1,1),(0,0))
    return ((mid,1),(cap-1,cap-1),(mid,mid-1),(0,0))

def cases_for(op,width,count=128,seed_base=20261124):
    if op not in (0,1) or not 2<=width<=128 or not 0<=count<=128:
        raise ValueError('case config')
    cap=10**width
    stress=stress_pairs(op,width)
    seen=set(stress)
    if len(seen)!=4:
        raise RuntimeError('stress duplicate')
    out=[(op,width,'stress',a,b) for a,b in stress]
    rng=random.Random(seed_base+100*width+op)
    tries=0
    while len(out)<count+4:
        tries+=1
        if tries>10000: raise RuntimeError('case exhaustion')
        a,b=rng.randrange(cap),rng.randrange(cap)
        if op and a<b: a,b=b,a
        if (a,b) in seen: continue
        seen.add((a,b))
        out.append((op,width,'random',a,b))
    return tuple(out)

def reference(case):
    op,width,kind,a,b=case
    xs,ys=digits(a,width),digits(b,width)
    c=0
    trace=[]
    keys=[]
    for x,y in zip(xs,ys):
        keys.append((op,c,x,y))
        d,c=teacher(op,c,x,y)
        trace.append((d,c))
    expected=a+b if op==0 else a-b
    if value(op,trace)!=expected:
        raise RuntimeError('independent whole-word check')
    return tuple(trace),tuple(keys)

def value(op,trace):
    if not trace or (op and trace[-1][1]):
        return None
    out=sum(d*10**i for i,(d,c) in enumerate(trace))
    return out+(trace[-1][1]*10**len(trace) if op==0 else 0)

def dfeat(d):
    return [d/9]+[float((d>>i)&1) for i in range(4)]

def action(op,x,y):
    return dfeat(x)+dfeat(y)+[float(op)]

def tensor(v):
    return torch.tensor(v,dtype=torch.float32)

def batch(rows):
    return (tensor([[c] for op,c,x,y,d,n in rows]),
            tensor([action(op,x,y) for op,c,x,y,d,n in rows]),
            torch.tensor([d for op,c,x,y,d,n in rows]),
            torch.tensor([n for op,c,x,y,d,n in rows]))

class Cell(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(1,16),nn.SiLU(),nn.Linear(16,16))
        self.transition=nn.Sequential(nn.Linear(27,64),nn.SiLU(),nn.Linear(64,16))
        self.readout=nn.Sequential(nn.Linear(16,64),nn.SiLU(),nn.Linear(64,12))
        self.target=copy.deepcopy(self.encoder).requires_grad_(False)
    def encode(self,c):
        return self.encoder(c)
    def step(self,state,a):
        nxt=self.transition(torch.cat((state,a),dim=-1))
        logits=self.readout(nxt)
        return logits[:,:10],logits[:,10:],nxt
    @torch.no_grad()
    def ema(self):
        for t,o in zip(self.target.parameters(),self.encoder.parameters()):
            t.mul_(.99).add_(o,alpha=.01)

class Memory:
    def __init__(self,rows):
        self.fit={r[:4]:r[4:] for r in rows}
        self.cache={}
        for op in (0,1):
            for c in (0,1):
                group=sorted(k for k in self.fit if k[:2]==(op,c))
                if not group: raise ValueError('memory stratum missing')
                for x in range(10):
                    for y in range(10):
                        k=(op,c,x,y)
                        if k in self.fit:
                            self.cache[k]=self.fit[k]
                        else:
                            v=dfeat(x)+dfeat(y)
                            best=min(group,key=lambda z:(sum((a-b)**2 for a,b in zip(v,dfeat(z[2])+dfeat(z[3]))),z))
                            self.cache[k]=self.fit[best]
    def predict(self,op,c,x,y):
        return self.cache[(op,c,x,y)]

@torch.no_grad()
def local_score(model,rows,kind):
    if kind=='symbolic':
        pred=[teacher(*r[:4]) for r in rows]
    elif kind=='memory':
        pred=[model.predict(*r[:4]) for r in rows]
    else:
        c,a,d,n=batch(rows)
        dl,cl,_=model.step(model.encode(c),a)
        if not torch.isfinite(dl).all() or not torch.isfinite(cl).all():
            raise RuntimeError('nonfinite local inference')
        pred=list(zip(dl.argmax(-1).tolist(),cl.argmax(-1).tolist()))
    counts=Counter();correct=Counter()
    digit=state=0
    for row,(d,c) in zip(rows,pred):
        k='%d:%d'%row[:2]
        counts[k]+=1
        correct[k]+=int((d,c)==row[4:])
        digit+=int(d==row[4]);state+=int(c==row[5])
    return dict(count=len(rows),exact=sum(correct.values())/len(rows),
                digit=digit/len(rows),state=state/len(rows),strata_counts=dict(counts),
                strata_correct=dict(correct))

@torch.no_grad()
def rollout(model,cases,kind,deadline):
    # Only operand digits, operation and predicted state enter this interface.
    if not cases: raise ValueError('empty rollout')
    op,width=cases[0][:2]
    if any(case[:2]!=(op,width) for case in cases):
        raise ValueError('mixed rollout')
    xs=[digits(a,width) for _,_,_,a,b in cases]
    ys=[digits(b,width) for _,_,_,a,b in cases]
    size=len(cases)
    carry=[0]*size
    traces=[[] for _ in cases]
    state=None if kind in ('memory','symbolic') else model.encode(torch.zeros(size,1))
    for i in range(width):
        check_deadline(deadline)
        if kind in ('memory','symbolic'):
            fn=teacher if kind=='symbolic' else model.predict
            pred=[fn(op,c,x[i],y[i]) for c,x,y in zip(carry,xs,ys)]
        else:
            a=tensor([action(op,x[i],y[i]) for x,y in zip(xs,ys)])
            dl,cl,nxt=model.step(state,a)
            if not torch.isfinite(dl).all() or not torch.isfinite(cl).all():
                raise RuntimeError('nonfinite rollout')
            pred=list(zip(dl.argmax(-1).tolist(),cl.argmax(-1).tolist()))
            state=model.encode(tensor([[c] for d,c in pred])) if kind=='explicit' else nxt
        carry=[c for d,c in pred]
        for t,v in zip(traces,pred): t.append(v)
    return tuple(tuple(t) for t in traces)

@torch.no_grad()
def score(model,kind,fit,test,cases,truth,deadline):
    groups=defaultdict(list)
    for case in cases: groups[case[:2]].append(case)
    metrics=defaultdict(Counter)
    for (op,width),rr in sorted(groups.items()):
        preds=rollout(model,rr,kind,deadline)
        for case,pred in zip(rr,preds):
            ref=truth[case]
            k='%d:%d:%s'%case[:3]
            m=metrics[k]
            m['count']+=1
            m['trace_correct']+=int(pred==ref)
            m['value_correct']+=int(value(op,pred)==(case[3]+case[4] if op==0 else case[3]-case[4]))
            m['columns']+=width
            m['column_correct']+=sum(x==y for x,y in zip(pred,ref))
    sums=Counter()
    for m in metrics.values(): sums.update(m)
    return dict(fit=local_score(model,fit,kind),heldout=local_score(model,test,kind),
        trace_accuracy=sums['trace_correct']/sums['count'],
        value_accuracy=sums['value_correct']/sums['count'],
        column_accuracy=sums['column_correct']/sums['columns'],
        word_count=sums['count'],word_correct=sums['trace_correct'],
        strata={k:dict(v) for k,v in sorted(metrics.items())})

def train_arm(arm,seed,fit,test,cases,truth,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    t0=time.monotonic();c0=time.process_time()
    torch.manual_seed(seed)
    model=Cell()
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    c,a,d,n=batch(fit)
    perm=torch.randperm(len(fit),generator=torch.Generator().manual_seed(seed+100000))
    mismatch=float((n!=n[perm]).float().mean())
    pair_mismatch=float(((n!=n[perm])|(d!=d[perm])).float().mean())
    if mismatch<.25 or pair_mismatch<.80:
        raise RuntimeError('negative control mismatch insufficient')
    target_state=n[perm] if arm in ('shuffled_aux','shuffled_result') else n
    if arm=='shuffled_result': d,n=d[perm],n[perm]
    before=score(model,arm,fit,test,cases,truth,deadline)
    before_explicit=score(model,'explicit',fit,test,cases,truth,deadline) if arm=='no_latent' else None
    history=[]
    steps=0
    for epoch in range(EPOCHS):
        ids=torch.randperm(len(fit),generator=torch.Generator().manual_seed(seed*1000+epoch))
        total=0.
        for ii in ids.split(BATCH):
            check_deadline(deadline)
            dl,cl,nxt=model.step(model.encode(c[ii]),a[ii])
            loss=F.cross_entropy(dl,d[ii])+F.cross_entropy(cl,n[ii])
            if arm!='no_latent':
                with torch.no_grad(): expected=model.target(target_state[ii,None].float())
                loss=loss+.5*F.smooth_l1_loss(nxt,expected)
            if not torch.isfinite(loss): raise RuntimeError('nonfinite loss')
            opt.zero_grad()
            loss.backward()
            opt.step()
            if arm!='no_latent': model.ema()
            total+=float(loss.detach())*len(ii);steps+=1
        history.append(total/len(fit))
    if steps!=EPOCHS*math.ceil(len(fit)/BATCH):
        raise RuntimeError('step accounting')
    after=score(model,arm,fit,test,cases,truth,deadline)
    after_explicit=score(model,'explicit',fit,test,cases,truth,deadline) if arm=='no_latent' else None
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    checkpoint_sha=digest(path.read_bytes())
    if digest(path.read_bytes())!=checkpoint_sha: raise RuntimeError('checkpoint readback')
    delta=max(history[-10:])-min(history[-10:])
    plateau=delta<=.001 or delta/max(abs(history[-10]),1e-12)<=.03
    count=sum(p.numel() for p in params)
    with torch.no_grad():
        separation=float((model.encode(tensor([[0.]]))-model.encode(tensor([[1.]]))).norm())
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,before_explicit=before_explicit,
        after_explicit=after_explicit,loss_first=history[0],loss_last_ten=history[-10:],
        plateau=plateau,steps=steps,examples_exposed=EPOCHS*len(fit),
        state_mismatch=mismatch,pair_mismatch=pair_mismatch,state_separation=separation,
        trainable_params=count,parameter_op_estimate=6*count*EPOCHS*len(fit),
        checkpoint_sha256=checkpoint_sha,checkpoint_bytes=path.stat().st_size,
        wall_seconds=time.monotonic()-t0,cpu_seconds=time.process_time()-c0)

def checks_for(completed,baseline):
    checks=[]
    for seed in SEEDS:
        rs={r['arm']:r for r in completed if r['seed']==seed}
        primary=rs['jepa']['after']
        control=max(baseline['trace_accuracy'],rs['no_latent']['after']['trace_accuracy'],
                    rs['no_latent']['after_explicit']['trace_accuracy'],rs['shuffled_aux']['after']['trace_accuracy'])
        worst=min(m['trace_correct']/m['count'] for m in primary['strata'].values())
        checks.append(dict(seed=seed,heldout=primary['heldout']['exact']>=.95,
            minimum_stratum_trace=worst,all_strata=worst>=.90,
            control_margin=primary['trace_accuracy']-control,
            negative_margin=primary['trace_accuracy']-rs['shuffled_result']['after']['trace_accuracy'],
            control_fit=rs['no_latent']['after']['fit']['exact']>=.98,
            control_plateau=rs['no_latent']['plateau']))
    return checks

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.receipt.exists():
        raise ValueError('source SHA or prior result')
    root=args.receipt.parent
    if not root.is_dir() or any(root.iterdir()):
        raise RuntimeError('exclusive trial directory required')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    fit,test=local_data()
    cases=tuple(case for w in WIDTHS for op in (0,1) for case in cases_for(op,w))
    if len(cases)!=1056 or len(set(cases))!=1056:
        raise RuntimeError('case accounting')
    truth={};test_keys={r[:4] for r in test};coverage=Counter();columns=Counter()
    for case in cases:
        ref,keys=reference(case)
        truth[case]=ref
        k='%d:%d:%s'%case[:3]
        coverage[k]+=sum(x in test_keys for x in keys)
        columns[k]+=len(keys)
    manifest=dict(fit_rows=len(fit),heldout_rows=len(test),word_count=len(cases),
        fit_sha256=digest(canonical(fit)),heldout_sha256=digest(canonical(test)),
        word_sha256=digest(canonical(cases)),heldout_column_counts=dict(coverage),
        total_columns=dict(columns),source_type='deterministic_synthetic_DEV',epochs=EPOCHS,
        batch=BATCH,seeds=SEEDS,arms=ARMS,torch=str(torch.__version__))
    emit('manifest',source_sha=args.source_sha,**manifest)
    memory=Memory(fit)
    baseline=score(memory,'memory',fit,test,cases,truth,deadline)
    symbolic=score(None,'symbolic',fit,test,cases,truth,deadline)
    if symbolic['heldout']['exact']!=1 or symbolic['trace_accuracy']!=1 or symbolic['value_accuracy']!=1:
        raise RuntimeError('symbolic reference inconsistency')
    emit('reference',memory=baseline,symbolic=symbolic)
    completed=[]
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',seed=seed,arm=arm)
            result=train_arm(arm,seed,fit,test,cases,truth,root,deadline)
            emit('arm_completed',**result)
            completed.append(result)
    checks=checks_for(completed,baseline)
    screen=all(c['heldout'] and c['all_strata'] and c['control_margin']>=.05 and c['negative_margin']>=.10
               and c['control_fit'] and c['control_plateau'] for c in checks)
    means={a:sum(r['after']['trace_accuracy'] for r in completed if r['arm']==a)/3 for a in ARMS}
    means['explicit']=sum(r['after_explicit']['trace_accuracy'] for r in completed if r['arm']=='no_latent')/3
    final=dict(arms_fitted=len(completed),evaluated_neural_configurations=15,
        model_training_steps=sum(r['steps'] for r in completed),checks=checks,
        mean_trace_accuracy=means,continuation_screen=screen,scientific_gain_verified=False,
        compute_parity_verified=False,convergence_verified=False,cold_retention_verified=False,
        protected_evaluation_accessed=False,real_data_training=False)
    payload=canonical(dict(source_sha=args.source_sha,manifest=manifest,reference=dict(memory=baseline,symbolic=symbolic),
                           arms=completed,result=final))
    with args.receipt.open('xb') as f: f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload): raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),receipt_bytes=len(payload),**final)

if __name__=='__main__':
    main()
