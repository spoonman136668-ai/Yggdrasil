"""Source-free CVH02 policy seam tests; all environments are fabricated mocks."""
import hashlib
import json
import sys
from pathlib import Path
from collections import namedtuple
import unittest

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'CVH-01'
if not PARENT.exists():
    PARENT = HERE.parent/'cvh01'/'CVH-01'
sys.path.insert(0,str(PARENT))
from earned_memory import EarnedReturnMemory
from strong_conventional import batch_public_returns
from public_policy import PublicEarnedPolicy, _canonical

P = namedtuple('PublicConsequence',('before','action','reward','after','terminated','truncated'))


class ForbiddenInfo:
    def __getattribute__(self, name):
        raise AssertionError('PRIVATE_SOURCE_INFO_ACCESSED')


class MockSource:
    def __init__(self, finish=5):
        self.state=0
        self.n=0
        self.finish=finish
        self.closed=0
        self.reset_count=0
        self.used=[]

    def reset(self, *, seed):
        self.reset_count += 1
        self.state=0
        return self.state,ForbiddenInfo()

    def do(self, callback):
        a=callback(self.state)
        if type(a) is not int or a not in (0,1):
            raise AssertionError('WRONG_ACTION')
        b=self.state
        self.state=(self.state+a+1)%2
        self.n+=1
        self.used.append((b,a))
        return self.state,int(a==1),False,self.n>=self.finish,ForbiddenInfo()

    def close(self):
        self.closed+=1


def drive_mock(policy, source, max_actions=32):
    # Faithful six-field public choose/observe order of FKP24's trusted adapter.
    state, _private = source.reset(seed=996100) # strictly MOCK, not original CausalGym.
    rows=[]
    for i in range(max_actions):
        selected=policy.choose(state,tuple(rows))
        def closure(observed):
            if observed!=state: raise AssertionError('SOURCE_OBSERVATION_DRIFT')
            return selected
        nxt,reward,done,truncated,_private=source.do(closure)
        row=P(state,selected,reward,nxt,bool(done),bool(truncated))
        policy.observe(row)
        rows.append(row)
        state=nxt
        if done or truncated:break
    source.close()
    return rows


class PublicPolicyTests(unittest.TestCase):
    def test_01_two_completed_mock_episodes_retain_and_match_batch(self):
        m=PublicEarnedPolicy()
        one=drive_mock(m,MockSource(finish=5))
        two=drive_mock(m,MockSource(finish=5))
        c,t=batch_public_returns(one+two)
        self.assertEqual((m.memory.count,m.memory.total),(c,t))
        self.assertEqual(m.memory.seen,10)
        self.assertEqual(sum(m.attempts),10)
        self.assertEqual(m.episode_history,[])
        self.assertEqual(m.memory.pending,[])
        self.assertTrue(any(v>0 for v in m.memory.total))

    def test_02_public_delayed_credit_and_context_leak_prevented(self):
        m=PublicEarnedPolicy(min_support=2)
        self.assertIsNone(m.memory.choose_supported(0,2,2,2))
        for a in [0,1,0,1]:
            # Public-only fabricated consequence. Action must match chosen result.
            events=[P(0,a,0,0,False,False),P(0,0,0,0,False,False),
                    P(0,0,a,0,False,False),P(0,0,0,0,True,False)]
            for e in events:m.memory.observe(e)
        self.assertEqual(m.memory.choose_supported(0,2,2,2),1)

    def test_03_cold_completed_episode_roundtrip_and_next_episode(self):
        m=PublicEarnedPolicy()
        r1=drive_mock(m,MockSource(finish=7))
        cold=PublicEarnedPolicy.restore(m.snapshot())
        self.assertEqual(cold.snapshot(),m.snapshot())
        r2=drive_mock(m,MockSource(finish=4))
        rr2=drive_mock(cold,MockSource(finish=4))
        self.assertEqual(r2,rr2)
        self.assertEqual(m.snapshot(),cold.snapshot())

    def test_04_cold_mid_episode_in_same_live_source(self):
        m=PublicEarnedPolicy()
        source=MockSource(finish=5)
        s,_=source.reset(seed=996100)
        hist=[]
        for step in range(3):
            a=m.choose(s,tuple(hist))
            new,r,d,t,_=source.do(lambda _:a)
            row=P(s,a,r,new,d,t)
            m.observe(row)
            hist.append(row)
            s=new
        cloned=PublicEarnedPolicy.restore(m.snapshot())
        self.assertEqual(cloned.snapshot(),m.snapshot())
        self.assertEqual(cloned.choose(s,tuple(hist)),m.choose(s,tuple(hist)))
        self.assertEqual(cloned.outstanding,m.outstanding)
        with self.assertRaisesRegex(ValueError,'CANNOT_SNAPSHOT'):
            cloned.snapshot()

    def test_05_ambiguous_budget_exhaustion_cannot_start_new_episode(self):
        m=PublicEarnedPolicy()
        rows=drive_mock(m,MockSource(finish=100),max_actions=2)
        self.assertEqual(len(rows),2)
        self.assertIsNotNone(m.memory.previous_after)
        with self.assertRaisesRegex(ValueError,'HISTORY_DRIFT'):
            m.choose(0,())
        self.assertEqual(len(m.episode_history),2)

    def test_06_forged_private_extra_field_refused_atomically(self):
        m=PublicEarnedPolicy()
        a=m.choose(0,())
        raw_before=m.memory.snapshot()
        Extra=namedtuple('Extra',P._fields+('source_future',))
        bad=Extra(0,a,1,0,False,False,ForbiddenInfo())
        with self.assertRaisesRegex(ValueError,'PUBLIC_FIELDS'):
            m.observe(bad)
        self.assertEqual(m.memory.snapshot(),raw_before)
        self.assertEqual(m.outstanding,(0,a))
        with self.assertRaisesRegex(ValueError,'IN_FLIGHT'):
            m.choose(0,())

    def test_07_wrong_state_action_and_history_do_not_update_memory(self):
        m=PublicEarnedPolicy()
        with self.assertRaises(ValueError):m.choose(True,())
        with self.assertRaises(ValueError):m.choose(0,[])
        with self.assertRaises(ValueError):m.observe(P(0,0,1,0,False,False))
        action=m.choose(0,())
        before=m.memory.snapshot()
        with self.assertRaises(ValueError):m.observe(P(0,1-action,1,0,False,False))
        self.assertEqual(before,m.memory.snapshot())
        m.observe(P(0,action,0,1,False,False))
        with self.assertRaises(ValueError):m.choose(0,tuple([P(0,action,0,1,False,False)]))
        with self.assertRaises(ValueError):m.choose(1,())

    def test_08_cold_tampering_or_validly_rehashed_semantic_forgery(self):
        m=PublicEarnedPolicy()
        drive_mock(m,MockSource(finish=3))
        raw=m.snapshot()
        forged=bytearray(raw);forged[20]^=1
        with self.assertRaises(ValueError):PublicEarnedPolicy.restore(bytes(forged))
        doc=json.loads(raw)
        doc['payload']['attempts'][0] = -1
        doc['sha256']=hashlib.sha256(_canonical(doc['payload'])).hexdigest()
        with self.assertRaises(ValueError):PublicEarnedPolicy.restore(_canonical(doc))

    def test_09_no_real_source_code_import(self):
        import inspect
        import public_policy
        raw=inspect.getsource(public_policy)
        self.assertNotIn('causal_gym',raw.split('from __future__ import annotations',1)[1])
        self.assertNotIn('.do(',raw)
        self.assertNotIn('.reset(',raw)
        self.assertNotIn('native_source_factory(',raw)
        self.assertEqual(len(P._fields),6)


if __name__=='__main__':unittest.main()
