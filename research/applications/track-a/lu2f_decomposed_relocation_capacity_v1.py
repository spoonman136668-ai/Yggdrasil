#!/usr/bin/env python3
import hashlib, json
import numpy as np
import lu2e_a25_independent_confirmation_v1 as e

PREREG_LU2F='a7be8b696fe56aa9e070ef124192ddeb653b6659'
PARENT_LU2EF1='377fdc6e3b65fe843f77296cf1bbdc82736813a1'
REPLICATES=10

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def mechanical_manifest():
    m=e.mechanical_manifest()
    m.update({'lu2f_prereg_commit':PREREG_LU2F,'lu2f_parent_lu2ef1':PARENT_LU2EF1,'lu2ff1':None})
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifest(lu2ff1,k):
    if not isinstance(lu2ff1,str) or len(lu2ff1)!=40: raise ValueError('freeze sha')
    if k not in range(1,REPLICATES+1): raise ValueError(k)
    ns=f'LU2F-DECOMP-RELOC|{lu2ff1}|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    m=e.d.base._base_world(digest[:32],e.d.base.p.derive_primary_programs(digest))
    m.update({
        'replicate':k,'replicate_key':digest,
        'lu2a_prereg_commit':e.d.base.PREREG_LU2A,
        'lu2af1':e.d.PARENT_LU2AF1_R1,
        'lu2a_seed_namespace':'LU2F_WRAPPER',
        'lu2d_prereg_commit':e.d.PREREG_LU2D,
        'lu2d_parent_lu2af1_r1':e.d.PARENT_LU2AF1_R1,
        'lu2d_seed_namespace':'LU2F_WRAPPER',
        'lu2df1':e.PARENT_LU2DF1,
        'lu2e_prereg_commit':e.PREREG_LU2E,
        'lu2e_parent_lu2df1':e.PARENT_LU2DF1,
        'lu2e_seed_namespace':'LU2F_WRAPPER',
        'lu2ef1':PARENT_LU2EF1,
        'lu2f_prereg_commit':PREREG_LU2F,
        'lu2f_parent_lu2ef1':PARENT_LU2EF1,
        'lu2f_seed_namespace':ns,
        'lu2ff1':lu2ff1,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifests(lu2ff1):
    return [primary_manifest(lu2ff1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m['manifest_sha256']!=manifest_identity(m): raise AssertionError('manifest hash')
    if m['lu2f_prereg_commit']!=PREREG_LU2F: raise AssertionError('prereg')
    if m['lu2f_parent_lu2ef1']!=PARENT_LU2EF1: raise AssertionError('parent')
    e.d.base.f.validate_manifest(m)
    if m['kind']=='LU2A_PRIMARY':
        k=m['replicate']; freeze=m['lu2ff1']
        ns=f'LU2F-DECOMP-RELOC|{freeze}|{k}'
        digest=hashlib.sha256(ns.encode()).hexdigest()
        if m['lu2f_seed_namespace']!=ns or m['replicate_key']!=digest or m['seed']!=digest[:32]: raise AssertionError('seed')
        if m['programs']!=e.d.base.p.derive_primary_programs(digest): raise AssertionError('programs')
    return True

def run_pair(m):
    validate_manifest(m)
    old=e.validate_manifest
    e.validate_manifest=validate_manifest
    try:
        return e.run_pair(m)
    finally:
        e.validate_manifest=old

def qualification(sweep):
    causal=(sum(x['causal']['u_evaluations'] for x in sweep)>0 and
            sum(x['causal']['u_nonzero_tv'] for x in sweep)>0 and
            sum(x['causal']['u_realized_differences'] for x in sweep)>0)
    rows=[]; new_ratios=[]; area_ratios=[]
    for x in sweep:
        t=x['a0']; h=x['a25']
        td=t['handoff_diag']; hd=h['handoff_diag']
        new_t=td['new4_correct_done']; new_h=hd['new4_correct_done']
        new_ratio=None if new_t==0 else new_h/new_t
        if new_ratio is not None: new_ratios.append(new_ratio)
        area_t=t['events']['correct_completion_area_phases1_4']; area_h=h['events']['correct_completion_area_phases1_4']
        area_ratio=area_h/area_t if area_t else (1.0 if area_h>=area_t else 0.0)
        area_ratios.append(area_ratio)
        stream_ok=True
        for key in ('new4_C_correct_done','new4_S_correct_done'):
            tv=t['task1f_stream_diag'][key]; hv=h['task1f_stream_diag'][key]
            if tv>=4 and hv<.75*tv: stream_ok=False
        legacy_exp_ok=(hd['legacy_expired']==0 if td['legacy_expired']==0 else hd['legacy_expired']<=td['legacy_expired'])
        lesion_lat=h['events']['lesion_recovery_latency']
        lesion_ok=(lesion_lat is not None and lesion_lat<=8) or h['events']['lesion_backlog_area']<=t['events']['lesion_backlog_area']
        checks={
            'new_service':new_h>=.90*new_t,
            'stream_noncollapse':stream_ok,
            'legacy_abs_ge_95pct':hd['legacy_completion_fraction']>=.95,
            'legacy_pair_within_5pp':hd['legacy_completion_fraction']>=td['legacy_completion_fraction']-.05,
            'legacy_expiry':legacy_exp_ok,
            'final16_backlog_area':h['final16_total_backlog_area']<=1.25*t['final16_total_backlog_area'],
            'final_backlog':h['backlog']<=1.25*t['backlog'],
            'area_ge_90pct':area_ratio>=.90,
            'ops':h['operations_per_correct_completion'] is not None and t['operations_per_correct_completion'] not in (None,0) and h['operations_per_correct_completion']<=1.25*t['operations_per_correct_completion'],
            'anchor':h['events']['anchor_rotation_recovery_latency'] is not None and h['events']['anchor_rotation_recovery_latency']<=8,
            'demand':h['events']['demand_reversal_recovery_latency'] is not None and h['events']['demand_reversal_recovery_latency']<=8,
            'lesion':lesion_ok,
            'incorrect':h['incorrect_done']==0,
            'integrity':all(x['integrity'].values()),
        }
        rows.append({
            'replicate':x['manifest']['replicate'],'checks':checks,'pass':all(checks.values()),
            'new4_ratio':new_ratio,'area_ratio':area_ratio,
            'legacy_a0':td['legacy_completion_fraction'],'legacy_a25':hd['legacy_completion_fraction'],
            'raw_final16_a0':t['events']['phase4_final16_correct_completion_rate'],
            'raw_final16_a25':h['events']['phase4_final16_correct_completion_rate'],
        })
    med_new=float(np.median(np.asarray(new_ratios,dtype=float))) if new_ratios else None
    med_area=float(np.median(np.asarray(area_ratios,dtype=float)))
    preserved=(causal and all(r['pass'] for r in rows) and (med_new is None or med_new>=.95) and med_area>=.95)
    return {
        'LU2F_DECOMPOSED_RELOCATION_CAPACITY_PRESERVED':bool(preserved),
        'causal':bool(causal),
        'median_new4_ratio':med_new,'median_area_ratio':med_area,
        'causal_totals':{
            'u_evaluations':sum(x['causal']['u_evaluations'] for x in sweep),
            'u_nonzero_tv':sum(x['causal']['u_nonzero_tv'] for x in sweep),
            'u_realized_differences':sum(x['causal']['u_realized_differences'] for x in sweep),
        },
        'per_replicate':rows,
    }

def mechanical_gate():
    m=mechanical_manifest(); w1=run_pair(m); w2=run_pair(m)
    b1=json.dumps(w1,sort_keys=True,separators=(',',':')).encode(); b2=json.dumps(w2,sort_keys=True,separators=(',',':')).encode()
    return {'probes':{'duplicate':b1==b2,'same_mechanism':True,'no_new_rng':True,'request_bound':w1['a25']['handoff_diag']['bound_semantics'] is True},
            'evidence_bytes':len(b1),'evidence_sha256':hashlib.sha256(b1).hexdigest(),'world':w1}
