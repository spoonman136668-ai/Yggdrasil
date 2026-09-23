#!/usr/bin/env python3
import hashlib, json, math, sys
import numpy as np
import lu2a_partial_learned_hu_closed_loop_v1_r1 as base

PREREG_LU2C='44b2cf29148f3d2f3ef19815ef23d8c1ed61bb34'
PARENT_LU2AF1_R1='ba771ec410b5a35498e0b146e71781ac4df4285c'
REPLICATES=10

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def diagnostic_manifest(k):
    if k not in range(1,REPLICATES+1):
        raise ValueError(k)
    ns=f'LU2C-U-SHIFT|LU2AF1-R1|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    m=base._base_world(digest[:32],base.p.derive_primary_programs(digest))
    m.update({
        'replicate':k,
        'replicate_key':digest,
        'lu2a_prereg_commit':base.PREREG_LU2A,
        'lu2af1':PARENT_LU2AF1_R1,
        'lu2a_seed_namespace':'DIAGNOSTIC_WRAPPER',
        'lu2c_prereg_commit':PREREG_LU2C,
        'lu2c_seed_namespace':ns,
        'lu2c_parent_lu2af1_r1':PARENT_LU2AF1_R1,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m

def diagnostic_manifests():
    return [diagnostic_manifest(k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m['manifest_sha256']!=manifest_identity(m): raise AssertionError('manifest hash')
    if m['lu2c_prereg_commit']!=PREREG_LU2C: raise AssertionError('prereg')
    if m['lu2c_parent_lu2af1_r1']!=PARENT_LU2AF1_R1: raise AssertionError('parent')
    base.f.validate_manifest(m)
    k=m['replicate']
    ns=f'LU2C-U-SHIFT|LU2AF1-R1|{k}'
    digest=hashlib.sha256(ns.encode()).hexdigest()
    if m['lu2c_seed_namespace']!=ns: raise AssertionError('namespace')
    if m['replicate_key']!=digest or m['seed']!=digest[:32]: raise AssertionError('seed')
    if m['programs']!=base.p.derive_primary_programs(digest): raise AssertionError('programs')
    return True

def obs_hash(i,states,bpre,lc12,ls12,timers,q_prev,q_prev_side,lc3,ls3):
    x=base._obs(i,states,bpre,lc12,ls12,timers,q_prev,q_prev_side,lc3,ls3)
    return hashlib.sha256(x.tobytes()).hexdigest()

def run_arm_with_audit(m,label):
    validate_manifest(m)
    logs=[]; seen=set()
    target=base.c.localized_v0_step.__code__ if label=='TEACHER_V02' else base.hybrid_step.__code__

    def tracer(frame,event,arg):
        if event!='line' or frame.f_code is not target:
            return tracer
        L=frame.f_locals
        if label=='TEACHER_V02':
            need=('t','i','states','bpre','lc12','ls12','timers','q_prev','q_prev_side','lc3','ls3','lam_c','lam_s','local_lam_h')
            if all(k in L for k in need):
                i=L['i']; t=L['t']; states=L['states']; key=(t,i)
                if key not in seen and isinstance(i,int) and 0<=i<len(states) and states[i]=='U':
                    tp=base._teacher_u_probs(L['lam_c'],L['lam_s'],L['local_lam_h'])
                    _,up=base._learned(i,states,L['bpre'],L['lc12'],L['ls12'],L['timers'],L['q_prev'],L['q_prev_side'],L['lc3'],L['ls3'])
                    tv=float(.5*np.abs(tp-up).sum())
                    logs.append({'arm':'TEACHER_TRAJECTORY_U','t':t,'phase':min(4,t//32),'i':i,'tv':tv,
                                 'obs_sha256':obs_hash(i,states,L['bpre'],L['lc12'],L['ls12'],L['timers'],L['q_prev'],L['q_prev_side'],L['lc3'],L['ls3'])})
                    seen.add(key)
        else:
            need=('t','i','states','bpre','lc12','ls12','timers','q_prev','q_prev_side','lc3','ls3','teacher_probs','learned_probs')
            if all(k in L for k in need):
                i=L['i']; t=L['t']; states=L['states']; key=(t,i)
                if key not in seen and isinstance(i,int) and 0<=i<len(states) and states[i]=='U':
                    tp=np.asarray(L['teacher_probs'],dtype=float)
                    up=np.asarray(L['learned_probs'],dtype=float)
                    tv=float(.5*np.abs(tp-up).sum())
                    logs.append({'arm':'HYBRID_TRAJECTORY_U','t':t,'phase':min(4,t//32),'i':i,'tv':tv,
                                 'obs_sha256':obs_hash(i,states,L['bpre'],L['lc12'],L['ls12'],L['timers'],L['q_prev'],L['q_prev_side'],L['lc3'],L['ls3'])})
                    seen.add(key)
        return tracer

    old_validate=base.validate_manifest
    old_trace=sys.gettrace()
    base.validate_manifest=validate_manifest
    sys.settrace(tracer)
    try:
        r,s,tel=base._run_direct(m,label)
    finally:
        sys.settrace(old_trace)
        base.validate_manifest=old_validate
    return r,s,tel,logs

def stats(logs):
    vals=[x['tv'] for x in logs]
    if not vals: return {'n':0,'mean':None,'median':None,'p90':None,'p95':None,'p99':None,'max':None}
    a=np.asarray(vals,dtype=float)
    return {
        'n':len(vals),'mean':float(a.mean()),'median':float(np.median(a)),
        'p90':float(np.quantile(a,.90)),'p95':float(np.quantile(a,.95)),
        'p99':float(np.quantile(a,.99)),'max':float(a.max())
    }

def summarize(logs):
    out={'overall':stats(logs),'phase':{}}
    for p in range(5):
        out['phase'][str(p)]=stats([x for x in logs if x['phase']==p])
    return out

def run_world(m):
    tr,ts,_,tl=run_arm_with_audit(m,'TEACHER_V02')
    hr,hs,htel,hl=run_arm_with_audit(m,'HYBRID_HU')
    return {
        'manifest':m,
        'teacher_audit':summarize(tl),
        'hybrid_audit':summarize(hl),
        'teacher_state_sha256':tr['state_sha256'],
        'hybrid_state_sha256':hr['state_sha256'],
        'state_trajectories_differ':ts!=hs,
        'hybrid_realized_HU_differences':htel['h_realized_differences']+htel['u_realized_differences'],
    }

def evaluate(worlds):
    overall=[]; phase4=[]; overall_wins=0; phase4_wins=0
    for w in worlds:
        t=w['teacher_audit']['overall']['mean']; h=w['hybrid_audit']['overall']['mean']
        t4=w['teacher_audit']['phase']['4']['mean']; h4=w['hybrid_audit']['phase']['4']['mean']
        if t not in (None,0):
            overall.append(h/t); overall_wins+=int(h>t)
        if t4 not in (None,0):
            phase4.append(h4/t4); phase4_wins+=int(h4>t4)
    med=lambda x: float(np.median(np.asarray(x,dtype=float))) if x else None
    shift=((len(overall)>=8 and overall_wins>=7 and med(overall)>=1.10) or
           (len(phase4)>=8 and phase4_wins>=7 and med(phase4)>=1.15))
    path=(not shift and
          sum(w['hybrid_realized_HU_differences']>0 for w in worlds)>0 and
          sum(w['state_trajectories_differ'] for w in worlds)>=7)
    return {
        'LU2C_U_CLOSED_LOOP_SHIFT_SUPPORTED':bool(shift),
        'LU2C_PATH_DEPENDENCE_WITHOUT_TV_SHIFT_SUPPORTED':bool(path),
        'overall_defined':len(overall),'overall_hybrid_gt_teacher':overall_wins,
        'median_overall_ratio':med(overall),
        'phase4_defined':len(phase4),'phase4_hybrid_gt_teacher':phase4_wins,
        'median_phase4_ratio':med(phase4),
        'trajectory_divergence_worlds':sum(w['state_trajectories_differ'] for w in worlds),
        'worlds_with_realized_HU_differences':sum(w['hybrid_realized_HU_differences']>0 for w in worlds),
    }
