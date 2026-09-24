#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

EXPECTED_BYTES=1016475
EXPECTED_SHA256="ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da"
LOADS=(1,2,3)
REPAIR_KEYS=(
    "scheduled_corruptions",
    "corruption_applied",
    "corruptions_reaching_egress",
    "verification_detected",
    "repaired",
    "correct_done_after_repair",
)

def ratio(a,b):
    return None if b==0 else a/b

def median(vals):
    return statistics.median(vals) if vals else None

def open_exact(p1,p2):
    a=Path(p1).read_bytes()
    b=Path(p2).read_bytes()
    if a!=b:
        raise SystemExit("LU2J accepted duplicate mismatch")
    if len(a)!=EXPECTED_BYTES:
        raise SystemExit(f"LU2J accepted byte-count mismatch: {len(a)}")
    sha=hashlib.sha256(a).hexdigest()
    if sha!=EXPECTED_SHA256:
        raise SystemExit(f"LU2J accepted SHA mismatch: {sha}")
    return a,sha

raw,sha=open_exact(sys.argv[1],sys.argv[2])
data=json.loads(raw.decode("utf-8"))
rows=data.get("rows")
if not isinstance(rows,list) or len(rows)!=30:
    raise SystemExit("LU2J expected exactly 30 accepted rows")

by={L:sorted((r for r in rows if r.get("load")==L),key=lambda r:r["replicate"]) for L in LOADS}
if any(len(by[L])!=10 for L in LOADS):
    raise SystemExit("LU2J expected ten rows per load")

repair={}
per_world={}
zero_wrong={}
streams_all={}
for L in LOADS:
    sums={k:sum(int(r["repair"][k]) for r in by[L]) for k in REPAIR_KEYS}
    repair[str(L)]={
        **sums,
        "detection_given_egress":ratio(sums["verification_detected"],sums["corruptions_reaching_egress"]),
        "repair_given_detected":ratio(sums["repaired"],sums["verification_detected"]),
        "done_given_repaired":ratio(sums["correct_done_after_repair"],sums["repaired"]),
        "done_given_egress":ratio(sums["correct_done_after_repair"],sums["corruptions_reaching_egress"]),
        "strict_baseline_feasible_worlds":sum(bool(r["strict_baseline_feasible"]) for r in by[L]),
        "repair_integrity_worlds":sum(bool(r["repair"]["repair_integrity"]) for r in by[L]),
    }
    per_world[str(L)]=[]
    for r in by[L]:
        x=r["repair"]
        per_world[str(L)].append({
            "replicate":r["replicate"],
            "strict_baseline_feasible":bool(r["strict_baseline_feasible"]),
            "repair_integrity":bool(x["repair_integrity"]),
            "corruptions_reaching_egress":x["corruptions_reaching_egress"],
            "verification_detected":x["verification_detected"],
            "repaired":x["repaired"],
            "correct_done_after_repair":x["correct_done_after_repair"],
            "detection_given_egress":ratio(x["verification_detected"],x["corruptions_reaching_egress"]),
            "repair_given_detected":ratio(x["repaired"],x["verification_detected"]),
            "done_given_repaired":ratio(x["correct_done_after_repair"],x["repaired"]),
            "done_given_egress":ratio(x["correct_done_after_repair"],x["corruptions_reaching_egress"]),
        })
    zero_wrong[L]=all(r["incorrect_done"]==0 for r in by[L])
    streams_all[L]=all(r["stream_total"]["C"]>=1 and r["stream_total"]["S"]>=1 for r in by[L])

r2=repair["2"]; r3=repair["3"]
exposure_supported=bool(
    r2["corruptions_reaching_egress"]>r3["corruptions_reaching_egress"]
    and r2["detection_given_egress"]>=r3["detection_given_egress"]
    and r2["repair_given_detected"]>=r3["repair_given_detected"]
    and r2["done_given_repaired"]>=r3["done_given_repaired"]
    and r2["done_given_egress"]>=r3["done_given_egress"]
    and zero_wrong[2] and zero_wrong[3]
)

labels=("C","S","U","H","FC","FS")
organization={}
cs_medians={}
for L in LOADS:
    organization[str(L)]={}
    cs_medians[L]={}
    for ph in range(5):
        vals={lab:[r["phase_state_mean"][str(ph)][lab] for r in by[L]] for lab in labels}
        row={lab:median(vals[lab]) for lab in labels}
        row["C_plus_S"]=median([
            r["phase_state_mean"][str(ph)]["C"]+r["phase_state_mean"][str(ph)]["S"]
            for r in by[L]
        ])
        row["FC_plus_FS"]=median([
            r["phase_state_mean"][str(ph)]["FC"]+r["phase_state_mean"][str(ph)]["FS"]
            for r in by[L]
        ])
        organization[str(L)][str(ph)]=row
        cs_medians[L][ph]=row["C_plus_S"]

l2_lower_both_phases=[
    ph for ph in range(5)
    if cs_medians[2][ph] < cs_medians[1][ph] and cs_medians[2][ph] < cs_medians[3][ph]
]
l2_stream_loss=not streams_all[2]
organization_collapse=bool(l2_stream_loss or len(l2_lower_both_phases)>=2)

request_timestamp_fields={
    "first_verify","failed_first_verify","repair_epoch","post_repair_verify",
    "remaining_lifetime_at_verify","remaining_lifetime_at_repair"
}
timestamps_present=any(any(k in r for k in request_timestamp_fields) for r in rows)

decision={
    "EXPOSURE_CONDITIONED_METRIC_ARTIFACT_SUPPORTED":exposure_supported,
    "L2_DEVELOPMENTAL_ORGANIZATION_COLLAPSE_SUPPORTED":organization_collapse,
    "NO_L2_ORGANIZATION_COLLAPSE_OBSERVED":not organization_collapse,
    "REQUEST_LEVEL_DEADLINE_GEOMETRY_RESOLVED":bool(timestamps_present),
    "NEXT_STEP_L1_FRESH_EXACT_PARENT_VALIDATION_AUTHORIZED_BY_DIAGNOSTIC":bool(exposure_supported and not organization_collapse),
}

out={
    "schema":1,
    "lu2j_prereg":"5defdaacf15f3e9c5ac72b4cd72518399e2294a3",
    "parent_lu2i_closure":"1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d",
    "accepted_run_id":36050323979,
    "accepted_artifact_id":10829937783,
    "artifact_identity":{"duplicate_byte_identical":True,"bytes":len(raw),"sha256":sha},
    "repair_by_load":repair,
    "repair_per_world":per_world,
    "organization_phase_medians":organization,
    "both_streams_active_all_worlds":{str(L):streams_all[L] for L in LOADS},
    "zero_incorrect_done_all_worlds":{str(L):zero_wrong[L] for L in LOADS},
    "l2_cs_lower_than_both_other_loads_phases":l2_lower_both_phases,
    "artifact_deadline_timestamp_fields_present":bool(timestamps_present),
    "decision":decision,
}
Path(sys.argv[3]).write_bytes(json.dumps(out,sort_keys=True,separators=(",",":")).encode())
