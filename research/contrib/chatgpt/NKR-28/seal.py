"""Preserve composition audit without rewriting preceding frozen studies."""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit import stable
linux=json.loads(os.environ["NKR28_LINUX_RESULT"])
windows=json.loads(os.environ["NKR28_WINDOWS_RESULT"])
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if stable(linux)!=stable(windows) or any(d["source_candidate_sha"]!=source for d in (linux,windows)):
    raise RuntimeError("NKR28_SOURCE_OR_STABLE_DRIFT")
for name,d in (("result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
provenance={"schema":"yggdrasil.nkr28.full-image-composition.provenance.v1",
 "prereg_sha":os.environ["NKR28_PREREG_SHA"],"source_sha":source,
 "run_id":os.environ["GITHUB_RUN_ID"],"parent_pr":1172,"compiled_image_artifact":14220169461,
 "original_fault_checkpoint":linux["fault_checkpoint_sha256"],
 "separate_repaired_checkpoint":linux["repaired_checkpoint_sha256"],
 "new_original_source_actions":0,"scientific_pass":False,"native_accepted":False,
 "qualification":"final exact-source root/NKR05/G29 both OS pending at evidence commit; see terminal PR receipt"}
(HERE/"provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
lines=["# NKR28: can repaired factual memory still be used?","",
"The full21,343,681-row historical image was present. This engineering audit",
"applied the EXISTING bounded two-hop graph operator through the existing",
"NativeKnowledgeSession interface. A small compatibility wrapper lets a",
"repaired candidate answer the same compositional queries as factual memory.","",
"Eligible query contexts:"+str(linux["eligible_contexts"]),
"Fixed broad indexed sample:"+str(linux["query_count"]),
"Queries where the deliberately faulted candidate changed baseline output:"+
 str(linux["faulted_different_from_base_queries"]),
"Queries where maximum repaired candidate changed baseline output:"+
 str(linux["repaired_different_from_base_queries"]),"",
"| Memory | Reference matches | Nonempty answers | Returned path hypotheses |",
"|---|---:|---:|---:|"]
for name,a in linux["arms"].items():
    lines.append(f'| {name} | {a["reference_matches"]}/{a["queries"]} | {a["nonempty_outputs"]} | {a["returned_hypotheses"]} |')
lines+=["","Every native output matches an independently implemented raw-row symbolic",
"join under the same16-intermediate/64-candidate limits. Strong-control gain0.",
"All composed outputs stay UNVERIFIED_PATH_HYPOTHESES. A path does not",
"authorize a new fact or causal consequence. No operator was learned here.","",
"## What this means","",
"Boundedly repaired stored facts remain usable by existing composition code.",
"This adds compatibility/application evidence beyond yes/no membership repair.",
"It does not demonstrate native understanding, independently discovered rules,",
"new semantic knowledge, new-world generalization or control superiority.",
"The original damaged checkpoint and maximum repaired checkpoint are unchanged;",
"the entire source binary hash is unchanged. Main/owner models remain untouched.","",
"## Exact source and timing","",
"Source SHA:"+source,
"Prereg SHA:"+os.environ["NKR28_PREREG_SHA"],
"Query SHA256:"+linux["query_sha256"],
"Stable result SHA256:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s; setup:{linux["setup_seconds"]:.6f}s.',
f'Windows audit:{windows["wall_seconds"]:.6f}s; setup:{windows["setup_seconds"]:.6f}s.',
"No raw archive parse, original environment actions, new runner or paid API.",
"Network/checkout costs are additional. Complete final regression and independent",
"G29 both OS qualify the final source after this evidence is committed.","",
"Scientific status:false. Accepted native integration:false. Deployment:none."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
