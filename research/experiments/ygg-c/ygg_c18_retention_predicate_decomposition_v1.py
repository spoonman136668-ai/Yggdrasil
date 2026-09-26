#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c17_interaction_onset_functional_pressure_v1 as c17
PREREG="7694c5079859a1ae014b2e7a258e1aae7a0a9486"
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def one_pass():
    data=c17.one_pass()
    pressure={str(r["alpha"]):r for r in data["pressure"]}
    rows=[]
    for alpha in c17.ALPHAS:
        r=pressure[str(alpha)]
        levels=[]
        for level in sorted(int(k) for k in r["retained_by_level"]):
            key=str(level)
            levels.append({"level":level,"retained":bool(r["retained_by_level"][key]),
              "summary":r["levels"][key] if "levels" in r and key in r["levels"] else None})
        rows.append({"alpha":alpha,"retained_by_level":r["retained_by_level"],"levels":levels})
    return {"rows":rows}
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); same=canonical(a)==canonical(b)
    false_accounted=True
    for arm in a["rows"]:
        for row in arm["levels"]:
            if not row["retained"] and row["summary"] is None: false_accounted=False
    out={"schema":1,"experiment":"YGG-C18","prereg":PREREG,
      "duplicate_sha256":hashlib.sha256(canonical(a)).hexdigest(),
      "valid":bool(same and false_accounted),
      "qualification":{"YGG_C18_RETENTION_PREDICATE_DECOMPOSITION":bool(same and false_accounted)},
      "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
