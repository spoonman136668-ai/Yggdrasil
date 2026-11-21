"""G27: opt-in SOURCE-BOUND shadow readout; not a canonical checkpoint.

A genuine NativeCausalAmalgam is independently restored through its unchanged
v1 source-equivalence contract. G26 then reconstructs bounded four-head weights.
Only native planning and shadow prediction may be queried. No updates, checkpoint
promotion, owner custody or scientific benefit are conferred by this wrapper.
This is not a security sandbox; only use in isolated research qualification.
"""
from math import isfinite

from headwise_capsule import restore_capsule, _saved
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest


class FrozenShadowReadout:
    """Usable forecasts from verified source model + G26 heads, never an actor."""

    __slots__ = ("_source", "_heads", "_source_pin", "_heads_pin")

    def __init__(self, source_model, selected_heads):
        if type(selected_heads) is not tuple or len(selected_heads) != 4:
            raise ValueError("G27_HEAD_COUNT")
        self._source = source_model
        self._heads = tuple(h.clone() for h in selected_heads)
        self._source_pin = digest(source_model.checkpoint())
        self._heads_pin = digest(canonical([_saved(h) for h in self._heads]))

    def _verify_unchanged(self):
        if digest(self._source.checkpoint()) != self._source_pin:
            raise ValueError("G27_SOURCE_MODEL_MUTATED")
        if digest(canonical([_saved(h) for h in self._heads])) != self._heads_pin:
            raise ValueError("G27_SELECTED_HEAD_MUTATED")

    def plan(self, view):
        self._verify_unchanged()
        return self._source.plan(view)  # unchanged native plan ONLY

    def specialist_forecasts(self, views, first, state=None, second=None):
        self._verify_unchanged()
        terminal = state is not None or second is not None
        history = self._source.native._episode_reader()._ledger[-8:]
        extras = (first, state, second) if terminal else (first,)
        direct, temporal = (self._heads[1], self._heads[3]) if terminal else (
            self._heads[0], self._heads[2])
        values = (direct.probability(views, *extras),
                  temporal.probability(views, extras, history))
        if any(not isinstance(v, (int, float)) or not isfinite(v)
               or v < 0 or v > 1 for v in values):
            raise ValueError("G27_INVALID_FORECAST")
        self._verify_unchanged()
        return values

    def observe_experience(self, *args, **kwargs):
        raise ValueError("G27_READ_ONLY_NO_TRAINING")

    def checkpoint(self):
        raise ValueError("G27_NOT_AN_OFFICIAL_NATIVE_CHECKPOINT")


def materialize_research_readout(capsule_raw, capsule_pin, anchor, current,
                                 proposed, *, native_parent, native_pin,
                                 donor_parent, donor_pin):
    """Cold-restore ORIGINAL source proposal; overlay G26 readout in isolation.

    Anchor/current/proposed are already original-source-verified by the caller.
    The final proposed checkpoint is re-opened independently using the existing
    official native restore and original parent bytes. The consolidated heads
    remain strictly noncanonical, not a continuing learner.
    """
    if any(type(m) is not NativeCausalAmalgam for m in (anchor, current, proposed)):
        raise ValueError("G27_NATIVE_TYPE_REQUIRED")
    original = tuple(m.checkpoint() for m in (anchor, current, proposed))
    restored_proposal = NativeCausalAmalgam.restore(
        original[2], digest(original[2]), native_parent=native_parent,
        native_pin=native_pin, donor_parent=donor_parent, donor_pin=donor_pin)
    if restored_proposal.checkpoint() != original[2]:
        raise ValueError("G27_OFFICIAL_SOURCE_COLD_RESTORE_DRIFT")
    heads, g26 = restore_capsule(
        capsule_raw, capsule_pin, anchor, current, restored_proposal)
    if not (g26["selected_head_bytes_recomputed"]
            and g26["canonical_native_model_restored"] is False):
        raise ValueError("G27_G26_CUSTODY")
    if tuple(m.checkpoint() for m in (anchor, current, proposed)) != original:
        raise ValueError("G27_INPUT_MODEL_MUTATION")
    readout = FrozenShadowReadout(restored_proposal, heads)
    return readout, {
        "schema": "yggdrasil.amalgam.dev-readonly-cold-readout.v1",
        "source_native_restored_with_original_v1": True,
        "source_proposal_sha256": digest(original[2]),
        "selected_head_state_sha256": readout._heads_pin,
        "head_count": 4,
        "original_native_plan_only": True,
        "canonical_consolidated_checkpoint_restored": False,
        "continuing_native_training_supported": False,
        "new_world_actions": 0,
        "scientific_pass": False,
        "owner_acceptance": False,
        "deployment": "NONE",
    }
