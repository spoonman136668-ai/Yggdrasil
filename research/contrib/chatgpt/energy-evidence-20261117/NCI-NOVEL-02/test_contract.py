"""Source-free engineering checks only; no prospective scientific seeds."""
import unittest
import hashlib
import json
from core import ResearchArm,TEMPLATES,functions,digest
from world import OLD_IDS,NEW_IDS,inputs,truth,consequence,identity,SEEDS,PILOT_SEED

class Contract(unittest.TestCase):
    def test_grammar_nonempty_and_repeatable(self):
        self.assertEqual(functions(5),TEMPLATES[5]);self.assertEqual(functions(6),TEMPLATES[6])
        self.assertGreater(len(TEMPLATES[5]),50)
    def test_no_private_law_import(self):
        import core
        from pathlib import Path
        self.assertNotIn('from world import',Path(core.__file__).read_text(encoding='utf-8'))
    def test_input_role_is_disjoint(self):
        self.assertFalse(set(OLD_IDS)&set(NEW_IDS))
        self.assertEqual(len(OLD_IDS),len(NEW_IDS))
    def test_outcome_is_binary(self):
        for i in range(16):
            x=inputs(PILOT_SEED,'novel_guard','new_fit',i)
            y=consequence(PILOT_SEED,'novel_guard','new_fit',i,'t',x,i%2)
            self.assertIn(y,(0,1))
    def test_fourth_variable_real_in_new_laws(self):
        for name in ('novel_toggle','novel_guard','novel_cross','novel_parity4'):
            effects=[]
            for first in (0,1):
                for second in (0,1):
                    for a in (0,1):
                        x=(first,second,0,0)
                        u=truth(name,'new_fit',x,a)
                        v=truth(name,'new_fit',(*x[:3],1),a)
                        effects.append(u!=v)
            self.assertTrue(any(effects),name)
    def test_relevance_hidden_from_model(self):
        arm=ResearchArm('GATED_MAP')
        self.assertFalse(arm.component(NEW_IDS,'t').evidence()['identified'])
    def test_new_update_preserves_old(self):
        a=ResearchArm('GATED_MAP')
        w=lambda x: hashlib.sha256(x.encode('ascii')).hexdigest()
        a.admit(OLD_IDS,'t',(0,0,0,0,1),1,w('old'))
        initial=a.old_digest(OLD_IDS)
        a.admit(NEW_IDS,'t',(0,0,0,1,0),1,w('new'))
        self.assertEqual(initial,a.old_digest(OLD_IDS))
    def test_replay_is_idempotent_but_rebind_rejected(self):
        a=ResearchArm('BMA');id=hashlib.sha256(b'id').hexdigest();f=(0,1,1,0,0)
        self.assertEqual(a.admit(NEW_IDS,'t',f,1,id),'ADMITTED')
        before=a.checkpoint()
        self.assertEqual(a.admit(NEW_IDS,'t',f,1,id),'DUPLICATE')
        self.assertEqual(before,a.checkpoint())
        with self.assertRaisesRegex(ValueError,'WITNESS_REBOUND'):
            a.admit(NEW_IDS,'t',f,0,id)
        self.assertEqual(before,a.checkpoint())
    def test_cold_restores_exact(self):
        a=ResearchArm('GATED_MAP');f=(0,1,0,1,1)
        a.admit(NEW_IDS,'t',f,1,hashlib.sha256(b'w').hexdigest())
        raw=a.checkpoint();z=ResearchArm.restore(raw,digest(raw))
        self.assertEqual(raw,z.checkpoint())
        self.assertEqual(a.predict(NEW_IDS,'t',f),z.predict(NEW_IDS,'t',f))
    def test_restore_tamper_refused(self):
        a=ResearchArm('GATED_MAP');raw=a.checkpoint()
        with self.assertRaisesRegex(ValueError,'CHECKPOINT_SHA_MISMATCH'):
            ResearchArm.restore(raw+b'\n',digest(raw))
    def test_unknown_on_no_evidence(self):
        a=ResearchArm('GATED_MAP')
        self.assertFalse(a.component(NEW_IDS,'y').evidence()['identified'])
    def test_strict_binary(self):
        a=ResearchArm('GATED_MAP')
        with self.assertRaisesRegex(ValueError,'NOT_BINARY_PUBLIC_VALUE'):
            a.predict(NEW_IDS,'t',(0,1,0,2,0))
    def test_no_primary_seeds_in_pilot(self):
        self.assertNotIn(PILOT_SEED,SEEDS)

if __name__=='__main__':unittest.main()
