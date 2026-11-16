"""CVH01 frozen source-free engineering tests; NO original CausalGym first use."""
from __future__ import annotations
from collections import namedtuple
from hashlib import sha256
from pathlib import Path
import ast
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-24"))
from native_public_mdp import PublicConsequence as P  # Import is lazy and side-effect-free.
import earned_memory as m
from strong_conventional import batch_public_returns,immediate_only_public_returns


def episode(action, rewarded):
    # Exactly one delayed earned consequence at time t+2.
    return [
      P(0,action,0,0,False,False),
      P(0,0,0,0,False,False),
      P(0,0,rewarded,0,False,False),
      P(0,0,0,0,True,False),
    ]


def tape():
    return (episode(0,0)+episode(1,1)+
            [P(1,1,0,0,False,False),P(0,1,0,1,False,False),
             P(1,0,1,1,False,False),P(1,1,0,0,True,False)]+
            episode(1,1)+episode(0,0))


class PublicTemporalMemoryTests(unittest.TestCase):
    def test_01_exact_delayed_reward_at_two_steps(self):
        learner=m.EarnedReturnMemory()
        events=episode(1,1)
        for e in events:learner.observe(e)
        key=m._slot(2,2,0,1)
        self.assertEqual(learner.count[key],1)
        self.assertEqual(learner.total[key],2)
        self.assertAlmostEqual(learner.estimate(0,2,2,1),.25)
        _,immediate=immediate_only_public_returns(events)
        self.assertEqual(immediate[key],0)

    def test_02_same_present_state_distinct_predecessor_context(self):
        learner=m.EarnedReturnMemory()
        for e in [P(0,0,0,0,False,False),P(0,1,0,0,False,False),
                  P(0,1,1,0,False,False),P(0,1,0,0,True,False)]:
            learner.observe(e)
        base=m._slot(2,2,0,0)
        conditioned=m._slot(0,0,0,1)
        self.assertNotEqual(base,conditioned)
        self.assertEqual(learner.count[base],1)
        self.assertEqual(learner.count[conditioned],1)

    def test_03_terminal_and_truncation_flush_without_episode_leak(self):
        learner=m.EarnedReturnMemory()
        for e in [P(0,1,0,0,False,False),P(0,0,1,0,True,False),
                  P(1,1,1,1,False,True)]:
            learner.observe(e)
        k=m._slot(2,2,0,1)
        self.assertEqual(learner.total[k],4)
        self.assertEqual(learner.pending,[])
        self.assertIsNone(learner.previous_after)
        self.assertEqual(learner.prev_action,2)
        self.assertEqual(learner.prev_reward,2)

    def test_04_cold_midstream_exact_future_updates(self):
        events=tape()
        uninterrupted=m.EarnedReturnMemory()
        for e in events:uninterrupted.observe(e)
        before=m.EarnedReturnMemory()
        for e in events[:3]:before.observe(e)
        self.assertEqual(len(before.pending),3)
        cold=m.EarnedReturnMemory.restore(before.snapshot())
        self.assertEqual(cold.snapshot(),before.snapshot())
        for e in events[3:]:cold.observe(e)
        self.assertEqual(cold.snapshot(),uninterrupted.snapshot())
        self.assertEqual(cold.receipt(),uninterrupted.receipt())

    def test_05_strong_independent_batch_conventional_exact_tie(self):
        for cut in (0,1,2,3,4,len(tape())):
            events=tape()[:cut]
            learner=m.EarnedReturnMemory()
            for e in events:learner.observe(e)
            expected_count,expected_total=batch_public_returns(events)
            self.assertEqual(learner.count,expected_count)
            self.assertEqual(learner.total,expected_total)
        learner=m.EarnedReturnMemory()
        for e in tape():learner.observe(e)
        c,t=batch_public_returns(tape())
        self.assertEqual((learner.count,learner.total),(c,t))

    def test_06_delayed_credit_changes_supported_decision(self):
        learner=m.EarnedReturnMemory()
        self.assertIsNone(learner.choose_supported(0,2,2))
        for a in (0,1,0,1):
            for e in episode(a,a):learner.observe(e)
        self.assertEqual(learner.choose_supported(0,2,2,min_support=2),1)
        self.assertAlmostEqual(learner.estimate(0,2,2,0),0.)
        self.assertAlmostEqual(learner.estimate(0,2,2,1),.25)

    def test_07_invalid_extra_private_fields_fail_atomically(self):
        learner=m.EarnedReturnMemory()
        good=P(0,0,0,0,False,False)
        Extra=namedtuple("Extra",m.FIELDS+("private_info",))
        bad=(Extra(*good,{"future":1}),P(True,0,0,0,False,False),
             P(0,True,0,0,False,False),P(0,0,1.0,0,False,False),
             P(0,0,0,0,True,True),P(0,0,0,0,0,False))
        before=learner.snapshot()
        for v in bad:
            with self.assertRaises(ValueError):learner.observe(v)
            self.assertEqual(before,learner.snapshot())
        learner.observe(good)
        checkpoint=learner.snapshot()
        with self.assertRaises(ValueError):learner.observe(P(1,0,0,0,False,False))
        self.assertEqual(checkpoint,learner.snapshot())

    def test_08_cold_invalid_checksum_and_semantic_forgery_rejected(self):
        learner=m.EarnedReturnMemory()
        for e in episode(1,1):learner.observe(e)
        raw=learner.snapshot()
        forged=bytearray(raw);forged[-8]^=1
        with self.assertRaises(ValueError):m.EarnedReturnMemory.restore(bytes(forged))
        doc=json.loads(raw)
        doc["payload"]["count"][0]=-1
        doc["sha256"]=sha256(m._canonical(doc["payload"])).hexdigest()
        validly_rehashed=m._canonical(doc)
        with self.assertRaises(ValueError):m.EarnedReturnMemory.restore(validly_rehashed)

    def test_09_unfinished_partial_is_not_imagined_as_full_return(self):
        learner=m.EarnedReturnMemory()
        rows=episode(1,1)
        for e in rows[:3]:learner.observe(e)
        key=m._slot(2,2,0,1)
        self.assertEqual(learner.count[key],0)
        self.assertIsNone(learner.estimate(0,2,2,1))
        c,t=batch_public_returns(rows[:3])
        self.assertEqual(c,learner.count)
        self.assertEqual(t,learner.total)

    def test_10_no_source_import_or_external_actions(self):
        for path in (m.__file__,sys.modules["strong_conventional"].__file__):
            source=Path(path).read_text()
            parsed=ast.parse(source)
            names=set()
            for node in ast.walk(parsed):
                if isinstance(node,ast.Import):names.update(x.name for x in node.names)
                elif isinstance(node,ast.ImportFrom):names.add(node.module)
            self.assertNotIn("causal_gym",names)
            self.assertNotIn("native_public_mdp",names)
            self.assertNotIn("public_world",names)
            self.assertNotIn("public_source",names)
            self.assertNotIn(".do(",source)
        self.assertEqual(m.CONTEXTS,36)


if __name__=="__main__":unittest.main()
