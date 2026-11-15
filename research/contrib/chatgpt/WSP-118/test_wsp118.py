"""WSP-118 source-safe deterministic tests: no reserved/protected worlds."""
from __future__ import annotations

import json
from pathlib import Path
import random
import unittest

import mechanism as m


class WSP118Fixture(unittest.TestCase):
    def test_source_custody_and_nested_foundation(self):
        self.assertEqual(len(m.PUBLIC_SEEDS),24)
        self.assertEqual(len(m.RESERVED_SCIENCE),64)
        self.assertFalse(set(m.PUBLIC_SEEDS)&set(m.RESERVED_SCIENCE))
        self.assertEqual((m.ENTITIES,m.PREDICATES,len(m.TRIPLES)),(64,6,216))
        for bad in (118800,118863,117000,118024,True,1.0):
            with self.subTest(seed=bad),self.assertRaises((PermissionError,ValueError)):
                m.new_public_world(bad)
        world=m.new_public_world(m.PUBLIC_SEEDS[0])
        self.assertEqual(world,m.new_public_world(m.PUBLIC_SEEDS[0]))
        self.assertEqual(len(world.edges),6)
        self.assertEqual(len(world.targets),4)
        self.assertEqual(len(set(world.targets)),4)
        self.assertEqual(len(set(world.sources)),64)
        self.assertEqual(len(world.held_subjects()),24)
        self.assertFalse(set(world.sources[:12])&set(world.held_subjects()))
        previous=set()
        for density in m.DENSITIES:
            graph=world.public_graph(density)
            facts={(rel,s,o) for rel,edges in enumerate(graph)
                   for s,o in edges.items()}
            self.assertTrue(previous.issubset(facts))
            previous=facts
        self.assertEqual(len(world.public_graph(0)[0]),0)
        self.assertEqual(sum(len(x) for x in world.public_graph(256)),384)
        with self.assertRaises(ValueError):
            world.public_graph(63)

    def test_new_third_hop_outside_previous_grammar(self):
        for seed in m.PUBLIC_SEEDS[:8]:
            world=m.new_public_world(seed)
            one_and_two={tuple(world.actual(s,law) for s in range(64))
                         for law in m.SHORT}
            graph=world.public_graph(256)
            for law in world.targets:
                self.assertEqual(len(law),3)
                self.assertNotIn(tuple(world.actual(s,law) for s in range(64)),
                                 one_and_two)
                demo=world.public_examples(law)
                self.assertEqual(len(demo),12)
                actual=m.NumericTripleWeights(graph,256).learn(demo)
                exact=m.ExactSymbolicSynthesizer(graph).learn(demo)
                self.assertEqual(actual.law(),exact.law())
                self.assertEqual(actual.law(),law)
                self.assertEqual(actual.synapses.itemsize,4)
                self.assertEqual(len(actual.synapses)*actual.synapses.itemsize,1728)
                for s in world.held_subjects()[:8]:
                    self.assertEqual(actual.infer(s),world.actual(s,law))
                    self.assertEqual(actual.infer(s),exact.infer(s))

    def test_empty_foundation_and_source_negative(self):
        world=m.new_public_world(118000)
        graph=world.public_graph(0)
        demos=world.public_examples(world.targets[0])
        direct=m.NumericTripleWeights(graph,0).learn(demos)
        exact=m.ExactSymbolicSynthesizer(graph).learn(demos)
        self.assertEqual(direct.acceptable(),())
        self.assertIsNone(direct.infer(world.held_subjects()[0]))
        self.assertIsNone(exact.infer(world.held_subjects()[0]))
        self.assertTrue(all(x==0 for x in direct.synapses))
        with self.assertRaises(ValueError):
            m.visible_walk(graph,65,(0,1,2))
        with self.assertRaises(ValueError):
            m.visible_walk(graph,0,(0,6,2))
        with self.assertRaises(ValueError):
            direct.learn(demos)

    def test_observation_equivalent_laws_abstain(self):
        # Even with a full public foundation: all six primitive maps are
        # identity, so 216 distinct program strings induce the same behavior.
        graph=tuple({s:s for s in range(64)} for _ in range(6))
        demos=tuple((s,s) for s in range(12))
        numeric=m.NumericTripleWeights(graph,256).learn(demos)
        exact=m.ExactSymbolicSynthesizer(graph).learn(demos)
        self.assertEqual(len(numeric.acceptable()),216)
        self.assertEqual(len(exact.solutions),216)
        self.assertIsNone(numeric.law())
        self.assertIsNone(numeric.infer(44))
        self.assertIsNone(exact.infer(44))

    def test_cold_exact_restore_and_tamper_rejected(self):
        w=m.new_public_world(118007)
        g=w.public_graph(192)
        d=m.NumericTripleWeights(g,192).learn(w.public_examples(w.targets[1]))
        packed=d.snapshot()
        restored=m.NumericTripleWeights.restore(g,packed)
        self.assertEqual(packed,restored.snapshot())
        self.assertEqual([d.infer(s) for s in w.held_subjects()],
                         [restored.infer(s) for s in w.held_subjects()])
        corrupt=bytearray(packed);corrupt[73]^=1
        with self.assertRaises(ValueError):
            m.NumericTripleWeights.restore(g,bytes(corrupt))
        with self.assertRaises(ValueError):
            m.NumericTripleWeights.restore(g,b"W118")
        with self.assertRaises(ValueError):
            m.NumericTripleWeights(g,250)

    def test_no_shortcut_negative_and_no_held_label_training(self):
        w=m.new_public_world(118005)
        law=w.targets[0]
        demos=w.public_examples(law)
        shuffled=m.shuffled_examples(demos,w.seed,0)
        self.assertEqual(tuple(s for s,_ in demos),tuple(s for s,_ in shuffled))
        self.assertNotEqual(demos,shuffled)
        self.assertEqual(shuffled,m.shuffled_examples(demos,w.seed,0))
        self.assertFalse(set(s for s,_ in demos)&set(w.held_subjects()))
        with self.assertRaises(ValueError):
            m.examples_guard(((0,1),(0,2)))
        with self.assertRaises(ValueError):
            m.examples_guard(tuple((x,x) for x in range(13)))
        with self.assertRaises(ValueError):
            m.examples_guard(((-1,1),))
        with self.assertRaises(ValueError):
            m.examples_guard(tuple())

    def test_prereg_immutable_limits_and_no_real_source(self):
        base=Path(__file__).resolve().parent
        p=json.loads((base/"prereg.json").read_text(encoding="utf-8"))
        self.assertEqual(p["experiment_id"],"WSP-118")
        self.assertEqual(p["fixture"]["seeds"],"118000..118023 inclusive 24 worlds")
        self.assertFalse(p["authority"]["scientific_first_use"])
        self.assertEqual(len(p["fixture"]["tiers"]),len(m.DENSITIES))
        self.assertEqual(tuple(x["byte_threshold"] for x in p["fixture"]["tiers"]),
                         m.DENSITIES)
        source=(base/"mechanism.py").read_text(encoding="utf-8")
        self.assertNotIn("env.unwrapped",source)
        self.assertNotIn("Wikidata5M",source)
        self.assertFalse(any(seed in m.PUBLIC_SEEDS for seed in m.RESERVED_SCIENCE))


if __name__=="__main__":
    unittest.main()
