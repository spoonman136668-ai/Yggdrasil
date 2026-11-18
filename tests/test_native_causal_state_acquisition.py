"""CKAD25-Y: actual native source-grounded causal memory allocation negatives."""
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from test_native_causal_regime_recall import original, rows


def law(kind, m):
    c0,c1,c2,a=((m>>i)&1 for i in range(4))
    if kind=="A":return 1^(c0&a)^(c1&c2)
    if kind=="B":return c2^(c0&c1)^(c1&a)
    if kind=="C":return c0^c1^a
    if kind=="D":return c0^c1^c2^a
    if kind=="P":return c0^c2^a
    if kind=="Q":return 1^(c0&c2)
    raise ValueError("UNKNOWN_TEST_CAUSAL_WORLD")


def observed(kind,masks):
    return [[m&7,m>>3,law(kind,m)] for m in masks]


def learn(m,kind,masks,*,source):
    data=observed(kind,masks)
    return m.incorporate_causal_world(data,digest(canonical(data)),source_ref=source)


class NativeCausalStateAcquisitionTests(unittest.TestCase):
    def test_new_causal_state_from_true_witnesses_and_cold_return(self):
        root=original()
        initial=root.checkpoint()
        m,a,status=learn(root,"A",list(range(12)),source="a"*64)
        self.assertEqual((a,status),(1,"ACQUIRED"))
        self.assertEqual(m._source._seen[1].bit_count(),12)
        self.assertGreater(m._compiled[1].model_count,0)
        first=m._compiled[1].checkpoint()
        m,b,status=learn(m,"B",list(range(12)),source="b"*64)
        self.assertEqual((b,status),(2,"ACQUIRED"))
        self.assertEqual(first,m._compiled[1].checkpoint())
        self.assertGreater(m._compiled[2].model_count,0)
        m2,returned,status=learn(m,"A",[0,2,5,11],source="c"*64)
        self.assertIs(m2,m)
        self.assertEqual((returned,status),(1,"RECALLED"))
        m,c,status=learn(m,"C",list(range(12)),source="d"*64)
        self.assertEqual((c,status),(3,"ACQUIRED"))
        self.assertGreater(m._compiled[3].model_count,0)
        frozen=[m._compiled[i].checkpoint() for i in (1,2,3)]
        after=m.checkpoint()
        cold=NativeCumulativeLearner.restore(after,digest(after))
        self.assertEqual(cold.checkpoint(),after)
        self.assertEqual([cold._compiled[i].checkpoint() for i in (1,2,3)],frozen)
        self.assertEqual(cold._properties.checkpoint(),root._properties.checkpoint())
        self.assertEqual(cold._source._seen[0],root._source._seen[0])
        self.assertEqual(cold._hypotheses[0].checkpoint(),root._hypotheses[0].checkpoint())
        self.assertEqual(cold._events[:len(root._events)],root._events)
        self.assertNotEqual(cold.checkpoint(),initial)

    def test_novel_out_of_class_preserves_compiled_knowledge(self):
        m=original()
        for kind,letter in (("A","a"),("B","b"),("C","c")):
            m,slot,status=learn(m,kind,list(range(12)),source=letter*64)
            self.assertEqual(status,"ACQUIRED")
        original_committee=[m._compiled[i].checkpoint() for i in (1,2,3)]
        fresh,slot,status=learn(m,"D",list(range(12)),source="d"*64)
        self.assertEqual(slot,4)
        self.assertIn(status,("INCOMPATIBLE","ACQUIRED"))
        self.assertEqual([fresh._compiled[i].checkpoint() for i in (1,2,3)],
                         original_committee)
        self.assertEqual([fresh._source._seen[i].bit_count() for i in (1,2,3,4)],
                         [12,12,12,12])
        if status=="INCOMPATIBLE":
            self.assertEqual(fresh.causal_relation_probability(4,4,1),(1,2))

    def test_source_quarantine_and_unrelated_pressure_isolation(self):
        m=original()
        m,_,_=learn(m,"A",list(range(12)),source="a"*64)
        basis=m._compiled[1].checkpoint()
        rows_p=observed("P",list(range(8)))
        rows_q=observed("Q",list(range(8)))
        m=m.observe(10,rows_p,digest(canonical(rows_p)),source_ref="e"*64)
        m=m.observe(11,rows_q,digest(canonical(rows_q)),source_ref="f"*64)
        raw=m.checkpoint()
        cold=NativeCumulativeLearner.restore(raw,digest(raw))
        self.assertEqual(cold._compiled[1].checkpoint(),basis)
        self.assertEqual([cold._source._seen[i].bit_count() for i in (10,11)],[8,8])
        self.assertEqual(cold.checkpoint(),raw)
        broken=observed("A",[0])
        broken[0][2]^=1
        changed=cold.observe(1,broken,digest(canonical(broken)),source_ref="b"*64)
        self.assertTrue(changed._quarantined[1])
        self.assertEqual(cold._compiled[1].checkpoint(),basis)
        self.assertEqual(cold.checkpoint(),raw)

    def test_low_evidence_abstains_and_source_replays_fail_closed(self):
        m=original()
        rows_a=observed("A",[0,2,5,11])
        old=m.checkpoint()
        after,slot,status=m.incorporate_causal_world(rows_a,digest(canonical(rows_a)),source_ref="a"*64)
        self.assertIs(after,m)
        self.assertEqual((slot,status),(None,"ABSTAIN"))
        self.assertEqual(m.checkpoint(),old)
        bad_packets=[
            rows_a+[rows_a[0]],rows_a[:3]+[rows_a[0]],
            rows_a[:3]+[[7,1,True]],rows_a[:3]+[[0,0,2]],
        ]
        for bad in bad_packets:
            with self.subTest(packet=bad),self.assertRaises(ValueError):
                m.incorporate_causal_world(bad,digest(canonical(bad)),source_ref="a"*64)
        with self.assertRaises(ValueError):
            m.incorporate_causal_world(rows_a,"0"*64,source_ref="a"*64)

    def test_source_capacity_fails_closed_and_existing_state_not_mutated(self):
        m=original()
        m,_,_=learn(m,"A",list(range(12)),source="a"*64)
        original_checkpoint=m.checkpoint()
        data=observed("B",list(range(12)))
        with self.assertRaises(ValueError):
            m.incorporate_causal_world(data,digest(canonical(data)),
                                       source_ref="b"*64,available_slots=(1,))
        self.assertEqual(m.checkpoint(),original_checkpoint)


if __name__=="__main__": unittest.main()
