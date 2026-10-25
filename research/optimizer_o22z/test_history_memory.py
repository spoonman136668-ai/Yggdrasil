"""O22-Z bounded source-only history vs identical public current units."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
from research.native.itd02.r1.native_policy import LocalCell,canonical
from research.optimizer_o22x.transition_belief import NativeCausalCells,check_transition
from research.optimizer_o22z.memory_control import ConditionalRecencyBeta,choice
from research.optimizer_o22z.evaluate import current,selected_return,fixture,train,actual

class PersistentIdentifiabilityPreflight(unittest.TestCase):
    def test_original_native_r1_and_r3_source_unchanged(self):
        root=Path(__file__).resolve().parents[2]
        for path,pin in {
            "research/native/itd02/r1/native_policy.py":"3aa22b1e418a7f8cd9619c476f02b8c614917b16",
            "research/native/itd02/r3/navigator.py":"5348238f4ec2183bea29262659883391b5f429fd"
        }.items():
            raw=(root/path).read_bytes().replace(b"\r\n",b"\n")
            self.assertEqual(
                hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(),pin
            )
    def test_predeclared_exact_24_plus_24_legal_public_turn_events(self):
        before=current()
        self.assertEqual(before,{"x":3,"y":3,"goal_x":3,"goal_y":6,
                                  "direction":0,"front_blocked":True})
        for phase in ("A","B"):
            seq=fixture(phase)
            self.assertEqual(len(seq),24)
            self.assertEqual(sum(e["selected_action"]==0 for e in seq),12)
            self.assertEqual(sum(e["selected_action"]==1 for e in seq),12)
            for e in seq:
                self.assertEqual(e["before"],before)
                returned=e["returned_after"]
                self.assertEqual(check_transition(before,e["selected_action"],returned)[1],0)
                self.assertEqual(set(returned),set(before))
                self.assertNotIn("hidden",returned)
        with self.assertRaises(ValueError):fixture("C")
    def test_native_original_r1_localcell_actually_receives_contradictions(self):
        native=NativeCausalCells();neg=NativeCausalCells()
        self.assertIs(type(native.cells["0"][0][0]),LocalCell)
        self.assertIsNone(choice(native,current()))
        train(native,neg,ConditionalRecencyBeta(),fixture("A"))
        self.assertEqual(native.events,24)
        self.assertEqual(native.cells["0"][0][0].updates,12)
        self.assertEqual(native.cells["1"][0][0].updates,12)
        self.assertEqual(native.cells["2"][0][0].updates,0)
        self.assertEqual(neg.events,24)
        self.assertNotEqual(native.predict(current(),0)[0],
                            neg.predict(current(),0)[0])
    def test_conventional_is_independent_finite_and_revisable(self):
        c=ConditionalRecencyBeta()
        for e in fixture("A"):
            c.learn(e["before"],e["selected_action"],e["returned_after"])
        self.assertEqual(c.events,24)
        self.assertEqual(choice(c,current()),1)
        for e in fixture("B"):
            c.learn(e["before"],e["selected_action"],e["returned_after"])
        self.assertEqual(c.events,48)
        self.assertEqual(choice(c,current()),0)
        self.assertEqual(ConditionalRecencyBeta.restore(c.checkpoint()).checkpoint(),c.checkpoint())
    def test_unseen_context_and_hidden_state_fail_closed(self):
        c=ConditionalRecencyBeta()
        alt=dict(current(),source_seed=47101)
        with self.assertRaises(ValueError):choice(c,alt)
        with self.assertRaises(ValueError):
            c.learn(current(),2,selected_return(current(),0,False))
        with self.assertRaises(ValueError):
            c.learn(current(),0,dict(current(),direction=0))
        with self.assertRaises(ValueError):
            NativeCausalCells().predict(alt,0)
    def test_true_fresh_python_cold_and_tamper(self):
        for model in (NativeCausalCells(),ConditionalRecencyBeta()):
            for e in fixture("A"):
                model.learn(e["before"],e["selected_action"],e["returned_after"])
            cp=model.checkpoint()
            prog=(
                "import json,sys;"
                "from research.optimizer_o22x.transition_belief import NativeCausalCells;"
                "from research.optimizer_o22z.memory_control import ConditionalRecencyBeta,choice;"
                "d=json.loads(sys.stdin.buffer.read());"
                "m=globals()[d['name']].restore(d['cold'].encode());"
                "print(json.dumps({'action':choice(m,d['state']),'events':m.events}))"
            )
            p=json.dumps({"name":type(model).__name__,"cold":cp.decode(),
                          "state":current()}).encode()
            out=subprocess.run([sys.executable,"-B","-c",prog],
                               input=p,capture_output=True,timeout=20)
            self.assertEqual(out.returncode,0,out.stderr.decode())
            self.assertEqual(json.loads(out.stdout),
                             {"action":choice(model,current()),"events":24})
            bad=json.loads(cp)
            bad["sha256"]="0"*64
            with self.assertRaises(ValueError):type(model).restore(json.dumps(bad).encode())
    def test_source_free_no_orig_world_claim_and_fixed_history_decision_gate(self):
        report=actual()["science"]
        self.assertEqual(report["scenario_selected_public_turn_return_rows_count"],48)
        self.assertEqual(report["public_world_source_original_new_episodes"],0)
        self.assertTrue(report["authored_fixtures_cannot_prove_world_dynamics_or_reward"])
        self.assertIsNone(report["phases"]["prior"]["native_R1_fast_slow"])
        # Preregistered first before observing result: test must fail honestly
        # if actual unchanged native R1 cannot reverse on 12 contradictory pairs.
        self.assertEqual(report["phases"]["A"]["native_R1_fast_slow"],1)
        self.assertEqual(report["phases"]["A_then_B"]["native_R1_fast_slow"],0)
        self.assertIsNone(report["phases"]["A_then_B"]["native_frozen_zero_cell"])
        self.assertTrue(report["independently_trained_conventional_recency_also_revises"])

if __name__=="__main__":unittest.main(verbosity=2)
