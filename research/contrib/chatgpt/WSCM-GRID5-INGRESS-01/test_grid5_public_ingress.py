import hashlib
import json
import unittest
import grid5_public_ingress as g

P = 'a' * 64
Q = 'b' * 64


def mk(step, action=0, state=(0,0), target=(1,0), episode=P, source_id=None,
       reward=0, term=None, extra=None):
    req = dict(episode_id=episode, step_index=step,
               public_state=list(state), public_action=action)
    if term is None: term = step == 49
    row = dict(req, source_id=source_id or f'{step+1:064x}',
               next_state=list(target), reward=reward,
               terminated=term, truncated=term,
               schema=g.SCHEMA, source_mode=g.SOURCE_MODE)
    if extra: row.update(extra)
    raw = g.canonical(row)
    return req, raw, hashlib.sha256(raw).hexdigest()


class DevIngressTests(unittest.TestCase):
    def test_exposes_only_public_evidence(self):
        req,raw,pin=mk(0)
        result=g.accept_fixture_receipt(req,raw,pin)
        self.assertEqual(result[1:9],(P,0,(0,0),0,(1,0),0,False,False))

    def test_exact_canonical_receipt_and_checksum(self):
        req,raw,pin=mk(0)
        self.assertEqual(g.accept_fixture_receipt(req,raw,pin)[-1],pin)
        with self.assertRaises(ValueError): g.accept_fixture_receipt(req,raw,b'0'*64)
        with self.assertRaises(ValueError): g.accept_fixture_receipt(req,raw+b' ',hashlib.sha256(raw+b' ').hexdigest())

    def test_no_hidden_fields_even_with_correct_hash(self):
        for field in ('perm_idx','perm','goal','optimal_action','private_role','hidden_state'):
            req,raw,pin=mk(0,extra={field:0})
            with self.subTest(field=field), self.assertRaises(ValueError):
                g.accept_fixture_receipt(req,raw,pin)

    def test_all_native_actions_and_state_positions(self):
        for a in range(5):
            for st, nxt in (((0,0),(0,0)),((4,4),(4,5)),((8,8),(8,8))):
                req,raw,pin=mk(0,a,st,nxt)
                self.assertEqual(g.accept_fixture_receipt(req,raw,pin)[4],a)

    def test_bool_int_and_out_of_range_rejected_before_cache(self):
        for bad in (True,False,-1,5,5.0,'3',None):
            req,raw,pin=mk(0,action=bad)
            with self.subTest(action=bad),self.assertRaises(ValueError):
                g.accept_fixture_receipt(req,raw,pin)
        for bad in (True,False,-1,9,9.0,'1'):
            req,raw,pin=mk(0,state=(bad,0))
            with self.subTest(state=bad),self.assertRaises(ValueError):
                g.accept_fixture_receipt(req,raw,pin)

    def test_impossible_moves_and_outcomes_rejected(self):
        for target in ((2,0),(1,1),(-1,0),(9,0)):
            req,raw,pin=mk(0,target=target)
            with self.subTest(target=target),self.assertRaises(ValueError):
                g.accept_fixture_receipt(req,raw,pin)
        for reward in (True,-1,2,0.5,'1'):
            req,raw,pin=mk(0,reward=reward)
            with self.subTest(reward=reward),self.assertRaises(ValueError):
                g.accept_fixture_receipt(req,raw,pin)

    def test_50_step_termination_contract(self):
        for step, term, valid in ((0,False,True),(49,True,True),(49,False,False),(0,True,False)):
            req,raw,pin=mk(step,term=term)
            with self.subTest(step=step,term=term):
                if valid:self.assertEqual(g.accept_fixture_receipt(req,raw,pin)[7],term)
                else:
                    with self.assertRaises(ValueError):g.accept_fixture_receipt(req,raw,pin)

    def test_request_receipt_pair_must_match(self):
        req,raw,pin=mk(0)
        req['public_action']=1
        with self.assertRaises(ValueError):g.accept_fixture_receipt(req,raw,pin)

    def test_duplicate_json_keys_rejected(self):
        req,raw,pin=mk(0)
        modified=raw[:-1]+b',"reward":0}'
        with self.assertRaises(ValueError):g.accept_fixture_receipt(req,modified,hashlib.sha256(modified).hexdigest())

    def test_contiguous_valid_batch(self):
        batch=[mk(t,state=(0,0),target=(0,0)) for t in range(50)]
        events=g.validate_public_batch(batch)
        self.assertEqual(len(events),50)
        self.assertTrue(events[-1][7])

    def test_source_replay_conflict_fails(self):
        first=mk(0)
        second=mk(1,state=(1,0),target=(1,1),source_id='1'.zfill(64))
        with self.assertRaises(ValueError):g.validate_public_batch([first,second])

    def test_sequence_skip_and_state_drift_fail(self):
        first=mk(0)
        for later in (mk(2,state=(1,0),target=(1,1)),mk(1,state=(0,0),target=(0,1))):
            with self.assertRaises(ValueError):g.validate_public_batch([first,later])

    def test_premature_reset_and_reentry_fail(self):
        first=mk(0)
        with self.assertRaises(ValueError):g.validate_public_batch([first,mk(0,episode=Q,source_id='f'*64)])
        episode=[mk(i,state=(0,0),target=(0,0)) for i in range(50)]
        with self.assertRaises(ValueError):g.validate_public_batch(episode+[mk(0,episode=P,source_id='f'*64)])

    def test_capacity_and_type_fail_closed(self):
        for invalid in ([],tuple(),[None],[(0,1)], [mk(0)]*257):
            with self.assertRaises(ValueError):g.validate_public_batch(invalid)

    def test_source_mode_and_canonical_schema_guards(self):
        for extra in ({'source_mode':'original'}, {'schema':'incorrect'}, {'source_id':'not-a-pin'}, {'terminated':1}, {'truncated':1}):
            req,raw,pin=mk(0,extra=extra)
            with self.subTest(extra=extra),self.assertRaises(ValueError):g.accept_fixture_receipt(req,raw,pin)


if __name__=='__main__':unittest.main()
