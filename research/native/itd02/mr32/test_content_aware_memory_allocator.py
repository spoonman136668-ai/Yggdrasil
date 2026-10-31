import unittest
from content_aware_memory_allocator import ContentAwareMemoryAllocator, TOTAL, ACTIVE, RETAINED, META, REPRESENTATION
from learned_memory_allocator import LearnedMemoryAllocator


def content(positive, i):
    values=[0.0]*REPRESENTATION
    values[0]=1.0 if positive else -1.0
    values[(i%7)+1]=0.25
    return tuple(values)


class ContentAwareAllocatorTests(unittest.TestCase):
    def test_exact_fixed_partition_and_learned_content_weights(self):
        m=ContentAwareMemoryAllocator()
        self.assertEqual(len(m.memories),TOTAL)
        self.assertEqual(sum(x.active for x in m.memories),ACTIVE)
        self.assertEqual(sum(not x.active for x in m.memories),RETAINED)
        for i in range(8):
            m.insert(f"fit-{i}",content(i%2==0,i),evidence_count=8,
                     prediction_error=0.5,contradiction_rate=0.5)
        before=list(m.weights)
        for epoch in range(40):
            for i in range(8):
                key=f"fit-{i}"
                m.mark_use(key)
                m.observe_task_outcome(key,1.0 if i%2==0 else 0.0)
        rep_weight_index=META+1
        self.assertNotEqual(before[rep_weight_index],m.weights[rep_weight_index])
        self.assertGreater(m.weights[rep_weight_index],0.0)
        self.assertEqual(m.stats()["total"],TOTAL)
        self.assertEqual(m.stats()["active"],ACTIVE)
        self.assertEqual(m.stats()["retained"],RETAINED)

    def test_heldout_content_ranking_beats_metadata_only(self):
        fit=ContentAwareMemoryAllocator()
        for i in range(8):
            fit.insert(f"fit-{i}",content(i%2==0,i),evidence_count=8,
                       prediction_error=0.5,contradiction_rate=0.5)
        for epoch in range(40):
            for i in range(8):
                key=f"fit-{i}"
                fit.mark_use(key)
                fit.observe_task_outcome(key,1.0 if i%2==0 else 0.0)

        held=ContentAwareMemoryAllocator()
        held.weights=list(fit.weights)
        meta=LearnedMemoryAllocator()
        cohort=[]
        # Negative keys sort first for the metadata-only tie-breaker.
        for i in range(8):
            key=f"a-negative-{i}"
            held.insert(key,content(False,i),evidence_count=8,
                        prediction_error=0.5,contradiction_rate=0.5)
            meta.insert(key,content(False,i),evidence_count=8,
                        prediction_error=0.5,contradiction_rate=0.5)
            cohort.append((key,0))
        for i in range(8):
            key=f"z-positive-{i}"
            held.insert(key,content(True,i),evidence_count=8,
                        prediction_error=0.5,contradiction_rate=0.5)
            meta.insert(key,content(True,i),evidence_count=8,
                        prediction_error=0.5,contradiction_rate=0.5)
            cohort.append((key,1))
        held_active={m.key for m in held.memories if m.occupied and m.active}
        meta_active={m.key for m in meta.memories if m.occupied and m.active}
        held_hits=sum(label for key,label in cohort if key in held_active)
        meta_hits=sum(label for key,label in cohort if key in meta_active)
        self.assertEqual(held_hits,7)
        self.assertEqual(meta_hits,0)
        self.assertGreater(held_hits,meta_hits)
        self.assertEqual(held.feedback_count,0)

    def test_cold_restart_preserves_content_conditioned_ranking(self):
        m=ContentAwareMemoryAllocator()
        for i in range(8):
            m.insert(f"fit-{i}",content(i%2==0,i),evidence_count=8)
        for epoch in range(20):
            for i in range(8):
                key=f"fit-{i}";m.mark_use(key)
                m.observe_task_outcome(key,1.0 if i%2==0 else 0.0)
        restored=ContentAwareMemoryAllocator.restore(m.snapshot())
        self.assertEqual(restored.weights,m.weights)
        self.assertEqual(restored.stats(),m.stats())

    def test_delayed_feedback_uses_use_time_content_and_metadata(self):
        m=ContentAwareMemoryAllocator()
        m.insert("source",content(True,0),evidence_count=32,prediction_error=0.25,contradiction_rate=0.5)
        m.mark_use("source")
        captured=tuple(m._get("source").pending_features)
        before=list(m.weights)
        expected_prediction=m._utility_for_features(captured)
        error=1.0-expected_prediction
        expected=[w+0.08*error*x for w,x in zip(before,captured)]
        for i in range(5):
            m.insert(f"later-{i}",content(False,i),evidence_count=1)
        self.assertNotEqual(captured,tuple(m._features(m._get("source"))))
        m.observe_task_outcome("source",1.0)
        for got,want in zip(m.weights,expected):
            self.assertAlmostEqual(got,want,places=12)
        self.assertIsNone(m._get("source").pending_features)
        self.assertFalse(m._get("source").pending_use)

    def test_pending_feedback_and_invalid_content_rejected(self):
        m=ContentAwareMemoryAllocator()
        with self.assertRaisesRegex(ValueError,"REPRESENTATION_DIMENSION"):
            m.insert("bad",(1.0,),evidence_count=1)
        m.insert("ok",content(True,0))
        m.mark_use("ok")
        with self.assertRaisesRegex(RuntimeError,"PENDING"):
            m.snapshot()


if __name__=="__main__":unittest.main()
