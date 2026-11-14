"""WSP100 wider-than-generating-class DEV audit; no original worlds."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fixture import sources, heldout_plan
from fixture_auditor import audit_fixture as narrow_audit, version_space as narrow_space
from broad_auditor import ALL_PROGRAMS, audit, identifiability, version_space, validate_plan


def _independent_primitive(f, a, b):
    if f == 0: return (a + b) % 4
    if f == 1: return a ^ b
    if f == 2: return a if b % 2 == 0 else 3 - a
    if f == 3: return (a * b + b) % 4
    raise AssertionError("invalid independent probe")


def _shifted_law_probe():
    """Fixture-only counterexample to exact generating-family assumptions.

    Deliberately separate test-world equations: no import of auditor step.
    """
    f, w, t, p = 2, 1, 0, 3
    episodes = []
    for i in range(8):
        x = tuple((i * (j + 1) + j * j) % 4 for j in range(6))
        h = (0, 0)
        rows = []
        for k in range(4):
            action = (i + 2 * k) % 4
            out = []
            for j in range(6):
                first = _independent_primitive(f, x[(j+w)%6], x[(j+1+w)%6])
                second = _independent_primitive((f+1+j%3+1)%4,
                                                first, x[(j+3)%6])
                val = (second + p * (1+j%2)) % 4
                if j < 4:
                    val = (val + h[j%2]) % 4
                out.append(val)
            next_h = list(h)
            for j in range(2):
                active = action == (t+j)%4
                condition = (x[(w+j)%6]+x[(w+j+2)%6]+p+j)%2 == 1
                if active and condition:
                    next_h[j] = (h[j] + 1 + (p+j)%3) % 4
            y = tuple(out)
            rows.append((x, action, y, int((y[0]+y[1])%4 == 3)))
            x,h = y,tuple(next_h)
        episodes.append(tuple(rows))
    return tuple(episodes)


class BroadAuditDevelopmentTests(unittest.TestCase):
    def test_cardinality_and_original_embedding(self):
        self.assertEqual(len(ALL_PROGRAMS), 2048)
        self.assertEqual(len(set(ALL_PROGRAMS)), 2048)
        self.assertEqual(sum(p[4:] == (0, 0) for p in ALL_PROGRAMS), 256)

    def test_every_fixture_has_wider_source_consistent_program(self):
        for fid in range(8):
            b = sources(fid)
            p = heldout_plan(b)
            broad = audit(b, p)
            narrow = narrow_audit(b, p)
            self.assertEqual(broad["catalogue"], 2048)
            self.assertEqual(broad["slots"], 432)
            self.assertGreaterEqual(broad["survivors"], narrow["survivor_count"])
            self.assertGreater(broad["survivors"], 0)
            self.assertLessEqual(broad["fraction"], narrow["fraction"] + 1e-12)
            self.assertFalse(broad["scientific_superiority"])
            self.assertFalse(broad["original_worlds_consumed"])
            self.assertEqual(broad, audit(b, p))

    def test_original_worlds_cannot_be_pretended_to_be_fixtures(self):
        b = sources(0)
        p = heldout_plan(b)
        for bad_id in (100011, 100101, 100201, 100301, -1, 8, True):
            changed = copy.deepcopy(b)
            changed["fixture_id"] = bad_id
            with self.assertRaises((ValueError, PermissionError)):
                audit(changed, p)
        altered = copy.deepcopy(p)
        altered["fixture_id"] = 1
        with self.assertRaises(ValueError):
            audit(b, altered)

    def test_digest_and_counterfactual_plan_tampering_fails_closed(self):
        b = sources(1)
        p = heldout_plan(b)
        changed = copy.deepcopy(b)
        changed["passive"][0] = changed["active"][0]
        with self.assertRaises((ValueError, PermissionError, TypeError)):
            audit(changed, p)
        altered = copy.deepcopy(p)
        altered["targets"] = list(altered["targets"])
        altered["targets"][0] = altered["targets"][1]
        with self.assertRaises(ValueError):
            audit(b, altered)
        altered = copy.deepcopy(p)
        altered["plan_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            audit(b, altered)

    def test_empty_history_falsifies_certainty(self):
        plan = heldout_plan(sources(0))
        survivors = version_space(())
        self.assertEqual(len(survivors), 2048)
        result = identifiability(survivors, plan["targets"])
        self.assertEqual(result["slots"], 432)
        self.assertLess(result["fraction"], 1.0)
        zero = identifiability((), plan["targets"])
        self.assertEqual(zero["classification"], "INVALID_EMPTY_VERSION_SPACE")
        self.assertIsNone(zero["fraction"])

    def test_different_second_stage_operator_refuses_narrow_assumption(self):
        observed = _shifted_law_probe()
        self.assertEqual(len(narrow_space(observed)), 0)
        wider = version_space(observed)
        self.assertIn((2, 1, 0, 3, 1, 0), wider)


if __name__ == "__main__":
    unittest.main()
