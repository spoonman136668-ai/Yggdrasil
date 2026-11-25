"""UJ04R R0: unused GSM8K question groups, deterministic chain-cluster split."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import re
import time

from uj03a_pilot import BYTES, canonical, digest, check_deadline
from uj04p_source_audit import chain_key, decision
from uj04q_source_audit import (GSM_BYTES,GSM_BLOB,git_blob,old_groups,
                                annotations,select_gsm,scan)

GSM_SHA='17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
Q_GROUP_HASHES=('bff15ce07065ce76fee6ad078af975d6edee264709efb186678b9fe03dbc4924',
                'be9f12a8d81a68c99fca3adc87b9fd7f28d43fa1944678bf3b03aa59864c522f')
Q_ID_HASHES=('f070c558f0a59b54a9fd8086a2cc44bea79349b2b56c37cfd34adb7f5c21ec04',
             '55757435a1bf2d78392b3f6ee809293340644ede416f69dc79e5b15942891bca')
Q_RECEIPT_SHA='1653348f0102ae7f396e49006a5ad6d46c1ab5282d6a6c278dec018bdd8252ba'

def unused(raw,excluded):
    old,manifest,counts=select_gsm(raw,excluded,3072,1024)
    if tuple(m['group_sha256'] for m in manifest)!=Q_GROUP_HASHES:
        raise RuntimeError('Q0 group custody mismatch')
    if tuple(m['ids_sha256'] for m in manifest)!=Q_ID_HASHES:
        raise RuntimeError('Q0 row custody mismatch')
    if counts['eligible_groups']!=7472:
        raise RuntimeError('eligible group count drift')
    parts,_,_=select_gsm(raw,excluded,4096,3376)
    if tuple(r[0] for r in parts[0])!=tuple(r[0] for part in old for r in part):
        raise RuntimeError('prior partition drift')
    seen={r[1] for r in parts[0]}
    fresh={r[1] for r in parts[1]}
    if len(fresh)!=3376 or seen&fresh or fresh&excluded:
        raise RuntimeError('unused source isolation')
    return parts[1],manifest,counts

def bucket(key,group):
    if key is None:
        raw=b'UJ04R:20261124:reject:'+group.encode('ascii')
    else:
        raw=b'UJ04R:20261124:chain:'+canonical(key)
    return int(digest(raw),16)%3==0

def split(rows,deadline):
    parts=([],[])
    assignments={}
    for row in rows:
        check_deadline(deadline)
        if row[1] in assignments:
            raise RuntimeError('duplicate question group')
        run,reason,_=annotations(row[2])
        key=None if reason else chain_key([s for s,_ in run])
        i=int(bucket(key,row[1]))
        assignments[row[1]]=(i,key)
        parts[i].append(row)
    return parts,assignments

def receipt_key(row):
    return chain_key([(Fraction(*s['left']),s['op'],Fraction(*s['right']),
                       Fraction(*s['result'])) for s in row['steps']])

def prior_keys(raw):
    if digest(raw)!=Q_RECEIPT_SHA:
        raise ValueError('Q0 receipt drift')
    obj=json.loads(raw)
    return {receipt_key(r) for part in ('fit','diagnostic') for r in obj['receipts'][part]}

def audit(rows,deadline,previous=None):
    parts,assignment=split(rows,deadline)
    a,ak,am=scan(parts[0],deadline)
    b,bk,bm=scan(parts[1],deadline)
    gs=[{r[1] for r in part} for part in parts]
    if gs[0]&gs[1] or len(gs[0]|gs[1])!=len(rows):
        raise RuntimeError('group partition mismatch')
    for i,receipts in enumerate((a,b)):
        expected={g for g,(j,k) in assignment.items() if j==i and k is not None}
        if {r['group'] for r in receipts}!=expected:
            raise RuntimeError('accepted membership drift')
        for r in receipts:
            if assignment[r['group']]!=(i,receipt_key(r)):
                raise RuntimeError('chain assignment drift')
    overlap=len(ak&bk)
    if overlap:
        raise RuntimeError('chain partition invariant')
    manifest=[dict(count=len(part),group_sha256=digest(canonical(sorted(g))),
                   ids_sha256=digest(canonical([r[0] for r in part])))
              for part,g in zip(parts,gs)]
    report=dict(group_partitions=manifest,fit=am,diagnostic=bm,group_overlap=0,
        exact_full_chain_overlap=overlap,prior_q0_chain_overlap_verified=previous is not None,
        prior_q0_chain_overlap=None if previous is None else len((ak|bk)&previous),
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
    if git_blob(raw)!=GSM_BLOB or digest(raw)!=GSM_SHA:
        raise ValueError('GSM source drift')
    excluded,old_manifest=old_groups(args.old_train.read_bytes())
    rows,q_manifest,counts=unused(raw,excluded)
    previous=None if args.prior_receipt is None else prior_keys(args.prior_receipt.read_bytes())
    report,receipts=audit(rows,t0+300,previous)
    report.update(source_sha256=GSM_SHA,source_git_blob=GSM_BLOB,source_counts=counts,
                  old_group_partitions=old_manifest,excluded_q0_partitions=q_manifest,
                  unused_groups=len(rows))
    payload=canonical(dict(source_sha=args.source_sha,report=report,receipts=receipts))
    with args.receipt.open('xb') as f:
        f.write(payload)
    if digest(args.receipt.read_bytes())!=digest(payload):
        raise RuntimeError('receipt readback')
    print('UJ04R '+canonical(dict(event='complete',source_sha=args.source_sha,
        receipt_sha256=digest(payload),receipt_bytes=len(payload),
        wall_seconds=time.monotonic()-t0,**report)).decode(),flush=True)

if __name__=='__main__':
    main()
