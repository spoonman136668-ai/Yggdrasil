"""CKAD23 opt-in unsignaled stream: exact replay, source fence, negatives."""
from fractions import Fraction
from hashlib import sha256
import json
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, SCHEMA, CONTEXT_SCHEMA, NOVEL_CONTEXT_SCHEMA, STREAM_SCHEMA,
)


def witness(i, *, flipped=False):
    s1=i%2
    x1=(i//2)%2
    s2=1 if flipped else 0
    x2=i%2
    y=1 if flipped else 0
    identifier=digest(canonical(["ckad23-stream-unit",i,flipped]))
    views=((s1,0),(s1,1))
    row={"s1":s1,"x1":x1,"s2":s2,"x2":x2,"y":y}
    return identifier,views,row


def add(m,i,flipped=False):
    identifier,views,row=witness(i,flipped=flipped)
    return m.observe(identifier,views,row)


class UnsignaledStreamTests(unittest.TestCase):
    def test_legacy_v1_v2_v3_and_v4_checkpoint_bytes(self):
        m=NativeEpisodeExperience()
        with self.assertRaises(ValueError):m.begin_stream()
        for i in range(64):
            m=add(m,i)
        plain=m.checkpoint()
        self.assertEqual(json.loads(plain)["schema"],SCHEMA)
        self.assertEqual(NativeEpisodeExperience.restore(plain,digest(plain)).checkpoint(),plain)
        v2=m.begin_context()
        v3=m.begin_context(novel=True)
        for instance,schema in ((v2,CONTEXT_SCHEMA),(v3,NOVEL_CONTEXT_SCHEMA)):
            raw=instance.checkpoint()
            self.assertEqual(json.loads(raw)["schema"],schema)
            self.assertEqual(NativeEpisodeExperience.restore(raw,digest(raw)).checkpoint(),raw)
        v4=v3.begin_stream()
        raw=v4.checkpoint()
        self.assertEqual(json.loads(raw)["schema"],STREAM_SCHEMA)
        self.assertEqual(json.loads(raw)["stream_start"],64)
        self.assertNotIn("context_start",json.loads(raw))
        self.assertEqual(v4.info()["stream"]["score"],[1,1])
        self.assertEqual(NativeEpisodeExperience.restore(raw,digest(raw)).checkpoint(),raw)

    def test_prequential_score_before_evidence_and_exact_cold_replay(self):
        m=NativeEpisodeExperience()
        for i in range(64):m=add(m,i)
        m=m.begin_stream()
        initial=m.info()["stream"]["score"]
        identifier,views,row=witness(64,flipped=True)
        p_state=m.context_forecast(views[0],row["x1"])
        p_reward=m.context_forecast(views[0],row["x1"],row["s2"],row["x2"])
        p=p_state*p_reward
        self.assertGreater(p,0)
        expected=max(Fraction(1),Fraction(*initial)/(4*p))
        after=m.observe(identifier,views,row)
        self.assertEqual(Fraction(*after.info()["stream"]["score"]),expected)
        self.assertEqual(after.info()["stream"]["detections"],[])
        self.assertEqual(len(json.loads(after.checkpoint())["episodes"]),65)
        self.assertEqual(after.observe(identifier,views,row).checkpoint(),after.checkpoint())
        self.assertEqual(NativeEpisodeExperience.restore(
            after.checkpoint(),digest(after.checkpoint())).checkpoint(),after.checkpoint())

    def test_shift_can_trigger_at_frozen_minimum_and_preserve_prior(self):
        m=NativeEpisodeExperience()
        for i in range(64):m=add(m,i)
        baseline=m.checkpoint()
        current=m.begin_stream()
        # Exercise the frozen trigger with a deliberately adversarial PUBLIC
        # outcome stream. A one-time distribution shift alone need not trigger:
        # a rapidly adapting model can explain it without accumulated surprise.
        for i in range(64,88):
            identifier,views,row=witness(i,flipped=True)
            first,second=row["x1"],row["x2"]
            p_state=current.context_forecast(views[0],first)
            state=int(p_state<=Fraction(1,2))
            p_reward=current.context_forecast(views[0],first,state,second)
            reward=int(p_reward<=Fraction(1,2))
            current=current.observe(identifier,views,
                {**row,"s2":state,"y":reward})
        info=current.info()
        self.assertEqual(info["stream"]["stream_start"],64)
        self.assertEqual(info["count"],88)
        self.assertGreaterEqual(len(info["stream"]["detections"]),1)
        for event in info["stream"]["detections"]:
            self.assertGreaterEqual(event["count"],72)
            self.assertEqual(len(event["identifier"]),64)
        raw=current.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(raw,digest(raw)).checkpoint(),raw)
        self.assertEqual(current.consolidate().checkpoint(),raw)
        self.assertEqual(m.checkpoint(),baseline)
        with self.assertRaises(ValueError):current.begin_stream()

    def test_tampered_checkpoint_and_nonpublic_bits_denied(self):
        m=NativeEpisodeExperience()
        for i in range(16):m=add(m,i)
        m=m.begin_stream()
        raw=m.checkpoint()
        packet=json.loads(raw)
        packet["stream_start"]=False
        changed=canonical(packet)
        with self.assertRaises(ValueError):NativeEpisodeExperience.restore(changed,digest(changed))
        packet=json.loads(raw)
        packet["score"]=100
        changed=canonical(packet)
        with self.assertRaises(ValueError):NativeEpisodeExperience.restore(changed,digest(changed))
        identifier,views,row=witness(16)
        bogus={**row,"hidden":1}
        with self.assertRaises(ValueError):m.observe(identifier,views,bogus)
        self.assertEqual(m.checkpoint(),raw)


if __name__=="__main__":unittest.main()
