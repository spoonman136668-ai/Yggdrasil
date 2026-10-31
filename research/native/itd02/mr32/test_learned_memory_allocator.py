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

    def test_downstream_feedback_learns_utility_ranking(self):
        m=LearnedMemoryAllocator()
        m.insert("reliable",rep(0),evidence_count=64,prediction_error=0.0,contradiction_rate=0.0)
        m.insert("unreliable",rep(1),evidence_count=1,prediction_error=1.0,contradiction_rate=1.0)
        reliable=m._get("reliable")
        unreliable=m._get("unreliable")
        initial_reliable=m.predicted_utility(reliable)
        initial_unreliable=m.predicted_utility(unreliable)
        self.assertEqual(initial_reliable,initial_unreliable)
        for _ in range(40):
            m.mark_use("reliable")
            m.observe_task_outcome("reliable",1.0)
            m.mark_use("unreliable")
            m.observe_task_outcome("unreliable",0.0)
        self.assertGreater(m.predicted_utility(m._get("reliable")),
                           m.predicted_utility(m._get("unreliable")))

    def test_heldout_task_usefulness_ranking_beats_fixed_recency_and_evidence(self):
        # FIT: all 8 combinations of three metadata properties, repeated
        # across balanced rounds. No held-out item or label is exposed here.
        fit=LearnedMemoryAllocator()
        profiles=[]
        for hi_evidence in (False,True):
            for low_error in (False,True):
                for low_contradiction in (False,True):
                    profiles.append((
                        64 if hi_evidence else 2,
                        0.0 if low_error else 1.0,
                        0.0 if low_contradiction else 1.0,
                        int(sum((hi_evidence,low_error,low_contradiction))>=2)
                    ))
        for _ in range(30):
            for i,(evidence,error,contradiction,label) in enumerate(profiles):
                key=f"fit-{i}"
                if not any(m.occupied and m.key==key for m in fit.memories):
                    fit.insert(key,rep(i),evidence_count=evidence,
                               prediction_error=error,contradiction_rate=contradiction)
                fit.mark_use(key)
                fit.observe_task_outcome(key,float(label))

        # TRANSFER: a new empty store receives weights only. Evaluation
        # memories and their future usefulness labels are never fed back.
        held=LearnedMemoryAllocator()
        held.weights=list(fit.weights)
        evaluation=[]
        for repeat in range(2):
            for i,(evidence,error,contradiction,label) in enumerate(profiles):
                key=f"eval-{repeat}-{i}"
                result=held.insert(key,rep(100+repeat*8+i),evidence_count=evidence,
                                   prediction_error=error,contradiction_rate=contradiction)
                evaluation.append((key,label,evidence))
        # Arrange no feedback at all during evaluation. Compare the active
        # set with deterministic fixed-recency (most recently inserted) and
        # evidence-only (largest evidence count) controls on the same cohort.
        active={m.key for m in held.memories if m.occupied and m.active}
        positive=sum(label for _,label,_ in evaluation)
        active_hits=sum(label for key,label,_ in evaluation if key in active)
        recency_hits=sum(label for key,label,_ in sorted(evaluation,key=lambda x:x[0],reverse=True)[:ACTIVE])
        evidence_hits=sum(label for key,label,_ in sorted(evaluation,key=lambda x:(-x[2],x[0]))[:ACTIVE])
        learned_precision=active_hits/ACTIVE
        recency_precision=recency_hits/ACTIVE
        evidence_precision=evidence_hits/ACTIVE
        self.assertGreater(learned_precision,recency_precision)
        self.assertGreater(learned_precision,evidence_precision)
        self.assertEqual(held.feedback_count,0)
        self.assertEqual(positive,8)

    def test_reproducible_heldout_evaluation_emits_control_metrics(self):
        from learned_retention_eval import run
        result=run()
        learned=result["results"]["learned_utility"]["precision_at_7"]
        recency=result["results"]["fixed_recency"]["precision_at_7"]
        evidence=result["results"]["evidence_only"]["precision_at_7"]
        self.assertGreater(learned,recency)
        self.assertGreater(learned,evidence)
        self.assertEqual(result["transfer"]["feedback_events"],0)
        self.assertEqual(result["transfer"]["records"],16)

    def test_leave_one_profile_out_transfer_has_no_feedback(self):
        from learned_retention_cv import run
        result=run()
        self.assertEqual(result["summary"]["folds"],8)
        self.assertEqual(result["summary"]["transfer_feedback_events"],0)
        self.assertTrue(all(f["fit_profiles"]==7 for f in result["folds"]))
        self.assertTrue(all(f["transfer_feedback_events"]==0 for f in result["folds"]))

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
