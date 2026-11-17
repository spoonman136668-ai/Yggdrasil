import json
import unittest
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_property_observations import observed_property_view


def fixture():
    namespace='ckad11-engineering-unit'
    facts=[[e,p,(e>>p)&1] for e in range(16) for p in range(3)]
    k=NativePropertyKnowledge(namespace,entities=16,context_bits=3)
    k=k.stage_properties(facts,digest(canonical(facts)),source_namespace=namespace)
    events=[[e,1,e&1] for e in range(8)]
    k=k.stage_relation(0,events,digest(canonical(events)),source_namespace=namespace)
    return k,[[e,1] for e in range(8)]


class NativePropertyObservationsTests(unittest.TestCase):
    def test_only_original_witnesses_export_and_source_stays_exact(self):
        k,keys=fixture();raw=k.checkpoint()
        view,r=observed_property_view(raw,digest(raw),0,keys,observations=8)
        m=NativeContextAccumulator.restore(view,digest(view))
        self.assertEqual([m.predict(0,e,1) for e in range(8)],[e&1 for e in range(8)])
        self.assertIsNone(m.predict(0,0,0));self.assertEqual(k.checkpoint(),raw)
        self.assertEqual(r['source_records'],8);self.assertEqual(r['native_stored_properties'],48)

    def test_inferred_but_unwitnessed_entity_cannot_be_substituted(self):
        k,keys=fixture();raw=k.checkpoint();keys[-1]=[15,1]
        # Entity15 has the same property context as entity7. The model knows
        # its prediction, but that does NOT make its identity an old witness.
        self.assertEqual(k.predict_entity(0,15,1),k.predict_entity(0,7,1))
        with self.assertRaisesRegex(ValueError,'UNWITNESSED_ENTITY'):
            observed_property_view(raw,digest(raw),0,keys,observations=8)

    def test_wrong_event_order_or_action_is_not_original_evidence(self):
        k,keys=fixture();raw=k.checkpoint()
        with self.assertRaises(ValueError):observed_property_view(raw,digest(raw),0,list(reversed(keys)),observations=8)
        wrong=[x[:] for x in keys];wrong[0][1]=0
        with self.assertRaises(ValueError):observed_property_view(raw,digest(raw),0,wrong,observations=8)

    def test_context_binding_detects_changed_irrelevant_property(self):
        k,keys=fixture();d=json.loads(k.checkpoint())
        packed=bytearray.fromhex(d['known_value_planes_uint16le']);packed[2]^=4
        d['known_value_planes_uint16le']=packed.hex();bad=canonical(d)
        with self.assertRaisesRegex(ValueError,'CONTEXT_GROUNDING'):
            observed_property_view(bad,digest(bad),0,keys,observations=8)

    def test_pins_original_modes_and_invalid_exposures_rejected(self):
        k,keys=fixture();raw=k.checkpoint()
        with self.assertRaises(ValueError):observed_property_view(raw,'0'*64,0,keys,observations=8)
        with self.assertRaises(ValueError):observed_property_view(raw,digest(raw),0,keys,observations=8,source_mode='original')
        for n in (4,9,12,True):
            with self.assertRaises(ValueError):observed_property_view(raw,digest(raw),0,keys,observations=n)

    def test_duplicate_contexts_do_not_inflate_unique_knowledge(self):
        k,keys=fixture();ns=k._namespace
        events=[[e,1,e&1] for e in range(16)]
        k=k.stage_relation(0,events,digest(canonical(events)),source_namespace=ns)
        raw=k.checkpoint();view,r=observed_property_view(raw,digest(raw),0,[[e,1] for e in range(16)],observations=8)
        self.assertEqual(r['source_records'],16);self.assertEqual(r['unique_witnessed_contexts'],8)
        self.assertEqual(NativeContextAccumulator.restore(view,digest(view)).profile_info(0)['source_records'],8)


if __name__=='__main__':unittest.main()
