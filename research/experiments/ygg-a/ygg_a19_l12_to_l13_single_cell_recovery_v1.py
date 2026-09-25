#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a17_l12_topology_failure_rescue_v1 as a17

PREREG="59934276293c0f0d224fccb62f933e9cda8c984c"
PARENT_CLOSURE="b6b2a6c6726c7786946239b9658d24f5976f685c"
A15_ALPHA100_HASH="c094f01f6d5c3ae5987cab5215da3ce0146f84a44bce967f042d23cd474595a7"
EXPECTED_L12_FAILURE=[
    {"replicate":6,"phase":4,"stream":"S","l8":5,"l12":3,"ratio":0.6}
]

a13=a17.a13
a8=a17.a8
g=a17.g
p=a17.p
t=a17.t
ORIG_LESION_SET=a17.ORIG_LESION_SET
ORIG_VALIDATE=a17.ORIG_VALIDATE
TARGET_ALPHA=1.0

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def inherited_l8(seed):
    return a17.inherited_l8(seed)

def lesion_for(seed,count):
    if count not in (12,13):
        raise AssertionError("A19 unregistered lesion count")
    base=inherited_l8(seed)
    used=set(base)
    remaining=[c for c in range(p.N) if c not in used]
    ranked=sorted(remaining,key=lambda c:(p.h64("YGG-C3-RESOURCE-PRESSURE",seed,c),c))
    out=sorted(base+ranked[:count-8])
    if len(out)!=count or not set(base).issubset(out):
        raise AssertionError("A19 nested lesion construction")
    return out

def nonlesion_bytes(m):
    return a17.nonlesion_bytes(m)

def pressure_manifest(base,count):
    m=copy.deepcopy(base)
    m["lesion"]=lesion_for(m["seed"],count)
    m["manifest_sha256"]=t.manifest_identity(m)
    if nonlesion_bytes(m)!=nonlesion_bytes(base):
        raise AssertionError("A19 nonlesion mutation")
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

def stream_failures(anchor_rows,current_rows):
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
                        "current":cur_n,
                        "ratio":cur_n/base_n if base_n else None,
                    })
    return failures

def run_count(count,anchor_rows):
    base=t.primary_manifests(a8.A1_PREREG)
    manifests=[pressure_manifest(m,count) for m in base]
    mech=a8.mechanical()

    old_validate=t.validate_manifest
    old_lesion=p.lesion_set
    old_schedule=a8.damage_schedule
    old_alpha=float(g.ALPHA)

    t.validate_manifest=pressure_validate
    p.lesion_set=lambda seed:set(lesion_for(seed,count))
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
    on_total=sum(x["result"]["correct_done"] for x in on_rows)
    off_total=sum(x["result"]["correct_done"] for x in off_rows)
    damage_ratio=on_total/off_total if off_total else None
    vs_l8=on_total/1450.0

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
        len(r["manifest"]["lesion"])==count
        and r["manifest"]["lesion"]==lesion_for(r["manifest"]["seed"],count)
        and set(inherited_l8(r["manifest"]["seed"])).issubset(r["manifest"]["lesion"])
        for r in rows
    )
    nonlesion_exact=all(nonlesion_bytes(m)==nonlesion_bytes(b) for m,b in zip(manifests,base))
    failures=stream_failures(anchor_rows,rows)

    q={
        "mechanical_gate":bool(mech["all_pass"]),
        "exact_nested_lesion_construction":bool(lesion_exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion_exact),
        "branch_schedule_and_repair_exact_58":bool(branch_exact),
        "damaged_terminal_integrity_exact":bool(integrity),
        "aggregate_damage_ratio_ge_095":damage_ratio is not None and damage_ratio>=0.95,
        "all_world_damage_ratio_ge_090":all(
            r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90 for r in rows
        ),
        "damage_on_vs_l8_damage_on_ge_090":vs_l8>=0.90,
        "learned_arm_materially_exercised":any(r["learned_state_diverged"] for r in rows),
    }
    return {
        "lesion_cells":count,
        "aggregate":{
            "a25_off_correct_done":off_total,
            "a25_on_correct_done":on_total,
            "a25_damage_ratio":damage_ratio,
            "a25_damage_on_vs_a15_l8_damage_on":vs_l8,
            "stream_noncollapse":len(failures)==0,
            "stream_failures":failures,
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

    first12=run_count(12,anchor["rows"])
    first13=run_count(13,anchor["rows"])
    second12=run_count(12,anchor["rows"])
    second13=run_count(13,anchor["rows"])

    run1={"l12":first12,"l13":first13}
    run2={"l12":second12,"l13":second13}
    b1=canonical(run1)
    b2=canonical(run2)

    l12_fail=[
        {
            "replicate":x["replicate"],
            "phase":x["phase"],
            "stream":x["stream"],
            "l8":x["l8"],
            "l12":x["current"],
            "ratio":x["ratio"],
        }
        for x in first12["aggregate"]["stream_failures"]
    ]
    nesting=all(
        set(first12["rows"][i]["manifest"]["lesion"]).issubset(first13["rows"][i]["manifest"]["lesion"])
        and len(set(first13["rows"][i]["manifest"]["lesion"])-set(first12["rows"][i]["manifest"]["lesion"]))==1
        for i in range(len(first12["rows"]))
    )

    restoration={
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "lesion_set_restored":p.lesion_set is original_lesion,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
    }
    validity={
        "a15_alpha100_anchor_exact":anchor_hash==A15_ALPHA100_HASH,
        "l12_accepted_failure_exact":l12_fail==EXPECTED_L12_FAILURE,
        "l12_strict_subset_l13_one_cell":bool(nesting),
        "duplicate_l12_l13_execution_byte_identical":b1==b2,
        **restoration,
    }
    l12_q=first12["qualification"]
    l13_q=first13["qualification"]
    qualification={
        "l12_integrity_and_capability_gates":bool(all(l12_q.values())),
        "l13_integrity_and_capability_gates":bool(all(l13_q.values())),
        "l12_stream_noncollapse":bool(first12["aggregate"]["stream_noncollapse"]),
        "l13_stream_noncollapse":bool(first13["aggregate"]["stream_noncollapse"]),
    }
    qualification["YGG_A19_L12_TO_L13_SINGLE_CELL_RECOVERY"]=bool(
        all(validity.values())
        and qualification["l12_integrity_and_capability_gates"]
        and qualification["l13_integrity_and_capability_gates"]
        and not qualification["l12_stream_noncollapse"]
        and qualification["l13_stream_noncollapse"]
    )

    out={
        "schema":1,
        "experiment":"YGG-A19",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "a15_alpha100_anchor_sha256":anchor_hash,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "l12":first12,
        "l13":first13,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
