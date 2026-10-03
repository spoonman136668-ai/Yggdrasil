"""EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-FACTORIAL-ATTRIBUTION-040."""
import argparse, importlib.util, json, math
from pathlib import Path

E="EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-FACTORIAL-ATTRIBUTION-040"
P=Path("research/applications/plane/exp-dgr-external-cumulative-multirow-novel-interference-attribution-039.py")

def load_prior():
    s=importlib.util.spec_from_file_location("ygg039",P)
    if s is None or s.loader is None:
        raise RuntimeError("PRIOR_IMPORT_FAILED")
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def run(root):
    prior=load_prior()
    base=prior.run(root)
    m=dict(base["metrics"])
    m.update({
        "failure_order0_count":0.0,
        "failure_order1_count":0.0,
        "failure_pair_AB_count":0.0,
        "failure_pair_AC_count":0.0,
        "failure_pair_BC_count":0.0,
        "minimum_failures_per_schedule":36.0,
        "maximum_failures_per_schedule":0.0,
        "factorial_accounting_error_count":0.0,
    })
    per_schedule=[0]*6
    seen=0
    for d in base["diagnostics"]:
        seen+=1
        si=int(d["schedule_index"])
        oi=int(d["target_order_index"])
        pair="".join(d["target_pair"])
        if si<0 or si>=6 or oi not in (0,1) or pair not in ("AB","AC","BC"):
            m["factorial_accounting_error_count"]+=1.0
            continue
        if not d["safety_failure"]:
            continue
        per_schedule[si]+=1
        m[f"failure_order{oi}_count"]+=1.0
        m[f"failure_pair_{pair}_count"]+=1.0
    if seen!=36 or m["safety_case_count"]!=36:
        m["factorial_accounting_error_count"]+=1.0
    m["minimum_failures_per_schedule"]=float(min(per_schedule))
    m["maximum_failures_per_schedule"]=float(max(per_schedule))
    if m["failure_order0_count"]+m["failure_order1_count"]!=m["non_target_safety_failure_count"]:
        m["factorial_accounting_error_count"]+=1.0
    if m["failure_pair_AB_count"]+m["failure_pair_AC_count"]+m["failure_pair_BC_count"]!=m["non_target_safety_failure_count"]:
        m["factorial_accounting_error_count"]+=1.0
    if sum(per_schedule)!=m["non_target_safety_failure_count"]:
        m["factorial_accounting_error_count"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":E,
        "metrics":m,
        "first_failure":base.get("first_failure"),
        "diagnostics":base["diagnostics"],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":
    main()
