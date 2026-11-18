"""Preserve the second-source integration and prior qualified state."""
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
    if len(paths)!=1:raise RuntimeError('CKAD16_ARTIFACT_AMBIGUOUS')
    return paths[0]


lroot=Path(os.environ['CKAD16_LINUX_DIRECTORY']);wroot=Path(os.environ['CKAD16_WINDOWS_DIRECTORY'])
l=json.loads(unique(lroot,'campaign-result.json').read_text());w=json.loads(unique(wroot,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(l)!=stable(w) or any(d['source_candidate_sha']!=source for d in (l,w)):raise RuntimeError('CKAD16_SOURCE_OR_PLATFORM_DRIFT')
for name,d in (('result.json',l),('replication-windows.json',w)):(HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
for c in l['stages']:
    p=unique(lroot,c['checkpoint_name'])
    if digest(p.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD16_STATE_PIN')
    shutil.copyfile(p,HERE/c['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad16.provenance.v1','source_sha':source,
    'parent_sha':'d2f03363a61776f0e30c85e55dd27b33069dee9a',
    'prereg_sha':os.environ['CKAD16_PREREG_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
    'stable_sha256':l['stable_sha256'],'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
    'original_source_pr':433,'original_run':39932201242,'original_artifact':12492506361,
    'original_zip_sha256':'ada547777ba2ba49070fe2606ac99c8d9248532f1cb16c8a0f8eab0f4001508c'}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
lines=['# CKAD16 — second public source in one cumulative native checkpoint','',l['classification'],'',
'Continues the trained CKAD15 state. Each new DTR training batch executes in a',
'FRESH Python process, restores the preceding full state, applies a new public',
'training prefix and saves the successor. All prior deterministic weights,',
'property facts and MDP probability state are byte-exact and retain their readouts.',
'One unchanged PublicCausalCells bank estimates the first-stage state transition',
'and terminal outcome at separate addresses with the correct public history.',
'Immediate zero reward is never substituted for the full delayed consequence.','',
'| Training episodes/replica | Pooled episodes | Transition Brier | Terminal Brier | Pooled Brier | CART pooled |',
'|---|---:|---:|---:|---:|---:|']
for s in l['stages']:
    lines.append(f"| {s['prefix_episodes_per_replica']} | {s['training_episodes']} | {s['brier_transition']['value']:.12f} | {s['brier_terminal']['value']:.12f} | {s['brier_pooled']['value']:.12f} | {s['cart_brier_pooled']:.12f} |")
lines+=['',f"Frozen gates: {l['gates']}",
'The exact fully fitted Beta control matches every probability. Fully grown CART',
'fits each observed public conditional empirical mean and receives the same inputs.',
'No superiority over the strongest conventional learner is claimed.',
'The old DTR02 PUBLIC_DTR02_NO_GAIN result remains preserved; its policy reward',
'rates do not measure this forecast experiment and are not substituted as scores.','',
'Original archive authenticity: GitHub run39932201242/artifact12492506361, ZIP SHA256',
'ada547777ba2ba49070fe2606ac99c8d9248532f1cb16c8a0f8eab0f4001508c.',
'The768 public FIT episodes were previously consumed. This new retrospective',
'split trains on576 and holds192 complete episodes for384 forecasts per stage.',
'It is NOT a blind unfamiliar-family or virgin-source study. The compact state',
'stores only TRAIN records; held outcomes, seeds and replica IDs are not inputs.',
'No original environment import/reset/do, new intervention, policy rollout,',
'private U/info, source oracle, accepted-ref or source-owner mutation occurred.',
'Future causal policy value and independent fresh-world learning remain unproven.','',
f"Whole campaign Linux {l['whole_wall_seconds']:.6f}s / Windows {w['whole_wall_seconds']:.6f}s.",
f"Linux parent CPU {l['parent_cpu_seconds']:.6f}s plus measured child CPU {l['child_cpu_seconds']:.6f}s.",
'Source authoring, setup, sealing, CI scheduling and final qualification are additional.',
'No2x speedup, native novelty over Bayes, broad intelligence or deployment claim.',
'Source SHA: '+source,'Stable result SHA256: '+l['stable_sha256'],
'Reproduce: `python -B research/contrib/chatgpt/CKAD-16/campaign.py --output-directory /tmp/ckad16`.',
'Independent audit: `python -B research/contrib/chatgpt/CKAD-16/independent_audit.py`.',
'Mandatory full final Linux/Windows regression and independent raw/G29 qualification',
'follow sealing. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
