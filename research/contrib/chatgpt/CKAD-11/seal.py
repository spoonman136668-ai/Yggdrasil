"""Seal both-platform disjoint falsification, including failed hypotheses."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ['CKAD11_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD11_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD11_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD11_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    for name,pin in ((c['checkpoint_name'],c['checkpoint_sha256']),(c['view_checkpoint_name'],c['view_checkpoint_sha256'])):
        path=unique(linux_root,name)
        if digest(path.read_bytes())!=pin:raise RuntimeError('CKAD11_NATIVE_PIN')
        shutil.copyfile(path,HERE/name)
provenance={'schema':'yggdrasil.ckad11.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD11_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'3664b0f7b3e7d67f992983821fbc604052216322',
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
    'source_grounding':'native checkpoint original witnessed entity/context hashes; previously consumed synthetic knowledge only',
    'learner_changed':False,'new_original_source_actions':0,'historical_rescans':0,
    'qualification':'full final root/NKR05 and independent G29 both OS follow receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
lines=['# CKAD11 — disjoint native-knowledge learner probe','',linux['classification'],'',
'This applies the UNCHANGED CKAD09 learner to original CKAD01 majority3',
'observations authenticated against the native100000-property checkpoints.',
'No source generator, extra outcome, world or environment action was used.',
'No stopped learner was repaired or retuned. Failed fits remain committed.','',
'## Strict unfamiliar combinations','',
'These3754 held entity queries have property contexts absent from ALL512',
'original witnessed events, not just absent from the smaller training view.','',
'| Condition | Unique observations | Method | Correct | Wrong | Abstained |',
'|---|---:|---|---:|---:|---:|']
for key,group in linux['summary'].items():
    condition,n=key.rsplit('_',1)
    for method,score in group['strict_novel_features'].items():
        lines.append(f"| {condition} | {n} | {method} | {score['correct']} | {score['incorrect']} | {score['abstained']} |")
lines+=['','## Frozen gates','']+[f'- {k}: {"PASS" if v else "FAIL"}' for k,v in linux['gates'].items()]
lines+=['','All three100000-property checkpoints stayed byte exact. The existing',
'qualified native majority predictor still answers6144/6144 held entities',
'correctly, including all3754 strict unfamiliar combinations. It has512',
'original observations and a degree2 assumption, so its information/prior',
'advantage is explicit. This reference is not the tested greedy learner.',
'CART is fully trained on the SAME128/384 available unique observations.',
'The exact same-prior independent optimizer matches every weight/write and',
'all2048 parameter-space outputs in every trial. No unique native advantage',
'is shown. All12 hypotheses/views, provenance and failures are preserved.','',
f"Cold process restoration reproduced{receipt(linux)['cold_queries']} held readouts.",
'Properties are stored native bit-plane memory; learned relationship weights',
'are distinct from those stored facts. The100000 records are not100000',
'causally understood relationships. Action0 has no observed contrast here.',
'No real-world causal understanding, fresh scientific pass or deployment.','',
'Source SHA:'+source,'Prereg:'+os.environ['CKAD11_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Whole audit Ubuntu:{linux['whole_wall_seconds']:.6f}s; Windows:{windows['whole_wall_seconds']:.6f}s.",
'Exact final SHA/tree and full final both-platform CI receipts are recorded',
'in existing draft PR1182 after result sealing. Accepted main unchanged.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
