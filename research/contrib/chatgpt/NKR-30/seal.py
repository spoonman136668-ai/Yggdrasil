"""Preserve nominal analytic diagnostic without editing earlier evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit import stable
linux=json.loads(os.environ["NKR30_LINUX_RESULT"])
windows=json.loads(os.environ["NKR30_WINDOWS_RESULT"])
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if stable(linux)!=stable(windows) or any(d["source_candidate_sha"]!=source for d in (linux,windows)):
    raise RuntimeError("NKR30_SOURCE_OR_PARITY_DRIFT")
for name,value in (("result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
p={"schema":"yggdrasil.nkr30.nominal-calibration.provenance.v1",
   "source_sha":source,"prereg_sha":os.environ["NKR30_PREREG_SHA"],"run_id":os.environ["GITHUB_RUN_ID"],
   "source_blob":linux["source_blob"],"source_kernel_file_sha256":linux["original_kernel_file_sha256"],
   "source_feedback_file_sha256":linux["original_feedback_file_sha256"],
   "stable_sha256":linux["stable_sha256"],"nominal_iid_evaluator_only":True,
   "scientific_pass":False,"accepted_native":False,
   "qualification":"final exact-source full root/NKR05/G29 both OS pending at evidence commit; see terminal PR"}
(HERE/"provenance.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
lines=["# NKR30: did selective feedback damage calibration?","",
"Diagnostic:"+linux["classification"],"",
"NKR29's actual negative remains frozen. This follow-up restores its saved",
"native checkpoints and computes analytic expected error under the published",
"source's nominal IID law. No training, new source action or earned reward.",
"The source oracle is evaluator-only and never reaches the learned bank.","",
"| Maximum events | Memory | Expected Brier | Excess calibration error |",
"|---:|---|---:|---:|"]
for cap in linux["descending_caps"]:
    for name,a in linux["curves"][str(cap)]["arms"].items():
        lines.append(f'| {cap} | {name} | {a["expected_brier"]["value"]:.9f} | {a["excess_calibration_error"]["value"]:.9f} |')
lines+=["","Every checkpoint is scored on all32 world/target/state/action conditions",
"with equal weights, using exact fractions. Expected error decomposes exactly",
"into irreducible stochastic noise plus squared calibration error. The",
"source-kernel noise floor is0.1476. This oracle floor is an analytic reference,",
"not a learner supplied with hidden source laws and not an executed control.","",
"## Meaning and limits","",
"This distinguishes a diagnostic about learned probability quality from",
"relabeling individual stochastic outcomes as erroneous facts. Evidence from",
"previous negative results is unchanged. Neither future held-out worlds nor",
"the21.3M factual image were trained here. No claim of new relationship type,",
"native control superiority, unfamiliar-world transfer or general intelligence.",
"Expected values assume the same nominal IID structural equations; they are",
"not actual new-world trial scores, earned returns or pristine science.","",
"Source SHA:"+source,
"Prereg SHA:"+os.environ["NKR30_PREREG_SHA"],
"Stable SHA256:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s; Windows audit:{windows["wall_seconds"]:.6f}s.',
"All earlier evidence and saved checkpoints remain byte-identical.",
"Final-source mandatory full root/NKR05/independent G29 follows receipt commit.",
"Draft only, unmerged, undeployed, accepted native model unchanged."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
