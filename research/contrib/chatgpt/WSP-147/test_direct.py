"""Pure fabricated mechanical row tests; no WSP147 source or effect calls."""
from hashlib import sha256
from pathlib import Path
from unittest import TestCase
import direct as D
import poly_control as P

def rows():
    order=tuple(sorted(range(64),key=lambda x:
       (sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:32])
    return tuple((x,int((x&3)==3)^((x>>4)&1)) for x in order)

class DirectWeightMechanics(TestCase):
    def test_01_weights_are_64_boolean_bits_no_new_grammar_library(self):
        self.assertEqual(D.MAX_EDITS,16)
        self.assertEqual(len(D.MASKS),64)
        for file in ('direct.py','poly_control.py'):
            data=Path(__file__).with_name(file).read_text(encoding='utf8')
            for forbidden in ('import source','from source import','WSP147|SOURCE|','majority','MAJ5','Custodian','_truth('):
                self.assertNotIn(forbidden,data)
    def test_02_edits_deterministic_bounded_and_loss_improving(self):
        r=rows()
        a=D.program_weights(r);b=D.program_weights(r)
        self.assertEqual(a['weights'],b['weights'])
        self.assertEqual(a['writes'],b['writes'])
        self.assertLessEqual(len(a['writes']),16)
        self.assertEqual(a['residual_errors'],0)
        self.assertTrue(a['has_exact_fit'])
        self.assertEqual(D.predictions(a),D.predictions(D.restore(a,r)))
        self.assertTrue(all(D.predict(a,x)==y for x,y in r))
    def test_03_nonalias_exact_symbolic_rows(self):
        r=rows()
        b=P.fit(r)
        self.assertEqual(b['rank'],32)
        self.assertTrue(all(P.predict(b,x)==y for x,y in r))
        self.assertEqual(P.predictions(b),P.predictions(P.fit(r)))
    def test_04_invalid_rows_and_cold_corruption_refused(self):
        r=rows()
        invalid=(r[:-1],r[:-1]+((r[0][0],0),),r[:-1]+((63,2),),
                 r[:-1]+((True,1),))
        for bad in invalid:
            with self.assertRaises(ValueError):D.program_weights(bad)
            with self.assertRaises(ValueError):P.fit(bad)
        a=D.program_weights(r)
        with self.assertRaises(ValueError):D.restore(dict(a,weights=a['weights']^1),r)
    def test_05_unknown_label_not_guessed_if_not_exact_fit(self):
        r=tuple((x,(x*13+x//3)&1) for x in range(32))
        a=D.program_weights(r)
        if not a['has_exact_fit']:
            self.assertTrue(all(y is None for y in D.predictions(a)))
