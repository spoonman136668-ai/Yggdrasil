"""RD06 source-only post-hoc static one-lag sufficiency lower bound."""
import importlib.util
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/(
    "research/contrib/chatgpt/YGG-CAP04/rd06_identifiability.py")
spec=importlib.util.spec_from_file_location("cap04_rd06",SCRIPT)
rd06=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd06)


class RD06StaticIdentifiabilityCertificate(unittest.TestCase):
    def test_source_pin_and_witness_count(self):
        for source in rd06.SOURCES:
            with self.subTest(source=source):
                events=rd06.fixed_rows(source)
                self.assertEqual(len(events),256)
                self.assertEqual(len({r["id"] for r in events}),256)
                self.assertEqual(rd06.digest(rd06.canonical(events)),
                                 rd06.SOURCE_PINS[source])
                triples=rd06.keyed(events)
                self.assertEqual(triples[0]["key"][-1],(0,0))
                for t in range(1,256):
                    self.assertEqual(triples[t]["key"][-1],
                                     events[t-1]["action"])
                    self.assertEqual(triples[t]["y"],events[t]["y"])
        for bogus in (99917,"99917","cap04-rd04-source-c"):
            with self.assertRaisesRegex(ValueError,"UNKNOWN_SOURCE"):
                rd06.fixed_rows(bogus)

    def test_closed_form_optimum_against_independent_counting(self):
        for source in rd06.SOURCES:
            with self.subTest(source=source):
                events=rd06.keyed(rd06.fixed_rows(source))
                for length in (192,256):
                    data=events[:length]
                    table=defaultdict(lambda:[0,0])
                    for ev in data:
                        table[ev["key"]][ev["y"]]+=1
                    expected=sum((Fraction(n0*n1,n0+n1)
                                  for n0,n1 in table.values()),
                                 Fraction())/length
                    errors=sum(min(*v) for v in table.values())
                    conflicts=sum(v[0]>0 and v[1]>0 for v in table.values())
                    result=rd06.minimize(data)
                    value=result["static_bernoulli_minimum_brier"]
                    self.assertEqual(
                        Fraction(value["numerator"],value["denominator"]),
                        expected)
                    self.assertEqual(result["static_deterministic_minimum_errors"],
                                     errors)
                    self.assertEqual(result["conflicting_key_count"],conflicts)
                    self.assertLessEqual(expected,Fraction(1,4))
                    for example in result["witnessed_opposition_examples"]:
                        a=events[example["witness_0"]["t"]]
                        b=events[example["witness_1"]["t"]]
                        self.assertEqual(a["key"],b["key"])
                        self.assertNotEqual(a["y"],b["y"])
                        self.assertNotEqual(a["witness_id"],b["witness_id"])

    def test_unavailable_phase_oracle_is_not_a_learner(self):
        for source in rd06.SOURCES:
            with self.subTest(source=source):
                report=rd06.certificate(source)
                self.assertTrue(report["phase_is_evaluator_only"])
                self.assertFalse(report["scientific_pass"])
                self.assertFalse(report["canonical_model_modified"])
                self.assertFalse(report["registered_source_first_use"])
                self.assertFalse(
                    report["old_probe_context_limit"]["complete_history_input_frozen"])
                self.assertEqual(
                    report["unavailable_phase_tag_oracle_a_b"]
                      ["static_bernoulli_minimum_brier"]["numerator"],0)
                self.assertEqual(
                    report["unavailable_phase_tag_oracle_a_b_a"]
                      ["static_bernoulli_minimum_brier"]["numerator"],0)
                self.assertEqual(rd06.audit(rd06.canonical(report))["source"],
                                 source)

    def test_immutable_diagnostic_rejects_forged_scope_counts_and_witness(self):
        report=rd06.certificate(rd06.SOURCES[0])
        original=rd06.canonical(report)
        rd06.audit(original)
        changes=(
            (("pre_return_a_b","conflicting_key_count"),-1),
            (("pre_return_a_b","static_bernoulli_minimum_brier",
              "numerator"),0),
            (("pre_return_a_b","witnessed_opposition_examples"),[]),
            (("scientific_pass",),True),
            (("old_probe_context_limit","complete_history_input_frozen"),True),
            (("original_source_sha256",),"0"*64)
        )
        for path,value in changes:
            with self.subTest(path=path):
                mutated=json.loads(original)
                node=mutated
                for name in path[:-1]:
                    node=node[name]
                node[path[-1]]=value
                with self.assertRaisesRegex(ValueError,"DIAGNOSTIC_INVALID"):
                    rd06.audit(rd06.canonical(mutated))


if __name__=="__main__":
    unittest.main()
