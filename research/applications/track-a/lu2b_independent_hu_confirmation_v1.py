#!/usr/bin/env python3
import hashlib, json
import lu2a_partial_learned_hu_closed_loop_v1_r1 as base

PREREG_LU2B='2a8430c0b88be19adb4bf5c18c49d56abe1b0ab6'
PARENT_LU2AF1_R1='ba771ec410b5a35498e0b146e71781ac4df4285c'
REPLICATES=5

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def confirmation_manifest(k):
    if k not in range(1,REPLICATES+1):
        raise ValueError(k)
    ns=f'LU2B-CONFIRM|LU2AF1-R1|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    m=base._base_world(digest[:32],base.p.derive_primary_programs(digest))
    m.update({
        'replicate':k,
        'replicate_key':digest,
        'lu2a_prereg_commit':base.PREREG_LU2A,
        'lu2af1':PARENT_LU2AF1_R1,
        'lu2a_seed_namespace':'CONFIRMATION_WRAPPER',
        'lu2b_prereg_commit':PREREG_LU2B,
        'lu2b_seed_namespace':ns,
        'lu2b_parent_lu2af1_r1':PARENT_LU2AF1_R1,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def confirmation_manifests():
    return [confirmation_manifest(k) for k in range(1,REPLICATES+1)]

def validate_confirmation_manifest(m):
    if m['manifest_sha256']!=manifest_identity(m):
        raise AssertionError('manifest hash')
    if m['lu2b_prereg_commit']!=PREREG_LU2B:
        raise AssertionError('lu2b prereg')
    if m['lu2b_parent_lu2af1_r1']!=PARENT_LU2AF1_R1:
        raise AssertionError('parent freeze')
    base.f.validate_manifest(m)
    k=m['replicate']
    ns=f'LU2B-CONFIRM|LU2AF1-R1|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    if m['lu2b_seed_namespace']!=ns:
        raise AssertionError('namespace')
    if m['replicate_key']!=digest or m['seed']!=digest[:32]:
        raise AssertionError('seed binding')
    if m['programs']!=base.p.derive_primary_programs(digest):
        raise AssertionError('programs')
    return True

def run_pair(m):
    validate_confirmation_manifest(m)
    old=base.validate_manifest
    base.validate_manifest=validate_confirmation_manifest
    try:
        return base.run_pair(m)
    finally:
        base.validate_manifest=old

def run_sweep(manifests):
    if len(manifests)!=REPLICATES:
        raise AssertionError('need five')
    return [run_pair(m) for m in manifests]

def qualification(sweep):
    return base.qualification(sweep)
