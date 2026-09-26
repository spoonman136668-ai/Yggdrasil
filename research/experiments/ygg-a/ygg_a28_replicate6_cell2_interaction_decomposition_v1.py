#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a27_cell2_portability_v1 as a27

PREREG="7da272e4d8924051bba9c98449c0ee70bcc4e999"
PARENT_RUN="36229807712"
TARGET_CELL=2
MODES=("U_A0","U_A25")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def base6():
    rows=[m for m in a27.t.primary_manifests(a27.a8.A1_PREREG) if int(m["replicate"])==6]
    if len(rows)!=1: raise AssertionError("A28 replicate6 uniqueness")
    return rows[0]

def make_manifest(base, lesion):
    m=copy.deepcopy(base); m["lesion"]=sorted(lesion); m["manifest_sha256"]=a27.t.manifest_identity(m)
    if a27.a19.nonlesion_bytes(m)!=a27.a19.nonlesion_bytes(base): raise AssertionError("A28 nonlesion mutation")
    return m

def score(mode, lesion):
    base=base6(); m=make_manifest(base,lesion)
    old_validate=a27.t.validate_manifest; old_lesion=a27.p.lesion_set; old_alpha=float(a27.g.ALPHA)
    a27.g.ALPHA=a27.ALPHA; a27.t.validate_manifest=a27.a22.pressure_validate
    try:
        a27.p.lesion_set=lambda seed:set(lesion)
        row=a27.a8.scored(m,mode,False)
    finally:
        a27.t.validate_manifest=old_validate; a27.p.lesion_set=old_lesion; a27.g.ALPHA=old_alpha
    return row

def collapsed(anchor,row):
    failures=[]
    br=anchor["result"]["stream_phase"]; cr=row["result"]["stream_phase"]
    for ph in range(5):
        ps=str(ph)
        for stream in ("C","S"):
            b=br[ps][stream]; c=cr[ps][stream]
            if b>=4 and c<0.75*b:
                failures.append({"phase":ph,"stream":stream,"anchor":b,"current":c,"ratio":c/b})
    return failures

def one_mode(mode):
    base=base6(); l11=sorted(a27.anchor_lesion(base["seed"]))
    if TARGET_CELL in l11 or len(l11)!=11: raise AssertionError("A28 anchor")
    anchor=score(mode,l11); positive=score(mode,sorted(l11+[TARGET_CELL]))
    pc=collapsed(anchor,positive)
    arms=[]
    for removed in l11:
        lesion=sorted([x for x in l11 if x!=removed]+[TARGET_CELL])
        row=score(mode,lesion); fs=collapsed(anchor,row)
        arms.append({"removed_cell":removed,"collapse":bool(fs),"failures":fs,"correct_done":row["result"]["correct_done"],
                     "maturity_pass":bool(row["maturity"]["pass"]),"incorrect_done":row["result"]["incorrect_done"],
                     "matching_duplicate_cell":row["result"]["matching_duplicate_cell"],
                     "matching_duplicate_request":row["result"]["matching_duplicate_request"],
                     "branch_scheduled":row["branch"]["scheduled"],"branch_applied":row["branch"]["applied"],"branch_repaired":row["branch"]["repaired"]})
    return {"mode":mode,"replicate":int(base["replicate"]),"l11":l11,"positive_control_collapse":bool(pc),
            "positive_control_failures":pc,"abolishing_cells":sorted(x["removed_cell"] for x in arms if not x["collapse"]),"arms":arms}

def classify(rows):
    sets=[r["abolishing_cells"] for r in rows]
    if sets[0]!=sets[1]: return "CROSS_MODE_INTERACTION"
    if len(sets[0])==0: return "DISTRIBUTED_CONTEXT"
    if len(sets[0])==1: return "SINGLE_NECESSARY_PARTNER"
    if len(sets[0])>1: return "MULTIPLE_NECESSARY_PARTNERS"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allowed={"SINGLE_NECESSARY_PARTNER","MULTIPLE_NECESSARY_PARTNERS","CROSS_MODE_INTERACTION","DISTRIBUTED_CONTEXT","OTHER_VALID_PATTERN"}
    validity={
      "duplicate_complete_execution_byte_identical":b1==b2,
      "actual_replicate6_verified":all(r["replicate"]==6 for r in first["rows"]),
      "target_cell_exact":TARGET_CELL==2,
      "alpha_exact":a27.ALPHA==0.25,
      "positive_control_reproduced":all(r["positive_control_collapse"] for r in first["rows"]),
      "eleven_leave_one_out_arms":all(len(r["arms"])==11 for r in first["rows"]),
      "arm_integrity":all(all(a["maturity_pass"] and a["incorrect_done"]==0 and a["matching_duplicate_cell"]==0 and a["matching_duplicate_request"]==0 and a["branch_scheduled"]==0 and a["branch_applied"]==0 and a["branch_repaired"]==0 for a in r["arms"]) for r in first["rows"]),
    }
    cat=first["classification"]
    out={"schema":1,"experiment":"YGG-A28","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A28_REPLICATE6_CELL2_INTERACTION_DECOMPOSITION":bool(all(validity.values()) and cat in allowed),"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
