"""Source-free WSCM-01 router contracts; NO scientific score or first-use."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          'research/contrib/chatgpt/CAUSAL-AMALGAM/wscm01_wake_router.py')
SPEC = spec_from_file_location('wscm01_wake_router', SOURCE)
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WakeRouterTests(unittest.TestCase):
    def test_unfamiliar_ids_bind_from_charged_basis_without_id_index(self):
        # Known training templates; unseen action IDs map by witnessed deltas.
        r = MODULE.WakeRoleRouter({1: 0, 2: 1})
        for action, expected in ((4001, 1), (91, 2), (90017, 1)):
            self.assertEqual(r.next_probe(action), 0)
            self.assertEqual(r.observe(action, 0, int(expected == 2), action,
                                       charged=True, controlled=True), ('PROVISIONAL', expected))
            self.assertEqual(r.next_probe(action), 1)
            self.assertEqual(r.observe(action, 1, 0, action + 100000,
                                       charged=True, controlled=True), ('PROVISIONAL', expected))
            self.assertIsNone(r.next_probe(action))

    def test_two_charged_probes_disambiguate_when_separable(self):
        r = MODULE.WakeRoleRouter({1: 0, 2: 1 << 1, 3: 1 << 2})
        self.assertEqual(r.next_probe(3), 1)
        self.assertEqual(r.observe(3, 1, 0, 11, charged=True, controlled=True),
                         ('AMBIGUOUS', None))
        self.assertEqual(r.next_probe(3), 2)
        self.assertEqual(r.observe(3, 2, 0, 12, charged=True, controlled=True),
                         ('PROVISIONAL', 1))

    def test_two_probes_can_leave_partial_ambiguity(self):
        r = MODULE.WakeRoleRouter({1: 0, 2: 1 << 1, 3: 1 << 2, 4: 1 << 3})
        self.assertEqual(r.next_probe(6), 1)
        self.assertEqual(r.observe(6, 1, 0, 11, charged=True, controlled=True),
                         ('AMBIGUOUS', None))
        self.assertEqual(r.next_probe(6), 2)
        self.assertEqual(r.observe(6, 2, 0, 12, charged=True, controlled=True),
                         ('AMBIGUOUS', None))
        self.assertIsNone(r.next_probe(6))

    def test_nonidentifiable_roles_do_not_force_a_binding(self):
        r = MODULE.WakeRoleRouter({1: 0, 2: 0})
        self.assertIsNone(r.next_probe(5))
        self.assertEqual(r.status(5), ('UNSEEN', None))

    def test_unknown_signature_stays_unbound(self):
        r = MODULE.WakeRoleRouter({1: 0, 2: 1})
        self.assertEqual(r.observe(12, 0, 1, 1, charged=True, controlled=True),
                         ('PROVISIONAL', 2))
        # First receipt may be provisionally bound; a contradiction invalidates it.
        self.assertEqual(r.observe(12, 5, 1, 2, charged=True, controlled=True),
                         ('UNKNOWN', None))
        self.assertIsNone(r.next_probe(12))

    def test_one_bit_match_never_certifies_a_full_signature(self):
        # Unknown true 128-bit role differs only at the unseen bit 127.
        # An action can match both selected bits but remain NOT identifiable.
        r = MODULE.WakeRoleRouter({1: 0, 2: 1})
        self.assertEqual(r.observe(8, 0, 0, 100, charged=True, controlled=True),
                         ('PROVISIONAL', 1))
        self.assertEqual(r.next_probe(8), 1)
        self.assertEqual(r.observe(8, 1, 0, 101, charged=True, controlled=True),
                         ('PROVISIONAL', 1))
        self.assertIsNone(r.next_probe(8))
        self.assertNotEqual(r.status(8)[0], 'BOUND')

    def test_passive_or_uncharged_evidence_is_rejected_without_mutation(self):
        r = MODULE.WakeRoleRouter({1: 0})
        for charged, controlled in ((False, True), (True, False)):
            with self.assertRaisesRegex(ValueError, 'WSCM_CHARGED_RECEIPT_REQUIRED'):
                r.observe(7, 0, 0, 1, charged=charged, controlled=controlled)
        self.assertEqual(r.snapshot(), ())

    def test_conflicting_duplicate_is_rejected_and_exact_replay_idempotent(self):
        r = MODULE.WakeRoleRouter({1: 0})
        r.observe(7, 0, 0, 1, charged=True, controlled=True)
        before = r.snapshot()
        r.observe(7, 0, 0, 1, charged=True, controlled=True)
        self.assertEqual(r.snapshot(), before)
        with self.assertRaisesRegex(ValueError, 'WSCM_CONFLICTING_RECEIPT'):
            r.observe(7, 0, 1, 2, charged=True, controlled=True)
        self.assertEqual(r.snapshot(), before)

    def test_fixed_probe_action_and_role_caps(self):
        with self.assertRaisesRegex(ValueError, 'WSCM_ROLE_CAPACITY'):
            MODULE.WakeRoleRouter({i: i for i in range(17)})
        r = MODULE.WakeRoleRouter({1: 0})
        for a in range(64):
            r.observe(a, 0, 0, a, charged=True, controlled=True)
        with self.assertRaisesRegex(ValueError, 'WSCM_ACTION_CAPACITY'):
            r.observe(64, 0, 0, 64, charged=True, controlled=True)
        with self.assertRaisesRegex(ValueError, 'WSCM_PROBE_CAPACITY'):
            self._attempt_third()

    @staticmethod
    def _attempt_third():
        r = MODULE.WakeRoleRouter({1: 0})
        r.observe(1, 0, 0, 1, charged=True, controlled=True)
        r.observe(1, 1, 0, 2, charged=True, controlled=True)
        r.observe(1, 2, 0, 3, charged=True, controlled=True)

    def test_one_receipt_cannot_forge_two_charged_probes(self):
        r = MODULE.WakeRoleRouter({1: 0})
        r.observe(5, 0, 0, 22, charged=True, controlled=True)
        with self.assertRaisesRegex(ValueError, 'WSCM_RECEIPT_REUSE'):
            r.observe(5, 1, 0, 22, charged=True, controlled=True)
        self.assertEqual(len(r.snapshot()[0][1]), 1)

    def test_cold_restore_is_canonical_and_phenotype_only(self):
        templates = {1: 0, 2: 1}
        r = MODULE.WakeRoleRouter(templates)
        r.observe(80, 0, 1, 6, charged=True, controlled=True)
        r.observe(10, 0, 0, 7, charged=True, controlled=True)
        recovered = MODULE.WakeRoleRouter.restore(templates, r.snapshot())
        self.assertEqual(recovered.snapshot(), r.snapshot())
        self.assertEqual(recovered.status(80), ('PROVISIONAL', 2))
        self.assertEqual(templates, {1: 0, 2: 1})
        with self.assertRaisesRegex(ValueError, 'WSCM_NONCANONICAL_SNAPSHOT'):
            MODULE.WakeRoleRouter.restore(templates, tuple(reversed(r.snapshot())))

    def test_invalid_inputs_fail_closed(self):
        r = MODULE.WakeRoleRouter({1: 0})
        for action, bit, delta in ((True, 0, 0), (0, True, 0), (0, 128, 0), (0, 0, 2)):
            with self.assertRaises(ValueError):
                r.observe(action, bit, delta, 1, charged=True, controlled=True)
        self.assertEqual(r.snapshot(), ())

if __name__ == '__main__':
    unittest.main()
