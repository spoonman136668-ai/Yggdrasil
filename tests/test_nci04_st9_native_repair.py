"""ST9 genuine eight TRAIN intervention native repair / conventional fixtures.

All source worlds are from the eight prereg TRAIN ids. Do not inspect
held/new-rule data or use a source-private coefficient as a learner input.
"""
import json
import unittest

from research.nci04_st9.private_world import PrivateWorld
from research.nci04_st9.native_repair import (
    NativeRepair8,features,canonical
)
from research.nci04_st9.matched_controls import (
    ConventionalGF2,make_models,restore_all,select_active,
    active_plan,FROZEN_ACTIVE,ACTOR_GROUPS,
    PASSIVE_DISPERSED,PASSIVE_REPEAT
)


def one_real_episode(cohort,law,seed,B,train=True):
    world=PrivateWorld(law,seed,0)
    for model in cohort.values():
        model.reset_episode()
    for action in (0,B+1):
        public=world.public()
        forecasts={name:model.predict(public,action)
                   for name,model in cohort.items()}
        after,target=world.step(action)
        for name,model in cohort.items():
            assert model.observe(public,action,target,after,train=train)==forecasts[name]


def training_only_active(cohort):
    laws=(3,5,7,11,13,17,19,23)
    for index,(law,B) in enumerate(zip(laws,FROZEN_ACTIVE)):
        one_real_episode(cohort,law,100+index,B,True)


class ST9NativeMemoryRepair(unittest.TestCase):
    def test_frozen_public_actor_is_independent_of_private_law(self):
        self.assertEqual(active_plan(),FROZEN_ACTIVE)
        self.assertEqual(len(set(FROZEN_ACTIVE)),8)
        self.assertEqual(select_active(tuple()),1)
        self.assertEqual(select_active((1,2)),3)
        self.assertEqual(len(PASSIVE_DISPERSED),8)
        self.assertEqual(len(PASSIVE_REPEAT),8)

    def test_unknown_original_linear_rule_repair_trigger_and_exact_rank(self):
        cohort={"candidate":NativeRepair8("repair"),
                "no_replay":NativeRepair8("no_replay"),
                "no_growth":NativeRepair8("no_growth"),
                "adaptive_conventional":ConventionalGF2(
                    "adaptive_conventional"),
                "full_active":ConventionalGF2("full_active")}
        training_only_active(cohort)
        m=cohort["candidate"]
        self.assertEqual(m.updates,8)
        self.assertEqual(m.contradictions,1)
        self.assertEqual(m.growth_events,1)
        self.assertEqual(m.degree,2)
        self.assertEqual(m.rank,8)
        self.assertGreaterEqual(m.pre_growth_replay_count,2)
        self.assertEqual(m.post_growth_conflicts,0)
        self.assertLess(cohort["no_replay"].rank,8)
        self.assertEqual(cohort["no_growth"].degree,1)
        self.assertEqual(cohort["adaptive_conventional"].rank,8)
        self.assertEqual(cohort["full_active"].rank,8)
        self.assertEqual(m.accounting()["max_public_replay_cache_bytes"]
                         if "max_public_replay_cache_bytes" in m.accounting()
                         else m.accounting()["public_replay_cache_bytes_max"],16)

    def test_original_train_interface_no_private_source_coefficients(self):
        m=NativeRepair8()
        world=PrivateWorld(3,100,0)
        for action in (0,2):
            pre=world.public()
            prediction=m.predict(pre,action)
            self.assertEqual(prediction,[.5]*8)
            after,target=world.step(action)
            self.assertEqual(prediction,m.observe(pre,action,target,after))
        self.assertEqual(m.updates,1)
        self.assertEqual(m.rank,1)
        self.assertFalse(m.accounting()["source_private_coefficients_seen"])

    def test_true_native_cold_episode_midstream_and_after_growth(self):
        m=NativeRepair8()
        training_only_active({"candidate":m})
        m.reset_episode()
        world=PrivateWorld(3,100,0)
        pre=world.public();after,target=world.step(0)
        m.observe(pre,0,target,after,train=False)
        frozen=m.snapshot()
        clone=NativeRepair8.restore(frozen)
        self.assertEqual(clone.snapshot(),frozen)
        pre=world.public()
        self.assertEqual(m.predict(pre,3),clone.predict(pre,3))
        after,target=world.step(3)
        self.assertEqual(m.observe(pre,3,target,after,train=False),
                         clone.observe(pre,3,target,after,train=False))
        self.assertEqual(m.snapshot(),clone.snapshot())

    def test_no_replay_and_no_growth_remain_distinct(self):
        a=NativeRepair8("no_replay")
        b=NativeRepair8("no_growth")
        training_only_active({"no_replay":a,"no_growth":b})
        self.assertEqual(a.growth_events,1)
        self.assertEqual(a.pre_growth_replay_count,0)
        self.assertLess(a.rank,8)
        self.assertGreaterEqual(b.contradictions,1)
        self.assertEqual(b.growth_events,0)
        self.assertEqual(b.degree,1)

    def test_strong_conventional_public_precondition_and_memory_equal(self):
        a=NativeRepair8()
        b=ConventionalGF2("adaptive_conventional")
        training_only_active({"native":a,"conventional":b})
        self.assertEqual(a.degree,b.degree)
        self.assertEqual(a.rank,b.rank)
        self.assertEqual(a.updates,b.updates)
        self.assertEqual(a.pre_growth_replay_count,b.public_replay_count)
        self.assertEqual(a.accounting()["learned_GF2_evidence_bits_max"],
                         b.accounting()["max_GF2_learned_augmented_bits"])

    def test_erase_not_counted_as_persistent_learning(self):
        m=NativeRepair8("erase")
        one_real_episode({"erase":m},3,100,1)
        self.assertEqual(m.rank,1)
        m.reset_episode()
        self.assertEqual(m.rank,0)
        self.assertEqual(m.experiences,[])
        self.assertEqual(m.growth_events,0)

    def test_same_original_eight_action_budget_in_each_arm(self):
        cohort=make_models()
        self.assertEqual(len(cohort),8)
        self.assertEqual(len(ACTOR_GROUPS),8)
        for name,m in cohort.items():
            seq=(FROZEN_ACTIVE if ACTOR_GROUPS[name]=="active"
                 else PASSIVE_DISPERSED if ACTOR_GROUPS[name]=="dispersed"
                 else PASSIVE_REPEAT)
            for index,(law,B) in enumerate(zip(
                (3,5,7,11,13,17,19,23),seq
            )):
                one_real_episode({name:m},law,100+index,B)
            self.assertEqual(m.updates,8)
            self.assertFalse(
                m.accounting().get("source_private_coefficients_seen",
                                   m.accounting().get("inferred_source_private_coefficients_seen",True))
            )

    def test_all_cold_model_snapshots_exact(self):
        models=make_models()
        for name,m in models.items():
            one_real_episode({name:m},3,100,1)
        snapshots={name:m.snapshot() for name,m in models.items()}
        recovered=restore_all(snapshots)
        self.assertEqual(snapshots,{name:m.snapshot()
                                     for name,m in recovered.items()})

    def test_invalid_future_target_and_wrong_action_atomic(self):
        m=NativeRepair8()
        world=PrivateWorld(3,100,0)
        before=world.public();snap=m.snapshot()
        for act,target,after,train in ((2,(0,)*8,before,True),
                                       (0,(1,)*8,before,True),
                                       (0,(0,)*8,before,1),
                                       (0,(0,)*8,before,"yes")):
            with self.assertRaises(ValueError):
                m.observe(before,act,target,after,train=train)
            self.assertEqual(m.snapshot(),snap)

    def test_noncanonical_native_and_conventional_states_rejected(self):
        m=NativeRepair8()
        one_real_episode({"candidate":m},3,100,1)
        original=json.loads(m.snapshot())
        for patch in ({"schema":"bad"},{"phase":3},{"rank":9},
                      {"rows":[True]*4},{"degree":2},
                      {"updates":True},{"experiences":[[16,5]]},
                      {"growth_events":2},{"rotation":9}):
            d=dict(original);d.update(patch)
            with self.assertRaises(ValueError):
                NativeRepair8.restore(canonical(d))
        c=ConventionalGF2()
        one_real_episode({"conventional":c},3,100,1)
        d=json.loads(c.snapshot());d["rows"]=[True]*8
        with self.assertRaises(ValueError):
            ConventionalGF2.restore(canonical(d))

    def test_features_have_exact_public_linear_and_quadratic_family(self):
        self.assertEqual(features(0,2),0)
        self.assertEqual(features(15,1).bit_count(),4)
        self.assertEqual(features(15,2).bit_count(),8)
        self.assertNotEqual(features(3,2)>>4,0)


if __name__=="__main__":
    unittest.main()
