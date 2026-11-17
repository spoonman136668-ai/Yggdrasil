"""Preserve both-platform outcomes and native checkpoints without promotion."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from campaign import stable,compact_receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ["CKAD02_LINUX_DIRECTORY"])
windows_root=Path(os.environ["CKAD02_WINDOWS_DIRECTORY"])
def unique(root,name):
    paths=list(root.rglob(name))
    if len(paths)!=1:raise RuntimeError("CKAD02_ARTIFACT_MEMBERS")
    return paths[0]
linux=json.loads(unique(linux_root,"campaign-result.json").read_text())
windows=json.loads(unique(windows_root,"campaign-result.json").read_text())
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if stable(linux)!=stable(windows) or any(r["source_candidate_sha"]!=source for r in (linux,windows)):
    raise RuntimeError("CKAD02_SOURCE_OR_REPLICATION_DRIFT")
for name,result in (("result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
retention=HERE.parent/"CKAD-03";retention.mkdir(exist_ok=True)
repair=HERE.parent/"CKAD-04";repair.mkdir(exist_ok=True)
for item in linux["CKAD03"]:
    name=f'seed-{item["seed"]}-learned.json';path=unique(linux_root,name)
    if digest(path.read_bytes())!=item["checkpoint_sha256"]:raise RuntimeError("CKAD03_CHECKPOINT_PIN")
    shutil.copyfile(path,retention/name)
for item in linux["CKAD04"]:
    for suffix,key in (("repaired","repaired_checkpoint_sha256"),("frozen-before-repair","original_checkpoint_sha256")):
        name=f'seed-{item["seed"]}-{suffix}.json';path=unique(linux_root,name)
        if digest(path.read_bytes())!=item[key]:raise RuntimeError("CKAD04_CHECKPOINT_PIN")
        shutil.copyfile(path,repair/name)
(retention/"result.json").write_text(json.dumps(linux["CKAD03"],indent=2,sort_keys=True)+"\n")
(repair/"result.json").write_text(json.dumps(linux["CKAD04"],indent=2,sort_keys=True)+"\n")
p={"schema":"yggdrasil.ckad02-04.provenance.v1","prereg_sha":os.environ["CKAD02_PREREG_SHA"],
   "archive_supplement_sha":"8e71c66203240adf57cb0db34907de98200c23ef","source_sha":source,
   "run_id":os.environ["GITHUB_RUN_ID"],"stable_sha256":linux["stable_sha256"],
   "original_source_actions":0,"scientific_pass":False,"accepted_native":False,
   "qualified_parent_sha":"eac1cf94a5a0a352a11fdef136cc03efd7bfa782",
   "qualification":"mandatory complete final root/NKR05/G29 both OS pending at receipt commit; terminal PR authoritative"}
(HERE/"provenance.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
lines=["# CKAD02–04 native representation, persistence and bounded repair","",
"This is an optional native GF(2) extension, not accepted Yggdrasil training",
"or external causal science. It reuses native elimination, numeric binary",
"float32 coefficients and16-address active/retained semantics. No transformer,",
"tokens, donor architecture, owner activation or historical fact-to-cause claim.","",
"## Main representation result","",
"Each of48 source-free datasets supplies512 input/action consequences and",
"1536 unseen combinations. Data are deliberately constructed mechanical",
"qualification fixtures, not a repeat of CKAD01's36-arm knowledge-scale study.","",
"| Declared degree, widest first | Fitted datasets | Correct | Incorrect | Abstained |",
"|---:|---:|---:|---:|---:|"]
for row in compact_receipt(linux)["degree_summary"]:
    lines.append(f'| {row["degree"]} | {row["fitted"]}/{row["datasets"]} | {row["correct"]} | {row["incorrect"]} | {row["abstained"]} |')
lines+=["","The complete basis can express every Boolean relationship but512 examples",
"do not identify unobserved consequences in that class. Reduced-degree",
"success is conditional on a narrower declared model class, not unrestricted",
"new relationship discovery. Every native answer matches an independent",
"lowest-pivot set-XOR symbolic fitter. CART was fully trained once/dataset",
"on identical examples; its predictions are reused across basis arms. Full",
"case metrics, tree size, timings and unavoidable capacity differences appear",
"in result.json. A strongest-control learning advantage is not established.","",
"## Original CKAD01 targeted native regression","",
"Original archive/source/prereg/result bytes were independently hash-checked.",
"The old three-property failure remains unchanged. Only full-knowledge familyC",
"is reused as a backward-compatibility diagnostic; the original exposure",
"benchmark is not rerun. No majority template is passed to native fitting.","",
"| Seed | Original pairwise coverage | Native correct | Questions | Truly unseen context questions |",
"|---:|---:|---:|---:|---:|"]
for c in linux["targeted_ckad01_regression"]:
    lines.append(f'| {c["seed"]} | {c["previous_pair_learner_covered"]} | {c["native"]["correct"]} | {c["native"]["questions"]} | {c["native_unseen_contexts"]["questions"]} |')
lines+=["","A three-property majority can be composed from several pairwise polynomial",
"terms; a learner restricted to a SINGLE two-property truth table cannot",
"express that composition. The generic native basis learns coefficients",
"from all supplied observations, rather than hardcoding that relationship.","",
"## Persistence and bounded repair","",
"All earlier addresses'16384 possible queries/seed remained unchanged after",
"subsequent native learning. Three checkpoints cold-restored in fresh Python",
"processes receiving only checkpoint bytes and questions, without evaluator",
"source outcomes. The checkpoint contains coefficients and input-only support,",
"not per-query consequence records. Saved native checkpoints are underCKAD03.","",
"CKAD04 preserves each degree2 rejection, then refits ONE address atdegree3",
"using the SAME512 observed consequences. It never edits source labels or",
"selects only prediction errors. Old/frozen and repaired checkpoints remain",
"separate underCKAD04; earlier addresses remain unchanged. This planned",
"representation repair does not rewrite the original CKAD01 failure.","",
"## Historical resource and grounding limitation","",
"The complete21,343,681-row historical image was SHA-verified and100,000",
"broad indexed factual witnesses checked. All100,000 were correctly REFUSED",
"as causal training labels: no verified entity/property/action/outcome join",
"exists. These checks are a grounding negative, not100k facts learned into",
"causal understanding. No raw original dataset scan, official valid/test,",
"original causal-world action, protected seed or owner lease was consumed.","",
"## Qualification and disposition","",
"Source SHA:"+source,"Prereg:a0b3089024446325565a6ffd092a10546f9ca99b",
"Stable result SHA256:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s. Windows audit:{windows["wall_seconds"]:.6f}s.',
"Network/setup/regression costs are additional. Complete final root/NKR05 and",
"independent G29 both OS follow this evidence commit; terminal PR records them.","",
"ENGINEERING: native-module qualification supported, pending final regression.",
"SCIENTIFIC: source-grounded causal understanding/unfamiliar-family advantage",
"UNVERIFIED. DEPLOYMENT: NONE. Accepted main and other owner tracks unchanged."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
