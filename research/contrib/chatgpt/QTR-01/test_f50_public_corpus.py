"""F50 no-target source information parity, lossless graphs and FIT custody."""
import unittest
from unittest.mock import patch

import f50_public_corpus as p
import f50_worlds as w


class F50PublicParityTests(unittest.TestCase):
    def test_lossless_graph_roundtrip_and_onehot_for_every_source_operator(self):
        a,b,c = w.leaf(0),w.leaf(10),w.leaf(30)
        cases = (a, ("not",a), ("and",a,b), ("or",b,c),
                 ("xor",("and",a,b),("not",c)),
                 ("xor",("and",a,a),("and",a,b)))
        for ast in cases:
            with self.subTest(ast=ast):
                graph=p.encode_source_graph(ast)
                self.assertEqual(p.decode_source_graph(graph),ast)
                x,left,right,mask=p.graph_one_hot(graph)
                self.assertEqual(len(x),15)
                self.assertEqual(len(x[0]),38)
                self.assertEqual(len(left),15)
                self.assertEqual(len(right),15)
                self.assertEqual(sum(mask),len(graph.nodes))
                self.assertEqual(graph.root,len(graph.nodes)-1)
                self.assertEqual(sum(sum(row) for row in left),
                                 sum(node[2]>=0 for node in graph.nodes))
                self.assertEqual(sum(sum(row) for row in right),
                                 sum(node[3]>=0 for node in graph.nodes))

    def test_reject_bad_graph_and_noncanonical_edges(self):
        a=p.encode_source_graph(("and",w.leaf(0),w.leaf(10)))
        bad=[
            p.LawGraph(a.nodes[:-1],a.root),
            p.LawGraph(a.nodes,0),
            p.LawGraph(((2,-1,0,0),),0),
            p.LawGraph(((0,99,-1,-1),),0),
            p.LawGraph(((0,0,1,-1),),0),
            p.LawGraph(((99,-1,-1,-1),),0)
        ]
        for record in bad:
            with self.subTest(record=record):
                with self.assertRaises((p.PublicSourceRejected,w.F50Rejected)):
                    p.decode_source_graph(record)
        with self.assertRaises((p.PublicSourceRejected,w.F50Rejected)):
            p.encode_source_graph(("xor",a.nodes,a.nodes))

    def test_all_action_consequence_features_are_exact_3_by_33(self):
        episode=(7,31,63,5)
        arrays=p.action_features(episode)
        self.assertEqual(len(arrays),3)
        self.assertTrue(all(len(x)==33 for x in arrays))
        self.assertEqual(arrays[0][:3],(1,1,1))
        self.assertEqual(arrays[0][10:30],(0,)*20)
        self.assertEqual(arrays[1][10:13],(1,1,1))
        self.assertEqual(arrays[2][20:23],(1,1,1))
        self.assertEqual(arrays[2][30:33],(1,0,1))
        self.assertEqual(len(p.observed_episode(episode,(1,0,1))[1]),3)
        with self.assertRaises(p.PublicSourceRejected):
            p.observed_episode(episode,(True,0,1))
        with self.assertRaises(p.PublicSourceRejected):
            p.observed_episode(episode,(1,0,2))

    def test_fit_only_graphs_and_episodes_never_return_validation_rows(self):
        corpus=p.PublicFIT(1024)
        self.assertEqual(corpus.fit_count,1024*4//5)
        self.assertEqual(corpus.excluded_validation_count,1024-corpus.fit_count)
        a=corpus.ids[0]
        bad=next(iter(w.source_split(1024)[1]))
        graph=corpus.source_graph(a)
        ast=p.decode_source_graph(graph)
        self.assertTrue(w.exact_equal(ast,w.source_bank(1024)[a]))
        records=corpus.source_episodes(a)
        self.assertEqual(len(records),64)
        self.assertEqual(records[0],w.source_training_row(1024,a)[0])
        snapshot=corpus.snapshot(a)
        self.assertEqual(snapshot["graph"],graph.serialize())
        self.assertEqual(len(snapshot["episodes"]),64)
        for selected in (bad,True,-1,1024):
            with self.assertRaises(p.PublicSourceRejected):
                corpus.source_graph(selected)
            with self.assertRaises(p.PublicSourceRejected):
                corpus.source_episodes(selected)

    def test_shared_corpus_provenance_equal_for_independent_arms(self):
        x=p.PublicFIT(1024)
        y=p.PublicFIT(1024)
        frozen=p.assert_equal_source_access(x,y)
        self.assertEqual(len(frozen),64)
        self.assertEqual(frozen,x.digest_for_fit_graphs())
        self.assertEqual(x.snapshot(x.ids[0]),y.snapshot(x.ids[0]))
        with self.assertRaises(p.PublicSourceRejected):
            p.assert_equal_source_access(x,p.PublicFIT(2048))
        with self.assertRaises(p.PublicSourceRejected):
            p.assert_equal_source_access(x,object())

    def test_no_target_namespaces_or_evaluator_outcome_access_in_public_module(self):
        self.assertNotIn("target_ast",p.__dict__)
        self.assertNotIn("target_law",p.__dict__)
        self.assertNotIn("target_observations",p.__dict__)
        self.assertEqual(p.OPCODES,("leaf","not","and","or","xor"))
        with patch.object(w,"sealed_heldout_inputs_for_evaluator_only",
                          side_effect=AssertionError("no evaluator access")):
            corpus=p.PublicFIT(1024)
            self.assertEqual(len(corpus.source_episodes(corpus.ids[0])),64)


if __name__ == "__main__":
    unittest.main()
