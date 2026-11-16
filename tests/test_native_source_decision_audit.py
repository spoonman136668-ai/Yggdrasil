"""Source-only mechanics; no original environment and no primary decision scores."""
import ast
from fractions import Fraction
import importlib.util
import inspect
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr23_mechanical_checks",
    ROOT/"research/contrib/chatgpt/NKR-23/decision_audit.py")
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
REFERENCE=ROOT/"research/contrib/chatgpt/NKR-23/original_mdp.py.txt"

class SourceDecisionAuditTests(unittest.TestCase):
    def test_original_public_source_exact_git_blob(self):
        self.assertEqual(a.git_blob(REFERENCE.read_bytes()),a.SOURCE_BLOB)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"changed.txt";p.write_bytes(REFERENCE.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"PINNED_ORIGINAL_SOURCE_BLOB"):
                a.load_equations(p)

    def test_restricted_ast_forbids_calls_and_private_attributes(self):
        for expression in ("anything()", "self.private", "open('x')", "x+1"):
            with self.assertRaises(ValueError):
                a.expression(ast.parse(expression,mode="eval").body,{"x":0,"s":1})

    def test_all_joint_probabilities_nonnegative_normalized(self):
        k,r=a.kernel_from_source(REFERENCE)
        self.assertEqual(r["exact_boolean_assignments_checked"],32)
        self.assertEqual(len(k),4)
        for joint in k.values():
            self.assertEqual(sum(sum(v) for v in joint),1)
            self.assertTrue(all(0<=q<=1 for row in joint for q in row))

    def test_source_reward_marginal_and_transition(self):
        k,_=a.kernel_from_source(REFERENCE)
        for (s,action),j in k.items():
            self.assertEqual(sum(j[1]),Fraction(41,50) if s==action else Fraction(9,50))
            self.assertEqual(j[0][1]+j[1][1],
                             Fraction(41,50) if (s|action)==0 else Fraction(9,50))

    def test_oracle_value_is_same_for_every_starting_state(self):
        k,_=a.kernel_from_source(REFERENCE)
        for initial in ((Fraction(1),Fraction(0)),(Fraction(0),Fraction(1)),
                        (Fraction(1,2),Fraction(1,2))):
            self.assertEqual(a.exact_return(k,"source_oracle",{},initial,24),
                             7*Fraction(41,50))

    def test_always_zero_matches_frozen_zero_map(self):
        k,_=a.kernel_from_source(REFERENCE)
        initial=(Fraction(1,2),Fraction(1,2))
        self.assertEqual(a.exact_return(k,"always0",{},initial,8),
                         a.exact_return(k,"native",{0:0,1:0},initial,8))
        value=a.exact_return(k,"mechanical",{},initial,8)
        self.assertTrue(7*Fraction(9,50)<=value<=7*Fraction(41,50))

    def test_horizon_respects_original_truncation(self):
        k,_=a.kernel_from_source(REFERENCE)
        with self.assertRaises(ValueError):
            a.exact_return(k,"always0",{},(Fraction(1,2),Fraction(1,2)),25)
        with self.assertRaises(ValueError):
            a.exact_return(k,"always0",{},(Fraction(1),Fraction(1)),8)

    def test_learning_uses_public_counts_only_and_bayes_parity(self):
        data={}
        for seed in a.nkr19.SEEDS:
            data[seed]=[dict(before=i%2,action=(i//2)%2,reward=i%2,after=1-i%2,
                            terminated=False,truncated=i==30) for i in range(31)]
        for count in a.SCALES:
            maps,pin=a.learned_maps(data,count)
            self.assertEqual(len(maps),4)
            self.assertEqual(len(pin),64)
        source=inspect.getsource(a.learned_maps)
        for forbidden in ("kernel","source_oracle","41,50","original_mdp"):
            self.assertNotIn(forbidden,source)

    def test_source_auditor_does_not_execute_original_code(self):
        source=inspect.getsource(a)
        for forbidden in ("import causal_gym","np.random",".reset(",".do(","exec(","eval("):
            self.assertNotIn(forbidden,source)

    def test_replication_metadata_excluded_from_stable_values(self):
        x={"source_candidate_sha":"a","environment":{"python":"x"},"wall_seconds":1,
           "experiments":[{"score":2}]}
        y={"source_candidate_sha":"b","environment":{"python":"y"},"wall_seconds":3,
           "experiments":[{"score":2}]}
        self.assertEqual(a.stable(x),a.stable(y))

if __name__=="__main__":
    unittest.main()
