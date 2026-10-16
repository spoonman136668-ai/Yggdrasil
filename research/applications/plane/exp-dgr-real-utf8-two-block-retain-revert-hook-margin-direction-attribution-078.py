"""Read-only directional attribution of gate-margin differences."""
import argparse, hashlib, importlib.util, json, math, sys
from collections import Counter
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-DIRECTION-ATTRIBUTION-078"
P044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
P043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
P029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRESSURE = Path("research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py")
ERROR = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
P077 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-role-attribution-077.py")
SEALED = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-ROLE-ATTRIBUTION-077-38833999147/result.json")
NORTH = Path("research/architecture/yggdrasil-north-star.ice")
IDENTITIES = ((P044,"cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"),(P043,"5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"),(P029,"e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"),(PRESSURE,"0144922b4191abb451e821f5b4ab14885e1de11272c5d625c3963d1cffdbfeb9"),(ERROR,"5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"),(P077,"e00ebb0f06ecc8d0b7f7a565e4ab397f2882eff1df350693dfa55b8dc2d98d47"),(SEALED,"71eff907b74cbec49ab20ef06374303f9b0f29237f6dde9243628233167ab127"),(NORTH,"57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"))

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
    if sealed.get("experiment")!="EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-ROLE-ATTRIBUTION-077": raise RuntimeError("SEALED_EXPERIMENT_MISMATCH")
    p044,p043,clean=load(P044,"p044_margin_direction_078"),load(P043,"p043_margin_direction_078"),load(PRESSURE,"pressure_clean_078")
    p043.ORDERS,p043.DEMAND_FILES=p044.ORDERS,p044.DEMAND_FILES
    orders=tuple(tuple(order) for order in p044.ORDERS); scheduled=schedule(orders); scheduled_set=set(scheduled)
    rows,current=[],None
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
            current={"key":key,"cue_frozen":[],"cue_minimax":[]}
        elif event=="call" and frame.f_code.co_name=="gated_counts" and filename.endswith(norm(P043)):
            caller=frame.f_back; caller_file=norm(caller.f_code.co_filename) if caller else ""; line=caller.f_lineno if caller else -1
            role="cue_frozen" if caller_file.endswith(norm(P029)) and line==330 else "cue_minimax" if caller_file.endswith(norm(P029)) and line==333 else None
            if current is not None and role: current[role].append((frame.f_locals.get("prior"),frame.f_locals.get("data"),frame.f_locals.get("baseline"),frame.f_locals.get("learned")))
        elif event=="return" and filename.endswith(norm(P029)) and frame.f_code.co_name=="run": close()
        return trace
    old_trace=sys.gettrace(); sys.settrace(trace)
    try: gated,_wrapped,blocks=p043.gated_run()
    finally: sys.settrace(old_trace)
    old=gated["metrics"]; controls=("training_file_identity_mismatch_count","evaluation_file_identity_mismatch_count","future_stage_adaptation_access_count","second_half_adaptation_access_count","valid_stage_count","valid_seen_domain_evaluation_count","matched_assignment_failure_count","capacity_growth_event_count","retained_record_integrity_mismatch_count","state_partition_mismatch_count")
    metrics={name:old[name] for name in controls}; known=[row for row in rows if row["key"] in scheduled_set]; counts=Counter(row["key"] for row in known); by_key={row["key"]:row for row in known}; indices={key:i for i,key in enumerate(scheduled)}
    inherited={key:(block[0],block[1]) for key,block in zip(scheduled,blocks)}; counterfactual={}; empty_blocks=0
    for key,row in by_key.items():
        if len(row["cue_frozen"])!=1 or len(row["cue_minimax"])!=1: continue
        prior,data,baseline,frozen=row["cue_frozen"][0]; p2,data2,baseline2,minimax=row["cue_minimax"][0]
        midpoint=len(data)//2; early,late=data[:midpoint],data[midpoint:]; empty_blocks+=int(not early)+int(not late)
        if prior is not p2 or data!=data2 or baseline!=baseline2: continue
        early_frozen=clean.model_correct_counts(prior,early,baseline,frozen)[1]; early_minimax=clean.model_correct_counts(prior,early,baseline,minimax)[1]
        late_frozen=clean.model_correct_counts(prior,late,baseline,frozen)[1]; late_minimax=clean.model_correct_counts(prior,late,baseline,minimax)[1]
        counterfactual[key]=(early_minimax-early_frozen,late_minimax-late_frozen)
    aligned={key for key,i in indices.items() if 127&(1<<i)}; check_hook={key for key,i in indices.items() if 128&(1<<i)}; model_fraction_hook={key for key,i in indices.items() if 3840&(1<<i)}
    deltas={(key,j):inherited[key][j]-counterfactual[key][j] for key in scheduled_set if key in inherited and key in counterfactual for j in (0,1)}
    sign_divergences={(key,j) for (key,j),_delta in deltas.items() if (inherited[key][j]>=0)!=(counterfactual[key][j]>=0)}
    higher={(key,j) for (key,j),delta in deltas.items() if key in model_fraction_hook and delta>0}; lower={(key,j) for (key,j),delta in deltas.items() if key in model_fraction_hook and delta<0}; equal={(key,j) for (key,j),delta in deltas.items() if key in model_fraction_hook and delta==0}
    mask=lambda members: sum(1<<indices[key] for key in members); sm=sealed["metrics"]; all_margins=[value for pair in inherited.values() for value in pair]+[value for pair in counterfactual.values() for value in pair]
    aligned_differences=sum(key in aligned and delta!=0 for (key,_j),delta in deltas.items()); check_differences=sum(key in check_hook and delta!=0 for (key,_j),delta in deltas.items()); model_differences=len(higher)+len(lower)
    metrics.update({"aligned_margin_difference_count":float(aligned_differences),"check_hook_margin_difference_count":float(check_differences),"model_fraction_higher_inherited_count":float(len(higher)),"model_fraction_lower_inherited_count":float(len(lower)),"model_fraction_equal_margin_count":float(len(equal)),"model_fraction_direction_accounted_count":float(len(higher)+len(lower)+len(equal)),"model_fraction_absolute_delta_sum":float(sum(abs(delta) for (key,_j),delta in deltas.items() if key in model_fraction_hook)),"model_fraction_signed_delta_sum":float(sum(delta for (key,_j),delta in deltas.items() if key in model_fraction_hook)),"inherited_negative_margin_count":float(sum(value<0 for pair in inherited.values() for value in pair)),"counterfactual_negative_margin_count":float(sum(value<0 for pair in counterfactual.values() for value in pair)),"margin_sign_divergence_count":float(len(sign_divergences)),"missing_counterfactual_row_count":float(len(scheduled_set-set(counterfactual))),"duplicate_counterfactual_row_count":float(sum(n-1 for n in counts.values() if n>1)),"role_partition_mismatch_count":float(bool(aligned&check_hook or aligned&model_fraction_hook or check_hook&model_fraction_hook or (aligned|check_hook|model_fraction_hook)!=scheduled_set)),"direction_accounting_mismatch_count":float(len(rows)!=12 or len(blocks)!=12 or empty_blocks!=0 or any(n!=1 for n in counts.values()) or len(inherited)!=12 or len(counterfactual)!=12 or len(deltas)!=24 or any(type(value) is not int for value in all_margins) or any(type(delta) is not int for delta in deltas.values())),"sealed077_reproduction_mismatch_count":float(sm["aligned_margin_difference_count"]!=aligned_differences or sm["check_hook_margin_difference_count"]!=check_differences or sm["model_fraction_hook_margin_difference_count"]!=model_differences or sm["model_fraction_unchanged_margin_count"]!=len(equal) or sm["margin_sign_divergence_count"]!=len(sign_divergences) or sm["aligned_row_mask"]!=mask(aligned) or sm["check_hook_row_mask"]!=mask(check_hook) or sm["model_fraction_hook_row_mask"]!=mask(model_fraction_hook)),"aligned_row_mask":float(mask(aligned)),"check_hook_row_mask":float(mask(check_hook)),"model_fraction_hook_row_mask":float(mask(model_fraction_hook)),"higher_inherited_row_mask":float(mask({key for key,_j in higher})),"lower_inherited_row_mask":float(mask({key for key,_j in lower}))})
    if not all(isinstance(value,(int,float)) and math.isfinite(value) for value in metrics.values()): raise RuntimeError("NONFINITE_METRIC")
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))
if __name__=="__main__": main()
