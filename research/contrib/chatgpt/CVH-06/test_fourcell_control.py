"""CVH-06 source-free pre-qualification: no original environment actions."""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from fourcell_control import (
    FourCellEarnedPolicy, PublicEarnedPolicy,
    independent_fourcell_public_batch, _canonical
)

HERE=Path(__file__).resolve().parent
FIELDS=("before","action","reward","after","terminated","truncated")
Row=namedtuple("PublicConsequence",FIELDS)


def toy_action_step(seed, index, state, action):
    """Fixture-only computation (NOT any CausalGym world or source)."""
    if type(seed) is not int or seed not in (1,2,3,4,5,6):
        raise ValueError("CVH06_NO_EXTERNAL_SOURCE_SEED")
    if type(state) is not int or state not in (0,1):
        raise ValueError("CVH06_NONPUBLIC_TOY_STATE")
    if type(action) is not int or action not in (0,1):
        raise ValueError("CVH06_BAD_ACTION")
    n=state ^ action ^ ((index+seed)&1)
    r=int(index>=2 and (index+action+seed)%3==0)
    return Row(state,action,r,n,False,index==5)


def toy_episode(seed,policy,*,split_at=None):
    if type(seed) is not int or seed not in (1,2,3,4,5,6):
        raise PermissionError("CVH06_ONLY_MOCK_SEEDS_ONE_TO_SIX")
    state=seed%2;history=[]
    for index in range(6):
        selected=policy.choose(state,tuple(history))
        row=toy_action_step(seed,index,state,selected)
        policy.observe(row)
        history.append(row)
        state=row.after
        if split_at is not None and index+1==split_at:
            policy=type(policy).restore(policy.snapshot())
    return policy,tuple(history)


class FourCellPublicControlTests(unittest.TestCase):
    def test_sourcefree_fourstep_credit_matched_independent_exact_batch_every_step(self):
        policy=FourCellEarnedPolicy()
        entire=[]
        self.assertEqual(policy.count,[0,0,0,0])
        for seed in (1,2,3,4,5,6):
            state=seed%2;history=[]
            for index in range(6):
                chosen=policy.choose(state,tuple(history))
                row=toy_action_step(seed,index,state,chosen)
                policy.observe(row)
                entire.append(row);history.append(row)
                self.assertEqual((policy.count,policy.total),
                                 independent_fourcell_public_batch(entire))
                self.assertEqual(sum(policy.count)+len(policy.pending),policy.seen)
                self.assertEqual(sum(policy.attempts),policy.seen)
                state=row.after
        self.assertEqual(policy.seen,36)
        self.assertEqual(sum(policy.count),36)
        self.assertEqual(len(policy.pending),0)
        self.assertEqual(len(policy.episode_history),0)
        self.assertTrue(policy.snapshot())

    def test_strict_action_sealed_before_future_event(self):
        p=FourCellEarnedPolicy()
        a=p.choose(1,())
        self.assertIn(a,(0,1))
        with self.assertRaisesRegex(ValueError,"NO_REPLAY"):
            p.choose(1,())
        with self.assertRaisesRegex(ValueError,"CANNOT_COLD"):
            p.snapshot()
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_REPLY"):
            p.observe(Row(1,1-a,0,0,False,False))
        self.assertEqual(p.seen,0)
        self.assertEqual(sum(p.attempts),0)
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_REPLY"):
            p.observe(Row(0,a,0,1,False,False))
        # The source has not acted; only the exact sealed action may ACK.
        p.observe(Row(1,a,1,0,False,False))
        self.assertEqual(p.seen,1)
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_REPLY"):
            p.observe(Row(1,a,1,0,False,False))

    def test_sourceprivate_and_malformed_tuples_rejected_without_learning(self):
        p=FourCellEarnedPolicy()
        a=p.choose(0,())
        private=namedtuple("BadSource",FIELDS+("hidden_confounder",))
        bad=private(0,a,1,1,False,False,99)
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELDS_ONLY"):
            p.observe(bad)
        self.assertEqual(p.seen,0)
        with self.assertRaises(ValueError):
            p.observe(Row(0,a,2,1,False,False))
        with self.assertRaises(ValueError):
            p.observe(Row(0,a,1,1,1,False))
        self.assertEqual(p.seen,0)
        with self.assertRaises(ValueError):
            p.observe(Row(0,a,1,1,True,True))
        p.observe(Row(0,a,0,1,False,False))
        self.assertEqual(p.seen,1)

    def test_inherited_cvh02_native_policy_and_new_conventional_matched_mock_actions(self):
        native=PublicEarnedPolicy(min_support=2)
        conventional=FourCellEarnedPolicy(min_support=2)
        transcripts={"native":[],"fourcell":[]}
        for seed in range(1,7):
            native,ns=toy_episode(seed,native)
            conventional,cs=toy_episode(seed,conventional)
            self.assertEqual(len(ns),6)
            self.assertEqual(len(cs),6)
            self.assertTrue(ns[-1].truncated)
            self.assertTrue(cs[-1].truncated)
            transcripts["native"].append(ns)
            transcripts["fourcell"].append(cs)
        self.assertEqual(native.memory.seen,36)
        self.assertEqual(conventional.seen,36)
        self.assertEqual(native.memory.seen,conventional.seen)
        self.assertTrue(native.snapshot())
        self.assertTrue(conventional.snapshot())
        self.assertEqual(native.snapshot(),PublicEarnedPolicy.restore(native.snapshot()).snapshot())
        self.assertEqual(conventional.snapshot(),FourCellEarnedPolicy.restore(conventional.snapshot()).snapshot())
        # These are fabricated action-dependent fixtures, not original-source
        # science; do not treat any toy reward difference as a result.

    def test_cold_restoration_during_current_mock_episode_is_byte_identical(self):
        cold=FourCellEarnedPolicy()
        continuous=FourCellEarnedPolicy()
        seed=3;state=seed%2;public=[]
        for idx in range(6):
            a=continuous.choose(state,tuple(public))
            b=cold.choose(state,tuple(public))
            self.assertEqual(a,b)
            row=toy_action_step(seed,idx,state,a)
            continuous.observe(row)
            cold.observe(row)
            public.append(row);state=row.after
            if idx in (1,2,4):
                blob=cold.snapshot()
                cold=FourCellEarnedPolicy.restore(blob)
                self.assertEqual(cold.snapshot(),blob)
        self.assertEqual(cold.snapshot(),continuous.snapshot())

    def test_opaque_source_seeds_and_firstuse_denied_without_owner_cohort(self):
        doc=json.loads((HERE/"source_first_use_NOT_AUTHORIZED.json").read_text())
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(doc["state"],"NOT_AUTHORIZED_NO_ORIGINAL_SOURCE_ACTIONS")
        self.assertEqual(doc["actual_source_interventions_this_gate"],0)
        self.assertFalse(p["authority"]["new_original_source_firstuse_approved"])
        self.assertFalse(p["source_admission"]["original_first_use_runnable"])
        self.assertEqual(doc["train_seed_ids"],[])
        self.assertEqual(set(doc["held_seed_ids_by_arm"]),{"native","fourcell","recurrent","exploration"})
        self.assertEqual(set(doc["transfer_seed_ids_by_arm"]),{"native","fourcell","recurrent","exploration"})
        self.assertTrue(all(not x for x in doc["held_seed_ids_by_arm"].values()))
        self.assertTrue(all(not x for x in doc["transfer_seed_ids_by_arm"].values()))
        self.assertEqual(doc["consumed_previous_seed_ids"],[996100,996101,996102,996103])
        self.assertEqual(doc["max_source_interventions"],13312)
        self.assertEqual(p["future_science"]["maximum_total_original_do"],13312)
        for seed in (996100,996103,996500,996531,996600,996663):
            with self.assertRaises(PermissionError):
                toy_episode(seed,FourCellEarnedPolicy())

    def test_public_context_only_not_hidden_and_source_boundary_unchanged(self):
        body=(HERE/"fourcell_control.py").read_text()
        self.assertNotIn("import causal_gym",body)
        self.assertNotIn("source_factory(",body)
        self.assertNotIn("env.reset(",body)
        self.assertNotIn("env.do(",body)
        self.assertNotIn("ctf_do(",body)
        self.assertNotIn("requests.get(",body)
        self.assertNotIn("subprocess.",body)
        self.assertIn("from public_policy import _event, PublicEarnedPolicy",body)
        self.assertIn("independent_fourcell_public_batch",body)

    def test_reject_snapshot_tamper_and_semantic_rehash(self):
        p=FourCellEarnedPolicy()
        for seed in (1,2):
            p,_=toy_episode(seed,p)
        snapshot=p.snapshot()
        restored=FourCellEarnedPolicy.restore(snapshot)
        self.assertEqual(restored.snapshot(),snapshot)
        j=json.loads(snapshot)
        j["payload"]["count"][0]+=1
        with self.assertRaisesRegex(ValueError,"COLD_REJECTED"):
            FourCellEarnedPolicy.restore(_canonical(j))
        j["sha256"]=sha256(_canonical(j["payload"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"COLD_REJECTED"):
            FourCellEarnedPolicy.restore(_canonical(j))

    def test_unsupported_conventional_estimate_stays_unknown_until_real_observations(self):
        p=FourCellEarnedPolicy(min_support=2)
        self.assertIsNone(p.estimate(0,0))
        self.assertIsNone(p.estimate(1,1))
        with self.assertRaises(ValueError):
            p.estimate(2,0)
        self.assertEqual(p.count,[0]*4)
        self.assertEqual(p.total,[0]*4)

    def test_invalid_start_or_history_refuses_without_unsafe_replay(self):
        p=FourCellEarnedPolicy()
        for bad in (True,2,-1,None):
            with self.assertRaises(ValueError):
                p.choose(bad,())
        with self.assertRaises(ValueError):
            p.choose(0,[])
        with self.assertRaises(ValueError):
            p.choose(0,(Row(0,0,0,0,False,False),))
        a=p.choose(0,())
        p.observe(Row(0,a,0,1,False,False))
        with self.assertRaisesRegex(ValueError,"CONTINUITY"):
            p.choose(0,(Row(0,a,0,1,False,False),))
        with self.assertRaisesRegex(ValueError,"HISTORY_DRIFT"):
            p.choose(1,())

    def test_preserved_qualification_result_unchanged_and_not_science(self):
        import qualify_sourcefree as smoke
        verified=json.loads((HERE/"result.json").read_text())
        self.assertEqual(smoke.qualify(),verified)
        self.assertEqual(verified["original_env_do_calls"],0)
        self.assertFalse(verified["original_first_use_authorized"])
        self.assertFalse(verified["scientific_pass"])
        self.assertFalse(verified["fully_trained_recurrent_science_control_ready"])
        self.assertEqual(verified["arms"]["native"]["mock_action_count"],36)
        self.assertEqual(verified["arms"]["conventional"]["mock_action_count"],36)
        self.assertNotEqual(verified["arms"]["native"]["model_checkpoint_sha256"],
                            verified["arms"]["conventional"]["model_checkpoint_sha256"])

    def test_same_episode_toy_actions_cannot_replay_real_source_firstuse(self):
        original_approved=set([996100,996101,996102,996103])
        self.assertTrue(original_approved.isdisjoint(set(range(1,7))))
        self.assertTrue(all(seed not in original_approved for seed in range(1,7)))
        self.assertFalse((HERE/"real_original_source_runner.py").exists())
        self.assertFalse((HERE/"source_action_receipt.json").exists())


if __name__=="__main__":
    unittest.main()
