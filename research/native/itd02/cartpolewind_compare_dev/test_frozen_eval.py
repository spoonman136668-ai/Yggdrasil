"""PUBLIC-shaped, source-free validation of frozen recurrent evaluation.

These are literal authored protocol samples, not CartPoleWind episodes or scientific trials.
"""
import copy
import json
import subprocess
import sys
import unittest
from research.native.itd02.cartpolewind_compare_dev.compare import Model, ARMS, fit_identical_public_replay

X = [0., 0., 0., 0.]
ROW = {"observation":[0.1,-0.2,0.3,-0.4],"action":0,
       "next_observation":[0.2,-0.1,0.1,-0.2],"reward":1.,
       "terminated":False,"truncated":False}


class FrozenPublicEvaluationTests(unittest.TestCase):
    def test_history_changes_action_without_fitting(self):
        base=Model("recurrent")
        base.recurrent["0"][5]=2.
        identity=base.fitted_parameter_sha256()
        a,b=copy.deepcopy(base),copy.deepcopy(base)
        for m in (a,b):
            m.start_frozen_evaluation(identity)
        self.assertEqual((a.choose(X),b.choose(X)),(0,0))
        a.frozen_public_return([1.,0.,0.,0.])
        b.frozen_public_return([-1.,0.,0.,0.])
        self.assertEqual((a.choose(X),b.choose(X)),(0,1))
        self.assertEqual((a.trace[0],b.trace[0]),(.2,-.2))
        self.assertEqual({a.fitted_parameter_sha256(),b.fitted_parameter_sha256()},{identity})
        self.assertEqual((a.updates,b.updates),(0,0))

    def test_fit_and_scoring_separation(self):
        for arm in ARMS:
            m=Model(arm)
            m.observe(ROW)
            before_updates=m.updates
            identity=m.fitted_parameter_sha256()
            m.start_frozen_evaluation(identity)
            m.choose(X)
            m.frozen_public_return([1.,0.,0.,0.])
            self.assertEqual(m.fitted_parameter_sha256(),identity)
            self.assertEqual(m.updates,before_updates)
            with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
                m.observe(ROW)

    def test_no_fit_guard_rejects_unfrozen_model(self):
        m=Model("recurrent")
        with self.assertRaisesRegex(ValueError,"NOT_FROZEN"):
            m.frozen_public_return(X)
        with self.assertRaisesRegex(ValueError,"FITTED_WEIGHT_IDENTITY"):
            m.start_frozen_evaluation("0"*64)
        with self.assertRaises(ValueError):
            m.start_frozen_evaluation(m.fitted_parameter_sha256(),reset_trace=0)

    def test_invalid_return_is_atomic(self):
        m=Model("recurrent")
        m.start_frozen_evaluation(m.fitted_parameter_sha256())
        for v in ([1.,2.,3.],[0.,0.,float("nan"),0.],
                  {"private":42},[1e7,0.,0.,0.]):
            before=m.checkpoint()
            with self.assertRaises(ValueError):
                m.frozen_public_return(v)
            self.assertEqual(m.checkpoint(),before)
        before=m.checkpoint()
        with self.assertRaises(ValueError):
            m.frozen_public_return(X,terminal=1)
        self.assertEqual(before,m.checkpoint())

    def test_end_of_episode_resets_transient_memory(self):
        m=Model("recurrent")
        identity=m.fitted_parameter_sha256()
        m.start_frozen_evaluation(identity)
        m.frozen_public_return([1.,0.,0.,0.])
        self.assertEqual(m.trace[0],.2)
        m.frozen_public_return([2.,0.,0.,0.],truncated=True)
        self.assertEqual(m.trace,[0.]*4)
        m.frozen_public_return([1.,0.,0.,0.])
        m.start_frozen_evaluation(identity)
        self.assertEqual(m.trace,[0.]*4)

    def test_parameter_digest_ignores_public_trace_and_counters(self):
        m=Model("recurrent")
        identity=m.fitted_parameter_sha256()
        full=m.checkpoint()
        m.start_frozen_evaluation(identity)
        m.choose(X)
        m.frozen_public_return([1.,0.,0.,0.])
        self.assertNotEqual(m.checkpoint(),full)
        self.assertEqual(m.fitted_parameter_sha256(),identity)

    def test_fit_tampering_fails_closed_before_choice(self):
        m=Model("recurrent")
        identity=m.fitted_parameter_sha256()
        m.start_frozen_evaluation(identity)
        m.recurrent["0"][5]=2.
        calls=m.action_calls
        before=m.trace[:]
        with self.assertRaisesRegex(ValueError,"FROZEN_FIT_CHANGED"):
            m.choose(X)
        with self.assertRaisesRegex(ValueError,"FROZEN_FIT_CHANGED"):
            m.frozen_public_return([1.,0.,0.,0.])
        self.assertEqual(m.action_calls,calls)
        self.assertEqual(m.trace,before)

    def test_mid_trial_cold_restore_retains_history_and_pinned_weights(self):
        m=Model("recurrent")
        m.recurrent["0"][5]=2.
        identity=m.fitted_parameter_sha256()
        m.start_frozen_evaluation(identity)
        m.frozen_public_return([-1.,0.,0.,0.])
        expected=m.choose(X)
        snap=m.checkpoint()
        script = """
import json,sys
from research.native.itd02.cartpolewind_compare_dev.compare import Model
payload=json.loads(sys.stdin.buffer.read())
m=Model.restore(bytes.fromhex(payload['snapshot']))
m.start_frozen_evaluation(payload['weight'],reset_trace=False)
print(json.dumps({'choice':m.choose([0.,0.,0.,0.]),
    'trace':m.trace,'weight':m.fitted_parameter_sha256()},sort_keys=True))
"""
        results=[]
        for _ in range(2):
            run=subprocess.run([sys.executable,"-B","-c",script],
                input=json.dumps({"snapshot":snap.hex(),"weight":identity}).encode(),
                capture_output=True,timeout=20,check=True)
            results.append(json.loads(run.stdout))
        self.assertEqual(results[0],results[1])
        self.assertEqual(results[0]["choice"],expected)
        self.assertEqual(results[0]["weight"],identity)
        self.assertEqual(results[0]["trace"],[-.2,0.,0.,0.])

    def test_tampered_snapshot_rejected(self):
        m=Model("recurrent")
        body=json.loads(m.checkpoint())
        body["body"]["recurrent"]["0"][5]=12.
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_CHECKPOINT"):
            Model.restore(json.dumps(body).encode())

    def test_legacy_three_arm_source_only_parity(self):
        rows=[ROW,dict(ROW,terminated=True)]
        arms=[Model(a) for a in ARMS]
        receipt=fit_identical_public_replay(arms,rows)
        self.assertEqual(receipt["public_updates_per_arm"],2)
        self.assertFalse(receipt["scientific_go"])
        self.assertEqual({a.updates for a in arms},{2})


if __name__=="__main__":
    unittest.main()
