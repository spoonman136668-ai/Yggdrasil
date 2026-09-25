#!/usr/bin/env python3
import json, sys
from pathlib import Path
import ygg_a2_terminal_integrity_priority_v1 as a2

TARGET=141

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    manifest=a2.t.primary_manifests(a2.A1_PREREG)[9]
    rows=[]
    original_builder=a2.make_local_match

    def diagnostic_builder(stats):
        matcher=original_builder(stats)
        def observed(seed,tick,states,requests,lesioned):
            r=requests.get(TARGET)
            before=None
            if r is not None and r.unfinished():
                op=a2.a1.task_op(r)
                eligible=[]
                if op is not None:
                    for cell in range(a2.p.N):
                        if cell not in lesioned and a2.g.eligible(cell,tick,states,r,seed,lesioned):
                            eligible.append(cell)
                before={
                    "tick":tick,"stage":r.stage,"pos":r.pos,"op":op,
                    "eligible_cells":eligible,
                }
            matches=matcher(seed,tick,states,requests,lesioned)
            if before is not None:
                before["selected"]=[
                    {"cell":cell,"op":op}
                    for cell,rid,op in matches if rid==TARGET
                ]
                rows.append(before)
            return matches
        return observed

    a2.make_local_match=diagnostic_builder
    try:
        result,history,registry,detected,stats=a2.run_world(manifest)
    finally:
        a2.make_local_match=original_builder

    target=registry[TARGET]
    at_egress=[x for x in rows if x["stage"]=="AT_EGRESS"]
    eligible_verify=[x for x in at_egress if x["op"]=="VERIFY" and x["eligible_cells"]]
    selected_verify=[x for x in at_egress if x["selected"]]
    out={
        "schema":1,
        "diagnostic":"YGG-A3-terminal-observability",
        "source_experiment":"YGG-A2",
        "replicate":10,
        "target_rid":TARGET,
        "first_egress_epoch":target.first_egress_epoch,
        "terminal_state":target.stage,
        "detected":target.detected,
        "repaired":target.repaired,
        "verified_epoch":target.verified_epoch,
        "ticks_at_egress":len(at_egress),
        "eligible_verify_ticks":len(eligible_verify),
        "selected_verify_ticks":len(selected_verify),
        "egress_rows":at_egress,
        "priority_stats":stats,
        "result":a2.g.compact(result),
    }
    Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,separators=(",",":")),encoding="utf-8")

if __name__=="__main__":
    main()
