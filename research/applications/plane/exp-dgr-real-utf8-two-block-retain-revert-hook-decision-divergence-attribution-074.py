"""Read-only attribution of inherited versus row-local gate decisions."""
import argparse, hashlib, importlib.util, json, math, sys
from collections import Counter
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-DECISION-DIVERGENCE-ATTRIBUTION-074"
P044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
P043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
P029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRESSURE = Path("research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py")
ERROR = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
SEALED = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-CALL-ROLE-ATTRIBUTION-073-38827378772/result.json")
NORTH = Path("research/architecture/yggdrasil-north-star.ice")
IDENTITIES = ((P044,"cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"),(P043,"5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"),(P029,"e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"),(PRESSURE,"0144922b4191abb451e821f5b4ab14885e1de11272c5d625c3963d1cffdbfeb9"),(ERROR,"5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"),(SEALED,"30d382889990d80dce17069aece3141a9fba23b09a962e15b979938c98f6d45a"),(NORTH,"57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"))
DIRECT = {303:"evaluation_frozen",306:"evaluation_independent",309:"evaluation_pooled",312:"evaluation_minimax",330:"cue_frozen",333:"cue_minimax",337:"check_frozen",340:"check_minimax"}
AUX = {39:"model_fraction_full",40:"model_fraction_active"}

def norm(value): return str(value).replace("\\", "/")
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("IMPORT_SPEC_FAILED")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def schedule(orders): return [(oi,si,name) for oi,order in enumerate(orders) for si in range(1,4) for name in order[:si]]

def run():
    if any(digest(path)!=expected for path,expected in IDENTITIES): raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed=json.loads(SEALED.read_text(encoding="utf-8"))
    if sealed.get("experiment")!="EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-CALL-ROLE-ATTRIBUTION-073": raise RuntimeError("SEALED_EXPERIMENT_MISMATCH")
    p044,p043,clean=load(P044,"p044_decisions_074"),load(P043,"p043_decisions_074"),load(PRESSURE,"pressure_clean_074")
    p043.ORDERS,p043.DEMAND_FILES=p044.ORDERS,p044.DEMAND_FILES
    orders=tuple(tuple(order) for order in p044.ORDERS); scheduled=schedule(orders); scheduled_set=set(scheduled)
    rows,current,calls=[],None,[]
    def close():
        nonlocal current
        if current is not None: rows.append(current); current=None
    def trace(frame,event,_arg):
        nonlocal current
        filename=norm(frame.f_code.co_filename)
        if event=="line" and filename.endswith(norm(P029)) and frame.f_lineno==302:
            close()
            try: key=(orders.index(tuple(frame.f_locals.get("order",()))),len(tuple(frame.f_locals.get("seen",()))),frame.f_locals.get("name"))
            except ValueError: key=None
            current={"key":key,"cue_frozen":[],"cue_minimax":[],"decision_roles":[]}
        elif event=="call" and frame.f_code.co_name=="gated_counts" and filename.endswith(norm(P043)):
            caller=frame.f_back; caller_file=norm(caller.f_code.co_filename) if caller else ""; line=caller.f_lineno if caller else -1
            role=DIRECT.get(line) if caller_file.endswith(norm(P029)) else AUX.get(line) if caller_file.endswith(norm(ERROR)) else None
            offset=len(calls)%10; calls.append(role)
            if current is not None and role in ("cue_frozen","cue_minimax"):
                current[role].append((frame.f_locals.get("prior"),frame.f_locals.get("data"),frame.f_locals.get("baseline"),frame.f_locals.get("learned")))
            if current is not None and offset==5: current["decision_roles"].append(role)
        elif event=="return" and filename.endswith(norm(P029)) and frame.f_code.co_name=="run": close()
        return trace
    old_trace=sys.gettrace(); sys.settrace(trace)
    try: gated,_wrapped,blocks=p043.gated_run()
    finally: sys.settrace(old_trace)
    old=gated["metrics"]; controls=("training_file_identity_mismatch_count","evaluation_file_identity_mismatch_count","future_stage_adaptation_access_count","second_half_adaptation_access_count","valid_stage_count","valid_seen_domain_evaluation_count","matched_assignment_failure_count","capacity_growth_event_count","retained_record_integrity_mismatch_count","state_partition_mismatch_count")
    metrics={name:old[name] for name in controls}; known=[row for row in rows if row["key"] in scheduled_set]; counts=Counter(row["key"] for row in known); by_key={row["key"]:row for row in known}; indices={key:i for i,key in enumerate(scheduled)}
    inherited={key:bool(block[2]) for key,block in zip(scheduled,blocks)}; counterfactual={}; empty_blocks=0
    for key,row in by_key.items():
        if len(row["cue_frozen"])!=1 or len(row["cue_minimax"])!=1: continue
        prior,data,baseline,frozen=row["cue_frozen"][0]; p2,data2,baseline2,minimax=row["cue_minimax"][0]
        midpoint=len(data)//2; early,late=data[:midpoint],data[midpoint:]
        empty_blocks+=int(not early)+int(not late)
        if prior is not p2 or data!=data2 or baseline!=baseline2: continue
        early_frozen=clean.model_correct_counts(prior,early,baseline,frozen)[1]; early_minimax=clean.model_correct_counts(prior,early,baseline,minimax)[1]
        late_frozen=clean.model_correct_counts(prior,late,baseline,frozen)[1]; late_minimax=clean.model_correct_counts(prior,late,baseline,minimax)[1]
        counterfactual[key]=(early_minimax-early_frozen>=0 and late_minimax-late_frozen>=0)
    divergence={key for key in scheduled_set if key in inherited and key in counterfactual and inherited[key]!=counterfactual[key]}; aligned_mask=127; aligned={key for key,i in indices.items() if aligned_mask&(1<<i)}; drifted=scheduled_set-aligned
    mask=lambda members: sum(1<<indices[key] for key in members); decision_roles={key:row["decision_roles"][0] for key,row in by_key.items() if len(row["decision_roles"])==1}
    sm=sealed["metrics"]; aligned_role=mask({key for key,role in decision_roles.items() if role=="cue_minimax"}); check_role=mask({key for key,role in decision_roles.items() if role=="check_minimax"}); model_role=mask({key for key,role in decision_roles.items() if role=="model_fraction_active"})
    metrics.update({"inherited_decision_count":float(len(inherited)),"counterfactual_decision_count":float(len(counterfactual)),"inherited_retain_count":float(sum(inherited.values())),"counterfactual_retain_count":float(sum(counterfactual.values())),"decision_divergence_count":float(len(divergence)),"aligned_row_divergence_count":float(len(divergence&aligned)),"drifted_row_divergence_count":float(len(divergence&drifted)),"missing_counterfactual_row_count":float(len(scheduled_set-set(counterfactual))),"duplicate_counterfactual_row_count":float(sum(n-1 for n in counts.values() if n>1)),"decision_accounting_mismatch_count":float(len(calls)!=116 or len(rows)!=12 or len(blocks)!=12 or empty_blocks!=0 or any(n!=1 for n in counts.values())),"sealed073_role_reproduction_mismatch_count":float(aligned_role!=sm["aligned_decision_row_mask"] or check_role!=sm["check_decision_row_mask"] or model_role!=sm["model_fraction_decision_row_mask"]),"inherited_retain_row_mask":float(mask({key for key,value in inherited.items() if value})),"counterfactual_retain_row_mask":float(mask({key for key,value in counterfactual.items() if value})),"decision_divergence_row_mask":float(mask(divergence))})
    if not all(isinstance(value,(int,float)) and math.isfinite(value) for value in metrics.values()): raise RuntimeError("NONFINITE_METRIC")
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))
if __name__=="__main__": main()
