"""WSP67 frozen SELFTEST of direct programming of ACTUAL executable neural weights.

All arms see the SAME charged 96-step physically continuous source-blind
evidence. Stage A after 64, Stage B after another 32. Actual neural
W1/b1/W2/b2/W3/b3 matrices provide every direct test prediction;
source-private physics is called ONLY by evaluator for scoring.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import zip_longest
from random import Random
from pathlib import Path
import json
import time
import unittest

from source import SEEDS,STATES,ACTIONS,PHASE_A,TRAIN_ACTIONS,COMPOSITES,build_world,rng
from weight_programmer import DirectNeuralProgrammer,NeuralWeights,PREDICATES
from independent_symbolic import IndependentSymbolic,ExactMemory
from conventional_mlp import ConventionalMLP


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()


def audit(predict,world,known):
    record={"correct":0,"wrong_confident":0,"abstain":0,
            "unseen_correct":0,"unseen_wrong":0,"unseen_abstain":0,
            "unseen_total":0}
    for start in STATES:
        for action in ACTIONS:
            guess=predict(start,action)
            truth=world._step_oracle(start,action) # evaluator ONLY
            unseen=(start,action) not in known
            if unseen:
                record["unseen_total"]+=1
            if guess is None:
                record["abstain"]+=1
                if unseen:record["unseen_abstain"]+=1
            elif guess==truth:
                record["correct"]+=1
                if unseen:record["unseen_correct"]+=1
            else:
                record["wrong_confident"]+=1
                if unseen:record["unseen_wrong"]+=1
    assert record["correct"]+record["wrong_confident"]+record["abstain"]==64
    assert record["unseen_correct"]+record["unseen_wrong"]+record["unseen_abstain"]==record["unseen_total"]
    return record


def compose(predict,world,heldout):
    summary={"correct":0,"wrong_confident":0,"abstain":0}
    for case in heldout:
        a,b=case.actions
        first=predict(case.start,a)
        second=predict(first,b) if first is not None else None
        if second is None:
            summary["abstain"]+=1
        elif second==case._finish:
            summary["correct"]+=1
        else:
            summary["wrong_confident"]+=1
    assert sum(summary.values())==len(heldout)
    return summary


def weight_diffs(a,b):
    def members(net):
        out=[]
        for label in ("w1","b1","w2","b2","w3","b3"):
            data=getattr(net,label)
            if label.startswith("w"):
                out.extend((label,i,j,x) for i,row in enumerate(data)
                           for j,x in enumerate(row))
            else:
                out.extend((label,i,None,x) for i,x in enumerate(data))
        return {(label,i,j):v for label,i,j,v in out}
    before,after=members(a),members(b)
    keys=set(before)|set(after)
    return sum(before.get(k)!=after.get(k) for k in keys)


class FrozenDirectWeightProgramming(unittest.TestCase):
    def test_isolation_and_neural_gate(self):
        writer_text=(Path(__file__).parent/"weight_programmer.py").read_text("utf8")
        sgd_text=(Path(__file__).parent/"conventional_mlp.py").read_text("utf8")
        symbolic_text=(Path(__file__).parent/"independent_symbolic.py").read_text("utf8")
        for content in (writer_text,sgd_text,symbolic_text):
            self.assertNotIn("from source import",content)
            self.assertNotIn("import source",content)
        self.assertIn("self.w1",writer_text)
        self.assertIn("self.w2",writer_text)
        self.assertIn("self.w3",writer_text)
        self.assertEqual(DirectNeuralProgrammer.gradient_steps,0)
        self.assertEqual(len(PREDICATES),34)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(4101,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(3101)
        for seed in SEEDS:
            self.assertEqual(build_world(seed).receipt(),build_world(seed).receipt())
        world=build_world(4101)
        programmer=DirectNeuralProgrammer()
        first=world.training_session().step(0)
        with self.assertRaises(ValueError):
            from source import Experience
            programmer.observe(Experience((1,1,1,1),0,first.after))
        self.assertEqual(programmer.ledger,[])
        programmer.observe(first)
        with self.assertRaises(ValueError):
            programmer.observe(first)
        with self.assertRaises(ValueError):
            programmer.observe(type(first)(programmer.current,0,programmer.current,0))

    def test_eight_worlds_two_stage_weight_edit_and_controls(self):
        total={
            "worlds":0,"physical_queries":0,"heldout_composites":0,
            "A_correct":0,"A_wrong_confident":0,"A_abstain":0,
            "B_correct":0,"B_wrong_confident":0,"B_abstain":0,
            "B_unseen_correct":0,"B_unseen_wrong":0,"B_unseen_abstain":0,
            "B_unseen_total":0,
            "memory_correct":0,"memory_wrong_confident":0,
            "symbolic_correct":0,"symbolic_wrong_confident":0,
            "sgd_forced_correct":0,"sgd_confident_correct":0,
            "sgd_confident_wrong":0,"sgd_unconverged_worlds":0,
            "A_compositions_correct":0,"B_compositions_correct":0,
            "B_compositions_wrong":0,"memory_compositions_correct":0,
            "symbolic_compositions_correct":0,
            "sgd_compositions_forced_correct":0,
            "retention_violations":0,"weight_edited_worlds":0,
            "cold_restores":0,"source_actions":0
        }
        receipts=[]
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                session=world.training_session()
                p=DirectNeuralProgrammer()
                r=rng(seed,"charged-random-continuous-action-policy")
                start_cpu=time.process_time()
                start_wall=time.perf_counter()
                for _ in range(PHASE_A):
                    row=session.step(r.choice(ACTIONS))
                    p.observe(row)
                self.assertEqual(len(session.ledger),64)
                self.assertEqual(len(p.ledger),64)
                stage_a=p.compile()
                stage_a_snapshot=stage_a.snapshot()
                cold_a=NeuralWeights.restore(stage_a_snapshot)
                self.assertEqual(cold_a.snapshot(),stage_a_snapshot)
                before_a={(s,a):stage_a.predict(s,a) for s in STATES for a in ACTIONS}
                seen_a={(b,a) for b,a,y in p.ledger}
                self.assertTrue(all(p.ledger[i][2]==p.ledger[i+1][0]
                                    for i in range(63)))
                self.assertEqual(stage_a.nonzero_parameters()>0,True)
                old_weights_hash=sha256(stage_a_snapshot.encode("ascii")).hexdigest()
                for _ in range(TRAIN_ACTIONS-PHASE_A):
                    row=session.step(r.choice(ACTIONS))
                    p.observe(row)
                self.assertEqual(len(p.ledger),96)
                self.assertEqual(len(session.ledger),96)
                self.assertTrue(all(p.ledger[i][2]==p.ledger[i+1][0]
                                    for i in range(95)))
                self.assertEqual(p.ledger[0][0],(0,0,0,0))
                begin_programming=time.perf_counter()
                stage_b=p.compile()
                program_wall=time.perf_counter()-begin_programming
                stage_b_snapshot=stage_b.snapshot()
                cold_b=NeuralWeights.restore(stage_b_snapshot)
                self.assertEqual(cold_b.snapshot(),stage_b_snapshot)
                self.assertNotIn('"ledger"',stage_b_snapshot)
                self.assertNotIn('"rules"',stage_b_snapshot)
                with self.assertRaises(ValueError):
                    NeuralWeights.restore(stage_b_snapshot.replace(
                        "wsp67.executable-neural-weights.v1",
                        "wsp67.executable-neural-weights.v2"))
                for s in STATES:
                    for a in ACTIONS:
                        self.assertEqual(cold_a.predict(s,a),stage_a.predict(s,a))
                        self.assertEqual(cold_b.predict(s,a),stage_b.predict(s,a))
                self.assertIsNone(stage_b.zeros_ablation().predict((0,0,0,0),0))
                self.assertIsNone(stage_b.confidence_erase_ablation().predict((0,0,0,0),0))
                stage_changes=weight_diffs(stage_a,stage_b)
                changed=int(stage_changes>0)
                old_hash=sha256(stage_b_snapshot.encode("ascii")).hexdigest()
                self.assertEqual(p.gradient_steps,0)
                self.assertGreater(stage_b.parameter_count(),0)
                symbolic=IndependentSymbolic(p.ledger)
                memory=ExactMemory(p.ledger)
                for s in STATES:
                    for a in ACTIONS:
                        self.assertEqual(stage_b.predict(s,a),symbolic.predict(s,a))
                # The compiled matrix is self-contained: the programmer is
                # deliberately destroyed before heldout neural inference.
                p._candidate_functions=lambda *args: (_ for _ in ()).throw(
                    RuntimeError("symbolic writer not permitted at inference"))
                known={(b,a) for b,a,y in p.ledger}
                a_audit=audit(stage_a.predict,world,seen_a)
                b_audit=audit(cold_b.predict,world,known)
                memory_audit=audit(memory.predict,world,known)
                symbolic_audit=audit(symbolic.predict,world,known)
                retention=sum(1 for (s,a),guess in before_a.items()
                              if guess is not None and stage_b.predict(s,a)!=guess)
                tests=world.composite_tests()
                a_comp=compose(stage_a.predict,world,tests)
                b_comp=compose(cold_b.predict,world,tests)
                m_comp=compose(memory.predict,world,tests)
                sym_comp=compose(symbolic.predict,world,tests)
                # Independently optimized conventional network using exactly
                # the same 96 charged examples and no hidden physics.
                grad=ConventionalMLP(seed)
                begin_sgd=time.perf_counter()
                train_diag=grad.fit(p.ledger)
                sgd_wall=time.perf_counter()-begin_sgd
                grad_forced=audit(lambda s,a:grad.predict(s,a),world,known)
                grad_confident=audit(lambda s,a:grad.predict(s,a,confidence=True),world,known)
                grad_composed=compose(lambda s,a:grad.predict(s,a),world,tests)
                total["worlds"]+=1
                total["physical_queries"]+=64
                total["heldout_composites"]+=len(tests)
                total["A_correct"]+=a_audit["correct"]
                total["A_wrong_confident"]+=a_audit["wrong_confident"]
                total["A_abstain"]+=a_audit["abstain"]
                total["B_correct"]+=b_audit["correct"]
                total["B_wrong_confident"]+=b_audit["wrong_confident"]
                total["B_abstain"]+=b_audit["abstain"]
                total["B_unseen_correct"]+=b_audit["unseen_correct"]
                total["B_unseen_wrong"]+=b_audit["unseen_wrong"]
                total["B_unseen_abstain"]+=b_audit["unseen_abstain"]
                total["B_unseen_total"]+=b_audit["unseen_total"]
                total["memory_correct"]+=memory_audit["correct"]
                total["memory_wrong_confident"]+=memory_audit["wrong_confident"]
                total["symbolic_correct"]+=symbolic_audit["correct"]
                total["symbolic_wrong_confident"]+=symbolic_audit["wrong_confident"]
                total["sgd_forced_correct"]+=grad_forced["correct"]
                total["sgd_confident_correct"]+=grad_confident["correct"]
                total["sgd_confident_wrong"]+=grad_confident["wrong_confident"]
                total["sgd_unconverged_worlds"]+=int(not train_diag["fully_trained"])
                total["A_compositions_correct"]+=a_comp["correct"]
                total["B_compositions_correct"]+=b_comp["correct"]
                total["B_compositions_wrong"]+=b_comp["wrong_confident"]
                total["memory_compositions_correct"]+=m_comp["correct"]
                total["symbolic_compositions_correct"]+=sym_comp["correct"]
                total["sgd_compositions_forced_correct"]+=grad_composed["correct"]
                total["retention_violations"]+=retention
                total["weight_edited_worlds"]+=changed
                total["cold_restores"]+=1
                total["source_actions"]+=len(p.ledger)
                receipts.append({
                    "seed":seed,"source":world.receipt(),
                    "charged_ledger_sha256":digest(p.ledger),
                    "all_stage_a_actions":64,"all_stage_b_actions":96,
                    "stage_a_neural_sha256":old_weights_hash,
                    "stage_b_neural_sha256":old_hash,
                    "stage_a":a_audit,"stage_b":b_audit,
                    "memorization":memory_audit,
                    "symbolic":symbolic_audit,
                    "SGD_forced":grad_forced,
                    "SGD_confident":grad_confident,
                    "SGD_train":train_diag,
                    "two_action":{"A":a_comp,"B":b_comp,"memory":m_comp,
                                  "symbolic":sym_comp,"SGD":grad_composed},
                    "stage_b_weight_changes":stage_changes,
                    "stage_b_parameter_count":stage_b.parameter_count(),
                    "stage_b_nonzero_params":stage_b.nonzero_parameters(),
                    "stage_b_snapshot_bytes":len(stage_b_snapshot.encode("ascii")),
                    "no_forgetting_count":retention,
                    "all_test_unseen_physical_count":b_audit["unseen_total"],
                    "program_wall_seconds":round(program_wall,6),
                    "SGD_wall_seconds":round(sgd_wall,6),
                    "total_world_wall_seconds":round(time.perf_counter()-start_wall,6),
                    "total_world_cpu_seconds":round(time.process_time()-start_cpu,6)
                })
        self.assertEqual(total["worlds"],8)
        self.assertEqual(total["physical_queries"],512)
        self.assertEqual(total["heldout_composites"],256)
        self.assertEqual(total["source_actions"],8*96)
        self.assertEqual(total["cold_restores"],8)
        self.assertTrue(all(x["stage_b"]["unseen_correct"]+
                            x["stage_b"]["unseen_wrong"]+
                            x["stage_b"]["unseen_abstain"]==
                            x["stage_b"]["unseen_total"] for x in receipts))
        passed={
            "unseen_correct_ge_48":total["B_unseen_correct"]>=48,
            "no_confident_errors":total["B_wrong_confident"]==0,
            "two_action_correct_ge_120":total["B_compositions_correct"]>=120,
            "beats_exact_lookup_by_20":
                total["B_correct"]-total["memory_correct"]>=20,
            "no_stage_A_forgetting":total["retention_violations"]==0,
            "changed_neural_weights_4_worlds":total["weight_edited_worlds"]>=4,
            "cold_inference_and_tamper_pass":total["cold_restores"]==8
        }
        category=("SELFTEST_SIGNAL" if all(passed.values())
                  else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP67_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":category,"criteria":passed,"totals":total,
            "worlds":receipts
        },sort_keys=True,separators=(",",":")))
        # A negative development criterion is never repaired by retuning.


if __name__=="__main__":
    unittest.main()
