#!/usr/bin/env python3
import importlib, inspect, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
m=importlib.import_module("lu2a_partial_learned_hu_closed_loop_v1")

out={}
for name in sorted(dir(m)):
    if name.startswith("_"):
        continue
    obj=getattr(m,name)
    if callable(obj):
        try:
            sig=str(inspect.signature(obj))
        except Exception:
            sig="<unavailable>"
        out[name]={"kind":"callable","signature":sig}
    elif name.isupper():
        try:
            json.dumps(obj)
            out[name]={"kind":"value","value":obj}
        except Exception:
            pass

path=Path(sys.argv[1])
path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
