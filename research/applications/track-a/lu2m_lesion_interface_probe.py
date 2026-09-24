#!/usr/bin/env python3
import inspect, json, sys
from pathlib import Path
import task1f_local_hedge_ambiguity_r1_v1 as p

names=[
  "lesion_set",
  "phase_of",
  "anchors_for",
  "run_task",
  "validate_manifest",
]
out={
  "constants":{k:getattr(p,k,None) for k in ["N","T","D","R_TASK","EXPIRY","LESION_START","LESION_END","LESION_SIZE"] if hasattr(p,k)},
  "sources":{}
}
for name in names:
    obj=getattr(p,name,None)
    if obj is None:
        out["sources"][name]=None
    else:
        try: out["sources"][name]=inspect.getsource(obj)
        except Exception as e: out["sources"][name]=f"<unavailable:{type(e).__name__}:{e}>"
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
