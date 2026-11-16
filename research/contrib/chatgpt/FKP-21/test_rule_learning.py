"""FKP-21 exact-source public rule representation and identifiability negatives.

Only synthetic TRAIN source 993100 and its paired 993108 appear in focused
tests. No protected DEV/TRANSFER and no original predecessor cohort is read.
"""
import json
from collections import namedtuple
from pathlib import Path
import unittest

import public_rule_source as source
import rule_learning as m


class SourceOnlyRuleTests(unittest.TestCase):
    def test_disjoint_public_train_and_first_probe_split(self):
        self.assertEqual(source.TRAIN,tuple(range(993100,993116)))
        self.assertEqual(source.TRAIN_PATTERNS,
                         (3,4,5,6,8,9,10,11,12,13,14,15))
        self.assertEqual(source.FIRST_PROBES,(0,1,2,7))
        self.assertEqual(set(source.TRAIN_PATTERNS)&set(source.FIRST_PROBES),set())
        self.assertEqual(set(source.TRAIN_PATTERNS)|set(source.FIRST_PROBES),set(range(16)))

    def test_frozen_full_rank_degree2_but_no_source_oracle_input(self):
        rows=[(x,m._predict(0x451,x)) for x in source.TRAIN_PATTERNS]
        self.assertEqual(len({m._monomials(x) for x,y in rows}),12)
        self.assertEqual(m._solve_innovative(rows),0x451)
        self.assertEqual(m._solve_independent(rows),0x451)
        for x in source.FIRST_PROBES:
            self.assertEqual(m._predict(m._solve_innovative(rows),x),
                             m._predict(0x451,x))

    def test_all_protected_and_out_of_range_denied(self):
        for seed in (993500,993531,993600,993663,992500,
                     991500,978500,976500,993116,-1,True,993100.0):
            with self.subTest(seed=seed),self.assertRaises(PermissionError):
                source.PublicRuleSession(seed,0)
        for ctx in (2,-1,True,0.0):
            with self.assertRaises(ValueError):
                source.PublicRuleSession(993100,ctx)
        for x in (-1,16,True,1.0):
            with self.assertRaises(ValueError):
                source.physical_probe(993100,x)

    def test_only_final_selected_action_earns_feedback(self):
        episode=source.PublicRuleSession(993100,1)
        for invalid in (-1,2,True,1.0):
            with self.assertRaises(ValueError):
                episode.apply(invalid)
        rows=[]
        for phase,action in enumerate((1,0,1,0)):
            before=episode.public_state
            row=episode.apply(action)
            self.assertEqual(row.before,before)
            self.assertEqual(row.action,action)
            self.assertEqual(row.before[1],phase)
            self.assertEqual(row.after[1],phase+1)
            self.assertEqual(len(row.history),phase)
            if phase<3:
                self.assertEqual(row.reward,0.0)
                self.assertFalse(row.done)
            else:
                self.assertTrue(row.done)
                self.assertIn(row.reward,(-1.0,1.0))
            rows.append(row)
        self.assertTrue(episode.done)
        with self.assertRaises(ValueError):
            episode.apply(0)
        self.assertEqual(m._actual(tuple(rows))[0],8|1|4)

    def test_pair_of_physical_training_worlds_indistinguishable(self):
        original=[]
        adversarial=[]
        for x in source.TRAIN_PATTERNS:
            a=source.physical_probe(993100,x)
            b=source.physical_probe(993108,x)
            self.assertEqual(a,b)
            original.append(m._actual(a)[:2])
            adversarial.append(m._actual(b)[:2])
        self.assertEqual(original,adversarial)
        self.assertEqual(m._solve_innovative(original),m._solve_independent(adversarial))

    def test_atomic_future_private_bad_schema_and_nonphysical_history(self):
        legit=source.physical_probe(993100,source.TRAIN_PATTERNS[0])
        arm=m.PublicRuleArm("INNOVATION_GF2")
        snapshot=arm.state_receipt()
        bogus=namedtuple("PrivateStep",(*legit[-1]._fields,"oracle_next_reward"))
        cases=[
            (*legit[:3],bogus(*legit[-1],1.0)),
            (*legit[:3],legit[-1]._replace(history=())),
            (*legit[:3],legit[-1]._replace(reward=0.0)),
            (*legit[:3],legit[-1]._replace(done=False)),
            (*legit[:3],legit[-1]._replace(after=(16,)*8))
        ]
        for rows in cases:
            with self.assertRaises(ValueError):
                arm.observe_train(tuple(rows),event_id=0)
            self.assertEqual(arm.state_receipt(),snapshot)
        arm.observe_train(legit,event_id=0)
        with self.assertRaises(ValueError):
            arm.observe_train(legit,event_id=0)

    def test_source_independent_model_cannot_import_private_world(self):
        body=Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("from temporal_trace import",body)
        self.assertNotIn("import public_rule_source",body)
        self.assertNotIn("def _private_reward",body)
        self.assertNotIn("993500",body)
        self.assertNotIn("allow_dev=True",body)

    def test_concrete_train_only_candidate_and_independent_fit(self):
        first=source.TRAIN[0]
        a=m.PublicRuleArm("INNOVATION_GF2")
        b=m.PublicRuleArm("INDEPENDENT_GF2_ELIMINATION")
        lookup=m.PublicRuleArm("EXACT_PUBLIC_LOOKUP_ABSTAIN")
        for i,x in enumerate(source.TRAIN_PATTERNS):
            actual=source.physical_probe(first,x)
            for arm in (a,b,lookup):
                arm.observe_train(actual,event_id=i)
        for arm in (a,b,lookup):
            arm.freeze()
        self.assertEqual(a.observations,12)
        self.assertEqual(a._fit,b._fit)
        self.assertEqual(a._fit,source.MASKS[0])
        self.assertEqual(lookup.predict_first(source.FIRST_PROBES[0]),None)
        for x in source.FIRST_PROBES:
            self.assertEqual(a.predict_first(x),b.predict_first(x))
        self.assertLess(a.logical_learned_bytes,65536)

    def test_no_preoutcome_score_and_atomic_ordered_microfeedback(self):
        arm=m.PublicRuleArm("INNOVATION_GF2")
        with self.assertRaises(ValueError):
            arm.predict_first(0)
        with self.assertRaises(ValueError):
            arm.freeze()
        for i,x in enumerate(source.TRAIN_PATTERNS):
            arm.observe_train(source.physical_probe(993100,x),event_id=i)
        arm.freeze()
        before=arm.state_receipt()
        x=source.FIRST_PROBES[0]
        pre=arm.predict_first(x)
        self.assertIn(pre,(0,1))
        witnessed=source.physical_probe(993100,x)
        with self.assertRaises(ValueError):
            arm.record_actual_feedback(witnessed,index=1)
        self.assertEqual(arm.state_receipt(),before)
        arm.record_actual_feedback(witnessed,index=0)
        actual=1 if witnessed[-1].reward==1.0 else 0
        self.assertEqual(arm.recall(x),actual)
        with self.assertRaises(ValueError):
            arm.predict_first(x)
        with self.assertRaises(ValueError):
            arm.record_actual_feedback(witnessed,index=0)
        fresh=m.PublicRuleArm.restore(arm.checkpoint())
        self.assertEqual(fresh.checkpoint(),arm.checkpoint())
        self.assertEqual(fresh.recall(x),actual)

    def test_no_update_cannot_memorize_and_lookup_can_after_feedback(self):
        arms=[m.PublicRuleArm("NO_UPDATE"),
              m.PublicRuleArm("EXACT_PUBLIC_LOOKUP_ABSTAIN")]
        for i,x in enumerate(source.TRAIN_PATTERNS):
            row=source.physical_probe(993100,x)
            for arm in arms:arm.observe_train(row,event_id=i)
        for arm in arms:arm.freeze()
        first=source.FIRST_PROBES[0]
        self.assertEqual(arms[0].predict_first(first),0)
        self.assertIsNone(arms[1].predict_first(first))
        row=source.physical_probe(993100,first)
        for arm in arms:arm.record_actual_feedback(row,index=0)
        self.assertIsNone(arms[0].recall(first))
        self.assertEqual(arms[1].recall(first),1 if row[-1].reward==1.0 else 0)

    def test_corrupt_snapshot_and_noncanonical_state_rejected(self):
        arm=m.PublicRuleArm("INNOVATION_GF2")
        for i,x in enumerate(source.TRAIN_PATTERNS):
            arm.observe_train(source.physical_probe(993100,x),event_id=i)
        arm.freeze()
        raw=arm.checkpoint()
        self.assertEqual(m.PublicRuleArm.restore(raw).state_receipt(),arm.state_receipt())
        for bad in (b"\x80\x04pickle",b"not json",b"{" + b"x"*65536 + b"}"):
            with self.assertRaises(ValueError):
                m.PublicRuleArm.restore(bad)
        payload=json.loads(raw)
        payload["body"]["fit"]=0
        with self.assertRaises(ValueError):
            m.PublicRuleArm.restore(json.dumps(payload).encode("ascii"))
        payload=json.loads(raw)
        payload["body"]["observed"][0][1]^=1
        payload["sha256"]=__import__("hashlib").sha256(
            m._encode(payload["body"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"FIT_MISMATCH|OUTSIDE_FROZEN"):
            m.PublicRuleArm.restore(m._encode(payload))

    def test_source_safe_no_protected_actions_when_building_direct_toy(self):
        from run_public_feedback import _paired_bootstrap
        with self.assertRaisesRegex(ValueError,"SEED_SCHEDULE_DRIFT"):
            _paired_bootstrap({})
        self.assertEqual(len(m.MODES),5)
        self.assertEqual(m.TRAIN_COUNT,12)
        self.assertEqual(m.FIRST_COUNT,4)


if __name__=="__main__":
    unittest.main()
