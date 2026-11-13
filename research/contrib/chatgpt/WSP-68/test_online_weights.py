"""WSP68 prospective neural-weight edit / converged-control SELFTEST.

No hidden source physics or oracle labels enter any training model.
Stage A at 48 and Stage B at 96 real sequential charged actions. All
full-source audits and heldout two-action compositions are evaluator-only
and executed after learning. Online neural inference uses only actual
numeric matrices/covariance from the cold snapshot, not the training ledger.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import sys
import time
import unittest

from source import SEEDS, STATES, ACTIONS, STAGE_A, TRAIN_ACTIONS, build_world
from online_weights import (
    OnlineNeuralWeightEditor, RIDGE_LAMBDA, FEATURE_SEED,
    FEATURES, HIDDEN, OUTPUTS, MARGIN_THRESHOLD, LEVERAGE_THRESHOLD
)
from independent_batch import BatchTrainedReadout

_PARENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PARENT / "WSP-67"))
from independent_symbolic import ExactMemory
from weight_programmer import DirectNeuralProgrammer
sys.path.insert(0, str(_PARENT / "WSP-64"))
from independent_tree import IndependentTreeControl


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True,
                  separators=(",", ":")).encode("ascii")).hexdigest()


def audit(predict, world, known):
    result = {"correct":0, "wrong_confident":0, "abstain":0,
              "unseen_correct":0, "unseen_wrong":0,
              "unseen_abstain":0, "unseen_total":0}
    for before in STATES:
        for action in ACTIONS:
            outcome = predict(before, action)
            true = world._step_oracle(before, action)  # evaluator-only scoring
            unseen = (before, action) not in known
            if unseen:
                result["unseen_total"] += 1
            if outcome is None:
                result["abstain"] += 1
                if unseen:
                    result["unseen_abstain"] += 1
            elif outcome == true:
                result["correct"] += 1
                if unseen:
                    result["unseen_correct"] += 1
            else:
                result["wrong_confident"] += 1
                if unseen:
                    result["unseen_wrong"] += 1
    assert (result["correct"] + result["wrong_confident"] +
            result["abstain"] == 64)
    assert (result["unseen_correct"] + result["unseen_wrong"] +
            result["unseen_abstain"] == result["unseen_total"])
    return result


def compose(predict, cases):
    result = {"correct":0, "wrong_confident":0, "abstain":0}
    for case in cases:
        a, b = case.actions
        mid = predict(case.start, a)
        finish = predict(mid, b) if mid is not None else None
        if finish is None:
            result["abstain"] += 1
        elif finish == case._finish:
            result["correct"] += 1
        else:
            result["wrong_confident"] += 1
    assert sum(result.values()) == len(cases)
    return result


class FrozenNumericalWeightEditor(unittest.TestCase):
    def test_source_isolation_and_neural_parameter_custody(self):
        paths = ["online_weights.py", "independent_batch.py"]
        for path in paths:
            content = (Path(__file__).parent / path).read_text("utf-8")
            self.assertNotIn("from source import", content)
            self.assertNotIn("import source", content)
            self.assertNotIn("from weight_programmer import", content)
            self.assertNotIn("hypothesis", content.lower() if path == "online_weights.py" else
                             "an unlikely literal marker")
        self.assertEqual(OnlineNeuralWeightEditor.gradient_updates, 0)
        self.assertEqual(FEATURES, 41)
        self.assertEqual(HIDDEN, 32)
        self.assertEqual(OUTPUTS, 4)
        self.assertEqual(RIDGE_LAMBDA, 0.5)
        self.assertEqual(FEATURE_SEED, 68182026)
        self.assertEqual(MARGIN_THRESHOLD, 0.27)
        self.assertEqual(LEVERAGE_THRESHOLD, 2.0)
        writer = OnlineNeuralWeightEditor()
        batch = BatchTrainedReadout()
        for state, action in [((0,0,0,0), 0), ((1,1,0,1), 2)]:
            a = writer._features(state, action)
            b = batch._phi(state, action)
            self.assertEqual(len(a), 41)
            self.assertTrue(all(abs(x-y) < 1e-14 for x,y in zip(a,b)))
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(4201, cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4101)
        for seed in SEEDS:
            world = build_world(seed)
            self.assertEqual(world.receipt(), build_world(seed).receipt())
            self.assertEqual(len(world.composition_tests()), 32)
        world = build_world(SEEDS[0])
        row = world.training_session().step(0)
        with self.assertRaises(ValueError):
            from source import Experience
            writer.charge(Experience((1,1,1,1), 0, row.after))
        with self.assertRaises(ValueError):
            writer.charge(Experience((0,0,0,0), 4, row.after))
        with self.assertRaises(ValueError):
            writer.charge(Experience((0,0,0,0), 0, row.after, 0))
        self.assertEqual(writer.charged_actions, 0)
        writer.charge(row)
        self.assertEqual(writer.charged_actions, 1)
        tamper = writer.snapshot().replace(
            "wsp68.online-neural-matrices.v1",
            "wsp68.online-neural-matrices.v2")
        with self.assertRaises(ValueError):
            OnlineNeuralWeightEditor.restore(tamper)

    def test_twelve_world_frozen_direct_online_vs_batch_and_symbolic(self):
        total = {
            "worlds":0, "source_actions":0, "full_source_audit":0,
            "heldout_compositions":0,
            "stageA_correct":0, "stageA_confident_wrong":0,
            "stageB_correct":0, "stageB_confident_wrong":0,
            "stageB_abstain":0, "stageB_unseen_correct":0,
            "stageB_unseen_wrong":0, "stageB_unseen_total":0,
            "forced_correct":0, "forced_wrong":0,
            "exact_memory_correct":0, "exact_memory_wrong":0,
            "tree_correct":0, "tree_wrong":0,
            "batch_forced_correct":0, "batch_forced_wrong":0,
            "composition_direct_correct":0, "composition_direct_wrong":0,
            "composition_exact_memory_correct":0,
            "composition_tree_correct":0,
            "stageA_retained_correct":0, "stageA_eligible_correct":0,
            "weights_changed_worlds":0, "cold_snapshots":0,
            "independent_batch_converged_worlds":0,
            "prior_symbolic_rejected_worlds":0
        }
        reports = []
        max_coefficient_difference = 0.0
        max_normal_equation_residual = 0.0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                session = world.training_session()
                writer = OnlineNeuralWeightEditor()
                rng = Random(int.from_bytes(sha256(
                    f"WSP68|public-random-action-policy|{seed}".encode("ascii")
                ).digest(), "big"))
                ledger = []
                start_wall = time.perf_counter()
                start_cpu = time.process_time()
                for _ in range(STAGE_A):
                    row = session.step(rng.choice(ACTIONS))
                    writer.charge(row)
                    ledger.append((row.before, row.action, row.after))
                self.assertEqual(writer.charged_actions, 48)
                self.assertEqual(len(session.ledger), 48)
                a_snap = writer.snapshot()
                cold_a = OnlineNeuralWeightEditor.restore(a_snap)
                self.assertEqual(cold_a.snapshot(), a_snap)
                self.assertNotIn('"ledger"', a_snap)
                self.assertNotIn('"rules"', a_snap)
                self.assertNotIn('"source"', a_snap)
                for _ in range(TRAIN_ACTIONS-STAGE_A):
                    row = session.step(rng.choice(ACTIONS))
                    writer.charge(row)
                    ledger.append((row.before, row.action, row.after))
                self.assertEqual(len(ledger), 96)
                self.assertEqual(len(session.ledger), 96)
                self.assertEqual(writer.charged_actions, 96)
                self.assertTrue(all(ledger[i][2] == ledger[i+1][0]
                                    for i in range(95)))
                self.assertEqual(ledger[0][0], (0,0,0,0))
                b_snap = writer.snapshot()
                cold_b = OnlineNeuralWeightEditor.restore(b_snap)
                self.assertEqual(cold_b.snapshot(), b_snap)
                with self.assertRaises(ValueError):
                    OnlineNeuralWeightEditor.restore(b_snap.replace(
                        "wsp68.online-neural-matrices.v1",
                        "wsp68.online-neural-matrices.v2"))
                self.assertNotIn('"ledger"', b_snap)
                self.assertNotIn('"physics"', b_snap)
                for state in STATES:
                    for action in ACTIONS:
                        self.assertEqual(cold_b.raw(state, action),
                                         writer.raw(state, action))
                        self.assertEqual(cold_b.predict(state, action),
                                         writer.predict(state, action))
                        self.assertEqual(cold_a.predict(state, action),
                                         OnlineNeuralWeightEditor.restore(a_snap).predict(
                                             state, action))
                changed = writer.learned_weights_changed(cold_a)
                self.assertGreater(writer.nonzero_learned_weights(),0)
                seen = {(b,a) for b,a,y in ledger}
                prior_seen = {(b,a) for b,a,y in ledger[:STAGE_A]}
                stage_a_audit = audit(cold_a.predict, world, prior_seen)
                stage_b_audit = audit(cold_b.predict, world, seen)
                forced = audit(lambda s,a: cold_b.predict(s,a,force=True),
                               world, seen)
                memory = ExactMemory(ledger)
                tree = IndependentTreeControl(ledger,4)
                memory_audit = audit(memory.predict, world, seen)
                tree_audit = audit(tree.predict, world, seen)
                batch_start = time.perf_counter()
                batch = BatchTrainedReadout()
                fit = batch.fit(ledger)
                batch_wall = time.perf_counter()-batch_start
                batch_audit = audit(batch.predict, world, seen)
                coefficient_diff = max(
                    abs(writer.w_readout[j][k] - batch.output_weights[j][k])
                    for j in range(OUTPUTS) for k in range(FEATURES)
                )
                max_coefficient_difference = max(
                    max_coefficient_difference, coefficient_diff)
                max_normal_equation_residual = max(
                    max_normal_equation_residual,
                    fit["objective_stationarity_infinity"])
                stage_a_eligible = 0
                stage_a_retained = 0
                for state in STATES:
                    for action in ACTIONS:
                        old = cold_a.predict(state, action)
                        truth = world._step_oracle(state,action)
                        if old is not None and old == truth:
                            stage_a_eligible += 1
                            stage_a_retained += int(cold_b.predict(state,action)==truth)
                cases = world.composition_tests()
                composite_b = compose(cold_b.predict,cases)
                composite_memory = compose(memory.predict,cases)
                composite_tree = compose(tree.predict,cases)
                # Out-of-WSP67-rule-family diagnostic only. The old
                # predicate compiler is NOT used by the new neural writer.
                old = DirectNeuralProgrammer()
                for row in session.ledger:
                    old.observe(row)
                try:
                    old.compile()
                    prior_rejected = 0
                except ValueError:
                    prior_rejected = 1
                total["worlds"]+=1
                total["source_actions"]+=len(ledger)
                total["full_source_audit"]+=64
                total["heldout_compositions"]+=32
                total["stageA_correct"]+=stage_a_audit["correct"]
                total["stageA_confident_wrong"]+=stage_a_audit["wrong_confident"]
                total["stageB_correct"]+=stage_b_audit["correct"]
                total["stageB_confident_wrong"]+=stage_b_audit["wrong_confident"]
                total["stageB_abstain"]+=stage_b_audit["abstain"]
                total["stageB_unseen_correct"]+=stage_b_audit["unseen_correct"]
                total["stageB_unseen_wrong"]+=stage_b_audit["unseen_wrong"]
                total["stageB_unseen_total"]+=stage_b_audit["unseen_total"]
                total["forced_correct"]+=forced["correct"]
                total["forced_wrong"]+=forced["wrong_confident"]
                total["exact_memory_correct"]+=memory_audit["correct"]
                total["exact_memory_wrong"]+=memory_audit["wrong_confident"]
                total["tree_correct"]+=tree_audit["correct"]
                total["tree_wrong"]+=tree_audit["wrong_confident"]
                total["batch_forced_correct"]+=batch_audit["correct"]
                total["batch_forced_wrong"]+=batch_audit["wrong_confident"]
                total["composition_direct_correct"]+=composite_b["correct"]
                total["composition_direct_wrong"]+=composite_b["wrong_confident"]
                total["composition_exact_memory_correct"]+=composite_memory["correct"]
                total["composition_tree_correct"]+=composite_tree["correct"]
                total["stageA_retained_correct"]+=stage_a_retained
                total["stageA_eligible_correct"]+=stage_a_eligible
                total["weights_changed_worlds"]+=int(changed>0)
                total["cold_snapshots"]+=1
                total["independent_batch_converged_worlds"]+=int(
                    fit["objective_stationarity_infinity"]<=1e-7)
                total["prior_symbolic_rejected_worlds"]+=prior_rejected
                reports.append({
                    "seed":seed,
                    "family":world.family,
                    "source":world.receipt(),
                    "charged_training_ledger_sha256":_digest(ledger),
                    "charged_action_count":96,
                    "stageA_neural_sha256":sha256(a_snap.encode("ascii")).hexdigest(),
                    "stageB_neural_sha256":sha256(b_snap.encode("ascii")).hexdigest(),
                    "stageA_audit":stage_a_audit,
                    "stageB_audit":stage_b_audit,
                    "forced_audit":forced,
                    "memory_audit":memory_audit,
                    "tree_audit":tree_audit,
                    "batch_audit":batch_audit,
                    "compositions":{
                        "neural":composite_b,
                        "memory":composite_memory,
                        "tree":composite_tree
                    },
                    "stageA_retained_correct":stage_a_retained,
                    "stageA_eligible_correct":stage_a_eligible,
                    "changed_readout_coefficients":changed,
                    "neural_parameter_count":writer.parameter_count(),
                    "stageB_nonzero_readout_parameters":writer.nonzero_learned_weights(),
                    "neural_weight_plus_covariance_bytes":writer.weight_bytes(),
                    "batch_convergence":fit,
                    "max_batch_online_coefficient_difference":coefficient_diff,
                    "prior_wsp67_symbolic_rejected":bool(prior_rejected),
                    "batch_fit_wall_seconds":round(batch_wall,6),
                    "total_world_wall_seconds":round(time.perf_counter()-start_wall,6),
                    "total_world_cpu_seconds":round(time.process_time()-start_cpu,6)
                })
        self.assertEqual(total["worlds"],12)
        self.assertEqual(total["source_actions"],12*96)
        self.assertEqual(total["full_source_audit"],768)
        self.assertEqual(total["heldout_compositions"],384)
        self.assertEqual(total["cold_snapshots"],12)
        self.assertTrue(all(x["stageB_audit"]["unseen_correct"]+
                            x["stageB_audit"]["unseen_wrong"]+
                            x["stageB_audit"]["unseen_abstain"]==
                            x["stageB_audit"]["unseen_total"] for x in reports))
        retention = (
            total["stageA_retained_correct"]/total["stageA_eligible_correct"]
            if total["stageA_eligible_correct"] else 0.0
        )
        gates={
            "true_unseen_correct_ge_40":total["stageB_unseen_correct"]>=40,
            "confident_correct_ge_160":total["stageB_correct"]>=160,
            "beat_memory_by_25":
                total["stageB_correct"]-total["exact_memory_correct"]>=25,
            "confident_errors_le_16":total["stageB_confident_wrong"]<=16,
            "two_action_compositions_ge_96":
                total["composition_direct_correct"]>=96,
            "retention_ge_90pct":retention>=0.90,
            "changed_weights_ge_10_worlds":total["weights_changed_worlds"]>=10,
            "cold_snapshots_12":total["cold_snapshots"]==12,
            "batch_stationarity_le_1e-7":
                max_normal_equation_residual<=1e-7 and
                total["independent_batch_converged_worlds"]==12,
            "batch_online_coeff_diff_le_2e-6":
                max_coefficient_difference<=2e-6
        }
        status=("SELFTEST_SIGNAL" if all(gates.values())
                else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP68_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":status,
            "criteria":gates,
            "retention_rate":round(retention,8),
            "max_independent_batch_coefficient_difference":
                max_coefficient_difference,
            "max_independent_batch_optimality_residual":
                max_normal_equation_residual,
            "totals":total,
            "worlds":reports
        },sort_keys=True,separators=(",",":")))
        # Frozen hypothesis misses remain negative, never Python test fixes.


if __name__=="__main__":
    unittest.main()
