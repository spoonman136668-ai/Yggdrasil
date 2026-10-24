"""MR34J2 source-free tests: equal-size public-symbol code, fit-only roles and gates."""
import math
from pathlib import Path
import unittest

import numpy as np

from research.mr34j2 import matched_public as p


def frame(chars):
    return np.asarray([ord(c) for c in chars],dtype="<u4").tobytes()


def fake_episode_sources():
    fit=[]
    symbols=(".", "_", "O", "→", "□")
    for i in range(16):
        rows=[]
        for t in range(3):
            chars=[symbols[(k+t+i)%len(symbols)] for k in range(9)]
            c=frame(chars)
            features=np.zeros(23,dtype=np.float64)
            features[(t+i)%16]=.25
            action=(i+t)%5
            features[16+action]=1.
            rows.append({
                "public36":c,
                "previous_public36":rows[-1]["public36"] if rows else None,
                "action":action,
                "public23":features,
                "previous_public23":np.zeros(23,dtype=np.float64),
                "target8":np.array([(i+j+t)%2 for j in range(8)],dtype=np.float64)
            })
        fit.append((2801+i,0,rows))
    return fit


class CapacityMatchedPublicTests(unittest.TestCase):
    def test_frozen_contract_and_nonoverlap_with_previous_held_roles(self):
        self.assertEqual(p.FIRST,"789f122b92c8cc2ae644154daeafb135a27d1045")
        self.assertEqual(p.PARENT,"a8b81e674b6d583549a5c80bede3a4ee5998665f")
        self.assertEqual(len(p.FIT),16)
        self.assertEqual(len(p.HELD),8)
        self.assertTrue(min(p.FIT)>2797)
        self.assertTrue(max(p.FIT)<min(p.HELD))
        self.assertEqual(p.GAIN,.005)
        self.assertEqual(p.WINS,6)
        self.assertEqual(p.BOOT_DRAWS,4096)
        self.assertEqual(len(set(p.CODEPAIRS)),6)
        self.assertEqual(set(p.ORDER_A),set(p.ORDER_B))

    def test_lossless_public_symbol_injective_23_features_same_dimensions_as_pooled(self):
        book=sorted([ord(c) for c in (".","_","O","→","□")])
        codes={c:[] for c in book}
        for mode in (p.ORDER_A,p.ORDER_B):
            encodings=set()
            for c in book:
                one=p.exact_public_symbols(frame([chr(c)]+["."]*8),3,book,mode)
                self.assertEqual(one.shape,(23,))
                self.assertEqual(one[18:].sum(),1.)
                encodings.add(tuple(one[:2]))
            self.assertEqual(len(encodings),len(book))
            self.assertNotIn(p.CODEPAIRS[5],encodings)
        self.assertEqual(len(p.CODEPAIRS),6)
        with self.assertRaises(ValueError):
            p.exact_public_symbols(frame(["."]*9),5,book,p.ORDER_A)
        with self.assertRaises(ValueError):
            p.exact_public_symbols(frame(["."]*9),0,book+[100],p.ORDER_A)

    def test_actual_fit_only_continuous_source_and_parameter_capacity(self):
        fit=fake_episode_sources()
        book=p.fit_codebook(fit)
        self.assertEqual(len(book),5)
        mean,std=p.fit_statistics(fit)
        self.assertEqual(mean.shape,(23,))
        self.assertEqual(std.shape,(23,))
        x,y,roles,oov=p.source_design(fit,book,mean,std)
        self.assertEqual(oov,0)
        self.assertEqual(y.shape,(48,8))
        self.assertEqual(set(x),set(p.LOGISTIC_NAMES))
        for name in p.MATCHED_NAMES:
            self.assertEqual(x[name].shape[1],23)
            (weights,bias),audit=p.train_logistic(x[name],y)
            self.assertEqual(weights.shape,(23,8))
            self.assertEqual(bias.shape,(8,))
            self.assertEqual(audit["native_float64_coefficient_checkpoint_bytes"],1536)
            self.assertEqual(audit["frozen_full_batch_optimizer_epochs"],200)
        self.assertGreater(x["categorical_onehot_full_reference"].shape[1],23)
        self.assertEqual(int(x["source_action_only23"][:,:18].sum()),0)

    def test_bootstrap_respects_eight_independent_clusters_and_frozen_thresholds(self):
        scores={}
        for name in p.ALL_NAMES:
            vals={}
            for seed in p.HELD:
                if name=="pooled23_original":v=.20
                elif name=="pooled23_FIT_standardized":v=.19
                elif name=="symbol23_coordinates_A":v=.16
                elif name=="symbol23_coordinates_B":v=.17
                else:v=.22
                vals[str(seed)]=v
            scores[name]={
                "source_HELD_mean_eight_independent_seed_Brier":sum(vals.values())/8,
                "genuine_original_held_seed_cluster_Brier":vals
            }
        decision,pas=p.fixed_verdict(scores)
        self.assertTrue(pas)
        self.assertEqual(decision["symbol23_coordinates_A"]["paired_genuine_original_reset_seed_wins_vs_both_pooled"],8)
        self.assertGreater(decision["symbol23_coordinates_A"]["strict_cluster_bootstrap"]["2p5th_percentile_paired_gain"],0)

    def test_no_scientific_first_use_or_held_training(self):
        src=Path(p.__file__).read_text()
        self.assertLess(src.index("fit,fit_receipt=source_cohort"),
                        src.index("seal={name:train[name][\"checkpoint_SHA256\"]"))
        self.assertLess(src.index("seal={name:train[name][\"checkpoint_SHA256\"]"),
                        src.index("held,held_receipt=source_cohort"))
        self.assertIn("source_original_git_readonly(original)",src)
        self.assertNotIn("native.train",src)
        self.assertNotIn("source_cohort(original,tuple(range",src)


if __name__=="__main__":
    unittest.main()
