"""Source-free mechanics. Full-image campaign executes separately once per OS."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from yggdrasil.native_factual_weights import NativeFactualWeights,canonical,digest,SCHEMA
from yggdrasil.native_bounded_fact_repair import BoundedFactRepair
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr25_mechanics",
 ROOT/"research/contrib/chatgpt/NKR-25/campaign.py")
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def image(directory,extra=False):
    triples=[(1,1,o) for o in range(1,601)]+[(s,2,s+10) for s in range(10,42)]
    if extra:
        triples.append((99,2,100))
    triples=sorted(triples)
    raw=b"".join(struct.pack("<III",*t) for t in triples)
    root=Path(directory);root.mkdir(parents=True,exist_ok=True)
    (root/"facts.uint32le").write_bytes(raw)
    manifest={"schema":SCHEMA,"data_kind":"historical-train-only-QPQ",
     "source_archive_sha256":"1"*64,"source_train_sha256":"2"*64,
     "records":len(triples),"numeric_bytes":len(raw),"packed_sha256":digest(raw),
     "scientific_pass":False,"accepted_native":False}
    meta=canonical(manifest);(root/"manifest.json").write_bytes(meta)
    return NativeFactualWeights(root/"facts.uint32le",root/"manifest.json",digest(meta)),triples

class BoundedFactRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base,self.triples=image(Path(self.temp.name)/"base")
    def tearDown(self):
        self.base.close();self.temp.cleanup()

    def test_injected_fault_is_separate_from_frozen_baseline(self):
        before=helper.file_sha(self.base.path)
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0,1,2])
        for i in (0,1,2):
            t=self.triples[i];f=(t[0],t[1],t[2]^0x80000000)
            self.assertTrue(self.base.has_fact(*t));self.assertFalse(bad.has_fact(*t))
            self.assertFalse(self.base.has_fact(*f));self.assertTrue(bad.has_fact(*f))
        self.assertEqual(helper.file_sha(self.base.path),before)

    def test_atomic_bounded_repair_and_frozen_original(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,list(range(30)))
        old=bad.checkpoint()
        raw=helper.witnesses(bad,list(range(10)),"unit-repair",20)
        repaired,receipt=bad.stage_repair(raw,digest(raw),operation_budget=20)
        self.assertEqual(receipt["operations"],20)
        self.assertEqual(repaired.fault_count,20)
        self.assertEqual(bad.checkpoint(),old)
        for i in range(30):
            t=self.triples[i]
            self.assertEqual(repaired.has_fact(*t),i<10)

    def test_budget_parent_and_wrong_witness_reject_without_partial_write(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0,1])
        old=bad.checkpoint()
        good=helper.witnesses(bad,[0,1],"unit-errors",4)
        cases=[]
        d=json.loads(good);d["records"][1][1][2]+=1;cases.append(canonical(d))
        d=json.loads(good);d["parent_checkpoint_sha256"]="0"*64;cases.append(canonical(d))
        d=json.loads(good);d["records"].reverse();cases.append(canonical(d))
        d=json.loads(good);d["source_kind"]="unverified_real_world_update";cases.append(canonical(d))
        for raw in cases:
            with self.assertRaises(ValueError):
                bad.stage_repair(raw,digest(raw),operation_budget=4)
            self.assertEqual(bad.checkpoint(),old)
        for budget in (2,65538,True,-2):
            with self.assertRaises(ValueError):
                bad.stage_repair(good,digest(good),operation_budget=budget)
        self.assertEqual(bad.checkpoint(),old)

    def test_cold_snapshot_pin_and_source_binding(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0,2,5])
        cold=BoundedFactRepair(self.base,bad.checkpoint(),bad.checkpoint_sha256)
        self.assertEqual(cold.checkpoint(),bad.checkpoint())
        with self.assertRaises(ValueError):
            BoundedFactRepair(self.base,bad.checkpoint(),"0"*64)
        other,_=image(Path(self.temp.name)/"other",extra=True)
        try:
            with self.assertRaises(ValueError):
                BoundedFactRepair(other,bad.checkpoint(),bad.checkpoint_sha256)
        finally:
            other.close()

    def test_snapshot_semantic_flags_and_declared_fault_pattern(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0])
        for field,value in (("accepted_native",True),("scientific_pass",True),
                            ("mode","real_world_truth")):
            d=json.loads(bad.checkpoint());d[field]=value;raw=canonical(d)
            with self.assertRaises(ValueError):
                BoundedFactRepair(self.base,raw,digest(raw))
        d=json.loads(bad.checkpoint());d["faults"][0][1]+=1;raw=canonical(d)
        with self.assertRaises(ValueError):
            BoundedFactRepair(self.base,raw,digest(raw))

    def test_pagination_skips_many_removed_source_rows(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,list(range(300)))
        expected=sorted(({o for s,p,o in self.triples if (s,p)==(1,1)}
                         -set(range(1,301)))|{o^0x80000000 for o in range(1,301)})
        for after in (0,250,590,0x80000005,0xFFFFFFFF):
            self.assertEqual(bad.objects(1,1,limit=16,after=after),
                             [o for o in expected if o>after][:16])

    def test_idempotent_replay_and_source_id_rebound(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0,1])
        raw=helper.witnesses(bad,[0],"same-source",2)
        new,_=bad.stage_repair(raw,digest(raw),operation_budget=2)
        replay,receipt=new.stage_repair(raw,digest(raw),operation_budget=2)
        self.assertEqual(replay.checkpoint(),new.checkpoint())
        self.assertEqual(receipt["operations"],0)
        different=helper.witnesses(new,[1],"same-source",2)
        with self.assertRaisesRegex(ValueError,"SOURCE_ID_REBOUND"):
            new.stage_repair(different,digest(different),operation_budget=2)

    def test_sequential_repairs_preserve_all_unrelated_source_facts(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,list(range(20)))
        for chosen,ident in ((list(range(10)),"stage-one"),(list(range(10,20)),"stage-two")):
            raw=helper.witnesses(bad,chosen,ident,20)
            bad,_=bad.stage_repair(raw,digest(raw),operation_budget=20)
        self.assertEqual(bad.fault_count,0)
        self.assertTrue(all(bad.has_fact(*t) for t in self.triples))
        self.assertEqual(bad.objects(1,1,limit=256),self.base.objects(1,1,limit=256))

    def test_fresh_process_can_restore_complete_base_and_patch(self):
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0])
        raw=helper.witnesses(bad,[0],"cold-repair",2)
        new,_=bad.stage_repair(raw,digest(raw),operation_budget=2)
        t=self.triples[0];f=(t[0],t[1],t[2]^0x80000000)
        result=helper.cold_process(self.base,new,[list(t),list(f)])
        self.assertEqual(result["rows"],len(self.triples))
        self.assertEqual(result["answers"],[True,False])

    def test_capacity_and_strict_public_query_inputs(self):
        for indices in ([0,0],[True],[-1],[len(self.triples)],list(range(32769))):
            with self.assertRaises(ValueError):
                BoundedFactRepair.inject_fixture_faults(self.base,indices)
        bad=BoundedFactRepair.inject_fixture_faults(self.base,[0])
        for params in ((True,1,1),(1,0,1),(1,1,-1)):
            with self.assertRaises(ValueError):
                bad.has_fact(*params)
        with self.assertRaises(ValueError):
            bad.objects(1,1,limit=257)

if __name__=="__main__":
    unittest.main()
