"""Post-result Yggdrasil CB7 regret attribution. NO source execution/first-use.

Uses only pinned original public world *configuration* and CB7 policies,
plus the SHA-frozen world-level net returns of the already-consumed run.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
EXCERPT_SHA256 = '3386643d415cc27f4eb3a74e4cf7bfc502c6be2a7bba355ebe89595b0f8ec728'
POLICY_BLOB = 'af0809fd61a51bdfdd504aedf611449f55b572f1'
WORLD_BLOB = 'c0b6c2ad5a874162f1963833f3261e360c57ee46'
WORLD_DIGEST = '2a296ecd8c48cdb1b05c2b42801d82bc6b9c85d9c8f126e1ddf8bb401bbf37d2'


def _gitblob(content):
    return hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()


def _pin_module(name, blob):
    original=ROOT.parent/'FKP18-CB7'/name
    if not original.exists():  # exact-byte local mirror; never bypass hash pin
        original=Path('/mnt/data/cb7local')/name
    source=original.read_bytes()
    if _gitblob(source)!=blob: raise ValueError('CB7_FORENSIC_SOURCE_BLOB_DRIFT')
    spec=importlib.util.spec_from_file_location('_frozen_cb7_'+name.replace('.','_'),original)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit():
    src=_pin_module('public_world.py',WORLD_BLOB)
    m=_pin_module('policies.py',POLICY_BLOB)
    source=(ROOT/'world_net.json').read_bytes()
    if hashlib.sha256(source).hexdigest()!=EXCERPT_SHA256:
        raise ValueError('CB7_FORENSIC_ARCHIVED_WORLD_NET_DRIFT')
    archive=json.loads(source)
    if archive.get('original_world_sha256')!=WORLD_DIGEST or archive.get('schema')!='yggdrasil.cb7.frozen-world-net.v1':
        raise ValueError('CB7_FORENSIC_CUSTODY')
    rows=archive['rows']
    if len(rows)!=32 or [r[0] for r in rows]!=list(range(82600,82632)):
        raise ValueError('CB7_FORENSIC_COHORT_DRIFT')
    groups={name:[] for name in ('stops_early','different_first_probe','same_first_later_diverges','equal_expected_return')}
    audit_rows=[]
    for seed,direct_net,bayes_net in rows:
        prior,costs=src.public_config(seed)  # public metadata only; no World/probe
        greedy=m.DirectOneStep(prior,costs)
        exact=m.ExactBayesianDP(prior,costs)
        if abs(exact.expected_optimal-bayes_net)>1e-10:
            raise ValueError('CB7_FORENSIC_SOURCE_SCORE_NOT_OPTIMAL')
        regret=bayes_net-direct_net
        if regret < -1e-10: raise ValueError('CB7_FORENSIC_BAYES_DOMINANCE')
        first_g=greedy.next_probe();first_b=exact.next_probe()
        if regret < 1e-10: kind='equal_expected_return'
        elif first_g is None and first_b is not None: kind='stops_early'
        elif first_g != first_b: kind='different_first_probe'
        else: kind='same_first_later_diverges'
        groups[kind].append((seed,max(0.,regret)))
        audit_rows.append([seed,first_g,first_b,kind,max(0.,regret)])
    mean=sum(x[4] for x in audit_rows)/32
    stats={k:{'worlds':len(v),'seeds':[x[0] for x in v],
              'contribution_to_world_average_regret':sum(x[1] for x in v)/32}
           for k,v in groups.items()}
    return {'schema':'yggdrasil.cb7.posthoc-regret-audit.v1',
      'source_first_use':False,'actual_new_paid_actions':0,'model_training':0,
      'mean_net_direct':statistics.mean(x[1] for x in rows),
      'mean_net_bayes':statistics.mean(x[2] for x in rows),
      'mean_regret':mean,'groups':stats,
      'stop_early_regret_fraction':stats['stops_early']['contribution_to_world_average_regret']/mean,
      'per_world_decision_receipts':audit_rows,
      'scientific_pass':False,
      'interpretation':'Post-result failure attribution; dominant gap is contingent multi-step action value.'}

if __name__=='__main__':
    print(json.dumps(audit(),indent=2,sort_keys=True))
