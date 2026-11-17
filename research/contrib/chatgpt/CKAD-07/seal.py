"""Persist bounded repair independently of the frozen failed predecessor."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ['CKAD07_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD07_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD07_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD07_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    path=unique(linux_root,c['checkpoint_name'])
    if digest(path.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD07_CHECKPOINT_PIN')
    shutil.copyfile(path,HERE/path.name)
p={'schema':'yggdrasil.ckad07.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD07_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'95af9a8d0805eee5c58d4d40f8970e854921321f',
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
    'source_grounding':'post-result engineering repair; reused synthetic source only',
    'qualification':'full final root/NKR05 and independent G29 both OS follow receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
s=receipt(linux)
lines=['# CKAD07 — bounded stale readout repair','','Earlier CKAD06 failures remain frozen. The new optional readout guard',
'quarantines a relation only when observed, admitted training evidence',
'contradicts its fitted model class. It does not receive test labels,',
'family IDs or an error list. No hidden automatic family expansion occurs.','',
'| Same73728 questions | Correct | Wrong | Abstained |','|---|---:|---:|---:|']
for key in ('before','after'):
    d=s[key];lines.append(f"| {key} | {d['correct']} | {d['incorrect']} | {d['abstained']} |")
lines+=['','12 contradicted addresses are quarantined. All55296 earlier correct',
'held answers in36 compatible addresses remain exact. The354 stale wrong',
'answers become abstentions, along with810 coincidentally correct stale',
'answers. This is a correctness/coverage tradeoff, NOT354 newly solved tasks.',
'The original errors made before contradictions arrived remain inCKAD06.','',
'Every new answer matches the previously qualified independent exact symbolic',
'full-prefix control. Fully trained CART512 remains65364 correct/8364 wrong;',
'its exact same-source receipts were reused, NOT trained again in this audit.',
'No compute-parity or strongest-control advantage is claimed.','',
'Three native bundles keep all original learned coefficient/support/input-mask',
'and source-ledger bytes unchanged. Quarantine metadata is separate. Cold',
f"processes reproduced{s['cold_queries']} readouts with only saved checkpoint bytes.",
'All three complete bundle checkpoints and their SHA256 pins are committed.','',
'What improved: a known-disproved representation is no longer used after',
'its observed contradiction. What did not improve: the model still cannot',
'learn the incompatible family or detect an unsupported assumption before',
'diagnostic evidence. Repairing that representation remains open research.','',
'No new original-source action, protected first-use, historical scan, accepted',
'owner mutation, controller, scheduler, paid API, merge or deployment.','',
'Source SHA:'+source,'Prereg:'+os.environ['CKAD07_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Ubuntu audit:{linux['wall_seconds']:.6f}s; Windows:{windows['wall_seconds']:.6f}s.",
'Full final Ubuntu/Windows regression+independent G29 follows sealing;',
'exact final receipts are in draft PR1182. ENGINEERING repair supported;',
'SCIENCE genuine-world/unfamiliar-family superiority UNVERIFIED; DEPLOYMENT NONE.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
