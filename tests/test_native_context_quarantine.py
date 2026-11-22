import json
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_quarantine import NativeContextQuarantine


def checked(model,rows,address=0,**kwargs):
    return model.stage_checked_update(address,rows,digest(canonical(rows)),max_degree=1,**kwargs)


class NativeContextQuarantineTests(unittest.TestCase):
    def initial(self):
        return checked(NativeContextQuarantine(NativeContextAccumulator(1)),[[0,0,0],[1,0,1]])

    def test_healthy_update_keeps_identified_answers_and_old_bytes(self):
        old=self.initial();raw=old.checkpoint()
        new=checked(old,[[0,1,1]])
        self.assertEqual(new.predict(0,1,0),1);self.assertEqual(new.predict(0,0,1),1)
        self.assertEqual(old.checkpoint(),raw);self.assertFalse(any(new._failures))

    def test_contradiction_quarantines_only_new_candidate(self):
        old=self.initial();raw=old._native.checkpoint()
        new=checked(old,[[1,0,0]])
        self.assertIsNone(new.predict(0,1,0));self.assertEqual(old.predict(0,1,0),1)
        self.assertEqual(new._native.checkpoint(),raw)
        self.assertTrue(new._failures[0])

    def test_other_active_and_retained_relations_survive(self):
        old=checked(self.initial(),[[0,0,1]],address=1)
        old=checked(old,[[0,0,1]],retained=True)
        new=checked(old,[[1,0,0]])
        self.assertEqual(new.predict(1,0,0),1)
        self.assertEqual(new.predict(0,0,0,retained=True),1)

    def test_unverified_source_and_wrong_hash_cannot_quarantine(self):
        old=self.initial();raw=old.checkpoint();rows=[[1,0,0]]
        for extra in ({'source_mode':'original'},{'source_kind':'historical_fact'}):
            with self.assertRaises(ValueError):checked(old,rows,**extra)
        with self.assertRaises(ValueError):old.stage_checked_update(0,rows,'0'*64,max_degree=1)
        self.assertEqual(old.checkpoint(),raw)

    def test_class_change_is_not_source_contradiction(self):
        old=self.initial()
        with self.assertRaisesRegex(ValueError,'CLASS_DRIFT'):
            old.stage_checked_update(0,[[0,1,1]],digest(canonical([[0,1,1]])),max_degree=2)
        self.assertFalse(any(old._failures))

    def test_no_silent_unquarantine_or_invalid_query_bypass(self):
        new=checked(self.initial(),[[1,0,0]])
        with self.assertRaisesRegex(ValueError,'EXPLICIT_REPAIR'):checked(new,[[1,0,1]])
        with self.assertRaises(ValueError):new.predict(0,2,0)
        self.assertIsNone(new.predict_partial(0,0,0,0))

    def test_checkpoint_flags_and_failure_pins_rejected(self):
        new=checked(self.initial(),[[1,0,0]]);raw=new.checkpoint()
        self.assertEqual(NativeContextQuarantine.restore(raw,digest(raw)).checkpoint(),raw)
        for key,value in [('accepted_native',True),('contradiction_batch_sha256',['bad']*16)]:
            doc=json.loads(raw);doc[key]=value;bad=canonical(doc)
            with self.assertRaises(ValueError):NativeContextQuarantine.restore(bad,digest(bad))

    def test_undetectable_wrong_assumptions_are_not_magically_repaired(self):
        # Hidden true function could be x0 AND x1. Before its contrary witnessed
        # row arrives, the affine source assumption cannot be certified true.
        rows=[[0,0,0],[1,0,0],[2,0,0]]
        native=NativeContextAccumulator(2).stage_update(0,rows,digest(canonical(rows)),max_degree=1)
        old=NativeContextQuarantine(native)
        self.assertEqual(old.predict(0,3,0),0)  # wrong if actual source is AND
        new=checked(old,[[3,0,1]])
        self.assertIsNone(new.predict(0,3,0));self.assertEqual(old.predict(0,3,0),0)


if __name__=='__main__':unittest.main()
