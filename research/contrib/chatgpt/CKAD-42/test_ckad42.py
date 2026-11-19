"""CKAD42 DEV-only native learned intervention-relation qualification fixtures.

No registered DEV, original pilot or reserved primary is scored in unit tests.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad42_dev_module",HERE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def fixture(t,ctx,x1,s2,x2,y):
    identifier=hashlib.sha256(("ckad42-pure-fixture|"+str(t)).encode()).hexdigest()
    return identifier,((ctx,t%2),(ctx,(t//3)%2)),{
        "s1":ctx,"x1":x1,"s2":s2,"x2":x2,"y":y}


class CKAD42Tests(unittest.TestCase):
    def test_prereg_source_identity_and_no_reserved_first_use(self):
        self.assertEqual(C.PREREG,"05f37a8675177b102b041741a1d3b678598a411e")
        self.assertEqual(C.DEV,(42111,42112))
        self.assertEqual(C.PILOT,(42211,42212))
        self.assertEqual(C.PRIMARY,(42311,42312,42313))
        self.assertTrue(set(C.DEV).isdisjoint(C.PILOT+C.PRIMARY+C.DISALLOWED))
        for seed in (*C.PILOT,*C.PRIMARY,*C.DISALLOWED):
            with self.assertRaisesRegex(ValueError,"CKAD42_ONLY_REGISTERED_DEV"):
                C.run(seed)

    def test_generic_grammar_and_coverage_from_input_only(self):
        self.assertEqual(len(C.TRANSITION),16)
        self.assertGreater(len(C.TERMINAL),20)
        self.assertLess(len(C.TERMINAL),2049)
        def pattern(bits,fn):
            return sum(fn(*tuple((state>>j)&1 for j in range(bits)))<<state
                       for state in range(1<<bits))
        self.assertIn(pattern(2,lambda c,a:c^a),C.TRANSITION)
        self.assertIn(pattern(4,lambda c,a,s,b:(c&a)^(s&b)),C.TERMINAL)
        self.assertIn(pattern(4,lambda c,a,s,b:(c&s)|(a&b)),C.TERMINAL)
        self.assertIn(pattern(4,lambda c,a,s,b:c^(s&b)),C.TERMINAL)
        self.assertIn(pattern(4,lambda c,a,s,b:(c&s)^(a|b)),C.TERMINAL)

    def test_public_action_learning_and_cold_weights(self):
        model=C.NativeInterventionRelations()
        for t in range(128):
            ctx=t%2
            x1=(t//2)%2
            x2=(t//4)%2
            next_state=ctx^x1
            reward=(ctx&x1)^(next_state&x2)
            event=fixture(t,ctx,x1,next_state,x2,reward)
            before=model.checkpoint()
            _=model.read("dual",event[1][0],x1)
            self.assertEqual(before,model.checkpoint())
            model.observe(*event)
        self.assertEqual(model.n,128)
        # After authentic interventions the model must retain a conditional
        # first-action difference; the ablated no-action control cannot.
        p0=model.read("full",(0,0),0)
        p1=model.read("full",(0,0),1)
        self.assertLess(p0,0.4)
        self.assertGreater(p1,0.6)
        self.assertAlmostEqual(model.read("no_action",(0,0),0),
                               model.read("no_action",(0,0),1))
        raw=model.checkpoint()
        restored=C.NativeInterventionRelations.restore(raw,digest(raw))
        self.assertEqual(raw,restored.checkpoint())
        self.assertEqual(model.read("dual",(1,0),1),
                         restored.read("dual",(1,0),1))

    def test_source_identity_atomicity_and_duplicate_idempotence(self):
        model=C.NativeInterventionRelations()
        event=fixture(0,1,1,1,0,1)
        model.observe(*event)
        raw=model.checkpoint()
        self.assertIs(model.observe(*event),model)
        self.assertEqual(raw,model.checkpoint())
        altered=dict(event[2]);altered["y"]=0
        with self.assertRaisesRegex(ValueError,"CKAD42_CONFLICTING_SOURCE_ID"):
            model.observe(event[0],event[1],altered)
        self.assertEqual(raw,model.checkpoint())
        with self.assertRaisesRegex(ValueError,"CKAD42_CHECKPOINT_SHA_MISMATCH"):
            C.NativeInterventionRelations.restore(raw,"0"*64)
        with self.assertRaisesRegex(ValueError,"CKAD42_PUBLIC_INPUT_BITS"):
            model.read("full",(1,1),2)

    def test_same_information_and_no_stage_future_effect(self):
        model=C.NativeInterventionRelations()
        event=fixture(4,1,0,1,1,0)
        before=model.checkpoint()
        t=model.read("dual",event[1][0],event[2]["x1"])
        q=model.read("dual",event[1][0],event[2]["x1"],
                     event[2]["s2"],event[2]["x2"])
        self.assertTrue(0<t<1 and 0<q<1)
        self.assertEqual(before,model.checkpoint())
        model.observe(*event)
        self.assertNotEqual(before,model.checkpoint())
        self.assertEqual(model.transition.n,model.terminal.n)
        self.assertEqual(model.mask_transition.n,model.mask_terminal.n)

    def test_frozen_dev_stop_strongest_conventional_and_native(self):
        def example(seed,dual=.10,base=.13,full=.13,short=.13,conv=.14,noact=.14):
            phases=(*C.PHASES,"pooled_late_shift_and_return")
            groups={}
            for phase in phases:
                arm={a:.22 for a in C.ARMS}
                arm.update({"native_dual_causal":dual,"native_stream":base,
                            "causal_full":full,"causal_discount93":short,
                            "causal_no_action":noact})
                for a in C.CONVENTIONAL:arm[a]=conv
                groups[phase]={"brier":arm}
            return {"seed":seed,"phase_metrics":groups,
                    "worlds":[{"source_complete":True,"cold_exact":True,
                     "source_prefix_exact":True,"read_only":True,
                     "duplicate_idempotent":True,"conflict_atomic":True}]}
        a,b=(example(seed) for seed in C.DEV)
        self.assertEqual(C.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(C.classify([a,example(C.DEV[1],full=.105)]),"DEV_NO_GO")
        self.assertEqual(C.classify([a,example(C.DEV[1],base=.105)]),"DEV_NO_GO")
        self.assertEqual(C.classify([a,example(C.DEV[1],noact=.105)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):C.classify([b,a])

    def test_cli_reserved_seed_rejected_without_model_training(self):
        p=subprocess.run([sys.executable,"-B",str(HERE/"campaign.py"),
                "--mode","dev","--seed",str(C.PRIMARY[0])],
                cwd=HERE.parents[3],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("CKAD42_ONLY_REGISTERED_DEV",p.stderr)


if __name__=="__main__":
    unittest.main()
