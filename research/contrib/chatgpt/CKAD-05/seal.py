"""Freeze complete native knowledge-state checkpoints after dual-OS parity."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ["CKAD05_LINUX_DIRECTORY"])
windows_root=Path(os.environ["CKAD05_WINDOWS_DIRECTORY"])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError("CKAD05_ARTIFACT_MEMBERS")
    return found[0]
linux=json.loads(unique(linux_root,"campaign-result.json").read_text())
windows=json.loads(unique(windows_root,"campaign-result.json").read_text())
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if stable(linux)!=stable(windows) or any(x["source_candidate_sha"]!=source for x in (linux,windows)):
    raise RuntimeError("CKAD05_SOURCE_OR_REPLICATION_DRIFT")
for name,result in (("result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
for case in linux["cases"]:
    for suffix,key in (("complete-native-knowledge","checkpoint_sha256"),
                       ("before-trainingB","before_trainingB_checkpoint_sha256")):
        name=f'seed-{case["seed"]}-{suffix}.json';path=unique(linux_root,name)
        if digest(path.read_bytes())!=case[key]:raise RuntimeError("CKAD05_CHECKPOINT_PIN")
        shutil.copyfile(path,HERE/name)
p={"schema":"yggdrasil.ckad05.provenance.v1","source_sha":source,
   "prereg_sha":os.environ["CKAD05_PREREG_SHA"],"run_id":os.environ["GITHUB_RUN_ID"],
   "parent_sha":"935bb8720b6cc4df2402003efb1d7e41243de07d",
   "stable_sha256":linux["stable_sha256"],"scientific_pass":False,"accepted_native":False,
   "source_grounding":"pinned synthetic simulator only; no historical-to-real-causal bridge",
   "qualification":"full final root/NKR05 and independent G29 both OS follow this receipt commit; terminal PR authoritative"}
(HERE/"provenance.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
lines=["# CKAD05 — native persistent property knowledge and learned consequence use","",
"The complete checkpoint now contains100,000 explicitly observed synthetic",
"binary property facts per seed, plus native learned relation coefficients.",
"Facts are stored knowledge; the relation coefficients are learned. This",
"does not make all100k facts semantic understanding or genuine-world causes.","",
"Source code is the unchanged hash-pinned CKAD01 simulator. This experiment",
"trains at FULL knowledge once, then varies inference observability. It does",
"not repeat the original knowledge-scale training benchmark. No new CausalGym",
"source action, protected cohort or historical dataset scan is performed.","",
"## Cold entity/action questions","",
"| Visible properties | Correct | Incorrect | Abstained | Questions |",
"|---|---:|---:|---:|---:|"]
for name,s in receipt(linux)["conditions"].items():
    lines.append(f'| {name} | {s["correct"]} | {s["incorrect"]} | {s["abstained"]} | {s["questions"]} |')
lines+=["","IRRELEVANT_WITHHELD exposes only source property bits4,5,6; the learner",
"was never told these were the relevant variables. RELEVANT_WITHHELD hides",
"bit4; ZERO exposes none. These evaluator-known diagnostic masks are fixed",
"before execution. Unknown features are never filled in as false facts.","",
"Every native prediction agrees with an independently fitted symbolic model",
"under the same missing-information completions. Fully trained unpruned CART",
"gets the same observations and partial knowledge; unknown branches are BOTH",
"traversed, with a prediction only if all possible leaves agree. Full control",
"metrics and tree sizes/timings are in result.json; no weak zero-imputation",
"baseline or hidden outcome labels are used.","",
"## What is persistent","",
"Each of3 complete native checkpoints stores both witnessed1 and witnessed0",
"property values with separate known bits, an engineering source namespace,",
"source byte pins and learned native GF2 coefficients/input support. It has",
"no per-entity consequence lookup table. The original property matrix/source",
"generator is not passed into fresh-process inference. Cold queries supply",
"only entity IDs, chosen action, relation address and visibility mask.","",
"After relationC, relationB is trained on512 additional synthetic consequences",
"in a separate native address. All100k property values, earlier C coefficients",
"and old question readouts remain unchanged. Checkpoints before and after",
"this new training are separately frozen here.","",
"| Seed | Native properties | Retained old answers | Cold questions | Complete checkpoint bytes |",
"|---:|---:|---:|---:|---:|"]
for c in linux["cases"]:
    lines.append(f'| {c["seed"]} | {c["native_property_count"]} | {c["old_consequence_answers_retained"]} | {c["cold_queries"]} | {c["checkpoint_bytes"]} |')
lines+=["","## Meaning and scientific boundary","",
"This closes a native-input-state gap: answering no longer depends on an",
"externally supplied property vector. Stored facts feed learned composition",
"inside the saved native research checkpoint. The synthetic join is checked",
"against its pinned source; a self-asserted namespace/hash is not real-world",
"causal authentication. Historical Q/P/Q and original source modes are refused.","",
"The new entity questions remain in the same simulator/mechanism family and",
"declared polynomial representation. No unrestricted unfamiliar family was",
"discovered; the strongest equally informed symbolic control ties. Real-world",
"causal grounding, virgin-source custody and qualified owner execution remain",
"unverified. No accepted-model promotion, controller/scheduler or deployment.","",
"Source SHA:"+source,"Prereg:"+os.environ["CKAD05_PREREG_SHA"],
"Stable SHA256:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s. Windows audit:{windows["wall_seconds"]:.6f}s.',
"Setup, CI scheduling and final regression are additional workflow costs.",
"Mandatory final full root/NKR05/independent G29 both OS follows this receipt",
"commit; final PR records the exact final SHA/tree and terminal qualification.","",
"ENGINEERING: supported native synthetic knowledge use, pending final checks.",
"SCIENTIFIC: genuine-world causal understanding and new-family superiority",
"UNVERIFIED. DEPLOYMENT: NONE; accepted main/owner states unchanged."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
