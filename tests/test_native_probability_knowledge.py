"""NKR19 source-free mechanics; never opens original transcripts or sources."""
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
from fractions import Fraction
import tempfile
import unittest
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr19_mechanics",
    ROOT/"research/contrib/chatgpt/NKR-19/audit.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def fixture():
    rows=[]
    state=0
    for i in range(31):
        after=(state^(i&1))
        rows.append(dict(before=state,action=i%2,reward=(i//4)%2,after=after,
                         terminated=False,truncated=i==30))
        state=after
    return {seed:[dict(r) for r in rows] for seed in audit.SEEDS}

class NativeProbabilityKnowledgeTests(unittest.TestCase):
    def test_probability_exact_prior_posterior_and_no_read_mutation(self):
        bank=PublicCausalCells()
        self.assertEqual(bank.outcome_probability(0,0),(1,2))
        for y in (1,0,1):
            bank.observe(0,0,y)
        before=bank.snapshot()
        self.assertEqual(bank.outcome_probability(0,0),(3,5))
        self.assertEqual(bank.outcome_probability(0,1),(1,2))
        self.assertEqual(bank.snapshot(),before)
        self.assertEqual(len(before),164)

    def test_native_count_capacity_and_cold_readout_all_addresses(self):
        bank=PublicCausalCells()
        for s in range(16):
            local,retained=audit.address(s)
            bank.observe(local,1,s%2,retained=retained)
        cold=PublicCausalCells.restore(bank.snapshot())
        self.assertEqual(cold.snapshot(),bank.snapshot())
        for s in range(16):
            local,retained=audit.address(s)
            self.assertEqual(cold.outcome_probability(local,1,retained=retained),
                             bank.outcome_probability(local,1,retained=retained))

    def test_strict_probability_inputs(self):
        bank=PublicCausalCells()
        for address,action,retained in ((7,0,False),(9,0,True),
                                       (0,True,False),(True,0,False),(0,0,1)):
            with self.assertRaises(ValueError):
                bank.outcome_probability(address,action,retained=retained)

    def test_probabilistic_public_contradictions_are_counted(self):
        bank=PublicCausalCells()
        bank.observe(0,1,0)
        bank.observe(0,1,1)
        self.assertEqual(bank.outcome_probability(0,1),(2,4))
        # Existing deterministic data contract is distinct, not silently relaxed.
        source=inspect.getsource(PublicCausalCells.outcome_probability)
        self.assertNotIn("observe(",source)
        self.assertNotIn("_counts =",source)

    def test_batch_fit_and_native_probabilities_match_for_all_public_prefixes(self):
        data=fixture()[audit.SEEDS[0]]
        bank=PublicCausalCells()
        prefix=[]
        for row in data:
            if prefix:
                answers=audit.predict_all(bank,0,prefix,row)
                self.assertEqual(answers["native_beta"],answers["exact_beta"])
            audit.update(bank,0,row)
            prefix.append(row)

    def test_fixed_exposure_deduplication_and_retention_counts(self):
        for k in audit.SCALES:
            r=audit.fixed_scale(fixture(),k)
            self.assertEqual(r["native_outcome_updates"],8*k)
            self.assertEqual(r["unique_training_events"],4*k)
            self.assertEqual(r["presentations"],96)
            self.assertEqual(r["replayed_presentations_skipped"],96-4*k)
            self.assertEqual(r["retained_probability_readouts"],48)
            self.assertTrue(r["retention_all_equal"])
            self.assertEqual(r["scores"]["native_beta"]["scored_outputs"],56)

    def test_prequential_predict_then_update_and_all_controls(self):
        r=audit.prequential(fixture())
        self.assertEqual(r["scored_transitions"],92)
        self.assertEqual(r["scores"]["native_beta"]["scored_outputs"],184)
        self.assertEqual(r["scores"]["native_beta"],r["scores"]["exact_beta"])
        self.assertEqual(r["checkpoint_bytes"],164)

    def test_binary_temporal_source_contract_negatives(self):
        rows=fixture()[audit.SEEDS[0]]
        audit.validate_rows(rows)
        for key,value in (("before",True),("reward",0.5),
                          ("truncated",0),("extra","private")):
            altered=json.loads(json.dumps(rows))
            altered[0][key]=value
            with self.assertRaises(ValueError):
                audit.validate_rows(altered)
        bad=json.loads(json.dumps(rows));bad[1]["before"]=1-bad[0]["after"]
        with self.assertRaises(ValueError):
            audit.validate_rows(bad)

    def test_wrong_cached_archive_denied_before_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"not-original.zip"
            file.write_bytes(b"not-the-authorized-cache")
            with self.assertRaisesRegex(ValueError,"CACHED_ARCHIVE_SHA_OR_SIZE"):
                audit.load_source(file)

    def test_no_external_environment_runtime_in_auditor(self):
        source=inspect.getsource(audit)
        for forbidden in ("import causal_gym","native_source_factory(",
                          ".reset(", ".do(", "urlopen(", "requests."):
            self.assertNotIn(forbidden,source)
        result=audit.deterministic_audit(fixture())
        self.assertGreater(result["groups_with_both_outcomes"],0)
        self.assertGreater(result["rejected_deterministic_updates"],0)

if __name__=="__main__":
    unittest.main()
