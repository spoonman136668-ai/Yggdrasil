"""Typed native property/relationship join and cold persistence mechanics."""
import json
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_property_knowledge import NativePropertyKnowledge


def properties():
    rows = [[entity, bit, (entity >> bit) & 1] for entity in range(8) for bit in range(3)]
    return NativePropertyKnowledge("fixture", entities=8, context_bits=3).stage_properties(
        rows, digest(canonical(rows)), source_namespace="fixture")


def learned():
    model = properties()
    rows = [[entity, 1, int(entity.bit_count() >= 2)] for entity in range(7)]
    return model.stage_relation(0, rows, digest(canonical(rows)), source_namespace="fixture")


class NativePropertyKnowledgeTests(unittest.TestCase):
    def test_positive_and_negative_facts_are_explicit_native_state(self):
        model = properties()
        self.assertEqual(model.property_count, 24)
        self.assertEqual(model._known[0], 7)
        self.assertEqual(model._values[0], 0)
        self.assertEqual(model._values[7], 7)

    def test_unseen_entity_consequence_uses_learned_relationship(self):
        model = learned()
        self.assertEqual(model.predict_entity(0, 7, 1), 1)
        self.assertIsNone(model.predict_entity(0, 7, 0))
        self.assertIsNone(model.predict_entity(0, 7, 1, visible_mask=0))

    def test_incomplete_training_context_is_not_filled_with_false_values(self):
        model = NativePropertyKnowledge("fixture", entities=8, context_bits=3)
        rows = [[0, 0, 1]]
        model = model.stage_properties(rows, digest(canonical(rows)), source_namespace="fixture")
        observation = [[0, 1, 1]]; frozen = model.checkpoint()
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_TRAINING_CONTEXT"):
            model.stage_relation(0, observation, digest(canonical(observation)), source_namespace="fixture")
        self.assertEqual(model.checkpoint(), frozen)

    def test_namespaces_original_modes_and_historical_labels_are_refused(self):
        model = properties(); frozen = model.checkpoint(); rows = [[0, 1, 1]]
        for kwargs in ({"source_namespace": "different"},
                       {"source_namespace": "fixture", "source_mode": "original_source"},
                       {"source_namespace": "fixture", "source_kind": "historical_QPQ"}):
            with self.assertRaises(ValueError):
                model.stage_relation(0, rows, digest(canonical(rows)), **kwargs)
        self.assertEqual(model.checkpoint(), frozen)

    def test_conflicting_or_malformed_properties_cannot_partially_overwrite(self):
        model = properties(); frozen = model.checkpoint()
        for rows in ([[0, 0, 1]], [[0, 0, 0], [True, 1, 1]], [[0, 3, 0]]):
            with self.assertRaises(ValueError):
                model.stage_properties(rows, digest(canonical(rows)), source_namespace="fixture")
        self.assertEqual(model.checkpoint(), frozen)

    def test_exact_property_replay_does_not_inflate_knowledge(self):
        rows = [[entity, bit, (entity >> bit) & 1] for entity in range(8) for bit in range(3)]
        model = properties()
        replay = model.stage_properties(rows, digest(canonical(rows)), source_namespace="fixture")
        self.assertIs(replay, model)
        self.assertEqual(replay.property_count, 24)

    def test_subsequent_relation_learning_preserves_facts_and_older_answers(self):
        model = learned(); frozen = model.checkpoint()
        answers = [model.predict_entity(0, e, 1) for e in range(8)]
        rows = [[entity, 1, entity & 1] for entity in range(7)]
        after = model.stage_relation(1, rows, digest(canonical(rows)), source_namespace="fixture")
        self.assertEqual(answers, [after.predict_entity(0, e, 1) for e in range(8)])
        self.assertEqual(after._known, model._known)
        self.assertEqual(after._values, model._values)
        self.assertEqual(model.checkpoint(), frozen)

    def test_cold_complete_model_and_semantic_flags_are_verified(self):
        model = learned(); raw = model.checkpoint()
        cold = NativePropertyKnowledge.restore(raw, digest(raw))
        self.assertEqual(cold.property_count, 24)
        self.assertEqual(cold.predict_entity(0, 7, 1), 1)
        self.assertEqual(cold.checkpoint(), raw)
        with self.assertRaises(ValueError):
            NativePropertyKnowledge.restore(raw, "0" * 64)
        for flag in ("accepted_native", "scientific_pass"):
            d = json.loads(raw); d[flag] = True; altered = canonical(d)
            with self.assertRaises(ValueError):
                NativePropertyKnowledge.restore(altered, digest(altered))


if __name__ == "__main__": unittest.main()
