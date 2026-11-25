"""UJ04P P0: strict source-only operation-chain feasibility, no fitting."""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import re
import time

from uj03a_pilot import SHA256, BYTES, select, group, digest, canonical, check_deadline
from symbolic_control import arithmetic, Unsupported

SKIP, FIT, DIAG = 2304, 3072, 1024
WALL_SECONDS = 300
OPS = ('+', '-', '*', '/')
NUM = r'[+-]?[0-9]+(?:\.[0-9]+)?'
EQ = re.compile(r'[ \t]*('+NUM+r')[ \t]*([+\-*/])[ \t]*('+NUM+r')[ \t]*=[ \t]*('+NUM+r')[ \t]*',re.ASCII)
FRAGMENT = re.compile(r'[^;\r\n]+')

def bounded(value):
    return max(value.numerator.bit_length(),value.denominator.bit_length())<=64

def independent_number(text):
    # Normalize only decimal spelling for the existing AST evaluator.
    sign='-' if text.startswith('-') else ''
    a,sep,b=text.lstrip('+-').partition('.')
    return sign+(a.lstrip('0') or '0')+(sep+b if sep else '')

def parse_fragment(text):
    m=EQ.fullmatch(text)
    if not m:
        return None,'unsupported'
    a,op,b,c=m.groups()
    if max(map(len,(a,b,c)))>128:
        return None,'numeric_bound'
    x,y,z=map(Fraction,(a,b,c))
    if not all(map(bounded,(x,y,z))):
        return None,'numeric_bound'
    if op=='/' and not y:
        return None,'zero_divisor'
    expected={'+':lambda:x+y,'-':lambda:x-y,'*':lambda:x*y,'/':lambda:x/y}[op]()
    if expected!=z:
        return None,'conflicting_arithmetic'
    if not bounded(expected):
        return None,'numeric_bound'
    try:
        lhs=arithmetic(('('+independent_number(a)+')'+op+'('+independent_number(b)+')').encode('ascii'))
        rhs=arithmetic(independent_number(c).encode('ascii'))
    except Unsupported:
        return None,'independent_unsupported'
    if lhs!=expected or rhs!=z:
        raise RuntimeError('independent arithmetic disagreement')
    return (x,op,y,z),None

def rational(v):
    return [v.numerator,v.denominator]

def chain_key(steps):
    return tuple((str(x),op,str(y),str(z)) for x,op,y,z in steps)

def extract(rationale):
    """Return one earliest maximal valid chain, or a reason; character spans."""
    counts=Counter()
    if type(rationale) is not str or not rationale.strip():
        return None,'missing_rationale',counts
    if len(rationale)>65536:
        return None,'rationale_bound',counts
    fragments=[]
    for m in FRAGMENT.finditer(rationale):
        if not m.group().strip():
            fragments.append((None,m.span()))
            continue
        step,reason=parse_fragment(m.group())
        if reason:
            counts[reason]+=1
        else:
            counts['verified_equation']+=1
        fragments.append((step,m.span()))
    # Never admit a row containing an explicitly contradictory or invalid equation.
    for reason in ('conflicting_arithmetic','zero_divisor','numeric_bound','independent_unsupported'):
        if counts[reason]:
            return None,reason,counts
    verified=[(i,s) for i,(s,_) in enumerate(fragments) if s is not None]
    # Reject ambiguous provenance anywhere in the row: more than one prior
    # result can explain a later operand, or a result fans out to later steps.
    successors=Counter()
    for j,s in verified:
        x,_,y,_=s
        links=[(i,side) for i,t in verified if i<j
               for side,value in enumerate((x,y)) if t[3]==value]
        if len(links)>1:
            return None,'ambiguous_linkage',counts
        if links:
            successors[links[0][0]]+=1
    if any(v>1 for v in successors.values()):
        return None,'branching_linkage',counts
    runs=[]
    current=[]
    for i,(step,span) in enumerate(fragments):
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
            steps=[s for s,_ in run]
            # Repeated result values make later identity attribution ambiguous.
            if len({s[3] for s in steps})!=len(steps):
                return None,'repeated_result',counts
            return run,None,counts
        if len(run)>4:
            counts['chain_too_long']+=1
    return None,'no_eligible_chain',counts

def pools(raw,expected=SHA256,skip=SKIP,fit=FIT,diag=DIAG):
    prior,tail,_=select(raw,expected,skip+fit,diag)
    parts=(prior[:skip],prior[skip:],tail)
    groups=[set(group(r[2].decode()) for r in part) for part in parts]
    if any(a&b for i,a in enumerate(groups) for b in groups[i+1:]):
        raise RuntimeError('group overlap')
    return parts,[dict(count=len(part),group_sha256=digest(canonical(sorted(g))),
                       ids_sha256=digest(canonical([r[0] for r in part])))
                  for g,part in zip(groups,parts)]

def scan_pool(rows,lines,expected,deadline):
    receipts=[]
    keys=set()
    ops=Counter()
    lengths=Counter()
    pairs=Counter()
    tuples=set()
    rejects=Counter()
    fragments=Counter()
    for row in rows:
        check_deadline(deadline)
        prefix,line=row[0].rsplit(':',1)
        if prefix!=expected:
            raise RuntimeError('row provenance')
        obj=json.loads(lines[int(line)])
        if obj['question'].encode()!=row[2]:
            raise RuntimeError('row question mismatch')
        rationale=obj.get('rationale')
        run,reason,counts=extract(rationale)
        fragments.update(counts)
        if reason:
            rejects[reason]+=1
            continue
        steps=[s for s,_ in run]
        key=chain_key(steps)
        keys.add(key)
        ops.update(s[1] for s in steps)
        lengths[len(steps)]+=1
        pairs.update(set(a[1]+b[1] for a,b in zip(steps,steps[1:])))
        tuples.update((str(x),op,str(y),str(z)) for x,op,y,z in steps)
        receipts.append(dict(row_id=row[0],group=group(obj['question']),
            rationale_sha256=digest(rationale.encode('utf-8')),
            steps=[dict(left=rational(x),op=op,right=rational(y),result=rational(z),
                        span=list(span)) for (x,op,y,z),span in run]))
    if len(receipts)+sum(rejects.values())!=len(rows):
        raise RuntimeError('receipt accounting')
    summary=dict(rows=len(rows),accepted_chains=len(receipts),rejected_rows=dict(rejects),
                 fragment_counts=dict(fragments),op_transitions=dict(ops),
                 chain_lengths=dict(lengths),ordered_pair_chain_counts=dict(pairs),
                 unique_ordered_pairs=len(pairs),unique_operand_result_tuples=len(tuples),
                 unique_full_chains=len(keys),receipt_sha256=digest(canonical(receipts)))
    return receipts,keys,summary

def decision(fit,diag,overlap):
    eligible=[op for op,n in fit['op_transitions'].items() if n>=64]
    pairs=[pair for pair,n in diag['ordered_pair_chain_counts'].items()
           if n>=16 and all(fit['op_transitions'].get(op,0)>0 for op in pair)]
    criteria=dict(fit_chains=fit['accepted_chains']>=256,
                  diagnostic_chains=diag['accepted_chains']>=64,
                  fit_operation_coverage=len(eligible)>=2,
                  diagnostic_pair_coverage=len(pairs)>=2,zero_full_chain_overlap=overlap==0)
    return dict(criteria=criteria,eligible_fit_operations=sorted(eligible),
                eligible_diagnostic_pairs=sorted(pairs),source_feasible=all(criteria.values()))

def audit(raw,expected=SHA256,skip=SKIP,fit=FIT,diag=DIAG,deadline=None):
    if deadline is None: deadline=time.monotonic()+WALL_SECONDS
    parts,manifest=pools(raw,expected,skip,fit,diag)
    check_deadline(deadline)
    lines=raw.splitlines()
    a,ak,am=scan_pool(parts[1],lines,expected,deadline)
    b,bk,bm=scan_pool(parts[2],lines,expected,deadline)
    overlap=len(ak&bk)
    report=dict(source_sha256=expected,group_partitions=manifest,fit=am,diagnostic=bm,
                exact_full_chain_overlap=overlap,group_overlap=0,**decision(am,bm,overlap),
                model_training_steps=0,protected_evaluation_accessed=False,scientific_gain_verified=False)
    check_deadline(deadline)
    return report,dict(fit=a,diagnostic=b)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train',type=Path,required=True)
    p.add_argument('--source-sha',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha) or args.train.stat().st_size!=BYTES:
        raise ValueError('source custody')
    if args.receipt.exists():
        raise RuntimeError('receipt already exists; no replay')
    t0=time.monotonic()
    report,receipts=audit(args.train.read_bytes(),deadline=t0+WALL_SECONDS)
    payload=canonical(dict(source_sha=args.source_sha,report=report,receipts=receipts))
    with args.receipt.open('xb') as f:
        f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload):
        raise RuntimeError('receipt readback')
    print('UJ04P '+canonical(dict(event='complete',source_sha=args.source_sha,
        receipt_sha256=digest(payload),receipt_bytes=len(payload),wall_seconds=time.monotonic()-t0,
        **report)).decode(),flush=True)

if __name__=='__main__':
    main()
