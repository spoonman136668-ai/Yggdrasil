"""CB3 public-only frozen feature-gate discovery contract/negative tests."""
from collections import namedtuple
from pathlib import Path
import ast
import unittest

import binding
import gate_binding as m
import public_source as source

class GateDiscoveryTests(unittest.TestCase):
    def test_fenced_new_public_worlds_and_source_is_deterministic(self):
        self.assertEqual(source.WORLDS,tuple(range(82300,82316)))
        for bad in (978500,978600,82316,82300.0,True):
            with self.assertRaises(PermissionError): source.public_training(bad)
        self.assertEqual(source.public_training(82300),source.public_training(82300))

    def test_real_public_delayed_credit_not_present_action(self):
        rows=source.public_training(82300)
        self.assertEqual(len(rows),515)
        for t,row in enumerate(rows):
            credit,_=m._extract(row)
            if t<3: self.assertIsNone(credit); self.assertEqual(row.reward,0)
            else:
                self.assertEqual(credit[1],
                                 row.history[-2].action if row.reward==1
                                 else 1-row.history[-2].action)
                self.assertEqual(row.history[-1].after,row.before)

    def test_public_only_schema_and_atomic_invalid_rejection(self):
        model=m.DiscoveredGateBinder()
        row=source.public_training(82300)[4]
        Extra=namedtuple("Extra",binding.FIELDS+("private_future",))
        for invalid in (Extra(*row,1),row._replace(action=True),
                        row._replace(reward=float("nan")),
                        row._replace(after=(0,)*7),
                        row._replace(history=row.history+(row.history[-1],))):
            with self.assertRaises(ValueError): model.observe_public(invalid)
            self.assertEqual(model._count,0)
            self.assertEqual(len(model._samples),0)

    def test_lexical_pair_search_and_two_stage_public_support(self):
        rows=source.public_training(82300)
        samples=[m._extract(row)[0] for row in rows if m._extract(row)[0] is not None]
        self.assertEqual(len(samples),512)
        global_fit=m._fit_base(samples)
        self.assertLess(global_fit[0]/512,.9)
        gate=m._fit_conditional(samples,global_fit[1],global_fit[2])
        self.assertEqual(gate[0],512)
        self.assertEqual(tuple(sorted(gate[1:3])),source.source_private_feature_pairs(82300)[0])
        self.assertEqual(tuple(sorted(gate[3:5])),source.source_private_feature_pairs(82300)[1])

    def test_equal_information_independent_learner_on_new_contexts(self):
        native,conventional=m.DiscoveredGateBinder(),m.ConventionalExhaustiveFour()
        for row in source.public_training(82300):
            native.observe_public(row);conventional.observe_public(row)
        native.seal();conventional.seal()
        correct=0
        for state,history,target in source.unseen_queries(82300):
            a=native.choose_public(state,history)
            b=conventional.choose_public(state,history)
            self.assertEqual(a,b)
            correct+=a==target
        self.assertEqual(correct,128)

    def test_cold_78_byte_checkpoint_and_corruption(self):
        native=m.DiscoveredGateBinder()
        for row in source.public_training(82300): native.observe_public(row)
        native.seal(); raw=native.snapshot()
        self.assertEqual(len(raw),m.DiscoveredGateBinder.CHECKPOINT_BYTES)
        self.assertLessEqual(len(raw),128)
        cold=m.DiscoveredGateBinder.restore(raw)
        self.assertEqual(cold.snapshot(),raw)
        for state,history,_ in source.unseen_queries(82300):
            self.assertEqual(native.choose_public(state,history),cold.choose_public(state,history))
        wrong=bytearray(raw);wrong[11]^=1
        for case in (bytes(wrong),b"",raw+b" "):
            with self.assertRaises(ValueError): m.DiscoveredGateBinder.restore(case)

    def test_public_budget_and_warmup_do_not_consume_credits(self):
        model=m.DiscoveredGateBinder()
        rows=source.public_training(82300)
        for row in rows: model.observe_public(row)
        self.assertEqual(model._count,512)
        self.assertEqual(len(model._samples),3072)
        with self.assertRaises(ValueError):model.observe_public(rows[-1])
        model.seal()
        self.assertEqual(len(model._samples),0)
        with self.assertRaises(ValueError):model.observe_public(rows[-1])

    def test_candidate_and_symbolic_have_no_source_import_or_private_index(self):
        path=Path(m.__file__)
        tree=ast.parse(path.read_text("utf-8"))
        imported=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): imported.update(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom): imported.add(node.module)
        self.assertNotIn("public_source",imported)
        self.assertNotIn("PRIVATE_CONFIGS",path.read_text("utf-8"))
        self.assertNotIn("_law(",path.read_text("utf-8"))

if __name__=="__main__":
    unittest.main()
