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
        raise RuntimeError('CKAD25_SEAL_' + label)

def unique(root, name):
    matches = list(root.rglob(name))
    check(len(matches) == 1, 'UNIQUE_' + name)
    return matches[0]

def write(name, value):
    (HERE / name).write_bytes((json.dumps(value, indent=2, sort_keys=True) + '\n').encode('ascii'))

left_root = Path(os.environ['CKAD25_LINUX_DIRECTORY'])
right_root = Path(os.environ['CKAD25_WINDOWS_DIRECTORY'])
source = os.environ['CKAD25_SOURCE_COMMIT']
run_id = int(os.environ['CKAD25_EVIDENCE_RUN'])
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
    check(name == f"seed-{case['seed']}-capacity-native.json", 'STATE_NAME')
    raw = unique(left_root, name).read_bytes()
    replica = unique(right_root, name).read_bytes()
    check(raw == replica and len(raw) == case['final_checkpoint_bytes']
          and digest(raw) == case['final_checkpoint_sha256'], 'STATE_BYTES')
    (HERE / name).write_bytes(raw)
write('campaign-result.json', left)
write('replication-windows.json', right)
write('provenance.json', {
    'schema':'yggdrasil.ckad25.remote-retention-capacity.provenance.v1',
    'preregistration_commit':'c91ca6d65040cf5eec593fce73597aa83f39c0dc',
    'parent':'a5faea392679756f172b87f3e40399ed88329a06',
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

report = f"""# CKAD25 remote causal retention through native capacity

**{left['classification']}**. Frozen synthetic development evidence only;
strongest-control scientific superiority and deployment remain unestablished.

The unchanged native learner continues three qualified CKAD24 states from832 to
1024 witnessed episodes. Its inherited stream_start448, context, detector score,
prior witnesses and legacy learned planes are preserved. No native code, policy,
capacity, checkpoint schema, representation class or controller is replaced.

Remote previously learned families return under unequal evaluator-side durations:
context-switch0 for48 episodes, terminal-switch0 for32, context-switch1 for64,
then invariant0 for48. Boundaries48/80/144 and family/regime labels never reach
learner callbacks. Cohorts and source seeds are disjoint from previous campaigns.

Primary criteria assess ALL13 held checkpoints and every replica; a separate
preset improvement over the frozen832-state readout uses16 observations into
each phase (counts16,64,96,160). Final return tests retention. This does not
claim new-family discovery or original-world transfer.

Frozen gates:
```json
{json.dumps(left['development_gates'], indent=2, sort_keys=True)}
```
Frozen metrics (exact ratios plus display decimals):
```json
{json.dumps(human(left['development_metrics']), indent=2, sort_keys=True)}
```

Training source SHA:{source}.
Preregistration FIRST:c91ca6d65040cf5eec593fce73597aa83f39c0dc.
Training, Windows reproduction and qualification run:{run_id}.
Linux/Windows semantic result SHA256:{pin}.

Four acquisition arms share the same832-state initialization and equal data/action
budgets: coverage plus disagreement, original disagreement, uniform random, and
coverage with uniform ties. All8 held controls, including pooled replay, trailing64
MLE, frozen parent and independent exact mixture, are preserved. The strongest
same-method exact control must tie; scientific superiority is not established by
passing development thresholds. Nulls and per-replica losses remain recorded.

At count80 a fresh process learns the next actual revealed receipt from the full
912-event saved state, saves913 events, matches uninterrupted learning byte-exactly,
and supplies the state used for remaining training. The final1024-state cold readout
also matches. Full832-event prefixes and legacy state must remain byte-exact.

At capacity, a deliberately invalid unit admission copies a previously witnessed
public row under a distinct unit ID. It must be rejected with
CKAD_NATIVE_EPISODE_CAPACITY and leave checkpoint bytes unchanged. This is a guard
negative, not an authenticated new observation or an extra source episode/action.
No witnesses are evicted and the1024-event capacity is not increased.

Each campaign acquires2304 synthetic training episodes/4608 acquisition actions.
Held evaluation comprises3744 source episodes and8 policy paths plus a matched
Brier path:33696 evaluation trajectories/67392 synthetic evaluation action
callbacks. Windows reproduction and independent replay add compute. Held learning
updates, original-source actions, protected first-use and paid APIs remain0.

Parent/child CPU and individual process peaks are recorded in raw results. A
simultaneous process-tree peak, per-arm compute parity and a2x improvement are not
asserted. Setup, CI, audits, artifact handling and authoring are additional.

If any development predicate fails, preserve DEVELOPMENT_NO_GO and all saturated
states as negative research evidence. Do not silently replace the separately
qualified CKAD24 parent for scientific acceptance. Exact-candidate complete
Linux/Windows regression, independent CKAD13–25/G29 replay and tamper checks are
separate required workflow jobs.

Reproduce:python -B research/contrib/chatgpt/CKAD-25/campaign.py --output-directory /tmp/ckad25
Audit:python -B research/contrib/chatgpt/CKAD-25/independent_audit.py
Tamper checks:python -B research/contrib/chatgpt/CKAD-25/audit_negative_controls.py

No accepted-ref, source-owner/controller/scheduler change, merge, deployment or
interruption of independent research is authorized by this evidence. Protected
original-world first-use still requires its separate owner/cohort custody.
"""
(HERE / 'SESSION_REPORT.md').write_text(report, encoding='utf-8')
subprocess.check_call([sys.executable, '-B', str(HERE/'independent_audit.py'), str(HERE)], cwd=ROOT)
subprocess.check_call([sys.executable, '-B', str(HERE/'audit_negative_controls.py'), str(HERE)], cwd=ROOT)
print(json.dumps({'sealed':True,'classification':left['classification'],'stable_sha256':pin}))
