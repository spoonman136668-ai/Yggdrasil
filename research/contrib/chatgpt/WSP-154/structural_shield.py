"""WSP154: source-free OOD structural ambiguity guard, experimental only.

No protected source, no native model weights, no accepted ref. Version-space
unanimity is conditional on the enumerated algebraic hypothesis class.
"""
from functools import reduce
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from json import dumps
from operator import xor
from pathlib import Path
from time import perf_counter_ns, process_time_ns
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("_wsp154_parent",ROOT/"WSP-153"/"sparse_operators.py")
P=module_from_spec(spec)
sys.modules[spec.name]=P
spec.loader.exec_module(P)

MONOMIALS=P.MONOMIALS+tuple(sum(1<<i for i in item)
                             for item in combinations(range(6),3))
assert len(MONOMIALS)==42 and len(set(MONOMIALS))==42
TERM_BITS=tuple(sum(1<<x for x in range(64) if (x&m)==m)
                for m in MONOMIALS)
CANDIDATES=tuple(reduce(xor,(TERM_BITS[j] for j in pick),0)
                 for k in range(4) for pick in combinations(range(42),k))
assert len(CANDIDATES)==12384 and len(set(CANDIDATES))==12384
ON=("AND2","OR2","XOR2","COMPOSE3")
OFF=("CUBIC3","CUBIC_XOR","PAIR_TRIPLE","ODD4","EXACT2OF4","QUAD4")
NAMESPACE="WSP154|FAKE|"

def digest(x):
    return sha256(dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate(rows):
    return P.validate(rows)

def survivors(rows):
    r=validate(rows)
    must1=sum(1<<x for x,y,_ in r if y)
    must0=sum(1<<x for x,y,_ in r if not y)
    return tuple(c for c in CANDIDATES
                 if c&must1==must1 and c&must0==0)

def fit(rows):
    r=validate(rows)
    remaining=survivors(r)
    return {"rows":r,"candidate_count":len(remaining),
            "predictions":P.readout_from_survivors(remaining)}

def symbolic_independent(rows):
    """Independent direct bit-by-bit GF(2) evaluation, not candidate cache."""
    r=validate(rows)
    basis=(0,)+tuple(1<<i for i in range(6))+tuple(
        (1<<i)|(1<<j) for i,j in combinations(range(6),2))+tuple(
        (1<<i)|(1<<j)|(1<<k) for i,j,k in combinations(range(6),3))
    good=[]
    for k in range(4):
        for combo in combinations(basis,k):
            if all((sum((x&m)==m for m in combo)&1)==y for x,y,_ in r):
                bits=0
                for x in range(64):
                    if sum((x&m)==m for m in combo)&1:
                        bits|=1<<x
                good.append(bits)
    return P.readout_from_survivors(good),len(good)

def _variables(i):
    return tuple(sorted(range(6),key=lambda k:(
        sha256((NAMESPACE+"VARS|"+str(i)+"|"+str(k)).encode()).digest(),k))[:5])

def effect(kind,vars_,x):
    v=tuple(int(bool(x&(1<<i))) for i in vars_)
    a,b,c,d,e=v
    if kind=="AND2":return a&b
    if kind=="OR2":return a|b
    if kind=="XOR2":return a^b
    if kind=="COMPOSE3":return a^(b&c)
    if kind=="CUBIC3":return a&b&c
    if kind=="CUBIC_XOR":return (a&b&c)^d
    if kind=="PAIR_TRIPLE":return (a&b)^(c&d&e)
    if kind=="ODD4":return a^b^c^d
    if kind=="EXACT2OF4":return int(a+b+c+d==2)
    if kind=="QUAD4":return a&b&c&d
    raise ValueError("WSP154_UNRECOGNIZED_FABRICATED_GENERATOR")

def collect(kind,variables):
    rows=tuple((x,effect(kind,variables,x),"observed_do")
               for x in P.WARM)
    for i in range(4):
        x=P.choose_next(rows)
        if x in {v for v,_,_ in rows}:
            raise AssertionError("WSP154_DUPLICATE_ACTION")
        rows+=((x,effect(kind,variables,x),"do"),)
    return rows

def alias_witness(observations,x):
    """An off-class one-hot perturbation matches all charged zero observations.

    This is a constructive impossibility witness, not a prediction algorithm.
    """
    seen={v for v,_,_ in validate(observations)}
    if x in seen:
        raise ValueError("WSP154_REQUIRES_UNCHARGED_COORDINATE")
    witness=1<<x
    assert all(not ((witness>>v)&1) for v in seen)
    # The coefficient of the degree-six ANF term is XOR of all 64 outputs.
    # Every original degree <=3 polynomial has coefficient 0, spike has 1.
    assert witness.bit_count()==1
    assert witness not in CANDIDATES
    return witness

def study():
    wall=perf_counter_ns();cpu=process_time_ns()
    keys=("sparse","guarded","symbolic","cart","wsp151")
    global_scores={name:{"on":{"right":0,"wrong":0,"abstain":0,"held":0},
                         "off":{"right":0,"wrong":0,"abstain":0,"held":0}}
                   for name in keys}
    worlds=[]
    for i in range(24):
        kind=ON[i%4] if i<12 else OFF[(i-12)%6]
        vars_=_variables(i)
        rows=collect(kind,vars_)
        old=P.fit(rows)
        new=fit(rows)
        sym,n=symbolic_independent(rows)
        if new["predictions"]!=sym or new["candidate_count"]!=n:
            raise AssertionError("WSP154_SYMBOLIC_PARITY")
        ctrls={
            "sparse":old["prediction"],
            "guarded":new["predictions"],
            "symbolic":sym,
            "cart":P.train_cart(rows),
            "wsp151":P.W151.readout(P.W151.fit(rows))}
        spent={x for x,_,_ in rows}
        held=tuple(x for x in range(64) if x not in spent)
        if len(held)!=56:
            raise AssertionError("WSP154_PAID_ACTION_COUNT")
        # Seal all complete readouts before evaluating a single held target.
        seals={name:digest(output) for name,output in ctrls.items()}
        group="on" if i<12 else "off"
        world={"world":i,"cohort":group,"actions":tuple(x for x,y,p in rows),
               "candidate_old":old["candidate_count"],
               "candidate_guarded":new["candidate_count"],
               "seals":seals,"scores":{}}
        for name,preds in ctrls.items():
            ok=wrong=abstain=0
            for x in held:
                predicted=preds[x]
                if predicted is None:abstain+=1
                elif predicted==effect(kind,vars_,x):ok+=1
                else:wrong+=1
            got={"right":ok,"wrong":wrong,"abstain":abstain,"held":56}
            world["scores"][name]=got
            total=global_scores[name][group]
            for k,v in got.items():total[k]+=v
        worlds.append(world)
    on=global_scores["guarded"]["on"]
    off=global_scores["guarded"]["off"]
    old_off=global_scores["sparse"]["off"]
    on_coverage_pct=100*(on["right"]+on["wrong"])/on["held"]
    off_wrong_pct=100*off["wrong"]/off["held"]
    off_reduction_pct=(100*(old_off["wrong"]-off["wrong"])/old_off["wrong"]
                       if old_off["wrong"] else 0)
    success=(off_wrong_pct<=2 and on_coverage_pct>=20 and
             off_reduction_pct>=50 and on["wrong"]==0)
    return {"classification":("SOURCEFREE_STRUCTURAL_SHIELD_DEVELOPMENT_SUPPORTED"
                              if success else
                              "SOURCEFREE_STRUCTURAL_SHIELD_DEVELOPMENT_NO_GO"),
            "on_coverage_pct":round(on_coverage_pct,6),
            "off_wrong_pct":round(off_wrong_pct,6),
            "off_wrong_reduction_pct":round(off_reduction_pct,6),
            "worlds":24,"on_worlds":12,"off_worlds":12,
            "scores":global_scores,
            "worlds_digest":digest(worlds),
            "science_pass":False,"original_first_use":False,
            "cpu_s":round((process_time_ns()-cpu)/1e9,4),
            "wall_s":round((perf_counter_ns()-wall)/1e9,4)}
