"""CVH10 original authored DTR PCH *signature* tests using mock callbacks only.

NO original causal_gym import, reset, do, first-use or privileged source.
No model-science result or transfer claim from this intentionally mock tape.
"""
from __future__ import annotations

import ast
from collections import namedtuple
from hashlib import sha256
import json
from pathlib import Path
import unittest

import dtr_public_bridge as bridge

HERE=Path(__file__).resolve().parent


class ForbiddenInfo:
    def __getattribute__(self,name):
        raise AssertionError("CVH10_PRIVATE_DTR_INFO_READ_OR_USED")


def local_fake_two_stage(policy,first_state,second_state,final_reward):
    """Mock callback data, NOT independent DTR dynamics or original rewards."""
    b=bridge.SourceFreeDTRPublicBridge(policy)
    self_info=ForbiddenInfo()
    self_before=b.accept_reset((first_state,self_info))
    assert self_before==first_state
    a1=b.stage0_action(first_state)
    row0=b.accept_stage0_result((second_state,0,False,False,self_info))
    a2=b.stage1_action(first_state,a1,second_state)
    row1=b.accept_stage1_result((None,final_reward,True,False,self_info))
    return b,(row0,row1),(a1,a2)


class DTRSourceFreePublicTests(unittest.TestCase):
    def test_original_distinct_source_signature_static_sha_and_firstuse(self):
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(p["source"]["commit"],bridge.SOURCE_SHA)
        self.assertEqual(p["source"]["blob"],bridge.DTR_BLOB)
        self.assertEqual(bridge.SOURCE_SHA,
                         "c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(bridge.DTR_BLOB,
                         "6af2371dce21804140ea141ccb7be14e003ba275")
        self.assertEqual(p["parent"]["sha"],
                         "07b213891dc6424b9ea1aa685b0ff77014f49080")
        self.assertFalse(p["future_science"]["source_first_use_approved_to_run_now"])
        self.assertEqual(p["future_science"]["original_seed_ids_verified"],[])
        self.assertIsNone(p["future_science"]["original_source_owner_lease"])
        self.assertEqual(bridge.original_source_authority_preflight()["new_original_DTR_do_calls"],0)
        self.assertFalse(bridge.original_source_authority_preflight()["first_use_execution_allowed"])

    def test_native_tokenless_delayed_terminal_reward_two_stages_and_info_unread(self):
        from public_policy import PublicEarnedPolicy
        policy=PublicEarnedPolicy(min_support=2)
        actor,events,actions=local_fake_two_stage(policy,1,0,1)
        self.assertEqual(actor.phase,"completed")
        self.assertEqual(events[0],bridge.PublicConsequence(1,actions[0],0,0,False,False))
        self.assertEqual(events[1],bridge.PublicConsequence(0,actions[1],1,0,True,False))
        self.assertEqual(policy.memory.seen,2)
        self.assertIsNone(policy.memory.previous_after)
        self.assertEqual(sum(policy.attempts),2)
        self.assertEqual(len(bridge.PUBLIC_FIELDS),6)
        self.assertEqual(tuple(events[0]._fields),tuple(bridge.PUBLIC_FIELDS))
        self.assertEqual(policy.snapshot(),
                         PublicEarnedPolicy.restore(policy.snapshot()).snapshot())
        r=actor.completed_public_only_receipt()
        self.assertFalse(r["source_first_use_owner_verified"])
        self.assertEqual(r["new_original_source_reset_or_do_by_this_module"],0)
        self.assertFalse(r["terminal_after_is_observation"])
        self.assertEqual(r["public_earned_rewards"],[0,1])
        self.assertEqual(r["public_action_count"],2)
        self.assertEqual(r["public_transitions_sha256"],bridge.public_report_digest(events))

    def test_fourcell_sourcefree_and_explorer_unchanged_policy_interfaces(self):
        from fourcell_control import FourCellEarnedPolicy
        from recurrent_control import SeededPublicExplorer
        for policy in (FourCellEarnedPolicy(),SeededPublicExplorer(1777)):
            actor,events,actions=local_fake_two_stage(policy,0,1,0)
            self.assertEqual(len(events),2)
            self.assertEqual(policy.seen,2)
            self.assertEqual(actor.completed_public_only_receipt()["public_earned_rewards"],[0,0])
            self.assertEqual(type(policy).restore(policy.snapshot()).snapshot(),policy.snapshot())

    def test_recurrent_unchanged_public_policy_fitted_then_DTR_mock_transfer_interface(self):
        # Fit the already-qualified recurrent control only on the frozen CVH07
        # non-DTR toy episodes: this tests code interface not scientific transfer.
        from recurrent_control import ConventionalPublicRNN,training_tape
        model=ConventionalPublicRNN()
        original=tuple(training_tape(i) for i in range(101,197))
        before,after=model.fit(original)
        self.assertLess(after,before)
        actor,events,_=local_fake_two_stage(model,1,1,1)
        self.assertEqual(len(events),2)
        self.assertEqual(model.seen,2)
        self.assertEqual(type(model).restore(model.snapshot()).snapshot(),model.snapshot())
        self.assertTrue(actor.completed_public_only_receipt()["terminal_after_placeholder"]==0)

    def test_same_realistic_two_stage_public_grammar_accepted_as_64_training_episodes(self):
        # The 64 events here are MOCKS; this proves CVH08 can ingest terminal
        # public 'None' normalization without changing any native learner.
        from public_policy import PublicEarnedPolicy
        from public_training import validate_completed_train
        policy=PublicEarnedPolicy()
        tapes=[]
        for index in range(64):
            actor,rows,actions=local_fake_two_stage(
                policy,index%2,(index+1)%2,index%2)
            tapes.append(rows)
        clean=validate_completed_train(tuple(tapes))
        self.assertEqual(len(clean),64)
        self.assertEqual(sum(len(x) for x in clean),128)
        self.assertTrue(all(ep[0].terminated is False and ep[1].terminated is True
                            and ep[1].after==bridge.TERMINAL_ABSENT_OBSERVATION_SENTINEL
                            for ep in clean))
        self.assertEqual(policy.memory.seen,128)
        self.assertEqual(sum(policy.attempts),128)

    def test_action_is_sealed_before_result_and_unknown_outcome_cannot_replay(self):
        from public_policy import PublicEarnedPolicy
        policy=PublicEarnedPolicy()
        b=bridge.SourceFreeDTRPublicBridge(policy)
        b.accept_reset((0,ForbiddenInfo()))
        with self.assertRaises(PermissionError):
            b.completed_public_only_receipt()
        with self.assertRaises(PermissionError):
            b.stage1_action(0,0,0)
        first=b.stage0_action(0)
        with self.assertRaises(PermissionError):
            b.stage0_action(0)
        with self.assertRaises(PermissionError):
            b.accept_reset((0,ForbiddenInfo()))
        with self.assertRaises(PermissionError):
            b.completed_public_only_receipt()
        self.assertEqual(sum(policy.attempts),0)
        with self.assertRaises(ValueError):
            b.accept_stage0_result((None,0,False,False,ForbiddenInfo()))
        with self.assertRaises(PermissionError):
            b.stage0_action(0)
        self.assertEqual(sum(policy.attempts),0)

    def test_early_terminal_at_first_action_denied_no_model_commit(self):
        from public_policy import PublicEarnedPolicy
        policy=PublicEarnedPolicy()
        b=bridge.SourceFreeDTRPublicBridge(policy)
        b.accept_reset((1,ForbiddenInfo()))
        a=b.stage0_action(1)
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_STAGE0"):
            b.accept_stage0_result((1,0,True,False,ForbiddenInfo()))
        self.assertEqual(policy.memory.seen,0)
        with self.assertRaises(PermissionError):
            b.stage1_action(1,a,1)

    def test_nonzero_stage0_reward_denied_and_no_retry(self):
        from public_policy import PublicEarnedPolicy
        policy=PublicEarnedPolicy()
        b=bridge.SourceFreeDTRPublicBridge(policy)
        b.accept_reset((0,ForbiddenInfo()))
        b.stage0_action(0)
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_STAGE0"):
            b.accept_stage0_result((1,1,False,False,ForbiddenInfo()))
        self.assertEqual(policy.memory.seen,0)
        with self.assertRaises(PermissionError):
            b.stage0_action(0)

    def test_repeated_incorrect_source_callbacks_deny_unsafe_replay(self):
        from public_policy import PublicEarnedPolicy
        b=bridge.SourceFreeDTRPublicBridge(PublicEarnedPolicy())
        b.accept_reset((0,ForbiddenInfo()))
        with self.assertRaisesRegex(ValueError,"STATE_MISMATCH"):
            b.stage0_action(1)
        with self.assertRaises(PermissionError):
            b.stage0_action(0)
        b=bridge.SourceFreeDTRPublicBridge(PublicEarnedPolicy())
        b.accept_reset((0,ForbiddenInfo()))
        first=b.stage0_action(0)
        b.accept_stage0_result((1,0,False,False,ForbiddenInfo()))
        with self.assertRaisesRegex(ValueError,"CALLBACK_HISTORY_DRIFT"):
            b.stage1_action(0,1-first,1)
        with self.assertRaises(PermissionError):
            b.stage1_action(0,first,1)

    def test_stage1_actual_terminal_requires_none_flag_and_binary_reward(self):
        from public_policy import PublicEarnedPolicy
        for bad,term,trunc in [(1,True,False),(0,True,False),
                               (None,False,False),(None,True,True),
                               (None,True,False)]:
            b=bridge.SourceFreeDTRPublicBridge(PublicEarnedPolicy())
            b.accept_reset((0,ForbiddenInfo()))
            a=b.stage0_action(0)
            b.accept_stage0_result((1,0,False,False,ForbiddenInfo()))
            b.stage1_action(0,a,1)
            if bad is None and term and not trunc:
                b.accept_stage1_result((None,1,True,False,ForbiddenInfo()))
                self.assertEqual(b.phase,"completed")
                continue
            with self.assertRaises(ValueError):
                b.accept_stage1_result((bad,1,term,trunc,ForbiddenInfo()))
            with self.assertRaises(PermissionError):
                b.completed_public_only_receipt()

    def test_source_private_extra_and_malformed_public_results_denied(self):
        from public_policy import PublicEarnedPolicy
        b=bridge.SourceFreeDTRPublicBridge(PublicEarnedPolicy())
        with self.assertRaises(ValueError):
            b.accept_reset((0,1,2))
        b.accept_reset((0,ForbiddenInfo()))
        b.stage0_action(0)
        with self.assertRaises(ValueError):
            b.accept_stage0_result((1,0,False,False,ForbiddenInfo(),99))
        with self.assertRaises(PermissionError):
            b.stage1_action(0,0,1)

    def test_unauthorized_source_and_replay_still_blocked_in_prior_owner_manifest(self):
        pre=bridge.original_source_authority_preflight()
        self.assertEqual(pre["owner_qualified_virgin_seeds"],0)
        self.assertEqual(pre["new_original_DTR_reset_calls"],0)
        self.assertEqual(pre["new_original_DTR_do_calls"],0)
        self.assertEqual(pre["user_authorized_original_action_ceiling"],13312)
        self.assertFalse(pre["first_use_execution_allowed"])
        self.assertFalse(pre["native_scientific_superiority_verified"])
        source=(HERE.parent/"FKP-24"/"native_public_mdp.py").read_text()
        self.assertIn("MECHANICAL_PUBLIC_SEEDS=(996100,996101,996102,996103)",source)
        self.assertIn('raise PermissionError("FKP24_UNAUTHORIZED_OR_PROTECTED_WORLD")',source)

    def test_no_call_import_to_real_environment_or_source_firstuse_runner(self):
        src=(HERE/"dtr_public_bridge.py").read_text()
        py=ast.parse(src)
        imports=[n.names[0].name for n in ast.walk(py)
                 if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertTrue(all("causal_gym" not in k for k in imports))
        self.assertFalse((HERE/"real_original_source_runner.py").exists())
        self.assertFalse((HERE/"owner_firstuse_seed_lease.json").exists())
        self.assertFalse((HERE/"original_source_event_tape.json").exists())
        self.assertTrue(all(not(isinstance(n,ast.Call) and
             isinstance(n.func,ast.Attribute) and n.func.attr in ("do","reset"))
             for n in ast.walk(py)))
        self.assertEqual(bridge.MAX_PHYSICAL_ACTIONS,2)


if __name__=="__main__":
    unittest.main()
