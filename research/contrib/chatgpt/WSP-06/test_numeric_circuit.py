"""WSP-06 public DEV tests: raw-event numerical circuit vs independent controls."""
from __future__ import annotations

import hashlib
import pathlib
import sys
import unittest

from numeric_circuit import (
    N, PLASTIC_SHAPES, PLASTIC_COUNT, FIXED_COUNT,
    FIXED_SIGNATURE, FIXED_ROUTE, READ_TAPE, LEARN_TAPE, PROGRAM_SHA256,
    NumericalTape, CompleteTaskCircuit,
)

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "WSP-05"))
from causal_signature import (PublicWorld, ExactSymbolicSignature,
                              TrainedMLPControl, SEEDS)

PROTOCOL_BLOB = "3d7b09700f476b7464e9392d7c2ad9bd2f15bec0"


class WSP06Tests(unittest.TestCase):
    def test_protocol_frozen_and_all_matrix_weights_custodied(self):
        contents = (ROOT / "protocol.json").read_bytes().replace(b"\r\n",b"\n")
        blob = b"blob " + str(len(contents)).encode() + b"\0" + contents
        self.assertEqual(hashlib.sha1(blob).hexdigest(), PROTOCOL_BLOB)
        self.assertEqual(N,12)
        self.assertEqual(PLASTIC_COUNT,177)
        self.assertEqual(FIXED_COUNT,16)
        self.assertEqual(CompleteTaskCircuit.GRADIENT_STEPS,0)
        self.assertEqual(len(PROGRAM_SHA256),64)
        m = CompleteTaskCircuit()
        self.assertEqual(m.weights["SIG"],FIXED_SIGNATURE)
        self.assertEqual(m.weights["ROUTE"],FIXED_ROUTE)
        self.assertEqual(set(m.weights),
                         set(PLASTIC_SHAPES) | {"SIG","ROUTE"})
        for name,(rows,cols) in PLASTIC_SHAPES.items():
            self.assertEqual((len(m.weights[name]),len(m.weights[name][0])),
                             (rows,cols))
            self.assertTrue(all(not x for row in m.weights[name] for x in row))

    def test_four_signature_neurons_decode_only_numeric_inputs(self):
        model = CompleteTaskCircuit()
        for first in (0,1):
            for second in (0,1):
                out = NumericalTape.run(
                    (("dot","scores","SIG","x"),
                     ("threshold","sig","scores",1.5)),
                    model.weights,{"x":[first,second,1]})
                self.assertEqual(out["sig"],
                                 [int(i == 2*first+second) for i in range(4)])

    def test_all_32_worlds_complete_causal_task_from_raw_events(self):
        count = restores = replay = new_synapses = 0
        for seed in SEEDS:
            world = PublicWorld(seed)
            network,control = CompleteTaskCircuit(),ExactSymbolicSignature()
            events = world.public_experiences()
            self.assertEqual(len(events),20)
            for event in events:
                network.observe(*event)
                control.observe(*event)
            self.assertEqual(sum(sum(row) for row in network.weights["C0"]),12)
            self.assertEqual(sum(sum(row) for row in network.weights["T0"]),12)
            self.assertEqual(sum(sum(row) for row in network.weights["C1"]),4)
            self.assertEqual(network.weights["F"],[[0]])
            new_synapses += network.learned_positive_synapses()
            snapshot = network.snapshot()
            recovered = CompleteTaskCircuit.restore(snapshot)
            self.assertEqual(recovered.programmed_sha256(),
                             network.programmed_sha256())
            restores += recovered.snapshot() == snapshot
            for e in (events[0],events[11],events[12],events[-1]):
                recovered.observe(*e)
            replay += recovered.snapshot() == snapshot
            for state in world.test:
                target = world.outcome(state,1)[2]
                self.assertEqual(network.predict_a1(state), target)
                self.assertEqual(recovered.predict_a1(state), target)
                self.assertEqual(control.predict_a1(state), target)
                count += 1
        self.assertEqual((count,restores,replay), (128,32,32))
        self.assertGreater(new_synapses,0)

    def test_core_weight_ablations_block_memory_and_inference(self):
        w = PublicWorld(17)
        m = CompleteTaskCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        self.assertTrue(all(m.predict_a1(s) is not None for s in w.test))
        no_transition = CompleteTaskCircuit.restore(m.snapshot())
        no_transition.weights["T0"] = [[0]*12 for _ in range(12)]
        self.assertTrue(all(no_transition.predict_a1(s) is None for s in w.test))
        no_signature = CompleteTaskCircuit.restore(m.snapshot())
        no_signature.weights["SIG"] = [[0,0,0] for _ in range(4)]
        self.assertTrue(all(no_signature.predict_a1(s) is None for s in w.test))
        no_reward = CompleteTaskCircuit.restore(m.snapshot())
        no_reward.weights["C1"] = [[0]*4]
        self.assertTrue(all(no_reward.predict_a1(s) is None for s in w.test))
        empty = CompleteTaskCircuit()
        self.assertTrue(all(empty.predict_a1(s) is None for s in w.test))

    def test_learning_requires_public_consequences_and_not_hidden_class(self):
        w = PublicWorld(11)
        m = CompleteTaskCircuit()
        events = w.public_experiences()
        before = m.snapshot()
        with self.assertRaises(ValueError):
            m.observe(*events[12])
        self.assertEqual(m.snapshot(),before)
        for event in events[:12]:
            m.observe(*event)
        self.assertTrue(all(m.predict_a1(s) is None for s in w.test))
        self.assertEqual(m.weights["C1"],[[0,0,0,0]])
        for event in events[12:]:
            m.observe(*event)
        self.assertEqual(m.weights["C1"],[[1,1,1,1]])
        self.assertTrue(all(m.predict_a1(s) is not None for s in w.test))

    def test_unknown_hidden_reward_shift_is_detected_not_learned(self):
        wrong = abstain = 0
        for seed in SEEDS:
            w = PublicWorld(seed)
            m = CompleteTaskCircuit()
            for event in w.public_experiences():
                m.observe(*event)
            for s in w.test:
                prediction = m.predict_a1(s)
                self.assertIsNotNone(prediction)
                self.assertNotEqual(prediction,
                                    w.outcome(s,1,heldout_shift=True)[2])
                wrong += 1
            m.observe(*w.outcome(w.test[0],1,heldout_shift=True))
            self.assertEqual(m.weights["F"],[[1]])
            self.assertEqual(m.weights["C1"],[[1,1,1,1]])
            for s in w.test:
                self.assertIsNone(m.predict_a1(s))
                abstain += 1
            self.assertEqual(CompleteTaskCircuit.restore(m.snapshot()).weights["F"],
                             [[1]])
        self.assertEqual((wrong,abstain),(128,128))

    def test_repeated_observation_conflict_sets_numeric_fault(self):
        w=PublicWorld(7)
        m=CompleteTaskCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        e=w.public_experiences()[0]
        m.observe(e[0],e[1],e[2]^1,e[3])
        self.assertEqual(m.weights["F"],[[1]])
        self.assertIsNone(m.predict_a1(w.test[0]))
        self.assertEqual(CompleteTaskCircuit.restore(m.snapshot()).weights["F"],
                         [[1]])

    def test_cold_checkpoint_rejects_integrity_fixed_weight_or_shape_damage(self):
        w=PublicWorld(4)
        m=CompleteTaskCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        raw=m.snapshot()
        altered=bytearray(raw)
        altered[20]^=1
        for b in (raw[:-1],bytes(altered),bytearray(raw),b"MISS"+raw[4:]):
            with self.subTest(value=type(b)),self.assertRaises(ValueError):
                CompleteTaskCircuit.restore(b)
        tamper=CompleteTaskCircuit.restore(raw)
        tamper.weights["SIG"][0][0]+=1
        with self.assertRaises(ValueError):
            CompleteTaskCircuit.restore(tamper.snapshot())
        tamper=CompleteTaskCircuit.restore(raw)
        tamper.weights["T0"][0][0]=2
        with self.assertRaises(ValueError):
            CompleteTaskCircuit.restore(tamper.snapshot())

    def test_malformed_raw_inputs_are_noops(self):
        m=CompleteTaskCircuit()
        before=m.snapshot()
        for e in ((999,0,0,1000),(1012,0,0,1000),
                  (True,0,0,1000),(1000,True,0,1000),
                  (1000,2,0,1000),(1000,0,True,1000),
                  (1000,0,0,2000)):
            with self.subTest(e=e),self.assertRaises(ValueError):
                m.observe(*e)
            self.assertEqual(m.snapshot(),before)
        with self.assertRaises(ValueError):
            m.predict_a1(999)

    def test_independent_environment_has_no_cross_world_mutation(self):
        a,b=CompleteTaskCircuit(),CompleteTaskCircuit()
        wa,wb=PublicWorld(8),PublicWorld(9)
        for e in wa.public_experiences():
            a.observe(*e)
        frozen=a.snapshot()
        for e in wb.public_experiences():
            b.observe(*e)
        self.assertEqual(a.snapshot(),frozen)
        self.assertNotEqual(a.programmed_sha256(),b.programmed_sha256())
        self.assertTrue(all(a.predict_a1(s)==wa.outcome(s,1)[2]
                            for s in wa.test))
        self.assertTrue(all(b.predict_a1(s)==wb.outcome(s,1)[2]
                            for s in wb.test))


if __name__=="__main__":
    unittest.main()
