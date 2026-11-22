"""Seal witness-only repair and retain its scientific no-recovery result."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from campaign import stable,receipt
from yggdrasil.native_context_basis import digest

linux_root=Path(os.environ['CKAD08_LINUX_DIRECTORY']);windows_root=Path(os.environ['CKAD08_WINDOWS_DIRECTORY'])
def unique(root,name):
    found=list(root.rglob(name))
    if len(found)!=1:raise RuntimeError('CKAD08_ARTIFACT_MEMBERS')
    return found[0]
linux=json.loads(unique(linux_root,'campaign-result.json').read_text());windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD08_SOURCE_OR_REPLICATION_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for c in linux['cases']:
    path=unique(linux_root,c['checkpoint_name'])
    if digest(path.read_bytes())!=c['checkpoint_sha256']:raise RuntimeError('CKAD08_CHECKPOINT_PIN')
    shutil.copyfile(path,HERE/path.name)
p={'schema':'yggdrasil.ckad08.provenance.v1','source_sha':source,'prereg_sha':os.environ['CKAD08_PREREG_SHA'],
    'run_id':os.environ['GITHUB_RUN_ID'],'parent_sha':'9fa7524e1218c46a7fbb20292e754163840962b8',
    'stable_sha256':linux['stable_sha256'],'scientific_pass':False,'accepted_native':False,
    'source_grounding':'post-result witness-only engineering repair; reused synthetic source only',
    'qualification':'full final root/NKR05 and independent G29 both OS follow receipt; terminal PR authoritative'}
(HERE/'provenance.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
s=receipt(linux)
lines=['# CKAD08 — knowledge survives explicit representation repair','',
'The native candidate can now expand a disproved relation, recover its earlier',
'witnessed outcomes from its own cold checkpoint, and accept the previously',
'rejected evidence. It retains observed facts rather than carrying forward',
'unsupported deductions from the disproved narrow model.','',
'| Measure | Result |','|---|---:|',
f"| Earlier observed answers retained without old raw rows | {s['old_observed_correct']} |",
f"| Additional observed answers learned | {s['new_observed_correct']} |",
f"| Old answers unidentified by no-memory reset | {s['no_memory_old_abstained']} |",
f"| Repaired relation addresses | {s['repaired_addresses']} |",
f"| Cold readouts reproduced | {s['cold_queries']} |",'',
'All6144 observed questions at12 formerly quarantined addresses are correct.',
'The1536 old labels are reconstructed only at the native observed-input mask;',
'the repair API rejects delivery of those old raw rows. The4608 additional',
'observations come from the same already consumed fixed source, not new',
'original environment calls. The384 new rows/address include the exact pinned',
'contradiction that invalidated the earlier fit. Guard clearance occurs only',
'after that evidence and all other packets fit the explicitly expanded class.','',
'## Unfamiliar relationship result is still negative','',
'The richest complete degree11 basis was used without capacity tuning.',
'It identifies ZERO of18432 unseen higher-order questions. The other36',
'relationships retain55296 correct held answers,0 wrong. These predictions',
'are unchanged fromCKAD07. Observed-answer recovery is not new-family discovery.',
'Every2048-query profile agrees with the qualified cached complete native',
'control; that control was independently qualified against exact symbolic.',
'Fully fitted CART remains65364 correct/8364 wrong on the broad held set,',
'from exact same-source frozen receipts, not newly repeated control training.',
'The weaker no-memory reset drops all1536 old witnessed questions; this',
'ablation demonstrates retained information, not strongest-control superiority.','',
'Three complete repaired16-address native checkpoints are committed. All36',
'unaffected profiles, masks, source ledgers and guard flags stay byte exact.',
'Fresh processes receive only checkpoint bytes and numeric queries. Earlier',
'CKAD06 failures andCKAD07 quarantined checkpoints are preserved unchanged.','',
'ENGINEERING: witness-preserving representation repair supported.',
'SCIENCE: UNFAMILIAR_FAMILY_RECOVERY_NO_GO; scientific_pass=false.',
'DEPLOYMENT: NONE. No original first-use, new source cohort, historical scan,',
'live owner mutation, controller/scheduler, new runner, paid API or merge.','',
'Source SHA:'+source,'Prereg:'+os.environ['CKAD08_PREREG_SHA'],
'Stable SHA256:'+linux['stable_sha256'],
f"Ubuntu audit:{linux['wall_seconds']:.6f}s; Windows:{windows['wall_seconds']:.6f}s.",
'Mandatory full final root/NKR05+independent G29 BOTH OS follows sealing.',
'Exact terminal final SHA/tree and receipts are in existing draft PR1182.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
