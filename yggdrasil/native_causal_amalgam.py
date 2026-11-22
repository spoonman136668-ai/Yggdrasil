"""One coordinated native learner and its witnessed-consequence specialists."""
import json

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import (
    NativeTemporalMultiLearner, TemporalLatentSpecialist, _source_equivalent,
)

SCHEMA = "yggdrasil.ckad.native-causal-amalgam.v1"
MAX_BYTES = 32 * 1024 * 1024
KINDS = ("transition", "reward")


class NativeCausalAmalgam:
    """Share native witness history with four learned consequence predictors.

    The existing model retains the decision. The predictors learn in shadow
    from the same accepted atomic update. No donor witness ledger is carried
    in the running state. The original checkpoints authenticate cold replay.
    """

    def __init__(self, native, heads, native_parent, specialist_parent):
        self.native = native
        self._heads = heads
        self._native_parent = native_parent
        self._specialist_parent = specialist_parent

    @classmethod
    def activate(cls, native_raw, native_pin, donor_raw, donor_pin):
        base = NativeCumulativeLearner.restore(native_raw, native_pin)
        donor = NativeTemporalMultiLearner.restore(donor_raw, donor_pin)
        native = base.extend_experience_capacity()
        require(native._episode_reader().info()["projection"] == 0
                and donor.base.native.info()["projection"] == 0,
                "AMALGAM_PUBLIC_COORDINATES")
        heads = (donor.base.transition, donor.base.reward, donor.transition, donor.reward)
        return cls(native, heads, native_pin, donor_pin)

    def plan(self, view):
        return self.native.experience_context_plan(view)

    def specialist_forecasts(self, views, first, state=None, second=None):
        terminal = state is not None or second is not None
        history = self.native._episode_reader()._ledger[-8:]
        extras = (first, state, second) if terminal else (first,)
        direct, temporal = (self._heads[1], self._heads[3]) if terminal else (self._heads[0], self._heads[2])
        return direct.probability(views, *extras), temporal.probability(views, extras, history)

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        native = self.native.observe_experience(
            identifier, views, row, source_sha256=source_sha256, packet_sha256=packet_sha256)
        if native is self.native:
            return self
        require(views[0][0] == views[1][0], "AMALGAM_PAIRED_VIEW_COORDINATE")
        history = self.native._episode_reader()._ledger[-8:]
        transition = (row["x1"],)
        reward = (row["x1"], row["s2"], row["x2"])
        direct_t, direct_r, temporal_t, temporal_r = (head.clone() for head in self._heads)
        direct_t.observe(views, transition, row["s2"])
        direct_r.observe(views, reward, row["y"])
        temporal_t.observe(views, transition, history, row["s2"])
        temporal_r.observe(views, reward, history, row["y"])
        return NativeCausalAmalgam(native, (direct_t, direct_r, temporal_t, temporal_r),
                                  self._native_parent, self._specialist_parent)

    def checkpoint(self):
        data = {
            "schema": SCHEMA, "native_ascii": self.native.checkpoint().decode("ascii"),
            "native_parent_sha256": self._native_parent,
            "specialist_parent_sha256": self._specialist_parent,
            "action_heads": [head.as_data() for head in self._heads[:2]],
            "temporal_heads": [head.data() for head in self._heads[2:]],
        }
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "AMALGAM_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha, *, native_parent, native_pin, donor_parent, donor_pin):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and pin(expected_sha) and digest(raw) == expected_sha, "AMALGAM_CHECKPOINT_PIN")
        data = json.loads(raw)
        require(type(data) is dict and set(data) == {
            "schema", "native_ascii", "native_parent_sha256", "specialist_parent_sha256",
            "action_heads", "temporal_heads"
        } and data["schema"] == SCHEMA and canonical(data) == raw
                and data["native_parent_sha256"] == native_pin
                and data["specialist_parent_sha256"] == donor_pin, "AMALGAM_CHECKPOINT_CONTRACT")
        replay = cls.activate(native_parent, native_pin, donor_parent, donor_pin)
        current = data["native_ascii"].encode("ascii")
        native = NativeCumulativeLearner.restore(current, digest(current))
        old_ledger = replay.native._episode_reader()._ledger
        new_ledger = native._episode_reader()._ledger
        require(new_ledger[:len(old_ledger)] == old_ledger, "AMALGAM_NATIVE_PREFIX")

        for identifier, views, first, state, second, reward in new_ledger[len(old_ledger):]:
            row = {"s1": views[0][0], "x1": first, "s2": state, "x2": second, "y": reward}
            replay = replay.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])))
        require(replay.native.checkpoint() == current, "AMALGAM_NATIVE_REPLAY")
        action_heads = tuple(ActionLatentSpecialist.from_data(d, kind)
                             for d, kind in zip(data["action_heads"], KINDS, strict=True))
        temporal_heads = tuple(TemporalLatentSpecialist.from_data(d, kind)
                               for d, kind in zip(data["temporal_heads"], KINDS, strict=True))
        heads = action_heads + temporal_heads
        for saved, recomputed in zip(heads, replay._heads, strict=True):
            _source_equivalent(saved, recomputed)
        candidate = cls(native, heads, native_pin, donor_pin)
        require(candidate.checkpoint() == raw, "AMALGAM_CHECKPOINT_REPLAY")
        return candidate
