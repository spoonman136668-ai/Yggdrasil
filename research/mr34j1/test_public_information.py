"""Source-free checks for frozen original public information test MR34J1."""
import math
from pathlib import Path
import unittest

import numpy as np

from research.mr34j1 import public_information as p


def public(chars):
    return np.asarray([ord(ch) for ch in chars],dtype="<u4").tobytes()


def synthetic_data():
    data=[]
    for i in range(8):
        rec=[]
        prior=None
        old=np.zeros(23,dtype=np.float64)
        for t in range(4):
            val=public(("."*8)+("!" if (i+t)%2 else "?"))
            x=np.zeros(23,dtype=np.float64)
            x[t%16]=.25
            x[16+((i+t)%5)]=1.
            rec.append({
                "public36":val,"previous_public36":prior,
                "action":(i+t)%5,
                "public23":x,"previous_public23":old,
                "target8":np.array([(i+j+t)%2 for j in range(8)],dtype=np.float64)
            })
            prior=val;old=x
        data.append((2609+i,0,rec))
    return data


class OriginalPublicInformationTests(unittest.TestCase):
    def test_frozen_source_governance_and_unused_development_roles(self):
        self.assertEqual(p.FIRST,"23e336a093673f9c5a05e81a08d3f91485367f7e")
        self.assertEqual(p.PARENT,"dbdd9b75c7fb518e28441597421e86f0073421ea")
        self.assertEqual(len(p.FIT),16)
        self.assertEqual(len(p.HELD),8)
        self.assertFalse(set(p.FIT)&set(p.HELD))
        self.assertTrue(min(p.FIT)>2557)
        self.assertEqual(p.STEPS,48)
        self.assertEqual(p.EPOCHS,200)
        self.assertEqual(p.MAX_CODEPOINTS,32)
        self.assertEqual(p.MIN_SEED_WINS,6)

    def test_lossless_public_identity_and_previous_public_only(self):
        frame=public(".........")
        self.assertEqual(len(frame),36)
        self.assertEqual(p.public_codepoints(frame),(46,)*9)
        codes=[46,33]
        single=p.onehot_public(frame,3,codes)
        self.assertEqual(single.shape,(9*(len(codes)+1)+7,))
        self.assertEqual(single.sum(),10.)
        self.assertEqual(single[9*3+3],1.)
        missing=p.onehot_public(None,0,codes)
        self.assertTrue(np.all(missing==0.))
        with self.assertRaises(ValueError):
            p.public_codepoints(frame[:32])
        with self.assertRaises(ValueError):
            p.onehot_public(frame,6,codes)

    def test_sham_history_fit_only_donors_and_source_equal_dimensions(self):
        fit=synthetic_data()
        book=p.fit_codebook(fit)
        x,y,meta=p.design(fit,book,fit)
        self.assertEqual(len(meta),32)
        self.assertEqual(y.shape,(32,8))
        self.assertEqual(x["pooled_current"].shape,(32,23))
        self.assertEqual(x["pooled_previous"].shape,(32,46))
        self.assertEqual(x["categorical_previous"].shape,
                         x["categorical_sham_previous"].shape)
        self.assertTrue(np.all(x["categorical_previous"][0,
                         x["categorical_current"].shape[1]:]==0))
        self.assertFalse(np.array_equal(
            x["categorical_previous"],x["categorical_sham_previous"]))
        self.assertFalse(np.isnan(y).any())

    def test_original_eightbit_logistic_fits_and_seals_source_free(self):
        fit=synthetic_data()
        book=p.fit_codebook(fit)
        x,y,_=p.design(fit,book,fit)
        for name in ("pooled_current","categorical_current",
                     "categorical_previous"):
            model,audit=p.train_logistic(x[name],y)
            w,b=model
            self.assertEqual(w.shape[1],8)
            self.assertEqual(b.shape,(8,))
            self.assertEqual(len(audit["checkpoint_SHA256"]),64)
            self.assertEqual(audit["frozen_full_batch_optimizer_epochs"],200)
            self.assertLessEqual(audit["source_fit_final_Brier"],
                                 audit["source_fit_initial_Brier"])
            self.assertTrue(math.isfinite(audit["source_fit_final_Brier"]))
        collision=p.ambiguity(fit)
        self.assertIn("full_public_plus_action",collision)
        self.assertIn("pooled_23_plus_action",collision)
        self.assertFalse(collision["full_public_plus_action"]["empirical_ambiguity_is_irreducibility_proof"])

    def test_heldout_never_used_to_select_model_or_dictionary(self):
        src=Path(p.__file__).read_text()
        self.assertLess(src.index("fit,fit_receipt=source_cohort"),
                        src.index("seal={name:v[\"checkpoint_SHA256\"]"))
        self.assertLess(src.index("seal={name:v[\"checkpoint_SHA256\"]"),
                        src.index("held,held_receipt=source_cohort"))
        self.assertIn("source_original_git_readonly(root)",src)
        self.assertIn("env.step(action)",src)
        self.assertNotIn("env.unwrapped",src)
        self.assertNotIn("model_native.train",src)
        self.assertNotIn("source_cohort(original_source,(2503",src)


if __name__=="__main__":
    unittest.main()
