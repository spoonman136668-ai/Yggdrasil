"""CB2 public-only multi-relation interference gate; no protected first-use."""
import ast
from collections import namedtuple
from pathlib import Path
import unittest

import binding
from context_bank import GatedRelationBank, ConventionalFourSlotBank
from study import tape, queries, study


class MultiRelationTests(unittest.TestCase):
    def _train(self):
        native, control = GatedRelationBank(), ConventionalFourSlotBank()
        rows = tape(82210)
        for row in rows:
            native.observe_public(row)
            control.observe_public(row)
        return native.seal(), control.seal()

    def test_common_interleaved_timeline_and_correct_two_step_mode(self):
        rows=tape(82210)
        self.assertEqual(len(rows),515)
        counts=[0]*4
        mismatch_current=0
        for i, row in enumerate(rows):
            credit, _=binding._credit_public(row)
            if i<3:
                self.assertIsNone(credit)
                continue
            bits, label=credit
            credited_mode=(bits>>28)&3
            counts[credited_mode]+=1
            self.assertEqual(credited_mode,(i-2)%4)
            mismatch_current+=(credited_mode!=(row.before[7]&3))
            self.assertEqual(row.history[-1].after,row.before)
            self.assertEqual(label, (row.history[-2].action if row.reward==1 else 1-row.history[-2].action))
        self.assertEqual(counts,[128]*4)
        self.assertEqual(mismatch_current,512)

    def test_four_relations_new_contexts_and_independent_control(self):
        native,control=self._train()
        self.assertEqual(native.credits,512)
        self.assertEqual(native.versions,(1,1,1,1))
        self.assertEqual(native.logical_persisted_relation_bytes,300)
        for mode,state,history,target in queries(82220):
            self.assertEqual(native.choose_public(state,history),target)
            self.assertEqual(control.choose_public(state,history),target)

    def test_contradiction_trigger_and_atomic_change_only_one_scope(self):
        native, control=self._train()
        initial=native.slot_receipts()
        mismatch=0
        shadow_start=None
        for i,row in enumerate(tape(82211,revised=True,n=600)):
            credit,_=binding._credit_public(row)
            native.observe_public(row)
            control.observe_public(row)
            if credit and ((credit[0]>>28)&3)==1 and 1 not in native.repairs:
                mismatch+=1
                if 1 in native._shadows and shadow_start is None:
                    shadow_start=mismatch
                self.assertEqual(initial,native.slot_receipts())
        self.assertEqual(shadow_start,8)
        self.assertEqual(native.repairs,(1,))
        self.assertEqual(control.repairs,(1,))
        self.assertEqual(native.versions,(1,2,1,1))
        after=native.slot_receipts()
        self.assertEqual(tuple(after[i] for i in (0,2,3)),tuple(initial[i] for i in (0,2,3)))
        self.assertNotEqual(after[1],initial[1])
        for mode,state,history,target in queries(82221):
            self.assertEqual(native.choose_public(state,history),target)
            self.assertEqual(control.choose_public(state,history),target)

    def test_strict_public_only_schema_and_atomic_invalid_step(self):
        native=GatedRelationBank()
        good=tape(82210)[7]
        Extra=namedtuple('Extra',binding.FIELDS+('future_oracle',))
        before=(native.credits,tuple(x._credited for x in native._models))
        for invalid in (Extra(*good,123),good._replace(action=True),
                        good._replace(reward=float('nan')),
                        good._replace(before=(0,)*7),
                        good._replace(history=good.history+(good.history[-1],))):
            with self.assertRaises(ValueError):
                native.observe_public(invalid)
            self.assertEqual(before,(native.credits,tuple(x._credited for x in native._models)))

    def test_cold_checkpoint_exact_and_tamper_fail_closed(self):
        native,_=self._train()
        raw=native.snapshot()
        self.assertEqual(len(raw),774)
        clone=GatedRelationBank.restore(raw)
        self.assertEqual(clone.snapshot(),raw)
        for mode,state,history,_ in queries(82220):
            self.assertEqual(native.choose_public(state,history),clone.choose_public(state,history))
        damaged=bytearray(raw); damaged[18]^=1
        for invalid in (bytes(damaged),b'',raw+b' '):
            with self.assertRaises(ValueError): GatedRelationBank.restore(invalid)

    def test_no_snapshot_mid_repair_and_unchanged_other_slots(self):
        native,_=self._train()
        originals=native.slot_receipts()
        started=False
        for row in tape(82211,revised=True,n=600):
            native.observe_public(row)
            if 1 in native._shadows:
                started=True
                break
        self.assertTrue(started)
        self.assertEqual(originals,native.slot_receipts())
        with self.assertRaises(ValueError): native.snapshot()

    def test_reference_source_independent_no_private_generator_import(self):
        source=Path(__file__).with_name('context_bank.py').read_text('utf-8')
        tree=ast.parse(source)
        modules=set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): modules.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom): modules.add(node.module)
        self.assertNotIn('study',modules)
        self.assertNotIn('FAMILIES',source)
        self.assertNotIn('truth(',source)

    def test_initial_and_repair_scoring_with_frozen_negatives(self):
        metrics=study()
        self.assertEqual(metrics['initial_scores']['candidate'],[128]*4)
        self.assertEqual(metrics['initial_scores']['conventional'],[128]*4)
        self.assertEqual(metrics['revised_scores']['candidate'],[128]*4)
        self.assertEqual(metrics['revised_scores']['conventional'],[128]*4)
        self.assertEqual(metrics['revised_scores']['no_revision'],[128,0,128,128])
        self.assertLessEqual(sum(metrics['wrong_current_mode_score']),int(.75*512))
        self.assertEqual(metrics['repairs'] if 'repairs' in metrics else metrics['earned_repairs'],(1,))
        self.assertTrue(metrics['unchanged_slot_bit_exact'])
        self.assertTrue(metrics['cold_snapshot_exact'])
        self.assertFalse(metrics['scientific_pass'])


if __name__=='__main__': unittest.main()
