"""F10 source-free controls and native regression; no donor model or protected worlds."""
import unittest
from pathlib import Path
from f10_fixture import SEEDS,events,relation,shuffled,truth
from f10_transfer import PublicCausalCells,Link,NativeTransfer,ExactRetrieval
from f10_experiment import links,run
def prepare(seed):
    c=PublicCausalCells()
    data=events(seed)
    for s,a,y in data:c.observe(s,a,y)
    return c,data,links(relation(seed))
class F10(unittest.TestCase):
    def test_fixed_seeds_and_budget(self):
        self.assertEqual(SEEDS,tuple(range(7001,7009)))
        self.assertEqual(len(events(SEEDS[0])),32)
    def test_native_without_map_abstains(self):
        c,data,g=prepare(SEEDS[0])
        self.assertIsNone(c.choose(0,retained=True))
        self.assertIn(NativeTransfer(c,g).choose_target(0),(0,1))
    def test_matched_retrieval_and_native_parity(self):
        for seed in SEEDS:
            c,data,g=prepare(seed)
            n,r=NativeTransfer(c,g),ExactRetrieval(data,g)
            for t in range(4):
                self.assertEqual(n.choose_target(t),r.choose_target(t))
                self.assertEqual(n.choose_target(t),truth(seed,t))
    def test_negative_shuffled_relations(self):
        for seed in SEEDS:
            c,data,g=prepare(seed)
            n=NativeTransfer(c,links(shuffled(seed)))
            self.assertEqual(sum(n.choose_target(t)!=truth(seed,t) for t in range(4)),2)
    def test_cold_restore_and_nonmutating_read(self):
        c,data,g=prepare(SEEDS[0]);raw=c.snapshot()
        n=NativeTransfer(c,g);cold=NativeTransfer(PublicCausalCells.restore(raw),g)
        self.assertEqual([n.choose_target(t) for t in range(4)],
                         [cold.choose_target(t) for t in range(4)])
        self.assertEqual(c.snapshot(),raw)
    def test_interference_independence(self):
        c,data,g=prepare(SEEDS[1]);n=NativeTransfer(c,g)
        old=[n.choose_target(t) for t in range(4)]
        c.observe(6,0,1);c.observe(0,1,1,retained=True)
        self.assertEqual(old,[n.choose_target(t) for t in range(4)])
    def test_revises_on_real_public_contradiction(self):
        c,data,g=prepare(SEEDS[0]);n=NativeTransfer(c,g)
        t=next(t for t,e in g.items() if e.source==0)
        old=n.choose_target(t);arm=old^g[t].flip
        for _ in range(9):
            c.observe(0,arm,0);c.observe(0,arm^1,1)
        self.assertEqual(n.choose_target(t),old^1)
    def test_malformed_input_rejected(self):
        c,data,g=prepare(SEEDS[0])
        with self.assertRaises(ValueError):Link(0,True)
        with self.assertRaises(ValueError):Link(True,1)
        with self.assertRaises(ValueError):NativeTransfer(c,{})
        with self.assertRaises(ValueError):NativeTransfer(c,{**g,2:(0,1)})
        with self.assertRaises(ValueError):ExactRetrieval(((0,True,1),),g)
        with self.assertRaises(ValueError):NativeTransfer(c,g).choose_target(True)
    def test_no_world_or_donor_in_policy(self):
        s=Path(__file__).with_name("f10_transfer.py").read_text()
        self.assertNotIn("import f10_fixture",s)
        self.assertNotIn("from f10_fixture",s)
        self.assertNotIn("transformers",s)
    def test_bytes_and_checkpoint_unchanged(self):
        self.assertEqual(PublicCausalCells.LEARNED_BYTES,128)
        self.assertEqual(PublicCausalCells.CHECKPOINT_BYTES,164)
    def test_dev_result_cannot_claim_sci_pass(self):
        x=run()
        self.assertEqual(x["classification"],"DEV_INTERFACE_PARITY_ONLY")
        self.assertFalse(x["scientific_pass"])
        self.assertFalse(x["unique_gain_over_strongest_retrieval"])
if __name__=="__main__":unittest.main()
