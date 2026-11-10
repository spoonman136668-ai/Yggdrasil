"""WSP-08: frozen, adversarial tests of learned neural feature-depth selection."""
from __future__ import annotations

import hashlib
import math
import pathlib
import unittest

from graph import (
    N, SEEDS, MODES, PLASTIC_COUNT, INPUT_N,
    MAX_FIXED, MAX_NODES, MAX_EDGES, SPEC, PublicWorld,
    UniformVM, GrowingSynapseCircuit, encode,
)
from controls import SymbolicAdaptive, TrainedMLP

ROOT=pathlib.Path(__file__).resolve().parent
PROTOCOL_BLOB="d4addc190df49fc52dd8fa9dfae5df55e4a2c9e0"


class WSP08Tests(unittest.TestCase):
    def test_precommitted_protocol_and_graph_capacity(self):
        raw=(ROOT/"protocol.json").read_bytes().replace(b"\r\n",b"\n")
        encoded=b"blob "+str(len(raw)).encode()+b"\0"+raw
        self.assertEqual(hashlib.sha1(encoded).hexdigest(),PROTOCOL_BLOB)
        self.assertEqual((N,INPUT_N,PLASTIC_COUNT),(24,51,747))
        self.assertEqual((SEEDS,MODES),(tuple(range(12)),(1,2,3)))
        self.assertLessEqual(len(SPEC.fixed_indices),MAX_FIXED)
        self.assertLessEqual(len(SPEC.threshold),MAX_NODES)
        self.assertLessEqual(len(SPEC.edges),MAX_EDGES)
        self.assertEqual(len(SPEC.plastic_indices),747)
        self.assertEqual(len(SPEC.rules),747)
        self.assertEqual(len(set(x[0] for x in SPEC.rules)),747)
        self.assertEqual(len(SPEC.graph_sha256),64)
        self.assertEqual(GrowingSynapseCircuit.GRADIENT_STEPS,0)
        self.assertEqual(TrainedMLP.PARAMETERS,41)

    def test_raw_worlds_exact_40_experiences_and_blind_public_labels(self):
        for seed in SEEDS:
            for mode in MODES:
                world=PublicWorld(seed,mode)
                obs=world.public_events()
                self.assertEqual(len(obs),40)
                self.assertEqual({x[0] for x in obs[:24]},set(range(1000,1024)))
                self.assertTrue(set(world.train).isdisjoint(world.test))
                self.assertEqual((len(world.train),len(world.test)),(16,8))
                self.assertEqual(set(x[1] for x in obs[:24]),{0})
                self.assertEqual(set(x[1] for x in obs[24:]),{1})
                self.assertEqual(len(set(x[0] for x in obs[24:])),16)

    def test_36_worlds_adapt_depth_from_actual_contradictions_and_transfer(self):
        total=learned_2=learned_3=cold=replayed=0
        for seed in SEEDS:
            for mode in MODES:
                world=PublicWorld(seed,mode)
                circuit=GrowingSynapseCircuit()
                symbolic=SymbolicAdaptive()
                observations=world.public_events()
                for event in observations:
                    circuit.observe(*event)
                    symbolic.observe(*event)
                self.assertEqual(circuit.fault,0)
                self.assertEqual(circuit.depth,mode)
                self.assertEqual(symbolic.active_depth(),mode)
                self.assertGreater(circuit.active_plastic(),0)
                learned_2 += circuit.weights[SPEC.depth2_slot]
                learned_3 += circuit.weights[SPEC.depth3_slot]
                self.assertEqual(circuit.weights[SPEC.depth3_slot]<=
                                 circuit.weights[SPEC.depth2_slot],True)
                raw=circuit.snapshot()
                restored=GrowingSynapseCircuit.restore(raw)
                self.assertEqual(restored.snapshot(),raw)
                self.assertEqual(restored.programmed_sha256(),circuit.programmed_sha256())
                cold+=1
                for event in (observations[0],observations[23],
                              observations[24],observations[-1]):
                    restored.observe(*event)
                self.assertEqual(restored.snapshot(),raw)
                replayed+=1
                for state in world.test:
                    expected=world.outcome(state,1)[2]
                    self.assertEqual(circuit.predict_a1(state),expected)
                    self.assertEqual(restored.predict_a1(state),expected)
                    self.assertEqual(symbolic.predict_a1(state),expected)
                    total+=1
        self.assertEqual((total,learned_2,learned_3,cold,replayed),
                         (288,24,12,36,36))

    def test_one_and_two_hop_controls_cannot_solve_higher_depth_modes(self):
        correct1=correct2=0
        for seed in SEEDS:
            for mode in MODES:
                w=PublicWorld(seed,mode)
                one,two=SymbolicAdaptive(1),SymbolicAdaptive(2)
                for event in w.public_events():
                    one.observe(*event)
                    two.observe(*event)
                for s in w.test:
                    target=w.outcome(s,1)[2]
                    correct1+=one.predict_a1(s)==target
                    correct2+=two.predict_a1(s)==target
        self.assertEqual((correct1,correct2),(96,192))

    def test_adversarial_hidden_outcomes_are_not_identifiable(self):
        wrong_confident=after_abstain=0
        for seed in SEEDS:
            for mode in MODES:
                world=PublicWorld(seed,mode)
                m=GrowingSynapseCircuit()
                for e in world.public_events():
                    m.observe(*e)
                for state in world.test:
                    guess=m.predict_a1(state)
                    self.assertIsNotNone(guess)
                    self.assertNotEqual(guess,world.outcome(state,1,shift=True)[2])
                    wrong_confident+=1
                m.observe(*world.outcome(world.test[0],1,shift=True))
                self.assertEqual(m.fault,1)
                for state in world.test:
                    self.assertIsNone(m.predict_a1(state))
                    after_abstain+=1
                self.assertEqual(GrowingSynapseCircuit.restore(m.snapshot()).fault,1)
        self.assertEqual((wrong_confident,after_abstain),(288,288))

    def test_ablate_numeric_transition_and_feature_gate_memory(self):
        for mode in MODES:
            w=PublicWorld(3,mode)
            m=GrowingSynapseCircuit()
            for e in w.public_events():
                m.observe(*e)
            self.assertTrue(all(m.predict_a1(s) is not None for s in w.test))
            no_successor=GrowingSynapseCircuit.restore(m.snapshot())
            for slot in SPEC.successor_slots:
                no_successor.weights[slot]=0
            self.assertTrue(all(no_successor.predict_a1(s) is None for s in w.test))
            no_action1=GrowingSynapseCircuit.restore(m.snapshot())
            for slot in SPEC.a1_coverage_slots:
                no_action1.weights[slot]=0
            self.assertTrue(all(no_action1.predict_a1(s) is None for s in w.test))
            empty=GrowingSynapseCircuit()
            self.assertTrue(all(empty.predict_a1(s) is None for s in w.test))

    def test_conflicting_action0_repeat_writes_numeric_fault(self):
        w=PublicWorld(5,2)
        m=GrowingSynapseCircuit()
        for e in w.public_events():
            m.observe(*e)
        previous=m.snapshot()
        e=w.public_events()[0]
        m.observe(*e)
        self.assertEqual(m.snapshot(),previous)
        m.observe(e[0],e[1],e[2]^1,e[3])
        self.assertEqual(m.fault,1)
        self.assertTrue(all(m.predict_a1(s) is None for s in w.test))

    def test_out_of_order_action1_refuses_to_learn_unexplained_features(self):
        world=PublicWorld(1,3)
        m=GrowingSynapseCircuit()
        m.observe(*world.public_events()[24])
        self.assertEqual(m.fault,1)
        self.assertEqual(m.active_plastic(),1)
        self.assertTrue(all(m.predict_a1(s) is None for s in world.test))

    def test_tampered_checkpoint_fixed_graph_and_plastic_weights_rejected(self):
        world=PublicWorld(7,3)
        m=GrowingSynapseCircuit()
        for e in world.public_events():
            m.observe(*e)
        original=m.snapshot()
        changed=bytearray(original)
        changed[12]^=1
        for bad in (original[:-1],bytes(changed),
                    bytearray(original),b"NOPE"+original[4:]):
            with self.subTest(value=type(bad)),self.assertRaises(ValueError):
                GrowingSynapseCircuit.restore(bad)
        altered=GrowingSynapseCircuit.restore(original)
        altered.weights[SPEC.fixed_indices[0]]+=1
        with self.assertRaises(ValueError):
            GrowingSynapseCircuit.restore(altered.snapshot())
        altered=GrowingSynapseCircuit.restore(original)
        altered.weights[SPEC.plastic_indices[0]]=2
        with self.assertRaises(ValueError):
            GrowingSynapseCircuit.restore(altered.snapshot())

    def test_invalid_input_never_mutates_weight_state(self):
        m=GrowingSynapseCircuit()
        raw=m.snapshot()
        for event in ((999,0,0,1000),(1024,0,0,1000),
                      (True,0,0,1000),(1000,True,0,1000),
                      (1000,2,0,1000),(1000,0,True,1000),
                      (1000,0,0,900)):
            with self.subTest(event=event),self.assertRaises(ValueError):
                m.observe(*event)
            self.assertEqual(m.snapshot(),raw)
        with self.assertRaises(ValueError):
            m.predict_a1(-1)

    def test_isolated_world_learning_never_changes_existing_weight_state(self):
        a,b=GrowingSynapseCircuit(),GrowingSynapseCircuit()
        wa,wb=PublicWorld(4,1),PublicWorld(8,3)
        for e in wa.public_events():
            a.observe(*e)
        original=a.snapshot()
        for e in wb.public_events():
            b.observe(*e)
        self.assertEqual(a.snapshot(),original)
        self.assertNotEqual(a.programmed_sha256(),b.programmed_sha256())
        self.assertEqual((a.depth,b.depth),(1,3))
        self.assertTrue(all(a.predict_a1(s)==wa.outcome(s,1)[2] for s in wa.test))
        self.assertTrue(all(b.predict_a1(s)==wb.outcome(s,1)[2] for s in wb.test))

    def test_fully_trained_comparator_deterministic_and_input_limited(self):
        w=PublicWorld(7,3)
        sym=SymbolicAdaptive()
        for e in w.public_events():
            sym.observe(*e)
        examples=tuple((sym.signature(e[0],3),e[2])
                       for e in w.public_events()[24:])
        a,b=TrainedMLP(),TrainedMLP()
        a.fit(examples)
        b.fit(examples)
        self.assertTrue(math.isfinite(a.loss))
        self.assertEqual((a.loss,a.steps,a.converged),
                         (b.loss,b.steps,b.converged))
        self.assertEqual(a.w,b.w)
        self.assertEqual(a.converged,a.loss<=0.02)
        with self.assertRaises(ValueError):
            TrainedMLP().fit(examples[:-1])

    def test_generic_neuron_vm_does_not_use_class_or_depth_program_dispatch(self):
        raw=(ROOT/"graph.py").read_text("utf-8")
        start=raw.index("class UniformVM:")
        end=raw.index("def encode(",start)
        vm=raw[start:end]
        self.assertNotIn("if mode",vm)
        self.assertNotIn("if depth",vm)
        self.assertNotIn("if action",vm)
        self.assertNotIn("if reward",vm)
        self.assertNotIn("PublicWorld",vm)
        self.assertNotIn("if op ==",vm)
        self.assertEqual(len(SPEC.rules),747)


if __name__=="__main__":
    unittest.main()
