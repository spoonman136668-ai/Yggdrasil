"""Source-only negative contracts for native cross-world causal falsification."""
import itertools
import unittest
from yggdrasil.native_context_basis import canonical, digest, feature_row
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from test_native_causal_state_acquisition import original, observed


def train():
    m=original()
    root=m.checkpoint()
    for law,ref in (("A","a"),("B","b"),("C","c")):
        packet=observed(law,list(range(12)))
        m,slot,status=m.incorporate_causal_world(
            packet,digest(canonical(packet)),source_ref=ref*64)
        assert status=="ACQUIRED",(law,slot,status)
    return root,m


def append(m,kind,records,query,slot=12):
    return m.validate_causal_source_with_witnesses(
        3,records,digest(canonical(records)),source_ref=(kind*64),
        evidence_slot=slot,query_context=query&7,query_action=query>>3)


class NativeCausalWitnessTests(unittest.TestCase):
    def test_actual_new_witnesses_are_persisted_without_erasing_learned_state(self):
        root,m=train()
        old=[m._compiled[i].checkpoint() for i in (1,2,3)]
        before=m.checkpoint()
        good=observed("C",[12,13])
        new,prob,verdict=append(m,"d",good,14)
        self.assertEqual(verdict,"CONSISTENT")
        self.assertEqual(new._source._seen[12].bit_count(),2)
        self.assertNotEqual(new.checkpoint(),before)
        self.assertEqual([new._compiled[i].checkpoint() for i in (1,2,3)],old)
        self.assertEqual(new._source._seen[0],m._source._seen[0])
        self.assertEqual(new._properties.checkpoint(),m._properties.checkpoint())
        self.assertEqual(new._events[:len(m._events)],m._events)
        self.assertGreater(prob[1],0)
        raw=new.checkpoint()
        cold=NativeCumulativeLearner.restore(raw,digest(raw))
        self.assertEqual(cold.checkpoint(),raw)
        repeat,pred,status=append(cold,"d",good,14)
        self.assertEqual((pred,status),(prob,verdict))
        self.assertEqual(repeat.checkpoint(),raw)
        self.assertEqual(m.checkpoint(),before)

    def test_explicit_contradiction_abstains_but_preserves_true_source(self):
        root,m=train()
        original=m.checkpoint()
        options=[12,13,14,15]
        models=m._compiled[3]._models
        contradiction=None
        for mask_a,mask_b in itertools.combinations(options,2):
            for y_a,y_b in itertools.product((0,1),repeat=2):
                if all((((w & feature_row(mask_a,4)).bit_count()&1)!=y_a)
                       or (((w & feature_row(mask_b,4)).bit_count()&1)!=y_b)
                       for w in models):
                    contradiction=[[mask_a&7,mask_a>>3,y_a],
                                   [mask_b&7,mask_b>>3,y_b]]
                    held=next(x for x in options if x not in (mask_a,mask_b))
                    break
            if contradiction:break
        self.assertIsNotNone(contradiction)
        new,prob,status=append(m,"e",contradiction,held)
        self.assertEqual(status,"FALSIFIED")
        self.assertEqual(prob,(1,2))
        self.assertEqual(m.checkpoint(),original)
        self.assertEqual(new._compiled[3].checkpoint(),m._compiled[3].checkpoint())
        self.assertEqual(new._source._seen[12].bit_count(),2)

    def test_witness_validation_and_slot_fail_closed(self):
        _,m=train()
        evidence=observed("C",[12,13])
        raw=m.checkpoint()
        for packet,slot,q in [
            (evidence+evidence[:1],12,14),
            ([evidence[0],evidence[0]],12,14),
            ([observed("C",[0])[0],evidence[1]],12,14),
            (evidence,11,14),
            (evidence,12,12),
            (evidence,12,0),
            ([evidence[0],evidence[1][:2]+[True]],12,14),
        ]:
            with self.subTest(rows=packet,slot=slot,query=q),self.assertRaises(ValueError):
                m.validate_causal_source_with_witnesses(
                    3,packet,digest(canonical(packet)),source_ref="f"*64,
                    evidence_slot=slot,query_context=q&7,query_action=q>>3)
        with self.assertRaises(ValueError):
            m.validate_causal_source_with_witnesses(
                3,evidence,"0"*64,source_ref="f"*64,
                evidence_slot=12,query_context=6,query_action=1)
        added,_,_=append(m,"g",evidence,14)
        with self.assertRaises(ValueError):
            append(added,"h",evidence,14)
        self.assertEqual(m.checkpoint(),raw)


if __name__=="__main__":unittest.main()
