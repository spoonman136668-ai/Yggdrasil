"""WSP101 H01: fixed public-transcript symbolic audit, original worlds blocked."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paired_fixture import DEV_CONTEXTS, digits4, observe_world, passive_source
from headroom_h01_symbolic import (
    GRAMMAR, _rows, hidden_candidates, visible_candidates
)

STARTS = (17, 1234)
POLICIES = ((1, 0, 2, 0), (3, 0, 0, 0))


def collect(observer, actions=POLICIES):
    episodes = []
    for start, policy in zip(STARTS, actions):
        current = observer.reset(digits4(start))
        rows = []
        for action in policy:
            result = observer.step(action)
            next_x, reward = result["observation"], result["reward"]
            rows.append((current, action, next_x, reward))
            current = next_x
        episodes.append(tuple(rows))
    return tuple(episodes)


def audit():
    visible_counts = []
    hidden_counts = []
    public_digests = []
    for context in DEV_CONTEXTS:
        passive = passive_source(context, 0)
        assert passive == passive_source(context, 1)
        visible = visible_candidates(passive)
        visible_counts.append(len(visible))
        for mode in (0, 1):
            observed = collect(observe_world(context, mode))
            solutions = hidden_candidates(passive, observed)
            hidden_counts.append(len(solutions))
            # The evaluator may inspect the true mode; the symbolic learner
            # receives only transcripts and never the mode or oracle itself.
            if solutions and not any(candidate[2] == mode for candidate in solutions):
                raise AssertionError("published grammar excludes actual hidden mode")
            public_digests.append(hashlib.sha256(json.dumps(
                {"passive": passive, "active": observed}, sort_keys=True,
                separators=(",", ":"), allow_nan=False
            ).encode("utf-8")).hexdigest())
    if any(c == 0 for c in visible_counts + hidden_counts):
        classification = "DEV_INVALID_GRAMMAR_OR_EVIDENCE"
    elif all(c == 1 for c in visible_counts + hidden_counts):
        classification = "DEV_SYMBOLIC_CEILING"
    else:
        classification = "DEV_SYMBOLIC_HEADROOM_OPEN"
    return {
        "schema": "yggdrasil.wsp101.h01.symbolic-dev-audit.v1",
        "fixed_source_parent": "8582e6f030f09dacdab388804c584e9e09695230",
        "freeze_commit": "6f18b44b9751de438476452c66765e7549375416",
        "classification": classification,
        "audit_is_post_manual_dev_diagnostic": True,
        "scientific_superiority": False,
        "original_worlds_touched": False,
        "fully_trained_recurrent_baseline_run": False,
        "passive_hypotheses": len(GRAMMAR),
        "passive_survivors_by_context": visible_counts,
        "hidden_hypotheses_per_visible": 6,
        "hidden_survivors_by_context_mode": hidden_counts,
        "contexts": len(DEV_CONTEXTS),
        "evaluated_context_mode_pairs": len(hidden_counts),
        "active_actions_per_pair": sum(map(len, POLICIES)),
        "public_trace_sha256": hashlib.sha256(
            "".join(public_digests).encode("ascii")
        ).hexdigest(),
    }


class HeadroomH01Tests(unittest.TestCase):
    def test_frozen_cohort_and_budget(self):
        self.assertEqual(DEV_CONTEXTS, tuple(range(8)))
        self.assertEqual(STARTS, (17, 1234))
        self.assertEqual(POLICIES, ((1, 0, 2, 0), (3, 0, 0, 0)))
        self.assertEqual(sum(map(len, POLICIES)), 8)
        self.assertEqual(len(GRAMMAR), 96)

    def test_control_does_not_import_oracle_or_hidden_truth(self):
        code = (HERE / "headroom_h01_symbolic.py").read_text("utf-8")
        for forbidden in ("from paired_fixture import", "import paired_fixture", "._program",
                          "._mode", "._hidden", "rank(", "make_world(", "torch", "transformers"):
            self.assertNotIn(forbidden, code)

    def test_passive_and_hidden_causal_diagnostic(self):
        results = audit()
        self.assertIn(results["classification"], (
            "DEV_SYMBOLIC_CEILING", "DEV_SYMBOLIC_HEADROOM_OPEN"))
        self.assertEqual(results["evaluated_context_mode_pairs"], 16)
        self.assertTrue(all(1 <= n <= 96 for n in results["passive_survivors_by_context"]))
        self.assertTrue(all(1 <= n <= 576 for n in results["hidden_survivors_by_context_mode"]))
        self.assertFalse(results["scientific_superiority"])

    def test_no_intervention_cannot_identify_hidden_mode(self):
        # Explicit negative: passive-only source cannot distinguish modes.
        passive = passive_source(0, 0)
        active = collect(observe_world(0, 0), ((0, 0, 0, 0), (0, 0, 0, 0)))
        solutions = hidden_candidates(passive, active)
        self.assertGreaterEqual(len(solutions), 6)

    def test_bad_source_rows_fail_closed(self):
        passive = passive_source(0, 0)
        bad = [[list(row) for row in episode] for episode in passive]
        bad[0][0][3] = 8
        with self.assertRaises(ValueError):
            visible_candidates(bad)
        bad2 = [[list(row) for row in episode] for episode in passive]
        bad2[0][0][1] = True
        with self.assertRaises(ValueError):
            visible_candidates(bad2)

    def test_original_sources_unavailable(self):
        for source in (8, 101011, 101101, 101201, 101301):
            with self.assertRaises(PermissionError):
                observe_world(source, 0)

    def test_no_mutation_and_deterministic_public_reads(self):
        passive = passive_source(4, 0)
        c1 = collect(observe_world(4, 1))
        c2 = collect(observe_world(4, 1))
        self.assertEqual(c1, c2)
        self.assertEqual(passive, passive_source(4, 1))
        _rows(c1, require_passive=False)

    def test_no_transplant_or_scientific_claim(self):
        outcome = audit()
        self.assertTrue(outcome["audit_is_post_manual_dev_diagnostic"])
        self.assertFalse(outcome["scientific_superiority"])
        self.assertFalse(outcome["original_worlds_touched"])


if __name__ == "__main__":
    unittest.main()
