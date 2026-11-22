"""CPR-02 synthetic negative controls; successful tests are NOT science acceptance."""
import importlib.util
from hashlib import sha256
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt'

def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj
base=module('cpr01_for_cpr02',ROOT/'CPR-01/router.py')
cp=module('cpr02_monitor',ROOT/'CPR-02/monitor.py')
PIN='4'*64
P={'A':900000,'C':900000}

def fresh():
    models=(base.FrozenCalibration.from_holdout(name,name.lower()*64,str(i)*64,[900000]*128,[1]*128,alpha_percent=10)
            for name,i in [('A',1),('C',3)])
    return cp.CausalConfirmationMonitor(base.ConformalRouter(tuple(models),window=8),probe_source_sha256=PIN)

def step(m,primary,probe_y=None,seq=None):
    probe=None if probe_y is None else {'sequence':seq,'source_sha256':PIN,'intervention_id':'do:x','probabilities':P}
    r=m.route(P,'do:x',probe=probe)
    obs=m.observe(primary,probe_label=probe_y)
    return r,obs

class CPR02Tests(unittest.TestCase):
    def test_clean_channel_blocks_clustered_single_channel_alarm(self):
        m=fresh();raw=0;confirmed=0
        for i,y in enumerate([1]*64+[0]*8+[1]*8):
            r,o=step(m,y,1,i+1)
            raw+=int(r['raw_alarm']);confirmed+=int(o['confirmed_change'])
        self.assertEqual(raw,1)  # CPR-01 failed under this corrupted primary stream
        self.assertEqual(confirmed,0)

    def test_sustained_shift_confirmed_within_frozen_16_step_limit(self):
        m=fresh()
        for i in range(16):step(m,1,1,i+1)
        confirmed=[]
        for i in range(1,33):
            r,o=step(m,0,0,16+i)
            if o['confirmed_change']:confirmed.append(i)
        self.assertEqual(len(confirmed),1)
        self.assertLessEqual(confirmed[0],16)

    def test_without_independent_measurements_never_confirm(self):
        m=fresh();alerts=0
        for y in [1]*16+[0]*32:
            r,o=step(m,y); alerts+=int(r['raw_alarm'])
            self.assertFalse(o['confirmed_change'])
        self.assertEqual(alerts,1)

    def test_correlated_noise_defeats_gate_negative_control(self):
        m=fresh();confirmed=0
        for i,y in enumerate([1]*64+[0]*16+[1]*8):
            # Corrupted probe is not independent: both channels flip together.
            r,o=step(m,y,y,i+1)
            confirmed+=int(o['confirmed_change'])
        self.assertEqual(confirmed,1,'correlated contamination must remain an explicit failure case')

    def test_reject_wrong_source_and_replay_without_mutation(self):
        m=fresh();before=m.checkpoint()
        with self.assertRaisesRegex(ValueError,'CUSTODY'):
            m.route(P,'do:x',probe={'sequence':1,'source_sha256':'5'*64,'intervention_id':'do:x','probabilities':P})
        self.assertEqual(m.checkpoint(),before)
        step(m,1,1,1)
        before=m.checkpoint()
        with self.assertRaisesRegex(ValueError,'CUSTODY'):
            m.route(P,'do:x',probe={'sequence':1,'source_sha256':PIN,'intervention_id':'do:x','probabilities':P})
        self.assertEqual(m.checkpoint(),before)

    def test_cold_restore_and_tamper(self):
        m=fresh()
        for i,y in enumerate([1]*16+[0]*13):step(m,y,1 if i<16 else 0,i+1)
        raw=m.checkpoint();pins={c.name:c.model_sha256 for c in m.router.calibrations}
        restored=cp.CausalConfirmationMonitor.restore(raw,sha256(raw).hexdigest(),base_router_cls=base.ConformalRouter,model_pins=pins,probe_source_sha256=PIN)
        self.assertEqual(restored.checkpoint(),raw)
        with self.assertRaisesRegex(ValueError,'PIN'):
            cp.CausalConfirmationMonitor.restore(raw+b'x',sha256(raw).hexdigest(),base_router_cls=base.ConformalRouter,model_pins=pins,probe_source_sha256=PIN)
        with self.assertRaisesRegex(ValueError,'INVALID'):
            cp.CausalConfirmationMonitor.restore(raw,sha256(raw).hexdigest(),base_router_cls=base.ConformalRouter,model_pins=pins,probe_source_sha256='f'*64)

    def test_broken_observation_cannot_advance_base(self):
        m=fresh();step(m,1,1,1)
        m.route(P,'do:x',probe={'sequence':2,'source_sha256':PIN,'intervention_id':'do:x','probabilities':P})
        before=m.router.checkpoint if False else m.router.history['A'].copy()
        with self.assertRaisesRegex(ValueError,'PROBE_PAIR'):
            m.observe(1)
        self.assertEqual(list(m.router.history['A']),list(before))
        m.observe(1,probe_label=1)

if __name__=='__main__':unittest.main()
