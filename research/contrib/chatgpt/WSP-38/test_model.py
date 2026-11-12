import unittest
from model import NumericalWorld
from battery import run,query_schedule,source,observed_records,ref_reach

class WSP38Tests(unittest.TestCase):
    def test_tiny_composition_and_snapshot(self):
        graph=source(16,7)
        p,n=NumericalWorld.from_observations(16,observed_records(graph,7,16,False))
        self.assertEqual(n,16*8*3)
        for src,path,dst in query_schedule(16,7,16):
            self.assertEqual(p.answer(src,path,dst),int(dst in ref_reach(graph,src,path)))
        self.assertEqual(p.snapshot(),NumericalWorld.restore(p.snapshot()).snapshot())
    def test_fail_closed(self):
        p,_=NumericalWorld.from_observations(16,((0,0,1),))
        raw=p.snapshot()
        for altered in [raw[:-1],raw+b'!',raw[:-1]+bytes((raw[-1]^1,)),b'']:
            with self.assertRaises(ValueError):NumericalWorld.restore(altered)
        with self.assertRaises(ValueError):NumericalWorld.from_observations(16,((8,0,1),))
        with self.assertRaises(ValueError):p.patch(0,0,1,2)
        with self.assertRaises(ValueError):p.reach(0,(0,)*7)
    def test_unseen_fact_negative(self):
        graph=source(32,19)
        records=observed_records(graph,19,32,True)
        p,_=NumericalWorld.from_observations(32,records)
        self.assertLess(p.active_edges,32*8*3)
    def test_max_first_dev(self):
        result=run('DEV')
        self.assertEqual(result['engineering'],'PASS')
        self.assertEqual(result['largest_executed'],16384)
        self.assertEqual(result['levels'][0]['status'],'RESOURCE_SCREENED_NOT_EXECUTED')

if __name__=='__main__':unittest.main()
