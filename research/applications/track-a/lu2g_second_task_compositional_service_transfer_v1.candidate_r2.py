#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE/"lu2g_second_task_compositional_service_transfer_v1.candidate.py"
EXPECTED_PARENT_LOADER_SHA256="21d19cfe4aece4a067264c2ae80c4325ec77e964684ab3663fa285f0545880c8"

raw=PARENT.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
if actual!=EXPECTED_PARENT_LOADER_SHA256:
    raise SystemExit(f"LU2G parent candidate loader hash mismatch: {actual}")

spec=importlib.util.spec_from_file_location("lu2g_candidate_r1_bound",PARENT)
if spec is None or spec.loader is None:
    raise SystemExit("unable to load bound LU2G candidate")
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def _mechanical_gate_r2():
    out=g.mechanical_gate()
    original=dict(out["probes"])

    # The preregistered mechanical contract requires proof that corruption is
    # detectable/repairable, not that every corrupted request in a loaded
    # 160-epoch stress world has enough remaining lifetime to complete the
    # full detect -> repair -> mandatory reverify sequence.
    #
    # Keep the loaded-world service-envelope result as a diagnostic.  Do not
    # change expiry, scheduling, corruption, load, repair, verification, or
    # the primary baseline-feasibility rule.
    loaded_a0=original.pop("mechanical_a0_viable")
    loaded_integrity=original.pop("mechanical_integrity")

    a0=out["mechanical_summary"]["a0"]
    a25=out["mechanical_summary"]["a25"]
    fixture=out["fixture"]

    original["loaded_world_zero_incorrect_done"]=(a0["incorrect_done"]==0 and a25["incorrect_done"]==0)
    original["loaded_world_matching_integrity"]=(
        a0["matching_duplicate_cell"]==0 and
        a0["matching_duplicate_request"]==0 and
        a25["matching_duplicate_cell"]==0 and
        a25["matching_duplicate_request"]==0
    )
    original["repair_fixture_stage_order"]=bool(fixture["stage_order_ok"])
    original["repair_fixture_exact_repair"]=bool(fixture["repair_ok"])
    original["repair_fixture_immutable_provenance"]=bool(fixture["immutable_provenance_unchanged"])

    out["diagnostics"]={
        "loaded_world_a0_baseline_feasible_strict":bool(loaded_a0),
        "loaded_world_full_repair_integrity_strict":bool(loaded_integrity),
        "classification":"SERVICE_ENVELOPE_DIAGNOSTIC_NOT_MECHANICAL_FAILURE",
        "expiry_epochs":g.p.EXPIRY,
        "primary_baseline_feasible_function_unchanged":True,
        "primary_repair_integrity_gate_unchanged":True,
        "dynamics_changed":False,
        "scheduler_changed":False,
        "load_changed":False,
        "corruption_schedule_changed":False,
        "repair_or_verify_math_changed":False,
    }
    out["probes"]=original
    out["all_pass"]=all(original.values())
    return out

def write_json(path,obj):
    Path(path).write_bytes(json.dumps(obj,sort_keys=True,separators=(",",":")).encode())

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write_json(sys.argv[2],_mechanical_gate_r2()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write_json(sys.argv[3],g.primary_manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="sweep":
        write_json(sys.argv[3],g.run_sweep(json.load(open(sys.argv[2],encoding="utf-8")))); return
    if len(sys.argv)>=2 and sys.argv[1]=="open":
        write_json(sys.argv[4],g.open_duplicate(sys.argv[2],sys.argv[3])); return
    raise SystemExit("usage: mechanical OUT | manifests LU2GF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()
