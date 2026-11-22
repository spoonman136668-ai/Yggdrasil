"""Seal the frozen full-scope continuation and preserve negative evidence."""
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
    p=list(root.rglob(name))
    if len(p)!=1:raise RuntimeError('CKAD18_ARTIFACT_AMBIGUOUS')
    return p[0]


lroot=Path(os.environ['CKAD18_LINUX_DIRECTORY']);wroot=Path(os.environ['CKAD18_WINDOWS_DIRECTORY'])
l=json.loads(unique(lroot,'campaign-result.json').read_text());w=json.loads(unique(wroot,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(l)!=stable(w) or any(d['source_candidate_sha']!=source for d in (l,w)):raise RuntimeError('CKAD18_PLATFORM_OR_SOURCE_DRIFT')
for name,d in (('result.json',l),('replication-windows.json',w)):(HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
for p in l['parents']:
    raw=unique(lroot,p['checkpoint_name'])
    if digest(raw.read_bytes())!=p['checkpoint_sha256']:raise RuntimeError('CKAD18_STATE_PIN')
    shutil.copyfile(raw,HERE/p['checkpoint_name'])
provenance={'schema':'yggdrasil.ckad18.provenance.v1','source_sha':source,
    'parent_sha':'ba3a3b7513806d17e0a8f4b808e0055d18957555','prereg_sha':os.environ['CKAD18_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'stable_sha256':l['stable_sha256'],
    'scientific_pass':False,'accepted_native':False,'deployment':'NONE','original_source_actions':0}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
lines=['# CKAD18 — complete the retained witness scope','',l['classification'],'',
'This continues existing trained replicas, without changing the native learner.',
'All eight empty relation slots per replica acquire512 already-witnessed inputs.',
'Each replica trains inside a fresh child process restored from its retained',
'parent. The evidence selector and existing bounded sparse compiler receive',
'only observed rows, no evaluator law, family label or held outcomes.',
'The deliberately damaged slot5 stays quarantined. Its negative packet, earlier',
'hypotheses, source profiles, stored properties and prior readouts are preserved.','',
f"Eligible15-slot totals across3 replicas: {l['eligible_totals']}.",
f"Full16-slot totals, INCLUDING the fault quarantine: {l['full_totals']}.",
f"Parent full-scope totals before new learning: {l['parent_totals']}.",
f"Fully trained cached CART on matched eligible15-slot information: {l['cart_eligible_totals']}.",
f"New slot admissions {l['new_slot_admissions']}/24; bounded sparse attempts {l['sparse_attempts']}/6.",
'All full-domain readouts are independently decoded without native/solver imports.',
'The same conventional sparse compiler supplies native weights; superiority over',
'that conventional method is not established. The raw audit is an independent',
'implementation of readout/scoring, not independent scientific acceptance.','',
'Seeds202/303 also ingest the SAME historical MDP and DTR caches as seed101.',
'These are model replicas, NOT independent new original-source observations.',
'All final states include both probability banks and the known optional history',
'backoff readout. Seed101 earlier probability bytes and readouts stay unchanged.',
f"Reused witness acquisitions {l['reused_witness_acquisitions']}; repeated historical events {l['repeated_historical_events']}.",
'Original-source actions0, held training updates0, factual-corpus rescans0.','',
f"Whole Linux {l['whole_wall_seconds']:.6f}s / Windows {w['whole_wall_seconds']:.6f}s.",
f"Linux parentCPU {l['parent_cpu_seconds']:.6f}s + measured childCPU {l['child_cpu_seconds']:.6f}s.",
'Costs exclude authoring, CI setup/scheduling and final regression. Cached CART',
'fit times remain historical and are included by reference; equal compute or',
'a2x end-to-end improvement is not asserted.',
'No new source reset/do, learned-policy rollout, source-owner lease, controller,',
'scheduler, accepted-main mutation, protected scientific first-use, merge or deployment.',
'This bounds integration of consumed fixtures/caches. It does not establish',
'fresh-world transfer, shared-weight forgetting resistance, intervention value,',
'autonomous discovery, strongest-control superiority or general intelligence.','',
'Source SHA: '+source,'Stable result SHA256: '+l['stable_sha256'],
'Reproduce: python -B research/contrib/chatgpt/CKAD-18/campaign.py --output-directory /tmp/ckad18',
'Audit: python -B research/contrib/chatgpt/CKAD-18/independent_audit.py',
'Exact-final Linux/Windows regression and independent G29/raw audits follow seal.',
'SCIENCE: SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
