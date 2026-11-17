import json
import subprocess
import sys
import unittest

from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator


def rows(inputs):
    return [[x & 7, x >> 3, ((x & 1) ^ (((x >> 1) & 1) & ((x >> 2) & 1)) ^ (x >> 3))] for x in inputs]


def add(model, data, **kwargs):
    return model.stage_update(0, data, digest(canonical(data)), max_degree=2, **kwargs)


class NativeContextAccumulatorTests(unittest.TestCase):
    def test_cumulative_equals_full_batch_and_preserves_old_answers(self):
        model = NativeContextAccumulator(3)
        accumulated = []
        for group in (range(0, 5), range(5, 10), range(10, 16)):
            data = rows(group); accumulated.extend(data)
            before = [model.predict(0, x & 7, x >> 3) for x in range(16)]
            frozen = model.checkpoint()
            updated = add(model, data)
            batch = NativeContextBasis(3).stage_fit(0, accumulated, digest(canonical(accumulated)), max_degree=2)
            after = [updated.predict(0, x & 7, x >> 3) for x in range(16)]
            self.assertEqual(after, [batch.predict(0, x & 7, x >> 3) for x in range(16)])
            self.assertTrue(all(a is None or a == b for a, b in zip(before, after)))
            self.assertEqual(model.checkpoint(), frozen)
            model = updated
        self.assertEqual(model.profile_info(0)['unique_inputs'], 16)

    def test_exact_replay_and_overlapping_evidence_are_not_new_rank(self):
        data = rows(range(8)); model = add(NativeContextAccumulator(3), data)
        self.assertIs(add(model, data), model)
        repeat = add(model, list(reversed(data)))
        self.assertEqual(model.profile_info(0)['rank'], repeat.profile_info(0)['rank'])
        self.assertEqual(repeat.profile_info(0)['source_records'], 16)
        self.assertEqual(repeat.profile_info(0)['unique_inputs'], 8)

    def test_conflict_rejection_is_atomic(self):
        model = add(NativeContextAccumulator(3), rows(range(16)))
        frozen = model.checkpoint(); data = rows([0]); data[0][2] ^= 1
        with self.assertRaisesRegex(ValueError, 'CUMULATIVE_MODEL_INADEQUATE'):
            add(model, data)
        self.assertEqual(model.checkpoint(), frozen)

    def test_source_pin_and_real_source_type_rejected_before_replay(self):
        data = rows(range(4)); model = add(NativeContextAccumulator(3), data)
        with self.assertRaises(ValueError):
            model.stage_update(0, data, '0' * 64, max_degree=2)
        for kwargs in ({'source_mode':'original'}, {'source_kind':'historical_fact'}):
            with self.assertRaises(ValueError): add(model, data, **kwargs)

    def test_declared_class_cannot_silently_change(self):
        data = rows(range(4)); model = add(NativeContextAccumulator(3), data)
        with self.assertRaisesRegex(ValueError, 'CLASS_DRIFT'):
            model.stage_update(0, data, digest(canonical(data)), max_degree=3)

    def test_cold_sufficient_statistics_continue_without_old_rows(self):
        model = add(NativeContextAccumulator(3), rows(range(8)))
        raw = model.checkpoint()
        script = '''import json,sys
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=p['checkpoint'].encode('ascii')
m=NativeContextAccumulator.restore(raw,digest(raw))
m=m.stage_update(0,p['new'],digest(canonical(p['new'])),max_degree=2)
print(json.dumps([m.predict(0,x&7,x>>3) for x in range(16)]))
'''
        completed = subprocess.run([sys.executable,'-B','-c',script], input=json.dumps({'checkpoint':raw.decode('ascii'),'new':rows(range(8,16))}), text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(completed.stdout), [r[2] for r in rows(range(16))])

    def test_checkpoint_metadata_tampering_rejected(self):
        model = add(NativeContextAccumulator(3), rows(range(8)))
        for edit in ('mask','count','ledger','flags'):
            doc = json.loads(model.checkpoint())
            if edit == 'mask':doc['observed_input_masks'][0] = '1'
            elif edit == 'count':doc['batch_ledgers'][0][0][1] += 1
            elif edit == 'ledger':doc['batch_ledgers'][0][0][0] = 'f' * 64
            else:doc['accepted_native'] = True
            raw = canonical(doc)
            with self.assertRaises(ValueError):NativeContextAccumulator.restore(raw, digest(raw))

    def test_input_support_swap_rejected_even_with_preserved_count(self):
        model = add(NativeContextAccumulator(3), rows([0,1]))
        doc = json.loads(model.checkpoint());doc['observed_input_masks'][0] = 'c'
        raw = canonical(doc)
        with self.assertRaises(ValueError):NativeContextAccumulator.restore(raw,digest(raw))

    def test_untouched_native_v1_checkpoint_still_byte_exact(self):
        data = rows(range(8))
        old = NativeContextBasis(3).stage_fit(0,data,digest(canonical(data)),max_degree=2)
        raw = old.checkpoint()
        self.assertEqual(NativeContextBasis.restore(raw,digest(raw)).checkpoint(),raw)
        self.assertNotIn('batch_ledgers',json.loads(raw))

    def test_retained_slot_and_invalid_address_isolation(self):
        data = rows(range(8)); model = add(NativeContextAccumulator(3),data,retained=True)
        self.assertIsNone(model.predict(0,0,0))
        self.assertEqual(model.predict(0,0,0,retained=True),0)
        with self.assertRaises(ValueError):model.stage_update(7,data,digest(canonical(data)))


if __name__ == '__main__':unittest.main()
