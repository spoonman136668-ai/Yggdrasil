"""Source-free engineering tests. No primary source seeds used in tests."""
import unittest
import hashlib
from itertools import product
from learner import SparseANF,ResearchArm,grammar,digest
import world
import trial

class Tests(unittest.TestCase):
    def test_public_binary(self):
        from learner import bit
        for x in (None,1.0,2,True,'0'):
            with self.assertRaises(ValueError):bit(x)
    def test_two_grammar_sizes(self):
        self.assertTrue(len(grammar(6))>len(grammar(5))>100)
    def test_search_contains_cubic_operator_without_seeded_correct_labels(self):
        g=grammar(5)
        self.assertTrue(any(set(z[2]) == {(0,1,3),(4,)} for z in g))
    def test_candidate_and_bma_share_template_space(self):
        self.assertEqual(SparseANF('t','MAP').templates,SparseANF('t','BMA').templates)
    def test_nox3_ablates_causal_fourth_coordinate(self):
        self.assertTrue(all(not z[4] for z in SparseANF('y','NOX3').templates))
    def test_no_private_world_import(self):
        import learner
        with open(learner.__file__,encoding='utf8') as f:
            src=f.read()
        self.assertNotIn('import world',src)
    def test_new_source_roles_distinct(self):
        self.assertTrue(set(world.OLD_IDS).isdisjoint(world.NEW_IDS))
    def test_source_timing_first_step_independent_future_action(self):
        x=world.inputs(world.PILOT,'cubic_action','new_fit',5)
        a=world.balanced(world.PILOT,'cubic_action','new_fit',5,'t')
        self.assertEqual(world.reveal(world.PILOT,'cubic_action','new_fit',5,'t',x,a),
                         world.reveal(world.PILOT,'cubic_action','new_fit',5,'t',x,a,0,1))
    def test_held_ids_frozen_separate(self):
        self.assertNotEqual(world.witness(world.PILOT,'cubic_action','new_fit',1,'t'),
                            world.witness(world.PILOT,'cubic_action','held_shared',1,'t'))
    def test_no_out_of_class_syntax(self):
        # Degree-four polynomial term cannot be a degree-3 two-term expression.
        g=grammar(5)
        witness=sum(((i&15)==15)<<i for i in range(32))
        self.assertFalse(any(x[0]==witness for x in g))
    def test_zero_public_fourth_identifiability_requires_contrasts(self):
        m=SparseANF('t','MAP')
        for i in range(128):
            x=(i&1,i>>1&1,i>>2&1,0,i>>3&1)
            m.update(x,0)
        self.assertFalse(m.evidence()['identified'])
    def test_cold_exact_and_tamper(self):
        m=ResearchArm('MAP')
        m.admit(world.OLD_IDS,'t',(0,1,0,1,1),1,'a'*64)
        raw=m.checkpoint()
        self.assertEqual(ResearchArm.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaises(ValueError):ResearchArm.restore(raw[:-1]+b'\x00',digest(raw))
    def test_duplicate_idempotent_conflict_negative(self):
        m=ResearchArm('BMA')
        x=(1,0,1,1,0)
        self.assertTrue(m.admit(world.OLD_IDS,'t',x,1,'b'*64))
        before=m.checkpoint()
        self.assertFalse(m.admit(world.OLD_IDS,'t',x,1,'b'*64))
        self.assertEqual(before,m.checkpoint())
        with self.assertRaises(ValueError):m.admit(world.OLD_IDS,'t',x,0,'b'*64)
    def test_old_bank_preserved_after_new_update(self):
        m=ResearchArm('MAP')
        m.admit(world.OLD_IDS,'t',(0,1,0,0,1),1,'a'*64)
        old=m.old_digest(world.OLD_IDS)
        m.admit(world.NEW_IDS,'t',(1,1,1,1,0),0,'b'*64)
        self.assertEqual(old,m.old_digest(world.OLD_IDS))
    def test_pilot_seed_separate(self):
        self.assertNotIn(world.PILOT,world.SEEDS)
    def test_frozen_action_budget(self):
        self.assertEqual(7*sum(world.COUNTS.values())*2,4928)

if __name__=='__main__':unittest.main()
