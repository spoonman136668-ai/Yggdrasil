"""WSP-150: source-free exact ambiguity certificates for WSP-149 numerical weights.

Each output is conditional on precisely 32 supplied (x, effect) observations and
the unrestricted 64-monomial GF(2) hypothesis space. No new source/evaluator
calls, previous scored outcomes, or native model modifications.
"""
from hashlib import sha256

MASKS=tuple(sorted(range(64),key=lambda m:(m.bit_count(),m)))
SCHEMA='wsp150.gf2.ambiguity.certificate.v1'

def _feature_row(x):
    return sum(1<<m for m in range(64) if (x&m)==m)

def predict(weights,x):
    if type(weights) is not int or not 0<=weights<(1<<64):
        raise ValueError('WSP150_INVALID_WEIGHTS')
    if type(x) is not int or not 0<=x<64:
        raise ValueError('WSP150_INVALID_CONTEXT')
    return (weights&_feature_row(x)).bit_count()&1

def _checked(rows,weights,x):
    if (type(rows) not in (tuple,list) or len(rows)!=32 or
        any(type(row) not in (tuple,list) or len(row)!=2 for row in rows)):
        raise ValueError('WSP150_REQUIRES_32_ROWS')
    if any(type(a) is not int or not 0<=a<64 or
           type(b) is not int or b not in (0,1) for a,b in rows):
        raise ValueError('WSP150_REQUIRES_BINARY_EFFECTS')
    if len({a for a,b in rows})!=32:
        raise ValueError('WSP150_REQUIRES_DISTINCT_CONTEXTS')
    predict(weights,x)
    if any(predict(weights,a)!=b for a,b in rows):
        raise ValueError('WSP150_MODEL_DOES_NOT_FIT_CHARGED_ROWS')
    return tuple((a,b) for a,b in rows)

def _flip_witness(rows,x):
    # Find a nonzero delta: phi(observed)*delta == 0, phi(x)*delta == 1.
    # Because the 64-ANF truth-table map is invertible, each distinct
    # new context raises row rank from 32 to 33.
    matrix=[[_feature_row(a),0] for a,b in rows]+[[_feature_row(x),1]]
    pivots=[];rank=0
    for mask in MASKS:
        k=next((j for j in range(rank,len(matrix)) if
                (matrix[j][0]>>mask)&1),None)
        if k is None:continue
        matrix[rank],matrix[k]=matrix[k],matrix[rank]
        for j in range(len(matrix)):
            if j!=rank and (matrix[j][0]>>mask)&1:
                matrix[j][0]^=matrix[rank][0]
                matrix[j][1]^=matrix[rank][1]
        pivots.append(mask);rank+=1
        if rank==len(matrix):break
    if rank!=33 or any(bits==0 and y for bits,y in matrix[rank:]):
        raise AssertionError('WSP150_FULL_ANF_IDENTIFIABILITY_DRIFT')
    delta=0
    for i in range(rank-1,-1,-1):
        if matrix[i][1]^((matrix[i][0]&delta).bit_count()&1):
            delta|=1<<pivots[i]
    if any(predict(delta,a)!=0 for a,b in rows) or predict(delta,x)!=1:
        raise AssertionError('WSP150_INVALID_NULLSPACE_WITNESS')
    return delta,rank

def certificate(rows,weights,x):
    rows=_checked(rows,weights,x)
    current=predict(weights,x)
    if x in {a for a,b in rows}:
        return {'schema':SCHEMA,'status':'OBSERVED','x':x,
                'observed_effect':current,'observed_rank':32}
    delta,rank=_flip_witness(rows,x)
    alternate=weights^delta
    cert={'schema':SCHEMA,'status':'UNIDENTIFIABLE','x':x,
          'reference_prediction':current,'witness_prediction':predict(alternate,x),
          'witness_weights':alternate,'witness_delta':delta,
          'observed_rank':32,'query_rank':rank}
    verify_certificate(rows,weights,x,cert)
    return cert

def verify_certificate(rows,weights,x,cert):
    rows=_checked(rows,weights,x)
    if type(cert) is not dict or cert.get('schema')!=SCHEMA or cert.get('x')!=x:
        raise ValueError('WSP150_INVALID_CERTIFICATE')
    observed=x in {a for a,b in rows}
    if observed:
        if set(cert)!={'schema','status','x','observed_effect','observed_rank'} or (
            cert['status']!='OBSERVED' or cert['observed_rank']!=32 or
            cert['observed_effect']!=predict(weights,x)):
            raise ValueError('WSP150_FALSE_OBSERVED_CERTIFICATE')
    else:
        expected={'schema','status','x','reference_prediction',
                  'witness_prediction','witness_weights','witness_delta',
                  'observed_rank','query_rank'}
        if set(cert)!=expected or cert['status']!='UNIDENTIFIABLE' or (
            cert['observed_rank']!=32 or cert['query_rank']!=33):
            raise ValueError('WSP150_FALSE_UNCERTAINTY_CERTIFICATE')
        w=cert['witness_weights'];d=cert['witness_delta']
        if (type(w) is not int or not 0<=w<(1<<64) or
            type(d) is not int or not 0<d<(1<<64) or w!=weights^d or
            cert['reference_prediction']!=predict(weights,x) or
            cert['witness_prediction']!=predict(w,x) or
            predict(w,x)==predict(weights,x) or
            any(predict(w,a)!=b for a,b in rows)):
            raise ValueError('WSP150_BAD_WITNESS')
    return True
