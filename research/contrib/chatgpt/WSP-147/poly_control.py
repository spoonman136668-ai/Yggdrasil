"""Independent algebraic normal form GF2 row reduction baseline.

No greedy weight programmer symbols shared, except public typed input rows.
Underdetermined systems resolve all free variables to 0; this is descriptive
same-information exact algebra, not a learned causal source oracle.
"""
from time import process_time_ns,perf_counter_ns

def fit(rows):
    if (type(rows) not in (list,tuple) or len(rows)!=32
        or len({x for x,y in rows})!=32
        or any(type(x) is not int or x not in range(64)
               or type(y) is not int or y not in (0,1) for x,y in rows)):
        raise ValueError('WSP147_POLYNOMIAL_NEEDS_32_REAL_EFFECTS')
    cpu=process_time_ns();wall=perf_counter_ns()
    A=[[sum(1<<m for m in range(64) if (x&m)==m),y] for x,y in rows]
    pivot=[]
    rank=0
    for mask in sorted(range(64),key=lambda m:(m.bit_count(),m)):
        found=next((i for i in range(rank,32) if (A[i][0]>>mask)&1),None)
        if found is None:continue
        A[rank],A[found]=A[found],A[rank]
        for i in range(32):
            if i!=rank and ((A[i][0]>>mask)&1):
                A[i][0]^=A[rank][0];A[i][1]^=A[rank][1]
        pivot.append(mask)
        rank+=1
        if rank==32:break
    inconsistent=any(bits==0 and val!=0 for bits,val in A[rank:])
    if inconsistent:raise AssertionError('WSP147_ALGEBRAIC_TRAIN_CONTRADICTION')
    coefficients=0
    for i in range(rank-1,-1,-1):
        mask=pivot[i]
        val=A[i][1]^((A[i][0]&coefficients).bit_count()&1)
        if val:coefficients|=1<<mask
    for x,y in rows:
        actual=sum((coefficients>>m)&1 for m in range(64) if (x&m)==m)&1
        if actual!=y:raise AssertionError('WSP147_INDEPENDENT_ANF_TRAIN_MISMATCH')
    return {'weights':coefficients,'rank':rank,
            'cpu_s':round((process_time_ns()-cpu)/1e9,6),
            'wall_s':round((perf_counter_ns()-wall)/1e9,6)}

def predict(model,x):
    if type(x) is not int or not 0<=x<64:raise ValueError('BAD_X')
    return sum((model['weights']>>m)&1 for m in range(64) if (x&m)==m)&1

def predictions(model):
    return tuple(predict(model,x) for x in range(64))
