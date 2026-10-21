"""MR16: bounded prequential learning from the ORIGINAL MiniGrid public observation.

Development only. The only training targets are eight post-action local visual
delta bits produced by the existing MR15 sensor from env.step public image.
This explicitly designed seven-feature action channel is not autonomous feature
discovery, latent causal memory, novel transfer, or damage recovery.
"""
import math

from research.mr15.public_view_delta import PublicViewLocalDelta, SOURCE_COMMIT
from yggdrasil.developmental import N, K, D, sig, softmax, valid
from yggdrasil.task_runtime import LocalTaskRuntime

RATE = 0.035


def action_features(bits, cell, action):
    valid(bits)
    if type(cell) is not int or not 0 <= cell < N:
        raise ValueError("MR16_INVALID_CELL")
    if type(action) is not int or not 0 <= action <= 6:
        raise ValueError("MR16_INVALID_ORIGINAL_ACTION")
    a, b = (cell - 1) % N, (cell + 1) % N
    x, left, right = (float(2*bits[i]-1) for i in (cell,a,b))
    # Seven existing coefficient slots, no new model parameter. The seventh
    # feature exchanges one previous spatial product for signed native action.
    return (1., x, left, right, left*right, x*left, (action-3.)/3.)


def prediction(runtime, bits, action):
    if type(runtime) is not LocalTaskRuntime:
        raise TypeError("MR16_ORIGINAL_NATIVE_RUNTIME_REQUIRED")
    if runtime.damaged:
        raise ValueError("MR16_PRELESION_LEARNING_ONLY")
    output = []
    for i in range(N):
        features = action_features(bits,i,action)
        experts = [sig(sum(w*v for w,v in zip(row,features)))
                   for row in runtime.core.genome]
        gates = softmax(runtime.core.roles[i])
        output.append(sum(g*p for g,p in zip(gates,experts)))
    return output


class NativePublicPrequential:
    """Original fixed-budget trainable genome, with a bounded MR15 sidecar."""
    __slots__ = ("sensor","runtime")

    def __init__(self, sensor=None, runtime=None):
        self.sensor = PublicViewLocalDelta() if sensor is None else sensor
        self.runtime = LocalTaskRuntime() if runtime is None else runtime
        if (type(self.sensor) is not PublicViewLocalDelta or
            type(self.runtime) is not LocalTaskRuntime or
            self.runtime.neighbors != LocalTaskRuntime().neighbors or
            self.runtime.damaged or
            self.runtime.core.events != self.sensor.steps):
            raise ValueError("MR16_NATIVE_RUNTIME_SENSOR_IDENTITY_MISMATCH")

    def prime(self, first_public_image):
        if self.runtime.core.events or self.sensor.steps:
            raise ValueError("MR16_ALREADY_STARTED")
        return self.sensor.prime(first_public_image)

    def snapshot(self):
        return (self.sensor.snapshot(), self.runtime.snapshot())

    @classmethod
    def restore(cls, sensor_snapshot, runtime_snapshot):
        return cls(PublicViewLocalDelta.restore(sensor_snapshot),
                   LocalTaskRuntime.restore(runtime_snapshot))

    def step(self, original_environment, action):
        """Only an original environment step can provide the learner's target.

        The caller supplies an ORIGINAL environment and a chosen action; it
        cannot supply arbitrary outcome bits, reward, object IDs or role labels.
        Upstream Git custody is verified independently by the MR16 probe/CI.
        """
        if type(action) is not int or not 0 <= action <= 6:
            raise ValueError("MR16_INVALID_ORIGINAL_ACTION")
        if self.sensor.steps != self.runtime.core.events:
            raise ValueError("MR16_EVENT_SEQUENCE_DRIFT")
        start = self.snapshot()
        bits = tuple(self.sensor.bits)
        predicted = prediction(self.runtime,bits,action)  # BEFORE native step
        next_observation,reward,terminated,truncated,info = original_environment.step(action)
        if type(next_observation) is not dict or "image" not in next_observation:
            raise ValueError("MR16_ORIGINAL_PUBLIC_IMAGE_MISSING")
        event = self.sensor.observe_after_native_step(action,next_observation["image"])
        if (event["source_commit"] != SOURCE_COMMIT or
            event["observed_action"] != action or
            event["prior_local_bits"] != list(bits) or
            self.sensor.steps != self.runtime.core.events + 1):
            raise ValueError("MR16_NATIVE_SOURCE_EVENT_MISMATCH")
        targets = event["observed_next_local_bits"]
        valid(targets)
        proposal = LocalTaskRuntime.restore(start[1])
        for i,target in enumerate(targets):
            features = action_features(bits,i,action)
            experts = [sig(sum(w*x for w,x in zip(row,features)))
                       for row in proposal.core.genome]
            gate = softmax(proposal.core.roles[i])
            losses = [(target-p)**2 for p in experts]
            avg = sum(g*l for g,l in zip(gate,losses))
            for k in range(K):
                proposal.core.roles[i][k] = max(-20.,min(20.,
                    proposal.core.roles[i][k] + RATE*2*(avg-losses[k])))
                delta = RATE*gate[k]*(target-experts[k])
                for j in range(D):
                    new_w = proposal.core.genome[k][j] + delta*features[j]
                    if not math.isfinite(new_w):
                        raise ValueError("MR16_NONFINITE_NATIVE_MODEL_UPDATE")
                    proposal.core.genome[k][j] = max(-15.,min(15.,new_w))
        proposal.core.events += 1
        if (sum(len(row) for row in proposal.core.genome) +
            sum(len(row) for row in proposal.core.roles) != 45):
            raise ValueError("MR16_MODEL_CAPACITY_DRIFT")
        restored = LocalTaskRuntime.restore(proposal.snapshot())
        if restored.snapshot() != proposal.snapshot() or self.runtime.snapshot()!=start[1]:
            raise ValueError("MR16_RUNTIME_SNAPSHOT_DRIFT")
        self.runtime.core = proposal.core
        return {
            "pre_action_probabilities": predicted,
            "native_observed_delta_targets": list(targets),
            "prequential_brier": sum((p-y)**2 for p,y in zip(predicted,targets))/N,
            "observed_original_action": action,
            "original_source_commit": SOURCE_COMMIT,
            "learned_native_events": self.runtime.core.events,
            "fixed_native_coefficients": 45,
            "sensor_raw_sidecar_bytes": 24,
            "sensor_delta_bits": 8,
            "native_reward_was_not_training_target": True,
            "scientific_first_use": False,
        }


class MatchedActionCount:
    """Fully informed simple conventional baseline; memory is NOT budget-matched."""
    def __init__(self):
        self.table = {}
    def probabilities(self, bits, action):
        valid(bits)
        if type(action) is not int or not 0 <= action <= 6:
            raise ValueError("MR16_INVALID_ACTION_CONTROL")
        result=[]
        for i in range(N):
            key=(i,action,bits[i],bits[(i-1)%N],bits[(i+1)%N])
            positives,total=self.table.get(key,(0,0))
            result.append((positives+1)/(total+2))
        return result
    def observe(self, bits, action, targets):
        valid(bits);valid(targets)
        self.probabilities(bits,action)
        for i,target in enumerate(targets):
            key=(i,action,bits[i],bits[(i-1)%N],bits[(i+1)%N])
            positives,total=self.table.get(key,(0,0))
            self.table[key]=(positives+target,total+1)
