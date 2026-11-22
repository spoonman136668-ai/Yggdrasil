import json
from pathlib import Path
import subprocess
import sys
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_stochastic_history import NativeStochasticHistory,SOURCE_PIN

ROOT=Path(__file__).resolve().parents[1]


def fixture():return (ROOT/'research/contrib/chatgpt/NKR-20/source_fixture.json').read_bytes()


class StochasticHistoryTests(unittest.TestCase):
    def test_existing_backoff_formula_matches_exact_raw_tables_without_mutation(self):
        from fractions import Fraction
        raw=fixture();m=NativeStochasticHistory().stage_prefix(raw,SOURCE_PIN,23);before=m.checkpoint()
        data=json.loads(raw);table={}
        for world,e in enumerate(data['episodes']):
            rows=bytes.fromhex(e['rows_hex'])
            for i in range(1,24):
                v=rows[i];key=(world,v>>5,(v>>4)&1,(rows[i-1]>>3)&1)
                for t,y in enumerate(((v>>3)&1,(v>>2)&1)):table.setdefault((key,t),[]).append(y)
        for w in range(4):
            for c in range(2):
                for a in range(2):
                    for prev in range(2):
                        expected=[]
                        for t in range(2):
                            child=table.get(((w,c,a,prev),t),[])
                            pooled=table.get(((w,c,a,0),t),[])+table.get(((w,c,a,1),t),[])
                            parent=Fraction(sum(pooled)+1,len(pooled)+2)
                            p=(sum(child)+4*parent)/(len(child)+4)
                            expected.append((p.numerator,p.denominator))
                        self.assertEqual(m.predict_backoff(w,c,a,prev),tuple(expected))
        self.assertEqual(m.checkpoint(),before)

    def test_cumulative_source_counts_match_qualified_parent_and_are_replay_safe(self):
        raw=fixture();m=NativeStochasticHistory()
        for stop in (8,16,23):
            m=m.stage_prefix(raw,SOURCE_PIN,stop);snapshot=m.checkpoint()
            self.assertIs(m.stage_prefix(raw,SOURCE_PIN,stop),m)
            self.assertEqual(m.info()['training_events'],4*stop)
            self.assertEqual(NativeStochasticHistory.restore(snapshot,digest(snapshot)).checkpoint(),snapshot)
        self.assertEqual(digest(m.counters()),'5f35402435acccc835644d717c0107ede73354f9f2ff6c6bdbf4fe03abd2f4a7')
        self.assertGreater(m.info()['counter_keys_with_both_outcomes'],0)
        with self.assertRaises(ValueError):m.stage_prefix(raw,SOURCE_PIN,16)

    def test_predictions_equal_independent_exact_beta_fit_for_every_key(self):
        raw=fixture();data=json.loads(raw);m=NativeStochasticHistory().stage_prefix(raw,SOURCE_PIN,23)
        counts={}
        for world,e in enumerate(data['episodes']):
            events=bytes.fromhex(e['rows_hex'])
            for i in range(1,24):
                v=events[i];key=(world,v>>5,(v>>4)&1,(events[i-1]>>3)&1)
                for t,y in enumerate(((v>>3)&1,(v>>2)&1)):
                    a=counts.setdefault((key,t),[0,0]);a[y]+=1
        for w in range(4):
            for c in range(2):
                for a in range(2):
                    for prev in range(2):
                        expected=tuple((counts.get(((w,c,a,prev),t),[0,0])[1]+1,
                                        sum(counts.get(((w,c,a,prev),t),[0,0]))+2) for t in range(2))
                        self.assertEqual(m.predict(w,c,a,prev),expected)

    def test_cold_readout_requires_no_solver_or_original_cache(self):
        m=NativeStochasticHistory().stage_prefix(fixture(),SOURCE_PIN,16);raw=m.checkpoint()
        script='''import sys,json
sys.modules['scipy']=None
from yggdrasil.native_stochastic_history import NativeStochasticHistory
from yggdrasil.native_context_basis import digest
raw=json.load(sys.stdin).encode('ascii');m=NativeStochasticHistory.restore(raw,digest(raw))
print(json.dumps(m.predict(0,0,0,0)))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=json.dumps(raw.decode('ascii')),
                         text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(p.stdout),[list(p) for p in m.predict(0,0,0,0)])

    def test_bad_source_wrong_prefix_and_invalid_public_features_rejected(self):
        m=NativeStochasticHistory();raw=fixture()
        for data,pin,stop in ((raw+b'\n',SOURCE_PIN,8),(raw,'0'*64,8),(raw,SOURCE_PIN,24),(raw,SOURCE_PIN,True)):
            with self.assertRaises(ValueError):m.stage_prefix(data,pin,stop)
        for args in ((4,0,0,0),(True,0,0,0),(0,True,0,0),(0,0,2,0),(0,0,0,True)):
            with self.assertRaises(ValueError):m.predict(*args)

    def test_prefix_and_bank_tamper_are_detected_with_recomputed_outer_pin(self):
        m=NativeStochasticHistory().stage_prefix(fixture(),SOURCE_PIN,8);raw=m.checkpoint()
        for field,value in (('accepted_native',True),('scientific_pass',True),('source_cache_sha256','0'*64),
            ('rows_hex',['00'*8]*4),('native_counters_hex','00'*328)):
            d=json.loads(raw);d[field]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativeStochasticHistory.restore(bad,digest(bad))


if __name__=='__main__':unittest.main()
