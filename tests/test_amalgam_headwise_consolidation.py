"""G25 source-free negative controls on real four direct+temporal JEPA head types."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location("g25_blend", HERE / "headwise_consolidation.py")
G25 = module_from_spec(SPEC)
SPEC.loader.exec_module(G25)


class _Native:
    def __init__(self, rows):
        self._ledger = tuple(rows)

    def _episode_reader(self):
        return self


class _Core:
    def __init__(self, rows, hs=None):
        self.native = _Native(rows)
        self._heads = tuple(hs) if hs is not None else (
            ActionLatentSpecialist("transition"),
            ActionLatentSpecialist("reward"),
            TemporalLatentSpecialist("transition"),
            TemporalLatentSpecialist("reward"),
        )

    def checkpoint(self):
        return canonical({
            "ledger": self.native._ledger,
            "heads": [h.as_data() if hasattr(h, "as_data") else h.data()
                      for h in self._heads],
        })

    def clone(self, rows=None):
        return _Core(
            self.native._ledger if rows is None else rows,
            [h.clone() for h in self._heads],
        )


def _history():
    return tuple(
        (f"old-{i}", ((i % 2, 0), (i % 2, 1)), i % 2, 1, i % 2, 1)
        for i in range(24)
    )


class G25BlendTests(unittest.TestCase):
    def setUp(self):
        self.anchor = _Core(_history())
        self.later = ("consumed-24", ((0, 0), (0, 1)), 0, 0, 0, 0)
        self.proposed = self.anchor.clone(_history() + (self.later,))

    def test_bound_and_custody_on_unchanged_head_proposal(self):
        before = self.anchor.checkpoint(), self.proposed.checkpoint()
        result = G25.assess_bounded_blend(self.anchor, self.anchor, self.proposed)
        self.assertEqual(tuple(result["heads"]), G25.HEAD_NAMES)
        self.assertEqual(result["head_count"], 4)
        self.assertEqual(result["old_witness_count"], 24)
        self.assertEqual(result["old_ledger_sha256"], digest(canonical(_history())))
        self.assertEqual(result["source_actions"], 0)
        self.assertFalse(result["official_checkpoint_restore_supported"])
        self.assertFalse(result["repaired_learner_constructed"])
        self.assertFalse(result["scientific_pass"])
        self.assertEqual(
            [h["selected_alpha"] for h in result["heads"].values()], [1.0] * 4)
        self.assertEqual(before, (self.anchor.checkpoint(), self.proposed.checkpoint()))

    def test_headwise_backtrack_does_not_veto_entire_update(self):
        bad = self.proposed.clone()
        bad._heads[0].predictor_bias = [-3.0, 3.0]
        before = bad.checkpoint()
        report = G25.assess_bounded_blend(self.anchor, self.anchor, bad)
        self.assertEqual(report["heads"]["direct_transition"]["selected_alpha"], 0.0)
        self.assertEqual(report["heads"]["direct_reward"]["selected_alpha"], 1.0)
        self.assertEqual(report["heads"]["temporal_transition"]["selected_alpha"], 1.0)
        self.assertEqual(bad.checkpoint(), before)

    def test_alpha_grid_is_strictly_frozen(self):
        with self.assertRaisesRegex(ValueError, "ALPHA_NOT_FROZEN"):
            G25._blend_head(self.anchor._heads[0], self.proposed._heads[0], 0.6)
        with self.assertRaisesRegex(ValueError, "ALPHA_NOT_FROZEN"):
            G25._blend_head(self.anchor._heads[0], self.proposed._heads[0], 1)

    def test_input_prefix_forgery_or_two_events_rejected(self):
        original = self.proposed.native._ledger
        forged = list(original)
        forged[0] = ("forged-old",) + forged[0][1:]
        with self.assertRaisesRegex(ValueError, "SOURCE_PREFIX"):
            G25.assess_bounded_blend(
                self.anchor, self.anchor, self.proposed.clone(forged))
        with self.assertRaisesRegex(ValueError, "EXACTLY_ONE"):
            G25.assess_bounded_blend(
                self.anchor, self.anchor,
                self.proposed.clone(original + (("extra",) + self.later[1:],)))

    def test_wrong_head_class_order_fails_closed(self):
        bad = self.proposed.clone()
        bad._heads = bad._heads[::-1]
        with self.assertRaisesRegex(ValueError, "HEAD4_HEAD_IDENTITY"):
            G25.assess_bounded_blend(self.anchor, self.anchor, bad)

    def test_bounded_interpolation_preserves_all_shapes_and_proposal_steps(self):
        head = self.anchor._heads[0].clone()
        head.predictor_bias[0] += 0.4
        head.steps += 3
        for alpha in G25.ALPHAS_DESCENDING:
            result = G25._blend_head(self.anchor._heads[0], head, alpha)
            self.assertEqual(result.steps, head.steps)
            self.assertEqual(len(result.encoder), len(head.encoder))
            self.assertEqual(len(result.predictor_bias), len(head.predictor_bias))
        self.assertEqual(
            G25._blend_head(self.anchor._heads[0], head, 0.0).predictor_bias,
            self.anchor._heads[0].predictor_bias)


if __name__ == "__main__":
    unittest.main()
