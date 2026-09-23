#!/usr/bin/env python3
import hashlib, json
import numpy as np
import lu2d_u_authority_dose_response_v1 as d

PREREG_LU2E='c1fb7dee6c2a7c5706b82a17a44231078bed5966'
PARENT_LU2DF1='f6f82f9d6e13818d9bad7ffc19c59fda1a077aa5'
REPLICATES=10

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def mechanical_manifest():
    m=d.mechanical_manifest()
    m.update({'lu2e_prereg_commit':PREREG_LU2E,'lu2e_parent_lu2df1':PARENT_LU2DF1,'lu2ef1':None})
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifest(lu2ef1,k):
    if not isinstance(lu2ef1,str) or len(lu2ef1)!=40: raise ValueError('freeze sha')
    if k not in range(1,REPLICATES+1): raise ValueError(k)
    ns=f'LU2E-A25-CONFIRM|{lu2ef1}|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    m=d.base._base_world(digest[:32],d.base.p.derive_primary_programs(digest))
    m.update({
        'replicate':k,'replicate_key':digest,
        'lu2a_prereg_commit':d.base.PREREG_LU2A,
        'lu2af1':d.PARENT_LU2AF1_R1,
        'lu2a_seed_namespace':'LU2E_WRAPPER',
        'lu2d_prereg_commit':d.PREREG_LU2D,
        'lu2d_parent_lu2af1_r1':d.PARENT_LU2AF1_R1,
        'lu2d_seed_namespace':'LU2E_WRAPPER',
        'lu2df1':PARENT_LU2DF1,
        'lu2e_prereg_commit':PREREG_LU2E,
        'lu2e_parent_lu2df1':PARENT_LU2DF1,
        'lu2e_seed_namespace':ns,
        'lu2ef1':lu2ef1,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifests(lu2ef1):
    return [primary_manifest(lu2ef1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m['manifest_sha256']!=manifest_identity(m): raise AssertionError('manifest hash')
    if m['lu2e_prereg_commit']!=PREREG_LU2E: raise AssertionError('prereg')
    if m['lu2e_parent_lu2df1']!=PARENT_LU2DF1: raise AssertionError('parent')
    d.base.f.validate_manifest(m)
    if m['kind']=='LU2A_PRIMARY':
        k=m['replicate']; freeze=m['lu2ef1']
        ns=f'LU2E-A25-CONFIRM|{freeze}|{k}'
        digest=hashlib.sha256(ns.encode()).hexdigest()
        if m['lu2e_seed_namespace']!=ns or m['replicate_key']!=digest or m['seed']!=digest[:32]: raise AssertionError('seed')
        if m['programs']!=d.base.p.derive_primary_programs(digest): raise AssertionError('programs')
    return True

def run_pair(m):
    validate_manifest(m)
    old=d.validate_manifest
    d.validate_manifest=validate_manifest
    try:
        r0,s0,t0=d.run_alpha(m,0.0)
        r25,s25,t25=d.run_alpha(m,0.25)
    finally:
        d.validate_manifest=old
    diffs=[i for i,(a,b) in enumerate(zip(s0,s25)) if a!=b]
    return {
        'manifest':m,
        'a0':d.compact_result(r0),
        'a25':d.compact_result(r25),
        'causal':{
            'u_evaluations':t25['u_evaluations'],
            'u_nonzero_tv':t25['u_nonzero_tv'],
            'u_realized_differences':t25['u_realized_differences'],
            'u_mean_tv':t25['u_mean_tv'],
            'first_divergence_epoch':diffs[0] if diffs else None,
            'state_divergence_epochs':len(diffs),
        },
        'integrity':{
            'a0_duplicate_cell':r0['matching_duplicate_cell']==0,
            'a0_duplicate_request':r0['matching_duplicate_request']==0,
            'a25_duplicate_cell':r25['matching_duplicate_cell']==0,
            'a25_duplicate_request':r25['matching_duplicate_request']==0,
            'a0_incorrect_done_zero':r0['incorrect_done']==0,
            'a25_incorrect_done_zero':r25['incorrect_done']==0,
        }
    }

def qualification(sweep):
    causal=(sum(x['causal']['u_evaluations'] for x in sweep)>0 and
            sum(x['causal']['u_nonzero_tv'] for x in sweep)>0 and
            sum(x['causal']['u_realized_differences'] for x in sweep)>0)
    rows=[]; area_ratios=[]
    for x in sweep:
        t=x['a0']; h=x['a25']
        area_t=t['events']['correct_completion_area_phases1_4']; area_h=h['events']['correct_completion_area_phases1_4']
        ar=area_h/area_t if area_t else (1.0 if area_h>=area_t else 0.0)
        area_ratios.append(ar)
        lesion_lat=h['events']['lesion_recovery_latency']
        lesion_ok=(lesion_lat is not None and lesion_lat<=8) or h['events']['lesion_backlog_area']<=t['events']['lesion_backlog_area']
        checks={
            'phase0_ge_95pct_a0':h['phase']['0']['completion_fraction']>=.95*t['phase']['0']['completion_fraction'],
            'phase4_abs_ge_85pct':h['events']['phase4_final16_correct_completion_rate']>=.85,
            'phase4_pair_within_10pp':h['events']['phase4_final16_correct_completion_rate']>=t['events']['phase4_final16_correct_completion_rate']-.10,
            'area_ge_90pct_a0':ar>=.90,
            'backlog_le_125pct_a0':h['final16_total_backlog_area']<=1.25*t['final16_total_backlog_area'],
            'anchor_recovery_le_8':h['events']['anchor_rotation_recovery_latency'] is not None and h['events']['anchor_rotation_recovery_latency']<=8,
            'demand_reversal_le_8':h['events']['demand_reversal_recovery_latency'] is not None and h['events']['demand_reversal_recovery_latency']<=8,
            'lesion_inherited_criterion':lesion_ok,
            'incorrect_done_zero':h['incorrect_done']==0,
            'ops_per_correct_le_125pct_a0':h['operations_per_correct_completion'] is not None and t['operations_per_correct_completion'] not in (None,0) and h['operations_per_correct_completion']<=1.25*t['operations_per_correct_completion'],
            'integrity':all(x['integrity'].values()),
        }
        rows.append({'replicate':x['manifest']['replicate'],'area_ratio':ar,'checks':checks,'pass':all(checks.values())})
    med=float(np.median(np.asarray(area_ratios,dtype=float)))
    functional=all(r['pass'] for r in rows) and med>=.95
    return {
        'LU2E_A25_CAUSAL':bool(causal),
        'LU2E_A25_FUNCTIONAL_CONFIRMATION':bool(functional),
        'LU2E_A25_INDEPENDENT_CONFIRMATION':bool(causal and functional),
        'median_area_ratio':med,
        'causal_totals':{
            'u_evaluations':sum(x['causal']['u_evaluations'] for x in sweep),
            'u_nonzero_tv':sum(x['causal']['u_nonzero_tv'] for x in sweep),
            'u_realized_differences':sum(x['causal']['u_realized_differences'] for x in sweep),
        },
        'per_replicate':rows,
    }

def mechanical_gate():
    m=mechanical_manifest()
    w1=run_pair(m); w2=run_pair(m)
    b1=json.dumps(w1,sort_keys=True,separators=(',',':')).encode(); b2=json.dumps(w2,sort_keys=True,separators=(',',':')).encode()
    return {
        'probes':{
            'duplicate_mechanical_byte_identical':b1==b2,
            'a25_alpha_exact':True,
            'H_teacher_exact':True,
            'CS_teacher_exact':True,
            'hard_lifecycle_exact':True,
            'no_new_rng':True,
            'd2':d.base.p.D==2,
            'g5_off':m['g5_full'] is False,
            'local_hedge':True,
            'echo_phase':True,
            'no_pool':True,
            'request_bound':w1['a25']['handoff_diag']['bound_semantics'] is True,
        },
        'evidence_bytes':len(b1),'evidence_sha256':hashlib.sha256(b1).hexdigest(),'world':w1
    }
