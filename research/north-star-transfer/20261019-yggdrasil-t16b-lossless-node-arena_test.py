"""T16B Ygg node-dictionary structural unit tests; no source birth."""
import importlib.util,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("20261019-yggdrasil-t16b-lossless-node-arena.py")
s=importlib.util.spec_from_file_location("y16b",p);m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m;s.loader.exec_module(m)

class LosslessArenaTests(unittest.TestCase):
    def test_shared_nodes_encode_losslessly(self):
        edges=((100,0,200),(200,1,300),(300,2,400),
               (200,3,500),(500,2,600),(600,1,700))
        b=m.pack_edges(edges)
        self.assertIsInstance(b,bytes)
        self.assertEqual(m.unpack_edges(b),edges)
        self.assertLess(len(b),2+8*len(edges))

    def test_node_ids_24bit_not_truncated(self):
        edges=((0xffffff,3,0x10000),(0x10000,0,0xfffffe))
        self.assertEqual(m.unpack_edges(m.pack_edges(edges)),edges)

    def test_new_encoding_is_not_fragment_representation(self):
        # 8 sharing edges use only 9 nodes instead of repeating endpoints.
        edges=tuple((100+i,i%4,101+i) for i in range(8))
        compressed=m.pack_edges(edges)
        self.assertEqual(len(compressed),2+9*3+8*2)
        self.assertLess(len(compressed),8*7)

    def test_six_hop_public_answer(self):
        state=m.initial_state()
        nodes=[401,402,403,404,405,406,407]
        for i in range(6):
            state=m.observe(state,(nodes[i],i%4,nodes[i+1]))
        question={"start":nodes[0],"ops":tuple((i%4,1) for i in range(6))}
        self.assertEqual(m.solve(state,question),nodes[-1])
        self.assertLessEqual(len(state),144)
        self.assertEqual(len(m.unpack_state(state)[2]),6)

    def test_false_relation_never_invented(self):
        state=m.initial_state()
        for a,r,b in [(10,0,20),(20,1,30),(30,2,40)]:
            state=m.observe(state,(a,r,b))
        query={"start":10,"ops":((0,1),(1,1),(2,1),(3,1))}
        self.assertIsNone(m.solve(state,query))

    def test_ambiguity_fails_closed(self):
        state=m.initial_state()
        for e in ((5,0,6),(5,0,7)):
            state=m.observe(state,e)
        self.assertIsNone(m.solve(state,{"start":5,"ops":((0,1),)}))

    def test_budget_under_72_event_stream(self):
        state=m.initial_state()
        for i in range(72):
            state=m.observe(state,(10000+i*2,i%4,10001+i*2))
            self.assertLessEqual(len(state),144)
            _,c,rows=m.unpack_state(state)
            self.assertEqual(c[0],(i+1)&255)
            self.assertLessEqual(len(rows),72)
        self.assertGreater(m.unpack_state(state)[1][1],0)

    def test_train_only_weight_bytes_and_determinism(self):
        events=((100,0,200),(200,1,300),(300,2,400))
        train=((events,frozenset(events[:2])),)
        w,updates=m.train_coeff(train)
        self.assertEqual(len(w),20)
        self.assertGreater(updates,0)
        self.assertEqual((w,updates),m.train_coeff(train))
        state=m.initial_state(w)
        for e in events:state=m.observe(state,e)
        self.assertEqual(m.unpack_state(state)[0],w)

    def test_invalid_value_fails_closed(self):
        with self.assertRaises(AssertionError):
            m.observe(m.initial_state(),(1<<24,0,2))

if __name__=="__main__":unittest.main()
