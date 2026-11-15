"""ST6 only original source mechanics / prereg failure controls."""
import json
import unittest
from research.nci04_st6.original_world import (
    OriginalWorld,ACTIONS,TRIALS,law_params,rotate,composition,
    hypothesis_outputs,public_signature,source_episode,initial_state,bits,byte
)
from research.nci04_st6.source_audit import audit_gate,TRAIN,SEEDS


class ST6Source(unittest.TestCase):
    def test_actor_and_real_diagnostics_recover_two_hidden_actuators(self):
        for law in TRAIN:
            events,cue=source_episode(law,100,0)
            self.assertEqual(tuple(z[1] for z in events),ACTIONS)
            self.assertEqual(cue,law_params(law))
            self.assertEqual(len(events),5)
            for before,action,after,change in events:
                self.assertEqual(tuple(x^y for x,y in zip(before,after)),change)

    def test_delayed_compound_effect_is_consequential(self):
        for law in (3,5,11):
            events,cue=source_episode(law,101,1)
            prior,act,after,_=events[-1]
            self.assertEqual(act,3)
            observed=byte(after)^rotate(byte(prior),cue[0])
            self.assertEqual(observed,composition(cue[1],cue[2]))
            self.assertEqual(observed,hypothesis_outputs(cue[1],cue[2])[0])

    def test_negative_law_uses_other_rule_genuine_not_oracle(self):
        for law in (43,47):
            rows,cue=source_episode(law,100,2)
            previous,action,after,_=rows[-1]
            self.assertEqual(
                byte(after)^rotate(byte(previous),cue[0]),
                composition(cue[1],cue[2],"different_rule")
            )

    def test_public_start_rotation_identifiable_without_law(self):
        for seed in SEEDS[:3]:
            for trial in range(TRIALS):
                x=initial_state(seed,trial)
                self.assertEqual(len({rotate(x,r) for r in (1,2,3)}),3)

    def test_private_checkpoint_cold_exact_real_action_continuation(self):
        w=OriginalWorld(3,100,0)
        for action in ACTIONS[:3]:w.step(action)
        snap=w.snapshot()
        restored=OriginalWorld.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        for action in ACTIONS[3:]:
            self.assertEqual(restored.step(action),w.step(action))
        self.assertEqual(restored.snapshot(),w.snapshot())

    def test_invalid_action_never_changes_original_source(self):
        w=OriginalWorld(3,100,0);snap=w.snapshot()
        for bad in (0,1,2,4,-1,True,"3",1.5):
            with self.assertRaises(ValueError):w.step(bad)
            self.assertEqual(w.snapshot(),snap)

    def test_cold_source_checkpoint_rejects_invalids(self):
        w=OriginalWorld(3,100,0);raw=json.loads(w.snapshot())
        for changes in ({"schema":"other"},{"step":6},{"pending":256},
                        {"state":-1},{"law":True},{"law":-1}):
            mutated={**raw,**changes}
            with self.assertRaises(ValueError):
                OriginalWorld.restore(json.dumps(mutated,sort_keys=True,
                                                 separators=(",",":")))

    def test_frozen_prereg_stage0_refuses_unidentifiable_source(self):
        cues={n:(1,i,7+i) for i,n in enumerate(TRAIN)}
        ok=audit_gate(7680,1536,1536,cues,[17]*7)
        self.assertEqual(ok["disposition"],
                         "SOURCE_COMPOSITION_IDENTIFIABLE_DEV_ONLY")
        for a,e,c,cs,ds in (
            (7679,1536,1536,cues,[17]*7),
            (7680,1535,1536,cues,[17]*7),
            (7680,1536,1535,cues,[17]*7),
            (7680,1536,1536,cues,[15]*7),
            (7680,1536,1536,{**cues,23:cues[3]},[17]*7)
        ):
            self.assertEqual(
                audit_gate(a,e,c,cs,ds)["disposition"],
                "SOURCE_COMPOSITION_IDENTIFIABILITY_NO_GO"
            )


if __name__=="__main__":unittest.main()
