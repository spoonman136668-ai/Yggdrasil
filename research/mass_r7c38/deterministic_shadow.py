"""Independent C38 exact-rational FIT-only reference. No MiniGrid import or execution."""
from fractions import Fraction
import hashlib,json,math,time
SCHEMA="itd02.c38.fit-only.exact-rational-shadow-v1"
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(v):return hashlib.sha256(canonical(v)).hexdigest()
def rational(v):
    if type(v) not in (float,int) or not math.isfinite(v):
        raise ValueError("SHADOW_NONFINITE_OR_UNTYPED_NUMBER")
    return Fraction(*float(v).as_integer_ratio())
def solve(a,b):
    n=len(b)
    if not n or len(a)!=n or any(len(r)!=n for r in a):
        raise ValueError("SHADOW_SQUARE_LINEAR_SYSTEM_REQUIRED")
    u=[list(r)+[b[i]] for i,r in enumerate(a)]
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(u[i][k]))
        if u[pivot][k]==0:raise ValueError("SHADOW_SINGULAR_FIT_SYSTEM")
        if pivot!=k:u[k],u[pivot]=u[pivot],u[k]
        denominator=u[k][k]
        for i in range(k+1,n):
            if u[i][k]==0:continue
            ratio=u[i][k]/denominator
            u[i][k]=Fraction(0)
            for j in range(k+1,n+1):u[i][j]-=ratio*u[k][j]
    values=[Fraction(0)]*n
    for k in range(n-1,-1,-1):
        values[k]=(u[k][n]-sum((u[k][j]*values[j] for j in range(k+1,n)),Fraction(0)))/u[k][k]
    return values
def shadow_fit(rows,labels,penalty,max_dim=32,max_rows=8192):
    t0=time.process_time()
    if not isinstance(rows,(list,tuple)) or not rows or len(rows)>max_rows or len(labels)!=len(rows):
        raise ValueError("SHADOW_ROW_BUDGET_OR_LENGTH")
    n=len(rows[0])
    if not 1<=n<=max_dim or any(len(row)!=n for row in rows):
        raise ValueError("SHADOW_FEATURE_DIMENSION")
    x=[[rational(v) for v in row] for row in rows]
    y=[rational(v) for v in labels]
    reg=rational(penalty)
    if reg<=0:raise ValueError("SHADOW_POSITIVE_REGULARIZATION_REQUIRED")
    a=[[Fraction(0) for _ in range(n)] for _ in range(n)]
    b=[Fraction(0) for _ in range(n)]
    for xx,yy in zip(x,y):
        for i,vi in enumerate(xx):
            b[i]+=vi*yy
            for j in range(i,n):a[i][j]+=vi*xx[j]
    for i in range(n):
        for j in range(i):a[i][j]=a[j][i]
        if i:a[i][i]+=reg
    answer=solve(a,b)
    if any(sum((a[i][j]*answer[j] for j in range(n)),Fraction(0))!=b[i] for i in range(n)):
        raise ValueError("SHADOW_EXACT_RESIDUAL")
    coeff=[float(v) for v in answer]
    if not all(math.isfinite(z) for z in coeff):raise ValueError("SHADOW_NONFINITE_MODEL")
    size=max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in answer)
    if size>200000:raise ValueError("SHADOW_RATIONAL_RESOURCE_BUDGET")
    return {"schema":SCHEMA,"exact_binary64_input":True,"fit_rows":len(rows),
       "feature_dimensions":n,"shadow_coefficients":coeff,
       "shadow_coefficients_sha256":sha(coeff),"exact_regularizer":str(reg),
       "largest_exact_coeff_numerator_denominator_bit_length":size,
       "runtime_shadow_fit_cpu_seconds":time.process_time()-t0,
       "original_C36_model_modified":False,"real_original_world_steps_in_shadow":0,
       "scientific_go":False}
def compare_models(original,reference,rows,tol=1e-10):
    """Only three original C36 candidate pairs are scored, not all nine C35 forks."""
    if len(original)!=len(reference["shadow_coefficients"]):
        raise ValueError("SHADOW_ORIGINAL_C36_FEATURE_SIZE_DRIFT")
    w=reference["shadow_coefficients"]
    if any(type(z) not in (float,int) or not math.isfinite(z) for z in original):
        raise ValueError("SHADOW_UNTRUSTED_ORIGINAL_WEIGHTS")
    if len(rows)%3:raise ValueError("SHADOW_INCOMPLETE_THREE_ORIGINAL_C36_FIT_OPTIONS")
    diffs=[float(a)-float(b) for a,b in zip(original,w)]
    flips=0;ties=0
    for i in range(0,len(rows),3):
        chunk=rows[i:i+3]
        old=[sum(v*x for v,x in zip(r,original)) for r in chunk]
        new=[sum(v*x for v,x in zip(r,w)) for r in chunk]
        flips+=old.index(max(old))!=new.index(max(new))
        ties+=sum(abs(v-max(new))<=tol for v in new)>1
    return {"comparison":"ORIGINAL_C36_VS_EXACT_SHADOW_FIT_ONLY_NOT_POLICY_ACCEPTANCE",
       "max_absolute_coeff_delta":max(map(abs,diffs)),
       "l2_coeff_delta":math.sqrt(sum(v*v for v in diffs)),
       "original_source_FIT_anchor_count":len(rows)//3,
       "original_source_FIT_three_candidate_rank_flip_count":flips,
       "shadow_near_tie_FIT_anchor_count":ties,
       "source_family_transfer":"NOT_TESTED","new_original_source_steps":0}
