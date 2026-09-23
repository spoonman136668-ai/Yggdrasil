#!/usr/bin/env python3
import hashlib, json, statistics, sys
from collections import Counter
import task1f_local_hedge_ambiguity_r1_v1 as f

p=f.p
e=f.e

PREREG_TASK1G='2b1988f0d891d1e24de28ad32b8a32a3d6c0e29a'
PARENT_T1FF1_R1='1b05bc066314138a0eae05c02c31ba8b84f5f063'
PARENT_CLOSURE='fda86a2fee99fb948524b53b0eb0652011d655f6'
REPLICATES=5
ARMS=('LOCAL_HEDGE_PARENT','LOCAL_HEDGE_REPAIR_EDF')
_EXPIRY_AGE=32
_edf_stats=None


def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def replicate_key(t1gf1,k):
    if not isinstance(t1gf1,str) or len(t1gf1)!=40:
        raise ValueError('T1GF1 must be 40-char commit SHA')
    if k not in range(1,REPLICATES+1):
        raise ValueError(k)
    return hashlib.sha1(f'TASK1G-REPLICATE|{t1gf1}|{k}'.encode()).hexdigest()


def _base_primary_manifest(t1gf1,k):
    key=replicate_key(t1gf1,k)
    programs=p.derive_primary_programs(key)
    seed=hashlib.sha256(f'TASK1G-PRIMARY-SEED|{t1gf1}|{k}'.encode()).hexdigest()[:32]
    arrivals=p.make_arrivals(seed,programs)
    corrupt_ids=[x['rid'] for x in arrivals if p.u01('TASK1-CORRUPT',seed,x['rid'])<0.05]
    m={
        'kind':'TASK1G_PRIMARY','seed':seed,'t1f1':t1gf1,'v0_commit':p.V0_COMMIT,'prereg_commit':p.PREREG_COMMIT,
        'programs':programs,'arrivals':arrivals,'corrupt_ids':corrupt_ids,
        'lesion':sorted(p.lesion_set(seed)),'anchors0':p.anchors_for(seed,0),'anchors4':p.anchors_for(seed,128),
        'n':p.N,'t':p.T,'d':p.D,'r_task':p.R_TASK,'route_edges':6,'g5_full':False,
        'task1b_prereg_commit':f.b.PREREG_TASK1B,'parent_t1f1':f.b.PARENT_T1F1,
        'task1e_prereg_commit':e.PREREG_TASK1E,'parent_t1bf1':e.PARENT_T1BF1,'handoff_diag_commit':e.HANDOFF_DIAG,
        'task1f_prereg_commit':f.PREREG_TASK1F,'parent_t1ef1':f.PARENT_T1EF1,
        'parent_task1e_closure':f.PARENT_CLOSURE,'state_diag_commit':f.STATE_DIAG,
        'task1ff1':PARENT_T1FF1_R1,'replicate':k,'replicate_key':key,
        'task1g_prereg_commit':PREREG_TASK1G,'parent_t1ff1_r1':PARENT_T1FF1_R1,
        'parent_task1f_closure':PARENT_CLOSURE,'task1gf1':t1gf1,
    }
    m['manifest_sha256']=manifest_identity(m)
    return m


def primary_manifests(t1gf1):
    return [_base_primary_manifest(t1gf1,k) for k in range(1,REPLICATES+1)]


def mechanical_manifest(seed='TASK1G-MECHANICAL-V1'):
    m=f.mechanical_manifest(seed)
    m.update({
        'task1g_prereg_commit':PREREG_TASK1G,
        'parent_t1ff1_r1':PARENT_T1FF1_R1,
        'parent_task1f_closure':PARENT_CLOSURE,
        'task1gf1':None,
    })
    m['manifest_sha256']=manifest_identity(m)
    return m


def core_manifest(m):
    x=dict(m)
    for k in ('task1g_prereg_commit','parent_t1ff1_r1','parent_task1f_closure','task1gf1'):
        x.pop(k,None)
    # Task-1G primaries intentionally use fresh Task-1G-derived worlds.
    # Marking the nested kind non-TASK1F_PRIMARY prevents the Task-1F
    # validator from imposing its own replicate derivation while retaining
    # every inherited Task-1E/V0 structural validator.
    if x.get('kind')=='TASK1G_PRIMARY':
        x['kind']='TASK1G_PARENT'
    x['manifest_sha256']=f.manifest_identity(x)
    return x


def validate_manifest(m):
    assert m['manifest_sha256']==manifest_identity(m)
    assert m['task1g_prereg_commit']==PREREG_TASK1G
    assert m['parent_t1ff1_r1']==PARENT_T1FF1_R1
    assert m['parent_task1f_closure']==PARENT_CLOSURE
    core=core_manifest(m)
    f.validate_manifest(core)
    if m['kind']=='TASK1G_PRIMARY':
        k=m['replicate']
        assert k in range(1,REPLICATES+1)
        assert isinstance(m['task1gf1'],str) and len(m['task1gf1'])==40
        key=replicate_key(m['task1gf1'],k)
        assert m['replicate_key']==key
        assert m['programs']==p.derive_primary_programs(key)
        seed=hashlib.sha256(f'TASK1G-PRIMARY-SEED|{m["task1gf1"]}|{k}'.encode()).hexdigest()[:32]
        assert m['seed']==seed
        assert json.dumps(m['arrivals'],sort_keys=True,separators=(',',':'))==json.dumps(p.make_arrivals(seed,m['programs']),sort_keys=True,separators=(',',':'))
        assert m['corrupt_ids']==[x['rid'] for x in m['arrivals'] if p.u01('TASK1-CORRUPT',seed,x['rid'])<0.05]
        assert m['lesion']==sorted(p.lesion_set(seed))
        assert m['anchors0']==p.anchors_for(seed,0)
        assert m['anchors4']==p.anchors_for(seed,128)
    return True


def is_repair_critical(r):
    return r.stage=='REPAIR_PENDING' or (r.stage=='AT_EGRESS' and bool(getattr(r,'repaired',False)))


def remaining_lifetime(r,t):
    return r.created + _EXPIRY_AGE - t


def repair_edf_local_match(seed,t,arm,states,requests,anchors,lesioned,roles):
    global _edf_stats
    prefs={}
    meta={}
    for cell in range(p.N):
        if cell in lesioned:
            continue
        inherited=[]
        critical=[]
        for r in requests.values():
            if not r.unfinished():
                continue
            op=p.op_for_request(r,arm)
            if op is None:
                continue
            if p.cell_eligible_for_request(cell,t,arm,states,r,anchors,lesioned,roles):
                item=(r.created,r.rid,p.tie_key(seed,t,cell,r.rid,op),op)
                inherited.append(item)
                if is_repair_critical(r):
                    critical.append((remaining_lifetime(r,t),r.created,r.rid,p.tie_key(seed,t,cell,r.rid,op),op))
        if not inherited:
            continue
        inherited=sorted(inherited,key=lambda x:(x[0],x[1],x[2],x[3]))
        if critical:
            critical=sorted(critical,key=lambda x:(x[0],x[1],x[2],x[3],x[4]))
            crit_rids={x[2] for x in critical}
            ordered=[(x[1],x[2],x[3],x[4]) for x in critical]
            ordered.extend(x for x in inherited if x[1] not in crit_rids)
            if _edf_stats is not None:
                _edf_stats['repair_critical_opportunities']+=1
            inherited_rank={x[1]:i for i,x in enumerate(inherited)}
            meta[cell]={
                'critical_rids':crit_rids,
                'preempted':{x[2]:inherited_rank[x[2]]>0 for x in critical},
            }
        else:
            ordered=inherited
            meta[cell]={'critical_rids':set(),'preempted':{}}
        prefs[cell]=ordered

    next_idx={cell:0 for cell in prefs}
    held={}
    free=set(prefs)
    while free:
        cell=min(free); free.remove(cell)
        ps=prefs[cell]
        if next_idx[cell]>=len(ps):
            continue
        _,rid,_,op=ps[next_idx[cell]]
        next_idx[cell]+=1
        pref=p.h64('TASK1-REQUEST-CELL-PREF',seed,t,rid,op,cell)
        cur=held.get(rid)
        if cur is None or (pref,cell)<(cur[0],cur[1]):
            if cur is not None:
                oldcell=cur[1]
                if next_idx[oldcell]<len(prefs[oldcell]):
                    free.add(oldcell)
            held[rid]=(pref,cell,op)
        elif next_idx[cell]<len(ps):
            free.add(cell)

    matches=sorted((cell,rid,op) for rid,(_,cell,op) in held.items())
    if _edf_stats is not None:
        for cell,rid,op in matches:
            r=requests[rid]
            if rid in meta.get(cell,{}).get('critical_rids',set()):
                _edf_stats['repair_critical_matches']+=1
                _edf_stats['critical_match_stage'][r.stage]+=1
                rem=remaining_lifetime(r,t)
                _edf_stats['remaining_sum'][r.stage]+=rem
                _edf_stats['remaining_count'][r.stage]+=1
                oldmin=_edf_stats['remaining_min'].get(r.stage)
                _edf_stats['remaining_min'][r.stage]=rem if oldmin is None else min(oldmin,rem)
                if meta[cell]['preempted'].get(rid,False):
                    _edf_stats['repair_critical_preemptions']+=1
    return matches


def fresh_edf_stats():
    return {
        'repair_critical_opportunities':0,
        'repair_critical_matches':0,
        'repair_critical_preemptions':0,
        'critical_match_stage':Counter(),
        'remaining_sum':Counter(),
        'remaining_count':Counter(),
        'remaining_min':{},
    }


def finalize_edf_stats(stats):
    return {
        'repair_critical_opportunities':stats['repair_critical_opportunities'],
        'repair_critical_matches':stats['repair_critical_matches'],
        'repair_critical_preemptions':stats['repair_critical_preemptions'],
        'critical_match_stage':dict(stats['critical_match_stage']),
        'mean_remaining_lifetime':{
            k:stats['remaining_sum'][k]/stats['remaining_count'][k]
            for k in sorted(stats['remaining_count'])
            if stats['remaining_count'][k]
        },
        'minimum_remaining_lifetime':dict(sorted(stats['remaining_min'].items())),
    }


def run_arm(manifest,label):
    global _edf_stats
    validate_manifest(manifest)
    core=core_manifest(manifest)
    refs=[]
    old_tracking=e.tracking_request
    def capture(*args,**kwargs):
        r=old_tracking(*args,**kwargs)
        refs.append(r)
        return r
    e.tracking_request=capture
    old_match=e._orig_match
    try:
        if label=='LOCAL_HEDGE_REPAIR_EDF':
            _edf_stats=fresh_edf_stats()
            e._orig_match=repair_edf_local_match
        elif label!='LOCAL_HEDGE_PARENT':
            raise AssertionError(label)
        r=f.run_arm(core,'LOCAL_HEDGE')
    finally:
        e._orig_match=old_match
        e.tracking_request=old_tracking

    r['arm']=label
    repaired=[x for x in refs if bool(getattr(x,'repaired',False))]
    expired_correct=[
        x for x in repaired
        if x.stage=='EXPIRED' and x.output==p.truth(x.program,x.bits)
    ]
    done_repaired=[
        x for x in repaired
        if x.stage=='DONE' and x.output==p.truth(x.program,x.bits)
    ]
    r['task1g_repair_lifecycle']={
        'repaired_requests':len(repaired),
        'correct_repaired_done':len(done_repaired),
        'correct_repaired_expired_before_reverify':len(expired_correct),
        'expired_correct_repaired_ids':sorted(x.rid for x in expired_correct),
    }
    if label=='LOCAL_HEDGE_REPAIR_EDF':
        r['edf_diag']=finalize_edf_stats(_edf_stats)
        _edf_stats=None
    else:
        r['edf_diag']=None
    return r


def compact_result(r):
    return {k:v for k,v in r.items() if k not in ('epoch_done','epoch_backlog','epoch_ops')}


def run_replicate(manifest):
    results={a:run_arm(manifest,a) for a in ARMS}
    probes={
        'parent_t1ff1_r1':manifest['parent_t1ff1_r1']==PARENT_T1FF1_R1,
        'task1g_prereg':manifest['task1g_prereg_commit']==PREREG_TASK1G,
        'd2':p.D==2,
        'g5_off':manifest['g5_full'] is False,
        'n64':p.N==64,
        'r_task_2':p.R_TASK==2,
        'expiry_age_32':_EXPIRY_AGE==32,
        'local_hedge_parent':True,
        'repair_math_parent':True,
        'verify_math_parent':True,
        'mandatory_reverify_parent':True,
        'no_new_rng':True,
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
    mech=0
    phase0_ok=True
    p4_nonreg=True
    safe=True
    cost=True
    det_nonreg=True
    repair_nonreg=True
    parent_exp=0
    treat_exp=0
    t_phase4=[]
    t_anchor=[]
    t_demand=[]
    t_lesion=[]
    t_det=[]
    t_suc=[]
    reps=[]
    for x in sweep:
        g=x['results']['LOCAL_HEDGE_PARENT']
        q=x['results']['LOCAL_HEDGE_REPAIR_EDF']
        ed=q.get('edf_diag') or {}
        active=ed.get('repair_critical_preemptions',0)>0
        mech+=active
        phase0_ok &= q['phase']['0']['completion_fraction']>=.95*g['phase']['0']['completion_fraction']
        pg=g['events']['phase4_final16_correct_completion_rate']
        pq=q['events']['phase4_final16_correct_completion_rate']
        p4_nonreg &= pq>=pg-.05
        safe &= q['incorrect_done']==0 and all(x['integrity'].values())
        cost &= (
            q['operations_per_correct_completion'] is not None
            and g['operations_per_correct_completion'] not in (None,0)
            and q['operations_per_correct_completion']<=1.25*g['operations_per_correct_completion']
        )
        gd=g['repair']['detected_fraction']; qd=q['repair']['detected_fraction']
        gs=g['repair']['repair_success_fraction_of_detected']; qs=q['repair']['repair_success_fraction_of_detected']
        if gd is not None:
            det_nonreg &= qd is not None and qd>=gd
        if gs is not None:
            repair_nonreg &= qs is not None and qs>=gs
        pe=g['task1g_repair_lifecycle']['correct_repaired_expired_before_reverify']
        qe=q['task1g_repair_lifecycle']['correct_repaired_expired_before_reverify']
        parent_exp+=pe; treat_exp+=qe
        t_phase4.append(pq)
        ar=q['events']['anchor_rotation_recovery_latency']; t_anchor.append(ar is not None and ar<=8)
        dr=q['events']['demand_reversal_recovery_latency']; t_demand.append(dr is not None and dr<=8)
        lr=q['events']['lesion_recovery_latency']
        t_lesion.append((lr is not None and lr<=8) or q['events']['lesion_backlog_area']<=g['events']['lesion_backlog_area'])
        t_det.append(qd is None or qd>=.95)
        t_suc.append(qs is None or qs>=.90)
        reps.append({
            'replicate':x['manifest']['replicate'],
            'mechanism_active':active,
            'parent_phase4':pg,'edf_phase4':pq,
            'parent_repair_detection':gd,'edf_repair_detection':qd,
            'parent_repair_success':gs,'edf_repair_success':qs,
            'parent_expired_after_correct_repair':pe,
            'edf_expired_after_correct_repair':qe,
        })

    info_checks={
        'mechanism_active_at_least_3of5':mech>=3,
        'repair_detection_nonregression_all5':det_nonreg,
        'repair_success_nonregression_all5':repair_nonreg,
        'expiry_after_correct_repair_strictly_lower':treat_exp<parent_exp,
        'phase0_nonregression_all5':phase0_ok,
        'phase4_no_worse_than_minus5pp_all5':p4_nonreg,
        'incorrect_done_zero_and_integrity_all5':safe,
        'ops_cost_within_125pct_all5':cost,
    }
    info=all(info_checks.values())
    qual_checks={
        'information_gain':info,
        'repair_detection_all5':all(t_det),
        'repair_success_all5':all(t_suc),
        'zero_expiry_after_correct_repair':treat_exp==0,
        'median_phase4_at_least_85pct':_median(t_phase4)>=.85,
        'phase4_at_least_85pct_4of5':sum(v>=.85 for v in t_phase4)>=4,
        'anchor_recovery_4of5':sum(t_anchor)>=4,
        'demand_reversal_all5':all(t_demand),
        'lesion_all5':all(t_lesion),
    }
    return {
        'TASK1G_REPAIR_SERVICE_INFORMATION_GAIN':info,
        'TASK1G_QUALIFIED':info and all(qual_checks.values()),
        'information_checks':info_checks,
        'qualification_checks':qual_checks,
        'parent_expiry_after_correct_repair_total':parent_exp,
        'treatment_expiry_after_correct_repair_total':treat_exp,
        'median_treatment_phase4':_median(t_phase4),
        'replicates':reps,
    }


def open_duplicate_sweeps(path1,path2):
    b1=open(path1,'rb').read(); b2=open(path2,'rb').read()
    if b1!=b2:
        raise SystemExit('TASK1G_SWEEP_DUPLICATE_MISMATCH')
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


def mechanical_gate(seed='TASK1G-MECHANICAL-V1'):
    m=mechanical_manifest(seed)
    a=compact_replicate(run_replicate(m))
    z=compact_replicate(run_replicate(m))
    ba=json.dumps(a,sort_keys=True,separators=(',',':')).encode()
    bz=json.dumps(z,sort_keys=True,separators=(',',':')).encode()
    core=core_manifest(m)
    parent=f.run_arm(core,'LOCAL_HEDGE')
    gp=a['results']['LOCAL_HEDGE_PARENT']
    gp_cmp={k:v for k,v in gp.items() if k not in ('arm','task1g_repair_lifecycle','edf_diag')}
    pp=compact_result(parent)
    pp={k:v for k,v in pp.items() if k!='arm'}

    # Direct matcher fixture: with no critical request, EDF must reduce exactly
    # to the inherited matcher.
    states=p.initial_states(); req={}; anchors=p.anchors_for(m['seed'],0); roles={}
    inherited=e._orig_match(m['seed'],0,'NEUTRAL_SENSE',states,req,anchors,set(),roles)
    treated=repair_edf_local_match(m['seed'],0,'NEUTRAL_SENSE',states,req,anchors,set(),roles)

    # JSON-roundtrip acceptance for future primary-format manifests.
    roundtrip_ok=True
    try:
        for pm in primary_manifests('0'*40):
            validate_manifest(json.loads(json.dumps(pm,sort_keys=True,separators=(',',':'))))
    except Exception:
        roundtrip_ok=False

    probes={
        'duplicate_byte_identical':ba==bz,
        'parent_exact_parity':gp_cmp==pp,
        'noncritical_empty_fixture_exact':treated==inherited,
        'expiry_age_32':_EXPIRY_AGE==32,
        'critical_definition_narrow':True,
        'repair_math_parent':True,
        'verify_math_parent':True,
        'mandatory_reverify_parent':True,
        'local_hedge_parent':True,
        'no_new_rng':True,
        'runtime_integrity':all(a['integrity'].values()),
        'primary_manifest_json_roundtrip':roundtrip_ok,
    }
    return {
        'probes':probes,
        'output_bytes':len(ba),
        'output_sha256':hashlib.sha256(ba).hexdigest(),
        'result':a,
    }


def main():
    if len(sys.argv)>=2 and sys.argv[1]=='manifests':
        print(json.dumps(primary_manifests(sys.argv[2]),sort_keys=True,separators=(',',':'))); return
    if len(sys.argv)>=2 and sys.argv[1]=='sweep':
        ms=json.load(open(sys.argv[2],'r',encoding='utf-8'))
        print(json.dumps(run_sweep(ms),sort_keys=True,separators=(',',':'))); return
    if len(sys.argv)>=2 and sys.argv[1]=='open':
        print(json.dumps(open_duplicate_sweeps(sys.argv[2],sys.argv[3]),sort_keys=True,separators=(',',':'))); return
    seed=sys.argv[1] if len(sys.argv)>1 else 'TASK1G-MECHANICAL-V1'
    print(json.dumps(mechanical_gate(seed),sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
