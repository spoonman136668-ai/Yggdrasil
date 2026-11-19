"""Read-only CAP01 sealed-model replay drift diagnosis, no new science actions."""
from __future__ import annotations
import json
from pathlib import Path
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA

ROOT=Path(__file__).resolve().parents[4]
PARENT=ROOT/"research/contrib/chatgpt/YGG-CAP01/original/linux"
OLD_SHA={
    14071:"6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14",
    14072:"c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827",
}

def difference(x,y,p="$",found=None):
    if found is None:
        found=[]
    if type(x) is not type(y):
        found.append([p,"type",str(type(x)),str(type(y))])
    elif isinstance(x,dict):
        if set(x)!=set(y):
            found.append([p,"keys",sorted(x),sorted(y)])
        for k in sorted(set(x)&set(y)):
            if k in ("ascii","archive_ascii"): # nested exact strings reported separately
                if x[k]!=y[k]:
                    found.append([p+"."+k,"nested-ascii",len(x[k]),len(y[k])])
            else:
                difference(x[k],y[k],p+"."+k,found)
    elif isinstance(x,list):
        if len(x)!=len(y):
            found.append([p,"length",len(x),len(y)])
        for i,(a,b) in enumerate(zip(x,y)):
            difference(a,b,p+"["+str(i)+"]",found)
    elif x!=y:
        if isinstance(x,(float,int)) and isinstance(y,(float,int)):
            found.append([p,"numeric",x,y,abs(x-y)])
        else:
            found.append([p,"exact",str(x)[:160],str(y)[:160]])
    return found

for seed,pin in OLD_SHA.items():
    entry=json.loads((PARENT/f"seed-{seed}-state.json").read_bytes())
    raw=entry["continued_ascii"].encode("ascii")
    assert digest(raw)==pin
    expected=json.loads(raw)
    archive=expected["archive_ascii"].encode("ascii")
    model=SegmentedNativeJEPA.from_archive(archive,expected["archive_sha256"])
    for e in expected["events"]:
        views=tuple(tuple(v) for v in e["views"])
        post=tuple(e["post"])
        model=model.observe(e["identifier"],views,{
            "s1":views[0][0],"x1":e["first"],
            "s2":e["state"],"x2":e["second"],"y":e["reward"],
        },post)
    actual=model.checkpoint()
    try:
        restored=SegmentedNativeJEPA.restore(raw,pin)
        restore_result=("PASS",restored.checkpoint()==raw)
    except ValueError as exc:
        restore_result=("FAIL",str(exc),repr(exc.__cause__))
    print("CAP02_RESTORE_DIAGNOSTIC",seed,restore_result,flush=True)
    d=difference(expected,json.loads(actual))
    nums=[v for v in d if v[1]=="numeric"]
    structural=[v for v in d if v[1] not in ("numeric","nested-ascii")]
    print("CAP02_CUSTODY_READONLY_DRIFT_DIAGNOSTIC",
          "prior_seed",seed,"saved_sha",pin,
          "rebuilt_sha",digest(actual),"bytes",len(raw),len(actual),
          "numeric_field_differences",len(nums),
          "max_numeric_delta",max((x[4] for x in nums),default=0),
          "structural_differences",len(structural),
          "first_structural",structural[:5],
          "first_numerical",nums[:6],flush=True)
