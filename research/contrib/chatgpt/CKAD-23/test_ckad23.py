"""Backward-compatible stream checkpoint and consequence monitor tests."""
import json
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience, STREAM_SCHEMA

def witness(model, index):
    views = ((index & 1, index & 1), (index & 1, (index + 1) & 1))
    public = {"s1": 0, "x1": index & 1, "s2": (index // 2) & 1,
              "x2": (index // 3) & 1, "y": (index // 4) & 1}
    return model.observe(digest(canonical(["ckad23-stream-test", index])), views, public)

class StreamRegression(unittest.TestCase):
    def test_roundtrip_legacy_stream_and_cold_continuation(self):
        model = NativeEpisodeExperience()
        for n in range(16):
            model = witness(model, n)
        old = model.checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(old, digest(old)).checkpoint(), old)
        v3 = model.begin_context(novel=True).checkpoint()
        self.assertEqual(NativeEpisodeExperience.restore(v3, digest(v3)).checkpoint(), v3)
        stream = model.begin_stream()
        first = stream.checkpoint()
        self.assertEqual(json.loads(first)["schema"], STREAM_SCHEMA)
        self.assertEqual(NativeEpisodeExperience.restore(first, digest(first)).checkpoint(), first)
        for n in range(16, 46):
            stream = witness(stream, n)
        self.assertEqual(stream.info()["count"], 46)
        self.assertEqual(stream.info()["stream"]["stream_start"], 16)
        self.assertEqual(stream.consolidate().checkpoint(), stream.checkpoint())
        raw = stream.checkpoint()
        replica = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(replica.checkpoint(), raw)
        self.assertEqual(witness(stream, 46).checkpoint(), witness(replica, 46).checkpoint())

    def test_no_unsignaled_duplicate_stream(self):
        model = NativeEpisodeExperience()
        for n in range(8):
            model = witness(model, n)
        with self.assertRaises(ValueError):
            model.begin_stream().begin_stream()

if __name__ == "__main__":
    unittest.main()
