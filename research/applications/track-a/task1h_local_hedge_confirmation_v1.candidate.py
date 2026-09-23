#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path
import task1f_local_hedge_ambiguity_r1_v1 as f

p=f.p
e=f.e

PREREG_TASK1H='1e284a15d0e176cbee09c57a1e219ba6927f05b0'
PARENT_T1FF1_R1='1b05bc066314138a0eae05c02c31ba8b84f5f063'
PARENT_TASK1F_CLOSURE='fda86a2fee99fb948524b53b0eb0652011d655f6'
PARENT_TASK1G_CLOSURE='b11eb856b1348d8d08cc99497ac59f7a15e7ceaa'
SERVICE_ENVELOPE_AUDIT='e6ea693894ab12a6d542d50e297e97abf801124c'
REPLICATES=5
ARMS=('GLOBAL_HEDGE','LOCAL_HEDGE')


def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def replicate_key(t1hf1,k):
    if not isinstance(t1hf1,str) or len(t1hf1)!=40:
        raise ValueError('T1HF1 must be 40-char commit SHA')
    if k not in range(1,REPLICATES+1):
        raise ValueError(k)
    return hashlib.sha1(f'TASK1H-CONFIRM|{t1hf1}|{k}'.encode()).hexdigest()


def _base_primary_manifest(t1hf1,k):
    key=replicate_key(t1hf1,k)
    programs=p.derive_primary_programs(key)
    seed=hashlib.sha256(f'TASK1H-PRIMARY-SEED|{t1hf1}|{k}'.encode()).hexdigest()[:32]
    arrivals=p.make_arrivals(seed,programs)
    corrupt_ids=[x['rid'] for x in arrivals if p.u01('TASK1-CORRUPT',seed,x['rid'])<0.05]
    m={
        'kind':'TASK1H_PRIMARY','seed':seed,'t1f1':t1hf1,
        'v0_commit':p.V0_COMMIT,'prereg_commit':p.PREREG_COMMIT,
        'programs':programs,'arrivals':arrivals,'corrupt_ids':corrupt_ids,
        'lesion':sorted(p.lesion_set(seed)),
        'anchors0':p.anchors_for(seed,0),'anchors4':p.anchors_for(seed,128),
        'n':p.N,'t':p.T,'d':p.D,'r_task':p.R_TASK,'route_edges':6,'g5_full':False,
        'task1b_prereg_commit':f.b.PREREG_TASK1B,'parent_t1f1':f.b.PARENT_T1F1,
        'task1e_prereg_commit':e.PREREG_TASK1E,'parent_t1bf1':e.PARENT_T1BF1,
        'handoff_diag_commit':e.HANDOFF_DIAG,
        'task1f_prereg_commit':f.PREREG_TASK1F,'parent_t1ef1':f.PARENT_T1EF1,
        'parent_task1e_closure':f.PARENT_CLOSURE,'state_diag_commit':f.STATE_DIAG,
        'task1ff1':PARENT_T1FF1_R1,'replicate':k,'replicate_key':key,
        'task1h_prereg_commit':PREREG_TASK1H,
        'parent_t1ff1_r1':PARENT_T1FF1_R1,
        'parent_task1f_closure':PARENT_TASK1F_CLOSURE,
        'parent_task1g_closure':PARENT_TASK1G_CLOSURE,
        'service_envelope_audit':SERVICE_ENVELOPE_AUDIT,
        'task1hf1':t1hf1,
    }
    m['manifest_sha256']=manifest_identity(m)
    return m


def primary_manifests(t1hf1):
    return [_base_primary_manifest(t1hf1,k) for k in range(1,REPLICATES+1)]


def mechanical_manifest(seed='TASK1H-MECHANICAL-V1'):
    m=f.mechanical_manifest(seed)
    m.update({
        'task1h_prereg_commit':PREREG_TASK1H,
        'parent_t1ff1_r1':PARENT_T1FF1_R1,
        'parent_task1f_closure':PARENT_TASK1F_CLOSURE,
        'parent_task1g_closure':PARENT_TASK1G_CLOSURE,
        'service_envelope_audit':SERVICE_ENVELOPE_AUDIT,
        'task1hf1':None,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m


def core_manifest(m):
    x=dict(m)
    for k in (
        'task1h_prereg_commit','parent_t1ff1_r1','parent_task1f_closure',
        'parent_task1g_closure','service_envelope_audit','task1hf1'
    ):
        x.pop(k,None)
    if x.get('kind')=='TASK1H_PRIMARY':
        x['kind']='TASK1H_PARENT'
    x['manifest_sha256']=f.manifest_identity(x)
    return x


def validate_manifest(m):
    assert m['manifest_sha256']==manifest_identity(m)
    assert m['task1h_prereg_commit']==PREREG_TASK1H
    assert m['parent_t1ff1_r1']==PARENT_T1FF1_R1
    assert m['parent_task1f_closure']==PARENT_TASK1F_CLOSURE
    assert m['parent_task1g_closure']==PARENT_TASK1G_CLOSURE
    assert m['service_envelope_audit']==SERVICE_ENVELOPE_AUDIT
    core=core_manifest(m)
    f.validate_manifest(core)
    if m['kind']=='TASK1H_PRIMARY':
        k=m['replicate']
        assert k in range(1,REPLICATES+1)
        assert isinstance(m['task1hf1'],str) and len(m['task1hf1'])==40
        key=replicate_key(m['task1hf1'],k)
        assert m['replicate_key']==key
        assert m['programs']==p.derive_primary_programs(key)
        seed=hashlib.sha256(f'TASK1H-PRIMARY-SEED|{m["task1hf1"]}|{k}'.encode()).hexdigest()[:32]
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


def run_arm(manifest,label):
    if label not in ARMS:
        raise AssertionError(label)
    validate_manifest(manifest)
    core=core_manifest(manifest)
    r=f.run_arm(core,label)
    r['arm']=label
    r['task1h_repair_report']={
        'detected_fraction':r['repair']['detected_fraction'],
        'repair_success_fraction_of_detected':r['repair']['repair_success_fraction_of_detected'],
        'service_envelope_audit_parent':SERVICE_ENVELOPE_AUDIT,
        'deadline_impossible_and_horizon_censoring_are_descriptive_not_confirmation_gates':True,
    }
    return r


def compact_result(r):
    return {k:v for k,v in r.items() if k not in ('epoch_done','epoch_backlog','epoch_ops')}


def run_replicate(manifest):
    results={a:run_arm(manifest,a) for a in ARMS}
    probes={
        'parent_t1ff1_r1':manifest['parent_t1ff1_r1']==PARENT_T1FF1_R1,
        'task1h_prereg':manifest['task1h_prereg_commit']==PREREG_TASK1H,
        'exact_task1f_run_arm_reused':True,
        'd2':p.D==2,
        'g5_off':manifest['g5_full'] is False,
        'n64':p.N==64,
        'r_task_2':p.R_TASK==2,
        'request_bound':all(x['handoff_diag']['bound_semantics'] for x in results.values()),
        'one_op_cell':all(x['matching_duplicate_cell']==0 for x in results.values()),
        'one_op_request':all(x['matching_duplicate_request']==0 for x in results.values()),
        'incorrect_done_zero':all(x['incorrect_done']==0 for x in results.values()),
    }
    return {'manifest':manifest,'results':results,'integrity':probes}


def compact_replicate(x):
    return {
        'manifest':x['manifest'],
        'integrity':x['integrity'],
        'results':{a:compact_result(r) for a,r in x['results'].items()},
    }


def run_sweep(manifests):
    return [compact_replicate(run_replicate(m)) for m in manifests]


def _median(xs):
    return statistics.median(xs) if xs else None


def qualification(sweep):
    gains=[]
    backlog_red=[]
    gain_pos=0
    backlog_pos=0
    s_gain_pos=0
    phase0_ok=True
    cost_ok=True
    safe=True
    mech_all=True
    q_phase4=[]
    q_anchor=[]
    q_demand=[]
    q_lesion=[]
    reps=[]

    for x in sweep:
        g=x['results']['GLOBAL_HEDGE']
        q=x['results']['LOCAL_HEDGE']
        p4g=g['events']['phase4_final16_correct_completion_rate']
        p4q=q['events']['phase4_final16_correct_completion_rate']
        gain=p4q-p4g
        gains.append(gain)
        gain_pos+=gain>0
        br=(
            (g['final16_total_backlog_area']-q['final16_total_backlog_area'])
            / g['final16_total_backlog_area']
            if g['final16_total_backlog_area'] else 0.0
        )
        backlog_red.append(br)
        backlog_pos+=q['final16_total_backlog_area']<g['final16_total_backlog_area']
        sg=(
            q['task1f_stream_diag']['new4_S_correct_done']
            - g['task1f_stream_diag']['new4_S_correct_done']
        )
        s_gain_pos+=sg>0
        phase0_ok &= (
            q['phase']['0']['completion_fraction']
            >= .95*g['phase']['0']['completion_fraction']
        )
        cost_ok &= (
            q['operations_per_correct_completion'] is not None
            and g['operations_per_correct_completion'] not in (None,0)
            and q['operations_per_correct_completion']
                <=1.25*g['operations_per_correct_completion']
        )
        safe &= q['incorrect_done']==0 and all(x['integrity'].values())
        hd=q.get('hedge_diag') or {}
        changed=sum(
            v.get('release_prob_changed',0)+v.get('formation_lambda_changed',0)
            for v in hd.values()
        )
        mech_all &= changed>0
        q_phase4.append(p4q)
        ar=q['events']['anchor_rotation_recovery_latency']
        q_anchor.append(ar is not None and ar<=8)
        dr=q['events']['demand_reversal_recovery_latency']
        q_demand.append(dr is not None and dr<=8)
        lr=q['events']['lesion_recovery_latency']
        q_lesion.append(
            (lr is not None and lr<=8)
            or q['events']['lesion_backlog_area']<=g['events']['lesion_backlog_area']
        )
        reps.append({
            'replicate':x['manifest']['replicate'],
            'phase4_gain':gain,
            'backlog_reduction':br,
            'global_phase4':p4g,
            'local_phase4':p4q,
            'global_new4_S_done':g['task1f_stream_diag']['new4_S_correct_done'],
            'local_new4_S_done':q['task1f_stream_diag']['new4_S_correct_done'],
            'local_repair_detection':q['repair']['detected_fraction'],
            'local_repair_success':q['repair']['repair_success_fraction_of_detected'],
        })

    confirm_checks={
        'mechanism_active_all5':mech_all,
        'phase0_nonregression_all5':phase0_ok,
        'positive_phase4_gain_at_least_4of5':gain_pos>=4,
        'median_phase4_gain_at_least_10pp':_median(gains)>=.10,
        'backlog_lower_at_least_4of5':backlog_pos>=4,
        'median_backlog_reduction_at_least_15pct':_median(backlog_red)>=.15,
        'new4_S_completion_gain_at_least_4of5':s_gain_pos>=4,
        'incorrect_done_zero_and_integrity_all5':safe,
        'ops_cost_within_125pct_all5':cost_ok,
    }
    confirmed=all(confirm_checks.values())
    strong_checks={
        'confirmation':confirmed,
        'median_local_phase4_at_least_85pct':_median(q_phase4)>=.85,
        'local_phase4_at_least_85pct_4of5':sum(v>=.85 for v in q_phase4)>=4,
        'anchor_recovery_4of5':sum(q_anchor)>=4,
        'demand_reversal_all5':all(q_demand),
        'lesion_all5':all(q_lesion),
    }
    strong=confirmed and all(strong_checks.values())

    return {
        'TASK1H_LOCAL_HEDGE_CONFIRMED':confirmed,
        'TASK1H_LOCAL_HEDGE_STRONG_CONFIRMATION':strong,
        'confirmation_checks':confirm_checks,
        'strong_confirmation_checks':strong_checks,
        'median_phase4_gain':_median(gains),
        'median_backlog_reduction':_median(backlog_red),
        'median_local_phase4':_median(q_phase4),
        'replicates':reps,
    }


def open_duplicate_sweeps(path1,path2):
    b1=open(path1,'rb').read()
    b2=open(path2,'rb').read()
    if b1!=b2:
        raise SystemExit('TASK1H_SWEEP_DUPLICATE_MISMATCH')
    raw=json.loads(b1.decode())
    assert len(raw)==REPLICATES
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


def mechanical_gate(seed='TASK1H-MECHANICAL-V1'):
    m=mechanical_manifest(seed)
    a=compact_replicate(run_replicate(m))
    z=compact_replicate(run_replicate(m))
    ba=json.dumps(a,sort_keys=True,separators=(',',':')).encode()
    bz=json.dumps(z,sort_keys=True,separators=(',',':')).encode()

    core=core_manifest(m)
    parent_g=f.run_arm(core,'GLOBAL_HEDGE')
    parent_l=f.run_arm(core,'LOCAL_HEDGE')
    ag=a['results']['GLOBAL_HEDGE']
    al=a['results']['LOCAL_HEDGE']

    def comparable(x):
        return {k:v for k,v in compact_result(x).items()
                if k not in ('arm','task1h_repair_report')}

    hd=al.get('hedge_diag') or {}
    changed=sum(
        v.get('release_prob_changed',0)+v.get('formation_lambda_changed',0)
        for v in hd.values()
    )

    roundtrip_ok=True
    try:
        for pm in primary_manifests('0'*40):
            validate_manifest(json.loads(json.dumps(pm,sort_keys=True,separators=(',',':'))))
    except Exception:
        roundtrip_ok=False

    probes={
        'global_parent_exact_parity':comparable(ag)==comparable(parent_g),
        'local_parent_exact_parity':comparable(al)==comparable(parent_l),
        'local_hedge_mechanism_active':changed>0,
        'no_dynamics_reimplemented':True,
        'd2':p.D==2,
        'g5_off':m['g5_full'] is False,
        'n64':p.N==64,
        'r_task_2':p.R_TASK==2,
        'request_bound_preserved':al['handoff_diag']['bound_semantics'] is True,
        'one_op_cell':a['integrity']['one_op_cell'],
        'one_op_request':a['integrity']['one_op_request'],
        'primary_manifest_json_roundtrip':roundtrip_ok,
        'duplicate_byte_identical':ba==bz,
        'runtime_integrity':all(a['integrity'].values()),
    }
    return {
        'probes':probes,
        'output_bytes':len(ba),
        'output_sha256':hashlib.sha256(ba).hexdigest(),
        'result':a,
    }


def write_json(path,obj):
    data=json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
    Path(path).write_bytes(data)


def main():
    if len(sys.argv)>=2 and sys.argv[1]=='manifests':
        obj=primary_manifests(sys.argv[2])
        if len(sys.argv)>=4:
            write_json(sys.argv[3],obj)
        else:
            print(json.dumps(obj,sort_keys=True,separators=(',',':')))
        return
    if len(sys.argv)>=2 and sys.argv[1]=='sweep':
        ms=json.load(open(sys.argv[2],'r',encoding='utf-8'))
        out=run_sweep(ms)
        if len(sys.argv)>=4:
            write_json(sys.argv[3],out)
        else:
            print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    if len(sys.argv)>=2 and sys.argv[1]=='open':
        out=open_duplicate_sweeps(sys.argv[2],sys.argv[3])
        if len(sys.argv)>=5:
            write_json(sys.argv[4],out)
        else:
            print(json.dumps(out,sort_keys=True,separators=(',',':')))
        return
    seed=sys.argv[1] if len(sys.argv)>1 else 'TASK1H-MECHANICAL-V1'
    print(json.dumps(mechanical_gate(seed),sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
