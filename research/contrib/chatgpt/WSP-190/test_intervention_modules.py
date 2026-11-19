"""Source-free engineering tests ONLY, not scientific experiments."""
from __future__ import annotations

import ast
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import intervention_modules as m


def fixture():
    """Deterministic manufacturing of rows ONLY for unit-code qualification."""
    groups={}
    for group,shift,n in (("uniform_reference",-1,64),
                          ("uniform_red_mid",0,1000),
                          ("uniform_green_mid",1,1000),
                          ("uniform_blue_mid",2,1000)):
        points=[]
        for i in range(n):
            x=[float(30 + 5*math.sin((i+1)*(j+2)*.019)
                     + 2*math.cos((i+5)*(j+1)*.037))
               for j in range(11)]
            if shift>=0:
                x[shift]+=90
            y=(x[0]+.25*x[1]+.2*x[3]+.1*x[5]+math.sin(i*.11),
               .4*x[0]+1.3*x[1]+.2*x[2]+math.sin(i*.21+.3),
               .3*x[1]+1.2*x[2]+.12*x[6]+math.cos(i*.13))
            points.append((tuple(x),tuple(y)))
        groups[group]=points
    return groups


class InterventionModuleEngineering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups=fixture()
        with patch.object(m,"FIT_REF",64):
            cls.model=m.fit(cls.groups)

    def test_frozen_cohorts_and_model_constraints(self):
        self.assertEqual(len(m.INPUTS),11)
        self.assertEqual(len(m.TARGETS),3)
        self.assertEqual(m.FIT_REF,8000)
        self.assertEqual(m.VALID_REF,2000)
        self.assertEqual(len(m.FIT_MID),3)
        self.assertEqual(len(m.DEV),4)
        self.assertEqual(m.NULL_Z,2.0)
        self.assertEqual(self.model["fit_samples"],3064)
        self.assertEqual(len(self.model["modules"]),3)
        self.assertEqual(len(self.model["module_nuisance"]),3)
        self.assertEqual(len(self.model["module_nuisance"][0]),9)
        self.assertEqual(len(self.model["quadratic_ridge"][0]),26)
        self.assertEqual(len(self.model["group_centered_ridge"][0]),11)

    def test_real_intervention_labels_change_module_edges(self):
        s=self.model["modules"]
        self.assertGreater(s[0][0],0.)
        self.assertGreater(s[1][1],0.)
        self.assertGreater(s[2][2],0.)
        self.assertTrue(any(s[k]!=self.model["shuffled_modules"][k]
                            for k in range(3)))
        x=self.groups["uniform_red_mid"][10][0]
        preds=m.predict_all(self.model,x)
        self.assertEqual(set(preds),set(m.ARMS))
        self.assertNotEqual(preds["module"],preds["shuffled_edges"])

    def test_frozen_checkpoint_does_not_see_current_target(self):
        wire=m.freeze(self.model)
        rows=self.groups["uniform_reference"][10:]
        a=m.evaluate(rows,self.model)
        b=m.evaluate(rows,self.model)
        self.assertEqual(a,b)
        self.assertEqual(wire,m.freeze(self.model))
        x,y=rows[0]
        pred1=m.predict_all(self.model,x)
        altered_y=tuple(v+1e6 for v in y)
        pred2=m.predict_all(self.model,x)
        self.assertEqual(pred1,pred2)
        self.assertNotEqual(y,altered_y)
        self.assertEqual(a["rows"],54)
        self.assertTrue(all(math.isfinite(v)
                   for vals in a["normalized_rmse"].values() for v in vals))

    def test_real_record_prefix_policy_and_malformed_guard(self):
        header=",".join(m.INPUTS+m.TARGETS)+"\n"
        row=",".join(["1.0"]*14)+"\n"
        raw=(header+row*1000+"NOT,PARSED,AFTER,FROZEN,PREFIX\n").encode()
        examples,receipt=m.parse_prefix(raw,"uniform_red_mid")
        self.assertEqual(len(examples),1000)
        self.assertEqual(receipt["observed_original_records"],1001)
        self.assertEqual(receipt["extra_original_records_not_parsed"],1)
        with self.assertRaisesRegex(ValueError,"TOO_FEW_ORIGINAL_RECORDS"):
            m.parse_prefix((header+row*999).encode(),"uniform_red_mid")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_HEADERS"):
            m.parse_prefix(b"red,blue,vis_1\n1,2,3\n","uniform_red_mid")

    def test_original_archive_hash_before_values(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"source.zip"
            path.write_bytes(b"not published original physical data")
            with self.assertRaisesRegex(ValueError,"UPSTREAM_MD5"):
                m.inspect_source(path)

    def test_no_simulator_actor_or_target_leakage(self):
        code=Path(__file__).with_name("intervention_modules.py").read_text("utf-8")
        imports={part.name.partition(".")[0]
                 for node in ast.walk(ast.parse(code))
                 if isinstance(node,ast.Import) for part in node.names}
        self.assertFalse(imports & {"requests","numpy","pandas","torch",
                                   "causalchamber","gym","boto3","openai"})
        for bad in ("source_env.step(","env.reset(","urlopen(",
                    "source_first_use_authority","train_original_world("):
            self.assertNotIn(bad,code)
        self.assertIn('best_control = min(CONTROLS',code)
        self.assertIn('for name in DEV:',code)


if __name__ == "__main__":
    unittest.main()
