import unittest
from agent import Agent
from world import World,rng_for
from equations import EquationBank

class Tests(unittest.TestCase):
    def test_empty(self):
        a=Agent(4,'frontier');self.assertEqual(a.choose(),0);self.assertEqual(a.shadow(),0)
    def test_visits(self):
        a=Agent(4,'least_visit');a.transition(lambda x,y:0);self.assertEqual(a.visits[0][0],1);self.assertEqual(a.visits[1][0],0);self.assertEqual(a.choose(),1)
    def test_partial_graph_parity(self):
        rng=rng_for('WSP48unitgraph')
        for _ in range(60):
            a=Agent(4,'frontier')
            for x in range(16):
                for action in range(2):
                    if rng.randrange(3):
                        y=rng.randrange(16);a.models[-1].banks[action].observe(x,y);a.predecessors[y]|=1<<x
                    a.visits[action][x]=rng.randrange(7)
            for x in range(16):a.state=x;self.assertEqual(a.choose(),a.shadow())
    def test_actual_trajectory(self):
        w=World(4,'quadratic','WSP48unitworld');a=Agent(4,'frontier')
        for i in range(256):
            old=0 if i%64==0 else a.state
            action,x,y=a.transition(w.apply);self.assertEqual(x,old);self.assertEqual(y,w.apply(action,x))
        self.assertEqual(a.resets,3)
        for action,x,y in a.rows:self.assertEqual(a.apply(action,x),y)
    def test_cold_banks(self):
        a=Agent(4,'frontier');w=World(4,'linear','WSP48cold')
        for _ in range(40):a.transition(w.apply)
        for m in a.models:
            for b in m.banks:
                snap=b.snapshot();self.assertEqual(EquationBank.restore(snap).snapshot(),snap)
                with self.assertRaises(ValueError):EquationBank.restore(snap+b'x')
    def test_frontier_path(self):
        a=Agent(4,'frontier')
        for action,x,y in [(0,0,0),(1,0,1),(0,1,0),(1,1,2)]:
            a.models[-1].banks[action].observe(x,y);a.predecessors[y]|=1<<x
        self.assertEqual(a.choose(),1)
    def test_frozen_equations(self):
        import hashlib
        from pathlib import Path
        self.assertEqual(hashlib.sha256(Path(__file__).with_name('equations.py').read_bytes()).hexdigest(),'bf04ed6499b35880bd7f38fccd55c0bd28999d9060c96b3217f825e10f402810')

if __name__=='__main__':unittest.main()
