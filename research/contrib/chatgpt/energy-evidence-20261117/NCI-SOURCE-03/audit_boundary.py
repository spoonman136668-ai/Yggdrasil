#!/usr/bin/env python3
"""NCI-SOURCE-03: isolated Amalgam admission-boundary compatibility audit.

No source actor, no model import/training, no native checkpoint mutation. The
original method body is an excerpt of the pinned GitHub source. Optionally pass
the full exact original source for a strict Git blob / AST-body comparison.
"""
import argparse
import ast
import copy
import hashlib
import json
from itertools import product
from pathlib import Path

PINNED_AMALGAM_BLOB = '287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952'
PINNED_EPISODE_BLOB = '5a18b00a4c4131526e71f51d63dfd9eb9471c81e'
PINNED_AMALGAM_COMMIT = '86264b41a08d49f558418c0fba367f3a2636befa'
METHOD = '''class NativeCausalAmalgam:
    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        native = self.native.observe_experience(
            identifier, views, row, source_sha256=source_sha256, packet_sha256=packet_sha256)
        if native is self.native:
            return self
        require(views[0][0] == views[1][0], "AMALGAM_PAIRED_VIEW_COORDINATE")
        history = self.native._episode_reader()._ledger[-8:]
        transition = (row["x1"],)
        reward = (row["x1"], row["s2"], row["x2"])
        direct_t, direct_r, temporal_t, temporal_r = (head.clone() for head in self._heads)
        direct_t.observe(views, transition, row["s2"])
        direct_r.observe(views, reward, row["y"])
        temporal_t.observe(views, transition, history, row["s2"])
        temporal_r.observe(views, reward, history, row["y"])
        return NativeCausalAmalgam(native, (direct_t, direct_r, temporal_t, temporal_r),
                                  self._native_parent, self._specialist_parent)
'''


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def original_method():
    tree = ast.parse(METHOD)
    return tree.body[0].body[0]


def method_in_full_source(raw):
    tree = ast.parse(raw.decode('utf-8'))
    cl = next(v for v in tree.body if isinstance(v, ast.ClassDef)
              and v.name == 'NativeCausalAmalgam')
    return next(v for v in cl.body if isinstance(v, ast.FunctionDef)
                and v.name == 'observe_experience')


def require(check, code):
    if not check:
        raise ValueError(code)


def guard(s1, views):
    """Proposed preflight, to be placed BEFORE native.observe_experience.

    No changes to the model or resident checkpoint. Other native validation
    remains responsible for action/next-state/reward bit/shape enforcement.
    """
    require(type(views) is tuple and len(views) == 2 and
            all(type(v) is tuple and len(v) == 2 for v in views) and
            type(s1) is int and s1 in (0, 1) and
            all(type(v[0]) is int and v[0] in (0, 1) for v in views) and
            s1 == views[0][0] == views[1][0],
            'AMALGAM_PUBLIC_INITIAL_STATE_MISMATCH')


def source_functions():
    old = copy.deepcopy(original_method())
    new = copy.deepcopy(original_method())
    instruction = ast.parse('guard(row.get("s1") if type(row) is dict else None, views)').body[0]
    new.body.insert(0, instruction)

    def compile_method(method):
        ast_mod = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
        namespace = {}
        exec(compile(ast_mod, '<pinned-Amalgam-method-excerpt>', 'exec'),
             {'require': require, 'guard': guard, 'NativeCausalAmalgam': FixtureAmalgam}, namespace)
        return namespace['observe_experience']

    return compile_method(old), compile_method(new)


class FixtureHead:
    def __init__(self, name, observations=()):
        self.name, self.observations = name, tuple(observations)

    def clone(self):
        return FixtureHead(self.name, self.observations)

    def observe(self, *args):
        self.observations += (json.loads(json.dumps(args)),)

    def dump(self):
        return [self.name, list(self.observations)]


class FixtureEpisode:
    """Exact pinned projected EVENT format, not a full native implementation."""
    def __init__(self, ledger=()):
        self._ledger = tuple(ledger)


class FixtureNative:
    def __init__(self, episode=None):
        self.episode = episode or FixtureEpisode()
        self.calls = 0

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        self.calls += 1
        assert type(identifier) is str and len(identifier) == 64
        assert all(type(row[k]) is int and row[k] in (0, 1)
                   for k in ('s1', 'x1', 's2', 'x2', 'y'))
        assert len(views) == 2 and all(len(v) == 2 for v in views)
        assert source_sha256 == 'fixture-public-source' and packet_sha256 == 'fixture-packet'
        event = (identifier, views, row['x1'], row['s2'], row['x2'], row['y'])
        same_id = next((x for x in self.episode._ledger if x[0] == identifier), None)
        if same_id is not None:
            require(same_id == event, 'EPISODE_CONFLICTING_REPLAY')
            return self
        return FixtureNative(FixtureEpisode(self.episode._ledger + (event,)))

    def _episode_reader(self):
        return self.episode


class FixtureAmalgam:
    def __init__(self, native=None, heads=None, native_parent='preexisting-native', specialist_parent='preexisting-specialists'):
        self.native = native or FixtureNative()
        self._heads = heads or tuple(FixtureHead(n) for n in ('direct_t', 'direct_r','temporal_t','temporal_r'))
        self._native_parent, self._specialist_parent = native_parent, specialist_parent

    def snapshot(self):
        """Fixture serializable state (NOT a native amalgam checkpoint)."""
        return json.dumps({'ledger':self.native.episode._ledger,
                           'heads':[head.dump() for head in self._heads],
                           'native_parent':self._native_parent,
                           'specialist_parent':self._specialist_parent},sort_keys=True,separators=(',',':'))

    @classmethod
    def restore_fixture(cls, raw):
        data=json.loads(raw)
        history=[]
        for event in data['ledger']:
            history.append((event[0], tuple(tuple(x) for x in event[1]), *event[2:]))
        heads=tuple(FixtureHead(row[0], row[1]) for row in data['heads'])
        return cls(FixtureNative(FixtureEpisode(history)), heads,
                   data['native_parent'],data['specialist_parent'])


def attempt(fn, state, identifier, views, row):
    return fn(state, identifier, views, row,
              source_sha256='fixture-public-source', packet_sha256='fixture-packet')


def run_test(fn_old, fn_new):
    tally={'valid_first_admissions':0, 'valid_duplicate_replays':0,
           'valid_cold_fixture_replays':0, 'bad_s1_first_rejections':0,
           'bad_s1_duplicate_rejections':0, 'bad_view_duplicate_rejections':0,
           'legacy_bad_s1_first_accepted':0,
           'legacy_bad_s1_duplicate_silently_replayed':0,
           'legacy_bad_view_duplicate_silently_replayed':0,
           'native_calls_prevented_on_bad_s1_duplicate':0,
           'unchanged_valid_serialized_fixture_states':0}
    # 2 initial states, each two independent auxiliary-view bits, 16 valid
    # action/transition/terminal outcome bits: 128 independent valid cases.
    for s,p,q,x1,s2,x2,y in product((0,1),repeat=7):
        views=((s,p),(s,q))
        row={'s1':s,'x1':x1,'s2':s2,'x2':x2,'y':y}
        ident=(f'{s}{p}{q}{x1}{s2}{x2}{y}'*10)[:64]
        baseline=FixtureAmalgam()
        before=baseline.snapshot()
        old=attempt(fn_old,baseline,ident,views,row)
        fresh=attempt(fn_new,FixtureAmalgam(),ident,views,row)
        assert old.snapshot()==fresh.snapshot()
        assert before==FixtureAmalgam().snapshot()  # copy-on-write
        assert len(fresh.native.episode._ledger)==1
        assert all(len(head.observations)==1 for head in fresh._heads)
        assert fresh._native_parent=='preexisting-native'
        tally['valid_first_admissions']+=1
        tally['unchanged_valid_serialized_fixture_states']+=1
        assert attempt(fn_old,old,ident,views,row) is old
        assert attempt(fn_new,fresh,ident,views,row) is fresh
        tally['valid_duplicate_replays']+=1

        cold=FixtureAmalgam.restore_fixture(fresh.snapshot())
        assert cold.snapshot()==fresh.snapshot()
        # Actual NativeCausalAmalgam.restore reconstructs row s1 from view.
        restored_row=dict(row,s1=views[0][0])
        assert attempt(fn_new,cold,ident,views,restored_row) is cold
        assert cold.snapshot()==fresh.snapshot()
        tally['valid_cold_fixture_replays']+=1

        altered=dict(row,s1=1-s)
        legacy=attempt(fn_old,FixtureAmalgam(),ident,views,altered)
        assert legacy.snapshot()==fresh.snapshot()
        tally['legacy_bad_s1_first_accepted']+=1
        try:
            attempt(fn_new,FixtureAmalgam(),ident,views,altered)
        except ValueError as exc:
            assert str(exc)=='AMALGAM_PUBLIC_INITIAL_STATE_MISMATCH'
        else:
            raise AssertionError('altered first event accepted')
        tally['bad_s1_first_rejections']+=1
        assert attempt(fn_old,old,ident,views,altered) is old
        tally['legacy_bad_s1_duplicate_silently_replayed']+=1
        calls=fresh.native.calls
        try:
            attempt(fn_new,fresh,ident,views,altered)
        except ValueError as exc:
            assert str(exc)=='AMALGAM_PUBLIC_INITIAL_STATE_MISMATCH'
        else:
            raise AssertionError('altered duplicate accepted')
        assert fresh.native.calls==calls
        assert fresh.snapshot()==old.snapshot()
        tally['native_calls_prevented_on_bad_s1_duplicate']+=1
        tally['bad_s1_duplicate_rejections']+=1

        # Incoming paired views disagree only in the initial-state bit; the
        # existing method's early idempotent return happens before its check.
        disagree=((s,p),(1-s,q))
        native_event_already=FixtureNative(FixtureEpisode([(ident,disagree,x1,s2,x2,y)]))
        dup_old=FixtureAmalgam(native=native_event_already)
        assert attempt(fn_old,dup_old,ident,disagree,row) is dup_old
        tally['legacy_bad_view_duplicate_silently_replayed']+=1
        dup_new=FixtureAmalgam(native=FixtureNative(FixtureEpisode([(ident,disagree,x1,s2,x2,y)])))
        try:
            attempt(fn_new,dup_new,ident,disagree,row)
        except ValueError as exc:
            assert str(exc)=='AMALGAM_PUBLIC_INITIAL_STATE_MISMATCH'
        else:
            raise AssertionError('bad view duplicate accepted')
        assert dup_new.native.calls==0
        tally['bad_view_duplicate_rejections']+=1
    assert all(v==128 for k,v in tally.items()), tally
    return tally


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--full-native-source', type=Path,
                        help='optional exact pinned full original Amalgam source to verify method AST and Git blob')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    validation='METHOD_EXCERPT_ONLY_STRICT_FULL_SOURCE_NOT_RUN'
    if args.full_native_source:
        raw=args.full_native_source.read_bytes()
        require(git_blob(raw)==PINNED_AMALGAM_BLOB,'FULL_NATIVE_BLOB_DRIFT')
        actual=method_in_full_source(raw)
        expected=original_method()
        require(ast.dump(actual,include_attributes=False)==ast.dump(expected,include_attributes=False),
                'PINNED_ORIGINAL_METHOD_DRIFT')
        validation='EXACT_FULL_GIT_BLOB_AND_METHOD_AST_PASS'
    old,new=source_functions()
    counts=run_test(old,new)
    report={
        'schema':'nci-source-03.boundary-admission-fixture.v1',
        'source_pinned_commit':PINNED_AMALGAM_COMMIT,
        'source_pinned_git_blob':PINNED_AMALGAM_BLOB,
        'source_method_qualification':validation,
        'classification':'ISOLATED_ADMISSION_METHOD_COMPATIBILITY_PASS',
        'guard_installed_in_native':False,
        'native_checkpoint_tested':False,
        'cold_restore_is_fixture_only':True,
        'original_source_first_use':False,
        'native_training':False,
        'scientific_pass':False,
        'counts':counts,
    }
    formatted=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if args.report:
        require(not args.report.exists(),'REFUSE_OVERWRITE')
        args.report.write_text(formatted,encoding='utf-8')
    print(formatted,end='')

if __name__=='__main__':
    main()
