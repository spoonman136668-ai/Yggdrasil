#!/usr/bin/env python3
"""Read-only YGG-A2 inspector for dynamically reconstructed frozen LU2G source."""
from __future__ import annotations
import ast, base64, gzip, hashlib, json, subprocess, sys
from pathlib import Path

TRACK=Path(__file__).resolve().parents[2]/"applications"/"track-a"
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path("a2-inspector")
OUT.mkdir(parents=True,exist_ok=True)

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def constants(path:Path):
    tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
    out={}
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try: out[n.targets[0].id]=ast.literal_eval(n.value)
            except Exception: pass
    return out

def segment(src:str,node:ast.AST)->str:
    s=ast.get_source_segment(src,node)
    if s is None: raise RuntimeError("AST_SOURCE_SEGMENT_MISSING")
    return s

outer=TRACK/"lu2g_second_task_compositional_service_transfer_v1.py"
oc=constants(outer)
parts=sorted(TRACK.glob("lu2g_second_task_compositional_service_transfer_v1.source.chunk*.b64"))
encoded="".join(p.read_text(encoding="ascii").strip() for p in parts)
gz=base64.b64decode(encoded,validate=True)
srcb=gzip.decompress(gz)
if len(parts)!=oc["EXPECTED_PARTS"]: raise RuntimeError("OUTER_PART_COUNT")
if len(encoded)!=oc["EXPECTED_B64_CHARS"] or sha(encoded.encode("ascii"))!=oc["EXPECTED_B64_SHA256"]: raise RuntimeError("OUTER_B64_IDENTITY")
if len(gz)!=oc["EXPECTED_GZIP_BYTES"] or sha(gz)!=oc["EXPECTED_GZIP_SHA256"]: raise RuntimeError("OUTER_GZIP_IDENTITY")
if len(srcb)!=oc["EXPECTED_SOURCE_BYTES"] or sha(srcb)!=oc["EXPECTED_SOURCE_SHA256"]: raise RuntimeError("OUTER_SOURCE_IDENTITY")
outer_src=srcb.decode("utf-8")
outer_tree=ast.parse(outer_src,filename="<frozen-lu2g-outer>")

candidate=TRACK/"lu2g_second_task_compositional_service_transfer_v1.candidate.py"
cc=constants(candidate)
cgz=base64.b64decode(cc["ENCODED"],validate=True)
csrcb=gzip.decompress(cgz)
if len(cgz)!=cc["EXPECTED_GZIP_BYTES"] or sha(cgz)!=cc["EXPECTED_GZIP_SHA256"]: raise RuntimeError("CANDIDATE_GZIP_IDENTITY")
if len(csrcb)!=cc["EXPECTED_SOURCE_BYTES"] or sha(csrcb)!=cc["EXPECTED_SOURCE_SHA256"]: raise RuntimeError("CANDIDATE_SOURCE_IDENTITY")
candidate_src=csrcb.decode("utf-8")
tree=ast.parse(candidate_src,filename="<frozen-lu2g-candidate>")

defs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
if "run_world" not in defs: raise RuntimeError("RUN_WORLD_NOT_FOUND")
run=defs["run_world"]
names=sorted({n.id for n in ast.walk(run) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)})
related=[n for n in names if n in defs]

diagnostics={
 "schema":1,
 "outer_loader":str(outer.relative_to(TRACK.parent.parent.parent)),
 "outer_loader_sha256":sha(outer.read_bytes()),
 "outer_source_bytes":len(srcb),
 "outer_source_sha256":sha(srcb),
 "outer_top_level_defs":sorted(n.name for n in outer_tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))),
 "candidate_loader_sha256":sha(candidate.read_bytes()),
 "candidate_source_bytes":len(csrcb),
 "candidate_source_sha256":sha(csrcb),
 "candidate_source_lines":len(candidate_src.splitlines()),
 "run_world_lineno":run.lineno,
 "run_world_end_lineno":run.end_lineno,
 "run_world_global_def_refs":related,
}
(OUT/"inspector_diagnostics.json").write_text(json.dumps(diagnostics,sort_keys=True,indent=2)+"\n",encoding="utf-8")
(OUT/"run_world.py.txt").write_text(segment(candidate_src,run)+"\n",encoding="utf-8")
with (OUT/"related_defs.py.txt").open("w",encoding="utf-8",newline="\n") as h:
    for name in related:
        h.write(f"\n# === {name} ===\n")
        h.write(segment(candidate_src,defs[name]))
        h.write("\n")
print("YGG_A2_INSPECTOR_DIAGNOSTICS="+json.dumps(diagnostics,sort_keys=True))
print("===RUN_WORLD_AST_SOURCE===")
print(segment(candidate_src,run))
for name in related:
    print(f"===GLOBAL_AST_SOURCE {name}===")
    print(segment(candidate_src,defs[name]))
print("YGG_A2_INSPECTOR_PASS=true")

# Optional read-only continuation diagnostic. Reuse the already-authorized
# a2_dev inspector lane rather than adding a competing execution path.
control_path=Path(__file__).resolve().parents[2]/"control"/"ygg-a-run.json"
try:
    control=json.loads(control_path.read_text(encoding="utf-8"))
except Exception:
    control={}
if str(control.get("request_id","")).startswith("YGG-A3-TERMINAL-OBSERVABILITY-DIAG"):
    diag=Path(__file__).with_name("ygg_a3_terminal_observability_diagnostic_v1.py")
    diag_out=OUT/"a3-diagnostic.json"
    subprocess.check_call([sys.executable,str(diag),str(diag_out)])
    print("===YGG_A3_TERMINAL_OBSERVABILITY===")
    print(diag_out.read_text(encoding="utf-8"))
    print("YGG_A3_DIAGNOSTIC_PASS=true")

# YGG-A3 read-only continuation: execute the bounded replicate-10
# terminal-observability diagnostic after the frozen scheduler inspection.
import ygg_a3_terminal_observability_diagnostic_v1 as a3diag
_saved_argv=sys.argv
try:
    sys.argv=[str(Path(a3diag.__file__)),str(OUT/"a3-terminal-observability.json")]
    a3diag.main()
finally:
    sys.argv=_saved_argv
print("YGG_A3_TERMINAL_OBSERVABILITY_DIAGNOSTIC_PASS=true")
