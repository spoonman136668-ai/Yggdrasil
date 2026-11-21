"""KNOW32 independent static support audit: NO private outcomes / held first-use.

The KNOWN32 prospective protocol was frozen at Git blob
9f8664601b2161183b16d7b47ac53303e1b73d51 before this test.
Only enumerate the six possible opaque action permutations and public tapes.
"""
import collections
import hashlib
import itertools
import json
import unittest
from pathlib import Path

from unknown_action_affordance_dev import ALL_MAPS, TRUE_MAPS
from know27_online_action_policy_dev import LAWS

PREREG_BLOB = "9f8664601b2161183b16d7b47ac53303e1b73d51"
PHASES = (range(0, 16), range(16, 32), range(32, 48))


def protocol():
    raw = Path(__file__).with_name("know32_balanced_access_protocol.json").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != PREREG_BLOB:
        raise ValueError("KNOW32_PREREG_CHANGED_BEFORE_SOURCE")
    x = json.loads(raw)
    if x["schema"] != "yggdrasil.know32.balanced-access-causal-retention-prereg.v1":
        raise ValueError("KNOW32_WRONG_PROTOCOL")
    return x


def tape(t, balanced):
    if type(t) is not int or not 0 <= t < 48 or type(balanced) is not bool:
        raise ValueError("KNOW32_PUBLIC_TAPE")
    c = t % 4
    # Exactly the frozen KNOW32 proposal, not a new/fitted schedule.
    a = (t // 4) % 4 if balanced else t % 4
    return c, a


def physical_counts(mapping, phase, balanced):
    if tuple(mapping) not in ALL_MAPS or type(phase) is not int or phase not in range(3):
        raise ValueError("KNOW32_PHYSICAL_CUSTODY")
    public = collections.Counter()
    physical = collections.Counter()
    per_block = []
    for block in range(4):
        acts = set()
        for t in range(16 * phase + 4 * block, 16 * phase + 4 * (block + 1)):
            c, a = tape(t, balanced)
            public[(c, a)] += 1
            physical[c ^ mapping[a]] += 1
            acts.add(a)
        per_block.append(acts)
    return public, physical, per_block


class Know32CoverageBeforeHeld(unittest.TestCase):
    def test_frozen_24_world_first_use_not_consumed_here(self):
        p = protocol()
        self.assertEqual(len(ALL_MAPS), 6)
        self.assertTrue(all(tuple(x) in ALL_MAPS for x in TRUE_MAPS))
        self.assertEqual(p["source"]["world_count"], 24)
        self.assertEqual(p["budgets"]["unique_observed_consequences_total"], 1920)
        self.assertFalse(p["scope"]["original_first_use_issue_426"])
        self.assertFalse(p["scope"]["accepted_native_modified"])
        self.assertEqual(p["scope"]["deployment"], "NONE")

    def test_legacy_diagonal_tape_never_reaches_hidden_context_4(self):
        for mapping in ALL_MAPS:
            for phase in range(3):
                _, physical, _ = physical_counts(mapping, phase, False)
                self.assertEqual(physical[4], 0)
                self.assertEqual(sum(physical.values()), 16)

    def test_frozen_public_grid_guarantees_complete_but_unequal_physical_support(self):
        for mapping in ALL_MAPS:
            for phase in range(3):
                grid, counts, _ = physical_counts(mapping, phase, True)
                self.assertEqual(len(grid), 16)
                self.assertEqual(set(grid.values()), {1})
                self.assertEqual(sum(counts.values()), 16)
                self.assertEqual([counts[c] for c in range(8)], [3, 3, 3, 3, 1, 1, 1, 1])

    def test_each_block_holds_one_action_over_all_four_contexts(self):
        for mapping in ALL_MAPS:
            for phase in range(3):
                grid, _, blocks = physical_counts(mapping, phase, True)
                self.assertEqual(blocks, [{0}, {1}, {2}, {3}])
                self.assertEqual({c for c, _ in grid}, set(range(4)))
        self.assertEqual([tape(t, True)[0] for t in range(48)],
                         [t % 4 for t in range(48)])

    def test_exact_unidentifiability_null_for_laws_differing_only_at_bit_four(self):
        # Two otherwise identical Boolean laws produce the SAME conditional
        # Bernoulli distribution along the legacy tape, for EVERY possible map.
        # The new tape opens a distinguishable possibility but no data is drawn.
        law0, law1 = 0, 1 << 4
        for mapping in ALL_MAPS:
            old = [tape(t, False) for t in range(48)]
            new = [tape(t, True) for t in range(48)]
            self.assertTrue(all(((law0 >> (c ^ mapping[a])) & 1) ==
                                ((law1 >> (c ^ mapping[a])) & 1)
                                for c, a in old))
            self.assertTrue(any(((law0 >> (c ^ mapping[a])) & 1) !=
                                ((law1 >> (c ^ mapping[a])) & 1)
                                for c, a in new))
        self.assertEqual((.85 - .15), .70)

    def test_scope_of_unfamiliar_law_is_local_fit_only(self):
        # H1 has already been in KNOW27's published candidate law set;
        # it is new to the two labelled KNOW30 FIT regimes, not an
        # independently unfamiliar causal *family* or global transfer test.
        p = protocol()
        self.assertIn("H1", LAWS)
        self.assertIn("H1", p["source"]["unfamiliar_B_rule"])
        self.assertNotIn("H1", ("H0", "H2"))
        self.assertEqual(p["source"]["mode"], "engineering_fixture_only")

    def test_invalid_tape_inputs_fail_closed(self):
        for t in (True, -1, 48, 0.0):
            with self.assertRaises(ValueError):
                tape(t, True)
        with self.assertRaises(ValueError):
            tape(0, "True")
        with self.assertRaises(ValueError):
            physical_counts((0, 0, 0, 0), 0, True)


if __name__ == "__main__":
    unittest.main()
