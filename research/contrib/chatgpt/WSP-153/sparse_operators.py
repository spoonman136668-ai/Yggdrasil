"""WSP153: source-free, sparse GF(2) causal-operator version space.

Pure fabricated development, no protected first use, no token model, no native
Yggdrasil weight mutation. Certainty is CONDITIONAL on the exact sparse class.
"""
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from itertools import combinations
from json import dumps
from pathlib import Path
from time import perf_counter_ns,process_time_ns
import importlib.util
import sys

FULL=(1<<64)-1
MONOMIALS=(0,1,2,4,8,16,32)+tuple((1<<i)|(1<<j)
                                    for i in range(6) for j in range(i+1,6))
assert len(MONOMIALS)==22 and len(set(MONOMIALS))==22
TERM_BITS=tuple(sum((1<<x) for x in range(64) if (x&m)==m)
                for m in MONOMIALS)
COEFFS=tuple(combo for k in range(4)
             for combo in combinations(range(len(MONOMIALS)),k))
CANDIDATES=tuple(reduce(int.__xor__,(TERM_BITS[i] for i in combo),0)
                 for combo in COEFFS)
assert len(CANDIDATES)==1794

ROOT=Path(__file__).resolve().parents[1]
_parent=importlib.util.spec_from_file_location("_wsp153_parent",
                                              ROOT/"WSP-151"/"overhypothesis.py")
W151=importlib.util.module_from_spec(_parent)
sys.modules[_parent.name]=W151
_parent.loader.exec_module(W151)

def digest(obj):
    return sha256(dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate(rows):
    return W151.validate_rows(rows)

def survivors(rows):
    r=validate(rows)
    return tuple(bits for bits in CANDIDATES
                 if all(((bits>>x)&1)==y for x,y,_ in r))

def readout_from_survivors(cands):
    if not cands:return (None,)*64
    all_ones=FULL
    any_ones=0
    for bits in cands:
        all_ones&=bits
        any_ones|=bits
    return tuple(1 if (all_ones>>x)&1 else
                 (0 if not (any_ones>>x)&1 else None)
                 for x in range(64))

def fit(rows):
    r=validate(rows)
    c=survivors(r)
    return {"rows":r,"candidate_count":len(c),"candidates":c,
            "prediction":readout_from_survivors(c)}

def choose_next(rows):
    r=validate(rows)
    if len(r)>=8:raise ValueError("WSP153_CHARGED_BUDGET_EXHAUSTED")
    c=survivors(r)
    taken={x for x,_,_ in r}
    # If all hypotheses are excluded, complete the fixed action budget
    # with deterministic uncharged actions; never guess a prediction.
    if not c:
        return min(x for x in range(64) if x not in taken)
    best=-1
    xbest=None
    for x in range(64):
        if x in taken:continue
        num1=sum((bits>>x)&1 for bits in c)
        split=min(num1,len(c)-num1)
        if split>best:
            best=split
            xbest=x
    assert xbest is not None
    return xbest

def exact_symbolic_independent(rows):
    """Independent truth-table reconstruction, not CANDIDATES or TERM_BITS."""
    r=validate(rows)
    terms=[0]+[1<<i for i in range(6)]+[(1<<i)|(1<<j)
                                         for i in range(6) for j in range(i+1,6)]
    viable=[]
    for k in (0,1,2,3):
        for choice in combinations(terms,k):
            if all((sum(int((x&term)==term) for term in choice)%2)==y
                   for x,y,_ in r):
                bits=0
                for x in range(64):
                    if sum(int((x&term)==term) for term in choice)%2:
                        bits|=1<<x
                viable.append(bits)
    if not viable:return (None,)*64,0
    results=[]
    for x in range(64):
        observed={(bits>>x)&1 for bits in viable}
        results.append(next(iter(observed)) if len(observed)==1 else None)
    return tuple(results),len(viable)

def train_cart(rows):
    """Fully fitted deterministic binary CART with six available features."""
    r=validate(rows)
    def node(items,features):
        n0=sum(y==0 for x,y,_ in items)
        n1=len(items)-n0
        base=Fraction(2*n0*n1,len(items))
        majority=1 if n1>n0 else 0
        if not n0 or not n1 or not features:return ("leaf",majority)
        # Continue through zero-gain splits to allow full supervised
        # fitting of XOR-like interactions, not a weak stump control.
        chosen=None;score=None
        for feature in features:
            left=tuple(v for v in items if not (v[0]&(1<<feature)))
            right=tuple(v for v in items if v not in left)
            if not left or not right:continue
            def impurity(vals):
                a=sum(v[1]==0 for v in vals)
                b=len(vals)-a
                return Fraction(2*a*b,len(vals))
            proposed=impurity(left)+impurity(right)
            if score is None or proposed<score:
                chosen=(feature,left,right)
                score=proposed
        if chosen is None:return ("leaf",majority)
        feature,left,right=chosen
        keep=tuple(f for f in features if f!=feature)
        return ("node",feature,node(left,keep),node(right,keep))
    tree=node(r,tuple(range(6)))
    def read(x,t):
        if t[0]=="leaf":return t[1]
        return read(x,t[3] if x&(1<<t[1]) else t[2])
    return tuple(read(x,tree) for x in range(64))

WARM=(1,2,4,8)
POLICIES=("fixed","active")

def _effect(form,variables,x):
    v=tuple(int(bool(x&(1<<i))) for i in variables)
    if form=="AND2":return v[0]&v[1]
    if form=="XOR2":return v[0]^v[1]
    if form=="OR2":return v[0]|v[1]
    if form=="COMPOSE3":return v[0]^(v[1]&v[2])
    if form=="CUBIC3":return v[0]&v[1]&v[2]
    if form=="CUBIC_XOR":return (v[0]&v[1]&v[2])^v[3]
    if form=="ODD4":return v[0]^v[1]^v[2]^v[3]
    if form=="EXACT2OF4":return int(sum(v[:4])==2)
    raise ValueError("WSP153_UNKNOWN_FABRICATED_FORM")

def _variables(i):
    ranking=sorted(range(6),key=lambda k:
                   (sha256(("WSP153|FAKE|VARS|"+str(i)+"|"+str(k)).encode()).digest(),k))
    return tuple(ranking[:4])

def _fixed_tail():
    return tuple(sorted((x for x in range(64) if x not in WARM),
        key=lambda x:(sha256(("WSP153|FAKE|FIXED|"+str(x)).encode()).digest(),x))[:4])

def collect(form,vs,policy):
    rows=tuple((x,_effect(form,vs,x),"observed_do") for x in WARM)
    for k in range(4):
        x=_fixed_tail()[k] if policy=="fixed" else choose_next(rows)
        if x in {a for a,_,_ in rows}:raise AssertionError("WSP153_DUPLICATE_ACTION")
        # The effect is revealed ONLY after the policy selects this do action.
        rows=rows+((x,_effect(form,vs,x),"do"),)
    return rows

def fabricated_study():
    wall=perf_counter_ns();cpu=process_time_ns()
    all_worlds=[]
    on_kinds=("AND2","OR2","XOR2","COMPOSE3")
    off_kinds=("CUBIC3","CUBIC_XOR","ODD4","EXACT2OF4")
    scores={p:{"correct":0,"wrong":0,"abstain":0,"held":0} for p in
            ("fixed","active","symbolic","cart","wsp151")}
    on_scores={p:{"correct":0,"wrong":0,"abstain":0,"held":0} for p in scores}
    off_scores={p:{"correct":0,"wrong":0,"abstain":0,"held":0} for p in scores}
    for i in range(20):
        form=on_kinds[i%4] if i<16 else off_kinds[i-16]
        vs=_variables(i)
        r_fixed=collect(form,vs,"fixed")
        r_active=collect(form,vs,"active")
        f=fit(r_fixed);a=fit(r_active)
        symbolic,sym_count=exact_symbolic_independent(r_active)
        if a["prediction"]!=symbolic or a["candidate_count"]!=sym_count:
            raise AssertionError("WSP153_INDEPENDENT_SYMBOLIC_PARITY_FAIL")
        tree=train_cart(r_active)
        parent=W151.readout(W151.fit(r_active))
        outputs={"fixed":f["prediction"],"active":a["prediction"],
                 "symbolic":symbolic,"cart":tree,"wsp151":parent}
        spent=set(x for x,_,_ in r_fixed)|set(x for x,_,_ in r_active)
        held=tuple(x for x in range(64) if x not in spent)
        if len(held)<48:raise AssertionError("WSP153_SHARED_HELD_LT48")
        world={"index":i,"form":form,"group":"ON" if i<16 else "OFF",
               "charged":{ "fixed":tuple(x for x,_,_ in r_fixed),
                           "active":tuple(x for x,_,_ in r_active)},
               "held":len(held),"active_remaining":a["candidate_count"],
               "fixed_remaining":f["candidate_count"],"pred_seals":{
                 p:digest(o) for p,o in outputs.items()},
               "score":{}}
        for p,pred in outputs.items():
            correct=wrong=abstain=0
            # All policies and controls have sealed predictions before truth
            # is computed for ANY held context.
            for x in held:
                v=pred[x]
                if v is None:abstain+=1
                elif v==_effect(form,vs,x):correct+=1
                else:wrong+=1
            vals={"correct":correct,"wrong":wrong,
                  "abstain":abstain,"held":len(held)}
            world["score"][p]=vals
            for group in (scores,on_scores if i<16 else off_scores):
                for k,v in vals.items():group[p][k]+=v
        all_worlds.append(world)
    eligible=on_scores["active"]
    on_held=eligible["held"]
    strongest=max(on_scores["cart"]["correct"],on_scores["wsp151"]["correct"])
    pp_gain=100*(eligible["correct"]-strongest)/on_held
    offwrong=100*off_scores["active"]["wrong"]/off_scores["active"]["held"]
    coverage=100*(eligible["correct"]+eligible["wrong"])/on_held
    parity=all(w["score"]["active"]==w["score"]["symbolic"] for w in all_worlds)
    if not parity:raise AssertionError("WSP153_SYMBOLIC_SCORE_MISMATCH")
    passed=(eligible["wrong"]==0 and coverage>=30 and pp_gain>=5 and
            offwrong<=2 and parity)
    return {
        "classification":"SOURCEFREE_SPARSE_OPERATOR_DEVELOPMENT_SUPPORTED"
             if passed else "SOURCEFREE_SPARSE_OPERATOR_DEVELOPMENT_NO_GO",
        "scientific_pass":False,"first_use":False,"worlds":20,
        "on_worlds":16,"off_worlds":4,"on_held":on_held,
        "active_on_coverage_pct":round(coverage,6),
        "gain_pp_vs_strongest_same_action_control":round(pp_gain,6),
        "active_on_wrong":eligible["wrong"],"active_off_wrong_pct":round(offwrong,6),
        "symbolic_parity":parity,
        "scores":scores,"on_scores":on_scores,"off_scores":off_scores,
        "receipt_sha256":digest(all_worlds),
        "cpu_s":round((process_time_ns()-cpu)/1e9,5),
        "wall_s":round((perf_counter_ns()-wall)/1e9,5)
    }
