"""Persist frozen readout application, control trees and all negative results."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ['CKAD10_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD10_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD10_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD10_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    files=[(c['checkpoint_name'],c['checkpoint_sha256'])]
    files.extend((r['cart_snapshot_name'],r['cart_snapshot_sha256']) for r in c['relations'])
    for name,pin in files:
        path=unique(linux_root,name)
        if digest(path.read_bytes())!=pin:raise RuntimeError('CKAD10_NATIVE_OR_TREE_PIN')
        shutil.copyfile(path,HERE/name)
p={'schema':'yggdrasil.ckad10.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD10_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'17919374b8d731fc7be7ea56117fecd14df879c1',
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
    'source_grounding':'new offline task on previously consumed synthetic fixtures; no action/source first-use',
    'hypothesis_training_calls':0,
    'qualification':'full final root/NKR05 and independent G29 both OS follow receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
s=receipt(linux);d=s['summary']['decisions']
lines=['# CKAD10 — frozen knowledge application','',
'Outcome:'+linux['classification'],
'The readout now combines identified native memory with separately marked',
'provisional hypotheses after validating their source and fit metadata.',
'The old learned bytes and answers retain precedence. No hypothesis training',
'or environment action was performed. CKAD09 remains scientificallyNO_GO.','',
'## Prediction retention','',
'| Held queries | Correct | Wrong | Abstained |','|---|---:|---:|---:|']
for method,x in s['summary']['held'].items():
    lines.append(f"| {method} | {x['correct']} | {x['incorrect']} | {x['abstained']} |")
lines+=['',f"All{s['summary']['identified_preserved']} earlier identified readouts remain exact.",
'These are model-class-conditional readouts, not that many independently',
'observed facts. The underlying source contains512 observations/address.',
'New provisional answers are never silently labelled identified.','',
'## Offline action-choice use','',
'Recommend only when both predicted consequences are available and unequal.',
'Correct/wrong preferences below count true action-sensitive contexts only.',
'For the separate simulated policy reward, action0 is an explicit default',
'when no recommendation exists, including ties. No real action was executed.','',
'| Method/subset | Contexts | Correct preferences | Wrong preferences | Missed sensitive | Default-policy reward | Best reward | Regret |',
'|---|---:|---:|---:|---:|---:|---:|---:|']
for key,x in d.items():
    lines.append(f"| {key} | {x['contexts']} | {x['correct_preference']} | {x['wrong_preference']} | {x['missed_sensitive']} | {x['policy_reward']} | {x['best_reward']} | {x['regret']} |")
lines+=['','The unfamiliar subset requires BOTH actions to have been unobserved in',
'the original source input mask. Source fixtures/results were already known:',
'this is new application/engineering evidence, not fresh world generalization',
'or new causal learning. Independent raw-parameter/source-space composition',
'matches all98304 values/statuses, so no unique native superiority is shown.',
'CART control reconstruction matches every qualified old held hash, and every',
'new2048-output vector matches independent scalar tree traversal. All48 trees',
'and output vectors are committed to avoid repeated training for future tasks.','',
'Frozen application gates:']
lines += [f'- {key}: {"PASS" if value else "FAIL"}' for key,value in linux['gates'].items()]
lines+=['',f"Cold bundle inference reproduced{s['cold_queries']} readouts and statuses.",
'The training-rule entry point was patched to raise during primary and cold',
'inference, verifying that no frozen hypothesis was retrained. Three complete',
'bundles are committed; all native parents and prior checkpoints stay exact.','',
'ENGINEERING/application evidence only. scientific_pass=false; deploymentNONE.',
'No first-use, original source action, historical scan, accepted/live owner',
'mutation, controller/scheduler, new runner, paid API, model promotion or merge.','',
'Source SHA:'+source,'Prereg:'+os.environ['CKAD10_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Whole audit Ubuntu:{linux['whole_wall_seconds']:.6f}s; Windows:{windows['whole_wall_seconds']:.6f}s.",
'Final full root/NKR05+independent G29 BOTH OS follows result sealing;',
'exact final SHA/tree and terminal receipts are in existing draft PR1182.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
