"""UJ04V V0: explicit predicted state, separate outcome prediction; DEV only."""
import argparse
import copy
from pathlib import Path
import random
import re
import time

import torch
from torch import nn
from torch.nn import functional as F
import uj04t_microstate_pilot as t
import uj04u_stability_pilot as u
from uj03a_pilot import canonical, digest, check_deadline

SEEDS=(2601,2602,2603)
EPOCHS=800
BATCH=64
ARM_SECONDS=180
TOTAL_SECONDS=3600
ARMS=t.ARMS

def emit(event, **fields):
    print('UJ04V '+canonical(dict(event=event, **fields)).decode(), flush=True)

class Cell(nn.Module):
    def __init__(self):
        super().__init__()
        self.trunk=nn.Sequential(nn.Linear(12,128),nn.SiLU(),nn.Linear(128,128),nn.SiLU())
        self.digit=nn.Linear(128,10)
        self.carry=nn.Linear(128,2)
        self.predict=nn.Linear(128,16)
        self.outcome=nn.Embedding(20,16)
        self.reconstruct=nn.Linear(16,20)
        self.target=copy.deepcopy(self.outcome).requires_grad_(False)

    def encode(self,c):
        u.finite(c)
        if c.ndim!=2 or c.shape[1]!=1 or not bool(((c==0)|(c==1)).all()):
            raise ValueError('invalid explicit state')
        return c

    def heads(self,c,a):
        self.encode(c)
        u.finite(a)
        h=self.trunk(torch.cat((c,a),dim=-1))
        d,n,z=self.digit(h),self.carry(h),self.predict(h).tanh()
        u.finite(h,d,n,z)
        return d,n,z

    def step(self,c,a):
        d,n,_=self.heads(c,a)
        return d,n,n.argmax(dim=-1,keepdim=True).to(c.dtype)

    @torch.no_grad()
    def ema(self):
        self.target.weight.mul_(.99).add_(self.outcome.weight,alpha=.01)

def loss_for(model,c,a,d,n,arm,perm):
    if arm not in ARMS or sorted(perm.tolist())!=list(range(len(c))):
        raise ValueError('arm or permutation')
    pd,pn=d[perm],n[perm]
    ld,ln=(pd,pn) if arm=='shuffled_result' else (d,n)
    label=2*ld+ln
    target_label=2*pd+pn if arm in ('shuffled_aux','shuffled_result') else label
    dl,cl,z=model.heads(c,a)
    embedding=model.outcome(label).tanh()
    reconstruction=model.reconstruct(embedding)
    with torch.no_grad():
        expected=model.target(target_label).tanh()
    aux=F.smooth_l1_loss(z,expected)
    loss=F.cross_entropy(dl,ld)+F.cross_entropy(cl,ln)+F.cross_entropy(reconstruction,label)
    loss=loss+(.0 if arm=='no_latent' else .5)*aux
    u.finite(loss,embedding,expected,reconstruction)
    return loss,int((n!=pn).sum()),int(((d!=pd)|(n!=pn)).sum())

def fresh_cases(deadline):
    old_u={(op,w,a,b) for op,w,_,a,b in u.fresh_cases(deadline)}
    out=[]
    for w in t.WIDTHS:
        cap=10**w; mid=10**(w-1)
        for op in (0,1):
            old={(a,b) for _,_,_,a,b in t.cases_for(op,w)}
            old.update((a,b) for o,k,a,b in old_u if (o,k)==(op,w))
            offsets=range(2,100)
            families=(
                [(cap-k,k) for k in offsets],
                [(cap-k,cap-k) for k in offsets],
                [(mid-k,k) for k in offsets],
                [(k,0) for k in offsets]
            ) if op==0 else (
                [(mid+1,k) for k in offsets],
                [(cap-k,cap-k) for k in offsets],
                [(mid+k,mid) for k in offsets],
                [(k,0) for k in offsets]
            )
            seen=set()
            for family in families:
                pair=next((q for q in family if q not in old and q not in seen
                    and all(0<=x<cap for x in q) and (not op or q[0]>=q[1])),None)
                if pair is None: raise RuntimeError('fresh stress exhaustion')
                seen.add(pair); out.append((op,w,'stress',*pair))
            rng=random.Random(20261126+100*w+op)
            for _ in range(10000):
                check_deadline(deadline)
                if len(seen)==132: break
                a,b=rng.randrange(cap),rng.randrange(cap)
                if op and a<b: a,b=b,a
                if (a,b) in old or (a,b) in seen: continue
                seen.add((a,b)); out.append((op,w,'random',a,b))
            if len(seen)!=132: raise RuntimeError('fresh random exhaustion')
    if len(out)!=1056 or len(set(out))!=1056: raise RuntimeError('case accounting')
    return tuple(out)

def train_arm(arm,seed,fit,test,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic(); cpu=time.process_time()
    torch.manual_seed(seed)
    model=Cell()
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    c,a,d,n=t.batch(fit)
    before=dict(fit=t.local_score(model,fit,'factorized'),known=t.local_score(model,test,'factorized'))
    history=[]; steps=cm=pm=exposures=0
    for epoch in range(EPOCHS):
        ids=torch.randperm(len(fit),generator=torch.Generator().manual_seed(seed*1000+epoch))
        total=0.
        for ii in ids.split(BATCH):
            check_deadline(deadline)
            perm=torch.randperm(len(ii),generator=torch.Generator().manual_seed(seed*100000+steps))
            opt.zero_grad()
            loss,x,y=loss_for(model,c[ii],a[ii],d[ii],n[ii],arm,perm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
            opt.step(); model.ema()
            u.finite(*params,*model.target.parameters())
            total+=float(loss.detach())*len(ii)
            steps+=1; cm+=x; pm+=y; exposures+=len(ii)
        history.append(total/len(fit))
    if steps!=4000 or exposures!=EPOCHS*len(fit) or cm/exposures<.25 or pm/exposures<.80:
        raise RuntimeError('exposure or permutation accounting')
    after=dict(fit=t.local_score(model,fit,'factorized'),known=t.local_score(model,test,'factorized'))
    last=history[-10:]; delta=max(last)-min(last)
    plateau=delta<=.001 or delta/max(abs(last[0]),1e-12)<=.03
    with torch.no_grad():
        sep=float(torch.pdist(model.target.weight.tanh()).min())
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if h!=digest(path.read_bytes()): raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    row=dict(arm=arm,seed=seed,before=before,after=after,steps=steps,examples_exposed=exposures,
        carry_mismatch=cm/exposures,pair_mismatch=pm/exposures,plateau=plateau,
        loss_first=history[0],loss_last_ten=last,min_target_separation=sep,
        trainable_params=sum(p.numel() for p in params),checkpoint_sha256=h,
        checkpoint_bytes=path.stat().st_size,wall_seconds=time.monotonic()-start,
        cpu_seconds=time.process_time()-cpu)
    return row,model

def mastery(rows,seeds=SEEDS):
    checks=[]
    for seed in seeds:
        arms={r['arm']:r for r in rows if r['seed']==seed}
        if set(arms)!=set(ARMS): raise RuntimeError('incomplete arms')
        n,j=arms['no_latent'],arms['jepa']
        checks.append(dict(seed=seed,control_fit=n['after']['fit']['exact']>=.98,
            control_known=n['after']['known']['exact']>=.95,control_plateau=n['plateau'],
            jepa_fit=j['after']['fit']['exact']>=.98,jepa_known=j['after']['known']['exact']>=.95))
    return checks,all(all(v for k,v in c.items() if k!='seed') for c in checks)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.receipt.exists():
        raise ValueError('source SHA or prior receipt')
    root=args.receipt.parent
    if not root.is_dir() or any(root.iterdir()): raise RuntimeError('exclusive trial directory required')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    fit,test=t.local_data()
    manifest=dict(source_sha=args.source_sha,fit_sha256=digest(canonical(fit)),
        known_local_diagnostic_sha256=digest(canonical(test)),seeds=SEEDS,arms=ARMS,
        epochs=EPOCHS,batch=BATCH,torch=str(torch.__version__),protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[]; models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',seed=seed,arm=arm)
            row,model=train_arm(arm,seed,fit,test,root,deadline)
            rows.append(row); models[seed,arm]=model; emit('arm_completed',**row)
    local,eligible=mastery(rows)
    emit('mastery_gate',checks=local,composition_eligible=eligible)
    composition=None; checks=[]; screen=False
    if eligible:
        cases=fresh_cases(deadline)
        truth={case:t.reference(case)[0] for case in cases}
        emit('composition_manifest',word_sha256=digest(canonical(cases)),word_count=len(cases))
        memory=t.score(t.Memory(fit),'memory',fit,test,cases,truth,deadline)
        symbolic=t.score(None,'symbolic',fit,test,cases,truth,deadline)
        if symbolic['trace_accuracy']!=1 or symbolic['value_accuracy']!=1:
            raise RuntimeError('symbolic reference failure')
        scores=[]
        for seed in SEEDS:
            measured={}
            for arm in ARMS:
                result=t.score(models[seed,arm],'factorized',fit,test,cases,truth,deadline)
                measured[arm]=result; scores.append(dict(seed=seed,arm=arm,score=result))
                emit('composition_score',seed=seed,arm=arm,score=result)
            j=measured['jepa']
            strongest=max(memory['trace_accuracy'],measured['no_latent']['trace_accuracy'],
                measured['shuffled_aux']['trace_accuracy'])
            checks.append(dict(seed=seed,worst_stratum=min(v['trace_correct']/v['count']
                for v in j['strata'].values()),control_margin=j['trace_accuracy']-strongest,
                negative_margin=j['trace_accuracy']-measured['shuffled_result']['trace_accuracy']))
        screen=all(c['worst_stratum']>=.90 and c['control_margin']>=.05
            and c['negative_margin']>=.10 for c in checks)
        composition=dict(word_sha256=digest(canonical(cases)),memory=memory,symbolic=symbolic,scores=scores)
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
        examples_exposed=sum(r['examples_exposed'] for r in rows),mastery_checks=local,
        composition_executed=eligible,composition_checks=checks,continuation_screen=screen,
        scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
        protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,composition=composition,result=final))
    with args.receipt.open('xb') as f: f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload): raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
