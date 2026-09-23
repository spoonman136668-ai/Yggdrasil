#!/usr/bin/env python3
import json, runpy, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/"research/applications/track-a/task1f_local_hedge_ambiguity_r1_v1.py"

def public_interface():
    ns=runpy.run_path(str(PARENT), run_name="task1f_parent")
    out={}
    for k,v in sorted(ns.items()):
        if k.startswith("_"):
            continue
        if callable(v):
            out[k]={"kind":"callable","repr":repr(v)}
        elif k.isupper() or k in {"T","N","R_TASK"}:
            try:
                json.dumps(v)
                out[k]={"kind":"value","value":v}
            except TypeError:
                pass
    return out

def main():
    if len(sys.argv)!=3 or sys.argv[1]!="interface":
        raise SystemExit("usage: ... interface OUT")
    out=Path(sys.argv[2])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(public_interface(),sort_keys=True,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
