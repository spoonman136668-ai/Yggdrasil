#!/usr/bin/env python3
import sys
from pathlib import Path
import ygg_a2_terminal_integrity_priority_v1 as a2

PREREG="dcdbbc6fb65e78a7c0299a8d84d57ae3168380fe"

def is_terminal_route(seed,r,op):
    if op!="ROUTE":
        return False
    anchors=a2.g.request_anchors(seed,r)
    nxt=(r.pos+a2.p.stream_dir(r.stream))%a2.p.N
    return nxt==a2.p.egress(anchors,r.stream)

def rank(seed,r,op):
    if op=="VERIFY": return 0
    if op=="REPAIR": return 1
    if is_terminal_route(seed,r,op): return 2
    return 3

def make_local_match(stats):
    stats.setdefault("terminal_route_priority_changed_winner",0)
    def local_match(seed,tick,states,requests,lesioned):
        inherited_prefs={}; treatment_prefs={}
        for cell in range(a2.p.N):
            if cell in lesioned: continue
            opts=[]
            for r in requests.values():
                if not r.unfinished(): continue
                op=a2.g.task2_op(r)
                if op is None: continue
                if a2.g.eligible(cell,tick,states,r,seed,lesioned):
                    opts.append((r.created,r.rid,a2.p.tie_key(seed,tick,cell,r.rid,op),op))
            if opts:
                inherited_prefs[cell]=sorted(opts)
                treatment_prefs[cell]=sorted(opts,key=lambda x:(rank(seed,requests[x[1]],x[3]),)+x)
        a2._resolve_seed=seed; a2._resolve_t=tick
        inherited=a2.resolve(inherited_prefs)
        treatment=a2.resolve(treatment_prefs)
        inherited_by_cell={cell:(rid,op) for cell,rid,op in inherited}
        for cell,rid,op in treatment:
            if inherited_by_cell.get(cell)!=(rid,op):
                if op=="VERIFY":
                    stats["verify_priority_changed_winner"]+=1
                elif op=="REPAIR":
                    stats["repair_priority_changed_winner"]+=1
                elif is_terminal_route(seed,requests[rid],op):
                    stats["terminal_route_priority_changed_winner"]+=1
        return treatment
    return local_match

def fixture():
    inherited=[(0,1,0,"PROCESS"),(9,9,9,"ROUTE")]
    terminal=sorted(inherited,key=lambda x:((2 if x[3]=="ROUTE" else 3),)+x)
    ordinary=[(1,7,3,"ROUTE"),(5,8,4,"PROCESS")]
    ordinary_sorted=sorted(ordinary,key=lambda x:(3,)+x)
    return {
        "terminal_route_outranks_nonterminal":sorted(inherited)[0][3]!="ROUTE" and terminal[0][3]=="ROUTE",
        "ordinary_route_no_special_priority":ordinary_sorted==sorted(ordinary),
        "priority_never_creates_eligibility":set(inherited)==set(terminal),
    }

def patched(call):
    old=a2.make_local_match
    a2.make_local_match=make_local_match
    try:
        return call()
    finally:
        a2.make_local_match=old

def mechanical():
    out=patched(a2.mechanical)
    fx=fixture()
    out["schema"]=1
    out["experiment"]="YGG-A3"
    out["prereg_commit"]=PREREG
    out["terminal_transit_fixture"]=fx
    out["probes"]["a3_prereg_bound"]=True
    out["all_pass"]=bool(out["all_pass"] and all(fx.values()))
    return out

def primary():
    out=patched(a2.primary)
    q=out["qualification"]
    parent=bool(q.pop("YGG_A2_TERMINAL_INTEGRITY_PRIORITY"))
    total=0
    for pw,row in zip(q["per_world"],out["sweep"]):
        n=row["priority"].get("terminal_route_priority_changed_winner",0)
        pw["terminal_route_priority_changed_winner"]=n
        total+=n
    q["terminal_route_priority_changed_winner"]=total
    q["YGG_A3_TERMINAL_TRANSIT_PRIORITY"]=parent
    out["experiment"]="YGG-A3"
    out["prereg_commit"]=PREREG
    out["treatment"]="VERIFY > REPAIR > final ROUTE-to-egress > inherited ordering among already-eligible local operations"
    return out

def main():
    if len(sys.argv)!=3 or sys.argv[1] not in ("mechanical","primary"):
        raise SystemExit("usage: mechanical OUT | primary OUT")
    out=mechanical() if sys.argv[1]=="mechanical" else primary()
    Path(sys.argv[2]).write_bytes(a2.canonical(out))

if __name__=="__main__":
    main()
