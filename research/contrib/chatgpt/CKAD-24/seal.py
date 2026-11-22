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
        raise RuntimeError('CKAD24_SEAL_' + label)

def unique(root, name):
    matches = list(root.rglob(name))
    check(len(matches) == 1, 'UNIQUE_' + name)
    return matches[0]

def write(name, value):
    (HERE / name).write_bytes((json.dumps(value, indent=2, sort_keys=True) + '\n').encode('ascii'))

left_root = Path(os.environ['CKAD24_LINUX_DIRECTORY'])
right_root = Path(os.environ['CKAD24_WINDOWS_DIRECTORY'])
source = os.environ['CKAD24_SOURCE_COMMIT']
run_id = int(os.environ['CKAD24_EVIDENCE_RUN'])
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
    check(name == f"seed-{case['seed']}-coverage-native.json", 'STATE_NAME')
    raw = unique(left_root, name).read_bytes()
    replica = unique(right_root, name).read_bytes()
    check(raw == replica and len(raw) == case['final_checkpoint_bytes']
          and digest(raw) == case['final_checkpoint_sha256'], 'STATE_BYTES')
    (HERE / name).write_bytes(raw)
write('campaign-result.json', left)
write('replication-windows.json', right)
write('provenance.json', {
    'schema':'yggdrasil.ckad24.coverage-continuation.provenance.v1',
    'preregistration_commit':'02c595156ce9c9ef18d55c588fe7bdc99bf86a16',
    'parent':'be46b0409b0c4bfc9b30e595ae19b62ccb1cf007',
    'training_source_sha':source,'training_run_id':run_id,'stable_sha256':pin,
    'source_sha256':left['source_sha256'],
    'original_source_actions':0,'protected_first_use':0,
    'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
    'advance_as_qualified_scientific_parent':False,
})
def human(value):
    if isinstance(value, list) and len(value) == 2 and all(type(v) is int for v in value) and value[1] > 0:
        return {'ratio':value,'decimal':value[0]/value[1]}
    if isinstance(value, dict):
        return {key:human(item) for key,item in value.items()}
    if isinstance(value, list):
        return [human(item) for item in value]
    return value

report = f'''# CKAD24 continued native learning with recent action coverage

**{left['classification']}**. This is a frozen synthetic development acquisition
comparison, not a scientific superiority or deployment acceptance.

Every acquisition arm begins from each same qualified CKAD23 full state with640
episodes and stream_start448. All continue192 new episodes, retaining832 each.
No initial reset, source phase notification, new detector rule, checkpoint schema,
cognitive architecture or controller is introduced. Candidate exploration balances
action counts over the last32 total witnessed rows after filtering by the learned
public context and decision history, using existing hypothesis disagreement on ties.
Matched controls include unchanged native acquisition, uniform random and coverage
with uniform ties; pooled and trailing64MLE read exact candidate receipts. The
independent same-method exact mixture must tie and cannot establish superiority.

Frozen gates:
```json
{json.dumps(left['development_gates'], indent=2, sort_keys=True)}
```
Metrics (ratios and display decimals):
```json
{json.dumps(human(left['development_metrics']), indent=2, sort_keys=True)}
```

Source SHA:{source}. Preregistration FIRST:02c595156ce9c9ef18d55c588fe7bdc99bf86a16.
Training, Windows replication and qualification run:{run_id}.
Semantic result SHA256:{pin}.

The primary results and all negative predicates are preserved. The unchanged
detector's sensitivity is descriptive; more action coverage is not a guaranteed
change-detection repair. These are fresh draws from already learned structural
families, not novel-family discovery or original-world transfer. If development
criteria fail, the new states remain negative research artifacts and do not replace
the qualified CKAD23 parent for subsequent scientific acceptance.

Cost receipts for both platforms are retained in the raw JSON. Parent and child
process CPU/peak measurements are separate; a simultaneous process-tree peak,
equal compute and a2x gain are not asserted. Setup, auditing, CI, authoring and
original source acquisition are additional to campaign timings.

Reproduce:python -B research/contrib/chatgpt/CKAD-24/campaign.py --output-directory /tmp/ckad24
Audit:python -B research/contrib/chatgpt/CKAD-24/independent_audit.py
Tamper controls:python -B research/contrib/chatgpt/CKAD-24/audit_negative_controls.py

Full final candidate Linux/Windows regression and independent CKAD13–24/G29
qualification are separate workflow jobs. Protected original-source actions,
held updates, paid APIs, merge, promotion and deployment remain zero/none.
'''
(HERE / 'SESSION_REPORT.md').write_text(report, encoding='utf-8')
subprocess.check_call([sys.executable, '-B', str(HERE/'independent_audit.py'), str(HERE)], cwd=ROOT)
subprocess.check_call([sys.executable, '-B', str(HERE/'audit_negative_controls.py'), str(HERE)], cwd=ROOT)
print(json.dumps({'sealed':True,'classification':left['classification'],'stable_sha256':pin}))
