"""Strictly source-free tests: no MiniGrid import, reset, or step."""
import gzip, hashlib, tempfile, unittest
from pathlib import Path
from public_scaffold import PublicView, MISSION, ProtocolBlocked
from source_preflight import (SEEDS, SOURCE_BLOBS, UPSTREAM, encode_row,
                              deterministic_gzip, verify_checkout)

class SourcePreflightOfflineTests(unittest.TestCase):
    def _public(self):
        arr=[[[0,0,0] for _ in range(7)] for _ in range(7)]
        return PublicView.from_observation({"image":arr,"direction":0,"mission":MISSION})
    def test_static_seed_count_and_disjoint_roles(self):
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(SEEDS,tuple(3_000_000+i for i in range(16)))
        self.assertFalse(set(SEEDS)&{3_100_000+100*c+e for c in range(1,25) for e in range(32)})
        self.assertFalse(set(SEEDS)&{3_200_000+100*c+e for c in range(1,9) for e in range(16)})
        self.assertFalse(set(SEEDS)&{3_300_000+100*c+e for c in range(1,17) for e in range(16)})
    def test_expected_source_blob_names_and_sha(self):
        self.assertEqual(len(UPSTREAM),40)
        self.assertEqual(set(SOURCE_BLOBS),{ "minigrid/envs/memory.py", "minigrid/__init__.py", "minigrid/minigrid_env.py" })
        self.assertTrue(all(len(x)==40 for x in SOURCE_BLOBS.values()))
    def test_original_source_checker_rejects_noncheckout(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(Exception):
                verify_checkout(Path(d))
    def test_original_public_row_roundtrip_and_exact_image(self):
        s=self._public()
        row=encode_row(SEEDS[0],1,s,2,s,0.0,False,False,"")
        self.assertIn(s.image_bytes.hex().encode(),row)
        gz=deterministic_gzip(row)
        self.assertEqual(gzip.decompress(gz),row)
        self.assertEqual(gz,deterministic_gzip(row))
        self.assertEqual(hashlib.sha256(gz).hexdigest(),hashlib.sha256(deterministic_gzip(row)).hexdigest())
    def test_no_extra_oracle_information_in_trace(self):
        s=self._public()
        row=encode_row(SEEDS[1],2,s,0,s,0.,False,False,"")
        for denied in (b"success_pos",b"failure_pos",b"agent_pos",b"unwrapped",b"hidden_branch"):
            self.assertNotIn(denied,row)

if __name__=="__main__": unittest.main()

# Additional source-free harness-interface tests. These scripted fake responses
# are NOT a simulator, benchmark source, or evidence of environment feasibility.
class ScriptedHarnessTests(unittest.TestCase):
    def make_obs(self, cue=False, fork=False):
        from public_scaffold import KEY, BALL
        image=[[[0,0,0] for _ in range(7)] for _ in range(7)]
        if cue: image[3][5][0]=KEY
        if fork: image[3][4][0]=BALL
        return {"image":image,"direction":3,"mission":MISSION}
    def test_actual_harness_emits_fork_event_into_public_trace(self):
        import json
        from unittest.mock import patch
        import source_preflight as sp
        from public_scaffold import Step
        owner=self
        class Nav:
            def __init__(self): self.calls=0
            def advance(self, obs):
                self.calls+=1
                if self.calls==1: return Step(2,"PUBLIC_CUE_EXPOSURE")
                if self.calls==2: return Step(None,"PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")
                return Step(2)
            def commit(self, choice): self.choice=choice
        class Policy:
            def __init__(self): self.events=[]
            def observe(self, view,event): self.events.append(event)
            def choose(self): return 'north'
        class Env:
            def __init__(self): self.steps=0
            def reset(self,seed):return owner.make_obs(cue=True),{}
            def step(self,action):
                self.steps+=1
                if self.steps==1:return owner.make_obs(fork=True),0.,False,False,{}
                return owner.make_obs(),0.8,True,False,{}
            def close(self):pass
        class Gym:
            def make(self,name):return Env()
        with patch.object(sp,'PublicOnlyNavigation',Nav), patch.object(sp,'PublicRuleSession',Policy):
            r=sp.preflight_episode(Gym(),SEEDS[0])
        self.assertEqual(len(r['rows']),2)
        self.assertEqual(json.loads(r['rows'][0])['public_stage_event'],'PUBLIC_CUE_EXPOSURE')
        self.assertEqual(json.loads(r['rows'][1])['public_stage_event'],'PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE')
    def test_failed_scripted_episode_retains_attempted_public_row(self):
        from unittest.mock import patch
        import source_preflight as sp
        from public_scaffold import Step
        owner=self
        class Nav:
            def advance(self,obs): return Step(2)
        class Env:
            def reset(self,seed):return owner.make_obs(),{}
            def step(self,action):return owner.make_obs(),0.0,True,False,{}
            def close(self):pass
        class Gym:
            def make(self,name):return Env()
        with patch.object(sp,'PublicOnlyNavigation',Nav):
            with self.assertRaisesRegex(ProtocolBlocked,'ORIGINAL_PUBLIC_RULE_DID_NOT_SUCCEED') as ex:
                sp.preflight_episode(Gym(),SEEDS[0])
        self.assertEqual(len(ex.exception.original_rows),1)


class CkbOwnerAdmissionNegativeTests(unittest.TestCase):
    """New tests must be source-free; no actual original-source execution."""
    def test_original_collector_denies_before_any_io(self):
        from unittest.mock import patch
        import source_preflight as sp
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'not-created'
            with patch.object(sp,'verify_checkout',side_effect=AssertionError('unauthorized checkout')):
                with self.assertRaisesRegex(ProtocolBlocked,'CKB_OWNER_LEASE_VERIFIER_NOT_INSTALLED'):
                    sp.collect_16_original(Path(d),output)
            self.assertFalse(output.exists())
    def test_unqualified_cli_original_attempt_fails_before_import_or_output(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'must-not-create'
            proc=subprocess.run([sys.executable,str(Path(__file__).with_name('source_preflight.py')),
                '--run-original-source','--pinned-source-checkout',d,'--output',str(output)],
                capture_output=True,text=True,check=False)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('CKB_OWNER_LEASE_VERIFIER_NOT_INSTALLED',proc.stderr)
            self.assertFalse(output.exists())
    def test_original_collector_disallows_caller_supplied_paths_as_permission(self):
        import source_preflight as sp
        for raw in ('.','/tmp/any','C:/fake/trusted'):
            with self.assertRaisesRegex(ProtocolBlocked,'CKB_OWNER_LEASE_VERIFIER_NOT_INSTALLED'):
                sp.collect_16_original(Path(raw),Path(raw)/'output')
    def test_kernel_disallows_any_unlisted_seed_before_gym_make(self):
        import source_preflight as sp
        class NoGym:
            def make(self,*a,**k):raise AssertionError('unexpected original env make')
        for seed in (True,0,3_000_016,3_100_100,3_200_100,3_300_100,-1):
            with self.assertRaisesRegex(ProtocolBlocked,'PREFLIGHT_SEED_NOT_IN_PROPOSED_INVENTORY'):
                sp.preflight_episode(NoGym(),seed)
    def test_static_inspection_remains_available(self):
        import subprocess,sys,json
        proc=subprocess.run([sys.executable,str(Path(__file__).with_name('source_preflight.py')),
                '--inspect-spec-only'],capture_output=True,text=True,check=True)
        info=json.loads(proc.stdout)
        self.assertEqual(info['status'],'STATIC_SPEC_ONLY_NO_ENV_IMPORT_OR_RESET')
        self.assertEqual(info['preflight_seeds'],list(SEEDS))
