"""CKAD23 frozen new-world action-consequence negative controls."""
import importlib.util
import json
from pathlib import Path
import inspect
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad23_campaign",HERE/"campaign.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CKAD23Controls(unittest.TestCase):
    def test_new_equations_require_conjunction_and_action_interaction(self):
        e=m.episode("conjunctive_terminal","ckad23-unit",101,0)
        self.assertTrue(all(type(v) is int for v in m.GEN.public_views(e)[0]))
        self.assertEqual(e.transition(0)^e.transition(1),1)
        self.assertEqual(m.NewWorld(e.base,"conjunctive_terminal").transition(0),
                         e.base.transition_noise)
        # This public rule differs from source-side XOR target when s1=1,s2=0.
        b=e.base
        if b.s1==1:
            with self.subTest(condition="AND distinct from XOR"):
                self.assertNotEqual(b.s1 ^ 0, (b.s1 & 0))
        f=m.episode("interaction_gate","ckad23-unit",101,0)
        if f.s1==0:self.assertEqual(f.transition(0),f.transition(1))
        else:self.assertNotEqual(f.transition(0),f.transition(1))
        self.assertNotEqual(
            m.episode("conjunctive_terminal","ckad23-unit",101,0).family,
            f.family)

    def test_source_determinism_and_matched_exogenous_draw(self):
        for world in m.WORLDS:
            for seed in m.ENV_SEEDS:
                a=m.episode(world,"ckad23-unit-held",m.source_seed(101,seed),5)
                b=m.episode(world,"ckad23-unit-held",m.source_seed(101,seed),5)
                self.assertEqual(m.GEN.public_views(a),m.GEN.public_views(b))
                self.assertEqual((a.base.hidden,a.base.transition_noise,a.base.reward_noise),
                                 (b.base.hidden,b.base.transition_noise,b.base.reward_noise))
                self.assertEqual(m.GEN.rollout(a,lambda _:0,lambda *_:1),
                                 m.GEN.rollout(b,lambda _:0,lambda *_:1))
        self.assertNotEqual(m.source_seed(101,1009),m.source_seed(202,1009))

    def test_hard_public_bounds_and_callback_scope(self):
        w=m.episode("conjunctive_terminal","ckad23-unit",101,5)
        with self.assertRaisesRegex(ValueError,"FIRST_ACTION"):w.transition(True)
        with self.assertRaisesRegex(ValueError,"SECOND_ACTION"):w._reward(0,0,2)
        with self.assertRaisesRegex(ValueError,"WORLD"):m.episode("unknown","ckad23-unit",101,5)
        self.assertEqual(list(inspect.signature(m.GEN.rollout).parameters),
                         ["episode","choose_first","choose_second"])

    def test_history_protocol_and_hardcoded_bounds(self):
        protocol=json.loads((HERE/"prereg.json").read_bytes())
        self.assertEqual(protocol["parent_sha"],m.PARENT_COMMIT)
        self.assertEqual(protocol["source_dependency"]["sha256"],m.SOURCE_PIN)
        self.assertEqual(protocol["probe_budget_per_case"],16)
        self.assertEqual(protocol["held_per_case_per_world"],48)
        self.assertEqual(protocol["parent_groups"],list(m.SEEDS))
        self.assertEqual(protocol["evaluation_namespace_seeds"],list(m.ENV_SEEDS))
        self.assertEqual(protocol["scientific_pass"],False)
        self.assertEqual(m.digest((m.CK20/"synthetic_world.py").read_bytes()),m.SOURCE_PIN)

if __name__=="__main__":unittest.main()
