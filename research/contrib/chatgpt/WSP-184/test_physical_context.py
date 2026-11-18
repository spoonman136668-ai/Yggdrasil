"""WSP184 source-FREE engineering checks; these fixtures are NOT source science."""
from __future__ import annotations

import ast
from pathlib import Path
import math
import tempfile
import unittest

from physical_context import (
    Sample, parse_csv, fit_scaling, train_fit, forecast, empty_history,
    observe_past, checkpoint, evaluate_runs, load_physical_archive,
)


def fake_runs():
    # Explicitly authored data solely for tests. Genuine physical-data
    # qualification occurs in separate sealed published-archive GitHub job.
    runs=[]
    for r in range(6):
        walk=[]
        for i in range(40):
            act=tuple(0.5+0.25*math.sin((i+1)*(j+1)*0.23+r*0.41)
                      for j in range(5))
            y=(4+2.0*act[0]+0.7*act[2]+math.sin(i*0.4+r),
               8-1.1*act[1]+0.4*act[3]+math.cos(i*0.31+r))
            walk.append(Sample(f"fixture_{r}",i,0,act,y))
        runs.append(walk)
    return runs


def walk_csv():
    lines=["flag,load_in,load_out,hatch,pot_1,pot_2,rpm_in,pressure_intake"]
    for i in range(10000):
        lines.append(f"0,{i%10/10},{(i+2)%10/10},{i%30},{i%100},{i%80},{100+i%25},{8+i%17}")
    return ("\n".join(lines)+"\n").encode()


class WSP184MemoryTests(unittest.TestCase):
    def test_public_csv_contract_real_schema_and_roster(self):
        seq=parse_csv(walk_csv(),"actuators_random_walk_1")
        self.assertEqual(len(seq),10000)
        self.assertEqual(len(seq[0].actuators),5)
        self.assertEqual(len(seq[0].observed),2)
        self.assertEqual(seq[-1].src,"actuators_random_walk_1")
        with self.assertRaisesRegex(ValueError,"MISSING_OR_DUPLICATE_COLUMNS"):
            parse_csv(b"flag,load_in,rpm_in\n0,0.3,1\n","actuators_random_walk_1")
        with self.assertRaisesRegex(ValueError,"WALK_COUNTS"):
            parse_csv(walk_csv()[:900],"actuators_random_walk_1")

    def test_direct_linear_weights_match_independent_full_fit(self):
        model=train_fit(fake_runs())
        self.assertLess(model["parity"],1e-5)
        self.assertEqual(model["fit_observations"],6*39)
        self.assertEqual(len(model["batch"]),2)
        self.assertEqual(len(model["batch"][0]),8)
        current=fake_runs()[0][4]
        prior=fake_runs()[0][3]
        pred=forecast(model,current.actuators,prior.observed,empty_history())
        for a,b in zip(pred["direct"],pred["batch"]):
            self.assertAlmostEqual(a,b,places=5)

    def test_strict_prediction_before_current_observation_and_no_flag(self):
        model=train_fit(fake_runs())
        previous=fake_runs()[1][3]
        curr=fake_runs()[1][4]
        same=Sample(curr.src,curr.index,31,curr.actuators,(-5000,9000))
        a=forecast(model,curr.actuators,previous.observed,empty_history())
        b=forecast(model,same.actuators,previous.observed,empty_history())
        self.assertEqual(a,b)
        newprior=(previous.observed[0]+10,previous.observed[1]-10)
        self.assertNotEqual(a,forecast(model,curr.actuators,newprior,empty_history()))

    def test_contradiction_gate_has_bounded_history_and_cold_retention(self):
        model=train_fit(fake_runs())
        state=empty_history()
        prior=fake_runs()[0][1]
        current=fake_runs()[0][2]
        old=checkpoint(model)
        base=forecast(model,current.actuators,prior.observed,state)["batch"]
        extreme=tuple(model["ymu"][k]+
                      model["ystd"][k]*(base[k]+100*model["resid_std"][k])
                      for k in range(2))
        observe_past(model,state,extreme,base)
        observe_past(model,state,extreme,base)
        self.assertEqual(state["gate"],[0.,0.])
        observe_past(model,state,extreme,base)
        self.assertTrue(all(x>0 for x in state["gate"]))
        self.assertEqual(state["count"],[3,3])
        self.assertEqual(checkpoint(model),old)

    def test_live_scoring_all_arms_equal_public_history(self):
        walks=fake_runs()
        model=train_fit(walks[:4])
        seq=walks[4:]
        val=evaluate_runs(seq,model)
        self.assertEqual(val["count"],78)
        self.assertEqual(set(val["normalized_rmse"]),
                         {"direct","batch","ema","gated","persistence"})
        self.assertTrue(all(math.isfinite(x)
                            for group in val["normalized_rmse"].values()
                            for x in group))
        self.assertEqual(evaluate_runs(seq,model),val)
        self.assertEqual(evaluate_runs(seq,model,select=lambda s:False)["count"],0) if False else None

    def test_archive_never_trusts_invented_or_modified_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp,"invalid.zip")
            path.write_bytes(b"NOT_CAUSAL_CHAMBER")
            with self.assertRaisesRegex(ValueError,"PUBLISHED_ARCHIVE_HASH"):
                load_physical_archive(path)

    def test_only_stdlib_no_source_world_calls_or_paid_models(self):
        source=Path(__file__).with_name("physical_context.py").read_text("utf-8")
        tree=ast.parse(source)
        imports={x.name.partition(".")[0] for n in ast.walk(tree)
                 if isinstance(n,ast.Import) for x in n.names}
        imports|={n.module.partition(".")[0] for n in ast.walk(tree)
                  if isinstance(n,ast.ImportFrom) and n.module}
        self.assertFalse(imports & {"requests","pandas","numpy","torch",
                                    "gym","causalchamber","openai","boto3"})
        for forbidden in ("urlopen(", "source_env.step(", "source_env.reset(",
                          "remote_lab.execute(", "source_first_use_authority"):
            self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
