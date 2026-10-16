"""Read-only attribution of global gate hooks to logical call roles."""
import argparse, hashlib, importlib.util, json, math, sys
from collections import Counter
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-CALL-ROLE-ATTRIBUTION-073"
P044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
P043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
P029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRESSURE = Path("research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py")
ERROR = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
SEALED = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-ROW-OFFSET-DRIFT-ATTRIBUTION-072-38822951064/result.json")
NORTH = Path("research/architecture/yggdrasil-north-star.ice")
IDENTITIES = ((P044,"cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"),(P043,"5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"),(P029,"e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"),(PRESSURE,"0144922b4191abb451e821f5b4ab14885e1de11272c5d625c3963d1cffdbfeb9"),(ERROR,"5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"),(SEALED,"446a5b293997f0c6f201bc6ff106a83246b0abd94847e434081df41126048ecb"),(NORTH,"57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"))
DIRECT = {303:"evaluation_frozen",306:"evaluation_independent",309:"evaluation_pooled",312:"evaluation_minimax",330:"cue_frozen",333:"cue_minimax",337:"check_frozen",340:"check_minimax"}
AUX = {39:"model_fraction_full",40:"model_fraction_active"}

def norm(value): return str(value).replace("\\", "/")
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise RuntimeError("IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def schedule(orders): return [(oi,si,name) for oi,order in enumerate(orders) for si in range(1,4) for name in order[:si]]

def run():
    if any(digest(path) != expected for path,expected in IDENTITIES): raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    if sealed.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-ROW-OFFSET-DRIFT-ATTRIBUTION-072": raise RuntimeError("SEALED_EXPERIMENT_MISMATCH")
    p044,p043 = load(P044,"p044_roles_073"),load(P043,"p043_roles_073")
    p043.ORDERS,p043.DEMAND_FILES = p044.ORDERS,p044.DEMAND_FILES
    orders = tuple(tuple(order) for order in p044.ORDERS); scheduled = schedule(orders)
    rows,current,calls = [],None,[]
    def close():
        nonlocal current
        if current is not None: current["end"]=len(calls); rows.append(current); current=None
    def trace(frame,event,_arg):
        nonlocal current
        filename=norm(frame.f_code.co_filename)
        if event=="line" and filename.endswith(norm(P029)) and frame.f_lineno==302:
            close()
            try: key=(orders.index(tuple(frame.f_locals.get("order",()))),len(tuple(frame.f_locals.get("seen",()))),frame.f_locals.get("name"))
            except ValueError: key=None
            current={"key":key,"start":len(calls),"hooks":[]}
        elif event=="call" and frame.f_code.co_name=="gated_counts" and filename.endswith(norm(P043)):
            caller=frame.f_back; caller_file=norm(caller.f_code.co_filename) if caller else ""; line=caller.f_lineno if caller else -1
            role=DIRECT.get(line) if caller_file.endswith(norm(P029)) else AUX.get(line) if caller_file.endswith(norm(ERROR)) else None
            offset=len(calls)%10; calls.append(role)
            if current is not None and offset in (4,5): current["hooks"].append((offset,role))
        elif event=="return" and filename.endswith(norm(P029)) and frame.f_code.co_name=="run": close()
        return trace
    old_trace=sys.gettrace(); sys.settrace(trace)
    try: gated,wrapped,_blocks=p043.gated_run()
    finally: sys.settrace(old_trace)
    old=gated["metrics"]; controls=("training_file_identity_mismatch_count","evaluation_file_identity_mismatch_count","future_stage_adaptation_access_count","second_half_adaptation_access_count","valid_stage_count","valid_seen_domain_evaluation_count","matched_assignment_failure_count","capacity_growth_event_count","retained_record_integrity_mismatch_count","state_partition_mismatch_count")
    metrics={name:old[name] for name in controls}; scheduled_set=set(scheduled); known=[row for row in rows if row["key"] in scheduled_set]
    counts=Counter(row["key"] for row in known); by_key={row["key"]:row for row in known}; indices={key:i for i,key in enumerate(scheduled)}
    offsets={key:row["start"]%10 for key,row in by_key.items()}; capture=[(row["key"],role) for row in known for offset,role in row["hooks"] if offset==4]; decision=[(row["key"],role) for row in known for offset,role in row["hooks"] if offset==5]
    cc,dc=Counter(role for _key,role in capture),Counter(role for _key,role in decision); known_roles=set(DIRECT.values())|set(AUX.values())
    mask=lambda pairs,role: sum(1<<indices[key] for key,found in pairs if found==role); pack=lambda values: sum(value<<(4*i) for i,value in enumerate(values)); sm=sealed["metrics"]
    order0=pack([offsets.get(key,15) for key in scheduled if key[0]==0]); order1=pack([offsets.get(key,15) for key in scheduled if key[0]==1])
    metrics.update({"observed_call_count":float(len(calls)),"capture_hook_count":float(len(capture)),"decision_hook_count":float(len(decision)),"capture_cue_frozen_count":float(cc["cue_frozen"]),"decision_cue_minimax_count":float(dc["cue_minimax"]),"capture_check_frozen_count":float(cc["check_frozen"]),"decision_check_minimax_count":float(dc["check_minimax"]),"capture_model_fraction_full_count":float(cc["model_fraction_full"]),"decision_model_fraction_active_count":float(dc["model_fraction_active"]),"other_capture_role_count":float(sum(n for role,n in cc.items() if role not in {"cue_frozen","check_frozen","model_fraction_full"})),"other_decision_role_count":float(sum(n for role,n in dc.items() if role not in {"cue_minimax","check_minimax","model_fraction_active"})),"unknown_call_role_count":float(sum(role not in known_roles for role in calls)),"duplicate_hook_row_count":float(sum(n-1 for n in Counter(key for key,_ in capture).values() if n>1)+sum(n-1 for n in Counter(key for key,_ in decision).values() if n>1)),"missing_capture_row_count":float(len(scheduled_set-{key for key,_ in capture})),"missing_decision_row_count":float(len(scheduled_set-{key for key,_ in decision})),"hook_accounting_mismatch_count":float(len(calls)!=len(wrapped) or len(rows)!=12 or any(n!=1 for n in counts.values())),"sealed072_offset_reproduction_mismatch_count":float(len(calls)!=sm["observed_call_count"] or order0!=sm["order0_row_start_offset_mask"] or order1!=sm["order1_row_start_offset_mask"]),"aligned_decision_row_mask":float(mask(decision,"cue_minimax")),"check_decision_row_mask":float(mask(decision,"check_minimax")),"model_fraction_decision_row_mask":float(mask(decision,"model_fraction_active"))})
    if not all(isinstance(value,(int,float)) and math.isfinite(value) for value in metrics.values()): raise RuntimeError("NONFINITE_METRIC")
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))
if __name__=="__main__": main()
