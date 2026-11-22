"""Seal cumulative stochastic integration without rewriting earlier results."""
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
    if len(paths)!=1:raise RuntimeError('CKAD15_ARTIFACT_AMBIGUOUS')
    return paths[0]


lroot=Path(os.environ['CKAD15_LINUX_DIRECTORY']);wroot=Path(os.environ['CKAD15_WINDOWS_DIRECTORY'])
l=json.loads(unique(lroot,'campaign-result.json').read_text());w=json.loads(unique(wroot,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(l)!=stable(w) or any(d['source_candidate_sha']!=source for d in (l,w)):
    raise RuntimeError('CKAD15_SOURCE_OR_PLATFORM_DRIFT')
for name,d in (('result.json',l),('replication-windows.json',w)):
    (HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
for c in l['stages']:
    path=unique(lroot,c['checkpoint_name'])
    if digest(path.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD15_STATE_PIN')
    shutil.copyfile(path,HERE/c['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad15.provenance.v1','source_sha':source,
    'parent_sha':'30437508aef0a143605e472e31388496de14738e',
    'prereg_sha':'119da9304ec020f764bc375b057a2b3d45611ac4','run_id':os.environ['GITHUB_RUN_ID'],
    'stable_sha256':l['stable_sha256'],'scientific_pass':False,'accepted_native':False,'deployment':'NONE'}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
lines=['# CKAD15 — stochastic learning in the accumulated native checkpoint','',l['classification'],'',
'The already trained CKAD14 seed101 state now accumulates public stochastic',
'transition evidence in the SAME checkpoint. Existing deterministic facts,',
'constraints, sparse weights, quarantine records and readouts remain unchanged.',
'This adds the existing NKR20 two-bank public-history mechanism; it does not',
'replace the architecture or create a controller, scheduler, or memory service.','',
'| Learned public rows/world | Learned events | Held pooled Brier |',
'|---|---:|---:|']
for s in l['stages']:lines.append(f"| {s['prefix_rows_per_world']} | {s['training_events']} | {s['brier']['value']:.12f} |")
lines+=['',f"Frozen gates: {l['gates']}",
'All56 held probability forecasts match an independent fully fitted exact Beta',
'history control at every stage. The qualified current-state Beta control',
'Brier0.183062553042 and hierarchical-backoff control0.177355054293 are better',
'than the final history-only Brier0.188219364460. Earlier NKR20/21 usefulness',
'failures remain valid. This is learned probability and engineering integration,',
'not native scientific superiority. Lower Brier is better.','',
'The124 cached public simulator transitions were consumed by earlier research.',
'Only92 TRAIN rows (indices1..23 per world) contribute184 target counter updates;',
'row0 supplies the past-history cue. Held row indices24..30 never train the model.',
'Held outcomes are not stored in the learned history state. No external source',
'was imported/reset/stepped, no new original intervention or learned-policy',
'rollout occurred, and protected-source custody remains separate.','',
'Legitimate stochastic within-key variation is counted; it does not quarantine',
'the deterministic relation memory. Replay is idempotent; the final328-byte',
'counter image exactly matches NKR20 history SHA256',
'5f35402435acccc835644d717c0107ede73354f9f2ff6c6bdbf4fe03abd2f4a7.',
'Each full state is cold-restored without a solver or source-cache read and',
'then feeds the next training stage. All16x2048 deterministic readouts survive.',
'Stored facts are not semantic understanding; forecasting is not identified',
'counterfactual policy value, broad causal discovery, or general intelligence.','',
f"Whole campaign Linux {l['whole_wall_seconds']:.6f}s / Windows {w['whole_wall_seconds']:.6f}s.",
'This includes full-state checkpoint/cold/retention and control accounting;',
'setup, source authoring, sealing, final regression and CI scheduling are additional.',
'Source SHA: '+source,'Prereg SHA: 119da9304ec020f764bc375b057a2b3d45611ac4',
'Stable result SHA256: '+l['stable_sha256'],
'Reproduce: `python -B research/contrib/chatgpt/CKAD-15/campaign.py --output-directory /tmp/ckad15`.',
'Independent audit: `python -B research/contrib/chatgpt/CKAD-15/independent_audit.py`.',
'Mandatory full final Linux/Windows regression and independent raw/G29 qualification',
'follow seal. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
