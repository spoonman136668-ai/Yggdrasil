"""Fabricated-row unit checks ONLY: no scored WSP149 source event calls."""
from hashlib import sha256
from pathlib import Path
from unittest import TestCase
import exact_weights as W

def fabricated(i):
    xs=tuple(sorted(range(64),key=lambda x:(
        sha256(('WSP149|FAKE-UNIT|'+str(i)+'|'+str(x)).encode()).digest(),x))[:32])
    return tuple((x,((x>>(i%6))&1)^int((x&11)==11)^
            (int((x&15)==15) if i%3==0 else 0)) for x in xs)

class SourceFreeGF2(TestCase):
    def test_01_exact_32_under_48_fabricated_worlds(self):
        self.assertEqual(len(W.FEATURES),64)
        txt=Path(W.__file__).read_text(encoding='utf8')
        for forbidden in ('import source','from source import',
                          'WSP149|SOURCE|','Custodian','_truth(','WSP149|HELD|'):
            self.assertNotIn(forbidden,txt)
        for i in range(48):
            rows=fabricated(i);m=W.fit(rows)
            self.assertEqual(m['rank'],32)
            self.assertEqual(len(set(m['pivot_masks'])),32)
            self.assertTrue(all(W.predict(m,x)==y for x,y in rows))
            self.assertEqual(len(W.predictions(m)),64)
            self.assertEqual(W.predictions(m),W.predictions(W.restore_model(m,rows)))
    def test_02_random_label_interpolation(self):
        xs=tuple(x for x,y in fabricated(37))
        for i in range(8):
            rows=tuple((x,int.from_bytes(sha256(('WSP149|RANDOM-UNIT-LABEL|'+
                str(i)+'|'+str(x)).encode()).digest()[:2],'big')&1) for x in xs)
            model=W.fit(rows)
            self.assertTrue(all(W.predict(model,x)==y for x,y in rows))
    def test_03_train_16_prior_then_frozen_transfer_and_cold(self):
        prior=W.empty_memory();receipts=[]
        for i in range(16):
            old=prior;rows=fabricated(i)
            prior,m=W.remember(prior,rows)
            receipts.append(m['rows_sha256'])
            self.assertEqual(prior['worlds'],i+1)
            self.assertEqual(prior['row_receipts'],tuple(receipts))
            self.assertEqual(W.predictions(m),W.predictions(W.restore_model(m,rows,old)))
        frozen=W.freeze_memory(prior)
        self.assertEqual(W.restore_memory(frozen),frozen)
        rows=fabricated(80)
        a=W.fit(rows,frozen);b=W.fit(rows);c=W.fit(rows,W.mismatched_memory(frozen))
        for m in (a,b,c):
            self.assertTrue(all(W.predict(m,x)==y for x,y in rows))
        self.assertEqual(W.predictions(a),W.predictions(W.restore_model(a,rows,frozen)))
        with self.assertRaises(ValueError):W.remember(frozen,rows)
        with self.assertRaises(ValueError):W.restore_model(a,rows)
    def test_04_negative_invalid_and_duplicate_custody(self):
        r=fabricated(0)
        for bad in (r[:-1],r[:-1]+((r[0][0],1),),
                    r[:-1]+((True,1),),r[:-1]+((63,2),)):
            with self.assertRaises(ValueError):W.fit(bad)
        m=W.empty_memory();n,model=W.remember(m,r)
        with self.assertRaises(ValueError):W.remember(n,r)
        with self.assertRaises(ValueError):W.freeze_memory(n)
        for corrupt in ({**n,'counts':(1,)*64},{**n,'worlds':16},
                        {**n,'digest':'0'*64}):
            with self.assertRaises(ValueError):W.restore_memory(corrupt)
        with self.assertRaises(ValueError):
            W.restore_model({**model,'weights':model['weights']^1},r,m)
        for x in (True,64,-1,'0'):
            with self.assertRaises(ValueError):W.predict(model,x)
    def test_05_generic_prior_changes_order_not_source(self):
        p=W.empty_memory()
        self.assertEqual(W.coefficient_order(p),tuple(sorted(range(64),
            key=lambda m:(m.bit_count(),m))))
        for i in range(16):
            p,m=W.remember(p,fabricated(i))
            self.assertLessEqual(m['active_coefficients'],32)
        p=W.freeze_memory(p)
        self.assertEqual(W.coefficient_order(p),W.coefficient_order(p))
        self.assertNotEqual(W.coefficient_order(p),
                            W.coefficient_order(W.mismatched_memory(p)))
