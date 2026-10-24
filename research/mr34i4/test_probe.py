"""MR34I4 focused source-free tests; never acquire protected or original episodes."""
import ast
from pathlib import Path
import unittest
import numpy as np

from research.mr34i4 import forward_probe as p


class FakeFrozenNative:
    def __init__(self):
        self.g=np.linspace(-.3,.4,21,dtype=np.float64).reshape(3,7)
        self.roles=np.linspace(-.2,.3,24,dtype=np.float64).reshape(8,3)
    def params(self):
        return self.g,self.roles
    def forward(self,episode,cache=False):
        f=np.arange(56,dtype=np.float64).reshape(8,7)/41.
        s=np.linspace(-.3,.3,8,dtype=np.float64)
        read=f@self.g[1]+self.roles[:,1]
        u=f@self.g[0]+self.roles[:,0]+s*read
        prob=1./(1.+np.exp(-np.clip(u,-35.,35.)))
        ns=np.tanh(f@self.g[2]+self.roles[:,2]*(2.*prob-1.))
        return np.asarray([prob]),[(f,s,read,prob,ns)]


class ForwardStageTests(unittest.TestCase):
    def test_exact_source_free_native_reconstruction(self):
        model=FakeFrozenNative()
        prior=[z.copy() for z in model.params()]
        stages=p.unmodified_native_forward_stages(model,[()])
        self.assertEqual(len(stages),1)
        x=stages[0]
        self.assertEqual(x["source_time_index"],0)
        for name in ("original_u_matmul","original_u_preactivation","original_numpy_exp",
                     "original_predicted_probability","original_cached_predicted_probability",
                     "diagnostic_readonly_scalar_math_exp"):
            self.assertEqual(len(x[name]["hex"]),8)
            self.assertEqual(len(x[name]["sha256"]),64)
        self.assertEqual(x["original_predicted_probability"]["sha256"],
                         x["original_cached_predicted_probability"]["sha256"])
        for a,b in zip(prior,model.params()):
            self.assertEqual(a.tobytes(),b.tobytes())

    def test_frozen_original_source_scope(self):
        self.assertEqual(p.MAX_ORIGINAL_TRAIN_UPDATES,3)
        self.assertEqual(p.FIRST,"e294f1417ac5048f71be79d6db5099c5b6c40f44")
        self.assertEqual(len(p.SEEDS),20)
        self.assertTrue(max(p.SEEDS)<2003)
        self.assertEqual(set(p.SOURCES),set(p.EXPECTED_SOURCE_EVENTS))
        self.assertEqual(p.S4C1_SHA,"8e1561eb1a542e21307bac669c42435cf48e59bd")

    def test_no_held_episode_acquisition_or_native_weight_repair(self):
        tree=ast.parse(Path(p.__file__).read_text())
        f=next(node for node in tree.body if isinstance(node,ast.FunctionDef)
               and node.name=="trace_source")
        src=ast.unparse(f)
        self.assertIn("episodes(root, family, SEEDS)",src)
        self.assertIn("data[:MAX_ORIGINAL_TRAIN_UPDATES]",src)
        self.assertIn("update_exact(",src)
        self.assertNotIn("EVAL",src)
        self.assertNotIn("model.g =",src)
        self.assertNotIn("model.roles =",src)

    def test_diagnostic_scalar_never_replaces_training(self):
        tree=ast.parse(Path(p.__file__).read_text())
        f=next(node for node in tree.body if isinstance(node,ast.FunctionDef)
               and node.name=="unmodified_native_forward_stages")
        src=ast.unparse(f)
        self.assertIn("math.exp",src)
        self.assertIn("np.exp",src)
        self.assertIn("model.forward(episode, cache=True)",src)
        self.assertNotIn("model.analytic_bptt",src)


if __name__=="__main__":
    unittest.main()
