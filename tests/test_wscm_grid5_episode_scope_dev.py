"""First failing cross-world transfer case; source-free publicly witnessed fixtures."""
import hashlib
import unittest

from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from yggdrasil.native_grid5_ingress import SCHEMA, SOURCE_MODE, canonical

A, B, C = 'a'*64, 'b'*64, 'c'*64


def ingest(memory, episode, step, action, before, after, serial):
    request = {'episode_id': episode, 'step_index': step,
               'public_state': list(before), 'public_action': action}
    data = {**request, 'schema': SCHEMA, 'source_mode': SOURCE_MODE,
            'source_id': f'{serial:064x}', 'next_state': list(after),
            'reward': 0, 'terminated': step == 49, 'truncated': step == 49}
    raw = canonical(data)
    return memory.observe_public_receipt(request, raw, hashlib.sha256(raw).hexdigest())


def two_episode_bank():
    memory = NativeGrid5Evidence()
    for n in range(50):
        memory = ingest(memory, A, n, 0 if n == 0 else 4,
                        (0,0) if n == 0 else (0,1), (0,1), n + 1)
    # New episode B is a distinct source-private action permutation. Action 0
    # has NOT been witnessed in B. Prior witnessed A outcome must not be used.
    memory = ingest(memory, B, 0, 1, (0,0), (0,0), 51)
    return memory


class EpisodeScopeNegativeTests(unittest.TestCase):
    def test_old_world_unwitnessed_action_must_abstain(self):
        m = two_episode_bank()
        self.assertEqual(m.public_forecast([0,0], 0, episode_id=A), [0,1])
        self.assertIsNone(m.public_forecast([0,0], 0, episode_id=B))
        self.assertIsNone(m.public_forecast([0,0], 0, episode_id=C))

    def test_current_episode_counts_not_historical_counts(self):
        m = two_episode_bank()
        self.assertEqual(m.public_plan([0,0], episode_id=B)['public_action'], 0)
        self.assertEqual(m.public_plan([0,0], episode_id=B)['witness_count'], 0)
        self.assertEqual(m.public_plan([0,0], episode_id=C)['public_action'], 0)
        self.assertIsNone(m.public_plan([0,0], episode_id=C)['observed_next_state'])

    def test_source_free_changed_law_confirmed_after_own_receipt(self):
        m = two_episode_bank()
        m = ingest(m, B, 1, 0, (0,0), (1,0), 52)
        self.assertEqual(m.public_forecast([0,0], 0, episode_id=A), [0,1])
        self.assertEqual(m.public_forecast([0,0], 0, episode_id=B), [1,0])
        raw=m.checkpoint()
        cold=NativeGrid5Evidence.restore(raw,hashlib.sha256(raw).hexdigest())
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.public_forecast([0,0], 0, episode_id=B), [1,0])
        self.assertEqual(cold.public_forecast([0,0], 0, episode_id=A), [0,1])

    def test_episode_pin_is_mandatory_and_cannot_be_boolean(self):
        m=two_episode_bank()
        with self.assertRaises(TypeError):m.public_forecast([0,0], 0)
        with self.assertRaises(TypeError):m.public_plan([0,0])
        for bad in ('a',True,False,1,None,1.0,'A'*64):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                m.public_forecast([0,0], 0, episode_id=bad)
            with self.subTest(value=bad), self.assertRaises(ValueError):
                m.public_plan([0,0], episode_id=bad)

    def test_cross_world_unchanged_familiar_role_still_requires_own_witness(self):
        m=two_episode_bank()
        # Source-private mapping B may happen to agree with A, but absent B
        # witness there is no reason to bind B's action 0.
        self.assertIsNone(m.public_forecast([0,0], 0, episode_id=B))

    def test_no_model_or_oracle_fields_in_proposal(self):
        m=two_episode_bank()
        self.assertEqual(set(m.public_plan([0,0],episode_id=B)),
                         {'source_mode','public_action','observed_next_state','witness_count'})

if __name__=='__main__': unittest.main()
