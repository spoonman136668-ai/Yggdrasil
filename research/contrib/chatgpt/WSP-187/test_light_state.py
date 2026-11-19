"""WSP-187 source-FREE developer tests. Fixture values are not scientific results."""
from __future__ import annotations

import ast
import hashlib
import math
from pathlib import Path
import tempfile
import unittest

from light_state import (
    INPUTS,OUTPUTS,FEAT,ROSTER,PATIENCE,THRESHOLD,RANK,
    parse_recording,fit,features,projection,frozen_core,score,observe,
    admit,read,CONTROLS
)


def generated(n=420):
    """Deterministic hand-authored signal sole purpose is code qualification."""
    rows=[]
    for i in range(n):
        x=(
            90+40*math.sin(i*.23), 80+35*math.cos(i*.27),
            70+30*math.sin(i*.19+1), -30+50*math.sin(i*.07),
            30+40*math.cos(i*.11), 120+25*math.sin(i*.137),
            90+20*math.cos(i*.091)
        )
        y=(
            .7*x[0]+.2*x[2]+12*math.cos(math.radians(2*x[3]))+2*math.sin(i*.89),
            .3*x[1]+.4*x[5]+8*math.sin(math.radians(2*x[4]))+3*math.cos(i*.77),
            .2*x[2]+.3*x[6]+.2*x[0]+4*math.sin(i*.61+2)
        )
        rows.append((x,y))
    return rows


class LightStateDeveloperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=generated()
        cls.model=fit(cls.rows[:300])

    def test_frozen_true_public_features_and_limited_rank(self):
        m=self.model
        self.assertEqual(FEAT,12)
        self.assertEqual(len(INPUTS),7)
        self.assertEqual(len(OUTPUTS),3)
        self.assertEqual(len(m["basis"]),RANK)
        self.assertEqual(len(m["lowrank"]),3)
        self.assertEqual(len(m["lowrank"][0]),2)
        self.assertEqual(len(features(self.rows[1][0],m)),FEAT)
        axes=m["basis"]
        self.assertAlmostEqual(sum(x*x for x in axes[0]),1.,places=6)
        self.assertAlmostEqual(sum(x*x for x in axes[1]),1.,places=6)
        self.assertAlmostEqual(sum(x*y for x,y in zip(*axes)),0.,places=5)

    def test_no_future_target_leak_in_any_prediction(self):
        m=self.model
        previous=self.rows[320]
        x,y=self.rows[321]
        patch=[[0.]*RANK for _ in range(3)]
        e=[0.]*3
        first,_,_=observe(m,x,y,previous[0],previous[1],
                          patch,e,0)
        impossible_y=(1e10,-1e10,2e10)
        second,_,_=observe(m,x,impossible_y,previous[0],previous[1],
                           [[0.]*RANK for _ in range(3)],[0.]*3,0)
        self.assertEqual(first,second)
        self.assertNotEqual(first["persistence"],
                            observe(m,x,y,previous[0],(0.,0.,0.),
                                    [[0.]*RANK for _ in range(3)],[0.]*3,0)[0]["persistence"])

    def test_streaming_readout_runs_and_pretrained_memory_unchanged(self):
        m=self.model
        old=frozen_core(m)
        a=score(self.rows,m,start=300)
        b=score(self.rows,m,start=300)
        self.assertEqual(a,b)
        self.assertEqual(a["rows"],120)
        self.assertEqual(set(a["normalized_rmse"]),
                         set(CONTROLS)|{"gated"})
        self.assertTrue(all(math.isfinite(v)
                            for row in a["normalized_rmse"].values()
                            for v in row))
        self.assertEqual(old,frozen_core(m))
        self.assertEqual(hashlib.sha256(old).hexdigest(),
                         hashlib.sha256(frozen_core(m)).hexdigest())

    def test_invalid_source_does_not_fit_or_open_measurements(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fake.zip"
            p.write_bytes(b"no published light-chamber archive")
            with self.assertRaisesRegex(ValueError,"PUBLISHED_HASH"):
                admit(p)
        with self.assertRaisesRegex(ValueError,"SOURCE_ROWCOUNT"):
            parse_recording((",".join(INPUTS+OUTPUTS)+"\n"+
                             ",".join(["0"]*10)+"\n").encode(),"actuators_white")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_SOURCE_COLUMNS"):
            parse_recording(b"red,green,blue\n0,0,0\n","actuators_white")

    def test_only_public_licensed_source_path_and_no_imported_simulation(self):
        code=Path(__file__).with_name("light_state.py").read_text("utf-8")
        tree=ast.parse(code)
        deps={x.name.partition(".")[0] for n in ast.walk(tree)
              if isinstance(n,ast.Import) for x in n.names}
        deps|={n.module.partition(".")[0] for n in ast.walk(tree)
               if isinstance(n,ast.ImportFrom) and n.module}
        self.assertFalse(deps&{"numpy","torch","gym","causalchamber","pandas",
                               "requests","subprocess","openai","boto3"})
        for s in ("urlopen(","env.step(","source_first_use_authority",
                  "remote_lab.execute(","model.train_original("):
            self.assertNotIn(s,code)
        self.assertEqual(ROSTER,("actuators_white","color_mix",
                                 "smooth_polarizers"))
        self.assertEqual(PATIENCE,3)
        self.assertEqual(THRESHOLD,2.0)


if __name__=="__main__":
    unittest.main()
