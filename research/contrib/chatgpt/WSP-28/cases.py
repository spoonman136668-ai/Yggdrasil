"""Evaluator-only dataset identity validation, never imported by the learner."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST_SHA='451987dfc6bd29c0f6af28da74f85d14bbb0102c422d3e95034bf9dd905a3636'

def validate_manifest(d):
    old=json.loads((ROOT.parent/'WSP-23/workload-trace.json').read_text())
    oldset={c['observed_target'] for c in old};expected=[]
    for c in old:
        target=c['observed_target']^32
        if target not in oldset:expected.append({'seed':c['seed'],'signature':c['original_signature'],'old_target':c['observed_target'],'target':target,'protected_mask':c['protected_mask']})
    if type(d) is not dict or set(d)!={'schema','construction','old_unique_observed_targets','cases'} or d['schema']!='wsp28.disjoint-label-cases.v1':raise ValueError('WSP28_BAD_MANIFEST_SCHEMA')
    if d['old_unique_observed_targets']!=sorted(oldset) or d['cases']!=expected or len(expected)!=120 or len({x['target'] for x in expected})!=30:raise ValueError('WSP28_MANIFEST_NOT_DISJOINT_OR_COMPLETE')
    if any(type(v) is not int for c in d['cases'] for v in c.values()):raise ValueError('WSP28_BAD_MANIFEST_TYPES')
    return d

def load_manifest(path=None):
    # Normalize transport line endings; hash is of the exact LF Git source text.
    raw=(ROOT/'cases.json' if path is None else Path(path)).read_bytes().replace(b'\r\n',b'\n')
    if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA:raise ValueError('WSP28_MANIFEST_HASH_MISMATCH')
    try:return validate_manifest(json.loads(raw))
    except (TypeError,KeyError,UnicodeError,RecursionError):raise ValueError('WSP28_BAD_MANIFEST') from None
