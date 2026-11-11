"""WSP-14 frozen controls: synthesis, information impossibility and custody."""
import hashlib
import json
import unittest

from nand_program import (MAX_NANDS, OBSERVED, HIDDEN, GRADIENT_STEPS_DIRECT,
                          MAGIC, NumericNand, bits, catalog, synthesize,
                          symbolic_eval, observed_world, fully_train_8hot,
                          trained_predict)


class WSP14Tests(unittest.TestCase):
    def test_nand_tree_catalog_complete_within_frozen_budget(self):
        programs = catalog()
        self.assertEqual(len(programs), 256)
        self.assertLessEqual(max(k for k,_ in programs.values()), MAX_NANDS)
        for mask, (gates, program) in programs.items():
            self.assertGreaterEqual(gates, 0)
            self.assertEqual(gates, self._count_gates(program))
            for index in range(8):
                self.assertEqual(symbolic_eval(program, bits(index)),
                                 (mask >> index) & 1)

    def _count_gates(self, node):
        return 0 if node[0] == 0 else (
            1 + self._count_gates(node[1]) + self._count_gates(node[2]))

    def test_public_examples_fit_and_numeric_matches_symbolic(self):
        count = equal = 0
        for target in range(256):
            _cost, _mask, program = synthesize(observed_world(target))
            circuit = NumericNand.from_program(program)
            for i in range(8):
                predicted = circuit.predict(bits(i))
                equal += predicted == symbolic_eval(program,bits(i))
                if i in OBSERVED:
                    count += predicted == (target >> i) & 1
        self.assertEqual((count,equal),(1280,2048))

    def test_exhaustive_unknown_label_bound(self):
        correct = reversed_correct = zero = symbolic_correct = 0
        for target in range(256):
            obs = observed_world(target)
            _, _, program = synthesize(obs)
            circuit = NumericNand.from_program(program)
            for i in HIDDEN:
                truth = (target >> i) & 1
                predicted = circuit.predict(bits(i))
                correct += predicted == truth
                symbolic_correct += symbolic_eval(program,bits(i)) == truth
                reversed_correct += predicted != truth
                zero += truth == 0
        self.assertEqual((correct,symbolic_correct,reversed_correct,zero),
                         (384,384,384,384))

    def test_adam_8hot_trained_to_convergence_all_public_signatures(self):
        converged = set()
        correct = 0
        for target in range(256):
            obs = observed_world(target)
            weights, steps, bce = fully_train_8hot(obs)
            self.assertLessEqual(bce,0.02)
            self.assertLessEqual(steps,2048)
            converged.add(tuple(y for _,y in obs))
            for i in HIDDEN:
                correct += trained_predict(weights,i)==((target>>i)&1)
        self.assertEqual(len(converged),32)
        self.assertEqual(correct,384)

    def test_numeric_programs_cold_restore_all_worlds(self):
        for target in range(256):
            _, _, program = synthesize(observed_world(target))
            model = NumericNand.from_program(program)
            raw = model.snapshot()
            restored = NumericNand.restore(raw)
            self.assertEqual(raw, restored.snapshot())
            for i in range(8):
                self.assertEqual(model.predict(bits(i)),restored.predict(bits(i)))
        self.assertEqual(GRADIENT_STEPS_DIRECT,0)

    def test_gate_ablation_changes_derived_outputs(self):
        changed = 0
        for target in range(256):
            _, _, program = synthesize(observed_world(target))
            model = NumericNand.from_program(program)
            if model.used == 0:
                continue
            damaged = NumericNand.restore(model.snapshot())
            damaged.weights[damaged.used-1] = [0,0]
            for i in range(8):
                # Deliberately use raw numeric gate evaluator to assay damaged
                # coefficients; canonical checkpoint must reject this lesion.
                def damaged_output(x):
                    vals=list(x)
                    for idx in range(damaged.used):
                        a,b=damaged.sources[idx]
                        w1,w2=damaged.weights[idx]
                        vals.append(int(vals[a]*w1+vals[b]*w2 >= -1))
                    return vals[damaged.output]
                changed += (model.predict(bits(i)) != damaged_output(bits(i)))
            with self.assertRaisesRegex(ValueError,"WSP14_NONCANONICAL_CIRCUIT"):
                damaged.snapshot()
        self.assertGreater(changed,0)

    def test_unprogrammed_and_corrupt_checkpoints_fail_closed(self):
        model=NumericNand()
        with self.assertRaisesRegex(ValueError,"WSP14_UNPROGRAMMED"):
            model.predict(bits(0))
        with self.assertRaisesRegex(ValueError,"WSP14_NONCANONICAL"):
            model.snapshot()
        _, _, program=synthesize(observed_world(255))
        real=NumericNand.from_program(program)
        raw=real.snapshot()
        for bad in (raw[:-1],raw+b"x",raw[:-1]+bytes([raw[-1]^1])):
            with self.assertRaisesRegex(ValueError,"WSP14_CHECKPOINT_REJECTED"):
                NumericNand.restore(bad)

    def test_digest_correct_but_noncanonical_rejected(self):
        _, _, program=synthesize(observed_world(7))
        raw=NumericNand.from_program(program).snapshot()
        data=json.loads(raw[9:-32].decode("ascii"))
        data["weights"][0][0]=0
        body=json.dumps(data,sort_keys=True,separators=(",",":")).encode("ascii")
        prefix=MAGIC+len(body).to_bytes(4,"big")+body
        with self.assertRaisesRegex(ValueError,"WSP14_CHECKPOINT_REJECTED"):
            NumericNand.restore(prefix+hashlib.sha256(prefix).digest())

    def test_strict_exposure_order_and_value_validation(self):
        obs=observed_world(85)
        malformed=([], (), (obs[1],)+obs[1:],
                   tuple((x,True) for x,_ in obs),
                   tuple((list(x),y) for x,y in obs))
        for invalid in malformed:
            with self.assertRaises(ValueError):
                synthesize(invalid)
        with self.assertRaises(ValueError):
            observed_world(True)

    def test_isolated_circuits_and_original_gate_only_vocabulary(self):
        a=NumericNand.from_program(synthesize(observed_world(22))[2])
        b=NumericNand.from_program(synthesize(observed_world(29))[2])
        before=b.snapshot()
        if a.used:
            a.weights[0][0]=0
        self.assertEqual(before,b.snapshot())
        for mask,(cost,tree) in catalog().items():
            def check(node):
                self.assertIn(node[0],(0,1))
                if node[0] == 1:
                    check(node[1])
                    check(node[2])
            check(tree)


if __name__=="__main__":
    unittest.main()
