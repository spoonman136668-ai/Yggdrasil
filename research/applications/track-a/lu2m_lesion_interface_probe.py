#!/usr/bin/env python3
import inspect, json, sys
from pathlib import Path
import lu2l_l1_learned_u_transfer_v1 as x

mods={"p":x.p,"g":x.g}
names={
  "p":["lesion_set","phase_of","anchors_for","validate_manifest"],
  "g":["run_world","run_pair","validate_manifest","run_task2_world"],
}
out={"constants":{},"sources":{}}
for k in ["N","T","D","R_TASK","EXPIRY","LESION_START","LESION_END","LESION_SIZE"]:
    if hasattr(x.p,k):
        out["constants"][k]=getattr(x.p,k)
for mname,nlist in names.items():
    mod=mods[mname]
    for name in nlist:
        key=f"{mname}.{name}"
        obj=getattr(mod,name,None)
        if obj is None:
            out["sources"][key]=None
        else:
            try: out["sources"][key]=inspect.getsource(obj)
            except Exception as e: out["sources"][key]=f"<unavailable:{type(e).__name__}:{e}>"
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
