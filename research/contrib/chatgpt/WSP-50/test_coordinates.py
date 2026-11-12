import hashlib,unittest
from pathlib import Path
from coordinates import CycleModel,inverse_numeric
from domains import LatentWorld,Encoding,EncodedSource
class Tests(unittest.TestCase):
    def test_inverse(self):
        for n in (16,64,256):
            for x in range(1,n,2):self.assertEqual(inverse_numeric(x,n),pow(x,-1,n))
    def test_numeric_address_write(self):
        m=CycleModel(4);m.record_cycle(7,3);self.assertEqual(m.coord(7),3);self.assertEqual(m.decode(3),7);self.assertEqual(m.coords[6],0)
    def test_cycle_certification(self):
        m=CycleModel(4)
        for x in range(16):m.record_cycle(x,x)
        m.certify(0);self.assertEqual(m.valid,1);m.certify(1);self.assertEqual(m.valid,0)
    def test_bad_spine(self):
        m=CycleModel(4)
        for i in range(16):m.record_cycle(0,i)
        m.certify(0);self.assertEqual(m.valid,0);self.assertIsNone(m.apply(1,3))
    def test_affine_encoded(self):
        for k in ('identity','linear_bijection','random_permutation'):
            w=LatentWorld(4,'affine','unit');e=Encoding(4,k,'unit');s=EncodedSource(w,e);m=CycleModel(4);x=0
            for i in range(16):m.record_cycle(x,i);y=s.apply(0,x);m.observe(0,x,y);x=y
            m.certify(x);y=s.apply(1,x);m.observe(1,x,y);m.fit_first(y);x=y
            if not m.coord(x)&1:y=s.apply(0,x);m.observe(0,x,y);x=y
            y=s.apply(1,x);m.observe(1,x,y);m.fit_second(x,y)
            for a in range(2):
                for x in range(16):self.assertEqual(m.apply(a,x),s.apply(a,x))
    def test_reject_and_retain(self):
        m=CycleModel(4)
        for x in range(16):m.record_cycle(x,x)
        m.certify(0);m.fit_first(1);m.fit_second(1,2);m.observe(1,3,9)
        self.assertEqual(m.rejected,1);self.assertEqual(m.apply(1,3),9);self.assertIsNone(m.apply(1,4))
    def test_cold_and_tamper(self):
        m=CycleModel(4);m.observe(1,5,3);s=m.snapshot();r=CycleModel.restore(s);self.assertEqual(r.snapshot(),s);self.assertEqual(r.apply(1,5),3)
        with self.assertRaises(ValueError):CycleModel.restore(s+b'x')
    def test_frozen_raw(self):self.assertEqual(hashlib.sha256(Path(__file__).with_name('raw_equations.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'bf04ed6499b35880bd7f38fccd55c0bd28999d9060c96b3217f825e10f402810')
if __name__=='__main__':unittest.main()
