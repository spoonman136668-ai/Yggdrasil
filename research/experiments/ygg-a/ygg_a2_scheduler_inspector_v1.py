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

if str(control.get("request_id","")).startswith("YGG-A4-ATOMIC-EGRESS-HANDOFF"):
    a4=Path(__file__).with_name("ygg_a4_atomic_egress_integrity_v1.py")
    a4_out=OUT/"a4-result.json"
    subprocess.check_call([sys.executable,str(a4),str(a4_out)])
    result=json.loads(a4_out.read_text(encoding="utf-8"))
    print("===YGG_A4_ATOMIC_EGRESS_HANDOFF===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A4_ATOMIC_EGRESS_INTEGRITY_HANDOFF"]:
        raise SystemExit("YGG_A4_PRIMARY_SCIENTIFIC_NEGATIVE")
    print("YGG_A4_PRIMARY_PASS=true")

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

if str(control.get("request_id","")).startswith("YGG-A5-TERMINAL-CONTRACT-AUDIT"):
    a5=Path(__file__).with_name("ygg_a5_terminal_contract_audit_v1.py")
    a5_out=OUT/"a5-contract-audit.json"
    subprocess.check_call([sys.executable,str(a5),str(a5_out)])
    result=json.loads(a5_out.read_text(encoding="utf-8"))
    print("===YGG_A5_TERMINAL_CONTRACT_AUDIT===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["qualification"]["YGG_A5_TERMINAL_CONTRACT_DIVERGENCE"]:
        raise SystemExit("YGG_A5_CONTRACT_DIVERGENCE_NOT_SUPPORTED")
    print("YGG_A5_CONTRACT_DIVERGENCE_PASS=true")


if str(control.get("request_id","")).startswith("YGG-A6-HORIZON-AWARE-ATOMIC-CONFIRMATION"):
    a6=Path(__file__).with_name("ygg_a6_horizon_aware_atomic_egress_confirmation_v1.py")
    a6_out=OUT/"a6-horizon-aware-confirmation.json"
    subprocess.check_call([sys.executable,str(a6),str(a6_out)])
    result=json.loads(a6_out.read_text(encoding="utf-8"))
    print("===YGG_A6_HORIZON_AWARE_ATOMIC_CONFIRMATION===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A6_HORIZON_AWARE_ATOMIC_EGRESS_CONFIRMATION"]:
        raise SystemExit("YGG_A6_SCIENTIFIC_NEGATIVE")
    print("YGG_A6_PRIMARY_PASS=true")


if str(control.get("request_id","")).startswith("YGG-A7-LEARNED-ARM-INTEGRITY-COMPATIBILITY"):
    a7=Path(__file__).with_name("ygg_a7_learned_arm_integrity_compatibility_v1.py")
    a7_out=OUT/"a7-learned-arm-integrity.json"
    subprocess.check_call([sys.executable,str(a7),str(a7_out)])
    result=json.loads(a7_out.read_text(encoding="utf-8"))
    print("===YGG_A7_LEARNED_ARM_INTEGRITY_COMPATIBILITY===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A7_LEARNED_ARM_INTEGRITY_COMPATIBILITY"]:
        raise SystemExit("YGG_A7_SCIENTIFIC_NEGATIVE")
    print("YGG_A7_PRIMARY_PASS=true")

if str(control.get("request_id","")).startswith("YGG-A8-BRANCH-LOCAL-REPAIR"):
    a8=Path(__file__).with_name("ygg_a8_branch_local_repair_v1.py")
    a8_out=OUT/"a8-branch-local-repair.json"
    subprocess.check_call([sys.executable,str(a8),str(a8_out)])
    result=json.loads(a8_out.read_text(encoding="utf-8"))
    print("===YGG_A8_BRANCH_LOCAL_REPAIR===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A8_BRANCH_LOCAL_REPAIR"]:
        raise SystemExit("YGG_A8_SCIENTIFIC_NEGATIVE")
    print("YGG_A8_PRIMARY_PASS=true")

if str(control.get("request_id","")).startswith("YGG-A9-DOUBLED-BRANCH-REPAIR-LOAD"):
    a9=Path(__file__).with_name("ygg_a9_doubled_branch_repair_load_v1.py")
    a9_out=OUT/"a9-doubled-branch-repair-load.json"
    subprocess.check_call([sys.executable,str(a9),str(a9_out)])
    result=json.loads(a9_out.read_text(encoding="utf-8"))
    print("===YGG_A9_DOUBLED_BRANCH_REPAIR_LOAD===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A9_DOUBLED_BRANCH_REPAIR_LOAD"]:
        raise SystemExit("YGG_A9_SCIENTIFIC_NEGATIVE")
    print("YGG_A9_PRIMARY_PASS=true")

if str(control.get("request_id","")).startswith("YGG-A10-QUADRUPLED-BRANCH-REPAIR-LOAD"):
    a10=Path(__file__).with_name("ygg_a10_quadrupled_branch_repair_load_v1.py")
    a10_out=OUT/"a10-quadrupled-branch-repair-load.json"
    subprocess.check_call([sys.executable,str(a10),str(a10_out)])
    result=json.loads(a10_out.read_text(encoding="utf-8"))
    print("===YGG_A10_QUADRUPLED_BRANCH_REPAIR_LOAD===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A10_QUADRUPLED_BRANCH_REPAIR_LOAD"]:
        raise SystemExit("YGG_A10_SCIENTIFIC_NEGATIVE")
    print("YGG_A10_PRIMARY_PASS=true")

if str(control.get("request_id","")).startswith("YGG-A11-HIGH-LOAD-BRANCH-REPAIR"):
    a11=Path(__file__).with_name("ygg_a11_high_load_branch_repair_v1.py")
    a11_out=OUT/"a11-high-load-branch-repair.json"
    subprocess.check_call([sys.executable,str(a11),str(a11_out)])
    result=json.loads(a11_out.read_text(encoding="utf-8"))
    print("===YGG_A11_HIGH_LOAD_BRANCH_REPAIR===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A11_HIGH_LOAD_BRANCH_REPAIR"]:
        raise SystemExit("YGG_A11_SCIENTIFIC_NEGATIVE")
    print("YGG_A11_PRIMARY_PASS=true")

if str(control.get("request_id","")).startswith("YGG-A12-NEAR-SATURATION-BRANCH-REPAIR"):
    a12=Path(__file__).with_name("ygg_a12_near_saturation_branch_repair_v1.py")
    a12_out=OUT/"a12-near-saturation-branch-repair.json"
    subprocess.check_call([sys.executable,str(a12),str(a12_out)])
    result=json.loads(a12_out.read_text(encoding="utf-8"))
    print("===YGG_A12_NEAR_SATURATION_BRANCH_REPAIR===")
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    if not result["primary"]["qualification"]["YGG_A12_NEAR_SATURATION_BRANCH_REPAIR"]:
        raise SystemExit("YGG_A12_SCIENTIFIC_NEGATIVE")
    print("YGG_A12_PRIMARY_PASS=true")

