#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

import torch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27
import ygg_b29_read1_interference_attribution_v1 as b29

PREREG="8f364c6cda0a4932acc7c7e5ea9ccf9d80bec10f"
PARENT_CLOSURE="3d15770c538b9009131f12de0d21b7e637f15294"
THRESHOLD=0.90
POSITIONS=tuple(range(7))

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def seed_result(seed):
    model=b29.train_model(seed,True)
    xev,y1ev,_y2,q1ev,*_=b27.evaluation_data(seed,b27.EVAL_N)
    model.eval()
    with torch.no_grad():
        logits=b29.immediate_read1_logits(model,xev)
        pred=logits.argmax(dim=1)

    rows=[]
    for pos in POSITIONS:
        mask=(q1ev==pos)
        count=int(mask.sum().item())
        if count<=0:
            raise AssertionError("B30 empty write position")
        acc=float((pred[mask]==y1ev[mask]).float().mean().item())
        rows.append({"position":pos,"count":count,"accuracy":acc})

    return {
        "seed":seed,
        "positions":rows,
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":b27.PERSISTENT_SCALARS,
    }

def classify(rows):
    mins={}
    for pos in POSITIONS:
        mins[str(pos)]=min(
            next(x["accuracy"] for x in row["positions"] if x["position"]==pos)
            for row in rows
        )
    capable={pos:(mins[str(pos)]>=THRESHOLD) for pos in POSITIONS}
    threshold_ks=[
        k for k in range(1,7)
        if all(not capable[p] for p in range(0,k))
        and all(capable[p] for p in range(k,7))
    ]
    if len(threshold_ks)==1:
        category="AGE_THRESHOLD_PATTERN"
    elif all(not capable[p] for p in POSITIONS):
        category="BROAD_PREFIX_LIMIT"
    elif all(capable[p] for p in POSITIONS):
        category="NO_REPRODUCED_POSITION_LIMIT"
    else:
        category="POSITION_SPECIFIC_NONMONOTONIC"
    return {
        "classification":category,
        "minimum_accuracy_by_position":mins,
        "capable_by_position":{str(k):v for k,v in capable.items()},
        "threshold_k":threshold_ks[0] if len(threshold_ks)==1 else None,
    }

def one_pass():
    rows=[seed_result(seed) for seed in b27.SEEDS]
    return {"rows":rows,"attribution":classify(rows)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=b27.mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B30_MECHANICAL_GATE_FAILED")
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)
    allowed={
        "AGE_THRESHOLD_PATTERN","POSITION_SPECIFIC_NONMONOTONIC",
        "BROAD_PREFIX_LIMIT","NO_REPRODUCED_POSITION_LIMIT",
    }
    validity={
        "mechanical_gate":bool(mech["all_pass"]),
        "threshold_inherited_exact":THRESHOLD==0.90,
        "positions_exact":list(POSITIONS)==list(range(7)),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "all_positions_populated":all(
            len(r["positions"])==7 and all(x["count"]>0 for x in r["positions"])
            for r in first["rows"]
        ),
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in first["rows"]),
        "parameter_count_exactly_120":all(r["parameter_count"]==120 for r in first["rows"]),
    }
    category=first["attribution"]["classification"]
    out={
        "schema":1,
        "experiment":"YGG-B30",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "inherited_threshold":THRESHOLD,
        "mechanical":mech,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_B30_READ1_WRITE_POSITION_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
            **first["attribution"],
        },
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
