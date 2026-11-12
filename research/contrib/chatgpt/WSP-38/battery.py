"""WSP38 peak-first ceiling and backoff battery; no gradients, no external APIs."""
import argparse
import hashlib
import json
import random
import time
from model import NumericalWorld,RELATIONS

LEVELS=(32768,16384,8192,4096,1024,256)
DENSE_BUDGET_BYTES=512*1024*1024
DEGREE=3
SEEDS={'DEV':(7,), 'PRIMARY':(1103,1109,1117)}


def digest_int(*args):
    return int.from_bytes(hashlib.sha256('|'.join(map(str,args)).encode('ascii')).digest()[:8],'big')


def source(n,world):
    """Independent evaluator retains complete source; compiler only sees records."""
    original=[]
    for rel in range(RELATIONS):
        rows=[]
        for i in range(n):
            targets=set()
            j=0
            while len(targets)<DEGREE:
                targets.add(digest_int('WSP38-EDGE-V1',world,n,rel,i,j)%n)
                j+=1
            rows.append(tuple(sorted(targets)))
        original.append(tuple(rows))
    return tuple(original)


def observed_records(graph,world,n,partial):
    records=[]
    for rel,group in enumerate(graph):
        for src,targets in enumerate(group):
            for dest in targets:
                if partial and digest_int('WSP38-WITHHOLD',world,n,rel,src,dest)%2:
                    continue
                records.append((rel,src,dest))
    return tuple(records)


def ref_reach(graph,source,sequence):
    frontier={source}
    for rel in sequence:
        nxt=set()
        for src in frontier:
            nxt.update(graph[rel][src])
        frontier=nxt
    return frontier


def query_schedule(n,world,count=48):
    schedule=[]
    for q in range(count):
        length=(1,2,3,4,5,6)[q%6]
        relations=tuple(digest_int('WSP38-REL-V1',world,n,q,p)%RELATIONS for p in range(length))
        src=digest_int('WSP38-SOURCE-V1',world,n,q)%n
        dest=digest_int('WSP38-TARGET-V1',world,n,q)%n
        schedule.append((src,relations,dest))
    return tuple(schedule)


def one_trial(n,world):
    start=time.perf_counter()
    graph=source(n,world)
    records=observed_records(graph,world,n,False)
    t=time.perf_counter()
    compiled,unique=NumericalWorld.from_observations(n,records)
    compile_time=time.perf_counter()-t
    if unique!=n*RELATIONS*DEGREE or compiled.active_edges!=unique:
        raise AssertionError('WSP38_EDGE_CUSTODY')
    if compiled.numerical_heap_bytes>DENSE_BUDGET_BYTES:
        raise AssertionError('WSP38_RUNTIME_BUDGET')
    t=time.perf_counter()
    snap=compiled.snapshot()
    restored=NumericalWorld.restore(snap)
    cold_time=time.perf_counter()-t
    if snap!=restored.snapshot():
        raise AssertionError('WSP38_COLD_CHECK')
    qs=query_schedule(n,world)
    hits=0
    positives=negatives=0
    t_num=t_ref=0.0
    digest=hashlib.sha256()
    for src,sequence,dst in qs:
        t=time.perf_counter()
        predicted=restored.answer(src,sequence,dst)
        t_num+=time.perf_counter()-t
        t=time.perf_counter()
        reached=ref_reach(graph,src,sequence)
        oracle=int(dst in reached)
        t_ref+=time.perf_counter()-t
        # Check the FULL set of reachable positive targets, not only sparse random negatives.
        numeric_reach=restored.reach(src,sequence)
        oracle_reach=sum(1<<node for node in reached)
        if numeric_reach!=oracle_reach or predicted!=oracle:
            raise AssertionError('WSP38_KNOWN_PATH_INCORRECT')
        positives+=len(reached)
        negatives+=n-len(reached)
        digest.update(bytes((oracle,len(sequence))))
        hits+=1
    # New combinatorial queries after compilation; no supervision on them.
    new_qs=query_schedule(n,world+500,24)
    for src,sequence,dst in new_qs:
        val=restored.answer(src,sequence,dst)
        novel_reached=ref_reach(graph,src,sequence)
        if val!=int(dst in novel_reached) or restored.reach(src,sequence)!=sum(1<<node for node in novel_reached):
            raise AssertionError('WSP38_NOVEL_COMPOSITION')
        positives+=len(novel_reached)
        negatives+=n-len(novel_reached)
        digest.update(bytes((val,len(sequence))))
    # Active partial-information negative: missing edges are not spontaneously recovered.
    partial_records=observed_records(graph,world,n,True)
    half,_=NumericalWorld.from_observations(n,partial_records)
    false_negatives=0
    for rel,src,dst in records:
        if half.knows(rel,src,dst)==0:
            false_negatives+=1
    if false_negatives<=0 or len(partial_records)>=len(records):
        raise AssertionError('WSP38_MISSING_KNOWLEDGE_NEGATIVE')
    # Local counterfactual repair and noninterference.
    rel=(world*3)%RELATIONS
    node=(world*7)%n
    target=graph[rel][node][0]
    if restored.knows(rel,node,target)!=1:
        raise AssertionError('WSP38_MISSING_EDIT_TARGET')
    edited=restored.patch(rel,node,target,0)
    if edited.knows(rel,node,target)!=0 or edited.active_edges!=unique-1:
        raise AssertionError('WSP38_BAD_REPAIR')
    if NumericalWorld.restore(edited.snapshot()).active_edges!=unique-1:
        raise AssertionError('WSP38_REPAIR_NOT_COLD')
    for j in range(RELATIONS):
        if j!=rel and edited.rows[j]!=restored.rows[j]:
            raise AssertionError('WSP38_CROSSTALK_RELATION')
    if edited.rows[rel][:node]!=restored.rows[rel][:node] or edited.rows[rel][node+1:]!=restored.rows[rel][node+1:]:
        raise AssertionError('WSP38_CROSSTALK_NEIGHBOR')
    # Intervened relation must affect a query, not just a stored bit.
    if edited.answer(node,(rel,),target)!=0 or restored.answer(node,(rel,),target)!=1:
        raise AssertionError('WSP38_COUNTERFACTUAL_FAIL')
    return {'size':n,'world':world,'active_edges':unique,'capacity_bits':compiled.nominal_bits,
            'heap_bytes':compiled.numerical_heap_bytes,'checkpoint_bytes':len(snap),
            'correct':hits,'queries':len(qs),'unseen_compositions':len(new_qs),
            'exact_positive_targets':positives,'exact_negative_targets':negatives,
            'missing_edges':false_negatives,'observed_half_edges':len(partial_records),
            'compile_s':round(compile_time,6),'cold_s':round(cold_time,6),
            'numeric_query_s':round(t_num,6),'sparse_oracle_query_s':round(t_ref,6),
            'elapsed_s':round(time.perf_counter()-start,6),'trace':digest.hexdigest()}


def run(cohort='DEV'):
    if cohort not in SEEDS:
        raise ValueError('WSP38_BAD_COHORT')
    levels=[]
    for n in LEVELS:
        # Predeclared memory boundary. This marks budget exclusion, *not* a model failure.
        nominal=n*n*RELATIONS//8
        if nominal>DENSE_BUDGET_BYTES:
            levels.append({'size':n,'status':'RESOURCE_SCREENED_NOT_EXECUTED',
                           'required_dense_bytes':nominal,'budget_bytes':DENSE_BUDGET_BYTES})
            continue
        trials=[]
        for world in SEEDS[cohort]:
            trials.append(one_trial(n,world))
        levels.append({'size':n,'status':'PASS','trials':trials})
    passed=[x for x in levels if x['status']=='PASS']
    if not passed or len(levels)!=len(LEVELS):
        raise AssertionError('WSP38_BAD_LEVELS')
    if not all(t['correct']==t['queries'] and t['missing_edges']>0 and
               t['exact_positive_targets']>0 and t['exact_negative_targets']>0
               for lvl in passed for t in lvl['trials']):
        raise AssertionError('WSP38_FAILED_CONTROLS')
    feasible=[]
    for lvl in passed:
        items=lvl['trials']
        # Preset sweet spot uses 100% reliability AND memory/cost competitiveness against sparse oracle.
        speed_ratio=sum(x['numeric_query_s'] for x in items)/max(sum(x['sparse_oracle_query_s'] for x in items),1e-9)
        feasible.append({'size':lvl['size'],'speed_ratio_vs_sparse':round(speed_ratio,4),
                         'cost_competitive':speed_ratio<=2.0,
                         'heap_mebibytes':round(max(x['heap_bytes'] for x in items)/1048576,3),
                         'checkpoint_mebibytes':round(max(x['checkpoint_bytes'] for x in items)/1048576,3)})
    winners=[x['size'] for x in feasible if x['cost_competitive']]
    return {'schema':'wsp38.training-free-upper-bound.v1','cohort':cohort,'engineering':'PASS',
            'science':'BOUNDARY_MEASURED_NO_SUPERIORITY_CLAIM',
            'largest_executed':max(x['size'] for x in passed),
            'largest_speed_competitive':max(winners) if winners else None,
            'relative_costs':feasible,'levels':levels,
            'limitations':'Source edge triples and a general-purpose interpreter are supplied. No unknown knowledge or new algorithm is created. Dense capacity is not equal to learned parameter intelligence. Clock measurements are implementation-dependent.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--cohort',choices=tuple(SEEDS),default='DEV')
    print(json.dumps(run(p.parse_args().cohort),sort_keys=True,indent=2))
