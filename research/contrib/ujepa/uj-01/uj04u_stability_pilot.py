"""UJ04U U0: isolated bounded self-fed numeric-state DEV falsification."""
import argparse
from collections import defaultdict
from pathlib import Path
import random
import re
import time

import torch
from torch.nn import functional as F
import uj04t_microstate_pilot as t
from uj03a_pilot import canonical, digest, check_deadline

SEEDS=(2501,2502,2503)
LENGTHS=(2,4,8,16)
STEPS=800
BATCH=32
TOTAL_SECONDS=1800
ARM_SECONDS=120
ARMS=t.ARMS

def emit(event, **fields):
    print('UJ04U '+canonical(dict(event=event, **fields)).decode(), flush=True)

def finite(*values):
    if not all(bool(torch.isfinite(v).all()) for v in values):
        raise RuntimeError('nonfinite U0 state, output or gradient')

class Cell(t.Cell):
    def encode(self,c):
        finite(c)
        z=self.encoder(c)
        finite(z)
        return z.tanh()
    def step(self,state,a):
        finite(state,a)
        z=self.transition(torch.cat((state,a),dim=-1))
        finite(z)
        nxt=z.tanh()
        logits=self.readout(nxt)
        finite(logits,nxt)
        return logits[:,:10],logits[:,10:],nxt

def fresh_cases(deadline):
    out=[]
    for w in t.WIDTHS:
        cap=10**w
        mid=10**(w-1)
        for op in (0,1):
            old={(a,b) for _,_,_,a,b in t.cases_for(op,w)}
            # One deterministic unused pair from each prespecified stress family.
            offsets=range(2,10)
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
            stress=[]
            for family in families:
                pair=next((p for p in family if p not in old and p not in stress),None)
                if pair is None: raise RuntimeError('fresh stress family exhausted')
                stress.append(pair)
            seen=set(stress)
            out.extend((op,w,'stress',a,b) for a,b in stress)
            rng=random.Random(20261125+100*w+op)
            for _ in range(10000):
                check_deadline(deadline)
                if len(seen)==132: break
                a,b=rng.randrange(cap),rng.randrange(cap)
                if op and a<b: a,b=b,a
                if (a,b) in old or (a,b) in seen: continue
                seen.add((a,b)); out.append((op,w,'random',a,b))
            if len(seen)!=132: raise RuntimeError('diagnostic exhaustion')
    if len(out)!=1056 or len(set(out))!=1056: raise RuntimeError('case accounting')
    return tuple(out)

def operand_key(path):
    op,c=path[0][:2]
    return (op,len(path),sum(r[2]*10**i for i,r in enumerate(path)),
            sum(r[3]*10**i for i,r in enumerate(path))) if c==0 else None

def make_batches(fit,seed,blocked,deadline,steps=STEPS,batch_size=BATCH):
    pools=defaultdict(list)
    for r in fit: pools[r[:2]].append(r)
    if set(pools)!={(0,0),(0,1),(1,0),(1,1)}: raise ValueError('missing fit stratum')
    rng=random.Random(seed)
    batches=[]
    for i in range(steps):
        check_deadline(deadline)
        width=LENGTHS[i%len(LENGTHS)]
        batch=[]
        for _ in range(10000):
            if len(batch)==batch_size: break
            op,c=rng.randrange(2),rng.randrange(2)
            path=[]
            for j in range(width):
                row=rng.choice(pools[op,c]); path.append(row); c=row[5]
            if operand_key(path) not in blocked: batch.append(tuple(path))
        if len(batch)!=batch_size: raise RuntimeError('training path exhaustion')
        batches.append(tuple(batch))
    return tuple(batches)

def pack(paths):
    if not paths or not paths[0] or any(len(x)!=len(paths[0]) for x in paths):
        raise ValueError('path batch')
    for path in paths:
        if any(a[0]!=b[0] or a[5]!=b[1] for a,b in zip(path,path[1:])):
            raise ValueError('inconsistent training path')
    init=t.tensor([[p[0][1]] for p in paths])
    actions=t.tensor([[t.action(r[0],r[2],r[3]) for r in p] for p in paths])
    digits=torch.tensor([[r[4] for r in p] for p in paths])
    carries=torch.tensor([[r[5] for r in p] for p in paths])
    return init,actions,digits,carries

def sequence_loss(model,packed,arm,permutation):
    if arm not in ARMS: raise ValueError('arm')
    init,actions,digits,carries=packed
    if sorted(permutation.tolist())!=list(range(len(init))): raise ValueError('permutation')
    sd,sc=digits[permutation],carries[permutation]
    target=sc if arm in ('shuffled_aux','shuffled_result') else carries
    label_d,label_c=(sd,sc) if arm=='shuffled_result' else (digits,carries)
    state=model.encode(init)
    losses=[]
    for j in range(actions.shape[1]):
        dl,cl,state=model.step(state,actions[:,j,:])
        loss=F.cross_entropy(dl,label_d[:,j])+F.cross_entropy(cl,label_c[:,j])
        if arm!='no_latent':
            with torch.no_grad():
                raw=model.target(target[:,j,None].float())
                finite(raw)
                expected=raw.tanh()
            loss=loss+.5*F.smooth_l1_loss(state,expected)
        finite(loss,state)
        losses.append(loss)
    return torch.stack(losses).mean(),int((carries!=sc).sum()),int(((digits!=sd)|(carries!=sc)).sum())

def train_arm(arm,seed,batches,fit,test,cases,truth,root,overall):
    deadline=min(overall,time.monotonic()+ARM_SECONDS)
    start=time.monotonic(); cpu=time.process_time()
    torch.manual_seed(seed)
    model=Cell()
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.003)
    before=t.score(model,arm,fit,test,cases,truth,deadline)
    explicit_before=t.score(model,'explicit',fit,test,cases,truth,deadline) if arm=='no_latent' else None
    history=[]; columns=carry_mismatch=pair_mismatch=0
    for i,paths in enumerate(batches):
        check_deadline(deadline)
        packed=pack(paths)
        permutation=torch.randperm(BATCH,generator=torch.Generator().manual_seed(seed*100000+i))
        opt.zero_grad()
        loss,cm,pm=sequence_loss(model,packed,arm,permutation)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
        opt.step()
        finite(*params)
        if arm!='no_latent':
            model.ema()
            finite(*model.target.parameters())
        columns+=packed[2].numel(); carry_mismatch+=cm; pair_mismatch+=pm
        history.append(float(loss.detach()))
    if len(history)!=STEPS or carry_mismatch/columns<.25 or pair_mismatch/columns<.80:
        raise RuntimeError('matched update/exposure or negative control mismatch')
    after=t.score(model,arm,fit,test,cases,truth,deadline)
    explicit=t.score(model,'explicit',fit,test,cases,truth,deadline) if arm=='no_latent' else None
    # Compare equal-length cyclic losses to avoid a mixture of different rollout lengths.
    last=[sum(history[i:i+4])/4 for i in range(STEPS-40,STEPS,4)]
    delta=max(last)-min(last)
    plateau=delta<=.001 or delta/max(abs(last[0]),1e-12)<=.03
    path=root/('%s-%d.pt'%(arm,seed))
    with path.open('xb') as f:
        torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),arm=arm,seed=seed),f)
    h=digest(path.read_bytes())
    if h!=digest(path.read_bytes()): raise RuntimeError('checkpoint readback')
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,before_explicit=explicit_before,
        after_explicit=explicit,steps=len(history),columns_exposed=columns,plateau=plateau,
        loss_first=history[0],loss_last_ten_cycles=last,carry_mismatch=carry_mismatch/columns,
        pair_mismatch=pair_mismatch/columns,trainable_params=sum(p.numel() for p in params),
        checkpoint_sha256=h,checkpoint_bytes=path.stat().st_size,
        wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu)

def checks_for(completed,baseline):
    checks=[]
    for seed in SEEDS:
        rows={r['arm']:r for r in completed if r['seed']==seed}
        if set(rows)!=set(ARMS): raise RuntimeError('incomplete arms')
        j=rows['jepa']['after']; n=rows['no_latent']
        control=max(baseline['trace_accuracy'],n['after']['trace_accuracy'],
            n['after_explicit']['trace_accuracy'],rows['shuffled_aux']['after']['trace_accuracy'])
        worst=min(m['trace_correct']/m['count'] for m in j['strata'].values())
        checks.append(dict(seed=seed,local=j['heldout']['exact']>=.95,worst_stratum=worst,
            control_margin=j['trace_accuracy']-control,
            negative_margin=j['trace_accuracy']-rows['shuffled_result']['after']['trace_accuracy'],
            control_fit=n['after']['fit']['exact']>=.98,control_plateau=n['plateau']))
    return checks

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
    cases=fresh_cases(deadline)
    truth={case:t.reference(case)[0] for case in cases}
    blocked={(op,w,a,b) for op,w,_,a,b in cases}
    batches={seed:make_batches(fit,seed,blocked,deadline) for seed in SEEDS}
    manifest=dict(source_sha=args.source_sha,fit_sha256=digest(canonical(fit)),
        known_local_diagnostic_sha256=digest(canonical(test)),fresh_word_sha256=digest(canonical(cases)),
        batch_sha256={str(s):digest(canonical(batches[s])) for s in SEEDS},
        seeds=SEEDS,arms=ARMS,lengths=LENGTHS,steps=STEPS,batch=BATCH,word_count=len(cases),
        torch=str(torch.__version__),protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    baseline=t.score(t.Memory(fit),'memory',fit,test,cases,truth,deadline)
    symbolic=t.score(None,'symbolic',fit,test,cases,truth,deadline)
    if symbolic['trace_accuracy']!=1 or symbolic['value_accuracy']!=1 or symbolic['heldout']['exact']!=1:
        raise RuntimeError('symbolic reference failure')
    emit('reference',memory=baseline,symbolic=symbolic)
    completed=[]
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',arm=arm,seed=seed)
            row=train_arm(arm,seed,batches[seed],fit,test,cases,truth,root,deadline)
            completed.append(row); emit('arm_completed',**row)
    checks=checks_for(completed,baseline)
    screen=all(c['local'] and c['worst_stratum']>=.90 and c['control_margin']>=.05
        and c['negative_margin']>=.10 and c['control_fit'] and c['control_plateau'] for c in checks)
    final=dict(arms_fitted=len(completed),updates=sum(r['steps'] for r in completed),
        columns_exposed=sum(r['columns_exposed'] for r in completed),checks=checks,
        continuation_screen=screen,scientific_gain_verified=False,compute_parity_verified=False,
        cold_retention_verified=False,protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,reference=dict(memory=baseline,symbolic=symbolic),
        arms=completed,result=final))
    with args.receipt.open('xb') as f: f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload): raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
