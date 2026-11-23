"""No original world construction: source-free native evidence component tests."""
import hashlib
import json
import unittest
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from yggdrasil.native_grid5_ingress import SCHEMA, SOURCE_MODE, canonical


def receipt(step, act=0, before=(0, 0), after=(0, 0), episode='a'*64,
            sid=None, reward=0, term=None):
    if term is None:
        term = (step == 49)
    request = {'episode_id': episode, 'step_index': step,
               'public_state': list(before), 'public_action': act}
    obj = {**request, 'schema': SCHEMA, 'source_mode': SOURCE_MODE,
           'source_id': sid or f'{step+1:064x}', 'next_state': list(after),
           'reward': reward, 'terminated': term, 'truncated': term}
    raw = canonical(obj)
    return request, raw, hashlib.sha256(raw).hexdigest()


def persist_and_restore(obj):
    raw = obj.checkpoint()
    return NativeGrid5Evidence.restore(raw, hashlib.sha256(raw).hexdigest())


class NativeGrid5Tests(unittest.TestCase):
    def test_empty_plan_is_stable(self):
        self.assertEqual(NativeGrid5Evidence().public_plan([0, 0], episode_id='a'*64),
                         {'source_mode':SOURCE_MODE,'public_action':0,
                          'observed_next_state':None,'witness_count':0})

    def test_observation_immutable_and_witness_only(self):
        start = NativeGrid5Evidence()
        nextobj = start.observe_public_receipt(*receipt(0, after=(1, 0)))
        self.assertEqual(len(start._rows), 0)
        self.assertEqual(len(nextobj._rows), 1)
        self.assertEqual(nextobj.public_plan([0, 0], episode_id='a'*64)['public_action'], 1)
        self.assertEqual(nextobj.public_plan([1, 0], episode_id='a'*64)['public_action'], 0)
        self.assertIsNone(nextobj.public_plan([0, 0], episode_id='a'*64)['observed_next_state'])

    def test_idempotent_identical_receipt(self):
        one = receipt(0)
        obj = NativeGrid5Evidence().observe_public_receipt(*one)
        self.assertIs(obj.observe_public_receipt(*one), obj)

    def test_conflicting_source_id_rejected(self):
        one = receipt(0)
        obj = NativeGrid5Evidence().observe_public_receipt(*one)
        req,raw,pin = receipt(1, before=(0, 0), after=(1, 0), sid='1'.zfill(64))
        with self.assertRaisesRegex(ValueError, 'GRID5_SOURCE_REPLAY_CONFLICT'):
            obj.observe_public_receipt(req,raw,pin)

    def test_cold_restores_identically(self):
        obj=NativeGrid5Evidence()
        obj=obj.observe_public_receipt(*receipt(0,after=(1, 0)))
        obj=obj.observe_public_receipt(*receipt(1,act=2,before=(1, 0),after=(1, 1)))
        restored=persist_and_restore(obj)
        self.assertEqual(restored.checkpoint(),obj.checkpoint())
        self.assertEqual(restored.public_plan([1, 0], episode_id='a'*64),obj.public_plan([1, 0], episode_id='a'*64))

    def test_all_five_action_labels(self):
        obj = NativeGrid5Evidence()
        # Source-realizable five-action sequence, identity permutation.
        # No private action-role labels are supplied to the evidence API.
        states = ((0,0),(1,0),(0,0),(0,1),(0,0),(0,0))
        for action in range(5):
            obj=obj.observe_public_receipt(*receipt(
                action,act=action,before=states[action],after=states[action+1]))
        self.assertEqual(
            [obj.public_forecast(list(states[a]), a, episode_id='a'*64)
             for a in range(5)], [list(s) for s in states[1:]])
        self.assertEqual(obj.public_plan([0,0], episode_id='a'*64)['public_action'],1)
        self.assertIsNone(obj.public_plan([0,0], episode_id='a'*64)['observed_next_state'])
        self.assertEqual(obj.public_plan([0,0], episode_id='a'*64)['witness_count'],0)
        self.assertEqual(
            persist_and_restore(obj).public_plan([0,0], episode_id='a'*64),
            obj.public_plan([0,0], episode_id='a'*64))

    def test_contradictory_same_context_forces_abstention(self):
        obj=NativeGrid5Evidence()
        obj=obj.observe_public_receipt(*receipt(0,act=0,after=(1,0)))
        obj=obj.observe_public_receipt(*receipt(1,act=0,before=(1,0),after=(0,0)))
        obj=obj.observe_public_receipt(*receipt(2,act=0,before=(0,0),after=(0,0)))
        for a in range(1,5):
            obj=obj.observe_public_receipt(*receipt(2+a,act=a,before=(0,0),after=(0,0)))
        self.assertIsNone(obj.public_forecast([0,0], 0, episode_id='a'*64))
        self.assertEqual(persist_and_restore(obj).public_forecast([0,0], 0, episode_id='a'*64), obj.public_forecast([0,0], 0, episode_id='a'*64))

    def test_source_mode_not_original(self):
        r=receipt(0)
        data=json.loads(r[1]);data['source_mode']='owner_real_source'
        raw=canonical(data)
        with self.assertRaises(ValueError):
            NativeGrid5Evidence().observe_public_receipt(r[0],raw,hashlib.sha256(raw).hexdigest())

    def test_forced_hidden_role_rejected(self):
        req,raw,pin=receipt(0)
        obj=json.loads(raw);obj['perm_idx']=13
        raw=canonical(obj)
        with self.assertRaises(ValueError):
            NativeGrid5Evidence().observe_public_receipt(req,raw,hashlib.sha256(raw).hexdigest())

    def test_checkpoint_modified_outcome_rejected_even_with_new_outer_pin(self):
        obj=NativeGrid5Evidence().observe_public_receipt(*receipt(0,after=(1,0)))
        checkpoint=json.loads(obj.checkpoint())
        checkpoint['records'][0][5]=[0,0]
        forged=canonical(checkpoint)
        with self.assertRaises(ValueError):
            NativeGrid5Evidence.restore(forged,hashlib.sha256(forged).hexdigest())

    def test_checkpoint_mutated_flags_rejected(self):
        obj=NativeGrid5Evidence().observe_public_receipt(*receipt(0))
        for k in ('native_accepted','scientific_pass'):
            checkpoint=json.loads(obj.checkpoint())
            checkpoint[k]=True
            forged=canonical(checkpoint)
            with self.assertRaises(ValueError):
                NativeGrid5Evidence.restore(forged,hashlib.sha256(forged).hexdigest())

    def test_checkpoint_duplicate_source_and_noncanonical_rejected(self):
        obj=NativeGrid5Evidence().observe_public_receipt(*receipt(0))
        checkpoint=json.loads(obj.checkpoint());checkpoint['records'].append(checkpoint['records'][0])
        forged=canonical(checkpoint)
        with self.assertRaises(ValueError):
            NativeGrid5Evidence.restore(forged,hashlib.sha256(forged).hexdigest())
        raw=obj.checkpoint()+b' '
        with self.assertRaises(ValueError):
            NativeGrid5Evidence.restore(raw,hashlib.sha256(raw).hexdigest())

    def test_contiguous_50_step_then_distinct_episode(self):
        obj=NativeGrid5Evidence()
        for i in range(50):
            obj=obj.observe_public_receipt(*receipt(i))
        obj=obj.observe_public_receipt(*receipt(0,episode='b'*64,sid='f'*64))
        self.assertEqual(len(persist_and_restore(obj)._rows),51)

    def test_premature_reset_and_ended_same_episode_rejected(self):
        one=NativeGrid5Evidence().observe_public_receipt(*receipt(0))
        with self.assertRaises(ValueError):
            one.observe_public_receipt(*receipt(0,episode='b'*64,sid='f'*64))
        end=NativeGrid5Evidence()
        for i in range(50):end=end.observe_public_receipt(*receipt(i))
        with self.assertRaises(ValueError):
            end.observe_public_receipt(*receipt(0,sid='f'*64))

    def test_state_and_step_sequence_mismatch_rejected(self):
        first=NativeGrid5Evidence().observe_public_receipt(*receipt(0,after=(1,0)))
        for nxt in (receipt(2,before=(1,0)),receipt(1,before=(0,0))):
            with self.assertRaises(ValueError):first.observe_public_receipt(*nxt)

    def test_empty_checkpoint_not_restorable(self):
        empty=NativeGrid5Evidence().checkpoint()
        with self.assertRaises(ValueError):
            NativeGrid5Evidence.restore(empty,hashlib.sha256(empty).hexdigest())

    def test_falsely_renamed_original_action_rejected(self):
        req,raw,pin=receipt(0,act=4)
        req['public_action']=1301
        with self.assertRaises(ValueError):
            NativeGrid5Evidence().observe_public_receipt(req,raw,pin)

    def test_one_cold_result_cannot_mutate_previous(self):
        old=NativeGrid5Evidence().observe_public_receipt(*receipt(0))
        restored=persist_and_restore(old)
        revised=restored.observe_public_receipt(*receipt(1))
        self.assertEqual(len(restored._rows),1)
        self.assertEqual(len(revised._rows),2)
        self.assertEqual(restored.checkpoint(),old.checkpoint())


if __name__=='__main__':unittest.main()
