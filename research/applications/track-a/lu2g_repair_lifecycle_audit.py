#!/usr/bin/env python3
import importlib.util, json, sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
LOADER=HERE/"lu2g_second_task_compositional_service_transfer_v1.candidate.py"
spec=importlib.util.spec_from_file_location("lu2g_candidate_probe",LOADER)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def audit(mode):
    objs=[]
    orig=m.Task2Request
    def factory(*a,**kw):
        r=orig(*a,**kw); objs.append(r); return r
    m.Task2Request=factory
    try:
        result,_,_=m.run_world(m.mechanical_manifest(),mode)
    finally:
        m.Task2Request=orig
    reached=[r for r in objs if r.scheduled_corrupt and r.corruption_applied and r.reached_egress_after_corrupt]
    undetected=[r for r in reached if not r.detected]
    detected=[r for r in reached if r.detected]
    unrepaired=[r for r in detected if not r.repaired]
    repaired=[r for r in detected if r.repaired]
    def row(r):
        return {
          "rid":r.rid,"created":r.created,"stage":r.stage,
          "first_egress_epoch":r.first_egress_epoch,
          "age_at_first_egress":None if r.first_egress_epoch is None else r.first_egress_epoch-r.created,
          "detected":r.detected,"repaired":r.repaired,
          "repair_epoch":r.repair_epoch,"expired_epoch":r.expired_epoch,
          "verified_after_repair":r.verified_after_repair,
        }
    return {
      "mode":mode,
      "expiry":m.p.EXPIRY,
      "reached":len(reached),"detected":len(detected),"repaired":len(repaired),
      "undetected":list(map(row,undetected)),
      "detected_unrepaired":list(map(row,unrepaired)),
      "repaired_terminal_stages":dict(Counter(r.stage for r in repaired)),
      "incorrect_done":result["incorrect_done"],
      "reported_repair_integrity":result["repair"]["repair_integrity"],
    }

out={"a0":audit("U_A0"),"a25":audit("U_A25")}
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
