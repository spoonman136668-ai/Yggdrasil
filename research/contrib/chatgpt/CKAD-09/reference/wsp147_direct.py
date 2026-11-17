"""WSP147: source-blind gradient-free direct numerical weight programming.

64-bit GF(2) ANF crossbar, 16 strictly improving one-coordinate edits.
This is a NEW source-independent numerical learner. No oracle, new grammar
operator, future-question coordinates, gradient, or symbolic fit in its path.
"""
from hashlib import sha256
from time import perf_counter_ns,process_time_ns
MASKS=tuple(range(64))
MAX_EDITS=16

def _validate(rows):
    if (type(rows) not in (tuple,list) or len(rows)!=32
        or len({x for x,y in rows})!=32
        or any(type(x) is not int or not 0<=x<64 or type(y) is not int
               or y not in (0,1) for x,y in rows)):
        raise ValueError('WSP147_EXACT_32_CHARGED_EFFECTS_REQUIRED')
    return tuple(rows)

def signature(mask,xs):
    return sum(int((x&mask)==mask)<<i for i,x in enumerate(xs))

def program_weights(rows):
    rows=_validate(rows)
    xs=tuple(x for x,y in rows)
    residual=sum(y<<i for i,(x,y) in enumerate(rows))
    masks=tuple(signature(m,xs) for m in MASKS)
    weights=0
    writes=[]
    cpu=process_time_ns();wall=perf_counter_ns()
    for _ in range(MAX_EDITS):
        best=None
        bestkey=None
        for mask,sign in enumerate(masks):
            gain=2*(residual&sign).bit_count()-sign.bit_count()
            if gain<=0:continue
            candidate=(-gain,mask.bit_count(),mask)
            if bestkey is None or candidate<bestkey:
                bestkey=candidate;best=mask
        if best is None:break
        residual^=masks[best]
        weights^=1<<best
        writes.append(best)
    return {
      'weights':weights,'writes':tuple(writes),'residual_errors':residual.bit_count(),
      'has_exact_fit':residual==0,
      'cpu_s':round((process_time_ns()-cpu)/1e9,6),
      'wall_s':round((perf_counter_ns()-wall)/1e9,6),
      'source_rows_digest':sha256(repr(rows).encode()).hexdigest(),
    }

def predict(model,x):
    if type(x) is not int or not 0<=x<64:raise ValueError('BAD_INTERVENTION_X')
    if not model['has_exact_fit']:return None
    return sum((model['weights']>>m)&1 for m in MASKS if (x&m)==m)&1

def predictions(model):
    return tuple(predict(model,x) for x in range(64))

def restore(saved,rows):
    verified=program_weights(rows)
    for k in ('weights','writes','residual_errors','has_exact_fit','source_rows_digest'):
        if saved.get(k)!=verified.get(k):
            raise ValueError('WSP147_COLD_WEIGHT_RESTORE_MISMATCH')
    return verified
