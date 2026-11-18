"""CKAD38 DEV-only native memory repair and retained-context recall checks.

Original frozen pilot seeds are NEVER executed by this file.
"""
import importlib.util
import json
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad38_dev_campaign",HERE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
aspec=importlib.util.spec_from_file_location("ckad38_dev_auditor",HERE/"seal_pilot.py")
AUD=importlib.util.module_from_spec(aspec)
aspec.loader.exec_module(AUD)


class CKAD38Tests(unittest.TestCase):
    def test_frozen_firstuse_and_reserved_seeds(self):
        self.assertEqual(C.PILOT,(14181,14182))
        self.assertEqual(C.PRIMARY,(24181,24182,24183))
        self.assertEqual(C.DEV,(88511,88512))
        for seed in (*C.DEV,*C.PRIMARY,14071,14072):
            with self.assertRaisesRegex(ValueError,"CKAD38_ONLY_REGISTERED_PILOT"):
                C.score(seed)

    def test_two_fresh_structural_families_and_source_only_contract(self):
        for seed in C.DEV:
            for world in C.WORLDS:
                events,private=C.generator(seed,world)
                independent,ref_private=AUD.reference(seed,world)
                self.assertEqual(private,ref_private)
                self.assertEqual(len(events),len(independent))
                self.assertEqual(len({e[0] for e in events}),len(events))
                self.assertEqual(events[0][3],"warm")
                self.assertEqual(events[48][3],"stable_A")
                self.assertEqual(events[private["boundary_A_to_B"]][3],"early_B")
                for i,(identifier,views,row,phase) in enumerate(events):
                    ref=independent[i]
                    self.assertEqual(identifier,ref["source_id"])
                    self.assertEqual([list(x) for x in views],ref["public_views"])
                    self.assertEqual(row,ref["public_row"])
                    self.assertEqual(phase,ref["phase"])
                    self.assertEqual(views[0][0],views[1][0])
                    self.assertTrue(all(x in (0,1) for x in row.values()))

    def test_native_optin_recall_pure_without_source_or_detector(self):
        native=NativeEpisodeExperience(repair=True)
        # No change detector, so recalls are exactly the existing native read.
        # Source-only API does not admit reading an uninitialized context.
        with self.assertRaises(ValueError):
            native.context_forecast_recall((0,1),0)

    def test_native_recall_cold_snapshot_and_repair_ablation(self):
        seed=88511
        events,meta=C.generator(seed,0)
        model=NativeEpisodeExperience(repair=True)
        no_repair=NativeEpisodeExperience(repair=False)
        for t,(identifier,views,row,phase) in enumerate(events[:80]):
            if t==48:
                model=model.begin_stream()
                no_repair=no_repair.begin_stream()
            if t>=48:
                old=model.checkpoint()
                for action in (0,1):
                    self.assertEqual(model.context_forecast_recall(views[0],action),
                                     model.context_forecast(views[0],action))
                self.assertEqual(old,model.checkpoint())
            model=model.observe(identifier,views,row)
            no_repair=no_repair.observe(identifier,views,row)
        old=model.checkpoint()
        cold=NativeEpisodeExperience.restore(old,digest(old))
        self.assertEqual(old,cold.checkpoint())
        self.assertEqual(model.context_forecast_recall((0,0),1),
                         cold.context_forecast_recall((0,0),1))
        self.assertNotEqual(model.checkpoint(),no_repair.checkpoint())

    def test_fully_trained_adaptive_conventional_controls(self):
        model=C.Conventional()
        row={"s1":1,"x1":1,"s2":1,"x2":1,"y":0}
        self.assertEqual(len(C.CONVENTIONAL),6)
        for name in (*C.CONVENTIONAL,"beta_hedge","sham"):
            self.assertAlmostEqual(model.p(name,"transition",1,1),.5)
        model.observe(row,{k:.25 for k in C.CONVENTIONAL})
        for name in (*C.CONVENTIONAL,"beta_hedge"):
            self.assertAlmostEqual(model.p(name,"transition",1,1),2/3)
            self.assertAlmostEqual(model.p(name,"terminal",1,1,1,1),1/3)
        self.assertEqual(len(model.rows),1)

    def test_full_dev_pipeline_and_independent_audit_no_pilots(self):
        seed=88511
        result=C._dev_or_pilot(seed)
        self.assertEqual(result["world_count"],2)
        self.assertEqual(result["total_authentic_consequences"],
                         result["total_authentic_episodes"]*2)
        for w in result["worlds"]:
            for key in ("old_source_preserved","recall_pure_read",
                        "duplicate_idempotent","conflict_atomic",
                        "consolidated_exact","cold_exact"):
                self.assertIs(w[key],True)
        envelope={"schema":C.SCHEMA,"mode":"pilot","seed":seed,
                  "source_lock":{"fixture":True},"primary_scored":False,"case":result}
        verified=AUD.audit_case(json.dumps(envelope).encode("ascii"),
                                seed,{"fixture":True})
        self.assertEqual(verified["metric_groups"],result["metric_groups"])
        self.assertEqual(set(result["metric_groups"]["stable_A"]),set(C.ARMS))

    def test_frozen_stop_strongest_conventional_and_recall_baseline(self):
        def fixture(seed,recall=.1,baseline=.15,conv=.18):
            phases=(*C.PHASES,"pooled_late_shift_and_return")
            metrics={phase:{arm:{"brier":.2,"episodes":24} for arm in C.ARMS}
                     for phase in phases}
            for phase in ("pooled_late_shift_and_return","early_B","late_return_A"):
                metrics[phase]["native_recall"]["brier"]=recall
                metrics[phase]["native_stream"]["brier"]=baseline
            for arm in (*C.CONVENTIONAL,"beta_hedge"):
                metrics["pooled_late_shift_and_return"][arm]["brier"]=conv
            return {"seed":seed,"metric_groups":metrics,
                    "worlds":[{"old_source_preserved":True,
                      "duplicate_idempotent":True,"conflict_atomic":True,
                      "consolidated_exact":True,"cold_exact":True,
                      "recall_pure_read":True}]}
        a=fixture(14181);b=fixture(14182)
        self.assertEqual(C.classify([a,b])["decision"],"ENGINEERING_FEASIBLE")
        self.assertFalse(C.classify([a,b])["scientific_pass"])
        self.assertEqual(C.classify([a,fixture(14182,conv=.11)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(C.classify([a,fixture(14182,baseline=.105)])["decision"],"SCREEN_NO_GO")
        with self.assertRaises(AssertionError):C.classify([b,a])


if __name__=="__main__":
    unittest.main()
