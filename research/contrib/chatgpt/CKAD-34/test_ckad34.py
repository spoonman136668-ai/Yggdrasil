"""CKAD34 pre-first-use negative and source-only interface qualification."""
import importlib.util
import itertools
import unittest
from pathlib import Path

from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad34_frozen_campaign",HERE/"campaign.py")
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CKAD34Tests(unittest.TestCase):
    def test_full_rank_input_only_partition(self):
        self.assertEqual([len(c.monomials(k)) for k in (1,2,3)],[7,22,42])
        for seed in (88701,88702): # fixture only, NEVER pilot/primary
            fit,cal,held=c.source_partition(seed)
            self.assertEqual((len(fit),len(cal),len(held)),(42,6,16))
            self.assertEqual(len(set(fit+cal+held)),64)
            all_zero=[[x&31,x>>5,0] for x in fit]
            self.assertEqual(len(c.conventional_fit(all_zero,3)),42)

    def test_native_selects_class_from_witnesses_not_family_label(self):
        fit,cal,held=c.source_partition(88701)
        functions=(
            lambda x:1^((x&13).bit_count()&1),
            lambda x:1^((x&13).bit_count()&1)^int(bool(x&1) and bool(x&2)),
            lambda x:1^((x&13).bit_count()&1)^int(all(x&(1<<i) for i in (0,1,2)))
        )
        for degree,fun in enumerate(functions,1):
            data=[[x&31,x>>5,fun(x)] for x in fit]
            chosen,model=c.native_choose(data)
            self.assertEqual(chosen,degree)
            self.assertEqual(c.choose_degree(data),degree)
            self.assertEqual(c.profile(model,0)["degree"],degree)
            for x in held:
                self.assertEqual(c.native_prob(model,0,x),float(fun(x)))
            raw=model.checkpoint()
            cold=NativeContextAccumulator.restore(raw,digest(raw))
            self.assertEqual(cold.checkpoint(),raw)

    def test_separately_fitted_source_and_ood_negative(self):
        fit,cal,held=c.source_partition(88702)
        fun=lambda x:((x&45).bit_count()&1)^int(all(x&(1<<i) for i in (0,1,2,3)))
        rows=[[x&31,x>>5,fun(x)] for x in fit]
        d,m=c.native_choose(rows)
        self.assertEqual(d,3)
        self.assertEqual(c.profile(m,0)["rank"],42)
        wrong=[x for x in (*cal,*held) if c.native_prob(m,0,x)!=fun(x)]
        self.assertTrue(wrong)
        raw=m.checkpoint()
        self.assertEqual(m.checkpoint(),raw)

    def test_exact_atomically_rejects_contradictory_source(self):
        fit,cal,held=c.source_partition(88701)
        inputs=[[x&31,x>>5,(x&7).bit_count()&1] for x in fit]
        model=c.native_stage(NativeContextAccumulator(5),0,inputs,1)
        before=model.checkpoint()
        conflicting=[list(inputs[0])];conflicting[0][2]^=1
        with self.assertRaises(ValueError):
            c.native_stage(model,0,conflicting,1)
        self.assertEqual(model.checkpoint(),before)

    def test_preserved_frozen_science_and_seed_boundary(self):
        self.assertEqual(c.PILOT,(13741,13742))
        self.assertEqual(c.PRIMARY,(23741,23742,23743))
        self.assertFalse(set(c.PILOT)&set(c.PRIMARY))
        with self.assertRaisesRegex(ValueError,"ONLY_FROZEN_PILOT"):
            c.score(23741)
        for g in c.GRAPHS:
            for bits in itertools.product((0,1),repeat=3):
                self.assertIn(c.C30.composition(g,bits),(0,1))

    def test_strong_conventional_matched_information_and_no_truth(self):
        fit,cal,held=c.source_partition(88702)
        data=[[x&31,x>>5,(x&15).bit_count()&1] for x in fit]
        mdl=c.conventional_fit(data,1)
        full=c.conventional_fit(data,3)
        for x in range(64):
            y=float((x&15).bit_count()&1)
            self.assertEqual(c.conventional_predict(mdl,x,1),y)
            self.assertEqual(c.conventional_predict(full,x,3),y)
        with self.assertRaises(ValueError):
            c.conventional_fit([[0,0,1],[0,0,0]],1)

    def test_full_fixture_pipeline_without_consuming_any_frozen_pilot(self):
        # Exercises all native interfaces and conventional fitting on a distinct
        # hard-coded DEV fixture namespace before first-use of pilot source.
        seed=88703
        fit,cal,held=c.source_partition(seed)
        compiled,fixed,source,calibration,pressure,selection,admit,custody=(
            c.train_selected(seed,fit,cal))
        old,meta=c.native_baseline(seed,source,calibration,held)
        self.assertTrue(custody["cold_exact"])
        self.assertTrue(custody["retention_all64_exact"])
        self.assertTrue(custody["conflict_atomic"])
        self.assertEqual(len(old),12)
        self.assertTrue(meta["cold_exact"])
        self.assertEqual(len(pressure),4)
        for slot in c.OLD_SLOTS:
            self.assertEqual(len(source[slot]),42)
            self.assertEqual(len(calibration[slot]),6)
            self.assertEqual(selection[str(slot)],c.choose_degree(source[slot]))
            conventional=c.conventional_fit(source[slot],selection[str(slot)])
            for x in held:
                self.assertEqual(c.native_prob(compiled,slot,x),
                                 c.conventional_predict(conventional,x,selection[str(slot)]))
        weights=c.logistic_fit(source[0]+calibration[0])
        self.assertTrue(0<=c.logistic_predict(weights,held[0])<=1)

    def test_stop_rule_honors_conventional_and_ood_constraints(self):
        def case(seed,wrong=0,better=.25):
            sizes={"str":0}
            m={"profile_selected_bytes":{str(k):100 if k<6 else 200 for k in range(12)},
               "profile_fixed_degree3_bytes":{str(k):300 for k in range(12)},
               "cold_exact":True,"retention_all64_exact":True,"conflict_atomic":True}
            f={arm:{"brier":0.0,"cases":48} for arm in c.ARMS}
            mtrx={name:dict(f) for name in c.FAMILIES}
            for fam in c.FAMILIES:
                mtrx[fam]["native_unmodified"]={"brier":better,"cases":48}
            mtrx["quartic_ood"]["compiled_selected"]={"brier":.25,"cases":48}
            mtrx["quartic_ood"]["compiled_ungated"]={"brier":.35,"cases":48}
            d={str(i):1 if i<3 else 2 if i<6 else 3 for i in range(12)}
            admit={str(i):i<9 for i in range(12)}
            coverage={f:{"compiled_selected":1.} for f in c.FAMILIES}
            return {"seed":seed,"metrics":mtrx,"selected_degrees":d,
                    "source_only_admitted":admit,"primitive_coverage":coverage,
                    "primitive_confident_wrong":{"quartic_ood":{"compiled_selected":wrong}},
                    "native_checkpoint":m,"old_native_checkpoint":{"cold_exact":True}}
        good=[case(13741),case(13742)]
        self.assertEqual(c.classify(good)["decision"],"ENGINEERING_FEASIBLE")
        self.assertEqual(c.classify([good[0],case(13742,wrong=1)])["decision"],"SCREEN_NO_GO")
        with self.assertRaises(AssertionError):
            c.classify(good[::-1])


if __name__=="__main__":
    unittest.main()
