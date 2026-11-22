"""Seal primary and independent platform replica; never retune results."""
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

linux_root=Path(os.environ['CKAD06_LINUX_DIRECTORY'])
windows_root=Path(os.environ['CKAD06_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD06_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text())
windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD06_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
# All96 cold checkpoints are in immutable workflow artifacts; keep six compact
# representative checkpoints in Git, with every other SHA in complete results.
for case in linux['cases']:
    path=unique(linux_root,case['checkpoint_name'])
    if digest(path.read_bytes())!=case['checkpoint_sha256']:raise RuntimeError('CKAD06_CHECKPOINT_PIN')
    if case['slot']==0:shutil.copyfile(path,HERE/path.name)
p={'schema':'yggdrasil.ckad06.provenance.v1','source_sha':source,
   'prereg_sha':os.environ['CKAD06_PREREG_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
   'parent_sha':'28948ec34d8f5727daa10578a34c96825e3c1a54',
   'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
   'source_grounding':'reused synthetic CKAD02 fixtures only',
   'qualification':'full final root/NKR05 and independent G29 both OS follow this receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
summary=receipt(linux)
lines=['# CKAD06 — same-address knowledge accumulation','','The native research model now carries earlier identified constraints into',
'new batches at the SAME address, without replaying raw old outcome rows.',
'This closes a stationary cumulative-training gap; it does not establish',
'real-world causal understanding or an advantage over exact symbolic inference.','',
'| Declared degree | Observations | Correct | Wrong | Abstain | Valid profiles | Earlier answers lost | Replacement earlier answers lost |',
'|---:|---:|---:|---:|---:|---:|---:|---:|']
for row in summary['curve']:
    s=row['native'];lines.append(f"| {row['degree']} | {row['exposures']} | {s['correct']} | {s['incorrect']} | {s['abstained']} | {row['valid_profiles']} | {row['prior_lost']} | {row['replacement_prior_lost']} |")
lines+=['','Each row has73728 never-trained questions across48 fixed datasets.',
'Stopped/incompatible profiles retain their earlier checkpoint; their stale',
'outputs are recorded, never claimed to fit the contradictory full prefix.',
'Exact all-prefix batch and independent symbolic predictions match EVERY',
'query for every valid stationary native profile. Fully fitted CART scores',
'and all source hashes, costs and rank curves are preserved in result.json.',
'The complete degree11 class still cannot identify unseen combinations.',
'Its stored constraints are lossless memory rather than unfamiliar inference.','',
f"Fresh processes verified {summary['cold_queries']} forecasts from96 final checkpoints.",
'No old source labels or source program enters the cold inference process.',
'Six representative checkpoints are committed; all96 are in the workflow',
'artifact, whose temporary retention is30days; every hash is committed.',
'The earlier CKAD05 facts and module/checkpoint formats remain unchanged.','',
'No new original CausalGym action, protected cohort, historical dataset scan,',
'accepted-model mutation, controller, scheduler, paid API or deployment.',
'SYNTHETIC ENGINEERING evidence only; unrestricted unfamiliar-family causal',
'understanding and strongest-control superiority remain UNVERIFIED.','',
'Source SHA: '+source,'Prereg: '+os.environ['CKAD06_PREREG_SHA'],
'Stable SHA256: '+linux['stable_sha256'],
f"Ubuntu audit: {linux['wall_seconds']:.6f}s; Windows: {windows['wall_seconds']:.6f}s.",
'Final full regression/independent G29 both OS follows this sealing commit.',
'Exact final SHA/tree and terminal qualification are recorded in draft PR1182.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
