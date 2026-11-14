"""AAI-07B mechanical tests only, synthetic tiny ledgers, NO science seeds."""
import ast
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("aai07b", HERE/"evaluate.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AAI07BTests(unittest.TestCase):
    def test_disjoint_scientific_splits_without_executing_them(self):
        self.assertEqual([len(m.TRAIN),len(m.DEV),len(m.TRANSFER),
                          len(m.NEGATIVE),len(m.CONTINUATION)],[48,64,64,64,16])
        self.assertTrue(set(m.TRAIN).isdisjoint(m.DEV))
        self.assertTrue(set(m.DEV).isdisjoint(m.TRANSFER))
        self.assertTrue(set(m.NEGATIVE).isdisjoint(m.CONTINUATION))
        self.assertEqual(m.PREREG,"10e0ad453454a0f85eafbda1c8618657979810bd")

    def test_synthetic_learning_without_programmed_match(self):
        self.assertTrue(m.audit())
        k,b=m.CUES
        records=[{"cue":k,"upper":b,"chosen_top":True,"success":False},
                 {"cue":k,"upper":b,"chosen_top":False,"success":True}]
        x=m.DirectAssociation()
        x.learn(records)
        self.assertFalse(x.choose(k,b))
        self.assertEqual(x.dump(),m.DirectAssociation.restore(x.dump()).dump())

    def test_same_information_conventional(self):
        k,b=m.CUES
        data=[{"cue":k,"upper":b,"chosen_top":True,"success":False},
              {"cue":b,"upper":b,"chosen_top":False,"success":False}]
        a=m.DirectAssociation()
        c=m.BetaTable()
        a.learn(data)
        c.learn(data)
        self.assertEqual(m.fixed_predictions(a),m.fixed_predictions(c))

    def test_source_no_hidden_simulator_attribute(self):
        tree=ast.parse((HERE/"evaluate.py").read_text(encoding="utf-8"))
        forbidden=("unwrapped","success_pos","failure_pos","agent_pos","grid","mission")
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr in forbidden
                             for node in ast.walk(tree)))

    def test_serializable_shared_updates(self):
        k,b=m.CUES
        model=m.DirectAssociation()
        model.learn([{"cue":k,"upper":b,"chosen_top":True,"success":False}])
        snapshot=model.dump()
        model.learn([{"cue":b,"upper":k,"chosen_top":True,"success":True}])
        restored=m.DirectAssociation.restore(snapshot)
        self.assertFalse(restored.choose(k,b))
        self.assertFalse(model.choose(k,b))

    def test_paired_bootstrap_protocol(self):
        rows=[{"direct":True,"reactive":False}]*4
        lower,upper=m.ci(rows,"direct","reactive")
        self.assertEqual((lower,upper),(1.0,1.0))
        self.assertEqual(m.BOOTSTRAP,1024)


if __name__=="__main__":
    unittest.main()
