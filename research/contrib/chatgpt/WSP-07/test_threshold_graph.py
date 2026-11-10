"""WSP-07: fixed protocol; test neural control as actual numeric connectivity."""
from __future__ import annotations

import hashlib
import pathlib
import sys
import unittest

from threshold_graph import (
    N_STATES, INPUT_COUNT, PLASTIC_COUNT, MAX_FIXED_WEIGHTS,
    MAX_NEURONS, SPEC, Compiler, UniformNeuronVM, CompiledPlasticCircuit,
    _encode,
)

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "WSP-05"))
sys.path.insert(0, str(ROOT.parent / "WSP-06"))
from causal_signature import (PublicWorld, SEEDS, ExactSymbolicSignature)
from numeric_circuit import CompleteTaskCircuit

PROTOCOL_BLOB = "ab9dc59ec030858d5fe28a4efa6019b5509ed3b3"


class WSP07Tests(unittest.TestCase):
    def test_frozen_protocol_and_compiled_numeric_budgets(self):
        raw = (ROOT / "protocol.json").read_bytes().replace(b"\r\n",b"\n")
        git_blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        self.assertEqual(hashlib.sha1(git_blob).hexdigest(), PROTOCOL_BLOB)
        self.assertEqual((N_STATES,INPUT_COUNT,PLASTIC_COUNT),(12,27,177))
        self.assertEqual(CompiledPlasticCircuit.GRADIENT_STEPS, 0)
        self.assertLessEqual(len(SPEC.fixed_indices),MAX_FIXED_WEIGHTS)
        self.assertLessEqual(len(SPEC.threshold),MAX_NEURONS)
        self.assertEqual(len(SPEC.plastic_indices),177)
        self.assertEqual(len(SPEC.plastic_rules),177)
        self.assertEqual(len(set(x[0] for x in SPEC.plastic_rules)),177)
        self.assertEqual(len(SPEC.initial_weights),
                         len(SPEC.fixed_indices)+len(SPEC.plastic_indices))
        self.assertTrue(all(SPEC.initial_weights[i] == 0
                            for i in SPEC.plastic_indices))
        self.assertEqual(len(SPEC.graph_sha256),64)

    def test_flat_synaptic_graph_acyclic_and_same_numeric_rule_for_all_nodes(self):
        for target,source,coeff in SPEC.edges:
            self.assertTrue(source < target)
            self.assertGreaterEqual(target,INPUT_COUNT)
            self.assertTrue(0 <= coeff < len(SPEC.initial_weights))
        m=CompiledPlasticCircuit()
        z=_encode(1000)
        activities=UniformNeuronVM.evaluate(SPEC,m.weights,z)
        self.assertEqual(len(activities),len(SPEC.threshold))
        self.assertEqual(activities[SPEC.output_fault],0)
        self.assertEqual(activities[SPEC.output_valid],0)
        self.assertEqual(m.predict_a1(1000),None)

    def test_full_32_worlds_from_raw_events_matches_independent_and_prior(self):
        correct = restores = replays = developed = 0
        for seed in SEEDS:
            world=PublicWorld(seed)
            m=CompiledPlasticCircuit()
            symbolic=ExactSymbolicSignature()
            previous=CompleteTaskCircuit()
            events=world.public_experiences()
            self.assertEqual(len(events),20)
            for event in events:
                m.observe(*event)
                symbolic.observe(*event)
                previous.observe(*event)
            self.assertEqual(m.fault_value(),0)
            self.assertGreater(m.learned_positive_weights(),0)
            developed += 1
            saved=m.snapshot()
            recovered=CompiledPlasticCircuit.restore(saved)
            self.assertEqual(recovered.programmed_sha256(),m.programmed_sha256())
            self.assertEqual(recovered.snapshot(),saved)
            restores += 1
            for event in (events[0],events[11],events[12],events[-1]):
                recovered.observe(*event)
            self.assertEqual(recovered.snapshot(),saved)
            replays += 1
            for state in world.test:
                truth=world.outcome(state,1)[2]
                self.assertEqual(m.predict_a1(state),truth)
                self.assertEqual(recovered.predict_a1(state),truth)
                self.assertEqual(previous.predict_a1(state),truth)
                self.assertEqual(symbolic.predict_a1(state),truth)
                correct += 1
        self.assertEqual((developed,correct,restores,replays),(32,128,32,32))

    def test_heldout_only_shift_falsifies_confident_inference_before_witness(self):
        confident_errors=abstained=0
        for seed in SEEDS:
            w=PublicWorld(seed)
            m=CompiledPlasticCircuit()
            for e in w.public_experiences():
                m.observe(*e)
            for s in w.test:
                original=m.predict_a1(s)
                self.assertIsNotNone(original)
                self.assertNotEqual(original,w.outcome(s,1,heldout_shift=True)[2])
                confident_errors += 1
            m.observe(*w.outcome(w.test[0],1,heldout_shift=True))
            self.assertEqual(m.fault_value(),1)
            for s in w.test:
                self.assertIsNone(m.predict_a1(s))
                abstained += 1
            self.assertEqual(CompiledPlasticCircuit.restore(m.snapshot()).fault_value(),1)
        self.assertEqual((confident_errors,abstained),(128,128))

    def test_ablation_of_real_synaptic_memories_causes_abstention(self):
        w=PublicWorld(9)
        m=CompiledPlasticCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        self.assertTrue(all(m.predict_a1(s) is not None for s in w.test))
        dead_signature=CompiledPlasticCircuit.restore(m.snapshot())
        for slot in SPEC.signature_indices:
            dead_signature.weights[slot]=0
        self.assertTrue(all(dead_signature.predict_a1(s) is None for s in w.test))
        no_transition=CompiledPlasticCircuit.restore(m.snapshot())
        # Exactly 144 distinct initially zeroed transition-memory synapses.
        for slot in SPEC.plastic_indices[:N_STATES*N_STATES]:
            no_transition.weights[slot]=0
        self.assertTrue(all(no_transition.predict_a1(s) is None for s in w.test))
        erased=CompiledPlasticCircuit()
        self.assertTrue(all(erased.predict_a1(s) is None for s in w.test))
        no_coverage=CompiledPlasticCircuit.restore(m.snapshot())
        # Plastic matrices are ordered: T 144, R0 12, C0 12, R1 4, C1 4, F1.
        for slot in SPEC.plastic_indices[172:176]:
            no_coverage.weights[slot]=0
        self.assertTrue(all(no_coverage.predict_a1(s) is None for s in w.test))

    def test_no_basis_action1_sets_numeric_fault_without_spurious_reward_gates(self):
        w=PublicWorld(4)
        m=CompiledPlasticCircuit()
        m.observe(*w.public_experiences()[12])
        self.assertEqual(m.fault_value(),1)
        self.assertEqual(m.learned_positive_weights(),1)
        self.assertTrue(all(m.predict_a1(s) is None for s in w.test))

    def test_repeated_observation_idempotence_and_actual_reward_conflicts(self):
        w=PublicWorld(7)
        m=CompiledPlasticCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        saved=m.snapshot()
        for e in w.public_experiences():
            m.observe(*e)
        self.assertEqual(m.snapshot(),saved)
        e=w.public_experiences()[0]
        m.observe(e[0],e[1],e[2]^1,e[3])
        self.assertEqual(m.fault_value(),1)
        self.assertTrue(all(m.predict_a1(s) is None for s in w.test))

    def test_bad_input_cannot_modify_synapses(self):
        m=CompiledPlasticCircuit()
        original=m.snapshot()
        for args in ((999,0,0,1000),(1012,0,0,1000),
                     (True,0,0,1000),(1000,True,0,1000),
                     (1000,2,0,1000),(1000,0,True,1000),
                     (1000,0,0,999)):
            with self.subTest(case=args),self.assertRaises(ValueError):
                m.observe(*args)
            self.assertEqual(m.snapshot(),original)
        with self.assertRaises(ValueError):
            m.predict_a1(2000)

    def test_checkpoint_integrity_and_fixed_coefficient_tamper_rejected(self):
        w=PublicWorld(6)
        m=CompiledPlasticCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        original=m.snapshot()
        altered=bytearray(original)
        altered[32]^=1
        for damaged in (original[:-1], bytes(altered),
                        bytearray(original),b"BAD7"+original[4:]):
            with self.subTest(type=type(damaged)),self.assertRaises(ValueError):
                CompiledPlasticCircuit.restore(damaged)
        fake=CompiledPlasticCircuit.restore(original)
        fake.weights[SPEC.fixed_indices[0]] += 1
        with self.assertRaises(ValueError):
            CompiledPlasticCircuit.restore(fake.snapshot())
        corrupt=CompiledPlasticCircuit.restore(original)
        corrupt.weights[SPEC.plastic_indices[0]]=2
        with self.assertRaises(ValueError):
            CompiledPlasticCircuit.restore(corrupt.snapshot())

    def test_separate_opaque_worlds_do_not_share_learned_synapses(self):
        a,b=CompiledPlasticCircuit(),CompiledPlasticCircuit()
        wa,wb=PublicWorld(5),PublicWorld(8)
        for e in wa.public_experiences(): a.observe(*e)
        freeze=a.snapshot()
        for e in wb.public_experiences(): b.observe(*e)
        self.assertEqual(a.snapshot(),freeze)
        self.assertNotEqual(a.programmed_sha256(),b.programmed_sha256())
        self.assertTrue(all(a.predict_a1(s)==wa.outcome(s,1)[2]
                            for s in wa.test))
        self.assertTrue(all(b.predict_a1(s)==wb.outcome(s,1)[2]
                            for s in wb.test))

    def test_runtime_has_no_task_specific_opcode_or_symbolic_map(self):
        raw=(ROOT/"threshold_graph.py").read_text("utf-8")
        begin=raw.index("class UniformNeuronVM:")
        end=raw.index("def _encode(",begin)
        vm=raw[begin:end]
        self.assertNotIn("if action",vm)
        self.assertNotIn("if reward",vm)
        self.assertNotIn("if signature",vm)
        self.assertNotIn("if op ==",vm)
        self.assertNotIn("PublicWorld",vm)
        self.assertNotIn("ExactSymbolic",vm)
        self.assertNotIn("dict[tuple[int, int]",vm)
        self.assertEqual(len(SPEC.plastic_rules),177)


if __name__ == "__main__":
    unittest.main()
