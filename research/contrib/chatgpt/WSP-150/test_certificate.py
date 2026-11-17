"""WSP-150: fabricated-only tests; NEVER run WSP-149 protected source."""
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from unittest import TestCase
import certificate as C

ROOT=Path(__file__).resolve().parents[1]
def load_wsp149():
    spec=spec_from_file_location('_wsp150_pin_wsp149',ROOT/'WSP-149'/'exact_weights.py')
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
W=load_wsp149()

FIXED=tuple(sorted(range(64),key=lambda x:(
    sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:32])

def fake_rows(i):
    xs=tuple(sorted(range(64),key=lambda x:(
        sha256(('WSP150|FAKE|'+str(i)+'|'+str(x)).encode()).digest(),x))[:32])
    return tuple((x, ((x>>(i%6))&1)^int((x&7)==7)^
                  int((x&19)==19)) for x in xs)

def fixed_rows(i):
    return tuple((x,((x>>(i%6))&1)^int((x&7)==7)^
                  int((x&43)==43)) for x in FIXED)

class SourceFreeIdentifiability(TestCase):
    def test_01_unseen_ambiguity_across_16_fabricated_worlds(self):
        for i in range(16):
            rows=fake_rows(i);model=W.fit(rows)
            self.assertEqual(model['rank'],32)
            seen={x for x,y in rows}
            self.assertEqual(len(seen),32)
            for x in range(64):
                cert=C.certificate(rows,model['weights'],x)
                self.assertTrue(C.verify_certificate(rows,model['weights'],x,cert))
                if x in seen:
                    self.assertEqual(cert['status'],'OBSERVED')
                else:
                    self.assertEqual(cert['status'],'UNIDENTIFIABLE')
                    self.assertNotEqual(cert['reference_prediction'],cert['witness_prediction'])
                    self.assertEqual(cert['query_rank'],33)
            self.assertEqual(W.predictions(model),tuple(C.predict(model['weights'],x)
                                                      for x in range(64)))

    def test_02_exact_inherited_fixed_schedule_8_worlds(self):
        self.assertEqual(len(FIXED),32)
        for i in range(8):
            rows=fixed_rows(i);weights=W.fit(rows)['weights']
            for x in range(64):
                cert=C.certificate(rows,weights,x)
                self.assertEqual(cert['status'],
                                 'OBSERVED' if x in FIXED else 'UNIDENTIFIABLE')
                if x not in FIXED:
                    self.assertTrue(all(C.predict(cert['witness_weights'],a)==b for a,b in rows))

    def test_03_cold_repeat_exact(self):
        rows=fake_rows(19);weights=W.fit(rows)['weights']
        first=tuple(C.certificate(rows,weights,x) for x in range(64))
        self.assertEqual(first,tuple(C.certificate(rows,weights,x) for x in range(64)))
        self.assertEqual(first,tuple(C.certificate(list(rows),weights,x) for x in range(64)))

    def test_04_invalid_rows_weights_and_context(self):
        rows=fake_rows(3);weights=W.fit(rows)['weights']
        for bad in (rows[:-1],rows[:-1]+(rows[0],),
                    rows[:-1]+((True,0),),
                    rows[:-1]+((rows[-1][0],2),)):
            with self.assertRaises(ValueError):C.certificate(bad,weights,0)
        for badx in (-1,64,True,'1'):
            with self.assertRaises(ValueError):C.certificate(rows,weights,badx)
        for badw in (-1,1<<64,True,'1',weights^1):
            with self.assertRaises(ValueError):C.certificate(rows,badw,0)

    def test_05_corrupt_witness_rejected(self):
        rows=fake_rows(2);weights=W.fit(rows)['weights']
        x=next(x for x in range(64) if x not in {a for a,b in rows})
        cert=C.certificate(rows,weights,x)
        bad=({**cert,'witness_weights':cert['witness_weights']^1},
             {**cert,'witness_delta':0},
             {**cert,'query_rank':32},
             {**cert,'status':'OBSERVED'})
        for item in bad:
            with self.assertRaises(ValueError):
                C.verify_certificate(rows,weights,x,item)
        observed=rows[0][0]
        known=C.certificate(rows,weights,observed)
        with self.assertRaises(ValueError):
            C.verify_certificate(rows,weights,observed,{**known,'status':'UNIDENTIFIABLE'})

    def test_06_source_custody_and_no_native_promotion(self):
        source=(Path(__file__).with_name('certificate.py')).read_text(encoding='utf8')
        for forbidden in ('import source','from source import','WSP149|SOURCE|',
                          'WSP149|HELD|','OwnerPostCommit','Custodian(',
                          'SCIENTIFIC_PASS.json','first_use_authorization.json'):
            self.assertNotIn(forbidden,source)
        self.assertEqual(len(C.MASKS),64)
        self.assertEqual(set(range(64)),set(C.MASKS))
