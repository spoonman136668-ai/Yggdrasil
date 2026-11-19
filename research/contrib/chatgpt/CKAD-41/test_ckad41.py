"""CKAD41 fixture-only unit tests: real DEV seeds are never scored here."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad41_campaign",HERE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def fixture(index):
    """Explicitly not any registered development/pilot world."""
    ident=hashlib.sha256(("ckad41_fixture|"+str(index)).encode()).hexdigest()
    first=index%2
    row={"s1":first,"x1":(index//2)%2,
         "s2":(index//3)%2,"x2":(index//4)%2,"y":(index//5)%2}
    return (ident,((first,(index//7)%2),(first,(index//11)%2)),row,"warm")


class CKAD41Tests(unittest.TestCase):
    def test_first_use_guard_and_frozen_source_contract(self):
        self.assertEqual(C.PREREG,"3464c859e79b101894c9682042d460ced5068291")
        self.assertEqual(C.DEV,(41101,41102))
        self.assertTrue(set(C.DEV).isdisjoint(C.RESERVED))
        for seed in (*C.RESERVED,*C.DISALLOWED):
            with self.assertRaisesRegex(ValueError,"CKAD41_ONLY_REGISTERED_DEV"):
                C.run(seed)
        self.assertEqual(C.CAP,128)
        self.assertEqual(C.WINDOW,16)

    def test_capacity_and_new_source_only(self):
        a=C.NativeAnchors(16)
        source=[fixture(i) for i in range(160)]
        for i,event in enumerate(source):
            a.observe(event)
            self.assertEqual(a.training_observations,i+1)
            self.assertLessEqual(len(a.archive)*16,128)
        self.assertEqual(a.total_frozen,10)
        self.assertEqual(len(a.archive),8)
        self.assertEqual(a.archive[0][0],32)
        self.assertEqual(a.live_start,160)
        with self.assertRaisesRegex(AssertionError,"CKAD41_ANCHOR_DUPLICATE"):
            a.observe(source[-1])

    def test_cold_native_anchor_read_is_pure_and_disjoint(self):
        a=C.NativeAnchors(16)
        source=[fixture(i) for i in range(64)]
        for event in source:
            a.observe(event)
        self.assertEqual(len(a.eligible(16)),0)
        self.assertEqual(len(a.eligible(32)),1)
        self.assertEqual(len(a.eligible(48)),2)
        self.assertEqual(len(a.eligible(64)),3)
        before=[(s,e,m.checkpoint()) for s,e,m in a.archive]
        p=a.predict(source,(0,1),1)
        q=a.predict(source,(0,1),1,1,0)
        self.assertTrue(0<p<1)
        self.assertTrue(0<q<1)
        self.assertEqual(before,[(s,e,m.checkpoint()) for s,e,m in a.archive])
        for _,_,model in a.archive:
            saved=model.checkpoint()
            restored=NativeEpisodeExperience.restore(saved,digest(saved))
            self.assertEqual(saved,restored.checkpoint())

    def test_equal_retained_source_budget_different_chunk_size(self):
        a=C.NativeAnchors(16)
        b=C.NativeAnchors(32)
        source=[fixture(i) for i in range(160)]
        for event in source:
            a.observe(event)
            b.observe(event)
        self.assertEqual(len(a.archive)*a.block,128)
        self.assertEqual(len(b.archive)*b.block,128)
        self.assertEqual(a.training_observations,b.training_observations)
        self.assertEqual(a.count,b.count)
        self.assertNotEqual(len(a.archive),len(b.archive))

    def test_true_phase_excluded_from_training(self):
        a=C.NativeAnchors(16)
        first=fixture(0)
        second=(first[0],first[1],first[2],"late_B")
        a.observe(first)
        b=C.NativeAnchors(16)
        b.observe(second)
        self.assertEqual(a.live.checkpoint(),b.live.checkpoint())
        self.assertEqual(a.live._ledger,b.live._ledger)

    def test_causal_scientific_gate_strongest_comparator(self):
        def sample(seed,micro=.10,original=.13,match=.13,conv=.13):
            groups={}
            for phase in (*C.PHASES,"pooled_late_shift_and_return"):
                scores={arm:.2 for arm in C.ARMS}
                scores.update({"native_micro16":micro,"native_stream":original,
                               "native_anchor32":match})
                for arm in C.CONVENTIONAL:
                    scores[arm]=conv
                groups[phase]={"brier":scores}
            return {"seed":seed,"metric_groups":groups,
                    "worlds":[{"cold_exact":True,"source_preserved":True,
                               "read_only":True,"duplicate_idempotent":True,
                               "conflict_atomic":True,
                               "micro16_source_records":128,
                               "anchor32_source_records":128,
                               "native_training_events":128,
                               "micro_training_events":128,
                               "anchor32_training_events":128}]}
        a,b=[sample(seed) for seed in C.DEV]
        self.assertEqual(C.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(C.classify([a,sample(C.DEV[1],conv=.109)]),"DEV_NO_GO")
        self.assertEqual(C.classify([a,sample(C.DEV[1],match=.11)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):
            C.classify([b,a])

    def test_cli_blocks_reserved_without_scoring(self):
        p=subprocess.run([sys.executable,"-B",str(HERE/"campaign.py"),"--mode","dev",
                          "--seed",str(C.RESERVED[0])],cwd=HERE.parents[3],
                         capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("CKAD41_ONLY_REGISTERED_DEV",p.stderr)


if __name__=="__main__":
    unittest.main()
