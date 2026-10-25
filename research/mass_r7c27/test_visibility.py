"""C27 source-only observation rights, no original MiniGrid environment episode."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r1.native_policy import PublicGrid
from research.mass_r7c27.visibility import (
    BLOCKED, CLEAR, UNKNOWN, PublicView, VisibilityEvidenceDemonstrator,
    canonical, from_source, to_original,
)


def src(blocked=False, x=2, y=3, direction=0):
    return PublicGrid(x, y, 6, 6, direction, blocked)


def seen(blocked=False, x=2, y=3, direction=0):
    return from_source(src(blocked, x, y, direction), True)


def unknown(blocked=False, x=2, y=3, direction=0):
    return from_source(src(blocked, x, y, direction), False)


class SourceOnlyVisibility(unittest.TestCase):
    def test_real_clear_is_not_masked_unknown(self):
        full = seen(False)
        blind = unknown(False)
        self.assertEqual(full.front, CLEAR)
        self.assertEqual(blind.front, UNKNOWN)
        self.assertNotEqual(full, blind)
        self.assertEqual(VisibilityEvidenceDemonstrator().choose(full), 2)
        self.assertEqual(VisibilityEvidenceDemonstrator().choose(blind), 0)

    def test_real_blocked_is_not_masked_unknown(self):
        full = seen(True)
        blind = unknown(True)
        self.assertEqual(full.front, BLOCKED)
        self.assertEqual(blind.front, UNKNOWN)
        self.assertNotEqual(full, blind)
        self.assertEqual(VisibilityEvidenceDemonstrator().choose(full), 0)

    def test_unknown_cannot_be_downcast_to_original_six_field_bool(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_CANNOT_DOWNCAST"):
            to_original(unknown())
        self.assertIs(to_original(seen(True)).front_blocked, True)
        self.assertIs(to_original(seen(False)).front_blocked, False)

    def test_masked_after_clear_never_creates_false_clear_edge(self):
        m = VisibilityEvidenceDemonstrator()
        before = unknown(False)
        after = unknown(False, direction=3)
        m.observe_return(before, 0, after, 0.5, False, False)
        self.assertEqual(m.evidence, {})
        self.assertEqual(m.action_counts, {"0": 1, "1": 0, "2": 0})
        self.assertEqual(m.reward_total, 0.5)
        self.assertEqual(m.choose(after), 0)

    def test_masked_after_blocked_never_creates_false_clear_edge(self):
        m = VisibilityEvidenceDemonstrator()
        before = unknown(True)
        after = unknown(True, direction=3)
        m.observe_return(before, 0, after, -1.0, False, False)
        self.assertEqual(m.evidence, {})
        self.assertNotIn(CLEAR, m.snapshot().decode())
        self.assertEqual(m.choose(after), 0)

    def test_visible_return_can_update_only_public_edge(self):
        m = VisibilityEvidenceDemonstrator()
        before = unknown(True)
        after = seen(True, direction=3)
        m.observe_return(before, 0, after, 0.0, False, False)
        self.assertEqual(m.evidence, {"2,3,3": BLOCKED})
        self.assertEqual(m.choose(unknown(False, direction=3)), 0)
        self.assertEqual(m.action_counts["0"], 1)

    def test_valid_existing_public_memory_survives_masking(self):
        m = VisibilityEvidenceDemonstrator()
        m.observe_return(unknown(), 0, seen(False, direction=3), 0., False, False)
        self.assertEqual(m.choose(unknown(True, direction=3)), 2)
        self.assertEqual(m.evidence, {"2,3,3": CLEAR})

    def test_selected_public_motor_consequence_preserved_without_sensor(self):
        m = VisibilityEvidenceDemonstrator()
        m.observe_return(unknown(), 2, unknown(False, x=3), 1.0, False, False)
        self.assertEqual(m.evidence, {})
        self.assertEqual(m.last_return, (3, 3, 6, 6, 0))
        self.assertEqual(m.action_counts["2"], 1)
        self.assertEqual(m.reward_total, 1.)

    def test_reject_illegal_action_or_return_without_any_mutation(self):
        m = VisibilityEvidenceDemonstrator()
        before,after = unknown(),unknown(direction=3)
        snapshot = m.snapshot()
        cases=[(True,after,0.), (7,after,0.), (0,before,0.), (0,after,float("nan"))]
        for act,post,reward in cases:
            with self.assertRaises(ValueError):
                m.observe_return(before,act,post,reward,False,False)
            self.assertEqual(m.snapshot(),snapshot)

    def test_extra_private_payload_and_malformed_public_rejected(self):
        base = unknown()
        bad = {"x":2,"y":3,"goal_x":6,"goal_y":6,"direction":0,
               "front":UNKNOWN,"env_hidden_map":True}
        with self.assertRaisesRegex(ValueError,"EXPECTED_EXACT"):
            VisibilityEvidenceDemonstrator().choose(bad)
        with self.assertRaises(ValueError):
            PublicView(True,3,6,6,0,UNKNOWN)
        with self.assertRaises(ValueError):
            from_source(PublicGrid(2,3,6,6,0,0),False)
        with self.assertRaises(ValueError):
            from_source(src(),0)
        self.assertEqual(base.front, UNKNOWN)

    def test_after_termination_or_mismatched_link_rejected(self):
        m=VisibilityEvidenceDemonstrator()
        before,after=unknown(),unknown(direction=3)
        m.observe_return(before,0,after,0.,False,True)
        snapshot=m.snapshot()
        with self.assertRaisesRegex(ValueError,"ALREADY_ENDED"):
            m.observe_return(after,1,unknown(direction=0),0.,False,False)
        self.assertEqual(m.snapshot(),snapshot)
        n=VisibilityEvidenceDemonstrator()
        n.observe_return(before,0,after,0.,False,False)
        with self.assertRaisesRegex(ValueError,"UNLINKED"):
            n.observe_return(before,0,after,0.,False,False)

    def test_checkpoint_digest_and_corruption_fail_closed(self):
        m=VisibilityEvidenceDemonstrator()
        m.observe_return(unknown(True),0,seen(True,direction=3),0.,False,False)
        restored=VisibilityEvidenceDemonstrator.restore(m.snapshot())
        self.assertEqual(restored.snapshot(),m.snapshot())
        wire=json.loads(m.snapshot())
        wire["data"]["evidence"]["2,3,3"]=CLEAR
        with self.assertRaisesRegex(ValueError,"UNAUTHENTICATED_CHECKPOINT"):
            VisibilityEvidenceDemonstrator.restore(canonical(wire))
        with self.assertRaises(ValueError):
            VisibilityEvidenceDemonstrator.restore(b"[]")

    def test_actual_fresh_python_process_restores_known_and_unknown_choices(self):
        m=VisibilityEvidenceDemonstrator()
        m.observe_return(unknown(),0,seen(False,direction=3),0.,False,False)
        query=[seen(False,direction=3),unknown(True,direction=3),
               unknown(False,direction=0)]
        expected=[m.choose(v) for v in query]
        payload={"checkpoint":m.snapshot().decode(),
                 "queries":[v.payload() for v in query],
                 "expected":expected}
        script="""import json,sys
from research.mass_r7c27.visibility import PublicView,VisibilityEvidenceDemonstrator
p=json.loads(sys.stdin.read())
m=VisibilityEvidenceDemonstrator.restore(p['checkpoint'].encode())
assert [m.choose(PublicView(**x)) for x in p['queries']]==p['expected']
print('C27_FRESH_OS_PROCESS_KNOWN_AND_UNKNOWN_DECISIONS=PASS')
"""
        root=Path(__file__).resolve().parents[2]
        r=subprocess.run([sys.executable,"-B","-c",script],
             input=json.dumps(payload),text=True,capture_output=True,
             cwd=root,timeout=20,
             env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("C27_FRESH_OS_PROCESS_KNOWN_AND_UNKNOWN_DECISIONS=PASS",r.stdout)


if __name__=="__main__":
    unittest.main()
