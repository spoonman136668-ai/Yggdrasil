"""HC09 engineering tests: no hidden physics, checkpoint, equal physical budgets."""
import unittest,json

from model import DualRegimeCausalCells,effect,FULL,SNAP_LIMIT
from conventional_control import ConventionalContextModel,eval_rule
from eval_dev import World,one_world,SEEDS


class DualRegimeTests(unittest.TestCase):
    def test_independent_conventional_rule_library_identical(self):
        for s in range(16):
            for h in range(40):
                self.assertEqual(effect(s,h),eval_rule(s,h))

    def test_executable_majority_not_representable_as_affine(self):
        model=DualRegimeCausalCells()
        h=32   # majority of sites 0,1,2, zero sign
        for state in range(16):
            result=state^(effect(state,h)<<2)
            model.observe(state,2,result)
        self.assertEqual(model.banks[0][2],1<<h)
        for s in range(16):
            self.assertEqual(model.predict(s,2),s^(effect(s,h)<<2))
        self.assertEqual(model.capacity_bits,320)

    def test_true_A_B_A_switch_and_cold_reactivation(self):
        m=DualRegimeCausalCells()
        m.observe(0,0,0)
        m.observe(0,0,1)
        self.assertEqual(m.splits,1)
        self.assertEqual(len(m.banks),2)
        m.observe(0,0,0)
        self.assertEqual(m.reactivations,1)
        self.assertEqual(m.active,0)
        self.assertFalse(m.unresolved)
        self.assertEqual(m.predict(0,0),0)
        snap=m.snapshot()
        self.assertEqual(DualRegimeCausalCells.restore(snap).snapshot(),snap)

    def test_equal_capacity_no_reactivation_preserves_and_abstains(self):
        m=DualRegimeCausalCells(reactivate=False)
        m.observe(0,0,0)
        m.observe(0,0,1)
        first=m.banks[0][0]
        m.observe(0,0,0)
        self.assertEqual(m.banks[0][0],first)
        self.assertEqual(m.splits,1)
        self.assertEqual(m.reactivations,0)
        self.assertTrue(m.unresolved)
        self.assertIsNone(m.predict(0,0))
        self.assertEqual(m.capacity_bits,320)

    def test_all_controls_charged_equal_actions_without_oracle(self):
        for seed,grp in ((71001,"stationary_affine"),
                         (71009,"stationary_majority"),
                         (71017,"A_B_A"),
                         (71025,"out_of_grammar")):
            row=one_world(seed,grp)
            total=32 if grp=="A_B_A" else 48
            cap=6 if grp=="A_B_A" else 8
            for name,arm in row["arms"].items():
                with self.subTest(seed=seed,arm=name):
                    self.assertEqual(arm["total_charged"],total)
                    self.assertEqual(arm["causal_observations"]+
                                     arm["charged_flips"],total)
                    self.assertLessEqual(arm["charged_flips"],cap)
                    self.assertLessEqual(arm["snapshot_bytes"],4096)
                    self.assertTrue(arm["cold_restore"])
                    self.assertEqual(sum(arm["score"][k] for k in
                        ("correct","wrong_confident","abstained")),64)
                    self.assertEqual(arm["score"]["unseen_total"],
                        sum(arm["score"]["unseen_"+k] for k in
                            ("correct","wrong_confident","abstained")))

    def test_evaluator_only_world_checks_do_not_charge(self):
        world=World(71017,"A_B_A")
        for phase in (0,1):
            for s in range(16):
                for a in range(4):
                    world.true_next_for_evaluator(s,a,phase)
        self.assertEqual(world.used,0)
        first=world.charge_flip(0,2)
        self.assertEqual(first,4)
        self.assertEqual(world.used,1)
        world.charge_causal(first,0,1)
        self.assertEqual(world.used,2)

    def test_sources_are_frozen_and_nonoverlapping(self):
        seen=set()
        for grp,seeds in SEEDS.items():
            self.assertEqual(len(seeds),4 if grp=="out_of_grammar" else 8)
            self.assertFalse(seen.intersection(seeds))
            seen.update(seeds)
        self.assertEqual(len(seen),28)
        with self.assertRaises(ValueError):
            World(71001,"A_B_A")

    def test_all_input_rejection_is_atomic(self):
        for cls in (DualRegimeCausalCells,ConventionalContextModel):
            m=cls()
            prior=m.snapshot()
            for invalid in ((-1,0,0),(16,0,0),(0,4,0),
                            (0,0,16),(0,0,2),(True,0,0),(0,True,0)):
                with self.subTest(cls=cls.__name__,invalid=invalid):
                    with self.assertRaises(ValueError):
                        m.observe(*invalid)
                    self.assertEqual(prior,m.snapshot())
            with self.assertRaises(TypeError):
                m.observe(0,0,0,hidden_phase=1)

    def test_canonical_checkpoint_and_tamper_fail_closed(self):
        for cls in (DualRegimeCausalCells,ConventionalContextModel):
            m=cls()
            m.observe(0,0,0)
            m.observe(0,0,1)
            original=m.snapshot()
            self.assertEqual(cls.restore(original).snapshot(),original)
            modified=bytearray(original)
            modified[len(modified)//2]^=1
            for bad in (bytes(modified),original[:-1],original+b" ",
                        bytearray(original),b"x"*(SNAP_LIMIT+1)):
                with self.subTest(cls=cls.__name__,n=len(bad)):
                    with self.assertRaises(ValueError):cls.restore(bad)

    def test_source_blind_action_selection_does_not_mutate_memory(self):
        m=DualRegimeCausalCells()
        prior=m.snapshot()
        for s in range(16):
            what,index=m.choose(s,0,8)
            self.assertIn(what,("flip","causal"))
            self.assertIn(index,range(4))
        self.assertEqual(m.snapshot(),prior)
        with self.assertRaises(ValueError):m.choose(9,9,8)
        with self.assertRaises(ValueError):DualRegimeCausalCells(bank_limit=3)
        with self.assertRaises(ValueError):DualRegimeCausalCells(reactivate=1)


if __name__=="__main__":
    unittest.main()
