#!/usr/bin/env python3
"""NCI-SOURCE-02 read-only public-ingress contract audit.

No original-world actions, model training, checkpoint writes, or hidden data.
With --sources, checks EXACT pinned upstream/native source blobs and executes
ONLY the original NativeEpisodeExperience.observe method isolated with a
restricted test-double for ledger storage; does not import/train native model.
Without --sources, tests the public contract with invented examples only.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

SOURCE_FILES = {
    'native_episode': ('native_episode_experience.py', '5a18b00a4c4131526e71f51d63dfd9eb9471c81e'),
    'native_amalgam': ('native_causal_amalgam.py', '287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952'),
    'upstream_dtr': ('dtr.py', '6af2371dce21804140ea141ccb7be14e003ba275'),
    'upstream_mdp': ('mdp.py', '6264ec5450754c009e98c3e85f6d5927ece0a9ab'),
    'public_mdp': ('native_public_mdp.py', '4424eadef179996ff491911efadfbe4e07761062'),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def source_method(source: str, class_name: str, method_name: str):
    tree = ast.parse(source)
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == class_name)
    method = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == method_name)
    return method


def test_exact_observe_source(source: str) -> dict:
    """Execute the pinned original observe *method body* with a ledger-only stub.

    Intentionally not claiming an import, full class execution or trained state.
    """
    fn = copy.deepcopy(source_method(source, 'NativeEpisodeExperience', 'observe'))
    fn.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))

    def require(condition, code):
        if not condition:
            raise ValueError(code)

    def bit(value, kind):
        require(type(value) is int and value in (0, 1), kind)
        return value

    class Bits:
        _bit = staticmethod(bit)

    def views_check(views):
        require(type(views) is tuple and len(views) == 2, 'VIEWS')
        for pair in views:
            require(type(pair) is tuple and len(pair) == 2, 'VIEW')
            for elem in pair:
                bit(elem, 'VIEW_BIT')
        return views

    class Ledger:
        def __init__(self):
            self._ids = {}
            self._ledger = []
            self._episode_limit = 1152
        def _clone(self):
            replica = Ledger()
            replica._ids = self._ids.copy()
            replica._ledger = self._ledger[:]
            return replica
        def _accept(self, event):
            self._ids[event[0]] = event
            self._ledger.append(event)

    env = {'require': require, '_views': views_check,
           'pin': lambda x: type(x) is str and len(x) == 64 and all(c in '0123456789abcdef' for c in x),
           'ROW_FIELDS': ('s1','x1','s2','x2','y'), 'PublicCausalCells': Bits}
    namespace = {}
    exec(compile(module, '<exact-pinned-native-observe>', 'exec'), env, namespace)
    observe = namespace['observe']
    k = 'b' * 64
    views = ((0, 0), (0, 1))
    good = dict(s1=0, x1=1, s2=1, x2=0, y=0)
    bad = dict(good, s1=1)
    good_after = observe(Ledger(), k, views, good)
    bad_after = observe(Ledger(), k, views, bad)
    assert good_after._ledger == bad_after._ledger, 'EXPECTED_COLLISION_NO_LONGER_PRESENT'
    assert len(good_after._ledger) == 1
    repeated = observe(good_after, k, views, bad)
    assert repeated is good_after, 'EXPECTED_CONFLICTING_ROW_REPLAY_NO_LONGER_ALIAS'
    invalid = dict(good, s1=2)
    try:
        observe(Ledger(), k, views, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('INVALID_BIT_NOT_REFUSED')
    return {'tested_original_method': True, 'two_distinct_public_s1_values_one_stored_event': True,
            'same_identifier_changed_s1_not_detected': True,
            'invalid_nonbinary_s1_refused': True}


def require_text(source: str, literal: str, label: str):
    if literal not in source:
        raise ValueError('PINNED_SOURCE_SIGNATURE_DRIFT_' + label)


def sources_check(locations: dict[str, Path]):
    texts = {}
    for name, path in locations.items():
        raw = path.read_bytes()
        assert git_blob(raw) == SOURCE_FILES[name][1], (name, git_blob(raw))
        texts[name] = raw.decode('utf-8')
        ast.parse(texts[name])
    require_text(texts['upstream_dtr'], 'do_policy(self.env.s1)', 'DTR_INITIAL')
    require_text(texts['upstream_dtr'], 'do_policy(self.env.s1, self.env.x1, self.env.s2)', 'DTR_STAGE2')
    require_text(texts['upstream_mdp'], 'do_policy(self.env.s)', 'MDP_PUBLIC_CALLBACK')
    require_text(texts['public_mdp'], 'policy.choose(state,tuple(events))', 'FKP24_PUBLIC_HISTORY')
    require_text(texts['public_mdp'], 'result[4] (info) is NEVER accessed', 'FKP24_PRIVILEGE_FENCE')
    require_text(texts['native_amalgam'], 'views[0][0] == views[1][0]', 'VIEW_CONSISTENCY')
    require_text(texts['native_amalgam'], 'row = {"s1": views[0][0]', 'RESTORE_RECONSTRUCTION')
    require_text(texts['native_episode'], 'event = (identifier, views, *bits[1:])', 'S1_PROJECTION')
    proof = test_exact_observe_source(texts['native_episode'])
    return {'pin_count': len(texts), 'pinned_git_blobs_pass': True,
            'upstream_dtr_public_stage1': ['s1'],
            'upstream_dtr_public_stage2': ['s1','x1','s2'],
            'upstream_mdp_public_callback': ['state'],
            'fkp24_public_transition': ['before','action','reward','after','terminated','truncated'],
            'native_observe': proof}


def check_proposed_guard(s1: int, views) -> bool:
    """Proposed new contract only; NOT installed in NativeEpisodeExperience."""
    if type(s1) is not int or s1 not in (0, 1):
        return False
    if type(views) is not tuple or len(views) != 2:
        return False
    if any(type(p) is not tuple or len(p) != 2 for p in views):
        return False
    if any(type(v) is not int or v not in (0, 1) for p in views for v in p):
        return False
    return s1 == views[0][0] == views[1][0]


class ProposedContractTests(unittest.TestCase):
    def test_valid_shared_s1(self):
        self.assertTrue(check_proposed_guard(0, ((0,0),(0,1))))
    def test_mismatched_public_s1(self):
        self.assertFalse(check_proposed_guard(1, ((0,0),(0,1))))
    def test_mismatched_views(self):
        self.assertFalse(check_proposed_guard(0, ((0,0),(1,1))))
    def test_refuse_missing_view(self):
        self.assertFalse(check_proposed_guard(0, ((0,0),)))
    def test_refuse_nonbinary(self):
        self.assertFalse(check_proposed_guard(0, ((0,2),(0,1))))
    def test_refuse_string_bit(self):
        self.assertFalse(check_proposed_guard('0', ((0,0),(0,1))))
    def test_legacy_view_projection_collision(self):
        views = ((0,0),(0,1))
        def projected(s1):
            row = (s1,1,1,0,0)
            return (views, *row[1:])
        self.assertEqual(projected(0), projected(1))
    def test_guard_distinguishes_collision(self):
        views = ((0,0),(0,1))
        self.assertNotEqual(check_proposed_guard(0, views), check_proposed_guard(1, views))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-episode', type=Path)
    parser.add_argument('--native-amalgam', type=Path)
    parser.add_argument('--upstream-dtr', type=Path)
    parser.add_argument('--upstream-mdp', type=Path)
    parser.add_argument('--public-mdp', type=Path)
    parser.add_argument('--report', type=Path)
    a = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProposedContractTests)
    scored = unittest.TestResult()
    suite.run(scored)
    assert scored.testsRun == 8 and not scored.failures and not scored.errors
    args = {name:getattr(a,name) for name in SOURCE_FILES}
    if any(p is not None for p in args.values()):
        if not all(p is not None for p in args.values()):
            raise SystemExit('ALL_FIVE_PINNED_SOURCE_PATHS_REQUIRED')
        evidence = sources_check(args)
        state = 'PINNED_INGRESS_METHOD_CONSISTENCY_GAP_DEMONSTRATED'
    else:
        evidence = {'source_method_execution':'NOT_RUN_NO_EXACT_LOCAL_SOURCE',
                    'pinned_references':'independently read from original GitHub blobs, not fetched by this tool'}
        state = 'PROPOSED_CONTRACT_FIXTURE_ONLY'
    result = {'schema':'nci-source-02.public-ingress-audit.v1',
              'classification':state,
              'local_source_free_contract_tests':scored.testsRun,
              'local_source_free_contract_tests_pass':True,
              'scientific_status':'UNVERIFIED', 'native_training':False,'source_actions':0,
              'checkpoint_mutation':False,
              'source_evidence':evidence}
    out = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.report:
        if a.report.exists():
            raise SystemExit('REFUSE_REPORT_OVERWRITE')
        a.report.write_text(out,encoding='utf8')
    print(out,end='')


if __name__=='__main__':
    main()
