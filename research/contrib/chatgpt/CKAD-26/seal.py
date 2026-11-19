"""Preserve original dual-platform outcomes without another training run."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
from campaign import stable
from yggdrasil.native_context_basis import digest

def check(value, label):
    if not value:
        raise RuntimeError('CKAD26_SEAL_' + label)

def unique(root, name):
    matches = list(root.rglob(name))
    check(len(matches) == 1, 'UNIQUE_' + name)
    return matches[0]

def write(name, value):
    (HERE / name).write_bytes((json.dumps(value, indent=2, sort_keys=True) + '\n').encode('ascii'))

left_root = Path(os.environ['CKAD26_LINUX_DIRECTORY'])
right_root = Path(os.environ['CKAD26_WINDOWS_DIRECTORY'])
source = os.environ['CKAD26_SOURCE_COMMIT']
run_id = int(os.environ['CKAD26_EVIDENCE_RUN'])
actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
check(actual == source, 'EXACT_TRAINING_SOURCE')
left = json.loads(unique(left_root, 'campaign-result.json').read_bytes())
right = json.loads(unique(right_root, 'campaign-result.json').read_bytes())
pin = digest(stable(left))
check(pin == digest(stable(right)) == left['stable_sha256'] == right['stable_sha256'], 'PLATFORM_SEMANTIC_PARITY')
check(left['source_candidate_sha'] == right['source_candidate_sha'] == source, 'SOURCE_IDENTITY')
check(left['scientific_pass'] is False and right['scientific_pass'] is False
      and left['accepted_native'] is False and right['accepted_native'] is False
      and left['deployment'] == right['deployment'] == 'NONE', 'SCIENTIFIC_FENCE')
check([case['seed'] for case in left['seeds']] == [101, 202, 303], 'SEEDS')
for case in left['seeds']:
    name = case['final_checkpoint_name']
    check(name == f"seed-{case['seed']}-refresh-native.json", 'STATE_NAME')
    raw = unique(left_root, name).read_bytes()
    replica = unique(right_root, name).read_bytes()
    check(raw == replica and len(raw) == case['final_checkpoint_bytes']
          and digest(raw) == case['final_checkpoint_sha256'], 'STATE_BYTES')
    (HERE / name).write_bytes(raw)
write('campaign-result.json', left)
write('replication-windows.json', right)
write('provenance.json', {
    'schema':'yggdrasil.ckad26.retained-context-refresh.provenance.v1',
    'preregistration_commit':'25e83a20c973bba98d170757771777c400cf6acb',
    'parent':'48a736933aa84f61d0a450acf322ef62d13fac5f',
    'qualified_initial':'a5faea392679756f172b87f3e40399ed88329a06',
    'receipt_source':'48a736933aa84f61d0a450acf322ef62d13fac5f',
    'refresh_rate':[1,32],
    'new_training_source_actions':0,
    'training_source_sha':source,'training_run_id':run_id,'stable_sha256':pin,
    'source_sha256':left['source_sha256'],
    'original_source_actions':0,'protected_first_use':0,
    'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
    'advance_as_qualified_scientific_parent':False,
})
def human(value):
    if isinstance(value, list) and len(value) == 2 and all(type(v) is int for v in value) and value[1] > 0:
        return round(value[0]/value[1],12)
    if isinstance(value, dict):
        return {key:human(item) for key,item in value.items()}
    if isinstance(value, list):
        return [human(item) for item in value]
    return value

report = f"""# CKAD26 native retained-context refresh

**{left['classification']}**. Frozen matched-receipt development evidence only;
engineering qualification does not establish strongest-control scientific superiority.

The learner starts from the separately qualified CKAD24 full832-event state and
replays the exact192 authenticated public receipts collected by CKAD25 coverage
acquisition. It does not start from the failed CKAD25 final weights. Every native
arm receives identical rows in identical order. No new training world, intervention,
family label or boundary signal is supplied. This tests retained-evidence context
selection, not active-exploration superiority.

An explicit native mode keeps31/32 of each joint-likelihood posterior and returns
1/32 to the existing context prior after scoring actual consequences. The existing
new candidate learns only afterward. The original alarm and other native weights
remain coupled to actual predictions. Default old schemas remain byte-compatible;
the new nestedv5 preserves activation count832 and fixedrate[1,32].

Primary evaluation uses fresh held cohortckad26-held-count, source seeds+112000,
all13 checkpoints, all3 replicas, prespecified worst-replica101 repair, post16
adaptation and final retention. Nine controls include unchanged native product,
independent exact refresh, both no-alarm variants, prior-only, pooled, trailing64MLE
and frozen832 readout. The same-method exact control must tie.

Frozen gates:
```json
{json.dumps(left['development_gates'], indent=2, sort_keys=True)}
```
Metrics (display decimals; full exact ratios remain in rawresultJSON):
```json
{json.dumps(human(left['development_metrics']), indent=2, sort_keys=True)}
```

Frozen source:{source}.
Preregistration FIRST:25e83a20c973bba98d170757771777c400cf6acb.
Training/reproduction/qualification run:{run_id}.
Semantic Linux/Windows SHA256:{pin}.

The same1024 witness ledger and legacy learned planes are retained. A fresh child
restores912 events, learns the next cached actual receipt, saves913, matches warm
learning byte-exactly, and supplies remaining training. Final1024 cold restore,
consolidation and capacity rejection are checked. Product-mode snapshot hashes
must match the original CKAD25 record; prior negative evidence is not erased.

New training source actions/episodes:0. Each unique576 retained receipts is replayed
into two native arms (1152 native admissions). All9 policies are evaluated across
39 checkpoints (33696 policy rollouts), plus3744 matched Brier trajectories:
74880 synthetic evaluation callbacks per campaign. Held learning updates,
original-source actions, protected first-use and paid APIs remain0.

Parent/child CPU and individual peaks are recorded separately. Simultaneous
process-tree peak and per-arm compute equality are not asserted. Setup, final
serialization, audit, artifact work, authoring and fullCI are additional.

Historical CKAD13–25 raw audits execute in their pinned25final worktree
48a736933aa84f61d0a450acf322ef62d13fac5f so their original native-source custody
checks remain intact. Current native legacy compatibility, G29, complete final
Linux/Windows regression and independent26 state/control replay execute on the
actual new candidate. Historical checks are not weakened for changed native code.

If any frozen development predicate fails, preserve DEVELOPMENT_NO_GO and hold
promotion. No rate/threshold/policy/budget tuning follows the score. Capacity
remains1024 and no observations are evicted. New-family discovery, original-world
transfer, general intelligence and scientific superiority remain unproven.

Reproduce:python -B research/contrib/chatgpt/CKAD-26/campaign.py --output-directory /tmp/ckad26
Audit:python -B research/contrib/chatgpt/CKAD-26/independent_audit.py
Tamper controls:python -B research/contrib/chatgpt/CKAD-26/audit_negative_controls.py

No merge, accepted-ref promotion, owner/controller/scheduler change, deployment or
interruption of other research is authorized by this evidence.
"""
(HERE/'SESSION_REPORT.md').write_text(report,encoding='utf-8')
subprocess.check_call([sys.executable,'-B',str(HERE/'independent_audit.py'),str(HERE)],cwd=ROOT)
subprocess.check_call([sys.executable,'-B',str(HERE/'audit_negative_controls.py'),str(HERE)],cwd=ROOT)
print(json.dumps({'sealed':True,'classification':left['classification'],'stable_sha256':pin}))
