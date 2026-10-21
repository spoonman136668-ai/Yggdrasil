"""MR9: native pre-lesion learning -> lesion -> label-free repair outcome audit.

This is a *development* falsifier of recovered functional performance, NOT
a new independent task family or protected first-use. Uses the original
NCI-04D2 existing binary neighbor-XOR task with exact native G7A->MR8 repair.
No post-lesion target bits enter the native learner. The original frozen MR7
negative, MR8 positive and abstention cases remain separately qualified.
"""
import hashlib
import json
import pathlib
import subprocess
import tempfile
import time
import unittest

from yggdrasil.developmental import N
from yggdrasil.task_runtime import LocalTaskRuntime, LocalCountControl
from yggdrasil.nci04i_atomic_pair import NativeAtomicPairRepair

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET_CELL = 0
EPOCHS = 3

# Frozen, model-independent development partition; disjoint pre-lesion
# training, unlabeled local-repair inputs and evaluation examples. We never
# select or adjust partitions by candidate or control predictions.
ORDER = sorted(
    range(1 << N),
    key=lambda n: hashlib.sha256(("MR9-native-sealed-dev-v1:" + str(n)).encode()).digest()
)
TRAIN_IDS = tuple(ORDER[:128])
UNLABELED_REPAIR_IDS = tuple(ORDER[128:144])
EVAL_IDS = tuple(ORDER[144:208])
assert len(set(TRAIN_IDS) | set(UNLABELED_REPAIR_IDS) | set(EVAL_IDS)) == 208
assert not (set(TRAIN_IDS) & set(UNLABELED_REPAIR_IDS))
assert not (set(TRAIN_IDS) & set(EVAL_IDS))
assert not (set(UNLABELED_REPAIR_IDS) & set(EVAL_IDS))


def bits_for(n):
    return [(n >> i) & 1 for i in range(N)]


def original_native_task_outcomes(bits, neighbors):
    # This is the existing pre-lesion source-owned D2 task rule, not a
    # post-lesion repair teacher or input to the MR8 adapter.
    return [bits[left] ^ bits[right] for left, right in neighbors]


def brier(predictions, truths):
    return sum((p - y) ** 2 for p, y in zip(predictions, truths)) / len(truths)


class NativeFunctionalRecoveryGate(unittest.TestCase):
    def test_frozen_development_task_recovers_function_not_just_role_motion(self):
        temp = tempfile.TemporaryDirectory(prefix="mr9-native-source-")
        self.addCleanup(temp.cleanup)
        checkout = pathlib.Path(temp.name) / "native"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout",
             str(ROOT), str(checkout)], check=True, capture_output=True
        )
        subprocess.run(
            ["git", "-C", str(checkout), "config", "core.autocrlf", "false"],
            check=True, capture_output=True
        )
        sha = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        subprocess.run(
            ["git", "-C", str(checkout), "checkout", "--quiet", "--detach", sha],
            check=True, capture_output=True
        )

        native = LocalTaskRuntime()
        conventional = LocalCountControl(native.neighbors)
        # All post-lesion labels are withheld. Both native learner and
        # conventional count receive equal pre-lesion target observations.
        for _ in range(EPOCHS):
            for index in TRAIN_IDS:
                bits = bits_for(index)
                targets = original_native_task_outcomes(bits, native.neighbors)
                native.observe(bits, targets)
                conventional.observe(bits, targets)
        self.assertEqual(native.core.events, len(TRAIN_IDS) * EPOCHS)
        trained = native.snapshot()
        prelesion = [
            native.component(bits_for(index), TARGET_CELL) for index in EVAL_IDS
        ]

        # Native lesion erases the learned damaged-cell role only.
        native.lesion([TARGET_CELL])
        lesioned = native.snapshot()
        frozen_no_repair = LocalTaskRuntime.restore(lesioned)
        no_repair = [
            frozen_no_repair.component(bits_for(index), TARGET_CELL)
            for index in EVAL_IDS
        ]
        control = [
            conventional.predict(bits_for(index))[TARGET_CELL]
            for index in EVAL_IDS
        ]
        original_genome = json.loads(lesioned)["core"]["genome"]
        source_prior = native.core.events

        # Native MR8 consumes only same-epoch sender observations produced by
        # the original independently running G7A simulator; no damaged-cell
        # post-lesion answer, outcome label or teacher rule crosses this API.
        repaired = LocalTaskRuntime.restore(lesioned)
        adapter = NativeAtomicPairRepair(checkout, repaired)
        changed = abstained = 0
        receipt_wires = 0
        child_process_wall_ns = 0
        cpu_start = time.process_time_ns()
        wall_start = time.perf_counter_ns()
        for sequence, index in enumerate(UNLABELED_REPAIR_IDS, start=1):
            start = time.perf_counter_ns()
            receipt = adapter.observe_and_repair(
                bits_for(index), sequence % 2, TARGET_CELL, sequence
            )
            child_process_wall_ns += time.perf_counter_ns() - start
            self.assertFalse(receipt["external_sensor_attested"])
            self.assertFalse(receipt["scientific_first_use"])
            if receipt["changed"]:
                changed += 1
                self.assertEqual(receipt["wire_bytes"], 76)
                self.assertFalse(receipt["functional_regeneration_proven"])
            else:
                abstained += 1
                self.assertEqual(receipt["classification"], "ATOMIC_NATIVE_PAIR_ABSTAINED")
            receipt_wires += 76
        parent_wall_ns = time.perf_counter_ns() - wall_start
        parent_cpu_ns = time.process_time_ns() - cpu_start

        # Evaluate only AFTER native learning is finished. Truth is obtained
        # by the independent local test evaluator, never fed to the learner
        # after lesion. These 64 inputs were not used in train or repair.
        postrepair = [
            repaired.component(bits_for(index), TARGET_CELL) for index in EVAL_IDS
        ]
        truth = [
            original_native_task_outcomes(bits_for(index), native.neighbors)[TARGET_CELL]
            for index in EVAL_IDS
        ]
        losses = {
            "trained_prelesion": brier(prelesion, truth),
            "lesioned_no_repair": brier(no_repair, truth),
            "repaired": brier(postrepair, truth),
            "fully_trained_count_control": brier(control, truth),
        }
        gain = losses["lesioned_no_repair"] - losses["repaired"]
        lost = losses["lesioned_no_repair"] - losses["trained_prelesion"]
        fraction_recovered = gain / lost if lost > 0 else None
        criterion = (
            lost > 0.01 and gain >= 0.1 * lost
            and losses["repaired"] < losses["fully_trained_count_control"]
        )

        self.assertEqual(len(prelesion), len(no_repair))
        self.assertEqual(len(postrepair), 64)
        self.assertEqual(changed + abstained, len(UNLABELED_REPAIR_IDS))
        self.assertEqual(repaired.damaged, {TARGET_CELL})
        self.assertEqual(repaired.core.genome, original_genome)
        self.assertEqual(repaired.core.events, source_prior + 2 * changed)
        self.assertEqual(len(repaired.core.genome) * len(repaired.core.genome[0]) +
                         sum(len(row) for row in repaired.core.roles), 45)
        self.assertEqual(
            LocalTaskRuntime.restore(repaired.snapshot()).snapshot(),
            repaired.snapshot()
        )
        # A hard false positive is a high-confidence prediction of a native
        # positive when the independent evaluator's binary target is 0.
        hard_fp = sum(p >= 0.9 and y == 0 for p, y in zip(postrepair, truth))
        print("MR9_NATIVE_FUNCTIONAL_RECOVERY=" + json.dumps({
            "gate": "MR9-frozen-internal-native-development",
            "exact_source_commit": sha,
            "prelesion_training_examples": len(TRAIN_IDS),
            "prelesion_training_epochs": EPOCHS,
            "unlabeled_postlesion_repair_examples": len(UNLABELED_REPAIR_IDS),
            "evaluation_examples_no_training_or_repair": len(EVAL_IDS),
            "task": "existing-native-D2-neighbor-XOR",
            "loss_brier": losses,
            "lesion_loss_increase": lost,
            "repair_loss_reduction": gain,
            "fraction_of_lesion_loss_recovered": fraction_recovered,
            "function_recovery_criterion_met": criterion,
            "changed_repair_steps": changed,
            "abstained_repair_steps": abstained,
            "hard_false_positive_threshold": 0.9,
            "hard_false_positives": hard_fp,
            "new_trainable_parameters": 0,
            "total_original_native_wire_bytes": receipt_wires,
            "repair_wall_ns_including_native_child_processes": parent_wall_ns,
            "parent_cpu_ns_only": parent_cpu_ns,
            "unmeasured_child_cpu_rss": True,
            "restart_exact_state": True,
            "external_sensor_attested": False,
            "independent_scientific_first_use": False,
            "scientific_admission": "BLOCKED",
        }, sort_keys=True))
        # Scientific/development negatives are valid measured evidence, not
        # harness failures; do not impose a passing accuracy threshold that
        # invites tuning against the frozen evaluation.
        self.assertEqual(frozen_no_repair.snapshot(), lesioned)
        self.assertEqual(native.snapshot(), lesioned)


if __name__ == "__main__":
    unittest.main()
