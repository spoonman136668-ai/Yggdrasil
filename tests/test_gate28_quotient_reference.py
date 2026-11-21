"""Algebra and ABI fixtures only; no scientific-world outcomes."""
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import core
import full_reference as full
import quotient_reference as quotient


class TestGate28QuotientReference(unittest.TestCase):
    def test_signed_alias_rule_identity(self):
        self.assertEqual(sum(quotient.SIZES), 5244)
        self.assertEqual(sum(map(len, quotient.MAPS)), 11424)
        for node, bank in enumerate(full.BANKS):
            for rule, (index, sign) in zip(bank, quotient.MAPS[node]):
                rep = quotient.BASES[node][index]
                for prev in (None, (0, 1, 1, 0, 1, 0, 0, 1)):
                    for mask in (0, 16383, 0x1555, 0x2AAA):
                        cells = [(mask >> i) & 1 for i in range(14)]
                        a = full._rule(rule, cells, prev, full.Meter())
                        b = full._rule(rep, cells, prev, full.Meter())
                        self.assertEqual(a, None if b is None else
                                         b ^ int(sign < 0))

    def test_full_fit_exact_parity_and_budgets(self):
        reference = full.new(full.ARMS[0])
        candidate = quotient.new(quotient.ARMS[0])
        peak_work = peak_bytes = full_work = 0
        cpu_full = cpu_quotient = 0
        for step in range(224):
            octets = hashlib.sha256(("quotient-public-fixture-v1:" +
                                    str(step)).encode("ascii")).digest()
            ctx = core.as_bits(octets[0])
            med = [(octets[1] >> p) & 1 for p in range(6)]
            action = 12 if step % 3 == 0 else step % 13
            if action < 12:
                med[action // 2] = action % 2
            med = tuple(med)
            reward = octets[2] & 1
            fw, qw = full.Meter(), core.Work()
            query = step in (0, 95, 96, 159, 160, 223)
            started = time.process_time_ns()
            if query:
                expected_choice = full.choose(reference, ctx, fw)
                expected = full.predict(reference, ctx, action, fw)
            full.observe(reference, ctx, med, action, reward, fw)
            cpu_full += time.process_time_ns() - started
            started = time.process_time_ns()
            if query:
                self.assertEqual(quotient.choose(candidate, ctx, qw),
                                 expected_choice)
                self.assertEqual(quotient.predict(candidate, ctx, action, qw),
                                 expected)
            quotient.observe(candidate, ctx, med, action, reward, qw)
            cpu_quotient += time.process_time_ns() - started
            self.assertEqual(quotient.expanded_scores(candidate),
                             reference["scores"])
            peak_work = max(peak_work, qw.count)
            full_work = max(full_work, fw.evaluations)
            if step == 95:
                full.seal_source(reference)
                quotient.seal_source(candidate)
                source_ctx = ctx
                source_function = [full.source_predict(reference, ctx, a,
                                                       full.Meter())
                                   for a in range(13)]
            if step in (95, 159, 223):
                raw = quotient.pack(candidate)
                peak_bytes = max(peak_bytes, len(raw))
                candidate = quotient.unpack(raw)
                self.assertEqual(quotient.pack(candidate), raw)
                self.assertEqual([quotient.source_predict(candidate, source_ctx,
                                  a, core.Work()) for a in range(13)],
                                 source_function)
                for a in range(13):
                    self.assertEqual(quotient.predict(candidate, ctx, a,
                                                     core.Work()),
                                     full.predict(reference, ctx, a, full.Meter()))
                reference["arm"], candidate["arm"] = full.ARMS[1], quotient.ARMS[1]
                self.assertEqual(quotient.choose(candidate, ctx, core.Work()),
                                 full.choose(reference, ctx, full.Meter()))
                reference["arm"], candidate["arm"] = full.ARMS[0], quotient.ARMS[0]
        self.assertLessEqual(peak_work, 8192)
        self.assertLessEqual(peak_bytes, 16384)
        self.assertGreater(full_work, 8192)
        self.assertGreaterEqual(full_work, 2 * peak_work)
        damaged = bytearray(quotient.pack(candidate))
        damaged[-4] ^= 1
        with self.assertRaises(ValueError):
            quotient.unpack(bytes(damaged))
        with self.assertRaises(ValueError):
            quotient.observe(candidate, ctx, med, action, reward, core.Work())
        print("G28_QUOTIENT_EQUIVALENCE", json.dumps({
            "scope": "public ABI fixtures; no scientific first-use",
            "represented": 11424, "representatives": 5244, "public_rows": 224,
            "full_peak_rule_work": full_work, "quotient_peak_rule_work": peak_work,
            "checkpoint_peak_bytes": peak_bytes, "full_cpu_ns": cpu_full,
            "quotient_cpu_ns": cpu_quotient, "full_score_grid_exact": True,
            "source_function_exact": True, "scientific_gain_verified": False},
            sort_keys=True))
