"""Freeze full-image repair results and exact candidate snapshots after parity."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from campaign import stable
from yggdrasil.native_factual_weights import digest

linux=json.loads(os.environ["NKR25_LINUX_RESULT"])
windows=json.loads(os.environ["NKR25_WINDOWS_RESULT"])
if stable(linux)!=stable(windows):
    raise RuntimeError("NKR25_WIDE_REPLICATION_DRIFT")
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if linux["source_candidate_sha"]!=source or windows["source_candidate_sha"]!=source:
    raise RuntimeError("NKR25_SOURCE_CHANGED")
folder=Path(os.environ["NKR25_CHECKPOINT_DIRECTORY"])
pairs=(("frozen-fault-checkpoint.json",linux["NKR25"]["checkpoint_sha256"],HERE),
       ("max-repaired-checkpoint.json",linux["NKR26"]["descending_stages"][0]["repaired_checkpoint_sha256"],
        HERE.parent/"NKR-26"))
for name,pin,destination in pairs:
    matches=list(folder.rglob(name))
    if len(matches)!=1:
        raise RuntimeError("NKR25_CHECKPOINT_ARTIFACT_MEMBERS")
    raw=matches[0].read_bytes()
    if digest(raw)!=pin:
        raise RuntimeError("NKR25_CHECKPOINT_ARTIFACT_SHA")
    destination.mkdir(exist_ok=True)
    (destination/name).write_bytes(raw)
(HERE/"campaign-result.json").write_text(json.dumps(linux,indent=2,sort_keys=True)+"\n")
(HERE/"replication-windows.json").write_text(json.dumps(windows,indent=2,sort_keys=True)+"\n")
for name in ("NKR25","NKR26","NKR27"):
    destination=HERE.parent/name.replace("NKR","NKR-")
    destination.mkdir(exist_ok=True)
    (destination/"result.json").write_text(json.dumps(linux[name],indent=2,sort_keys=True)+"\n")
provenance={"schema":"yggdrasil.nkr25-27.full-image-repair.provenance.v1",
 "source_sha":source,"prereg_sha":os.environ["NKR25_PREREG_SHA"],
 "github_run_id":os.environ["GITHUB_RUN_ID"],
 "compiled_image_source_run":43856374741,"compiled_image_artifact":14220169461,
 "image_manifest_sha256":"aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f",
 "image_sha256":linux["base_image_sha256"],"rows":linux["base_rows"],
 "relations":linux["base_relations"],"native_accepted":False,"scientific_pass":False,
 "max_membership_operations":65536,"frozen_failure_preserved":True,
 "frozen_checkpoint_sha256":linux["NKR25"]["checkpoint_sha256"],
 "repaired_checkpoint_sha256":linux["NKR26"]["descending_stages"][0]["repaired_checkpoint_sha256"],
 "stable_result_sha256":linux["stable_sha256"],
 "bounded_algorithmic_repair_edits_used":0,"development_replays_used":1,
 "qualification":"pending full final-source root/NKR05/G29; terminal PR receipt authoritative"}
(HERE/"provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
lines=["# Full-knowledge-image wide-first bounded repair campaign","",
"Full immutable base:"+str(linux["base_rows"])+" historical Q/P/Q records,",
str(linux["base_relations"])+" relation IDs, "+str(linux["base_numeric_bytes"])+" binary bytes.",
"The whole image remains present at every stage; no tiny replacement KB.","",
"## Important scope","",
"These are DELIBERATELY injected engineering membership faults in a research",
"candidate, not newly discovered errors in real-world knowledge or evidence",
"of native understanding. Repairs restore exact historical-source membership.",
"Historical source truth/currentness, new learning, unseen-world reasoning",
"and cognitive superiority are NOT established. scientific_pass=false.","",
"## Frozen failure and bounded repaired candidates","",
"32768 source memberships were deliberately suppressed and32768 wrong-object",
"associations injected in a separate candidate. Original source stayed read-only.",
"The exact original faulted checkpoint is committed and was never rewritten.",
"Maximum repaired checkpoint is separately frozen under NKR26.","",
"| Allowed operations, descending | Actual operations | True memberships restored | False associations left | Unchanged source probes retained |",
"|---:|---:|---:|---:|---:|"]
for row in linux["NKR26"]["descending_stages"]:
    m=row["metrics"]
    lines.append(f'| {row["budget"]} | {row["actual_operations"]} | {m["source_true_memberships_present"]} | {m["injected_false_memberships_present"]} | {row["retained_unchanged"]}/{row["retention_queries"]} |')
lines+=["","Every stage checks the same original fault candidate and fixed probe sets.",
"The widest65536-operation stage executes first. Two membership changes repair",
"each fault pair. Smaller budgets intentionally leave more faults unresolved.",
"Independent source-row/set reference agrees; strongest exact repair-control",
"gain is zero. Confidence/knowledge understanding is not inferred from this.","",
"## Retention, cold restore and source custody","",
"Full base SHA256:"+linux["base_image_sha256"],
"Frozen fault candidate:"+linux["NKR25"]["checkpoint_sha256"],
"Maximum repaired candidate:"+linux["NKR26"]["descending_stages"][0]["repaired_checkpoint_sha256"],
"Fresh process remapped/verified all"+str(linux["NKR27"]["cold_process_complete_image_rows"])+" source rows",
"and reproduced the selected repaired query decisions.",
"Sequential half-then-half repair recovers all memberships with separate audit",
"history. Witness/budget/parent/source misuse is rejected atomically.",
"Full image digest is unchanged after the entire campaign.","",
"## Preservation and qualification","",
"Core source is the already-compiled historical image in original artifact",
"14220169461; no raw archive download, TRAIN parser, official valid/test or",
"original scientific first-use. No owner install, main mutation or deployment.",
"Only candidate checkpoint bytes/results/code are committed here. The original",
"large source artifact still needs owner-controlled long-lived custody; the",
"existing artifact expiresDecember16,2026 and is not a permanent accepted install.","",
"Source SHA:"+source,
"Stable campaign receipt:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s, setup:{linux["setup_seconds"]:.6f}s.',
f'Windows audit:{windows["wall_seconds"]:.6f}s, setup:{windows["setup_seconds"]:.6f}s.',
"Setup includes compiled-ZIP integrity/extraction and complete image verification;",
"network download and CI checkout are additional workflow-step costs.",
"Full exact-final root/NKR05/independent G29 both OS is pending at evidence",
"commit time; terminal PR receipt supplies final qualification.","",
"The user authorized bounded repairs. This campaign predeclared up to3 targeted",
"algorithmic edits if needed, preserving original failures and classifying",
"post-result repair work as exploratory. No such edits are silently promoted",
"to original scientific success. Independent source confirmation and accepted",
"native integration remain separate."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
