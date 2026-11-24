"""UJ-03B: fresh TRAIN-source groups, matched candidate-choice DEV training."""
import argparse
from collections import Counter
import io
import math
import random
import time
from pathlib import Path
import re

import torch
from torch.nn import functional as F

from learned_jepa import LearnedJEPA
from pair_controls import PairControl
from grounded_eval import evaluate
from checkpoint import representation_health
from symbolic_control import scores as symbolic_scores
from uj03a_pilot import SHA256, BYTES, select, digest, canonical, group, check_deadline

ARMS = ('positive_only', 'contrastive', 'contrastive_wide', 'shuffled', 'recurrent', 'attention')
SEEDS = (1801, 1802, 1803)
BATCH = 8
EPOCHS = (8, 4)
STAGE1, STAGE2, DIAG = 512, 256, 128
ARM_SECONDS, TOTAL_SECONDS = 180, 3300

def emit(event, **fields):
    print('UJ03B ' + canonical(dict(event=event, **fields)).decode(), flush=True)

def fresh(raw, expected=SHA256, n1=STAGE1, n2=STAGE2, nd=DIAG, skip=640):
    prior, tail, _ = select(raw, expected, skip+n1+nd+n2, nd)
    parts = (prior[skip:skip+n1], prior[skip+n1:skip+n1+nd],
             prior[skip+n1+nd:], tail)
    groups = [set(group(r[2].decode()) for r in part) for part in (prior[:skip],)+parts]
    if any(a & b for i,a in enumerate(groups) for b in groups[i+1:]):
        raise RuntimeError('group leakage')
    manifest = [dict(count=len(g), groups_sha256=digest(canonical(sorted(g))),
                     ids_sha256=digest(canonical([r[0] for r in part])))
                for g,part in zip(groups,(prior[:skip],)+parts)]
    return parts, manifest

class FastJEPA(LearnedJEPA):
    def encode(self, rows, target=False):
        if not 2 <= len(rows) <= 64 or any(type(r) is not bytes or not 1 <= len(r) <= 256 for r in rows):
            raise ValueError('signal bounds')
        lengths = torch.tensor([len(r) for r in rows], dtype=torch.long)
        signal = torch.zeros(len(rows), int(lengths.max()), 8)
        bits = torch.arange(8)
        for i,row in enumerate(rows):
            signal[i,:len(row)] = 2*((torch.tensor(list(row))[:,None] >> bits)&1)-1
        return (self.target if target else self.online)(signal, lengths)

def model_for(arm, seed):
    if arm not in ARMS:
        raise ValueError('unknown arm')
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        if arm in ('recurrent','attention'):
            return PairControl(arm)
        return FastJEPA(width=32,latent=16) if arm=='contrastive_wide' else FastJEPA()

def scores(model, rows):
    contexts = tuple(r[2] for r in rows)
    options = tuple(o for r in rows for o in r[3])
    n = len(rows)
    if isinstance(model, LearnedJEPA):
        z = model.encode(contexts)
        logp, means = model._distribution(z)
        with torch.no_grad():
            y = model.encode(options,target=True).reshape(n,5,model.latent)
        logits = torch.logsumexp(logp[:,None,:] -
            (means[:,None,:,:]-y[:,:,None,:]).square().sum(-1)/.5, dim=-1)
        return logits,z,y
    x = model.encode(contexts)
    y = model.encode(options).reshape(n,5,-1)
    return (x[:,None,:]*y).sum(-1),x,y

def loss_for(model, rows, labels, arm):
    logits,z,_ = scores(model,rows)
    labels = torch.tensor(labels,dtype=torch.long)
    if isinstance(model,LearnedJEPA):
        # Same latent positive objective in both arms; explicit candidate
        # discrimination is the only narrow-arm objective difference.
        pos = -logits.gather(1,labels[:,None]).mean()
        online_choices = model.encode(tuple(o for r in rows for o in r[3]))
        reg = sum(F.relu(.2-torch.sqrt(v.var(0,unbiased=False)+1e-4)).mean()
                  for v in (z,online_choices))/2
        return pos+reg+(0 if arm=='positive_only' else F.cross_entropy(logits,labels))
    return F.cross_entropy(logits,labels)

def labels_for(rows, arm, seed):
    original = [r[4] for r in rows]
    labels = original.copy()
    if arm=='shuffled':
        random.Random(seed+991).shuffle(labels)
        if labels==original:
            raise ValueError('degenerate shuffle')
    assert Counter(labels)==Counter(original)
    return labels

def fit(model, rows, arm, seed, epochs, deadline):
    if len(rows)%BATCH or not 1<=epochs<=8:
        raise ValueError('invalid fixed training budget')
    labels=labels_for(rows,arm,seed)
    opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=.001,weight_decay=0.)
    rng=random.Random(seed)
    order=list(range(len(rows)))
    history=[]
    model.train()
    for _ in range(epochs):
        rng.shuffle(order)
        losses=[]
        for offset in range(0,len(order),BATCH):
            check_deadline(deadline)
            ids=order[offset:offset+BATCH]
            opt.zero_grad(set_to_none=True)
            loss=loss_for(model,[rows[i] for i in ids],[labels[i] for i in ids],arm)
            if not torch.isfinite(loss):
                raise RuntimeError('nonfinite loss')
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad):
                raise RuntimeError('invalid gradient')
            opt.step()
            model.update_target()
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise RuntimeError('nonfinite parameter')
            losses.append(float(loss.detach()))
        history.append(sum(losses)/len(losses))
    model.eval()
    check_deadline(deadline)
    # Last-three-epoch loss plateau is a screen, not proof of convergence.
    plateau=len(history)>=3 and max(abs(a-b)/max(abs(a),1e-8) for a,b in zip(history[-3:-1],history[-2:]))<=.01
    return dict(steps=epochs*len(rows)//BATCH, observations=epochs*len(rows),
        exposure_bytes=epochs*sum(len(r[2])+sum(map(len,r[3])) for r in rows),
        epoch_loss=history, plateau_screen=plateau,
        shuffled_changed=sum(a!=b for a,b in zip(labels,[r[4] for r in rows])))

@torch.no_grad()
def measure(model, rows, deadline):
    # Batched scoring shares the training path, and sees no correct labels.
    cached={}
    for i in range(0,len(rows),BATCH):
        check_deadline(deadline)
        chunk=rows[i:i+BATCH]
        if len(chunk)<2:
            raise ValueError('diagnostic singleton')
        vals,_,_=scores(model,chunk)
        for r,v in zip(chunk,vals):
            cached[(r[2],r[3])]=v.tolist()
    return evaluate(rows,lambda c,o:cached[(c,o)])['all']

def run_arm(arm,seed,parts,overall):
    t0,c0=time.monotonic(),time.process_time()
    deadline=min(overall,t0+ARM_SECONDS)
    tr,old,second,new=parts
    model=model_for(arm,seed)
    model.eval()
    before=measure(model,old,deadline)
    a=fit(model,tr,arm,seed,EPOCHS[0],deadline)
    old1=measure(model,old,deadline)
    new1=measure(model,new,deadline)
    # In-memory serialized weight reload into a fresh model, not a process
    # restart or optimizer-resume claim.
    buf=io.BytesIO()
    torch.save(model.state_dict(),buf)
    state_hash=digest(buf.getvalue())
    buf.seek(0)
    restored=model_for(arm,seed+10000)
    restored.load_state_dict(torch.load(buf,weights_only=True,map_location='cpu'),strict=True)
    restored.eval()
    if measure(restored,old,deadline)!=old1:
        raise RuntimeError('reload mismatch')
    del model
    b=fit(restored,second,arm,seed+100,EPOCHS[1],deadline)
    old2=measure(restored,old,deadline)
    new2=measure(restored,new,deadline)
    health=representation_health(restored,[r[2] for r in old[:32]]) if isinstance(restored,LearnedJEPA) else None
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,old_stage1=old1,new_stage1=new1,
        old_stage2=old2,new_stage2=new2,old_brier_drift=old2['brier']-old1['brier'],
        stage1=a,stage2=b,reload_sha256=state_hash,reload_exact=True,
        representation_health=health,parameters=sum(p.numel() for p in restored.parameters() if p.requires_grad),
        wall_seconds=time.monotonic()-t0,cpu_seconds=time.process_time()-c0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train',type=Path,required=True)
    p.add_argument('--source-sha',required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.train.stat().st_size!=BYTES:
        raise ValueError('source custody')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    parts,manifest=fresh(args.train.read_bytes())
    emit('manifest',source_sha=args.source_sha,train_sha256=SHA256,groups=manifest,
         arms=ARMS,seeds=SEEDS,epochs=EPOCHS,batch=BATCH,torch=str(torch.__version__),
         scope='TRAIN_SOURCE_ONLY_DEVELOPMENT_NOT_SCIENCE')
    tr,old,second,new=parts
    for name,rows in [('old',old),('new',new)]:
        covered=[0]
        def symbolic(c,o):
            values,ok=symbolic_scores(c,o)
            covered[0]+=int(ok)
            return values
        counts=Counter(r[3][r[4]] for r in tr)
        emit('reference',partition=name,uniform=evaluate(rows,lambda c,o:[0.]*len(o))['all'],
             frequency=evaluate(rows,lambda c,o:[math.log1p(counts[x]) for x in o])['all'],
             symbolic=evaluate(rows,symbolic)['all'],symbolic_coverage=covered[0]/len(rows))
    out=[]
    for seed in SEEDS:
        for arm in ARMS:
            check_deadline(deadline)
            emit('arm_started',arm=arm,seed=seed)
            result=run_arm(arm,seed,parts,deadline)
            emit('arm_completed',**result)
            out.append(result)
    means={a:sum(r['old_stage1']['accuracy'] for r in out if r['arm']==a)/len(SEEDS) for a in ARMS}
    strongest=max(means[a] for a in ('recurrent','attention','positive_only'))
    paired=[next(r for r in out if r['arm']=='contrastive' and r['seed']==s)['old_stage1']['accuracy']-
            max(r['old_stage1']['accuracy'] for r in out if r['arm'] in ('recurrent','attention','positive_only') and r['seed']==s) for s in SEEDS]
    screen=(means['contrastive']-means['shuffled']>=.10 and means['contrastive']-strongest>=.05
            and min(paired)>0 and all(r['old_brier_drift']<=.02 for r in out if r['arm']=='contrastive')
            and all(r['stage1']['plateau_screen'] for r in out if r['arm'] in ('recurrent','attention')))
    emit('complete',arms_completed=len(out),mean_stage1_accuracy=means,continuation_screen=screen,
         scientific_gain_verified=False,protected_evaluation_accessed=False,
         baseline_convergence_verified=False,compute_parity_verified=False,
         cold_process_retention_verified=False,unfamiliar_structure_transfer_verified=False)

if __name__=='__main__':
    main()
