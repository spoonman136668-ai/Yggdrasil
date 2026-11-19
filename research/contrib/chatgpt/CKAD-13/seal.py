"""Seal paired platform results without granting accepted-model authority."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from campaign import stable, receipt, ACTIVE
from yggdrasil.native_context_basis import digest


def unique(root,name):
    paths=list(root.rglob(name))
    if len(paths)!=1:raise RuntimeError('CKAD13_ARTIFACT_AMBIGUOUS')
    return paths[0]


linux_root=Path(os.environ['CKAD13_LINUX_DIRECTORY'])
windows_root=Path(os.environ['CKAD13_WINDOWS_DIRECTORY'])
linux=json.loads(unique(linux_root,'campaign-result.json').read_text())
windows=json.loads(unique(windows_root,'campaign-result.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
if stable(linux)!=stable(windows) or any(d['source_candidate_sha']!=source for d in (linux,windows)):
    raise RuntimeError('CKAD13_SOURCE_OR_PLATFORM_DRIFT')
for name,d in (('result.json',linux),('replication-windows.json',windows)):
    (HERE/name).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
for c in linux['checkpoints']:
    p=unique(linux_root,c['name'])
    if digest(p.read_bytes())!=c['sha256']:raise RuntimeError('CKAD13_CHECKPOINT_PIN')
    shutil.copyfile(p,HERE/c['name'])
provenance={'schema':'yggdrasil.ckad13.provenance.v1','source_sha':source,
    'parent_sha':'5df8dbf506027b914f66e19441376d1347a3e09d',
    'prereg_sha':'3302ca1635eb4e71a432d7dc208b25c5a2c712e5',
    'pre_primary_amendment_sha':'5c8599bda2f14f34afd92db9ab04b9fa71aab478',
    'run_id':os.environ['GITHUB_RUN_ID'],'stable_sha256':linux['stable_sha256'],
    'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
    'qualification':'sealed candidate needs mandatory full regression and independent raw-state/G29 qualification BOTH OS',
    'mind_palace_sha':'4f0ef7cda0441116b253fc53ac11cedd47ce24dc',
    'mind_palace_records_sha256':'f784f423c8ed302ba3f1cd047a08e1c4f085502539b688475b47298311e14dc2'}
(HERE/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
lines=['# CKAD13 — integrated cumulative native development','',
'One training interface now retains property planes, cumulative native constraints,',
'evidence-selected provisional representations, and preserved contradiction packets.',
'Each of A-F saves the whole state and a fresh Python process restores it before',
'the next stage. All stages run through one campaign command; no controller or scheduler.','',
'All source outcomes are previously consumed synthetic witnesses, authenticated',
'against original CKAD05/08 result pins. Hashes prove byte custody, not real-world',
'causal truth. The 21,343,681-row factual source was not rescanned or relabeled.','',
'| Final unfamiliar queries in seven unquarantined slots | Correct | Wrong | Abstained |',
'|---|---:|---:|---:|']
for method in ('native','exact','cart','replacement','witnessed_lookup'):
    scores=[]
    for case in linux['cases']:
        metrics=case['stages'][-1]['metrics']
        for s in ACTIVE:
            m=metrics[str(s)]
            scores.append(m[method] if method in ('native','witnessed_lookup') else m['controls'][method])
    lines.append('| '+method+' | '+' | '.join(str(sum(s[k] for s in scores)) for k in ('correct','incorrect','abstained'))+' |')
lines+=['','| Seed | Additional correct after continued evidence | Supported-family wrong |','|---|---:|---:|']
for c in linux['cases']:lines.append(f"| {c['seed']} | {c['gain_correct']} | {c['supported_wrong']} |")
lines+=['',f"Frozen development gain criterion: {linux['development_gain_pass']}.",
'300,000 stored properties retained across three seeds. These remain stored',
'facts, not learned semantics. New slots do not share coefficients, so disjoint-slot',
'retention does not establish resistance to shared-weight catastrophic forgetting.',
'Representation selection can retract earlier provisional answers; changes and',
'errors remain in result.json. Contradiction in slot5 is quarantined with its',
'old weights and rejected outcome preserved. It is not silently repaired as truth.',
'The learner supports deterministic Boolean polynomial families. Legitimate',
'stochastic outcomes need the separately qualified probability learner and an',
'authenticated public-history/source join; this interface deliberately refuses',
'correlation-only and claimed real-world source packets. That integration is incomplete.','',
'Stage E scores higher-order unseen slots before adaptation and after128 witnesses.',
'This is not a successful zero-shot world-transfer claim. Action selection in F',
'chooses outcome-blind inputs from a consumed witness pool; no new environmental',
'policy rollout or source-owned intervention was executed. Controls receive exactly',
'the same acquired outcomes and action opportunities; fit/inference costs are reported,',
'not asserted equal. CART is fully grown and fits all acquired observations.',
'Independent set-XOR uses the same class-order assumption and fit/calibration split.','',
f"Source SHA: {source}",f"Stable result SHA256: {linux['stable_sha256']}",
f"Whole campaign Linux {linux['whole_wall_seconds']:.6f}s; Windows {windows['whole_wall_seconds']:.6f}s.",
f"Linux parent CPU {linux['parent_cpu_seconds']:.6f}s; cold child CPU {linux['cold_child_cpu_seconds']:.6f}s.",
'Whole wall includes source reads, training, control fitting/scoring, save/restore and cold checks.',
'Dependency setup, CI scheduling, source authoring, sealing, regression and independent',
'qualification are separate. No measured end-to-end2x gain is claimed.','',
'Reproduce: `python -B research/contrib/chatgpt/CKAD-13/campaign.py --output-directory /tmp/ckad13`.',
'Independent raw audit: `python -B research/contrib/chatgpt/CKAD-13/independent_audit.py`.',
'Pinned comparator packages and full platform checks are in the CKAD13 workflow.','',
'ENGINEERING development completed; final acceptance requires completed final CI.',
'SCIENTIFIC_PASS=false. DEPLOYMENT NONE. Draft/unmerged. No owner or accepted main change.']
(HERE/'SESSION_REPORT.md').write_text('\n'.join(lines)+'\n')
