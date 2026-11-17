"""WSP143 frozen prospective source-safe engineering controls."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import concepts as H
import flat_control as F
import experiment as E

class HierarchicalConceptResearchTests(TestCase):
    def test_01_private_original_and_unregistered_source_denied(self):
        self.assertEqual((len(S.KNOWN),len(S.UNFAMILIAR),len(S.SWITCH),
                          len(S.CROSS),len(S.OFF),len(S.TRANSFER)),
                         (8,16,16,8,8,4))
        self.assertFalse(S.PROTECTED&S.ALLOWED)
        self.assertNotIn('source',H.__dict__)
        self.assertNotIn('source',F.__dict__)
        with patch.object(S.random,'Random',
                          side_effect=AssertionError('UNAUTHORIZED_RNG_BEFORE_SOURCE_GUARD')):
            for seed in (True,False,'250000',249999,250008,250800,
                         251016,251800,252016,252800,253008,253800,
                         254008,254800,255004,255800,240000,241000,
                         242000,243000,244000,198000,199000,206000,207000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
    def test_02_generated_lattice_and_independent_source_free_unit_controls(self):
        self.assertEqual([len(H.LEVELS[n]) for n in range(6)],[1,6,15,20,15,6])
        self.assertEqual(len(set(m for stage in H.LEVELS.values() for m in stage)),63)
        self.assertEqual(len(E.N.schedule()),32)
        # User-authored public boolean unit fixture; NOT any registered source world
        factors=(0,3,7,31)
        rows=tuple((x,sum(int((x&m)==m) for m in factors)%2)
                   for x in E.N.schedule())
        for max_depth in (2,3,4,5):
            h=H.fit(rows,max_depth=max_depth)
            f=F.symbolic_fit(rows,max_depth=max_depth)
            self.assertEqual((h['level'],h['terms'],h['degree'],h['tied_count'],h['overflow']),
                             (f['level'],f['terms'],f['degree'],f['count'],f['overflow']))
            for x in range(64):
                self.assertEqual(H.predict(h,x),F.symbolic_predict(f,x))
        snapshot=H.canon(H.fit(rows))
        self.assertEqual(H.canon(H.restore(snapshot,rows)),snapshot)
        with self.assertRaises(ValueError):H.fit(rows[:-1])
        with self.assertRaises(ValueError):F.symbolic_fit(rows[:-1])
        with self.assertRaises(ValueError):H.predict(H.fit(rows),64)
        with self.assertRaises(ValueError):F.symbolic_predict(F.symbolic_fit(rows),64)
    def test_03_original_source_safe_frozen_experiment(self):
        x=E.run()
        print('WSP143_RESULT_JSON='+S.canon(x))
        self.assertIn(x['status'],('DEVELOPMENT_HIERARCHICAL_COMPOSITION_SUPPORTED',
                                  'DEVELOPMENT_HIERARCHICAL_COMPOSITION_NO_GO'))
        self.assertFalse(x['scientific_pass'])
        self.assertFalse(x['native_yggdrasil_admission'])
        self.assertFalse(x['new_computational_primitives_invented'])
        self.assertEqual(x['original_first_use_effects'],0)
        self.assertEqual(x['source_safe_public_effects'],1792)
        self.assertEqual(x['cohort_worlds'],
                         {'known':8,'three':16,'five':16,'cross':8,'off':8})
        self.assertEqual(x['cold_relabel_exact_identity'],256)
        self.assertTrue(x['old_known_laws_unchanged'])
        self.assertTrue(x['candidate_and_independent_symbolic_exact_tie'])
        self.assertEqual(len(x['per_world']),56)
        self.assertEqual(x['max_sparse_terms'],4)
        for fam,n in x['cohort_worlds'].items():
            for arm in E.METHODS:
                for set_name,length in (('future',16*n),('all_unseen',32*n)):
                    values=x['scores'][fam][arm][set_name]
                    self.assertEqual(values['held'],length)
                    self.assertEqual(values['correct']+
                                     values['wrong_confident']+
                                     values['abstained'],length)
            self.assertEqual(x['scores'][fam]['hierarchical'],
                             x['scores'][fam]['equal_prior_flat'])
