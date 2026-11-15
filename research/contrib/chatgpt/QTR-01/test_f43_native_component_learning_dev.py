"""F43: authentic existing native-cell actions, exact F42 graph router and controls."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from f26_semantic_association import NotAdmitted
from f42_exact_index_dev import ExactIndex, source_facts
from f43_native_component_learning_dev import (
    PREREG,SCHEMA,TRAIN_ROOTS,RESERVED,FROZEN_PREF,FROZEN_F42_SHA,
    ConventionalCounts,preregistration,graph_contexts,route_entity,
    query_known_entities,outcome,run
)
from yggdrasil.public_causal_cells import PublicCausalCells


class F43KnownComponentLearning(unittest.TestCase):
    def test_frozen_before_first_learning_and_exhaustive_fences(self):
        p=preregistration()
        self.assertEqual(p["schema"],SCHEMA)
        self.assertEqual(p["source_exact_parent"],
                         "9ee47d2fa569e0f1cec772fce50ef75fb44cee2e")
        self.assertEqual(p["input_graph"]["known_graph_entity_holdouts"],71)
        self.assertEqual(p["native"]["training_public_outcome_law_by_component_slot"],
                         list(FROZEN_PREF))
        self.assertEqual(p["frozen_metrics"]["native_advantage_over_equal_information_conventional_min"],1)
        self.assertIs(p["frozen_metrics"]["strict_scientific_gain_expected"],False)
        self.assertTrue(all(x is True for x in p["fences"].values()))

    def test_contract_tampering_cannot_change_thresholds(self):
        original=json.loads(PREREG.read_text(encoding="utf-8"))
        original["frozen_metrics"]["native_advantage_over_equal_information_conventional_min"]=0
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"changed.json"
            f.write_text(json.dumps(original),encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted,"F43_PREREG_GIT_BLOB_DRIFT"):
                preregistration(f)

    def test_real_f42_archive_component_sizes_and_no_heldout_source(self):
        route,trainees,holdout,sizes,snapshot=graph_contexts()
        self.assertEqual(trainees,TRAIN_ROOTS)
        self.assertEqual(sizes,(5,22,5,23,7,8,8))
        self.assertEqual(len(holdout),71)
        self.assertEqual(len(route),78)
        self.assertEqual(len(snapshot),630)
        self.assertEqual(sha256(snapshot).hexdigest(),FROZEN_F42_SHA)
        self.assertFalse(set(holdout)&set(trainees))
        self.assertFalse(RESERVED&set(route))

    def test_reserved_and_unseen_entity_fails_closed(self):
        route,*_=graph_contexts()
        for qid in (*RESERVED,"Q987654321","Q0","Q","P2",2,None):
            with self.subTest(qid=qid),self.assertRaisesRegex(
                NotAdmitted,"F43_UNSEEN_OR_RESERVED_ENTITY_NOT_ADMITTED"):
                route_entity(route,qid)

    def test_real_native_abstains_on_missing_action_intervention(self):
        model=PublicCausalCells()
        self.assertIsNone(model.choose(0))
        for _ in range(4):
            model.observe(0,0,1)
        self.assertIsNone(model.choose(0))
        for _ in range(4):
            model.observe(0,1,0)
        self.assertEqual(model.choose(0),0)
        self.assertIsNone(model.choose(0,retained=True))
        self.assertIsNone(model.choose(1))

    def test_empirical_control_is_equal_learned_byte_budget_and_public_input(self):
        ctl=ConventionalCounts()
        native=PublicCausalCells()
        self.assertEqual(len(ctl.learned_state()),128)
        for i in range(7):
            for action in (0,1):
                for _ in range(4):
                    result=outcome(action,FROZEN_PREF[i])
                    ctl.observe(i,action,result)
                    native.observe(i,action,result)
        self.assertEqual(tuple(ctl.choose(i) for i in range(7)),
                         tuple(native.choose(i) for i in range(7)))
        self.assertEqual(len(ctl.learned_state()),128)
        self.assertEqual(native.LEARNED_BYTES,128)

    def test_wrong_component_routing_breaks_known_node_predictions(self):
        route,trainees,targets,*_=graph_contexts()
        model=PublicCausalCells()
        for i in range(7):
            for action in (0,1):
                for _ in range(4):
                    model.observe(i,action,outcome(action,FROZEN_PREF[i]))
        matched=query_known_entities(model,route,targets)
        misrouted=query_known_entities(model,route,targets,shift=1)
        self.assertEqual(matched,{"queries":71,"covered":71,"correct":71,"wrong":0,"abstained":0})
        self.assertEqual(misrouted["covered"],71)
        self.assertLess(misrouted["correct"],71)
        self.assertGreater(misrouted["wrong"],0)

    def test_full_cold_restore_survives_retained_interference(self):
        model=PublicCausalCells()
        for i in range(7):
            for action in (0,1):
                model.observe(i,action,outcome(action,FROZEN_PREF[i]))
        prior=tuple(model.choose(i) for i in range(7))
        checkpoint=model.snapshot()
        for i in range(9):
            for action in (0,1):
                model.observe(i,action,outcome(action,(i+1)%2),retained=True)
        self.assertEqual(tuple(model.choose(i) for i in range(7)),prior)
        self.assertNotEqual(model.snapshot(),checkpoint)
        self.assertEqual(model.snapshot(),PublicCausalCells.restore(model.snapshot()).snapshot())

    def test_corrupted_f42_graph_or_native_checkpoint_rejected(self):
        qids,pids,old,new=source_facts()
        src=ExactIndex(qids,pids)
        for item in old+new:src.insert(item)
        a=src.snapshot()
        for sample,decoder in [
            (a[:-1],ExactIndex.restore),
            (a[:-1]+bytes([a[-1]^1]),ExactIndex.restore),
            (PublicCausalCells().snapshot()[:-1],PublicCausalCells.restore)
        ]:
            with self.subTest(size=len(sample)),self.assertRaises((NotAdmitted,ValueError)):
                decoder(sample)

    def test_negative_wrong_training_inputs_do_not_mutate_control(self):
        ctl=ConventionalCounts()
        prior=ctl.learned_state()
        for args in [
            (7,0,0,False),(9,1,1,True),(0,2,1,False),
            (0,1,2,False),(True,1,1,False)
        ]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                ctl.observe(*args[:3],retained=args[3])
            self.assertEqual(ctl.learned_state(),prior)

    def test_frozen_native_public_learning_and_strong_control_no_advantage(self):
        d=run()
        self.assertEqual(d["classification"],"DEV_NATIVE_ROUTING_PARITY_ONLY")
        self.assertEqual(d["source_triples"],82)
        self.assertEqual(d["graph_entities"],78)
        self.assertEqual(d["components"],7)
        self.assertEqual(d["query_graph_entities_heldout_from_actions"],71)
        self.assertEqual(d["total_observed_action_consequence_events"],128)
        self.assertEqual(d["public_train_events"],56)
        self.assertEqual(d["retained_interference_events"],72)
        self.assertEqual(d["native_learned_bytes"],d["conventional_learned_bytes"])
        self.assertEqual(d["native_learned_bytes"],128)
        self.assertEqual(d["native_checkpoint_bytes"],164)
        self.assertEqual(d["graph_serialized_bytes"],630)
        self.assertEqual(d["native_and_exact_graph_snapshot_bytes"],794)
        for k in ("native_warm_known_component_entity_queries",
                  "native_cold_known_component_entity_queries",
                  "native_after_retained_interference",
                  "equal_information_trained_conventional"):
            self.assertEqual(d[k],{"queries":71,"covered":71,"correct":71,"wrong":0,"abstained":0})
        self.assertEqual(d["identity_only_source_heldout_coverage"],0)
        self.assertEqual(d["exact_symbolic_observed_action_rule_correct"],71)
        self.assertLess(d["wrong_component_mapping_negative"]["correct"],71)
        self.assertIs(d["native_and_conventional_predictions_identical"],True)
        self.assertIs(d["scientific_pass"],False)
        self.assertIs(d["transfer_to_new_source_graph"],False)
        self.assertIs(d["protected_scientific_first_use_consumed"],False)
        self.assertEqual(d["external_source_requests"],0)

    def test_source_known_synthetic_environment_not_generalization(self):
        report=run()
        self.assertIs(report["known_source_graph_unseen_externally"],False)
        self.assertIs(report["learned_graph_relations_natively"],False)
        self.assertIs(report["native_accepted_source_modified"],False)
        self.assertIs(report["fully_trained_conventional_comparison_performed"],True)
        self.assertEqual(report["new_scheduled_tasks"],0)


if __name__=="__main__":
    unittest.main()
