"""UJ04Q Q0: source-only annotated arithmetic feasibility; no training."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import time

from uj03a_pilot import SHA256, BYTES, group, digest, canonical, check_deadline
from uj04p_source_audit import pools, parse_fragment, chain_key, rational, decision

GSM_BLOB='7d97154b91aef28d01c3301741c81ce90039a4b1'
GSM_BYTES=4166206
FIT,DIAG=3072,1024
OLD_GROUP_HASHES=(
    '3e85603fa88fe04c75a9ef3fa9ce6a6b7618be04eaa82ee64373a8e8f60041d7',
    '81220bdf70a435373fce0f0dd304bf4abfe05703590ab4a1c5e32da1f2a47655',
    '9d6630ed0028ed0a3ca58010a8d3520e8b886cd3f077e2df5590eec42d026c3a')
DELIM=re.compile(r'<{2,}|>{2,}')
FINAL=re.compile(r'(?m)^[ \t]*####')

def git_blob(raw):
    return hashlib.sha1(('blob '+str(len(raw))+'\0').encode('ascii')+raw).hexdigest()

def old_groups(raw):
    if len(raw)!=BYTES or digest(raw)!=SHA256:
        raise ValueError('old source drift')
    parts,manifest=pools(raw,SHA256,2304,3072,1024)
    if tuple(x['group_sha256'] for x in manifest)!=OLD_GROUP_HASHES:
        raise RuntimeError('old group custody mismatch')
    g={group(row[2].decode()) for part in parts for row in part}
    if len(g)!=6400:
        raise RuntimeError('old groups not unique')
    return g,manifest

def annotations(answer):
    counts=Counter()
    if type(answer) is not str or not answer.strip():
        return None,'missing_answer',counts
    if len(answer)>65536:
        return None,'answer_bound',counts
    end=FINAL.search(answer)
    text=answer[:end.start()] if end else answer
    fragments=[]
    opening=None
    for m in DELIM.finditer(text):
        token=m.group()
        if token=='<<' and opening is None:
            opening=m
        elif token=='>>' and opening is not None:
            inner=text[opening.end():m.start()]
            if '<' in inner or '>' in inner:
                return None,'malformed_annotation',counts
            step,reason=parse_fragment(inner)
            counts[reason or 'verified_equation']+=1
            fragments.append((step,(opening.start(),m.end())))
            opening=None
        else:
            return None,'malformed_annotation',counts
    if opening is not None:
        return None,'malformed_annotation',counts
    if not fragments:
        return None,'no_annotation',counts
    for reason in ('conflicting_arithmetic','zero_divisor','numeric_bound','independent_unsupported'):
        if counts[reason]:
            return None,reason,counts
    verified=[(i,s) for i,(s,_) in enumerate(fragments) if s is not None]
    successors=Counter()
    for j,s in verified:
        links=[(i,side) for i,t in verified if i<j
               for side,value in enumerate((s[0],s[2])) if t[3]==value]
        if len(links)>1:
            return None,'ambiguous_linkage',counts
        if links:
            successors[links[0][0]]+=1
    if any(v>1 for v in successors.values()):
        return None,'branching_linkage',counts
    runs=[]
    current=[]
    for step,span in fragments:
        if step is None:
            if current: runs.append(current)
            current=[]
            continue
        if current:
            previous=current[-1][0][3]
            if (step[0]==previous)+(step[2]==previous)!=1:
                runs.append(current)
                current=[]
        current.append((step,span))
    if current: runs.append(current)
    for run in runs:
        if 2<=len(run)<=4:
            if len({s[3] for s,_ in run})!=len(run):
                return None,'repeated_result',counts
            return run,None,counts
        if len(run)>4:
            counts['chain_too_long']+=1
    return None,'no_eligible_chain',counts

def select_gsm(raw,excluded,fit=FIT,diag=DIAG):
    if type(raw) is not bytes or not 0<len(raw)<=16*1024**2:
        raise ValueError('source size')
    if min(fit,diag)<1:
        raise ValueError('partition size')
    # Decode strictly before selection; no annotation/answer-based sampling.
    sha=digest(raw)
    counts=Counter()
    unique={}
    for i,line in enumerate(raw.decode('utf-8',errors='strict').splitlines()):
        obj=json.loads(line)
        if (type(obj) is not dict or type(obj.get('question')) is not str
                or not obj['question'].strip() or type(obj.get('answer')) is not str):
            raise ValueError('source schema')
        counts['rows']+=1
        g=group(obj['question'])
        if g in unique:
            counts['duplicate_group_rows']+=1
            continue
        unique[g]=(sha+':'+str(i),g,obj['answer'])
    counts['unique_groups']=len(unique)
    counts['excluded_old_groups']=sum(g in excluded for g in unique)
    order=sorted((g for g in unique if g not in excluded),
                 key=lambda g:digest(('UJ04Q:20261124:'+g).encode()))
    counts['eligible_groups']=len(order)
    if len(order)<fit+diag:
        raise ValueError('insufficient new groups')
    parts=(tuple(unique[g] for g in order[:fit]),
           tuple(unique[g] for g in order[fit:fit+diag]))
    gs=[{r[1] for r in part} for part in parts]
    if gs[0]&gs[1] or (gs[0]|gs[1])&excluded:
        raise RuntimeError('group overlap')
    manifest=[dict(count=len(part),group_sha256=digest(canonical(sorted(g))),
                   ids_sha256=digest(canonical([r[0] for r in part])))
              for part,g in zip(parts,gs)]
    return parts,manifest,dict(counts)

def scan(rows,deadline):
    receipts=[]
    keys=set()
    ops,lengths,pairs,rejects,fragments=(Counter() for _ in range(5))
    tuples=set()
    for row_id,g,answer in rows:
        check_deadline(deadline)
        run,reason,counts=annotations(answer)
        fragments.update(counts)
        if reason:
            rejects[reason]+=1
            continue
        steps=[s for s,_ in run]
        key=chain_key(steps)
        keys.add(key)
        tuples.update(key)
        ops.update(s[1] for s in steps)
        lengths[len(steps)]+=1
        pairs.update(set(a[1]+b[1] for a,b in zip(steps,steps[1:])))
        receipts.append(dict(row_id=row_id,group=g,answer_sha256=digest(answer.encode()),
            steps=[dict(left=rational(x),op=op,right=rational(y),result=rational(z),
                        span=list(span)) for (x,op,y,z),span in run]))
    if len(receipts)+sum(rejects.values())!=len(rows):
        raise RuntimeError('receipt accounting')
    return receipts,keys,dict(rows=len(rows),accepted_chains=len(receipts),rejected_rows=dict(rejects),
        fragment_counts=dict(fragments),op_transitions=dict(ops),chain_lengths=dict(lengths),
        ordered_pair_chain_counts=dict(pairs),unique_ordered_pairs=len(pairs),
        unique_operand_result_tuples=len(tuples),unique_full_chains=len(keys),
        receipt_sha256=digest(canonical(receipts)))

def old_receipt_keys(raw):
    # Only an exact prior receipt can establish cross-source chain overlap.
    if digest(raw)!='1947dd5f9e26fd0fe9fbd743680da4de6b65d95058dc4dcf04c391288aaa3eef':
        raise ValueError('prior receipt drift')
    from fractions import Fraction
    obj=json.loads(raw)
    return {chain_key([(Fraction(*s['left']),s['op'],Fraction(*s['right']),Fraction(*s['result']))
                      for s in row['steps']])
            for part in ('fit','diagnostic') for row in obj['receipts'][part]}

def audit(raw,excluded,deadline,fit=FIT,diag=DIAG,prior_keys=None):
    parts,manifest,counts=select_gsm(raw,excluded,fit,diag)
    a,ak,am=scan(parts[0],deadline)
    b,bk,bm=scan(parts[1],deadline)
    overlap=len(ak&bk)
    report=dict(source_sha256=digest(raw),group_partitions=manifest,source_counts=counts,
        fit=am,diagnostic=bm,group_overlap=0,exact_full_chain_overlap=overlap,
        cross_source_chain_overlap=None if prior_keys is None else len((ak|bk)&prior_keys),
        cross_source_chain_overlap_verified=prior_keys is not None,
        **decision(am,bm,overlap),model_training_steps=0,
        protected_evaluation_accessed=False,scientific_gain_verified=False)
    check_deadline(deadline)
    return report,dict(fit=a,diagnostic=b)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train',type=Path,required=True)
    p.add_argument('--old-train',type=Path,required=True)
    p.add_argument('--prior-receipt',type=Path)
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha):
        raise ValueError('source SHA')
    if args.train.stat().st_size!=GSM_BYTES or args.old_train.stat().st_size!=BYTES:
        raise ValueError('source size')
    if args.receipt.exists():
        raise RuntimeError('receipt already exists; no replay')
    t0=time.monotonic()
    raw=args.train.read_bytes()
    if git_blob(raw)!=GSM_BLOB:
        raise ValueError('GSM8K blob drift')
    excluded,old_manifest=old_groups(args.old_train.read_bytes())
    prior_keys=None
    if args.prior_receipt is not None:
        prior_keys=old_receipt_keys(args.prior_receipt.read_bytes())
    report,receipts=audit(raw,excluded,t0+300,prior_keys=prior_keys)
    report.update(old_group_partitions=old_manifest,source_git_blob=GSM_BLOB)
    payload=canonical(dict(source_sha=args.source_sha,report=report,receipts=receipts))
    with args.receipt.open('xb') as f:
        f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload):
        raise RuntimeError('receipt readback')
    print('UJ04Q '+canonical(dict(event='complete',source_sha=args.source_sha,
        receipt_sha256=digest(payload),receipt_bytes=len(payload),
        wall_seconds=time.monotonic()-t0,**report)).decode(),flush=True)

if __name__=='__main__':
    main()
