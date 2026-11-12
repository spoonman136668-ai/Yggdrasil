import hashlib,itertools,unittest
from pathlib import Path
from domains import LatentWorld,Encoding,EncodedSource
from observer import Observer
from equations import EquationBank

class Tests(unittest.TestCase):
    def test_frozen_kernel(self):self.assertEqual(hashlib.sha256(Path(__file__).with_name('equations.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),'bf04ed6499b35880bd7f38fccd55c0bd28999d9060c96b3217f825e10f402810')
    def test_encodings_bijection(self):
        for w,k in itertools.product((4,6,8),('identity','linear_bijection','random_permutation')):
            e=Encoding(w,k,'unit');self.assertEqual(e.encode(0),0)
            for x in range(1<<w):self.assertEqual(e.decode(e.encode(x)),x)
    def test_linear_encoding(self):
        e=Encoding(6,'linear_bijection','unit')
        for x,y in itertools.product(range(64),repeat=2):self.assertEqual(e.encode(x^y),e.encode(x)^e.encode(y))
    def test_all_domains_range(self):
        for f in ('affine_bits','modular_arithmetic','saturating_counter','coupled_grid','checksum_machine','random_map'):
            w=LatentWorld(4,f,'unit')
            for a,x in itertools.product(range(2),range(16)):self.assertTrue(0<=w.apply(a,x)<16)
    def test_source_conjugacy(self):
        w=LatentWorld(4,'checksum_machine','unit');e=Encoding(4,'random_permutation','unit');s=EncodedSource(w,e)
        for a,x in itertools.product(range(2),range(16)):self.assertEqual(s.apply(a,e.encode(x)),e.encode(w.apply(a,x)))
    def test_latent_policy_equivalence(self):
        w=LatentWorld(4,'coupled_grid','unit');encs=[Encoding(4,k,'unit') for k in ('identity','linear_bijection','random_permutation')];agents=[Observer(4) for _ in encs]
        for _ in range(200):
            rows=[]
            for agent,e in zip(agents,encs):
                a,x,y=agent.transition(EncodedSource(w,e).apply);rows.append((a,e.decode(x),e.decode(y)))
            self.assertEqual(rows,[rows[0]]*3)
        for agent in agents:
            self.assertEqual(agent.resets,3)
            for a,x,y in agent.rows:self.assertEqual(agent.apply(a,x),y)
    def test_cold(self):
        a=Observer(4)
        for _ in range(20):a.transition(lambda action,x:(x+action+1)%16)
        for m in a.models:
            for b in m.banks:
                snap=b.snapshot();self.assertEqual(EquationBank.restore(snap).snapshot(),snap)
                with self.assertRaises(ValueError):EquationBank.restore(snap+b'x')
    def test_visit_gate(self):
        a=Observer(4);a.transition(lambda action,x:0);self.assertEqual(a.visits[0][0],1);self.assertEqual(a.visits[1][0],0);self.assertEqual(a.transition(lambda action,x:0)[0],1)

if __name__=='__main__':unittest.main()
