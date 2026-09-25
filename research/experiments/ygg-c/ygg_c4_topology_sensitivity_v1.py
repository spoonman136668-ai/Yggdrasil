#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c3_resource_pressure_retention_v1 as c3

PREREG="03a1a58172326e86e33f834d8a2d3d25d4a862aa"
PARENT_CLOSURE="8fb0d5fcb5aeaf3379f02ea680fd4728984f80e4"
EXPECTED_PARENT_HASH="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"
N=64
COUNT=16
C3_PRESSURE=c3.pressure_lesion
NAMES=("HASH16","CONTIGUOUS16","EVEN16","TWO_ARC16","FOUR_ARC16")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def topo(name,seed):
    if name=="HASH16":
        return sorted(C3_PRESSURE(seed,16))
    if name=="CONTIGUOUS16":
        s=c3.lu2v.p.h64("YGG-C4-CONTIGUOUS",seed)%64
        return sorted({(s+i)%64 for i in range(16)})
    if name=="EVEN16":
        o=c3.lu2v.p.h64("YGG-C4-EVEN",seed)%4
        return [o+4*i for i in range(16)]
    if name=="TWO_ARC16":
        s=c3.lu2v.p.h64("YGG-C4-TWO-ARC",seed)%32
        return sorted({(s+i)%64 for i in range(8)}|{(s+32+i)%64 for i in range(8)})
    if name=="FOUR_ARC16":
        s=c3.lu2v.p.h64("YGG-C4-FOUR-ARC",seed)%16
        cells=set()
        for base in (s,s+16,s+32,s+48):
            cells.update((base+i)%64 for i in range(4))
        return sorted(cells)
    raise ValueError(name)

def run_topology(base,name):
    old=c3.pressure_lesion
    c3.pressure_lesion=lambda seed,count: topo(name,seed)
    try:
        manifests=[c3.pressure_manifest(m,16) for m in base]
        for m in manifests:
            if len(m["lesion"])!=16 or len(set(m["lesion"]))!=16:
                raise AssertionError("topology cardinality")
        rows=[c3.run_pressure_manifest(m,16) for m in manifests]
        return {"name":name,"manifests":manifests,"rows":rows}
    finally:
        c3.pressure_lesion=old

def one_pass():
    base=c3.lu2v.primary_manifests(c3.LU2VF1)
    parent=[c3.lu2v.run_pair(m) for m in base]
    groups=[run_topology(base,n) for n in NAMES]
    summaries=[]
    for g in groups:
        s=c3.summarize_level(16,g["rows"],parent)
        s["topology"]=g["name"]
        summaries.append(s)
    return {"parent":parent,"groups":groups,"summaries":summaries}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass()
    ba=canonical(a); bb=canonical(b)
    parent_hash=hashlib.sha256(canonical(a["parent"])).hexdigest()
    retained=[x["retained"] for x in a["summaries"]]
    checks={
        "duplicate_complete_execution_byte_identical":ba==bb,
        "parent_reference_hash_exact":parent_hash==EXPECTED_PARENT_HASH,
        "all_topologies_cardinality_16":all(len(m["lesion"])==16 and len(set(m["lesion"]))==16 for g in a["groups"] for m in g["manifests"]),
        "all_matching_integrity":all(x["a25_matching_integrity"] for x in a["summaries"]),
    }
    q={
        "YGG_C4_TOPOLOGY_SENSITIVITY":bool(any(retained) and not all(retained)),
        "at_least_one_retained":bool(any(retained)),
        "at_least_one_not_retained":bool(not all(retained)),
        "summaries":a["summaries"],
    }
    out={"schema":1,"experiment":"YGG-C4","prereg":PREREG,"parent_closure":PARENT_CLOSURE,
         "parent_reference_sha256":parent_hash,"validity":checks,"valid":all(checks.values()),
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"qualification":q}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
