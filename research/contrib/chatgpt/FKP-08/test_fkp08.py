"""FKP-08 focused source/learner boundaries. Fixture-only, NO original DEV first-use."""
import unittest
from source import Source,CONTEXTS,MOTIF_MASKS,cohort
from model import Memory,CANDIDATES,standard_baseline_sizes

class FKP08Tests(unittest.TestCase):
    def test_source_fixture_paid_actions_and_disjoint_held(self):
        source=Source()
        x=source.view(700,1)
        self.assertEqual(cohort(700),"fixture")
        self.assertEqual(len(x.choices),128)
        self.assertEqual(len(x.held),128)
        self.assertFalse(set(x.choices)&set(x.held))
        self.assertEqual(len(set(x.choices+x.held)),256)
        for action in x.choices[:16]:
            self.assertIn(source.observe(700,1,action),(0,1))
        with self.assertRaises(PermissionError):
            source.observe(700,1,x.choices[0])
        with self.assertRaises(PermissionError):
            source.observe(700,1,x.choices[16])
        with self.assertRaises(ValueError):
            source.observe(700,1,256)
        with self.assertRaises(PermissionError):
            source.view(1800,1) if False else source.observe(1800,1,0)
        with self.assertRaises(PermissionError):
            source.held_dev(1800,1,())
        with self.assertRaises(ValueError):
            source.held_dev(700,1,x.held)

    def test_source_public_base_from_real_256_observations_fixture(self):
        source=Source()
        view=source.view(701,0)
        history=tuple((x,source.observe(701,0,x)) for x in view.choices)
        self.assertEqual(len(history),256)
        with self.assertRaises(PermissionError):
            source.observe(701,0,0)
        self.assertEqual(len({x for x,y in history}),256)
        self.assertTrue(all(y in (0,1) for x,y in history))

    def test_candidate_pair_grammar_has_exactly_6216(self):
        self.assertEqual(len(MOTIF_MASKS),112)
        self.assertEqual(len(CANDIDATES),6216)
        self.assertEqual(len(set(CANDIDATES)),6216)
        self.assertTrue(all(0<=a<b<112 for a,b in CANDIDATES))

    def test_shared_version_weight_repair_from_synthetic_evidence(self):
        mem=Memory()
        context=800
        zero=tuple((x,0) for x in range(256))
        mem.set_base(context,zero)
        original=mem.predict(context,0,tuple(range(256)))
        target_patch=MOTIF_MASKS[3]^MOTIF_MASKS[24]
        actions=tuple(range(0,256,16))
        history=tuple((x,(target_patch>>x)&1) for x in actions)
        fit=mem.fit(context,1,history)
        self.assertEqual(fit["source_actions"],16)
        self.assertEqual(fit["best_mismatches"],0)
        self.assertEqual(mem.predict(context,0,tuple(range(256))),original)
        with self.assertRaises(ValueError):
            mem.fit(context,1,history)
        with self.assertRaises(ValueError):
            mem.fit(context,2,history[:15])
        with self.assertRaises(ValueError):
            mem.predict(context,3,actions)

    def test_lossless_fixed_capacity_checkpoint_and_corruption(self):
        mem=Memory()
        for context in CONTEXTS:
            mem.set_base(context,tuple((x,(x+context)&1) for x in range(256)))
            for version in (1,2,3):
                mem.patches[(context,version)]=(0,1)
        raw=mem.raw_weights()
        self.assertEqual(len(raw),1216)
        snap=mem.snapshot()
        self.assertEqual(len(snap),1252)
        restored=Memory.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        for version in (0,1,2,3):
            self.assertEqual(restored.rule(800,version),mem.rule(800,version))
        changed=bytearray(snap)
        changed[10]^=1
        with self.assertRaises(ValueError):
            Memory.restore(bytes(changed))
        measures=standard_baseline_sizes(mem)
        self.assertEqual(measures["bitsets_raw"],4096)
        self.assertEqual(measures["learned_delta_raw"],1216)
        self.assertTrue(measures["conventional_exact_delta_ties_candidate"])

if __name__=="__main__":
    unittest.main()
