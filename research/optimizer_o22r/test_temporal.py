"""O22-R source-only chronological memory and equal input certification."""
import hashlib
import json
import subprocess
import sys
import unittest
from research.optimizer_o22r.temporal_baseline import TemporalBeta
from research.optimizer_o22p.effect_models import NativePlasticCells


def b(front=0):
    return [2,3,1,6,6,front]


def after(before,action,front=0,moved=False):
    x=list(before)
    x[5]=front
    if moved:
        x[0]+=1
    if action==0:x[2]=(x[2]-1)%4
    if action==1:x[2]=(x[2]+1)%4
    return x


class TemporalAdmission(unittest.TestCase):
    def test_original_public_source_only_features(self):
        model=TemporalBeta()
        for a in (0,1,2):
            model.learn(b(),a,after(b(),a,int(a==1),a==2),a)
        self.assertEqual(model.events,3)
        self.assertEqual(model.actions,{"0":1,"1":1,"2":1})
        with self.assertRaises(ValueError):
            model.learn(b(),5,after(b(),1),1)
        with self.assertRaises(ValueError):
            model.learn(b()+[99],0,after(b(),0),1)

    def test_fast_temporal_memory_revises_after_real_shaped_contradiction(self):
        recent=TemporalBeta("discounted")
        persistent=TemporalBeta("cumulative")
        for i in range(14):
            event=after(b(),0,1,False)
            recent.learn(b(),0,event,i)
            persistent.learn(b(),0,event,i)
        for i in range(14,24):
            event=after(b(),0,0,False)
            recent.learn(b(),0,event,i)
            persistent.learn(b(),0,event,i)
        self.assertLess(recent.predict(b(),0,30)[0],
                        persistent.predict(b(),0,30)[0])
        self.assertEqual(recent.actions,persistent.actions)

    def test_observed_front_and_time_phase_separation(self):
        original=TemporalBeta("cumulative")
        phase=TemporalBeta("phase_only")
        for i in range(4):
            original.learn(b(1),1,after(b(1),1,1,False),i)
            phase.learn(b(1),1,after(b(1),1,1,False),i)
        self.assertNotEqual(original.predict(b(1),1,1),
                            original.predict(b(0),1,1))
        self.assertEqual(phase.predict(b(1),1,1),phase.predict(b(0),1,1))
        self.assertNotEqual(phase.predict(b(1),1,1),
                            phase.predict(b(1),1,40))

    def test_chronology_matters_without_claiming_source_intervention(self):
        events=[1]*9+[0]*9
        fwd=TemporalBeta("discounted")
        rev=TemporalBeta("discounted")
        for i,v in enumerate(events):
            fwd.learn(b(),2,after(b(),2,v,False),i)
        for i,v in enumerate(reversed(events)):
            rev.learn(b(),2,after(b(),2,v,False),i)
        self.assertLess(fwd.predict(b(),2,20)[0],rev.predict(b(),2,20)[0])
        self.assertEqual(fwd.events,rev.events)

    def test_fast_slow_native_allows_history_specific_ablation(self):
        m=NativePlasticCells()
        for i in range(7):
            m.learn(b(),0,after(b(),0,1,False))
        learned=m.predict(b(),0)
        m.fast={head:{} for head in m.fast}
        self.assertNotEqual(learned,m.predict(b(),0))
        self.assertEqual(m.events,7)

    def test_exact_fresh_python_cold_full_memory_and_tamper(self):
        for mode in ("discounted","cumulative","phase_only"):
            model=TemporalBeta(mode)
            for i,a in enumerate((0,1,2,0,1,2)):
                model.learn(b(i%2),a,after(b(i%2),a,i%2,False),i)
            cp=model.checkpoint()
            self.assertEqual(TemporalBeta.restore(cp).checkpoint(),cp)
            code=(
                "import json,sys;"
                "from research.optimizer_o22r.temporal_baseline import TemporalBeta;"
                "m=TemporalBeta.restore(sys.stdin.buffer.read());"
                "print(json.dumps({'mode':m.mode,'events':m.events,"
                "'prediction':m.predict([2,3,1,6,6,0],1,10)}))"
            )
            r=subprocess.run([sys.executable,"-B","-c",code],
                             input=cp,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stderr.decode())
            self.assertEqual(json.loads(r.stdout),{
                "mode":mode,"events":6,
                "prediction":list(model.predict(b(),1,10))})
            bad=json.loads(cp)
            bad["body"]["events"]+=1
            with self.assertRaises(ValueError):
                TemporalBeta.restore(json.dumps(bad).encode())

if __name__=="__main__":
    unittest.main(verbosity=2)
