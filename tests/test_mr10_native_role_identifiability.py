"""MR10: source-native causal-role identifiability and frozen-state attribution.

No new task, evaluation cohort, learned mechanism, source labels or parameter
tuning. Exhaustively inspect the ORIGINAL D2 teacher's local conditional
function and decompose the MR9-trained state on TRAINING inputs ONLY.
MR9's unused/evaluation samples are never accessed, scored or reclassified.
This is a development structural diagnosis, not scientific first use.
"""
import hashlib
import json
import subprocess
import unittest

from yggdrasil.developmental import K, N
from yggdrasil.task_runtime import LocalTaskRuntime
from test_mr9_native_functional_recovery import (
    EPOCHS, TRAIN_IDS, bits_for, original_native_task_outcomes,
)


def native_training_loss(runtime, inputs):
    loss = 0.0
    n = 0
    for index in inputs:
        x = bits_for(index)
        answers = original_native_task_outcomes(x, runtime.neighbors)
        predictions = runtime.predict(x)
        for pred, answer in zip(predictions, answers):
            loss += (pred - answer) ** 2
            n += 1
    return loss / n


class SourceNativeRoleIdentifiability(unittest.TestCase):
    def test_original_task_has_one_shared_local_causal_function(self):
        # Every possible native eight-bit input is inspected for mathematical
        # identity, NOT for learner evaluation. This has no model or holdout
        # labels; it is exactly the preexisting public task definition.
        native = LocalTaskRuntime()
        contexts = {}
        per_cell = [set() for _ in range(N)]
        for index in range(1 << N):
            bits = bits_for(index)
            actual = original_native_task_outcomes(bits, native.neighbors)
            for i in range(N):
                left, right = native.neighbors[i]
                context = (bits[i], bits[left], bits[right])
                expected = bits[left] ^ bits[right]
                self.assertEqual(actual[i], expected)
                if context in contexts:
                    self.assertEqual(contexts[context], expected)
                contexts[context] = expected
                per_cell[i].add(context)

            # The ring transition law is equivariant under cyclic relabeling
            # of the cells. Distinct cell identities cannot make different
            # functions observable on this source task.
            shifted = bits[-1:] + bits[:-1]
            shifted_truth = original_native_task_outcomes(
                shifted, native.neighbors
            )
            self.assertEqual(shifted_truth, actual[-1:] + actual[:-1])

        self.assertEqual(len(contexts), 8)
        self.assertTrue(all(s == set(contexts) for s in per_cell))
        print("MR10_CAUSAL_LOCAL_TASK_IDENTIFIABILITY=" + json.dumps({
            "native_source_task": "original-D2-ring-neighbor-XOR",
            "all_source_inputs_checked": 1 << N,
            "all_cell_input_combinations_checked": N * (1 << N),
            "same_conditional_causal_function_every_cell": True,
            "cyclic_permutation_equivariant": True,
            "distinct_cell_specific_function_required": False,
            "claim": "native D2 source has no identifiable cell-specific target function",
            "new_native_task_or_scientific_first_use": False,
        }, sort_keys=True))

    def test_original_mr9_training_role_and_genome_ablation_on_training_only(self):
        native = LocalTaskRuntime()
        for _ in range(EPOCHS):
            for index in TRAIN_IDS:
                bits = bits_for(index)
                native.observe(
                    bits, original_native_task_outcomes(bits, native.neighbors)
                )
        trained_snapshot = native.snapshot()
        self.assertEqual(native.core.events, EPOCHS * len(TRAIN_IDS))

        # Exact causal attribution: remove only learned per-cell role logits,
        # leaving the original trained shared genome intact. In a second,
        # independent copy, reset only the shared genome to its original
        # initialized values while keeping all eight learned roles.
        no_role = LocalTaskRuntime.restore(trained_snapshot)
        for i in range(N):
            no_role.core.roles[i] = [0.0] * K
        no_genome = LocalTaskRuntime.restore(trained_snapshot)
        untrained = LocalTaskRuntime()
        no_genome.core.genome = [
            list(expert) for expert in untrained.core.genome
        ]
        original = LocalTaskRuntime.restore(trained_snapshot)

        native_training = native_training_loss(original, TRAIN_IDS)
        no_role_training = native_training_loss(no_role, TRAIN_IDS)
        no_genome_training = native_training_loss(no_genome, TRAIN_IDS)
        role_abs_effect = []
        role_max_effect = 0.0
        gate_deviation = []
        for index in TRAIN_IDS:
            x = bits_for(index)
            p = original.predict(x)
            q = no_role.predict(x)
            for a, b in zip(p, q):
                diff = abs(a - b)
                role_abs_effect.append(diff)
                role_max_effect = max(role_max_effect, diff)
        for i in range(N):
            logits = original.core.roles[i]
            centered = [v - sum(logits)/K for v in logits]
            gate_deviation.append(max(map(abs, centered)))
        self.assertEqual(original.snapshot(), trained_snapshot)
        self.assertEqual(
            LocalTaskRuntime.restore(trained_snapshot).snapshot(),
            trained_snapshot,
        )
        self.assertEqual(len(role_abs_effect), len(TRAIN_IDS) * N)
        self.assertEqual(
            len(native.core.genome) * len(native.core.genome[0]) +
            sum(len(role) for role in native.core.roles), 45,
        )

        result = {
            "gate": "MR10-original-native-source-role-necessity",
            "source_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "source": "unchanged MR9 original D2 source, TRAIN input subset only",
            "trained_checkpoint_sha256": hashlib.sha256(
                trained_snapshot.encode()
            ).hexdigest(),
            "training_examples": len(TRAIN_IDS),
            "training_epochs": EPOCHS,
            "training_only_brier_trained": native_training,
            "training_only_brier_role_reset": no_role_training,
            "training_only_brier_shared_genome_reset": no_genome_training,
            "training_only_role_reset_loss_delta":
                no_role_training - native_training,
            "training_only_shared_genome_reset_loss_delta":
                no_genome_training - native_training,
            "training_only_mean_abs_role_prediction_effect":
                sum(role_abs_effect)/len(role_abs_effect),
            "training_only_max_abs_role_prediction_effect":
                role_max_effect,
            "max_learned_role_logit_deviation":
                max(gate_deviation),
            "fixed_native_parameter_count": 45,
            "native_state_unchanged_after_ablation": True,
            "mr9_holdout_predictions_or_labels_read": False,
            "scientific_first_use": False,
            "scientific_admission": "BLOCKED",
        }
        print("MR10_NATIVE_CAUSAL_ROLE_ABLATION=" +
              json.dumps(result, sort_keys=True))
        # An unhelpful result is a real research negative, not a CI failure.
        # Do not impose performance thresholds that encourage tuning.
        self.assertTrue(
            all(isinstance(v, float) for v in
                (native_training, no_role_training, no_genome_training))
        )


if __name__ == "__main__":
    unittest.main()
