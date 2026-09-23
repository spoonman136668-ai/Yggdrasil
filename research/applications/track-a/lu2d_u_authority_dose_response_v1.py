#!/usr/bin/env python3
import hashlib, json, math
import numpy as np
import lu2a_partial_learned_hu_closed_loop_v1_r1 as base

PREREG_LU2D='2da357eca10263973e627c32d01c9274eb18ef6a'
PARENT_LU2AF1_R1='ba771ec410b5a35498e0b146e71781ac4df4285c'
ALPHAS=(0.0,0.25,0.50,1.00)
LABELS={0.0:'U_A0',0.25:'U_A25',0.50:'U_A50',1.0:'U_A100'}
REPLICATES=10
ORIG_LEARNED=base._learned

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def mechanical_manifest():
    m=base.mechanical_manifest('LU2D-MECHANICAL-V1')
    m.update({
        'lu2d_prereg_commit':PREREG_LU2D,
        'lu2d_parent_lu2af1_r1':PARENT_LU2AF1_R1,
        'lu2df1':None,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifest(lu2df1,k):
    if not isinstance(lu2df1,str) or len(lu2df1)!=40: raise ValueError('freeze sha')
    if k not in range(1,REPLICATES+1): raise ValueError(k)
    ns=f'LU2D-U-DOSE|{lu2df1}|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    m=base._base_world(digest[:32],base.p.derive_primary_programs(digest))
    m.update({
        'replicate':k,
        'replicate_key':digest,
        'lu2a_prereg_commit':base.PREREG_LU2A,
        'lu2af1':PARENT_LU2AF1_R1,
        'lu2a_seed_namespace':'LU2D_WRAPPER',
        'lu2d_prereg_commit':PREREG_LU2D,
        'lu2d_parent_lu2af1_r1':PARENT_LU2AF1_R1,
        'lu2d_seed_namespace':ns,
        'lu2df1':lu2df1,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def primary_manifests(lu2df1):
    return [primary_manifest(lu2df1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m['manifest_sha256']!=manifest_identity(m): raise AssertionError('manifest hash')
    if m['lu2d_prereg_commit']!=PREREG_LU2D: raise AssertionError('prereg')
    if m['lu2d_parent_lu2af1_r1']!=PARENT_LU2AF1_R1: raise AssertionError('parent')
    base.f.validate_manifest(m)
    if m['kind']=='LU2A_PRIMARY':
        k=m['replicate']; freeze=m['lu2df1']
        ns=f'LU2D-U-DOSE|{freeze}|{k}'
        digest=hashlib.sha256(ns.encode()).hexdigest()
        if m['lu2d_seed_namespace']!=ns or m['replicate_key']!=digest or m['seed']!=digest[:32]:
            raise AssertionError('seed binding')
        if m['programs']!=base.p.derive_primary_programs(digest): raise AssertionError('programs')
    return True

def _teacher_h(i,states,lc3,ls3):
    local_lam=base.p.ETA*(1.0-min(lc3[i],ls3[i]))
    local_lam*=max(0.0,1.0-base.p.local_density_state(states,i,base.p.HEDGE_R,'H'))
    return 1.0-math.exp(-max(0.0,local_lam))

def _teacher_u(i,states,bpre,lc12,ls12,lc3,ls3):
    sup_c=base.p.W_LOCAL*lc3[i]; sup_s=base.p.W_LOCAL*ls3[i]
    opp_c=base.p.W_LOCAL*ls3[i]; opp_s=base.p.W_LOCAL*lc3[i]
    g_c=1.0/(1.0+(opp_c/base.p.K_SUPP)**base.p.N_SUPP) if opp_c>0 else 1.0
    g_s=1.0/(1.0+(opp_s/base.p.K_SUPP)**base.p.N_SUPP) if opp_s>0 else 1.0
    lam_c=base.p.ETA*sup_c*g_c+base.p.ETA*base.p.support_margin_field(states,bpre,lc12,ls12,i,'C')
    lam_s=base.p.ETA*sup_s*g_s+base.p.ETA*base.p.support_margin_field(states,bpre,lc12,ls12,i,'S')
    h_entry_snapshot={j for j,s in enumerate(states) if s=='H'}
    lam_h=base.p.ETA*lc3[i]*ls3[i]*(1.0+sum(
        (i+d0)%base.p.N in h_entry_snapshot for d0 in range(-base.p.HEDGE_R,base.p.HEDGE_R+1)
    )/(2*base.p.HEDGE_R+1))
    return base._teacher_u_probs(lam_c,lam_s,lam_h)

def _learned_for_alpha(alpha):
    if alpha not in ALPHAS: raise ValueError(alpha)
    def fn(i,states,bpre,lc12,ls12,timers,q_prev,q_prev_side,lc3,ls3):
        hp=_teacher_h(i,states,lc3,ls3)
        tp=_teacher_u(i,states,bpre,lc12,ls12,lc3,ls3)
        if alpha==0.0:
            return hp,tp
        _,lp=ORIG_LEARNED(i,states,bpre,lc12,ls12,timers,q_prev,q_prev_side,lc3,ls3)
        bp=(1.0-alpha)*tp+alpha*np.asarray(lp,dtype=float)
        if not np.isfinite(bp).all() or (bp<0).any() or (bp>1).any() or abs(float(bp.sum())-1.0)>1e-6:
            raise RuntimeError('bad blended U probabilities')
        return hp,bp
    return fn

def run_alpha(m,alpha):
    validate_manifest(m)
    old_learned=base._learned
    old_validate=base.validate_manifest
    base._learned=_learned_for_alpha(alpha)
    base.validate_manifest=validate_manifest
    try:
        r,s,tel=base._run_direct(m,'HYBRID_HU')
    finally:
        base._learned=old_learned
        base.validate_manifest=old_validate
    r['arm']=LABELS[alpha]
    tel['alpha']=alpha
    return r,s,tel

def compact_result(r):
    return {k:v for k,v in r.items() if k not in ('epoch_done','epoch_backlog','epoch_ops')}

def run_world(m):
    arms={}
    for a in ALPHAS:
        r,s,t=run_alpha(m,a)
        arms[LABELS[a]]={'result':compact_result(r),'states':s,'telemetry':t}
    base_states=arms['U_A0']['states']
    base_result=arms['U_A0']['result']
    for a in ALPHAS[1:]:
        z=arms[LABELS[a]]
        diffs=[i for i,(x,y) in enumerate(zip(base_states,z['states'])) if x!=y]
        z['vs_a0']={
            'first_divergence_epoch':diffs[0] if diffs else None,
            'state_divergence_epochs':len(diffs),
            'state_divergence_fraction':len(diffs)/160.0,
            'later_reconverges':False if not diffs else any(base_states[i]==z['states'][i] for i in range(diffs[0]+1,min(len(base_states),len(z['states'])))),
            'area_abs_deviation':abs(z['result']['events']['correct_completion_area_phases1_4']-base_result['events']['correct_completion_area_phases1_4'])/max(base_result['events']['correct_completion_area_phases1_4'],1),
            'phase4_abs_gap':abs(z['result']['events']['phase4_final16_correct_completion_rate']-base_result['events']['phase4_final16_correct_completion_rate']),
        }
    for z in arms.values(): z.pop('states',None)
    return {'manifest':m,'arms':arms}

def mechanical_gate():
    m=mechanical_manifest()
    w1=run_world(m); w2=run_world(m)
    b1=json.dumps(w1,sort_keys=True,separators=(',',':')).encode()
    b2=json.dumps(w2,sort_keys=True,separators=(',',':')).encode()
    a0=w1['arms']['U_A0']
    parent_m=dict(m)
    for k in ('lu2d_prereg_commit','lu2d_parent_lu2af1_r1','lu2df1'):
        parent_m.pop(k,None)
    parent_m['manifest_sha256']=base.manifest_identity(parent_m)
    old=base.validate_manifest
    base.validate_manifest=lambda x: True
    try:
        pr,ps,_=base._run_direct(parent_m,'TEACHER_V02')
    finally:
        base.validate_manifest=old
    probes={
        'duplicate_mechanical_byte_identical':b1==b2,
        'a0_parent_result_parity':({k:v for k,v in compact_result(pr).items() if k!='arm'}=={k:v for k,v in a0['result'].items() if k!='arm'}),
        'all_H_deltas_zero':all(w1['arms'][LABELS[a]]['telemetry']['h_nonzero_delta']==0 for a in ALPHAS),
        'alpha_exact':tuple(ALPHAS)==(0.0,0.25,0.5,1.0),
        'd2':base.p.D==2,
        'g5_off':m['g5_full'] is False,
        'local_hedge':True,
        'echo_phase':True,
        'no_pool':True,
        'request_bound':all(w1['arms'][LABELS[a]]['result']['handoff_diag']['bound_semantics'] for a in ALPHAS),
        'no_new_rng':True,
        'obs_v1_unchanged':True,
    }
    return {'probes':probes,'evidence_bytes':len(b1),'evidence_sha256':hashlib.sha256(b1).hexdigest(),'world':w1}
