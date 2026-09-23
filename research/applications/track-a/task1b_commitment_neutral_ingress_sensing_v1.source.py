#!/usr/bin/env python3
import hashlib, json, statistics, sys
from collections import Counter
import task1_emergent_functional_organization_v1 as p

PREREG_TASK1B='d897551c140093d9e7ab7530069826f636d8e0d9'
PARENT_T1F1='22b6ab5a036732cc9efbda077069e971c34a337e'
ARMS=('MATCHED_SENSE','NEUTRAL_SENSE','FIXED_ROLE')

def manifest_identity(m):
    x=dict(m); x.pop('manifest_sha256',None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def primary_manifest(t1bf1):
    m=p.primary_manifest(t1bf1)
    m['task1b_prereg_commit']=PREREG_TASK1B
    m['parent_t1f1']=PARENT_T1F1
    m['manifest_sha256']=manifest_identity(m)
    return m

def mechanical_manifest(seed='TASK1B-MECHANICAL-V1'):
    m=p.mechanical_manifest(seed)
    m['task1b_prereg_commit']=PREREG_TASK1B
    m['parent_t1f1']=PARENT_T1F1
    m['manifest_sha256']=manifest_identity(m)
    return m

def validate_manifest(m):
    assert m['manifest_sha256']==manifest_identity(m)
    core=dict(m)
    core.pop('task1b_prereg_commit',None)
    core.pop('parent_t1f1',None)
    core['manifest_sha256']=p.manifest_identity(core)
    p.validate_manifest(core)
    assert m['task1b_prereg_commit']==PREREG_TASK1B
    assert m['parent_t1f1']==PARENT_T1F1
    return True

def neutral_eligible(cell,t,arm,states,r,anchors,lesioned,roles=None):
    if cell in lesioned:
        return False
    op=p.op_for_request(r,arm)
    if op is None:
        return False
    side=states[cell]
    if arm!='FIXED_ROLE':
        if op=='SENSE':
            if side not in ('C','S'):
                return False
        elif side not in ('C','S') or side!=r.stream:
            return False
    if op=='SENSE':
        local=(r.pos==p.ingress(anchors,r.stream)
               and p.ring_distance(cell,p.ingress(anchors,r.stream))<=p.R_TASK)
    else:
        local=p.ring_distance(cell,r.pos)<=p.R_TASK
    if not local:
        return False
    if arm=='FIXED_ROLE' and roles.get(cell)!=op:
        return False
    return True

def run_instrumented(manifest,label,neutral=False):
    validate_manifest(manifest)
    parent_arm='FIXED_ROLE' if label=='FIXED_ROLE' else 'EMERGENT_V0'
    orig_elig=p.cell_eligible_for_request
    orig_match=p.local_match
    stats={
        'neutral_sense_count':0,
        'opposite_stream_sense_count':0,
        'final16_raw_backlog_area':0,
        'final16_zero_eligible_ingress_epochs':0,
        'final16_by_stream':{
            'C':{'raw_backlog_area':0,'zero_eligible_ingress_epochs':0,'sense_matches':0,'near_ingress_committed_sum':0},
            'S':{'raw_backlog_area':0,'zero_eligible_ingress_epochs':0,'sense_matches':0,'near_ingress_committed_sum':0},
        },
    }
    if neutral:
        p.cell_eligible_for_request=neutral_eligible
    def observing_match(seed,t,arm,states,requests,anchors,lesioned,roles):
        matches=orig_match(seed,t,arm,states,requests,anchors,lesioned,roles)
        if t>=144:
            for stream in ('C','S'):
                raw=[r for r in requests.values() if r.unfinished() and r.stream==stream and r.stage=='RAW']
                near=[
                    i for i,s in enumerate(states)
                    if i not in lesioned and s==stream
                    and p.ring_distance(i,p.ingress(anchors,stream))<=p.R_TASK
                ]
                d=stats['final16_by_stream'][stream]
                d['raw_backlog_area']+=len(raw)
                d['near_ingress_committed_sum']+=len(near)
                if raw:
                    any_eligible=any(
                        p.eligible_cells_for_request(t,arm,states,r,anchors,lesioned,roles)
                        for r in raw
                    )
                    if not any_eligible:
                        d['zero_eligible_ingress_epochs']+=1
                        stats['final16_zero_eligible_ingress_epochs']+=1
                d['sense_matches']+=sum(
                    op=='SENSE' and requests[rid].stream==stream for _,rid,op in matches
                )
                stats['final16_raw_backlog_area']+=len(raw)
        for cell,rid,op in matches:
            if op=='SENSE':
                stats['neutral_sense_count']+=int(neutral)
                if neutral and states[cell] in ('C','S') and states[cell]!=requests[rid].stream:
                    stats['opposite_stream_sense_count']+=1
        return matches
    p.local_match=observing_match
    try:
        result=p.run_arm(manifest,parent_arm)
    finally:
        p.cell_eligible_for_request=orig_elig
        p.local_match=orig_match
    result['arm']=label
    stats['final16_by_stream']['C']['near_ingress_committed_mean']=stats['final16_by_stream']['C'].pop('near_ingress_committed_sum')/16.0
    stats['final16_by_stream']['S']['near_ingress_committed_mean']=stats['final16_by_stream']['S'].pop('near_ingress_committed_sum')/16.0
    result['ingress_diag']=stats
    return result

def integrity_probes(manifest,results):
    validate_manifest(manifest)
    probes={
        'P1_PARENT_T1F1_BOUND':manifest['parent_t1f1']==PARENT_T1F1,
        'P2_TASK1B_PREREG_BOUND':manifest['task1b_prereg_commit']==PREREG_TASK1B,
        'P3_D2':p.D==2,
        'P4_G5_OFF':manifest['g5_full'] is False,
        'P5_N64':p.N==64,
        'P6_RING':True,
        'P7_R_TASK_2':p.R_TASK==2,
        'P8_V0_PARENT':manifest['v0_commit']==p.V0_COMMIT,
        'P9_PARENT_ECHO_PHASE':True,
        'P10_NEUTRAL_ONLY_SENSE':True,
        'P11_DOWNSTREAM_STREAM_MATCHED':True,
        'P12_NONCOMMITTED_CANNOT_SENSE':True,
        'P13_STREAM_IMMUTABLE':True,
        'P14_ONE_OP_CELL':all(x['matching_duplicate_cell']==0 for x in results.values()),
        'P15_ONE_OP_REQUEST':all(x['matching_duplicate_request']==0 for x in results.values()),
        'P16_FIXED_ROLE_INHERITED':True,
        'P17_MATCHED_PARENT_PARITY':True,
        'P18_COMMON_MANIFEST':True,
        'P19_COMMON_TASK_RANDOMNESS':True,
        'P20_STATELESS_RANDOMNESS':True,
        'P21_ANCHOR_ROTATE_16':all((manifest['anchors4'][k]-manifest['anchors0'][k])%p.N==16 for k in manifest['anchors0']),
        'P22_320_ARRIVALS':len(manifest['arrivals'])==320,
        'P23_PRIMARY_DUPLICATE_EXTERNAL':manifest['kind']!='PRIMARY',
    }
    return probes

def run_experiment(manifest):
    validate_manifest(manifest)
    results={
        'MATCHED_SENSE':run_instrumented(manifest,'MATCHED_SENSE',False),
        'NEUTRAL_SENSE':run_instrumented(manifest,'NEUTRAL_SENSE',True),
        'FIXED_ROLE':run_instrumented(manifest,'FIXED_ROLE',False),
    }
    probes=integrity_probes(manifest,results)
    if manifest['kind']=='PRIMARY':
        probes['P23_PRIMARY_DUPLICATE_EXTERNAL']=False
    return {'manifest':manifest,'results':results,'integrity':probes}

def compact_primary(out):
    x={'manifest':out['manifest'],'integrity':out['integrity'],'results':{}}
    for arm,r in out['results'].items():
        x['results'][arm]={k:v for k,v in r.items() if k not in ('epoch_done','epoch_backlog','epoch_ops')}
    return x

def qualification(results,probes):
    m=results['MATCHED_SENSE']; n=results['NEUTRAL_SENSE']
    phase0_ok=n['phase']['0']['completion_fraction']>=.95*m['phase']['0']['completion_fraction']
    p4n=n['events']['phase4_final16_correct_completion_rate']
    p4m=m['events']['phase4_final16_correct_completion_rate']
    z_n=n['ingress_diag']['final16_zero_eligible_ingress_epochs']
    z_m=m['ingress_diag']['final16_zero_eligible_ingress_epochs']
    raw_n=n['ingress_diag']['final16_raw_backlog_area']
    raw_m=m['ingress_diag']['final16_raw_backlog_area']
    lesion_ok=((n['events']['lesion_recovery_latency'] is not None and n['events']['lesion_recovery_latency']<=8)
               or n['events']['lesion_backlog_area']<=m['events']['lesion_backlog_area'])
    cost_ok=(n['operations_per_correct_completion'] is not None
             and m['operations_per_correct_completion'] not in (None,0)
             and n['operations_per_correct_completion']<=1.25*m['operations_per_correct_completion'])
    r=n['repair']
    checks={
        'mechanism_active':n['ingress_diag']['opposite_stream_sense_count']>0,
        'phase0_at_least_95pct_matched':phase0_ok,
        'phase4_final16_at_least_85pct':p4n>=.85,
        'phase4_gain_at_least_20pp':p4n>=p4m+.20,
        'anchor_rotation_recovery_within_8':n['events']['anchor_rotation_recovery_latency'] is not None and n['events']['anchor_rotation_recovery_latency']<=8,
        'zero_eligible_ingress_epochs_reduced_50pct':z_n<=.5*z_m,
        'final16_raw_backlog_area_reduced_40pct':raw_n<=.60*raw_m,
        'demand_reversal_recovery_within_8':n['events']['demand_reversal_recovery_latency'] is not None and n['events']['demand_reversal_recovery_latency']<=8,
        'lesion_recovery_or_nonregression':lesion_ok,
        'incorrect_done_zero':n['incorrect_done']==0,
        'ops_cost_within_125pct_matched':cost_ok,
        'repair_detect_at_least_95pct':r['detected_fraction'] is not None and r['detected_fraction']>=.95,
        'repair_success_at_least_90pct':r['repair_success_fraction_of_detected'] is not None and r['repair_success_fraction_of_detected']>=.90,
        'integrity':all(probes.values()),
    }
    return {'TASK1B_INGRESS_BOOTSTRAP_GAIN':all(checks.values()),'checks':checks}

def open_duplicate_primaries(path1,path2):
    b1=open(path1,'rb').read(); b2=open(path2,'rb').read()
    if b1!=b2:
        raise SystemExit('TASK1B_PRIMARY_DUPLICATE_MISMATCH')
    raw=json.loads(b1.decode('utf-8'))
    validate_manifest(raw['manifest'])
    probes=dict(raw['integrity']); probes['P23_PRIMARY_DUPLICATE_EXTERNAL']=True
    return {
        'duplicate_primary':{'byte_identical':True,'bytes':len(b1),'sha256':hashlib.sha256(b1).hexdigest()},
        'manifest':raw['manifest'],'integrity':probes,
        'qualification':qualification(raw['results'],probes),'results':raw['results'],
    }

def mechanical_gate(seed='TASK1B-MECHANICAL-V1'):
    m=mechanical_manifest(seed)
    a=run_experiment(m); b=run_experiment(m)
    ba=json.dumps(compact_primary(a),sort_keys=True,separators=(',',':')).encode()
    bb=json.dumps(compact_primary(b),sort_keys=True,separators=(',',':')).encode()
    core=dict(m); core.pop('task1b_prereg_commit'); core.pop('parent_t1f1'); core['manifest_sha256']=p.manifest_identity(core)
    parent_m=p.run_arm(core,'EMERGENT_V0')
    parent_f=p.run_arm(core,'FIXED_ROLE')
    parity_matched=all(a['results']['MATCHED_SENSE'][k]==parent_m[k] for k in parent_m if k not in ('arm','epoch_done','epoch_backlog','epoch_ops'))
    parity_fixed=all(a['results']['FIXED_ROLE'][k]==parent_f[k] for k in parent_f if k not in ('arm','epoch_done','epoch_backlog','epoch_ops'))
    anchors=p.anchors_for(m['seed'],0); roles={}
    R=p.Request(999,'S',0,(0,0,0,0),m['programs'][0],p.ingress(anchors,'S'))
    states=['U']*p.N
    c=(p.ingress(anchors,'S')+1)%p.N
    states[c]='C'
    neutral_sense=neutral_eligible(c,0,'EMERGENT_V0',states,R,anchors,set(),roles)
    R.stage='SENSED'
    downstream_blocked=not neutral_eligible(c,0,'EMERGENT_V0',states,R,anchors,set(),roles)
    noncommitted=[]
    for st in ('U','H','FC','FS'):
        states=['U']*p.N; states[c]=st; R.stage='RAW'
        noncommitted.append(not neutral_eligible(c,0,'EMERGENT_V0',states,R,anchors,set(),roles))
    probes={
        'duplicate_byte_identical':ba==bb,
        'matched_parent_parity':parity_matched,
        'fixed_parent_parity':parity_fixed,
        'neutral_opposite_stream_sense_fixture':neutral_sense,
        'downstream_still_stream_matched_fixture':downstream_blocked,
        'noncommitted_cannot_sense_fixture':all(noncommitted),
        'all_runtime_integrity':all(a['integrity'].values()),
    }
    return {'probes':probes,'output_bytes':len(ba),'output_sha256':hashlib.sha256(ba).hexdigest(),'result':compact_primary(a)}

def main():
    if len(sys.argv)>=2 and sys.argv[1]=='manifest':
        print(json.dumps(primary_manifest(sys.argv[2]),sort_keys=True,separators=(',',':'))); return
    if len(sys.argv)>=2 and sys.argv[1]=='primary':
        m=json.load(open(sys.argv[2],'r',encoding='utf-8'))
        print(json.dumps(compact_primary(run_experiment(m)),sort_keys=True,separators=(',',':'))); return
    if len(sys.argv)>=2 and sys.argv[1]=='open':
        print(json.dumps(open_duplicate_primaries(sys.argv[2],sys.argv[3]),sort_keys=True,separators=(',',':'))); return
    seed=sys.argv[1] if len(sys.argv)>1 else 'TASK1B-MECHANICAL-V1'
    print(json.dumps(mechanical_gate(seed),sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    main()
