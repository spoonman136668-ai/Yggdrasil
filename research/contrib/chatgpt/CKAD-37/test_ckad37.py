"""CKAD37 DEV-only qualification; original pilot seeds never scored here."""
import importlib.util
import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("ckad37_dev",HERE/"campaign.py")
c=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)
AUDSPEC=importlib.util.spec_from_file_location("ckad37_audit_dev",HERE/"seal_pilot.py")
audit=importlib.util.module_from_spec(AUDSPEC)
AUDSPEC.loader.exec_module(audit)


class CKAD37Tests(unittest.TestCase):
    def test_frozen_first_use_and_no_primary(self):
        self.assertEqual(c.PILOT,(14071,14072))
        self.assertEqual(c.PRIMARY,(24071,24072,24073))
        self.assertEqual(c.DEV,(88411,88412))
        for seed in (88411,88412,*c.PRIMARY,13961,13962):
            with self.assertRaisesRegex(ValueError,"CKAD37_ONLY_REGISTERED_PILOT"):
                c.score(seed)

    def test_public_views_and_no_world_change_label(self):
        for seed in c.DEV:
            for world in c.WORLDS:
                rows,parts=c.generator(seed,world)
                self.assertEqual(len(rows),parts["total_episodes"])
                self.assertEqual(len(set(e[0] for e in rows)),len(rows))
                self.assertGreater(parts["boundary_A_to_B"],48)
                self.assertGreater(parts["boundary_B_to_A"]-
                                   parts["boundary_A_to_B"],48)
                self.assertEqual(rows[0][3],"warm")
                self.assertEqual(rows[48][3],"stable_A")
                self.assertEqual(rows[parts["boundary_A_to_B"]][3],"early_B")
                self.assertEqual(rows[parts["boundary_B_to_A"]][3],"early_return_A")
                for identifier,views,r,phase in rows:
                    self.assertEqual(views[0][0],views[1][0])
                    self.assertEqual(views[0][0],r["s1"])
                    self.assertEqual(set(r),{"s1","x1","s2","x2","y"})
                    self.assertTrue(all(v in (0,1) for v in r.values()))

    def test_conventional_source_only_controls(self):
        b=c.Conventional()
        row={"s1":1,"x1":1,"s2":1,"x2":1,"y":0}
        for arm in c.ARMS[2:]:
            self.assertAlmostEqual(b.p(arm,"transition",1,1),.5)
            self.assertAlmostEqual(b.p(arm,"terminal",1,1,1,1),.5)
        b.observe(row)
        for arm in c.ARMS[2:-1]:
            self.assertAlmostEqual(b.p(arm,"transition",1,1),2/3)
            self.assertAlmostEqual(b.p(arm,"terminal",1,1,1,1),1/3)
        self.assertEqual(len(b.rows),1)

    def test_complete_dev_native_cold_and_independent_audit(self):
        # Both worlds, full A->unannounced B->A stream, actual two-stage
        # consequences, never any original first-use or primary seed.
        seed=88411
        result=c._dev_or_pilot(seed)
        self.assertEqual(result["seed"],seed)
        self.assertEqual(result["world_count"],2)
        self.assertEqual(result["total_authentic_consequences"],
                         2*result["total_authentic_episodes"])
        for w in result["worlds"]:
            self.assertTrue(w["old_source_preserved"])
            self.assertTrue(w["consolidated_exact"])
            self.assertTrue(w["cold_exact"])
            self.assertTrue(w["conflict_atomic"])
            self.assertTrue(w["duplicate_idempotent"])
            self.assertEqual(w["source_count"],w["episodes"])
        envelope={"schema":c.SCHEMA,"mode":"pilot","seed":seed,
                  "source_lock":{"fixture":True},"primary_scored":False,
                  "case":result}
        independently=audit.audit_case(json.dumps(envelope).encode("ascii"),
                                       seed,{"fixture":True})
        self.assertEqual(independently["metric_groups"],result["metric_groups"])

    def test_frozen_decision_requires_strongest_conventional(self):
        def example(seed,native=.11,conv=.16,old=.22):
            m={phase:{k:{"brier":.22,"episodes":40} for k in c.ARMS}
               for phase in (*c.PHASES,"pooled_late_shift_and_return")}
            for phase in ("pooled_late_shift_and_return","early_B","late_return_A"):
                m[phase]["native_stream"]["brier"]=native
                m[phase]["native_global"]["brier"]=old
            for name in ("beta_full","beta_window24","beta_window48","beta_discount95"):
                m["pooled_late_shift_and_return"][name]["brier"]=conv
            return {"seed":seed,"metric_groups":m,"worlds":[{
                "old_source_preserved":True,"duplicate_idempotent":True,
                "conflict_atomic":True,"consolidated_exact":True,"cold_exact":True
            }]}
        a=example(14071);b=example(14072)
        self.assertEqual(c.classify([a,b])["decision"],"ENGINEERING_FEASIBLE")
        self.assertFalse(c.classify([a,b])["scientific_pass"])
        self.assertEqual(c.classify([a,example(14072,conv=.115)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(c.classify([a,example(14072,native=.18)])["decision"],"SCREEN_NO_GO")
        with self.assertRaises(AssertionError):
            c.classify([b,a])


if __name__=="__main__":
    unittest.main()
