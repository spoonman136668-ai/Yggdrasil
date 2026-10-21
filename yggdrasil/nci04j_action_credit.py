"""MR12: opt-in native action-conditioned local causal observation.

Consumes only an original Git-pinned G7A native sender consequence. The action
is known *before execution*, then matched with the original source-verified
native receipt and G5 wire. It is not smuggled into packet sequence or labels.

Reuse 45 existing shared-genome/role coefficients, no extra trainable fields.
This is a development interface in an internally simulated native world,
NOT scientific transfer, role specialization, recovery, or external sensing.
"""
import math

from .developmental import K, N, D, sig, softmax, valid
from .task_runtime import LocalTaskRuntime
from .nci04g7a_environment_adapter import BoundedLocalEnvironment
from .nci04g5_local_residual import LocalResidualAdapter, WIRE_BYTES


def action_local_features(runtime, bits, cell, action):
    if type(runtime) is not LocalTaskRuntime:
        raise TypeError("original native runtime required")
    valid(bits)
    if (type(cell) is not int or not 0 <= cell < N or
        type(action) is not int or action not in (0, 1)):
        raise ValueError("native local cell/action invalid")
    left, right = runtime.neighbors[cell]
    x, a, b = (2*bits[i]-1 for i in (cell, left, right))
    # Same 7 fixed feature slots. The last former x*right slot is explicitly
    # reserved for the observed causal intervention action in THIS opt-in path.
    # A counterfactual action cannot alias to identical feature vectors.
    return (1., float(x), float(a), float(b), float(a*b),
            float(x*a), float(2*action-1))


class NativeActionLocalCredit:
    __slots__ = ("root", "runtime")

    def __init__(self, root, runtime):
        if type(runtime) is not LocalTaskRuntime:
            raise TypeError("exact existing native task runtime required")
        self.root = root
        self.runtime = runtime

    def predict(self, bits, cell, action):
        rt = self.runtime
        features = action_local_features(rt, bits, cell, action)
        guesses = [sig(sum(w*x for w, x in zip(expert, features)))
                   for expert in rt.core.genome]
        gate = softmax(rt.core.roles[cell])
        value = sum(weight*guess for weight, guess in zip(gate, guesses))
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("invalid native action probability")
        return value

    def observe_native(self, bits, action, recipient, sender, sequence, rate=.035):
        rt = self.runtime
        valid(bits)
        if (type(recipient) is not int or recipient not in rt.damaged or
            type(sender) is not int or sender not in rt.neighbors[recipient] or
            sender in rt.damaged or type(action) is not int or action not in (0, 1) or
            type(sequence) is not int or not 0 <= sequence <= 65535 or
            type(rate) not in (int, float) or not math.isfinite(rate) or
            not 0 < rate <= .1):
            raise ValueError("invalid native local action observation envelope")
        features = action_local_features(rt, bits, sender, action)
        source = rt.snapshot()
        before = self.predict(bits, sender, action)

        # Existing G7A native program is the only consequence source.
        # It invokes its original Git-verified simulator subprocess, validates
        # the independent process response, and creates its existing G5 wire.
        fork = LocalTaskRuntime.restore(source)
        wire, receipt = BoundedLocalEnvironment(self.root, fork).observe(
            bits, action, recipient, sender, sequence
        )
        if (len(wire) != WIRE_BYTES or receipt["action"] != action or
            receipt["wire_bytes"] != WIRE_BYTES or
            receipt["postlesion_damaged_target_labels"] != 0 or
            receipt["observed_world"] != "DETERMINISTIC_SIMULATED_CAUSAL_TRANSITION" or
            receipt["producer"]["external_sensor_attestation"] is not False):
            raise ValueError("original causal action is not source authenticated")
        evidence = LocalResidualAdapter(
            LocalTaskRuntime.restore(source)).verify(wire, source)
        outcome = receipt["measured_sender_next_bit"]
        if (evidence["sender"] != sender or
            evidence["recipient"] != recipient or
            evidence["sequence"] != sequence or
            evidence["own_next_bit"] != outcome):
            raise ValueError("native wire/action/outcome coupling failed")
        # The original G6 observation on a disposable fork must have been
        # sender-only, and cannot act as a target-cell answer or second update.
        original = LocalTaskRuntime.restore(source)
        if (fork.neighbors != original.neighbors or
            fork.core.genome != original.core.genome or
            fork.damaged != original.damaged or
            fork.core.events != original.core.events + 1 or
            any(fork.core.roles[i] != original.core.roles[i]
                for i in range(N) if i != sender)):
            raise ValueError("native sender provenance changed foreign state")

        # Learn in a separate exact-state clone; original runtime commits
        # once, only after source and gradient shape checks have succeeded.
        proposal = LocalTaskRuntime.restore(source)
        gate = softmax(proposal.core.roles[sender])
        expert = [sig(sum(w*x for w, x in zip(row, features)))
                  for row in proposal.core.genome]
        p = sum(a*b for a, b in zip(gate, expert))
        next_roles = [max(-20., min(20., old +
                      rate * gate[k] * (expert[k]-p) * (outcome-p)))
                      for k, old in enumerate(proposal.core.roles[sender])]
        next_genome = [
            [max(-15., min(15., w + rate*gate[k]*(outcome-expert[k])*features[j]))
             for j, w in enumerate(row)]
            for k, row in enumerate(proposal.core.genome)
        ]
        if (any(not math.isfinite(w) for row in next_genome for w in row) or
            any(not math.isfinite(w) for w in next_roles)):
            raise ValueError("nonfinite native causal gradient")
        proposal.core.roles[sender] = next_roles
        proposal.core.genome = next_genome
        proposal.core.events += 1
        if (sum(len(row) for row in next_genome) +
            sum(len(row) for row in proposal.core.roles) != 45 or
            any(proposal.core.roles[i] != original.core.roles[i]
                for i in range(N) if i != sender)):
            raise ValueError("native role/genome budget or local authority drift")
        if rt.snapshot() != source:
            raise ValueError("native runtime changed during observation")
        encoded = proposal.snapshot()
        if LocalTaskRuntime.restore(encoded).snapshot() != encoded:
            raise ValueError("unrestorable native learning state")
        rt.core = proposal.core
        return {
            "native_action": action,
            "native_sender": sender,
            "pre_outcome_prediction": before,
            "native_observed_outcome": outcome,
            "post_update_prediction": self.predict(bits, sender, action),
            "wire_bytes": WIRE_BYTES,
            "source_commit": receipt["producer"]["source_commit"],
            "source_sha256": receipt["producer"]["environment_sha256"],
            "training_events": rt.core.events,
            "new_trainable_parameters": 0,
            "fixed_native_coefficients": K*D + N*K,
            "external_sensor_attested": False,
            "native_action_provenance": "pre-execution action matched to source-verified process and wire",
            "independent_scientific_first_use": False,
            "native_action_generalization_qualified": False,
        }
