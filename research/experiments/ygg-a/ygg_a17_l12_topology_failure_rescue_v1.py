#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a15_full_blend_max_repair_integration_v1 as a15

PREREG="cc3535e6c51b7cd5b7da37474f7b91ceeac13775"
PARENT_CLOSURE="1f22fb884b4329a1627da406204f9a5de2d1a2ea"
A15_ALPHA100_HASH="c094f01f6d5c3ae5987cab5215da3ce0146f84a44bce967f042d23cd474595a7"

a13=a15.a13
a8=a13.a8
g=a8.g
p=a8.p
t=a8.t
ORIG_LESION_SET=p.lesion_set
ORIG_VALIDATE=t.validate_manifest
ORIG_DAMAGE_SCHEDULE=a8.damage_schedule
TARGET_ALPHA=1.0

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def inherited_l8(seed):
    cells=sorted(ORIG_LESION_SET(seed))
    if len(cells)!=8:
        raise AssertionError("A17 inherited lesion cardinality")
    return cells

def lesion12(seed):
    base=inherited_l8(seed)
    used=set(base)
    remaining=[c for c in range(p.N) if c not in used]
    ranked=sorted(remaining,key=lambda c:(p.h64("YGG-C3-RESOURCE-PRESSURE",seed,c),c))
    out=sorted(base+ranked[:4])
    if len(out)!=12 or not set(base).issubset(out):
        raise AssertionError("A17 L12 construction")
    return out

def nonlesion_bytes(m):
    x=copy.deepcopy(m)
    x.pop("manifest_sha256",None)
    x.pop("lesion",None)
    return canonical(x)

def pressure_manifest(base):
    m=copy.deepcopy(base)
    m["lesion"]=lesion12(m["seed"])
    m["manifest_sha256"]=t.manifest_identity(m)
    if nonlesion_bytes(m)!=nonlesion_bytes(base):
        raise AssertionError("A17 nonlesion mutation")
    return m

def pressure_validate(candidate):
    normalized=copy.deepcopy(candidate)
    normalized["lesion"]=inherited_l8(candidate["seed"])
    normalized["manifest_sha256"]=t.manifest_identity(normalized)
    current=p.lesion_set
    p.lesion_set=ORIG_LESION_SET
    try:
        return ORIG_VALIDATE(normalized)
    finally:
        p.lesion_set=current

def stream_noncollapse(anchor_rows,current_rows):
    base={int(r["replicate"]):r["a25_on"] for r in anchor_rows}
    failures=[]
    for row in current_rows:
        rep=int(row["replicate"])
        br=base[rep]["result"]["stream_phase"]
        cr=row["a25_on"]["result"]["stream_phase"]
        for ph in range(5):
            ps=str(ph)
            for stream in ("C","S"):
                base_n=br[ps][stream]
                cur_n=cr[ps][stream]
                if base_n>=4 and cur_n<0.75*base_n:
                    failures.append({
                        "replicate":rep,
                        "phase":ph,
                        "stream":stream,
                        "l8":base_n,
                        "l12":cur_n,
                        "ratio":cur_n/base_n if base_n else None,
                    })
    return len(failures)==0,failures

def l12_one_pass(anchor_rows):
    base=t.primary_manifests(a8.A1_PREREG)
    manifests=[pressure_manifest(m) for m in base]
    mech=a8.mechanical()

    old_validate=t.validate_manifest
    old_lesion=p.lesion_set
    old_schedule=a8.damage_schedule
    old_alpha=float(g.ALPHA)

    t.validate_manifest=pressure_validate
    p.lesion_set=lambda seed:set(lesion12(seed))
    a8.damage_schedule=a13.damage_schedule58
    g.ALPHA=TARGET_ALPHA
    try:
        rows=[]
        for m in manifests:
            a0_on=a8.scored(m,"U_A0",True)
            a25_off=a8.scored(m,"U_A25",False)
            a25_on=a8.scored(m,"U_A25",True)
            rows.append({
                "replicate":m["replicate"],
                "manifest":m,
                "a0_on":a0_on,
                "a25_off":a25_off,
                "a25_on":a25_on,
                "a25_damage_ratio":(
                    a25_on["result"]["correct_done"]/a25_off["result"]["correct_done"]
                    if a25_off["result"]["correct_done"] else None
                ),
                "learned_state_diverged":a0_on["result"]["state_sha256"]!=a25_on["result"]["state_sha256"],
            })
    finally:
        t.validate_manifest=old_validate
        p.lesion_set=old_lesion
        a8.damage_schedule=old_schedule
        g.ALPHA=old_alpha

    on_rows=[r["a25_on"] for r in rows]
    off_rows=[r["a25_off"] for r in rows]
    a25_on_total=sum(x["result"]["correct_done"] for x in on_rows)
    a25_off_total=sum(x["result"]["correct_done"] for x in off_rows)
    damage_ratio=a25_on_total/a25_off_total if a25_off_total else None
    vs_l8=a25_on_total/1450.0
    stream_ok,stream_failures=stream_noncollapse(anchor_rows,rows)

    branch_exact=all(
        x["branch"]["scheduled"]==58
        and x["branch"]["scheduled_b"]==29
        and x["branch"]["scheduled_c"]==29
        and x["branch"]["applied"]==58
        and x["branch"]["repaired"]==58
        and x["branch"]["all_repaired_before_d"]
        and x["branch"]["unrepaired_terminal"]==0
        and x["branch_stats"]["d_while_branch_incorrect"]==0
        for x in on_rows
    )
    integrity=all(
        x["result"]["incorrect_done"]==0
        and x["result"]["matching_duplicate_cell"]==0
        and x["result"]["matching_duplicate_request"]==0
        and x["maturity"]["pass"]
        and x["horizon_aware_repair_integrity"]
        for x in on_rows
    )
    lesion_exact=all(
        len(r["manifest"]["lesion"])==12
        and r["manifest"]["lesion"]==lesion12(r["manifest"]["seed"])
        and set(inherited_l8(r["manifest"]["seed"])).issubset(r["manifest"]["lesion"])
        for r in rows
    )
    nonlesion_exact=all(nonlesion_bytes(m)==nonlesion_bytes(b) for m,b in zip(manifests,base))

    q={
        "mechanical_gate":bool(mech["all_pass"]),
        "l12_exact_c3_nested_construction":bool(lesion_exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion_exact),
        "branch_schedule_and_repair_exact_58":bool(branch_exact),
        "damaged_terminal_integrity_exact":bool(integrity),
        "l12_a25_damage_ratio_ge_095":damage_ratio is not None and damage_ratio>=0.95,
        "all_l12_world_damage_ratio_ge_090":all(
            r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90 for r in rows
        ),
        "l12_damage_on_vs_l8_damage_on_ge_090":vs_l8>=0.90,
        "l12_stream_noncollapse_rescued":bool(stream_ok),
        "learned_arm_materially_exercised":any(r["learned_state_diverged"] for r in rows),
    }
    return {
        "schema":1,
        "experiment":"YGG-A17-L12",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alpha":TARGET_ALPHA,
        "aggregate":{
            "a25_off_correct_done":a25_off_total,
            "a25_on_correct_done":a25_on_total,
            "a25_damage_ratio":damage_ratio,
            "a25_damage_on_vs_a15_l8_damage_on":vs_l8,
            "stream_noncollapse":stream_ok,
            "stream_failures":stream_failures,
        },
        "qualification":q,
        "rows":rows,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_alpha=float(g.ALPHA)
    original_validate=t.validate_manifest
    original_lesion=p.lesion_set
    original_schedule=a8.damage_schedule

    g.ALPHA=TARGET_ALPHA
    try:
        anchor=a13.one_pass()
    finally:
        g.ALPHA=original_alpha
    anchor_hash=hashlib.sha256(canonical(anchor)).hexdigest()

    first=l12_one_pass(anchor["rows"])
    second=l12_one_pass(anchor["rows"])
    b1=canonical(first)
    b2=canonical(second)

    restoration={
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "lesion_set_restored":p.lesion_set is original_lesion,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
    }
    validity={
        "a15_alpha100_anchor_exact":anchor_hash==A15_ALPHA100_HASH,
        "duplicate_l12_execution_byte_identical":b1==b2,
        **restoration,
    }
    qualification={
        **first["qualification"],
        "YGG_A17_L12_TOPOLOGY_FAILURE_RESCUE":bool(
            all(validity.values()) and all(first["qualification"].values())
        ),
    }
    out={
        "schema":1,
        "experiment":"YGG-A17",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "a15_alpha100_anchor_sha256":anchor_hash,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
