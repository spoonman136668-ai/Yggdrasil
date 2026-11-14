"""MD35 preregistered memory-loss negative control.

Ablates within-block adaptation while leaving a fully trained conventional
control's weights and physical action limits intact. Receives only public
episodes. This module never constructs worlds or opens held-out cohorts.
"""
from public_actions import PublicEpisode


class ResetMemoryEachEpisode:
    """The model has pretrained weights but cannot use past episode outcomes."""

    def __init__(self, trained_control):
        if not all(hasattr(trained_control, attr) for attr in
                   ("checkpoint", "begin_block", "predict_target", "update")):
            raise AssertionError("MD35_ABLATION_REQUIRES_FULL_CONTROL")
        # Checkpoint must already exist: never treat unfitted models as controls.
        trained_control.checkpoint()
        self._model = trained_control
        self._position = None

    def checkpoint(self):
        return {
            "schema": "md35.episode-memory-reset-negative.v1",
            "base": self._model.checkpoint(),
        }

    def begin_block(self):
        self._position = 0
        self._model.begin_block()

    def predict_target(self, context, route):
        if self._position is None or self._position >= 4:
            raise AssertionError("MD35_ABLATION_BLOCK_REQUIRED")
        return self._model.predict_target(context, route)

    def update(self, episode):
        if (self._position is None or self._position >= 4 or
                type(episode) is not PublicEpisode or
                episode.context != self._position):
            raise AssertionError("MD35_ABLATION_PUBLIC_EPISODE_ORDER")
        # Intentional negative: do not call _model.update(episode). Never
        # let the model's persistent scratch state learn this observation.
        self._model.begin_block()
        self._position += 1


class ModelBasedWithoutRetainedBelief(ResetMemoryEachEpisode):
    """Specific registered RL ablation: fitted dynamics, no local law memory."""

    def __init__(self, trained_control):
        from model_based_rl import ModelBasedRL
        if type(trained_control) is not ModelBasedRL:
            raise AssertionError("MD35_RL_ABLATION_REQUIRES_FITTED_MODEL_BASED")
        super().__init__(trained_control)

    def checkpoint(self):
        return {
            "schema": "md35.rl-no-retained-law-belief-negative.v1",
            "base": self._model.checkpoint(),
        }

    def plan_route(self, context):
        """Keep the *same* trained Bellman planner; erase only law memory."""
        if (self._position is None or self._position >= 4 or
                type(context) is not int or context != self._position):
            raise AssertionError("MD35_RL_NEGATIVE_PUBLIC_CONTEXT_ORDER")
        return self._model.plan_route(context)
