"""WSP149 source-blind exact GF(2) coefficient programming and cold prior memory.

Only 32 own charged binary effects enter each fit; no owner/source/evaluator.
FIT worlds may update empirical coefficient support. Transfer priors freeze.
"""
from hashlib import sha256
from json import dumps
from time import process_time_ns,perf_counter_ns

FEATURES=tuple(range(64))
DEGREE=tuple(m.bit_count() for m in FEATURES)
MODEL_SCHEMA='wsp149.exact.gf2.coefficients.v1'
MEMORY_SCHEMA='wsp149.learned.coefficient.prior.v1'

def digest(v):
    return sha256(dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate(rows):
    if (type(rows) not in (list,tuple) or len(rows)!=32 or
        len({x for x,y in rows})!=32 or
        any(type(x) is not int or not 0<=x<64 or
            type(y) is not int or y not in (0,1) for x,y in rows)):
        raise ValueError('WSP149_REQUIRES_32_DISTINCT_CHARGED_BINARY_EFFECTS')
    return tuple((x,y) for x,y in rows)

def _payload(worlds,counts,receipts,frozen):
    return {'schema':MEMORY_SCHEMA,'worlds':worlds,'counts':tuple(counts),
            'row_receipts':tuple(receipts),'frozen':frozen}

def _seal(value):
    return {**value,'digest':digest(value)}

def _check_memory(data):
    if (type(data) is not dict or set(data)!={
        'schema','worlds','counts','row_receipts','frozen','digest'
    } or data['schema']!=MEMORY_SCHEMA):
        raise ValueError('WSP149_MEMORY_SCHEMA_MISMATCH')
    n=data['worlds']
    counts=data['counts'];receipts=data['row_receipts']
    if (type(n) is not int or not 0<=n<=16 or
        type(counts) not in (tuple,list) or len(counts)!=64 or
        any(type(c) is not int or not 0<=c<=n for c in counts) or
        type(receipts) not in (tuple,list) or len(receipts)!=n or
        len(set(receipts))!=n or
        any(type(r) is not str or len(r)!=64 or
            any(s not in '0123456789abcdef' for s in r) for r in receipts) or
        type(data['frozen']) is not bool):
        raise ValueError('WSP149_CORRUPT_MEMORY_PAYLOAD')
    value=_payload(n,counts,receipts,data['frozen'])
    if data['digest']!=digest(value):
        raise ValueError('WSP149_MEMORY_DIGEST_MISMATCH')
    return value

def empty_memory():
    return _seal(_payload(0,(0,)*64,(),False))

def freeze_memory(data):
    value=_check_memory(data)
    if value['worlds']!=16:
        raise ValueError('WSP149_MUST_COMPLETE_16_FIT_WORLDS_BEFORE_TRANSFER')
    return _seal(_payload(value['worlds'],value['counts'],
                          value['row_receipts'],True))

def restore_memory(data):
    return _seal(_check_memory(data))

def coefficient_order(memory=None):
    counts=(0,)*64 if memory is None else _check_memory(memory)['counts']
    return tuple(sorted(FEATURES,key=lambda m:(-counts[m],DEGREE[m],m)))

def mismatched_memory(memory):
    value=_check_memory(memory)
    if not value['frozen']:
        raise ValueError('WSP149_PERMUTED_CONTROL_REQUIRES_FROZEN_PRIOR')
    order=tuple(sorted(FEATURES,key=lambda m:(
        sha256(('WSP149|PRIOR-ABLATION|'+str(m)).encode()).digest(),m)))
    counts=tuple(value['counts'][m] for m in order)
    return _seal(_payload(value['worlds'],counts,value['row_receipts'],True))

def _features(x):
    return sum(1<<m for m in FEATURES if (x&m)==m)

def _parity(bits):
    return bits.bit_count()&1

def fit(rows,memory=None):
    rows=validate(rows)
    if memory is not None:
        _check_memory(memory)
    cpu=process_time_ns();wall=perf_counter_ns()
    order=coefficient_order(memory)
    matrix=[[_features(x),y] for x,y in rows]
    pivots=[];rank=0
    for mask in order:
        i=next((j for j in range(rank,32) if (matrix[j][0]>>mask)&1),None)
        if i is None:continue
        matrix[rank],matrix[i]=matrix[i],matrix[rank]
        for j in range(32):
            if j!=rank and (matrix[j][0]>>mask)&1:
                matrix[j][0]^=matrix[rank][0]
                matrix[j][1]^=matrix[rank][1]
        pivots.append(mask);rank+=1
        if rank==32:break
    if rank!=32:raise AssertionError('WSP149_DISTINCT_INTERVENTIONS_RANK_DEFECT')
    weights=0
    for i in range(rank-1,-1,-1):
        y=matrix[i][1]^_parity(matrix[i][0]&weights)
        if y:weights|=1<<pivots[i]
    if any(_parity(_features(x)&weights)!=y for x,y in rows):
        raise AssertionError('WSP149_GF2_WEIGHT_FIT_NOT_EXACT')
    return {'schema':MODEL_SCHEMA,'weights':weights,'rank':rank,
            'pivot_masks':tuple(pivots),'active_coefficients':weights.bit_count(),
            'rows_sha256':digest(rows),
            'prior_sha256':memory['digest'] if memory else empty_memory()['digest'],
            'cpu_s':round((process_time_ns()-cpu)/1e9,6),
            'wall_s':round((perf_counter_ns()-wall)/1e9,6)}

def predict(model,x):
    if (type(model) is not dict or model.get('schema')!=MODEL_SCHEMA or
        type(model.get('weights')) is not int or
        not 0<=model['weights']<(1<<64) or model.get('rank')!=32):
        raise ValueError('WSP149_INVALID_MODEL')
    if type(x) is not int or not 0<=x<64:
        raise ValueError('WSP149_INVALID_PUBLIC_CONTEXT')
    return _parity(_features(x)&model['weights'])

def predictions(model):
    return tuple(predict(model,x) for x in FEATURES)

def remember(memory,rows):
    value=_check_memory(memory)
    if value['frozen'] or value['worlds']>=16:
        raise ValueError('WSP149_TRANSFER_MEMORY_MUST_REMAIN_FROZEN')
    rows=validate(rows);receipt=digest(rows)
    if receipt in value['row_receipts']:
        raise ValueError('WSP149_DUPLICATE_FIT_WORLD')
    current=fit(rows,memory)
    counts=tuple(value['counts'][m]+((current['weights']>>m)&1) for m in FEATURES)
    updated=_seal(_payload(value['worlds']+1,counts,
                          value['row_receipts']+(receipt,),False))
    return updated,current

def restore_model(saved,rows,memory=None):
    if type(saved) is not dict or saved.get('schema')!=MODEL_SCHEMA:
        raise ValueError('WSP149_BAD_RESTORE_MODEL')
    restored=fit(rows,memory)
    for k in ('schema','weights','rank','pivot_masks',
              'active_coefficients','rows_sha256','prior_sha256'):
        if restored[k]!=saved.get(k):
            raise ValueError('WSP149_COLD_WEIGHT_RESTORE_MISMATCH')
    return restored
