"""Exact, source-free, nonadaptive allocation bounds for two public probes."""
import argparse
import json
from fractions import Fraction as F
from math import comb

BUDGET = 32
CASES = {"STRONG": (F(1,4), F(3,4)), "MODERATE": (F(2,5), F(3,5)),
         "WEAK": (F(9,20), F(11,20)), "RARE": (F(0), F(1,64)),
         "NULL": (F(1,2), F(1,2))}

def risk(n, p, q):
    if type(n) is not int or n < 0: raise ValueError("invalid count")
    if type(p) is not F or type(q) is not F: raise TypeError("exact fractions required")
    if not (0 <= p <= 1 and 0 <= q <= 1): raise ValueError("invalid probability")
    return sum((min(comb(n,k)*p**k*(1-p)**(n-k),
                    comb(n,k)*q**k*(1-q)**(n-k))
                for k in range(n+1)), F(0))/2

def allocation(n0, n1, p, q):
    if type(n0) is not int or type(n1) is not int or min(n0,n1)<0 or n0+n1!=BUDGET:
        raise ValueError("fixed allocation must use exactly 32 probes")
    return max(risk(n0,p,q),risk(n1,p,q))

def minimax(p,q):
    options=[(allocation(n,BUDGET-n,p,q),abs(2*n-BUDGET),n)
             for n in range(BUDGET+1)]
    err,_,n=min(options)
    return {"allocation":[n,BUDGET-n],"worst_risk":err,
            "known_address_risk":risk(BUDGET,p,q),
            "one_address_worst":allocation(BUDGET,0,p,q),
            "enumerated_allocations":len(options)}

def as_json(x):
    return {"numerator":x.numerator,"denominator":x.denominator,
            "decimal_approx":f"{float(x):.12f}"}

def audit():
    results={}
    for label,(p,q) in CASES.items():
        d=minimax(p,q)
        results[label]={"allocation":d["allocation"],
                        "minimax_ideal_error":as_json(d["worst_risk"]),
                        "known_address_ideal_error":as_json(d["known_address_risk"]),
                        "one_address_worst_error":as_json(d["one_address_worst"]),
                        "allocation_count":d["enumerated_allocations"],
                        "passes_advisory_five_percent":d["worst_risk"]<=F(1,20)}
    return {"schema":"mass.r10.action-address-screen.v1",
            "budget":BUDGET,"cases":results,"fixed_nonadaptive_only":True,
            "likelihoods_and_active_address_known_to_ideal_inference":True,
            "sampled_rows":0,"source_generator_created":False,
            "scientific_first_use":False,
            "actual_r10_source_certificate":"NOT_ESTABLISHED",
            "ckb_admission":"NOT_OBSERVED"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--audit",action="store_true",required=True)
    ap.parse_args()
    print(json.dumps(audit(),sort_keys=True,indent=2))
