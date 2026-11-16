"""FKP-24 only mock-interface tests. NEVER open real external MDP worlds.

These tests verify the shape and ordering of the public action contract, but
do not constitute real-source admission, training, transfer or scientific proof.
"""
import json
import unittest
from pathlib import Path
import native_public_mdp as gate


class ForbiddenInfo:
    def __getattribute__(self,name):
        raise AssertionError("SOURCE_PRIVATE_INFO_WAS_READ")


class MockCausalEnvironment:
    def __init__(self,*,steps_until_done=3,duplicate_callback=False,
                 corrupt_return=False,callback_state_wrong=False):
        self.steps_until_done=steps_until_done
        self.duplicate_callback=duplicate_callback
        self.corrupt_return=corrupt_return
        self.callback_state_wrong=callback_state_wrong
        self.physical_calls=0
        self.closed=0
        self.seeds=[]
        self.state=0
        self.illegal_access=0

    def reset(self,*,seed):
        self.seeds.append(seed)
        self.state=0
        return (self.state,ForbiddenInfo())

    def do(self,action_callback):
        observed=self.state+(1 if self.callback_state_wrong else 0)
        selected=action_callback(observed)
        if self.duplicate_callback:
            action_callback(observed)
        self.physical_calls+=1
        self.state=int((self.state+selected+1)%2)
        if self.corrupt_return:
            return (self.state,0,False,False)
        return (self.state,int(selected==1),False,
                self.physical_calls>=self.steps_until_done,ForbiddenInfo())

    def see(self,*args):
        self.illegal_access+=1
        raise AssertionError("UNAUTHORIZED_BEHAVIOR_POLICY")

    def ctf_do(self,*args):
        self.illegal_access+=1
        raise AssertionError("COUNTERFACTUAL_ACTION_NOT_ALLOWED")

    def step(self,*args):
        self.illegal_access+=1
        raise AssertionError("DIRECT_SOURCE_STATE_UPDATE_NOT_ALLOWED")

    def close(self):
        self.closed+=1


class StrictRecorder:
    def __init__(self):
        self.before_calls=[]
        self.after_calls=[]
        self.actions=0

    def choose(self,state,history):
        self.before_calls.append((state,history))
        if len(history)!=self.actions:
            raise AssertionError("FUTURE_OBSERVATION_BEFORE_ACTION")
        if history and (type(history[-1]) is not gate.PublicConsequence):
            raise AssertionError("SOURCE_INFO_WAS_LEAKED")
        return int((state+self.actions)%2)

    def observe(self,row):
        if type(row) is not gate.PublicConsequence:
            raise AssertionError("SOURCE_PRIVATE_ENTITY_WAS_PASSED")
        self.after_calls.append(row)
        self.actions+=1


class IndependentCausalSourceContract(unittest.TestCase):
    def test_only_public_real_action_before_consequence(self):
        source=MockCausalEnvironment()
        p=StrictRecorder()
        receipt=gate.public_mechanical_episode(lambda:source,p,seed=996100)
        self.assertEqual(receipt["schema"],"fkp24.native-public-mdp-transcript.v1")
        self.assertEqual(receipt["physical_do_actions"],3)
        self.assertEqual(source.physical_calls,3)
        self.assertEqual(len(p.before_calls),3)
        self.assertEqual(len(p.after_calls),3)
        self.assertEqual(source.closed,1)
        self.assertEqual(source.illegal_access,0)
        self.assertEqual(p.before_calls[0][1],())
        self.assertEqual(p.before_calls[1][1],(p.after_calls[0],))
        self.assertEqual(p.before_calls[2][1],tuple(p.after_calls[:2]))
        self.assertTrue(receipt["ended_by_source"])
        self.assertFalse(receipt["budget_exhausted"])
        self.assertFalse(receipt["counterfactuals_used"])
        self.assertFalse(receipt["forbidden_info_passed_to_policy"])
        self.assertEqual(receipt["public_transitions_sha256"],
                         gate._digest(receipt["public_transitions"]))
        self.assertEqual(source.seeds,[996100])
        self.assertTrue(all("info" not in row and "natural_action" not in row
                            for row in receipt["public_transitions"]))
        self.assertNotIn("info",receipt["public_transitions"][0])

    def test_seal_selected_action_callback_once_without_hidden_label(self):
        for setup in ({"duplicate_callback":True},
                      {"callback_state_wrong":True}):
            with self.subTest(setup=setup):
                env=MockCausalEnvironment(**setup)
                with self.assertRaises(ValueError):
                    gate.public_mechanical_episode(
                        lambda:env,StrictRecorder(),seed=996101)
                self.assertEqual(env.closed,1)

    def test_no_possible_early_reward_or_future_label_to_policy(self):
        env=MockCausalEnvironment(steps_until_done=2)
        model=StrictRecorder()
        rec=gate.public_mechanical_episode(
            lambda:env,model,seed=996102)
        self.assertEqual(rec["physical_do_actions"],2)
        self.assertEqual(len(model.before_calls[0][1]),0)
        self.assertEqual(len(model.before_calls[1][1]),1)
        self.assertEqual(model.before_calls[1][1][-1],model.after_calls[0])
        self.assertNotEqual(model.after_calls[0].after,
                            None)

    def test_budget_stops_without_duplicate_physical_action(self):
        env=MockCausalEnvironment(steps_until_done=99)
        rec=gate.public_mechanical_episode(
            lambda:env,StrictRecorder(),seed=996103,max_actions=2)
        self.assertEqual(env.physical_calls,2)
        self.assertEqual(env.closed,1)
        self.assertFalse(rec["ended_by_source"])
        self.assertTrue(rec["budget_exhausted"])
        self.assertEqual(rec["physical_do_actions"],2)

    def test_unknown_protected_world_fails_before_creating_source(self):
        created=[]
        def factory():
            created.append("OPENED")
            return MockCausalEnvironment()
        for seed in (996500,996531,996600,996663,996104,
                     995500,994500,993500,976500,-1,True,996100.0):
            with self.subTest(seed=seed):
                with self.assertRaises(PermissionError):
                    gate.public_mechanical_episode(factory,StrictRecorder(),seed=seed)
        self.assertEqual(created,[])

    def test_nonbinary_and_future_source_fields_rejected(self):
        for value in (-1,2,1.0,0.0,"1",None,complex(0,1)):
            with self.subTest(value=str(value)):
                with self.assertRaises(ValueError):
                    gate._binary(value,"REWARD")
        for action in (True,1.0,-1,2,"0",None):
            with self.assertRaises(ValueError):
                gate._action(action)
        self.assertEqual(gate._binary(True,"REWARD"),1)
        self.assertEqual(gate._binary(False,"REWARD"),0)

    def test_policy_unsealed_action_never_enters_native_do(self):
        class Malicious(StrictRecorder):
            def choose(self,*a):
                return {"future_reward":1}
        env=MockCausalEnvironment()
        with self.assertRaises(ValueError):
            gate.public_mechanical_episode(lambda:env,Malicious(),seed=996100)
        self.assertEqual(env.physical_calls,0)
        self.assertEqual(env.closed,1)

    def test_invalid_source_schema_does_not_replay_after_affected_action(self):
        env=MockCausalEnvironment(corrupt_return=True)
        with self.assertRaisesRegex(ValueError,"NOT_ONE_NATIVE_PHYSICAL_DO"):
            gate.public_mechanical_episode(lambda:env,StrictRecorder(),seed=996100)
        self.assertEqual(env.physical_calls,1)
        self.assertEqual(env.closed,1)

    def test_no_authorization_to_increase_public_budget(self):
        for bad in (0,-1,33,1000,True,32.0):
            with self.assertRaises(ValueError):
                gate.public_mechanical_episode(
                    lambda:MockCausalEnvironment(),StrictRecorder(),
                    seed=996100,max_actions=bad)

    def test_policy_api_is_narrow_and_mock_reproducible(self):
        a=gate.public_mechanical_episode(
            lambda:MockCausalEnvironment(),gate.FixedPublicPolicy(),seed=996100)
        b=gate.public_mechanical_episode(
            lambda:MockCausalEnvironment(),gate.FixedPublicPolicy(),seed=996100)
        self.assertEqual(a,b)
        self.assertEqual(len(a["public_transitions_sha256"]),64)

    def test_native_source_import_is_lazy_and_never_in_mock_test(self):
        text=Path(gate.__file__).read_text("utf-8")
        self.assertIn("def native_source_factory():",text)
        self.assertIn("LearningRegime.do",text)
        self.assertIn("MDPPCH(max_step=30",text)
        self.assertNotIn("def _private_reward",text)
        self.assertNotIn("env.ctf_do(",text)
        self.assertNotIn("env.see(",text)
        self.assertNotIn("env.step(",text)
        self.assertNotIn("env.env",text)


if __name__=="__main__":
    unittest.main()
