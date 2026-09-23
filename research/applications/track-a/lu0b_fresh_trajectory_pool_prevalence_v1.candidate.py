#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import defaultdict
from pathlib import Path
import task1f_local_hedge_ambiguity_r1_v1 as f

p=f.p
e=f.e
b=f.b

PREREG_LU0B='fc0332e5ab625e5aa05b931dbf47a43034760dfd'
PARENT_LU0_CLOSURE='074513c64a64318053fcbfcabdc9207202849063'
PARENT_LU0F1='67b4c725193c6af707f5d3937d6854006704bfaa'
PARENT_V01='4d3887fba0478bc1ef3bc4bea44f8e08582f5803'
TASK1H_CLOSURE='1b848079ae0d54dd9e7b01c8d004a93b16aeb62d'
PARENT_T1FF1_R1='1b05bc066314138a0eae05c02c31ba8b84f5f063'
REPLICATES=5

_OBS=None
_ORIGINAL_STEP=f.local_hedge_v0_step


def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def replicate_key(lu0bf1,k):
    if not isinstance(lu0bf1,str) or len(lu0bf1)!=40:
        raise ValueError('LU0BF1 must be a 40-character commit SHA')
    if k not in range(1,REPLICATES+1):
        raise ValueError(k)
    return hashlib.sha1(f'LU0B-PREVALENCE|{lu0bf1}|{k}'.encode()).hexdigest()


def _primary_manifest(lu0bf1,k):
    key=replicate_key(lu0bf1,k)
    programs=p.derive_primary_programs(key)
    seed=hashlib.sha256(f'LU0B-PRIMARY-SEED|{lu0bf1}|{k}'.encode()).hexdigest()[:32]
    arrivals=p.make_arrivals(seed,programs)
    corrupt_ids=[x['rid'] for x in arrivals if p.u01('TASK1-CORRUPT',seed,x['rid'])<0.05]
    m={
        'kind':'LU0B_PRIMARY','seed':seed,'t1f1':lu0bf1,
        'v0_commit':p.V0_COMMIT,'prereg_commit':p.PREREG_COMMIT,
        'programs':programs,'arrivals':arrivals,'corrupt_ids':corrupt_ids,
        'lesion':sorted(p.lesion_set(seed)),
        'anchors0':p.anchors_for(seed,0),'anchors4':p.anchors_for(seed,128),
        'n':p.N,'t':p.T,'d':p.D,'r_task':p.R_TASK,'route_edges':6,'g5_full':False,
        'task1b_prereg_commit':b.PREREG_TASK1B,'parent_t1f1':b.PARENT_T1F1,
        'task1e_prereg_commit':e.PREREG_TASK1E,'parent_t1bf1':e.PARENT_T1BF1,
        'handoff_diag_commit':e.HANDOFF_DIAG,
        'task1f_prereg_commit':f.PREREG_TASK1F,'parent_t1ef1':f.PARENT_T1EF1,
        'parent_task1e_closure':f.PARENT_CLOSURE,'state_diag_commit':f.STATE_DIAG,
        'task1ff1':PARENT_T1FF1_R1,'replicate':k,'replicate_key':key,
        'lu0b_prereg_commit':PREREG_LU0B,
        'parent_lu0_closure':PARENT_LU0_CLOSURE,
        'parent_lu0f1':PARENT_LU0F1,
        'parent_v01':PARENT_V01,
        'task1h_closure':TASK1H_CLOSURE,
        'lu0bf1':lu0bf1,
    }
    m['manifest_sha256']=manifest_identity(m)
    return m


def primary_manifests(lu0bf1):
    return [_primary_manifest(lu0bf1,k) for k in range(1,REPLICATES+1)]


def mechanical_manifest(seed='LU0B-MECHANICAL-V1'):
    m=f.mechanical_manifest(seed)
    m.update({
        'lu0b_prereg_commit':PREREG_LU0B,
        'parent_lu0_closure':PARENT_LU0_CLOSURE,
        'parent_lu0f1':PARENT_LU0F1,
        'parent_v01':PARENT_V01,
        'task1h_closure':TASK1H_CLOSURE,
        'lu0bf1':None,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m


def core_manifest(m):
    x=dict(m)
    for k in (
        'lu0b_prereg_commit','parent_lu0_closure','parent_lu0f1',
        'parent_v01','task1h_closure','lu0bf1'
    ):
        x.pop(k,None)
    if x.get('kind')=='LU0B_PRIMARY':
        x['kind']='LU0B_PARENT'
    x['manifest_sha256']=f.manifest_identity(x)
    return x


def validate_manifest(m):
    assert m['manifest_sha256']==manifest_identity(m)
    assert m['lu0b_prereg_commit']==PREREG_LU0B
    assert m['parent_lu0_closure']==PARENT_LU0_CLOSURE
    assert m['parent_lu0f1']==PARENT_LU0F1
    assert m['parent_v01']==PARENT_V01
    assert m['task1h_closure']==TASK1H_CLOSURE
    core=core_manifest(m)
    f.validate_manifest(core)
    if m['kind']=='LU0B_PRIMARY':
        k=m['replicate']
        assert k in range(1,REPLICATES+1)
        assert isinstance(m['lu0bf1'],str) and len(m['lu0bf1'])==40
        key=replicate_key(m['lu0bf1'],k)
        assert m['replicate_key']==key
        assert m['programs']==p.derive_primary_programs(key)
        seed=hashlib.sha256(f'LU0B-PRIMARY-SEED|{m["lu0bf1"]}|{k}'.encode()).hexdigest()[:32]
        assert m['seed']==seed
        assert json.dumps(m['arrivals'],sort_keys=True,separators=(',',':'))==json.dumps(
            p.make_arrivals(seed,m['programs']),sort_keys=True,separators=(',',':')
        )
        assert m['corrupt_ids']==[
            x['rid'] for x in m['arrivals']
            if p.u01('TASK1-CORRUPT',seed,x['rid'])<0.05
        ]
        assert m['lesion']==sorted(p.lesion_set(seed))
        assert m['anchors0']==p.anchors_for(seed,0)
        assert m['anchors4']==p.anchors_for(seed,128)
    return True


def _phase(t):
    return min(4,max(0,int(t)//32))


def _new_bucket():
    return {
        'u_evaluations':0,
        'directional_evaluable':0,
        'tv_values':[],
        'rate_values':[],
        'side_flips':0,
        'pc_values':[],
        'ps_values':[],
        'pool_gap_values':[],
    }


def _fresh_observer():
    return {
        'all':_new_bucket(),
        'phase':{str(i):_new_bucket() for i in range(5)},
        'support_calls':0,
        'support_pairs':0,
        'support_sequence_errors':0,
        'pending':{},
        'observer_step_calls':0,
        'shadow_feedback_writes':0,
    }


def _side(a,b):
    if a>b: return 'C'
    if b>a: return 'S'
    return 'TIE'


def _record(bucket,pc,ps,lc3c,ls3c,sm_c,sm_s):
    sup_c=p.W_POOL*pc+p.W_LOCAL*lc3c
    sup_s=p.W_POOL*ps+p.W_LOCAL*ls3c
    opp_c=p.W_POOL*ps+p.W_LOCAL*ls3c
    opp_s=p.W_POOL*pc+p.W_LOCAL*lc3c
    g_c=1.0/(1.0+(opp_c/p.K_SUPP)**p.N_SUPP) if opp_c>0 else 1.0
    g_s=1.0/(1.0+(opp_s/p.K_SUPP)**p.N_SUPP) if opp_s>0 else 1.0
    lam_c=p.ETA*sup_c*g_c+p.ETA*sm_c
    lam_s=p.ETA*sup_s*g_s+p.ETA*sm_s

    sup_c0=p.W_LOCAL*lc3c
    sup_s0=p.W_LOCAL*ls3c
    opp_c0=p.W_LOCAL*ls3c
    opp_s0=p.W_LOCAL*lc3c
    g_c0=1.0/(1.0+(opp_c0/p.K_SUPP)**p.N_SUPP) if opp_c0>0 else 1.0
    g_s0=1.0/(1.0+(opp_s0/p.K_SUPP)**p.N_SUPP) if opp_s0>0 else 1.0
    lam_c0=p.ETA*sup_c0*g_c0+p.ETA*sm_c
    lam_s0=p.ETA*sup_s0*g_s0+p.ETA*sm_s

    actual=lam_c+lam_s
    local=lam_c0+lam_s0
    rr=abs(actual-local)/max(actual,1e-12)

    bucket['u_evaluations']+=1
    bucket['rate_values'].append(rr)
    bucket['pc_values'].append(pc)
    bucket['ps_values'].append(ps)
    bucket['pool_gap_values'].append(abs(pc-ps))

    if actual>0 and local>0:
        sc=lam_c/actual
        sc0=lam_c0/local
        tv=abs(sc-sc0)
        bucket['directional_evaluable']+=1
        bucket['tv_values'].append(tv)
        sa=_side(lam_c,lam_s)
        sl=_side(lam_c0,lam_s0)
        if (sa=='C' and sl=='S') or (sa=='S' and sl=='C'):
            bucket['side_flips']+=1


def observed_step(seed,t,states,timers,bstate,q_prev,q_prev_side,cp,sp,requests):
    global _OBS
    if _OBS is None:
        raise RuntimeError('LU0B observer not initialized')
    _OBS['observer_step_calls']+=1

    dc,ds,lc12,ls12,lc3,ls3=p.demand_adapter(requests)
    fb_c=sum(1 for i,s in enumerate(states) if s=='C' and dc[i]>=ds[i])
    fb_s=sum(1 for i,s in enumerate(states) if s=='S' and ds[i]>=dc[i])
    cp2=0.75*cp+sum(dc)+fb_c
    sp2=0.75*sp+sum(ds)+fb_s
    pc=min(1.0,cp2/p.POOL_NORM)
    ps=min(1.0,sp2/p.POOL_NORM)

    original_margin=p.support_margin_field
    pending={}
    phase_key=str(_phase(t))

    def spy(st,bpre,a12,b12,i,side):
        val=original_margin(st,bpre,a12,b12,i,side)
        _OBS['support_calls']+=1
        if side=='C':
            if i in pending:
                _OBS['support_sequence_errors']+=1
            pending[i]=val
        elif side=='S':
            if i not in pending:
                _OBS['support_sequence_errors']+=1
            else:
                sm_c=pending.pop(i)
                _OBS['support_pairs']+=1
                _record(_OBS['all'],pc,ps,lc3[i],ls3[i],sm_c,val)
                _record(_OBS['phase'][phase_key],pc,ps,lc3[i],ls3[i],sm_c,val)
        else:
            _OBS['support_sequence_errors']+=1
        return val

    p.support_margin_field=spy
    try:
        out=_ORIGINAL_STEP(seed,t,states,timers,bstate,q_prev,q_prev_side,cp,sp,requests)
    finally:
        p.support_margin_field=original_margin

    if pending:
        _OBS['support_sequence_errors']+=len(pending)
    return out


def _mean(xs):
    return sum(xs)/len(xs) if xs else None


def _median(xs):
    return statistics.median(xs) if xs else None


def _p90(xs):
    if not xs: return None
    ys=sorted(xs)
    return ys[max(0,math.ceil(.90*len(ys))-1)]


def _frac_ge(xs,cut):
    return sum(x>=cut for x in xs)/len(xs) if xs else 0.0


def _finalize_bucket(bk):
    tvs=bk['tv_values']
    rates=bk['rate_values']
    return {
        'u_evaluations':bk['u_evaluations'],
        'directional_evaluable':bk['directional_evaluable'],
        'directional_undefined':bk['u_evaluations']-bk['directional_evaluable'],
        'mean_tv_side':_mean(tvs),
        'median_tv_side':_median(tvs),
        'p90_tv_side':_p90(tvs),
        'fraction_tv_ge_001':_frac_ge(tvs,.01),
        'fraction_tv_ge_005':_frac_ge(tvs,.05),
        'fraction_tv_ge_010':_frac_ge(tvs,.10),
        'side_flips':bk['side_flips'],
        'side_flip_fraction':bk['side_flips']/bk['directional_evaluable'] if bk['directional_evaluable'] else 0.0,
        'mean_rate_delta':_mean(rates),
        'median_rate_delta':_median(rates),
        'p90_rate_delta':_p90(rates),
        'fraction_rate_ge_010':_frac_ge(rates,.10),
        'fraction_rate_ge_025':_frac_ge(rates,.25),
        'fraction_rate_ge_050':_frac_ge(rates,.50),
        'mean_abs_pc_minus_ps':_mean(bk['pool_gap_values']),
        'mean_pc':_mean(bk['pc_values']),
        'mean_ps':_mean(bk['ps_values']),
    }


def finalize_observer(obs):
    return {
        'all':_finalize_bucket(obs['all']),
        'phase':{k:_finalize_bucket(v) for k,v in obs['phase'].items()},
        'support_calls':obs['support_calls'],
        'support_pairs':obs['support_pairs'],
        'support_sequence_errors':obs['support_sequence_errors'],
        'observer_step_calls':obs['observer_step_calls'],
        'shadow_feedback_writes':obs['shadow_feedback_writes'],
    }


def run_world(manifest):
    global _OBS
    validate_manifest(manifest)
    core=core_manifest(manifest)
    parent_direct=f.run_arm(core,'LOCAL_HEDGE') if manifest['kind']=='LU0B_MECHANICAL' else None

    old_step=f.local_hedge_v0_step
    _OBS=_fresh_observer()
    try:
        f.local_hedge_v0_step=observed_step
        observed=f.run_arm(core,'LOCAL_HEDGE')
        telemetry=finalize_observer(_OBS)
    finally:
        f.local_hedge_v0_step=old_step
        _OBS=None

    parity=None
    if parent_direct is not None:
        parity=observed==parent_direct

    integrity={
        'observer_active':telemetry['observer_step_calls']>0 and telemetry['all']['u_evaluations']>0,
        'support_calls_paired':telemetry['support_calls']==2*telemetry['support_pairs'],
        'no_support_sequence_errors':telemetry['support_sequence_errors']==0,
        'shadow_never_writes_back':telemetry['shadow_feedback_writes']==0,
        'request_bound':observed['handoff_diag']['bound_semantics'] is True,
        'one_op_cell':observed['matching_duplicate_cell']==0,
        'one_op_request':observed['matching_duplicate_request']==0,
        'incorrect_done_zero':observed['incorrect_done']==0,
    }
    if parity is not None:
        integrity['parent_exact_parity']=parity

    parent_summary={
        'correct_done':observed['correct_done'],
        'incorrect_done':observed['incorrect_done'],
        'operations_per_correct_completion':observed['operations_per_correct_completion'],
        'phase4_final16_correct_completion_rate':observed['events']['phase4_final16_correct_completion_rate'],
        'anchor_rotation_recovery_latency':observed['events']['anchor_rotation_recovery_latency'],
        'demand_reversal_recovery_latency':observed['events']['demand_reversal_recovery_latency'],
        'matching_duplicate_cell':observed['matching_duplicate_cell'],
        'matching_duplicate_request':observed['matching_duplicate_request'],
    }
    return {'manifest':manifest,'observer':telemetry,'parent_summary':parent_summary,'integrity':integrity}


def mechanical_gate():
    m=f.mechanical_manifest('LU0B-MECHANICAL-V1')
    m.update({
        'kind':'LU0B_MECHANICAL',
        'lu0b_prereg_commit':PREREG_LU0B,
        'parent_lu0_closure':PARENT_LU0_CLOSURE,
        'parent_lu0f1':PARENT_LU0F1,
        'parent_v01':PARENT_V01,
        'task1h_closure':TASK1H_CLOSURE,
        'lu0bf1':None,
    })
    m['manifest_sha256']=manifest_identity(m)
    a=run_world(m)
    z=run_world(m)
    ba=json.dumps(a,sort_keys=True,separators=(',',':')).encode()
    bz=json.dumps(z,sort_keys=True,separators=(',',':')).encode()

    roundtrip=True
    try:
        for pm in primary_manifests('0'*40):
            validate_manifest(json.loads(json.dumps(pm,sort_keys=True,separators=(',',':'))))
    except Exception:
        roundtrip=False

    probes={
        'exact_parent_local_hedge_parity':a['integrity'].get('parent_exact_parity') is True,
        'observer_returns_parent_values_unchanged':a['integrity'].get('parent_exact_parity') is True,
        'primary_generator_frozen_pre_manifest':roundtrip,
        'observer_captures_u_evaluations':a['observer']['all']['u_evaluations']>0,
        'no_non_u_support_misclassification':a['integrity']['support_calls_paired'] and a['integrity']['no_support_sequence_errors'],
        'counterfactual_never_enters_dynamics':a['observer']['shadow_feedback_writes']==0,
        'phase_labels_diagnostic_only':sum(v['u_evaluations'] for v in a['observer']['phase'].values())==a['observer']['all']['u_evaluations'],
        'duplicate_byte_identical':ba==bz,
        'runtime_integrity':all(a['integrity'].values()),
    }
    return {
        'prereg':PREREG_LU0B,
        'parent_v01':PARENT_V01,
        'probes':probes,
        'mechanical_bytes':len(ba),
        'mechanical_sha256':hashlib.sha256(ba).hexdigest(),
        'directional_fraction_denominator':'directional_evaluable only; undefined local C/S denominator is reported separately',
        'p90_definition':'nearest-rank ceil(0.90*n)',
    }


def run_sweep(manifests):
    return [run_world(m) for m in manifests]


def qualification(sweep):
    assert len(sweep)==REPLICATES
    all_integrity=all(all(x['integrity'].values()) for x in sweep)
    active_all=all(x['observer']['all']['u_evaluations']>0 for x in sweep)
    tv5=[x['observer']['all']['fraction_tv_ge_005'] for x in sweep]
    rate10=[x['observer']['all']['fraction_rate_ge_010'] for x in sweep]
    worlds_flips=sum(x['observer']['all']['side_flips']>0 for x in sweep)
    total_flips=sum(x['observer']['all']['side_flips'] for x in sweep)
    total_eval=sum(x['observer']['all']['directional_evaluable'] for x in sweep)
    pooled_flip=total_flips/total_eval if total_eval else 0.0

    directional_checks={
        'observer_active_all5':active_all,
        'parent_runtime_integrity_all5':all_integrity,
        'median_fraction_tv_ge_005_at_least_010':statistics.median(tv5)>=.10,
        'side_flip_worlds_at_least_4of5':worlds_flips>=4,
        'pooled_side_flip_fraction_at_least_002':pooled_flip>=.02,
    }
    directional=all(directional_checks.values())

    rate_checks={
        'observer_active_all5':active_all,
        'parent_runtime_integrity_all5':all_integrity,
        'median_fraction_rate_ge_010_at_least_025':statistics.median(rate10)>=.25,
        'rate_nonzero_worlds_at_least_4of5':sum(x>0 for x in rate10)>=4,
    }
    rate=all(rate_checks.values())

    negligible_checks={
        'directional_not_prevalent':not directional,
        'rate_not_prevalent':not rate,
        'median_fraction_tv_ge_005_below_001':statistics.median(tv5)<.01,
        'median_fraction_rate_ge_010_below_005':statistics.median(rate10)<.05,
        'pooled_side_flip_fraction_below_0001':pooled_flip<.001,
    }
    negligible=all(negligible_checks.values())

    return {
        'LU0B_DIRECTIONAL_POOL_PREVALENT':directional,
        'LU0B_RATE_POOL_PREVALENT':rate,
        'LU0B_POOL_PRACTICALLY_NEGLIGIBLE':negligible,
        'directional_checks':directional_checks,
        'rate_checks':rate_checks,
        'negligible_checks':negligible_checks,
        'median_world_fraction_tv_ge_005':statistics.median(tv5),
        'median_world_fraction_rate_ge_010':statistics.median(rate10),
        'worlds_with_side_flips':worlds_flips,
        'pooled_side_flips':total_flips,
        'pooled_directional_evaluable':total_eval,
        'pooled_side_flip_fraction':pooled_flip,
        'worlds':[
            {
                'replicate':x['manifest']['replicate'],
                'manifest_sha256':x['manifest']['manifest_sha256'],
                'observer':x['observer'],
                'parent_summary':x['parent_summary'],
                'integrity':x['integrity'],
            } for x in sweep
        ],
    }


def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2:
        raise SystemExit('LU0B_SWEEP_DUPLICATE_MISMATCH')
    raw=json.loads(b1.decode())
    for x in raw:
        validate_manifest(x['manifest'])
    return {
        'duplicate_sweep':{
            'byte_identical':True,
            'bytes':len(b1),
            'sha256':hashlib.sha256(b1).hexdigest(),
        },
        'qualification':qualification(raw),
        'sweep':raw,
    }


def write_json(path,obj):
    Path(path).write_bytes(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())


def main():
    if len(sys.argv)>=2 and sys.argv[1]=='mechanical':
        out=mechanical_gate()
        if len(sys.argv)>=3: write_json(sys.argv[2],out)
        else: print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    if len(sys.argv)>=2 and sys.argv[1]=='manifests':
        out=primary_manifests(sys.argv[2])
        if len(sys.argv)>=4: write_json(sys.argv[3],out)
        else: print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    if len(sys.argv)>=2 and sys.argv[1]=='sweep':
        ms=json.load(open(sys.argv[2],'r',encoding='utf-8'))
        out=run_sweep(ms)
        if len(sys.argv)>=4: write_json(sys.argv[3],out)
        else: print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    if len(sys.argv)>=2 and sys.argv[1]=='open':
        out=open_duplicate(sys.argv[2],sys.argv[3])
        if len(sys.argv)>=5: write_json(sys.argv[4],out)
        else: print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    print(json.dumps(mechanical_gate(),sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
