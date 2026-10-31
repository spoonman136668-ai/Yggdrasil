import json
import unittest
from learned_memory_allocator import LearnedMemoryAllocator, TOTAL, ACTIVE, RETAINED

def rep(i):
    return tuple(1.0 if j==i%16 else 0.0 for j in range(16))

class LearnedAllocatorTests(unittest.TestCase):
    def test_fixed_total_active_retained_budget(self):
        m=LearnedMemoryAllocator()
        for i in range(40):
            m.insert(f"m{i}",rep(i))
            self.assertLessEqual(m.stats()["total"],TOTAL)
            self.assertLessEqual(m.stats()["active"],ACTIVE)
            self.assertLessEqual(m.stats()["retained"],RETAINED)

    def test_exact_partition_exists_from_empty_initialization(self):
        m=LearnedMemoryAllocator()
        self.assertEqual(len(m.memories),TOTAL)
        self.assertEqual(sum(slot.active for slot in m.memories),ACTIVE)
        self.assertEqual(sum(not slot.active for slot in m.memories),RETAINED)
        self.assertEqual(m.stats()["occupied"],0)

    def test_policy_weights_change_only_after_downstream_feedback(self):
        m=LearnedMemoryAllocator();m.insert("useful",rep(0),evidence_count=8)
        before=list(m.weights)
        m.mark_use("useful")
        self.assertEqual(before,m.weights)
        m.observe_task_outcome("useful",1.0)
        self.assertNotEqual(before,m.weights)
        self.assertEqual(m.feedback_count,1)

    def test_unselected_memory_cannot_receive_outcome_credit(self):
        m=LearnedMemoryAllocator();m.insert("m",rep(0))
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):
            m.observe_task_outcome("m",1.0)

    def test_prediction_is_pre_feedback_and_cold_restart(self):
        m=LearnedMemoryAllocator()
        for i in range(12):
            m.insert(f"m{i}",rep(i),evidence_count=i+1)
            m.mark_use(f"m{i}")
            m.observe_task_outcome(f"m{i}",1.0 if i%2==0 else 0.0)
        blob=m.snapshot()
        a=LearnedMemoryAllocator.restore(blob);b=LearnedMemoryAllocator.restore(blob)
        self.assertEqual(a.stats(),b.stats())
        self.assertEqual([x.key for x in a.memories],[x.key for x in b.memories])

    def test_pending_feedback_checkpoint_rejected(self):
        m=LearnedMemoryAllocator();m.insert("m",rep(0));m.mark_use("m")
        with self.assertRaisesRegex(RuntimeError,"PENDING"):
            m.snapshot()

    def test_checkpoint_tampering_rejected(self):
        m=LearnedMemoryAllocator();m.insert("m",rep(0))
        doc=json.loads(m.snapshot());doc["payload"]["weights"][0]=2
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
            LearnedMemoryAllocator.restore(json.dumps(doc).encode())

    def test_budget_eviction_preserves_nonpending_memories(self):
        m=LearnedMemoryAllocator()
        for i in range(TOTAL+5):
            m.insert(f"m{i}",rep(i),evidence_count=i+1)
        self.assertEqual(m.stats()["total"],TOTAL)
        self.assertEqual(m.stats()["active"],ACTIVE)
        self.assertEqual(m.stats()["retained"],RETAINED)

if __name__=="__main__":unittest.main()
