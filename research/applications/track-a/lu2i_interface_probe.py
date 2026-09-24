#!/usr/bin/env python3
import inspect, json, sys
from pathlib import Path
import lu2g_second_task_compositional_service_transfer_v1 as frozen

g=frozen.g
out={"values":{},"functions":{}}
for name in sorted(dir(g)):
    if name.startswith("_"): continue
    obj=getattr(g,name)
    if name.isupper():
        try: json.dumps(obj); out["values"][name]=obj
        except Exception: pass
    if inspect.isfunction(obj):
        try:
            src=inspect.getsource(obj)
        except Exception:
            continue
        if (
            "REQUESTS_PER_EPOCH" in src or
            "primary_manifests" in name or
            "validate_manifest" in name or
            "arrival" in name.lower() or
            "manifest" in name.lower() or
            "phase" in src and "request" in src.lower()
        ):
            out["functions"][name]={"signature":str(inspect.signature(obj)),"source":src}
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
