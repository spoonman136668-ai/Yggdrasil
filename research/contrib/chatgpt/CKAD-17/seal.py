"""Seal known-readout integration; preserve every earlier negative."""
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
    if len(paths)!=1:raise RuntimeError('CKAD17_ARTIFACT_AMBIGUOUS')
    return paths[0]


lroot=Path(os.environ['CKAD17_LINUX_DIRECTORY']);wroot=Path(os.environ['CKAD17_WINDOWS_DIRECTORY'])
l=json.loads(unique(lroot,'campaign-result.json').read_text());w=json.loads(unique(wroot,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(l)!=stable(w) or any(d['source_candidate_sha']!=source for d in (l,w)):raise RuntimeError('CKAD17_SOURCE_OR_PLATFORM_DRIFT')
for name,d in (('result.json',l),('replication-windows.json',w)):(HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
p=unique(lroot,l['checkpoint_name'])
if digest(p.read_bytes())!=l['checkpoint_sha256']:raise RuntimeError('CKAD17_STATE_PIN')
shutil.copyfile(p,HERE/l['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad17.provenance.v1','source_sha':source,
    'parent_sha':'95004026301863239ee50ae62e29aec2eced0471','prereg_sha':os.environ['CKAD17_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'stable_sha256':l['stable_sha256'],'scientific_pass':False,
    'accepted_native':False,'deployment':'NONE','training_updates':0}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
lines=['# CKAD17 — integrate the existing fixed hierarchical readout','',l['classification'],'',
'This imports the already-qualified NKR21 strength4 formula into the trained',
'NativeCumulativeLearner as the explicit history_forecast_backoff method.',
'Legacy methods, observations, weights, counters and full checkpoint bytes stay',
'unchanged. Zero new training updates: this is known-readout integration, not',
'new learning or scientific discovery. The earlier NKR21 negative criterion',
'HIERARCHICAL_VALUE_NOT_ESTABLISHED remains preserved and is not reinterpreted.','',
f"Legacy held Brier: {l['legacy_brier']:.12f}; integrated backoff: {l['brier']['value']:.12f}.",
f"Absolute Brier gain: {l['gain']:.12f}. All56 forecasts match the independent exact control.",
'Lower Brier is better. No gain over the strongest same-method control exists.',
'All current deterministic, MDP and DTR legacy readouts remain unchanged;',
'the new optional readout is restored in a fresh process without a source cache',
'or solver. The full trained state is byte-exact to CKAD16.','',
'No new original source action, intervention, policy rollout, source owner,',
'controller, scheduler, accepted-main change, merge or deployment.',
'Fresh unknown-world causal learning and general intelligence remain unproven.',
f"Whole Linux {l['whole_wall_seconds']:.6f}s / Windows {w['whole_wall_seconds']:.6f}s, excluding CI/setup/regression.",
'Source SHA: '+source,'Stable result SHA256: '+l['stable_sha256'],
'Reproduce: `python -B research/contrib/chatgpt/CKAD-17/campaign.py --output-directory /tmp/ckad17`.',
'Independent audit: `python -B research/contrib/chatgpt/CKAD-17/independent_audit.py`.',
'Mandatory exact-final full Linux/Windows regression and independent raw/G29',
'qualification follow seal. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
