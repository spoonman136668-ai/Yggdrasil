"""Seal all fixed-rule hypothesis outcomes, including every frozen failure."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ['CKAD09_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD09_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD09_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD09_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    path=unique(linux_root,c['checkpoint_name'])
    if digest(path.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD09_CHECKPOINT_PIN')
    shutil.copyfile(path,HERE/path.name)
    view=unique(linux_root,c['view_checkpoint_name'])
    if digest(view.read_bytes())!=c['view_checkpoint_sha256']:raise RuntimeError('CKAD09_VIEW_PIN')
p={'schema':'yggdrasil.ckad09.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD09_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'17ce78fd70d5d88ddf839ecfd8f3abb33dd924ad',
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
    'source_grounding':'post-result exploratory fixed-rule hypothesis test; retained synthetic knowledge only',
    'rule_reference_sha256':'b9867fbd7549f24a1b64121ce7702646a3c2d31e5d8f60d4c3670dc78705fec8',
    'qualification':'full final root/NKR05 and independent G29 both OS follow receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
s=receipt(linux)
lines=['# CKAD09 — retained knowledge to provisional relationships','',
'Frozen outcome: '+linux['classification'],
'The existingWSP147 strictly improving16-edit rule was reused, without a',
'larger optimization budget, on128/512 observed effects decoded from cold',
'native checkpoints. No original environment or held outcome enters fitting.',
'75% fits the weights;25% only calibrates. No refit after calibration.','',
'| Knowledge | Observations | Correct held | Wrong held | Abstained | Admitted /12 | CART correct | CART wrong |',
'|---|---:|---:|---:|---:|---:|---:|---:|']
for key,x in s['summary'].items():
    condition,n=key.split('_');a=x['native'];b=x['cart']
    lines.append(f"| {condition} | {n} | {a['correct']} | {a['incorrect']} | {a['abstained']} | {x['admitted']} | {b['correct']} | {b['incorrect']} |")
lines+=['','Each row contains18432 never-observed input/action combinations across',
'the12 previously repaired higher-order fixtures. SHUFFLED is mathematical',
'knowledge corruption, not authentic causal source evidence. All outputs',
'remainPROVISIONAL; passing calibration is not a confidence guarantee.','',
'The independent NumPy boolean-matrix optimizer matches every fitted weight,',
'edit, calibration decision and prediction. Any gain therefore does not prove',
'unique native numerical intelligence. The supplied AND/XOR basis and sparse',
'bias are assumptions, not discovered computational operators. Identified-only',
'native memory and memorization still abstain on all unobserved questions.','',
'Fully trained CART uses all available labels. Exact qualifiedREAL512 scores',
'are reused fromCKAD06, not retrained; other views have different data and',
'receive fresh fully fitted conventional controls. Zero-update is explicitly',
'untrained. Native/independent share16 edits; capacity and actual whole-process',
'compute differ across methods and exposure scales. No compute-parity claim.','',
'Frozen development gates:']
lines += [f'- {key}: {"PASS" if value else "FAIL"}' for key,value in linux['gates'].items()]
lines+=['',f"Cold processes reproduced{s['cold_queries']} readouts from48 saved hypotheses.",
'All48 small hypothesis checkpoints are committed, including failed fits and',
'rejected calibration states. Source-view hashes/splits are committed; full',
'views are in30-day workflow artifacts and exactly regenerable from committed',
'CKAD08 parents. All parent native checkpoint bytes remain unchanged.','',
'No new source world, original protected action, historical scan, architecture',
'merge, accepted/live owner mutation, controller/scheduler, runner or paid API.',
'The scientific result remains exploratory/prior-limited and scientific_pass',
'isfalse. No model admission, merge or deployment. Earlier negatives preserved.','',
'Source SHA:'+source,'Prereg:'+os.environ['CKAD09_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Whole audit Ubuntu:{linux['whole_wall_seconds']:.6f}s; Windows:{windows['whole_wall_seconds']:.6f}s.",
'Mandatory full final root/NKR05 and independent G29 BOTH OS follows sealing;',
'exact final SHA/tree and terminal receipts are in existing draft PR1182.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
