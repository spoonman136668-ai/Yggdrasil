"""Source-free tests. Must pass before any frozen DEV cohorts are consumed."""
import unittest
import sys, math, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import BooleanPosterior, NativeResearchArm, MASKS, COMPLEXITY, value
from world import OLD_NAMES,NEW_NAMES,source_inputs,world_step,FAMILIES,IDs,event_id

class Contracts(unittest.TestCase):
    def test_fixed_grammar(self):
        self.assertEqual(len(MASKS),256)
        self.assertEqual(len(set(MASKS)),256)
        self.assertEqual(set(COMPLEXITY.values()),set(range(5)))
    def test_new_factor_ids_disjoint(self):
        self.assertFalse(set(OLD_NAMES)&set(NEW_NAMES))
        self.assertEqual(len(FAMILIES),8)
    def test_private_truth_is_not_in_core(self):
        text=Path(__file__).with_name('core.py').read_text()
        self.assertNotIn('world import',text)
        self.assertNotIn('private_law',text)
    def test_source_is_deterministic_and_has_real_actions(self):
        v=source_inputs(123,'disjoint_xor','held_new',4)
        a=world_step(123,'disjoint_xor','held_new',4,*v,1)
        b=world_step(123,'disjoint_xor','held_new',4,*v,1)
        self.assertEqual(a,b)
        self.assertIn(a,(0,1))
    def test_read_only_conventional_forecasts(self):
        for kind in ('FULL','SUBSET','RECURRENT'):
            m=NativeResearchArm(kind)
            m.update(OLD_NAMES,'t',(0,0,0),0,0,event_id(1,'unchanged_a','old_fit',0,'t'))
            old=m.old_digest(OLD_NAMES)
            for v in ((1,1,1),(0,1,1),(1,0,0)):
                m.predict(OLD_NAMES,'t',v,1)
            self.assertEqual(m.old_digest(OLD_NAMES),old,kind)

    def test_unknown_before_witnesses(self):
        model=BooleanPosterior('MAP')
        self.assertFalse(model.confidence()['identified'])
    def test_replay_refusal(self):
        model=NativeResearchArm('MAP')
        i=event_id(1,'disjoint_xor','new_fit',0,'t')
        model.update(NEW_NAMES,'t',(0,1,0),0,1,i)
        with self.assertRaises(AssertionError):model.update(NEW_NAMES,'t',(0,1,0),0,1,i)
    def test_byte_exact_checkpoint_and_tamper(self):
        model=NativeResearchArm('BMA')
        i=event_id(1,'disjoint_xor','new_fit',0,'t')
        model.update(NEW_NAMES,'t',(0,1,0),0,1,i)
        snapshot=model.checkpoint()
        restored=NativeResearchArm.restore(snapshot['raw'],snapshot['sha256'])
        self.assertEqual(restored.checkpoint()['raw'],snapshot['raw'])
        with self.assertRaises(ValueError):NativeResearchArm.restore(snapshot['raw']+b'x',snapshot['sha256'])
    def test_old_new_source_memory_isolation(self):
        model=NativeResearchArm('MAP')
        model.update(OLD_NAMES,'t',(0,1,0),0,1,event_id(1,'disjoint_xor','old_fit',0,'t'))
        old=model.old_digest(OLD_NAMES)
        model.update(NEW_NAMES,'t',(0,1,1),1,0,event_id(1,'disjoint_xor','new_fit',0,'t'))
        self.assertEqual(old,model.old_digest(OLD_NAMES))
    def test_out_of_class_variable_is_public_but_grammar_ignores_it(self):
        self.assertIn(1,[source_inputs(123,'out_of_grammar','new_fit',i)[2] for i in range(64)])
        self.assertEqual(source_inputs(123,'equiv_unidentified','new_fit',0)[2],0)
        self.assertTrue(all(source_inputs(123,'equiv_unidentified','new_fit',i)[2]==0 for i in range(64)))
    def test_stage_masks_only_use_three_variables(self):
        for mask in MASKS:
            for a in (0,1):
                self.assertIn(value(mask,(1,a,0)),(0,1))
    def test_source_names_absent_private_laws(self):
        from trial import obs
        m=NativeResearchArm('MAP')
        packet=obs(m,1202,'disjoint_xor','old_fit',1,update=False)
        self.assertNotIn('private_law',str(packet))
        self.assertNotIn('truth',str(packet))

if __name__=='__main__':unittest.main()
