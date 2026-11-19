"""Archive the single-attempt repair results, including all negatives."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable
from yggdrasil.native_context_basis import digest


def unique(root,name):
    paths=list(root.rglob(name))
    if len(paths)!=1:raise RuntimeError('CKAD14_ARTIFACT_AMBIGUOUS')
    return paths[0]


lroot=Path(os.environ['CKAD14_LINUX_DIRECTORY']);wroot=Path(os.environ['CKAD14_WINDOWS_DIRECTORY'])
linux=json.loads(unique(lroot,'campaign-result.json').read_text());windows=json.loads(unique(wroot,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD14_SOURCE_OR_PLATFORM_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
for c in linux['cases']+linux['parents']:
    path=unique(lroot,c['checkpoint_name'])
    if digest(path.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD14_STATE_PIN')
    shutil.copyfile(path,HERE/c['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad14.provenance.v1','source_sha':source,
    'parent_sha':'8eb49bdb8f6d6886d05d6e3e67c0994aa6ebac2e',
    'prereg_sha':'736f6ccc08c9e688861bcb174752ac53eb8f9f6c','run_id':os.environ['GITHUB_RUN_ID'],
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,'deployment':'NONE'}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
real=[c for c in linux['cases'] if c['arm']=='REAL'];neg=[c for c in linux['cases'] if c['arm']=='SHUFFLED']
lines=['# CKAD14 — bounded sparse weight repair','',linux['classification'],'',
'This is a conventional mixed-integer training algorithm programming existing',
'native binary polynomial weights. It is not native superiority over the solver.',
'Each attempt uses384 existing fitting observations;128 calibration outcomes',
'are inspected only after fitting. The solver gets no degree/family label.',
'Only optimal, exactly checked weights with zero fitting/calibration error may',
'be adopted. Every failed/limited attempt remains preserved separately.','',
'| Seed | Slot | Arm | Solver status | Eligible | Correct | Wrong | Abstained |',
'|---|---:|---|---:|---|---:|---:|---:|']
for c in linux['cases']:
    s=c['native_sparse'];i=c['info']
    lines.append(f"| {c['seed']} | {c['slot']} | {c['arm']} | {i['solver_status']} | {i['eligible']} | {s['correct']} | {s['incorrect']} | {s['abstained']} |")
lines+=['',f"Frozen gates: {linux['gates']}",
f"Hard-query totals: {linux['real_totals']}",
f"Adopted repairs: {sum(p['adopted_repairs'] for p in linux['parents'])}/6.",
'All previous source constraints, stored property bytes, event history and',
'previously answered readouts are preserved. Failed repairs leave the entire',
'parent unchanged. The old CKAD13 states/results remain untouched.','',
'The strongest conventional sparse program is the training compiler itself,',
'so no claim of superiority over it is possible. CKAD13 CART and independent',
'exact-hierarchy controls reuse the identical512 observed-input information.',
'No additional source outcome, simulator action, virgin seed, historical scan,',
'accepted-ref update, new controller or scheduler was performed.','',
'This does not establish real-world causality, broad transfer, shared-weight',
'lifelong learning, autonomous discovery, or general intelligence.',
f"Whole campaign Linux {linux['whole_wall_seconds']:.6f}s / Windows {windows['whole_wall_seconds']:.6f}s.",
'Solver cost, bounds and node counts remain in the platform-specific results.',
'A timeout is a failure of this bounded method, not a successful repair.',
'Runtime numeric readout and cold restoration require no SciPy solver import.','',
'Source SHA: '+source,'Prereg SHA: 736f6ccc08c9e688861bcb174752ac53eb8f9f6c',
'Stable result SHA256: '+linux['stable_sha256'],
'Reproduce: `python -B research/contrib/chatgpt/CKAD-14/campaign.py --output-directory /tmp/ckad14`.',
'Independent audit: `python -B research/contrib/chatgpt/CKAD-14/independent_audit.py`.',
'Mandatory exact-final Linux/Windows root/NKR05 regression and independent raw/G29',
'qualification follow seal; completed CI/PR receipts determine engineering status.',
'SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
