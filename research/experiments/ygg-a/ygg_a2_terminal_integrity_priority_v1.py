#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import torch

import ygg_a1_fork_join_v1 as a1

g=a1.g
p=a1.p
t=a1.t

A1_PREREG=a1.PREREG
A2_PREREG_COMMIT="fe98512607bbd5a267a2735ae5fd881e47b5d86e"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def priority(op):
    if op=="VERIFY": return 0
    if op=="REPAIR": return 1
    return 2

def prioritized(opts):
    inherited=sorted(opts)
    treatment=sorted(opts,key=lambda x:(priority(x[3]),)+x)
    if set(inherited)!=set(treatment):
        raise AssertionError("priority created or removed eligibility")
    return inherited,treatment

def resolve(prefs):
    next_idx={cell:0 for cell in prefs}; held={}; free=set(prefs)
    while free:
        cell=min(free); free.remove(cell); ps=prefs[cell]
        if next_idx[cell]>=len(ps): continue
        _,rid,_,op=ps[next_idx[cell]]; next_idx[cell]+=1
        pref=p.h64("TASK1-REQUEST-CELL-PREF",_resolve_seed,_resolve_t,rid,op,cell)
        cur=held.get(rid)
        if cur is None or (pref,cell)<(cur[0],cur[1]):
            if cur is not None:
                old=cur[1]
                if next_idx[old]<len(prefs[old]): free.add(old)
            held[rid]=(pref,cell,op)
        elif next_idx[cell]<len(ps):
            free.add(cell)
    matches=sorted((cell,rid,op) for rid,(_,cell,op) in held.items())
    if len({x[0] for x in matches})!=len(matches) or len({x[1] for x in matches})!=len(matches):
        raise AssertionError("duplicate match")
    return matches

_resolve_seed=None
_resolve_t=None

def make_local_match(stats):
    def local_match(seed,tick,states,requests,lesioned):
        global _resolve_seed,_resolve_t
        inherited_prefs={}; treatment_prefs={}
        for cell in range(p.N):
            if cell in lesioned: continue
            opts=[]
            for r in requests.values():
                if not r.unfinished(): continue
                op=g.task2_op(r)
                if op is None: continue
                if g.eligible(cell,tick,states,r,seed,lesioned):
                    opts.append((r.created,r.rid,p.tie_key(seed,tick,cell,r.rid,op),op))
            if opts:
                inherited,treatment=prioritized(opts)
                inherited_prefs[cell]=inherited
                treatment_prefs[cell]=treatment

        _resolve_seed=seed; _resolve_t=tick
        inherited_matches=resolve(inherited_prefs)
        treatment_matches=resolve(treatment_prefs)

        inherited_by_cell={cell:(rid,op) for cell,rid,op in inherited_matches}
        for cell,rid,op in treatment_matches:
            if inherited_by_cell.get(cell)!=(rid,op):
                if op=="VERIFY":
                    stats["verify_priority_changed_winner"]+=1
                elif op=="REPAIR":
                    stats["repair_priority_changed_winner"]+=1
        return treatment_matches
    return local_match

def run_world(m):
    registry={}; detected={}
    programs=m["programs"]
    stats={"verify_priority_changed_winner":0,"repair_priority_changed_winner":0}
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH,g.local_match)

    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=t.Task4Request(rid,stream,created,bits,program_a,program_b,programs[stream]["C"],programs[stream]["D"],pos,scheduled_corrupt)
        registry[rid]=r
        return r

    def op(seed,tick,cell,name,r,trace):
        pre=r.stage
        a1.do_op(seed,tick,cell,name,r,trace)
        if name=="VERIFY" and pre=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected.setdefault(r.rid,tick)

    g.Task2Request=factory
    g.task2_op=a1.task_op
    g.do_operation=op
    g.expected_pair=a1.expected_pair
    g.validate_manifest=t.validate_manifest
    g.REQUESTS_PER_EPOCH=1
    g.local_match=make_local_match(stats)
    try:
        result,history,_=g.run_world(m,"U_A0")
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH,g.local_match=old
    return result,history,registry,detected,stats

def priority_fixture():
    verify_opts=[(0,1,0,"SENSE"),(9,9,9,"VERIFY")]
    repair_opts=[(0,1,0,"PROCESS"),(9,9,9,"REPAIR")]
    equal_opts=[(5,7,3,"PROCESS"),(1,8,4,"ROUTE"),(3,2,5,"SENSE")]
    vi,vt=prioritized(verify_opts)
    ri,rt=prioritized(repair_opts)
    ei,et=prioritized(equal_opts)
    return {
        "verify_already_eligible":set(vi)==set(vt),
        "verify_outranks_inherited_nonterminal":vi[0][3]!="VERIFY" and vt[0][3]=="VERIFY",
        "repair_already_eligible":set(ri)==set(rt),
        "repair_outranks_inherited_nonterminal":ri[0][3]!="REPAIR" and rt[0][3]=="REPAIR",
        "priority_never_creates_eligibility":set(vi)==set(vt) and set(ri)==set(rt) and set(ei)==set(et),
        "equal_priority_inherited_order_unchanged":ei==et,
    }

def mechanical():
    pf=priority_fixture()
    f_bc=a1.fixture("BC"); f_cb=a1.fixture("CB")
    m=a1.manifest()
    rng0=torch.random.get_rng_state().clone()
    a=run_world(m)
    rng1=torch.random.get_rng_state().clone()
    b=run_world(m)
    rowa={"result":g.compact(a[0]),"maturity":a1.maturity_summary(m,a[2],a[3]),"priority":a[4]}
    rowb={"result":g.compact(b[0]),"maturity":a1.maturity_summary(m,b[2],b[3]),"priority":b[4]}
    ba=canonical(rowa); bb=canonical(rowb)
    probes={
        "a2_prereg_bound":A2_PREREG_COMMIT=="fe98512607bbd5a267a2735ae5fd881e47b5d86e",
        **pf,
        "bc_order_exercised":f_bc["sibling1"]=="PROCESSED_B_ONLY",
        "cb_order_exercised":f_cb["sibling1"]=="PROCESSED_C_ONLY",
        "join_blocks_d":f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"],
        "d_after_both":f_bc["d_after_join"] and f_cb["d_after_join"],
        "dependencies_exact":f_bc["dependencies_exact"] and f_cb["dependencies_exact"],
        "repair_reverify":f_bc["detected"] and f_bc["repaired"] and f_bc["reverified"] and f_cb["detected"] and f_cb["repaired"] and f_cb["reverified"],
        "duplicate_byte_identical":ba==bb,
        "zero_incorrect_done":rowa["result"]["incorrect_done"]==0,
        "maturity_pass":rowa["maturity"]["pass"],
        "no_model_rng":torch.equal(rng0,rng1),
    }
    return {
        "schema":1,"experiment":"YGG-A2","stage":"mechanical","prereg_commit":A2_PREREG_COMMIT,
        "all_pass":all(probes.values()),"probes":probes,"priority_fixture":pf,
        "fixture_bc":f_bc,"fixture_cb":f_cb,
        "duplicate":{"bytes":len(ba),"sha256":hashlib.sha256(ba).hexdigest()},
        "world":rowa,
    }

def scored_world(m):
    t.validate_manifest(m)
    result,history,registry,detected,stats=run_world(m)
    return {
        "manifest":m,
        "result":g.compact(result),
        "maturity":a1.maturity_summary(m,registry,detected),
        "priority":stats,
        "integrity":{
            "duplicate_cell":result["matching_duplicate_cell"]==0,
            "duplicate_request":result["matching_duplicate_request"]==0,
            "incorrect_done_zero":result["incorrect_done"]==0,
        },
    }

def primary():
    manifests=t.primary_manifests(A1_PREREG)
    first=[scored_world(m) for m in manifests]
    second=[scored_world(m) for m in manifests]
    b1=canonical(first); b2=canonical(second)

    feasible=[row for row in first if t.baseline_feasible(row)]
    all_zero=all(row["result"]["incorrect_done"]==0 for row in first)
    all_matching=all(row["integrity"]["duplicate_cell"] and row["integrity"]["duplicate_request"] for row in first)
    all_repair=all(row["result"]["repair"]["repair_integrity"] for row in first)
    all_maturity=all(row["maturity"]["pass"] for row in first)
    f_bc=a1.fixture("BC"); f_cb=a1.fixture("CB")
    ordering=(f_bc["sibling1"]=="PROCESSED_B_ONLY" and f_cb["sibling1"]=="PROCESSED_C_ONLY")
    join=(f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"] and f_bc["d_after_join"] and f_cb["d_after_join"])
    dependency=(f_bc["dependencies_exact"] and f_cb["dependencies_exact"])
    repair_fixture=(f_bc["detected"] and f_bc["repaired"] and f_bc["reverified"] and f_cb["detected"] and f_cb["repaired"] and f_cb["reverified"])
    duplicate=(b1==b2)
    verify_changes=sum(row["priority"]["verify_priority_changed_winner"] for row in first)
    repair_changes=sum(row["priority"]["repair_priority_changed_winner"] for row in first)

    q={
        "baseline_feasible_count":len(feasible),
        "evidence_coverage_pass":len(feasible)>=8,
        "all_zero_incorrect_done":all_zero,
        "all_matching_integrity":all_matching,
        "both_sibling_orders_exercised":ordering,
        "d_never_before_join":join,
        "fork_dependencies_exact":dependency,
        "all_repair_integrity":all_repair,
        "all_maturity_pass":all_maturity,
        "repair_reverify_fixture":repair_fixture,
        "duplicate_byte_identical":duplicate,
    }
    q["YGG_A2_TERMINAL_INTEGRITY_PRIORITY"]=all([
        q["evidence_coverage_pass"],q["all_zero_incorrect_done"],q["all_matching_integrity"],
        q["both_sibling_orders_exercised"],q["d_never_before_join"],q["fork_dependencies_exact"],
        q["all_repair_integrity"],q["all_maturity_pass"],q["repair_reverify_fixture"],
        q["duplicate_byte_identical"],
    ])
    q["feasible_replicates"]=[row["manifest"]["replicate"] for row in feasible]
    q["verify_priority_changed_winner"]=verify_changes
    q["repair_priority_changed_winner"]=repair_changes
    q["per_world"]=[{
        "replicate":row["manifest"]["replicate"],
        "baseline_feasible":t.baseline_feasible(row),
        "correct_done":row["result"]["correct_done"],
        "incorrect_done":row["result"]["incorrect_done"],
        "expired":row["result"]["expired"],
        "backlog":row["result"]["backlog"],
        "ops_per_correct":row["result"]["operations_per_correct_completion"],
        "demand_recovery":row["result"]["events"]["demand_reversal_recovery_latency"],
        "lesion_recovery":row["result"]["events"]["lesion_recovery_latency"],
        "anchor_recovery":row["result"]["events"]["anchor_rotation_recovery_latency"],
        "maturity_pass":row["maturity"]["pass"],
        "repair_integrity":row["result"]["repair"]["repair_integrity"],
        "verify_priority_changed_winner":row["priority"]["verify_priority_changed_winner"],
        "repair_priority_changed_winner":row["priority"]["repair_priority_changed_winner"],
    } for row in first]
    return {
        "schema":1,"experiment":"YGG-A2","stage":"primary","prereg_commit":A2_PREREG_COMMIT,
        "frozen_a1_prereg":A1_PREREG,
        "treatment":"VERIFY > REPAIR > inherited ordering among already-eligible local operations",
        "duplicate":{"byte_identical":duplicate,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},
        "qualification":q,"sweep":first,
    }

def main():
    if len(sys.argv)!=3 or sys.argv[1] not in ("mechanical","primary"):
        raise SystemExit("usage: mechanical OUT | primary OUT")
    out=mechanical() if sys.argv[1]=="mechanical" else primary()
    Path(sys.argv[2]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
