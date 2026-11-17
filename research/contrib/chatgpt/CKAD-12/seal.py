"""Preserve all evidence-selected representations and failed calibrations."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

def unique(root,name):
    paths=list(root.rglob(name))
    if len(paths)!=1:raise RuntimeError('CKAD12_ARTIFACT_MEMBERS')
    return paths[0]
linux_root=Path(os.environ['CKAD12_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD12_WINDOWS_DIRECTORY'])
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD12_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    p=unique(linux_root,c['checkpoint_name'])
    if digest(p.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD12_MODEL_PIN')
    shutil.copyfile(p,HERE/c['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad12.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD12_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'e9cec0f79e723e7af0130ef87f6a4205213c2405','stable_sha256':linux['stable_sha256'],
    'source_grounding':'previously consumed synthetic native observations only; no factual triples promoted to causal labels',
    'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
    'qualification':'full final root/NKR05 and independent G29 BOTH OS follow seal; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
lines=['# CKAD12 — learning the native representation from evidence','',linux['classification'],'',
'The new optional training wrapper tries generic polynomial degrees in order',
'using FIT observations ONLY. It stops at the first consistent representation',
'and validates it ONCE against calibration observations. Calibration failure',
'never triggers a search for another class. Admitted readout is still marked',
'PROVISIONAL_ONLY; the class ordering is a supplied inductive assumption.',
'The stopped CKAD09/11 greedy rule remains unchanged and negative.','',
'## Unfamiliar combination results','',
'WIDE excludes all512 original source contexts from1536 queries/world.',
'MAJORITY below uses the stricter3754 novel-feature queries across three seeds,',
'not all6144 new-entity queries. No action0 contrast is learned in MAJORITY.','',
'| Recipe/condition/exposure | Admitted | Method | Correct | Wrong | Abstained |',
'|---|---:|---|---:|---:|---:|']
for key,g in linux['summary'].items():
    scores=g['held'] if key.startswith('WIDE') else g['strict_novel']
    for method,s in scores.items():lines.append(f"| {key} | {g['admitted']} | {method} | {s['correct']} | {s['incorrect']} | {s['abstained']} |")
lines+=['','Frozen development gates:','']+[f'- {k}: {"PASS" if v else "FAIL"}' for k,v in linux['gates'].items()]
lines+=['',f"Conventional superiority threshold met:{linux['conventional_superiority']}.",
'The independently coded set-XOR selector matches all2048 parameter-space',
'predictions for every trial. Its equal information/inductive assumptions',
'mean a tie, not native superiority. Existing manual-degree reference remains',
'separate. Generic monomial ordering is not unrestricted relationship discovery.',
'No unknown family label or held evaluator truth reaches native training.','',
f"Qualified controls reused:{linux['controls_reused']}; newly fitted distinct views:{linux['controls_fitted']}.",
f"All204 checkpoint restorations reproduced{receipt(linux)['cold_queries']} parameter-space readouts.",
'All16-address native parents and all three100000-property sources stayed',
'byte exact. This is retention under immutable hypothesis training, not proof',
'of adaptive lifelong interference repair. Earlier CKAD06–08 retention and',
'repair results remain separately qualified; new sequential-owner integration',
'has not occurred. No new original science/source action or historical scan.','',
'Source:'+source,'Prereg:'+os.environ['CKAD12_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Whole audit Ubuntu:{linux['whole_wall_seconds']:.6f}s; Windows:{windows['whole_wall_seconds']:.6f}s.",
'Full final root/NKR05 regression and independentG29 BOTH OS follow sealing;',
'exact final SHA/tree and completed CI receipts are recorded in draftPR1182.',
'ENGINEERING/DEVELOPMENT only; scientific_pass=false; accepted main unchanged;',
'no merge, deployment, owner mutation, new controller/scheduler/runner or paid API.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
