"""WSP180: developer-only offline public FIT/HELD integrity and scoring."""
from __future__ import annotations

import ast
import copy
from pathlib import Path
import unittest

from public_boundary import PublicEvidence
from offline_compare import PublicRow, evaluate

POS = ((0, 0), (0, 4), (4, 0), (4, 4), (2, 2))


def scene(colors):
    return tuple((x, y, color) for (x, y), color in zip(POS, colors))


def row(identifier, action=10, target3=4, current3=3):
    old = scene((0, 1, 2, current3, 4))
    goal = scene((0, 1, 0, 3, 4))
    new = scene((0, 1, 0, target3, 4))
    reward = sum(x[2] == g[2] for x, g in zip(new, goal)) / 5
    return PublicRow(identifier, PublicEvidence(
        current=old, goal=goal, action=action,
        next=new, reward=reward, done=False))


def row_no_desc(identifier):
    return PublicRow(identifier, PublicEvidence(
        current=scene((0, 1, 2, 3, 0)),
        goal=scene((0, 1, 2, 3, 0)),
        action=24, next=scene((0, 1, 2, 3, 4)), reward=0.8, done=False))


class OfflineComparisonTests(unittest.TestCase):
    def test_offline_benchmark_is_never_science_go(self):
        result = evaluate([row("fit01")], [row("held01")])
        self.assertEqual(result["fit_events"], 1)
        self.assertEqual(result["held_events"], 1)
        self.assertEqual(result["held_scored_actions"], 1)
        self.assertEqual(result["held_potential_downstream_slots"], 2)
        self.assertEqual(result["held_zero_descendant_actions"], 0)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["attested_source_origin"])
        self.assertFalse(result["owner_source_lease_qualified"])
        self.assertFalse(result["full_conventional_control_qualified"])
        self.assertFalse(result["old_law_retention_tested"])
        self.assertFalse(result["unfamiliar_family_transfer_tested"])
        self.assertEqual(result["original_source_actions_this_call"], 0)
        self.assertIn("DEV_ONLY", result["status"])

    def test_denominator_is_object_slots_not_episodes(self):
        # One 2-descendant event and one 0-descendant event: exactly 2
        # scored slots, never a spurious perfect score from action=24.
        result = evaluate([row("fit-a")],
                          [row("held-a"), row_no_desc("held-b")])
        self.assertEqual(result["held_events"], 2)
        self.assertEqual(result["held_scored_actions"], 1)
        self.assertEqual(result["held_zero_descendant_actions"], 1)
        self.assertEqual(result["held_potential_downstream_slots"], 2)
        self.assertGreater(result["brier_per_potential_downstream_object"]["identity"], 0)

    def test_no_evidence_produces_no_claim_or_score(self):
        with self.assertRaisesRegex(ValueError, "NO_SCORED_DESCENDANTS"):
            evaluate([row("fit")], [row_no_desc("held")])
        for a, b in (([], [row("held")]), ([row("fit")], []),
                     ("not rows", [row("held")])):
            with self.assertRaises(ValueError):
                evaluate(a, b)

    def test_duplicate_owner_event_ids_never_reused(self):
        e = row("evt1")
        for fit, held in (([e, e], [row("evt2")]), ([e], [e]),
                          ([e], [row("evt1", target3=3)])):
            with self.assertRaisesRegex(ValueError, "EVENT_ID_REUSE"):
                evaluate(fit, held)

    def test_repeated_stochastic_outcome_content_is_not_false_replay(self):
        # Two distinct actor event IDs may encode identical legitimate
        # observations. A content digest is NOT source-consumption identity.
        a, b = row("fit-identical"), row("held-identical")
        self.assertEqual(a.evidence.sha256(), b.evidence.sha256())
        result = evaluate([a], [b])
        self.assertNotEqual(result["fit_rows_digest"], result["held_rows_digest"])

    def test_pretrained_control_is_fit_only_no_held_update(self):
        fit = [row("fit-one", target3=3), row("fit-two", target3=4)]
        held = [row("held-one", target3=4),
                row("held-two", target3=3)]
        baseline = evaluate(fit, held)
        changed = evaluate(fit, [row("held-three", target3=0)])
        self.assertEqual(baseline["fit_summary"], changed["fit_summary"])
        self.assertNotEqual(baseline["held_rows_digest"], changed["held_rows_digest"])
        self.assertEqual(baseline["fit_rows_digest"], changed["fit_rows_digest"])

    def test_conventional_context_sensitivity_negative_control(self):
        fit = [row("fit-a", current3=3, target3=4),
               row("fit-b", current3=4, target3=3)]
        held = [row("held", current3=3, target3=4)]
        r = evaluate(fit, held)
        self.assertLess(r["brier_per_potential_downstream_object"]["categorical_conditional"],
                        r["brier_per_potential_downstream_object"]["direct_programmed"])
        self.assertGreater(r["direct_minus_best_restricted_control"], 0)

    def test_data_and_score_are_deterministic_and_unmodified(self):
        fit = [row("fit1"), row("fit2", target3=3)]
        held = [row("held1"), row("held2", target3=3)]
        input_identities = [x.evidence.sha256() for x in fit + held]
        a = evaluate(fit, held)
        b = evaluate(tuple(fit), tuple(held))
        self.assertEqual(a, b)
        self.assertEqual(input_identities, [x.evidence.sha256() for x in fit + held])
        self.assertEqual(a["brier_per_potential_downstream_object"].keys(),
                         {"direct_programmed", "categorical_conditional", "identity", "uniform"})

    def test_public_row_metadata_is_restricted(self):
        for ident in ("", "bad space", "🙂", "a" * 129, "../abc", "\\hidden"):
            with self.subTest(ident=ident), self.assertRaisesRegex(ValueError, "EVENT_ID"):
                PublicRow(ident, row("v").evidence)
        with self.assertRaisesRegex(ValueError, "PUBLIC_EVIDENCE"):
            PublicRow("id", {"source_graph": "secret"})
        with self.assertRaisesRegex(ValueError, "ROW_TYPE"):
            evaluate([row("fit")], [{"event_id": "held"}])

    def test_only_source_free_imports(self):
        content = Path(__file__).with_name("offline_compare.py").read_text("utf-8")
        tree = ast.parse(content)
        names = {x.name.partition(".")[0] for n in ast.walk(tree)
                 if isinstance(n, ast.Import) for x in n.names}
        names |= {n.module.partition(".")[0] for n in ast.walk(tree)
                  if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(names & {"numpy", "torch", "gym", "causal_gym"})
        self.assertNotIn("source_env.reset", content)
        self.assertNotIn("source_env.step", content)
        self.assertNotIn("source_first_use_authority", content)


if __name__ == "__main__":
    unittest.main()
