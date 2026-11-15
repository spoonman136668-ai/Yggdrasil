"""ST5 source-only public intervention and frozen gate negative controls."""
import json
import unittest

from research.nci04_st5.diagnostic_world import (
    ACTIONS,DiagnosticWorld,initial_public,public_rotation,
    public_signature,run_original_episode,
)
from research.nci04_st5.source_audit import (
    source_disposition,TRAIN_LAWS,INTERFERENCE_LAWS,
)
from research.nci04_st4.paired_world import (
    rotation,immediate_mask,delayed_mask,public_bits,check_public,rotate_byte,
)


class ST5PublicDiagnosticSource(unittest.TestCase):
    def test_rotation_identifiability_before_source_outcomes(self):
        for seed in (100,101,111):
            for trial in range(16):
                val=initial_public(seed,trial)
                candidates={
                    rotate_byte(val,r) for r in (1,2,3)
                }
                self.assertEqual(len(candidates),3)

    def test_all_five_acts_are_real_and_source_cue_is_public_only(self):
        for law in (3,5,43):
            history,cue=run_original_episode(law,100,1)
            self.assertEqual(tuple(x[1] for x in history),ACTIONS)
            self.assertEqual(cue,(
                rotation(law),immediate_mask(law,0),
                immediate_mask(law,1)
            ))
            self.assertEqual(len(history),5)
            for before,action,after,change in history:
                self.assertEqual(
                    change,tuple(a^b for a,b in zip(before,after))
                )

    def test_no_future_label_used_to_construct_public_cue(self):
        history,cue=run_original_episode(7,101,2)
        self.assertEqual(public_signature(history[:3]),cue)
        self.assertEqual(public_signature(history),cue)
        self.assertIsNone(public_signature(history[:2]))
        changed=list(history)
        raw,a,after,y=changed[4]
        changed[4]=(raw,a,after,tuple(1-z for z in y))
        self.assertEqual(public_signature(changed),cue)

    def test_neutral_rotation_and_delayed_effect_are_authentic(self):
        for law in (3,11):
            world=DiagnosticWorld(law,100,2)
            rows=[]
            for action in ACTIONS:
                x=world.public();nxt,target=world.step(action)
                rows.append((x,action,nxt,target))
            self.assertEqual(public_rotation(rows[0][0],rows[0][2]),
                             rotation(law))
            r=rotation(law)
            prior=check_public(rows[4][0])
            target=check_public(rows[4][2])
            self.assertEqual(
                target^rotate_byte(prior,r),delayed_mask(law)
            )

    def test_true_cold_continuation_and_actor_limits(self):
        model=DiagnosticWorld(13,102,1)
        for action in ACTIONS[:3]:
            model.step(action)
        snap=model.snapshot()
        restored=DiagnosticWorld.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        for action in ACTIONS[3:]:
            self.assertEqual(model.step(action),restored.step(action))
        self.assertEqual(model.snapshot(),restored.snapshot())
        with self.assertRaises(ValueError):
            model.step(3)

    def test_invalid_source_action_does_not_mutate_world(self):
        world=DiagnosticWorld(3,100,0)
        snap=world.snapshot()
        for bad in (-1,0,1,2,4,True,1.0,"3"):
            with self.assertRaises(ValueError):
                world.step(bad)
            self.assertEqual(world.snapshot(),snap)

    def test_canonical_private_checkpoint_rejects_tamper(self):
        world=DiagnosticWorld(7,103,5)
        model=json.loads(world.snapshot())
        for mutate in (
            lambda d:d.update(schema="wrong"),
            lambda d:d.update(pending=256),
            lambda d:d.update(step=6),
            lambda d:d.update(trial=16),
            lambda d:d.update(seed=-1),
            lambda d:d.update(law=True),
        ):
            d=dict(model);mutate(d)
            with self.assertRaises(ValueError):
                DiagnosticWorld.restore(
                    json.dumps(d,sort_keys=True,separators=(",",":"))
                )

    def test_source_gate_strict_thresholds_and_alias_negative(self):
        cues={
            law:(1,i+1,17*i+1)
            for i,law in enumerate(TRAIN_LAWS+INTERFERENCE_LAWS)
        }
        passed=source_disposition(cues,7680,1536,128,0,0)
        self.assertEqual(passed["disposition"],
                         "SOURCE_LAW_RETRIEVAL_IDENTIFIABLE_DEV_ONLY")
        dup=dict(cues)
        dup[INTERFERENCE_LAWS[0]]=dup[TRAIN_LAWS[0]]
        self.assertEqual(
            source_disposition(dup,7680,1536,128,0,0)["disposition"],
            "SOURCE_DIAGNOSTIC_IDENTIFIABILITY_NO_GO"
        )
        self.assertEqual(
            source_disposition(cues,7679,1536,128,0,0)["disposition"],
            "SOURCE_DIAGNOSTIC_IDENTIFIABILITY_NO_GO"
        )
        self.assertEqual(
            source_disposition(cues,7680,1536,128,1,0)["disposition"],
            "SOURCE_DIAGNOSTIC_IDENTIFIABILITY_NO_GO"
        )


if __name__=="__main__":
    unittest.main()
