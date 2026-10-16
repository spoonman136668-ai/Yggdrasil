"""Y-F57 FIT-only bounded-memory source checks. No held-out use."""
import importlib.util
import json
import pathlib
import sys
import unittest

HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("y57_src",HERE/"source_fit.py")
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)

class FITSource(unittest.TestCase):
    def test_no_diag_or_original_first_use(self):
        for seed,family in ((671100,1264),(672000,1268),(671000,1264),(671100,1260)):
            with self.assertRaises(ValueError):
                m.source(seed,family)
    def test_frozen_public_first_use(self):
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(p["fit"]["seed_range"],[m.FIT.start,m.FIT.stop])
        self.assertEqual(p["fit"]["families"],list(m.FAMILY))
        self.assertEqual(p["resource"]["max_serialized_payload_bytes"],12*m.RECORD_CAP)
        self.assertEqual(p["resource"]["public_events_per_stream"],m.EVENTS)
    def test_lossless_direction_reversal_and_byte_provenance(self):
        z=(111,333,(0,3,4,7))
        self.assertEqual(m.unpack(m.pack(z)),z)
        self.assertEqual(m.inverse(m.inverse(z)),z)
        with self.assertRaises(ValueError):
            m.pack((111,333,(0,3,4,7,6)))
    def test_two_new_fit_source_regimes_are_public_only(self):
        for seed,family in ((671000,1260),(671001,1261)):
            public,query,regime=m.source(seed,family)
            self.assertEqual(len(public),72)
            self.assertEqual(len(set(public)),72)
            self.assertEqual(sum(e[3] for e in public),36)
            # There are four complete eight-hop components, independently
            # recognizable without the withheld future query.
            offline=m.full_public_reference(public)
            self.assertEqual(m.solve(offline,query),1)
            self.assertLessEqual(len(offline),m.RECORD_CAP)
            for policy in ("incremental_boundary_merge","frozen_greedy_merge","raw_fifo"):
                retained=m.causal_online(public,policy)
                self.assertLessEqual(len(retained),m.RECORD_CAP)
                self.assertLessEqual(sum(len(m.pack(r)) for r in retained),144)
                self.assertTrue(all(m.unpack(m.pack(z))==z for z in retained))

if __name__=="__main__":
    unittest.main()
