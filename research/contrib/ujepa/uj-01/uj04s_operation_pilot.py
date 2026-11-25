"""UJ04S: bounded one-step grounded arithmetic DEV training; no protected evaluation."""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import time

import torch
from torch import nn
from torch.nn import functional as F

from uj03a_pilot import BYTES,canonical,digest,check_deadline
from uj04q_source_audit import GSM_BYTES,GSM_BLOB,git_blob,old_groups
from uj04r_source_audit import GSM_SHA,unused,audit as r0_audit

R0_SHA='84a22408d64ea6849589ecb18fdac9a6398c2c01'
R0_RECEIPT='e7511eaf5ddd1dfee6d8b067e52090e9112334efc0bdfbf36f5f5123e59af24a'
OPS=('+','-','*','/')
SEEDS=(2001,2002,2003)
ARMS=('jepa','no_latent','direct','shuffled')
EPOCHS=40
BATCH=64
BITS=129
FEATURES=132
ARM_SECONDS=150
TOTAL_SECONDS=2200

def emit(event,**fields):
    print('UJ04S '+canonical(dict(event=event,**fields)).decode(),flush=True)

def valid(v):
    return isinstance(v,Fraction) and max(abs(v.numerator).bit_length(),v.denominator.bit_length())<=64

def arithmetic(x,op,y):
    if op=='+': return x+y
    if op=='-': return x-y
    if op=='*': return x*y
    if op=='/': return x/y
    raise ValueError('op')

def key(x,op,y):
    if op in ('+','*') and y<x:
        x,y=y,x
    return op,str(x),str(y)

def read_steps(row):
    out=[]
    for s in row['steps']:
        x,y,z=(Fraction(*s[k]) for k in ('left','right','result'))
        op=s['op']
        if not all(map(valid,(x,y,z))) or arithmetic(x,op,y)!=z:
            raise ValueError('receipt arithmetic')
        out.append((x,op,y,z))
    if not 2<=len(out)<=4:
        raise ValueError('receipt chain length')
    return tuple(out)

def atoms(rows):
    result={}
    for row in rows:
        for x,op,y,z in read_steps(row):
            k=key(x,op,y)
            if k in result and result[k][3]!=z:
                raise ValueError('conflicting result')
            result[k]=(Fraction(k[1]),op,Fraction(k[2]),z)
    return result

def plan(steps):
    start=steps[0][0]
    prev=start
    actions=[]
    truth=[]
    for i,(x,op,y,z) in enumerate(steps):
        if i==0 or (x==prev and y!=prev):
            other,side=y,0
        elif y==prev and x!=prev:
            other,side=x,1
        else:
            raise ValueError('ambiguous chain')
        actions.append((op,other,side))
        truth.append(z)
        prev=z
    return start,tuple(actions),tuple(truth)

def prepare(receipts):
    fit,diag=receipts['fit'],receipts['diagnostic']
    if {r['group'] for r in fit}&{r['group'] for r in diag}:
        raise ValueError('group overlap')
    train=atoms(fit)
    test=atoms(diag)
    unseen={k:v for k,v in test.items() if k not in train}
    chains={}
    mixed=0
    for row in sorted(diag,key=lambda r:r['row_id']):
        steps=read_steps(row)
        ks=tuple(key(x,o,y) for x,o,y,_ in steps)
        if any(k in train for k in ks):
            mixed+=1
            continue
        chains.setdefault(ks,plan(steps))
    coverage=Counter(k[0] for k in unseen)
    gates=dict(fit_atoms=len(train)>=256,unseen_atoms=len(unseen)>=64,
               unseen_chains=len(chains)>=64,all_ops=all(coverage[o]>=16 for o in OPS))
    manifest=dict(fit_atoms=len(train),diagnostic_atoms=len(test),unseen_atoms=len(unseen),
        unseen_atom_ops=dict(coverage),all_unseen_chains=len(chains),
        excluded_chains_with_seen_atoms=mixed,
        duplicate_unseen_chains=len(diag)-mixed-len(chains),criteria=gates,
        eligible=all(gates.values()),train_keys_sha256=digest(canonical(sorted(train))),
        diagnostic_keys_sha256=digest(canonical(sorted(unseen))),
        diagnostic_chain_keys_sha256=digest(canonical(sorted(chains))))
    return tuple(train[k] for k in sorted(train)),tuple(unseen[k] for k in sorted(unseen)),tuple(chains[k] for k in sorted(chains)),manifest

def receipt(raw,old,prior=None):
    if len(raw)!=GSM_BYTES or git_blob(raw)!=GSM_BLOB or digest(raw)!=GSM_SHA:
        raise ValueError('GSM custody')
    if prior is None:
        t0=time.monotonic()
        excluded,om=old_groups(old)
        rows,qm,counts=unused(raw,excluded)
        report,receipts=r0_audit(rows,t0+300,None)
        report.update(source_sha256=GSM_SHA,source_git_blob=GSM_BLOB,source_counts=counts,
                      old_group_partitions=om,excluded_q0_partitions=qm,unused_groups=len(rows))
        prior=canonical(dict(source_sha=R0_SHA,report=report,receipts=receipts))
        mode='EXACT_RECONSTRUCTION'
    else:
        # Old source independently verified by the existing native acquisition step.
        mode='ORIGINAL_RECEIPT'
    if len(prior)!=620241 or digest(prior)!=R0_RECEIPT:
        raise ValueError('R0 receipt custody')
    obj=json.loads(prior)
    if obj['source_sha']!=R0_SHA or not obj['report']['source_feasible'] or obj['report']['model_training_steps']:
        raise ValueError('R0 report custody')
    if len(obj['receipts']['fit'])!=956 or len(obj['receipts']['diagnostic'])!=510:
        raise ValueError('R0 receipt counts')
    return obj['receipts'],mode

def bits(v):
    if not valid(v):
        raise ValueError('numeric bound')
    return [float(v.numerator<0)]+[float((abs(v.numerator)>>i)&1) for i in range(64)]+[float((v.denominator>>i)&1) for i in range(64)]

def features(v):
    return bits(v)+[math.asinh(float(v))/45,
                    math.log2(abs(v.numerator)+1)/64,math.log2(v.denominator+1)/64]

def decode(logits):
    vals=(logits.detach().cpu()>0).tolist()
    n=sum(int(v)<<i for i,v in enumerate(vals[1:65]))
    d=sum(int(v)<<i for i,v in enumerate(vals[65:129]))
    return Fraction(-n if vals[0] else n,d) if d else None

def action(op,side):
    return [float(op==x) for x in OPS]+[float(side)]

def tensor(x):
    return torch.tensor(x,dtype=torch.float32)

def oriented(rows):
    return [(x,o,y,0,z) for x,o,y,z in rows]+[(y,o,x,1,z) for x,o,y,z in rows]

def batch_tensors(rows):
    return (tensor([features(x) for x,o,y,s,z in rows]),tensor([features(y) for x,o,y,s,z in rows]),
            tensor([action(o,s) for x,o,y,s,z in rows]),tensor([bits(z) for x,o,y,s,z in rows]),
            tensor([features(z) for x,o,y,s,z in rows]))

class Latent(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(FEATURES,64),nn.SiLU(),nn.Linear(64,64))
        self.transition=nn.Sequential(nn.Linear(133,128),nn.SiLU(),nn.Linear(128,64))
        self.readout=nn.Sequential(nn.Linear(64,128),nn.SiLU(),nn.Linear(128,BITS))
        self.target=copy.deepcopy(self.encoder).requires_grad_(False)
    def advance(self,state,other,a):
        return self.transition(torch.cat((state,self.encoder(other),a),-1))
    def forward(self,x,y,a):
        state=self.advance(self.encoder(x),y,a)
        return self.readout(state),state
    @torch.no_grad()
    def ema(self):
        for target,online in zip(self.target.parameters(),self.encoder.parameters()):
            target.mul_(.99).add_(online,alpha=.01)

class Direct(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(269,128),nn.SiLU(),nn.Linear(128,96),nn.SiLU(),nn.Linear(96,BITS))
    def forward(self,x,y,a):
        return self.net(torch.cat((x,y,a),-1)),None

class Memory:
    def __init__(self,rows):
        self.exact={key(x,o,y):z for x,o,y,z in rows}
        self.groups={}
        for o in OPS:
            for side in (0,1):
                rr=[(x,y,z) for x,op,y,s,z in oriented(rows) if op==o and s==side]
                self.groups[o,side]=(tensor([features(x)+features(y) for x,y,z in rr]),[z for x,y,z in rr])
    def predict(self,x,op,y,side):
        left,right=(x,y) if not side else (y,x)
        k=key(left,op,right)
        if k in self.exact: return self.exact[k]
        matrix,values=self.groups[op,side]
        if not values: return None
        i=int(((matrix-tensor(features(x)+features(y)))**2).sum(-1).argmin())
        return values[i]

@torch.no_grad()
def roll(model,start,actions):
    current=start
    state=model.encoder(tensor([features(start)])) if isinstance(model,Latent) else None
    results=[]
    for o,y,s in actions:
        if isinstance(model,Latent):
            state=model.advance(state,tensor([features(y)]),tensor([action(o,s)]))
            z=decode(model.readout(state)[0])
        elif current is None:
            z=None
        elif isinstance(model,Direct):
            z=decode(model(tensor([features(current)]),tensor([features(y)]),tensor([action(o,s)]))[0][0])
        elif isinstance(model,Memory):
            z=model.predict(current,o,y,s)
        else:
            z=arithmetic(current,o,y) if not s else arithmetic(y,o,current)
        results.append(z)
        current=z
    return tuple(results)

@torch.no_grad()
def score(model,unseen,chains,deadline):
    ac=Counter()
    n=Counter()
    invalid=0
    bit_brier=None
    if isinstance(model,nn.Module):
        rows=[(x,o,y,0,z) for x,o,y,z in unseen]
        x,y,a,b,_=batch_tensors(rows)
        logits=model(x,y,a)[0]
        if not torch.isfinite(logits).all():
            raise RuntimeError('nonfinite inference')
        bit_brier=float(((logits.sigmoid()-b)**2).mean())
        predictions=[decode(v) for v in logits]
    else:
        predictions=[roll(model,x,((o,y,0),))[0] for x,o,y,z in unseen]
    for (_,o,_,z),pred in zip(unseen,predictions):
        n[o]+=1
        ac[o]+=int(pred==z)
        invalid+=int(pred is None)
    depth=Counter()
    correct=Counter()
    final=0
    all_steps=0
    chain_invalid=0
    for start,actions,truth in chains:
        check_deadline(deadline)
        pred=roll(model,start,actions)
        ok=pred==truth
        depth[len(actions)]+=1
        correct[len(actions)]+=int(ok)
        all_steps+=int(ok)
        final+=int(pred[-1]==truth[-1])
        chain_invalid+=int(None in pred)
    return dict(atom_accuracy=sum(ac.values())/len(unseen),atom_correct=sum(ac.values()),
        atom_count=len(unseen),atom_correct_by_op=dict(ac),atom_counts_by_op=dict(n),
        atom_invalid=invalid,bit_brier=bit_brier,chain_accuracy=all_steps/len(chains),
        chain_correct=all_steps,chain_count=len(chains),final_accuracy=final/len(chains),
        chain_invalid=chain_invalid,chain_correct_by_depth=dict(correct),chain_counts_by_depth=dict(depth))

def train_arm(arm,seed,train,unseen,chains,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    t0=time.monotonic()
    c0=time.process_time()
    torch.manual_seed(seed)
    model=Direct() if arm=='direct' else Latent()
    opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.001)
    rows=oriented(train)
    x,y,a,b,z=batch_tensors(rows)
    changed=None
    if arm=='shuffled':
        bb=b.roll(2,0)
        changed=float((bb!=b).any(-1).float().mean())
        if changed<.80: raise RuntimeError('shuffled negative insufficient')
        b,z=bb,z.roll(2,0)
    weights=torch.ones(BITS)
    weights[0]=4
    weights[1:17]=4
    weights[65:81]=4
    before=score(model,unseen,chains,deadline)
    history=[]
    steps=0
    for epoch in range(EPOCHS):
        gen=torch.Generator().manual_seed(seed*1000+epoch)
        order=torch.randperm(len(rows),generator=gen)
        total=0.
        for ids in order.split(BATCH):
            check_deadline(deadline)
            logits,state=model(x[ids],y[ids],a[ids])
            loss=F.binary_cross_entropy_with_logits(logits,b[ids],weight=weights)
            if arm in ('jepa','shuffled'):
                with torch.no_grad(): target=model.target(z[ids])
                loss=loss+.5*F.smooth_l1_loss(state,target)
            if not torch.isfinite(loss): raise RuntimeError('nonfinite loss')
            opt.zero_grad()
            loss.backward()
            opt.step()
            if arm in ('jepa','shuffled'): model.ema()
            total+=float(loss.detach())*len(ids)
            steps+=1
        history.append(total/len(rows))
    if steps!=EPOCHS*math.ceil(len(rows)/BATCH):
        raise RuntimeError('step accounting')
    after=score(model,unseen,chains,deadline)
    plateau=(max(history[-3:])-min(history[-3:]))/max(abs(history[-3]),1e-12)<=.01
    path=root/(arm+'-'+str(seed)+'.pt')
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),seed=seed,arm=arm),f)
    checkpoint_sha=digest(path.read_bytes())
    count=sum(p.numel() for p in model.parameters() if p.requires_grad)
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,epoch_loss=history,plateau=plateau,
        steps=steps,examples_per_epoch=len(rows),examples_exposed=EPOCHS*len(rows),
        trainable_params=count,shuffled_changed=changed,checkpoint_sha256=checkpoint_sha,
        checkpoint_bytes=path.stat().st_size,wall_seconds=time.monotonic()-t0,cpu_seconds=time.process_time()-c0,
        approximate_training_flops=6*count*EPOCHS*len(rows))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train',type=Path,required=True)
    p.add_argument('--old-train',type=Path,required=True)
    p.add_argument('--prior-receipt',type=Path)
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.receipt.exists():
        raise ValueError('source SHA or prior run')
    if args.old_train.stat().st_size!=BYTES or args.train.stat().st_size!=GSM_BYTES:
        raise ValueError('source size')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    data,mode=receipt(args.train.read_bytes(),args.old_train.read_bytes(),
                      None if args.prior_receipt is None else args.prior_receipt.read_bytes())
    train,unseen,chains,manifest=prepare(data)
    emit('manifest',source_sha=args.source_sha,r0_receipt_sha256=R0_RECEIPT,receipt_mode=mode,
         torch=str(torch.__version__),seeds=SEEDS,arms=ARMS,epochs=EPOCHS,batch=BATCH,**manifest)
    root=args.receipt.parent
    if not manifest['eligible']:
        final=dict(source_eligible=False,model_training_steps=0,continuation_screen=False,
                   scientific_gain_verified=False,protected_evaluation_accessed=False)
    else:
        deadline=time.monotonic()+TOTAL_SECONDS
        mem=Memory(train)
        baseline=score(mem,unseen,chains,deadline)
        symbolic=score(None,unseen,chains,deadline)
        emit('reference',memory=baseline,symbolic=symbolic,
             memory_fit_atoms=len(mem.exact),memory_feature_bytes=sum(m.numel()*m.element_size() for m,_ in mem.groups.values()))
        if symbolic['atom_accuracy']!=1 or symbolic['chain_accuracy']!=1:
            raise RuntimeError('symbolic source consistency')
        completed=[]
        for seed in SEEDS:
            for arm in ARMS:
                emit('arm_started',seed=seed,arm=arm)
                r=train_arm(arm,seed,train,unseen,chains,root,deadline)
                emit('arm_completed',**r)
                completed.append(r)
        checks=[]
        for seed in SEEDS:
            rs={r['arm']:r for r in completed if r['seed']==seed}
            primary=rs['jepa']['after']
            strongest=max(baseline['chain_accuracy'],rs['direct']['after']['chain_accuracy'],rs['no_latent']['after']['chain_accuracy'])
            checks.append(dict(seed=seed,atom=primary['atom_accuracy']>=.95,
                chain=primary['chain_accuracy']>=.90,control_margin=primary['chain_accuracy']-strongest,
                shuffled_margin=primary['chain_accuracy']-rs['shuffled']['after']['chain_accuracy'],
                plateau=rs['direct']['plateau'] and rs['no_latent']['plateau']))
        final=dict(source_eligible=True,arms_completed=len(completed),model_training_steps=sum(r['steps'] for r in completed),
            checks=checks,continuation_screen=all(c['atom'] and c['chain'] and c['control_margin']>=.05 and c['shuffled_margin']>=.10 and c['plateau'] for c in checks),
            mean_atom_accuracy={a:sum(r['after']['atom_accuracy'] for r in completed if r['arm']==a)/len(SEEDS) for a in ARMS},
            mean_chain_accuracy={a:sum(r['after']['chain_accuracy'] for r in completed if r['arm']==a)/len(SEEDS) for a in ARMS},
            memory=baseline,symbolic=symbolic,scientific_gain_verified=False,protected_evaluation_accessed=False,
            convergence_verified=False,compute_parity_verified=False,cold_retention_verified=False)
    payload=canonical(dict(source_sha=args.source_sha,manifest=manifest,result=final))
    with args.receipt.open('xb') as f: f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload): raise RuntimeError('result readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
