"""WSP-09: proof that synaptic activity allocates blank concept slots."""
from __future__ import annotations

import hashlib
import math
import pathlib
import unittest

from slot_graph import (
    INPUT_BITS, SLOTS, INPUT_NODES, PLASTIC_COUNT, MAX_NODES, MAX_EDGES,
    SPEC, UniformNeuronVM, SelfAllocatingCircuit, encode,
)
from controls import (
    FUNCTIONS_3, FUNCTIONS_4, FIXED_4_MASKS,
    to_bits, observed_events, ExactAssociative, TrainedOneHotLogistic,
)

ROOT=pathlib.Path(__file__).resolve().parent
PROTOCOL_BLOB="eee3d254cc705ff951445089568a1dd3745af67a"


class WSP09Tests(unittest.TestCase):
    def test_protocol_preregistered_and_blank_memory_is_real(self):
        text=(ROOT/"protocol.json").read_bytes().replace(b"\r\n",b"\n")
        self.assertEqual(
            hashlib.sha1(b"blob "+str(len(text)).encode()+b"\0"+text).hexdigest(),
            PROTOCOL_BLOB)
        self.assertEqual((INPUT_BITS,SLOTS,INPUT_NODES,PLASTIC_COUNT),(4,16,6,97))
        self.assertEqual(len(SPEC.plastic_indices),PLASTIC_COUNT)
        self.assertEqual(len(SPEC.plastic_rules),PLASTIC_COUNT)
        self.assertEqual(len(set(r[0] for r in SPEC.plastic_rules)),PLASTIC_COUNT)
        self.assertLessEqual(len(SPEC.thresholds),MAX_NODES)
        self.assertLessEqual(len(SPEC.edges),MAX_EDGES)
        self.assertEqual(len(SPEC.fixed_indices),2)
        self.assertEqual(SelfAllocatingCircuit.GRADIENT_STEPS,0)
        model=SelfAllocatingCircuit()
        self.assertEqual(model.allocated_slots,0)
        self.assertEqual(model.positive_plastic,0)
        self.assertEqual(model.fault,0)
        self.assertEqual(len(SPEC.source_sha256),64)
        for i in SPEC.plastic_indices:
            self.assertEqual(model.weights[i],0)

    def test_all_worlds_are_frozen_and_exhaustive(self):
        self.assertEqual(FUNCTIONS_3,tuple(range(256)))
        self.assertEqual(len(FUNCTIONS_4),72)
        self.assertEqual(len(set(FUNCTIONS_4)),72)
        self.assertEqual(FUNCTIONS_4[:8],FIXED_4_MASKS)
        for bits,masks in ((3,FUNCTIONS_3),(4,FUNCTIONS_4)):
            for mask in masks:
                events=observed_events(mask,bits)
                self.assertEqual(len(events),1<<bits)
                self.assertEqual(len(set(x for x,y in events)),1<<bits)
                for x,y in events:
                    pattern=sum(value<<i for i,value in enumerate(x))
                    self.assertEqual(y,(mask>>pattern)&1)
                    self.assertEqual(x[3],0 if bits==3 else x[3])

    def test_every_three_and_four_bit_function_learned_only_after_witness(self):
        verified=pre_abstain=post=restores=replays=0
        for bits,masks in ((3,FUNCTIONS_3),(4,FUNCTIONS_4)):
            for mask in masks:
                model=SelfAllocatingCircuit()
                exact=ExactAssociative()
                events=observed_events(mask,bits)
                for x,label in events:
                    self.assertIsNone(model.predict(x))
                    pre_abstain+=1
                    model.observe(x,label)
                    exact.observe(x,label)
                    self.assertEqual(model.predict(x),label)
                    self.assertEqual(model.predict(x),exact.predict(x))
                    post+=1
                self.assertEqual(model.allocated_slots,len(events))
                self.assertEqual(model.fault,0)
                raw=model.snapshot()
                restored=SelfAllocatingCircuit.restore(raw)
                self.assertEqual(restored.snapshot(),raw)
                self.assertEqual(restored.programmed_sha256(),
                                 model.programmed_sha256())
                restores+=1
                for x,label in (events[0],events[1],events[-2],events[-1]):
                    restored.observe(x,label)
                self.assertEqual(restored.snapshot(),raw)
                replays+=1
                for x,label in events:
                    self.assertEqual(restored.predict(x),label)
                    verified+=1
        self.assertEqual((pre_abstain,post,verified),(3200,3200,3200))
        self.assertEqual((restores,replays),(328,328))

    def test_new_sensory_identity_and_label_are_written_in_synapses(self):
        m=SelfAllocatingCircuit()
        first=(1,0,1,0)
        second=(0,1,0,1)
        self.assertIsNone(m.predict(first))
        m.observe(first,1)
        self.assertEqual(m.allocated_slots,1)
        self.assertEqual(m.weights[SPEC.used_indices[0]],1)
        self.assertEqual(tuple(m.weights[i] for i in SPEC.address_indices[0]),first)
        self.assertEqual(m.weights[SPEC.label_indices[0]],1)
        self.assertEqual(m.predict(first),1)
        self.assertIsNone(m.predict(second))
        m.observe(second,0)
        self.assertEqual(m.allocated_slots,2)
        self.assertEqual(tuple(m.weights[i] for i in SPEC.address_indices[1]),second)
        self.assertEqual(m.weights[SPEC.label_indices[1]],0)
        self.assertEqual(m.predict(second),0)
        self.assertEqual(m.predict(first),1)

    def test_repeated_witness_does_not_allocate_or_modify_weights(self):
        m=SelfAllocatingCircuit()
        x=(1,0,1,1)
        m.observe(x,1)
        raw=m.snapshot()
        for _ in range(5):
            m.observe(x,1)
        self.assertEqual(m.snapshot(),raw)
        self.assertEqual(m.allocated_slots,1)

    def test_trained_onehot_control_meets_preregistered_loss_budget(self):
        correct=converged=steps=0
        for mask in FIXED_4_MASKS:
            examples=observed_events(mask,4)
            model=TrainedOneHotLogistic()
            model.fit(examples)
            self.assertTrue(math.isfinite(model.loss))
            self.assertLessEqual(model.steps,3000)
            converged+=int(model.converged)
            steps+=model.steps
            for x,label in examples:
                correct+=model.predict(x)==label
        self.assertEqual((converged,correct),(8,128))
        self.assertGreater(steps,0)
        with self.assertRaises(ValueError):
            TrainedOneHotLogistic().fit(observed_events(FIXED_4_MASKS[0],4)[:-1])

    def test_genuine_conflicting_witness_sets_fault_for_every_world(self):
        failures=0
        for bits,masks in ((3,FUNCTIONS_3),(4,FUNCTIONS_4)):
            for mask in masks:
                m=SelfAllocatingCircuit()
                events=observed_events(mask,bits)
                for x,y in events:
                    m.observe(x,y)
                before=m.allocated_slots
                x,y=events[0]
                m.observe(x,y^1)
                self.assertEqual(m.fault,1)
                self.assertEqual(m.allocated_slots,before)
                for x,y in events:
                    self.assertIsNone(m.predict(x))
                self.assertEqual(SelfAllocatingCircuit.restore(m.snapshot()).fault,1)
                failures+=1
        self.assertEqual(failures,328)

    def test_zero_used_and_label_memory_defeats_inference(self):
        m=SelfAllocatingCircuit()
        events=observed_events(0xffff,4)
        for x,y in events:
            m.observe(x,y)
        self.assertTrue(all(m.predict(x)==1 for x,y in events))
        wiped=SelfAllocatingCircuit.restore(m.snapshot())
        for slot in SPEC.used_indices:
            wiped.weights[slot]=0
        self.assertTrue(all(wiped.predict(x) is None for x,y in events))
        label_wiped=SelfAllocatingCircuit.restore(m.snapshot())
        label_wiped.weights[SPEC.label_indices[0]]=0
        self.assertNotEqual(label_wiped.predict(events[0][0]),1)

    def test_zero_addresses_collapses_distinctions(self):
        mask=0x6996
        m=SelfAllocatingCircuit()
        events=observed_events(mask,4)
        for x,y in events:
            m.observe(x,y)
        modified=SelfAllocatingCircuit.restore(m.snapshot())
        for row in SPEC.address_indices:
            for slot in row:
                modified.weights[slot]=0
        self.assertTrue(any(modified.predict(x)!=y for x,y in events))

    def test_checkpoint_integrity_and_unexpected_fifth_bit_fail_closed(self):
        m=SelfAllocatingCircuit()
        m.observe((1,1,0,0),1)
        raw=m.snapshot()
        changed=bytearray(raw)
        changed[25]^=1
        for corrupted in (raw[:-1],bytes(changed),bytearray(raw),b"FAKE"+raw[4:]):
            with self.assertRaises(ValueError):
                SelfAllocatingCircuit.restore(corrupted)
        bad=SelfAllocatingCircuit.restore(raw)
        bad.weights[SPEC.fixed_indices[0]]=0
        with self.assertRaises(ValueError):
            SelfAllocatingCircuit.restore(bad.snapshot())
        bad=SelfAllocatingCircuit.restore(raw)
        bad.weights[SPEC.plastic_indices[0]]=2
        with self.assertRaises(ValueError):
            SelfAllocatingCircuit.restore(bad.snapshot())
        before=m.snapshot()
        for x in ((1,0,0,0,1),(1,0,0),(1,0,2,0),
                  (True,0,0,0),(0,0,0,0,1)):
            with self.assertRaises(ValueError):
                m.observe(x,0)
            self.assertEqual(m.snapshot(),before)
        with self.assertRaises(ValueError):
            m.predict((1,0,0,0,1))
        with self.assertRaises(ValueError):
            m.observe((1,0,0,0),True)
        self.assertEqual(m.snapshot(),before)

    def test_uniform_runtime_not_a_task_specific_compiler(self):
        text=(ROOT/"slot_graph.py").read_text("utf-8")
        vm=text[text.index("class UniformNeuronVM:"):text.index("def encode(")]
        for forbidden in ("if mask", "if label", "if pattern",
                          "if index", "if op ==", "functions4",
                          "ExactAssociative", "dict[tuple"):
            self.assertNotIn(forbidden,vm)
        self.assertEqual(len(SPEC.plastic_rules),97)

    def test_separate_world_models_do_not_share_memory(self):
        a,b=SelfAllocatingCircuit(),SelfAllocatingCircuit()
        for x,y in observed_events(0x6996,4):
            a.observe(x,y)
        old=a.snapshot()
        for x,y in observed_events(0x9669,4):
            b.observe(x,y)
        self.assertEqual(a.snapshot(),old)
        self.assertNotEqual(a.programmed_sha256(),b.programmed_sha256())
        self.assertEqual(a.allocated_slots,b.allocated_slots)


if __name__=="__main__":
    unittest.main()
