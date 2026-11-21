"""CSMC-02 focused original-native FIT regression; no new source first-use."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from two_tier import TwoTier, COHORT, unpack_public, pack_public

TRACE = Path(__file__).resolve().parents[1] / "CAUSAL-AMALGAM/selection-dev-01/trace.json"
FIT_HEX = ("44e50907bd0e110cf3bb43a0edb6eeb40e51bda3fe4ca0fde3020eab5"
           "44c02a0ad1aa3ab445cf006fda3bee0ad5a04b359ee")
FIRST = "f21c705258698a9a2f287870fc94d3f90f223797a9db8127f0ab176e60af9723"
LAST = "fa41b1f46abfb41d614e650a54046191bb16c48c3eb26bfc112fe5ab3941065d"
SOURCE_BLOBS = {"native_episode_experience.py": "5a18b00a4c4131526e71f51d63dfd9eb9471c81e",
                "public_causal_cells.py": "de8722f38d987ef7bcb4b7a0c23466b8e6f25712"}


def fit():
    observed = []
    if TRACE.exists():
        raw = TRACE.read_bytes()
        if sha256(raw).hexdigest() != TwoTier.ARCHIVE_DIGEST:
            raise ValueError("CSMC02_SOURCE_DRIFT")
        events = json.loads(raw)
        if type(events) is not list or len(events) != 96:
            raise ValueError("CSMC02_ARCHIVE_SHAPE")
        for i, event in enumerate(events[:50]):
            views = tuple(tuple(x) for x in event["views"])
            byte = pack_public(views, event["row"])
            ident = event["id"]
            if event["phase"] != i // 32:
                raise ValueError("CSMC02_SOURCE_PHASE")
            observed.append((ident, views, event["row"], byte))
        if bytes(x[3] for x in observed).hex() != FIT_HEX:
            raise ValueError("CSMC02_SOURCE_PAYLOAD_DRIFT")
    else:
        # Offline source-pinned fallback: 50 public FIT bytes cross-checked against
        # original repository archive in a prior GitHub audit. Not full archive hash proof.
        for i, byte in enumerate(bytes.fromhex(FIT_HEX)):
            views, row = unpack_public(byte)
            ident = digest(canonical([COHORT, (764013, 764029)[i//32], i%32]))
            observed.append((ident, views, row, byte))
    if len(observed) != 50 or observed[0][0] != FIRST or observed[-1][0] != LAST:
        raise ValueError("CSMC02_WITNESS_IDENTITY")
    for i,(ident,_,_,_) in enumerate(observed):
        if ident != digest(canonical([COHORT, (764013, 764029)[i//32], i%32])):
            raise ValueError("CSMC02_WITNESS_IDENTITY")
    return observed


class CSMC02Native(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = fit()
        native = NativeEpisodeExperience()
        for identifier,views,row,_ in cls.rows:
            native = native.observe(identifier,views,row)
        cls.native = native
        cls.two = TwoTier.from_native(native)
        cls.payload = cls.two.checkpoint()
        cls.cold = TwoTier.restore(cls.payload, digest(cls.payload))

    def test_source_module_exact_git_blobs(self):
        import yggdrasil
        directory = Path(yggdrasil.__file__).parent
        for name, target in SOURCE_BLOBS.items():
            raw = (directory/name).read_bytes()
            self.assertEqual(sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(), target)
        self.assertEqual(len(self.rows),50)

    def test_twenty_forecasts_and_ten_actions_cold_exact(self):
        for model in (self.two, self.cold):
            for ctx in (0,1):
                view=(ctx,0)
                self.assertEqual(model.propose(view),self.native.propose(view))
                for first in (0,1):
                    self.assertEqual(model.forecast(view,first),self.native.forecast(view,first))
                    for state in (0,1):
                        self.assertEqual(model.propose(view,first,state),self.native.propose(view,first,state))
                        for second in (0,1):
                            self.assertEqual(model.forecast(view,first,state,second),self.native.forecast(view,first,state,second))

    def test_cached_witness_provenance_and_conflicts(self):
        self.assertEqual(len(self.two._p["cache"]),8)
        for ident,views,row,_ in self.rows[:8]:
            self.assertEqual(self.cold.check_witness(ident,views,row),"CACHE_EXACT_MATCH")
            altered=dict(row);altered["y"]^=1
            with self.assertRaisesRegex(ValueError,"CONFLICTING_REPLAY"):
                self.cold.check_witness(ident,views,altered)

    def test_uncached_witness_needs_source_and_archive_tamper_fails(self):
        ident,views,row,_ = self.rows[9]
        with self.assertRaisesRegex(ValueError,"ARCHIVE_REQUIRED"):
            self.cold.check_witness(ident,views,row)
        with self.assertRaisesRegex(ValueError,"ARCHIVE_INTEGRITY"):
            self.cold.check_witness(ident,views,row,archived_raw=b"forged")
        if TRACE.exists():
            self.assertEqual(self.cold.check_witness(ident,views,row,archived_raw=TRACE.read_bytes()),"ARCHIVE_EXACT_MATCH")

    def test_checkpoint_bitflip_and_invalid_format(self):
        with self.assertRaises(ValueError):
            TwoTier.restore(self.payload[:-1]+b"!",digest(self.payload))
        with self.assertRaises(ValueError):
            TwoTier.restore(self.payload,"0"*64)
        with self.assertRaises(ValueError):
            TwoTier.from_native(NativeEpisodeExperience())
        self.assertEqual(self.payload,self.cold.checkpoint())

    def test_checkpoint_sizes_vs_matched_compact(self):
        baseline=len(self.two.compact_only_checkpoint())
        dual=len(self.payload)
        native=len(self.native.checkpoint())
        self.assertLess(dual,native)
        self.assertGreater(dual,baseline)
        print("CHECKPOINT_BYTES",{"original_native":native,"two_tier":dual,"compact_only":baseline})

    def test_native_loss_projection_counter_exact(self):
        shadow=self.cold._readout_native()
        self.assertEqual(shadow._projection,self.native._projection)
        self.assertEqual(shadow._transition_loss,self.native._transition_loss)
        self.assertEqual(shadow._terminal_loss,self.native._terminal_loss)
        self.assertEqual(shadow._transition._counts,self.native._transition._counts)
        self.assertEqual(shadow._terminal._counts,self.native._terminal._counts)


if __name__ == "__main__":
    unittest.main()
