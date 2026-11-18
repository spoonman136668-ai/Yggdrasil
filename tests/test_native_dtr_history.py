import json
from pathlib import Path
import subprocess
import sys
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_dtr_history import NativeDTRHistory,SOURCE_PIN


def fixture():return (Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/CKAD-16/source_public_fit.json').read_bytes()


class DTRHistoryTests(unittest.TestCase):
    def test_cumulative_prefixes_are_idempotent_and_all_forecasts_match_exact_beta(self):
        raw=fixture();data=json.loads(raw);m=NativeDTRHistory()
        for stop in (64,128,192):
            m=m.stage_prefix(raw,SOURCE_PIN,stop);snap=m.checkpoint()
            self.assertIs(m.stage_prefix(raw,SOURCE_PIN,stop),m)
            self.assertEqual(NativeDTRHistory.restore(snap,digest(snap)).checkpoint(),snap)
            trans={};terminal={}
            for part in data['replicas']:
                for r in part['fit'][:stop]:
                    trans.setdefault((r['s1'],r['x1']),[]).append(r['s2'])
                    terminal.setdefault((r['s1'],r['x1'],r['s2'],r['x2']),[]).append(r['y'])
            for key,ys in trans.items():self.assertEqual(m.transition(*key),(sum(ys)+1,len(ys)+2))
            for key,ys in terminal.items():self.assertEqual(m.terminal(*key),(sum(ys)+1,len(ys)+2))
            self.assertEqual(m.info()['training_episodes'],3*stop)
        self.assertEqual(m.info()['outcome_updates'],1152)
        with self.assertRaises(ValueError):m.stage_prefix(raw,SOURCE_PIN,128)

    def test_two_stage_readout_is_available_without_source_cache_or_solver(self):
        m=NativeDTRHistory().stage_prefix(fixture(),SOURCE_PIN,64);raw=m.checkpoint()
        script='''import sys,json
sys.modules['scipy']=None
from yggdrasil.native_dtr_history import NativeDTRHistory
from yggdrasil.native_context_basis import digest
raw=json.load(sys.stdin).encode('ascii');m=NativeDTRHistory.restore(raw,digest(raw))
print(json.dumps([m.transition(0,0),m.terminal(0,0,0,0)]))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=json.dumps(raw.decode('ascii')),text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(p.stdout),[list(m.transition(0,0)),list(m.terminal(0,0,0,0))])

    def test_wrong_source_unknown_types_and_held_prefix_admission_denied(self):
        raw=fixture();m=NativeDTRHistory()
        for data,pin,stop in ((raw+b'\n',SOURCE_PIN,64),(raw,'0'*64,64),(raw,SOURCE_PIN,256),(raw,SOURCE_PIN,True)):
            with self.assertRaises(ValueError):m.stage_prefix(data,pin,stop)
        for args in ((True,0),(0,2)):
            with self.assertRaises(ValueError):m.transition(*args)
        for args in ((0,0,True,0),(0,0,0,2)):
            with self.assertRaises(ValueError):m.terminal(*args)

    def test_forged_prefix_counters_or_science_flags_rejected(self):
        m=NativeDTRHistory().stage_prefix(fixture(),SOURCE_PIN,64);raw=m.checkpoint()
        for key,value in (('rows_hex',['00'*64]*3),('native_counters_hex','00'*164),('accepted_native',True),('scientific_pass',True)):
            d=json.loads(raw);d[key]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativeDTRHistory.restore(bad,digest(bad))


if __name__=='__main__':unittest.main()
