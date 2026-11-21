"""NUM06 engineering-only manual fixtures; no source generator or held seeds."""
import json
import math
import unittest

from num05 import digest, public_row
from bayesian_filter import (BayesianTwoBank, HYPER_GRID,
                             fit_hyperparameters, prequential_score)


def packet(i, *, effects=(0., 0., 0.), action=4, state=(.7, .8)):
    dx, dy, reward = effects
    return public_row(digest(("num06-manual-fixture-"+str(i)).encode("ascii")),
                      state, action, (state[0]+dx, state[1]+dy), reward)


class BayesianComparatorTests(unittest.TestCase):
    def test_01_has_two_banks_and_no_oracle_or_original_source(self):
        m=BayesianTwoBank()
        self.assertEqual(len(m.banks),2)
        self.assertEqual(m.info()["rows"],0)
        for key in ("source_owner_authenticated","native_admission","scientific_gain_verified"):
            self.assertFalse(m.info()[key])
        self.assertEqual(m.predict([.7,.8],4),[0.,0.,0.])
        with self.assertRaises(ValueError):
            m.predict([.7,.8],5)

    def test_02_fits_public_witnessed_consequences_before_forecast(self):
        m=BayesianTwoBank()
        first=packet(1,effects=(.3,-.2,.4))
        self.assertEqual(m.observe(first),[0.,0.,0.])
        self.assertEqual(len(m.rows),1)
        self.assertGreater(m.predict([.7,.8],4)[0],0.)
        self.assertTrue(all(math.isfinite(z) for z in m.predict([.7,.8],4)))

    def test_03_public_phase_blind_change_and_return(self):
        m=BayesianTwoBank()
        for i in range(120):
            m.observe(packet(i,effects=(0.,0.,0.)))
        self.assertLess(m.posterior[1],.2)
        for i in range(120,200):
            m.observe(packet(i,effects=(1.,-.7,.9)))
        self.assertGreater(m.posterior[1],.8)
        self.assertLess(m.predict([.7,.8],4)[0]-1.,.15)
        for i in range(200,265):
            m.observe(packet(i,effects=(0.,0.,0.)))
        self.assertGreater(m.posterior[0],.8)
        self.assertEqual(m.active,0)
        self.assertTrue(any(sw[1]==1 for sw in m.mode_switches))
        self.assertTrue(any(sw[1]==0 for sw in m.mode_switches))

    def test_04_stationary_null_no_false_mode_switch(self):
        m=BayesianTwoBank()
        for i in range(250):
            m.observe(packet(i,effects=(.1,-.1,.15)))
        self.assertEqual(m.active,0)
        self.assertLess(m.posterior[1],.2)
        self.assertFalse(m.mode_switches)

    def test_05_checkpoint_cold_restore_and_corruption(self):
        m=BayesianTwoBank(hazard=.005,noise_sigma=.15,prior_std=1.)
        for i in range(110):
            m.observe(packet(i,effects=(.03,.04,.05)))
        raw=m.checkpoint()
        restored=BayesianTwoBank.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.predict([.7,.8],4),m.predict([.7,.8],4))
        with self.assertRaisesRegex(ValueError,"NUM06_CHECKPOINT_HASH"):
            BayesianTwoBank.restore(raw,"f"*64)
        state=json.loads(raw)
        state["scientific_gain_verified"]=True
        bad=json.dumps(state,sort_keys=True,separators=(",",":")).encode()
        with self.assertRaises(ValueError):
            BayesianTwoBank.restore(bad,digest(bad))

    def test_06_reject_duplicate_forgery_and_bad_hypers(self):
        m=BayesianTwoBank()
        x=packet(1)
        m.observe(x)
        raw=m.checkpoint()
        with self.assertRaisesRegex(ValueError,"NUM06_DUPLICATE"):
            m.observe(x)
        y=dict(packet(2))
        y["source_owner_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"NUM06_ROW_SCHEMA"):
            m.observe(y)
        self.assertEqual(m.checkpoint(),raw)
        for overrides in ({"hazard":0.}, {"hazard":0.5}, {"noise_sigma":-0.1},
                          {"prior_std":2.1}, {"hazard":True},
                          {"hazard":float("nan")}):
            with self.assertRaises(ValueError):
                BayesianTwoBank(**overrides)

    def test_07_grid_selection_fits_only_supplied_manual_cohorts(self):
        self.assertEqual(len(HYPER_GRID),12)
        fit=[[packet(i,effects=(.1,.2,.05)) for i in range(25)]]
        valid=[[packet(i+100,effects=(.1,.2,.05)) for i in range(25)]]
        chosen=fit_hyperparameters(fit,valid)
        self.assertIn(tuple(chosen["settings"]),HYPER_GRID)
        self.assertEqual(chosen["grid_size"],12)
        self.assertFalse(chosen["held_used"])
        self.assertFalse(chosen["scientific_gain_verified"])
        self.assertTrue(math.isfinite(chosen["selection_mse"]))
        score=prequential_score(fit[0],tuple(chosen["settings"]))
        self.assertGreaterEqual(score,0.)
        with self.assertRaisesRegex(ValueError,"NUM06_EMPTY_COHORT"):
            prequential_score([],tuple(chosen["settings"]))
        with self.assertRaises(ValueError):
            fit_hyperparameters([],valid)

    def test_08_control_isolated_from_generator_and_native_sources(self):
        from pathlib import Path
        source=Path(__file__).with_name("bayesian_filter.py").read_text(encoding="utf8")
        for forbidden in ("from num05_dev", "source_rows(", "import gymnasium",
                          "import highway_env", "from yggdrasil",
                          "import requests", "subprocess.", "PILOT_FIRST_USE"):
            self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
