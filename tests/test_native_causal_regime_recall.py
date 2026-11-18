"""Read-only native causal regime recall; no semantic world labels or owner route."""
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_property_knowledge import NativePropertyKnowledge


def original():
    props=NativePropertyKnowledge("ckad25w-tests",entities=8,context_bits=3)
    rows=[[e,b,(e>>b)&1] for e in range(8) for b in range(3)]
    props=props.stage_properties(rows,digest(canonical(rows)),source_namespace="ckad25w-tests")
    raw=props.checkpoint()
    m=NativeCumulativeLearner(raw,digest(raw))
    first=[[x&7,x>>3,int((x&7)==3)] for x in range(16) if x not in (2,5,9,14)]
    return m.observe(0,first,digest(canonical(first)),source_ref="a"*64)


def bit(law,mask):
    c0,c1,c2,a=((mask>>i)&1 for i in range(4))
    if law=="A":return 1^(c0&a)^(c1&c2)
    if law=="B":return c2^(c0&c1)^(c1&a)
    if law=="P":return c0^c2^a
    if law=="Q":return 1^(c0&c2)
    raise ValueError("bad test law")


def rows(law,masks):
    return [[x&7,x>>3,bit(law,x)] for x in masks]


def train(m,slot,law,masks):
    vals=rows(law,masks)
    ref=digest(canonical(["CKAD25-W-TEST",slot,law]))
    for batch in (vals[:8],vals[8:]):
        if batch:m=m.observe(slot,batch,digest(canonical(batch)),source_ref=ref)
    return m


def bank():
    old=original()
    masks=list(range(12))
    m=train(old,1,"A",masks).compile_causal_relations(1)
    m=train(m,2,"B",masks).compile_causal_relations(2)
    return old,m


class RegimeRecallTests(unittest.TestCase):
    def test_retained_numeric_knowledge_and_original_native_survive_pressure_and_cold(self):
        old,m=bank()
        refs=[m._compiled[j].checkpoint() for j in (1,2)]
        m=train(m,3,"P",list(range(8)))
        m=train(m,4,"Q",list(range(8)))
        raw=m.checkpoint()
        cold=NativeCumulativeLearner.restore(raw,digest(raw))
        self.assertEqual(cold.checkpoint(),raw)
        self.assertEqual([cold._compiled[j].checkpoint() for j in (1,2)],refs)
        self.assertEqual(cold._properties.checkpoint(),old._properties.checkpoint())
        self.assertEqual(cold._source._seen[0],old._source._seen[0])
        self.assertEqual(cold._events[:len(old._events)],old._events)
        self.assertEqual([cold.predict(0,c,a) for a in (0,1) for c in range(8)],
                         [old.predict(0,c,a) for a in (0,1) for c in range(8)])

    def test_unlabeled_returned_relation_selects_source_checkpoint(self):
        _,m=bank()
        # Public diagnostics only, not any regime label or held consequence.
        for law,expected in (("A",1),("B",2),("A",1)):
            diagnostics=rows(law,[0,2,5,11])
            p,q,slot=m.recall_causal_regime([1,2],diagnostics,13&7,13>>3)
            self.assertEqual(slot,expected)
            want=m.causal_relation_probability(expected,13&7,13>>3)
            self.assertEqual((p,q),want)

    def test_known_mismatch_abstains_without_source_learning(self):
        _,m=bank()
        raw=m.checkpoint()
        # On source-known probes, flip each source's expectation on at least one.
        a=rows("A",[0,2,5,11])
        b=rows("B",[0,2,5,11])
        disagree=[i for i in range(4) if a[i][2]!=b[i][2]]
        self.assertGreaterEqual(len(disagree),1)
        spoof=[x[:] for x in a]
        # Invert A's label on one agreement and one disagreement; reject both.
        shared=next((i for i in range(4) if a[i][2]==b[i][2]),None)
        self.assertIsNotNone(shared)
        spoof[shared][2]^=1
        got=m.recall_causal_regime((1,2),spoof,15&7,15>>3)
        self.assertEqual(got,(1,2,None))
        self.assertEqual(m.checkpoint(),raw)

    def test_invalid_probes_slots_and_future_outcome_forms_fail_closed(self):
        _,m=bank()
        good=rows("A",[0,2,5,11])
        before=m.checkpoint()
        for slots,data in [
            ([1,1],good),([1,3],good),([1],good),([1,2],good[:3]),
            ([1,2],good[:3]+[good[0]]),([1,2],good[:3]+[[0,0,True]]),
            ([1,2],good[:3]+[[0,0,2]]),([1,2],good[:3]+[[0,0,0,1]])
        ]:
            with self.subTest(slots=slots,data=data),self.assertRaises(ValueError):
                m.recall_causal_regime(slots,data,7,1)
        self.assertEqual(m.checkpoint(),before)

    def test_causal_recall_source_view_invalidation(self):
        _,m=bank()
        oldB=m._compiled[2].checkpoint()
        m=train(m,1,"A",[12,13,14,15])
        self.assertIsNone(m._compiled[1])
        self.assertEqual(m._compiled[2].checkpoint(),oldB)
        with self.assertRaises(ValueError):
            m.recall_causal_regime((1,2),rows("A",[0,2,5,11]),1,1)
        self.assertEqual(NativeCumulativeLearner.restore(m.checkpoint(),digest(m.checkpoint())).checkpoint(),
                         m.checkpoint())


if __name__=="__main__":
    unittest.main()
