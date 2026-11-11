"""WSP23 complete finite observed-response closure, independently checked.

Producer uses packed vectors; verifier uses componentwise Boolean tuples and
checks every successor. No oracle response is supplied to the neural learner.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-22'))
from dag_capacity import (OBSERVED,RAW,PlasticNand,context,search,check_certificate,
                          MAX_STATES,MAX_TRANSITIONS,brute_depth_two)
SEEDS=(17,29,43,71)


def canonical_bytes(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode('ascii')


def produce(mode,max_sites=6):
    if mode not in ('connected','allow_disconnected') or type(max_sites) is not int or max_sites not in range(7):
        raise ValueError('WSP23_BAD_PRODUCER_CONFIG')
    sources=set(RAW)
    if mode=='allow_disconnected':sources.add(0)
    layers=[[sum(1<<v for v in sources)]];outputs=[sorted(set(RAW))];transitions=0
    for depth in range(1,max_sites+1):
        following=set();all_outputs=set(outputs[-1])
        for state in layers[-1]:
            vals=[v for v in range(64) if state&(1<<v)]
            for i,a in enumerate(vals):
                for b in vals[i:]:
                    transitions+=1
                    if transitions>MAX_TRANSITIONS:raise RuntimeError('WSP23_CAP_UNRESOLVED')
                    value=63^(a&b);all_outputs.add(value)
                    if state&(1<<value):continue
                    following.add(state|(1<<value))
                    if sum(map(len,layers))+len(following)>MAX_STATES:raise RuntimeError('WSP23_CAP_UNRESOLVED')
        layers.append(sorted(following));outputs.append(sorted(all_outputs))
    return {'schema':'wsp23.response-closure.v1','mode':mode,'max_sites':max_sites,
            'layers':layers,'outputs':outputs,'transitions':transitions,'stored_states':sum(map(len,layers))}


def verify(proof):
    """Independent complete checker; never calls produce or packed NAND."""
    if type(proof) is not dict or set(proof)!={'schema','mode','max_sites','layers','outputs','transitions','stored_states'}:
        raise ValueError('WSP23_BAD_PROOF')
    mode=proof['mode'];depth=proof['max_sites'];layers=proof['layers'];outputs=proof['outputs']
    if (proof['schema']!='wsp23.response-closure.v1' or mode not in ('connected','allow_disconnected')
            or type(depth) is not int or depth not in range(7) or type(layers) is not list or type(outputs) is not list
            or len(layers)!=depth+1 or len(outputs)!=depth+1
            or type(proof['transitions']) is not int or proof['transitions']<0
            or type(proof['stored_states']) is not int or proof['stored_states']<1):raise ValueError('WSP23_BAD_PROOF')
    total=0
    for group in layers:
        if type(group) is not list or any(type(v) is not int or not 0<=v<2**64 for v in group) or group!=sorted(set(group)):
            raise ValueError('WSP23_BAD_FRONTIER')
        total+=len(group)
    if total>500000:raise ValueError('WSP23_PROOF_CAP_UNRESOLVED')
    for group in outputs:
        if type(group) is not list or any(type(v) is not int or v not in range(64) for v in group) or group!=sorted(set(group)):
            raise ValueError('WSP23_BAD_OUTPUTS')
    observed=(0,1,2,4,7,3)
    raw=[]
    for coordinate in range(3):
        row=[]
        for index in observed:
            bit=(index//(2**coordinate))%2;row.append(bool(bit))
        raw.append(tuple(row))
    encode=lambda row:sum(int(v)*(2**j) for j,v in enumerate(row))
    initial=set(encode(row) for row in raw)
    initial_outputs=sorted(initial)
    if mode=='allow_disconnected':initial.add(0)
    if layers[0]!=[sum(2**v for v in initial)] or outputs[0]!=initial_outputs:
        raise ValueError('WSP23_WRONG_ROOT_OR_FREE_OUTPUT')
    transitions=0
    for level in range(1,depth+1):
        expected_states=set();expected_outputs=set(outputs[level-1])
        for state in layers[level-1]:
            patterns=[v for v in range(64) if (state//(2**v))%2]
            vectors=[tuple(bool((v//(2**j))%2) for j in range(6)) for v in patterns]
            for i,left in enumerate(vectors):
                for right in vectors[i:]:
                    transitions+=1
                    if transitions>10000000:raise ValueError('WSP23_CHECKER_CAP_UNRESOLVED')
                    result=tuple(not(a and b) for a,b in zip(left,right))
                    value=encode(result);expected_outputs.add(value)
                    if value not in patterns:
                        expected_states.add(sum(2**v for v in set(patterns+[value])))
                        if sum(len(v) for v in layers[:level])+len(expected_states)>500000:
                            raise ValueError('WSP23_CHECKER_CAP_UNRESOLVED')
        if layers[level]!=sorted(expected_states) or outputs[level]!=sorted(expected_outputs):
            raise ValueError('WSP23_CLOSURE_MISMATCH')
    if proof['stored_states']!=total or proof['transitions']!=transitions:
        raise ValueError('WSP23_WRONG_ACCOUNTING')
    return {'verified':True,'states':total,'transitions':transitions,
            'output_count':len(outputs[-1]),'unreachable':sorted(set(range(64))-set(outputs[-1]))}


def workload_ceiling(reachable,saved):
    trace=[];total=old_total=infeasible=0
    for seed in SEEDS:
        for signature in range(32):
            original=tuple((context(index),(signature>>j)&1) for j,index in enumerate(OBSERVED[:5]))
            model=PlasticNand().learn(original,seed)
            witness=1-model.predict(context(3));target=signature+(witness<<5)
            protection=sum(1<<j for j,(x,y) in enumerate(original) if model.predict(x)==y)
            old_total+=protection.bit_count();infeasible+=target not in reachable
            eligible=[v for v in reachable if ((v^target)&protection)==0]
            if not eligible:raise AssertionError('WSP23_NO_INITIAL_MODEL_REPRESENTATION')
            best=max(6-(v^target).bit_count() for v in eligible)
            optimal=[v for v in eligible if 6-(v^target).bit_count()==best]
            total+=best;trace.append({'seed':seed,'original_signature':signature,'observed_target':target,
                                      'protected_mask':protection,'ceiling':best,'optimal_responses':optimal})
    score=saved['scores']['single_protected']['observed_correct']
    if old_total!=saved['initial_old_correct'] or saved['scores']['single_protected']['old_valid_lost']!=0:
        raise AssertionError('WSP23_WORKLOAD_SOURCE_DRIFT')
    if score>total:raise AssertionError('WSP23_CONTROL_EXCEEDS_CAPACITY_INVALID')
    return {'exact_protected_ceiling_of768':total,'saved_control_correct':score,
            'gap_to_ceiling':total-score,'target_infeasible_tasks_of128':infeasible,
            'initial_old_valid':old_total,'trace':trace}


def run(output_dir=None):
    start=time.perf_counter();proofs={};arms={}
    for mode in ('connected','allow_disconnected'):
        tick=time.perf_counter();proof=produce(mode);producer_seconds=time.perf_counter()-tick
        tick=time.perf_counter();checked=verify(proof);checker_seconds=time.perf_counter()-tick
        reachable=set(proof['outputs'][-1]);witnesses=search(mode,tuple(range(64)))['certificates']
        if {c['signature'] for c in witnesses}!=reachable:raise AssertionError('WSP23_SAT_COVERAGE_MISMATCH')
        for cert in witnesses:check_certificate(cert)
        # Independent full Boolean brute enumeration at depth<=2.
        if set(proof['outputs'][2])!=brute_depth_two(mode):raise AssertionError('WSP23_SMALL_AUDIT_FAILURE')
        proofs[mode]=proof
        arms[mode]={**checked,'layer_sizes':list(map(len,proof['layers'])),
                    'output_counts_by_depth':list(map(len,proof['outputs'])),'sat_witnesses_checked':len(witnesses),
                    'cold_restores':len(witnesses),'proof_sha256':hashlib.sha256(canonical_bytes(proof)).hexdigest(),
                    'proof_bytes':len(canonical_bytes(proof)),'producer_seconds':producer_seconds,'checker_seconds':checker_seconds}
    root=Path(__file__).resolve().parents[1]
    source=root/'WSP-20'/'result-first-packed.json';saved=json.loads(source.read_text())
    ceiling=workload_ceiling(set(proofs['allow_disconnected']['outputs'][-1]),saved)
    trace=ceiling.pop('trace')
    report={'schema':'wsp23.checked-capacity-ceiling.v1','engineering':'PASS','capacity_proof':'VERIFIED_COMPLETE',
            'native_control_classification':'CAPACITY_SATURATING' if ceiling['gap_to_ceiling']==0 else 'RESIDUAL_SEARCH_GAP',
            'arms':arms,'workload':ceiling,'workload_trace_sha256':hashlib.sha256(canonical_bytes(trace)).hexdigest(),
            'saved_control_result_sha256':hashlib.sha256(source.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
            'parent_sha':'1f340f1fa550675454d91cc0db7b9dd76fbea50a','synaptic_scalars':75,'max_sites':6,
            'seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},
            'scientific_superiority':'NONE; finite known-workload capacity proof, not a new learned improvement',
            'scope':'Six fixed observed inputs, exact NAND/row/output rules. Full hidden truth, unknown environments and general learning remain unverified.'}
    if output_dir is not None:
        folder=Path(output_dir);folder.mkdir(parents=True,exist_ok=True)
        for mode,proof in proofs.items():(folder/('proof-'+mode+'.json')).write_bytes(canonical_bytes(proof)+b'\n')
        (folder/'workload-trace.json').write_bytes(canonical_bytes(trace)+b'\n')
        (folder/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    # Verify repository evidence on final qualification without mutating it.
    own=Path(__file__).resolve().parent
    for mode,proof in proofs.items():
        artifact=own/('proof-'+mode+'.json')
        if artifact.exists() and json.loads(artifact.read_text())!=proof:raise AssertionError('WSP23_PROOF_ARTIFACT_DRIFT')
    artifact=own/'workload-trace.json'
    if artifact.exists() and json.loads(artifact.read_text())!=trace:raise AssertionError('WSP23_TRACE_ARTIFACT_DRIFT')
    print(json.dumps(report,sort_keys=True,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-evidence',type=Path);args=p.parse_args();run(args.write_evidence)
